"""
Standalone Code Generator Node Test Graph for LangGraph Studio

This creates a simple graph with just the code_generator_node for isolated testing.
"""

import logging
from langgraph.graph import StateGraph, END
from agents.agile_factory.state.agile_state import AgileFactoryState
from agents.agile_factory.nodes.code_generator_node import code_generator_node

logger = logging.getLogger(__name__)


def create_code_generator_test_graph():
    """
    Create a simple test graph with just the code generator node.
    
    This allows testing the code generator in isolation without the full workflow.
    """
    # Create workflow graph
    workflow = StateGraph(AgileFactoryState)
    
    # Add only the code generator node
    workflow.add_node("code_generator", code_generator_node)
    
    # Simple flow: START → code_generator → END
    workflow.set_entry_point("code_generator")
    workflow.add_edge("code_generator", END)
    
    # Compile workflow (no checkpointer for Studio testing)
    app = workflow.compile()
    
    logger.info("Code generator test graph created successfully")
    
    return app


# Create graph instance for LangGraph Studio
graph = create_code_generator_test_graph()

