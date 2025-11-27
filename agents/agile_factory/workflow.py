"""
Agile Factory LangGraph Workflow

Main workflow orchestrating all agent nodes with:
- LangGraph checkpointers for state persistence
- HITL checkpoints between stages
- Feedback loops with loop prevention
- Support for LangGraph Studio testing
"""

import logging
import os
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

from agents.agile_factory.state.agile_state import AgileFactoryState
from agents.agile_factory.nodes.requirements_node import requirements_node
from agents.agile_factory.nodes.architecture_node import architecture_node
from agents.agile_factory.nodes.code_reviewer_node import code_reviewer_node
from agents.agile_factory.nodes.node_wrappers import code_generator_node_with_auto_write, documentation_node_with_auto_write, testing_node_with_auto_write
from agents.agile_factory.nodes.routers import review_decision_router, test_decision_router, should_skip_code_review
from agents.agile_factory.nodes.feedback_nodes import review_feedback_node, test_feedback_node
from agents.agile_factory.hitl.hitl_checkpoints import hitl_checkpoint_node

logger = logging.getLogger(__name__)


# HITL checkpoint wrapper functions (required for LangGraph Studio serialization)
# Lambda functions cannot be serialized, so we create proper wrapper functions
def hitl_story_review_node(state: AgileFactoryState) -> dict:
    """HITL checkpoint for story review."""
    return hitl_checkpoint_node(state, "story_review")


def hitl_requirements_review_node(state: AgileFactoryState) -> dict:
    """HITL checkpoint for requirements review."""
    return hitl_checkpoint_node(state, "requirements_review")


def hitl_architecture_review_node(state: AgileFactoryState) -> dict:
    """HITL checkpoint for architecture review."""
    return hitl_checkpoint_node(state, "architecture_review")


def hitl_code_review_checkpoint_node(state: AgileFactoryState) -> dict:
    """HITL checkpoint for code generation review."""
    return hitl_checkpoint_node(state, "code_generation_review")


def hitl_final_review_node(state: AgileFactoryState) -> dict:
    """HITL checkpoint for final review."""
    return hitl_checkpoint_node(state, "final_review")


def create_agile_factory_workflow(use_checkpointer: bool = True, checkpointer_type: str = "memory") -> StateGraph:
    """
    Create Agile Factory LangGraph workflow.
    
    Args:
        use_checkpointer: Whether to use checkpointer for state persistence
        checkpointer_type: Type of checkpointer ("memory" or "sqlite")
        
    Returns:
        Compiled LangGraph workflow
    """
    # Create workflow graph
    workflow = StateGraph(AgileFactoryState)
    
    # Add nodes
    workflow.add_node("requirements_analyst", requirements_node)
    workflow.add_node("architecture_designer", architecture_node)
    # Use wrapped nodes with automatic file writing (NO LLM calls for file writing)
    workflow.add_node("code_generator", code_generator_node_with_auto_write)
    workflow.add_node("code_reviewer", code_reviewer_node)
    workflow.add_node("testing_agent", testing_node_with_auto_write)
    workflow.add_node("documentation_generator", documentation_node_with_auto_write)
    
    # Add feedback nodes
    workflow.add_node("review_feedback", review_feedback_node)
    workflow.add_node("test_feedback", test_feedback_node)
    
    # Add HITL checkpoint nodes (using wrapper functions, not lambdas - required for Studio serialization)
    workflow.add_node("hitl_story_review", hitl_story_review_node)
    workflow.add_node("hitl_requirements_review", hitl_requirements_review_node)
    workflow.add_node("hitl_architecture_review", hitl_architecture_review_node)
    workflow.add_node("hitl_code_review_checkpoint", hitl_code_review_checkpoint_node)
    workflow.add_node("hitl_final_review", hitl_final_review_node)
    
    # Define workflow edges
    # Start → Story Review (HITL)
    workflow.set_entry_point("hitl_story_review")
    
    # Story Review → Requirements Analyst
    workflow.add_edge("hitl_story_review", "requirements_analyst")
    
    # Requirements Analyst → Requirements Review (HITL)
    workflow.add_edge("requirements_analyst", "hitl_requirements_review")
    
    # Requirements Review → Architecture Designer
    workflow.add_edge("hitl_requirements_review", "architecture_designer")
    
    # Architecture Designer → Architecture Review (HITL)
    workflow.add_edge("architecture_designer", "hitl_architecture_review")
    
    # Architecture Review → Code Generator
    workflow.add_edge("hitl_architecture_review", "code_generator")
    
    # Code Generator → Conditional: Code Review or Skip to Testing
    workflow.add_conditional_edges(
        "code_generator",
        should_skip_code_review,  # New router function
        {
            "skip_review": "testing_agent",  # Skip review, go to testing
            "review": "hitl_code_review_checkpoint"  # Do review
        }
    )
    
    # Code Review Checkpoint → Code Reviewer
    workflow.add_edge("hitl_code_review_checkpoint", "code_reviewer")
    
    # Code Reviewer → Review Feedback (process results)
    workflow.add_edge("code_reviewer", "review_feedback")
    
    # Review Feedback → Decision Router (loop back or continue)
    workflow.add_conditional_edges(
        "review_feedback",
        review_decision_router,
        {
            "code_generator": "code_generator",  # Loop back for revision
            "testing_agent": "testing_agent"      # Continue to testing
        }
    )
    
    # Testing Agent → Test Feedback (process results)
    workflow.add_edge("testing_agent", "test_feedback")
    
    # Test Feedback → Decision Router (loop back or continue)
    workflow.add_conditional_edges(
        "test_feedback",
        test_decision_router,
        {
            "code_generator": "code_generator",           # Loop back for fixes
            "documentation_generator": "documentation_generator"  # Continue to docs
        }
    )
    
    # Documentation Generator → Final Review (HITL)
    workflow.add_edge("documentation_generator", "hitl_final_review")
    
    # Final Review → END
    workflow.add_edge("hitl_final_review", END)
    
    # Compile workflow
    if use_checkpointer:
        if checkpointer_type == "sqlite":
            # Use SqliteSaver for persistent state
            checkpointer = SqliteSaver.from_conn_string(":memory:")  # Can be changed to file path
        else:
            # Use MemorySaver for in-memory state (good for testing)
            checkpointer = MemorySaver()
        
        app = workflow.compile(checkpointer=checkpointer)
    else:
        # No checkpointer (for LangGraph Studio - Studio handles persistence)
        app = workflow.compile()
    
    logger.info("Agile Factory workflow created successfully")
    
    return app


# Create workflow instance for LangGraph Studio
# Note: For Studio, we don't pass checkpointer (Studio handles it)
graph = create_agile_factory_workflow(use_checkpointer=False)
