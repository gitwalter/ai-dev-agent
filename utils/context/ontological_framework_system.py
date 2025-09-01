#!/usr/bin/env python3
"""
Ontological Framework System for Clean Perspective Switching
============================================================

Implements pure ontological transitions between distinct perspective frameworks.
Each mode represents a complete ontological framework with its own language system,
truth criteria, and conceptual boundaries.

No mixing of ontologies - only clean, complete perspective switches.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class LanguageSystem:
    """Language system definition for an ontological framework."""
    primary_concepts: List[str]
    truth_criteria: str
    reasoning_pattern: str
    valid_expressions: List[str]
    invalid_expressions: List[str]


@dataclass
class MeaningStructure:
    """Meaning structure definition for an ontological framework."""
    success_definition: str
    problem_definition: str
    solution_approach: str
    quality_criteria: str


@dataclass
class ConceptualBoundaries:
    """Conceptual boundaries definition for an ontological framework."""
    what_exists: List[str]
    what_matters: List[str]
    time_horizon: str
    success_metrics: List[str]


@dataclass
class OntologicalFramework:
    """
    Complete ontological framework representing a distinct perspective.
    
    Each framework is a complete world of meaning with its own:
    - Language system (how to speak and reason)
    - Meaning structures (what success/failure/quality mean)
    - Conceptual boundaries (what exists and matters)
    """
    name: str
    world_view: str
    language_system: LanguageSystem
    meaning_structure: MeaningStructure
    conceptual_boundaries: ConceptualBoundaries
    keywords: List[str]
    
    def __post_init__(self):
        self.active = False
        self.activation_time = None
    
    def activate(self) -> None:
        """Activate this complete ontological framework."""
        self.active = True
        self.activation_time = datetime.now()
        print(f"🔄 Activated {self.name} ontological framework")
        print(f"   World View: {self.world_view}")
        print(f"   Primary Concepts: {self.language_system.primary_concepts}")
    
    def deactivate(self) -> None:
        """Completely deactivate this ontological framework."""
        self.active = False
        self.activation_time = None
        print(f"⏹️ Deactivated {self.name} ontological framework")
    
    def validate_expression(self, expression: str) -> Dict[str, Any]:
        """
        Validate if an expression is valid within this ontological framework.
        
        Returns validation result with reasoning.
        """
        if not self.active:
            return {
                "valid": False,
                "reason": "Framework not active",
                "framework": self.name
            }
        
        expression_lower = expression.lower()
        
        # Check for invalid expressions
        for invalid in self.language_system.invalid_expressions:
            if invalid.lower() in expression_lower:
                return {
                    "valid": False,
                    "reason": f"Contains invalid concept: '{invalid}'",
                    "framework": self.name,
                    "ontological_violation": True
                }
        
        # Check for valid concepts
        concept_matches = []
        for concept in self.language_system.primary_concepts:
            if concept.lower() in expression_lower:
                concept_matches.append(concept)
        
        # Check for valid expressions
        expression_matches = []
        for valid_expr in self.language_system.valid_expressions:
            if valid_expr.lower() in expression_lower:
                expression_matches.append(valid_expr)
        
        has_valid_concepts = len(concept_matches) > 0
        has_valid_expressions = len(expression_matches) > 0
        
        return {
            "valid": has_valid_concepts or has_valid_expressions,
            "reason": f"Matches concepts: {concept_matches}, expressions: {expression_matches}",
            "framework": self.name,
            "concept_matches": concept_matches,
            "expression_matches": expression_matches,
            "alignment_score": (len(concept_matches) + len(expression_matches)) / 
                             (len(self.language_system.primary_concepts) + len(self.language_system.valid_expressions))
        }


class ContaminationDetector:
    """Detects ontological contamination between frameworks."""
    
    def __init__(self):
        self.contamination_log = []
    
    def detect_contamination(self, expression: str, active_framework: OntologicalFramework, 
                           all_frameworks: Dict[str, OntologicalFramework]) -> Dict[str, Any]:
        """
        Detect if expression contains concepts from multiple ontological frameworks.
        This indicates dangerous ontological mixing.
        """
        contamination_detected = False
        framework_matches = {}
        
        # Check expression against all frameworks
        for name, framework in all_frameworks.items():
            if name == active_framework.name:
                continue
                
            # Check for concepts from other frameworks
            foreign_concepts = []
            for concept in framework.language_system.primary_concepts:
                if concept.lower() in expression.lower():
                    foreign_concepts.append(concept)
            
            if foreign_concepts:
                framework_matches[name] = foreign_concepts
                contamination_detected = True
        
        result = {
            "contamination_detected": contamination_detected,
            "active_framework": active_framework.name,
            "foreign_concepts": framework_matches,
            "expression": expression,
            "timestamp": datetime.now().isoformat()
        }
        
        if contamination_detected:
            self.contamination_log.append(result)
            print(f"⚠️ ONTOLOGICAL CONTAMINATION DETECTED!")
            print(f"   Expression: {expression}")
            print(f"   Active Framework: {active_framework.name}")
            print(f"   Foreign Concepts: {framework_matches}")
        
        return result


class OntologicalSwitchingSystem:
    """
    System for clean switching between ontological perspectives.
    
    Ensures complete ontological transitions with no mixing of frameworks.
    Each switch represents a complete change in perspective, language, and meaning.
    """
    
    def __init__(self):
        self.frameworks = {}
        self.current_framework = None
        self.transition_history = []
        self.contamination_detector = ContaminationDetector()
        
        # Initialize standard frameworks
        self._initialize_standard_frameworks()
    
    def _initialize_standard_frameworks(self):
        """Initialize the standard ontological frameworks."""
        
        # Engineering Framework
        engineering = OntologicalFramework(
            name="engineering",
            world_view="Reality consists of code, tests, performance metrics, and deployable systems",
            language_system=LanguageSystem(
                primary_concepts=["function", "class", "test", "bug", "deployment", "performance", "code", "implementation"],
                truth_criteria="Does it work? Do tests pass? Is it maintainable?",
                reasoning_pattern="Evidence-based, test-driven, pragmatic validation",
                valid_expressions=["implement", "test", "debug", "optimize", "deploy", "code", "build", "fix"],
                invalid_expressions=["design philosophy", "long-term vision", "conceptual beauty", "theoretical elegance"]
            ),
            meaning_structure=MeaningStructure(
                success_definition="All tests pass, performance meets requirements, features work correctly",
                problem_definition="Tests fail, performance degrades, bugs in production",
                solution_approach="Write code, fix bugs, optimize algorithms, improve implementation",
                quality_criteria="Clean code, good test coverage, reliable operation"
            ),
            conceptual_boundaries=ConceptualBoundaries(
                what_exists=["code files", "test suites", "runtime systems", "performance metrics"],
                what_matters=["functionality", "reliability", "performance", "maintainability"],
                time_horizon="current sprint, immediate delivery",
                success_metrics=["feature completion", "bug counts", "performance numbers", "test coverage"]
            ),
            keywords=["@engineering", "@code", "@implement", "@build"]
        )
        
        # Architecture Framework  
        architecture = OntologicalFramework(
            name="architecture",
            world_view="Reality consists of systems, patterns, relationships, and long-term evolution",
            language_system=LanguageSystem(
                primary_concepts=["component", "pattern", "relationship", "evolution", "scalability", "design", "structure"],
                truth_criteria="Is it well-designed? Will it scale? Is it maintainable long-term?",
                reasoning_pattern="Pattern-based, system-thinking, future-oriented analysis",
                valid_expressions=["design", "pattern", "structure", "evolve", "integrate", "architect", "model"],
                invalid_expressions=["quick fix", "just make it work", "technical debt acceptable", "hack it together"]
            ),
            meaning_structure=MeaningStructure(
                success_definition="Elegant design, clear patterns, sustainable growth, flexible architecture",
                problem_definition="Poor structure, tight coupling, architectural debt, inflexible design",
                solution_approach="Apply patterns, refactor structure, design for evolution, create abstractions",
                quality_criteria="Clear separation of concerns, flexible architecture, scalable design"
            ),
            conceptual_boundaries=ConceptualBoundaries(
                what_exists=["components", "interfaces", "patterns", "relationships", "abstractions"],
                what_matters=["structure", "maintainability", "evolution", "elegant design"],
                time_horizon="multiple years, long-term sustainability",
                success_metrics=["architectural clarity", "coupling metrics", "evolution capacity"]
            ),
            keywords=["@architecture", "@design", "@pattern", "@structure"]
        )
        
        # Debug Framework
        debug = OntologicalFramework(
            name="debug",
            world_view="Reality consists of observable symptoms, hidden causes, and investigatable systems",
            language_system=LanguageSystem(
                primary_concepts=["symptom", "hypothesis", "evidence", "root_cause", "reproduction", "investigation"],
                truth_criteria="Is it reproducible? Does evidence support hypothesis?",
                reasoning_pattern="Scientific method, systematic elimination, evidence-gathering",
                valid_expressions=["reproduce", "isolate", "hypothesize", "verify", "eliminate", "investigate", "trace"],
                invalid_expressions=["probably works", "good enough", "ship it anyway", "ignore for now"]
            ),
            meaning_structure=MeaningStructure(
                success_definition="Root cause identified, fix verified, no regressions introduced",
                problem_definition="Unreproducible symptoms, multiple possible causes, unclear evidence",
                solution_approach="Systematic investigation, hypothesis testing, controlled fixes, verification",
                quality_criteria="Thorough investigation, verified fixes, prevented regressions"
            ),
            conceptual_boundaries=ConceptualBoundaries(
                what_exists=["symptoms", "logs", "stack traces", "system states", "test conditions"],
                what_matters=["reproducibility", "evidence", "systematic investigation", "verification"],
                time_horizon="until problem is completely resolved",
                success_metrics=["problem resolution", "fix verification", "prevention success"]
            ),
            keywords=["@debug", "@investigate", "@trace", "@fix"]
        )
        
        # Register frameworks
        self.register_framework(engineering)
        self.register_framework(architecture)
        self.register_framework(debug)
    
    def register_framework(self, framework: OntologicalFramework):
        """Register an ontological framework."""
        self.frameworks[framework.name] = framework
        print(f"📋 Registered ontological framework: {framework.name}")
    
    def switch_perspective(self, target_framework_name: str, context: str = None) -> Dict[str, Any]:
        """
        Perform clean ontological perspective switch.
        
        Complete deactivation of current framework, clean transition, 
        complete activation of target framework.
        """
        
        if target_framework_name not in self.frameworks:
            return {
                "success": False,
                "error": f"Unknown ontological framework: {target_framework_name}"
            }
        
        target_framework = self.frameworks[target_framework_name]
        
        # Log transition
        transition = {
            "from_framework": self.current_framework.name if self.current_framework else None,
            "to_framework": target_framework_name,
            "timestamp": datetime.now().isoformat(),
            "context": context or "No context provided"
        }
        
        print(f"\n🔄 ONTOLOGICAL PERSPECTIVE SWITCH")
        print(f"   From: {transition['from_framework'] or 'None'}")
        print(f"   To: {target_framework_name}")
        print(f"   Context: {context or 'General transition'}")
        
        # 1. COMPLETE deactivation of current framework
        if self.current_framework:
            self.current_framework.deactivate()
        
        # 2. Clean transition state (no framework active)
        print("   🧹 Clean transition state (no active ontology)")
        
        # 3. COMPLETE activation of target framework
        target_framework.activate()
        self.current_framework = target_framework
        
        # 4. Log the transition
        self.transition_history.append(transition)
        
        print(f"   ✅ Ontological switch complete\n")
        
        return {
            "success": True,
            "active_framework": target_framework_name,
            "world_view": target_framework.world_view,
            "primary_concepts": target_framework.language_system.primary_concepts,
            "truth_criteria": target_framework.language_system.truth_criteria,
            "transition": transition
        }
    
    def validate_expression(self, expression: str) -> Dict[str, Any]:
        """
        Validate expression against current ontological framework.
        Also check for ontological contamination.
        """
        
        if not self.current_framework:
            return {
                "valid": False,
                "error": "No active ontological framework",
                "expression": expression
            }
        
        # Validate against current framework
        validation = self.current_framework.validate_expression(expression)
        
        # Check for ontological contamination
        contamination = self.contamination_detector.detect_contamination(
            expression, self.current_framework, self.frameworks
        )
        
        return {
            "validation": validation,
            "contamination": contamination,
            "expression": expression,
            "current_framework": self.current_framework.name
        }
    
    def detect_framework_from_keywords(self, text: str) -> Optional[str]:
        """Detect intended framework from keywords in text."""
        text_lower = text.lower()
        
        for framework_name, framework in self.frameworks.items():
            for keyword in framework.keywords:
                if keyword.lower() in text_lower:
                    return framework_name
        
        return None
    
    def get_framework_status(self) -> Dict[str, Any]:
        """Get current status of ontological framework system."""
        return {
            "current_framework": self.current_framework.name if self.current_framework else None,
            "available_frameworks": list(self.frameworks.keys()),
            "transition_count": len(self.transition_history),
            "contamination_count": len(self.contamination_detector.contamination_log),
            "last_transition": self.transition_history[-1] if self.transition_history else None
        }


def main():
    """Demonstration of ontological framework switching."""
    
    print("🧠 ONTOLOGICAL FRAMEWORK SYSTEM DEMONSTRATION")
    print("=" * 55)
    
    # Initialize system
    system = OntologicalSwitchingSystem()
    
    # Demonstrate framework switching
    print("\n1. SWITCHING TO ENGINEERING FRAMEWORK")
    system.switch_perspective("engineering", "Need to implement user authentication")
    
    # Test expressions in engineering framework
    test_expressions = [
        "Let's implement the login function with JWT tokens",
        "We need to design the overall system architecture",  # Should be invalid
        "Let's optimize this algorithm for better performance",
        "This needs better conceptual elegance"  # Should be invalid
    ]
    
    print("\n   Testing expressions in engineering framework:")
    for expr in test_expressions:
        result = system.validate_expression(expr)
        validation = result["validation"]
        contamination = result["contamination"]
        
        status = "✅" if validation["valid"] and not contamination["contamination_detected"] else "❌"
        print(f"   {status} '{expr}'")
        if not validation["valid"]:
            print(f"      Reason: {validation['reason']}")
        if contamination["contamination_detected"]:
            print(f"      Contamination: {contamination['foreign_concepts']}")
    
    # Switch to architecture framework
    print("\n\n2. SWITCHING TO ARCHITECTURE FRAMEWORK")
    system.switch_perspective("architecture", "Need to design system structure")
    
    print("\n   Testing same expressions in architecture framework:")
    for expr in test_expressions:
        result = system.validate_expression(expr)
        validation = result["validation"]
        contamination = result["contamination"]
        
        status = "✅" if validation["valid"] and not contamination["contamination_detected"] else "❌"
        print(f"   {status} '{expr}'")
        if not validation["valid"]:
            print(f"      Reason: {validation['reason']}")
        if contamination["contamination_detected"]:
            print(f"      Contamination: {contamination['foreign_concepts']}")
    
    # Show system status
    print("\n\n3. SYSTEM STATUS")
    status = system.get_framework_status()
    print(f"   Current Framework: {status['current_framework']}")
    print(f"   Available Frameworks: {status['available_frameworks']}")
    print(f"   Transitions Made: {status['transition_count']}")
    print(f"   Contaminations Detected: {status['contamination_count']}")
    
    print("\n✅ Ontological framework demonstration complete!")
    print("   Clean perspective switching with no ontological mixing achieved.")


if __name__ == "__main__":
    main()
