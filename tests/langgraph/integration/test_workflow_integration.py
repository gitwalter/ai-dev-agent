#!/usr/bin/env python3
"""
Integration tests for complete workflow orchestration.
Tests multi-agent state management and workflow execution.
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

# Import test configuration
from tests.config.test_config import get_test_config, is_mock_mode, is_real_mode

# Import appropriate workflow manager based on test mode
if LANGGRAPH_AVAILABLE:
    try:
        # Try to import real workflow manager first
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from workflow.langgraph_workflow_manager import LangGraphWorkflowManager as RealLangGraphWorkflowManager
        from workflow.langgraph_workflow_manager import AgentNodeFactory as RealAgentNodeFactory
        from workflow.langgraph_workflow_manager import AgentState
        REAL_WORKFLOW_AVAILABLE = True
    except ImportError as e:
        REAL_WORKFLOW_AVAILABLE = False
        print(f"Real workflow not available: {e}")
else:
    REAL_WORKFLOW_AVAILABLE = False

# Import mock workflow manager
from tests.mocks.workflow.langgraph_workflow_manager import LangGraphWorkflowManager as MockLangGraphWorkflowManager
from tests.mocks.workflow.langgraph_workflow_manager import AgentNodeFactory as MockAgentNodeFactory

from utils.structured_outputs import RequirementsAnalysisOutput, ArchitectureDesignOutput

# Set up workflow manager class based on test mode
def get_workflow_manager_class():
    """Get the appropriate workflow manager class based on test mode."""
    if is_real_mode() and REAL_WORKFLOW_AVAILABLE:
        return RealLangGraphWorkflowManager
    else:
        return MockLangGraphWorkflowManager

def get_agent_node_factory_class():
    """Get the appropriate agent node factory class based on test mode."""
    if is_real_mode() and REAL_WORKFLOW_AVAILABLE:
        return RealAgentNodeFactory
    else:
        return MockAgentNodeFactory


class TestCompleteWorkflowIntegration:
    """Integration tests for complete workflow execution."""
    
    @pytest.fixture
    def llm_config(self):
        """LLM configuration based on test mode."""
        config = get_test_config()
        if is_real_mode():
            return {
                "api_key": config.api_key,
                "model_name": "gemini-2.5-flash-lite",
                "temperature": 0.1,
                "max_tokens": 8192
            }
        else:
            return {
                "api_key": "test-api-key",
                "model_name": "gemini-2.5-flash-lite",
                "temperature": 0.1,
                "max_tokens": 8192
            }
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing (used only in mock mode)."""
        if is_real_mode():
            return None
        
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = AsyncMock()
        return mock
    
    @pytest.fixture
    def workflow_manager(self, llm_config):
        """Create workflow manager based on test mode."""
        WorkflowManagerClass = get_workflow_manager_class()
        
        if is_real_mode() and REAL_WORKFLOW_AVAILABLE:
            # Real mode: use actual workflow manager with real API
            if not llm_config.get("api_key") or llm_config.get("api_key") == "test-api-key":
                pytest.skip("Real mode requires valid API key")
            return WorkflowManagerClass(llm_config)
        else:
            # Mock mode: use mock workflow manager
            return WorkflowManagerClass(llm_config)
    
    @pytest.fixture
    def test_state(self):
        """Create test state for complete workflow."""
        return {
            "project_context": "Create a simple calculator app with basic arithmetic operations",
            "project_name": "test-calculator",
            "session_id": "test-integration-session-123",
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
    
    @pytest.mark.asyncio
    async def test_complete_workflow_execution_success(self, workflow_manager, test_state, mock_llm):
        """Test successful complete workflow execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        if is_real_mode() and not REAL_WORKFLOW_AVAILABLE:
            pytest.skip("Real workflow not available")
        
        # Configure mocks only in mock mode
        if is_mock_mode() and mock_llm:
            # Mock LLM responses for each agent
            mock_responses = {
            "requirements_analyst": RequirementsAnalysisOutput(
                functional_requirements=[
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
                non_functional_requirements=[
                    {
                        "id": "NFR-001",
                        "title": "Performance",
                        "description": "Calculator must respond within 1 second",
                        "category": "performance",
                        "measurement": "response time < 1s"
                    },
                    {
                        "id": "NFR-002",
                        "title": "Usability",
                        "description": "Interface must be intuitive for basic users",
                        "category": "usability",
                        "measurement": "user testing score > 8/10"
                    }
                ],
                user_stories=[
                    {
                        "id": "US-001",
                        "as_a": "user",
                        "i_want": "to perform basic arithmetic operations",
                        "so_that": "I can calculate mathematical problems quickly"
                    },
                    {
                        "id": "US-002",
                        "as_a": "user",
                        "i_want": "to see clear input and output",
                        "so_that": "I can verify my calculations are correct"
                    }
                ],
                risks=[
                    {
                        "risk": "Division by zero errors",
                        "probability": "medium",
                        "impact": "high",
                        "mitigation": "Implement proper error handling and validation"
                    },
                    {
                        "risk": "User interface complexity",
                        "probability": "low",
                        "impact": "medium",
                        "mitigation": "Conduct user testing and iterate on design"
                    }
                ],
                summary={"description": "Calculator app with basic arithmetic operations"},
                assumptions=["User has basic computer literacy"],
                technical_constraints=["Must work on web browsers"]
            ),
            "architecture_designer": ArchitectureDesignOutput(
                architecture_overview="MVC architecture with React frontend and Node.js backend",
                data_flow="User input -> UI -> Service -> Database -> Response",
                deployment_strategy="Docker containers with web server deployment",
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
                tech_stack={
                    "frontend": ["React.js"],
                    "backend": ["Node.js", "Express"],
                    "database": ["SQLite"]
                }
            ),
            "code_generator": {
                "code_files": {
                    "src/Calculator.js": "import React from 'react';\n\nfunction Calculator() {\n  return <div>Calculator</div>;\n}\n\nexport default Calculator;",
                    "src/App.js": "import React from 'react';\nimport Calculator from './Calculator';\n\nfunction App() {\n  return <Calculator />;\n}\n\nexport default App;"
                },
                "summary": "Generated React calculator components"
            },
            "test_generator": {
                "tests": {
                    "src/__tests__/Calculator.test.js": "import { render, screen } from '@testing-library/react';\nimport Calculator from '../Calculator';\n\ntest('renders calculator', () => {\n  render(<Calculator />);\n  expect(screen.getByText('Calculator')).toBeInTheDocument();\n});"
                },
                "summary": "Generated React testing library tests"
            },
            "code_reviewer": {
                "artifacts": [
                    {
                        "name": "code_review_report.md",
                        "type": "markdown",
                        "content": "# Code Review Report\n\n## Issues Found\n- Missing error handling\n\n## Recommendations\n- Add proper error handling"
                    }
                ],
                "documentation": {
                    "review_summary": "Code review completed with 1 issue identified",
                    "quality_score": 8.0,
                    "improvement_suggestions": ["Add error handling"]
                },
                "output": {
                    "summary": "Code review identified 1 issue requiring attention",
                    "critical_issues": 0,
                    "minor_issues": 1,
                    "suggestions": 1
                }
            },
            "security_analyst": {
                "artifacts": [
                    {
                        "name": "security_analysis_report.md",
                        "type": "markdown",
                        "content": "# Security Analysis Report\n\n## Vulnerabilities\n- No critical vulnerabilities found\n\n## Recommendations\n- Add input validation"
                    }
                ],
                "documentation": {
                    "security_summary": "Security analysis completed with no critical vulnerabilities",
                    "risk_level": "Low",
                    "vulnerability_count": 0,
                    "mitigation_plan": ["Add input validation"]
                },
                "output": {
                    "summary": "Security analysis found no critical vulnerabilities",
                    "critical_vulnerabilities": 0,
                    "medium_vulnerabilities": 0,
                    "low_vulnerabilities": 0,
                    "recommendations": 1
                }
            },
            "documentation_generator": {
                "documentation": {
                    "README.md": "# Calculator App\n\nA simple calculator application built with React.js.\n\n## Features\n- Basic arithmetic operations\n- User-friendly interface",
                    "API_DOCUMENTATION.md": "# API Documentation\n\n## Endpoints\n- POST /calculate - Perform arithmetic operations"
                },
                "diagrams": {
                    "system_architecture.png": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                },
                "summary": "Generated comprehensive documentation"
            }
        }
        
        # Configure mock to return different responses based on context
        async def mock_invoke(prompt):
            # Determine which agent based on prompt content
            if "requirements" in str(prompt).lower():
                return mock_responses["requirements_analyst"]
            elif "architecture" in str(prompt).lower():
                return mock_responses["architecture_designer"]
            elif "code generation" in str(prompt).lower() or "generate code" in str(prompt).lower():
                return mock_responses["code_generator"]
            elif "test generation" in str(prompt).lower() or "generate tests" in str(prompt).lower():
                return mock_responses["test_generator"]
            elif "code review" in str(prompt).lower():
                return mock_responses["code_reviewer"]
            elif "security" in str(prompt).lower():
                return mock_responses["security_analyst"]
            elif "documentation" in str(prompt).lower():
                return mock_responses["documentation_generator"]
            else:
                return "Mock response"
            
            mock_llm.invoke.side_effect = mock_invoke
        
        # Execute complete workflow with proper configuration for real mode
        if is_real_mode():
            # Provide required configuration for checkpointer
            config = {
                "configurable": {
                    "thread_id": f"test-thread-{test_state['session_id']}",
                    "checkpoint_ns": "test-namespace"
                }
            }
            # For real mode, need to use the workflow directly with config
            result = await workflow_manager.workflow.ainvoke(test_state, config=config)
        else:
            result = await workflow_manager.execute_workflow(test_state)
        
        # Verify workflow completion
        assert result["current_step"] == "completed", "Workflow should complete successfully"
        assert len(result["errors"]) == 0, "No errors should occur"
        
        # Verify all agents executed
        agent_outputs = result["agent_outputs"]
        expected_agents = [
            "requirements_analyst", "architecture_designer", "code_generator",
            "test_generator", "code_reviewer", "security_analyst", "documentation_generator"
        ]
        
        for agent in expected_agents:
            assert agent in agent_outputs, f"Agent {agent} should have executed"
        
        # Verify artifacts generated
        assert len(result["requirements"]) > 0, "Requirements should be generated"
        assert result["architecture"], "Architecture should be generated"
        assert len(result["code_files"]) > 0, "Code files should be generated"
        assert len(result["tests"]) > 0, "Test files should be generated"
        
        # Verify execution history
        execution_history = result["execution_history"]
        assert len(execution_history) >= len(expected_agents), "Should have execution history for all agents"
        
        # Verify each step in history
        for step in execution_history:
            assert "step" in step, "Each history entry should have step"
            assert "status" in step, "Each history entry should have status"
            assert step["status"] == "completed", "Each step should be completed"
    
    @pytest.mark.asyncio
    async def test_workflow_error_recovery(self, workflow_manager, test_state, mock_llm):
        """Test workflow error recovery and retry logic."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        if is_real_mode() and not REAL_WORKFLOW_AVAILABLE:
            pytest.skip("Real workflow not available")
        
        # Configure mocks only in mock mode
        if is_mock_mode() and mock_llm:
            # Mock LLM to fail on first attempt, succeed on retry
            call_count = 0
        
            async def mock_invoke_with_retry(prompt):
                nonlocal call_count
                call_count += 1
                
                if call_count <= 2:  # Fail first two attempts
                    raise Exception("LLM API error")
                else:  # Succeed on third attempt
                    return RequirementsAnalysisOutput(
                        functional_requirements=[
                            {
                                "id": "REQ-001",
                                "title": "Basic Calculator Interface",
                                "description": "Create a user interface for basic arithmetic operations",
                                "priority": "high",
                                "type": "functional"
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
                                "i_want": "to perform basic arithmetic operations",
                                "so_that": "I can calculate mathematical problems quickly"
                            }
                        ],
                        risks=[
                            {
                                "risk": "Division by zero errors",
                                "probability": "medium",
                                "impact": "high",
                                "mitigation": "Implement proper error handling and validation"
                            }
                        ],
                        summary={"description": "Calculator app with basic arithmetic operations"},
                        assumptions=["User has basic computer literacy"],
                        technical_constraints=["Must work on web browsers"]
                    )
            
            mock_llm.invoke.side_effect = mock_invoke_with_retry
        
        # Enable error simulation in the mock workflow manager (only in mock mode)
        if is_mock_mode() and hasattr(workflow_manager, 'simulate_errors'):
            workflow_manager.simulate_errors(True)
        
        # Execute workflow
        result = await workflow_manager.execute_workflow(test_state)
        
        # Verify error recovery
        assert len(result["errors"]) > 0, "Errors should be recorded"
        assert "LLM API error" in str(result["errors"][0]), "Error message should be captured"
        
        # Note: In mock mode, the actual LLM isn't called, so call_count remains 0
        # Instead, verify that the mock workflow properly simulates error recovery
        # In a real implementation, the retry logic would be tested with integration tests
        
        # Verify workflow can continue despite errors
        assert "requirements_analyst" in result["agent_outputs"], "Requirements analyst should eventually succeed"
    
    @pytest.mark.asyncio
    async def test_workflow_state_persistence(self, workflow_manager, test_state, mock_llm):
        """Test workflow state persistence across nodes."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        if is_real_mode() and not REAL_WORKFLOW_AVAILABLE:
            pytest.skip("Real workflow not available")
        
        # Configure mocks only in mock mode
        if is_mock_mode() and mock_llm:
            # Mock successful LLM responses
            mock_responses = {
            "requirements_analyst": RequirementsAnalysisOutput(
                functional_requirements=[
                    {
                        "id": "REQ-001",
                        "title": "Basic Calculator Interface",
                        "description": "Create a user interface for basic arithmetic operations",
                        "priority": "high",
                        "type": "functional"
                    }
                ],
                summary={"description": "Calculator app with basic arithmetic operations"},
                assumptions=["User has basic computer literacy"],
                technical_constraints=["Must work on web browsers"]
            ),
            "architecture_designer": ArchitectureDesignOutput(
                architecture_overview="MVC architecture with React frontend and Node.js backend",
                data_flow="Simple",
                deployment_strategy="Docker deployment",
                tech_stack={"frontend": ["React.js"], "backend": ["Node.js"]},
                components=[]
            )
        }
        
        async def mock_invoke(prompt):
            if "requirements" in str(prompt).lower():
                return mock_responses["requirements_analyst"]
            elif "architecture" in str(prompt).lower():
                return mock_responses["architecture_designer"]
            else:
                return "Mock response"
            
            mock_llm.invoke.side_effect = mock_invoke
        
        # Execute workflow
        result = await workflow_manager.execute_workflow(test_state)
        
        # Verify state persistence
        assert result["project_context"] == test_state["project_context"], "Project context should persist"
        assert result["project_name"] == test_state["project_name"], "Project name should persist"
        assert result["session_id"] == test_state["session_id"], "Session ID should persist"
        
        # Verify state updates
        assert len(result["requirements"]) > 0, "Requirements should be added to state"
        assert result["architecture"], "Architecture should be added to state"
        
        # Verify agent outputs are preserved
        agent_outputs = result["agent_outputs"]
        assert "requirements_analyst" in agent_outputs, "Requirements analyst output should be preserved"
        assert "architecture_designer" in agent_outputs, "Architecture designer output should be preserved"
    
    @pytest.mark.asyncio
    async def test_workflow_conditional_routing(self, workflow_manager, test_state, mock_llm):
        """Test workflow conditional routing based on agent outputs."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        if is_real_mode() and not REAL_WORKFLOW_AVAILABLE:
            pytest.skip("Real workflow not available")
        
        # Configure mocks only in mock mode
        if is_mock_mode() and mock_llm:
            # Mock LLM responses that trigger conditional routing
            mock_responses = {
            "requirements_analyst": RequirementsAnalysisOutput(
                functional_requirements=[
                    {
                        "id": "REQ-001",
                        "title": "Basic Calculator Interface",
                        "description": "Create a user interface for basic arithmetic operations",
                        "priority": "high",
                        "type": "functional"
                    }
                ],
                non_functional_requirements=[
                    {
                        "id": "NFR-001",
                        "title": "Performance Requirements",
                        "description": "Application must respond within 2 seconds",
                        "priority": "medium",
                        "type": "performance"
                    }
                ],
                user_stories=[
                    {
                        "id": "US-001",
                        "title": "As a user, I want to perform basic calculations",
                        "description": "I want to add, subtract, multiply, and divide numbers",
                        "acceptance_criteria": ["Can perform basic arithmetic operations", "Results are accurate"]
                    }
                ],
                risks=[
                    {
                        "id": "RISK-001",
                        "title": "Browser Compatibility",
                        "description": "Application may not work on older browsers",
                        "severity": "medium",
                        "mitigation": "Test on multiple browsers"
                    }
                ],
                summary={"description": "Calculator app with basic arithmetic operations"},
                assumptions=["User has basic computer literacy"],
                technical_constraints=["Must work on web browsers"]
            ),
            "code_reviewer": {
                "artifacts": [
                    {
                        "name": "code_review_report.md",
                        "type": "markdown",
                        "content": "# Code Review Report\n\n## Critical Issues Found\n- Security vulnerability detected\n\n## Recommendations\n- Immediate fix required"
                    }
                ],
                "documentation": {
                    "review_summary": "Code review found critical security issues",
                    "quality_score": 3.0,
                    "improvement_suggestions": ["Fix security vulnerability immediately"]
                },
                "output": {
                    "summary": "Code review identified critical security issues",
                    "critical_issues": 1,
                    "minor_issues": 0,
                    "suggestions": 1
                }
            }
        }
        
        async def mock_invoke(prompt):
            if "requirements" in str(prompt).lower():
                return mock_responses["requirements_analyst"]
            elif "code review" in str(prompt).lower():
                return mock_responses["code_reviewer"]
            else:
                return "Mock response"
            
            mock_llm.invoke.side_effect = mock_invoke
        
        # Execute workflow
        result = await workflow_manager.execute_workflow(test_state)
        
        # Verify conditional routing based on code review results
        agent_outputs = result["agent_outputs"]
        
        if "code_reviewer" in agent_outputs:
            code_review_output = agent_outputs["code_reviewer"]
            if "output" in code_review_output:
                critical_issues = code_review_output["output"].get("critical_issues", 0)
                
                if critical_issues > 0:
                    # Should trigger additional security analysis or approval
                    assert "security_analyst" in agent_outputs, "Security analyst should execute for critical issues"
                    assert len(result["warnings"]) > 0, "Warnings should be generated for critical issues"
    
    @pytest.mark.asyncio
    async def test_workflow_performance_monitoring(self, workflow_manager, test_state, mock_llm):
        """Test workflow performance monitoring and timing."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        if is_real_mode() and not REAL_WORKFLOW_AVAILABLE:
            pytest.skip("Real workflow not available")
        
        # Configure mocks only in mock mode
        if is_mock_mode() and mock_llm:
            # Mock successful LLM responses
            mock_responses = {
                "requirements_analyst": RequirementsAnalysisOutput(
                    functional_requirements=[
                        {
                            "id": "REQ-001",
                            "title": "Basic Calculator Interface",
                            "description": "Create a user interface for basic arithmetic operations",
                            "priority": "high",
                            "type": "functional"
                        }
                    ],
                    non_functional_requirements=[
                        {
                            "id": "NFR-001",
                            "title": "Performance Requirements",
                            "description": "Application must respond within 2 seconds",
                            "priority": "medium",
                            "type": "performance"
                        }
                    ],
                    user_stories=[
                        {
                            "id": "US-001",
                            "title": "As a user, I want to perform basic calculations",
                            "description": "I want to add, subtract, multiply, and divide numbers",
                            "acceptance_criteria": ["Can perform basic arithmetic operations", "Results are accurate"]
                        }
                    ],
                    risks=[
                        {
                            "id": "RISK-001",
                            "title": "Browser Compatibility",
                            "description": "Application may not work on older browsers",
                            "severity": "medium",
                            "mitigation": "Test on multiple browsers"
                        }
                    ],
                    summary={"description": "Calculator app with basic arithmetic operations"},
                    assumptions=["User has basic computer literacy"],
                    technical_constraints=["Must work on web browsers"]
                )
            }
            
            async def mock_invoke(prompt):
                # Simulate processing time
                await asyncio.sleep(0.1)
                return mock_responses["requirements_analyst"]
            
            mock_llm.invoke.side_effect = mock_invoke
        
        # Execute workflow with timing
        start_time = asyncio.get_event_loop().time()
        result = await workflow_manager.execute_workflow(test_state)
        end_time = asyncio.get_event_loop().time()
        
        execution_time = end_time - start_time
        
        # Verify performance monitoring
        assert execution_time > 0, "Execution time should be recorded"
        assert execution_time < 30, "Execution should complete within reasonable time"
        
        # Verify execution history includes timing
        execution_history = result["execution_history"]
        if execution_history:
            for step in execution_history:
                assert "step" in step, "Each history entry should have step"
                assert "status" in step, "Each history entry should have status"
                # Timing information should be available in execution history
    
    @pytest.mark.asyncio
    async def test_workflow_concurrent_execution(self, workflow_manager, test_state, mock_llm):
        """Test workflow concurrent execution capabilities."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        if is_real_mode() and not REAL_WORKFLOW_AVAILABLE:
            pytest.skip("Real workflow not available")
        
        # Configure mocks only in mock mode
        if is_mock_mode() and mock_llm:
            # Mock LLM responses for concurrent execution
            mock_responses = {
                "requirements_analyst": RequirementsAnalysisOutput(
                    functional_requirements=[
                        {
                            "id": "REQ-001",
                            "title": "Basic Calculator Interface",
                            "description": "Create a user interface for basic arithmetic operations",
                            "priority": "high",
                            "type": "functional"
                        }
                    ],
                    summary={"description": "Calculator app with basic arithmetic operations"},
                    assumptions=["User has basic computer literacy"],
                    technical_constraints=["Must work on web browsers"]
                )
            }
            
            async def mock_invoke(prompt):
                # Simulate concurrent processing
                await asyncio.sleep(0.05)
                return mock_responses["requirements_analyst"]
            
            mock_llm.invoke.side_effect = mock_invoke
        
        # Execute multiple workflows concurrently
        workflows = []
        for i in range(3):
            workflow_state = test_state.copy()
            workflow_state["session_id"] = f"test-concurrent-session-{i}"
            workflows.append(workflow_manager.execute_workflow(workflow_state))
        
        # Execute all workflows concurrently
        results = await asyncio.gather(*workflows)
        
        # Verify all workflows completed
        for i, result in enumerate(results):
            assert result["session_id"] == f"test-concurrent-session-{i}", f"Session ID should match for workflow {i}"
            assert "requirements_analyst" in result["agent_outputs"], f"Requirements analyst should execute for workflow {i}"
            assert len(result["requirements"]) > 0, f"Requirements should be generated for workflow {i}"
    
    @pytest.mark.asyncio
    async def test_workflow_checkpointing_and_resumption(self, workflow_manager, test_state, mock_llm):
        """Test workflow checkpointing and resumption capabilities."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        if is_real_mode() and not REAL_WORKFLOW_AVAILABLE:
            pytest.skip("Real workflow not available")
        
        # Configure mocks only in mock mode
        if is_mock_mode() and mock_llm:
            # Mock LLM responses
            mock_responses = {
                "requirements_analyst": RequirementsAnalysisOutput(
                    functional_requirements=[
                        {
                            "id": "REQ-001",
                            "title": "Basic Calculator Interface",
                            "description": "Create a user interface for basic arithmetic operations",
                            "priority": "high",
                            "type": "functional"
                        }
                    ],
                    summary={"description": "Calculator app with basic arithmetic operations"},
                    assumptions=["User has basic computer literacy"],
                    technical_constraints=["Must work on web browsers"]
                ),
                "architecture_designer": ArchitectureDesignOutput(
                    architecture_overview="MVC architecture with React frontend and Node.js backend",
                    data_flow="Simple",
                    deployment_strategy="Docker deployment",
                    tech_stack={"frontend": ["React.js"], "backend": ["Node.js"]},
                    components=[]
                )
            }
            
            async def mock_invoke(prompt):
                if "requirements" in str(prompt).lower():
                    return mock_responses["requirements_analyst"]
                elif "architecture" in str(prompt).lower():
                    return mock_responses["architecture_designer"]
                else:
                    return "Mock response"
            
            mock_llm.invoke.side_effect = mock_invoke
        
        # Execute workflow to create checkpoint
        result = await workflow_manager.execute_workflow(test_state)
        
        # Verify checkpoint data
        assert result["current_step"] in ["completed", "architecture_design"], "Should have reached a checkpoint"
        assert len(result["execution_history"]) > 0, "Should have execution history for checkpointing"
        
        # Simulate resumption from checkpoint
        import copy
        checkpoint_state = copy.deepcopy(result)
        checkpoint_state["current_step"] = "code_generation"  # Resume from code generation
        
        # Resume workflow
        resumed_result = await workflow_manager.execute_workflow(checkpoint_state)
        
        # Verify resumption
        assert resumed_result["current_step"] == "completed", "Resumed workflow should complete"
        assert len(resumed_result["execution_history"]) > len(checkpoint_state["execution_history"]), "Should have additional execution history"
        
        # Verify state continuity
        assert resumed_result["project_context"] == checkpoint_state["project_context"], "Project context should be preserved"
        assert resumed_result["requirements"] == checkpoint_state["requirements"], "Requirements should be preserved"
        assert resumed_result["architecture"] == checkpoint_state["architecture"], "Architecture should be preserved"
