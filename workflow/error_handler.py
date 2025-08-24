"""
Error Handler for AI Development Agent.
Handles errors and exceptions in the workflow.
"""

import logging
from typing import Dict, Any
from models.state import AgentState


class ErrorHandler:
    """
    Handles errors and exceptions in the workflow.
    """
    
    def __init__(self):
        """Initialize the error handler."""
        self.logger = logging.getLogger("error_handler")
        
    def handle_workflow_error(self, state: AgentState) -> AgentState:
        """
        Handle workflow errors.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        self.logger.error("Handling workflow error")
        
        # Add error information to state
        if "errors" not in state:
            state["errors"] = []
            
        error_info = {
            "task": state.get("current_task", "unknown"),
            "agent": state.get("current_agent", "unknown"),
            "timestamp": "2024-01-01T00:00:00Z",
            "retry_count": state.get("retry_count", 0)
        }
        
        state["errors"].append(error_info)
        
        # Increment retry count
        state["retry_count"] = state.get("retry_count", 0) + 1
        
        # Check if we should retry or fail
        max_retries = 3
        if state["retry_count"] <= max_retries:
            self.logger.info(f"Retrying task (attempt {state['retry_count']}/{max_retries})")
            state["current_task"] = "retry_task"
        else:
            self.logger.error("Max retries exceeded, marking workflow as failed")
            state["current_task"] = "workflow_failed"
            
        return state
    
    def retry_failed_task(self, state: AgentState) -> AgentState:
        """
        Retry a failed task.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        self.logger.info("Retrying failed task")
        
        # Reset current task to retry
        failed_task = state.get("current_task", "requirements_analysis")
        state["current_task"] = failed_task
        
        return state
    
    def handle_agent_error(self, state: AgentState, error: Exception, agent_name: str) -> AgentState:
        """
        Handle agent-specific errors.
        
        Args:
            state: Current workflow state
            error: The exception that occurred
            agent_name: Name of the agent that failed
            
        Returns:
            Updated state
        """
        self.logger.error(f"Agent {agent_name} failed: {str(error)}")
        
        # Add error to state
        if "errors" not in state:
            state["errors"] = []
            
        error_info = {
            "agent": agent_name,
            "error": str(error),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        state["errors"].append(error_info)
        
        # Set current agent
        state["current_agent"] = agent_name
        
        return state
    
    def handle_validation_error(self, state: AgentState, error: Exception, field: str) -> AgentState:
        """
        Handle validation errors.
        
        Args:
            state: Current workflow state
            error: The validation error
            field: Field that failed validation
            
        Returns:
            Updated state
        """
        self.logger.error(f"Validation error for field {field}: {str(error)}")
        
        # Add warning to state
        if "warnings" not in state:
            state["warnings"] = []
            
        warning_info = {
            "type": "validation_error",
            "field": field,
            "message": str(error),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        state["warnings"].append(warning_info)
        
        return state
    
    def cleanup_after_error(self, state: AgentState) -> AgentState:
        """
        Clean up resources after an error.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        self.logger.info("Cleaning up after error")
        
        # Reset error-related state
        state["current_task"] = "error_cleanup"
        state["human_approval_needed"] = False
        
        return state
