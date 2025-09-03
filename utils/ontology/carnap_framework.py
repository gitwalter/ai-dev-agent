#!/usr/bin/env python3
"""
Carnap's Ontological Framework Implementation
===========================================

Implementation of Rudolf Carnap's approach to logical frameworks and
ontological relativity for scientific language construction.

Based on Carnap's principles:
1. "The Logical Structure of the World" (1928)
2. "Logical Syntax of Language" (1934)  
3. "Meaning and Necessity" (1947)

CORE PRINCIPLE: Ontological questions are questions about linguistic frameworks,
not about the absolute nature of reality. The choice of linguistic framework
is pragmatic, based on efficiency and purpose.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

class OntologicalLevel(Enum):
    """Carnap's ontological levels with logical precedence."""
    OBSERVATION_LANGUAGE = "observation"      # Physical-thing language
    THEORETICAL_LANGUAGE = "theoretical"     # Scientific theoretical constructs
    LOGICAL_LANGUAGE = "logical"            # Pure logical-mathematical
    PRAGMATIC_LANGUAGE = "pragmatic"        # Practical decision-making

@dataclass
class LinguisticFramework:
    """Carnap's linguistic framework definition."""
    name: str
    level: OntologicalLevel
    logical_syntax: Dict[str, Any]
    formation_rules: List[str]
    transformation_rules: List[str]
    semantic_rules: Optional[Dict[str, Any]]
    pragmatic_efficiency: float
    domain_applicability: Set[str]

@dataclass
class ConstitutionSystemStep:
    """Step in Carnap's constitution system (Konstitutionssystem)."""
    level: int
    object_type: str
    construction_rule: str
    base_objects: List[str]
    logical_form: str

class CarnapOntologicalFramework:
    """
    Implementation of Carnap's scientific approach to ontological frameworks.
    
    Provides systematic method for:
    1. Constructing linguistic frameworks
    2. Defining logical syntax rules
    3. Establishing translation protocols
    4. Pragmatic framework selection
    """
    
    def __init__(self):
        self.frameworks = {}
        self.constitution_system = []
        self.translation_protocols = {}
        self.current_framework = None
        
        # Initialize core frameworks
        self._initialize_core_frameworks()
        
    def _initialize_core_frameworks(self):
        """Initialize core linguistic frameworks following Carnap's methodology."""
        
        # Technical Framework (Physical-thing language)
        self.frameworks["technical"] = LinguisticFramework(
            name="Technical Implementation Framework",
            level=OntologicalLevel.OBSERVATION_LANGUAGE,
            logical_syntax={
                "primitive_terms": ["function", "class", "interface", "algorithm"],
                "logical_constants": ["implements", "extends", "calls", "returns"],
                "formation_rules": ["object_formation", "predicate_formation"],
                "quantifiers": ["all_instances", "some_instances", "no_instances"]
            },
            formation_rules=[
                "If X is a function and Y is a parameter, then X(Y) is well-formed",
                "If X implements Y, then X has all properties of Y",
                "If X extends Y, then X is a subtype of Y"
            ],
            transformation_rules=[
                "Modus ponens for function calls",
                "Transitivity for inheritance relations",
                "Substitution for interface implementations"
            ],
            semantic_rules={
                "truth_conditions": "Based on execution semantics",
                "reference_relation": "Functions refer to computational processes",
                "satisfaction_conditions": "Test cases determine satisfaction"
            },
            pragmatic_efficiency=0.9,
            domain_applicability={"software_development", "system_architecture", "implementation"}
        )
        
        # Business Framework (Rational reconstruction of business concepts)
        self.frameworks["business"] = LinguisticFramework(
            name="Business Value Framework",
            level=OntologicalLevel.THEORETICAL_LANGUAGE,
            logical_syntax={
                "primitive_terms": ["requirement", "stakeholder", "value", "outcome"],
                "logical_constants": ["provides", "requires", "measures", "achieves"],
                "formation_rules": ["requirement_formation", "value_formation"],
                "quantifiers": ["all_stakeholders", "some_benefits", "measurable_outcomes"]
            },
            formation_rules=[
                "If X is a requirement and Y is a stakeholder, then Y needs X is well-formed",
                "If X provides Y, then Y is valuable to some stakeholder",
                "If X achieves Y, then Y is a measurable outcome"
            ],
            transformation_rules=[
                "Value transitivity: If X provides Y and Y achieves Z, then X contributes to Z",
                "Requirement inheritance: If X requires Y and Y requires Z, then X requires Z"
            ],
            semantic_rules={
                "truth_conditions": "Based on stakeholder satisfaction",
                "reference_relation": "Requirements refer to business objectives",
                "satisfaction_conditions": "Acceptance criteria determine satisfaction"
            },
            pragmatic_efficiency=0.8,
            domain_applicability={"business_analysis", "requirements_engineering", "stakeholder_management"}
        )
        
        # Philosophical Framework (Theoretical constructs)
        self.frameworks["philosophical"] = LinguisticFramework(
            name="Philosophical Principles Framework",
            level=OntologicalLevel.THEORETICAL_LANGUAGE,
            logical_syntax={
                "primitive_terms": ["principle", "value", "purpose", "excellence"],
                "logical_constants": ["embodies", "inspires", "guides", "manifests"],
                "formation_rules": ["principle_formation", "value_formation"],
                "quantifiers": ["universal_principles", "contextual_values", "aspirational_goals"]
            },
            formation_rules=[
                "If X is a principle and Y is an action, then Y embodies X is well-formed",
                "If X inspires Y, then Y tends toward excellence",
                "If X guides Y, then Y aligns with principle X"
            ],
            transformation_rules=[
                "Principle application: If principle P guides action A, and A leads to B, then B reflects P",
                "Value inheritance: If X embodies value V, and X influences Y, then Y tends toward V"
            ],
            semantic_rules={
                "truth_conditions": "Based on value alignment assessment",
                "reference_relation": "Principles refer to aspirational standards",
                "satisfaction_conditions": "Cultural resonance determines satisfaction"
            },
            pragmatic_efficiency=0.7,
            domain_applicability={"team_culture", "vision_creation", "inspirational_guidance", "cultural_development"}
        )
        
        # Meta-Framework (Logical-mathematical level)
        self.frameworks["meta"] = LinguisticFramework(
            name="Meta-Ontological Framework",
            level=OntologicalLevel.LOGICAL_LANGUAGE,
            logical_syntax={
                "primitive_terms": ["framework", "translation", "protocol", "consistency"],
                "logical_constants": ["translates_to", "consistent_with", "reduces_to", "equivalent_to"],
                "formation_rules": ["framework_formation", "translation_formation"],
                "quantifiers": ["all_frameworks", "some_translations", "consistent_mappings"]
            },
            formation_rules=[
                "If F1 and F2 are frameworks, then translation(F1, F2) is well-formed",
                "If T is a translation, then consistency(T) is decidable",
                "If F is a framework, then efficiency(F, domain) is measurable"
            ],
            transformation_rules=[
                "Translation transitivity: If F1 translates to F2 and F2 translates to F3, then F1 translates to F3",
                "Consistency preservation: If F1 is consistent and F1 translates to F2, then F2 is consistent"
            ],
            semantic_rules={
                "truth_conditions": "Based on logical consistency",
                "reference_relation": "Meta-terms refer to linguistic structures",
                "satisfaction_conditions": "Formal verification determines satisfaction"
            },
            pragmatic_efficiency=1.0,
            domain_applicability={"ontological_analysis", "framework_design", "translation_protocols"}
        )
    
    def constitute_object(self, object_name: str, base_objects: List[str], 
                         construction_rule: str, logical_form: str) -> ConstitutionSystemStep:
        """
        Constitute a higher-level object from base objects.
        Following Carnap's constitution system methodology.
        """
        
        level = len(self.constitution_system) + 1
        
        step = ConstitutionSystemStep(
            level=level,
            object_type=object_name,
            construction_rule=construction_rule,
            base_objects=base_objects,
            logical_form=logical_form
        )
        
        self.constitution_system.append(step)
        return step
    
    def define_translation_protocol(self, source_framework: str, target_framework: str, 
                                  translation_rules: List[str]) -> Dict[str, Any]:
        """
        Define scientific translation protocol between frameworks.
        Based on Carnap's approach to inter-linguistic translation.
        """
        
        if source_framework not in self.frameworks or target_framework not in self.frameworks:
            raise ValueError(f"Unknown framework: {source_framework} or {target_framework}")
        
        source = self.frameworks[source_framework]
        target = self.frameworks[target_framework]
        
        protocol = {
            "source": source_framework,
            "target": target_framework,
            "translation_rules": translation_rules,
            "logical_mapping": self._create_logical_mapping(source, target),
            "efficiency_preservation": self._calculate_efficiency_preservation(source, target),
            "consistency_verification": self._verify_translation_consistency(source, target, translation_rules)
        }
        
        protocol_key = f"{source_framework}_to_{target_framework}"
        self.translation_protocols[protocol_key] = protocol
        
        return protocol
    
    def _create_logical_mapping(self, source: LinguisticFramework, target: LinguisticFramework) -> Dict[str, str]:
        """Create logical mapping between framework terms following Carnap's method."""
        
        mapping = {}
        
        # Map primitive terms with logical relationships
        for source_term in source.logical_syntax["primitive_terms"]:
            # Find corresponding term in target framework
            target_term = self._find_corresponding_term(source_term, target)
            if target_term:
                mapping[source_term] = target_term
        
        # Map logical constants
        for source_constant in source.logical_syntax["logical_constants"]:
            target_constant = self._find_corresponding_constant(source_constant, target)
            if target_constant:
                mapping[source_constant] = target_constant
        
        return mapping
    
    def _find_corresponding_term(self, source_term: str, target: LinguisticFramework) -> Optional[str]:
        """Find corresponding term in target framework using semantic similarity."""
        
        # Semantic correspondence mappings
        correspondences = {
            # Technical to Business
            ("function", "business"): "capability",
            ("class", "business"): "entity",
            ("interface", "business"): "contract",
            ("algorithm", "business"): "process",
            
            # Business to Technical
            ("requirement", "technical"): "specification",
            ("stakeholder", "technical"): "user",
            ("value", "technical"): "output",
            ("outcome", "technical"): "result",
            
            # Technical to Philosophical
            ("function", "philosophical"): "purpose",
            ("optimization", "philosophical"): "excellence",
            ("implementation", "philosophical"): "manifestation",
            
            # Philosophical to Technical
            ("principle", "technical"): "rule",
            ("value", "technical"): "constant",
            ("excellence", "technical"): "optimization"
        }
        
        key = (source_term, target.name.split()[0].lower())
        return correspondences.get(key)
    
    def _find_corresponding_constant(self, source_constant: str, target: LinguisticFramework) -> Optional[str]:
        """Find corresponding logical constant in target framework."""
        
        constant_mappings = {
            # Technical to Business
            ("implements", "business"): "provides",
            ("returns", "business"): "achieves",
            ("calls", "business"): "requires",
            
            # Business to Technical
            ("provides", "technical"): "implements",
            ("achieves", "technical"): "returns",
            ("requires", "technical"): "depends_on"
        }
        
        target_name = target.name.split()[0].lower()
        return constant_mappings.get((source_constant, target_name))
    
    def _calculate_efficiency_preservation(self, source: LinguisticFramework, target: LinguisticFramework) -> float:
        """Calculate how much pragmatic efficiency is preserved in translation."""
        
        # Efficiency loss occurs when translating between different ontological levels
        level_distances = {
            (OntologicalLevel.OBSERVATION_LANGUAGE, OntologicalLevel.THEORETICAL_LANGUAGE): 0.1,
            (OntologicalLevel.THEORETICAL_LANGUAGE, OntologicalLevel.LOGICAL_LANGUAGE): 0.05,
            (OntologicalLevel.OBSERVATION_LANGUAGE, OntologicalLevel.LOGICAL_LANGUAGE): 0.15
        }
        
        distance = level_distances.get((source.level, target.level), 0.0)
        preservation = 1.0 - distance
        
        return max(0.0, min(1.0, preservation))
    
    def _verify_translation_consistency(self, source: LinguisticFramework, target: LinguisticFramework, 
                                      rules: List[str]) -> bool:
        """Verify that translation maintains logical consistency."""
        
        # Check that formation rules are preserved
        for rule in source.formation_rules:
            if not self._rule_translatable(rule, target):
                return False
        
        # Check that transformation rules maintain validity
        for rule in source.transformation_rules:
            if not self._transformation_preserves_validity(rule, target):
                return False
        
        return True
    
    def _rule_translatable(self, rule: str, target: LinguisticFramework) -> bool:
        """Check if a formation rule can be translated to target framework."""
        
        # Extract terms from rule and check if they have correspondences
        terms = self._extract_terms_from_rule(rule)
        
        for term in terms:
            if not self._find_corresponding_term(term, target):
                return False
        
        return True
    
    def _transformation_preserves_validity(self, rule: str, target: LinguisticFramework) -> bool:
        """Check if transformation rule preserves logical validity in target."""
        
        # For now, assume transformation rules preserve validity
        # In full implementation, this would involve formal logical verification
        return True
    
    def _extract_terms_from_rule(self, rule: str) -> List[str]:
        """Extract terms from a formation or transformation rule."""
        
        # Simple extraction - in full implementation would use proper parsing
        words = rule.lower().split()
        technical_terms = {"function", "class", "interface", "requirement", "stakeholder", "principle"}
        
        return [word for word in words if word in technical_terms]
    
    def select_optimal_framework(self, domain: str, efficiency_threshold: float = 0.7) -> Optional[str]:
        """
        Select optimal framework for domain using Carnap's pragmatic approach.
        Framework selection is based on efficiency for intended purpose.
        """
        
        candidates = []
        
        for name, framework in self.frameworks.items():
            if domain in framework.domain_applicability and framework.pragmatic_efficiency >= efficiency_threshold:
                candidates.append((name, framework.pragmatic_efficiency))
        
        if not candidates:
            return None
        
        # Select framework with highest efficiency
        optimal = max(candidates, key=lambda x: x[1])
        return optimal[0]
    
    def generate_carnap_analysis(self, domain: str) -> Dict[str, Any]:
        """
        Generate Carnapian analysis of ontological commitments for domain.
        """
        
        optimal_framework = self.select_optimal_framework(domain)
        
        if not optimal_framework:
            return {"error": f"No suitable framework found for domain: {domain}"}
        
        framework = self.frameworks[optimal_framework]
        
        analysis = {
            "domain": domain,
            "optimal_framework": optimal_framework,
            "ontological_level": framework.level.value,
            "logical_syntax": framework.logical_syntax,
            "pragmatic_efficiency": framework.pragmatic_efficiency,
            "constitution_steps": [
                step for step in self.constitution_system 
                if domain in step.object_type.lower()
            ],
            "available_translations": [
                key for key in self.translation_protocols.keys() 
                if key.startswith(optimal_framework)
            ],
            "carnapian_justification": f"Framework selected based on pragmatic efficiency ({framework.pragmatic_efficiency}) and domain applicability"
        }
        
        return analysis
    
    def get_framework_relationships(self) -> Dict[str, Any]:
        """Get complete map of framework relationships following Carnap's methodology."""
        
        return {
            "frameworks": {name: {
                "level": fw.level.value,
                "efficiency": fw.pragmatic_efficiency,
                "domains": list(fw.domain_applicability)
            } for name, fw in self.frameworks.items()},
            "translation_protocols": list(self.translation_protocols.keys()),
            "constitution_system_levels": len(self.constitution_system),
            "ontological_hierarchy": [level.value for level in OntologicalLevel]
        }

# Global Carnap framework instance
_carnap_framework = None

def get_carnap_framework() -> CarnapOntologicalFramework:
    """Get the global Carnap ontological framework instance."""
    global _carnap_framework
    if _carnap_framework is None:
        _carnap_framework = CarnapOntologicalFramework()
    return _carnap_framework

if __name__ == "__main__":
    # Test Carnap framework implementation
    print("🧪 Testing Carnap Ontological Framework")
    
    framework = CarnapOntologicalFramework()
    
    # Test framework selection
    print("\n📋 Testing Framework Selection:")
    domains = ["software_development", "business_analysis", "team_culture", "ontological_analysis"]
    
    for domain in domains:
        analysis = framework.generate_carnap_analysis(domain)
        if "error" not in analysis:
            print(f"   {domain} → {analysis['optimal_framework']} (efficiency: {analysis['pragmatic_efficiency']:.1f})")
        else:
            print(f"   {domain} → {analysis['error']}")
    
    # Test translation protocol
    print("\n🔄 Testing Translation Protocol:")
    protocol = framework.define_translation_protocol(
        "technical", "business",
        ["Map functions to capabilities", "Map classes to entities", "Map implementations to provisions"]
    )
    print(f"   Technical → Business protocol created")
    print(f"   Efficiency preservation: {protocol['efficiency_preservation']:.1f}")
    
    # Test constitution system
    print("\n🏗️ Testing Constitution System:")
    step = framework.constitute_object(
        "software_component",
        ["function", "interface"],
        "A software component is constituted by functions implementing interfaces",
        "∀x (SoftwareComponent(x) ↔ ∃f,i (Function(f) ∧ Interface(i) ∧ implements(f,i) ∧ constitutes(f,i,x)))"
    )
    print(f"   Constituted: {step.object_type} at level {step.level}")
    
    # Test framework relationships
    relationships = framework.get_framework_relationships()
    print(f"\n📊 Framework Relationships:")
    print(f"   Frameworks: {len(relationships['frameworks'])}")
    print(f"   Translation protocols: {len(relationships['translation_protocols'])}")
    print(f"   Constitution levels: {relationships['constitution_system_levels']}")
    
    print("\n✅ Carnap Ontological Framework: Scientific and Systematic!")
