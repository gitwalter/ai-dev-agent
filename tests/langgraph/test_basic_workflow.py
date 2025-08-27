#!/usr/bin/env python3
"""
Basic LangGraph Workflow Tests.
Starting with simple tests and building complexity incrementally.
"""

import pytest
import asyncio
from typing import Dict, Any, TypedDict
from unittest.mock import Mock, patch

# Test imports
try:
    from langgraph.graph import StateGraph, END, START
    from langgraph.checkpoint.memory import MemorySaver
    from langchain.output_parsers import PydanticOutputParser
    from langchain.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

from utils.structured_outputs import RequirementsAnalysisOutput


class TestState(TypedDict):
    """Test state for LangGraph workflows."""
    value: str
    errors: list
    step: str


class TestBasicLangGraphWorkflow:
    """Basic tests for LangGraph workflow functionality."""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        mock = Mock()
        mock.invoke.return_value = "Mock response"
        return mock
    
    @pytest.fixture
    def basic_state(self):
        """Basic test state."""
        return {
            "project_context": "Create a simple calculator app",
            "project_name": "test-calculator",
            "session_id": "test-session-123",
            "requirements": [],
            "architecture": {},
            "code_files": {},
            "tests": {},
            "documentation": {},
            "diagrams": {},
            "agent_outputs": {},
            "errors": [],
            "warnings": [],
            "approval_requests": [],
            "current_step": "started",
            "execution_history": []
        }
    
    def test_langgraph_imports(self):
        """Test that LangGraph and related libraries can be imported."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Test basic imports
        from langgraph.graph import StateGraph, END, START
        from langgraph.checkpoint.memory import MemorySaver
        from langchain.output_parsers import PydanticOutputParser
        from langchain.prompts import PromptTemplate
        
        assert StateGraph is not None
        assert END is not None
        assert START is not None
        assert MemorySaver is not None
        assert PydanticOutputParser is not None
        assert PromptTemplate is not None
    
    def test_create_basic_workflow(self):
        """Test creating a basic LangGraph workflow."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        from langgraph.graph import StateGraph, END, START
        
        # Create workflow with TypedDict state
        workflow = StateGraph(TestState)
        
        # Add a simple node that returns a dictionary
        def simple_node(state: TestState) -> TestState:
            return {
                "value": "processed",
                "errors": state.get("errors", []),
                "step": "simple_node"
            }
        
        workflow.add_node("simple_node", simple_node)
        
        # Add START edge and END edge
        workflow.add_edge(START, "simple_node")
        workflow.add_edge("simple_node", END)
        
        # Compile workflow
        app = workflow.compile()
        
        assert app is not None
        assert hasattr(app, 'invoke')
    
    def test_requirements_parser_creation(self):
        """Test creating a StrOutputParser for requirements analysis."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        from langchain_core.output_parsers.string import StrOutputParser

        # Create StrOutputParser
        parser = StrOutputParser()
        
        # Test parser creation
        assert parser is not None
        assert hasattr(parser, 'parse')
        
        # Test string parsing
        test_response = '{"test": "value"}'
        result = parser.parse(test_response)
        assert isinstance(result, str)
        assert result == test_response
    
    def test_prompt_template_creation(self):
        """Test creating a prompt template with StrOutputParser."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        from langchain_core.output_parsers.string import StrOutputParser
        from langchain.prompts import PromptTemplate
        
        # Create StrOutputParser
        parser = StrOutputParser()
        
        # Create prompt template
        prompt = PromptTemplate(
            template="Analyze requirements: {project_context}\n\nRespond with valid JSON only.",
            input_variables=["project_context"]
        )
        
        # Test prompt formatting
        formatted = prompt.format(project_context="Create a calculator")
        assert "Create a calculator" in formatted
        assert "Respond with valid JSON only" in formatted
    
    @pytest.mark.asyncio
    async def test_simple_workflow_execution(self):
        """Test executing a simple workflow."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        from langgraph.graph import StateGraph, END, START
        
        # Create workflow with TypedDict state
        workflow = StateGraph(TestState)
        
        # Add processing node that returns a dictionary
        def process_node(state: TestState) -> TestState:
            return {
                "value": f"processed_{state['value']}",
                "errors": state.get("errors", []),
                "step": "process"
            }
        
        workflow.add_node("process", process_node)
        
        # Add START edge and END edge
        workflow.add_edge(START, "process")
        workflow.add_edge("process", END)
        
        # Compile and execute
        app = workflow.compile()
        initial_state = TestState(value="test", errors=[], step="start")
        
        result = await app.ainvoke(initial_state)
        
        assert result["value"] == "processed_test"
        assert result["step"] == "process"
    
    def test_state_validation(self, basic_state):
        """Test that state structure is valid."""
        # Check required fields
        required_fields = [
            "project_context", "project_name", "session_id",
            "requirements", "architecture", "code_files",
            "tests", "documentation", "agent_outputs",
            "errors", "warnings", "current_step"
        ]
        
        for field in required_fields:
            assert field in basic_state, f"Missing required field: {field}"
        
        # Check data types
        assert isinstance(basic_state["project_context"], str)
        assert isinstance(basic_state["requirements"], list)
        assert isinstance(basic_state["architecture"], dict)
        assert isinstance(basic_state["errors"], list)
    
    def test_error_handling_in_workflow(self):
        """Test error handling in workflow nodes."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        from langgraph.graph import StateGraph, END, START
        
        # Create workflow with TypedDict state
        workflow = StateGraph(TestState)
        
        def error_node(state: TestState) -> TestState:
            try:
                # Simulate an error
                raise ValueError("Test error")
            except Exception as e:
                errors = state.get("errors", [])
                errors.append(str(e))
                return {
                    "value": "error_handled",
                    "errors": errors,
                    "step": "error_node"
                }
        
        workflow.add_node("error_node", error_node)
        
        # Add START edge and END edge
        workflow.add_edge(START, "error_node")
        workflow.add_edge("error_node", END)
        
        # Compile and execute
        app = workflow.compile()
        initial_state = TestState(value="test", errors=[], step="start")
        
        # Execute synchronously for this test
        result = app.invoke(initial_state)
        
        assert result["value"] == "error_handled"
        assert len(result["errors"]) == 1
        assert "Test error" in result["errors"][0]
        assert result["step"] == "error_node"
    
    def test_multi_node_workflow(self):
        """Test workflow with multiple nodes."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        from langgraph.graph import StateGraph, END, START
        
        # Create workflow with TypedDict state
        workflow = StateGraph(TestState)
        
        def first_node(state: TestState) -> TestState:
            return {
                "value": f"first_{state['value']}",
                "errors": state.get("errors", []),
                "step": "first"
            }
        
        def second_node(state: TestState) -> TestState:
            return {
                "value": f"second_{state['value']}",
                "errors": state.get("errors", []),
                "step": "second"
            }
        
        workflow.add_node("first", first_node)
        workflow.add_node("second", second_node)
        
        # Add edges: START -> first -> second -> END
        workflow.add_edge(START, "first")
        workflow.add_edge("first", "second")
        workflow.add_edge("second", END)
        
        # Compile and execute
        app = workflow.compile()
        initial_state = TestState(value="test", errors=[], step="start")
        
        result = app.invoke(initial_state)
        
        assert result["value"] == "second_first_test"
        assert result["step"] == "second"


class TestRequirementsAnalysisNode:
    """Tests for the requirements analysis node specifically."""
    
    @pytest.fixture
    def mock_requirements_output(self):
        """Mock requirements analysis output."""
        return {
            "functional_requirements": [
                {
                    "id": "FR-001",
                    "title": "Basic Calculator Operations",
                    "description": "Support addition, subtraction, multiplication, division",
                    "priority": "high",
                    "acceptance_criteria": ["Can add two numbers", "Can subtract two numbers"]
                }
            ],
            "non_functional_requirements": [
                {
                    "id": "NFR-001",
                    "title": "Performance",
                    "description": "Response time under 1 second",
                    "category": "performance",
                    "measurement": "Response time < 1s"
                }
            ],
            "user_stories": [
                {
                    "id": "US-001",
                    "as_a": "user",
                    "i_want": "to perform basic calculations",
                    "so_that": "I can solve mathematical problems"
                }
            ],
            "technical_constraints": ["Must work in web browser"],
            "assumptions": ["User has basic computer skills"],
            "risks": [
                {
                    "risk": "Complex calculations may be slow",
                    "probability": "medium",
                    "impact": "medium",
                    "mitigation": "Implement efficient algorithms"
                }
            ],
            "summary": {
                "total_functional_requirements": 1,
                "total_non_functional_requirements": 1,
                "total_user_stories": 1,
                "estimated_complexity": "low",
                "recommended_tech_stack": ["HTML", "CSS", "JavaScript"],
                "estimated_timeline": "1 week",
                "key_success_factors": ["Simple UI", "Fast response"]
            }
        }
    
    def test_requirements_analysis_output_structure(self, mock_requirements_output):
        """Test that requirements analysis output has correct structure."""
        # Validate against Pydantic model
        output = RequirementsAnalysisOutput(**mock_requirements_output)
        
        assert len(output.functional_requirements) == 1
        assert len(output.non_functional_requirements) == 1
        assert len(output.user_stories) == 1
        assert len(output.technical_constraints) == 1
        assert len(output.assumptions) == 1
        assert len(output.risks) == 1
        
        # Check specific fields
        assert output.functional_requirements[0]["id"] == "FR-001"
        assert output.functional_requirements[0]["priority"] == "high"
        assert output.summary["estimated_complexity"] == "low"
    
    @pytest.mark.asyncio
    async def test_requirements_node_integration(self, mock_llm, basic_state):
        """Test requirements analysis node with mock LLM."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        from langgraph.graph import StateGraph, END, START
        from langchain_core.output_parsers.string import StrOutputParser
        from langchain.prompts import PromptTemplate

        # Mock LLM response - JSON string format
        mock_response = """{
            "functional_requirements": [
                {
                    "id": "FR-001",
                    "title": "Test Requirement",
                    "description": "Test description",
                    "priority": "high",
                    "acceptance_criteria": ["Test criteria"]
                }
            ],
            "non_functional_requirements": [],
            "user_stories": [],
            "technical_constraints": [],
            "assumptions": [],
            "risks": [],
            "summary": {
                "total_functional_requirements": 1,
                "total_non_functional_requirements": 0,
                "total_user_stories": 0,
                "estimated_complexity": "low",
                "recommended_tech_stack": [],
                "estimated_timeline": "1 week",
                "key_success_factors": []
            }
        }"""

        # Create workflow
        workflow = StateGraph(dict)
        
        def requirements_node(state):
            # Simulate the chain execution with our mock response
            # Parse the JSON string result
            import json
            parsed_result = json.loads(mock_response)
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
