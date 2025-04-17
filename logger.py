import logging
import os
from datetime import datetime

def setup_logger():
    log_format = "%(asctime)s [%(levelname)s]: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set default level to INFO

    # Remove any existing handlers to avoid duplicate logging
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create log directory
    log_dir = './logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Get current date for log filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f'app_{current_date}.log')
    
    # File handler with rotation
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(file_handler)
    
    # Console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(console_handler)

    # Suppress third-party library logs
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    return logger

# Initialize the logger
logger = setup_logger()

# Convenience methods
def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    logger.critical(msg, *args, **kwargs)