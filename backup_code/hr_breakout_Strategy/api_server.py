"""
FastAPI Server for Breakout Trading Bot
Allows controlling bot via API while maintaining config.yaml support
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List
import asyncio
import threading
import logging
from datetime import datetime
import uvicorn

from config_loader import ConfigLoader
from delta_client import DeltaExchangeClient
from breakout_bot import BreakoutTradingBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Breakout Trading Bot API",
    description="REST API for controlling and monitoring breakout trading bot",
    version="1.0.0"
)

# Global bot instances storage
active_bots: Dict[str, Dict] = {}
bot_threads: Dict[str, threading.Thread] = {}


# ============================================================
# Pydantic Models for Request/Response
# ============================================================

class TradingConfig(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "symbol": "BTCUSD",
            "product_id": 27,
            "order_size": 1
        }
    })
    
    symbol: str = Field(..., description="Trading symbol")
    product_id: int = Field(..., description="Product ID")
    order_size: int = Field(..., gt=0, description="Order size")


class ScheduleConfig(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "timeframe": "4h",
            "timezone": "Asia/Kolkata",
            "wait_for_next_candle": True,
            "startup_delay_minutes": 5
        }
    })
    
    timeframe: str = Field(..., pattern="^(1m|3m|5m|15m|30m|1h|2h|4h|6h|1d|1w)$", description="Timeframe for trading")
    timezone: str = Field(default="Asia/Kolkata", description="Timezone")
    wait_for_next_candle: bool = Field(default=False, description="Wait for next candle")
    startup_delay_minutes: int = Field(default=0, ge=0, description="Startup delay in minutes")


class RiskManagementConfig(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "stop_loss_points": 10000,
            "take_profit_points": 40000,
            "breakeven_trigger_points": 10000
        }
    })
    
    stop_loss_points: float = Field(..., gt=0, description="Stop loss in points")
    take_profit_points: float = Field(..., gt=0, description="Take profit in points")
    breakeven_trigger_points: float = Field(..., gt=0, description="Breakeven trigger in points")


class MonitoringConfig(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "order_check_interval": 10,
            "position_check_interval": 5
        }
    })
    
    order_check_interval: int = Field(default=10, ge=1, description="Order check interval in seconds")
    position_check_interval: int = Field(default=5, ge=1, description="Position check interval in seconds")


class BotConfiguration(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "bot_id": "bot_4h_btcusd",
            "api_key": "your_api_key",
            "api_secret": "your_api_secret"
        }
    })
    
    bot_id: str = Field(..., description="Unique bot identifier")
    api_key: str = Field(..., description="Delta Exchange API Key")
    api_secret: str = Field(..., description="Delta Exchange API Secret")
    trading: TradingConfig
    schedule: ScheduleConfig
    risk_management: RiskManagementConfig
    monitoring: MonitoringConfig = MonitoringConfig()


class BotStatus(BaseModel):
    bot_id: str
    status: str  # running, stopped, error
    started_at: Optional[str]
    configuration: Optional[Dict]
    current_position: Optional[Dict]
    active_orders: Optional[List]
    last_error: Optional[str]


class BotControlResponse(BaseModel):
    success: bool
    message: str
    bot_id: str
    status: Optional[str]


# ============================================================
# Helper Functions
# ============================================================

def run_bot_in_thread(bot_id: str, bot: BreakoutTradingBot):
    """Run bot in a separate thread"""
    try:
        logger.info(f"Starting bot {bot_id} in thread")
        active_bots[bot_id]['status'] = 'running'
        active_bots[bot_id]['last_error'] = None
        bot.run()
    except Exception as e:
        logger.error(f"Bot {bot_id} encountered error: {e}", exc_info=True)
        active_bots[bot_id]['status'] = 'error'
        active_bots[bot_id]['last_error'] = str(e)


def get_bot_state(bot_id: str) -> Dict:
    """Get current state of a bot"""
    if bot_id not in active_bots:
        return None
    
    bot_info = active_bots[bot_id]
    bot = bot_info['bot']
    
    # Get current position info
    current_position = None
    if bot.active_position:
        current_position = {
            'side': bot.position_side,
            'entry_price': bot.entry_price,
            'size': bot.order_size,
            'breakeven_applied': bot.breakeven_applied
        }
    
    # Get active orders
    active_orders = []
    if bot.buy_order_id:
        active_orders.append({
            'type': 'buy_stop',
            'order_id': bot.buy_order_id,
            'price': bot.prev_period_high
        })
    if bot.sell_order_id:
        active_orders.append({
            'type': 'sell_stop',
            'order_id': bot.sell_order_id,
            'price': bot.prev_period_low
        })
    
    return {
        'bot_id': bot_id,
        'status': bot_info['status'],
        'started_at': bot_info['started_at'],
        'configuration': bot_info['config'],
        'trading_state': {
            'prev_period_high': bot.prev_period_high,
            'prev_period_low': bot.prev_period_low,
            'timeframe': bot.timeframe,
            'symbol': bot.symbol
        },
        'current_position': current_position,
        'active_orders': active_orders,
        'last_error': bot_info.get('last_error')
    }


# ============================================================
# API Endpoints
# ============================================================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Breakout Trading Bot API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/bot/start", response_model=BotControlResponse, status_code=status.HTTP_201_CREATED)
async def start_bot(config: BotConfiguration, background_tasks: BackgroundTasks):
    """
    Start a new trading bot with the provided configuration
    
    **Example Request:**
    ```json
    {
      "bot_id": "bot_4h_btc",
      "api_key": "your_api_key",
      "api_secret": "your_api_secret",
      "trading": {
        "symbol": "BTCUSD",
        "product_id": 27,
        "order_size": 1
      },
      "schedule": {
        "timeframe": "4h",
        "timezone": "Asia/Kolkata",
        "wait_for_next_candle": true,
        "startup_delay_minutes": 5
      },
      "risk_management": {
        "stop_loss_points": 10000,
        "take_profit_points": 40000,
        "breakeven_trigger_points": 10000
      }
    }
    ```
    """
    bot_id = config.bot_id
    
    # Check if bot already running
    if bot_id in active_bots and active_bots[bot_id]['status'] == 'running':
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Bot {bot_id} is already running"
        )
    
    try:
        # Initialize Delta Exchange client
        client = DeltaExchangeClient(
            api_key=config.api_key,
            api_secret=config.api_secret,
            base_url="https://api.india.delta.exchange"
        )
        
        # Test API connection
        ticker = client.get_ticker(config.trading.symbol)
        if not ticker:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to connect to Delta Exchange API. Check credentials."
            )
        
        # Calculate reset interval if not provided
        timeframe_map = {
            '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '6h': 360,
            '1d': 1440, '1w': 10080
        }
        reset_interval = timeframe_map.get(config.schedule.timeframe, 60)
        
        # Initialize bot
        bot = BreakoutTradingBot(
            client=client,
            symbol=config.trading.symbol,
            product_id=config.trading.product_id,
            order_size=config.trading.order_size,
            stop_loss_points=config.risk_management.stop_loss_points,
            take_profit_points=config.risk_management.take_profit_points,
            breakeven_trigger_points=config.risk_management.breakeven_trigger_points,
            timeframe=config.schedule.timeframe,
            reset_interval_minutes=reset_interval,
            timezone=config.schedule.timezone,
            order_check_interval=config.monitoring.order_check_interval,
            position_check_interval=config.monitoring.position_check_interval,
            wait_for_next_candle=config.schedule.wait_for_next_candle,
            startup_delay_minutes=config.schedule.startup_delay_minutes
        )
        
        # Store bot info
        active_bots[bot_id] = {
            'bot': bot,
            'config': config.dict(),
            'status': 'starting',
            'started_at': datetime.now().isoformat(),
            'last_error': None
        }
        
        # Start bot in background thread
        thread = threading.Thread(
            target=run_bot_in_thread,
            args=(bot_id, bot),
            daemon=True
        )
        thread.start()
        bot_threads[bot_id] = thread
        
        logger.info(f"Bot {bot_id} started successfully")
        
        return BotControlResponse(
            success=True,
            message=f"Bot {bot_id} started successfully",
            bot_id=bot_id,
            status="running"
        )
        
    except Exception as e:
        logger.error(f"Failed to start bot {bot_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start bot: {str(e)}"
        )


@app.post("/api/v1/bot/stop/{bot_id}", response_model=BotControlResponse)
async def stop_bot(bot_id: str):
    """
    Stop a running bot
    
    **Parameters:**
    - bot_id: Unique identifier of the bot to stop
    """
    if bot_id not in active_bots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )
    
    try:
        # Note: In production, you'd want to implement graceful shutdown
        # For now, we mark it as stopped and the thread will end
        active_bots[bot_id]['status'] = 'stopped'
        
        # Cancel all orders for this bot
        bot = active_bots[bot_id]['bot']
        bot.client.cancel_all_orders(product_id=bot.product_id)
        
        logger.info(f"Bot {bot_id} stopped")
        
        return BotControlResponse(
            success=True,
            message=f"Bot {bot_id} stopped successfully",
            bot_id=bot_id,
            status="stopped"
        )
        
    except Exception as e:
        logger.error(f"Failed to stop bot {bot_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop bot: {str(e)}"
        )


@app.get("/api/v1/bot/status/{bot_id}", response_model=BotStatus)
async def get_bot_status(bot_id: str):
    """
    Get current status and state of a bot
    
    **Parameters:**
    - bot_id: Unique identifier of the bot
    
    **Returns:**
    - Bot status, configuration, current position, and active orders
    """
    state = get_bot_state(bot_id)
    
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )
    
    return BotStatus(**state)


@app.get("/api/v1/bots", response_model=List[BotStatus])
async def list_all_bots():
    """
    List all bots (running and stopped)
    
    **Returns:**
    - List of all bot statuses
    """
    bot_list = []
    for bot_id in active_bots.keys():
        state = get_bot_state(bot_id)
        if state:
            bot_list.append(BotStatus(**state))
    
    return bot_list


@app.delete("/api/v1/bot/{bot_id}", response_model=BotControlResponse)
async def delete_bot(bot_id: str):
    """
    Delete a bot (must be stopped first)
    
    **Parameters:**
    - bot_id: Unique identifier of the bot to delete
    """
    if bot_id not in active_bots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )
    
    if active_bots[bot_id]['status'] == 'running':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bot {bot_id} is still running. Stop it first."
        )
    
    try:
        # Remove bot from storage
        del active_bots[bot_id]
        if bot_id in bot_threads:
            del bot_threads[bot_id]
        
        logger.info(f"Bot {bot_id} deleted")
        
        return BotControlResponse(
            success=True,
            message=f"Bot {bot_id} deleted successfully",
            bot_id=bot_id,
            status="deleted"
        )
        
    except Exception as e:
        logger.error(f"Failed to delete bot {bot_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete bot: {str(e)}"
        )


@app.get("/api/v1/bot/orders/{bot_id}")
async def get_bot_orders(bot_id: str):
    """
    Get active orders for a bot
    
    **Parameters:**
    - bot_id: Unique identifier of the bot
    """
    if bot_id not in active_bots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )
    
    try:
        bot = active_bots[bot_id]['bot']
        orders = bot.client.get_open_orders(product_id=bot.product_id)
        
        return {
            "bot_id": bot_id,
            "open_orders": orders,
            "count": len(orders) if isinstance(orders, list) else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get orders for bot {bot_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get orders: {str(e)}"
        )


@app.get("/api/v1/bot/position/{bot_id}")
async def get_bot_position(bot_id: str):
    """
    Get current position for a bot
    
    **Parameters:**
    - bot_id: Unique identifier of the bot
    """
    if bot_id not in active_bots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot {bot_id} not found"
        )
    
    try:
        bot = active_bots[bot_id]['bot']
        positions = bot.client.get_positions(product_id=bot.product_id)
        
        return {
            "bot_id": bot_id,
            "positions": positions,
            "has_position": bool(bot.active_position)
        }
        
    except Exception as e:
        logger.error(f"Failed to get position for bot {bot_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get position: {str(e)}"
        )


# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )



