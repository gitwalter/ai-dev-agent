"""
Core Agent Framework - Base Agent Implementation

This module provides the foundational base class for all AI agents in the system.
It includes prompt integration, lifecycle management, performance monitoring,
and error handling capabilities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import json
from pathlib import Path

# Universal agent tracking
try:
    from utils.system.universal_agent_tracker import get_universal_tracker, AgentType, ContextType
    UNIVERSAL_TRACKING_AVAILABLE = True
except ImportError:
    UNIVERSAL_TRACKING_AVAILABLE = False

@dataclass
class AgentConfig:
    """Configuration for agent instances."""
    agent_id: str
    agent_type: str = "base_agent"
    prompt_template_id: str = "default"
    optimization_enabled: bool = True
    performance_monitoring: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.1

@dataclass
class AgentState:
    """Current state of an agent."""
    agent_id: str
    status: str = "idle"  # 'idle', 'running', 'completed', 'error'
    current_task: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    success_count: int = 0
    total_executions: int = 0

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    Provides common functionality for agent lifecycle management,
    prompt integration, performance monitoring, and error handling.
    """
    
    def __init__(self, config: AgentConfig, gemini_client=None):
        self.config = config
        self.gemini_client = gemini_client
        self.state = AgentState(agent_id=config.agent_id)
        self.logger = logging.getLogger(f"agent.{config.agent_id}")
        self.performance_metrics = {}
        
        # Universal agent tracking via logging coordinator
        self.tracking_session_id = None
        try:
            from utils.system.agent_logging_coordinator import get_logging_coordinator
            self.logging_coordinator = get_logging_coordinator()
            
            # Register this agent through the coordinator for comprehensive logging
            self.tracking_session_id = self.logging_coordinator.register_framework_agent(
                agent_id=config.agent_id,
                agent_type="base_agent",
                agent_class=self.__class__.__name__
            )
            
            if self.tracking_session_id:
                self.logger.info(f"✅ Agent {config.agent_id} registered with logging coordinator: {self.tracking_session_id}")
            else:
                self.logger.warning(f"⚠️ Failed to register {config.agent_id} with logging coordinator")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Could not connect to logging coordinator: {e}")
            self.logging_coordinator = None
            
            # Fallback to direct universal tracker
            if UNIVERSAL_TRACKING_AVAILABLE:
                try:
                    self.universal_tracker = get_universal_tracker()
                    self.tracking_session_id = self.universal_tracker.register_agent(
                        agent_id=config.agent_id,
                        agent_type=AgentType.CUSTOM_AGENT,
                        initial_context=ContextType.SYSTEM_STARTUP,
                        metadata={
                            "agent_type": config.agent_type,
                            "prompt_template_id": config.prompt_template_id,
                            "model_name": config.model_name,
                            "fallback_registration": True
                        }
                    )
                    self.logger.info(f"✅ Agent {config.agent_id} registered with fallback tracker: {self.tracking_session_id}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to register with fallback tracker: {e}")
                    self.universal_tracker = None
            else:
                self.universal_tracker = None
                self.logger.warning("⚠️ No tracking available")
        
        # Initialize prompt engineering integration
        self.prompt_system = self._initialize_prompt_system()
        self.optimization_engine = self._initialize_optimization_engine()
        
        # Initialize LLM model
        self.llm_model = self._initialize_llm_model()
    
    @property
    def name(self) -> str:
        """Agent name for backward compatibility."""
        return self.config.agent_id
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's primary task.
        
        Args:
            task: Task parameters and context
            
        Returns:
            Task results and metadata
        """
        pass
    
    @abstractmethod
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate that the task is appropriate for this agent.
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid, False otherwise
        """
        pass
    
    async def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for agent execution with full lifecycle management.
        
        Args:
            task: Task to execute
            
        Returns:
            Execution results with metadata
        """
        try:
            # Validate task
            if not self.validate_task(task):
                raise ValueError(f"Invalid task for agent {self.config.agent_id}")
            
            # Update state
            self.state.status = 'running'
            self.state.current_task = str(task)
            self.state.start_time = datetime.now()
            self.state.total_executions += 1
            
            # Execute task
            result = await self.execute(task)
            
            # Update state
            self.state.status = 'completed'
            self.state.end_time = datetime.now()
            self.state.success_count += 1
            
            # Record performance metrics
            self._record_performance_metrics(result)
            
            return result
            
        except Exception as e:
            # Handle errors
            self.state.status = 'error'
            self.state.error_count += 1
            self.logger.error(f"Agent execution failed: {e}")
            
            # Attempt recovery if configured
            if self.config.max_retries > 0 and self.state.error_count <= self.config.max_retries:
                return await self._retry_execution(task)
            else:
                raise
    
    def _initialize_prompt_system(self):
        """Initialize integration with prompt engineering system."""
        try:
            from utils.prompt_management import PromptTemplateSystem, PromptManager
            return {
                'template_system': PromptTemplateSystem(),
                'prompt_manager': PromptManager(),
                'optimizer': None  # Will be initialized if optimization enabled
            }
        except ImportError as e:
            self.logger.warning(f"Prompt system not available: {e}")
            return None
    
    def _initialize_optimization_engine(self):
        """Initialize optimization engine if enabled."""
        if self.config.optimization_enabled:
            try:
                from utils.prompt_management import AdvancedPromptOptimizer
                return AdvancedPromptOptimizer()
            except ImportError as e:
                self.logger.warning(f"Optimization engine not available: {e}")
                return None
        return None
    
    def _initialize_llm_model(self):
        """Initialize the LLM model for agent operations."""
        try:
            import streamlit as st
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            # Get API key from Streamlit secrets
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in Streamlit secrets")
            
            return ChatGoogleGenerativeAI(
                model=self.config.model_name,
                google_api_key=api_key,
                temperature=self.config.temperature,
                max_tokens=8192
            )
        except Exception as e:
            self.logger.warning(f"LLM model initialization failed: {e}")
        return None
    
    def _record_performance_metrics(self, result: Dict[str, Any]):
        """Record performance metrics for optimization."""
        if self.config.performance_monitoring and self.state.start_time and self.state.end_time:
            execution_time = (self.state.end_time - self.state.start_time).total_seconds()
            
            self.performance_metrics = {
                'execution_time': execution_time,
                'success': self.state.status == 'completed',
                'error_count': self.state.error_count,
                'success_count': self.state.success_count,
                'total_executions': self.state.total_executions,
                'success_rate': self.state.success_count / max(self.state.total_executions, 1),
                'timestamp': datetime.now().isoformat(),
                'task_type': self.config.agent_type,
                'result_quality': self._assess_result_quality(result)
            }
    
    def _assess_result_quality(self, result: Dict[str, Any]) -> float:
        """Assess the quality of the agent's result."""
        # Basic quality assessment - can be overridden by specific agents
        if 'error' in result or 'exception' in result:
            return 0.0
        if 'confidence' in result:
            return result['confidence']
        if 'quality_score' in result:
            return result['quality_score']
        return 0.8  # Default quality score
    
    async def _retry_execution(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Retry task execution with exponential backoff."""
        retry_delay = 2 ** self.state.error_count  # Exponential backoff
        self.logger.info(f"Retrying execution in {retry_delay} seconds...")
        
        await asyncio.sleep(retry_delay)
        return await self.run(task)
    
    def get_optimized_prompt(self, prompt_id: str, context: Dict[str, Any]) -> str:
        """Get an optimized prompt for the current context."""
        if not self.prompt_system:
            return f"Default prompt for {prompt_id}"
        
        try:
            if self.optimization_engine:
                # Get optimization context
                optimization_context = self._create_optimization_context(context)
                
                # Optimize prompt
                result = self.optimization_engine.optimize_prompt(
                    prompt_id=prompt_id,
                    prompt_text=self.prompt_system['prompt_manager'].get_prompt(prompt_id),
                    context=optimization_context
                )
                
                return result.optimized_prompt
            else:
                # Return standard prompt
                return self.prompt_system['prompt_manager'].get_prompt(prompt_id)
        except Exception as e:
            self.logger.warning(f"Failed to get optimized prompt: {e}")
            return f"Fallback prompt for {prompt_id}"
    
    def _create_optimization_context(self, context: Dict[str, Any]):
        """Create optimization context for prompt optimization."""
        try:
            from utils.prompt_management import OptimizationContext
            
            return OptimizationContext(
                user_id=context.get('user_id', 'default'),
                task_type=self.config.agent_type,
                agent_type=self.config.agent_type,
                usage_pattern=self.performance_metrics,
                performance_history=self._get_performance_history(),
                success_rate=self._calculate_success_rate(),
                response_time=self.performance_metrics.get('execution_time', 0.0),
                cost_per_request=context.get('cost_per_request', 0.0),
                timestamp=datetime.now()
            )
        except Exception as e:
            self.logger.warning(f"Failed to create optimization context: {e}")
            return None
    
    def _get_performance_history(self) -> List[float]:
        """Get performance history for optimization."""
        # Simple implementation - can be enhanced with persistent storage
        return [self.performance_metrics.get('execution_time', 0.0)]
    
    def _calculate_success_rate(self) -> float:
        """Calculate current success rate."""
        if self.state.total_executions == 0:
            return 1.0
        return self.state.success_count / self.state.total_executions
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            'agent_id': self.config.agent_id,
            'agent_type': self.config.agent_type,
            'status': self.state.status,
            'current_task': self.state.current_task,
            'start_time': self.state.start_time.isoformat() if self.state.start_time else None,
            'end_time': self.state.end_time.isoformat() if self.state.end_time else None,
            'performance_metrics': self.performance_metrics,
            'error_count': self.state.error_count,
            'success_count': self.state.success_count,
            'total_executions': self.state.total_executions,
            'success_rate': self._calculate_success_rate()
        }
    
    def reset_state(self):
        """Reset agent state for fresh start."""
        self.state = AgentState(agent_id=self.config.agent_id)
        self.performance_metrics = {}
    
    def add_log_entry(self, level: str, message: str):
        """Add a log entry to the agent's log."""
        if level == "info":
            self.logger.info(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "debug":
            self.logger.debug(message)
        else:
            self.logger.info(message)
    
    def add_decision(self, decision: str, rationale: str, alternatives: List[str], impact: str):
        """Add a decision to the agent's decision log."""
        if not hasattr(self, 'decisions'):
            self.decisions = []
        
        decision_entry = {
            'decision': decision,
            'rationale': rationale,
            'alternatives': alternatives,
            'impact': impact,
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.config.agent_id
        }
        self.decisions.append(decision_entry)
        self.logger.info(f"Decision recorded: {decision}")
    
    def add_artifact(self, name: str, type: str, content: Any, description: str):
        """Add an artifact to the agent's artifact collection."""
        if not hasattr(self, 'artifacts'):
            self.artifacts = {}
        
        artifact_entry = {
            'name': name,
            'type': type,
            'content': content,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.config.agent_id
        }
        self.artifacts[name] = artifact_entry
        self.logger.info(f"Artifact added: {name} ({type})")
    
    def validate_input(self, state: Dict[str, Any]) -> bool:
        """Validate input state for agent execution."""
        # Basic validation - can be overridden by specific agents
        if not isinstance(state, dict):
            return False
        
        # Check for required fields
        required_fields = ['project_context', 'project_name']
        return all(field in state for field in required_fields)
    
    def handle_error(self, state: Dict[str, Any], error: Exception, task_type: str) -> Dict[str, Any]:
        """Handle errors during agent execution."""
        self.logger.error(f"{task_type} failed: {error}")
        
        # Update state with error information
        error_state = state.copy()
        error_state["agent_outputs"] = error_state.get("agent_outputs", {})
        error_state["agent_outputs"][self.config.agent_id] = {
            "status": "failed",
            "error": str(error),
            "task_type": task_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add error to state errors list
        if "errors" not in error_state:
            error_state["errors"] = []
        error_state["errors"].append(str(error))
        
        return error_state
    
    def update_state_with_result(self, state: Dict[str, Any], result: Any, task_type: str = "generic") -> Dict[str, Any]:
        """Update state with successful execution result."""
        updated_state = state.copy()
        
        # Ensure agent_outputs exists
        if "agent_outputs" not in updated_state:
            updated_state["agent_outputs"] = {}
        
        # Add agent output
        updated_state["agent_outputs"][self.config.agent_id] = {
            "status": "success",
            "result": result,
            "task_type": task_type,
            "timestamp": datetime.now().isoformat()
        }
        
        return updated_state
    
    def validate_gemini_config(self) -> bool:
        """Validate Gemini client configuration."""
        # Check if config exists
        if not hasattr(self, 'config') or self.config is None:
            return False
        
        # Check if client exists
        if not hasattr(self, 'gemini_client') or self.gemini_client is None:
            return False
        
        # Check if client has generate_content method
        if not hasattr(self.gemini_client, 'generate_content'):
            return False
        
        # Config parameters must exist and not be empty
        if not hasattr(self.config, 'parameters') or not self.config.parameters:
            return False
        
        return True
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Gemini client."""
        if not self.validate_gemini_config():
            raise ValueError("Invalid Gemini configuration")
        
        try:
            # Use the client to generate response
            response = await self.gemini_client.generate_content(prompt)
            
            # Extract text from response
            if hasattr(response, 'text'):
                if response.text and response.text.strip():
                    return response.text
                else:
                    raise ValueError("Empty or invalid response from Gemini API")
            elif hasattr(response, 'parts') and response.parts:
                # Handle parts structure directly
                return response.parts[0].text
            elif hasattr(response, 'candidates') and response.candidates:
                try:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content'):
                        if hasattr(candidate.content, 'parts'):
                            return candidate.content.parts[0].text
                        else:
                            return str(candidate.content)
                    else:
                        return str(candidate)
                except (IndexError, TypeError):
                    # Handle mock objects or empty candidates
                    return str(response)
            else:
                return str(response)
                
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise
    
    def parse_json_response(self, response: str) -> dict:
        """Parse JSON response with error handling."""
        import json
        import re
        
        # Clean the response - remove code blocks if present
        if "```json" in response:
            # Extract JSON from code blocks
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
        elif "```" in response:
            # Generic code blocks
            json_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
        
        # Remove trailing commas
        response = re.sub(r',(\s*[}\]])', r'\1', response)
        
        # Remove trailing commas in arrays
        response = re.sub(r',(\s*\])', r'\1', response)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}")
            # Return a fallback dict instead of raising
            return {"error": "JSON parsing failed", "original_response": response}
    
    def prepare_prompt(self, state: dict, **kwargs) -> str:
        """Prepare prompt using template and context."""
        if not hasattr(self.config, 'prompt_template'):
            raise ValueError("No prompt template configured")
        
        # Merge state and kwargs for template formatting
        context = {**state, **kwargs}
        
        try:
            # Get base prompt from template
            base_prompt = self.config.prompt_template.format(**context)
            
            # Add JSON format instructions if not already present
            if "JSON" not in base_prompt and "format" not in base_prompt:
                format_instruction = "\n\nPlease provide your response in valid JSON format."
                base_prompt += format_instruction
            
            return base_prompt
        except KeyError as e:
            self.logger.error(f"Missing template variable: {e}")
            raise ValueError(f"Missing template variable: {e}")
        except Exception as e:
            self.logger.error(f"Error preparing prompt: {e}")
            raise