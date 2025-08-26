#!/usr/bin/env python3
"""
Tests for LangGraph agent nodes.
Comprehensive test suite for individual agent node functionality.
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, patch, AsyncMock

# Test imports
try:
    from langgraph.graph import StateGraph, END, START
    from langchain.output_parsers import PydanticOutputParser
    from langchain.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

from langgraph_workflow_manager import LangGraphWorkflowManager, AgentNodeFactory, AgentState
from utils.structured_outputs import RequirementsAnalysisOutput, ArchitectureDesignOutput


class TestRequirementsAnalystNode:
    """Tests for requirements analyst node."""
    
    @pytest.fixture
    def node_factory(self, mock_llm):
        """Create agent node factory."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        return AgentNodeFactory(mock_llm)
    
    @pytest.fixture
    def test_state(self):
        """Create test state."""
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
            "current_step": "requirements_analysis",
            "execution_history": []
        }
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = AsyncMock()
        mock.ainvoke = AsyncMock()
        return mock
    
    def test_requirements_node_creation(self, node_factory):
        """Test that requirements node can be created."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        requirements_node = node_factory.create_requirements_node()
        assert callable(requirements_node)
    
    @pytest.mark.asyncio
    async def test_requirements_node_execution_success(self, node_factory, test_state, mock_llm):
        """Test successful requirements analysis execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Mock successful LLM response with correct structure
        mock_response = RequirementsAnalysisOutput(
            functional_requirements=[
                {
                    "id": "FR-001",
                    "title": "Basic Calculator Interface",
                    "description": "Create a user interface for basic arithmetic operations",
                    "priority": "high",
                    "acceptance_criteria": ["User can perform basic math operations"]
                },
                {
                    "id": "FR-002",
                    "title": "Arithmetic Operations",
                    "description": "Implement addition, subtraction, multiplication, and division",
                    "priority": "high",
                    "acceptance_criteria": ["All basic operations work correctly"]
                }
            ],
            non_functional_requirements=[
                {
                    "id": "NFR-001",
                    "title": "Performance",
                    "description": "Calculator must respond within 1 second",
                    "category": "performance",
                    "measurement": "response time < 1s"
                }
            ],
            user_stories=[
                {
                    "id": "US-001",
                    "as_a": "user",
                    "i_want": "to perform basic calculations",
                    "so_that": "I can solve mathematical problems quickly"
                }
            ],
            technical_constraints=["Must work on web browsers", "Must support basic arithmetic"],
            assumptions=["User has basic computer literacy"],
            risks=[
                {
                    "risk": "Complex calculations may be slow",
                    "probability": "low",
                    "impact": "medium",
                    "mitigation": "Implement efficient algorithms"
                }
            ],
            summary={
                "total_functional_requirements": 2,
                "total_non_functional_requirements": 1,
                "total_user_stories": 1,
                "estimated_complexity": "simple",
                "recommended_tech_stack": ["HTML", "CSS", "JavaScript"],
                "estimated_timeline": "1 week",
                "key_success_factors": ["Simple interface", "Accurate calculations"]
            }
        )
        
        mock_llm.ainvoke.return_value = mock_response

        # Create and execute node
        requirements_node = node_factory.create_requirements_node()
        result = await requirements_node(test_state)
        
        # Verify the result
        assert "requirements" in result
        assert len(result["requirements"]) > 0
        assert result["current_step"] == "requirements_analysis"
        assert "requirements_analyst" in result["agent_outputs"]
    
    @pytest.mark.asyncio
    async def test_requirements_node_execution_failure(self, node_factory, test_state, mock_llm):
        """Test requirements analysis with LLM failure."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Mock LLM failure
        mock_llm.ainvoke.side_effect = Exception("LLM API error")

        # Create and execute node
        requirements_node = node_factory.create_requirements_node()
        result = await requirements_node(test_state)
        
        # Verify error handling
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert "LLM API error" in str(result["errors"][0])
    
    @pytest.mark.asyncio
    async def test_requirements_node_empty_context(self, node_factory, mock_llm):
        """Test requirements analysis with empty project context."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Test state with empty context
        empty_state = {
            "project_context": "",
            "project_name": "test-empty",
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
            "current_step": "requirements_analysis",
            "execution_history": []
        }

        # Mock LLM response for empty context with correct structure
        mock_response = RequirementsAnalysisOutput(
            functional_requirements=[],
            non_functional_requirements=[],
            user_stories=[],
            technical_constraints=[],
            assumptions=[],
            risks=[],
            summary={
                "total_functional_requirements": 0,
                "total_non_functional_requirements": 0,
                "total_user_stories": 0,
                "estimated_complexity": "unknown",
                "recommended_tech_stack": [],
                "estimated_timeline": "unknown",
                "key_success_factors": ["Clear project requirements needed"]
            }
        )
        
        mock_llm.ainvoke.return_value = mock_response

        # Create and execute node
        requirements_node = node_factory.create_requirements_node()
        result = await requirements_node(empty_state)
        
        # Verify the result
        assert "warnings" in result
        assert len(result["warnings"]) > 0
        assert "empty project context" in str(result["warnings"][0]).lower()


class TestArchitectureDesignerNode:
    """Tests for architecture designer node."""
    
    @pytest.fixture
    def node_factory(self, mock_llm):
        """Create agent node factory."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        return AgentNodeFactory(mock_llm)
    
    @pytest.fixture
    def test_state_with_requirements(self):
        """Create test state with requirements."""
        return {
            "project_context": "Create a simple calculator app",
            "project_name": "test-calculator",
            "session_id": "test-session-123",
            "requirements": [
                {
                    "id": "FR-001",
                    "title": "Basic Calculator Interface",
                    "description": "Create a user interface for basic arithmetic operations",
                    "priority": "high",
                    "type": "functional"
                }
            ],
            "architecture": {},
            "code_files": {},
            "tests": {},
            "documentation": {},
            "diagrams": {},
            "agent_outputs": {},
            "errors": [],
            "warnings": [],
            "approval_requests": [],
            "current_step": "architecture_design",
            "execution_history": []
        }
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = Mock()
        return mock
    
    def test_architecture_node_creation(self, node_factory):
        """Test that architecture node can be created."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        architecture_node = node_factory.create_architecture_node()
        assert callable(architecture_node)
    
    @pytest.mark.asyncio
    async def test_architecture_node_execution_success(self, node_factory, test_state_with_requirements, mock_llm):
        """Test successful architecture design execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Mock successful LLM response with correct structure
        mock_response = ArchitectureDesignOutput(
            system_overview="A simple web-based calculator application with a clean user interface for performing basic arithmetic operations.",
            architecture_pattern="MVC",
            components=[
                {
                    "name": "Calculator UI",
                    "type": "frontend",
                    "description": "React component for calculator interface"
                },
                {
                    "name": "Calculator Service",
                    "type": "backend",
                    "description": "Express.js service for arithmetic operations"
                }
            ],
            data_flow="User input flows through the UI to the service layer, which processes calculations and returns results to the display.",
            technology_stack={
                "frontend": ["React.js", "HTML5", "CSS3"],
                "backend": ["Node.js", "Express.js"],
                "database": ["SQLite"],
                "deployment": ["Docker"]
            },
            security_considerations=["Input validation", "SQL injection prevention"],
            scalability_considerations=["Horizontal scaling", "Load balancing"],
            performance_considerations=["Caching strategies", "Database indexing"],
            deployment_strategy="Containerized deployment using Docker with simple orchestration for easy scaling and maintenance.",
            risk_mitigation=[
                {
                    "risk": "Single point of failure",
                    "mitigation": "Implement redundancy and failover mechanisms"
                }
            ],
            database_schema={
                "tables": [
                    {
                        "name": "calculations",
                        "columns": ["id", "operation", "result", "timestamp"],
                        "relationships": []
                    }
                ]
            },
            api_design={
                "endpoints": [
                    {
                        "path": "/calculate",
                        "method": "POST",
                        "description": "Perform arithmetic calculation",
                        "authentication": "none"
                    }
                ]
            }
        )
        
        mock_llm.ainvoke.return_value = mock_response

        # Create and execute node
        architecture_node = node_factory.create_architecture_node()
        result = await architecture_node(test_state_with_requirements)
        
        # Verify the result
        assert "architecture" in result
        assert result["current_step"] == "architecture_design"
        assert "architecture_designer" in result["agent_outputs"]
    
    @pytest.mark.asyncio
    async def test_architecture_node_no_requirements(self, node_factory, mock_llm):
        """Test architecture design with no requirements."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Test state with no requirements
        no_requirements_state = {
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
            "current_step": "architecture_design",
            "execution_history": []
        }

        # Mock LLM response for no requirements with correct structure
        mock_response = ArchitectureDesignOutput(
            system_overview="A basic calculator application with minimal architecture due to lack of detailed requirements.",
            architecture_pattern="Basic",
            components=[],
            data_flow="Simple data flow from user input to calculation processing and result display.",
            technology_stack={
                "frontend": ["HTML", "CSS", "JavaScript"],
                "backend": [],
                "database": [],
                "deployment": []
            },
            security_considerations=[],
            scalability_considerations=[],
            performance_considerations=[],
            deployment_strategy="Simple static file deployment with basic web server configuration.",
            risk_mitigation=[],
            database_schema={},
            api_design={}
        )
        
        mock_llm.ainvoke.return_value = mock_response

        # Create and execute node
        architecture_node = node_factory.create_architecture_node()
        result = await architecture_node(no_requirements_state)
        
        # Verify the result
        assert "warnings" in result
        assert len(result["warnings"]) > 0
        assert "no requirements" in str(result["warnings"][0]).lower()


class TestCodeGeneratorNode:
    """Tests for code generator node."""
    
    @pytest.fixture
    def node_factory(self, mock_llm):
        """Create agent node factory."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        return AgentNodeFactory(mock_llm)
    
    @pytest.fixture
    def test_state_with_architecture(self):
        """Create test state with architecture."""
        return {
            "project_context": "Create a simple calculator app",
            "project_name": "test-calculator",
            "session_id": "test-session-123",
            "requirements": [
                {
                    "id": "FR-001",
                    "title": "Basic Calculator Interface",
                    "description": "Create a user interface for basic arithmetic operations",
                    "priority": "high",
                    "type": "functional"
                }
            ],
            "architecture": {
                "components": [
                    {
                        "name": "Calculator UI",
                        "type": "frontend",
                        "description": "React component for calculator interface"
                    }
                ],
                "technology_stack": {
                    "frontend": ["React.js"],
                    "backend": ["Node.js with Express"]
                }
            },
            "code_files": {},
            "tests": {},
            "documentation": {},
            "diagrams": {},
            "agent_outputs": {},
            "errors": [],
            "warnings": [],
            "approval_requests": [],
            "current_step": "code_generation",
            "execution_history": []
        }
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = Mock()
        return mock
    
    def test_code_generator_node_creation(self, node_factory):
        """Test that code generator node can be created."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        code_generator_node = node_factory.create_code_generator_node()
        assert callable(code_generator_node)
    
    @pytest.mark.asyncio
    async def test_code_generator_node_execution_success(self, node_factory, test_state_with_architecture, mock_llm):
        """Test successful code generation execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Mock successful LLM response with code files
        mock_response = {
            "code_files": {
                "src/Calculator.js": "import React from 'react';\n\nfunction Calculator() {\n  return <div>Calculator</div>;\n}\n\nexport default Calculator;",
                "src/App.js": "import React from 'react';\nimport Calculator from './Calculator';\n\nfunction App() {\n  return <Calculator />;\n}\n\nexport default App;"
            },
            "summary": "Generated React calculator components"
        }
    
        mock_llm.ainvoke.return_value = mock_response

        # Create and execute node
        code_generator_node = node_factory.create_code_generator_node()
        result = await code_generator_node(test_state_with_architecture)
        
        # Verify the result
        assert "code_files" in result
        assert len(result["code_files"]) > 0
        assert result["current_step"] == "code_generation"
        assert "code_generator" in result["agent_outputs"]
    
    @pytest.mark.asyncio
    async def test_code_generator_node_no_architecture(self, node_factory, mock_llm):
        """Test code generation with no architecture."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Test state with no architecture
        no_architecture_state = {
            "project_context": "Create a simple calculator app",
            "project_name": "test-calculator",
            "session_id": "test-session-123",
            "requirements": [
                {
                    "id": "REQ-001",
                    "title": "Basic Calculator Interface",
                    "description": "Create a user interface for basic arithmetic operations",
                    "priority": "high",
                    "type": "functional"
                }
            ],
            "architecture": {},
            "code_files": {},
            "tests": {},
            "documentation": {},
            "diagrams": {},
            "agent_outputs": {},
            "errors": [],
            "warnings": [],
            "approval_requests": [],
            "current_step": "code_generation",
            "execution_history": []
        }

        # Mock LLM response for no architecture
        mock_response = {
            "code_files": {
                "index.html": "<!DOCTYPE html>\n<html>\n<head><title>Calculator</title></head>\n<body><h1>Calculator</h1></body>\n</html>"
            },
            "summary": "Generated basic HTML calculator"
        }
        mock_llm.ainvoke.return_value = mock_response

        # Create and execute node
        code_generator_node = node_factory.create_code_generator_node()
        result = await code_generator_node(no_architecture_state)
        
        # Verify the result
        assert "warnings" in result
        assert len(result["warnings"]) > 0
        assert "no architecture" in str(result["warnings"][0]).lower()


class TestTestGeneratorNode:
    """Tests for test generator node."""
    
    @pytest.fixture
    def node_factory(self, mock_llm):
        """Create agent node factory."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        return AgentNodeFactory(mock_llm)
    
    @pytest.fixture
    def test_state_with_code(self):
        """Create test state with code files."""
        return {
            "project_context": "Create a simple calculator app",
            "project_name": "test-calculator",
            "session_id": "test-session-123",
            "requirements": [
                {
                    "id": "FR-001",
                    "title": "Basic Calculator Interface",
                    "description": "Create a user interface for basic arithmetic operations",
                    "priority": "high",
                    "type": "functional"
                }
            ],
            "architecture": {
                "technology_stack": {
                    "frontend": ["React.js"],
                    "backend": ["Node.js with Express"]
                }
            },
            "code_files": {
                "src/Calculator.js": "import React from 'react';\n\nfunction Calculator() {\n  return <div>Calculator</div>;\n}\n\nexport default Calculator;",
                "src/App.js": "import React from 'react';\nimport Calculator from './Calculator';\n\nfunction App() {\n  return <Calculator />;\n}\n\nexport default App;"
            },
            "tests": {},
            "documentation": {},
            "diagrams": {},
            "agent_outputs": {},
            "errors": [],
            "warnings": [],
            "approval_requests": [],
            "current_step": "test_generation",
            "execution_history": []
        }
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = Mock()
        return mock
    
    def test_test_generator_node_creation(self, node_factory):
        """Test that test generator node can be created."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        test_generator_node = node_factory.create_test_generator_node()
        assert callable(test_generator_node)
    
    @pytest.mark.asyncio
    async def test_test_generator_node_execution_success(self, node_factory, test_state_with_code, mock_llm):
        """Test successful test generation execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Mock successful LLM response with test files
        from utils.structured_outputs import TestFile
        
        mock_response = TestGenerationOutput(
            test_files={
                "src/__tests__/Calculator.test.js": TestFile(
                    filename="src/__tests__/Calculator.test.js",
                    content="import { render, screen } from '@testing-library/react';\nimport Calculator from '../Calculator';\n\ntest('renders calculator', () => {\n  render(<Calculator />);\n  expect(screen.getByText('Calculator')).toBeInTheDocument();\n});",
                    test_type="unit",
                    coverage_target="80%",
                    dependencies=["@testing-library/react", "jest"]
                ),
                "src/__tests__/App.test.js": TestFile(
                    filename="src/__tests__/App.test.js",
                    content="import { render, screen } from '@testing-library/react';\nimport App from '../App';\n\ntest('renders app', () => {\n  render(<App />);\n  expect(screen.getByText('Calculator')).toBeInTheDocument();\n});",
                    test_type="unit",
                    coverage_target="80%",
                    dependencies=["@testing-library/react", "jest"]
                )
            },
            test_categories={
                "unit_tests": ["Component tests", "Function tests"],
                "integration_tests": ["API tests", "User interaction tests"]
            },
            test_data={
                "fixtures": "Sample test data for calculator components",
                "mocks": "Mock objects for isolated testing",
                "test_databases": "Test database setup"
            },
            coverage_targets={
                "unit_test_coverage": "80%",
                "integration_test_coverage": "60%",
                "critical_path_coverage": "100%"
            },
            testing_strategy={
                "framework": "jest",
                "assertion_library": "jest assertions",
                "mocking_framework": "jest.mock",
                "coverage_tool": "jest --coverage"
            },
            test_execution_plan=[
                "1. Run unit tests: npm test",
                "2. Run integration tests: npm run test:integration",
                "3. Generate coverage report: npm run test:coverage"
            ]
        )

        mock_llm.ainvoke.return_value = mock_response

        # Create and execute node
        test_generator_node = node_factory.create_test_generator_node()
        result = await test_generator_node(test_state_with_code)
        
        # Verify the result
        assert "tests" in result
        assert len(result["tests"]) > 0
        assert result["current_step"] == "test_generation"
        assert "test_generator" in result["agent_outputs"]
    
    @pytest.mark.asyncio
    async def test_test_generator_node_no_code(self, node_factory, mock_llm):
        """Test test generation with no code files."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")

        # Test state with no code files
        no_code_state = {
            "project_context": "Create a simple calculator app",
            "project_name": "test-calculator",
            "session_id": "test-session-123",
            "requirements": [
                {
                    "id": "REQ-001",
                    "title": "Basic Calculator Interface",
                    "description": "Create a user interface for basic arithmetic operations",
                    "priority": "high",
                    "type": "functional"
                }
            ],
            "architecture": {},
            "code_files": {},
            "tests": {},
            "documentation": {},
            "diagrams": {},
            "agent_outputs": {},
            "errors": [],
            "warnings": [],
            "approval_requests": [],
            "current_step": "test_generation",
            "execution_history": []
        }

        # Mock LLM response for no code
        mock_response = TestGenerationOutput(
            test_files={
                "test_placeholder.js": TestFile(
                    filename="test_placeholder.js",
                    content="// Placeholder test file\n// No code files to test",
                    test_type="unit",
                    coverage_target="0%",
                    dependencies=[]
                )
            },
            test_categories={
                "unit_tests": ["Placeholder tests"],
                "integration_tests": []
            },
            test_data={
                "fixtures": "No fixtures available",
                "mocks": "No mocks needed",
                "test_databases": "No database tests"
            },
            coverage_targets={
                "unit_test_coverage": "0%",
                "integration_test_coverage": "0%",
                "critical_path_coverage": "0%"
            },
            testing_strategy={
                "framework": "none",
                "assertion_library": "none",
                "mocking_framework": "none",
                "coverage_tool": "none"
            },
            test_execution_plan=[
                "1. No tests to run - no code files available"
            ]
        )
        mock_llm.ainvoke.return_value = mock_response

        # Create and execute node
        test_generator_node = node_factory.create_test_generator_node()
        result = await test_generator_node(no_code_state)
        
        # Verify the result
        assert "warnings" in result
        assert len(result["warnings"]) > 0
        assert "no code files" in str(result["warnings"][0]).lower()
