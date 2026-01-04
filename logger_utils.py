"""
Logging utilities for weather alert bot.
Provides centralized logging configuration and utilities.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        """Format log record with colors."""
        if sys.stdout.isatty():  # Only use colors if outputting to terminal
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset = self.COLORS['RESET']
            record.levelname = f"{color}{record.levelname}{reset}"
        
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    use_colors: bool = True,
    include_timestamp: bool = True
) -> logging.Logger:
    """
    Setup comprehensive logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        use_colors: Whether to use colored output in console
        include_timestamp: Whether to include timestamp in logs
        
    Returns:
        Root logger instance
    """
    # create formatters
    if include_timestamp:
        console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    else:
        console_format = '%(name)s - %(levelname)s - %(message)s'
        file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    if use_colors:
        console_formatter = ColoredFormatter(console_format)
    else:
        console_formatter = logging.Formatter(console_format)
    
    console_handler.setFormatter(console_formatter)
    
    # setup handlers list
    handlers = [console_handler]
    
    # setup file handler if log file specified
    if log_file:
        # create log directory if needed
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all logs
    
    # remove existing handlers
    root_logger.handlers.clear()
    
    # add our handlers
    for handler in handlers:
        root_logger.addHandler(handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """
    Log exception with full traceback.
    
    Args:
        logger: Logger instance
        exception: Exception to log
        context: Optional context message
    """
    if context:
        logger.error(f"{context}: {str(exception)}", exc_info=True)
    else:
        logger.error(f"exception occurred: {str(exception)}", exc_info=True)


class LoggerContext:
    """Context manager for temporary logging configuration."""
    
    def __init__(self, log_level: str):
        """
        Initialize context manager.
        
        Args:
            log_level: Temporary log level
        """
        self.log_level = log_level
        self.original_level = None
        self.logger = logging.getLogger()
    
    def __enter__(self):
        """Enter context - set new log level."""
        self.original_level = self.logger.level
        self.logger.setLevel(getattr(logging, self.log_level.upper()))
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - restore original log level."""
        self.logger.setLevel(self.original_level)


def create_daily_log_file(base_name: str = "weather_alert") -> str:
    """
    Create a daily log file with date in filename.
    
    Args:
        base_name: Base name for log file
        
    Returns:
        Log file path
    """
    date_str = datetime.now().strftime("%Y%m%d")
    return f"{base_name}_{date_str}.log"


# pre-configured logging setups for common scenarios

def setup_production_logging():
    """Setup logging for production environment."""
    log_file = create_daily_log_file()
    return setup_logging(
        log_level="INFO",
        log_file=log_file,
        use_colors=False,
        include_timestamp=True
    )


def setup_development_logging():
    """Setup logging for development environment."""
    return setup_logging(
        log_level="DEBUG",
        log_file="development.log",
        use_colors=True,
        include_timestamp=True
    )


def setup_quiet_logging():
    """Setup minimal logging (warnings and errors only)."""
    return setup_logging(
        log_level="WARNING",
        use_colors=True,
        include_timestamp=False
    )

