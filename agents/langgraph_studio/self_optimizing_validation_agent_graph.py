"""
Self Optimizing Validation Agent Graph for LangGraph Studio.
"""

from agents.management.self_optimizing_validation_agent_langgraph import SelfOptimizingValidationAgentCoordinator

coordinator = SelfOptimizingValidationAgentCoordinator()
graph = coordinator.app
