"""
🛡️ Validation System - Practical Excellence Enforcement

This module provides practical validation capabilities for:
- Formal system compliance  
- Universal naming validation
- Self-healing validation processes

Core Philosophy: Validation serves excellence, not bureaucracy.
"""

from .formal_system_detector import (
    FormalSystemDetector,
    ValidationLevel,
    RuleCategory,
    ValidationIssue,
    FileAnalysisResult,
    SystemComplianceReport,
    create_formal_system_detector,
    quick_file_check,
    quick_system_check
)

from .universal_naming_validator import (
    UniversalNamingValidator,
    ValidationResult
)

from .self_healing_naming_validator import (
    SelfHealingNamingValidator,
    NamingViolation,
    ValidationReport,
    NamingConventionPatterns
)

__all__ = [
    # Formal System Detector
    'FormalSystemDetector',
    'ValidationLevel',
    'RuleCategory',
    'ValidationIssue',
    'FileAnalysisResult',
    'SystemComplianceReport',
    'create_formal_system_detector',
    'quick_file_check',
    'quick_system_check',
    
    # Universal Naming Validator
    'UniversalNamingValidator',
    'ValidationResult',
    
    # Self-Healing Naming Validator
    'SelfHealingNamingValidator',
    'NamingViolation',
    'ValidationReport',
    'NamingConventionPatterns'
]
