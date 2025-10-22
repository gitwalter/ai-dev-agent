"""
Retrieval Specialist Agent Graph for LangGraph Studio.
"""

from agents.rag.retrieval_specialist_agent_langgraph import RetrievalSpecialistAgentCoordinator

coordinator = RetrievalSpecialistAgentCoordinator()
graph = coordinator.app
