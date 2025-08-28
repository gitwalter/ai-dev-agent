#!/usr/bin/env python3
"""
Advanced unit tests for remaining agent nodes.
Tests Code Reviewer, Security Analyst, and Documentation Generator nodes.
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

from tests.mocks.workflow.langgraph_workflow_manager import AgentNodeFactory, AgentState


class TestCodeReviewerNode:
    """Tests for the Code Reviewer node."""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = AsyncMock()
        return mock
    
    @pytest.fixture
    def node_factory(self, mock_llm):
        """Create agent node factory."""
        return AgentNodeFactory(mock_llm)
    
    @pytest.fixture
    def test_state_with_code(self):
        """Create test state with code files for code review."""
        return {
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
            "architecture": {
                "technology_stack": {
                    "frontend": "React.js",
                    "backend": "Node.js with Express"
                }
            },
            "code_files": {
                "src/Calculator.js": "import React from 'react';\n\nfunction Calculator() {\n  const [result, setResult] = useState(0);\n  \n  const add = (a, b) => a + b;\n  const subtract = (a, b) => a - b;\n  \n  return (\n    <div>\n      <h1>Calculator</h1>\n      <div>Result: {result}</div>\n    </div>\n  );\n}\n\nexport default Calculator;",
                "src/App.js": "import React from 'react';\nimport Calculator from './Calculator';\n\nfunction App() {\n  return <Calculator />;\n}\n\nexport default App;"
            },
            "tests": {
                "src/__tests__/Calculator.test.js": "import { render, screen } from '@testing-library/react';\nimport Calculator from '../Calculator';\n\ntest('renders calculator', () => {\n  render(<Calculator />);\n  expect(screen.getByText('Calculator')).toBeInTheDocument();\n});"
            },
            "documentation": {},
            "diagrams": {},
            "agent_outputs": {},
            "errors": [],
            "warnings": [],
            "approval_requests": [],
            "current_step": "code_review",
            "execution_history": []
        }
    
    def test_code_reviewer_node_creation(self, node_factory):
        """Test that code reviewer node can be created."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        code_reviewer_node = node_factory.create_code_reviewer_node()
        assert callable(code_reviewer_node), "Code reviewer node should be callable"
    
    @pytest.mark.asyncio
    async def test_code_reviewer_node_execution_success(self, node_factory, test_state_with_code, mock_llm):
        """Test successful code review execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Mock successful LLM response with code review
        mock_response = {
            "artifacts": [
                {
                    "name": "code_review_report.md",
                    "type": "markdown",
                    "content": "# Code Review Report\n\n## Issues Found\n- Missing error handling in Calculator component\n- useState import missing\n\n## Recommendations\n- Add proper error handling\n- Import useState from React"
                }
            ],
            "documentation": {
                "review_summary": "Code review completed with 2 issues identified",
                "quality_score": 7.5,
                "improvement_suggestions": [
                    "Add error handling for arithmetic operations",
                    "Include proper React imports",
                    "Add input validation"
                ]
            },
            "output": {
                "summary": "Code review identified 2 issues requiring attention",
                "critical_issues": 0,
                "minor_issues": 2,
                "suggestions": 3
            }
        }
        
        mock_llm.invoke.return_value = mock_response
        
        # Create and execute node
        code_reviewer_node = node_factory.create_code_reviewer_node()
        result = await code_reviewer_node(test_state_with_code)
        
        # Verify state updates
        assert result["current_step"] == "code_review", "Step should be updated"
        assert "code_reviewer" in result["agent_outputs"], "Agent output should be recorded"
        
        # Verify code review results
        agent_output = result["agent_outputs"]["code_reviewer"]
        assert "artifacts" in agent_output, "Should have artifacts"
        assert "documentation" in agent_output, "Should have documentation"
        assert "output" in agent_output, "Should have output"
        
        # Verify artifacts
        artifacts = agent_output["artifacts"]
        assert len(artifacts) > 0, "Should have at least one artifact"
        assert artifacts[0]["name"] == "code_review_report.md", "Should have review report"
        
        # Verify documentation
        documentation = agent_output["documentation"]
        assert "quality_score" in documentation, "Should have quality score"
        assert documentation["quality_score"] == 7.5, "Quality score should match"
    
    @pytest.mark.asyncio
    async def test_code_reviewer_node_no_code(self, node_factory, mock_llm):
        """Test code review with no code files."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Test state with no code files
        no_code_state = {
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
            "current_step": "code_review",
            "execution_history": []
        }
        
        # Mock LLM response for no code
        mock_response = {
            "artifacts": [
                {
                    "name": "no_code_report.md",
                    "type": "markdown",
                    "content": "# No Code Review Report\n\nNo code files available for review."
                }
            ],
            "documentation": {
                "review_summary": "No code files to review",
                "quality_score": 0,
                "improvement_suggestions": []
            },
            "output": {
                "summary": "No code files available for review",
                "critical_issues": 0,
                "minor_issues": 0,
                "suggestions": 0
            }
        }
        mock_llm.invoke.return_value = mock_response
        
        # Create and execute node
        code_reviewer_node = node_factory.create_code_reviewer_node()
        result = await code_reviewer_node(no_code_state)
        
        # Verify handling of no code files
        assert result["current_step"] == "code_review", "Step should be updated"
        assert "code_reviewer" in result["agent_outputs"], "Agent output should be recorded"


class TestSecurityAnalystNode:
    """Tests for the Security Analyst node."""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = AsyncMock()
        return mock
    
    @pytest.fixture
    def node_factory(self, mock_llm):
        """Create agent node factory."""
        return AgentNodeFactory(mock_llm)
    
    @pytest.fixture
    def test_state_with_code_and_architecture(self):
        """Create test state with code and architecture for security analysis."""
        return {
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
            "architecture": {
                "technology_stack": {
                    "frontend": "React.js",
                    "backend": "Node.js with Express",
                    "database": "SQLite"
                },
                "security_considerations": ["Input validation", "SQL injection prevention"]
            },
            "code_files": {
                "src/Calculator.js": "import React from 'react';\n\nfunction Calculator() {\n  const [result, setResult] = useState(0);\n  \n  const calculate = (operation, a, b) => {\n    // Direct eval - security risk\n    return eval(`${a} ${operation} ${b}`);\n  };\n  \n  return (\n    <div>\n      <h1>Calculator</h1>\n      <div>Result: {result}</div>\n    </div>\n  );\n}\n\nexport default Calculator;",
                "server/app.js": "const express = require('express');\nconst app = express();\n\napp.post('/calculate', (req, res) => {\n  const { operation, a, b } = req.body;\n  // SQL injection risk\n  const query = `SELECT ${operation}(${a}, ${b}) as result`;\n  // ...\n});"
            },
            "tests": {},
            "documentation": {},
            "diagrams": {},
            "agent_outputs": {},
            "errors": [],
            "warnings": [],
            "approval_requests": [],
            "current_step": "security_analysis",
            "execution_history": []
        }
    
    def test_security_analyst_node_creation(self, node_factory):
        """Test that security analyst node can be created."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        security_analyst_node = node_factory.create_security_analyst_node()
        assert callable(security_analyst_node), "Security analyst node should be callable"
    
    @pytest.mark.asyncio
    async def test_security_analyst_node_execution_success(self, node_factory, test_state_with_code_and_architecture, mock_llm):
        """Test successful security analysis execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Mock successful LLM response with security analysis
        mock_response = {
            "artifacts": [
                {
                    "name": "security_analysis_report.md",
                    "type": "markdown",
                    "content": "# Security Analysis Report\n\n## Critical Vulnerabilities\n- Use of eval() in Calculator.js (High Risk)\n- SQL injection vulnerability in server/app.js (High Risk)\n\n## Recommendations\n- Replace eval() with safe arithmetic functions\n- Use parameterized queries"
                },
                {
                    "name": "security_checklist.md",
                    "type": "markdown",
                    "content": "# Security Checklist\n\n- [ ] Remove eval() usage\n- [ ] Implement input validation\n- [ ] Use parameterized queries\n- [ ] Add authentication"
                }
            ],
            "documentation": {
                "security_summary": "Security analysis identified 2 critical vulnerabilities",
                "risk_level": "High",
                "vulnerability_count": 2,
                "mitigation_plan": [
                    "Replace eval() with safe arithmetic functions",
                    "Implement proper input validation",
                    "Use parameterized database queries",
                    "Add authentication and authorization"
                ]
            },
            "output": {
                "summary": "Security analysis found 2 critical vulnerabilities requiring immediate attention",
                "critical_vulnerabilities": 2,
                "medium_vulnerabilities": 0,
                "low_vulnerabilities": 0,
                "recommendations": 4
            }
        }
        
        mock_llm.invoke.return_value = mock_response
        
        # Create and execute node
        security_analyst_node = node_factory.create_security_analyst_node()
        result = await security_analyst_node(test_state_with_code_and_architecture)
        
        # Verify state updates
        assert result["current_step"] == "security_analysis", "Step should be updated"
        assert "security_analyst" in result["agent_outputs"], "Agent output should be recorded"
        
        # Verify security analysis results
        agent_output = result["agent_outputs"]["security_analyst"]
        assert "artifacts" in agent_output, "Should have artifacts"
        assert "documentation" in agent_output, "Should have documentation"
        assert "output" in agent_output, "Should have output"
        
        # Verify artifacts
        artifacts = agent_output["artifacts"]
        assert len(artifacts) >= 2, "Should have at least 2 artifacts"
        artifact_names = [a["name"] for a in artifacts]
        assert "security_analysis_report.md" in artifact_names, "Should have security report"
        assert "security_checklist.md" in artifact_names, "Should have security checklist"
        
        # Verify documentation
        documentation = agent_output["documentation"]
        assert "risk_level" in documentation, "Should have risk level"
        assert documentation["risk_level"] == "High", "Risk level should be High"
        assert documentation["vulnerability_count"] == 2, "Should have 2 vulnerabilities"
    
    @pytest.mark.asyncio
    async def test_security_analyst_node_no_code(self, node_factory, mock_llm):
        """Test security analysis with no code files."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Test state with no code files
        no_code_state = {
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
            "current_step": "security_analysis",
            "execution_history": []
        }
        
        # Mock LLM response for no code
        mock_response = {
            "artifacts": [
                {
                    "name": "no_code_security_report.md",
                    "type": "markdown",
                    "content": "# No Code Security Analysis Report\n\nNo code files available for security analysis."
                }
            ],
            "documentation": {
                "security_summary": "No code files to analyze",
                "risk_level": "Unknown",
                "vulnerability_count": 0,
                "mitigation_plan": []
            },
            "output": {
                "summary": "No code files available for security analysis",
                "critical_vulnerabilities": 0,
                "medium_vulnerabilities": 0,
                "low_vulnerabilities": 0,
                "recommendations": 0
            }
        }
        mock_llm.invoke.return_value = mock_response
        
        # Create and execute node
        security_analyst_node = node_factory.create_security_analyst_node()
        result = await security_analyst_node(no_code_state)
        
        # Verify handling of no code files
        assert result["current_step"] == "security_analysis", "Step should be updated"
        assert "security_analyst" in result["agent_outputs"], "Agent output should be recorded"


class TestDocumentationGeneratorNode:
    """Tests for the Documentation Generator node."""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = AsyncMock()
        return mock
    
    @pytest.fixture
    def node_factory(self, mock_llm):
        """Create agent node factory."""
        return AgentNodeFactory(mock_llm)
    
    @pytest.fixture
    def test_state_with_complete_project(self):
        """Create test state with complete project for documentation generation."""
        return {
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
                },
                {
                    "id": "REQ-002",
                    "title": "Arithmetic Operations",
                    "description": "Implement addition, subtraction, multiplication, and division",
                    "priority": "high",
                    "type": "functional"
                }
            ],
            "architecture": {
                "technology_stack": {
                    "frontend": "React.js",
                    "backend": "Node.js with Express",
                    "database": "SQLite"
                },
                "components": [
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
                ]
            },
            "code_files": {
                "src/Calculator.js": "import React from 'react';\n\nfunction Calculator() {\n  const [result, setResult] = useState(0);\n  \n  const add = (a, b) => a + b;\n  const subtract = (a, b) => a - b;\n  \n  return (\n    <div>\n      <h1>Calculator</h1>\n      <div>Result: {result}</div>\n    </div>\n  );\n}\n\nexport default Calculator;",
                "src/App.js": "import React from 'react';\nimport Calculator from './Calculator';\n\nfunction App() {\n  return <Calculator />;\n}\n\nexport default App;"
            },
            "tests": {
                "src/__tests__/Calculator.test.js": "import { render, screen } from '@testing-library/react';\nimport Calculator from '../Calculator';\n\ntest('renders calculator', () => {\n  render(<Calculator />);\n  expect(screen.getByText('Calculator')).toBeInTheDocument();\n});"
            },
            "documentation": {},
            "diagrams": {},
            "agent_outputs": {
                "requirements_analyst": {
                    "summary": "Requirements analysis completed"
                },
                "architecture_designer": {
                    "summary": "Architecture design completed"
                },
                "code_generator": {
                    "summary": "Code generation completed"
                },
                "test_generator": {
                    "summary": "Test generation completed"
                }
            },
            "errors": [],
            "warnings": [],
            "approval_requests": [],
            "current_step": "documentation_generation",
            "execution_history": []
        }
    
    def test_documentation_generator_node_creation(self, node_factory):
        """Test that documentation generator node can be created."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        documentation_generator_node = node_factory.create_documentation_generator_node()
        assert callable(documentation_generator_node), "Documentation generator node should be callable"
    
    @pytest.mark.asyncio
    async def test_documentation_generator_node_execution_success(self, node_factory, test_state_with_complete_project, mock_llm):
        """Test successful documentation generation execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Mock successful LLM response with documentation
        mock_response = {
            "documentation": {
                "README.md": "# Calculator App\n\nA simple calculator application built with React.js and Node.js.\n\n## Features\n- Basic arithmetic operations\n- User-friendly interface\n\n## Installation\n```bash\nnpm install\nnpm start\n```",
                "API_DOCUMENTATION.md": "# API Documentation\n\n## Endpoints\n- POST /calculate - Perform arithmetic operations\n\n## Request Format\n```json\n{\n  \"operation\": \"add\",\n  \"a\": 5,\n  \"b\": 3\n}\n```",
                "ARCHITECTURE.md": "# Architecture Documentation\n\n## Technology Stack\n- Frontend: React.js\n- Backend: Node.js with Express\n- Database: SQLite\n\n## Components\n- Calculator UI (Frontend)\n- Calculator Service (Backend)"
            },
            "diagrams": {
                "system_architecture.png": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "data_flow.png": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            },
            "summary": "Generated comprehensive documentation including README, API docs, architecture docs, and system diagrams"
        }
        
        mock_llm.invoke.return_value = mock_response
        
        # Create and execute node
        documentation_generator_node = node_factory.create_documentation_generator_node()
        result = await documentation_generator_node(test_state_with_complete_project)
        
        # Verify state updates
        assert result["current_step"] == "documentation_generation", "Step should be updated"
        assert "documentation_generator" in result["agent_outputs"], "Agent output should be recorded"
        
        # Verify documentation generation results
        agent_output = result["agent_outputs"]["documentation_generator"]
        assert "documentation" in agent_output, "Should have documentation"
        assert "diagrams" in agent_output, "Should have diagrams"
        assert "summary" in agent_output, "Should have summary"
        
        # Verify documentation files
        documentation = agent_output["documentation"]
        assert "README.md" in documentation, "Should have README"
        assert "API_DOCUMENTATION.md" in documentation, "Should have API docs"
        assert "ARCHITECTURE.md" in documentation, "Should have architecture docs"
        
        # Verify diagrams
        diagrams = agent_output["diagrams"]
        assert "system_architecture.png" in diagrams, "Should have system architecture diagram"
        assert "data_flow.png" in diagrams, "Should have data flow diagram"
        
        # Verify content
        readme_content = documentation["README.md"]
        assert "# Calculator App" in readme_content, "README should have title"
        assert "React.js" in readme_content, "README should mention React.js"
    
    @pytest.mark.asyncio
    async def test_documentation_generator_node_minimal_project(self, node_factory, mock_llm):
        """Test documentation generation with minimal project data."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Test state with minimal data
        minimal_state = {
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
            "current_step": "documentation_generation",
            "execution_history": []
        }
        
        # Mock LLM response for minimal project
        mock_response = {
            "documentation": {
                "README.md": "# Test Calculator\n\nA simple calculator application.\n\n## Project Overview\nThis project was created based on the context: Create a simple calculator app.\n\n## Getting Started\nNo specific installation instructions available."
            },
            "diagrams": {},
            "summary": "Generated basic documentation for minimal project"
        }
        mock_llm.invoke.return_value = mock_response
        
        # Create and execute node
        documentation_generator_node = node_factory.create_documentation_generator_node()
        result = await documentation_generator_node(minimal_state)
        
        # Verify handling of minimal project
        assert result["current_step"] == "documentation_generation", "Step should be updated"
        assert "documentation_generator" in result["agent_outputs"], "Agent output should be recorded"
        
        # Verify basic documentation is still generated
        agent_output = result["agent_outputs"]["documentation_generator"]
        assert "documentation" in agent_output, "Should have documentation"
        assert "README.md" in agent_output["documentation"], "Should have basic README"
    
    @pytest.mark.asyncio
    async def test_documentation_generator_node_error_handling(self, node_factory, test_state_with_complete_project, mock_llm):
        """Test documentation generation error handling."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Mock LLM failure
        mock_llm.invoke.side_effect = Exception("Documentation generation failed")
        
        # Create and execute node
        documentation_generator_node = node_factory.create_documentation_generator_node()
        result = await documentation_generator_node(test_state_with_complete_project)
        
        # Verify error handling
        assert len(result["errors"]) > 0, "Errors should be recorded"
        assert "Documentation generation failed" in str(result["errors"][0]), "Error message should be captured"
        assert result["current_step"] == "documentation_generation", "Step should remain the same"
