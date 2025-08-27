#!/usr/bin/env python3
"""
LangChain and LangGraph Logging Integration.
Provides comprehensive logging and observability using LangSmith and LangChain patterns.

Agent logs can be viewed at: https://smith.langchain.com/
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

try:
    from langsmith import Client
    from langchain.callbacks import LangChainTracer
    from langchain.callbacks.manager import CallbackManager
    from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
    from langchain.callbacks.file import FileCallbackHandler
    from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
    from langchain.schema.output import LLMResult
    from langchain.schema.runnable import RunnableConfig
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available for advanced logging")

logger = logging.getLogger(__name__)


class LangChainLoggingManager:
    """
    Comprehensive logging manager for LangChain and LangGraph workflows.
    Integrates with LangSmith for observability and provides detailed agent logs.
    """
    
    def __init__(self, project_name: str = "ai-dev-agent", enable_langsmith: bool = True):
        """
        Initialize the logging manager.
        
        Args:
            project_name: Name of the project for LangSmith
            enable_langsmith: Whether to enable LangSmith integration
        """
        self.project_name = project_name
        self.enable_langsmith = enable_langsmith and LANGCHAIN_AVAILABLE
        self.langsmith_client = None
        self.callback_manager = None
        self.log_dir = Path("logs/langchain")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup LangSmith and callback managers."""
        if not self.enable_langsmith:
            logger.info("LangSmith integration disabled")
            return
            
        try:
            # Setup LangSmith environment variables
            self._setup_langsmith_env()
            
            # Initialize LangSmith client with API key from secrets
            try:
                import streamlit as st
                api_key = st.secrets.get("LANGSMITH_API_KEY")
                if api_key:
                    self.langsmith_client = Client(api_key=api_key)
                    logger.info("LangSmith client initialized with API key from secrets")
                else:
                    self.langsmith_client = Client()
                    logger.warning("LangSmith client initialized without API key")
            except Exception as e:
                logger.warning(f"Failed to initialize LangSmith client with API key: {e}")
                self.langsmith_client = Client()
            
            # Create callback manager with multiple handlers
            self.callback_manager = CallbackManager([
                LangChainTracer(project_name=self.project_name),
                StreamingStdOutCallbackHandler(),
                FileCallbackHandler(str(self.log_dir / "langchain_calls.jsonl"))
            ])
            
            logger.info(f"LangChain logging initialized with project: {self.project_name}")
            logger.info(f"Log directory: {self.log_dir}")
            
        except Exception as e:
            logger.warning(f"Failed to setup LangSmith: {e}")
            self.enable_langsmith = False
            
    def _setup_langsmith_env(self):
        """Setup LangSmith environment variables from Streamlit secrets."""
        try:
            import streamlit as st
            
            # Get LangSmith configuration from Streamlit secrets
            langsmith_tracing = st.secrets.get("LANGSMITH_TRACING", "true")
            langsmith_endpoint = st.secrets.get("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
            langsmith_api_key = st.secrets.get("LANGSMITH_API_KEY")
            langsmith_project = st.secrets.get("LANGSMITH_PROJECT", self.project_name)
            
            # Set environment variables
            os.environ["LANGCHAIN_TRACING_V2"] = langsmith_tracing
            os.environ["LANGCHAIN_ENDPOINT"] = langsmith_endpoint
            os.environ["LANGCHAIN_PROJECT"] = langsmith_project
            
            if langsmith_api_key:
                os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
                logger.info("LangSmith API key configured from Streamlit secrets")
            else:
                logger.warning("LangSmith API key not found in Streamlit secrets")
                
        except Exception as e:
            logger.warning(f"Failed to load LangSmith config from Streamlit secrets: {e}")
            # Fallback to default values
            if not os.getenv("LANGCHAIN_TRACING_V2"):
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
            if not os.getenv("LANGCHAIN_ENDPOINT"):
                os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
            if not os.getenv("LANGCHAIN_PROJECT"):
                os.environ["LANGCHAIN_PROJECT"] = self.project_name
        
    def get_callback_manager(self) -> Optional[CallbackManager]:
        """Get the callback manager for LangChain operations."""
        return self.callback_manager
        
    def get_runnable_config(self, session_id: str = None, tags: List[str] = None) -> RunnableConfig:
        """
        Get RunnableConfig for LangChain operations with proper metadata.
        
        Args:
            session_id: Session identifier for tracing
            tags: Tags for categorization
            
        Returns:
            RunnableConfig with callbacks and metadata
        """
        config = {}
        
        if self.callback_manager:
            config["callbacks"] = self.callback_manager
            
        if session_id:
            # LangGraph expects thread_id in configurable, not session_id
            config["configurable"] = {"thread_id": session_id}
            
        if tags:
            config["tags"] = tags or []
            
        return config
        
    def log_agent_execution(self, agent_name: str, input_data: Dict[str, Any], 
                           output_data: Dict[str, Any], execution_time: float,
                           session_id: str = None, success: bool = True):
        """
        Log agent execution with detailed information.
        
        Args:
            agent_name: Name of the agent
            input_data: Input data to the agent
            output_data: Output data from the agent
            execution_time: Execution time in seconds
            session_id: Session identifier
            success: Whether execution was successful
        """
        # Log to standard logging
        log_level = logging.INFO if success else logging.ERROR
        logger.log(log_level, f"Agent {agent_name} execution: {execution_time:.2f}s - {'SUCCESS' if success else 'FAILED'}")
        
        # Log to LangSmith if available
        if self.enable_langsmith and self.langsmith_client:
            try:
                self.langsmith_client.create_run(
                    project_name=f"{self.project_name}-agents",
                    name=f"{agent_name}_execution",
                    run_type="chain",
                    inputs=input_data,
                    outputs=output_data,
                    tags=[agent_name, "agent_execution"],
                    metadata={
                        "execution_time": execution_time,
                        "success": success,
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to log to LangSmith: {e}")
                
    def log_workflow_step(self, step_name: str, state: Dict[str, Any], 
                         session_id: str = None, step_type: str = "workflow_step"):
        """
        Log workflow step execution.
        
        Args:
            step_name: Name of the workflow step
            state: Current workflow state
            session_id: Session identifier
            step_type: Type of step (workflow_step, agent_step, etc.)
        """
        logger.info(f"Workflow step: {step_name}")
        
        if self.enable_langsmith and self.langsmith_client:
            try:
                # Extract relevant state information
                state_summary = {
                    "current_step": state.get("current_step"),
                    "project_context": state.get("project_context", "")[:200] + "...",
                    "errors": state.get("errors", []),
                    "agent_outputs_count": len(state.get("agent_outputs", {})),
                    "completed_agents": state.get("completed_agents", [])
                }
                
                self.langsmith_client.create_run(
                    project_name=f"{self.project_name}-workflow",
                    name=f"{step_name}_step",
                    run_type="chain",
                    inputs={"step_name": step_name, "state_summary": state_summary},
                    outputs={"state": state},
                    tags=[step_type, "workflow"],
                    metadata={
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to log workflow step to LangSmith: {e}")
                
    def log_llm_call(self, model_name: str, prompt: str, response: str, 
                    execution_time: float, session_id: str = None):
        """
        Log individual LLM calls.
        
        Args:
            model_name: Name of the LLM model
            prompt: Input prompt
            response: LLM response
            execution_time: Execution time in seconds
            session_id: Session identifier
        """
        logger.debug(f"LLM call ({model_name}): {execution_time:.2f}s")
        
        if self.enable_langsmith and self.langsmith_client:
            try:
                self.langsmith_client.create_run(
                    project_name=f"{self.project_name}-llm",
                    name=f"{model_name}_call",
                    run_type="llm",
                    inputs={"prompt": prompt},
                    outputs={"response": response},
                    tags=["llm_call", model_name],
                    metadata={
                        "execution_time": execution_time,
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to log LLM call to LangSmith: {e}")
                
    def log_error(self, error: Exception, context: Dict[str, Any] = None, 
                 session_id: str = None, agent_name: str = None):
        """
        Log errors with context.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            session_id: Session identifier
            agent_name: Name of the agent (if applicable)
        """
        error_msg = f"Error in {agent_name or 'system'}: {str(error)}"
        logger.error(error_msg)
        
        if self.enable_langsmith and self.langsmith_client:
            try:
                self.langsmith_client.create_run(
                    project_name=f"{self.project_name}-errors",
                    name="error_log",
                    run_type="tool",
                    inputs={"error_type": type(error).__name__, "context": context or {}},
                    outputs={"error_message": str(error)},
                    tags=["error", agent_name] if agent_name else ["error"],
                    metadata={
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "traceback": str(error)
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to log error to LangSmith: {e}")
                
    def log_performance_metrics(self, metrics: Dict[str, Any], session_id: str = None):
        """
        Log performance metrics.
        
        Args:
            metrics: Dictionary of performance metrics
            session_id: Session identifier
        """
        logger.info(f"Performance metrics: {metrics}")
        
        if self.enable_langsmith and self.langsmith_client:
            try:
                self.langsmith_client.create_run(
                    project_name=f"{self.project_name}-metrics",
                    name="performance_metrics",
                    run_type="tool",
                    inputs={},
                    outputs={"metrics": metrics},
                    tags=["performance", "metrics"],
                    metadata={
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to log metrics to LangSmith: {e}")
                
    def create_session_logger(self, session_id: str) -> 'SessionLogger':
        """
        Create a session-specific logger.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionLogger instance
        """
        return SessionLogger(self, session_id)
        
    def get_langsmith_url(self, run_id: str) -> str:
        """
        Get LangSmith URL for a specific run.
        
        Args:
            run_id: Run identifier
            
        Returns:
            LangSmith URL
        """
        if self.enable_langsmith:
            return f"https://smith.langchain.com/runs/{run_id}"
        return "LangSmith not enabled"


class SessionLogger:
    """
    Session-specific logger for tracking individual workflow sessions.
    """
    
    def __init__(self, manager: LangChainLoggingManager, session_id: str):
        """
        Initialize session logger.
        
        Args:
            manager: Parent logging manager
            session_id: Session identifier
        """
        self.manager = manager
        self.session_id = session_id
        self.logger = logging.getLogger(f"session.{session_id}")
        
    def log_agent_execution(self, agent_name: str, input_data: Dict[str, Any], 
                           output_data: Dict[str, Any], execution_time: float, success: bool = True):
        """Log agent execution for this session."""
        self.manager.log_agent_execution(
            agent_name, input_data, output_data, execution_time, 
            self.session_id, success
        )
        
    def log_workflow_step(self, step_name: str, state: Dict[str, Any], step_type: str = "workflow_step"):
        """Log workflow step for this session."""
        self.manager.log_workflow_step(step_name, state, self.session_id, step_type)
        
    def log_llm_call(self, model_name: str, prompt: str, response: str, execution_time: float):
        """Log LLM call for this session."""
        self.manager.log_llm_call(model_name, prompt, response, execution_time, self.session_id)
        
    def log_error(self, error: Exception, context: Dict[str, Any] = None, agent_name: str = None):
        """Log error for this session."""
        self.manager.log_error(error, context, self.session_id, agent_name)
        
    def log_performance_metrics(self, metrics: Dict[str, Any]):
        """Log performance metrics for this session."""
        self.manager.log_performance_metrics(metrics, self.session_id)


# Global logging manager instance
_logging_manager = None

def get_logging_manager(project_name: str = "ai-dev-agent", enable_langsmith: bool = True) -> LangChainLoggingManager:
    """
    Get or create the global logging manager.
    
    Args:
        project_name: Name of the project
        enable_langsmith: Whether to enable LangSmith
        
    Returns:
        LangChainLoggingManager instance
    """
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LangChainLoggingManager(project_name, enable_langsmith)
    return _logging_manager

def setup_langchain_logging(project_name: str = "ai-dev-agent", enable_langsmith: bool = True):
    """
    Setup LangChain logging for the application.
    
    Args:
        project_name: Name of the project
        enable_langsmith: Whether to enable LangSmith
    """
    global _logging_manager
    _logging_manager = LangChainLoggingManager(project_name, enable_langsmith)
    logger.info(f"LangChain logging setup complete for project: {project_name}")
    return _logging_manager
