"""
Tests for the BaseAgent class to identify and fix the "src property must be a valid json object" error.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from agents.base_agent import BaseAgent
from models.config import AgentConfig
from models.state import AgentState


class MockAgent(BaseAgent):
    """Mock agent for testing BaseAgent functionality."""
    
    async def execute(self, state: AgentState) -> AgentState:
        return state
    
    def get_prompt_template(self) -> str:
        return "Test prompt template"


class TestBaseAgent:
    """Test cases for BaseAgent class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock agent configuration."""
        return AgentConfig(
            name="test_agent",
            description="Test agent",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Test prompt template",
            system_prompt="You are a test agent",
            parameters={
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_tokens": 8192
            }
        )
    
    @pytest.fixture
    def mock_gemini_client(self):
        """Create a mock Gemini client."""
        client = Mock()
        client.generate_content = Mock()
        return client
    
    @pytest.fixture
    def base_agent(self, mock_config, mock_gemini_client):
        """Create a base agent instance for testing."""
        return MockAgent(mock_config, mock_gemini_client)
    
    @pytest.fixture
    def sample_state(self):
        """Create a sample agent state."""
        return {
            "project_context": "Test project",
            "project_name": "test_project",
            "requirements": [],
            "user_stories": [],
            "architecture": {},
            "tech_stack": {},
            "database_schema": {},
            "code_files": {},
            "tests": {},
            "documentation": {},
            "configuration_files": {},
            "current_task": "test_task",
            "current_agent": "test_agent",
            "agent_outputs": {},
            "workflow_history": [],
            "human_approval_needed": False,
            "approval_requests": [],
            "human_feedback": {},
            "errors": [],
            "warnings": [],
            "retry_count": 0,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "session_id": "test_session"
        }
    
    def test_validate_gemini_config_success(self, base_agent):
        """Test successful Gemini configuration validation."""
        assert base_agent.validate_gemini_config() is True
    
    def test_validate_gemini_config_no_client(self, mock_config):
        """Test Gemini configuration validation with no client."""
        agent = MockAgent(mock_config, None)
        assert agent.validate_gemini_config() is False
    
    def test_validate_gemini_config_no_generate_content(self, mock_config):
        """Test Gemini configuration validation with missing generate_content method."""
        client = Mock()
        del client.generate_content
        agent = MockAgent(mock_config, client)
        assert agent.validate_gemini_config() is False
    
    def test_validate_gemini_config_no_config(self, mock_gemini_client):
        """Test Gemini configuration validation with no config."""
        agent = MockAgent(None, mock_gemini_client)
        assert agent.validate_gemini_config() is False
    
    def test_validate_gemini_config_no_parameters(self, mock_gemini_client):
        """Test Gemini configuration validation with no parameters."""
        config = AgentConfig(
            name="test_agent",
            description="Test agent",
            enabled=True,
            max_retries=3,
            timeout=300,
            parameters={}
        )
        agent = MockAgent(config, mock_gemini_client)
        assert agent.validate_gemini_config() is False
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, base_agent, mock_gemini_client):
        """Test successful response generation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = '{"test": "data"}'
        mock_gemini_client.generate_content.return_value = mock_response
        
        result = await base_agent.generate_response("Test prompt")
        assert result == '{"test": "data"}'
    
    @pytest.mark.asyncio
    async def test_generate_response_with_parts(self, base_agent, mock_gemini_client):
        """Test response generation with parts structure."""
        # Mock response with parts
        mock_part = Mock()
        mock_part.text = '{"test": "data"}'
        mock_response = Mock()
        mock_response.parts = [mock_part]
        mock_gemini_client.generate_content.return_value = mock_response
        
        result = await base_agent.generate_response("Test prompt")
        assert result == '{"test": "data"}'
    
    @pytest.mark.asyncio
    async def test_generate_response_with_candidates(self, base_agent, mock_gemini_client):
        """Test response generation with candidates structure."""
        # Mock response with candidates
        mock_part = Mock()
        mock_part.text = '{"test": "data"}'
        mock_content = Mock()
        mock_content.parts = [mock_part]
        mock_candidate = Mock()
        mock_candidate.content = mock_content
        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        mock_gemini_client.generate_content.return_value = mock_response
        
        result = await base_agent.generate_response("Test prompt")
        assert result == '{"test": "data"}'
    
    @pytest.mark.asyncio
    async def test_generate_response_empty_response(self, base_agent, mock_gemini_client):
        """Test response generation with empty response."""
        # Mock empty response
        mock_response = Mock()
        mock_response.text = ""
        mock_gemini_client.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError, match="Empty or invalid response from Gemini API"):
            await base_agent.generate_response("Test prompt")
    
    @pytest.mark.asyncio
    async def test_generate_response_invalid_config(self, mock_config, mock_gemini_client):
        """Test response generation with invalid configuration."""
        # Create agent with invalid config
        config = AgentConfig(
            name="test_agent",
            description="Test agent",
            enabled=True,
            max_retries=3,
            timeout=300,
            parameters={}  # Empty parameters
        )
        agent = MockAgent(config, mock_gemini_client)
        
        with pytest.raises(ValueError, match="Invalid Gemini configuration"):
            await agent.generate_response("Test prompt")
    
    def test_parse_json_response_simple_json(self, base_agent):
        """Test parsing simple JSON response."""
        response = '{"test": "data"}'
        result = base_agent.parse_json_response(response)
        assert result == {"test": "data"}
    
    def test_parse_json_response_with_code_blocks(self, base_agent):
        """Test parsing JSON response with code blocks."""
        response = '```json\n{"test": "data"}\n```'
        result = base_agent.parse_json_response(response)
        assert result == {"test": "data"}
    
    def test_parse_json_response_with_generic_code_blocks(self, base_agent):
        """Test parsing JSON response with generic code blocks."""
        response = '```\n{"test": "data"}\n```'
        result = base_agent.parse_json_response(response)
        assert result == {"test": "data"}
    
    def test_parse_json_response_with_trailing_commas(self, base_agent):
        """Test parsing JSON response with trailing commas."""
        response = '{"test": "data",}'
        result = base_agent.parse_json_response(response)
        assert result == {"test": "data"}
    
    def test_parse_json_response_with_trailing_commas_in_arrays(self, base_agent):
        """Test parsing JSON response with trailing commas in arrays."""
        response = '{"test": ["data",]}'
        result = base_agent.parse_json_response(response)
        assert result == {"test": ["data"]}
    
    def test_parse_json_response_invalid_json(self, base_agent):
        """Test parsing invalid JSON response."""
        response = '{"test": "data"'  # Missing closing brace
        with pytest.raises(ValueError, match="Invalid JSON response"):
            base_agent.parse_json_response(response)
    
    def test_parse_json_response_malformed_json(self, base_agent):
        """Test parsing malformed JSON response."""
        response = '{"test": data}'  # Missing quotes around value
        with pytest.raises(ValueError, match="Invalid JSON response"):
            base_agent.parse_json_response(response)
    
    def test_prepare_prompt(self, base_agent, sample_state):
        """Test prompt preparation."""
        result = base_agent.prepare_prompt(sample_state)
        assert "Test prompt template" in result
        assert "Test project" in result
        assert "test_project" in result
    
    def test_prepare_prompt_with_kwargs(self, base_agent, sample_state):
        """Test prompt preparation with additional kwargs."""
        result = base_agent.prepare_prompt(sample_state, extra_param="test_value")
        assert "Test prompt template" in result
        assert "test_value" in result
    
    def test_validate_input_success(self, base_agent, sample_state):
        """Test successful input validation."""
        assert base_agent.validate_input(sample_state) is True
    
    def test_validate_input_missing_required_fields(self, base_agent):
        """Test input validation with missing required fields."""
        incomplete_state = {"project_name": "test"}
        assert base_agent.validate_input(incomplete_state) is False
    
    def test_handle_error(self, base_agent, sample_state):
        """Test error handling."""
        error = ValueError("Test error")
        result = base_agent.handle_error(sample_state, error, "test_task")
        
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert result["errors"][0]["task"] == "test_task"
        assert "Test error" in result["errors"][0]["message"]
    
    def test_update_state_with_result(self, base_agent, sample_state):
        """Test state update with results."""
        output = {"test": "data"}
        result = base_agent.update_state_with_result(sample_state, "test_task", output, 1.5)
        
        assert "agent_outputs" in result
        assert "test_task" in result["agent_outputs"]
        assert result["agent_outputs"]["test_task"]["output"] == output
        assert result["agent_outputs"]["test_task"]["execution_time"] == 1.5


class TestGeminiAPIErrorScenarios:
    """Test scenarios specifically for Gemini API error handling."""
    
    @pytest.fixture
    def mock_config(self):
        return AgentConfig(
            name="test_agent",
            description="Test agent",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="Test prompt template",
            system_prompt="You are a test agent",
            parameters={
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_tokens": 8192
            }
        )
    
    @pytest.fixture
    def mock_gemini_client(self):
        client = Mock()
        client.generate_content = Mock()
        return client
    
    @pytest.mark.asyncio
    async def test_gemini_api_src_property_error(self, mock_config, mock_gemini_client):
        """Test handling of the specific 'src property must be a valid json object' error."""
        agent = MockAgent(mock_config, mock_gemini_client)
        
        # Mock the specific error
        mock_gemini_client.generate_content.side_effect = Exception("src property must be a valid json object")
        
        with pytest.raises(Exception, match="src property must be a valid json object"):
            await agent.generate_response("Test prompt")
    
    @pytest.mark.asyncio
    async def test_gemini_api_response_with_src_property(self, mock_config, mock_gemini_client):
        """Test handling of response that might contain src property."""
        agent = MockAgent(mock_config, mock_gemini_client)
        
        # Mock response that might cause the src property error
        mock_response = Mock()
        mock_response.text = '{"src": "invalid_value"}'
        mock_gemini_client.generate_content.return_value = mock_response
        
        # This should not raise the src property error
        result = await agent.generate_response("Test prompt")
        assert result == '{"src": "invalid_value"}'
    
    @pytest.mark.asyncio
    async def test_gemini_api_complex_response_structure(self, mock_config, mock_gemini_client):
        """Test handling of complex response structures that might cause issues."""
        agent = MockAgent(mock_config, mock_gemini_client)
        
        # Mock a complex response structure
        mock_response = Mock()
        mock_response.text = json.dumps({
            "src": {
                "type": "text",
                "content": "Generated content"
            },
            "metadata": {
                "model": "gemini-2.0-flash-exp",
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 200
                }
            }
        })
        mock_gemini_client.generate_content.return_value = mock_response
        
        result = await agent.generate_response("Test prompt")
        parsed = json.loads(result)
        assert "src" in parsed
        assert "metadata" in parsed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
