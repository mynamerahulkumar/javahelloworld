"""
Fear & Greed Index fetcher using CoinMarketCap API.
"""
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from config import Config

logger = logging.getLogger(__name__)


class FearGreedFetcher:
    """Fetches Fear & Greed Index data from CoinMarketCap API."""
    
    def __init__(self):
        """Initialize the Fear & Greed Index fetcher."""
        self.config = Config.get_crypto_market_config()
        self.api_key = self.config['api_key']
        self.base_url = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical"
        self.headers = {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json',
            'Accept-Encoding': 'deflate, gzip'
        }
    
    def fetch_current_index(self) -> Optional[Dict]:
        """
        Fetch the current Fear & Greed Index.
        
        Returns:
            Current Fear & Greed Index data or None if failed
        """
        try:
            params = {
                'start': 1,
                'limit': 1
            }
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status', {}).get('error_code') == 0:
                    index_data = data.get('data', [])
                    
                    if index_data:
                        current_index = index_data[0]
                        processed_data = self._process_index_data(current_index)
                        logger.info(f"Fetched current Fear & Greed Index: {processed_data['value']}")
                        return processed_data
                    else:
                        logger.warning("No Fear & Greed Index data received")
                        return None
                else:
                    error_msg = data.get('status', {}).get('error_message', 'Unknown error')
                    logger.error(f"CoinMarketCap API error: {error_msg}")
                    return None
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching Fear & Greed Index: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching Fear & Greed Index: {e}")
            return None
    
    def fetch_historical_data(self, days: int = 30) -> List[Dict]:
        """
        Fetch historical Fear & Greed Index data.
        
        Args:
            days: Number of days of historical data to fetch
            
        Returns:
            List of historical Fear & Greed Index data
        """
        try:
            params = {
                'start': 1,
                'limit': min(days, 365)  # API limit
            }
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status', {}).get('error_code') == 0:
                    index_data = data.get('data', [])
                    processed_data = [self._process_index_data(item) for item in index_data]
                    logger.info(f"Fetched {len(processed_data)} historical Fear & Greed Index records")
                    return processed_data
                else:
                    error_msg = data.get('status', {}).get('error_message', 'Unknown error')
                    logger.error(f"CoinMarketCap API error: {error_msg}")
                    return []
            else:
                logger.error(f"HTTP error {response.status_code}: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching historical Fear & Greed Index: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching historical Fear & Greed Index: {e}")
            return []
    
    def _process_index_data(self, raw_data: Dict) -> Dict:
        """
        Process raw Fear & Greed Index data from API.
        
        Args:
            raw_data: Raw data from API
            
        Returns:
            Processed data
        """
        try:
            value = raw_data.get('value', 0)
            value_classification = raw_data.get('value_classification', 'Neutral')
            timestamp_str = raw_data.get('timestamp', '')
            
            # Parse timestamp
            timestamp = self._parse_timestamp(timestamp_str)
            
            # Map classification to our model choices
            classification_mapping = {
                'Extreme Fear': 'EXTREME_FEAR',
                'Fear': 'FEAR',
                'Neutral': 'NEUTRAL',
                'Greed': 'GREED',
                'Extreme Greed': 'EXTREME_GREED'
            }
            
            processed_data = {
                'value': value,
                'value_classification': classification_mapping.get(value_classification, 'NEUTRAL'),
                'timestamp': timestamp,
                'raw_classification': value_classification,
                'raw_data': raw_data
            }
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing Fear & Greed Index data: {e}")
            return {
                'value': 50,
                'value_classification': 'NEUTRAL',
                'timestamp': datetime.now(timezone.utc),
                'raw_classification': 'Neutral',
                'raw_data': raw_data
            }
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse timestamp string to datetime object.
        
        Args:
            timestamp_str: ISO timestamp string
            
        Returns:
            datetime object
        """
        try:
            if timestamp_str:
                # Handle different timestamp formats
                if 'T' in timestamp_str:
                    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    return datetime.fromisoformat(timestamp_str)
            else:
                return datetime.now(timezone.utc)
        except Exception as e:
            logger.warning(f"Error parsing timestamp '{timestamp_str}': {e}")
            return datetime.now(timezone.utc)
    
    def get_classification_description(self, value: int) -> str:
        """
        Get description for Fear & Greed Index value.
        
        Args:
            value: Index value (0-100)
            
        Returns:
            Description string
        """
        if value <= 24:
            return "Extreme Fear - Investors are extremely fearful, potential buying opportunity"
        elif value <= 49:
            return "Fear - Investors are fearful, market may be oversold"
        elif value == 50:
            return "Neutral - Market sentiment is balanced"
        elif value <= 74:
            return "Greed - Investors are greedy, market may be overbought"
        else:
            return "Extreme Greed - Investors are extremely greedy, potential selling opportunity"
    
    def get_trading_recommendation(self, value: int) -> str:
        """
        Get trading recommendation based on Fear & Greed Index value.
        
        Args:
            value: Index value (0-100)
            
        Returns:
            Trading recommendation
        """
        if value <= 24:
            return "BUY - Market is in extreme fear, good time to accumulate"
        elif value <= 49:
            return "CONSIDER BUYING - Market is fearful, look for oversold conditions"
        elif value == 50:
            return "HOLD - Market sentiment is neutral, wait for clearer signals"
        elif value <= 74:
            return "CONSIDER SELLING - Market is greedy, look for overbought conditions"
        else:
            return "SELL - Market is in extreme greed, consider taking profits"
    
    def get_api_usage_info(self) -> Dict:
        """
        Get API usage information from the last response.
        
        Returns:
            Dictionary with API usage info
        """
        # This would need to be implemented based on CoinMarketCap API response headers
        # For now, return a placeholder
        return {
            'credits_used': 0,
            'credits_remaining': 0,
            'plan': 'basic'
        }


# Global fetcher instance
fear_greed_fetcher = FearGreedFetcher()

