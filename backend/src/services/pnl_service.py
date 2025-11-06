"""
PnL Service - Single Responsibility: Calculate and aggregate PnL metrics
"""
import logging
from typing import Dict, Any
from services.positions_service import PositionsService

logger = logging.getLogger(__name__)


class PnLService:
    """Service for calculating PnL metrics"""

    @staticmethod
    def get_pnl_summary(
        api_key: str,
        api_secret: str,
        base_url: str = "https://api.india.delta.exchange"
    ) -> Dict[str, Any]:
        """
        Get comprehensive PnL summary including total, realized, and unrealized PnL.
        
        Args:
            api_key: Delta Exchange API key (from client, never stored on server)
            api_secret: Delta Exchange API secret (from client, never stored on server)
            base_url: Delta Exchange base URL (default: India production)
        
        Returns:
            Dictionary with PnL summary including:
            - total_pnl: Total profit/loss
            - total_realized_pnl: Realized profit/loss
            - total_unrealized_pnl: Unrealized profit/loss
            - position_count: Number of positions
            - pnl_by_symbol: PnL breakdown by trading symbol
        """
        try:
            # Get all positions using PositionsService
            positions = PositionsService.get_all_positions(api_key, api_secret, base_url)
            
            # Calculate aggregate PnL
            aggregate_pnl = PositionsService.calculate_total_pnl(positions)
            
            # Calculate PnL by symbol
            pnl_by_symbol: Dict[str, Dict[str, Any]] = {}
            
            for position in positions:
                symbol = position.get('product_symbol', 'UNKNOWN')
                realized_pnl_str = position.get('realized_pnl', '0')
                
                try:
                    realized_pnl = float(realized_pnl_str) if realized_pnl_str else 0.0
                except (ValueError, TypeError):
                    realized_pnl = 0.0
                
                if symbol not in pnl_by_symbol:
                    pnl_by_symbol[symbol] = {
                        "symbol": symbol,
                        "realized_pnl": 0.0,
                        "position_count": 0
                    }
                
                pnl_by_symbol[symbol]["realized_pnl"] += realized_pnl
                pnl_by_symbol[symbol]["position_count"] += 1
            
            return {
                "total_pnl": aggregate_pnl["total_pnl"],
                "total_realized_pnl": aggregate_pnl["total_realized_pnl"],
                "total_unrealized_pnl": aggregate_pnl["total_unrealized_pnl"],
                "position_count": aggregate_pnl["position_count"],
                "pnl_by_symbol": list(pnl_by_symbol.values())
            }
        
        except Exception as e:
            logger.error(f"Error calculating PnL summary: {e}")
            raise

