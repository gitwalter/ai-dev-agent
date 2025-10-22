"""
Security Analyst Graph for LangGraph Studio.
"""

from agents.security.security_analyst_langgraph import SecurityAnalystCoordinator

coordinator = SecurityAnalystCoordinator()
graph = coordinator.app
