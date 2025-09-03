"""
🌍 Cross-Platform Operations System

Provides systematic cross-platform compatibility for all system operations.
Ensures code works reliably on Windows, Linux, and macOS without modification.

Core Philosophy: "Detect and adapt, never assume."
"""

from .cross_platform_operations import (
    CrossPlatformOperations,
    CrossPlatformCommands,
    CrossPlatformPaths,
    CrossPlatformAgent
)

from .cross_platform_validator import (
    CrossPlatformValidator,
    validate_cross_platform_compliance,
    ComplianceError
)

__all__ = [
    'CrossPlatformOperations',
    'CrossPlatformCommands', 
    'CrossPlatformPaths',
    'CrossPlatformAgent',
    'CrossPlatformValidator',
    'validate_cross_platform_compliance',
    'ComplianceError'
]
