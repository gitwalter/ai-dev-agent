#!/usr/bin/env python3
"""
Simple integration test for LangGraph workflow.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock

# Test imports
try:
    from langgraph.graph import StateGraph, END, START
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

@pytest.mark.asyncio
async def test_simple_workflow_integration():
    """Test simple workflow integration."""
    if not LANGGRAPH_AVAILABLE:
        pytest.skip("LangGraph not available")
    
    # Create mock LLM
    mock_llm = Mock()
    mock_response = """{
        "functional_requirements": [
            {
                "id": "FR-001",
                "title": "Test Requirement",
                "description": "Test description",
                "priority": "high"
            }
        ],
        "non_functional_requirements": [],
        "user_stories": [],
        "technical_constraints": [],
        "assumptions": [],
        "risks": [],
        "summary": {
            "total_functional_requirements": 1,
            "estimated_complexity": "low"
        }
    }"""
    mock_llm.invoke.return_value = mock_response
    
    # Create basic state
    basic_state = {
        "project_context": "Create a simple calculator app",
        "requirements": [],
        "agent_outputs": {},
        "current_step": "started"
    }
    
    # Create workflow
    workflow = StateGraph(dict)
    
    def requirements_node(state):
        # Simulate the chain execution
        result = mock_llm.invoke("Analyze requirements")
        parsed_result = json.loads(result)
        return {
            **state,
            "requirements": parsed_result.get("functional_requirements", []),
            "agent_outputs": {
                **state["agent_outputs"],
                "requirements_analyst": parsed_result
            },
            "current_step": "requirements_analysis"
        }
    
    workflow.add_node("requirements_analysis", requirements_node)
    workflow.add_edge(START, "requirements_analysis")
    workflow.add_edge("requirements_analysis", END)
    
    # Execute
    app = workflow.compile()
    result = await app.ainvoke(basic_state)
    
    # Verify results
    assert result["current_step"] == "requirements_analysis"
    assert len(result["requirements"]) == 1
    assert result["requirements"][0]["id"] == "FR-001"
    assert "requirements_analyst" in result["agent_outputs"]
    
    print("✅ Simple workflow integration test PASSED")

if __name__ == "__main__":
    asyncio.run(test_simple_workflow_integration())
