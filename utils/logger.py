"""Logging configuration for the application."""
import logging
import sys
from pathlib import Path
from config.settings import LOG_LEVEL, LOG_FILE

# Create logs directory if it doesn't exist
log_dir = Path(LOG_FILE).parent
log_dir.mkdir(exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    """Get or create a logger instance.
    
    Args:
        name: Name of the logger (usually __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LOG_LEVEL)
        
        # File handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(LOG_LEVEL)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.setLevel(LOG_LEVEL)
    
    return logger
