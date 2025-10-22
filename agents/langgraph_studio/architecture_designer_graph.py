"""
Architecture Designer Graph for LangGraph Studio.
"""

from agents.development.architecture_designer_langgraph import ArchitectureDesignerCoordinator

# Create coordinator and get compiled graph
coordinator = ArchitectureDesignerCoordinator()

# Export the compiled graph for LangGraph Studio
graph = coordinator.app

