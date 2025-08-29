"""
Quality Assurance Package
=========================

Provides comprehensive quality assurance utilities for AI agent validation.

Modules:
- quality_assurance: Core quality assurance system

Author: AI-Dev-Agent System  
Version: 1.0
"""

from .quality_assurance import (
    QualityAssuranceSystem,
    QualityLevel,
    ValidationType,
    QualityMetric,
    ValidationResult,
    QualityGateResult,
    quality_assurance,
    quality_assurance_validate,
    get_quality_assurance_system
)

from .performance_optimizer import (
    PerformanceOptimizer,
    PerformanceMetrics,
    get_performance_optimizer,
    record_agent_performance,
    get_agent_performance_stats,
    get_performance_recommendations
)

__all__ = [
    "QualityAssuranceSystem",
    "QualityLevel", 
    "ValidationType",
    "QualityMetric",
    "ValidationResult",
    "QualityGateResult",
    "quality_assurance",
    "quality_assurance_validate",
    "get_quality_assurance_system",
    "PerformanceOptimizer",
    "PerformanceMetrics",
    "get_performance_optimizer",
    "record_agent_performance",
    "get_agent_performance_stats",
    "get_performance_recommendations"
]
