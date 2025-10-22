"""
Web Search Agent Graph for LangGraph Studio.
"""

from agents.research.web_search_agent_langgraph import WebSearchAgentCoordinator

coordinator = WebSearchAgentCoordinator()
graph = coordinator.app
