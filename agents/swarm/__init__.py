"""
MCP-Powered Agent Swarm
=======================

Agent swarm implementation using Model Context Protocol for coordination.
Enables complex workflows through orchestrated agent collaboration.

Components:
- SwarmCoordinator: Orchestrates agent swarms
- Specialized Agents: Product, Development, Quality, Testing, Release agents
- Workflow Management: Complete workflow execution and monitoring

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 3)
"""

from .swarm_coordinator import SwarmCoordinator, create_swarm_coordinator, SwarmWorkflow, SwarmTask, AgentRole

__all__ = [
    'SwarmCoordinator', 
    'create_swarm_coordinator', 
    'SwarmWorkflow', 
    'SwarmTask', 
    'AgentRole'
]
