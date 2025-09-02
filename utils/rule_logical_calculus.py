"""
Rule Logical Calculus - Formal Logic System for Rule Ontologies
===============================================================

MISSION: Implement a formal logical calculus for rule systems, enabling:
- Ontological validation of rule relationships
- Logical inference and rule derivation
- Consistency checking across rule sets
- Formal verification of rule completeness
- Calculus-based rule optimization

Mathematical Foundation:
- Propositional Logic for rule conditions
- First-Order Logic for rule relationships  
- Modal Logic for context dependencies
- Set Theory for rule ontologies
- Graph Theory for rule dependencies

Philosophy: "Rules as logical propositions in a formal calculus"
"""

from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import itertools
from abc import ABC, abstractmethod

class LogicalOperator(Enum):
    """Logical operators for rule calculus."""
    AND = "∧"           # Conjunction
    OR = "∨"            # Disjunction  
    NOT = "¬"           # Negation
    IMPLIES = "→"       # Implication
    IFF = "↔"           # Biconditional
    FORALL = "∀"        # Universal quantifier
    EXISTS = "∃"        # Existential quantifier
    NECESSARILY = "□"   # Necessity (modal)
    POSSIBLY = "◇"      # Possibility (modal)

class RuleRelation(Enum):
    """Types of relationships between rules."""
    INDEPENDENT = "independent"     # R1 ⊥ R2 (no relationship)
    IMPLIES = "implies"            # R1 → R2 (R1 implies R2)
    EQUIVALENT = "equivalent"      # R1 ↔ R2 (R1 equivalent to R2)
    CONTRADICTS = "contradicts"    # R1 ∧ R2 = ⊥ (contradiction)
    SUBSUMES = "subsumes"          # R1 ⊃ R2 (R1 contains R2)
    DEPENDS_ON = "depends_on"      # R2 is prerequisite for R1

@dataclass
class LogicalProposition:
    """Logical proposition representing a rule or condition."""
    id: str
    proposition: str
    variables: Set[str]
    context_conditions: Set[str]
    truth_value: Optional[bool] = None

@dataclass
class RuleFormula:
    """Formal logical representation of a rule."""
    rule_id: str
    antecedent: List[LogicalProposition]  # Conditions (IF part)
    consequent: List[LogicalProposition]  # Actions (THEN part)
    context: Set[str]                     # Context constraints
    modal_operators: List[LogicalOperator]  # Modal constraints
    
    def to_logical_form(self) -> str:
        """Convert to formal logical notation."""
        ante = " ∧ ".join([p.proposition for p in self.antecedent])
        cons = " ∧ ".join([p.proposition for p in self.consequent])
        
        if self.context:
            context_str = " ∧ ".join([f"Context({c})" for c in self.context])
            return f"({context_str}) → (({ante}) → ({cons}))"
        else:
            return f"({ante}) → ({cons})"

class RuleOntology:
    """
    Formal ontology for rule systems using logical calculus.
    
    Implements:
    - Rule taxonomy and classification
    - Logical relationships between rules
    - Consistency validation
    - Completeness verification
    - Inference mechanisms
    """
    
    def __init__(self):
        self.rules: Dict[str, RuleFormula] = {}
        self.relations: Dict[Tuple[str, str], RuleRelation] = {}
        self.contexts: Set[str] = set()
        self.logical_constraints: List[str] = []
        
        # Ontological hierarchy
        self.rule_hierarchy = {
            "Foundation": {
                "Safety": ["safety_first_principle"],
                "Integrity": ["system_integrity", "data_consistency"],
                "Ethics": ["ethical_ai_principles"]
            },
            "Process": {
                "Development": ["test_driven_development", "clean_code"],
                "Coordination": ["agile_coordination", "stakeholder_management"],
                "Quality": ["scientific_verification", "quality_assurance"]
            },
            "Context": {
                "Situational": ["context_detection", "adaptive_behavior"],
                "Temporal": ["time_constraints", "deadline_management"],
                "Environmental": ["ide_optimization", "system_requirements"]
            }
        }
    
    def add_rule_formula(self, rule_formula: RuleFormula) -> None:
        """Add a rule to the ontology with logical validation."""
        
        # Validate logical consistency
        if self._check_consistency(rule_formula):
            self.rules[rule_formula.rule_id] = rule_formula
            self.contexts.update(rule_formula.context)
            self._update_relations(rule_formula)
        else:
            raise ValueError(f"Rule {rule_formula.rule_id} creates logical inconsistency")
    
    def derive_rule_relations(self) -> Dict[Tuple[str, str], RuleRelation]:
        """
        Derive logical relationships between rules using calculus.
        """
        
        relations = {}
        rule_ids = list(self.rules.keys())
        
        # Check all pairs of rules
        for r1_id, r2_id in itertools.combinations(rule_ids, 2):
            r1 = self.rules[r1_id]
            r2 = self.rules[r2_id]
            
            relation = self._compute_logical_relation(r1, r2)
            if relation != RuleRelation.INDEPENDENT:
                relations[(r1_id, r2_id)] = relation
        
        self.relations.update(relations)
        return relations
    
    def _compute_logical_relation(self, r1: RuleFormula, r2: RuleFormula) -> RuleRelation:
        """Compute logical relationship between two rules."""
        
        # Context analysis
        if r1.context.isdisjoint(r2.context) and r1.context and r2.context:
            return RuleRelation.INDEPENDENT
        
        # Logical analysis of antecedents and consequents
        r1_ante_props = {p.proposition for p in r1.antecedent}
        r1_cons_props = {p.proposition for p in r1.consequent}
        r2_ante_props = {p.proposition for p in r2.antecedent}
        r2_cons_props = {p.proposition for p in r2.consequent}
        
        # Check for implication (R1 → R2)
        if r1_cons_props.issubset(r2_ante_props):
            return RuleRelation.IMPLIES
        
        # Check for equivalence (R1 ↔ R2)
        if (r1_ante_props == r2_ante_props and r1_cons_props == r2_cons_props):
            return RuleRelation.EQUIVALENT
        
        # Check for contradiction
        if (r1_cons_props.intersection(r2_ante_props) and 
            any(f"¬{prop}" in r2_cons_props for prop in r1_cons_props)):
            return RuleRelation.CONTRADICTS
        
        # Check for subsumption
        if r2_ante_props.issubset(r1_ante_props) and r2_cons_props.issubset(r1_cons_props):
            return RuleRelation.SUBSUMES
        
        # Check for dependency
        if r1_cons_props.intersection(r2_ante_props):
            return RuleRelation.DEPENDS_ON
        
        return RuleRelation.INDEPENDENT
    
    def validate_ontological_consistency(self) -> Dict[str, Any]:
        """
        Validate logical consistency of the entire rule ontology.
        """
        
        validation_result = {
            "is_consistent": True,
            "contradictions": [],
            "circular_dependencies": [],
            "incomplete_chains": [],
            "orphaned_rules": [],
            "consistency_score": 0.0
        }
        
        # Check for contradictions
        contradictions = [
            (r1, r2) for (r1, r2), rel in self.relations.items() 
            if rel == RuleRelation.CONTRADICTS
        ]
        validation_result["contradictions"] = contradictions
        
        # Check for circular dependencies
        circular_deps = self._find_circular_dependencies()
        validation_result["circular_dependencies"] = circular_deps
        
        # Check for incomplete inference chains
        incomplete_chains = self._find_incomplete_chains()
        validation_result["incomplete_chains"] = incomplete_chains
        
        # Check for orphaned rules
        orphaned = self._find_orphaned_rules()
        validation_result["orphaned_rules"] = orphaned
        
        # Calculate consistency score
        total_issues = len(contradictions) + len(circular_deps) + len(incomplete_chains)
        total_rules = len(self.rules)
        validation_result["consistency_score"] = max(0.0, 1.0 - (total_issues / max(total_rules, 1)))
        
        validation_result["is_consistent"] = validation_result["consistency_score"] > 0.8
        
        return validation_result
    
    def infer_new_rules(self, context: str) -> List[RuleFormula]:
        """
        Use logical inference to derive new rules for a context.
        """
        
        inferred_rules = []
        context_rules = [r for r in self.rules.values() if context in r.context]
        
        # Apply modus ponens inference
        for r1, r2 in itertools.combinations(context_rules, 2):
            inferred = self._apply_modus_ponens(r1, r2)
            if inferred:
                inferred_rules.append(inferred)
        
        # Apply universal instantiation
        for rule in context_rules:
            instances = self._apply_universal_instantiation(rule, context)
            inferred_rules.extend(instances)
        
        return inferred_rules
    
    def _apply_modus_ponens(self, r1: RuleFormula, r2: RuleFormula) -> Optional[RuleFormula]:
        """
        Apply modus ponens: (P → Q) ∧ P ⊢ Q
        """
        
        # Check if r1's consequent matches r2's antecedent
        r1_cons_props = {p.proposition for p in r1.consequent}
        r2_ante_props = {p.proposition for p in r2.antecedent}
        
        if r1_cons_props.intersection(r2_ante_props):
            # Create inferred rule: r1.antecedent → r2.consequent
            inferred_id = f"inferred_{r1.rule_id}_{r2.rule_id}"
            
            return RuleFormula(
                rule_id=inferred_id,
                antecedent=r1.antecedent,
                consequent=r2.consequent,
                context=r1.context.union(r2.context),
                modal_operators=[]
            )
        
        return None
    
    def _apply_universal_instantiation(self, rule: RuleFormula, context: str) -> List[RuleFormula]:
        """
        Apply universal instantiation for context-specific rules.
        """
        
        instances = []
        
        # If rule contains universal quantifiers, instantiate for context
        if LogicalOperator.FORALL in rule.modal_operators:
            # Create context-specific instance
            instance_id = f"{rule.rule_id}_{context}_instance"
            
            instance = RuleFormula(
                rule_id=instance_id,
                antecedent=rule.antecedent,
                consequent=rule.consequent,
                context={context},
                modal_operators=[op for op in rule.modal_operators if op != LogicalOperator.FORALL]
            )
            
            instances.append(instance)
        
        return instances
    
    def _check_consistency(self, new_rule: RuleFormula) -> bool:
        """Check if adding a new rule maintains consistency."""
        
        # Temporarily add rule and check for contradictions
        temp_rules = self.rules.copy()
        temp_rules[new_rule.rule_id] = new_rule
        
        # Check against existing rules
        for existing_rule in self.rules.values():
            relation = self._compute_logical_relation(new_rule, existing_rule)
            if relation == RuleRelation.CONTRADICTS:
                return False
        
        return True
    
    def _update_relations(self, rule: RuleFormula) -> None:
        """Update relationships when a new rule is added."""
        
        for existing_id, existing_rule in self.rules.items():
            if existing_id != rule.rule_id:
                relation = self._compute_logical_relation(rule, existing_rule)
                if relation != RuleRelation.INDEPENDENT:
                    self.relations[(rule.rule_id, existing_id)] = relation
    
    def _find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in rule relationships."""
        
        # Build dependency graph
        dependency_graph = {}
        for (r1, r2), relation in self.relations.items():
            if relation == RuleRelation.DEPENDS_ON:
                if r1 not in dependency_graph:
                    dependency_graph[r1] = []
                dependency_graph[r1].append(r2)
        
        # Find cycles using DFS
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            if node in rec_stack:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependency_graph.get(node, []):
                dfs(neighbor, path + [neighbor])
            
            rec_stack.remove(node)
        
        for rule_id in dependency_graph:
            if rule_id not in visited:
                dfs(rule_id, [rule_id])
        
        return cycles
    
    def _find_incomplete_chains(self) -> List[str]:
        """Find incomplete inference chains."""
        
        incomplete = []
        
        for rule_id, rule in self.rules.items():
            # Check if rule has antecedents that aren't satisfied by other rules
            for antecedent in rule.antecedent:
                prop = antecedent.proposition
                
                # Look for rules that could satisfy this antecedent
                satisfying_rules = [
                    r_id for r_id, r in self.rules.items()
                    if any(cons.proposition == prop for cons in r.consequent)
                ]
                
                if not satisfying_rules:
                    incomplete.append(f"{rule_id}: unsatisfied antecedent '{prop}'")
        
        return incomplete
    
    def _find_orphaned_rules(self) -> List[str]:
        """Find rules that aren't connected to any others."""
        
        connected_rules = set()
        for (r1, r2) in self.relations.keys():
            connected_rules.add(r1)
            connected_rules.add(r2)
        
        all_rules = set(self.rules.keys())
        orphaned = all_rules - connected_rules
        
        return list(orphaned)
    
    def generate_logical_proof(self, goal_rule: str, premises: List[str]) -> Optional[List[str]]:
        """
        Generate a logical proof that derives goal_rule from premises.
        """
        
        if goal_rule not in self.rules:
            return None
        
        # Simple proof by forward chaining
        derived = set(premises)
        proof_steps = []
        
        max_iterations = 10
        for _ in range(max_iterations):
            initial_size = len(derived)
            
            # Apply inference rules
            for rule_id, rule in self.rules.items():
                antecedent_props = {p.proposition for p in rule.antecedent}
                
                if antecedent_props.issubset(derived):
                    consequent_props = {p.proposition for p in rule.consequent}
                    new_props = consequent_props - derived
                    
                    if new_props:
                        derived.update(new_props)
                        proof_steps.append(f"Apply {rule_id}: {antecedent_props} ⊢ {new_props}")
                        
                        # Check if goal is reached
                        goal_props = {p.proposition for p in self.rules[goal_rule].consequent}
                        if goal_props.issubset(derived):
                            return proof_steps
            
            # If no new derivations, stop
            if len(derived) == initial_size:
                break
        
        return None

# Global rule ontology
rule_ontology = RuleOntology()

def create_safety_rule_formula() -> RuleFormula:
    """Create formal logical representation of safety rule."""
    
    return RuleFormula(
        rule_id="safety_first_principle",
        antecedent=[
            LogicalProposition("operation_request", "OperationRequested(op)", {"op"}),
            LogicalProposition("safety_check", "¬SafetyValidated(op)", {"op"})
        ],
        consequent=[
            LogicalProposition("block_operation", "BlockOperation(op)", {"op"}),
            LogicalProposition("require_validation", "RequireValidation(op)", {"op"})
        ],
        context={"ALL"},
        modal_operators=[LogicalOperator.NECESSARILY]
    )

def create_agile_rule_formula() -> RuleFormula:
    """Create formal logical representation of agile coordination rule."""
    
    return RuleFormula(
        rule_id="agile_strategic_coordination",
        antecedent=[
            LogicalProposition("agile_request", "AgileRequest(req)", {"req"}),
            LogicalProposition("context_agile", "Context(AGILE)", set())
        ],
        consequent=[
            LogicalProposition("create_story", "CreateUserStory(req)", {"req"}),
            LogicalProposition("coordinate_work", "CoordinateWork(req)", {"req"}),
            LogicalProposition("manage_stakeholders", "ManageStakeholders(req)", {"req"})
        ],
        context={"AGILE"},
        modal_operators=[]
    )

# Test the logical calculus
if __name__ == "__main__":
    print("🧮 **RULE LOGICAL CALCULUS TEST**\n")
    
    # Add some rules to the ontology
    safety_rule = create_safety_rule_formula()
    agile_rule = create_agile_rule_formula()
    
    rule_ontology.add_rule_formula(safety_rule)
    rule_ontology.add_rule_formula(agile_rule)
    
    # Derive relationships
    relations = rule_ontology.derive_rule_relations()
    print(f"Derived {len(relations)} rule relationships")
    
    # Validate consistency
    validation = rule_ontology.validate_ontological_consistency()
    print(f"Ontology consistency: {validation['is_consistent']}")
    print(f"Consistency score: {validation['consistency_score']:.2f}")
    
    # Test logical forms
    print(f"\nSafety rule logical form:")
    print(safety_rule.to_logical_form())
    
    print(f"\nAgile rule logical form:")
    print(agile_rule.to_logical_form())
    
    print("\n✅ **LOGICAL CALCULUS OPERATIONAL**")
