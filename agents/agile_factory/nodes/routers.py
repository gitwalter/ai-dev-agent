"""
Decision routers for feedback loops with loop prevention.

These routers control the flow between code_reviewer ↔ code_generator
and testing_agent ↔ code_generator, preventing infinite loops.

Note: These routers are pure logic functions that determine the next node.
State updates (like incrementing counters) must be handled by feedback_nodes.py
BEFORE calling these routers.
"""

import logging
from typing import Literal
from agents.agile_factory.state.agile_state import AgileFactoryState

logger = logging.getLogger(__name__)


def should_skip_code_review(state: AgileFactoryState) -> Literal["skip_review", "review"]:
    """
    Determine if code review should be skipped based on rigidity parameter.
    
    Args:
        state: Current workflow state
        
    Returns:
        "skip_review" if review should be skipped, "review" if review should be performed
    """
    skip_review = state.get("skip_code_review", False)
    rigidity = state.get("review_rigidity", 0.3)  # Default: lenient (0.3)
    
    # Skip if explicitly requested
    if skip_review:
        logger.info("Router: Skipping code review (skip_code_review=True)")
        return "skip_review"
    
    # Skip if rigidity is 0 (very lenient = skip review)
    if rigidity <= 0.0:
        logger.info(f"Router: Skipping code review (rigidity={rigidity} <= 0.0)")
        return "skip_review"
    
    # Perform review
    logger.info(f"Router: Performing code review (rigidity={rigidity})")
    return "review"


def review_decision_router(state: AgileFactoryState) -> Literal["code_generator", "testing_agent"]:
    """
    Route after code review feedback: loop back to code generator or continue to testing.
    
    Uses rigidity parameter to determine strictness:
    - Low rigidity (0.0-0.3): Very lenient, auto-pass quickly
    - Medium rigidity (0.4-0.7): Moderate strictness
    - High rigidity (0.8-1.0): Strict, require multiple iterations
    
    Args:
        state: Current workflow state (already updated by review_feedback_node)
        
    Returns:
        Next node name: "code_generator" (if needs revision) or "testing_agent" (if approved/max iterations)
    """
    code_review = state.get("code_review", {})
    iteration_count = state.get("code_review_iteration_count", 0)
    rigidity = state.get("review_rigidity", 0.3)  # Default: lenient
    
    # Adjust max iterations based on rigidity
    # Low rigidity: 1 iteration max, High rigidity: 2-3 iterations
    if rigidity <= 0.3:
        max_iterations = 1  # Very lenient - pass after first attempt
    elif rigidity <= 0.7:
        max_iterations = state.get("max_iterations", 2)  # Default
    else:
        max_iterations = 3  # Strict - allow more iterations
    
    # Check if review passed
    review_passed = code_review.get("quality_gate_passed", False)
    
    if review_passed:
        # Review passed, continue to testing
        logger.info(f"Router: Code review passed (rigidity={rigidity}) -> testing_agent")
        return "testing_agent"
    
    # Review failed, check iteration limit based on rigidity
    # Note: iteration_count was already incremented by feedback node
    if iteration_count >= max_iterations:
        logger.warning(f"Router: Max iterations ({max_iterations}) reached for code review loop (rigidity={rigidity}) -> testing_agent (forced)")
        return "testing_agent"
    
    # For low rigidity, auto-pass even on first failure
    if rigidity <= 0.3 and iteration_count >= 1:
        logger.info(f"Router: Low rigidity ({rigidity}) - auto-passing after first attempt -> testing_agent")
        return "testing_agent"
    
    # Loop back to code generator for revision
    logger.info(f"Router: Code review failed (iter {iteration_count}/{max_iterations}, rigidity={rigidity}) -> code_generator")
    return "code_generator"


def test_decision_router(state: AgileFactoryState) -> Literal["code_generator", "documentation_generator"]:
    """
    Route after testing feedback: loop back to code generator or continue to documentation.
    
    Args:
        state: Current workflow state (already updated by test_feedback_node)
        
    Returns:
        Next node name: "code_generator" (if tests fail) or "documentation_generator" (if tests pass/max iterations)
    """
    test_results = state.get("test_results", {})
    iteration_count = state.get("test_iteration_count", 0)
    max_iterations = state.get("max_iterations", 2)  # Reduced for efficiency
    
    # Check if tests passed
    tests_passed = test_results.get("all_tests_passed", False)
    
    if tests_passed:
        # Tests passed, continue to documentation
        logger.info("Router: Tests passed -> documentation_generator")
        return "documentation_generator"
    
    # Tests failed, check iteration limit
    # Note: iteration_count was already incremented by feedback node
    if iteration_count >= max_iterations:
        logger.warning(f"Router: Max iterations ({max_iterations}) reached for test loop -> documentation_generator (forced)")
        return "documentation_generator"
    
    # Loop back to code generator for fixes
    logger.info(f"Router: Tests failed (iter {iteration_count}) -> code_generator")
    return "code_generator"
