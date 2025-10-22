"""
Base Supervisor Graph for LangGraph Studio.
"""

from agents.supervisor.base_supervisor_langgraph import BaseSupervisorCoordinator

coordinator = BaseSupervisorCoordinator()
graph = coordinator.app
