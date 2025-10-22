"""
Swarm Coordinator Graph for LangGraph Studio.
"""

from agents.swarm.swarm_coordinator_langgraph import SwarmCoordinatorCoordinator

coordinator = SwarmCoordinatorCoordinator()
graph = coordinator.app
