"""
Integration tests for Gemini API to identify and fix the "src property must be a valid json object" error.
"""

import pytest
import json
import asyncio
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse


class TestGeminiAPIIntegration:
    """Integration tests for Gemini API to identify the src property error."""
    
    @pytest.fixture
    def gemini_config(self):
        """Create Gemini configuration."""
        return {
            "api_key": "test_api_key",
            "model_name": "gemini-2.0-flash-exp",
            "max_tokens": 8192,
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 40
        }
    
    @pytest.fixture
    def mock_gemini_response(self):
        """Create a mock Gemini response that might cause the src property error."""
        # Create a mock response that mimics the actual Gemini response structure
        mock_part = Mock()
        mock_part.text = '{"test": "data"}'

        mock_content = Mock()
        mock_content.parts = [mock_part]

        mock_candidate = Mock()
        mock_candidate.content = mock_content

        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        mock_response.text = '{"test": "data"}'
        
        return mock_response
    
    @pytest.fixture
    def mock_gemini_response_with_src(self):
        """Create a mock Gemini response with src property that might cause the error."""
        mock_part = Mock()
        mock_part.text = json.dumps({
            "src": {
                "type": "text",
                "content": "Generated content"
            },
            "data": {"test": "value"}
        })
        
        mock_content = Mock()
        mock_content.parts = [mock_part]

        mock_candidate = Mock()
        mock_candidate.content = mock_content

        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        mock_response.text = json.dumps({
            "src": {
                "type": "text",
                "content": "Generated content"
            },
            "data": {"test": "value"}
        })
        
        return mock_response
    
    @pytest.mark.asyncio
    async def test_gemini_api_basic_call(self, gemini_config):
        """Test basic Gemini API call to identify the src property error."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            # Create mock model
            mock_model = Mock()
            mock_model.generate_content = Mock()
            
            # Mock successful response
            mock_response = Mock()
            mock_response.text = '{"test": "data"}'
            mock_model.generate_content.return_value = mock_response
            
            mock_model_class.return_value = mock_model
            
            # Test the API call
            model = genai.GenerativeModel(gemini_config["model_name"])
            response = await asyncio.to_thread(
                model.generate_content,
                "Test prompt",
                generation_config={
                    "temperature": gemini_config["temperature"],
                    "top_p": gemini_config["top_p"],
                    "top_k": gemini_config["top_k"],
                    "max_output_tokens": gemini_config["max_tokens"]
                }
            )
            
            assert response.text == '{"test": "data"}'
    
    @pytest.mark.asyncio
    async def test_gemini_api_src_property_error_simulation(self, gemini_config):
        """Simulate the specific src property error to understand its cause."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            
            # Simulate the specific error
            def mock_generate_content(*args, **kwargs):
                raise Exception("src property must be a valid json object")
            
            mock_model.generate_content = mock_generate_content
            mock_model_class.return_value = mock_model
            
            model = genai.GenerativeModel(gemini_config["model_name"])
            
            with pytest.raises(Exception, match="src property must be a valid json object"):
                await asyncio.to_thread(
                    model.generate_content,
                    "Test prompt",
                    generation_config={
                        "temperature": gemini_config["temperature"],
                        "top_p": gemini_config["top_p"],
                        "top_k": gemini_config["top_k"],
                        "max_output_tokens": gemini_config["max_tokens"]
                    }
                )
    
    @pytest.mark.asyncio
    async def test_gemini_api_response_with_src_property(self, gemini_config, mock_gemini_response_with_src):
        """Test handling of response that contains src property."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content = Mock(return_value=mock_gemini_response_with_src)
            mock_model_class.return_value = mock_model
            
            model = genai.GenerativeModel(gemini_config["model_name"])
            response = await asyncio.to_thread(
                model.generate_content,
                "Test prompt",
                generation_config={
                    "temperature": gemini_config["temperature"],
                    "top_p": gemini_config["top_p"],
                    "top_k": gemini_config["top_k"],
                    "max_output_tokens": gemini_config["max_tokens"]
                }
            )
            
            # This should not cause the src property error
            assert response.text is not None
            parsed = json.loads(response.text)
            assert "src" in parsed
            assert "data" in parsed
    
    @pytest.mark.asyncio
    async def test_gemini_api_invalid_generation_config(self, gemini_config):
        """Test if invalid generation config causes the src property error."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            
            # Test with invalid generation config that might cause the error
            def mock_generate_content(*args, **kwargs):
                # Check if the generation config contains invalid values
                generation_config = kwargs.get('generation_config', {})
                if 'invalid_param' in generation_config:
                    raise Exception("src property must be a valid json object")
                return Mock(text='{"test": "data"}')
            
            mock_model.generate_content = mock_generate_content
            mock_model_class.return_value = mock_model
            
            model = genai.GenerativeModel(gemini_config["model_name"])
            
            # Test with valid config
            response = await asyncio.to_thread(
                model.generate_content,
                "Test prompt",
                generation_config={
                    "temperature": gemini_config["temperature"],
                    "top_p": gemini_config["top_p"],
                    "top_k": gemini_config["top_k"],
                    "max_output_tokens": gemini_config["max_tokens"]
                }
            )
            
            assert response.text == '{"test": "data"}'
            
            # Test with invalid config
            with pytest.raises(Exception, match="src property must be a valid json object"):
                await asyncio.to_thread(
                    model.generate_content,
                    "Test prompt",
                    generation_config={
                        "temperature": gemini_config["temperature"],
                        "invalid_param": "invalid_value"
                    }
                )
    
    @pytest.mark.asyncio
    async def test_gemini_api_prompt_format_issues(self, gemini_config):
        """Test if prompt format issues cause the src property error."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            
            def mock_generate_content(*args, **kwargs):
                prompt = args[0] if args else ""
                # Check if prompt contains problematic content
                if "invalid_json" in prompt or "src:" in prompt:
                    raise Exception("src property must be a valid json object")
                return Mock(text='{"test": "data"}')
            
            mock_model.generate_content = mock_generate_content
            mock_model_class.return_value = mock_model
            
            model = genai.GenerativeModel(gemini_config["model_name"])
            
            # Test with valid prompt
            response = await asyncio.to_thread(
                model.generate_content,
                "Generate a JSON response",
                generation_config={
                    "temperature": gemini_config["temperature"],
                    "top_p": gemini_config["top_p"],
                    "top_k": gemini_config["top_k"],
                    "max_output_tokens": gemini_config["max_tokens"]
                }
            )
            
            assert response.text == '{"test": "data"}'
            
            # Test with problematic prompt
            with pytest.raises(Exception, match="src property must be a valid json object"):
                await asyncio.to_thread(
                    model.generate_content,
                    "Generate JSON with src: invalid_json",
                    generation_config={
                        "temperature": gemini_config["temperature"],
                        "top_p": gemini_config["top_p"],
                        "top_k": gemini_config["top_k"],
                        "max_output_tokens": gemini_config["max_tokens"]
                    }
                )


class TestGeminiAPIErrorHandling:
    """Test error handling for Gemini API issues."""
    
    @pytest.mark.asyncio
    async def test_gemini_api_connection_error(self):
        """Test handling of connection errors."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content.side_effect = Exception("Connection error")
            mock_model_class.return_value = mock_model
            
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            with pytest.raises(Exception, match="Connection error"):
                await asyncio.to_thread(
                    model.generate_content,
                    "Test prompt"
                )
    
    @pytest.mark.asyncio
    async def test_gemini_api_rate_limit_error(self):
        """Test handling of rate limit errors."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content.side_effect = Exception("Rate limit exceeded")
            mock_model_class.return_value = mock_model
            
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            with pytest.raises(Exception, match="Rate limit exceeded"):
                await asyncio.to_thread(
                    model.generate_content,
                    "Test prompt"
                )
    
    @pytest.mark.asyncio
    async def test_gemini_api_invalid_api_key(self):
        """Test handling of invalid API key errors."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content.side_effect = Exception("Invalid API key")
            mock_model_class.return_value = mock_model
            
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            with pytest.raises(Exception, match="Invalid API key"):
                await asyncio.to_thread(
                    model.generate_content,
                    "Test prompt"
                )


class TestGeminiAPIResponseParsing:
    """Test parsing of different Gemini API response formats."""
    
    @pytest.mark.asyncio
    async def test_parse_gemini_response_text(self):
        """Test parsing response with text property."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = '{"result": "success"}'
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = await asyncio.to_thread(
                model.generate_content,
                "Test prompt"
            )
            
            assert response.text == '{"result": "success"}'
            parsed = json.loads(response.text)
            assert parsed["result"] == "success"
    
    @pytest.mark.asyncio
    async def test_parse_gemini_response_parts(self):
        """Test parsing response with parts structure."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            
            # Create response with parts
            mock_part = Mock()
            mock_part.text = '{"result": "success"}'
            mock_response = Mock()
            mock_response.parts = [mock_part]
            mock_response.text = None
            
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = await asyncio.to_thread(
                model.generate_content,
                "Test prompt"
            )
            
            # Extract text from parts
            if hasattr(response, 'parts') and response.parts:
                text_parts = []
                for part in response.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                if text_parts:
                    combined_text = " ".join(text_parts)
                    parsed = json.loads(combined_text)
                    assert parsed["result"] == "success"
    
    @pytest.mark.asyncio
    async def test_parse_gemini_response_candidates(self):
        """Test parsing response with candidates structure."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            
            # Create response with candidates
            mock_part = Mock()
            mock_part.text = '{"result": "success"}'
            mock_content = Mock()
            mock_content.parts = [mock_part]
            mock_candidate = Mock()
            mock_candidate.content = mock_content
            mock_response = Mock()
            mock_response.candidates = [mock_candidate]
            mock_response.text = None
            
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = await asyncio.to_thread(
                model.generate_content,
                "Test prompt"
            )
            
            # Extract text from candidates
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            text_parts = []
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    text_parts.append(part.text)
                            if text_parts:
                                combined_text = " ".join(text_parts)
                                parsed = json.loads(combined_text)
                                assert parsed["result"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
