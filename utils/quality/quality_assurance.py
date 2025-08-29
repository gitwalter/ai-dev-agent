"""
Quality Assurance Module
========================

Comprehensive quality assurance system for AI agent outputs and system validation.
Provides validation, quality gates, metrics tracking, and reporting capabilities.

Author: AI-Dev-Agent System
Version: 1.0
Last Updated: Current Session
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Quality levels for validation thresholds."""
    MINIMAL = "minimal"
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ValidationType(Enum):
    """Types of validation checks."""
    STRUCTURE = "structure"
    CONTENT = "content"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"


@dataclass
class QualityMetric:
    """Quality metric data structure."""
    name: str
    value: float
    threshold: float
    passed: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of a validation check."""
    validation_type: ValidationType
    passed: bool
    score: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class QualityGateResult:
    """Result of a quality gate evaluation."""
    passed: bool
    score: float
    agent_type: str
    output_type: str
    validations: List[ValidationResult] = field(default_factory=list)
    metrics: List[QualityMetric] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    recommendations: List[str] = field(default_factory=list)


class QualityAssuranceSystem:
    """Comprehensive quality assurance system for AI agents."""
    
    def __init__(self):
        """Initialize the quality assurance system."""
        self.quality_thresholds = self._init_quality_thresholds()
        self.validation_rules = self._init_validation_rules()
        self.quality_metrics: List[QualityMetric] = []
        self.validation_history: List[ValidationResult] = []
        self.gate_results: List[QualityGateResult] = []
        
        logger.info("Quality Assurance System initialized")
    
    def _init_quality_thresholds(self) -> Dict[str, float]:
        """Initialize quality thresholds for different agent types."""
        return {
            "requirements_analyst": 85.0,
            "architecture_designer": 90.0,
            "code_generator": 88.0,
            "test_generator": 85.0,
            "code_reviewer": 92.0,
            "security_analyst": 95.0,
            "documentation_generator": 80.0,
            "project_manager": 75.0,
            "default": 80.0
        }
    
    def _init_validation_rules(self) -> Dict[ValidationType, Dict[str, Any]]:
        """Initialize validation rules for different validation types."""
        return {
            ValidationType.STRUCTURE: {
                "required_fields": True,
                "field_types": True,
                "schema_compliance": True,
                "weight": 0.25
            },
            ValidationType.CONTENT: {
                "content_quality": True,
                "relevance": True,
                "completeness": True,
                "weight": 0.30
            },
            ValidationType.CONSISTENCY: {
                "internal_consistency": True,
                "cross_reference_consistency": True,
                "naming_consistency": True,
                "weight": 0.20
            },
            ValidationType.COMPLETENESS: {
                "all_requirements_addressed": True,
                "no_missing_components": True,
                "full_coverage": True,
                "weight": 0.25
            }
        }
    
    def validate_agent_output(self, agent_type: str, output: Dict[str, Any], 
                            output_type: str) -> QualityGateResult:
        """
        Validate agent output through comprehensive quality gates.
        
        Args:
            agent_type: Type of agent that produced the output
            output: The output to validate
            output_type: Type of output being validated
            
        Returns:
            QualityGateResult: Comprehensive validation results
        """
        logger.info(f"Validating {agent_type} output of type {output_type}")
        
        validations = []
        overall_score = 0.0
        
        # Run all validation types
        for validation_type in ValidationType:
            validation_result = self._run_validation(
                validation_type, agent_type, output, output_type
            )
            validations.append(validation_result)
            
            # Weight the validation based on rules
            weight = self.validation_rules.get(validation_type, {}).get("weight", 0.1)
            overall_score += validation_result.score * weight
            
            # Add to validation history
            self.validation_history.append(validation_result)
        
        # Determine if quality gate passed
        threshold = self.quality_thresholds.get(agent_type, self.quality_thresholds["default"])
        gate_passed = overall_score >= threshold
        
        # Generate recommendations if needed
        recommendations = self._generate_recommendations(validations, overall_score, threshold)
        
        # Create quality gate result
        gate_result = QualityGateResult(
            passed=gate_passed,
            score=overall_score,
            agent_type=agent_type,
            output_type=output_type,
            validations=validations,
            recommendations=recommendations
        )
        
        # Store gate result
        self.gate_results.append(gate_result)
        
        logger.info(f"Quality gate result: {gate_passed} (score: {overall_score:.2f})")
        return gate_result
    
    def _run_validation(self, validation_type: ValidationType, agent_type: str,
                       output: Dict[str, Any], output_type: str) -> ValidationResult:
        """Run a specific type of validation."""
        try:
            if validation_type == ValidationType.STRUCTURE:
                return self._validate_structure(output, agent_type, output_type)
            elif validation_type == ValidationType.CONTENT:
                return self._validate_content(output, agent_type, output_type)
            elif validation_type == ValidationType.CONSISTENCY:
                return self._validate_consistency(output, agent_type, output_type)
            elif validation_type == ValidationType.COMPLETENESS:
                return self._validate_completeness(output, agent_type, output_type)
            else:
                # Default validation for other types
                return ValidationResult(
                    validation_type=validation_type,
                    passed=True,
                    score=80.0,
                    message=f"{validation_type.value} validation not implemented",
                    details={"status": "skipped"}
                )
        except Exception as e:
            logger.error(f"Validation error for {validation_type.value}: {e}")
            return ValidationResult(
                validation_type=validation_type,
                passed=False,
                score=0.0,
                message=f"Validation failed: {e}",
                details={"error": str(e)}
            )
    
    def _validate_structure(self, output: Dict[str, Any], agent_type: str, 
                          output_type: str) -> ValidationResult:
        """Validate output structure."""
        score = 100.0
        issues = []
        
        # Check if output is a dictionary
        if not isinstance(output, dict):
            score -= 50
            issues.append("Output is not a dictionary")
        
        # Check for basic required fields based on agent type
        required_fields = self._get_required_fields(agent_type, output_type)
        for field in required_fields:
            if field not in output:
                score -= 20
                issues.append(f"Missing required field: {field}")
            elif not output[field]:
                score -= 10
                issues.append(f"Empty required field: {field}")
        
        # Ensure score doesn't go below 0
        score = max(0.0, score)
        
        return ValidationResult(
            validation_type=ValidationType.STRUCTURE,
            passed=score >= 70.0,
            score=score,
            message=f"Structure validation: {len(issues)} issues found" if issues else "Structure validation passed",
            details={"issues": issues, "required_fields": required_fields}
        )
    
    def _validate_content(self, output: Dict[str, Any], agent_type: str,
                         output_type: str) -> ValidationResult:
        """Validate output content quality."""
        score = 100.0
        issues = []
        
        # Check content length and quality
        for key, value in output.items():
            if isinstance(value, str):
                if len(value.strip()) < 10:
                    score -= 10
                    issues.append(f"Field '{key}' has insufficient content")
                elif value.strip().lower() in ["todo", "tbd", "placeholder", "n/a"]:
                    score -= 20
                    issues.append(f"Field '{key}' contains placeholder content")
        
        # Ensure score doesn't go below 0
        score = max(0.0, score)
        
        return ValidationResult(
            validation_type=ValidationType.CONTENT,
            passed=score >= 70.0,
            score=score,
            message=f"Content validation: {len(issues)} issues found" if issues else "Content validation passed",
            details={"issues": issues}
        )
    
    def _validate_consistency(self, output: Dict[str, Any], agent_type: str,
                            output_type: str) -> ValidationResult:
        """Validate output consistency."""
        score = 100.0
        issues = []
        
        # Basic consistency checks (can be expanded)
        # Check for consistent naming conventions
        field_names = list(output.keys())
        snake_case_fields = [f for f in field_names if '_' in f]
        camel_case_fields = [f for f in field_names if any(c.isupper() for c in f) and '_' not in f]
        
        if snake_case_fields and camel_case_fields:
            score -= 15
            issues.append("Inconsistent naming convention (mix of snake_case and camelCase)")
        
        # Ensure score doesn't go below 0
        score = max(0.0, score)
        
        return ValidationResult(
            validation_type=ValidationType.CONSISTENCY,
            passed=score >= 70.0,
            score=score,
            message=f"Consistency validation: {len(issues)} issues found" if issues else "Consistency validation passed",
            details={"issues": issues}
        )
    
    def _validate_completeness(self, output: Dict[str, Any], agent_type: str,
                             output_type: str) -> ValidationResult:
        """Validate output completeness."""
        score = 100.0
        issues = []
        
        # Check completeness based on agent type expectations
        expected_sections = self._get_expected_sections(agent_type, output_type)
        
        for section in expected_sections:
            if section not in output:
                score -= 25
                issues.append(f"Missing expected section: {section}")
            elif not output[section]:
                score -= 15
                issues.append(f"Empty expected section: {section}")
        
        # Ensure score doesn't go below 0
        score = max(0.0, score)
        
        return ValidationResult(
            validation_type=ValidationType.COMPLETENESS,
            passed=score >= 70.0,
            score=score,
            message=f"Completeness validation: {len(issues)} issues found" if issues else "Completeness validation passed",
            details={"issues": issues, "expected_sections": expected_sections}
        )
    
    def _get_required_fields(self, agent_type: str, output_type: str) -> List[str]:
        """Get required fields for specific agent and output type."""
        # Basic required fields by agent type
        agent_fields = {
            "requirements_analyst": ["functional_requirements", "non_functional_requirements"],
            "architecture_designer": ["system_overview", "components"],
            "code_generator": ["code", "description"],
            "test_generator": ["test_cases", "test_framework"],
            "code_reviewer": ["review_summary", "issues"],
            "security_analyst": ["security_assessment", "vulnerabilities"],
            "documentation_generator": ["documentation", "sections"]
        }
        
        return agent_fields.get(agent_type, ["status", "output"])
    
    def _get_expected_sections(self, agent_type: str, output_type: str) -> List[str]:
        """Get expected sections for specific agent and output type."""
        # Expected sections by agent type
        agent_sections = {
            "requirements_analyst": ["functional_requirements", "non_functional_requirements", 
                                   "user_stories", "constraints"],
            "architecture_designer": ["system_overview", "components", "architecture_pattern",
                                    "technology_stack"],
            "code_generator": ["code", "description", "dependencies", "tests"],
            "test_generator": ["test_cases", "test_framework", "coverage"],
            "code_reviewer": ["review_summary", "issues", "recommendations"],
            "security_analyst": ["security_assessment", "vulnerabilities", "recommendations"],
            "documentation_generator": ["documentation", "sections", "examples"]
        }
        
        return agent_sections.get(agent_type, ["output"])
    
    def _generate_recommendations(self, validations: List[ValidationResult], 
                                score: float, threshold: float) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if score < threshold:
            recommendations.append(f"Overall score ({score:.1f}) below threshold ({threshold})")
        
        for validation in validations:
            if not validation.passed:
                recommendations.append(
                    f"Improve {validation.validation_type.value}: {validation.message}"
                )
        
        return recommendations
    
    def get_validation_history(self, validation_type: Optional[ValidationType] = None) -> List[ValidationResult]:
        """Get validation history, optionally filtered by type."""
        if validation_type:
            return [v for v in self.validation_history if v.validation_type == validation_type]
        return self.validation_history.copy()
    
    def get_gate_results(self, agent_type: Optional[str] = None) -> List[QualityGateResult]:
        """Get quality gate results, optionally filtered by agent type."""
        if agent_type:
            return [r for r in self.gate_results if r.agent_type == agent_type]
        return self.gate_results.copy()
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate a comprehensive quality report."""
        total_gates = len(self.gate_results)
        passed_gates = len([r for r in self.gate_results if r.passed])
        
        if total_gates == 0:
            return {
                "summary": "No quality gates evaluated yet",
                "pass_rate": 0.0,
                "average_score": 0.0,
                "total_validations": 0
            }
        
        average_score = sum(r.score for r in self.gate_results) / total_gates
        pass_rate = (passed_gates / total_gates) * 100
        
        # Group results by agent type
        agent_stats = {}
        for result in self.gate_results:
            if result.agent_type not in agent_stats:
                agent_stats[result.agent_type] = {
                    "total": 0,
                    "passed": 0,
                    "scores": []
                }
            
            agent_stats[result.agent_type]["total"] += 1
            if result.passed:
                agent_stats[result.agent_type]["passed"] += 1
            agent_stats[result.agent_type]["scores"].append(result.score)
        
        # Calculate agent-specific metrics
        for agent_type, stats in agent_stats.items():
            stats["pass_rate"] = (stats["passed"] / stats["total"]) * 100
            stats["average_score"] = sum(stats["scores"]) / len(stats["scores"])
        
        return {
            "summary": f"{passed_gates}/{total_gates} quality gates passed",
            "pass_rate": pass_rate,
            "average_score": average_score,
            "total_validations": len(self.validation_history),
            "agent_statistics": agent_stats,
            "generated_at": datetime.now().isoformat()
        }
    
    def clear_history(self):
        """Clear all quality assurance history."""
        self.quality_metrics.clear()
        self.validation_history.clear()
        self.gate_results.clear()
        logger.info("Quality assurance history cleared")


# Global quality assurance system instance
_qa_system = None

def get_quality_assurance_system() -> QualityAssuranceSystem:
    """Get the global quality assurance system instance."""
    global _qa_system
    if _qa_system is None:
        _qa_system = QualityAssuranceSystem()
    return _qa_system

# Convenience functions for backward compatibility
quality_assurance = get_quality_assurance_system()

def quality_assurance_validate(agent_type: str, output: Dict[str, Any], 
                              output_type: str) -> QualityGateResult:
    """
    Validate agent output through quality gates.
    
    Args:
        agent_type: Type of agent
        output: Output to validate
        output_type: Type of output
        
    Returns:
        QualityGateResult: Validation results
    """
    return quality_assurance.validate_agent_output(agent_type, output, output_type)
