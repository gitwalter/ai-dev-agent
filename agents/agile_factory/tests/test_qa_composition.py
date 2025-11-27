
import logging
import os
from unittest.mock import MagicMock, patch
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage

from agents.agile_factory.state.agile_state import AgileFactoryState
from agents.agile_factory.nodes.code_generator_node import code_generator_node
from agents.agile_factory.nodes.code_reviewer_node import code_reviewer_node
from agents.agile_factory.nodes.feedback_nodes import review_feedback_node
from agents.agile_factory.nodes.routers import review_decision_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_qa_composition_loop():
    """
    Test the Code Generator <-> Code Reviewer loop in isolation.
    Verifies that the loop terminates after max_iterations.
    """
    print("\n=== TESTING QA COMPOSITION LOOP ===")
    
    # 1. Define the Workflow Subset
    workflow = StateGraph(AgileFactoryState)
    
    # Add nodes
    # We use the REAL nodes, but we'll patch their internals
    workflow.add_node("code_generator", code_generator_node)
    workflow.add_node("code_reviewer", code_reviewer_node)
    workflow.add_node("review_feedback", review_feedback_node)
    
    # Mock Testing Agent as exit point
    def mock_testing_agent(state: AgileFactoryState) -> AgileFactoryState:
        print("-> Entered Testing Agent (Loop Terminated)")
        state["current_node"] = "testing_agent"
        return state
    workflow.add_node("testing_agent", mock_testing_agent)
    
    # Define Edges
    workflow.set_entry_point("code_generator")
    workflow.add_edge("code_generator", "code_reviewer")
    workflow.add_edge("code_reviewer", "review_feedback")
    
    # Conditional Edge
    workflow.add_conditional_edges(
        "review_feedback",
        review_decision_router,
        {
            "code_generator": "code_generator",
            "testing_agent": "testing_agent"
        }
    )
    workflow.add_edge("testing_agent", END)
    
    # Compile
    app = workflow.compile(checkpointer=MemorySaver())
    
    # 2. Setup Mocks
    # We need to mock LLMs to simulate:
    # - Code Generator: Always produces a file
    # - Code Reviewer: Always fails
    
    with patch("agents.agile_factory.nodes.code_reviewer_node.ChatGoogleGenerativeAI") as MockLLMReviewer, \
         patch("agents.agile_factory.nodes.code_reviewer_node.get_agent_prompt_loader") as MockLoaderReviewer, \
         patch("agents.agile_factory.nodes.code_generator_node.ChatGoogleGenerativeAI") as MockLLMGenerator, \
         patch("agents.agile_factory.nodes.code_generator_node.get_agent_prompt_loader") as MockLoaderGenerator, \
         patch("agents.agile_factory.nodes.code_generator_node.extract_files_from_directory") as MockExtract:
         
        # Mock Reviewer LLM (Always Fail)
        mock_llm_reviewer = MagicMock()
        mock_llm_reviewer.invoke.return_value = AIMessage(content='```json\n{"quality_gate_passed": false, "issues": ["Fix it"]}\n```')
        MockLLMReviewer.return_value = mock_llm_reviewer
        
        # Mock Reviewer Prompt
        mock_loader_reviewer = MagicMock()
        mock_loader_reviewer.get_system_prompt.return_value = "You are a reviewer."
        MockLoaderReviewer.return_value = mock_loader_reviewer
        
        # Mock Generator LLM/Graph
        # Since code_generator_node constructs a graph internally, mocking the LLM is hard because the graph invokes it.
        # Instead, we'll mock the compiled_agent.invoke inside code_generator_node if possible, 
        # OR we just mock the LLM to return tool calls.
        
        # Easier: Mock extract_files_from_directory to always return files, 
        # so code_generator_node "thinks" it generated files even if LLM does nothing.
        MockExtract.return_value = {"app.py": "print('hello')"}
        
        # We also need to make the internal graph execution succeed.
        # We can patch compiled_agent.invoke inside code_generator_node? 
        # No, it's a local variable.
        
        # We'll patch StateGraph.compile().invoke
        # But StateGraph is imported in code_generator_node.
        
        # Let's patch ChatGoogleGenerativeAI for Generator to return a simple message
        mock_llm_generator = MagicMock()
        # The internal agent is tools bound.
        mock_llm_generator.bind_tools.return_value.invoke.return_value = AIMessage(content="Generated code.")
        MockLLMGenerator.return_value = mock_llm_generator
        
        mock_loader_generator = MagicMock()
        mock_loader_generator.get_system_prompt.return_value = "You are a coder."
        MockLoaderGenerator.return_value = mock_loader_generator
        
        # 3. Execute
        initial_state = {
            "user_story": "Build a website",
            "project_type": "website",
            "max_iterations": 3,
            "code_review_iteration_count": 0
        }
        
        config = {"configurable": {"thread_id": "qa_composition_test"}}
        
        print("Starting workflow execution...")
        # Limit max steps to prevent actual infinite loop if bug exists
        events = list(app.stream(initial_state, config=config, recursion_limit=20))
        
        # 4. Verify
        final_state = app.get_state(config).values
        count = final_state.get('code_review_iteration_count')
        node = final_state.get('current_node')
        
        print(f"Final Iteration Count: {count}")
        print(f"Final Node: {node}")
        
        # Count should be 3 now (>= max_iterations)
        # 0 (start) -> fail -> 1
        # 1 (retry 1) -> fail -> 2
        # 2 (retry 2) -> fail -> 3
        # 3 >= 3 -> Exit
        
        if count == 3 and node == "testing_agent":
            print("[PASS] Loop terminated correctly.")
        else:
            print(f"[FAIL] Loop did not behave as expected. Count: {count}, Node: {node}")

if __name__ == "__main__":
    test_qa_composition_loop()

