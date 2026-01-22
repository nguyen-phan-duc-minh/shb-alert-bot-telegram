import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management with environment variable support"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Stock
    STOCK_SYMBOL = os.getenv('STOCK_SYMBOL', 'SHB')
    
    # Market
    MARKET_TIMEZONE = os.getenv('MARKET_TIMEZONE', 'Asia/Ho_Chi_Minh')
    MARKET_DAYS = [int(d) for d in os.getenv('MARKET_DAYS', '0,1,2,3,4').split(',')]
    MARKET_OPEN_TIME = os.getenv('MARKET_OPEN_TIME', '09:15')
    MARKET_CLOSE_TIME = os.getenv('MARKET_CLOSE_TIME', '14:45')
    
    # Polling
    POLL_INTERVAL_OPEN = int(os.getenv('POLL_INTERVAL_OPEN', '60'))
    POLL_INTERVAL_CLOSED = int(os.getenv('POLL_INTERVAL_CLOSED', '300'))
    
    # Strategy
    STRATEGY_PRE_BUY_RANGE = float(os.getenv('STRATEGY_PRE_BUY_RANGE', '0.05'))
    STRATEGY_PRE_SELL_RANGE = float(os.getenv('STRATEGY_PRE_SELL_RANGE', '0.05'))
    STRATEGY_DOWN_THRESHOLD = float(os.getenv('STRATEGY_DOWN_THRESHOLD', '0.3'))
    STRATEGY_UP_THRESHOLD = float(os.getenv('STRATEGY_UP_THRESHOLD', '0.5'))
    STRATEGY_COOLDOWN_MINUTES = int(os.getenv('STRATEGY_COOLDOWN_MINUTES', '15'))
    
    # API
    STOCK_API_PROVIDER = os.getenv('STOCK_API_PROVIDER', 'vnd')
    STOCK_API_TIMEOUT = int(os.getenv('STOCK_API_TIMEOUT', '10'))
    STOCK_API_MAX_RETRIES = int(os.getenv('STOCK_API_MAX_RETRIES', '3'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/bot.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # Health Check
    HEALTH_CHECK_ENABLED = os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
    HEALTH_CHECK_PORT = int(os.getenv('HEALTH_CHECK_PORT', '8080'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN or cls.TELEGRAM_BOT_TOKEN == 'PUT_YOUR_BOT_TOKEN_HERE':
            errors.append("TELEGRAM_BOT_TOKEN is not set")
        
        if not cls.TELEGRAM_CHAT_ID or cls.TELEGRAM_CHAT_ID == 'PUT_YOUR_CHAT_ID_HERE':
            errors.append("TELEGRAM_CHAT_ID is not set")
        
        if cls.STRATEGY_DOWN_THRESHOLD < 0:
            errors.append("STRATEGY_DOWN_THRESHOLD must be >= 0")
        
        if cls.STRATEGY_UP_THRESHOLD < 0:
            errors.append("STRATEGY_UP_THRESHOLD must be >= 0")
        
        if cls.POLL_INTERVAL_OPEN < 1:
            errors.append("POLL_INTERVAL_OPEN must be >= 1")
        
        if cls.POLL_INTERVAL_CLOSED < 1:
            errors.append("POLL_INTERVAL_CLOSED must be >= 1")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    @classmethod
    def to_dict(cls):
        """Convert config to dict for legacy compatibility"""
        return {
            'symbol': cls.STOCK_SYMBOL,
            'market': {
                'timezone': cls.MARKET_TIMEZONE,
                'days': cls.MARKET_DAYS,
                'open': cls.MARKET_OPEN_TIME,
                'close': cls.MARKET_CLOSE_TIME,
            },
            'poll': {
                'open': cls.POLL_INTERVAL_OPEN,
                'closed': cls.POLL_INTERVAL_CLOSED,
            },
            'strategy': {
                'pre_buy_range': cls.STRATEGY_PRE_BUY_RANGE,
                'pre_sell_range': cls.STRATEGY_PRE_SELL_RANGE,
                'down_threshold': cls.STRATEGY_DOWN_THRESHOLD,
                'up_threshold': cls.STRATEGY_UP_THRESHOLD,
                'cooldown_minutes': cls.STRATEGY_COOLDOWN_MINUTES,
            },
            'telegram': {
                'token': cls.TELEGRAM_BOT_TOKEN,
                'chat_id': cls.TELEGRAM_CHAT_ID,
            }
        }
