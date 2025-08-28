#!/usr/bin/env python3
"""
LLM Fixtures for Configurable Testing

Provides pytest fixtures that automatically select appropriate LLM provider
based on test configuration mode (MOCK/REAL).
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock

from tests.config.test_config import get_test_config, TestMode, is_mock_mode, is_real_mode
from tests.providers.llm_provider import LLMProviderFactory, LLMProvider


@pytest.fixture
def test_mode_info():
    """Fixture providing current test mode information."""
    config = get_test_config()
    return {
        "mode": config.mode.value,
        "is_mock": is_mock_mode(),
        "is_real": is_real_mode(),
        "has_api_key": bool(config.api_key),
        "timeout": config.timeout,
        "max_retries": config.max_retries
    }


@pytest.fixture
def llm_provider():
    """Fixture providing appropriate LLM provider based on test mode."""
    return LLMProviderFactory.create_provider()


@pytest.fixture
async def async_llm_provider():
    """Async fixture providing LLM provider."""
    provider = LLMProviderFactory.create_provider()
    yield provider
    # Cleanup if needed
    provider.clear_performance_metrics()


@pytest.fixture
def mock_llm_provider():
    """Fixture providing mock LLM provider explicitly."""
    return LLMProviderFactory.create_mock_provider()


@pytest.fixture
def mock_llm():
    """Fixture providing mock LLM for backward compatibility with existing tests."""
    if is_mock_mode():
        # Return mock LLM provider wrapped as legacy mock
        provider = LLMProviderFactory.create_mock_provider()
        
        # Create mock that delegates to provider
        mock = Mock()
        mock.ainvoke = AsyncMock()
        
        async def mock_invoke(prompt):
            response = await provider.generate_response(prompt)
            # Return mock response object
            mock_response = Mock()
            mock_response.content = response.content
            return mock_response
        
        mock.ainvoke.side_effect = mock_invoke
        mock.invoke = Mock()
        
        def sync_invoke(prompt):
            # For sync calls, run async version
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(mock_invoke(prompt))
                return result
            finally:
                loop.close()
        
        mock.invoke.side_effect = sync_invoke
        return mock
    else:
        # Real mode - return actual LangChain LLM
        config = get_test_config()
        if not config.api_key:
            pytest.skip("No API key available for real LLM testing")
        
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                google_api_key=config.api_key,
                temperature=0.1,
                max_tokens=2048
            )
        except ImportError:
            pytest.skip("LangChain not available for real LLM testing")


@pytest.fixture
def llm_config():
    """Fixture providing LLM configuration for current test mode."""
    config = get_test_config()
    
    if config.mode == TestMode.MOCK:
        return {
            "provider": "mock",
            "response_delay": 0.05,  # Faster for testing
            "model": "mock-model"
        }
    else:
        return {
            "provider": "real",
            "api_key": config.api_key,
            "model": "gemini-2.5-flash-lite",
            "temperature": 0.1,
            "max_tokens": 2048,
            "timeout": config.timeout,
            "max_retries": config.max_retries
        }


@pytest.fixture
def performance_tracker():
    """Fixture for tracking test performance across modes."""
    
    class PerformanceTracker:
        def __init__(self):
            self.metrics = []
        
        def start_timer(self, operation: str):
            import time
            return time.time()
        
        def end_timer(self, operation: str, start_time: float, **metadata):
            import time
            execution_time = time.time() - start_time
            
            self.metrics.append({
                "operation": operation,
                "execution_time": execution_time,
                "mode": get_test_config().mode.value,
                "timestamp": time.time(),
                **metadata
            })
            
            return execution_time
        
        def get_metrics(self):
            return self.metrics.copy()
        
        def get_total_time(self):
            return sum(m["execution_time"] for m in self.metrics)
        
        def get_avg_time(self):
            if not self.metrics:
                return 0
            return self.get_total_time() / len(self.metrics)
    
    return PerformanceTracker()


@pytest.fixture
def mode_validator():
    """Fixture for validating test behavior in different modes."""
    
    class ModeValidator:
        def __init__(self):
            self.config = get_test_config()
        
        def validate_mock_response(self, response):
            """Validate mock response meets expectations."""
            if not is_mock_mode():
                return True  # Skip validation in real mode
            
            # Check response structure
            assert response is not None, "Mock response should not be None"
            assert hasattr(response, 'content'), "Mock response should have content"
            assert len(response.content) > 0, "Mock response content should not be empty"
            
            return True
        
        def validate_real_response(self, response):
            """Validate real response meets expectations."""
            if not is_real_mode():
                return True  # Skip validation in mock mode
            
            # Check response structure
            assert response is not None, "Real response should not be None"
            assert hasattr(response, 'content'), "Real response should have content"
            assert len(response.content) > 0, "Real response content should not be empty"
            
            # Additional real mode validations
            assert len(response.content) > 10, "Real response should be substantial"
            
            return True
        
        def validate_response(self, response):
            """Validate response based on current mode."""
            if is_mock_mode():
                return self.validate_mock_response(response)
            else:
                return self.validate_real_response(response)
        
        def assert_fast_execution(self, execution_time: float, max_time: float = 1.0):
            """Assert execution was fast (for mock mode)."""
            if is_mock_mode():
                assert execution_time < max_time, f"Mock execution too slow: {execution_time:.2f}s > {max_time}s"
        
        def assert_reasonable_execution(self, execution_time: float, max_time: float = 30.0):
            """Assert execution was reasonable (for real mode)."""
            if is_real_mode():
                assert execution_time < max_time, f"Real execution too slow: {execution_time:.2f}s > {max_time}s"
    
    return ModeValidator()


@pytest.fixture(autouse=True)
def mode_marker(request):
    """Auto-use fixture that handles mode-specific test markers."""
    config = get_test_config()
    
    # Check for mode-specific markers
    if request.node.get_closest_marker("mock_only") and config.mode != TestMode.MOCK:
        pytest.skip("Test marked as mock-only but running in real mode")
    
    if request.node.get_closest_marker("real_only") and config.mode != TestMode.REAL:
        pytest.skip("Test marked as real-only but running in mock mode")
    
    # Log test start with mode info
    print(f"🧪 Running test in {config.mode.value} mode")


# Backward compatibility fixtures for existing tests
@pytest.fixture
def workflow_manager():
    """Backward compatibility fixture for workflow manager."""
    from tests.mocks.workflow.langgraph_workflow_manager import LangGraphWorkflowManager
    return LangGraphWorkflowManager()


@pytest.fixture
def test_state():
    """Backward compatibility fixture for test state."""
    return {
        "project_context": "Test project context",
        "agent_outputs": {},
        "requirements": [],
        "architecture": {},
        "code_files": {},
        "tests": {},
        "documentation": {},
        "execution_history": [],
        "errors": [],
        "warnings": [],
        "approval_requests": []
    }


# Test mode performance benchmarks
@pytest.fixture
def performance_benchmarks():
    """Fixture providing performance benchmarks for different modes."""
    return {
        "mock_mode": {
            "max_total_time": 10.0,  # 10 seconds max for all mock tests
            "max_single_test": 2.0,  # 2 seconds max per mock test
            "expected_avg": 0.5      # Expected average time per mock test
        },
        "real_mode": {
            "max_total_time": 300.0,  # 5 minutes max for all real tests
            "max_single_test": 60.0,  # 1 minute max per real test  
            "expected_avg": 10.0      # Expected average time per real test
        }
    }
