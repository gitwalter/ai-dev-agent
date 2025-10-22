"""
Verification Agent Graph for LangGraph Studio.
"""

from agents.research.verification_agent_langgraph import VerificationAgentCoordinator

coordinator = VerificationAgentCoordinator()
graph = coordinator.app
