"""
Test Configuration Package

Provides centralized configuration management for test execution modes.
"""

from .test_config import (
    ConfigMode as TestMode,
    Config as TestConfig,
    ConfigManager as TestConfigManager,
    get_test_config,
    set_test_config,
    is_mock_mode,
    is_real_mode,
    force_mock_mode,
    force_real_mode,
    get_mode_info,
    pytest_configure,
    pytest_addoption,
    pytest_collection_modifyitems
)

__all__ = [
    "TestMode",
    "TestConfig", 
    "TestConfigManager",
    "get_test_config",
    "set_test_config",
    "is_mock_mode",
    "is_real_mode",
    "force_mock_mode",
    "force_real_mode",
    "get_mode_info",
    "pytest_configure",
    "pytest_addoption",
    "pytest_collection_modifyitems"
]
