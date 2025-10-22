"""
Project Manager Supervisor Graph for LangGraph Studio.
"""

from agents.supervisor.project_manager_supervisor_langgraph import ProjectManagerSupervisorCoordinator

coordinator = ProjectManagerSupervisorCoordinator()
graph = coordinator.app
