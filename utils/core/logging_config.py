"""
Core logging configuration for agent-specific logging.
Provides specialized logging setup for individual agents.
"""

import logging
from typing import Optional
from pathlib import Path

# Import from parent logging_config
import sys
sys.path.append(str(Path(__file__).parent.parent))
from logging_config import setup_logging, get_logger


def setup_agent_logging(agent_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging for a specific agent with agent-specific configuration.
    
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
    
    # Create agent-specific log file if needed
    agent_log_file = f"./logs/agents/{agent_name}.log"
    log_path = Path(agent_log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add agent-specific file handler if not already present
    agent_file_handler = None
    for handler in agent_logger.handlers:
        if isinstance(handler, logging.FileHandler) and handler.baseFilename.endswith(f"{agent_name}.log"):
            agent_file_handler = handler
            break
    
    if not agent_file_handler:
        agent_file_handler = logging.FileHandler(agent_log_file, mode='a', encoding='utf-8')
        agent_file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Use same format as main logging
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        agent_file_handler.setFormatter(formatter)
        agent_logger.addHandler(agent_file_handler)
    
    return agent_logger


def setup_workflow_logging(workflow_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging for workflow components.
    
    Args:
        workflow_name: Name of the workflow
        log_level: Logging level
        
    Returns:
        Configured logger for the workflow
    """
    
    return get_logger(f"workflow.{workflow_name}", log_level)


def setup_utils_logging(utils_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging for utility components.
    
    Args:
        utils_name: Name of the utility
        log_level: Logging level
        
    Returns:
        Configured logger for the utility
    """
    
    return get_logger(f"utils.{utils_name}", log_level)

