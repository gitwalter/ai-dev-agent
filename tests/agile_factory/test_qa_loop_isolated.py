"""
Test for Isolated QA Loop (Code Generator <-> Code Reviewer)

Verifies that the feedback loop correctly increments iteration counts
and respects the maximum iteration limit.
"""

import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.agile_factory.state.agile_state import AgileFactoryState
from agents.agile_factory.nodes.feedback_nodes import review_feedback_node
from agents.agile_factory.nodes.routers import review_decision_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MOCK NODES
def mock_code_generator(state: AgileFactoryState) -> AgileFactoryState:
    logger.info("MOCK: Generating code...")
    state["code_files"] = {"app.py": "print('hello')"}
    state["current_node"] = "code_generator"
    return state

def mock_code_reviewer_fail(state: AgileFactoryState) -> AgileFactoryState:
    logger.info("MOCK: Reviewing code (FAIL scenario)...")
    state["code_review"] = {
        "quality_gate_passed": False,
        "issues": ["Fix this"]
    }
    state["current_node"] = "code_reviewer"
    return state

def mock_code_reviewer_pass(state: AgileFactoryState) -> AgileFactoryState:
    logger.info("MOCK: Reviewing code (PASS scenario)...")
    state["code_review"] = {
        "quality_gate_passed": True,
        "issues": []
    }
    state["current_node"] = "code_reviewer"
    return state

def mock_testing_agent(state: AgileFactoryState) -> AgileFactoryState:
    logger.info("MOCK: Testing agent (Exit point)...")
    state["current_node"] = "testing_agent"
    return state

def create_isolated_loop_graph(reviewer_node):
    workflow = StateGraph(AgileFactoryState)
    
    workflow.add_node("code_generator", mock_code_generator)
    workflow.add_node("code_reviewer", reviewer_node)
    workflow.add_node("review_feedback", review_feedback_node)
    workflow.add_node("testing_agent", mock_testing_agent)
    
    workflow.set_entry_point("code_generator")
    
    workflow.add_edge("code_generator", "code_reviewer")
    workflow.add_edge("code_reviewer", "review_feedback")
    
    workflow.add_conditional_edges(
        "review_feedback",
        review_decision_router,
        {
            "code_generator": "code_generator",
            "testing_agent": "testing_agent"
        }
    )
    
    workflow.add_edge("testing_agent", END)
    
    return workflow.compile(checkpointer=MemorySaver())

def test_loop_termination():
    """Test that loop terminates after max iterations."""
    print("\n=== TESTING LOOP TERMINATION (Max 3 iterations) ===")
    
    app = create_isolated_loop_graph(mock_code_reviewer_fail)
    
    initial_state = {
        "user_story": "Test Story",
        "project_type": "website",
        "max_iterations": 3,
        "code_review_iteration_count": 0
    }
    
    config = {"configurable": {"thread_id": "test_loop_1"}}
    
    # Run the graph
    events = list(app.stream(initial_state, config=config))
    
    # Analyze results
    final_state = app.get_state(config).values
    
    print(f"Final Iteration Count: {final_state.get('code_review_iteration_count')}")
    print(f"Final Status: {final_state.get('status')}")
    print(f"Current Node: {final_state.get('current_node')}")
    
    # Verification
    # Count ends at 4 because:
    # Start: 0
    # Fail 1 -> 1 (Loop)
    # Fail 2 -> 2 (Loop)
    # Fail 3 -> 3 (Loop)
    # Fail 4 -> 4 (Router sees 4 > 3, exits)
    assert final_state.get("code_review_iteration_count") == 4
    assert final_state.get("current_node") == "testing_agent"
    print("[OK] Loop terminated correctly at max iterations")

def test_loop_success():
    """Test that loop exits immediately on success."""
    print("\n=== TESTING LOOP SUCCESS (Immediate Pass) ===")
    
    app = create_isolated_loop_graph(mock_code_reviewer_pass)
    
    initial_state = {
        "user_story": "Test Story",
        "project_type": "website",
        "max_iterations": 3,
        "code_review_iteration_count": 0
    }
    
    config = {"configurable": {"thread_id": "test_success_1"}}
    
    # Run the graph
    events = list(app.stream(initial_state, config=config))
    
    # Analyze results
    final_state = app.get_state(config).values
    
    print(f"Final Iteration Count: {final_state.get('code_review_iteration_count')}")
    print(f"Final Status: {final_state.get('status')}")
    print(f"Current Node: {final_state.get('current_node')}")
    
    # Verification
    # Count should start at 0 and not increment if passed immediately? 
    # Wait, feedback node only increments if failed.
    # If passed, it doesn't increment.
    assert final_state.get("code_review_iteration_count") == 0
    assert final_state.get("status") == "approved"
    assert final_state.get("current_node") == "testing_agent"
    print("[OK] Loop exited correctly on success")

if __name__ == "__main__":
    test_loop_termination()
    test_loop_success()

