"""
Layered Rule Architecture System
===============================

VISION: Create organized layers of rules and rule sets for different purposes,
allowing precise control over which rules apply in which contexts while maintaining
orchestral coordination and organic growth.

Core Architecture:
- FOUNDATIONAL LAYER: Universal principles (always active)
- OPERATIONAL LAYER: Context-specific rule sets
- EMERGENT LAYER: Dynamically generated patterns
- ORCHESTRAL LAYER: Cross-layer coordination patterns

Rule Sets by Purpose:
- Essential Foundation (always active)
- Development Context Sets (activated by context)
- Specialized Purpose Sets (activated by goals)
- Emergent Pattern Sets (activated by conditions)
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

class RuleLayer(Enum):
    """Different layers in our rule architecture."""
    FOUNDATIONAL = "foundational"      # Universal principles - always active
    OPERATIONAL = "operational"        # Context-specific working rules
    EMERGENT = "emergent"             # Dynamically generated patterns
    ORCHESTRAL = "orchestral"         # Cross-layer coordination

class RuleSetPurpose(Enum):
    """Different purposes for rule sets."""
    ESSENTIAL_FOUNDATION = "essential_foundation"
    AGILE_COORDINATION = "agile_coordination"
    CODE_DEVELOPMENT = "code_development"
    TESTING_VALIDATION = "testing_validation"
    DEBUGGING_ANALYSIS = "debugging_analysis"
    DOCUMENTATION_EXCELLENCE = "documentation_excellence"
    ARCHITECTURE_DESIGN = "architecture_design"
    SECURITY_PROTECTION = "security_protection"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    GIT_WORKFLOW = "git_workflow"
    META_SYSTEM = "meta_system"
    EMERGENT_PATTERNS = "emergent_patterns"

@dataclass
class RuleDefinition:
    """Definition of a single rule."""
    rule_id: str
    rule_name: str
    description: str
    layer: RuleLayer
    purpose: RuleSetPurpose
    always_apply: bool
    contexts: List[str]
    priority: int                     # 1 = highest, 10 = lowest
    file_path: str                   # Path to .mdc file
    activation_triggers: List[str]   # What activates this rule
    dependencies: List[str]          # Other rules this depends on
    orchestral_coordination: str     # How this coordinates with others

@dataclass
class RuleSet:
    """A coherent set of rules for a specific purpose."""
    set_id: str
    set_name: str
    purpose: RuleSetPurpose
    layer: RuleLayer
    rules: List[RuleDefinition]
    activation_conditions: List[str]
    coordination_patterns: List[str]
    organic_growth_potential: float

class LayeredRuleArchitecture:
    """
    Main system for managing layered rule architecture.
    """
    
    def __init__(self):
        self.rule_layers: Dict[RuleLayer, List[RuleSet]] = {
            RuleLayer.FOUNDATIONAL: [],
            RuleLayer.OPERATIONAL: [],
            RuleLayer.EMERGENT: [],
            RuleLayer.ORCHESTRAL: []
        }
        self.rule_definitions: Dict[str, RuleDefinition] = {}
        self.rule_sets: Dict[str, RuleSet] = {}
        self._initialize_layered_architecture()
    
    def _initialize_layered_architecture(self):
        """Initialize the complete layered rule architecture."""
        
        # FOUNDATIONAL LAYER - Universal Principles (Always Active)
        self._create_foundational_layer()
        
        # OPERATIONAL LAYER - Context-Specific Rule Sets
        self._create_operational_layer()
        
        # EMERGENT LAYER - Dynamic Pattern Sets
        self._create_emergent_layer()
        
        # ORCHESTRAL LAYER - Cross-Layer Coordination
        self._create_orchestral_layer()
    
    def _create_foundational_layer(self):
        """Create the foundational layer with universal principles."""
        
        # Essential Foundation Rule Set (Always Active)
        essential_foundation_rules = [
            RuleDefinition(
                rule_id="FOUNDATION_SAFETY",
                rule_name="Safety First Principle",
                description="Never harm user or system - all else follows",
                layer=RuleLayer.FOUNDATIONAL,
                purpose=RuleSetPurpose.ESSENTIAL_FOUNDATION,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                file_path=".cursor/rules/core/safety_first_principle.mdc",
                activation_triggers=["ANY_OPERATION"],
                dependencies=[],
                orchestral_coordination="safety_consensus_building"
            ),
            RuleDefinition(
                rule_id="FOUNDATION_EVIDENCE",
                rule_name="Evidence-Based Success",
                description="No claims without concrete proof and validation",
                layer=RuleLayer.FOUNDATIONAL,
                purpose=RuleSetPurpose.ESSENTIAL_FOUNDATION,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                file_path=".cursor/rules/core/no_premature_victory_declaration_rule.mdc",
                activation_triggers=["SUCCESS_CLAIM", "COMPLETION_DECLARATION"],
                dependencies=["FOUNDATION_SAFETY"],
                orchestral_coordination="evidence_based_validation"
            ),
            RuleDefinition(
                rule_id="FOUNDATION_SYSTEMATIC",
                rule_name="Systematic Completion",
                description="Complete all work systematically and thoroughly",
                layer=RuleLayer.FOUNDATIONAL,
                purpose=RuleSetPurpose.ESSENTIAL_FOUNDATION,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                file_path=".cursor/rules/core/core_rule_application_framework.mdc",
                activation_triggers=["TASK_START", "WORK_EXECUTION"],
                dependencies=["FOUNDATION_EVIDENCE"],
                orchestral_coordination="systematic_work_completion"
            ),
            RuleDefinition(
                rule_id="FOUNDATION_STRUCTURE",
                rule_name="Structural Harmony",
                description="Perfect organization and file placement",
                layer=RuleLayer.FOUNDATIONAL,
                purpose=RuleSetPurpose.ESSENTIAL_FOUNDATION,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                file_path=".cursor/rules/development/file_organization_cleanup_rule.mdc",
                activation_triggers=["FILE_OPERATION", "ORGANIZATION_CHECK"],
                dependencies=["FOUNDATION_SYSTEMATIC"],
                orchestral_coordination="structural_harmony_maintenance"
            ),
            RuleDefinition(
                rule_id="FOUNDATION_LEARNING",
                rule_name="Learning from Failure",
                description="Transform all failures into collective wisdom",
                layer=RuleLayer.FOUNDATIONAL,
                purpose=RuleSetPurpose.ESSENTIAL_FOUNDATION,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                file_path=".cursor/rules/core/disaster_report_learning_rule.mdc",
                activation_triggers=["FAILURE_DETECTED", "ERROR_ENCOUNTERED"],
                dependencies=["FOUNDATION_STRUCTURE"],
                orchestral_coordination="collective_wisdom_building"
            )
        ]
        
        essential_foundation_set = RuleSet(
            set_id="ESSENTIAL_FOUNDATION",
            set_name="Essential Foundation Rules",
            purpose=RuleSetPurpose.ESSENTIAL_FOUNDATION,
            layer=RuleLayer.FOUNDATIONAL,
            rules=essential_foundation_rules,
            activation_conditions=["ALWAYS"],
            coordination_patterns=["safety_first", "evidence_based", "systematic_completion"],
            organic_growth_potential=0.9
        )
        
        self.rule_layers[RuleLayer.FOUNDATIONAL].append(essential_foundation_set)
        self.rule_sets["ESSENTIAL_FOUNDATION"] = essential_foundation_set
        
        # Register all rules
        for rule in essential_foundation_rules:
            self.rule_definitions[rule.rule_id] = rule
    
    def _create_operational_layer(self):
        """Create operational layer with context-specific rule sets."""
        
        # Agile Coordination Rule Set
        agile_rules = [
            RuleDefinition(
                rule_id="AGILE_STRATEGIC_COORDINATION",
                rule_name="Agile Strategic Coordination",
                description="@agile conductor orchestrating harmonious delivery",
                layer=RuleLayer.OPERATIONAL,
                purpose=RuleSetPurpose.AGILE_COORDINATION,
                always_apply=False,
                contexts=["AGILE"],
                priority=2,
                file_path=".cursor/rules/agile/agile_strategic_coordination_rule.mdc",
                activation_triggers=["@agile", "user_story", "sprint", "backlog"],
                dependencies=["FOUNDATION_SYSTEMATIC"],
                orchestral_coordination="agile_team_harmony"
            ),
            RuleDefinition(
                rule_id="AGILE_ARTIFACT_MAINTENANCE",
                rule_name="Agile Artifact Maintenance",
                description="Live updates to all agile documentation",
                layer=RuleLayer.OPERATIONAL,
                purpose=RuleSetPurpose.AGILE_COORDINATION,
                always_apply=False,
                contexts=["AGILE"],
                priority=2,
                file_path=".cursor/rules/agile/agile_artifacts_maintenance_rule.mdc",
                activation_triggers=["story_update", "sprint_change", "artifact_modification"],
                dependencies=["AGILE_STRATEGIC_COORDINATION"],
                orchestral_coordination="artifact_synchronization"
            )
        ]
        
        agile_set = RuleSet(
            set_id="AGILE_COORDINATION",
            set_name="Agile Coordination Rule Set",
            purpose=RuleSetPurpose.AGILE_COORDINATION,
            layer=RuleLayer.OPERATIONAL,
            rules=agile_rules,
            activation_conditions=["@agile", "user_story", "sprint", "agile_context"],
            coordination_patterns=["stakeholder_value_translation", "cross_team_synchronization"],
            organic_growth_potential=0.8
        )
        
        # Code Development Rule Set
        code_rules = [
            RuleDefinition(
                rule_id="CODE_DEVELOPMENT_PRINCIPLES",
                rule_name="Development Core Principles",
                description="Clean code, SOLID principles, best practices",
                layer=RuleLayer.OPERATIONAL,
                purpose=RuleSetPurpose.CODE_DEVELOPMENT,
                always_apply=False,
                contexts=["CODING", "DEVELOPMENT"],
                priority=2,
                file_path=".cursor/rules/development/development_core_principles_rule.mdc",
                activation_triggers=["@code", "implement", "develop", "create"],
                dependencies=["FOUNDATION_SYSTEMATIC"],
                orchestral_coordination="code_excellence_harmony"
            ),
            RuleDefinition(
                rule_id="CODE_TYPE_PRECISION",
                rule_name="Type Signature Precision",
                description="Absolute precision in typing and API usage",
                layer=RuleLayer.OPERATIONAL,
                purpose=RuleSetPurpose.CODE_DEVELOPMENT,
                always_apply=False,
                contexts=["CODING", "DEVELOPMENT"],
                priority=3,
                file_path=".cursor/rules/development/development_type_signature_precision_rule.mdc",
                activation_triggers=["type_definition", "api_usage", "function_signature"],
                dependencies=["CODE_DEVELOPMENT_PRINCIPLES"],
                orchestral_coordination="type_safety_coordination"
            )
        ]
        
        code_set = RuleSet(
            set_id="CODE_DEVELOPMENT",
            set_name="Code Development Rule Set",
            purpose=RuleSetPurpose.CODE_DEVELOPMENT,
            layer=RuleLayer.OPERATIONAL,
            rules=code_rules,
            activation_conditions=["@code", "implement", "develop", "code_files"],
            coordination_patterns=["clean_code_harmony", "type_safety_enforcement"],
            organic_growth_potential=0.7
        )
        
        # Testing Validation Rule Set
        testing_rules = [
            RuleDefinition(
                rule_id="TESTING_TDD_FIRST",
                rule_name="Test-Driven Development",
                description="Tests first, implementation second, always",
                layer=RuleLayer.OPERATIONAL,
                purpose=RuleSetPurpose.TESTING_VALIDATION,
                always_apply=False,
                contexts=["TESTING", "TDD"],
                priority=2,
                file_path=".cursor/rules/testing/xp_test_first_development_rule.mdc",
                activation_triggers=["@test", "testing", "pytest", "validation"],
                dependencies=["FOUNDATION_EVIDENCE"],
                orchestral_coordination="test_driven_harmony"
            ),
            RuleDefinition(
                rule_id="TESTING_NO_FAILING",
                rule_name="No Failing Tests",
                description="Zero tolerance for failing tests",
                layer=RuleLayer.OPERATIONAL,
                purpose=RuleSetPurpose.TESTING_VALIDATION,
                always_apply=False,
                contexts=["TESTING"],
                priority=1,
                file_path=".cursor/rules/core/no_failing_tests_rule.mdc",
                activation_triggers=["test_execution", "ci_cd", "validation"],
                dependencies=["TESTING_TDD_FIRST"],
                orchestral_coordination="test_quality_assurance"
            )
        ]
        
        testing_set = RuleSet(
            set_id="TESTING_VALIDATION",
            set_name="Testing Validation Rule Set",
            purpose=RuleSetPurpose.TESTING_VALIDATION,
            layer=RuleLayer.OPERATIONAL,
            rules=testing_rules,
            activation_conditions=["@test", "testing", "pytest", "test_files"],
            coordination_patterns=["test_first_development", "quality_assurance"],
            organic_growth_potential=0.8
        )
        
        # Documentation Excellence Rule Set
        docs_rules = [
            RuleDefinition(
                rule_id="DOCS_LIVE_UPDATES",
                rule_name="Live Documentation Updates",
                description="Documentation synchronizes immediately with changes",
                layer=RuleLayer.OPERATIONAL,
                purpose=RuleSetPurpose.DOCUMENTATION_EXCELLENCE,
                always_apply=False,
                contexts=["DOCUMENTATION"],
                priority=2,
                file_path=".cursor/rules/quality/documentation_live_updates_rule.mdc",
                activation_triggers=["@docs", "documentation", "readme", "guide"],
                dependencies=["FOUNDATION_SYSTEMATIC"],
                orchestral_coordination="documentation_harmony"
            )
        ]
        
        docs_set = RuleSet(
            set_id="DOCUMENTATION_EXCELLENCE",
            set_name="Documentation Excellence Rule Set",
            purpose=RuleSetPurpose.DOCUMENTATION_EXCELLENCE,
            layer=RuleLayer.OPERATIONAL,
            rules=docs_rules,
            activation_conditions=["@docs", "documentation", "*.md", "guides"],
            coordination_patterns=["live_documentation", "excellence_standards"],
            organic_growth_potential=0.6
        )
        
        # Git Workflow Rule Set
        git_rules = [
            RuleDefinition(
                rule_id="GIT_STREAMLINED_OPS",
                rule_name="Streamlined Git Operations",
                description="Efficient git workflow: add, commit, push",
                layer=RuleLayer.OPERATIONAL,
                purpose=RuleSetPurpose.GIT_WORKFLOW,
                always_apply=False,
                contexts=["GIT"],
                priority=2,
                file_path=".cursor/rules/core/streamlined_git_operations_rule.mdc",
                activation_triggers=["@git", "commit", "push", "git_operations"],
                dependencies=["FOUNDATION_STRUCTURE"],
                orchestral_coordination="git_workflow_harmony"
            )
        ]
        
        git_set = RuleSet(
            set_id="GIT_WORKFLOW",
            set_name="Git Workflow Rule Set",
            purpose=RuleSetPurpose.GIT_WORKFLOW,
            layer=RuleLayer.OPERATIONAL,
            rules=git_rules,
            activation_conditions=["@git", "commit", "push", "git_context"],
            coordination_patterns=["streamlined_workflow", "version_control_harmony"],
            organic_growth_potential=0.5
        )
        
        # Add all operational sets
        operational_sets = [agile_set, code_set, testing_set, docs_set, git_set]
        
        for rule_set in operational_sets:
            self.rule_layers[RuleLayer.OPERATIONAL].append(rule_set)
            self.rule_sets[rule_set.set_id] = rule_set
            
            for rule in rule_set.rules:
                self.rule_definitions[rule.rule_id] = rule
    
    def _create_emergent_layer(self):
        """Create emergent layer for dynamic pattern sets."""
        
        emergent_rules = [
            RuleDefinition(
                rule_id="EMERGENT_SWARM_INTELLIGENCE",
                rule_name="Swarm Intelligence Patterns",
                description="Collectively intelligent coordination patterns",
                layer=RuleLayer.EMERGENT,
                purpose=RuleSetPurpose.EMERGENT_PATTERNS,
                always_apply=False,
                contexts=["EMERGENT"],
                priority=5,
                file_path="", # Generated dynamically
                activation_triggers=["collective_behavior", "swarm_coordination"],
                dependencies=["FOUNDATION_LEARNING"],
                orchestral_coordination="swarm_intelligence_emergence"
            ),
            RuleDefinition(
                rule_id="EMERGENT_ORGANIC_GROWTH",
                rule_name="Organic Growth Patterns",
                description="Naturally evolving coordination patterns",
                layer=RuleLayer.EMERGENT,
                purpose=RuleSetPurpose.EMERGENT_PATTERNS,
                always_apply=False,
                contexts=["EMERGENT"],
                priority=5,
                file_path="", # Generated dynamically
                activation_triggers=["organic_evolution", "natural_patterns"],
                dependencies=["EMERGENT_SWARM_INTELLIGENCE"],
                orchestral_coordination="organic_pattern_growth"
            )
        ]
        
        emergent_set = RuleSet(
            set_id="EMERGENT_PATTERNS",
            set_name="Emergent Pattern Rule Set",
            purpose=RuleSetPurpose.EMERGENT_PATTERNS,
            layer=RuleLayer.EMERGENT,
            rules=emergent_rules,
            activation_conditions=["emergence_detected", "pattern_formation"],
            coordination_patterns=["spontaneous_coordination", "collective_intelligence"],
            organic_growth_potential=1.0
        )
        
        self.rule_layers[RuleLayer.EMERGENT].append(emergent_set)
        self.rule_sets["EMERGENT_PATTERNS"] = emergent_set
        
        for rule in emergent_rules:
            self.rule_definitions[rule.rule_id] = rule
    
    def _create_orchestral_layer(self):
        """Create orchestral layer for cross-layer coordination."""
        
        orchestral_rules = [
            RuleDefinition(
                rule_id="ORCHESTRAL_CONDUCTOR",
                rule_name="Orchestral Conductor System",
                description="Coordinates all layers into harmonious symphony",
                layer=RuleLayer.ORCHESTRAL,
                purpose=RuleSetPurpose.META_SYSTEM,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                file_path=".cursor/rules/core/divine_harmony_integration_system.mdc",
                activation_triggers=["MULTI_LAYER_COORDINATION"],
                dependencies=["FOUNDATION_SYSTEMATIC"],
                orchestral_coordination="divine_harmony_orchestration"
            ),
            RuleDefinition(
                rule_id="ORCHESTRAL_INTELLIGENCE",
                rule_name="Intelligent Context Awareness",
                description="Smart detection and rule set activation",
                layer=RuleLayer.ORCHESTRAL,
                purpose=RuleSetPurpose.META_SYSTEM,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                file_path=".cursor/rules/meta/intelligent_context_aware_rule_system.mdc",
                activation_triggers=["CONTEXT_DETECTION"],
                dependencies=["ORCHESTRAL_CONDUCTOR"],
                orchestral_coordination="intelligent_coordination"
            )
        ]
        
        orchestral_set = RuleSet(
            set_id="ORCHESTRAL_COORDINATION",
            set_name="Orchestral Coordination Rule Set",
            purpose=RuleSetPurpose.META_SYSTEM,
            layer=RuleLayer.ORCHESTRAL,
            rules=orchestral_rules,
            activation_conditions=["ALWAYS"],
            coordination_patterns=["divine_harmony", "intelligent_context", "cross_layer_sync"],
            organic_growth_potential=0.95
        )
        
        self.rule_layers[RuleLayer.ORCHESTRAL].append(orchestral_set)
        self.rule_sets["ORCHESTRAL_COORDINATION"] = orchestral_set
        
        for rule in orchestral_rules:
            self.rule_definitions[rule.rule_id] = rule
    
    def get_active_rule_sets(self, context: Dict) -> List[RuleSet]:
        """Get active rule sets based on current context."""
        
        active_sets = []
        
        # Always include foundational and orchestral layers
        active_sets.extend(self.rule_layers[RuleLayer.FOUNDATIONAL])
        active_sets.extend(self.rule_layers[RuleLayer.ORCHESTRAL])
        
        # Add operational sets based on context
        context_str = str(context).lower()
        
        for rule_set in self.rule_layers[RuleLayer.OPERATIONAL]:
            for condition in rule_set.activation_conditions:
                if condition.lower() in context_str:
                    active_sets.append(rule_set)
                    break
        
        # Add emergent sets if patterns detected
        for rule_set in self.rule_layers[RuleLayer.EMERGENT]:
            for condition in rule_set.activation_conditions:
                if condition.lower() in context_str:
                    active_sets.append(rule_set)
                    break
        
        return active_sets
    
    def get_active_rules(self, context: Dict) -> List[RuleDefinition]:
        """Get all active rules based on context."""
        
        active_sets = self.get_active_rule_sets(context)
        active_rules = []
        
        for rule_set in active_sets:
            active_rules.extend(rule_set.rules)
        
        return active_rules
    
    def generate_layer_summary(self) -> Dict:
        """Generate summary of the layered architecture."""
        
        summary = {
            "total_layers": len(self.rule_layers),
            "total_rule_sets": len(self.rule_sets),
            "total_rules": len(self.rule_definitions),
            "layers": {}
        }
        
        for layer, rule_sets in self.rule_layers.items():
            layer_info = {
                "layer_name": layer.value,
                "rule_sets": len(rule_sets),
                "total_rules": sum(len(rs.rules) for rs in rule_sets),
                "purposes": list(set(rs.purpose.value for rs in rule_sets))
            }
            summary["layers"][layer.value] = layer_info
        
        return summary
    
    def validate_architecture(self) -> Dict:
        """Validate the architecture for consistency and completeness."""
        
        validation = {
            "valid": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check foundational layer has essential rules
        foundational_rules = []
        for rule_set in self.rule_layers[RuleLayer.FOUNDATIONAL]:
            foundational_rules.extend(rule_set.rules)
        
        if len(foundational_rules) < 5:
            validation["issues"].append("Foundational layer has too few rules")
            validation["valid"] = False
        
        # Check all rules have dependencies satisfied
        for rule_id, rule in self.rule_definitions.items():
            for dep in rule.dependencies:
                if dep not in self.rule_definitions:
                    validation["issues"].append(f"Rule {rule_id} has unsatisfied dependency: {dep}")
                    validation["valid"] = False
        
        # Check operational layer coverage
        operational_purposes = set()
        for rule_set in self.rule_layers[RuleLayer.OPERATIONAL]:
            operational_purposes.add(rule_set.purpose)
        
        expected_purposes = {
            RuleSetPurpose.AGILE_COORDINATION,
            RuleSetPurpose.CODE_DEVELOPMENT, 
            RuleSetPurpose.TESTING_VALIDATION,
            RuleSetPurpose.DOCUMENTATION_EXCELLENCE
        }
        
        missing_purposes = expected_purposes - operational_purposes
        if missing_purposes:
            validation["recommendations"].append(f"Consider adding rule sets for: {missing_purposes}")
        
        return validation

# Global layered architecture system
layered_architecture = LayeredRuleArchitecture()

def get_architecture_summary():
    """Get summary of the layered rule architecture."""
    return layered_architecture.generate_layer_summary()

def get_active_rules_for_context(context: Dict):
    """Get active rules for a given context."""
    return layered_architecture.get_active_rules(context)

def validate_rule_architecture():
    """Validate the rule architecture."""
    return layered_architecture.validate_architecture()

if __name__ == "__main__":
    # Demo the layered architecture
    print("🏗️ LAYERED RULE ARCHITECTURE SYSTEM")
    print("=" * 50)
    
    summary = get_architecture_summary()
    
    print(f"📊 Architecture Summary:")
    print(f"  Total Layers: {summary['total_layers']}")
    print(f"  Total Rule Sets: {summary['total_rule_sets']}")
    print(f"  Total Rules: {summary['total_rules']}")
    print()
    
    for layer_name, layer_info in summary["layers"].items():
        print(f"🏗️ {layer_name.upper()} LAYER:")
        print(f"  Rule Sets: {layer_info['rule_sets']}")
        print(f"  Total Rules: {layer_info['total_rules']}")
        print(f"  Purposes: {', '.join(layer_info['purposes'])}")
        print()
    
    # Test context activation
    print("🎯 CONTEXT ACTIVATION TEST:")
    test_context = {
        "user_message": "@agile implement user authentication with comprehensive testing",
        "files": ["auth.py", "test_auth.py"],
        "keywords": ["@agile", "@code", "@test"]
    }
    
    active_rules = get_active_rules_for_context(test_context)
    active_sets = layered_architecture.get_active_rule_sets(test_context)
    
    print(f"  Context: {test_context}")
    print(f"  Active Rule Sets: {[rs.set_name for rs in active_sets]}")
    print(f"  Active Rules: {len(active_rules)}")
    
    # Validation
    validation = validate_rule_architecture()
    print(f"\n✅ Architecture Valid: {validation['valid']}")
    if validation['issues']:
        print(f"❌ Issues: {validation['issues']}")
    if validation['recommendations']:
        print(f"💡 Recommendations: {validation['recommendations']}")
    
    print("\n🏗️ Layered Rule Architecture System Ready! 🏗️")
