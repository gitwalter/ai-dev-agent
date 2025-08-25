"""
Tests for actual agent execution to identify and fix the "src property must be a valid json object" error.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from agents.base_agent import BaseAgent
from agents.requirements_analyst import RequirementsAnalyst
from agents.architecture_designer import ArchitectureDesigner
from agents.code_generator import CodeGenerator
from models.config import AgentConfig, SystemConfig, GeminiConfig
from models.state import AgentState


class TestAgentExecution:
    """Test actual agent execution to identify the src property error."""
    
    @pytest.fixture
    def system_config(self):
        """Create a system configuration."""
        gemini_config = GeminiConfig(
            api_key="test_api_key",
            model_name="gemini-2.0-flash-exp",
            max_tokens=8192,
            temperature=0.1,
            top_p=0.8,
            top_k=40
        )
        
        return SystemConfig(
            project_name="Test Project",
            version="1.0.0",
            environment="development",
            gemini=gemini_config
        )
    
    @pytest.fixture
    def agent_config(self):
        """Create an agent configuration."""
        return AgentConfig(
            name="test_agent",
            description="Test agent",
            enabled=True,
            max_retries=3,
            timeout=300,
            parameters={
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_tokens": 8192
            }
        )
    
    @pytest.fixture
    def sample_state(self):
        """Create a sample agent state."""
        return {
            "project_context": "Create a simple REST API for user management",
            "project_name": "user_management_api",
            "requirements": [],
            "user_stories": [],
            "architecture": {},
            "tech_stack": {},
            "database_schema": {},
            "code_files": {},
            "tests": {},
            "documentation": {},
            "configuration_files": {},
            "current_task": "requirements_analysis",
            "current_agent": "requirements_analyst",
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
    
    @pytest.fixture
    def mock_gemini_client(self):
        """Create a mock Gemini client."""
        client = Mock()
        client.generate_content = Mock()
        return client
    
    @pytest.mark.asyncio
    async def test_requirements_analyst_execution(self, system_config, agent_config, sample_state, mock_gemini_client):
        """Test RequirementsAnalyst execution to identify the src property error."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content = Mock()
            
            # Mock a successful response
            mock_response = Mock()
            mock_response.text = json.dumps({
                "functional_requirements": [
                    {
                        "id": "FR-001",
                        "title": "User Registration",
                        "description": "Users can register new accounts",
                        "priority": "high",
                        "complexity": "medium",
                        "category": "authentication"
                    }
                ],
                "non_functional_requirements": [
                    {
                        "id": "NFR-001",
                        "title": "Performance",
                        "description": "API response time under 200ms",
                        "metric": "response_time",
                        "target": "200ms",
                        "category": "performance"
                    }
                ],
                "user_stories": [
                    {
                        "id": "US-001",
                        "as_a": "user",
                        "i_want": "to register an account",
                        "so_that": "I can access the system",
                        "acceptance_criteria": ["Email validation", "Password requirements"],
                        "priority": "high",
                        "story_points": 5
                    }
                ],
                "acceptance_criteria": [],
                "technical_constraints": [],
                "assumptions": [],
                "risks": []
            })
            
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            # Create the agent
            agent = RequirementsAnalyst(agent_config, mock_model)
            
            # Execute the agent
            result = await agent.execute(sample_state)
            
            # Verify the result
            assert "requirements" in result
            assert len(result["requirements"]) > 0
            assert result["requirements"][0]["id"] == "FR-001"
    
    @pytest.mark.asyncio
    async def test_requirements_analyst_src_property_error(self, system_config, agent_config, sample_state, mock_gemini_client):
        """Test RequirementsAnalyst execution with the specific src property error."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            
            # Mock the specific src property error
            def mock_generate_content(*args, **kwargs):
                raise Exception("src property must be a valid json object")
            
            mock_model.generate_content = mock_generate_content
            mock_model_class.return_value = mock_model
            
            # Create the agent
            agent = RequirementsAnalyst(agent_config, mock_model)
            
            # Execute the agent and expect the error
            result = await agent.execute(sample_state)
            
            # The agent should handle the error gracefully
            assert "errors" in result
            assert len(result["errors"]) > 0
            assert "src property must be a valid json object" in str(result["errors"][0]["message"])
    
    @pytest.mark.asyncio
    async def test_architecture_designer_execution(self, system_config, agent_config, sample_state, mock_gemini_client):
        """Test ArchitectureDesigner execution."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content = Mock()
            
            # Mock a successful response
            mock_response = Mock()
            mock_response.text = json.dumps({
                "system_overview": "Layered architecture for user management",
                "architecture_pattern": "layered",
                "components": [
                    {
                        "name": "User Management Service",
                        "responsibility": "Handle user operations",
                        "dependencies": ["Database"],
                        "interfaces": ["REST API"]
                    }
                ],
                "data_flow": "User requests flow through API to service to database",
                "technology_stack": {
                    "frontend": ["React"],
                    "backend": ["Python", "FastAPI"],
                    "database": ["PostgreSQL"],
                    "infrastructure": ["Docker"],
                    "devops": ["GitHub Actions"]
                },
                "security_considerations": ["Authentication", "Authorization"],
                "scalability_considerations": ["Horizontal scaling"],
                "performance_considerations": ["Caching"],
                "deployment_strategy": "Container-based",
                "risk_mitigation": ["Monitoring", "Backup"]
            })
            
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            # Create the agent
            agent = ArchitectureDesigner(agent_config, mock_model)
            
            # Execute the agent
            result = await agent.execute(sample_state)
            
            # Verify the result
            assert "architecture" in result
            assert result["architecture"]["architecture_pattern"] == "layered"
    
    @pytest.mark.asyncio
    async def test_code_generator_execution(self, system_config, agent_config, sample_state, mock_gemini_client):
        """Test CodeGenerator execution."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content = Mock()
            
            # Mock a successful response
            mock_response = Mock()
            mock_response.text = json.dumps({
                "project_structure": ["src/", "tests/", "docs/"],
                "source_files": {
                    "src/main.py": "# Main application file\nfrom fastapi import FastAPI\n\napp = FastAPI()",
                    "src/models.py": "# Data models\nfrom pydantic import BaseModel\n\nclass User(BaseModel):\n    id: int\n    name: str"
                },
                "configuration_files": {
                    "requirements.txt": "fastapi==0.104.0\nuvicorn==0.24.0",
                    "Dockerfile": "FROM python:3.9\nCOPY . .\nRUN pip install -r requirements.txt"
                },
                "dependencies": {
                    "requirements.txt": "fastapi==0.104.0\nuvicorn==0.24.0"
                },
                "documentation": {
                    "README.md": "# User Management API\n\nA simple REST API for user management."
                }
            })
            
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            # Create the agent
            agent = CodeGenerator(agent_config, mock_model)
            
            # Execute the agent
            result = await agent.execute(sample_state)
            
            # Verify the result
            assert "code_files" in result
            assert len(result["code_files"]) > 0
            assert "src/main.py" in result["code_files"]
    
    @pytest.mark.asyncio
    async def test_agent_execution_with_malformed_json(self, system_config, agent_config, sample_state, mock_gemini_client):
        """Test agent execution with malformed JSON response."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content = Mock()
            
            # Mock a malformed JSON response
            mock_response = Mock()
            mock_response.text = '{"test": "data",}'  # Trailing comma
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            # Create the agent
            agent = RequirementsAnalyst(agent_config, mock_model)
            
            # Execute the agent - should handle malformed JSON
            result = await agent.execute(sample_state)
            
            # Should not have errors due to JSON parsing
            assert "errors" not in result or len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_agent_execution_with_empty_response(self, system_config, agent_config, sample_state, mock_gemini_client):
        """Test agent execution with empty response."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content = Mock()
            
            # Mock an empty response
            mock_response = Mock()
            mock_response.text = ""
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            # Create the agent
            agent = RequirementsAnalyst(agent_config, mock_model)
            
            # Execute the agent
            result = await agent.execute(sample_state)
            
            # Should handle empty response gracefully
            assert "errors" in result
            assert len(result["errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_agent_execution_with_invalid_config(self, system_config, sample_state, mock_gemini_client):
        """Test agent execution with invalid configuration."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content = Mock()
            mock_model_class.return_value = mock_model
            
            # Create agent with invalid config
            invalid_config = AgentConfig(
                name="test_agent",
                description="Test agent",
                enabled=True,
                max_retries=3,
                timeout=300,
                parameters={}  # Empty parameters
            )
            
            # Create the agent
            agent = RequirementsAnalyst(invalid_config, mock_model)
            
            # Execute the agent
            result = await agent.execute(sample_state)
            
            # Should handle invalid config gracefully
            assert "errors" in result
            assert len(result["errors"]) > 0


class TestAgentErrorHandling:
    """Test error handling in agents."""
    
    @pytest.fixture
    def agent_config(self):
        return AgentConfig(
            name="test_agent",
            description="Test agent",
            enabled=True,
            max_retries=3,
            timeout=300,
            parameters={
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_tokens": 8192
            }
        )
    
    @pytest.fixture
    def sample_state(self):
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
    
    @pytest.mark.asyncio
    async def test_agent_handles_connection_error(self, agent_config, sample_state):
        """Test agent handles connection errors gracefully."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content.side_effect = Exception("Connection error")
            mock_model_class.return_value = mock_model
            
            agent = RequirementsAnalyst(agent_config, mock_model)
            result = await agent.execute(sample_state)
            
            assert "errors" in result
            assert len(result["errors"]) > 0
            assert "Connection error" in str(result["errors"][0]["message"])
    
    @pytest.mark.asyncio
    async def test_agent_handles_rate_limit_error(self, agent_config, sample_state):
        """Test agent handles rate limit errors gracefully."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content.side_effect = Exception("Rate limit exceeded")
            mock_model_class.return_value = mock_model
            
            agent = RequirementsAnalyst(agent_config, mock_model)
            result = await agent.execute(sample_state)
            
            assert "errors" in result
            assert len(result["errors"]) > 0
            assert "Rate limit exceeded" in str(result["errors"][0]["message"])
    
    @pytest.mark.asyncio
    async def test_agent_handles_invalid_api_key(self, agent_config, sample_state):
        """Test agent handles invalid API key errors gracefully."""
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            mock_model = Mock()
            mock_model.generate_content.side_effect = Exception("Invalid API key")
            mock_model_class.return_value = mock_model
            
            agent = RequirementsAnalyst(agent_config, mock_model)
            result = await agent.execute(sample_state)
            
            assert "errors" in result
            assert len(result["errors"]) > 0
            assert "Invalid API key" in str(result["errors"][0]["message"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
