"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal, Dict, Any, List


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
    wait_time_seconds: Optional[int] = Field(default=60, description="Wait time in seconds for position to exist before placing bracket orders (minimum: 30)", ge=30)
    
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


class LoginRequest(BaseModel):
    """Request model for login"""
    
    srp_client_id: str = Field(..., description="SRP Client ID")
    srp_client_email: str = Field(..., description="SRP Client Email")
    srp_password: str = Field(..., description="SRP Client Password")


class LoginResponse(BaseModel):
    """Response model for login"""
    
    success: bool = Field(..., description="Whether login was successful")
    message: str = Field(..., description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")


# Strategy models
class TradingConfig(BaseModel):
    """Trading configuration for breakout strategy"""
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSD)")
    product_id: int = Field(..., description="Product ID", gt=0)
    order_size: int = Field(..., description="Order size", gt=0)
    max_position_size: Optional[int] = Field(None, description="Maximum position size (default: order_size * 3)")
    check_existing_orders: Optional[bool] = Field(True, description="Check for existing orders before placing new ones")


class ScheduleConfig(BaseModel):
    """Schedule configuration for breakout strategy"""
    timeframe: str = Field(..., pattern="^(1m|3m|5m|15m|30m|1h|2h|4h|6h|1d|1w)$", description="Timeframe for trading")
    timezone: str = Field(default="Asia/Kolkata", description="Timezone")
    wait_for_next_candle: Optional[bool] = Field(False, description="Wait for next candle before placing orders")
    startup_delay_minutes: Optional[int] = Field(0, ge=0, description="Startup delay in minutes")
    reset_interval_minutes: Optional[int] = Field(None, description="Reset interval in minutes (auto-calculated from timeframe if not provided)")


class RiskManagementConfig(BaseModel):
    """Risk management configuration for breakout strategy"""
    stop_loss_points: float = Field(..., gt=0, description="Stop loss in points")
    take_profit_points: float = Field(..., gt=0, description="Take profit in points")
    breakeven_trigger_points: float = Field(..., gt=0, description="Breakeven trigger in points")


class MonitoringConfig(BaseModel):
    """Monitoring configuration for breakout strategy"""
    order_check_interval: Optional[int] = Field(10, ge=1, description="Order check interval in seconds")
    position_check_interval: Optional[int] = Field(5, ge=1, description="Position check interval in seconds")


class APIConfig(BaseModel):
    """API configuration for breakout strategy"""
    base_url: Optional[str] = Field(None, description="Delta Exchange base URL (uses default if not provided)")
    api_key: Optional[str] = Field(None, description="Delta Exchange API key (required if not in headers)")
    api_secret: Optional[str] = Field(None, description="Delta Exchange API secret (required if not in headers)")


class BreakoutStrategyConfig(BaseModel):
    """Complete configuration for breakout strategy"""
    trading: TradingConfig
    schedule: ScheduleConfig
    risk_management: RiskManagementConfig
    monitoring: Optional[MonitoringConfig] = Field(default_factory=MonitoringConfig)
    api: Optional[APIConfig] = Field(default_factory=APIConfig)


class StartStrategyRequest(BaseModel):
    """Request to start a breakout strategy"""
    strategy_type: Literal["breakout"] = Field("breakout", description="Strategy type")
    config: BreakoutStrategyConfig


class StrategyStatusResponse(BaseModel):
    """Response model for strategy status"""
    strategy_id: str
    status: str
    start_time: Optional[float] = None
    stop_time: Optional[float] = None
    error_message: Optional[str] = None
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    prev_period_high: Optional[float] = None
    prev_period_low: Optional[float] = None
    active_position: Optional[Dict[str, Any]] = None
    buy_order_id: Optional[int] = None
    sell_order_id: Optional[int] = None
    stop_loss_order_id: Optional[int] = None
    take_profit_order_id: Optional[int] = None
    breakeven_applied: Optional[bool] = None


class StrategyListResponse(BaseModel):
    """Response model for list of strategies"""
    strategies: List[StrategyStatusResponse]
    total: int


class StartStrategyResponse(BaseModel):
    """Response model for starting a strategy"""
    success: bool
    strategy_id: Optional[str] = None
    message: str
    error: Optional[str] = None


class StopStrategyResponse(BaseModel):
    """Response model for stopping a strategy"""
    success: bool
    message: str
    error: Optional[str] = None


class StrategyLogsResponse(BaseModel):
    """Response model for strategy logs"""
    strategy_id: str
    logs: str


# Positions and Orders models
class Position(BaseModel):
    """Position data structure"""
    user_id: int
    size: float
    entry_price: str
    margin: str
    liquidation_price: Optional[str] = None
    bankruptcy_price: Optional[str] = None
    adl_level: Optional[int] = None
    product_id: int
    product_symbol: str
    commission: Optional[str] = None
    realized_pnl: Optional[str] = None
    realized_funding: Optional[str] = None


class PositionResponse(BaseModel):
    """Response model for positions"""
    success: bool = True
    positions: List[Position]


class OrderHistoryItem(BaseModel):
    """Single order history item"""
    id: int
    user_id: int
    size: int
    unfilled_size: Optional[int] = None
    side: str
    order_type: str
    limit_price: Optional[str] = None
    stop_order_type: Optional[str] = None
    stop_price: Optional[str] = None
    paid_commission: Optional[str] = None
    commission: Optional[str] = None
    reduce_only: bool = False
    client_order_id: Optional[str] = None
    state: str
    created_at: str
    product_id: int
    product_symbol: str


class OrderHistoryMeta(BaseModel):
    """Pagination metadata for order history"""
    after: Optional[str] = None
    before: Optional[str] = None


class OrderHistoryResponse(BaseModel):
    """Response model for order history"""
    success: bool = True
    result: List[OrderHistoryItem]
    meta: Optional[OrderHistoryMeta] = None


class PnLBySymbol(BaseModel):
    """PnL breakdown by symbol"""
    symbol: str
    realized_pnl: float
    position_count: int


class PnLSummaryResponse(BaseModel):
    """Response model for PnL summary"""
    success: bool = True
    total_pnl: float
    total_realized_pnl: float
    total_unrealized_pnl: float
    position_count: int
    pnl_by_symbol: List[PnLBySymbol]


class PollingIntervalResponse(BaseModel):
    """Response model for polling interval configuration"""
    interval_seconds: int
    min_interval: int = 1
    max_interval: int = 5


# Auth0 User Models
class Auth0User(BaseModel):
    """User information from Auth0 token"""
    email: str
    sub: str
    name: Optional[str] = None
    email_verified: bool = False
    client_id: Optional[str] = None
    whitelisted: bool = False


class UserInfoResponse(BaseModel):
    """Response model for user info endpoint"""
    success: bool = True
    user: Auth0User


class TradeHistoryItem(BaseModel):
    """Single trade/fill history item"""
    id: int
    user_id: int
    order_id: int
    size: int
    price: str
    side: str
    product_id: int
    product_symbol: str
    commission: Optional[str] = None
    realized_funding: Optional[str] = None
    created_at: str


class TradeHistoryMeta(BaseModel):
    """Pagination metadata for trade history"""
    after: Optional[str] = None
    before: Optional[str] = None


class TradeHistoryResponse(BaseModel):
    """Response model for trade history"""
    success: bool = True
    result: List[TradeHistoryItem]
    meta: Optional[TradeHistoryMeta] = None


class TestDeltaConnectionRequest(BaseModel):
    """Request model for testing Delta Exchange connection"""
    delta_api_key: str = Field(..., description="Delta Exchange API Key")
    delta_api_secret: str = Field(..., description="Delta Exchange API Secret")
    delta_base_url: Optional[str] = Field(None, description="Delta Exchange Base URL (optional)")


class TestDeltaConnectionResponse(BaseModel):
    """Response model for Delta Exchange connection test"""
    success: bool = Field(..., description="Whether the connection test was successful")
    connected: bool = Field(..., description="Whether the connection is established")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")
