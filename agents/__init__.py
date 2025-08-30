"""
Agent System - Main Entry Point

This module provides the main entry point for the agent system, including
agent registration, management, and unified interfaces.
"""

from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent, AgentConfig, AgentState
from .agent_factory import AgentFactory
from .agent_manager import AgentManager, AgentPerformanceMonitor, AgentConfigManager
from .requirements_analysis_agent import RequirementsAnalysisAgent

# Global agent manager instance
_agent_manager = None

def get_agent_manager() -> AgentManager:
    """Get the global agent manager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
        _register_default_agents(_agent_manager)
    return _agent_manager

def _register_default_agents(manager: AgentManager):
    """Register default agent types with the factory."""
    factory = manager.factory
    
    # Register requirements analysis agent
    factory.register_agent_type('requirements_analysis', RequirementsAnalysisAgent)
    
    # Register other agents as they become available
    # factory.register_agent_type('code_generation', CodeGenerationAgent)
    # factory.register_agent_type('test_generation', TestGenerationAgent)

async def execute_task(agent_type: str, task: Dict[str, Any], 
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
    manager = get_agent_manager()
    return await manager.execute_task(agent_type, task, config)

def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status."""
    manager = get_agent_manager()
    return manager.get_system_status()

def list_available_agents() -> List[str]:
    """List all available agent types."""
    manager = get_agent_manager()
    return manager.list_available_agent_types()

def list_active_agents() -> List[str]:
    """List all active agent IDs."""
    manager = get_agent_manager()
    return manager.list_active_agents()

def get_agent_status(agent_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a specific agent."""
    manager = get_agent_manager()
    return manager.get_agent_status(agent_id)

def shutdown_agent(agent_id: str) -> bool:
    """Shutdown a specific agent."""
    manager = get_agent_manager()
    return manager.shutdown_agent(agent_id)

def shutdown_all_agents():
    """Shutdown all active agents."""
    manager = get_agent_manager()
    manager.shutdown_all_agents()

# Convenience functions for common operations
async def analyze_requirements(description: str, context: str, 
                             requirements: List[str] = None,
                             constraints: List[str] = None,
                             stakeholders: List[str] = None) -> Dict[str, Any]:
    """
    Analyze requirements using the requirements analysis agent.
    
    Args:
        description: Task description
        context: Task context
        requirements: List of requirements
        constraints: List of constraints
        stakeholders: List of stakeholders
        
    Returns:
        Analysis results
    """
    task = {
        'description': description,
        'context': context,
        'requirements': requirements or [],
        'constraints': constraints or [],
        'stakeholders': stakeholders or []
    }
    
    return await execute_task('requirements_analysis', task)

# Export main classes and functions
__all__ = [
    'BaseAgent',
    'AgentConfig', 
    'AgentState',
    'AgentFactory',
    'AgentManager',
    'AgentPerformanceMonitor',
    'AgentConfigManager',
    'RequirementsAnalysisAgent',
    'get_agent_manager',
    'execute_task',
    'get_system_status',
    'list_available_agents',
    'list_active_agents',
    'get_agent_status',
    'shutdown_agent',
    'shutdown_all_agents',
    'analyze_requirements'
]
