#!/usr/bin/env python3
"""
Rule Application Self-Testing Framework

A comprehensive framework for testing and validating the systematic application
of development rules to ensure disciplined, complete, and high-quality work.
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
from pathlib import Path

class TaskType(Enum):
    FILE_OPERATION = "file_operation"
    CODE_IMPLEMENTATION = "code_implementation" 
    PROJECT_COMPLETION = "project_completion"
    ERROR_HANDLING = "error_handling"
    DOCUMENTATION_UPDATE = "documentation_update"
    TESTING = "testing"
    CONFIGURATION = "configuration"
    REFACTORING = "refactoring"

class RulePriority(Enum):
    CRITICAL_FOUNDATION = 1
    DISCIPLINARY = 2
    TECHNICAL_STANDARDS = 3

@dataclass
class RuleApplication:
    rule_name: str
    priority: RulePriority
    applied: bool = False
    evidence_provided: bool = False
    completion_verified: bool = False
    sequence_position: Optional[int] = None
    
@dataclass
class RuleViolation:
    rule_name: str
    violation_type: str
    severity: str
    description: str
    evidence_missing: List[str]
    recovery_steps: List[str]

@dataclass
class SessionAnalysis:
    task_type: TaskType
    applicable_rules: List[str]
    applied_rules: List[RuleApplication]
    violations: List[RuleViolation]
    completeness_score: float
    sequence_score: float
    evidence_score: float
    overall_grade: str

class RuleApplicationTester:
    """
    Self-testing framework for validating rule application discipline.
    
    Tests whether rules are:
    1. Correctly identified for task types
    2. Applied in proper sequence
    3. Completed with evidence
    4. Validated systematically
    """
    
    def __init__(self):
        self.rule_definitions = self._load_rule_definitions()
        self.test_scenarios = self._load_test_scenarios()
        
    def _load_rule_definitions(self) -> Dict[str, Dict]:
        """Load rule definitions and their application criteria."""
        return {
            # CRITICAL FOUNDATION RULES
            "Context Awareness and Excellence Rule": {
                "priority": RulePriority.CRITICAL_FOUNDATION,
                "always_applies": True,
                "triggers": ["ANY_TASK"],
                "sequence_position": 1,
                "evidence_required": ["context_summary", "documentation_review"],
                "completion_criteria": ["README_read", "context_understood", "patterns_identified"]
            },
            
            "No Premature Victory Declaration Rule": {
                "priority": RulePriority.CRITICAL_FOUNDATION,
                "always_applies": True,
                "triggers": ["ANY_TASK"],
                "sequence_position": 2,
                "evidence_required": ["test_results", "validation_output", "success_metrics"],
                "completion_criteria": ["evidence_provided", "claims_verified", "testing_complete"]
            },
            
            "Live Documentation Updates Rule": {
                "priority": RulePriority.CRITICAL_FOUNDATION,
                "always_applies": True,
                "triggers": ["file_operation", "code_implementation", "configuration", "ANY_CHANGE"],
                "sequence_position": 3,
                "evidence_required": ["documentation_diff", "updated_files_list", "change_log"],
                "completion_criteria": ["changelog_updated", "readme_updated", "docs_synced"]
            },
            
            "Clean Repository Focus Rule": {
                "priority": RulePriority.CRITICAL_FOUNDATION,
                "always_applies": True,
                "triggers": ["ANY_TASK"],
                "sequence_position": 4,
                "evidence_required": ["clean_status", "temp_files_removed", "artifacts_cleaned"],
                "completion_criteria": ["git_status_clean", "no_temp_files", "organized_structure"]
            },
            
            "No Silent Errors and Mock Fallbacks Rule": {
                "priority": RulePriority.CRITICAL_FOUNDATION,
                "always_applies": True,
                "triggers": ["code_implementation", "error_handling"],
                "sequence_position": 5,
                "evidence_required": ["error_exposure", "no_fallbacks", "exception_handling"],
                "completion_criteria": ["errors_exposed", "fallbacks_removed", "proper_exceptions"]
            },
            
            # DISCIPLINARY RULES
            "Boy Scout Rule": {
                "priority": RulePriority.DISCIPLINARY,
                "triggers": ["code_implementation", "file_operation", "refactoring"],
                "evidence_required": ["improvements_list", "quality_enhancements", "cleanup_actions"],
                "completion_criteria": ["codebase_improved", "quality_enhanced", "debt_reduced"]
            },
            
            "Courage Rule": {
                "priority": RulePriority.DISCIPLINARY,
                "triggers": ["project_completion", "error_handling", "complex_tasks"],
                "evidence_required": ["complete_task_list", "systematic_completion", "no_shortcuts"],
                "completion_criteria": ["all_tasks_complete", "systematic_approach", "comprehensive_solution"]
            },
            
            "Test-Driven Development Rule": {
                "priority": RulePriority.DISCIPLINARY,
                "triggers": ["code_implementation", "testing"],
                "evidence_required": ["test_results", "tdd_sequence", "test_coverage"],
                "completion_criteria": ["tests_written_first", "tests_passing", "coverage_adequate"]
            },
            
            # TECHNICAL STANDARDS
            "File Organization Rule": {
                "priority": RulePriority.TECHNICAL_STANDARDS,
                "triggers": ["file_operation"],
                "evidence_required": ["structure_compliance", "organized_layout", "proper_placement"],
                "completion_criteria": ["files_organized", "structure_correct", "conventions_followed"]
            },
            
            "Model Selection Rule": {
                "priority": RulePriority.TECHNICAL_STANDARDS,
                "triggers": ["code_implementation", "ai_usage"],
                "evidence_required": ["model_selection_rationale", "complexity_assessment", "standardized_usage"],
                "completion_criteria": ["proper_model_selected", "standards_followed", "configuration_correct"]
            },
            
            "Streamlit Secrets Management Rule": {
                "priority": RulePriority.TECHNICAL_STANDARDS,
                "triggers": ["configuration", "security", "api_usage"],
                "evidence_required": ["secrets_usage", "security_compliance", "api_key_handling"],
                "completion_criteria": ["secrets_used", "security_maintained", "no_hardcoded_keys"]
            }
        }
    
    def _load_test_scenarios(self) -> Dict[str, Dict]:
        """Load test scenarios for different task types."""
        return {
            "file_organization_task": {
                "description": "Moving files to correct locations",
                "task_type": TaskType.FILE_OPERATION,
                "expected_rules": [
                    "Context Awareness and Excellence Rule",
                    "File Organization Rule", 
                    "Live Documentation Updates Rule",
                    "Clean Repository Focus Rule",
                    "Boy Scout Rule"
                ],
                "expected_sequence": [1, 3, 2, 4, 5],  # By sequence_position
                "evidence_requirements": [
                    "context_summary",
                    "structure_compliance", 
                    "documentation_diff",
                    "clean_status",
                    "improvements_list"
                ]
            },
            
            "code_implementation_task": {
                "description": "Implementing new functionality",
                "task_type": TaskType.CODE_IMPLEMENTATION,
                "expected_rules": [
                    "Context Awareness and Excellence Rule",
                    "Test-Driven Development Rule",
                    "No Silent Errors and Mock Fallbacks Rule",
                    "Model Selection Rule",
                    "Live Documentation Updates Rule",
                    "Boy Scout Rule"
                ],
                "expected_sequence": [1, 6, 5, 7, 3, 6],
                "evidence_requirements": [
                    "context_summary",
                    "test_results",
                    "error_exposure", 
                    "model_selection_rationale",
                    "documentation_diff",
                    "improvements_list"
                ]
            },
            
            "project_completion_task": {
                "description": "Completing project or major feature",
                "task_type": TaskType.PROJECT_COMPLETION,
                "expected_rules": [
                    "Courage Rule",
                    "No Premature Victory Declaration Rule",
                    "Live Documentation Updates Rule", 
                    "Clean Repository Focus Rule"
                ],
                "expected_sequence": [8, 2, 3, 4],
                "evidence_requirements": [
                    "complete_task_list",
                    "test_results",
                    "documentation_diff",
                    "clean_status"
                ]
            }
        }
    
    def identify_applicable_rules(self, task_description: str, task_type: TaskType) -> List[str]:
        """
        Identify which rules should apply to a given task.
        
        Args:
            task_description: Description of the task
            task_type: Type of task being performed
            
        Returns:
            List of rule names that should be applied
        """
        applicable_rules = []
        
        for rule_name, rule_def in self.rule_definitions.items():
            # Always apply foundation rules
            if rule_def["priority"] == RulePriority.CRITICAL_FOUNDATION:
                applicable_rules.append(rule_name)
            
            # Apply rules based on triggers
            elif any(trigger in rule_def["triggers"] for trigger in [task_type.value, "ANY_TASK"]):
                applicable_rules.append(rule_name)
            
            # Apply rules based on task description keywords
            elif any(keyword in task_description.lower() for keyword in self._get_rule_keywords(rule_name)):
                applicable_rules.append(rule_name)
        
        return applicable_rules
    
    def test_rule_determination(self, task_description: str, task_type: TaskType) -> Dict[str, any]:
        """
        Test whether correct rules are identified for a task.
        
        Args:
            task_description: Task description to test
            task_type: Type of task
            
        Returns:
            Test results with identified rules and validation
        """
        # Get my rule identification
        identified_rules = self.identify_applicable_rules(task_description, task_type)
        
        # Get expected rules from test scenarios
        scenario_key = f"{task_type.value}_task"
        expected_rules = self.test_scenarios.get(scenario_key, {}).get("expected_rules", [])
        
        # Calculate accuracy
        identified_set = set(identified_rules)
        expected_set = set(expected_rules)
        
        correct_rules = identified_set.intersection(expected_set)
        missing_rules = expected_set - identified_set
        extra_rules = identified_set - expected_set
        
        accuracy = len(correct_rules) / len(expected_set) if expected_set else 0.0
        
        return {
            "task_description": task_description,
            "task_type": task_type.value,
            "identified_rules": identified_rules,
            "expected_rules": expected_rules,
            "correct_rules": list(correct_rules),
            "missing_rules": list(missing_rules),
            "extra_rules": list(extra_rules),
            "accuracy_score": accuracy,
            "grade": self._calculate_grade(accuracy),
            "improvement_needed": accuracy < 0.9
        }
    
    def test_rule_sequence(self, applied_rules: List[RuleApplication]) -> Dict[str, any]:
        """
        Test whether rules are applied in correct sequence.
        
        Args:
            applied_rules: List of rules that were applied
            
        Returns:
            Sequence validation results
        """
        # Check sequence by priority
        priority_violations = []
        prev_priority = 0
        
        for rule_app in applied_rules:
            rule_def = self.rule_definitions.get(rule_app.rule_name, {})
            current_priority = rule_def.get("priority", RulePriority.TECHNICAL_STANDARDS).value
            
            if current_priority < prev_priority:
                priority_violations.append({
                    "rule": rule_app.rule_name,
                    "expected_priority": current_priority,
                    "actual_position": rule_app.sequence_position,
                    "violation": "Rule applied out of priority order"
                })
            
            prev_priority = current_priority
        
        # Check specific sequence positions
        sequence_violations = []
        for rule_app in applied_rules:
            rule_def = self.rule_definitions.get(rule_app.rule_name, {})
            expected_position = rule_def.get("sequence_position")
            
            if expected_position and rule_app.sequence_position != expected_position:
                sequence_violations.append({
                    "rule": rule_app.rule_name,
                    "expected_position": expected_position,
                    "actual_position": rule_app.sequence_position,
                    "violation": "Rule applied in wrong sequence position"
                })
        
        sequence_score = 1.0 - (len(priority_violations) + len(sequence_violations)) / len(applied_rules)
        
        return {
            "sequence_score": max(0.0, sequence_score),
            "priority_violations": priority_violations,
            "sequence_violations": sequence_violations,
            "grade": self._calculate_grade(sequence_score),
            "improvement_needed": sequence_score < 0.9
        }
    
    def test_evidence_completeness(self, applied_rules: List[RuleApplication]) -> Dict[str, any]:
        """
        Test whether proper evidence is provided for all rule applications.
        
        Args:
            applied_rules: List of rules that were applied
            
        Returns:
            Evidence completeness validation results
        """
        evidence_violations = []
        
        for rule_app in applied_rules:
            rule_def = self.rule_definitions.get(rule_app.rule_name, {})
            required_evidence = rule_def.get("evidence_required", [])
            
            if not rule_app.evidence_provided:
                evidence_violations.append({
                    "rule": rule_app.rule_name,
                    "required_evidence": required_evidence,
                    "violation": "No evidence provided for rule application"
                })
            
            completion_criteria = rule_def.get("completion_criteria", [])
            if not rule_app.completion_verified:
                evidence_violations.append({
                    "rule": rule_app.rule_name,
                    "completion_criteria": completion_criteria,
                    "violation": "Rule completion not verified with evidence"
                })
        
        evidence_score = 1.0 - len(evidence_violations) / (len(applied_rules) * 2)  # 2 checks per rule
        
        return {
            "evidence_score": max(0.0, evidence_score),
            "evidence_violations": evidence_violations,
            "grade": self._calculate_grade(evidence_score),
            "improvement_needed": evidence_score < 0.9
        }
    
    def analyze_current_session(self, task_description: str, task_type: TaskType, 
                               applied_rules: List[RuleApplication]) -> SessionAnalysis:
        """
        Comprehensive analysis of current session's rule application.
        
        Args:
            task_description: Description of current task
            task_type: Type of current task
            applied_rules: Rules that were applied
            
        Returns:
            Complete session analysis with scores and recommendations
        """
        # Test rule determination
        rule_determination = self.test_rule_determination(task_description, task_type)
        
        # Test rule sequence
        sequence_analysis = self.test_rule_sequence(applied_rules)
        
        # Test evidence completeness
        evidence_analysis = self.test_evidence_completeness(applied_rules)
        
        # Calculate overall scores
        completeness_score = rule_determination["accuracy_score"]
        sequence_score = sequence_analysis["sequence_score"] 
        evidence_score = evidence_analysis["evidence_score"]
        
        overall_score = (completeness_score + sequence_score + evidence_score) / 3
        overall_grade = self._calculate_grade(overall_score)
        
        # Identify violations
        violations = []
        
        # Add missing rule violations
        for missing_rule in rule_determination["missing_rules"]:
            violations.append(RuleViolation(
                rule_name=missing_rule,
                violation_type="MISSING_RULE_APPLICATION",
                severity="HIGH",
                description=f"Required rule '{missing_rule}' was not applied",
                evidence_missing=self.rule_definitions[missing_rule]["evidence_required"],
                recovery_steps=[
                    f"Apply {missing_rule} immediately",
                    "Provide required evidence",
                    "Verify completion criteria"
                ]
            ))
        
        # Add sequence violations
        for violation in sequence_analysis["priority_violations"]:
            violations.append(RuleViolation(
                rule_name=violation["rule"],
                violation_type="SEQUENCE_VIOLATION",
                severity="MEDIUM",
                description=violation["violation"],
                evidence_missing=[],
                recovery_steps=[
                    "Reapply rules in correct sequence",
                    "Validate sequence compliance"
                ]
            ))
        
        # Add evidence violations
        for violation in evidence_analysis["evidence_violations"]:
            violations.append(RuleViolation(
                rule_name=violation["rule"],
                violation_type="EVIDENCE_VIOLATION", 
                severity="HIGH",
                description=violation["violation"],
                evidence_missing=violation.get("required_evidence", []),
                recovery_steps=[
                    "Provide missing evidence",
                    "Verify completion criteria",
                    "Document evidence clearly"
                ]
            ))
        
        return SessionAnalysis(
            task_type=task_type,
            applicable_rules=rule_determination["expected_rules"],
            applied_rules=applied_rules,
            violations=violations,
            completeness_score=completeness_score,
            sequence_score=sequence_score,
            evidence_score=evidence_score,
            overall_grade=overall_grade
        )
    
    def generate_session_report(self, analysis: SessionAnalysis) -> str:
        """
        Generate comprehensive session analysis report.
        
        Args:
            analysis: Session analysis results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("🔍 RULE APPLICATION SELF-TEST REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Overall Summary
        report.append(f"📊 **OVERALL GRADE: {analysis.overall_grade}**")
        report.append(f"Task Type: {analysis.task_type.value}")
        report.append(f"Rules Applied: {len(analysis.applied_rules)}")
        report.append(f"Violations Detected: {len(analysis.violations)}")
        report.append("")
        
        # Detailed Scores
        report.append("📈 **DETAILED SCORES**")
        report.append(f"- Rule Completeness: {analysis.completeness_score:.2f}")
        report.append(f"- Sequence Adherence: {analysis.sequence_score:.2f}")
        report.append(f"- Evidence Quality: {analysis.evidence_score:.2f}")
        report.append("")
        
        # Violations
        if analysis.violations:
            report.append("❌ **VIOLATIONS DETECTED**")
            for i, violation in enumerate(analysis.violations, 1):
                report.append(f"{i}. **{violation.rule_name}**")
                report.append(f"   Type: {violation.violation_type}")
                report.append(f"   Severity: {violation.severity}")
                report.append(f"   Issue: {violation.description}")
                if violation.evidence_missing:
                    report.append(f"   Missing Evidence: {', '.join(violation.evidence_missing)}")
                report.append(f"   Recovery: {'; '.join(violation.recovery_steps)}")
                report.append("")
        else:
            report.append("✅ **NO VIOLATIONS DETECTED**")
            report.append("")
        
        # Recommendations
        if analysis.violations:
            report.append("🔧 **IMMEDIATE ACTION REQUIRED**")
            high_severity = [v for v in analysis.violations if v.severity == "HIGH"]
            if high_severity:
                report.append(f"- {len(high_severity)} HIGH severity violations need immediate attention")
            
            medium_severity = [v for v in analysis.violations if v.severity == "MEDIUM"]
            if medium_severity:
                report.append(f"- {len(medium_severity)} MEDIUM severity violations should be addressed")
            
            report.append("")
            report.append("📋 **RECOVERY PLAN**:")
            for i, violation in enumerate(high_severity + medium_severity, 1):
                report.append(f"{i}. {violation.rule_name}: {violation.recovery_steps[0]}")
        else:
            report.append("🎉 **EXCELLENT RULE APPLICATION**")
            report.append("All rules applied systematically with proper evidence.")
        
        return "\n".join(report)
    
    def self_test_current_session(self) -> str:
        """
        Self-test the current file organization session.
        
        Returns:
            Self-test report for current session
        """
        # Define current session parameters
        task_description = "Apply file organization rule and move python files from root directory to correct locations"
        task_type = TaskType.FILE_OPERATION
        
        # Define what I actually applied (based on my actions)
        applied_rules = [
            RuleApplication("File Organization Rule", RulePriority.TECHNICAL_STANDARDS, 
                          applied=True, evidence_provided=False, completion_verified=False, sequence_position=1),
            RuleApplication("Clean Repository Focus Rule", RulePriority.CRITICAL_FOUNDATION,
                          applied=True, evidence_provided=False, completion_verified=False, sequence_position=2),
            # Missing: Context Awareness Rule (I should have read README first)
            # Missing: Live Documentation Updates Rule (I forgot to update docs)
            # Missing: Boy Scout Rule (didn't look for other improvements)
        ]
        
        # Analyze the session
        analysis = self.analyze_current_session(task_description, task_type, applied_rules)
        
        # Generate report
        return self.generate_session_report(analysis)
    
    def _get_rule_keywords(self, rule_name: str) -> List[str]:
        """Get keywords that trigger a specific rule."""
        keyword_map = {
            "File Organization Rule": ["file", "move", "organize", "structure", "directory"],
            "Test-Driven Development Rule": ["test", "tdd", "testing", "coverage"],
            "Model Selection Rule": ["llm", "model", "ai", "gemini"],
            "Live Documentation Updates Rule": ["change", "update", "modify", "create"],
            "Clean Repository Focus Rule": ["clean", "temp", "artifact", "temporary"],
            "Boy Scout Rule": ["improve", "enhance", "quality", "refactor"],
            "Courage Rule": ["complete", "finish", "thorough", "systematic"]
        }
        return keyword_map.get(rule_name, [])
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from numeric score."""
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "B+"
        elif score >= 0.80:
            return "B"
        elif score >= 0.75:
            return "C+"
        elif score >= 0.70:
            return "C"
        elif score >= 0.60:
            return "D"
        else:
            return "F"
    
    def run_comprehensive_self_test(self) -> str:
        """
        Run comprehensive self-test of rule application capabilities.
        
        Returns:
            Complete self-test report
        """
        report = []
        report.append("🧪 COMPREHENSIVE RULE APPLICATION SELF-TEST")
        report.append("=" * 60)
        report.append("")
        
        # Test each scenario
        total_score = 0
        test_count = 0
        
        for scenario_name, scenario in self.test_scenarios.items():
            test_result = self.test_rule_determination(
                scenario["description"], 
                scenario["task_type"]
            )
            
            total_score += test_result["accuracy_score"]
            test_count += 1
            
            report.append(f"📋 **{scenario_name.upper()}**")
            report.append(f"Grade: {test_result['grade']}")
            report.append(f"Accuracy: {test_result['accuracy_score']:.2f}")
            
            if test_result["missing_rules"]:
                report.append(f"❌ Missing: {', '.join(test_result['missing_rules'])}")
            
            if test_result["extra_rules"]:
                report.append(f"⚠️ Extra: {', '.join(test_result['extra_rules'])}")
            
            report.append("")
        
        # Overall Assessment
        average_score = total_score / test_count
        overall_grade = self._calculate_grade(average_score)
        
        report.append("🎯 **OVERALL SELF-TEST RESULTS**")
        report.append(f"Average Score: {average_score:.2f}")
        report.append(f"Overall Grade: {overall_grade}")
        
        if average_score < 0.85:
            report.append("")
            report.append("❌ **IMPROVEMENT REQUIRED**")
            report.append("Rule determination accuracy below acceptable threshold.")
            report.append("Systematic training and discipline improvements needed.")
        else:
            report.append("")
            report.append("✅ **ACCEPTABLE PERFORMANCE**")
            report.append("Rule determination meets basic standards.")
        
        return "\n".join(report)

def main():
    """Demonstrate the rule application self-testing framework."""
    tester = RuleApplicationTester()
    
    print("🧪 RULE APPLICATION SELF-TESTING FRAMEWORK")
    print("=" * 60)
    print()
    
    # Test current session
    print("📊 CURRENT SESSION ANALYSIS:")
    current_session_report = tester.self_test_current_session()
    print(current_session_report)
    print()
    
    # Run comprehensive self-test
    print("🔬 COMPREHENSIVE CAPABILITY TEST:")
    comprehensive_report = tester.run_comprehensive_self_test()
    print(comprehensive_report)

if __name__ == "__main__":
    main()
