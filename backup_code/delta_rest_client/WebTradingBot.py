from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
import json
import os
import sys
import logging
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
import secrets

# Add parent directory to path to import strategy module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategymovingaverage import MovingAverageTradingBot, DeltaExchangeAPI
from news_service.crypto_news_trader import CryptoNewsTrader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
# Try to load from parent directory first, then current directory
env_path = os.environ.get("ENV_FILE_PATH")
if env_path and os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Try parent directory
    parent_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(parent_env):
        load_dotenv(parent_env)
    else:
        # Fallback to current directory
        load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key for sessions
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables for bot state
trading_bot = None
bot_thread = None
bot_running = False
news_trader = None
news_thread = None
news_running = False
bot_status = {
    'running': False,
    'symbol': None,
    'current_price': 0,
    'position': None,
    'signals': {},
    'last_update': None,
    'pnl': 0,
    'trades_today': 0
}

# News data storage
latest_news = {
    'articles': [],
    'signals': {},
    'recommendation': {},
    'last_update': None
}

class WebTradingBot(MovingAverageTradingBot):
    """Extended trading bot with web interface support"""
    
    def __init__(self, api_key: str, api_secret: str, symbol: str = 'BTCUSD'):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"WebTradingBot initialized with Symbol: {symbol}")
        
        super().__init__(api_key, api_secret, symbol)
        self.last_status_update = 0
        
    def log_status(self, signals: Dict):
        """Override to emit status updates via WebSocket"""
        super().log_status(signals)
        
        # Update global status
        current_position = self.get_current_position()
        position_info = None
        
        if current_position:
            size = float(current_position.get('size', 0))
            side = 'long' if size > 0 else 'short'
            abs_size = abs(size)
            entry_price = float(current_position.get('entry_price', 0) or 0)
            
            # Use realized_pnl from official API response format
            realized_pnl = current_position.get('realized_pnl')
            realized_pnl_value = float(realized_pnl) if realized_pnl is not None else 0.0
            
            # Also try to get unrealized_pnl if available
            api_unrealized = current_position.get('unrealized_pnl')
            unrealized_from_api = float(api_unrealized) if api_unrealized is not None else None
            
            # Compute unrealized P&L if API doesn't provide it, using latest price
            computed_unrealized = None
            try:
                latest_price = float(signals.get('current_price') or 0)
                if entry_price and abs_size and latest_price:
                    if side == 'long':
                        computed_unrealized = (latest_price - entry_price) * abs_size
                    else:
                        computed_unrealized = (entry_price - latest_price) * abs_size
            except Exception:
                computed_unrealized = None
            
            final_unrealized = unrealized_from_api if (unrealized_from_api is not None and unrealized_from_api != 0) else (computed_unrealized or 0.0)
            
            # Total P&L = realized + unrealized
            total_pnl = realized_pnl_value + final_unrealized
            
            position_info = {
                'side': side,
                'size': abs_size,
                'entry_price': entry_price,
                'realized_pnl': realized_pnl_value,
                'unrealized_pnl': final_unrealized,
                'total_pnl': total_pnl
            }
        
        # Update global bot status
        global bot_status
        bot_status.update({
            'running': True,
            'symbol': self.symbol,
            'current_price': signals['current_price'],
            'position': position_info,
            'signals': {
                'sma_signal': signals['sma_signal'],
                'ema_signal': signals['ema_signal'],
                'sma_short': signals['sma_short'],
                'sma_long': signals['sma_long'],
                'ema_short': signals['ema_short'],
                'ema_long': signals['ema_long']
            },
            'last_update': datetime.now().isoformat(),
            'pnl': position_info['total_pnl'] if position_info else 0
        })
        
        # Emit status update via WebSocket
        socketio.emit('status_update', bot_status)
    
    def apply_strategy_parameters(self, params):
        """Apply custom strategy parameters from frontend"""
        self.logger.info(f"Applying strategy parameters: {params}")
        
        # Update moving average periods
        if 'sma_short' in params:
            self.short_ma_period = int(params['sma_short'])
        if 'sma_long' in params:
            self.long_ma_period = int(params['sma_long'])
        if 'ema_short' in params:
            self.ema_short_period = int(params['ema_short'])
        if 'ema_long' in params:
            self.ema_long_period = int(params['ema_long'])
        
        # Update risk management parameters
        if 'stop_loss_pct' in params:
            self.risk_manager.stop_loss_pct = float(params['stop_loss_pct']) / 100.0
        if 'take_profit_pct' in params:
            self.risk_manager.take_profit_pct = float(params['take_profit_pct']) / 100.0
        if 'position_size' in params:
            self.risk_manager.max_position_size = int(params['position_size'])
            self.risk_manager.configured_position_size = int(params['position_size'])
        
        # Store news weightage for signal combination
        if 'news_weightage' in params:
            self.news_weightage = float(params['news_weightage']) / 100.0
        else:
            self.news_weightage = 0.3  # Default 30%
        
        self.logger.info(f"Updated strategy: SMA({self.short_ma_period},{self.long_ma_period}), EMA({self.ema_short_period},{self.ema_long_period})")
        self.logger.info(f"Risk management: SL={self.risk_manager.stop_loss_pct*100}%, TP={self.risk_manager.take_profit_pct*100}%, Position={self.risk_manager.max_position_size}")
        self.logger.info(f"News weightage: {self.news_weightage*100}%")
    
    def run(self):
        """Override main loop to work with web interface"""
        global bot_running, bot_status
        
        self.logger.info("Starting Web Trading Bot")
        bot_status['running'] = True
        
        # Fetch initial historical data
        if not self.fetch_historical_data():
            self.logger.error("Failed to fetch historical data")
            bot_status['running'] = False
            return
        
        try:
            while bot_running:
                # Update current price
                current_price = self.update_current_price()
                if not current_price:
                    self.logger.warning("Failed to get current price, retrying...")
                    time.sleep(30)
                    continue
                
                # Calculate signals
                signals = self.calculate_signals()
                
                # Log current status (this will emit WebSocket update)
                self.log_status(signals)
                
                # Check for trading signals
                primary_signal = signals['sma_signal']
                secondary_signal = signals['ema_signal']
                
                # Get news-based recommendation
                news_recommendation = self.get_news_recommendation()
                
                # Combine technical and news signals
                final_signal = self.combine_signals(primary_signal, secondary_signal, news_recommendation)
                
                if final_signal:
                    self.logger.info(f"Trading signal detected: {final_signal.upper()}")
                    self.logger.info(f"Technical: {primary_signal}, News: {news_recommendation}")
                    
                    # Execute trade
                    if self.execute_trade(final_signal, current_price):
                        self.logger.info(f"Trade executed successfully: {final_signal}")
                        socketio.emit('trade_executed', {
                            'signal': final_signal,
                            'price': current_price,
                            'timestamp': datetime.now().isoformat(),
                            'news_sentiment': news_recommendation
                        })
                    else:
                        self.logger.warning(f"Failed to execute trade: {final_signal}")
                        
                elif primary_signal or secondary_signal:
                    self.logger.info(f"Technical signal detected but news sentiment is neutral: {primary_signal or secondary_signal}")
                    self.logger.info(f"News recommendation: {news_recommendation}")
                
                # Wait before next iteration
                time.sleep(10)
                
        except Exception as e:
            self.logger.error(f"Error in trading bot: {e}")
            socketio.emit('bot_error', {'error': str(e)})
        finally:
            bot_status['running'] = False
            socketio.emit('bot_stopped', {})
    
    def get_news_recommendation(self):
        """Get news-based trading recommendation"""
        global latest_news, news_trader
        
        try:
            if not news_trader or not latest_news.get('recommendation'):
                return 'NEUTRAL'
            
            recommendation = latest_news['recommendation']
            
            # Only use high-confidence news signals
            if recommendation.get('overall_confidence', 0) >= 0.7:
                return recommendation.get('recommendation', 'NEUTRAL')
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            self.logger.error(f"Error getting news recommendation: {e}")
            return 'NEUTRAL'
    
    def combine_signals(self, technical_signal, secondary_signal, news_signal):
        """Combine technical analysis with news sentiment using configurable weightage"""
        
        # If no technical signal, don't trade
        if not technical_signal and not secondary_signal:
            return None
        
        # Use primary technical signal if available
        signal = technical_signal or secondary_signal
        
        # Get news weightage (default to 30% if not set)
        news_weight = getattr(self, 'news_weightage', 0.3)
        technical_weight = 1.0 - news_weight
        
        self.logger.info(f"Signal combination - Technical: {signal}, News: {news_signal}, News Weight: {news_weight*100}%, Technical Weight: {technical_weight*100}%")
        
        # If news weightage is 0, only use technical signals
        if news_weight == 0:
            return signal
        
        # If news weightage is 100%, only use news signals
        if news_weight == 1.0:
            if news_signal == 'NEUTRAL':
                return None
            return news_signal.lower() if news_signal in ['BUY', 'SELL'] else None
        
        # Combined signal logic with weighted approach
        if news_signal == 'NEUTRAL':
            # News is neutral, use technical signal with reduced confidence
            return signal
        elif news_signal == signal.upper():
            # News confirms technical signal - proceed with confidence
            self.logger.info(f"News confirms technical signal: {signal}")
            return signal
        elif news_signal != signal.upper():
            # News contradicts technical signal
            self.logger.warning(f"News sentiment ({news_signal}) contradicts technical signal ({signal})")
            
            # If technical weight is higher, still proceed with technical signal but with caution
            if technical_weight > news_weight:
                self.logger.info(f"Technical signal overrides news due to higher weight ({technical_weight*100}% vs {news_weight*100}%)")
                return signal
            else:
                # News has higher weight, follow news signal
                self.logger.info(f"News signal overrides technical due to higher weight ({news_weight*100}% vs {technical_weight*100}%)")
                return news_signal.lower() if news_signal in ['BUY', 'SELL'] else None
        
        return signal

# Authentication middleware
def require_auth(f):
    """Decorator to require authentication for routes"""
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect('/login')
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def news_worker():
    """Background worker for fetching and analyzing crypto news"""
    global news_trader, news_running, latest_news
    
    try:
        logger.info("Starting crypto news service")
        news_trader = CryptoNewsTrader()
        
        while news_running:
            try:
                logger.info("Fetching latest crypto news...")
                
                # Get news from RSS feeds
                all_news = news_trader.get_crypto_news_feeds()
                
                if all_news:
                    # Analyze each news item
                    high_confidence_signals = []
                    
                    for news_item in all_news:
                        try:
                            signal_data = news_trader.generate_trading_signal(news_item)
                            news_trader.save_news_signal(news_item, signal_data)
                            
                            # Collect high-confidence signals
                            if signal_data['confidence'] >= 0.65:
                                high_confidence_signals.append({
                                    'news': news_item,
                                    'signal': signal_data
                                })
                                
                        except Exception as e:
                            logger.error(f"Error processing news item: {e}")
                            continue
                    
                    # Get overall trading recommendation
                    recommendation = news_trader.get_trading_recommendation(min_confidence=0.65)
                    
                    # Update global news data
                    latest_news.update({
                        'articles': all_news[:10],  # Top 10 articles
                        'signals': high_confidence_signals[:5],  # Top 5 signals
                        'recommendation': recommendation,
                        'last_update': datetime.now().isoformat()
                    })
                    
                    # Emit news update via WebSocket
                    socketio.emit('news_update', latest_news)
                    
                    logger.info(f"Updated news: {len(all_news)} articles, {len(high_confidence_signals)} signals")
                
            except Exception as e:
                logger.error(f"Error in news worker: {e}")
                
            # Wait 60 seconds before next update
            time.sleep(60)
            
    except Exception as e:
        logger.error(f"News worker failed: {e}")
        socketio.emit('news_error', {'error': str(e)})
    finally:
        news_running = False

# Authentication routes
@app.route('/login')
def login():
    """Serve the login page"""
    # If already authenticated, redirect to dashboard
    if session.get('authenticated'):
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
@require_auth
def dashboard():
    """Serve the main trading dashboard"""
    return render_template('index.html')

@app.route('/auth/verify', methods=['POST'])
def verify_auth():
    """Verify Firebase authentication token and create session"""
    try:
        data = request.get_json()
        user_data = data.get('user')
        
        if not user_data:
            return jsonify({'success': False, 'message': 'No user data provided'})
        
        # Store user data in session
        session['authenticated'] = True
        session['user'] = {
            'uid': user_data.get('uid'),
            'email': user_data.get('email'),
            'displayName': user_data.get('displayName'),
            'photoURL':"../static/user_icon.png"
        }
        
        logger.info(f"User authenticated: {user_data.get('email')}")
        return jsonify({'success': True, 'message': 'Authentication successful'})
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return jsonify({'success': False, 'message': f'Authentication failed: {str(e)}'})

@app.route('/auth/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    try:
        session.clear()
        logger.info("User logged out")
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'success': False, 'message': f'Logout failed: {str(e)}'})

@app.route('/auth/status')
def auth_status():
    """Check authentication status"""
    if session.get('authenticated'):
        return jsonify({
            'authenticated': True,
            'user': session.get('user', {})
        })
    return jsonify({'authenticated': False})

@app.route('/')
def index():
    """Redirect to login or dashboard based on auth status"""
    if session.get('authenticated'):
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/api/status')
@require_auth
def get_status():
    """Get current bot status"""
    return jsonify(bot_status)

@app.route('/api/news')
@require_auth
def get_news():
    """Get latest crypto news and signals"""
    return jsonify(latest_news)

@app.route('/api/start-news', methods=['POST'])
@require_auth
def start_news():
    """Start the crypto news service"""
    global news_thread, news_running
    
    if news_running:
        return jsonify({'success': False, 'message': 'News service is already running'})
    
    try:
        news_running = True
        news_thread = threading.Thread(target=news_worker)
        news_thread.daemon = True
        news_thread.start()
        
        logger.info("Crypto news service started")
        return jsonify({'success': True, 'message': 'News service started successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting news service: {str(e)}'})

@app.route('/api/stop-news', methods=['POST'])
@require_auth
def stop_news():
    """Stop the crypto news service"""
    global news_running
    
    if not news_running:
        return jsonify({'success': False, 'message': 'News service is not running'})
    
    try:
        news_running = False
        logger.info("Crypto news service stopped")
        return jsonify({'success': True, 'message': 'News service stopped successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error stopping news service: {str(e)}'})

@app.route('/api/crypto-signals/<crypto_symbol>')
@require_auth
def get_crypto_signals(crypto_symbol):
    """Get signals specific to a particular cryptocurrency"""
    try:
        if not news_trader:
            return jsonify({'success': False, 'message': 'News service not initialized'})
        
        signals = news_trader.get_crypto_specific_signals(crypto_symbol.upper())
        return jsonify({'success': True, 'signals': signals})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting crypto signals: {str(e)}'})

@app.route('/api/start', methods=['POST'])
@require_auth
def start_bot():
    """Start the trading bot"""
    global trading_bot, bot_thread, bot_running
    
    if bot_running:
        return jsonify({'success': False, 'message': 'Bot is already running'})
    
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        symbol = data.get('symbol', 'BTCUSD')
        strategy_params = data.get('strategy_params', {})
        
        if not api_key or not api_secret:
            return jsonify({'success': False, 'message': 'API credentials required'})
        
        # Create and start bot
        try:
            logger.info(f"Starting bot with Symbol: {symbol}")
            logger.info(f"Strategy parameters: {strategy_params}")
            
            trading_bot = WebTradingBot(api_key, api_secret, symbol)
            
            # Apply strategy parameters if provided
            if strategy_params:
                trading_bot.apply_strategy_parameters(strategy_params)
            
            bot_running = True
            
            # Start bot in separate thread
            bot_thread = threading.Thread(target=trading_bot.run)
            bot_thread.daemon = True
            bot_thread.start()
            
            logger.info(f"Trading bot started successfully for {symbol}")
        except Exception as e:
            logger.error(f"Failed to create trading bot: {e}")
            return jsonify({'success': False, 'message': f'Failed to create bot: {str(e)}'})
        
        return jsonify({'success': True, 'message': 'Bot started successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error starting bot: {str(e)}'})

@app.route('/api/stop', methods=['POST'])
@require_auth
def stop_bot():
    """Stop the trading bot"""
    global bot_running, trading_bot
    
    if not bot_running:
        return jsonify({'success': False, 'message': 'Bot is not running'})
    
    try:
        bot_running = False
        bot_status['running'] = False
        
        return jsonify({'success': True, 'message': 'Bot stopped successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error stopping bot: {str(e)}'})

@app.route('/api/positions')
@require_auth
def get_positions():
    """Get current positions"""
    try:
        if not trading_bot:
            return jsonify({'success': False, 'message': 'Bot not initialized'})
        
        positions = trading_bot.api.get_positions()
        return jsonify({'success': True, 'positions': positions})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting positions: {str(e)}'})

@app.route('/api/orders')
@require_auth
def get_orders():
    """Get current orders"""
    try:
        if not trading_bot:
            return jsonify({'success': False, 'message': 'Bot not initialized'})
        
        orders = trading_bot.api.get_orders()
        return jsonify({'success': True, 'orders': orders})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting orders: {str(e)}'})

@app.route('/api/manual-trade', methods=['POST'])
@require_auth
def manual_trade():
    """Execute manual trade"""
    try:
        if not trading_bot:
            return jsonify({'success': False, 'message': 'Bot not initialized'})
        
        data = request.get_json()
        side = data.get('side')  # 'buy' or 'sell'
        size = data.get('size', 1)
        order_type = data.get('order_type', 'market_order')
        
        if not side:
            return jsonify({'success': False, 'message': 'Side (buy/sell) required'})
        
        # Get current price
        current_price = trading_bot.update_current_price()
        if not current_price:
            return jsonify({'success': False, 'message': 'Could not get current price'})
        
        # Execute trade
        if side == 'buy':
            success = trading_bot.open_long_position(current_price)
        else:
            success = trading_bot.open_short_position(current_price)
        
        if success:
            return jsonify({'success': True, 'message': f'{side.capitalize()} order executed'})
        else:
            return jsonify({'success': False, 'message': 'Failed to execute order'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error executing trade: {str(e)}'})

@app.route('/api/close-position', methods=['POST'])
@require_auth
def close_position():
    """Close current position"""
    try:
        if not trading_bot:
            return jsonify({'success': False, 'message': 'Bot not initialized'})
        
        position = trading_bot.get_current_position()
        if not position:
            return jsonify({'success': False, 'message': 'No position to close'})
        
        success = trading_bot.close_position(position)
        
        if success:
            return jsonify({'success': True, 'message': 'Position closed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to close position'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error closing position: {str(e)}'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status_update', bot_status)
    emit('news_update', latest_news)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Production mode configuration
    import os
    
    # Set production environment variables
    os.environ.setdefault('FLASK_ENV', 'production')
    
    logger.info("Starting Flask application...")
    
    # Check if running in production mode
    if os.environ.get('FLASK_ENV') == 'production':
        logger.info("Running in production mode")
        # In production, Gunicorn will handle the server
        # This is just for development/testing
        socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    else:
        logger.info("Running in development mode")
        socketio.run(app, debug=True, host='0.0.0.0', port=5003, allow_unsafe_werkzeug=True)
