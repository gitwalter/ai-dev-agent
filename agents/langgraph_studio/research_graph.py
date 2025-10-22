"""
Research Pipeline Graph for LangGraph Studio.

This module provides a compiled LangGraph workflow for the web research pipeline.
"""

from agents.research.web_research_swarm import WebResearchSwarmCoordinator

# Create research coordinator and get compiled graph
coordinator = WebResearchSwarmCoordinator()

# Export the compiled graph for LangGraph Studio
graph = coordinator.app

