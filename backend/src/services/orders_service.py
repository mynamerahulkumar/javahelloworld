"""
Orders Service - Single Responsibility: Handle all order-related operations
"""
import logging
from typing import List, Dict, Any, Optional
from delta_rest_client import DeltaRestClient

logger = logging.getLogger(__name__)


class OrdersService:
    """Service for managing trading orders"""

    @staticmethod
    def get_order_history(
        api_key: str,
        api_secret: str,
        base_url: str = "https://api.india.delta.exchange",
        page_size: int = 100,
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch order history for the given API credentials.
        
        Args:
            api_key: Delta Exchange API key (from client, never stored on server)
            api_secret: Delta Exchange API secret (from client, never stored on server)
            base_url: Delta Exchange base URL (default: India production)
            page_size: Number of orders to fetch per page (default: 100)
            after: Pagination cursor (optional)
        
        Returns:
            Dictionary with 'result' (list of orders) and 'meta' (pagination info)
        
        Raises:
            ValueError: If credentials are missing
            Exception: If API call fails
        """
        if not api_key or not api_secret:
            raise ValueError("API key and secret must be provided (client-side only, never stored on server)")
        
        try:
            client = DeltaRestClient(
                base_url=base_url,
                api_key=api_key,
                api_secret=api_secret,
                raise_for_status=True
            )
            
            query = {}
            if after:
                query['after'] = after
            
            order_history = client.order_history(query=query, page_size=page_size, after=after)
            
            # order_history returns a dict with 'result' and 'meta' keys
            logger.info(f"Fetched order history: {len(order_history.get('result', []))} orders")
            return order_history
        
        except Exception as e:
            logger.error(f"Error fetching order history: {e}")
            raise

    @staticmethod
    def get_active_orders(
        api_key: str,
        api_secret: str,
        base_url: str = "https://api.india.delta.exchange"
    ) -> List[Dict[str, Any]]:
        """
        Fetch active/live orders for the given API credentials.
        
        Args:
            api_key: Delta Exchange API key (from client, never stored on server)
            api_secret: Delta Exchange API secret (from client, never stored on server)
            base_url: Delta Exchange base URL (default: India production)
        
        Returns:
            List of active order dictionaries
        
        Raises:
            ValueError: If credentials are missing
            Exception: If API call fails
        """
        if not api_key or not api_secret:
            raise ValueError("API key and secret must be provided (client-side only, never stored on server)")
        
        try:
            client = DeltaRestClient(
                base_url=base_url,
                api_key=api_key,
                api_secret=api_secret,
                raise_for_status=True
            )
            
            live_orders = client.get_live_orders(query=None)
            logger.info(f"Fetched {len(live_orders)} active orders")
            return live_orders if live_orders else []
        
        except Exception as e:
            logger.error(f"Error fetching active orders: {e}")
            raise

    @staticmethod
    def get_trade_history(
        api_key: str,
        api_secret: str,
        base_url: str = "https://api.india.delta.exchange",
        page_size: int = 100,
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch trade history (fills) for the given API credentials.
        
        Args:
            api_key: Delta Exchange API key (from client, never stored on server)
            api_secret: Delta Exchange API secret (from client, never stored on server)
            base_url: Delta Exchange base URL (default: India production)
            page_size: Number of trades to fetch per page (default: 100)
            after: Pagination cursor (optional)
        
        Returns:
            Dictionary with 'result' (list of fills/trades) and 'meta' (pagination info)
        
        Raises:
            ValueError: If credentials are missing
            Exception: If API call fails
        """
        if not api_key or not api_secret:
            raise ValueError("API key and secret must be provided (client-side only, never stored on server)")
        
        try:
            client = DeltaRestClient(
                base_url=base_url,
                api_key=api_key,
                api_secret=api_secret,
                raise_for_status=True
            )
            
            query = {}
            if after:
                query['after'] = after
            
            trade_history = client.fills(query=query, page_size=page_size, after=after)
            
            # fills returns a dict with 'result' and 'meta' keys
            logger.info(f"Fetched trade history: {len(trade_history.get('result', []))} trades")
            return trade_history
        
        except Exception as e:
            logger.error(f"Error fetching trade history: {e}")
            raise

