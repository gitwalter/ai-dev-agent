"""
Code Generator Graph for LangGraph Studio.
"""

from agents.development.code_generator_langgraph import CodeGeneratorCoordinator

# Create coordinator and get compiled graph
coordinator = CodeGeneratorCoordinator()

# Export the compiled graph for LangGraph Studio
graph = coordinator.app

