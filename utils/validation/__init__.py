"""
🛡️ Validation System - Systematic Excellence Enforcement

This module provides comprehensive validation capabilities for:
- Mathematical system foundations
- Formal system compliance
- Universal naming validation
- Self-healing validation processes

Core Philosophy: Validation serves excellence, not bureaucracy.
"""

from .mathematical_system_foundation import (
    MathematicalSystemFoundation,
    Operation,
    LayerIndex,
    MathematicalValidationResult,
    DivineMathematicalConstants,
    DivineConstantValidator,
    ScientificMethodValidator,
    EthicalMathematicsValidator,
    HarmonicIntegrationValidator,
    FormalVerificationSystem
)

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
    # Mathematical System Foundation
    'MathematicalSystemFoundation',
    'Operation',
    'LayerIndex', 
    'MathematicalValidationResult',
    'DivineMathematicalConstants',
    'DivineConstantValidator',
    'ScientificMethodValidator',
    'EthicalMathematicsValidator',
    'HarmonicIntegrationValidator',
    'FormalVerificationSystem',
    
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
