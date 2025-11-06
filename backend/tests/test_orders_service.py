"""
Unit tests for OrdersService
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.orders_service import OrdersService


class TestOrdersService:
    """Test cases for OrdersService"""

    def test_get_order_history_success(self):
        """Test successfully fetching order history"""
        mock_history = {
            "result": [
                {
                    "id": 123,
                    "product_symbol": "BTCUSD",
                    "side": "buy",
                    "order_type": "limit_order",
                    "state": "filled",
                }
            ],
            "meta": {"after": "cursor123"}
        }

        with patch("services.orders_service.DeltaRestClient") as mock_client_class:
            mock_client = Mock()
            mock_client.order_history.return_value = mock_history
            mock_client_class.return_value = mock_client

            result = OrdersService.get_order_history(
                api_key="test_key",
                api_secret="test_secret",
                page_size=100
            )

            assert result == mock_history
            mock_client_class.assert_called_once()

    def test_get_order_history_missing_credentials(self):
        """Test that missing credentials raise ValueError"""
        with pytest.raises(ValueError, match="API key and secret must be provided"):
            OrdersService.get_order_history(
                api_key="",
                api_secret="test_secret"
            )

    def test_get_active_orders_success(self):
        """Test successfully fetching active orders"""
        mock_orders = [
            {"id": 1, "state": "open"},
            {"id": 2, "state": "open"},
        ]

        with patch("services.orders_service.DeltaRestClient") as mock_client_class:
            mock_client = Mock()
            mock_client.get_live_orders.return_value = mock_orders
            mock_client_class.return_value = mock_client

            result = OrdersService.get_active_orders(
                api_key="test_key",
                api_secret="test_secret"
            )

            assert result == mock_orders

