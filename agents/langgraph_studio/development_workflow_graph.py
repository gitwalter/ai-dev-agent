"""
Development Workflow Graph for LangGraph Studio.
Complete software development lifecycle orchestration.
"""

from agents.teams.development_workflow_langgraph import DevelopmentWorkflowCoordinator

coordinator = DevelopmentWorkflowCoordinator()
graph = coordinator.app

