import logging
import os
from datetime import datetime

def setup_logger(log_level=logging.INFO, log_file=None):
    """
    Set up a logger that logs both to the console and to a file.

    :param log_level: The logging level - default INFO
    :param log_file: The log file path - default logs/thermal_control_YYYY-MM-DD.log)
    
    :returns: A configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_file is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
    
        # Create log file with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = os.path.join(log_dir, f'thermal_control_{timestamp}.log')

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Log initial message
    logger.info(f"Logging initialized. Log file: {log_file}")

    return logger


def get_logger(log_level=logging.INFO):
    """
    Gets the configured logger. If it is not configured, apply the default settings.
    """
    logger = logging.getLogger()

    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        return setup_logger(log_level=log_level)
    
    return logger
