"""
Quality Assurance System for AI Development Agent.
Provides comprehensive quality validation, metrics, and monitoring.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import re

from models.state import AgentState
from models.responses import AgentResponse


class QualityLevel(Enum):
    """Quality levels for validation."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValidationType(Enum):
    """Types of validation."""
    STRUCTURE = "structure"
    CONTENT = "content"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class QualityMetric:
    """Quality metric for tracking agent performance."""
    agent_name: str
    metric_name: str
    value: float
    threshold: float
    passed: bool
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of a validation check."""
    validation_type: ValidationType
    passed: bool
    score: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityGateResult:
    """Result of a quality gate check."""
    gate_name: str
    passed: bool
    score: float
    threshold: float
    validations: List[ValidationResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class QualityAssuranceSystem:
    """
    Comprehensive quality assurance system for AI Development Agent.
    
    Provides:
    - Quality gates for each agent
    - Output validation and consistency checks
    - Quality metrics and monitoring
    - Comprehensive testing capabilities
    """
    
    def __init__(self):
        """Initialize the quality assurance system."""
        self.logger = logging.getLogger(__name__)
        
        # Quality thresholds for different agents
        self.quality_thresholds = {
            "requirements_analyst": 8.0,
            "architecture_designer": 8.5,
            "code_generator": 8.0,
            "test_generator": 7.5,
            "code_reviewer": 8.5,
            "security_analyst": 9.0,
            "documentation_generator": 7.5,
            "project_manager": 8.0
        }
        
        # Validation rules for different output types
        self.validation_rules = {
            "requirements": self._validate_requirements_output,
            "architecture": self._validate_architecture_output,
            "code": self._validate_code_output,
            "tests": self._validate_test_output,
            "review": self._validate_review_output,
            "security": self._validate_security_output,
            "documentation": self._validate_documentation_output
        }
        
        # Quality metrics storage
        self.quality_metrics: List[QualityMetric] = []
        self.validation_history: List[ValidationResult] = []
        self.gate_results: List[QualityGateResult] = []
    
    def validate_agent_output(self, agent_name: str, output: Dict[str, Any], 
                            output_type: str) -> QualityGateResult:
        """
        Validate agent output against quality standards.
        
        Args:
            agent_name: Name of the agent
            output: Agent output to validate
            output_type: Type of output (requirements, code, etc.)
            
        Returns:
            QualityGateResult with validation results
        """
        self.logger.info(f"Validating {agent_name} output (type: {output_type})")
        
        # Get quality threshold for this agent
        threshold = self.quality_thresholds.get(agent_name, 7.0)
        
        # Perform comprehensive validation
        validations = []
        
        # 1. Structure validation
        structure_validation = self._validate_output_structure(output, output_type)
        validations.append(structure_validation)
        
        # 2. Content validation
        content_validation = self._validate_output_content(output, output_type)
        validations.append(content_validation)
        
        # 3. Consistency validation
        consistency_validation = self._validate_output_consistency(output, output_type)
        validations.append(consistency_validation)
        
        # 4. Completeness validation
        completeness_validation = self._validate_output_completeness(output, output_type)
        validations.append(completeness_validation)
        
        # 5. Type-specific validation
        if output_type in self.validation_rules:
            type_validation = self.validation_rules[output_type](output)
            validations.append(type_validation)
        
        # Calculate overall score
        scores = [v.score for v in validations if v.score is not None]
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Determine if quality gate passed
        passed = overall_score >= threshold and all(v.passed for v in validations)
        
        # Create quality gate result
        gate_result = QualityGateResult(
            gate_name=f"{agent_name}_quality_gate",
            passed=passed,
            score=overall_score,
            threshold=threshold,
            validations=validations
        )
        
        # Store results
        self.gate_results.append(gate_result)
        self.validation_history.extend(validations)
        
        # Log results
        if passed:
            self.logger.info(f"Quality gate PASSED for {agent_name}: {overall_score:.2f}/{threshold}")
        else:
            self.logger.warning(f"Quality gate FAILED for {agent_name}: {overall_score:.2f}/{threshold}")
            for validation in validations:
                if not validation.passed:
                    self.logger.warning(f"  - {validation.validation_type.value}: {validation.issues}")
        
        return gate_result
    
    def _validate_output_structure(self, output: Dict[str, Any], output_type: str) -> ValidationResult:
        """Validate output structure and format."""
        issues = []
        recommendations = []
        
        # Check if output is a dictionary
        if not isinstance(output, dict):
            issues.append("Output must be a dictionary")
            return ValidationResult(
                validation_type=ValidationType.STRUCTURE,
                passed=False,
                score=0.0,
                issues=issues,
                recommendations=recommendations
            )
        
        # Check for required fields based on output type
        required_fields = self._get_required_fields(output_type)
        missing_fields = [field for field in required_fields if field not in output]
        
        if missing_fields:
            issues.append(f"Missing required fields: {missing_fields}")
            recommendations.append(f"Add missing fields: {missing_fields}")
        
        # Check for unexpected fields
        unexpected_fields = self._get_unexpected_fields(output, output_type)
        if unexpected_fields:
            recommendations.append(f"Consider removing unexpected fields: {unexpected_fields}")
        
        # Calculate structure score
        score = 10.0
        if missing_fields:
            score -= len(missing_fields) * 2.0
        if unexpected_fields:
            score -= len(unexpected_fields) * 0.5
        
        score = max(0.0, score)
        passed = len(missing_fields) == 0
        
        return ValidationResult(
            validation_type=ValidationType.STRUCTURE,
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _validate_output_content(self, output: Dict[str, Any], output_type: str) -> ValidationResult:
        """Validate output content quality."""
        issues = []
        recommendations = []
        score = 10.0
        
        # Check for empty or null values
        empty_fields = []
        for key, value in output.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                empty_fields.append(key)
        
        if empty_fields:
            issues.append(f"Empty or null values in fields: {empty_fields}")
            score -= len(empty_fields) * 1.0
        
        # Check for meaningful content
        meaningful_content = self._check_meaningful_content(output, output_type)
        if not meaningful_content:
            issues.append("Output lacks meaningful content")
            score -= 3.0
        
        # Check for appropriate data types
        type_issues = self._check_data_types(output, output_type)
        if type_issues:
            issues.extend(type_issues)
            score -= len(type_issues) * 1.0
        
        score = max(0.0, score)
        passed = score >= 7.0
        
        return ValidationResult(
            validation_type=ValidationType.CONTENT,
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _validate_output_consistency(self, output: Dict[str, Any], output_type: str) -> ValidationResult:
        """Validate output consistency."""
        issues = []
        recommendations = []
        score = 10.0
        
        # Check for internal consistency
        consistency_issues = self._check_internal_consistency(output, output_type)
        if consistency_issues:
            issues.extend(consistency_issues)
            score -= len(consistency_issues) * 1.0
        
        # Check for naming consistency
        naming_issues = self._check_naming_consistency(output, output_type)
        if naming_issues:
            issues.extend(naming_issues)
            score -= len(naming_issues) * 0.5
        
        # Check for format consistency
        format_issues = self._check_format_consistency(output, output_type)
        if format_issues:
            issues.extend(format_issues)
            score -= len(format_issues) * 0.5
        
        score = max(0.0, score)
        passed = score >= 7.0
        
        return ValidationResult(
            validation_type=ValidationType.CONSISTENCY,
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _validate_output_completeness(self, output: Dict[str, Any], output_type: str) -> ValidationResult:
        """Validate output completeness."""
        issues = []
        recommendations = []
        score = 10.0
        
        # Check if all expected sections are present
        expected_sections = self._get_expected_sections(output_type)
        missing_sections = [section for section in expected_sections if section not in output]
        
        if missing_sections:
            issues.append(f"Missing expected sections: {missing_sections}")
            score -= len(missing_sections) * 2.0
        
        # Check for minimum content requirements
        content_issues = self._check_minimum_content(output, output_type)
        if content_issues:
            issues.extend(content_issues)
            score -= len(content_issues) * 1.0
        
        # Check for comprehensive coverage
        coverage_issues = self._check_coverage(output, output_type)
        if coverage_issues:
            issues.extend(coverage_issues)
            score -= len(coverage_issues) * 1.0
        
        score = max(0.0, score)
        passed = score >= 7.0
        
        return ValidationResult(
            validation_type=ValidationType.COMPLETENESS,
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _get_required_fields(self, output_type: str) -> List[str]:
        """Get required fields for a specific output type."""
        field_mappings = {
            "requirements": ["requirements", "summary"],
            "architecture": ["architecture", "components", "diagrams"],
            "code": ["source_files", "project_structure"],
            "tests": ["test_files", "test_strategy"],
            "review": ["overall_score", "issues", "recommendations"],
            "security": ["vulnerabilities", "security_score", "recommendations"],
            "documentation": ["documentation_files", "readme", "api_docs"]
        }
        return field_mappings.get(output_type, [])
    
    def _get_unexpected_fields(self, output: Dict[str, Any], output_type: str) -> List[str]:
        """Get unexpected fields for a specific output type."""
        expected_fields = self._get_required_fields(output_type)
        return [field for field in output.keys() if field not in expected_fields]
    
    def _check_meaningful_content(self, output: Dict[str, Any], output_type: str) -> bool:
        """Check if output has meaningful content."""
        # Check for non-empty string values
        string_values = [v for v in output.values() if isinstance(v, str)]
        if string_values:
            return any(len(v.strip()) > 10 for v in string_values)
        
        # Check for non-empty list/dict values
        complex_values = [v for v in output.values() if isinstance(v, (list, dict))]
        if complex_values:
            return any(len(v) > 0 for v in complex_values)
        
        return False
    
    def _check_data_types(self, output: Dict[str, Any], output_type: str) -> List[str]:
        """Check if data types are appropriate."""
        issues = []
        
        # Type-specific checks
        if output_type == "requirements":
            if "requirements" in output and not isinstance(output["requirements"], (list, dict)):
                issues.append("Requirements should be a list or dictionary")
        
        elif output_type == "code":
            if "source_files" in output and not isinstance(output["source_files"], dict):
                issues.append("Source files should be a dictionary")
        
        elif output_type == "review":
            if "overall_score" in output:
                try:
                    score = float(output["overall_score"])
                    if not (0 <= score <= 10):
                        issues.append("Overall score should be between 0 and 10")
                except (ValueError, TypeError):
                    issues.append("Overall score should be a number")
        
        return issues
    
    def _check_internal_consistency(self, output: Dict[str, Any], output_type: str) -> List[str]:
        """Check for internal consistency issues."""
        issues = []
        
        # Check for conflicting information
        if output_type == "code" and "source_files" in output and "project_structure" in output:
            source_files = output["source_files"]
            project_structure = output["project_structure"]
            
            # Check if all source files are mentioned in project structure
            for filename in source_files.keys():
                if filename not in str(project_structure):
                    issues.append(f"Source file {filename} not mentioned in project structure")
        
        return issues
    
    def _check_naming_consistency(self, output: Dict[str, Any], output_type: str) -> List[str]:
        """Check for naming consistency issues."""
        issues = []
        
        # Check for consistent naming patterns
        if output_type == "code" and "source_files" in output:
            filenames = list(output["source_files"].keys())
            
            # Check for consistent file extensions
            extensions = [f.split('.')[-1] for f in filenames if '.' in f]
            if len(set(extensions)) > 3:  # Too many different extensions
                issues.append("Inconsistent file extensions detected")
        
        return issues
    
    def _check_format_consistency(self, output: Dict[str, Any], output_type: str) -> List[str]:
        """Check for format consistency issues."""
        issues = []
        
        # Check for consistent formatting patterns
        if output_type == "documentation":
            # Check for consistent markdown formatting
            markdown_fields = [v for v in output.values() if isinstance(v, str)]
            for content in markdown_fields:
                if '#' in content and not content.startswith('#'):
                    issues.append("Inconsistent markdown heading format")
        
        return issues
    
    def _get_expected_sections(self, output_type: str) -> List[str]:
        """Get expected sections for a specific output type."""
        section_mappings = {
            "requirements": ["requirements", "summary", "priorities"],
            "architecture": ["architecture", "components", "diagrams", "decisions"],
            "code": ["source_files", "project_structure", "dependencies"],
            "tests": ["test_files", "test_strategy", "test_data"],
            "review": ["overall_score", "issues", "recommendations", "summary"],
            "security": ["vulnerabilities", "security_score", "recommendations", "summary"],
            "documentation": ["documentation_files", "readme", "api_docs", "setup_instructions"]
        }
        return section_mappings.get(output_type, [])
    
    def _check_minimum_content(self, output: Dict[str, Any], output_type: str) -> List[str]:
        """Check for minimum content requirements."""
        issues = []
        
        if output_type == "requirements":
            if "requirements" in output:
                reqs = output["requirements"]
                if isinstance(reqs, list) and len(reqs) < 3:
                    issues.append("Should have at least 3 requirements")
                elif isinstance(reqs, dict) and len(reqs) < 3:
                    issues.append("Should have at least 3 requirements")
        
        elif output_type == "code":
            if "source_files" in output:
                files = output["source_files"]
                if len(files) < 1:
                    issues.append("Should have at least 1 source file")
        
        elif output_type == "tests":
            if "test_files" in output:
                files = output["test_files"]
                if len(files) < 1:
                    issues.append("Should have at least 1 test file")
        
        return issues
    
    def _check_coverage(self, output: Dict[str, Any], output_type: str) -> List[str]:
        """Check for comprehensive coverage."""
        issues = []
        
        if output_type == "review":
            if "issues" in output:
                issues_list = output["issues"]
                if isinstance(issues_list, list) and len(issues_list) == 0:
                    issues.append("Review should identify at least some areas for improvement")
        
        elif output_type == "security":
            if "vulnerabilities" in output:
                vulns = output["vulnerabilities"]
                if isinstance(vulns, list) and len(vulns) == 0:
                    issues.append("Security analysis should identify potential vulnerabilities")
        
        return issues
    
    # Type-specific validation methods
    def _validate_requirements_output(self, output: Dict[str, Any]) -> ValidationResult:
        """Validate requirements analyst output."""
        issues = []
        recommendations = []
        score = 10.0
        
        # Check for functional and non-functional requirements
        if "requirements" in output:
            reqs = output["requirements"]
            if isinstance(reqs, list):
                functional_reqs = [r for r in reqs if "functional" in str(r).lower()]
                non_functional_reqs = [r for r in reqs if "non-functional" in str(r).lower()]
                
                if len(functional_reqs) == 0:
                    issues.append("No functional requirements identified")
                    score -= 2.0
                
                if len(non_functional_reqs) == 0:
                    recommendations.append("Consider adding non-functional requirements")
                    score -= 1.0
        
        score = max(0.0, score)
        passed = score >= 7.0
        
        return ValidationResult(
            validation_type=ValidationType.CONTENT,
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _validate_architecture_output(self, output: Dict[str, Any]) -> ValidationResult:
        """Validate architecture designer output."""
        issues = []
        recommendations = []
        score = 10.0
        
        # Check for architectural components
        if "components" in output:
            components = output["components"]
            if isinstance(components, (list, dict)) and len(components) < 2:
                issues.append("Architecture should have at least 2 components")
                score -= 2.0
        
        # Check for architectural decisions
        if "decisions" not in output:
            recommendations.append("Consider documenting architectural decisions")
            score -= 1.0
        
        score = max(0.0, score)
        passed = score >= 7.0
        
        return ValidationResult(
            validation_type=ValidationType.CONTENT,
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _validate_code_output(self, output: Dict[str, Any]) -> ValidationResult:
        """Validate code generator output."""
        issues = []
        recommendations = []
        score = 10.0
        
        # Check for source files
        if "source_files" in output:
            files = output["source_files"]
            if isinstance(files, dict):
                # Check for main application file
                main_files = [f for f in files.keys() if "main" in f.lower() or "app" in f.lower()]
                if not main_files:
                    recommendations.append("Consider adding a main application file")
                    score -= 1.0
                
                # Check for requirements.txt or similar
                dependency_files = [f for f in files.keys() if "requirements" in f.lower() or "dependencies" in f.lower()]
                if not dependency_files:
                    recommendations.append("Consider adding dependency management file")
                    score -= 1.0
        
        score = max(0.0, score)
        passed = score >= 7.0
        
        return ValidationResult(
            validation_type=ValidationType.CONTENT,
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _validate_test_output(self, output: Dict[str, Any]) -> ValidationResult:
        """Validate test generator output."""
        issues = []
        recommendations = []
        score = 10.0
        
        # Check for test files
        if "test_files" in output:
            files = output["test_files"]
            if isinstance(files, dict):
                # Check for unit tests
                unit_tests = [f for f in files.keys() if "test" in f.lower() and "unit" in f.lower()]
                if not unit_tests:
                    recommendations.append("Consider adding unit tests")
                    score -= 1.0
        
        score = max(0.0, score)
        passed = score >= 7.0
        
        return ValidationResult(
            validation_type=ValidationType.CONTENT,
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _validate_review_output(self, output: Dict[str, Any]) -> ValidationResult:
        """Validate code reviewer output."""
        issues = []
        recommendations = []
        score = 10.0
        
        # Check for overall score
        if "overall_score" in output:
            try:
                score_val = float(output["overall_score"])
                if not (0 <= score_val <= 10):
                    issues.append("Overall score should be between 0 and 10")
                    score -= 2.0
            except (ValueError, TypeError):
                issues.append("Overall score should be a number")
                score -= 2.0
        
        # Check for issues
        if "issues" in output:
            issues_list = output["issues"]
            if isinstance(issues_list, list):
                if len(issues_list) == 0:
                    recommendations.append("Consider providing more detailed review feedback")
                    score -= 1.0
        
        score = max(0.0, score)
        passed = score >= 7.0
        
        return ValidationResult(
            validation_type=ValidationType.CONTENT,
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _validate_security_output(self, output: Dict[str, Any]) -> ValidationResult:
        """Validate security analyst output."""
        issues = []
        recommendations = []
        score = 10.0
        
        # Check for security score
        if "security_score" in output:
            try:
                security_score = float(output["security_score"])
                if not (0 <= security_score <= 10):
                    issues.append("Security score should be between 0 and 10")
                    score -= 2.0
            except (ValueError, TypeError):
                issues.append("Security score should be a number")
                score -= 2.0
        
        # Check for vulnerabilities
        if "vulnerabilities" in output:
            vulns = output["vulnerabilities"]
            if isinstance(vulns, list):
                if len(vulns) == 0:
                    recommendations.append("Consider providing more detailed security analysis")
                    score -= 1.0
        
        score = max(0.0, score)
        passed = score >= 7.0
        
        return ValidationResult(
            validation_type=ValidationType.SECURITY,
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _validate_documentation_output(self, output: Dict[str, Any]) -> ValidationResult:
        """Validate documentation generator output."""
        issues = []
        recommendations = []
        score = 10.0
        
        # Check for README
        if "readme" in output:
            readme = output["readme"]
            if isinstance(readme, str) and len(readme.strip()) < 100:
                issues.append("README should be more comprehensive")
                score -= 2.0
        
        # Check for API documentation
        if "api_docs" not in output:
            recommendations.append("Consider adding API documentation")
            score -= 1.0
        
        score = max(0.0, score)
        passed = score >= 7.0
        
        return ValidationResult(
            validation_type=ValidationType.CONTENT,
            passed=passed,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
    
    def get_quality_metrics(self, agent_name: Optional[str] = None) -> List[QualityMetric]:
        """Get quality metrics for tracking."""
        if agent_name:
            return [m for m in self.quality_metrics if m.agent_name == agent_name]
        return self.quality_metrics
    
    def get_validation_history(self, validation_type: Optional[ValidationType] = None) -> List[ValidationResult]:
        """Get validation history."""
        if validation_type:
            return [v for v in self.validation_history if v.validation_type == validation_type]
        return self.validation_history
    
    def get_gate_results(self, agent_name: Optional[str] = None) -> List[QualityGateResult]:
        """Get quality gate results."""
        if agent_name:
            return [g for g in self.gate_results if agent_name in g.gate_name]
        return self.gate_results
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate a comprehensive quality report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_validations": len(self.validation_history),
                "passed_validations": len([v for v in self.validation_history if v.passed]),
                "failed_validations": len([v for v in self.validation_history if not v.passed]),
                "total_gates": len(self.gate_results),
                "passed_gates": len([g for g in self.gate_results if g.passed]),
                "failed_gates": len([g for g in self.gate_results if not g.passed])
            },
            "agent_performance": {},
            "validation_breakdown": {},
            "recommendations": []
        }
        
        # Agent performance breakdown
        for agent_name in self.quality_thresholds.keys():
            agent_gates = [g for g in self.gate_results if agent_name in g.gate_name]
            if agent_gates:
                avg_score = sum(g.score for g in agent_gates) / len(agent_gates)
                passed_count = len([g for g in agent_gates if g.passed])
                report["agent_performance"][agent_name] = {
                    "average_score": round(avg_score, 2),
                    "gates_passed": passed_count,
                    "total_gates": len(agent_gates),
                    "success_rate": round(passed_count / len(agent_gates) * 100, 1)
                }
        
        # Validation breakdown by type
        for validation_type in ValidationType:
            type_validations = [v for v in self.validation_history if v.validation_type == validation_type]
            if type_validations:
                passed_count = len([v for v in type_validations if v.passed])
                avg_score = sum(v.score for v in type_validations) / len(type_validations)
                report["validation_breakdown"][validation_type.value] = {
                    "total": len(type_validations),
                    "passed": passed_count,
                    "failed": len(type_validations) - passed_count,
                    "average_score": round(avg_score, 2),
                    "success_rate": round(passed_count / len(type_validations) * 100, 1)
                }
        
        # Generate recommendations
        recommendations = []
        
        # Check for consistently failing validations
        for validation_type in ValidationType:
            type_validations = [v for v in self.validation_history if v.validation_type == validation_type]
            if type_validations:
                failed_count = len([v for v in type_validations if not v.passed])
                if failed_count > len(type_validations) * 0.3:  # More than 30% failure rate
                    recommendations.append(f"Focus on improving {validation_type.value} validation quality")
        
        # Check for agents with low success rates
        for agent_name, performance in report["agent_performance"].items():
            if performance["success_rate"] < 70:
                recommendations.append(f"Improve quality standards for {agent_name} agent")
        
        report["recommendations"] = recommendations
        
        return report


# Global quality assurance system instance
quality_assurance = QualityAssuranceSystem()
