"""
Quality Assurance Agent Graph for LangGraph Studio.
"""

from agents.rag.quality_assurance_agent_langgraph import QualityAssuranceAgentCoordinator

coordinator = QualityAssuranceAgentCoordinator()
graph = coordinator.app
