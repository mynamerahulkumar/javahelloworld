"""Configuration loader for the breakout trading bot"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv


class ConfigLoader:
    """Load and validate configuration from YAML file and environment variables"""
    
    def __init__(self, config_path: str = "../config.yaml"):
        """
        Initialize configuration loader
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = {}
        self._load_env()
        self._load_yaml()
        self._validate()
    
    def _load_env(self):
        """Load environment variables from .env file"""
        load_dotenv()
        
        # Load API credentials from environment
        self.api_key = os.getenv('DELTA_API_KEY')
        self.api_secret = os.getenv('DELTA_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API credentials not found. Please set DELTA_API_KEY and "
                "DELTA_API_SECRET in .env file"
            )
    
    def _load_yaml(self):
        """Load configuration from YAML file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        if not self.config:
            raise ValueError("Configuration file is empty")
    
    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        timeframe_map = {
            '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '6h': 360,
            '1d': 1440, '1w': 10080
        }
        if timeframe not in timeframe_map:
            raise ValueError(
                f"Invalid timeframe '{timeframe}'. "
                f"Valid options: {', '.join(timeframe_map.keys())}"
            )
        return timeframe_map[timeframe]
    
    def _validate(self):
        """Validate required configuration fields"""
        required_sections = ['trading', 'schedule', 'risk_management', 'monitoring', 'api']
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate trading section
        trading_required = ['symbol', 'product_id', 'order_size']
        for field in trading_required:
            if field not in self.config['trading']:
                raise ValueError(f"Missing required field in trading section: {field}")
        
        # Set defaults for optional trading fields
        if 'max_position_size' not in self.config['trading']:
            self.config['trading']['max_position_size'] = self.config['trading']['order_size'] * 2
        
        if 'check_existing_orders' not in self.config['trading']:
            self.config['trading']['check_existing_orders'] = True
        
        # Validate schedule section - timeframe is required, reset_interval_minutes is optional
        if 'timeframe' not in self.config['schedule']:
            raise ValueError("Missing required field in schedule section: timeframe")
        
        if 'timezone' not in self.config['schedule']:
            raise ValueError("Missing required field in schedule section: timezone")
        
        # Validate timeframe
        timeframe = self.config['schedule']['timeframe']
        calculated_interval = self._timeframe_to_minutes(timeframe)
        
        # Auto-calculate reset_interval_minutes if not provided
        if 'reset_interval_minutes' not in self.config['schedule']:
            self.config['schedule']['reset_interval_minutes'] = calculated_interval
            print(f"ℹ Auto-calculated reset_interval_minutes: {calculated_interval} for timeframe '{timeframe}'")
        else:
            # Validate that provided interval matches timeframe
            provided_interval = self.config['schedule']['reset_interval_minutes']
            if provided_interval != calculated_interval:
                print(
                    f"⚠ Warning: reset_interval_minutes ({provided_interval}) doesn't match "
                    f"timeframe '{timeframe}' ({calculated_interval} minutes). "
                    f"Using provided value."
                )
        
        # Set defaults for optional delay settings
        if 'wait_for_next_candle' not in self.config['schedule']:
            self.config['schedule']['wait_for_next_candle'] = False
        
        if 'startup_delay_minutes' not in self.config['schedule']:
            self.config['schedule']['startup_delay_minutes'] = 0
        
        # Validate risk management section
        risk_required = ['stop_loss_points', 'take_profit_points', 'breakeven_trigger_points']
        for field in risk_required:
            if field not in self.config['risk_management']:
                raise ValueError(f"Missing required field in risk_management section: {field}")
        
        # Validate monitoring section
        monitoring_required = ['order_check_interval', 'position_check_interval']
        for field in monitoring_required:
            if field not in self.config['monitoring']:
                raise ValueError(f"Missing required field in monitoring section: {field}")
        
        # Validate API section
        if 'base_url' not in self.config['api']:
            raise ValueError("Missing required field in api section: base_url")
    
    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            section: Configuration section name
            key: Configuration key (optional)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if key is None:
            return self.config.get(section, default)
        return self.config.get(section, {}).get(key, default)
    
    def get_trading_config(self) -> Dict[str, Any]:
        """Get trading configuration"""
        return self.config['trading']
    
    def get_schedule_config(self) -> Dict[str, Any]:
        """Get schedule configuration"""
        return self.config['schedule']
    
    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk management configuration"""
        return self.config['risk_management']
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return self.config['monitoring']
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return self.config['api']
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration with defaults"""
        return {
            'level': self.get('logging', 'level', 'INFO'),
            'file': self.get('logging', 'file', 'breakout_bot.log')
        }
    
    def get_api_credentials(self) -> tuple[str, str]:
        """
        Get API credentials
        
        Returns:
            Tuple of (api_key, api_secret)
        """
        return self.api_key, self.api_secret

