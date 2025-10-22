"""
Writer Agent Graph for LangGraph Studio.
"""

from agents.rag.writer_agent_langgraph import WriterAgentCoordinator

coordinator = WriterAgentCoordinator()
graph = coordinator.app
