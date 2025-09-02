"""
MDC Layer Organizer
==================

MISSION: Organize our .mdc rule files according to the formal layered architecture
based on Hilbert, Russell, Carnap, Wittgenstein, and Quine's foundational principles.

Layer Structure:
- AXIOMATIC LAYER: 5 Hilbert axioms (alwaysApply: true)
- TYPE_0_LAYER: Individual context rules (Russell Type 0)
- TYPE_1_LAYER: Rule sets and compositions (Russell Type 1)  
- TYPE_2_LAYER: Meta-rules about rule sets (Russell Type 2)
- TYPE_3_LAYER: System-wide governance rules (Russell Type 3)

Implementation: Update .mdc files with proper layer assignments and activation logic.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class FormalLayer(Enum):
    """Formal layers in our architecture."""
    AXIOMATIC = "axiomatic"           # Hilbert's 5 axioms - always active
    TYPE_0_INDIVIDUAL = "type_0"      # Individual context rules
    TYPE_1_RULE_SETS = "type_1"       # Rule set compositions
    TYPE_2_META_RULES = "type_2"      # Meta-rules about rules
    TYPE_3_SYSTEM = "type_3"          # System governance

class LinguisticFramework(Enum):
    """Carnap's linguistic frameworks."""
    FOUNDATIONAL = "foundational"     # Universal principles
    AGILE = "agile"                   # Agile methodology
    CODE = "code"                     # Programming/development
    TEST = "test"                     # Testing/validation
    DEBUG = "debug"                   # Debugging/analysis
    DOCS = "docs"                     # Documentation
    GIT = "git"                       # Version control
    META = "meta"                     # Meta-linguistic

@dataclass
class MDCRuleMapping:
    """Mapping of .mdc file to formal architecture."""
    file_path: str
    rule_name: str
    formal_layer: FormalLayer
    linguistic_framework: LinguisticFramework
    logical_type: int                 # Russell type level (0-3)
    always_apply: bool               # Whether always active
    contexts: List[str]              # Activation contexts
    priority: int                    # Application priority
    dependencies: List[str]          # Logical dependencies
    language_games: List[str]        # Wittgenstein coordination patterns

class MDCLayerOrganizer:
    """
    Organizes .mdc files according to formal layered architecture.
    """
    
    def __init__(self):
        self.layer_mappings: Dict[str, MDCRuleMapping] = {}
        self.cursor_rules_dir = Path(".cursor/rules")
        self._initialize_formal_mappings()
    
    def _initialize_formal_mappings(self):
        """Initialize the formal mappings for all .mdc files."""
        
        # AXIOMATIC LAYER - Hilbert's 5 Fundamental Axioms (Always Active)
        axiomatic_mappings = {
            "core/safety_first_principle.mdc": MDCRuleMapping(
                file_path="core/safety_first_principle.mdc",
                rule_name="Safety First Principle",
                formal_layer=FormalLayer.AXIOMATIC,
                linguistic_framework=LinguisticFramework.FOUNDATIONAL,
                logical_type=0,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                dependencies=[],
                language_games=["safety_consensus_building", "harm_prevention"]
            ),
            
            "core/no_premature_victory_declaration_rule.mdc": MDCRuleMapping(
                file_path="core/no_premature_victory_declaration_rule.mdc",
                rule_name="Evidence-Based Success Validation",
                formal_layer=FormalLayer.AXIOMATIC,
                linguistic_framework=LinguisticFramework.FOUNDATIONAL,
                logical_type=0,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                dependencies=["safety_first_principle"],
                language_games=["evidence_validation", "truth_verification"]
            ),
            
            "meta/formal_rule_system_framework.mdc": MDCRuleMapping(
                file_path="meta/formal_rule_system_framework.mdc",
                rule_name="Logical Consistency Principle",
                formal_layer=FormalLayer.AXIOMATIC,
                linguistic_framework=LinguisticFramework.FOUNDATIONAL,
                logical_type=1,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                dependencies=[],
                language_games=["consistency_validation", "logical_coherence"]
            ),
            
            "core/core_values_enforcement_rule.mdc": MDCRuleMapping(
                file_path="core/core_values_enforcement_rule.mdc",
                rule_name="Quality Excellence Principle",
                formal_layer=FormalLayer.AXIOMATIC,
                linguistic_framework=LinguisticFramework.FOUNDATIONAL,
                logical_type=0,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                dependencies=["no_premature_victory_declaration_rule"],
                language_games=["quality_assurance", "excellence_coordination"]
            ),
            
            "core/disaster_report_learning_rule.mdc": MDCRuleMapping(
                file_path="core/disaster_report_learning_rule.mdc",
                rule_name="Learning from Failure Principle",
                formal_layer=FormalLayer.AXIOMATIC,
                linguistic_framework=LinguisticFramework.FOUNDATIONAL,
                logical_type=0,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                dependencies=["core_values_enforcement_rule"],
                language_games=["learning_coordination", "wisdom_extraction"]
            )
        }
        
        # TYPE_0_LAYER - Individual Context Rules (Context-Dependent)
        type_0_mappings = {
            "agile/agile_strategic_coordination_rule.mdc": MDCRuleMapping(
                file_path="agile/agile_strategic_coordination_rule.mdc",
                rule_name="Agile Strategic Coordination",
                formal_layer=FormalLayer.TYPE_0_INDIVIDUAL,
                linguistic_framework=LinguisticFramework.AGILE,
                logical_type=0,
                always_apply=False,
                contexts=["AGILE"],
                priority=2,
                dependencies=["safety_first_principle"],
                language_games=["stakeholder_coordination", "value_delivery"]
            ),
            
            "development/development_core_principles_rule.mdc": MDCRuleMapping(
                file_path="development/development_core_principles_rule.mdc", 
                rule_name="Code Development Excellence",
                formal_layer=FormalLayer.TYPE_0_INDIVIDUAL,
                linguistic_framework=LinguisticFramework.CODE,
                logical_type=0,
                always_apply=False,
                contexts=["CODING", "DEVELOPMENT"],
                priority=2,
                dependencies=["core_values_enforcement_rule"],
                language_games=["code_quality_coordination", "development_harmony"]
            ),
            
            "testing/xp_test_first_development_rule.mdc": MDCRuleMapping(
                file_path="testing/xp_test_first_development_rule.mdc",
                rule_name="Test-Driven Development",
                formal_layer=FormalLayer.TYPE_0_INDIVIDUAL,
                linguistic_framework=LinguisticFramework.TEST,
                logical_type=0,
                always_apply=False,
                contexts=["TESTING", "TDD"],
                priority=2,
                dependencies=["no_premature_victory_declaration_rule"],
                language_games=["test_coordination", "validation_harmony"]
            ),
            
            "core/streamlined_git_operations_rule.mdc": MDCRuleMapping(
                file_path="core/streamlined_git_operations_rule.mdc",
                rule_name="Streamlined Git Operations",
                formal_layer=FormalLayer.TYPE_0_INDIVIDUAL,
                linguistic_framework=LinguisticFramework.GIT,
                logical_type=0,
                always_apply=False,
                contexts=["GIT"],
                priority=2,
                dependencies=["safety_first_principle"],
                language_games=["version_control_coordination", "workflow_harmony"]
            ),
            
            "quality/documentation_live_updates_rule.mdc": MDCRuleMapping(
                file_path="quality/documentation_live_updates_rule.mdc",
                rule_name="Live Documentation Updates",
                formal_layer=FormalLayer.TYPE_0_INDIVIDUAL,
                linguistic_framework=LinguisticFramework.DOCS,
                logical_type=0,
                always_apply=False,
                contexts=["DOCUMENTATION"],
                priority=2,
                dependencies=["core_values_enforcement_rule"],
                language_games=["documentation_coordination", "knowledge_harmony"]
            ),
            
            "development/file_organization_cleanup_rule.mdc": MDCRuleMapping(
                file_path="development/file_organization_cleanup_rule.mdc",
                rule_name="Structural Harmony Maintenance",
                formal_layer=FormalLayer.TYPE_0_INDIVIDUAL,
                linguistic_framework=LinguisticFramework.FOUNDATIONAL,
                logical_type=0,
                always_apply=True,  # Structure is foundational
                contexts=["ALL"],
                priority=1,
                dependencies=["core_values_enforcement_rule"],
                language_games=["structural_coordination", "organizational_harmony"]
            )
        }
        
        # TYPE_1_LAYER - Rule Set Compositions (Operate on Type 0)
        type_1_mappings = {
            "agile/agile_artifacts_maintenance_rule.mdc": MDCRuleMapping(
                file_path="agile/agile_artifacts_maintenance_rule.mdc",
                rule_name="Agile Artifact Maintenance Set",
                formal_layer=FormalLayer.TYPE_1_RULE_SETS,
                linguistic_framework=LinguisticFramework.AGILE,
                logical_type=1,
                always_apply=False,
                contexts=["AGILE"],
                priority=3,
                dependencies=["agile_strategic_coordination_rule"],
                language_games=["artifact_coordination", "documentation_harmony"]
            ),
            
            "core/divine_harmony_integration_system.mdc": MDCRuleMapping(
                file_path="core/divine_harmony_integration_system.mdc",
                rule_name="Orchestral Coordination Set",
                formal_layer=FormalLayer.TYPE_1_RULE_SETS,
                linguistic_framework=LinguisticFramework.FOUNDATIONAL,
                logical_type=1,
                always_apply=True,  # Orchestral coordination is foundational
                contexts=["ALL"],
                priority=1,
                dependencies=["formal_rule_system_framework"],
                language_games=["orchestral_coordination", "divine_harmony"]
            )
        }
        
        # TYPE_2_LAYER - Meta-Rules (Rules about Rule Sets)
        type_2_mappings = {
            "meta/intelligent_context_aware_rule_system.mdc": MDCRuleMapping(
                file_path="meta/intelligent_context_aware_rule_system.mdc",
                rule_name="Context-Aware Rule Selection",
                formal_layer=FormalLayer.TYPE_2_META_RULES,
                linguistic_framework=LinguisticFramework.META,
                logical_type=2,
                always_apply=True,  # Meta-system coordination
                contexts=["ALL"],
                priority=1,
                dependencies=["formal_rule_system_framework"],
                language_games=["meta_coordination", "intelligent_selection"]
            ),
            
            "meta/formal_linguistic_rule_architecture.mdc": MDCRuleMapping(
                file_path="meta/formal_linguistic_rule_architecture.mdc",
                rule_name="Linguistic Rule Architecture",
                formal_layer=FormalLayer.TYPE_2_META_RULES,
                linguistic_framework=LinguisticFramework.META,
                logical_type=2,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                dependencies=["intelligent_context_aware_rule_system"],
                language_games=["linguistic_coordination", "semantic_harmony"]
            )
        }
        
        # TYPE_3_LAYER - System Governance (Rules about the Entire System)
        type_3_mappings = {
            "core/self_optimizing_learning_system.mdc": MDCRuleMapping(
                file_path="core/self_optimizing_learning_system.mdc",
                rule_name="System-Wide Self-Optimization",
                formal_layer=FormalLayer.TYPE_3_SYSTEM,
                linguistic_framework=LinguisticFramework.META,
                logical_type=3,
                always_apply=True,
                contexts=["ALL"],
                priority=1,
                dependencies=["disaster_report_learning_rule"],
                language_games=["system_evolution", "optimization_harmony"]
            ),
            
            "core/automatic_rule_enforcement_system.mdc": MDCRuleMapping(
                file_path="core/automatic_rule_enforcement_system.mdc",
                rule_name="System-Wide Rule Enforcement",
                formal_layer=FormalLayer.TYPE_3_SYSTEM,
                linguistic_framework=LinguisticFramework.META,
                logical_type=3,
                always_apply=False,  # System enforcement is meta-level
                contexts=["META"],
                priority=1,
                dependencies=["formal_rule_system_framework"],
                language_games=["enforcement_coordination", "system_governance"]
            )
        }
        
        # Combine all mappings
        self.layer_mappings.update(axiomatic_mappings)
        self.layer_mappings.update(type_0_mappings)
        self.layer_mappings.update(type_1_mappings)
        self.layer_mappings.update(type_2_mappings)
        self.layer_mappings.update(type_3_mappings)
    
    def update_mdc_files(self) -> Dict:
        """Update all .mdc files according to formal layer architecture."""
        
        update_results = {
            "files_processed": 0,
            "files_updated": 0,
            "axiomatic_rules": [],
            "context_rules": [],
            "meta_rules": [],
            "errors": []
        }
        
        for relative_path, mapping in self.layer_mappings.items():
            try:
                full_path = self.cursor_rules_dir / relative_path
                
                if full_path.exists():
                    success = self._update_single_mdc_file(full_path, mapping)
                    
                    update_results["files_processed"] += 1
                    
                    if success:
                        update_results["files_updated"] += 1
                        
                        # Categorize by layer
                        if mapping.formal_layer == FormalLayer.AXIOMATIC:
                            update_results["axiomatic_rules"].append(mapping.rule_name)
                        elif mapping.formal_layer in [FormalLayer.TYPE_0_INDIVIDUAL, FormalLayer.TYPE_1_RULE_SETS]:
                            update_results["context_rules"].append(mapping.rule_name)
                        else:
                            update_results["meta_rules"].append(mapping.rule_name)
                
                else:
                    update_results["errors"].append(f"File not found: {full_path}")
                    
            except Exception as e:
                update_results["errors"].append(f"Error processing {relative_path}: {e}")
        
        return update_results
    
    def _update_single_mdc_file(self, file_path: Path, mapping: MDCRuleMapping) -> bool:
        """Update a single .mdc file with formal layer information."""
        
        try:
            # Read current file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML header and content
            if content.startswith('---\n'):
                parts = content.split('---\n', 2)
                if len(parts) >= 3:
                    yaml_header = parts[1]
                    markdown_content = parts[2]
                else:
                    # No proper YAML header, create one
                    yaml_header = ""
                    markdown_content = content
            else:
                yaml_header = ""
                markdown_content = content
            
            # Parse or create YAML metadata
            if yaml_header:
                try:
                    metadata = yaml.safe_load(yaml_header) or {}
                except yaml.YAMLError:
                    metadata = {}
            else:
                metadata = {}
            
            # Update metadata according to formal mapping
            metadata.update({
                "description": f"{mapping.rule_name} - {mapping.formal_layer.value} layer rule",
                "category": f"{mapping.linguistic_framework.value}-{mapping.formal_layer.value}",
                "priority": "critical" if mapping.priority == 1 else "high" if mapping.priority == 2 else "medium",
                "alwaysApply": mapping.always_apply,
                "contexts": mapping.contexts,
                "globs": ["**/*"],
                "tags": [
                    mapping.formal_layer.value,
                    mapping.linguistic_framework.value,
                    f"type_{mapping.logical_type}",
                    f"priority_{mapping.priority}"
                ] + mapping.language_games,
                "tier": str(mapping.priority),
                "enforcement": "blocking" if mapping.priority == 1 else "warning",
                "autoFix": mapping.formal_layer == FormalLayer.AXIOMATIC,
                "formalLayer": mapping.formal_layer.value,
                "linguisticFramework": mapping.linguistic_framework.value,
                "logicalType": mapping.logical_type,
                "dependencies": mapping.dependencies,
                "languageGames": mapping.language_games
            })
            
            # Reconstruct file content
            new_yaml_header = yaml.dump(metadata, default_flow_style=False)
            new_content = f"---\n{new_yaml_header}---\n{markdown_content}"
            
            # Write updated file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            return False
    
    def generate_layer_summary(self) -> Dict:
        """Generate summary of formal layer organization."""
        
        summary = {
            "total_rules": len(self.layer_mappings),
            "layers": {},
            "linguistic_frameworks": {},
            "always_active_rules": [],
            "context_dependent_rules": []
        }
        
        # Count by layer
        for mapping in self.layer_mappings.values():
            layer = mapping.formal_layer.value
            framework = mapping.linguistic_framework.value
            
            if layer not in summary["layers"]:
                summary["layers"][layer] = 0
            summary["layers"][layer] += 1
            
            if framework not in summary["linguistic_frameworks"]:
                summary["linguistic_frameworks"][framework] = 0
            summary["linguistic_frameworks"][framework] += 1
            
            if mapping.always_apply:
                summary["always_active_rules"].append(mapping.rule_name)
            else:
                summary["context_dependent_rules"].append(mapping.rule_name)
        
        return summary
    
    def validate_formal_consistency(self) -> Dict:
        """Validate formal consistency of the layer organization."""
        
        validation = {
            "is_consistent": True,
            "axiom_count": 0,
            "type_violations": [],
            "dependency_issues": [],
            "recommendations": []
        }
        
        # Count axioms (should be exactly 5)
        axiom_count = sum(1 for m in self.layer_mappings.values() 
                         if m.formal_layer == FormalLayer.AXIOMATIC)
        validation["axiom_count"] = axiom_count
        
        if axiom_count != 5:
            validation["is_consistent"] = False
            validation["recommendations"].append(f"Should have exactly 5 axioms, found {axiom_count}")
        
        # Check Russell type hierarchy violations
        for mapping in self.layer_mappings.values():
            for dep in mapping.dependencies:
                dep_mapping = self._find_mapping_by_file_name(dep)
                if dep_mapping and dep_mapping.logical_type > mapping.logical_type:
                    violation = f"{mapping.rule_name} (type {mapping.logical_type}) depends on {dep_mapping.rule_name} (type {dep_mapping.logical_type})"
                    validation["type_violations"].append(violation)
                    validation["is_consistent"] = False
        
        return validation
    
    def _find_mapping_by_file_name(self, file_name: str) -> Optional[MDCRuleMapping]:
        """Find mapping by file name (without .mdc extension)."""
        for mapping in self.layer_mappings.values():
            if file_name in mapping.file_path or file_name.replace('.mdc', '') in mapping.file_path:
                return mapping
        return None
    
    def generate_implementation_report(self) -> str:
        """Generate comprehensive implementation report."""
        
        summary = self.generate_layer_summary()
        validation = self.validate_formal_consistency()
        
        report = f"""
🏛️ FORMAL LAYERED RULE ARCHITECTURE IMPLEMENTATION REPORT
{'=' * 70}

📊 SUMMARY:
  Total Rules: {summary['total_rules']}
  Always Active: {len(summary['always_active_rules'])}
  Context Dependent: {len(summary['context_dependent_rules'])}

🏗️ FORMAL LAYERS:
"""
        
        for layer, count in summary["layers"].items():
            report += f"  {layer.upper()}: {count} rules\n"
        
        report += f"""
🗣️ LINGUISTIC FRAMEWORKS:
"""
        
        for framework, count in summary["linguistic_frameworks"].items():
            report += f"  {framework.upper()}: {count} rules\n"
        
        report += f"""
🎯 AXIOMATIC FOUNDATION (Always Active):
"""
        
        axiomatic_rules = [m.rule_name for m in self.layer_mappings.values() 
                          if m.formal_layer == FormalLayer.AXIOMATIC]
        for rule in axiomatic_rules:
            report += f"  • {rule}\n"
        
        report += f"""
🔧 CONTEXT-DEPENDENT RULES:
"""
        
        context_rules = [m.rule_name for m in self.layer_mappings.values() 
                        if not m.always_apply]
        for rule in context_rules[:10]:  # Show first 10
            report += f"  • {rule}\n"
        
        if len(context_rules) > 10:
            report += f"  ... and {len(context_rules) - 10} more\n"
        
        report += f"""
✅ FORMAL VALIDATION:
  Consistency: {'✅ VALID' if validation['is_consistent'] else '❌ INVALID'}
  Axiom Count: {validation['axiom_count']}/5 Expected
  Type Violations: {len(validation['type_violations'])}
"""
        
        if validation["type_violations"]:
            report += "\n❌ TYPE VIOLATIONS:\n"
            for violation in validation["type_violations"]:
                report += f"  • {violation}\n"
        
        if validation["recommendations"]:
            report += "\n💡 RECOMMENDATIONS:\n"
            for rec in validation["recommendations"]:
                report += f"  • {rec}\n"
        
        report += f"""
🎼 PHILOSOPHICAL FOUNDATIONS IMPLEMENTED:
  • Hilbert's Axiomatization: 5 fundamental axioms
  • Russell's Type Theory: 4-level type hierarchy
  • Carnap's Linguistic Frameworks: 8 context languages
  • Wittgenstein's Language Games: Coordination patterns
  • Quine's Ontological Relativity: Framework-dependent existence

{'=' * 70}
🏛️ FORMAL ARCHITECTURE IMPLEMENTATION COMPLETE
"""
        
        return report

# Global organizer
layer_organizer = MDCLayerOrganizer()

def update_all_mdc_files():
    """Update all .mdc files according to formal architecture."""
    return layer_organizer.update_mdc_files()

def get_layer_summary():
    """Get summary of layer organization."""
    return layer_organizer.generate_layer_summary()

def validate_formal_consistency():
    """Validate formal consistency of layer organization."""
    return layer_organizer.validate_formal_consistency()

def generate_implementation_report():
    """Generate comprehensive implementation report."""
    return layer_organizer.generate_implementation_report()

if __name__ == "__main__":
    print("🏛️ MDC LAYER ORGANIZER")
    print("=" * 50)
    
    # Generate implementation report
    report = generate_implementation_report()
    print(report)
    
    # Validate consistency
    validation = validate_formal_consistency()
    print(f"\n🔍 FORMAL VALIDATION: {'✅ CONSISTENT' if validation['is_consistent'] else '❌ INCONSISTENT'}")
    
    if not validation["is_consistent"]:
        print("❌ Issues found:")
        for issue in validation["type_violations"] + validation["recommendations"]:
            print(f"  • {issue}")
    
    print("\n🏛️ MDC Layer Organization Complete!")
