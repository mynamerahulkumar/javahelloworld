"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal


class PlaceLimitOrderWaitRequest(BaseModel):
    """Request model for placing limit orders that wait for price to reach entry level"""
    
    symbol: Optional[str] = Field(default="BTC", description="Trading symbol (default: BTC)")
    product_id: Optional[int] = Field(None, description="Product ID - optional if symbol provided")
    product_symbol: Optional[str] = Field(None, description="Product symbol (e.g., BTCUSD, ETHUSD)")
    
    entry_price: float = Field(..., description="Entry price (limit price) for the order", gt=0)
    size: int = Field(..., description="Order size (quantity)", gt=0)
    side: Literal["buy", "sell"] = Field(default="buy", description="Order side: buy or sell")
    
    stop_loss_price: Optional[float] = Field(None, description="Stop loss price", gt=0)
    take_profit_price: Optional[float] = Field(None, description="Take profit price", gt=0)
    client_order_id: Optional[str] = Field(None, description="Client order ID for tracking")
    
    @model_validator(mode='after')
    def validate_product_identifier(self):
        if self.symbol is None and not self.product_id and not self.product_symbol:
            raise ValueError("Either symbol, product_id, or product_symbol must be provided")
        return self


class OrderResponse(BaseModel):
    """Response model for order placement"""
    
    success: bool = Field(..., description="Whether the order was placed successfully")
    order_id: Optional[int] = Field(None, description="Order ID if successful")
    message: str = Field(..., description="Response message")
    order_data: Optional[dict] = Field(None, description="Full order data from exchange")
    error: Optional[str] = Field(None, description="Error message if failed")
