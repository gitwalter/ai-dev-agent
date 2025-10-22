"""
Requirements Analyst Graph for LangGraph Studio.
"""

from agents.development.requirements_analyst_langgraph import RequirementsAnalystCoordinator

# Create coordinator and get compiled graph
coordinator = RequirementsAnalystCoordinator()

# Export the compiled graph for LangGraph Studio
graph = coordinator.app

