"""
Agent Manager - High-Level Agent Coordination

This module provides the high-level manager for agent operations and coordination.
It includes task execution, performance monitoring, and configuration management.
"""

from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent, AgentConfig
from .agent_factory import AgentFactory
import logging
import asyncio
from datetime import datetime

class AgentPerformanceMonitor:
    """Monitor and track agent performance metrics."""
    
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger("agent_performance_monitor")
    
    def record_execution(self, agent: BaseAgent, result: Dict[str, Any]):
        """Record an agent execution for performance tracking."""
        execution_record = {
            'agent_id': agent.config.agent_id,
            'agent_type': agent.config.agent_type,
            'timestamp': datetime.now().isoformat(),
            'execution_time': agent.performance_metrics.get('execution_time', 0.0),
            'success': agent.state.status == 'completed',
            'result_quality': agent.performance_metrics.get('result_quality', 0.0),
            'error_count': agent.state.error_count,
            'task_summary': str(agent.state.current_task)[:100]  # Truncate for storage
        }
        
        self.execution_history.append(execution_record)
        self.logger.debug(f"Recorded execution for agent {agent.config.agent_id}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary for all agents."""
        if not self.execution_history:
            return {'total_executions': 0, 'success_rate': 0.0, 'avg_execution_time': 0.0}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for record in self.execution_history if record['success'])
        success_rate = successful_executions / total_executions if total_executions > 0 else 0.0
        
        execution_times = [record['execution_time'] for record in self.execution_history if record['execution_time'] > 0]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
        
        return {
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'success_rate': success_rate,
            'avg_execution_time': avg_execution_time,
            'recent_executions': self.execution_history[-10:]  # Last 10 executions
        }

class AgentConfigManager:
    """Manage agent configurations and defaults."""
    
    def __init__(self):
        self.default_configs: Dict[str, Dict[str, Any]] = {
            'requirements_analysis': {
                'model_name': 'gemini-2.5-flash',
                'temperature': 0.1,
                'max_retries': 3,
                'timeout_seconds': 30
            },
            'code_generation': {
                'model_name': 'gemini-2.5-flash',
                'temperature': 0.1,
                'max_retries': 3,
                'timeout_seconds': 45
            },
            'test_generation': {
                'model_name': 'gemini-2.5-flash-lite',
                'temperature': 0.1,
                'max_retries': 2,
                'timeout_seconds': 30
            }
        }
    
    def get_default_config(self, agent_type: str) -> AgentConfig:
        """Get default configuration for an agent type."""
        defaults = self.default_configs.get(agent_type, {})
        
        return AgentConfig(
            agent_id=f"{agent_type}_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            agent_type=agent_type,
            prompt_template_id=f"{agent_type}_template",
            model_name=defaults.get('model_name', 'gemini-2.5-flash-lite'),
            temperature=defaults.get('temperature', 0.1),
            max_retries=defaults.get('max_retries', 3),
            timeout_seconds=defaults.get('timeout_seconds', 30)
        )
    
    def create_custom_config(self, agent_type: str, **kwargs) -> AgentConfig:
        """Create a custom configuration for an agent type."""
        base_config = self.get_default_config(agent_type)
        
        # Update with custom values
        for key, value in kwargs.items():
            if hasattr(base_config, key):
                setattr(base_config, key, value)
        
        return base_config

class AgentManager:
    """
    High-level manager for agent operations and coordination.
    """
    
    def __init__(self):
        self.factory = AgentFactory()
        self.performance_monitor = AgentPerformanceMonitor()
        self.config_manager = AgentConfigManager()
        self.logger = logging.getLogger("agent_manager")
    
    async def execute_task(self, agent_type: str, task: Dict[str, Any], 
                          config: Optional[AgentConfig] = None) -> Dict[str, Any]:
        """
        Execute a task using the specified agent type.
        
        Args:
            agent_type: Type of agent to use
            task: Task to execute
            config: Optional agent configuration
            
        Returns:
            Task results
        """
        try:
            # Create or get agent configuration
            if config is None:
                config = self.config_manager.get_default_config(agent_type)
            
            # Create agent
            agent = self.factory.create_agent(agent_type, config)
            
            # Execute task
            result = await agent.run(task)
            
            # Monitor performance
            self.performance_monitor.record_execution(agent, result)
            
            self.logger.info(f"Task executed successfully with agent {agent.config.agent_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            raise
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of an agent."""
        return self.factory.get_agent_status(agent_id)
    
    def get_all_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active agents."""
        return self.factory.get_all_agent_statuses()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all agents."""
        return self.performance_monitor.get_summary()
    
    def list_available_agent_types(self) -> List[str]:
        """List all available agent types."""
        return self.factory.list_agent_types()
    
    def list_active_agents(self) -> List[str]:
        """List all active agent IDs."""
        return self.factory.list_agents()
    
    def shutdown_agent(self, agent_id: str) -> bool:
        """Shutdown a specific agent."""
        return self.factory.shutdown_agent(agent_id)
    
    def shutdown_all_agents(self):
        """Shutdown all active agents."""
        self.factory.shutdown_all_agents()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'active_agents': len(self.factory.active_agents),
            'available_agent_types': self.factory.list_agent_types(),
            'performance_summary': self.performance_monitor.get_summary(),
            'agent_statuses': self.factory.get_all_agent_statuses()
        }
