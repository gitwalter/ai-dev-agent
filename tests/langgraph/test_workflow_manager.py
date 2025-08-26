#!/usr/bin/env python3
"""
Tests for LangGraph Workflow Manager.
Comprehensive test suite for the new implementation.
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
from utils.structured_outputs import RequirementsAnalysisOutput


class TestLangGraphWorkflowManager:
    """Tests for the LangGraph workflow manager."""
    
    @pytest.fixture
    def mock_llm_config(self):
        """Mock LLM configuration."""
        return {
            "api_key": "test-api-key",
            "model_name": "gemini-2.5-flash-lite",
            "temperature": 0.1,
            "max_tokens": 8192
        }
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = Mock()
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
    
    def test_workflow_manager_initialization(self, mock_llm_config):
        """Test workflow manager initialization."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        with patch('langgraph_workflow_manager.ChatGoogleGenerativeAI') as mock_chat:
            mock_chat.return_value = Mock()
            
            workflow_manager = LangGraphWorkflowManager(mock_llm_config)
            
            assert workflow_manager is not None
            assert workflow_manager.llm_config == mock_llm_config
            assert workflow_manager.node_factory is not None
            assert workflow_manager.workflow is not None
    
    def test_agent_node_factory_creation(self, mock_llm):
        """Test agent node factory creation."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        factory = AgentNodeFactory(mock_llm)
        
        assert factory is not None
        assert factory.llm == mock_llm
        
        # Test node creation
        requirements_node = factory.create_requirements_node()
        assert callable(requirements_node)
        
        architecture_node = factory.create_architecture_node()
        assert callable(architecture_node)
        
        code_generator_node = factory.create_code_generator_node()
        assert callable(code_generator_node)
    
    def test_requirements_node_execution(self, mock_llm, basic_state):
        """Test requirements analysis node execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Mock the parser and chain
        mock_result = Mock()
        mock_result.functional_requirements = [
            {
                "id": "FR-001",
                "title": "Test Requirement",
                "description": "Test description",
                "priority": "high",
                "acceptance_criteria": ["Test criteria"]
            }
        ]
        mock_result.dict.return_value = {
            "functional_requirements": mock_result.functional_requirements,
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
        }
        
        mock_llm.invoke.return_value = mock_result
        
        with patch('langgraph_workflow_manager.PydanticOutputParser') as mock_parser, \
             patch('langgraph_workflow_manager.PromptTemplate') as mock_prompt:
            
            # Mock parser and prompt
            mock_parser_instance = Mock()
            mock_parser_instance.get_format_instructions.return_value = "Format instructions"
            mock_parser.return_value = mock_parser_instance
            
            mock_prompt_instance = Mock()
            mock_prompt_instance.format.return_value = "Formatted prompt"
            mock_prompt.return_value = mock_prompt_instance
            
            # Create factory and node
            factory = AgentNodeFactory(mock_llm)
            requirements_node = factory.create_requirements_node()
            
            # Execute node
            result = requirements_node(basic_state)
            
            # Verify results
            assert result["current_step"] == "requirements_analysis"
            assert len(result["requirements"]) == 1
            assert result["requirements"][0]["id"] == "FR-001"
            assert "requirements_analyst" in result["agent_outputs"]
            assert len(result["execution_history"]) == 1
            assert result["execution_history"][0]["step"] == "requirements_analysis"
            assert result["execution_history"][0]["status"] == "completed"
    
    def test_requirements_node_error_handling(self, mock_llm, basic_state):
        """Test requirements analysis node error handling."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Mock LLM to raise an exception
        mock_llm.invoke.side_effect = Exception("Test error")
        
        factory = AgentNodeFactory(mock_llm)
        requirements_node = factory.create_requirements_node()
        
        # Execute node
        result = requirements_node(basic_state)
        
        # Verify error handling
        assert result["current_step"] == "requirements_analysis"
        assert len(result["errors"]) == 1
        assert "Requirements analysis failed: Test error" in result["errors"][0]
        assert len(result["execution_history"]) == 1
        assert result["execution_history"][0]["step"] == "requirements_analysis"
        assert result["execution_history"][0]["status"] == "failed"
        assert "Test error" in result["execution_history"][0]["error"]
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self, mock_llm_config):
        """Test complete workflow execution."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        # Mock all dependencies
        with patch('langgraph_workflow_manager.ChatGoogleGenerativeAI') as mock_chat, \
             patch('langgraph_workflow_manager.PydanticOutputParser') as mock_parser, \
             patch('langgraph_workflow_manager.PromptTemplate') as mock_prompt:
            
            # Setup mocks
            mock_llm = Mock()
            mock_chat.return_value = mock_llm
            
            # Mock parser
            mock_parser_instance = Mock()
            mock_parser_instance.get_format_instructions.return_value = "Format instructions"
            mock_parser.return_value = mock_parser_instance
            
            # Mock prompt
            mock_prompt_instance = Mock()
            mock_prompt_instance.format.return_value = "Formatted prompt"
            mock_prompt.return_value = mock_prompt_instance
            
            # Mock workflow execution
            mock_workflow = AsyncMock()
            mock_workflow.ainvoke.return_value = {
                "project_context": "Create a calculator",
                "project_name": "test-calculator",
                "session_id": "test-session-123",
                "requirements": [{"id": "FR-001", "title": "Test"}],
                "architecture": {"type": "web-app"},
                "code_files": {"main.py": "print('Hello')"},
                "tests": {},
                "documentation": {},
                "diagrams": {},
                "agent_outputs": {"requirements_analyst": {}},
                "errors": [],
                "warnings": [],
                "approval_requests": [],
                "current_step": "completed",
                "execution_history": []
            }
            
            with patch.object(LangGraphWorkflowManager, '_create_workflow') as mock_create:
                mock_create.return_value = mock_workflow
                
                # Create workflow manager
                workflow_manager = LangGraphWorkflowManager(mock_llm_config)
                
                # Execute workflow
                initial_state = {
                    "project_context": "Create a calculator",
                    "project_name": "test-calculator",
                    "session_id": "test-session-123"
                }
                
                result = await workflow_manager.execute_workflow(initial_state)
                
                # Verify results
                assert result["current_step"] == "completed"
                assert len(result["requirements"]) == 1
                assert result["requirements"][0]["id"] == "FR-001"
                assert result["architecture"]["type"] == "web-app"
                assert "main.py" in result["code_files"]
    
    def test_workflow_execution_error(self, mock_llm_config):
        """Test workflow execution error handling."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        with patch('langgraph_workflow_manager.ChatGoogleGenerativeAI') as mock_chat:
            mock_chat.side_effect = Exception("LLM setup failed")
            
            # Should raise an exception during initialization
            with pytest.raises(Exception):
                LangGraphWorkflowManager(mock_llm_config)
    
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
    
    def test_workflow_manager_methods(self, mock_llm_config):
        """Test workflow manager public methods."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        with patch('langgraph_workflow_manager.ChatGoogleGenerativeAI') as mock_chat:
            mock_chat.return_value = Mock()
            
            workflow_manager = LangGraphWorkflowManager(mock_llm_config)
            
            # Test public methods exist
            assert hasattr(workflow_manager, 'execute_workflow')
            assert callable(workflow_manager.execute_workflow)
            
            # Test private methods exist
            assert hasattr(workflow_manager, '_setup_llm')
            assert hasattr(workflow_manager, '_create_workflow')
            assert hasattr(workflow_manager, '_error_handler_node')
            assert hasattr(workflow_manager, '_workflow_complete_node')


class TestAgentNodeFactory:
    """Tests for the agent node factory."""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        mock = Mock(spec=ChatGoogleGenerativeAI)
        mock.invoke = Mock()
        return mock
    
    def test_factory_initialization(self, mock_llm):
        """Test factory initialization."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        factory = AgentNodeFactory(mock_llm)
        
        assert factory.llm == mock_llm
        assert factory.logger is not None
    
    def test_node_creation_methods(self, mock_llm):
        """Test that all node creation methods return callables."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        factory = AgentNodeFactory(mock_llm)
        
        # Test all node creation methods
        node_methods = [
            factory.create_requirements_node,
            factory.create_architecture_node,
            factory.create_code_generator_node
        ]
        
        for method in node_methods:
            node = method()
            assert callable(node)
    
    def test_node_signature(self, mock_llm):
        """Test that nodes have correct signature."""
        if not LANGGRAPH_AVAILABLE:
            pytest.skip("LangGraph not available")
        
        factory = AgentNodeFactory(mock_llm)
        
        # Test requirements node signature
        requirements_node = factory.create_requirements_node()
        
        # Test that it accepts AgentState and returns AgentState
        test_state = {
            "project_context": "test",
            "project_name": "test",
            "session_id": "test",
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
            "current_step": "test",
            "execution_history": []
        }
        
        result = requirements_node(test_state)
        
        # Verify result has same structure
        assert isinstance(result, dict)
        assert "project_context" in result
        assert "current_step" in result
        assert "execution_history" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
