"""Breakout Trading Bot with configurable timeframes (hourly/daily)"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import pytz

# Handle both direct execution and module import
try:
    from .delta_client import DeltaExchangeClient
except ImportError:
    from delta_client import DeltaExchangeClient

logger = logging.getLogger(__name__)


class BreakoutTradingBot:
    """
    Configurable timeframe breakout trading bot that:
    1. Calculates previous period high/low (hourly/daily)
    2. Places limit orders at breakout levels
    3. Monitors positions and implements breakeven logic
    4. Automatically resets based on configured interval
    """
    
    def __init__(
        self,
        client: DeltaExchangeClient,
        symbol: str,
        product_id: int,
        order_size: int,
        stop_loss_points: float,
        take_profit_points: float,
        breakeven_trigger_points: float,
        timeframe: str,
        reset_interval_minutes: int,
        timezone: str,
        order_check_interval: int,
        position_check_interval: int,
        wait_for_next_candle: bool = False,
        startup_delay_minutes: int = 0,
        max_position_size: int = None,
        check_existing_orders: bool = True
    ):
        """
        Initialize breakout trading bot
        
        Args:
            client: Delta Exchange API client
            symbol: Trading symbol
            product_id: Product ID
            order_size: Order size for each trade
            stop_loss_points: Stop loss distance in points
            take_profit_points: Take profit distance in points
            breakeven_trigger_points: Profit threshold to move SL to breakeven
            timeframe: Candle timeframe ('1h', '2h', '4h', '1d', etc.)
            reset_interval_minutes: Reset interval in minutes
            timezone: Timezone for operations
            order_check_interval: Interval to check orders in seconds
            position_check_interval: Interval to check positions in seconds
            wait_for_next_candle: Wait for next candle before placing orders
            startup_delay_minutes: Delay in minutes after candle close before placing orders
        """
        self.client = client
        self.symbol = symbol
        self.product_id = product_id
        self.order_size = order_size
        self.stop_loss_points = stop_loss_points
        self.take_profit_points = take_profit_points
        self.breakeven_trigger_points = breakeven_trigger_points
        self.timeframe = timeframe
        self.reset_interval_minutes = reset_interval_minutes
        self.timezone = pytz.timezone(timezone)
        self.order_check_interval = order_check_interval
        self.position_check_interval = position_check_interval
        self.wait_for_next_candle = wait_for_next_candle
        self.startup_delay_minutes = startup_delay_minutes
        self.max_position_size = max_position_size or (order_size * 3)
        self.check_existing_orders = check_existing_orders
        
        # Trading state
        self.prev_period_high = None
        self.prev_period_low = None
        self.buy_order_id = None
        self.sell_order_id = None
        self.active_position = None
        self.entry_price = None
        self.position_side = None
        self.breakeven_applied = False
        self.stop_loss_order_id = None
        self.take_profit_order_id = None
        self.last_reset_time = None
        
        logger.info(f"Breakout bot initialized for {symbol} with {timeframe} timeframe")
        logger.info(f"Position size limits: order_size={order_size}, max_position_size={self.max_position_size}")
    
    def _recover_existing_position(self) -> bool:
        """
        Recover and monitor existing position when bot restarts
        
        This allows bot to continue monitoring a position even if it was stopped and restarted.
        
        Returns:
            True if existing position found and recovered, False otherwise
        """
        try:
            logger.info("🔍 Checking for existing open positions to recover...")
            
            positions = self.client.get_positions(product_id=self.product_id)
            
            if not isinstance(positions, list):
                logger.info("✅ No existing positions to recover")
                return False
            
            for position in positions:
                if not isinstance(position, dict):
                    continue
                
                if position.get('product_id') == self.product_id:
                    size = float(position.get('size', 0))
                    
                    if size != 0:
                        # Found existing position!
                        self.active_position = position
                        self.entry_price = float(position.get('entry_price', 0))
                        self.position_side = 'long' if size > 0 else 'short'
                        
                        logger.warning("=" * 60)
                        logger.warning("🔄 EXISTING POSITION RECOVERED!")
                        logger.warning("=" * 60)
                        logger.info(f"📊 Position Details:")
                        logger.info(f"   Side:        {self.position_side.upper()}")
                        logger.info(f"   Size:        {abs(size)} contracts")
                        logger.info(f"   Entry Price: {self.entry_price}")
                        logger.info(f"   Product:     {self.symbol}")
                        
                        # Check for existing SL/TP orders
                        self._recover_existing_orders()
                        
                        logger.warning("=" * 60)
                        logger.info("✅ Bot will now monitor this existing position")
                        logger.info("   - Calculating P&L every 5 seconds")
                        logger.info("   - Will apply breakeven if profit threshold reached")
                        logger.info("   - Monitoring for position close (SL/TP hit)")
                        logger.warning("=" * 60)
                        
                        return True
            
            logger.info("✅ No existing positions to recover")
            return False
            
        except Exception as e:
            logger.error(f"Error recovering existing position: {e}")
            return False
    
    def _recover_existing_orders(self):
        """
        Recover existing SL/TP orders for the recovered position
        """
        try:
            logger.info("🔍 Checking for existing SL/TP orders...")
            
            open_orders = self.client.get_open_orders(product_id=self.product_id)
            
            if not open_orders or not isinstance(open_orders, list):
                logger.warning("⚠️  No existing SL/TP orders found - position has no protection!")
                logger.info("💡 TIP: Manually set SL/TP on Delta Exchange dashboard for safety")
                return
            
            sl_found = False
            tp_found = False
            
            for order in open_orders:
                if not isinstance(order, dict):
                    continue
                
                order_id = order.get('id')
                order_type = order.get('order_type', '')
                side = order.get('side', '')
                limit_price = float(order.get('limit_price', 0))
                stop_price = order.get('stop_price')
                
                # Identify SL/TP orders
                if stop_price:
                    # This is a stop loss order
                    self.stop_loss_order_id = order_id
                    sl_found = True
                    logger.info(f"   ✅ Stop Loss recovered: Order #{order_id} @ {limit_price}")
                elif order_type == 'limit_order':
                    # This is likely a take profit order
                    self.take_profit_order_id = order_id
                    tp_found = True
                    logger.info(f"   ✅ Take Profit recovered: Order #{order_id} @ {limit_price}")
            
            if sl_found and tp_found:
                logger.info("✅ Both SL and TP orders recovered successfully")
            elif sl_found:
                logger.warning("⚠️  Only SL recovered - TP missing or already hit")
            elif tp_found:
                logger.warning("⚠️  Only TP recovered - SL missing (risky!)")
            else:
                logger.warning("⚠️  No SL/TP orders found - position unprotected!")
                logger.info("💡 TIP: Consider placing SL/TP manually for safety")
                
        except Exception as e:
            logger.error(f"Error recovering existing orders: {e}")
    
    def _check_existing_position_size(self) -> Tuple[bool, float]:
        """
        Check if there's an existing position and if it would exceed max size
        
        Returns:
            Tuple of (can_trade, current_position_size)
        """
        try:
            positions = self.client.get_positions(product_id=self.product_id)
            
            if not isinstance(positions, list):
                return True, 0
            
            for position in positions:
                if not isinstance(position, dict):
                    continue
                    
                if position.get('product_id') == self.product_id:
                    current_size = abs(float(position.get('size', 0)))
                    
                    if current_size > 0:
                        logger.info(f"📊 EXISTING POSITION DETECTED: {current_size} contracts")
                        
                        potential_size = current_size + self.order_size
                        
                        if potential_size > self.max_position_size:
                            logger.warning(
                                f"⚠️  POSITION SIZE LIMIT EXCEEDED! "
                                f"Current: {current_size}, Order: {self.order_size}, "
                                f"Potential: {potential_size}, Max: {self.max_position_size}"
                            )
                            logger.warning(
                                f"⛔ CANNOT PLACE NEW ORDERS - Would exceed maximum position size of {self.max_position_size}"
                            )
                            return False, current_size
                        else:
                            logger.info(
                                f"✅ Position size OK: Current {current_size} + Order {self.order_size} = "
                                f"{potential_size} (Max: {self.max_position_size})"
                            )
                            return True, current_size
                    
            return True, 0
            
        except Exception as e:
            logger.error(f"Error checking existing position: {e}")
            return True, 0  # Allow trading if check fails
    
    def _check_existing_orders(self) -> Tuple[bool, list]:
        """
        Check if there are already pending breakout orders
        
        Returns:
            Tuple of (has_orders, list_of_orders)
        """
        try:
            if not self.check_existing_orders:
                return False, []
            
            open_orders = self.client.get_open_orders(product_id=self.product_id)
            
            if not open_orders or not isinstance(open_orders, list):
                return False, []
            
            # Filter for breakout-type orders (those near our levels)
            breakout_orders = []
            for order in open_orders:
                if not isinstance(order, dict):
                    continue
                
                order_type = order.get('order_type', '')
                limit_price = float(order.get('limit_price', 0))
                side = order.get('side', '')
                order_id = order.get('id', '')
                
                # Check if this is likely a breakout order
                if order_type in ['limit_order', 'stop_loss_order']:
                    breakout_orders.append({
                        'id': order_id,
                        'side': side,
                        'price': limit_price,
                        'type': order_type
                    })
            
            if breakout_orders:
                logger.warning(f"⚠️  EXISTING ORDERS DETECTED: {len(breakout_orders)} open orders")
                for order in breakout_orders:
                    logger.info(
                        f"   📋 Order #{order['id']}: {order['side'].upper()} @ {order['price']} "
                        f"({order['type']})"
                    )
                logger.warning(
                    f"⛔ SKIPPING ORDER PLACEMENT - Bot already has active orders. "
                    f"If this is unexpected, cancel manually and restart."
                )
                return True, breakout_orders
            
            return False, []
            
        except Exception as e:
            logger.error(f"Error checking existing orders: {e}")
            return False, []  # Allow trading if check fails
    
    def calculate_previous_period_levels(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Calculate previous period's high and low from historical data
        
        Returns:
            Tuple of (previous_period_high, previous_period_low)
        """
        try:
            # Get historical candles (3x the timeframe to be safe)
            end_time = int(time.time())
            
            # Calculate start time based on timeframe
            timeframe_minutes = self._timeframe_to_minutes()
            start_time = end_time - (3 * timeframe_minutes * 60)
            
            candles = self.client.get_historical_candles(
                symbol=self.symbol,
                resolution=self.timeframe,
                start=start_time,
                end=end_time
            )
            
            if not candles or len(candles) < 2:
                logger.error("Insufficient candle data to calculate previous period levels")
                return None, None
            
            # Get the second-to-last candle (previous completed period)
            prev_period_candle = candles[-2]
            # | | |
            prev_high = float(prev_period_candle['high'])
            prev_low = float(prev_period_candle['low'])
            
            logger.info(f"Previous {self.timeframe} levels - High: {prev_high}, Low: {prev_low}")
            
            return prev_high, prev_low
            
        except Exception as e:
            logger.error(f"Error calculating previous period levels: {e}")
            return None, None
    
    def _timeframe_to_minutes(self) -> int:
        """Convert timeframe string to minutes"""
        timeframe_map = {
            '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '6h': 360,
            '1d': 1440, '1w': 10080
        }
        return timeframe_map.get(self.timeframe, 60)
    
    def place_breakout_orders(self) -> bool:
        """
        Place buy and sell STOP-LIMIT orders for breakout trading
        
        - Buy STOP above previous high (triggers on bullish breakout)
        - Sell STOP below previous low (triggers on bearish breakout)
        
        Checks:
        1. Current price to avoid immediate execution errors
        2. Existing orders to prevent duplicates
        3. Existing positions to prevent exceeding max size
        
        Returns:
            True if successful, False otherwise
        """
        if self.prev_period_high is None or self.prev_period_low is None:
            logger.error("❌ Previous period levels not set, cannot place orders")
            return False
        
        # ============================================================
        # SAFETY CHECK 1: Check for existing orders
        # ============================================================
        logger.info("🔍 Checking for existing orders...")
        has_existing_orders, existing_orders = self._check_existing_orders()
        
        if has_existing_orders:
            logger.warning(
                f"⛔ SKIPPING ORDER PLACEMENT: {len(existing_orders)} existing orders found"
            )
            logger.info(
                f"💡 TIP: If you want to place new orders, cancel existing ones first using Delta Exchange dashboard"
            )
            return False
        else:
            logger.info("✅ No existing orders found - safe to place new orders")
        
        # ============================================================
        # SAFETY CHECK 2: Check position size limits
        # ============================================================
        logger.info("🔍 Checking position size limits...")
        can_trade, current_position_size = self._check_existing_position_size()
        
        if not can_trade:
            logger.error(
                f"⛔ CANNOT PLACE ORDERS: Position size limit exceeded "
                f"(Current: {current_position_size}, Max: {self.max_position_size})"
            )
            logger.info(
                f"💡 TIP: Close existing position or increase max_position_size in config.yaml"
            )
            return False
        
        if current_position_size > 0:
            logger.info(
                f"⚠️  Note: You have existing position of {current_position_size} contracts. "
                f"New order will add {self.order_size} more."
            )
        else:
            logger.info("✅ No existing position - safe to place orders")
        
        try:
            # Get current price to check if we're already in a breakout
            ticker = self.client.get_ticker(self.symbol)
            if not ticker:
                logger.error("Failed to get current price")
                return False
            
            current_price = float(ticker.get('close', 0))
            logger.info(
                f"Current price: {current_price}, "
                f"Previous High: {self.prev_period_high}, "
                f"Previous Low: {self.prev_period_low}"
            )
            
            # Check if price is already outside the range (breakout already happened)
            if current_price >= self.prev_period_high:
                logger.warning(
                    f"Price {current_price} already above high {self.prev_period_high} - "
                    f"Bullish breakout already occurred! Skipping buy order."
                )
                # Could optionally enter position here
                return False
            
            if current_price <= self.prev_period_low:
                logger.warning(
                    f"Price {current_price} already below low {self.prev_period_low} - "
                    f"Bearish breakout already occurred! Skipping sell order."
                )
                # Could optionally enter position here
                return False
            
            # Price is between high and low - place both stop orders
            logger.info(f"Price is in range, placing breakout orders...")
            
            # Place BUY STOP-LIMIT order above previous period high
            # This triggers when price RISES ABOVE the high (bullish breakout)
            buy_order = self.client.place_limit_order(
                product_id=self.product_id,
                product_symbol=self.symbol,
                side='buy',
                size=self.order_size,
                limit_price=str(self.prev_period_high),
                stop_price=str(self.prev_period_high),  # Stop price triggers the order
                client_order_id=f"breakout_buy_{int(time.time())}"
            )
            
            if buy_order and buy_order.get('id'):
                self.buy_order_id = buy_order['id']
                logger.info(
                    f"Buy STOP order placed above {self.prev_period_high} "
                    f"(triggers on bullish breakout), ID: {self.buy_order_id}"
                )
            else:
                logger.error("Failed to place buy stop order")
                return False
            
            time.sleep(1)
            
            # Place SELL STOP-LIMIT order below previous period low  
            # This triggers when price FALLS BELOW the low (bearish breakout)
            sell_order = self.client.place_limit_order(
                product_id=self.product_id,
                product_symbol=self.symbol,
                side='sell',
                size=self.order_size,
                limit_price=str(self.prev_period_low),
                stop_price=str(self.prev_period_low),  # Stop price triggers the order
                client_order_id=f"breakout_sell_{int(time.time())}"
            )
            
            if sell_order and sell_order.get('id'):
                self.sell_order_id = sell_order['id']
                logger.info(
                    f"Sell STOP order placed below {self.prev_period_low} "
                    f"(triggers on bearish breakout), ID: {self.sell_order_id}"
                )
            else:
                logger.error("Failed to place sell stop order")
                if self.buy_order_id:
                    self.client.cancel_order(self.buy_order_id, self.product_id)
                return False
            
            logger.info("Both breakout orders placed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error placing breakout orders: {e}")
            return False
    
    def check_order_status(self) -> bool:
        """
        Check if any breakout order has been filled
        
        Returns:
            True if an order was filled, False otherwise
        """
        try:
            positions = self.client.get_positions(product_id=self.product_id)
            
            # Handle case where positions might not be a list
            if not isinstance(positions, list):
                logger.debug(f"Unexpected positions format: {type(positions)}")
                return False
            
            # Check if positions list is empty
            if not positions:
                return False
            
            for position in positions:
                # Ensure position is a dictionary
                if not isinstance(position, dict):
                    logger.warning(f"Position is not a dict: {type(position)} - {position}")
                    continue
                
                if position.get('product_id') == self.product_id:
                    size = float(position.get('size', 0))
                    
                    if size != 0 and self.active_position is None:
                        # Position opened
                        self.active_position = position
                        self.entry_price = float(position.get('entry_price', 0))
                        self.position_side = 'long' if size > 0 else 'short'
                        
                        logger.info(
                            f"Position opened: {self.position_side.upper()} "
                            f"{abs(size)} @ {self.entry_price}"
                        )
                        
                        # Cancel the opposite order
                        if self.position_side == 'long' and self.sell_order_id:
                            self.client.cancel_order(self.sell_order_id, self.product_id)
                            self.sell_order_id = None
                            logger.info("Sell order cancelled")
                        elif self.position_side == 'short' and self.buy_order_id:
                            self.client.cancel_order(self.buy_order_id, self.product_id)
                            self.buy_order_id = None
                            logger.info("Buy order cancelled")
                        
                        # Place stop loss and take profit orders
                        self._place_sl_tp_orders()
                        
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking order status: {e}", exc_info=True)
            return False
    
    def _place_sl_tp_orders(self):
        """Place stop loss and take profit orders for the active position"""
        if self.entry_price is None or self.position_side is None:
            logger.error("Cannot place SL/TP orders without entry price and position side")
            return
        
        try:
            if self.position_side == 'long':
                # For long position
                sl_price = self.entry_price - self.stop_loss_points
                tp_price = self.entry_price + self.take_profit_points
                
                # Place stop loss order (sell stop)
                sl_order = self.client.place_limit_order(
                    product_id=self.product_id,
                    product_symbol=self.symbol,
                    side='sell',
                    size=self.order_size,
                    limit_price=str(sl_price),
                    stop_price=str(sl_price),
                    client_order_id=f"sl_{int(time.time())}"
                )
                
                if sl_order and sl_order.get('id'):
                    self.stop_loss_order_id = sl_order['id']
                    logger.info(f"Stop loss order placed at {sl_price}, ID: {self.stop_loss_order_id}")
                
                time.sleep(1)
                
                # Place take profit order (sell limit)
                tp_order = self.client.place_limit_order(
                    product_id=self.product_id,
                    product_symbol=self.symbol,
                    side='sell',
                    size=self.order_size,
                    limit_price=str(tp_price),
                    client_order_id=f"tp_{int(time.time())}"
                )
                
                if tp_order and tp_order.get('id'):
                    self.take_profit_order_id = tp_order['id']
                    logger.info(f"Take profit order placed at {tp_price}, ID: {self.take_profit_order_id}")
                
            else:  # short position
                # For short position
                sl_price = self.entry_price + self.stop_loss_points
                tp_price = self.entry_price - self.take_profit_points
                
                # Place stop loss order (buy stop)
                sl_order = self.client.place_limit_order(
                    product_id=self.product_id,
                    product_symbol=self.symbol,
                    side='buy',
                    size=self.order_size,
                    limit_price=str(sl_price),
                    stop_price=str(sl_price),
                    client_order_id=f"sl_{int(time.time())}"
                )
                
                if sl_order and sl_order.get('id'):
                    self.stop_loss_order_id = sl_order['id']
                    logger.info(f"Stop loss order placed at {sl_price}, ID: {self.stop_loss_order_id}")
                
                time.sleep(1)
                
                # Place take profit order (buy limit)
                tp_order = self.client.place_limit_order(
                    product_id=self.product_id,
                    product_symbol=self.symbol,
                    side='buy',
                    size=self.order_size,
                    limit_price=str(tp_price),
                    client_order_id=f"tp_{int(time.time())}"
                )
                
                if tp_order and tp_order.get('id'):
                    self.take_profit_order_id = tp_order['id']
                    logger.info(f"Take profit order placed at {tp_price}, ID: {self.take_profit_order_id}")
                    
        except Exception as e:
            logger.error(f"Error placing SL/TP orders: {e}")
    
    def monitor_position_and_apply_breakeven(self):
        """
        Monitor active position and apply breakeven logic when profit threshold is reached
        """
        if self.active_position is None or self.breakeven_applied:
            return
        
        try:
            # Get current price
            ticker = self.client.get_ticker(self.symbol)
            if not ticker:
                return
            
            current_price = float(ticker.get('close', 0))
            
            # Calculate profit in points
            if self.position_side == 'long':
                profit_points = current_price - self.entry_price
            else:  # short
                profit_points = self.entry_price - current_price
            
            logger.debug(
                f"Position monitor - Current: {current_price}, "
                f"Entry: {self.entry_price}, Profit: {profit_points:.2f} points"
            )
            
            # Check if breakeven trigger is reached
            if profit_points >= self.breakeven_trigger_points:
                logger.info(
                    f"Breakeven trigger reached! Profit: {profit_points:.2f} points "
                    f"(threshold: {self.breakeven_trigger_points})"
                )
                
                # Move stop loss to entry price (breakeven)
                if self.stop_loss_order_id:
                    result = self.client.edit_order(
                        order_id=self.stop_loss_order_id,
                        product_id=self.product_id,
                        stop_price=str(self.entry_price),
                        limit_price=str(self.entry_price)
                    )
                    
                    # edit_order returns a dict, check if it has an 'id' field to confirm success
                    if result and result.get('id'):
                        self.breakeven_applied = True
                        logger.info(f"Stop loss moved to breakeven: {self.entry_price}")
                    else:
                        logger.error("Failed to move stop loss to breakeven")
                else:
                    logger.warning("No stop loss order ID found to edit")
                    
        except Exception as e:
            logger.error(f"Error monitoring position: {e}")
    
    def check_position_closed(self) -> bool:
        """
        Check if the active position has been closed
        
        Returns:
            True if position is closed, False otherwise
        """
        if self.active_position is None:
            return False
        
        try:
            positions = self.client.get_positions(product_id=self.product_id)
            
            for position in positions:
                if position.get('product_id') == self.product_id:
                    size = float(position.get('size', 0))
                    
                    if size == 0:
                        # Position closed
                        logger.info("Position closed")
                        self._reset_position_state()
                        return True
            
            # If no position found, it's closed
            if not positions or all(p.get('product_id') != self.product_id for p in positions):
                logger.info("Position closed (not found in positions)")
                self._reset_position_state()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking position status: {e}")
            return False
    
    def _reset_position_state(self):
        """Reset position-related state variables"""
        self.active_position = None
        self.entry_price = None
        self.position_side = None
        self.breakeven_applied = False
        self.stop_loss_order_id = None
        self.take_profit_order_id = None
        logger.info("Position state reset")
    
    def should_reset(self) -> bool:
        """
        Check if it's time for periodic reset based on interval
        
        Returns:
            True if it's reset time, False otherwise
        """
        try:
            now = datetime.now(self.timezone)
            
            # Initialize last reset time if not set
            if self.last_reset_time is None:
                self.last_reset_time = now
                return False
            
            # Calculate time since last reset
            time_since_reset = (now - self.last_reset_time).total_seconds() / 60  # in minutes
            
            # Check if reset interval has passed
            if time_since_reset >= self.reset_interval_minutes:
                logger.info(f"Reset interval reached: {time_since_reset:.1f} minutes")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking reset time: {e}")
            return False
    
    def perform_reset(self):
        """Perform periodic reset: cancel orders, reset state, calculate new levels"""
        logger.info(f"Performing {self.timeframe} reset...")
        
        try:
            # Cancel all open orders
            self.client.cancel_all_orders(product_id=self.product_id)
            
            # Reset order IDs
            self.buy_order_id = None
            self.sell_order_id = None
            
            # Reset position state
            self._reset_position_state()
            
            # Calculate new previous period levels
            self.prev_period_high, self.prev_period_low = self.calculate_previous_period_levels()
            
            if self.prev_period_high and self.prev_period_low:
                # Try to place new breakout orders
                order_result = self.place_breakout_orders()
                
                if order_result:
                    logger.info("Reset completed successfully - new orders placed")
                else:
                    logger.warning(
                        f"Reset completed but could not place orders "
                        f"(breakout may have already occurred). "
                        f"Will retry at next reset in {self.reset_interval_minutes} minutes."
                    )
                
                # Update last reset time regardless
                self.last_reset_time = datetime.now(self.timezone)
            else:
                logger.error("Failed to calculate new levels during reset")
                
        except Exception as e:
            logger.error(f"Error during reset: {e}")
    
    def _wait_for_next_candle_if_configured(self):
        """
        Wait for next candle if configured, plus any startup delay
        """
        if not self.wait_for_next_candle:
            # No delay configured
            return
        
        try:
            # Get current candles to determine when next candle starts
            end_time = int(time.time())
            timeframe_seconds = self._timeframe_to_minutes() * 60
            start_time = end_time - (2 * timeframe_seconds)
            
            candles = self.client.get_historical_candles(
                symbol=self.symbol,
                resolution=self.timeframe,
                start=start_time,
                end=end_time
            )
            
            if candles and len(candles) > 0:
                # Get the last candle close time
                last_candle = candles[-1]
                last_candle_time = int(last_candle['time'])
                
                # Calculate when next candle closes
                next_candle_close = last_candle_time + timeframe_seconds
                
                # Add startup delay
                target_time = next_candle_close + (self.startup_delay_minutes * 60)
                
                current_time = int(time.time())
                wait_seconds = target_time - current_time
                
                if wait_seconds > 0:
                    wait_minutes = wait_seconds / 60
                    next_time_str = datetime.fromtimestamp(target_time, self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')
                    
                    logger.info(
                        f"⏰ Configured to wait for next {self.timeframe} candle + {self.startup_delay_minutes} min delay"
                    )
                    logger.info(f"⏰ Current time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
                    logger.info(f"⏰ Will place orders at: {next_time_str}")
                    logger.info(f"⏰ Waiting {wait_minutes:.1f} minutes...")
                    
                    # Wait in chunks to allow for interruption
                    waited = 0
                    while waited < wait_seconds:
                        chunk = min(60, wait_seconds - waited)  # Wait in 1-minute chunks
                        time.sleep(chunk)
                        waited += chunk
                        
                        remaining = wait_seconds - waited
                        if remaining > 60:
                            logger.info(f"⏰ Still waiting... {remaining/60:.1f} minutes remaining")
                    
                    logger.info(f"✅ Wait complete! Proceeding to place orders...")
                else:
                    logger.info("✅ Next candle already started, proceeding immediately")
            
        except Exception as e:
            logger.error(f"Error calculating wait time: {e}")
            logger.warning("Proceeding without delay")
    
    def run(self):
        """Main bot loop with position recovery on restart"""
        logger.info(f"Starting {self.timeframe} Breakout Trading Bot")
        
        # ============================================================
        # CRITICAL: Check for existing position to recover
        # ============================================================
        # This is crucial for bot restarts - allows monitoring existing trades
        logger.info("")
        logger.info("=" * 60)
        logger.info("STEP 1: POSITION RECOVERY CHECK")
        logger.info("=" * 60)
        
        existing_position_found = self._recover_existing_position()
        
        if existing_position_found:
            # Position recovered! Skip order placement, go directly to monitoring
            logger.info("")
            logger.info("🔄 Recovered existing position - skipping order placement")
            logger.info("   Bot will continue monitoring the existing position")
            logger.info("")
            
            # Set initial reset time
            self.last_reset_time = datetime.now(self.timezone)
            
            # Go directly to main loop to monitor the recovered position
            logger.info("Entering main loop (monitoring recovered position)...")
            
        else:
            # No existing position - normal startup flow
            logger.info("")
            logger.info("=" * 60)
            logger.info("STEP 2: CALCULATE LEVELS & PLACE ORDERS")
            logger.info("=" * 60)
            
            # Initial setup: calculate levels
            self.prev_period_high, self.prev_period_low = self.calculate_previous_period_levels()
            
            if not self.prev_period_high or not self.prev_period_low:
                logger.error("Failed to calculate initial levels, exiting")
                return
            
            # Wait for next candle if configured
            self._wait_for_next_candle_if_configured()
            
            # Try to place initial orders
            # If it fails (e.g., breakout already happened), don't exit - wait for next reset
            initial_order_result = self.place_breakout_orders()
            if not initial_order_result:
                logger.warning(
                    f"Could not place initial orders (breakout may have already occurred or already exist). "
                    f"Will retry at next reset in {self.reset_interval_minutes} minutes."
                )
            else:
                logger.info("Initial orders placed successfully")
            
            # Set initial reset time
            self.last_reset_time = datetime.now(self.timezone)
            
            logger.info("")
            logger.info("Entering main loop (waiting for breakout)...")
        
        try:
            last_order_check = 0
            last_position_check = 0
            last_reset_check = 0
            
            while True:
                current_time = time.time()
                
                # Check for periodic reset (check every minute)
                if current_time - last_reset_check >= 60:
                    if self.should_reset():
                        self.perform_reset()
                    last_reset_check = current_time
                
                # Check order status if no active position
                if self.active_position is None:
                    if current_time - last_order_check >= self.order_check_interval:
                        self.check_order_status()
                        last_order_check = current_time
                
                # Monitor position if active
                if self.active_position is not None:
                    if current_time - last_position_check >= self.position_check_interval:
                        self.monitor_position_and_apply_breakeven()
                        self.check_position_closed()
                        last_position_check = current_time
                
                # Sleep to prevent excessive API calls
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self._cleanup()
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup on shutdown"""
        logger.info("Performing cleanup...")
        try:
            # Optionally cancel all orders (uncomment if desired)
            # self.client.cancel_all_orders(product_id=self.product_id)
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

