"""
Fast pytest configuration for unit tests.
Optimized for quick startup with minimal imports.
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def fast_test_config():
    """Fast test configuration with minimal setup."""
    return {
        "test_mode": True,
        "api_key": "test-key-123",
        "timeout": 5,
        "max_retries": 1
    }


@pytest.fixture
def temp_dir(tmp_path):
    """Provide temporary directory for tests."""
    return tmp_path


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    test_vars = {
        "AI_DEV_AGENT_ENV": "test",
        "LOG_LEVEL": "WARNING",
        "DISABLE_TELEMETRY": "true"
    }
    
    for key, value in test_vars.items():
        os.environ[key] = value
    
    yield test_vars
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {
        "project_name": "test-project",
        "description": "Test project for unit testing",
        "files": ["main.py", "test_main.py", "README.md"],
        "config": {"version": "1.0", "debug": True}
    }


# Configure pytest for fast execution
def pytest_configure(config):
    """Configure pytest for fast execution."""
    # Disable slow plugins if they exist
    config.option.disable_warnings = True
    
    # Set fast execution markers
    config.addinivalue_line("markers", "fast: mark test as fast")
    config.addinivalue_line("markers", "slow: mark test as slow")


def pytest_collection_modifyitems(config, items):
    """Modify test collection for performance."""
    # Skip slow tests by default in fast mode
    if config.getoption("--fast", default=False):
        skip_slow = pytest.mark.skip(reason="Skipping slow test in fast mode")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--fast",
        action="store_true",
        default=False,
        help="Run only fast tests, skip slow ones"
    )
    parser.addoption(
        "--no-heavy-imports",
        action="store_true", 
        default=False,
        help="Skip tests that require heavy imports"
    )


# Fast test utilities
class FastTestHelper:
    """Helper class for fast testing."""
    
    @staticmethod
    def create_mock_response(status="success", data=None):
        """Create a mock response quickly."""
        return {
            "status": status,
            "data": data or {},
            "timestamp": "2023-01-01T00:00:00Z",
            "execution_time": 0.001
        }
    
    @staticmethod
    def assert_fast_execution(func, max_time=0.1):
        """Assert that a function executes quickly."""
        import time
        start = time.time()
        result = func()
        end = time.time()
        
        execution_time = end - start
        assert execution_time < max_time, f"Function took {execution_time:.3f}s, expected < {max_time}s"
        return result


@pytest.fixture
def fast_helper():
    """Provide fast test helper."""
    return FastTestHelper()


# Performance monitoring
@pytest.fixture(autouse=True)
def monitor_test_performance(request):
    """Monitor test performance automatically."""
    import time
    
    start_time = time.time()
    yield
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Log slow tests
    if execution_time > 1.0:
        print(f"\n⚠️  Slow test detected: {request.node.name} took {execution_time:.3f}s")
    elif execution_time > 0.5:
        print(f"\n⏱️  Moderate test: {request.node.name} took {execution_time:.3f}s")


# Skip heavy imports in fast mode
def skip_if_heavy_imports(request):
    """Skip test if heavy imports are disabled."""
    if request.config.getoption("--no-heavy-imports"):
        pytest.skip("Skipping test with heavy imports")


# Fast mock factories
@pytest.fixture
def mock_agent_response():
    """Fast mock agent response."""
    return {
        "agent_name": "test_agent",
        "status": "completed",
        "output": {"result": "test_output"},
        "execution_time": 0.001,
        "memory_usage": 1024
    }


@pytest.fixture
def mock_config():
    """Fast mock configuration."""
    return {
        "agents": {"test_agent": {"enabled": True, "timeout": 5}},
        "logging": {"level": "WARNING", "file": None},
        "performance": {"max_execution_time": 10}
    }
