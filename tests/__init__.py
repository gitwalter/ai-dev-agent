"""
Test package for AI Development Agent.
Contains all test modules and utilities for testing the system.
"""

__version__ = "1.0.0"
__author__ = "AI Development Agent Team"

# Import common test utilities
from .unit.test_utils import *

# Test categories
TEST_CATEGORIES = {
    "unit": "Unit tests for individual components",
    "integration": "Integration tests for component interactions", 
    "system": "System-wide tests",
    "performance": "Performance and load tests",
    "security": "Security and vulnerability tests"
}
