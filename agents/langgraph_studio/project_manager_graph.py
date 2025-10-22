"""
Project Manager Graph for LangGraph Studio.
"""

from agents.management.project_manager_langgraph import ProjectManagerCoordinator

coordinator = ProjectManagerCoordinator()
graph = coordinator.app
