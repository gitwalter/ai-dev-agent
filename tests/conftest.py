"""
Shared pytest fixtures for AI Development Agent tests.
This file provides common fixtures that can be used across all test modules.
"""

import os
import sys
import tempfile
import shutil
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.config import SystemConfig, get_default_config
from models.state import create_initial_state
from tests.test_utils import TestConfig, MockGeminiClient, TestStateBuilder


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Provide test configuration with safe defaults."""
    return TestConfig.get_test_config()


@pytest.fixture
def temp_project_dir():
    """Provide temporary project directory for testing."""
    temp_dir = TestConfig.create_temp_project_dir()
    yield temp_dir
    TestConfig.cleanup_temp_dir(temp_dir)


@pytest.fixture
def mock_gemini_client():
    """Provide mock Gemini client for testing."""
    return MockGeminiClient()


@pytest.fixture
def test_state():
    """Provide test state for workflow testing."""
    return TestStateBuilder.create_test_state()


@pytest.fixture
def mock_agent_response():
    """Provide mock agent response for testing."""
    return {
        "agent_name": "test_agent",
        "task_name": "test_task",
        "status": "completed",
        "output": {"result": "test_output"},
        "execution_time": 1.0,
        "documentation": {"summary": "Test documentation"},
        "logs": [{"timestamp": "2023-01-01T00:00:00", "level": "info", "message": "Test log"}],
        "decisions": [{"decision": "Test decision", "rationale": "Test rationale"}],
        "artifacts": [{"name": "test_artifact", "type": "test", "description": "Test artifact"}]
    }


@pytest.fixture
def mock_workflow_result():
    """Provide mock workflow result for testing."""
    return {
        "workflow_id": "test-workflow-123",
        "session_id": "test-session-123",
        "status": "completed",
        "project_name": "test-project",
        "project_context": "Test project context",
        "agent_results": {},
        "generated_files": {"test.py": "# Test file content"},
        "code_files": {"main.py": "# Main code"},
        "test_files": {"test_main.py": "# Test code"},
        "documentation_files": {"README.md": "# Test documentation"},
        "configuration_files": {"config.py": "# Test config"},
        "total_execution_time": 10.0,
        "errors": [],
        "warnings": []
    }


@pytest.fixture
def sample_project_files():
    """Provide sample project files for testing."""
    return {
        "main.py": """
import sys
import json
from pathlib import Path

def main():
    print("Hello, World!")
    
if __name__ == "__main__":
    main()
""",
        "test_main.py": """
import pytest
from main import main

def test_main():
    # Test implementation
    assert True
""",
        "README.md": """
# Test Project

This is a test project for testing purposes.
""",
        "requirements.txt": """
pytest==7.0.0
"""
    }


@pytest.fixture
def test_project_context():
    """Provide test project context."""
    return """
    Create a simple Python application with the following features:
    - Basic CRUD operations
    - Simple file-based storage
    - Command-line interface
    - Basic error handling
    - Simple logging
    - Basic documentation
    - No external dependencies beyond standard library
    - Easy to understand and modify code
    """


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["GEMINI_API_KEY"] = "test-api-key"
    
    # Create temporary directories if needed
    temp_dirs = []
    
    yield
    
    # Cleanup
    for temp_dir in temp_dirs:
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)


@pytest.fixture
def mock_file_system():
    """Provide mock file system for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create some test files
        (temp_path / "test_file.txt").write_text("Test content")
        (temp_path / "test_dir").mkdir()
        (temp_path / "test_dir" / "nested_file.txt").write_text("Nested content")
        
        yield temp_path


@pytest.fixture
def mock_logger():
    """Provide mock logger for testing."""
    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger


@pytest.fixture
def mock_async_context():
    """Provide async context for testing."""
    class AsyncContext:
        def __init__(self):
            self.loop = None
        
        async def __aenter__(self):
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            return self.loop
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if self.loop:
                self.loop.close()
    
    return AsyncContext()


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Provide performance timer for testing."""
    from tests.test_utils import PerformanceTimer
    return PerformanceTimer()


# Security testing fixtures
@pytest.fixture
def mock_security_scan():
    """Provide mock security scan results."""
    return {
        "vulnerabilities": [
            {
                "id": "CVE-2023-1234",
                "severity": "high",
                "description": "Test vulnerability",
                "affected_component": "test_component"
            }
        ],
        "security_score": 7.5,
        "recommendations": [
            {
                "category": "authentication",
                "recommendation": "Implement MFA",
                "priority": "high"
            }
        ]
    }


# API testing fixtures
@pytest.fixture
def mock_api_response():
    """Provide mock API response."""
    return {
        "status": "success",
        "data": {"result": "test_data"},
        "message": "Test response"
    }


@pytest.fixture
def mock_http_client():
    """Provide mock HTTP client."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        yield mock_instance


# Database testing fixtures
@pytest.fixture
def mock_database():
    """Provide mock database connection."""
    with patch('sqlalchemy.create_engine') as mock_engine:
        mock_instance = Mock()
        mock_engine.return_value = mock_instance
        yield mock_instance


# File system testing fixtures
@pytest.fixture
def mock_file_operations():
    """Provide mock file operations."""
    with patch('pathlib.Path') as mock_path:
        mock_instance = Mock()
        mock_path.return_value = mock_instance
        yield mock_instance


# Configuration testing fixtures
@pytest.fixture
def mock_config_loader():
    """Provide mock configuration loader."""
    with patch('utils.toml_config.TOMLConfigLoader') as mock_loader:
        mock_instance = Mock()
        mock_loader.return_value = mock_instance
        yield mock_instance


# Workflow testing fixtures
@pytest.fixture
def mock_workflow_graph():
    """Provide mock workflow graph."""
    with patch('workflow.workflow_graph.create_workflow_graph') as mock_graph:
        mock_instance = Mock()
        mock_graph.return_value = mock_instance
        yield mock_instance


# Agent testing fixtures
@pytest.fixture
def mock_agent():
    """Provide mock agent."""
    with patch('agents.base_agent.BaseAgent') as mock_agent_class:
        mock_instance = Mock()
        mock_agent_class.return_value = mock_instance
        yield mock_instance


# Utility fixtures
@pytest.fixture
def sample_json_data():
    """Provide sample JSON data for testing."""
    return {
        "string": "test_string",
        "number": 42,
        "boolean": True,
        "array": [1, 2, 3],
        "object": {"key": "value"},
        "null": None
    }


@pytest.fixture
def sample_yaml_data():
    """Provide sample YAML data for testing."""
    return """
    name: Test Project
    version: 1.0.0
    description: A test project
    dependencies:
      - pytest
      - requests
    config:
      debug: true
      timeout: 30
    """


@pytest.fixture
def mock_time():
    """Provide mock time for testing."""
    with patch('time.time') as mock_time_func:
        mock_time_func.return_value = 1234567890.0
        yield mock_time_func


@pytest.fixture
def mock_uuid():
    """Provide mock UUID for testing."""
    with patch('uuid.uuid4') as mock_uuid_func:
        mock_uuid_func.return_value = "test-uuid-1234-5678-90ab-cdef12345678"
        yield mock_uuid_func


@pytest.fixture
def mock_llm():
    """Provide mock LLM for testing LangChain components."""
    mock = Mock()
    mock.invoke = Mock()
    mock.ainvoke = Mock()
    return mock


@pytest.fixture
def basic_state():
    """Provide basic state for LangGraph workflow testing."""
    return {
        "project_context": "Create a simple task management system",
        "project_name": "test-project",
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
        "current_step": "start"
    }
