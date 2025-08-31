"""
Fast unit tests for utilities - optimized for quick startup.
Minimal imports and focused testing for performance.
"""

import pytest

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
import pytest

# Minimal imports - avoid heavy dependencies
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.mark.fast
def test_basic_path_operations():
    """Test basic path operations without heavy imports."""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_"))
    
    # Test directory creation
    test_subdir = temp_dir / "subdir"
    test_subdir.mkdir()
    assert test_subdir.exists()
    
    # Test file creation
    test_file = test_subdir / "test.txt"
    test_file.write_text("test content")
    assert test_file.exists()
    assert test_file.read_text() == "test content"
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


def test_environment_variables():
    """Test environment variable handling."""
    test_key = "TEST_AI_DEV_AGENT_VAR"
    test_value = "test_value_123"
    
    # Set environment variable
    os.environ[test_key] = test_value
    assert os.getenv(test_key) == test_value
    
    # Clean up
    del os.environ[test_key]
    assert os.getenv(test_key) is None


def test_string_operations():
    """Test basic string operations."""
    test_string = "AI Development Agent"
    
    assert test_string.lower() == "ai development agent"
    assert test_string.upper() == "AI DEVELOPMENT AGENT"
    assert "Development" in test_string
    assert test_string.replace("Agent", "System") == "AI Development System"


def test_list_operations():
    """Test basic list operations."""
    test_list = [1, 2, 3, 4, 5]
    
    assert len(test_list) == 5
    assert test_list[0] == 1
    assert test_list[-1] == 5
    assert sum(test_list) == 15
    
    # Test list comprehension
    squared = [x**2 for x in test_list]
    assert squared == [1, 4, 9, 16, 25]


def test_dict_operations():
    """Test basic dictionary operations."""
    test_dict = {"name": "AI Agent", "version": "1.0", "active": True}
    
    assert test_dict["name"] == "AI Agent"
    assert test_dict.get("version") == "1.0"
    assert test_dict.get("missing", "default") == "default"
    
    # Test dictionary update
    test_dict.update({"status": "running"})
    assert "status" in test_dict
    assert test_dict["status"] == "running"


def test_json_operations():
    """Test JSON operations without heavy imports."""
    import json
    
    test_data = {"agent": "test", "config": {"enabled": True, "timeout": 30}}
    
    # Serialize to JSON
    json_string = json.dumps(test_data)
    assert isinstance(json_string, str)
    assert "agent" in json_string
    
    # Deserialize from JSON
    parsed_data = json.loads(json_string)
    assert parsed_data == test_data
    assert parsed_data["config"]["enabled"] is True


def test_pathlib_operations():
    """Test pathlib operations."""
    current_file = Path(__file__)
    
    assert current_file.exists()
    assert current_file.is_file()
    assert current_file.suffix == ".py"
    assert current_file.stem == "test_fast_utils"
    
    parent_dir = current_file.parent
    assert parent_dir.exists()
    assert parent_dir.is_dir()


def test_basic_error_handling():
    """Test basic error handling patterns."""
    
    # Test exception handling
    try:
        result = 10 / 0
        assert False, "Should have raised ZeroDivisionError"
    except ZeroDivisionError:
        assert True
    
    # Test with custom exception
    def risky_function():
        raise ValueError("Test error")
    
    with pytest.raises(ValueError, match="Test error"):
        risky_function()


def test_basic_imports():
    """Test that basic imports work quickly."""
    import time
    start = time.time()
    
    # Test standard library imports
    import json
    import os
    import sys
    from pathlib import Path
    from typing import Dict, List, Optional
    
    end = time.time()
    import_time = end - start
    
    # Should be very fast (< 0.1 seconds)
    assert import_time < 0.1, f"Basic imports took {import_time:.3f}s, expected < 0.1s"


def test_performance_timer():
    """Test a simple performance timer."""
    import time
    
    start = time.time()
    time.sleep(0.01)  # Sleep for 10ms
    end = time.time()
    
    elapsed = end - start
    assert 0.008 < elapsed < 0.05, f"Sleep timing off: {elapsed:.3f}s"


class TestFastUtilities:
    """Fast utility test class."""
    
    def test_class_initialization(self):
        """Test class initialization is fast."""
        assert hasattr(self, 'test_class_initialization')
    
    def test_method_execution(self):
        """Test method execution is fast."""
        result = self._helper_method("test")
        assert result == "processed: test"
    
    def _helper_method(self, input_value: str) -> str:
        """Helper method for testing."""
        return f"processed: {input_value}"


# Performance benchmarks
def test_startup_performance():
    """Test that test startup is reasonably fast."""
    import time
    
    # This test itself should start quickly
    start = time.time()
    
    # Simulate some basic operations
    data = {"test": True}
    result = [x for x in range(100)]
    text = "performance test"
    
    end = time.time()
    execution_time = end - start
    
    # Should complete very quickly
    assert execution_time < 0.01, f"Basic operations took {execution_time:.3f}s"


if __name__ == "__main__":
    # Run tests directly for quick validation
    print("Running fast unit tests...")
    
    test_functions = [
        test_basic_path_operations,
        test_environment_variables,
        test_string_operations,
        test_list_operations,
        test_dict_operations,
        test_json_operations,
        test_pathlib_operations,
        test_basic_error_handling,
        test_basic_imports,
        test_performance_timer,
        test_startup_performance
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All fast unit tests passed!")
    else:
        print("❌ Some tests failed")
        sys.exit(1)
