"""
FastAPI routes for trading API
"""
import logging
import httpx
from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
from models import (
    PlaceLimitOrderWaitRequest, OrderResponse, LoginRequest, LoginResponse,
    StartStrategyRequest, StartStrategyResponse, StopStrategyResponse,
    StrategyStatusResponse, StrategyListResponse, StrategyLogsResponse
)
from services.trading_service import TradingService
from auth.client_auth import client_auth
from config import DELTA_BASE_URL, PRICE_FETCH_INTERVAL_SECONDS, DELTA_API_KEY, DELTA_API_SECRET
from strategies.strategy_manager import get_strategy_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["trading"])
trading_service = TradingService()


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


@router.post("/place-limit-order-wait", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def place_limit_order_wait(
    request: PlaceLimitOrderWaitRequest,
    x_srp_client_id: str = Header(..., alias="X-SRP-Client-ID", description="Your SRP Client ID (required)"),
    x_srp_client_email: str = Header(..., alias="X-SRP-Client-Email", description="Your SRP Client Email (required)"),
    x_delta_api_key: Optional[str] = Header(None, alias="X-Delta-API-Key", description="Delta Exchange API Key (optional)"),
    x_delta_api_secret: Optional[str] = Header(None, alias="X-Delta-API-Secret", description="Delta Exchange API Secret (optional)"),
    x_delta_base_url: Optional[str] = Header(None, alias="X-Delta-Base-URL", description="Delta Exchange Base URL (optional)")
) -> OrderResponse:
    """Place a stop-limit order that waits for price to reach entry level, with bracket SL/TP"""
    try:
        # Validate client authentication
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

