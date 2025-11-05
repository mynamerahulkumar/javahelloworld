"""
Breakout strategy service wrapper for API integration
"""
import threading
import logging
import io
from typing import Dict, Any, Optional
from ..base_strategy import BaseStrategy, StrategyStatus
from .breakout_bot import BreakoutTradingBot
from .delta_client import DeltaExchangeClient

logger = logging.getLogger(__name__)


class BreakoutService(BaseStrategy):
    """
    Service wrapper for BreakoutTradingBot that implements BaseStrategy interface.
    Handles threading, status tracking, and error handling for API integration.
    """
    
    def __init__(self, strategy_id: str, config: Dict[str, Any]):
        """
        Initialize breakout strategy service
        
        Args:
            strategy_id: Unique identifier for this strategy instance
            config: Strategy configuration dictionary containing:
                - trading: symbol, product_id, order_size, max_position_size, check_existing_orders
                - schedule: timeframe, timezone, wait_for_next_candle, startup_delay_minutes, reset_interval_minutes
                - risk_management: stop_loss_points, take_profit_points, breakeven_trigger_points
                - monitoring: order_check_interval, position_check_interval
                - api: base_url, api_key, api_secret
        """
        super().__init__(strategy_id, config)
        
        # Extract configuration
        trading_config = config.get('trading', {})
        schedule_config = config.get('schedule', {})
        risk_config = config.get('risk_management', {})
        monitoring_config = config.get('monitoring', {})
        api_config = config.get('api', {})
        
        # Initialize Delta Exchange client
        self.client = DeltaExchangeClient(
            api_key=api_config.get('api_key'),
            api_secret=api_config.get('api_secret'),
            base_url=api_config.get('base_url', 'https://api.india.delta.exchange')
        )
        
        # Initialize breakout bot
        self.bot = BreakoutTradingBot(
            client=self.client,
            symbol=trading_config['symbol'],
            product_id=trading_config['product_id'],
            order_size=trading_config['order_size'],
            stop_loss_points=risk_config['stop_loss_points'],
            take_profit_points=risk_config['take_profit_points'],
            breakeven_trigger_points=risk_config['breakeven_trigger_points'],
            timeframe=schedule_config['timeframe'],
            reset_interval_minutes=schedule_config.get('reset_interval_minutes', self._timeframe_to_minutes(schedule_config['timeframe'])),
            timezone=schedule_config['timezone'],
            order_check_interval=monitoring_config.get('order_check_interval', 10),
            position_check_interval=monitoring_config.get('position_check_interval', 5),
            wait_for_next_candle=schedule_config.get('wait_for_next_candle', False),
            startup_delay_minutes=schedule_config.get('startup_delay_minutes', 0),
            max_position_size=trading_config.get('max_position_size'),
            check_existing_orders=trading_config.get('check_existing_orders', True)
        )
        
        # Threading
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.bot_thread: Optional[threading.Thread] = None
        
        # Logging capture
        self.log_capture = io.StringIO()
        self.log_handler = logging.StreamHandler(self.log_capture)
        self.log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        
        # Add handler to bot logger
        bot_logger = logging.getLogger('strategies.breakout.breakout_bot')
        bot_logger.addHandler(self.log_handler)
        
        logger.info(f"BreakoutService initialized with strategy_id: {strategy_id}")
    
    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        timeframe_map = {
            '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '6h': 360,
            '1d': 1440, '1w': 10080
        }
        return timeframe_map.get(timeframe, 60)
    
    def _run_bot(self):
        """Run bot in background thread"""
        try:
            self.set_status(StrategyStatus.RUNNING)
            logger.info(f"Starting breakout bot thread for strategy {self.strategy_id}")
            
            # Store bot thread reference
            self.bot_thread = threading.Thread(target=self.bot.run, daemon=True)
            self.bot_thread.start()
            
            # Wait for bot thread to finish or stop event
            while self.bot_thread.is_alive() and not self.stop_event.is_set():
                self.bot_thread.join(timeout=1.0)
            
            # If stop event is set, we need to interrupt the bot
            if self.stop_event.is_set():
                logger.info(f"Stop event set for strategy {self.strategy_id}, stopping bot...")
                # The bot will continue running until it naturally exits
                # We can't easily interrupt the while True loop, but cancelling orders helps
                
        except Exception as e:
            logger.error(f"Error in breakout bot thread: {e}", exc_info=True)
            self.set_status(StrategyStatus.ERROR, str(e))
        finally:
            if self.stop_event.is_set():
                self.set_status(StrategyStatus.STOPPED)
            logger.info(f"Breakout bot thread stopped for strategy {self.strategy_id}")
    
    def start(self) -> bool:
        """
        Start the strategy execution in a background thread
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.status == StrategyStatus.RUNNING:
            logger.warning(f"Strategy {self.strategy_id} is already running")
            return False
        
        try:
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run_bot, daemon=True)
            self.thread.start()
            logger.info(f"Strategy {self.strategy_id} started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start strategy {self.strategy_id}: {e}")
            self.set_status(StrategyStatus.ERROR, str(e))
            return False
    
    def stop(self) -> bool:
        """
        Stop the strategy execution
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if self.status == StrategyStatus.STOPPED:
            logger.warning(f"Strategy {self.strategy_id} is already stopped")
            return True
        
        try:
            self.stop_event.set()
            
            # Cancel all orders to stop trading activity
            if self.bot:
                try:
                    self.bot.client.cancel_all_orders(product_id=self.bot.product_id)
                    logger.info(f"Cancelled all orders for strategy {self.strategy_id}")
                except Exception as e:
                    logger.warning(f"Error cancelling orders during stop: {e}")
            
            # Wait for thread to finish (with timeout)
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5.0)
                if self.thread.is_alive():
                    logger.warning(f"Thread for strategy {self.strategy_id} did not stop within timeout")
            
            # Also wait for bot thread if it exists
            if self.bot_thread and self.bot_thread.is_alive():
                self.bot_thread.join(timeout=2.0)
            
            self.set_status(StrategyStatus.STOPPED)
            logger.info(f"Strategy {self.strategy_id} stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to stop strategy {self.strategy_id}: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current strategy status
        
        Returns:
            Dictionary containing status information
        """
        status_info = {
            'strategy_id': self.strategy_id,
            'status': self.status.value,
            'start_time': self.start_time,
            'stop_time': self.stop_time,
            'error_message': self.error_message,
            'symbol': self.bot.symbol if self.bot else None,
            'timeframe': self.bot.timeframe if self.bot else None,
        }
        
        # Add bot state if available
        if self.bot:
            status_info.update({
                'prev_period_high': self.bot.prev_period_high,
                'prev_period_low': self.bot.prev_period_low,
                'active_position': {
                    'side': self.bot.position_side,
                    'entry_price': self.bot.entry_price,
                    'size': abs(float(self.bot.active_position.get('size', 0))) if self.bot.active_position else None,
                } if self.bot.active_position else None,
                'buy_order_id': self.bot.buy_order_id,
                'sell_order_id': self.bot.sell_order_id,
                'stop_loss_order_id': self.bot.stop_loss_order_id,
                'take_profit_order_id': self.bot.take_profit_order_id,
                'breakeven_applied': self.bot.breakeven_applied,
            })
        
        return status_info
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get strategy configuration
        
        Returns:
            Dictionary containing configuration
        """
        return self.config
    
    def get_logs(self, limit: int = 100) -> str:
        """
        Get recent logs from the strategy
        
        Args:
            limit: Maximum number of log lines to return
            
        Returns:
            Log string
        """
        log_content = self.log_capture.getvalue()
        lines = log_content.split('\n')
        recent_lines = lines[-limit:] if len(lines) > limit else lines
        return '\n'.join(recent_lines)

