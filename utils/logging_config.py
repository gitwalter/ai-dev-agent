"""
Logging configuration module for the AI Development Agent system.
Provides centralized logging setup and configuration.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_logging: bool = True,
    file_logging: bool = True,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Set up centralized logging for the AI Development Agent system.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (defaults to ./logs/agent.log)
        console_logging: Whether to enable console logging
        file_logging: Whether to enable file logging
        log_format: Custom log format string
        
    Returns:
        Configured logger instance
    """
    
    # Ensure logs directory exists
    if log_file is None:
        log_file = "./logs/agent.log"
    
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure log format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Console handler
    if console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if file_logging:
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Create main logger
    logger = logging.getLogger("logging_config")
    
    # Log initialization success
    logger.info("Logging system initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Console logging: {console_logging}")
    logger.info(f"File logging: {file_logging}")
    
    return root_logger


def setup_agent_logging(agent_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging for a specific agent.
    
    Args:
        agent_name: Name of the agent
        log_level: Logging level for the agent
        
    Returns:
        Configured logger for the agent
    """
    
    # Ensure main logging is set up
    if not logging.getLogger().handlers:
        setup_logging(log_level=log_level)
    
    # Create agent-specific logger
    agent_logger = logging.getLogger(f"agent.{agent_name}")
    agent_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    return agent_logger


def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Get a logger with the specified name and level.
    
    Args:
        name: Logger name
        log_level: Logging level
        
    Returns:
        Configured logger
    """
    
    # Ensure main logging is set up
    if not logging.getLogger().handlers:
        setup_logging(log_level=log_level)
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    return logger


def configure_library_logging():
    """Configure logging for external libraries to reduce noise."""
    
    # Reduce httpx logging
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Reduce urllib3 logging
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Reduce google auth logging
    logging.getLogger("google.auth").setLevel(logging.WARNING)
    logging.getLogger("google.auth.transport").setLevel(logging.WARNING)
    
    # Reduce langchain logging
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("langchain_core").setLevel(logging.WARNING)
    
    # Reduce other noisy libraries
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)


# Initialize library logging configuration
configure_library_logging()

