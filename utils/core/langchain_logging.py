"""
LangChain-specific logging configuration for the AI Development Agent system.
Provides specialized logging setup for LangChain operations and workflows.
"""

import logging
from pathlib import Path
from typing import Optional
from .logging_config import setup_logging, get_logger


def setup_langchain_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up LangChain-specific logging configuration.
    
    Args:
        log_level: Logging level for LangChain operations
        
    Returns:
        Configured logger for LangChain operations
    """
    
    # Ensure main logging is set up
    if not logging.getLogger().handlers:
        setup_logging(log_level=log_level)
    
    # Create LangChain-specific logger
    langchain_logger = logging.getLogger("langchain_operations")
    langchain_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Create LangChain-specific log file
    langchain_log_file = "./logs/langchain/langchain_operations.log"
    log_path = Path(langchain_log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add LangChain-specific file handler if not already present
    langchain_file_handler = None
    for handler in langchain_logger.handlers:
        if isinstance(handler, logging.FileHandler) and "langchain_operations.log" in handler.baseFilename:
            langchain_file_handler = handler
            break
    
    if not langchain_file_handler:
        langchain_file_handler = logging.FileHandler(langchain_log_file, mode='a', encoding='utf-8')
        langchain_file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Use same format as main logging
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        langchain_file_handler.setFormatter(formatter)
        langchain_logger.addHandler(langchain_file_handler)
    
    return langchain_logger


def configure_langchain_library_logging():
    """Configure logging levels for LangChain libraries to reduce noise."""
    
    # Set appropriate levels for LangChain components
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("langchain_core").setLevel(logging.WARNING)
    logging.getLogger("langchain_community").setLevel(logging.WARNING)
    logging.getLogger("langchain_experimental").setLevel(logging.WARNING)
    
    # LangGraph specific logging
    logging.getLogger("langgraph").setLevel(logging.INFO)
    
    # LangSmith logging
    logging.getLogger("langsmith").setLevel(logging.WARNING)
    
    # Reduce HTTP request logging from LangChain
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_langchain_logger(component: str = "general") -> logging.Logger:
    """
    Get a LangChain-specific logger for a component.
    
    Args:
        component: Name of the LangChain component
        
    Returns:
        Configured logger for the component
    """
    
    # Ensure LangChain logging is set up
    setup_langchain_logging()
    
    # Create component-specific logger
    component_logger = logging.getLogger(f"langchain_operations.{component}")
    
    return component_logger


def log_langchain_operation(operation: str, details: Optional[str] = None, level: str = "INFO"):
    """
    Log a LangChain operation with standardized format.
    
    Args:
        operation: Name of the operation
        details: Optional details about the operation
        level: Logging level
    """
    
    logger = get_langchain_logger()
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    message = f"LangChain Operation: {operation}"
    if details:
        message += f" - {details}"
    
    logger.log(log_level, message)


# Initialize LangChain library logging configuration
configure_langchain_library_logging()


class LoggingManager:
    """
    Legacy compatibility class for logging management.
    Provides backward compatibility with existing code.
    """
    
    def __init__(self):
        """Initialize logging manager."""
        self.loggers = {}
        setup_langchain_logging()
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger."""
        if name not in self.loggers:
            self.loggers[name] = get_langchain_logger(name)
        return self.loggers[name]
    
    def setup_logging(self, log_level: str = "INFO"):
        """Set up logging with specified level."""
        setup_langchain_logging(log_level)
    
    def create_session_logger(self, session_id: str) -> logging.Logger:
        """
        Create a session-specific logger.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session-specific logger
        """
        session_logger_name = f"session_{session_id}"
        if session_logger_name not in self.loggers:
            session_logger = get_langchain_logger(session_logger_name)
            self.loggers[session_logger_name] = session_logger
            log_langchain_operation(f"Created session logger for {session_id}")
        
        return self.loggers[session_logger_name]
    
    def log_operation(self, operation: str, details: Optional[str] = None):
        """Log an operation."""
        log_langchain_operation(operation, details)


def get_logging_manager(*args, **kwargs) -> LoggingManager:
    """Get the global logging manager instance."""
    global _logging_manager
    if '_logging_manager' not in globals():
        _logging_manager = LoggingManager()
    
    # Handle additional parameters for compatibility
    enable_langsmith = kwargs.get('enable_langsmith', False)
    if enable_langsmith:
        _logging_manager.log_operation("LangSmith logging enabled")
    
    return _logging_manager


# Export commonly used functions
__all__ = [
    "setup_langchain_logging",
    "configure_langchain_library_logging", 
    "get_langchain_logger",
    "log_langchain_operation",
    "LoggingManager",
    "get_logging_manager"
]
