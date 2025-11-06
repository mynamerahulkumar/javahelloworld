"""
Positions Service - Single Responsibility: Handle all position-related operations
"""
import logging
from typing import List, Dict, Any, Optional
from delta_rest_client import DeltaRestClient

logger = logging.getLogger(__name__)


class PositionsService:
    """Service for managing trading positions"""

    @staticmethod
    def get_all_positions(api_key: str, api_secret: str, base_url: str = "https://api.india.delta.exchange") -> List[Dict[str, Any]]:
        """
        Fetch all margined positions for the given API credentials.
        
        Args:
            api_key: Delta Exchange API key (from client, never stored on server)
            api_secret: Delta Exchange API secret (from client, never stored on server)
            base_url: Delta Exchange base URL (default: India production)
        
        Returns:
            List of position dictionaries
        
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
            
            positions = client.get_all_margined_positions()
            logger.info(f"Fetched {len(positions)} positions")
            return positions
        
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise

    @staticmethod
    def calculate_total_pnl(positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate total PnL from positions.
        
        Args:
            positions: List of position dictionaries
        
        Returns:
            Dictionary with total_realized_pnl, total_unrealized_pnl, and total_pnl
        """
        total_realized_pnl = 0.0
        total_unrealized_pnl = 0.0
        
        for position in positions:
            # Realized PnL
            realized_pnl_str = position.get('realized_pnl', '0')
            try:
                total_realized_pnl += float(realized_pnl_str) if realized_pnl_str else 0.0
            except (ValueError, TypeError):
                pass
            
            # Unrealized PnL (if available in position data)
            # Note: Delta Exchange may not provide unrealized PnL directly
            # We'll calculate it if entry_price and current_price are available
            unrealized_pnl_str = position.get('unrealized_pnl', '0')
            try:
                total_unrealized_pnl += float(unrealized_pnl_str) if unrealized_pnl_str else 0.0
            except (ValueError, TypeError):
                pass
        
        total_pnl = total_realized_pnl + total_unrealized_pnl
        
        return {
            "total_realized_pnl": total_realized_pnl,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_pnl": total_pnl,
            "position_count": len(positions)
        }

