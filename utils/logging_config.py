"""
Logging configuration for the AI Development Agent system.
Provides structured logging with multiple handlers and formatters.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

from models.config import LoggingConfig


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        config: Logging configuration. If None, uses default configuration.
    """
    if config is None:
        config = LoggingConfig()
    
    # Create logs directory if it doesn't exist
    log_file_path = Path(config.log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    if config.enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.log_level))
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if config.enable_file_logging:
        file_handler = logging.handlers.RotatingFileHandler(
            config.log_file,
            maxBytes=config.max_log_size,
            backupCount=config.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, config.log_level))
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("google.generativeai").setLevel(logging.INFO)
    
    # Log startup message
    logger = logging.getLogger("logging_config")
    logger.info("Logging system initialized")
    logger.info(f"Log level: {config.log_level}")
    logger.info(f"Log file: {config.log_file}")
    logger.info(f"Console logging: {config.enable_console_logging}")
    logger.info(f"File logging: {config.enable_file_logging}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """
    Set the log level for all loggers.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.getLogger().setLevel(getattr(logging, level.upper()))
    
    # Update all handlers
    for handler in logging.getLogger().handlers:
        handler.setLevel(getattr(logging, level.upper()))


def add_file_handler(
    log_file: str,
    level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Add a file handler to the root logger.
    
    Args:
        log_file: Path to log file
        level: Log level
        max_bytes: Maximum file size before rotation
        backup_count: Number of backup files to keep
    """
    # Create directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create handler
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add to root logger
    logging.getLogger().addHandler(handler)


def setup_agent_logging(agent_name: str, log_dir: str = "./logs/agents") -> logging.Logger:
    """
    Set up logging for a specific agent.
    
    Args:
        agent_name: Name of the agent
        log_dir: Directory for agent logs
        
    Returns:
        Configured logger for the agent
    """
    # Create agent log directory
    agent_log_dir = Path(log_dir)
    agent_log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create agent logger
    agent_logger = logging.getLogger(f"agent.{agent_name}")
    agent_logger.setLevel(logging.INFO)
    
    # Create agent-specific file handler
    agent_log_file = agent_log_dir / f"{agent_name}.log"
    agent_handler = logging.handlers.RotatingFileHandler(
        agent_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    agent_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    agent_handler.setFormatter(formatter)
    
    # Add handler to agent logger
    agent_logger.addHandler(agent_handler)
    
    return agent_logger


def setup_workflow_logging(log_dir: str = "./logs/workflow") -> logging.Logger:
    """
    Set up logging for workflow execution.
    
    Args:
        log_dir: Directory for workflow logs
        
    Returns:
        Configured logger for workflow
    """
    # Create workflow log directory
    workflow_log_dir = Path(log_dir)
    workflow_log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create workflow logger
    workflow_logger = logging.getLogger("workflow")
    workflow_logger.setLevel(logging.INFO)
    
    # Create workflow-specific file handler
    workflow_log_file = workflow_log_dir / "workflow.log"
    workflow_handler = logging.handlers.RotatingFileHandler(
        workflow_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    workflow_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    workflow_handler.setFormatter(formatter)
    
    # Add handler to workflow logger
    workflow_logger.addHandler(workflow_handler)
    
    return workflow_logger


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class.
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def log_method_call(self, method_name: str, **kwargs):
        """Log a method call with parameters."""
        self.logger.debug(f"Calling {method_name} with params: {kwargs}")
    
    def log_method_result(self, method_name: str, result):
        """Log a method result."""
        self.logger.debug(f"{method_name} returned: {result}")
    
    def log_error(self, method_name: str, error: Exception):
        """Log an error in a method."""
        self.logger.error(f"Error in {method_name}: {str(error)}", exc_info=True)
