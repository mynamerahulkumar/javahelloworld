"""
FastAPI routes for trading API
"""
import logging
from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
from models import PlaceLimitOrderWaitRequest, OrderResponse
from trading_service import TradingService
from client_auth import client_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["trading"])
trading_service = TradingService()


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
            base_url=base_url
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
