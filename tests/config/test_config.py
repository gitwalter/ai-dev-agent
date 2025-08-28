#!/usr/bin/env python3
"""
Test Configuration System for Configurable Test Execution

Provides centralized configuration management for running tests in different modes:
- MOCK: Fast execution with mocked LLM responses  
- REAL: Full integration testing with actual LLM API calls

Support for:
- Environment variable configuration (TEST_MODE)
- Pytest command-line options (--test-mode)
- Programmatic configuration
- Validation and error handling
"""

import os
import logging
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class TestMode(Enum):
    """Test execution modes."""
    MOCK = "mock"
    REAL = "real"


@dataclass
class TestConfig:
    """Configuration for test execution."""
    mode: TestMode
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    log_level: str = "INFO"
    performance_tracking: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate configuration settings."""
        if self.mode == TestMode.REAL and not self.api_key:
            raise ValueError("API key required for REAL test mode")
        
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")


class TestConfigManager:
    """Manages test configuration from multiple sources."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._config: Optional[TestConfig] = None
    
    def get_config(self) -> TestConfig:
        """Get current test configuration, creating if necessary."""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def set_config(self, config: TestConfig) -> None:
        """Set test configuration programmatically."""
        config.validate()
        self._config = config
        self.logger.info(f"Test configuration set to {config.mode.value} mode")
    
    def _load_config(self) -> TestConfig:
        """Load configuration from environment and defaults."""
        # Get test mode from environment
        mode_str = os.getenv("TEST_MODE", "mock").lower()
        
        try:
            mode = TestMode(mode_str)
        except ValueError:
            self.logger.warning(f"Invalid TEST_MODE '{mode_str}', defaulting to MOCK")
            mode = TestMode.MOCK
        
        # Get API key if needed
        api_key = None
        if mode == TestMode.REAL:
            api_key = self._get_api_key()
            if not api_key:
                self.logger.warning("No API key found, falling back to MOCK mode")
                mode = TestMode.MOCK
        
        # Get other configuration
        timeout = int(os.getenv("TEST_TIMEOUT", "30"))
        max_retries = int(os.getenv("TEST_MAX_RETRIES", "3"))
        log_level = os.getenv("TEST_LOG_LEVEL", "INFO")
        performance_tracking = os.getenv("TEST_PERFORMANCE_TRACKING", "true").lower() == "true"
        
        config = TestConfig(
            mode=mode,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            log_level=log_level,
            performance_tracking=performance_tracking
        )
        
        self.logger.info(f"Loaded test configuration: {config.mode.value} mode")
        return config
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from various sources."""
        # Try environment variable first
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "your-gemini-api-key-here":
            return api_key
        
        # Try Streamlit secrets
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY")
            if api_key and api_key != "your-gemini-api-key-here":
                return api_key
        except Exception:
            pass
        
        return None
    
    def force_mock_mode(self) -> None:
        """Force test configuration to MOCK mode."""
        if self._config:
            self._config.mode = TestMode.MOCK
            self._config.api_key = None
        else:
            self._config = TestConfig(mode=TestMode.MOCK)
        
        self.logger.info("Forced test configuration to MOCK mode")
    
    def force_real_mode(self, api_key: str) -> None:
        """Force test configuration to REAL mode with provided API key."""
        if not api_key:
            raise ValueError("API key required for REAL mode")
        
        self._config = TestConfig(mode=TestMode.REAL, api_key=api_key)
        self.logger.info("Forced test configuration to REAL mode")
    
    def is_mock_mode(self) -> bool:
        """Check if currently in MOCK mode."""
        return self.get_config().mode == TestMode.MOCK
    
    def is_real_mode(self) -> bool:
        """Check if currently in REAL mode."""
        return self.get_config().mode == TestMode.REAL
    
    def get_mode_info(self) -> Dict[str, Any]:
        """Get information about current test mode."""
        config = self.get_config()
        return {
            "mode": config.mode.value,
            "has_api_key": bool(config.api_key),
            "timeout": config.timeout,
            "max_retries": config.max_retries,
            "performance_tracking": config.performance_tracking
        }


# Global instance
_test_config_manager = TestConfigManager()


def get_test_config() -> TestConfig:
    """Get current test configuration."""
    return _test_config_manager.get_config()


def set_test_config(config: TestConfig) -> None:
    """Set test configuration."""
    _test_config_manager.set_config(config)


def is_mock_mode() -> bool:
    """Check if currently in MOCK test mode."""
    return _test_config_manager.is_mock_mode()


def is_real_mode() -> bool:
    """Check if currently in REAL test mode."""
    return _test_config_manager.is_real_mode()


def force_mock_mode() -> None:
    """Force MOCK test mode."""
    _test_config_manager.force_mock_mode()


def force_real_mode(api_key: str) -> None:
    """Force REAL test mode with API key."""
    _test_config_manager.force_real_mode(api_key)


def get_mode_info() -> Dict[str, Any]:
    """Get current mode information."""
    return _test_config_manager.get_mode_info()


# Pytest configuration helper
def pytest_configure(config):
    """Configure pytest with test mode options."""
    # Add custom markers
    config.addinivalue_line("markers", "mock_mode: mark test as mock mode only")
    config.addinivalue_line("markers", "real_mode: mark test as real mode only")
    config.addinivalue_line("markers", "dual_mode: mark test as supporting both modes")
    
    # Handle command-line test mode option
    test_mode = config.getoption("--test-mode", default=None)
    if test_mode:
        os.environ["TEST_MODE"] = test_mode
        _test_config_manager._config = None  # Force reload


def pytest_addoption(parser):
    """Add pytest command-line options."""
    parser.addoption(
        "--test-mode",
        action="store",
        default=None,
        help="Test execution mode: mock or real"
    )
    parser.addoption(
        "--force-api-key",
        action="store",
        default=None,
        help="Force specific API key for real mode testing"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on current mode."""
    current_mode = get_test_config().mode
    
    for item in items:
        # Skip real-mode-only tests in mock mode
        if current_mode == TestMode.MOCK and item.get_closest_marker("real_mode"):
            item.add_marker("skip(reason='Real mode test skipped in mock mode')")
        
        # Skip mock-mode-only tests in real mode  
        if current_mode == TestMode.REAL and item.get_closest_marker("mock_mode"):
            item.add_marker("skip(reason='Mock mode test skipped in real mode')")


if __name__ == "__main__":
    # Demo/test the configuration system
    print("🔧 Test Configuration System Demo")
    print("=" * 40)
    
    # Show current configuration
    config = get_test_config()
    print(f"Current mode: {config.mode.value}")
    print(f"Has API key: {bool(config.api_key)}")
    print(f"Mode info: {get_mode_info()}")
    
    # Test mode switching
    print("\n🔄 Testing mode switching...")
    force_mock_mode()
    print(f"After force mock: {get_test_config().mode.value}")
    
    try:
        force_real_mode("test-key")
        print(f"After force real: {get_test_config().mode.value}")
    except Exception as e:
        print(f"Force real failed: {e}")
    
    print("\n✅ Configuration system demo complete")
