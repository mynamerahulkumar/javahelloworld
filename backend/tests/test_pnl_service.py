"""
Unit tests for PnLService
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.pnl_service import PnLService


class TestPnLService:
    """Test cases for PnLService"""

    def test_get_pnl_summary_success(self):
        """Test successfully calculating PnL summary"""
        mock_positions = [
            {
                "product_symbol": "BTCUSD",
                "realized_pnl": "100.50",
            },
            {
                "product_symbol": "ETHUSD",
                "realized_pnl": "-50.25",
            },
        ]

        with patch("services.pnl_service.PositionsService.get_all_positions") as mock_get_positions:
            mock_get_positions.return_value = mock_positions

            result = PnLService.get_pnl_summary(
                api_key="test_key",
                api_secret="test_secret"
            )

            assert result["total_realized_pnl"] == 50.25
            assert result["position_count"] == 2
            assert len(result["pnl_by_symbol"]) == 2
            assert result["pnl_by_symbol"][0]["symbol"] == "BTCUSD"
            assert result["pnl_by_symbol"][0]["realized_pnl"] == 100.50

