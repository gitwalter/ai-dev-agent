"""
Test utilities and common testing functions for AI Development Agent.
Provides shared testing infrastructure and helper functions.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import pytest
import asyncio
from unittest.mock import Mock, patch

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.config import SystemConfig, get_default_config
from models.state import create_initial_state


class TestConfig:
    """Test configuration and utilities."""
    
    @staticmethod
    def get_test_config() -> SystemConfig:
        """Get a test configuration with safe defaults."""
        config = get_default_config()
        config.gemini.api_key = "test-api-key"
        config.environment = "test"
        config.logging.level = "WARNING"
        return config
    
    @staticmethod
    def create_temp_project_dir() -> Path:
        """Create a temporary directory for test projects."""
        temp_dir = Path(tempfile.mkdtemp(prefix="ai_dev_agent_test_"))
        return temp_dir
    
    @staticmethod
    def cleanup_temp_dir(temp_dir: Path):
        """Clean up temporary test directory."""
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


class MockGeminiClient:
    """Mock Gemini client for testing."""
    
    def __init__(self, responses: Optional[Dict[str, str]] = None):
        self.responses = responses or {}
        self.calls = []
    
    async def generate_content(self, prompt: str, **kwargs) -> Mock:
        """Mock generate_content method."""
        self.calls.append({"prompt": prompt, "kwargs": kwargs})
        
        # Return a mock response
        mock_response = Mock()
        mock_response.text = self.responses.get(prompt, "Mock response")
        return mock_response


class TestStateBuilder:
    """Helper for building test states."""
    
    @staticmethod
    def create_test_state(
        project_context: str = "Test project",
        project_name: str = "test-project",
        session_id: str = "test-session-123"
    ) -> Dict[str, Any]:
        """Create a test state with default values."""
        return create_initial_state(
            project_context=project_context,
            project_name=project_name,
            session_id=session_id
        )


class AsyncTestCase:
    """Base class for async test cases."""
    
    @pytest.fixture(autouse=True)
    def setup_event_loop(self):
        """Setup event loop for async tests."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        yield
        self.loop.close()
    
    def run_async(self, coro):
        """Run an async coroutine in the test event loop."""
        return self.loop.run_until_complete(coro)


def create_mock_agent_response(
    agent_name: str = "test_agent",
    status: str = "completed",
    output: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a mock agent response for testing."""
    return {
        "agent_name": agent_name,
        "task_name": f"{agent_name}_task",
        "status": status,
        "output": output or {},
        "execution_time": 1.0,
        "documentation": {"summary": "Test documentation"},
        "logs": [{"timestamp": "2023-01-01T00:00:00", "level": "info", "message": "Test log"}],
        "decisions": [{"decision": "Test decision", "rationale": "Test rationale"}],
        "artifacts": [{"name": "test_artifact", "type": "test", "description": "Test artifact"}]
    }


def create_mock_workflow_result(
    project_name: str = "test-project",
    status: str = "completed",
    agent_results: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a mock workflow result for testing."""
    return {
        "workflow_id": "test-workflow-123",
        "session_id": "test-session-123",
        "status": status,
        "project_name": project_name,
        "project_context": "Test project context",
        "agent_results": agent_results or {},
        "generated_files": {"test.py": "# Test file content"},
        "code_files": {"main.py": "# Main code"},
        "test_files": {"test_main.py": "# Test code"},
        "documentation_files": {"README.md": "# Test documentation"},
        "configuration_files": {"config.py": "# Test config"},
        "total_execution_time": 10.0,
        "errors": [],
        "warnings": []
    }


# Pytest fixtures
@pytest.fixture
def test_config():
    """Fixture providing test configuration."""
    return TestConfig.get_test_config()


@pytest.fixture
def temp_project_dir():
    """Fixture providing temporary project directory."""
    temp_dir = TestConfig.create_temp_project_dir()
    yield temp_dir
    TestConfig.cleanup_temp_dir(temp_dir)


@pytest.fixture
def mock_gemini_client():
    """Fixture providing mock Gemini client."""
    return MockGeminiClient()


@pytest.fixture
def test_state():
    """Fixture providing test state."""
    return TestStateBuilder.create_test_state()


# Test decorators
def requires_api_key(func):
    """Decorator to skip tests that require API key."""
    def wrapper(*args, **kwargs):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your-gemini-api-key-here":
            pytest.skip("API key required for this test")
        return func(*args, **kwargs)
    return wrapper


def slow_test(func):
    """Decorator to mark slow tests."""
    func.slow = True
    return func


# Test assertions
def assert_file_exists(file_path: Path, content_contains: Optional[str] = None):
    """Assert that a file exists and optionally contains specific content."""
    assert file_path.exists(), f"File {file_path} does not exist"
    
    if content_contains:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert content_contains in content, f"File {file_path} does not contain '{content_contains}'"


def assert_directory_structure(base_path: Path, expected_structure: Dict[str, Any]):
    """Assert that a directory has the expected structure."""
    for item, expected in expected_structure.items():
        item_path = base_path / item
        
        if isinstance(expected, dict):
            # Directory
            assert item_path.is_dir(), f"Expected directory {item_path} does not exist"
            assert_directory_structure(item_path, expected)
        else:
            # File
            assert item_path.is_file(), f"Expected file {item_path} does not exist"
            
            if expected is not None:
                with open(item_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert expected in content, f"File {item_path} does not contain expected content"


# Performance testing utilities
class PerformanceTimer:
    """Utility for measuring test performance."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start timing."""
        self.start_time = asyncio.get_event_loop().time()
    
    def stop(self):
        """Stop timing."""
        self.end_time = asyncio.get_event_loop().time()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None or self.end_time is None:
            raise ValueError("Timer not started or stopped")
        return self.end_time - self.start_time
    
    def assert_faster_than(self, max_seconds: float):
        """Assert that the operation completed faster than max_seconds."""
        assert self.elapsed < max_seconds, f"Operation took {self.elapsed:.2f}s, expected less than {max_seconds}s"


# Test data generators
def generate_test_project_context() -> str:
    """Generate a test project context."""
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


def generate_test_files() -> Dict[str, str]:
    """Generate test files for testing."""
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
