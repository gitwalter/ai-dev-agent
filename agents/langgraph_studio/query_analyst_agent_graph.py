"""
Query Analyst Agent Graph for LangGraph Studio.
"""

from agents.rag.query_analyst_agent_langgraph import QueryAnalystAgentCoordinator

coordinator = QueryAnalystAgentCoordinator()
graph = coordinator.app
