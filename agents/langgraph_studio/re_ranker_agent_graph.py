"""
Re Ranker Agent Graph for LangGraph Studio.
"""

from agents.rag.re_ranker_agent_langgraph import ReRankerAgentCoordinator

coordinator = ReRankerAgentCoordinator()
graph = coordinator.app
