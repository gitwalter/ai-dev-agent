"""
Pydantic Experts Graph for LangGraph Studio.
"""

from agents.experts.pydantic_experts_langgraph import PydanticExpertsCoordinator

coordinator = PydanticExpertsCoordinator()
graph = coordinator.app
