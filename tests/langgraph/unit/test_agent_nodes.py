#!/usr/bin/env python3
"""
Tests for LangGraph agent nodes.
Comprehensive test suite for individual agent node functionality.
"""

import pytest
import asyncio
import uuid
import json
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, patch, AsyncMock

# Test imports
try:
    from langgraph.graph import StateGraph, END, START
    from langchain.output_parsers import PydanticOutputParser
    from langchain.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    # Provide fallback imports to prevent NameError
    ChatGoogleGenerativeAI = None
    StateGraph = None
    END = None
    START = None
    PydanticOutputParser = None
    PromptTemplate = None

def _has_valid_api_key():
    """Check if a valid API key is available for real LLM tests."""
    try:
        import streamlit as st
        # Get API key from Streamlit secrets
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            return False
        
        # Try to create a simple LLM instance to validate the key
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=api_key,
            temperature=0.1
        )
        return True
    except Exception:
        return False

from tests.mocks.workflow.langgraph_workflow_manager import LangGraphWorkflowManager, AgentNodeFactory, AgentState
from utils.structured_outputs import (
    RequirementsAnalysisOutput, 
    ArchitectureDesignOutput, 
    TestGenerationOutput,
    TestFile
)


class TestDataFactory:
    """Factory for creating isolated test data."""
    
    @staticmethod
    def create_isolated_test_state(project_context: str = None) -> Dict[str, Any]:
        """Create isolated test state with unique identifiers."""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "project_context": project_context or f"Create a test application {unique_id}",
            "project_name": f"test-project-{unique_id}",
            "session_id": f"test-session-{unique_id}",
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
            "current_step": "requirements_analysis",
            "execution_history": []
        }
    
    @staticmethod
    def create_isolated_requirements():
        """Create isolated requirements with unique identifiers."""
        unique_id = str(uuid.uuid4())[:8]
        return [
            {
                "id": f"REQ-{unique_id}-001",
                "title": f"Test Requirement {unique_id}",
                "description": f"Test description for requirement {unique_id}",
                "priority": "high",
                "type": "functional"
            }
        ]
    
    @staticmethod
    def create_isolated_architecture():
        """Create isolated architecture with unique identifiers."""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "system_overview": f"Test architecture overview {unique_id}",
            "architecture_pattern": "MVC",
            "technology_stack": {
                "frontend": ["React.js", "HTML5", "CSS3"],
                "backend": ["Node.js", "Express.js"],
                "database": ["SQLite"]
            },
            "components": [
                {
                    "name": f"Test Component {unique_id}",
                    "type": "frontend",
                    "description": f"Test component description {unique_id}"
                }
            ]
        }


class TestRequirementsAnalystNode:
    """Tests for requirements analyst node."""
    
    @pytest.fixture
    def isolated_node_factory(self, isolated_mock_llm):
        """Create isolated agent node factory."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        return AgentNodeFactory(isolated_mock_llm)
    
    @pytest.fixture
    def isolated_test_state(self):
        """Create isolated test state for each test."""
        return TestDataFactory.create_isolated_test_state()
    
    @pytest.fixture
    def isolated_mock_llm(self):
        """Create isolated mock LLM for each test."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = AsyncMock()
        mock.ainvoke = AsyncMock()
        return mock
    
    def test_requirements_node_creation(self, isolated_node_factory):
        """Test that requirements node can be created."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        requirements_node = isolated_node_factory.create_requirements_node()
        assert callable(requirements_node)
    
    @pytest.mark.asyncio
    async def test_requirements_node_execution_success(self, isolated_node_factory, isolated_test_state, isolated_mock_llm):
        """Test successful requirements analysis execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Mock successful LLM response as JSON string
        mock_response = {
            "functional_requirements": TestDataFactory.create_isolated_requirements(),
            "non_functional_requirements": [],
            "user_stories": [],
            "technical_constraints": [],
            "assumptions": [],
            "risks": [],
            "summary": "Test requirements analysis completed"
        }
        
        # Mock the LLM to return our expected response as JSON string
        isolated_mock_llm.ainvoke.return_value = Mock(content=json.dumps(mock_response))

        # Create and execute node
        requirements_node = isolated_node_factory.create_requirements_node()
        result = await requirements_node(isolated_test_state)
        
        # Verify the result
        assert "requirements" in result
        assert len(result["requirements"]) > 0
        assert result["current_step"] == "requirements_analysis"
        assert "requirements_analyst" in result["agent_outputs"]
    
        # Verify requirements structure
        requirements = result["requirements"]
        assert isinstance(requirements, list)
        assert len(requirements) > 0
        
        # Verify at least one requirement has required fields
        first_req = requirements[0]
        assert "id" in first_req
        assert "title" in first_req
        assert "description" in first_req
        assert "priority" in first_req


class TestArchitectureDesignerNode:
    """Tests for architecture designer node."""
    
    @pytest.fixture
    def isolated_node_factory(self, isolated_mock_llm):
        """Create isolated agent node factory."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        return AgentNodeFactory(isolated_mock_llm)
    
    @pytest.fixture
    def isolated_test_state_with_requirements(self):
        """Create isolated test state with requirements."""
        state = TestDataFactory.create_isolated_test_state()
        state["requirements"] = TestDataFactory.create_isolated_requirements()
        return state
    
    @pytest.fixture
    def isolated_mock_llm(self):
        """Create isolated mock LLM for each test."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = Mock()
        return mock
    
    def test_architecture_node_creation(self, isolated_node_factory):
        """Test that architecture node can be created."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        architecture_node = isolated_node_factory.create_architecture_node()
        assert callable(architecture_node)
    
    @pytest.mark.asyncio
    async def test_architecture_node_execution_success(self, isolated_node_factory, isolated_test_state_with_requirements, isolated_mock_llm):
        """Test successful architecture design execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Mock successful LLM response as JSON string
        mock_response = {
            "system_overview": "Test system overview",
            "architecture_pattern": "MVC",
            "technology_stack": {
                "frontend": ["React.js"],
                "backend": ["Node.js"]
            },
            "components": [],
            "data_flow": "Test data flow",
            "security_considerations": [],
            "scalability_considerations": [],
            "performance_considerations": [],
            "deployment_strategy": "Test deployment strategy",
            "risk_mitigation": [],
            "database_schema": {},
            "api_design": {}
        }
        
        # Mock the LLM to return our expected response as JSON string
        isolated_mock_llm.ainvoke.return_value = Mock(content=json.dumps(mock_response))

        # Create and execute node
        architecture_node = isolated_node_factory.create_architecture_node()
        result = await architecture_node(isolated_test_state_with_requirements)
        
        # Verify the result
        assert "architecture" in result
        assert result["current_step"] == "architecture_design"
        assert "architecture_designer" in result["agent_outputs"]
    
        # Verify architecture structure
        architecture = result["architecture"]
        assert isinstance(architecture, dict)
        assert "system_overview" in architecture
        assert "architecture_pattern" in architecture
        assert "technology_stack" in architecture


class TestCodeGeneratorNode:
    """Tests for code generator node."""
    
    @pytest.fixture
    def isolated_node_factory(self, isolated_mock_llm):
        """Create isolated agent node factory."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        return AgentNodeFactory(isolated_mock_llm)
    
    @pytest.fixture
    def isolated_test_state_with_architecture(self):
        """Create isolated test state with architecture."""
        state = TestDataFactory.create_isolated_test_state()
        state["requirements"] = TestDataFactory.create_isolated_requirements()
        state["architecture"] = TestDataFactory.create_isolated_architecture()
        return state
    
    @pytest.fixture
    def isolated_mock_llm(self):
        """Create isolated mock LLM for each test."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = Mock()
        return mock
    
    def test_code_generator_node_creation(self, isolated_node_factory):
        """Test that code generator node can be created."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        code_generator_node = isolated_node_factory.create_code_generator_node()
        assert callable(code_generator_node)
    
    @pytest.mark.asyncio
    async def test_code_generator_node_execution_success(self, isolated_node_factory, isolated_test_state_with_architecture, isolated_mock_llm):
        """Test successful code generation execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Mock successful LLM response with markdown code blocks
        unique_id = str(uuid.uuid4())[:8]
        mock_response = f"""## File: src/Calculator{unique_id}.js
```javascript
import React from 'react';

function Calculator{unique_id}() {{
  return <div>Calculator {unique_id}</div>;
}}

export default Calculator{unique_id};
```

## File: src/App{unique_id}.js
```javascript
import React from 'react';
import Calculator{unique_id} from './Calculator{unique_id}';

function App{unique_id}() {{
  return <Calculator{unique_id} />;
}}

export default App{unique_id};
```

## File: requirements.txt
```txt
react==18.2.0
react-dom==18.2.0
```"""
        
        # Mock the LLM to return our expected response as markdown string
        # Create a proper Mock that behaves like a real LLM response
        mock_response_obj = Mock()
        mock_response_obj.content = mock_response
        isolated_mock_llm.ainvoke.return_value = mock_response_obj

        # Create and execute node
        code_generator_node = isolated_node_factory.create_code_generator_node()
        result = await code_generator_node(isolated_test_state_with_architecture)
        
        # Verify the result
        assert "code_generation" in result
        assert "source_files" in result["code_generation"]
        assert len(result["code_generation"]["source_files"]) > 0
        assert "execution_history" in result
        assert "code_generator" in result["execution_history"]


class TestTestGeneratorNode:
    """Tests for test generator node."""
    
    @pytest.fixture
    def isolated_node_factory(self, isolated_mock_llm):
        """Create isolated agent node factory."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        return AgentNodeFactory(isolated_mock_llm)
    
    @pytest.fixture
    def isolated_test_state_with_code(self):
        """Create isolated test state with code files."""
        unique_id = str(uuid.uuid4())[:8]
        state = TestDataFactory.create_isolated_test_state()
        state["requirements"] = TestDataFactory.create_isolated_requirements()
        state["architecture"] = TestDataFactory.create_isolated_architecture()
        state["code_files"] = {
            f"src/Calculator{unique_id}.js": f"import React from 'react';\n\nfunction Calculator{unique_id}() {{\n  return <div>Calculator {unique_id}</div>;\n}}\n\nexport default Calculator{unique_id};",
            f"src/App{unique_id}.js": f"import React from 'react';\nimport Calculator{unique_id} from './Calculator{unique_id}';\n\nfunction App{unique_id}() {{\n  return <Calculator{unique_id} />;\n}}\n\nexport default App{unique_id};"
        }
        return state
    
    @pytest.fixture
    def isolated_mock_llm(self):
        """Create isolated mock LLM for each test."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = Mock()
        return mock
    
    def test_test_generator_node_creation(self, isolated_node_factory):
        """Test that test generator node can be created."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        test_generator_node = isolated_node_factory.create_test_generator_node()
        assert callable(test_generator_node)
    
    @pytest.mark.asyncio
    async def test_test_generator_node_execution_success(self, isolated_node_factory, isolated_test_state_with_code, isolated_mock_llm):
        """Test successful test generation execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Mock successful LLM response with test files
        unique_id = str(uuid.uuid4())[:8]
        mock_response = {
            "test_files": {
                f"tests/Calculator{unique_id}.test.js": f"import {{ render, screen }} from '@testing-library/react';\nimport Calculator{unique_id} from '../src/Calculator{unique_id}';\n\ntest('renders calculator', () => {{\n  render(<Calculator{unique_id} />);\n  expect(screen.getByText('Calculator {unique_id}')).toBeInTheDocument();\n}});\n",
                f"tests/App{unique_id}.test.js": f"import {{ render, screen }} from '@testing-library/react';\nimport App{unique_id} from '../src/App{unique_id}';\n\ntest('renders app', () => {{\n  render(<App{unique_id} />);\n  expect(screen.getByText('Calculator {unique_id}')).toBeInTheDocument();\n}});"
            },
            "test_strategy": {
                "unit_testing": "Jest and React Testing Library",
                "integration_testing": "End-to-end testing with Cypress",
                "test_data": "Mock data and fixtures",
                "coverage_goals": "90% code coverage"
            },
            "test_scenarios": [
                {
                    "id": f"SCENARIO-{unique_id}-001",
                    "description": f"Test scenario {unique_id}",
                    "test_cases": [f"Test case {unique_id}"],
                    "expected_outcomes": [f"Expected outcome {unique_id}"]
                }
            ],
            "test_environment": {
                "setup_instructions": [f"Setup step {unique_id}"],
                "dependencies": ["jest", "react-testing-library"],
                "configuration": f"Test configuration {unique_id}"
            }
        }
        
        # Mock the LLM to return our expected response as JSON string
        isolated_mock_llm.ainvoke.return_value = Mock(content=json.dumps(mock_response))

        # Create and execute node
        test_generator_node = isolated_node_factory.create_test_generator_node()
        result = await test_generator_node(isolated_test_state_with_code)
        
        # Verify the result
        assert "tests" in result
        assert len(result["tests"]) > 0
        assert result["current_step"] == "test_generation"
        assert "test_generator" in result["agent_outputs"]
    

class TestRealLLMIntegration:
    """Integration tests with real LLM usage to catch production issues."""
    
    @pytest.fixture
    def isolated_real_llm(self):
        """Create isolated real LLM instance for integration testing."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Use real LLM for integration tests
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            import streamlit as st
            
            # Get API key from Streamlit secrets
            api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                pytest.skip("GEMINI_API_KEY not available in Streamlit secrets for real LLM tests")
            
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.1,
                max_tokens=8192,
                google_api_key=api_key
            )
        except Exception as e:
            pytest.skip(f"Real LLM not available: {e}")
    
    @pytest.fixture
    def isolated_real_node_factory(self, isolated_real_llm):
        """Create isolated agent node factory with real LLM."""
        return AgentNodeFactory(isolated_real_llm)
    
    @pytest.fixture
    def isolated_real_test_state(self):
        """Create isolated test state for real LLM tests."""
        return TestDataFactory.create_isolated_test_state(
            "Create a simple todo list application with user authentication"
        )
    
    @pytest.mark.skipif(
        not LANGGRAPH_AVAILABLE, 
        reason="LangGraph not available"
    )
    @pytest.mark.skipif(
        not _has_valid_api_key(),
        reason="No valid API key configured for real LLM tests"
    )
    @pytest.mark.asyncio
    async def test_real_requirements_analysis(self, isolated_real_node_factory, isolated_real_test_state):
        """Test requirements analysis with real LLM."""
        
        # Create and execute node with real LLM
        requirements_node = isolated_real_node_factory.create_requirements_node()
        result = await requirements_node(isolated_real_test_state)
        
        # Verify the result
        assert "requirements" in result
        assert len(result["requirements"]) > 0
        assert result["current_step"] == "requirements_analysis"
        assert "requirements_analyst" in result["agent_outputs"]
        
        # Verify requirements structure
        requirements = result["requirements"]
        assert isinstance(requirements, list)
        assert len(requirements) > 0
        
        # Verify at least one requirement has required fields
        first_req = requirements[0]
        assert "id" in first_req
        assert "title" in first_req
        assert "description" in first_req
        assert "priority" in first_req
    
    @pytest.mark.skipif(
        not LANGGRAPH_AVAILABLE, 
        reason="LangGraph not available"
    )
    @pytest.mark.skipif(
        not _has_valid_api_key(),
        reason="No valid API key configured for real LLM tests"
    )
    @pytest.mark.asyncio
    async def test_real_architecture_design(self, isolated_real_node_factory, isolated_real_test_state):
        """Test architecture design with real LLM."""
        
        # Add requirements to test state
        test_state = isolated_real_test_state.copy()
        test_state["requirements"] = TestDataFactory.create_isolated_requirements()
        
        # Create and execute node with real LLM
        architecture_node = isolated_real_node_factory.create_architecture_node()
        result = await architecture_node(test_state)
        
        # Verify the result
        assert "architecture" in result
        assert result["current_step"] == "architecture_design"
        assert "architecture_designer" in result["agent_outputs"]
        
        # Verify architecture structure
        architecture = result["architecture"]
        assert isinstance(architecture, dict)
        assert "system_overview" in architecture
        assert "architecture_pattern" in architecture
        assert "technology_stack" in architecture
    
    @pytest.mark.skipif(
        not LANGGRAPH_AVAILABLE, 
        reason="LangGraph not available"
    )
    @pytest.mark.skipif(
        not _has_valid_api_key(),
        reason="No valid API key configured for real LLM tests"
    )
    @pytest.mark.asyncio
    async def test_real_code_generation(self, isolated_real_node_factory, isolated_real_test_state):
        """Test code generation with real LLM."""
        
        # Add requirements and architecture to test state
        test_state = isolated_real_test_state.copy()
        test_state["requirements"] = TestDataFactory.create_isolated_requirements()
        test_state["architecture"] = TestDataFactory.create_isolated_architecture()
        
        # Create and execute node with real LLM
        code_generator_node = isolated_real_node_factory.create_code_generator_node()
        result = await code_generator_node(test_state)
        
        # Verify the result
        assert "code_generation" in result
        assert "source_files" in result["code_generation"]
        assert "execution_history" in result
        assert "code_generator" in result["execution_history"]
        
        # Verify code files structure
        source_files = result["code_generation"]["source_files"]
        assert isinstance(source_files, dict)
        assert len(source_files) > 0
        
        # Verify at least one code file has content
        first_file = list(source_files.values())[0]
        assert isinstance(first_file, str)
        assert len(first_file) > 0
