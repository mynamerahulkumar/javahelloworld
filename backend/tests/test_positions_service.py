"""
Unit tests for PositionsService
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.positions_service import PositionsService


class TestPositionsService:
    """Test cases for PositionsService"""

    def test_get_all_positions_success(self):
        """Test successfully fetching all positions"""
        mock_positions = [
            {
                "user_id": 123,
                "size": 10.5,
                "entry_price": "50000",
                "margin": "1000",
                "product_id": 27,
                "product_symbol": "BTCUSD",
                "realized_pnl": "100.50",
            }
        ]

        with patch("services.positions_service.DeltaRestClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get_all_margined_positions.return_value = mock_positions
            mock_client_class.return_value = mock_client

            result = PositionsService.get_all_positions(
                api_key="test_key",
                api_secret="test_secret",
                base_url="https://api.test.delta.exchange"
            )

            assert result == mock_positions
            mock_client_class.assert_called_once()
            mock_client.get_all_margined_positions.assert_called_once()

    def test_get_all_positions_missing_credentials(self):
        """Test that missing credentials raise ValueError"""
        with pytest.raises(ValueError, match="API key and secret must be provided"):
            PositionsService.get_all_positions(
                api_key="",
                api_secret="test_secret"
            )

    def test_calculate_total_pnl(self):
        """Test calculating total PnL from positions"""
        positions = [
            {"realized_pnl": "100.50"},
            {"realized_pnl": "-50.25"},
            {"realized_pnl": "25.75"},
        ]

        result = PositionsService.calculate_total_pnl(positions)

        assert result["total_realized_pnl"] == 76.0
        assert result["total_unrealized_pnl"] == 0.0
        assert result["total_pnl"] == 76.0
        assert result["position_count"] == 3

