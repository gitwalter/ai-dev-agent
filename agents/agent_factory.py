"""
Agent Factory - Agent Creation and Management

This module provides the factory pattern for creating and managing agent instances.
It includes agent registry, lifecycle management, and configuration handling.
"""

from typing import Type, Dict, Any, Optional, List
from .base_agent import BaseAgent, AgentConfig
import logging

class AgentFactory:
    """
    Factory for creating and managing agent instances.
    """
    
    def __init__(self):
        self.agent_registry: Dict[str, Type[BaseAgent]] = {}
        self.active_agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("agent_factory")
    
    def register_agent_type(self, agent_type: str, agent_class: Type[BaseAgent]):
        """Register a new agent type."""
        self.agent_registry[agent_type] = agent_class
        self.logger.info(f"Registered agent type: {agent_type}")
    
    def create_agent(self, agent_type: str, config: AgentConfig) -> BaseAgent:
        """Create a new agent instance."""
        if agent_type not in self.agent_registry:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = self.agent_registry[agent_type]
        agent = agent_class(config)
        
        self.active_agents[config.agent_id] = agent
        self.logger.info(f"Created agent: {config.agent_id} of type {agent_type}")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an active agent by ID."""
        return self.active_agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all active agent IDs."""
        return list(self.active_agents.keys())
    
    def list_agent_types(self) -> List[str]:
        """List all registered agent types."""
        return list(self.agent_registry.keys())
    
    def shutdown_agent(self, agent_id: str) -> bool:
        """Shutdown and cleanup an agent."""
        if agent_id in self.active_agents:
            agent = self.active_agents[agent_id]
            # Perform cleanup
            agent.state.status = 'shutdown'
            del self.active_agents[agent_id]
            self.logger.info(f"Shutdown agent: {agent_id}")
            return True
        return False
    
    def shutdown_all_agents(self):
        """Shutdown all active agents."""
        agent_ids = list(self.active_agents.keys())
        for agent_id in agent_ids:
            self.shutdown_agent(agent_id)
        self.logger.info(f"Shutdown all {len(agent_ids)} agents")
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an agent."""
        agent = self.get_agent(agent_id)
        return agent.get_status() if agent else None
    
    def get_all_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active agents."""
        return {agent_id: agent.get_status() 
                for agent_id, agent in self.active_agents.items()}
