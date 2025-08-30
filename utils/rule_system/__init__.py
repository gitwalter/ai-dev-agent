"""
Formal Rule System - Self-Optimizing Automated Rule Application

This package provides a formal, self-optimizing rule system for systematic
development excellence with continuous learning and automated optimization.
"""

from .formal_rule_catalog import (
    FormalRule,
    RulePriority,
    RuleScope,
    RuleCategory,
    FormalRuleCatalog,
    RuleApplicationEngine,
    apply_formal_rule_system,
    FORMAL_RULES
)

from .intelligent_rule_optimizer import (
    IntelligentRuleOptimizer,
    TaskComplexity,
    ContextProfile,
    RuleOptimization
)

# Optional components - may not exist yet
try:
    from .self_optimizing_engine import (
        SelfOptimizingRuleEngine,
        AutomatedOptimizationController,
        ContinuousLearningSystem
    )
except ImportError:
    # Self-optimization components optional
    SelfOptimizingRuleEngine = None
    AutomatedOptimizationController = None
    ContinuousLearningSystem = None

__all__ = [
    # Core formal system
    "FormalRule",
    "RulePriority", 
    "RuleScope",
    "RuleCategory",
    "FormalRuleCatalog",
    "RuleApplicationEngine",
    "apply_formal_rule_system",
    "FORMAL_RULES",
    
    # Intelligent optimization
    "IntelligentRuleOptimizer",
    "TaskComplexity",
    "ContextProfile", 
    "RuleOptimization",
    
    # Self-optimization
    "SelfOptimizingRuleEngine",
    "AutomatedOptimizationController",
    "ContinuousLearningSystem"
]

# Package version
__version__ = "1.0.0"

# Package description
__description__ = "Formal Rule System with Self-Optimizing Automation"
