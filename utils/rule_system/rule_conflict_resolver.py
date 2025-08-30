#!/usr/bin/env python3
"""
Rule Conflict Resolver

Intelligent system for detecting and resolving conflicts between rules,
ensuring systematic and harmonious rule application without contradictions
or inefficiencies.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import json

class ConflictSeverity(Enum):
    """Severity levels for rule conflicts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ResolutionStrategy(Enum):
    """Available conflict resolution strategies."""
    HIERARCHY_PRIORITY = "hierarchy_priority"
    CONTEXT_BASED = "context_based"
    MERGE_APPROACHES = "merge_approaches"
    SEQUENTIAL_APPLICATION = "sequential_application"
    CUSTOM_RESOLUTION = "custom_resolution"

@dataclass
class RuleConflict:
    """Detected conflict between rules."""
    rule_a: str
    rule_b: str
    conflict_type: str
    severity: ConflictSeverity
    description: str
    context: Dict[str, Any]
    resolution_options: List[str]

@dataclass
class ConflictResolution:
    """Resolution for a rule conflict."""
    conflict: RuleConflict
    strategy: ResolutionStrategy
    primary_rule: str
    secondary_rule: str
    application_sequence: List[str]
    modifications: Dict[str, Any]
    rationale: str

class RuleConflictResolver:
    """
    Intelligent system for detecting and resolving rule conflicts.
    
    This system identifies potential conflicts between rules, analyzes
    their impact, and provides systematic resolution strategies to ensure
    harmonious and effective rule application.
    """
    
    def __init__(self, resolution_file: Path = None):
        self.resolution_file = resolution_file or Path('monitoring/rule_conflict_resolutions.json')
        self.resolution_file.parent.mkdir(parents=True, exist_ok=True)
        self.resolution_history = self._load_resolution_history()
        self.rule_hierarchy = self._define_rule_hierarchy()
        self.conflict_patterns = self._load_conflict_patterns()
        
    def detect_conflicts(self, 
                        active_rules: List[str],
                        task_context: Dict[str, Any]) -> List[RuleConflict]:
        """
        Detect potential conflicts between active rules.
        
        Args:
            active_rules: List of rules to be applied
            task_context: Context in which rules will be applied
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Check pairwise conflicts
        for i, rule_a in enumerate(active_rules):
            for rule_b in active_rules[i+1:]:
                conflict = self._analyze_rule_pair(rule_a, rule_b, task_context)
                if conflict:
                    conflicts.append(conflict)
        
        # Check multi-rule conflicts
        multi_conflicts = self._analyze_multi_rule_conflicts(active_rules, task_context)
        conflicts.extend(multi_conflicts)
        
        return conflicts
    
    def resolve_conflicts(self, conflicts: List[RuleConflict]) -> List[ConflictResolution]:
        """
        Resolve detected conflicts using intelligent strategies.
        
        Args:
            conflicts: List of conflicts to resolve
            
        Returns:
            List of conflict resolutions
        """
        resolutions = []
        
        for conflict in conflicts:
            resolution = self._generate_resolution(conflict)
            resolutions.append(resolution)
            
            # Record resolution for learning
            self._record_resolution(conflict, resolution)
        
        return resolutions
    
    def _analyze_rule_pair(self, 
                         rule_a: str, 
                         rule_b: str,
                         context: Dict[str, Any]) -> Optional[RuleConflict]:
        """Analyze two rules for potential conflicts."""
        
        # Known conflict patterns
        known_conflicts = {
            ('KISS Rule', 'Object-Oriented Programming Rule'): {
                'type': 'complexity_tension',
                'severity': ConflictSeverity.MEDIUM,
                'description': 'KISS promotes simplicity while OOP can introduce complexity'
            },
            ('Keep It Small and Simple (KISS) Rule', 'Don\'t Repeat Yourself (DRY) Rule'): {
                'type': 'abstraction_tension',
                'severity': ConflictSeverity.LOW,
                'description': 'KISS favors simplicity while DRY promotes abstraction'
            },
            ('No Premature Victory Declaration Rule', 'Clean Repository Focus Rule'): {
                'type': 'timing_conflict',
                'severity': ConflictSeverity.LOW,
                'description': 'Cleanup timing conflicts with thorough validation'
            }
        }
        
        # Check direct conflicts
        conflict_key = (rule_a, rule_b)
        reverse_key = (rule_b, rule_a)
        
        if conflict_key in known_conflicts:
            conflict_data = known_conflicts[conflict_key]
        elif reverse_key in known_conflicts:
            conflict_data = known_conflicts[reverse_key]
        else:
            # Analyze for potential implicit conflicts
            conflict_data = self._detect_implicit_conflict(rule_a, rule_b, context)
        
        if conflict_data:
            return RuleConflict(
                rule_a=rule_a,
                rule_b=rule_b,
                conflict_type=conflict_data['type'],
                severity=conflict_data['severity'],
                description=conflict_data['description'],
                context=context,
                resolution_options=self._generate_resolution_options(conflict_data)
            )
        
        return None
    
    def _detect_implicit_conflict(self, 
                                rule_a: str,
                                rule_b: str,
                                context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect implicit conflicts between rules."""
        
        # Analyze rule characteristics
        rule_a_key = rule_a.lower().replace(' ', '_').replace('-', '_')
        rule_b_key = rule_b.lower().replace(' ', '_').replace('-', '_')
        
        # Time-based conflicts
        if ('immediate' in rule_a_key or 'live' in rule_a_key) and ('thorough' in rule_b_key):
            return {
                'type': 'timing_conflict',
                'severity': ConflictSeverity.LOW,
                'description': f'{rule_a} requires immediate action while {rule_b} requires thorough analysis'
            }
        
        # Scope conflicts
        if ('simple' in rule_a_key or 'kiss' in rule_a_key) and ('comprehensive' in rule_b_key):
            return {
                'type': 'scope_conflict',
                'severity': ConflictSeverity.MEDIUM,
                'description': f'{rule_a} favors simplicity while {rule_b} requires comprehensive approach'
            }
        
        return None
    
    def _generate_resolution(self, conflict: RuleConflict) -> ConflictResolution:
        """Generate resolution strategy for a conflict."""
        
        # Determine strategy based on conflict type and context
        if conflict.severity == ConflictSeverity.CRITICAL:
            strategy = ResolutionStrategy.HIERARCHY_PRIORITY
        elif conflict.conflict_type == 'timing_conflict':
            strategy = ResolutionStrategy.SEQUENTIAL_APPLICATION
        elif conflict.conflict_type == 'scope_conflict':
            strategy = ResolutionStrategy.CONTEXT_BASED
        else:
            strategy = ResolutionStrategy.MERGE_APPROACHES
        
        # Apply resolution strategy
        resolution = self._apply_resolution_strategy(conflict, strategy)
        return resolution
    
    def _apply_resolution_strategy(self, 
                                 conflict: RuleConflict,
                                 strategy: ResolutionStrategy) -> ConflictResolution:
        """Apply specific resolution strategy."""
        
        if strategy == ResolutionStrategy.HIERARCHY_PRIORITY:
            # Use rule hierarchy to determine priority
            rule_a_priority = self._get_rule_priority(conflict.rule_a)
            rule_b_priority = self._get_rule_priority(conflict.rule_b)
            
            if rule_a_priority > rule_b_priority:
                primary, secondary = conflict.rule_a, conflict.rule_b
            else:
                primary, secondary = conflict.rule_b, conflict.rule_a
            
            return ConflictResolution(
                conflict=conflict,
                strategy=strategy,
                primary_rule=primary,
                secondary_rule=secondary,
                application_sequence=[primary, secondary],
                modifications={'secondary_rule_modifications': 'apply_with_primary_constraints'},
                rationale=f"Applied hierarchy priority: {primary} takes precedence over {secondary}"
            )
        
        elif strategy == ResolutionStrategy.SEQUENTIAL_APPLICATION:
            # Apply rules in sequence to avoid timing conflicts
            return ConflictResolution(
                conflict=conflict,
                strategy=strategy,
                primary_rule=conflict.rule_a,
                secondary_rule=conflict.rule_b,
                application_sequence=[conflict.rule_a, conflict.rule_b],
                modifications={'apply_sequentially': True},
                rationale=f"Sequential application: {conflict.rule_a} first, then {conflict.rule_b}"
            )
        
        elif strategy == ResolutionStrategy.CONTEXT_BASED:
            # Choose based on context appropriateness
            context_scores = {
                conflict.rule_a: self._assess_context_appropriateness(conflict.rule_a, conflict.context),
                conflict.rule_b: self._assess_context_appropriateness(conflict.rule_b, conflict.context)
            }
            
            primary = max(context_scores.items(), key=lambda x: x[1])[0]
            secondary = conflict.rule_b if primary == conflict.rule_a else conflict.rule_a
            
            return ConflictResolution(
                conflict=conflict,
                strategy=strategy,
                primary_rule=primary,
                secondary_rule=secondary,
                application_sequence=[primary, secondary],
                modifications={'context_adapted': True},
                rationale=f"Context-based priority: {primary} more appropriate for current context"
            )
        
        else:  # MERGE_APPROACHES
            return ConflictResolution(
                conflict=conflict,
                strategy=strategy,
                primary_rule=conflict.rule_a,
                secondary_rule=conflict.rule_b,
                application_sequence=[conflict.rule_a, conflict.rule_b],
                modifications={'merge_compatible_aspects': True},
                rationale=f"Merged approach: combine compatible aspects of both rules"
            )
    
    def _get_rule_priority(self, rule_name: str) -> int:
        """Get rule priority from hierarchy (1-10, higher is more important)."""
        return self.rule_hierarchy.get(rule_name, 5)  # Default medium priority
    
    def _define_rule_hierarchy(self) -> Dict[str, int]:
        """Define rule hierarchy with priority levels."""
        return {
            # Foundation rules (highest priority)
            "Context Awareness and Excellence Rule": 10,
            "No Premature Victory Declaration Rule": 9,
            "Live Documentation Updates Rule": 9,
            "Clean Repository Focus Rule": 8,
            "No Silent Errors and Mock Fallbacks Rule": 8,
            
            # Disciplinary rules (high priority)
            "Boy Scout Rule": 7,
            "Courage Rule": 7,
            "Test-Driven Development Rule": 7,
            
            # Technical standards (medium priority)
            "Model Selection Rule": 6,
            "Streamlit Secrets Management Rule": 6,
            "File Organization Rule": 5,
            "Best Practices and Standard Libraries Rule": 5,
            "Don't Repeat Yourself (DRY) Rule": 5,
            "Keep It Small and Simple (KISS) Rule": 5,
            "Object-Oriented Programming Rule": 5,
            "Clear Documentation Rule": 4
        }
    
    def _assess_context_appropriateness(self, rule_name: str, context: Dict[str, Any]) -> float:
        """Assess how appropriate a rule is for the given context."""
        # Simplified context assessment
        task_type = context.get('task_type', 'unknown')
        
        rule_context_scores = {
            'file_operation': {
                'File Organization Rule': 0.95,
                'Clean Repository Focus Rule': 0.9,
                'Boy Scout Rule': 0.8
            },
            'testing': {
                'Test-Driven Development Rule': 0.95,
                'No Premature Victory Declaration Rule': 0.9,
                'Courage Rule': 0.85
            },
            'documentation': {
                'Live Documentation Updates Rule': 0.95,
                'Clear Documentation Rule': 0.9,
                'Context Awareness and Excellence Rule': 0.85
            }
        }
        
        return rule_context_scores.get(task_type, {}).get(rule_name, 0.5)
    
    def _generate_resolution_options(self, conflict_data: Dict[str, Any]) -> List[str]:
        """Generate possible resolution options for a conflict."""
        return [
            "Apply rules sequentially based on priority",
            "Use context-based rule selection",
            "Merge compatible aspects of both rules",
            "Apply primary rule with secondary rule constraints",
            "Create custom resolution for this specific case"
        ]
    
    def _analyze_multi_rule_conflicts(self, 
                                   rules: List[str],
                                   context: Dict[str, Any]) -> List[RuleConflict]:
        """Analyze conflicts involving multiple rules."""
        # This would identify more complex interaction patterns
        # For now, return empty list
        return []
    
    def _record_resolution(self, conflict: RuleConflict, resolution: ConflictResolution) -> None:
        """Record conflict resolution for machine learning."""
        record = {
            'timestamp': datetime.now().isoformat(),
            'conflict': asdict(conflict),
            'resolution': asdict(resolution)
        }
        
        self.resolution_history.append(record)
        self._save_resolution_history()
    
    def _load_resolution_history(self) -> List[Dict[str, Any]]:
        """Load resolution history."""
        if self.resolution_file.exists():
            try:
                with open(self.resolution_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_resolution_history(self) -> None:
        """Save resolution history."""
        with open(self.resolution_file, 'w') as f:
            json.dump(self.resolution_history, f, indent=2)
    
    def _load_conflict_patterns(self) -> Dict[str, Any]:
        """Load known conflict patterns."""
        # This would load from configuration or learned patterns
        return {}
    
    def generate_resolution_report(self, 
                                 rules: List[str],
                                 context: Dict[str, Any]) -> str:
        """Generate comprehensive conflict resolution report."""
        conflicts = self.detect_conflicts(rules, context)
        
        report = []
        report.append("⚖️ RULE CONFLICT RESOLUTION REPORT")
        report.append("=" * 50)
        report.append("")
        report.append(f"**Active Rules**: {len(rules)}")
        report.append(f"**Context**: {context.get('task_type', 'unknown')}")
        report.append("")
        
        if conflicts:
            report.append(f"🚨 **CONFLICTS DETECTED**: {len(conflicts)}")
            report.append("")
            
            resolutions = self.resolve_conflicts(conflicts)
            
            for i, (conflict, resolution) in enumerate(zip(conflicts, resolutions), 1):
                report.append(f"**Conflict {i}**: {conflict.rule_a} vs {conflict.rule_b}")
                report.append(f"Severity: {conflict.severity.value.upper()}")
                report.append(f"Issue: {conflict.description}")
                report.append(f"Resolution: {resolution.strategy.value}")
                report.append(f"Primary Rule: {resolution.primary_rule}")
                report.append(f"Sequence: {' → '.join(resolution.application_sequence)}")
                report.append(f"Rationale: {resolution.rationale}")
                report.append("")
        else:
            report.append("✅ **NO CONFLICTS DETECTED**")
            report.append("All rules can be applied harmoniously")
        
        return "\n".join(report)

def demo_conflict_resolver():
    """Demonstrate the conflict resolver."""
    print("⚖️ RULE CONFLICT RESOLVER DEMO")
    print("=" * 50)
    
    resolver = RuleConflictResolver()
    
    # Test scenario with potential conflicts
    test_rules = [
        "Keep It Small and Simple (KISS) Rule",
        "Object-Oriented Programming Rule",
        "Don't Repeat Yourself (DRY) Rule",
        "No Premature Victory Declaration Rule",
        "Clean Repository Focus Rule"
    ]
    
    test_context = {
        'task_type': 'code_implementation',
        'complexity': 'complex',
        'quality_requirements': 0.95,
        'time_pressure': 0.6
    }
    
    print(resolver.generate_resolution_report(test_rules, test_context))

if __name__ == "__main__":
    demo_conflict_resolver()
