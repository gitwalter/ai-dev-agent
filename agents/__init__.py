"""
AI Development Agents Package

This package contains all agent classes organized by functionality:
- core: Base agent infrastructure and management
- development: Software development focused agents  
- security: Security and ethics agents
- teams: Specialized team agents for complex tasks
- experts: Domain-specific expert agents
- management: Project management and orchestration agents
- supervisor: Supervisor agents for coordination

Usage:
    # Import core infrastructure
    from agents.core import BaseAgent, AgentConfig, AgentFactory
    
    # Import development agents
    from agents.development import RequirementsAnalyst, ArchitectureDesigner
    
    # Import security agents
    from agents.security import SecurityAnalyst, EthicalAIProtectionTeam
    
    # Import specialized teams
    from agents.teams import SpecializedSubagentTeam, WorkflowOrchestrationTeam
"""

# Core infrastructure exports for convenience
from .core import BaseAgent, AgentConfig, AgentFactory, AgentManager
from .development import (
    RequirementsAnalyst, 
    ArchitectureDesigner, 
    CodeGenerator,
    CodeReviewer,
    TestGenerator, 
    DocumentationGenerator
)
from .security import SecurityAnalyst
from .management import ProjectManagerAgent

__all__ = [
    # Core infrastructure
    'BaseAgent',
    'AgentConfig', 
    'AgentFactory',
    'AgentManager',
    
    # Development agents
    'RequirementsAnalyst',
    'ArchitectureDesigner',
    'CodeGenerator',
    'CodeReviewer', 
    'TestGenerator',
    'DocumentationGenerator',
    
    # Security agents
    'SecurityAnalyst',
    
    # Management agents
    'ProjectManagerAgent',
    
    # Convenience functions
    'get_agent_manager',
    'execute_task',
    'analyze_requirements', 
    'get_system_status'
]

# Convenience functions for backward compatibility
_global_agent_manager = None

def get_agent_manager():
    """Get the global agent manager instance."""
    global _global_agent_manager
    if _global_agent_manager is None:
        from .core.agent_manager import AgentManager
        _global_agent_manager = AgentManager()
    return _global_agent_manager

async def execute_task(agent_type: str, task: dict, config=None):
    """Execute a task using the specified agent type."""
    manager = get_agent_manager()
    return await manager.execute_task(agent_type, task, config)

async def analyze_requirements(description: str, context: dict = None, 
                             requirements: list = None, constraints: list = None, 
                             stakeholders: list = None):
    """Analyze requirements using the RequirementsAnalyst."""
    task = {
        'description': description,
        'context': context or {},
        'requirements': requirements or [],
        'constraints': constraints or [],
        'stakeholders': stakeholders or []
    }
    return await execute_task('requirements_analyst', task)

def get_system_status():
    """Get comprehensive system status."""
    manager = get_agent_manager()
    return manager.get_system_status()