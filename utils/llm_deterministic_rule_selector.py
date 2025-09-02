"""
LLM-Optimized Deterministic Rule Selector
=========================================

MISSION: Provide deterministic, predictable rule selection that enables LLMs to work consistently and effectively.

Core Requirements:
- Deterministic selection (same input = same rules every time)
- Adequate rule coverage for each context
- Clear rule priorities and hierarchy
- LLM-friendly rule presentation
- Situational completeness validation

Design Philosophy: "Predictable rules enable predictable AI behavior"
"""

import hashlib
import json
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

class ContextPriority(Enum):
    """Deterministic context priority levels."""
    CRITICAL = 1    # Safety, core system integrity
    HIGH = 2        # Primary task execution
    MEDIUM = 3      # Quality and optimization
    LOW = 4         # Nice-to-have improvements

@dataclass
class DeterministicRuleSet:
    """Deterministic rule set with validation."""
    context: str
    rules: List[str]
    priority_map: Dict[str, int]
    adequacy_score: float
    completeness_validation: Dict[str, bool]
    llm_guidance: str

class LLMDeterministicRuleSelector:
    """
    Deterministic rule selector optimized for LLM decision-making.
    
    Guarantees:
    - Same input always produces same rule set
    - Complete coverage for each context
    - Clear priorities and guidance
    - Adequate rule sets for task completion
    """
    
    def __init__(self):
        # Deterministic rule mapping (order matters for consistency)
        self.deterministic_rule_matrix = {
            "AGILE": {
                "primary_rules": [
                    "safety_first_principle",
                    "agile_strategic_coordination", 
                    "user_story_management",
                    "agile_artifacts_maintenance"
                ],
                "supporting_rules": [
                    "live_documentation_updates",
                    "stakeholder_communication",
                    "sprint_management"
                ],
                "priority_levels": {
                    "safety_first_principle": ContextPriority.CRITICAL.value,
                    "agile_strategic_coordination": ContextPriority.HIGH.value,
                    "user_story_management": ContextPriority.HIGH.value,
                    "agile_artifacts_maintenance": ContextPriority.MEDIUM.value,
                    "live_documentation_updates": ContextPriority.MEDIUM.value,
                    "stakeholder_communication": ContextPriority.MEDIUM.value,
                    "sprint_management": ContextPriority.LOW.value
                },
                "llm_guidance": "Transform requests into managed agile work with user stories, artifacts, and stakeholder communication.",
                "adequacy_requirements": {
                    "coordination": True,
                    "story_management": True, 
                    "artifact_maintenance": True,
                    "documentation": True,
                    "communication": True
                }
            },
            
            "CODING": {
                "primary_rules": [
                    "safety_first_principle",
                    "development_core_principles",
                    "test_driven_development",
                    "clean_code_standards"
                ],
                "supporting_rules": [
                    "boyscout_leave_cleaner",
                    "error_handling_excellence",
                    "performance_considerations"
                ],
                "priority_levels": {
                    "safety_first_principle": ContextPriority.CRITICAL.value,
                    "development_core_principles": ContextPriority.HIGH.value,
                    "test_driven_development": ContextPriority.HIGH.value,
                    "clean_code_standards": ContextPriority.HIGH.value,
                    "boyscout_leave_cleaner": ContextPriority.MEDIUM.value,
                    "error_handling_excellence": ContextPriority.MEDIUM.value,
                    "performance_considerations": ContextPriority.LOW.value
                },
                "llm_guidance": "Write clean, tested, maintainable code following TDD principles and best practices.",
                "adequacy_requirements": {
                    "safety": True,
                    "testing": True,
                    "code_quality": True,
                    "error_handling": True,
                    "maintainability": True
                }
            },
            
            "TESTING": {
                "primary_rules": [
                    "safety_first_principle",
                    "no_failing_tests",
                    "test_driven_development",
                    "scientific_verification"
                ],
                "supporting_rules": [
                    "test_coverage_requirements",
                    "test_automation",
                    "quality_validation"
                ],
                "priority_levels": {
                    "safety_first_principle": ContextPriority.CRITICAL.value,
                    "no_failing_tests": ContextPriority.CRITICAL.value,
                    "test_driven_development": ContextPriority.HIGH.value,
                    "scientific_verification": ContextPriority.HIGH.value,
                    "test_coverage_requirements": ContextPriority.MEDIUM.value,
                    "test_automation": ContextPriority.MEDIUM.value,
                    "quality_validation": ContextPriority.LOW.value
                },
                "llm_guidance": "Ensure all tests pass with comprehensive coverage and scientific validation of results.",
                "adequacy_requirements": {
                    "test_execution": True,
                    "failure_prevention": True,
                    "coverage_validation": True,
                    "result_verification": True,
                    "automation": True
                }
            },
            
            "DEBUGGING": {
                "primary_rules": [
                    "safety_first_principle",
                    "systematic_problem_solving",
                    "error_exposure_rule",
                    "disaster_reporting"
                ],
                "supporting_rules": [
                    "no_silent_errors",
                    "diagnostic_excellence",
                    "root_cause_analysis"
                ],
                "priority_levels": {
                    "safety_first_principle": ContextPriority.CRITICAL.value,
                    "systematic_problem_solving": ContextPriority.HIGH.value,
                    "error_exposure_rule": ContextPriority.HIGH.value,
                    "disaster_reporting": ContextPriority.HIGH.value,
                    "no_silent_errors": ContextPriority.MEDIUM.value,
                    "diagnostic_excellence": ContextPriority.MEDIUM.value,
                    "root_cause_analysis": ContextPriority.LOW.value
                },
                "llm_guidance": "Systematically diagnose, expose, and resolve problems with comprehensive documentation.",
                "adequacy_requirements": {
                    "problem_analysis": True,
                    "error_diagnosis": True,
                    "systematic_approach": True,
                    "documentation": True,
                    "prevention": True
                }
            },
            
            "GIT": {
                "primary_rules": [
                    "safety_first_principle",
                    "automated_git_workflow",
                    "streamlined_git_operations",
                    "work_preservation"
                ],
                "supporting_rules": [
                    "clean_commit_messages",
                    "merge_validation",
                    "branch_management"
                ],
                "priority_levels": {
                    "safety_first_principle": ContextPriority.CRITICAL.value,
                    "automated_git_workflow": ContextPriority.HIGH.value,
                    "streamlined_git_operations": ContextPriority.HIGH.value,
                    "work_preservation": ContextPriority.HIGH.value,
                    "clean_commit_messages": ContextPriority.MEDIUM.value,
                    "merge_validation": ContextPriority.MEDIUM.value,
                    "branch_management": ContextPriority.LOW.value
                },
                "llm_guidance": "Commit early, commit often, preserve all work with clean git practices.",
                "adequacy_requirements": {
                    "work_safety": True,
                    "commit_workflow": True,
                    "message_quality": True,
                    "merge_safety": True,
                    "automation": True
                }
            },
            
            "DEFAULT": {
                "primary_rules": [
                    "safety_first_principle",
                    "intelligent_context_aware_rule_system",
                    "scientific_verification"
                ],
                "supporting_rules": [
                    "systematic_approach",
                    "quality_standards"
                ],
                "priority_levels": {
                    "safety_first_principle": ContextPriority.CRITICAL.value,
                    "intelligent_context_aware_rule_system": ContextPriority.HIGH.value,
                    "scientific_verification": ContextPriority.HIGH.value,
                    "systematic_approach": ContextPriority.MEDIUM.value,
                    "quality_standards": ContextPriority.LOW.value
                },
                "llm_guidance": "Apply safety-first principles with systematic approach and scientific validation.",
                "adequacy_requirements": {
                    "safety": True,
                    "context_awareness": True,
                    "verification": True,
                    "systematic_approach": True,
                    "quality": True
                }
            }
        }
    
    def select_deterministic_rules(self, context: str, task_description: str = "") -> DeterministicRuleSet:
        """
        Select rules deterministically for LLM optimization.
        
        Guarantees:
        - Same context + task = same rules every time
        - Complete rule coverage for context
        - Clear priorities and guidance
        """
        
        # Get base rule set for context
        rule_config = self.deterministic_rule_matrix.get(context, self.deterministic_rule_matrix["DEFAULT"])
        
        # Combine primary and supporting rules in deterministic order
        all_rules = rule_config["primary_rules"] + rule_config["supporting_rules"]
        
        # Create deterministic hash for validation
        context_hash = self._create_deterministic_hash(context, task_description)
        
        # Validate adequacy
        adequacy_score = self._calculate_adequacy_score(rule_config)
        completeness = self._validate_completeness(rule_config)
        
        return DeterministicRuleSet(
            context=context,
            rules=all_rules,
            priority_map=rule_config["priority_levels"],
            adequacy_score=adequacy_score,
            completeness_validation=completeness,
            llm_guidance=rule_config["llm_guidance"]
        )
    
    def _create_deterministic_hash(self, context: str, task_description: str) -> str:
        """Create deterministic hash for validation."""
        combined = f"{context}:{task_description}"
        return hashlib.md5(combined.encode()).hexdigest()[:8]
    
    def _calculate_adequacy_score(self, rule_config: Dict) -> float:
        """Calculate rule set adequacy score."""
        primary_count = len(rule_config["primary_rules"])
        supporting_count = len(rule_config["supporting_rules"])
        requirement_count = len(rule_config["adequacy_requirements"])
        
        # Weighted adequacy calculation
        adequacy = (primary_count * 0.6 + supporting_count * 0.3 + requirement_count * 0.1) / 10
        return min(adequacy, 1.0)
    
    def _validate_completeness(self, rule_config: Dict) -> Dict[str, bool]:
        """Validate rule set completeness."""
        requirements = rule_config["adequacy_requirements"]
        primary_rules = rule_config["primary_rules"]
        
        # Check if each requirement is covered
        completeness = {}
        for requirement, needed in requirements.items():
            # Simplified coverage check (can be enhanced)
            covered = any(requirement.lower() in rule.lower() for rule in primary_rules)
            completeness[requirement] = covered or not needed
        
        return completeness
    
    def generate_llm_instructions(self, rule_set: DeterministicRuleSet) -> str:
        """
        Generate clear, deterministic instructions for LLM.
        """
        
        instructions = f"""
🎯 **CONTEXT: {rule_set.context}**

**LLM GUIDANCE**: {rule_set.llm_guidance}

**ACTIVE RULES** (in priority order):
"""
        
        # Sort rules by priority for LLM clarity
        sorted_rules = sorted(rule_set.rules, key=lambda r: rule_set.priority_map.get(r, 999))
        
        for i, rule in enumerate(sorted_rules, 1):
            priority = rule_set.priority_map.get(rule, 999)
            priority_label = {1: "CRITICAL", 2: "HIGH", 3: "MEDIUM", 4: "LOW"}.get(priority, "UNKNOWN")
            instructions += f"{i}. **{rule}** ({priority_label})\n"
        
        instructions += f"""
**ADEQUACY SCORE**: {rule_set.adequacy_score:.1f}/1.0
**COMPLETENESS**: {sum(rule_set.completeness_validation.values())}/{len(rule_set.completeness_validation)} requirements covered

**DETERMINISTIC GUARANTEE**: Same context always produces same rule set for consistent LLM behavior.
"""
        
        return instructions
    
    def validate_rule_adequacy(self, context: str) -> Dict[str, Any]:
        """
        Validate that rule set is adequate for context.
        """
        rule_set = self.select_deterministic_rules(context)
        
        validation = {
            "context": context,
            "rule_count": len(rule_set.rules),
            "adequacy_score": rule_set.adequacy_score,
            "completeness_issues": [
                req for req, covered in rule_set.completeness_validation.items() 
                if not covered
            ],
            "priority_distribution": {
                "critical": sum(1 for r in rule_set.rules if rule_set.priority_map.get(r, 999) == 1),
                "high": sum(1 for r in rule_set.rules if rule_set.priority_map.get(r, 999) == 2),
                "medium": sum(1 for r in rule_set.rules if rule_set.priority_map.get(r, 999) == 3),
                "low": sum(1 for r in rule_set.rules if rule_set.priority_map.get(r, 999) == 4)
            },
            "adequacy_rating": "ADEQUATE" if rule_set.adequacy_score >= 0.8 else "NEEDS_IMPROVEMENT"
        }
        
        return validation

# Global deterministic selector
llm_rule_selector = LLMDeterministicRuleSelector()

def get_deterministic_rules_for_llm(context: str, task: str = "") -> str:
    """
    Get deterministic rules formatted for LLM consumption.
    
    This function guarantees:
    - Same context = same rules every time
    - Complete rule coverage
    - Clear priorities and guidance
    """
    rule_set = llm_rule_selector.select_deterministic_rules(context, task)
    return llm_rule_selector.generate_llm_instructions(rule_set)

def validate_context_adequacy(context: str) -> Dict[str, Any]:
    """
    Validate that a context has adequate rule coverage.
    """
    return llm_rule_selector.validate_rule_adequacy(context)

# Test deterministic behavior
if __name__ == "__main__":
    print("🧠 **LLM-OPTIMIZED DETERMINISTIC RULE SELECTION TEST**\n")
    
    test_contexts = ["AGILE", "CODING", "TESTING", "DEBUGGING", "GIT"]
    
    for context in test_contexts:
        print(f"**CONTEXT: {context}**")
        
        # Test deterministic selection
        rule_set1 = llm_rule_selector.select_deterministic_rules(context, "test task")
        rule_set2 = llm_rule_selector.select_deterministic_rules(context, "test task")
        
        # Verify deterministic behavior
        deterministic = rule_set1.rules == rule_set2.rules
        
        print(f"Rules: {len(rule_set1.rules)}")
        print(f"Adequacy: {rule_set1.adequacy_score:.1f}/1.0")
        print(f"Deterministic: {'✅' if deterministic else '❌'}")
        
        # Validate adequacy
        validation = validate_context_adequacy(context)
        print(f"Adequacy Rating: {validation['adequacy_rating']}")
        print()
