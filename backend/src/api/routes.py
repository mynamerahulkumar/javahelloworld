"""
FastAPI routes for trading API
"""
import logging
import httpx
import time
from fastapi import APIRouter, HTTPException, status, Header, Depends
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from models import (
    PlaceLimitOrderWaitRequest, OrderResponse, LoginRequest, LoginResponse,
    StartStrategyRequest, StartStrategyResponse, StopStrategyResponse,
    StrategyStatusResponse, StrategyListResponse, StrategyLogsResponse,
    PositionResponse, OrderHistoryResponse, PnLSummaryResponse, PollingIntervalResponse,
    TradeHistoryResponse, TestDeltaConnectionRequest, TestDeltaConnectionResponse
)
from services.trading_service import TradingService
from services.positions_service import PositionsService
from services.orders_service import OrdersService
from services.pnl_service import PnLService
from auth.client_auth import client_auth
from auth.supabase.middleware import get_current_user
from auth.email_validator import validate_email_against_csv
from config import DELTA_BASE_URL, PRICE_FETCH_INTERVAL_SECONDS, DELTA_API_KEY, DELTA_API_SECRET, POSITIONS_POLLING_INTERVAL_SECONDS
import os
from strategies.strategy_manager import get_strategy_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["trading"])
trading_service = TradingService()

# Cache for Fear & Greed Index (to avoid rate limiting)
_fear_greed_cache: Optional[Dict[str, Any]] = None
_fear_greed_cache_time: Optional[float] = None
FEAR_GREED_CACHE_TTL = 300  # Cache for 5 minutes (300 seconds)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest) -> LoginResponse:
    """Validate client credentials from CSV"""
    try:
        # Validate client authentication with password
        is_valid, error_msg = client_auth.validate_client(
            request.srp_client_id,
            request.srp_client_email,
            request.srp_password
        )
        
        if not is_valid:
            return LoginResponse(
                success=False,
                message="Login failed",
                error=error_msg
            )
        
        return LoginResponse(
            success=True,
            message="Login successful",
            error=None
        )
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return LoginResponse(
            success=False,
            message="Login failed",
            error=f"Internal server error: {str(e)}"
        )


@router.post("/test-delta-connection", response_model=TestDeltaConnectionResponse, status_code=status.HTTP_200_OK)
async def test_delta_connection(
    request: TestDeltaConnectionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> TestDeltaConnectionResponse:
    """
    Test Delta Exchange connection using provided credentials.
    Validates email against CSV whitelist and tests connection.
    CRITICAL: Credentials are never stored on server.
    """
    try:
        # Get email from Supabase session
        session_email = current_user.get("email", "").strip().lower() if current_user else ""
        
        if not session_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User email not found in session. Please sign in again."
            )
        
        # Validate email against CSV whitelist
        is_valid, client_id = validate_email_against_csv(session_email)
        if not is_valid:
            logger.warning(f"Connection test denied: User {session_email} is not in CSV whitelist")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {session_email} is not authorized. Please contact administrator."
            )
        
        # Test connection using PositionsService (simple API call)
        base_url = request.delta_base_url or "https://api.india.delta.exchange"
        
        try:
            # Test connection by fetching positions
            positions_data = PositionsService.get_all_positions(
                api_key=request.delta_api_key,
                api_secret=request.delta_api_secret,
                base_url=base_url
            )
            
            return TestDeltaConnectionResponse(
                success=True,
                connected=True,
                message="Successfully connected to Delta Exchange"
            )
        except Exception as e:
            logger.error(f"Delta Exchange connection test failed: {e}")
            error_message = str(e)
            if "401" in error_message or "Unauthorized" in error_message:
                error_message = "Invalid API credentials"
            elif "403" in error_message or "Forbidden" in error_message:
                error_message = "API credentials are not authorized"
            elif "timeout" in error_message.lower() or "network" in error_message.lower():
                error_message = "Network error. Please check your internet connection."
            
            return TestDeltaConnectionResponse(
                success=False,
                connected=False,
                error=error_message
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing Delta Exchange connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/place-limit-order-wait", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def place_limit_order_wait(
    request: PlaceLimitOrderWaitRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    x_srp_client_id: str = Header(..., alias="X-SRP-Client-ID", description="Your SRP Client ID (required)"),
    x_srp_client_email: str = Header(..., alias="X-SRP-Client-Email", description="Your SRP Client Email (required)"),
    x_delta_api_key: Optional[str] = Header(None, alias="X-Delta-API-Key", description="Delta Exchange API Key (optional)"),
    x_delta_api_secret: Optional[str] = Header(None, alias="X-Delta-API-Secret", description="Delta Exchange API Secret (optional)"),
    x_delta_base_url: Optional[str] = Header(None, alias="X-Delta-Base-URL", description="Delta Exchange Base URL (optional)")
) -> OrderResponse:
    """Place a stop-limit order that waits for price to reach entry level, with bracket SL/TP"""
    try:
        # Get email from Supabase session (authenticated user)
        session_email = current_user.get("email", "").strip().lower() if current_user else ""
        
        # Validate email from session against CSV whitelist
        if not session_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User email not found in session. Please sign in again."
            )
        
        # Validate email against CSV whitelist using email validator
        is_valid, client_id = validate_email_against_csv(session_email)
        if not is_valid:
            logger.warning(f"Order placement denied: User {session_email} is not in CSV whitelist")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {session_email} is not authorized to place orders. Please contact administrator."
            )
        
        # Validate that the email from session matches the email in headers (if provided)
        header_email = x_srp_client_email.strip().lower() if x_srp_client_email else ""
        if header_email and header_email != session_email:
            logger.warning(f"Email mismatch: Session email {session_email} does not match header email {header_email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email mismatch. Please ensure you are using the correct account."
            )
        
        # Validate client authentication (for backward compatibility)
        is_valid, error_msg = client_auth.validate_client(x_srp_client_id, x_srp_client_email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
        
        # Get API credentials
        from config import DELTA_API_KEY, DELTA_API_SECRET, DELTA_BASE_URL
        DEFAULT_BASE_URL = "https://api.india.delta.exchange"
        api_key = x_delta_api_key or DELTA_API_KEY
        api_secret = x_delta_api_secret or DELTA_API_SECRET
        base_url = x_delta_base_url or DELTA_BASE_URL or DEFAULT_BASE_URL
        
        if not api_key or not api_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API credentials required"
            )
        
        # Place the stop-limit order with brackets
        success, order_data, error = trading_service.place_limit_order_wait(
            entry_price=request.entry_price,
            size=request.size,
            side=request.side,
            stop_loss_price=request.stop_loss_price,
            take_profit_price=request.take_profit_price,
            client_order_id=request.client_order_id,
            product_id=request.product_id,
            product_symbol=request.product_symbol,
            symbol=request.symbol,
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url,
            wait_time_seconds=request.wait_time_seconds or 60
        )
        
        if success:
            order_id = order_data.get("id") if order_data else None
            message = "Stop-limit order with bracket SL/TP placed successfully"
            if order_data.get("bracket_order"):
                message += " - Bracket orders placed"
            elif order_data.get("bracket_order_error"):
                message += f" - Note: {order_data.get('bracket_order_note', '')}"
            
            return OrderResponse(
                success=True,
                order_id=order_id,
                message=message,
                order_data=order_data,
                error=error
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error or "Failed to place order")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}")


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """
    Get ticker data for a product by symbol from Delta Exchange.
    No authentication required - this is a public API endpoint.
    
    Args:
        symbol: Product symbol (e.g., BTCUSD, ETHUSD)
    
    Returns:
        Ticker data including mark_price, spot_price, volume, etc.
    """
    try:
        base_url = DELTA_BASE_URL or "https://api.india.delta.exchange"
        url = f"{base_url}/v2/tickers/{symbol}"
        
        headers = {
            'Accept': 'application/json'
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success") and data.get("result"):
                ticker_data = data["result"]
                # Return a simplified response with key price information
                return {
                    "success": True,
                    "symbol": ticker_data.get("symbol"),
                    "mark_price": float(ticker_data.get("mark_price", 0)) if ticker_data.get("mark_price") else None,
                    "spot_price": float(ticker_data.get("spot_price", 0)) if ticker_data.get("spot_price") else None,
                    "close": float(ticker_data.get("close", 0)) if ticker_data.get("close") else None,
                    "high": float(ticker_data.get("high", 0)) if ticker_data.get("high") else None,
                    "low": float(ticker_data.get("low", 0)) if ticker_data.get("low") else None,
                    "open": float(ticker_data.get("open", 0)) if ticker_data.get("open") else None,
                    "volume": float(ticker_data.get("volume", 0)) if ticker_data.get("volume") else None,
                    "timestamp": ticker_data.get("timestamp"),
                    "full_data": ticker_data  # Include full data for reference
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ticker data not found for symbol: {symbol}"
                )
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching ticker for {symbol}: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to fetch ticker data: {str(e)}"
        )
    except httpx.RequestError as e:
        logger.error(f"Request error fetching ticker for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to connect to Delta Exchange API: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching ticker for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/price-fetch-interval")
async def get_price_fetch_interval():
    """
    Get the configured price fetch interval in seconds.
    This is used by the frontend to know how often to poll for price updates.
    """
    return {
        "interval_seconds": PRICE_FETCH_INTERVAL_SECONDS
    }


# Strategy endpoints
@router.post("/strategies/breakout/start", response_model=StartStrategyResponse, status_code=status.HTTP_200_OK)
async def start_breakout_strategy(
    request: StartStrategyRequest,
    x_srp_client_id: str = Header(..., alias="X-SRP-Client-ID", description="Your SRP Client ID (required)"),
    x_srp_client_email: str = Header(..., alias="X-SRP-Client-Email", description="Your SRP Client Email (required)"),
    x_delta_api_key: Optional[str] = Header(None, alias="X-Delta-API-Key", description="Delta Exchange API Key (optional)"),
    x_delta_api_secret: Optional[str] = Header(None, alias="X-Delta-API-Secret", description="Delta Exchange API Secret (optional)"),
    x_delta_base_url: Optional[str] = Header(None, alias="X-Delta-Base-URL", description="Delta Exchange Base URL (optional)")
) -> StartStrategyResponse:
    """
    Start a new breakout strategy instance.
    Strategy runs continuously in background until explicitly stopped.
    """
    try:
        # Validate client authentication
        is_valid, error_msg = client_auth.validate_client(x_srp_client_id, x_srp_client_email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
        
        # Get API credentials (from headers or environment)
        api_key = x_delta_api_key or DELTA_API_KEY
        api_secret = x_delta_api_secret or DELTA_API_SECRET
        base_url = x_delta_base_url or DELTA_BASE_URL or "https://api.india.delta.exchange"
        
        if not api_key or not api_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API credentials required (provide via headers or environment variables)"
            )
        
        # Prepare configuration dict
        config_dict = request.config.model_dump()
        
        # Add API credentials to config
        if not config_dict.get('api'):
            config_dict['api'] = {}
        config_dict['api']['api_key'] = api_key
        config_dict['api']['api_secret'] = api_secret
        config_dict['api']['base_url'] = base_url
        
        # Auto-calculate reset_interval_minutes if not provided
        if not config_dict['schedule'].get('reset_interval_minutes'):
            timeframe = config_dict['schedule']['timeframe']
            timeframe_map = {
                '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '2h': 120, '4h': 240, '6h': 360,
                '1d': 1440, '1w': 10080
            }
            config_dict['schedule']['reset_interval_minutes'] = timeframe_map.get(timeframe, 60)
        
        # Start strategy
        strategy_manager = get_strategy_manager()
        strategy_id = strategy_manager.start_strategy(
            strategy_type=request.strategy_type,
            config=config_dict
        )
        
        return StartStrategyResponse(
            success=True,
            strategy_id=strategy_id,
            message=f"Breakout strategy started successfully with ID: {strategy_id}",
            error=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting strategy: {e}", exc_info=True)
        return StartStrategyResponse(
            success=False,
            strategy_id=None,
            message="Failed to start strategy",
            error=str(e)
        )


@router.post("/strategies/{strategy_id}/stop", response_model=StopStrategyResponse, status_code=status.HTTP_200_OK)
async def stop_strategy(
    strategy_id: str,
    x_srp_client_id: str = Header(..., alias="X-SRP-Client-ID", description="Your SRP Client ID (required)"),
    x_srp_client_email: str = Header(..., alias="X-SRP-Client-Email", description="Your SRP Client Email (required)")
) -> StopStrategyResponse:
    """
    Stop a specific running strategy instance.
    """
    try:
        # Validate client authentication
        is_valid, error_msg = client_auth.validate_client(x_srp_client_id, x_srp_client_email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
        
        strategy_manager = get_strategy_manager()
        success = strategy_manager.stop_strategy(strategy_id)
        
        if success:
            return StopStrategyResponse(
                success=True,
                message=f"Strategy {strategy_id} stopped successfully",
                error=None
            )
        else:
            return StopStrategyResponse(
                success=False,
                message=f"Failed to stop strategy {strategy_id}",
                error="Strategy not found or already stopped"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping strategy: {e}", exc_info=True)
        return StopStrategyResponse(
            success=False,
            message="Failed to stop strategy",
            error=str(e)
        )


@router.get("/strategies", response_model=StrategyListResponse, status_code=status.HTTP_200_OK)
async def get_all_strategies(
    x_srp_client_id: str = Header(..., alias="X-SRP-Client-ID", description="Your SRP Client ID (required)"),
    x_srp_client_email: str = Header(..., alias="X-SRP-Client-Email", description="Your SRP Client Email (required)")
) -> StrategyListResponse:
    """
    Get list of all strategy instances (running and stopped).
    """
    try:
        # Validate client authentication
        is_valid, error_msg = client_auth.validate_client(x_srp_client_id, x_srp_client_email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
        
        strategy_manager = get_strategy_manager()
        strategies_data = strategy_manager.get_all_strategies()
        
        strategies = [StrategyStatusResponse(**status) for status in strategies_data]
        
        return StrategyListResponse(
            strategies=strategies,
            total=len(strategies)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting strategies: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/strategies/{strategy_id}", response_model=StrategyStatusResponse, status_code=status.HTTP_200_OK)
async def get_strategy_status(
    strategy_id: str,
    x_srp_client_id: str = Header(..., alias="X-SRP-Client-ID", description="Your SRP Client ID (required)"),
    x_srp_client_email: str = Header(..., alias="X-SRP-Client-Email", description="Your SRP Client Email (required)")
) -> StrategyStatusResponse:
    """
    Get status and details of a specific strategy instance.
    """
    try:
        # Validate client authentication
        is_valid, error_msg = client_auth.validate_client(x_srp_client_id, x_srp_client_email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
        
        strategy_manager = get_strategy_manager()
        status_data = strategy_manager.get_strategy_status(strategy_id)
        
        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy {strategy_id} not found"
            )
        
        return StrategyStatusResponse(**status_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting strategy status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/strategies/{strategy_id}/logs", response_model=StrategyLogsResponse, status_code=status.HTTP_200_OK)
async def get_strategy_logs(
    strategy_id: str,
    limit: int = 100,
    x_srp_client_id: str = Header(..., alias="X-SRP-Client-ID", description="Your SRP Client ID (required)"),
    x_srp_client_email: str = Header(..., alias="X-SRP-Client-Email", description="Your SRP Client Email (required)")
) -> StrategyLogsResponse:
    """
    Get logs from a specific strategy instance.
    """
    try:
        # Validate client authentication
        is_valid, error_msg = client_auth.validate_client(x_srp_client_id, x_srp_client_email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
        
        strategy_manager = get_strategy_manager()
        logs = strategy_manager.get_strategy_logs(strategy_id, limit=limit)
        
        if logs is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy {strategy_id} not found or logs not available"
            )
        
        return StrategyLogsResponse(
            strategy_id=strategy_id,
            logs=logs
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting strategy logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Positions and Orders endpoints - CRITICAL: Only accept credentials via headers, never from server storage
@router.get("/positions", response_model=PositionResponse, status_code=status.HTTP_200_OK)
async def get_positions(
    x_srp_client_id: str = Header(..., alias="X-SRP-Client-ID", description="Your SRP Client ID (required)"),
    x_srp_client_email: str = Header(..., alias="X-SRP-Client-Email", description="Your SRP Client Email (required)"),
    x_delta_api_key: str = Header(..., alias="X-Delta-API-Key", description="Delta Exchange API Key (required, client-side only)"),
    x_delta_api_secret: str = Header(..., alias="X-Delta-API-Secret", description="Delta Exchange API Secret (required, client-side only)"),
    x_delta_base_url: Optional[str] = Header(None, alias="X-Delta-Base-URL", description="Delta Exchange Base URL (optional)")
) -> PositionResponse:
    """
    Get all margined positions.
    CRITICAL: API credentials are only accepted via headers (client-side only, never stored on server).
    """
    try:
        # Validate client authentication
        is_valid, error_msg = client_auth.validate_client(x_srp_client_id, x_srp_client_email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
        
        # CRITICAL: Only use credentials from headers, never from server storage
        base_url = x_delta_base_url or "https://api.india.delta.exchange"
        
        if not x_delta_api_key or not x_delta_api_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Delta API credentials required via headers (client-side only)"
            )
        
        # Get positions using PositionsService
        positions_data = PositionsService.get_all_positions(
            api_key=x_delta_api_key,
            api_secret=x_delta_api_secret,
            base_url=base_url
        )
        
        # Convert to Position models
        from models import Position
        positions = [Position(**pos) for pos in positions_data]
        
        return PositionResponse(
            success=True,
            positions=positions
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error fetching positions: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching positions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/orders/history", response_model=OrderHistoryResponse, status_code=status.HTTP_200_OK)
async def get_order_history(
    page_size: int = 100,
    after: Optional[str] = None,
    x_srp_client_id: str = Header(..., alias="X-SRP-Client-ID", description="Your SRP Client ID (required)"),
    x_srp_client_email: str = Header(..., alias="X-SRP-Client-Email", description="Your SRP Client Email (required)"),
    x_delta_api_key: str = Header(..., alias="X-Delta-API-Key", description="Delta Exchange API Key (required, client-side only)"),
    x_delta_api_secret: str = Header(..., alias="X-Delta-API-Secret", description="Delta Exchange API Secret (required, client-side only)"),
    x_delta_base_url: Optional[str] = Header(None, alias="X-Delta-Base-URL", description="Delta Exchange Base URL (optional)")
) -> OrderHistoryResponse:
    """
    Get order history with pagination.
    CRITICAL: API credentials are only accepted via headers (client-side only, never stored on server).
    """
    try:
        # Validate client authentication
        is_valid, error_msg = client_auth.validate_client(x_srp_client_id, x_srp_client_email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
        
        # CRITICAL: Only use credentials from headers, never from server storage
        base_url = x_delta_base_url or "https://api.india.delta.exchange"
        
        if not x_delta_api_key or not x_delta_api_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Delta API credentials required via headers (client-side only)"
            )
        
        # Validate page_size
        if page_size < 1 or page_size > 500:
            page_size = 100
        
        # Get order history using OrdersService
        order_history_data = OrdersService.get_order_history(
            api_key=x_delta_api_key,
            api_secret=x_delta_api_secret,
            base_url=base_url,
            page_size=page_size,
            after=after
        )
        
        # Convert to OrderHistoryItem models
        from models import OrderHistoryItem, OrderHistoryMeta
        orders = [OrderHistoryItem(**order) for order in order_history_data.get('result', [])]
        meta = OrderHistoryMeta(**order_history_data.get('meta', {})) if order_history_data.get('meta') else None
        
        return OrderHistoryResponse(
            success=True,
            result=orders,
            meta=meta
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error fetching order history: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching order history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/pnl", response_model=PnLSummaryResponse, status_code=status.HTTP_200_OK)
async def get_pnl_summary(
    x_srp_client_id: str = Header(..., alias="X-SRP-Client-ID", description="Your SRP Client ID (required)"),
    x_srp_client_email: str = Header(..., alias="X-SRP-Client-Email", description="Your SRP Client Email (required)"),
    x_delta_api_key: str = Header(..., alias="X-Delta-API-Key", description="Delta Exchange API Key (required, client-side only)"),
    x_delta_api_secret: str = Header(..., alias="X-Delta-API-Secret", description="Delta Exchange API Secret (required, client-side only)"),
    x_delta_base_url: Optional[str] = Header(None, alias="X-Delta-Base-URL", description="Delta Exchange Base URL (optional)")
) -> PnLSummaryResponse:
    """
    Get PnL summary including total, realized, and unrealized PnL.
    CRITICAL: API credentials are only accepted via headers (client-side only, never stored on server).
    """
    try:
        # Validate client authentication
        is_valid, error_msg = client_auth.validate_client(x_srp_client_id, x_srp_client_email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
        
        # CRITICAL: Only use credentials from headers, never from server storage
        base_url = x_delta_base_url or "https://api.india.delta.exchange"
        
        if not x_delta_api_key or not x_delta_api_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Delta API credentials required via headers (client-side only)"
            )
        
        # Get PnL summary using PnLService
        pnl_summary = PnLService.get_pnl_summary(
            api_key=x_delta_api_key,
            api_secret=x_delta_api_secret,
            base_url=base_url
        )
        
        # Convert to PnLBySymbol models
        from models import PnLBySymbol
        pnl_by_symbol = [PnLBySymbol(**item) for item in pnl_summary.get('pnl_by_symbol', [])]
        
        return PnLSummaryResponse(
            success=True,
            total_pnl=pnl_summary['total_pnl'],
            total_realized_pnl=pnl_summary['total_realized_pnl'],
            total_unrealized_pnl=pnl_summary['total_unrealized_pnl'],
            position_count=pnl_summary['position_count'],
            pnl_by_symbol=pnl_by_symbol
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error fetching PnL summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching PnL summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/polling-interval", response_model=PollingIntervalResponse, status_code=status.HTTP_200_OK)
async def get_polling_interval() -> PollingIntervalResponse:
    """
    Get the configured polling interval for positions/orders updates.
    """
    return PollingIntervalResponse(
        interval_seconds=POSITIONS_POLLING_INTERVAL_SECONDS,
        min_interval=1,
        max_interval=5
    )


@router.get("/fear-greed-index", status_code=status.HTTP_200_OK)
async def get_fear_greed_index() -> Dict[str, Any]:
    """
    Get Fear & Greed Index from CoinMarketCap API.
    This endpoint does NOT require authentication - it's a public market indicator.
    Only requires CRYPTO_MARKET_API_KEY to be configured on the server.
    
    Implements caching to avoid rate limiting (5 minute cache TTL).
    """
    global _fear_greed_cache, _fear_greed_cache_time
    
    try:
        logger.info("Fear & Greed Index endpoint called")
        
        # Check cache first
        current_time = time.time()
        if _fear_greed_cache and _fear_greed_cache_time:
            cache_age = current_time - _fear_greed_cache_time
            if cache_age < FEAR_GREED_CACHE_TTL:
                logger.info(f"Returning cached Fear & Greed Index (age: {cache_age:.1f}s)")
                return _fear_greed_cache
        
        # Get API key from environment
        api_key = os.getenv("CRYPTO_MARKET_API_KEY")
        if not api_key:
            logger.error("CRYPTO_MARKET_API_KEY is not configured in environment variables")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="CRYPTO_MARKET_API_KEY is not configured on the server"
            )
        
        logger.info("Fetching Fear & Greed Index from CoinMarketCap API...")
        
        # Fetch from CoinMarketCap API using latest endpoint
        base_url = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest"
        headers = {
            'X-CMC_PRO_API_KEY': api_key,
            'Accept': 'application/json',
            'Accept-Encoding': 'deflate, gzip'
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.debug(f"Making request to CoinMarketCap API: {base_url}")
                response = await client.get(base_url, headers=headers)
                logger.debug(f"CoinMarketCap API response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check error_code (can be string '0' or integer 0)
                    error_code = data.get('status', {}).get('error_code')
                    if error_code == 0 or error_code == '0' or str(error_code) == '0':
                        # The /latest endpoint returns data directly, not in an array
                        index_data = data.get('data', {})
                        
                        if index_data:
                            value = index_data.get('value', 50)
                            classification = index_data.get('value_classification', 'Neutral')
                            update_time = index_data.get('update_time', '')
                            logger.info(f"Fear & Greed Index fetched successfully: {value} ({classification})")
                            
                            # Cache the result
                            result = {
                                "success": True,
                                "data": {
                                    "value": value,
                                    "value_classification": classification,
                                    "update_time": update_time,
                                }
                            }
                            _fear_greed_cache = result
                            _fear_greed_cache_time = current_time
                            
                            return result
                        else:
                            logger.warning("CoinMarketCap API returned empty data")
                            # Return cached data if available, even if expired
                            if _fear_greed_cache:
                                logger.info("Returning stale cached data due to empty API response")
                                return _fear_greed_cache
                            raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND,
                                detail="No Fear & Greed Index data available"
                            )
                    else:
                        error_msg = data.get('status', {}).get('error_message', 'Unknown error')
                        logger.error(f"CoinMarketCap API error: error_code={error_code}, message={error_msg}")
                        # Return cached data if available on API error
                        if _fear_greed_cache:
                            logger.info("Returning cached data due to API error")
                            return _fear_greed_cache
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=f"CoinMarketCap API error: {error_msg}"
                        )
                elif response.status_code == 429:
                    # Rate limited - return cached data if available
                    logger.warning("CoinMarketCap API rate limited (429). Returning cached data if available.")
                    if _fear_greed_cache:
                        logger.info("Returning cached data due to rate limit")
                        return _fear_greed_cache
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again in a few minutes."
                    )
                else:
                    response_text = response.text[:500]  # Limit log size
                    logger.error(f"CoinMarketCap API HTTP error {response.status_code}: {response_text}")
                    # Return cached data if available on HTTP error
                    if _fear_greed_cache:
                        logger.info(f"Returning cached data due to HTTP {response.status_code} error")
                        return _fear_greed_cache
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Failed to fetch Fear & Greed Index: HTTP {response.status_code}"
                    )
        except httpx.TimeoutException as e:
            logger.error(f"Timeout while fetching Fear & Greed Index from CoinMarketCap API: {e}")
            # Return cached data if available on timeout
            if _fear_greed_cache:
                logger.info("Returning cached data due to timeout")
                return _fear_greed_cache
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to CoinMarketCap API timed out. Please try again later."
            )
        except httpx.RequestError as e:
            logger.error(f"Request error while fetching Fear & Greed Index: {e}", exc_info=True)
            # Return cached data if available on request error
            if _fear_greed_cache:
                logger.info("Returning cached data due to request error")
                return _fear_greed_cache
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to connect to CoinMarketCap API: {str(e)}"
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions (they're already logged)
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching Fear & Greed Index: {e}", exc_info=True)
        # Return cached data if available on unexpected error
        if _fear_greed_cache:
            logger.info("Returning cached data due to unexpected error")
            return _fear_greed_cache
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/trades/history", response_model=TradeHistoryResponse, status_code=status.HTTP_200_OK)
async def get_trade_history(
    page_size: int = 100,
    after: Optional[str] = None,
    x_srp_client_id: str = Header(..., alias="X-SRP-Client-ID", description="Your SRP Client ID (required)"),
    x_srp_client_email: str = Header(..., alias="X-SRP-Client-Email", description="Your SRP Client Email (required)"),
    x_delta_api_key: str = Header(..., alias="X-Delta-API-Key", description="Delta Exchange API Key (required, client-side only)"),
    x_delta_api_secret: str = Header(..., alias="X-Delta-API-Secret", description="Delta Exchange API Secret (required, client-side only)"),
    x_delta_base_url: Optional[str] = Header(None, alias="X-Delta-Base-URL", description="Delta Exchange Base URL (optional)")
) -> TradeHistoryResponse:
    """
    Get trade history (fills) with pagination.
    CRITICAL: API credentials are only accepted via headers (client-side only, never stored on server).
    """
    try:
        # Validate client authentication
        is_valid, error_msg = client_auth.validate_client(x_srp_client_id, x_srp_client_email)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg)
        
        # CRITICAL: Only use credentials from headers, never from server storage
        base_url = x_delta_base_url or "https://api.india.delta.exchange"
        
        if not x_delta_api_key or not x_delta_api_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Delta API credentials required via headers (client-side only)"
            )
        
        # Validate page_size
        if page_size < 1 or page_size > 500:
            page_size = 100
        
        # Get trade history using OrdersService
        trade_history_data = OrdersService.get_trade_history(
            api_key=x_delta_api_key,
            api_secret=x_delta_api_secret,
            base_url=base_url,
            page_size=page_size,
            after=after
        )
        
        # Convert to TradeHistoryItem models
        from models import TradeHistoryItem, TradeHistoryMeta
        trades = [TradeHistoryItem(**trade) for trade in trade_history_data.get('result', [])]
        meta = TradeHistoryMeta(**trade_history_data.get('meta', {})) if trade_history_data.get('meta') else None
        
        return TradeHistoryResponse(
            success=True,
            result=trades,
            meta=meta
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error fetching trade history: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching trade history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

