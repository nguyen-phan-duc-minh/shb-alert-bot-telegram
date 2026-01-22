import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Global logger cache
_loggers = {}

def setup_logger(name='shb_bot', log_file='logs/bot.log', level=logging.INFO,
                 max_bytes=10485760, backup_count=5):
    """
    Setup logger with file rotation and console output
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        max_bytes: Max log file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if name in _loggers:
        return _loggers[name]
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    _loggers[name] = logger
    return logger

def get_logger(name=None):
    """
    Get or create a logger instance
    
    Args:
        name: Logger name (default: calling module name)
        
    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        name = 'shb_bot'
    
    if name in _loggers:
        return _loggers[name]
    
    # Get log level from environment
    from core.config import Config
    
    level_str = Config.LOG_LEVEL.upper()
    level = getattr(logging, level_str, logging.INFO)
    
    return setup_logger(
        name=name,
        log_file=Config.LOG_FILE,
        level=level,
        max_bytes=Config.LOG_MAX_BYTES,
        backup_count=Config.LOG_BACKUP_COUNT
    )
