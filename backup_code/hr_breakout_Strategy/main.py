"""Main entry point for the Breakout Trading Bot"""

import logging
import sys
from pathlib import Path

# Handle both direct execution and module import
try:
    from .config_loader import ConfigLoader
    from .delta_client import DeltaExchangeClient
    from .breakout_bot import BreakoutTradingBot
except ImportError:
    from config_loader import ConfigLoader
    from delta_client import DeltaExchangeClient
    from breakout_bot import BreakoutTradingBot


def setup_logging(log_level: str, log_file: str):
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Log file path
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main function to initialize and run the trading bot"""
    
    # Load configuration
    try:
        # Try to find config.yaml in parent directory or current directory
        config_path = Path(__file__).parent.parent / 'config.yaml'
        if not config_path.exists():
            config_path = Path('config.yaml')
        
        config = ConfigLoader(str(config_path))
        print("✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        sys.exit(1)
    
    # Setup logging
    logging_config = config.get_logging_config()
    setup_logging(logging_config['level'], logging_config['file'])
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Breakout Trading Bot Starting")
    logger.info("=" * 60)
    
    # Get configurations
    trading_config = config.get_trading_config()
    schedule_config = config.get_schedule_config()
    risk_config = config.get_risk_config()
    monitoring_config = config.get_monitoring_config()
    api_config = config.get_api_config()
    
    # Get API credentials
    api_key, api_secret = config.get_api_credentials()
    
    # Log configuration (without sensitive data)
    logger.info(f"Trading Symbol: {trading_config['symbol']}")
    logger.info(f"Product ID: {trading_config['product_id']}")
    logger.info(f"Order Size: {trading_config['order_size']}")
    logger.info(f"Max Position Size: {trading_config.get('max_position_size', trading_config['order_size'] * 3)} (SAFETY LIMIT)")
    logger.info(f"Check Existing Orders: {trading_config.get('check_existing_orders', True)} (PREVENT DUPLICATES)")
    logger.info(f"Timeframe: {schedule_config['timeframe']}")
    logger.info(f"Reset Interval: {schedule_config['reset_interval_minutes']} minutes")
    logger.info(f"Timezone: {schedule_config['timezone']}")
    logger.info(f"Wait for Next Candle: {schedule_config.get('wait_for_next_candle', False)}")
    logger.info(f"Startup Delay: {schedule_config.get('startup_delay_minutes', 0)} minutes")
    logger.info(f"Stop Loss: {risk_config['stop_loss_points']} points")
    logger.info(f"Take Profit: {risk_config['take_profit_points']} points")
    logger.info(f"Breakeven Trigger: {risk_config['breakeven_trigger_points']} points")
    logger.info(f"API Base URL: {api_config['base_url']}")
    
    # Initialize Delta Exchange client
    try:
        client = DeltaExchangeClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=api_config['base_url']
        )
        logger.info("✓ Delta Exchange client initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Delta Exchange client: {e}")
        sys.exit(1)
    
    # Test API connection
    try:
        ticker = client.get_ticker(trading_config['symbol'])
        if ticker:
            current_price = ticker.get('close', 'N/A')
            logger.info(f"✓ API connection successful - Current {trading_config['symbol']} price: {current_price}")
        else:
            logger.warning("API connection test returned empty ticker")
    except Exception as e:
        logger.error(f"✗ API connection test failed: {e}")
        logger.error("Please check your API credentials and network connection")
        sys.exit(1)
    
    # Initialize and run the trading bot
    try:
        bot = BreakoutTradingBot(
            client=client,
            symbol=trading_config['symbol'],
            product_id=trading_config['product_id'],
            order_size=trading_config['order_size'],
            stop_loss_points=risk_config['stop_loss_points'],
            take_profit_points=risk_config['take_profit_points'],
            breakeven_trigger_points=risk_config['breakeven_trigger_points'],
            timeframe=schedule_config['timeframe'],
            reset_interval_minutes=schedule_config['reset_interval_minutes'],
            timezone=schedule_config['timezone'],
            order_check_interval=monitoring_config['order_check_interval'],
            position_check_interval=monitoring_config['position_check_interval'],
            wait_for_next_candle=schedule_config.get('wait_for_next_candle', False),
            startup_delay_minutes=schedule_config.get('startup_delay_minutes', 0),
            max_position_size=trading_config.get('max_position_size', trading_config['order_size'] * 3),
            check_existing_orders=trading_config.get('check_existing_orders', True)
        )
        
        logger.info("✓ Trading bot initialized successfully")
        logger.info("Starting main trading loop...")
        logger.info("=" * 60)
        
        # Run the bot
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("=" * 60)
        logger.info("Breakout Trading Bot Stopped")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()

