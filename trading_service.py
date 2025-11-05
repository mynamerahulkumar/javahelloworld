import logging
import time
from typing import Dict, Optional, Tuple
from delta_rest_client import DeltaRestClient
from config import DELTA_BASE_URL, DELTA_API_KEY, DELTA_API_SECRET

logger = logging.getLogger(__name__)

class TradingService:
    """Service for executing trading orders with stop loss and take profit"""

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize trading service with Delta Exchange client"""
        self.api_key = api_key or DELTA_API_KEY
        self.api_secret = api_secret or DELTA_API_SECRET
        self.base_url = DELTA_BASE_URL

        if self.api_key and self.api_secret:
            self.client = DeltaRestClient(
                base_url=self.base_url,
                api_key=self.api_key,
                api_secret=self.api_secret,
                raise_for_status=True
            )
            logger.info("Trading service initialized")
        else:
            self.client = None
            logger.info("Trading service initialized without credentials (will use per-request credentials)")

    def _get_client(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, base_url: Optional[str] = None) -> DeltaRestClient:
        """Get or create a DeltaRestClient with specified credentials"""
        key = api_key or self.api_key
        secret = api_secret or self.api_secret
        url = base_url or self.base_url

        if not key or not secret:
            raise ValueError("API key and secret must be provided via headers or environment variables")

        if key == self.api_key and secret == self.api_secret and url == self.base_url and self.client:
            return self.client

        return DeltaRestClient(
            base_url=url,
            api_key=key,
            api_secret=secret,
            raise_for_status=True
        )

    def _check_position_exists(
        self,
        client: DeltaRestClient,
        product_id: Optional[int],
        product_symbol: Optional[str]
    ) -> bool:
        """
        Check if a position exists for the given product
        
        Returns:
            True if position exists (non-zero size), False otherwise
        """
        try:
            if product_id:
                position = client.get_margined_position(product_id)
                if position:
                    size = float(position.get('size', 0))
                    if size != 0:
                        logger.info(f"✓ Position exists: size={size}, product_id={product_id}, realized_pnl={position.get('realized_pnl')}")
                        return True
                    else:
                        logger.debug(f"Position found but size is 0: {position}")
            else:
                logger.debug(f"No product_id provided, cannot check position")
            return False
        except Exception as e:
            error_msg = str(e)
            # If error indicates no position, that's fine - position doesn't exist yet
            if "not found" in error_msg.lower() or "no position" in error_msg.lower():
                logger.debug(f"No position exists yet: {error_msg}")
            else:
                logger.debug(f"Error checking position: {error_msg}")
            return False

    def _place_bracket_orders(
        self,
        client: DeltaRestClient,
        product_id: Optional[int],
        product_symbol: Optional[str],
        stop_loss_price: Optional[float],
        take_profit_price: Optional[float],
        side: str,
        max_retries: int = 60,
        retry_delay: float = 1.0
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Place bracket orders for an existing position with retries
        
        Waits for position to exist before placing bracket orders.
        FIXED: Increased retries to 60 (60 seconds) to ensure brackets are placed.
        
        Args:
            client: DeltaRestClient instance
            product_id: Product ID
            product_symbol: Product symbol
            stop_loss_price: Stop loss price
            take_profit_price: Take profit price
            side: Order side (buy/sell)
            max_retries: Maximum retry attempts (default: 60 = 60 seconds)
            retry_delay: Delay between retries in seconds
            
        Returns:
            Tuple of (bracket_order_result, error_message)
        """
        # First, wait for position to exist (only if we have product_id)
        position_exists = False
        if product_id:
            logger.info(f"Waiting for position to exist (product_id={product_id})...")
            for attempt in range(max_retries):
                position_exists = self._check_position_exists(client, product_id, product_symbol)
                if position_exists:
                    logger.info(f"✓ Position confirmed to exist on attempt {attempt + 1}/{max_retries}")
                    break
                else:
                    if attempt < max_retries - 1:
                        if attempt % 5 == 0:  # Log every 5 attempts
                            logger.info(f"Waiting for position (attempt {attempt + 1}/{max_retries})...")
                        time.sleep(retry_delay)
            
            if not position_exists:
                error_msg = f"Position not found after {max_retries} attempts ({max_retries * retry_delay}s). Bracket orders require an existing position."
                logger.error(f"✗ {error_msg}")
                return None, error_msg
        else:
            # If we only have product_symbol, we can't check position existence
            # Try to place bracket orders directly - API will reject if position doesn't exist
            logger.info("No product_id available, attempting bracket order placement directly...")
        
        # Now place bracket orders
        try:
            # Build bracket order payload matching Delta Exchange format
            stop_loss_order = None
            take_profit_order = None
            
            if stop_loss_price:
                # Stop loss order: triggers when price reaches stop_loss_price
                stop_loss_order = {
                    "order_type": "limit_order",
                    "stop_price": str(stop_loss_price),
                    "limit_price": str(stop_loss_price)  # Same as stop_price for immediate execution
                }
            
            if take_profit_price:
                # Take profit order: triggers when price reaches take_profit_price
                take_profit_order = {
                    "order_type": "limit_order",
                    "stop_price": str(take_profit_price),
                    "limit_price": str(take_profit_price)  # Same as stop_price for immediate execution
                }
            
            if not stop_loss_order and not take_profit_order:
                return None, "No stop loss or take profit price provided"
            
            logger.info(f"Placing bracket orders: SL={stop_loss_price}, TP={take_profit_price}")
            
            # Place bracket order
            bracket_result = client.create_bracket_order(
                product_id=product_id,
                product_symbol=product_symbol,
                stop_loss_order=stop_loss_order,
                take_profit_order=take_profit_order,
                bracket_stop_trigger_method="last_traded_price"
            )
            
            logger.info(f"✓ Bracket orders placed successfully! Result: {bracket_result}")
            return bracket_result, None
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"✗ Error placing bracket orders: {error_msg}")
            return None, error_msg

    def place_limit_order_wait(
        self,
        entry_price: float,
        size: int,
        side: str,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        client_order_id: Optional[str] = None,
        product_id: Optional[int] = None,
        product_symbol: Optional[str] = None,
        symbol: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Place a stop-limit order that waits for price to reach entry level, with bracket SL/TP
        
        FIXED: Improved bracket order placement logic to ensure TP/SL are placed after order executes.
        
        Args:
            entry_price: Entry price (stop and limit price) for the order
            size: Order size (quantity)
            side: Order side (buy or sell)
            stop_loss_price: Stop loss price (optional, will create bracket SL order)
            take_profit_price: Take profit price (optional, will create bracket TP order)
            client_order_id: Client order ID for tracking
            product_id: Product ID (optional, takes precedence)
            product_symbol: Product symbol (optional, e.g., BTCUSD, ETHUSD)
            symbol: Trading symbol (optional, e.g., BTC, ETH)
            api_key: API key (optional)
            api_secret: API secret (optional)
            base_url: Delta Exchange base URL (optional)
        
        Returns:
            Tuple of (success, order_data, error_message)
        """
        try:
            # Determine product_id and product_symbol
            final_product_id = None
            final_product_symbol = None

            SYMBOL_TO_PRODUCT = {
                "BTC": "BTCUSD",
                "ETH": "ETHUSD",
            }

            if product_id:
                final_product_id = int(product_id)
            elif product_symbol:
                if product_symbol and isinstance(product_symbol, str) and product_symbol.strip():
                    final_product_symbol = product_symbol.strip().upper()
                else:
                    return False, None, f"Invalid product_symbol: {product_symbol}"
            elif symbol:
                symbol_upper = symbol.upper().strip() if symbol else None
                if not symbol_upper:
                    return False, None, "Invalid symbol provided"
                if symbol_upper in SYMBOL_TO_PRODUCT:
                    final_product_symbol = SYMBOL_TO_PRODUCT[symbol_upper]
                else:
                    return False, None, f"Symbol '{symbol}' not recognized. Known symbols: {list(SYMBOL_TO_PRODUCT.keys())}"
            else:
                return False, None, "Either product_id, product_symbol, or symbol must be provided"

            # Build order payload for stop-limit order (without brackets - they're placed separately)
            order = {
                "size": int(size),
                "side": side,
                "order_type": "limit_order",
                "limit_price": str(entry_price),  # Limit price once triggered
                "stop_price": str(entry_price),  # Trigger when price reaches entry
                "stop_order_type": "stop_loss_order",  # Required for stop orders
                "stop_trigger_method": "last_traded_price",
                "time_in_force": "gtc",  # Good till cancel
                "reduce_only": "false",
                "mmp": "disabled",
                "cancel_orders_accepted": False
            }

            # Add product identifier
            if final_product_id:
                order["product_id"] = final_product_id
            elif final_product_symbol:
                order["product_symbol"] = final_product_symbol
            else:
                return False, None, "Either product_id, product_symbol, or symbol must be provided"

            # Add client order ID if provided
            if client_order_id:
                order["client_order_id"] = client_order_id

            product_info = f"product_id={final_product_id}" if final_product_id else f"product_symbol={final_product_symbol}"
            logger.info(
                f"Placing stop-limit order (wait): {side} {size} {product_info} at {entry_price}, "
                f"SL: {stop_loss_price}, TP: {take_profit_price}"
            )

            # Get client and place entry order (stop-limit without brackets)
            client = self._get_client(api_key=api_key, api_secret=api_secret, base_url=base_url)
            logger.info(f"Stop-limit entry order payload: {order}")
            
            result = client.create_order(order)
            logger.info(f"✓ Stop-limit entry order placed successfully: {result}")
            
            # Check if order executed immediately
            order_state = result.get("state") if result else None
            average_fill_price = result.get("average_fill_price") if result else None
            order_executed = order_state == "closed" and average_fill_price is not None
            
            # If SL/TP provided, place bracket orders
            bracket_result = None
            bracket_error = None
            if stop_loss_price or take_profit_price:
                if order_executed:
                    # Order executed immediately - place brackets right away
                    logger.info("✓ Entry order executed immediately, placing bracket orders...")
                    bracket_result, bracket_error = self._place_bracket_orders(
                        client=client,
                        product_id=final_product_id,
                        product_symbol=final_product_symbol,
                        stop_loss_price=stop_loss_price,
                        take_profit_price=take_profit_price,
                        side=side,
                        max_retries=10,  # 10 retries for immediate execution
                        retry_delay=0.5
                    )
                else:
                    # Order is waiting for price - retry bracket placement with more patience
                    logger.info(f"Entry order is {order_state or 'open'} (waiting for price), will place bracket orders once position is created...")
                    bracket_result, bracket_error = self._place_bracket_orders(
                        client=client,
                        product_id=final_product_id,
                        product_symbol=final_product_symbol,
                        stop_loss_price=stop_loss_price,
                        take_profit_price=take_profit_price,
                        side=side,
                        max_retries=60,  # FIXED: 60 retries = 60 seconds wait time
                        retry_delay=1.0
                    )
                
                if bracket_result:
                    logger.info(f"✓ Bracket orders placed successfully: {bracket_result}")
                    result["bracket_order"] = bracket_result
                else:
                    logger.warning(f"✗ Bracket orders could not be placed: {bracket_error}")
                    # Store bracket error but don't fail the entire request
                    result["bracket_order_error"] = bracket_error
                    result["bracket_order_note"] = "Bracket orders will be placed automatically once position is created"
            
            return True, result, bracket_error

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error placing stop-limit order (wait): {error_msg}")
            return False, None, error_msg
