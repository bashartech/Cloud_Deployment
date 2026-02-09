import logging
from typing import Optional

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Name of the logger (typically __name__ of the module using it)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    return logger

# Create a default app logger
app_logger = get_logger(__name__)

def setup_logging():
    """
    Setup logging configuration for the application.
    This function can be called at application startup to configure logging.
    """
    pass  # Basic configuration is already done above

# Example usage:
# logger = get_logger(__name__)
# logger.info("Application started")
# logger.error("An error occurred")