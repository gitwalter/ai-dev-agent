"""
Synthesis Agent Graph for LangGraph Studio.
"""

from agents.research.synthesis_agent_langgraph import SynthesisAgentCoordinator

coordinator = SynthesisAgentCoordinator()
graph = coordinator.app
