"""
Code Reviewer Graph for LangGraph Studio.
"""

from agents.development.code_reviewer_langgraph import CodeReviewerCoordinator

coordinator = CodeReviewerCoordinator()
graph = coordinator.app

