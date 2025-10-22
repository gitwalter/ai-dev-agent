"""
Query Planner Agent Graph for LangGraph Studio.
"""

from agents.research.query_planner_agent_langgraph import QueryPlannerAgentCoordinator

coordinator = QueryPlannerAgentCoordinator()
graph = coordinator.app
