"""
Comprehensive tests for the "src property must be a valid json object" error fix.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch
from typing import Dict, Any

from agents.base_agent import BaseAgent
from models.config import AgentConfig


class TestAgent(BaseAgent):
    """Test agent for src property error testing."""
    
    async def execute(self, state):
        return state
    
    def get_prompt_template(self):
        return "Test prompt template"


class TestSrcPropertyErrorFix:
    """Test the fixes for the src property error."""
    
    @pytest.fixture
    def agent_config(self):
        """Create agent configuration."""
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
        """Create mock Gemini client."""
        client = Mock()
        client.generate_content = Mock()
        return client
    
    @pytest.fixture
    def test_agent(self, agent_config, mock_gemini_client):
        """Create test agent instance."""
        return TestAgent(agent_config, mock_gemini_client)
    
    def test_sanitize_prompt_removes_problematic_patterns(self, test_agent):
        """Test that prompt sanitization removes problematic patterns."""
        
        # Test problematic patterns
        problematic_prompts = [
            "Generate JSON with src: invalid_value",
            "Create object with src: {invalid}",
            "Return JSON containing src: [invalid]",
            "```json\n{\n```",  # Incomplete JSON block
            "```\n{\n```",      # Incomplete code block
            '{"test": "data",}',  # Trailing comma
            '{"test": ["data",]}',  # Trailing comma in array
            '{"test": "data", "src": "value",}',  # Multiple trailing commas
        ]
        
        for prompt in problematic_prompts:
            sanitized = test_agent.sanitize_prompt(prompt)
            assert sanitized != prompt, f"Prompt should have been sanitized: {prompt}"
            assert "src:" not in sanitized.lower(), f"src: pattern should be removed: {sanitized}"
    
    def test_sanitize_prompt_preserves_valid_content(self, test_agent):
        """Test that prompt sanitization preserves valid content."""
        
        valid_prompts = [
            "Generate a simple JSON response",
            "Create a user object with name and email",
            "Return a list of requirements",
            '{"valid": "json"}',
            '{"array": [1, 2, 3]}',
            "```json\n{\"valid\": \"json\"}\n```",
        ]
        
        for prompt in valid_prompts:
            sanitized = test_agent.sanitize_prompt(prompt)
            assert sanitized == prompt, f"Valid prompt should not be changed: {prompt}"
    
    def test_validate_generation_config_validates_parameters(self, test_agent):
        """Test that generation config validation works correctly."""
        
        # Test valid configuration
        valid_config = {
            "temperature": 0.5,
            "top_p": 0.9,
            "top_k": 50,
            "max_output_tokens": 4096
        }
        
        validated = test_agent.validate_generation_config(valid_config)
        assert validated == valid_config
        
        # Test invalid configuration that should be corrected
        invalid_config = {
            "temperature": 3.0,  # Too high
            "top_p": 1.5,        # Too high
            "top_k": 0,          # Too low
            "max_output_tokens": 10000,  # Too high
            "unknown_param": "value"  # Unknown parameter
        }
        
        validated = test_agent.validate_generation_config(invalid_config)
        assert validated["temperature"] == 2.0  # Should be clamped to max
        assert validated["top_p"] == 1.0        # Should be clamped to max
        assert validated["top_k"] == 1          # Should be clamped to min
        assert validated["max_output_tokens"] == 8192  # Should be clamped to max
        assert "unknown_param" not in validated  # Should be removed
    
    def test_validate_generation_config_handles_errors(self, test_agent):
        """Test that generation config validation handles errors gracefully."""
        
        # Test with invalid input
        with patch.object(test_agent, 'logger') as mock_logger:
            result = test_agent.validate_generation_config("invalid")
            
            # Should return safe defaults
            assert result["temperature"] == 0.1
            assert result["top_p"] == 0.8
            assert result["top_k"] == 40
            assert result["max_output_tokens"] == 8192
            
            # Should log the error
            mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_generate_response_handles_src_property_error(self, test_agent, mock_gemini_client):
        """Test that generate_response handles the src property error correctly."""
        
        # Mock the specific src property error
        def mock_src_error(*args, **kwargs):
            raise Exception("src property must be a valid json object")
        
        mock_gemini_client.generate_content = mock_src_error
        
        # Test that the error is caught and handled properly
        with pytest.raises(ValueError, match="Gemini API configuration error"):
            await test_agent.generate_response("Test prompt")
        
        # Verify error count was incremented
        assert test_agent.error_count == 1
    
    @pytest.mark.asyncio
    async def test_generate_response_handles_other_api_errors(self, test_agent, mock_gemini_client):
        """Test that generate_response handles other API errors correctly."""
        
        # Test rate limit error
        def mock_rate_limit_error(*args, **kwargs):
            raise Exception("Rate limit exceeded")
        
        mock_gemini_client.generate_content = mock_rate_limit_error
        
        with pytest.raises(ValueError, match="rate limit exceeded"):
            await test_agent.generate_response("Test prompt")
        
        # Test quota error
        def mock_quota_error(*args, **kwargs):
            raise Exception("Quota exceeded")
        
        mock_gemini_client.generate_content = mock_quota_error
        
        with pytest.raises(ValueError, match="quota exceeded"):
            await test_agent.generate_response("Test prompt")
        
        # Test invalid parameter error
        def mock_invalid_param_error(*args, **kwargs):
            raise Exception("Invalid parameter")
        
        mock_gemini_client.generate_content = mock_invalid_param_error
        
        with pytest.raises(ValueError, match="Invalid parameter"):
            await test_agent.generate_response("Test prompt")
    
    @pytest.mark.asyncio
    async def test_generate_response_success_with_sanitization(self, test_agent, mock_gemini_client):
        """Test successful response generation with prompt sanitization."""
        
        # Mock successful response
        mock_response = Mock()
        mock_response.text = '{"test": "data"}'
        mock_gemini_client.generate_content.return_value = mock_response
        
        # Test with a prompt that should be sanitized
        problematic_prompt = "Generate JSON with src: invalid_value"
        
        result = await test_agent.generate_response(problematic_prompt)
        
        # Should get successful response
        assert result == '{"test": "data"}'
        
        # Verify the sanitized prompt was used
        call_args = mock_gemini_client.generate_content.call_args
        sanitized_prompt = call_args[0][0]  # First positional argument
        assert "src:" not in sanitized_prompt.lower()
    
    @pytest.mark.asyncio
    async def test_generate_response_uses_validated_config(self, test_agent, mock_gemini_client):
        """Test that generate_response uses validated configuration."""
        
        # Mock successful response
        mock_response = Mock()
        mock_response.text = '{"test": "data"}'
        mock_gemini_client.generate_content.return_value = mock_response
        
        # Test with invalid configuration that should be corrected
        test_agent.config.parameters = {
            "temperature": 3.0,  # Invalid
            "top_p": 1.5,        # Invalid
            "top_k": 0,          # Invalid
            "max_tokens": 10000  # Invalid
        }
        
        await test_agent.generate_response("Test prompt")
        
        # Verify the validated config was used
        call_args = mock_gemini_client.generate_content.call_args
        generation_config = call_args[1]['generation_config']  # Keyword argument
        
        assert generation_config["temperature"] == 2.0  # Should be clamped
        assert generation_config["top_p"] == 1.0        # Should be clamped
        assert generation_config["top_k"] == 1          # Should be clamped
        assert generation_config["max_output_tokens"] == 8192  # Should be clamped
    
    def test_validate_gemini_config_works_correctly(self, test_agent):
        """Test that Gemini configuration validation works correctly."""
        
        # Test valid configuration
        assert test_agent.validate_gemini_config() is True
        
        # Test missing client
        test_agent.gemini_client = None
        assert test_agent.validate_gemini_config() is False
        
        # Test missing generate_content method
        test_agent.gemini_client = Mock()
        del test_agent.gemini_client.generate_content
        assert test_agent.validate_gemini_config() is False
        
        # Test missing config
        test_agent.config = None
        assert test_agent.validate_gemini_config() is False
        
        # Test missing parameters
        test_agent.config = AgentConfig(
            name="test",
            description="test",
            enabled=True,
            max_retries=3,
            timeout=300,
            prompt_template="test",
            system_prompt="test",
            parameters={}
        )
        assert test_agent.validate_gemini_config() is False


class TestIntegrationScenarios:
    """Integration test scenarios for the src property error fix."""
    
    @pytest.fixture
    def agent_config(self):
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
    
    @pytest.mark.asyncio
    async def test_end_to_end_src_property_error_handling(self, agent_config):
        """Test end-to-end handling of src property error scenarios."""
        
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model_class.return_value = mock_model
            
            # Create agent
            agent = TestAgent(agent_config, mock_model)
            
            # Test scenario 1: Problematic prompt that should be sanitized
            def mock_success_response(*args, **kwargs):
                mock_response = Mock()
                mock_response.text = '{"result": "success"}'
                return mock_response
            
            mock_model.generate_content = mock_success_response
            
            problematic_prompt = "Generate JSON with src: invalid_value and malformed: {,}"
            result = await agent.generate_response(problematic_prompt)
            
            assert result == '{"result": "success"}'
            
            # Test scenario 2: API returns src property error
            def mock_src_error(*args, **kwargs):
                raise Exception("src property must be a valid json object")
            
            mock_model.generate_content = mock_src_error
            
            with pytest.raises(ValueError, match="Gemini API configuration error"):
                await agent.generate_response("Test prompt")
            
            # Test scenario 3: Invalid generation parameters
            agent.config.parameters = {
                "temperature": 5.0,  # Invalid
                "top_p": 2.0,        # Invalid
                "top_k": -1,         # Invalid
                "max_tokens": 20000  # Invalid
            }
            
            def mock_success_with_validated_config(*args, **kwargs):
                # Verify the config was validated
                generation_config = kwargs.get('generation_config', {})
                assert generation_config["temperature"] <= 2.0
                assert generation_config["top_p"] <= 1.0
                assert generation_config["top_k"] >= 1
                assert generation_config["max_output_tokens"] <= 8192
                
                mock_response = Mock()
                mock_response.text = '{"validated": "config"}'
                return mock_response
            
            mock_model.generate_content = mock_success_with_validated_config
            
            result = await agent.generate_response("Test prompt")
            assert result == '{"validated": "config"}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
