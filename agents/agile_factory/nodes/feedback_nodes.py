"""
Feedback Loop Nodes for Agile Factory workflow.

These nodes handle state updates for feedback loops, ensuring that
iteration counts and status updates are persisted correctly in the graph state.
routers.py should only handle routing logic, not state updates.
"""

import logging
from typing import Dict, Any
from agents.agile_factory.state.agile_state import AgileFactoryState

logger = logging.getLogger(__name__)


def review_feedback_node(state: AgileFactoryState) -> AgileFactoryState:
    """
    Node to process feedback from Code Reviewer.
    
    Updates iteration counts and status based on review results.
    This ensures state changes are persisted before the router makes a decision.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with iteration counts and status
    """
    code_review = state.get("code_review", {})
    iteration_count = state.get("code_review_iteration_count", 0)
    
    # Check if review passed
    review_passed = code_review.get("quality_gate_passed", False)
    
    updates = {}
    
    if review_passed:
        # Review passed
        updates["status"] = "approved"
        logger.info("Code review passed - status updated to approved")
    else:
        # Review failed - increment iteration count
        new_count = iteration_count + 1
        updates["code_review_iteration_count"] = new_count
        updates["status"] = "needs_revision"
        logger.info(f"Code review failed - incrementing iteration count to {new_count}")
        
    return updates


def test_feedback_node(state: AgileFactoryState) -> AgileFactoryState:
    """
    Node to process feedback from Testing Agent.
    
    Updates iteration counts and status based on test results.
    This ensures state changes are persisted before the router makes a decision.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with iteration counts and status
    """
    test_results = state.get("test_results", {})
    iteration_count = state.get("test_iteration_count", 0)
    
    # Check if tests passed
    tests_passed = test_results.get("all_tests_passed", False)
    
    updates = {}
    
    if tests_passed:
        # Tests passed
        updates["status"] = "verified"
        logger.info("Tests passed - status updated to verified")
    else:
        # Tests failed - increment iteration count
        new_count = iteration_count + 1
        updates["test_iteration_count"] = new_count
        updates["status"] = "needs_revision"
        logger.info(f"Tests failed - incrementing iteration count to {new_count}")
        
    return updates

