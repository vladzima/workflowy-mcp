"""Configuration management for WorkFlowy MCP server."""

import logging
import logging.handlers
import os
from pathlib import Path

from .models.config import ServerConfig

# Only load .env in development mode or if explicitly requested
# In production, MCP clients provide environment variables directly
if os.getenv("WORKFLOWY_DEV_MODE") or os.getenv("WORKFLOWY_LOAD_ENV"):
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        # python-dotenv is optional - only needed for development
        pass


def setup_logging(config: ServerConfig | None = None) -> None:
    """Setup logging configuration.

    Args:
        config: Optional server configuration. If not provided,
               will load from environment.
    """
    if config is None:
        try:
            config = ServerConfig()  # type: ignore[call-arg]
        except Exception:
            # If config loading fails, use defaults
            log_level = os.getenv("LOG_LEVEL", "INFO")
            log_file = os.getenv("LOG_FILE")
    else:
        log_level = config.log_level
        log_file = os.getenv("LOG_FILE")

    # Convert log level string to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    if isinstance(log_level, str):
        log_level = level_map.get(log_level.upper(), logging.INFO)  # type: ignore[assignment]

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if configured
    if log_file:
        try:
            # Create log directory if needed
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Use rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            logging.warning(f"Failed to setup file logging: {str(e)}")

    # Set levels for specific loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logging.info(f"Logging configured at level: {logging.getLevelName(log_level)}")
