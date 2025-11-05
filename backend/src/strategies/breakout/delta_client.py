"""Delta Exchange API client wrapper for trading operations"""

import time
import hmac
import hashlib
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DeltaExchangeClient:
    """Delta Exchange API client with authentication and trading operations"""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        """
        Initialize Delta Exchange client
        
        Args:
            api_key: API key for authentication
            api_secret: API secret for signature generation
            base_url: Base URL for API endpoints
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()
        
        logger.info(f"Delta Exchange client initialized with base URL: {base_url}")
    
    def _generate_signature(self, message: str) -> str:
        """
        Generate HMAC SHA256 signature for API authentication
        
        Args:
            message: Message string to sign
            
        Returns:
            Hex-encoded signature
        """
        message_bytes = bytes(message, 'utf-8')
        secret_bytes = bytes(self.api_secret, 'utf-8')
        hash_obj = hmac.new(secret_bytes, message_bytes, hashlib.sha256)
        return hash_obj.hexdigest()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in seconds"""
        return str(int(time.time()))
    
    def _build_query_string(self, params: Optional[Dict] = None) -> str:
        """
        Build query string from parameters
        
        Args:
            params: Dictionary of query parameters
            
        Returns:
            Query string with '?' prefix or empty string
        """
        if not params:
            return ''
        
        query_parts = []
        for key, value in params.items():
            query_parts.append(f"{key}={value}")
        
        return '?' + '&'.join(query_parts)
    
    def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        auth: bool = True
    ) -> Dict[str, Any]:
        """
        Make authenticated API request
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            params: Query parameters
            data: Request body data
            auth: Whether to authenticate request
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}{path}"
        timestamp = self._get_timestamp()
        query_string = self._build_query_string(params)
        
        # Prepare payload
        payload = ''
        if data:
            payload = json.dumps(data, separators=(',', ':'))
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'breakout-trading-bot/1.0'
        }
        
        # Add authentication headers if required
        if auth:
            signature_data = method + timestamp + path + query_string + payload
            signature = self._generate_signature(signature_data)
            
            headers.update({
                'api-key': self.api_key,
                'timestamp': timestamp,
                'signature': signature
            })
        
        try:
            logger.debug(f"Request: {method} {url} params={params}")
            
            if method == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, data=payload, headers=headers, timeout=30)
            elif method == 'PUT':
                response = self.session.put(url, data=payload, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = self.session.delete(url, data=payload, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            logger.debug(f"Response: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_body = e.response.json()
                    logger.error(f"Error response: {error_body}")
                    return {'success': False, 'error': error_body}
                except:
                    logger.error(f"Error response text: {e.response.text}")
            return {'success': False, 'error': str(e)}
    
    def get_historical_candles(
        self,
        symbol: str,
        resolution: str = '1d',
        start: Optional[int] = None,
        end: Optional[int] = None
    ) -> List[Dict]:
        """
        Get historical OHLC candle data
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSD')
            resolution: Candle resolution ('1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '1d', '1w', '2w', '7d', '30d')
            start: Start timestamp in seconds (optional)
            end: End timestamp in seconds (optional)
            
        Returns:
            List of candle dictionaries
        """
        if start is None:
            # Default to last 7 days
            end = int(time.time())
            start = end - (7 * 24 * 3600)
        elif end is None:
            end = int(time.time())
        
        params = {
            'symbol': symbol,
            'resolution': resolution,
            'start': start,
            'end': end
        }
        
        response = self._make_request('GET', '/v2/history/candles', params=params, auth=False)
        
        if response.get('success'):
            candles = response.get('result', [])
            logger.info(f"Fetched {len(candles)} candles for {symbol}")
            return candles
        else:
            logger.error(f"Failed to fetch candles: {response}")
            return []
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        Get current ticker data for a symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Ticker data dictionary
        """
        response = self._make_request('GET', f'/v2/tickers/{symbol}', auth=False)
        
        if response.get('success'):
            return response.get('result', {})
        else:
            logger.error(f"Failed to get ticker: {response}")
            return {}
    
    def place_limit_order(
        self,
        product_id: int,
        product_symbol: str,
        side: str,
        size: int,
        limit_price: str,
        stop_price: Optional[str] = None,
        client_order_id: Optional[str] = None
    ) -> Dict:
        """
        Place a limit order
        
        Args:
            product_id: Product ID
            product_symbol: Product symbol
            side: Order side ('buy' or 'sell')
            size: Order size
            limit_price: Limit price as string
            stop_price: Stop price for stop-loss orders (optional)
            client_order_id: Client-defined order ID (optional)
            
        Returns:
            Order response dictionary
        """
        order_data = {
            'product_id': product_id,
            'product_symbol': product_symbol,
            'side': side,
            'size': size,
            'order_type': 'limit_order',
            'limit_price': limit_price,
            'time_in_force': 'gtc',
            'post_only': False
        }
        
        if stop_price:
            order_data['stop_price'] = stop_price
            order_data['stop_order_type'] = 'stop_loss_order'
        
        if client_order_id:
            order_data['client_order_id'] = client_order_id
        
        response = self._make_request('POST', '/v2/orders', data=order_data)
        
        if response.get('success'):
            order = response.get('result', {})
            logger.info(f"Order placed: {side} {size} @ {limit_price}, Order ID: {order.get('id')}")
            return order
        else:
            logger.error(f"Failed to place order: {response}")
            return {}
    
    def edit_order(
        self,
        order_id: int,
        product_id: int,
        limit_price: Optional[str] = None,
        size: Optional[int] = None,
        stop_price: Optional[str] = None
    ) -> Dict:
        """
        Edit an existing order
        
        Args:
            order_id: Order ID to edit
            product_id: Product ID
            limit_price: New limit price (optional)
            size: New size (optional)
            stop_price: New stop price (optional)
            
        Returns:
            Updated order dictionary
        """
        edit_data = {
            'id': order_id,
            'product_id': product_id
        }
        
        if limit_price is not None:
            edit_data['limit_price'] = limit_price
        
        if size is not None:
            edit_data['size'] = size
        
        if stop_price is not None:
            edit_data['stop_price'] = stop_price
        
        response = self._make_request('PUT', '/v2/orders', data=edit_data)
        
        if response.get('success'):
            order = response.get('result', {})
            logger.info(f"Order edited: Order ID: {order_id}")
            return order
        else:
            logger.error(f"Failed to edit order: {response}")
            return {}
    
    def get_open_orders(self, product_id: Optional[int] = None) -> List[Dict]:
        """
        Get open orders
        
        Args:
            product_id: Filter by product ID (optional)
            
        Returns:
            List of open orders
        """
        params = {'state': 'open'}
        if product_id:
            params['product_id'] = product_id
        
        response = self._make_request('GET', '/v2/orders', params=params)
        
        if response.get('success'):
            orders = response.get('result', [])
            logger.debug(f"Fetched {len(orders)} open orders")
            return orders
        else:
            logger.error(f"Failed to get open orders: {response}")
            return []
    
    def get_positions(self, product_id: Optional[int] = None) -> List[Dict]:
        """
        Get current positions
        
        Args:
            product_id: Filter by product ID (optional)
            
        Returns:
            List of positions
        """
        params = {}
        if product_id:
            params['product_id'] = product_id
        
        response = self._make_request('GET', '/v2/positions', params=params)
        
        if response.get('success'):
            result = response.get('result', [])
            
            # Handle case where result might be a single dict instead of list
            if isinstance(result, dict):
                logger.debug(f"Single position returned, converting to list")
                return [result] if result else []
            elif isinstance(result, list):
                logger.debug(f"Fetched {len(result)} positions")
                return result
            else:
                logger.warning(f"Unexpected result type: {type(result)}")
                return []
        else:
            logger.error(f"Failed to get positions: {response}")
            return []
    
    def cancel_order(self, order_id: int, product_id: int) -> bool:
        """
        Cancel a specific order
        
        Args:
            order_id: Order ID to cancel
            product_id: Product ID
            
        Returns:
            True if successful, False otherwise
        """
        cancel_data = {
            'id': order_id,
            'product_id': product_id
        }
        
        response = self._make_request('DELETE', '/v2/orders', data=cancel_data)
        
        if response.get('success'):
            logger.info(f"Order cancelled: Order ID: {order_id}")
            return True
        else:
            logger.error(f"Failed to cancel order: {response}")
            return False
    
    def cancel_all_orders(self, product_id: Optional[int] = None) -> bool:
        """
        Cancel all open orders
        
        Args:
            product_id: Filter by product ID (optional)
            
        Returns:
            True if successful, False otherwise
        """
        cancel_data = {}
        if product_id:
            cancel_data['product_id'] = product_id
        
        response = self._make_request('DELETE', '/v2/orders/all', data=cancel_data)
        
        if response.get('success'):
            logger.info("All orders cancelled")
            return True
        else:
            logger.error(f"Failed to cancel all orders: {response}")
            return False
    
    def get_product_info(self, product_id: int) -> Dict:
        """
        Get product information
        
        Args:
            product_id: Product ID
            
        Returns:
            Product information dictionary
        """
        response = self._make_request('GET', f'/v2/products/{product_id}', auth=False)
        
        if response.get('success'):
            return response.get('result', {})
        else:
            logger.error(f"Failed to get product info: {response}")
            return {}

