"""
Layered Rule Trigger System
===========================

MISSION: Implement communication protocols where core rules trigger upper layer rules
through defined activation cascades, creating a systematic layered rule system.

Architecture:
- AXIOMATIC LAYER → Triggers TYPE_0 rules via protocol messages
- TYPE_0 LAYER → Triggers TYPE_1 rule sets via coordination protocols  
- TYPE_1 LAYER → Triggers TYPE_2 meta-rules via composition protocols
- TYPE_2 LAYER → Triggers TYPE_3 system rules via governance protocols

Communication Protocols:
- Protocol Messages: Formal messages passed between layers
- Activation Triggers: Specific conditions that activate higher layers
- Cascade Patterns: How activation flows through the system
- Feedback Loops: How higher layers inform lower layers
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import asyncio

class LayerLevel(Enum):
    """The hierarchical layers in our system."""
    AXIOMATIC = 0           # Foundation axioms
    TYPE_0_INDIVIDUAL = 1   # Individual context rules
    TYPE_1_RULE_SETS = 2    # Rule set compositions
    TYPE_2_META_RULES = 3   # Meta-rules about rules
    TYPE_3_SYSTEM = 4       # System governance

class ProtocolType(Enum):
    """Types of communication protocols between layers."""
    ACTIVATION_TRIGGER = "activation_trigger"       # Trigger higher layer activation
    CONTEXT_SIGNAL = "context_signal"              # Signal context change
    COMPOSITION_REQUEST = "composition_request"     # Request rule composition
    GOVERNANCE_DIRECTIVE = "governance_directive"  # System governance command
    FEEDBACK_RESPONSE = "feedback_response"        # Response from higher layer

@dataclass
class ProtocolMessage:
    """A formal protocol message between layers."""
    message_id: str
    source_layer: LayerLevel
    target_layer: LayerLevel
    protocol_type: ProtocolType
    trigger_condition: str
    payload: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: float
    requires_response: bool = False
    response_timeout: float = 5.0

@dataclass
class LayerActivationRule:
    """Rule defining how one layer activates another."""
    rule_id: str
    source_layer: LayerLevel
    target_layer: LayerLevel
    trigger_conditions: List[str]
    activation_protocol: ProtocolType
    message_template: Dict[str, Any]
    cascade_enabled: bool = True
    feedback_required: bool = False

class LayerTriggerProtocol:
    """
    Base class for layer communication protocols.
    """
    
    def __init__(self, protocol_type: ProtocolType):
        self.protocol_type = protocol_type
        self.message_queue: List[ProtocolMessage] = []
        self.response_handlers: Dict[str, callable] = {}
    
    def create_message(self, source_layer: LayerLevel, target_layer: LayerLevel,
                      trigger_condition: str, payload: Dict, context: Dict) -> ProtocolMessage:
        """Create a protocol message."""
        
        message = ProtocolMessage(
            message_id=f"{source_layer.value}_{target_layer.value}_{int(time.time() * 1000)}",
            source_layer=source_layer,
            target_layer=target_layer,
            protocol_type=self.protocol_type,
            trigger_condition=trigger_condition,
            payload=payload,
            context=context,
            timestamp=time.time()
        )
        
        return message
    
    def send_message(self, message: ProtocolMessage) -> bool:
        """Send a protocol message."""
        self.message_queue.append(message)
        return True
    
    def process_messages(self) -> List[Dict]:
        """Process all queued messages."""
        results = []
        
        for message in self.message_queue:
            result = self._process_single_message(message)
            results.append(result)
        
        self.message_queue.clear()
        return results
    
    def _process_single_message(self, message: ProtocolMessage) -> Dict:
        """Process a single protocol message."""
        return {
            "message_id": message.message_id,
            "processed": True,
            "result": "Message processed successfully"
        }

class AxiomaticTriggerProtocol(LayerTriggerProtocol):
    """
    Protocol for axiomatic layer triggering TYPE_0 rules.
    """
    
    def __init__(self):
        super().__init__(ProtocolType.ACTIVATION_TRIGGER)
        self.axiom_triggers = self._initialize_axiom_triggers()
    
    def _initialize_axiom_triggers(self) -> Dict[str, LayerActivationRule]:
        """Initialize how axioms trigger TYPE_0 rules."""
        
        return {
            "SAFETY_TRIGGERS_CONTEXT": LayerActivationRule(
                rule_id="SAFETY_TO_CONTEXT",
                source_layer=LayerLevel.AXIOMATIC,
                target_layer=LayerLevel.TYPE_0_INDIVIDUAL,
                trigger_conditions=["safety_assessment_required", "harm_risk_detected", "user_operation"],
                activation_protocol=ProtocolType.ACTIVATION_TRIGGER,
                message_template={
                    "safety_priority": "critical",
                    "required_validations": ["harm_assessment", "user_safety", "system_integrity"],
                    "activation_reason": "Safety axiom requires context-specific safety measures"
                },
                cascade_enabled=True,
                feedback_required=True
            ),
            
            "EVIDENCE_TRIGGERS_VALIDATION": LayerActivationRule(
                rule_id="EVIDENCE_TO_VALIDATION",
                source_layer=LayerLevel.AXIOMATIC,
                target_layer=LayerLevel.TYPE_0_INDIVIDUAL,
                trigger_conditions=["success_claim", "completion_declaration", "truth_assertion"],
                activation_protocol=ProtocolType.ACTIVATION_TRIGGER,
                message_template={
                    "evidence_required": True,
                    "validation_protocols": ["test_execution", "peer_review", "empirical_verification"],
                    "activation_reason": "Evidence axiom requires validation in specific context"
                },
                cascade_enabled=True,
                feedback_required=True
            ),
            
            "QUALITY_TRIGGERS_EXCELLENCE": LayerActivationRule(
                rule_id="QUALITY_TO_EXCELLENCE",
                source_layer=LayerLevel.AXIOMATIC,
                target_layer=LayerLevel.TYPE_0_INDIVIDUAL,
                trigger_conditions=["work_execution", "deliverable_creation", "code_implementation"],
                activation_protocol=ProtocolType.ACTIVATION_TRIGGER,
                message_template={
                    "quality_standards": "excellence",
                    "required_practices": ["clean_code", "test_coverage", "documentation"],
                    "activation_reason": "Quality axiom requires context-specific excellence measures"
                },
                cascade_enabled=True,
                feedback_required=False
            ),
            
            "LEARNING_TRIGGERS_IMPROVEMENT": LayerActivationRule(
                rule_id="LEARNING_TO_IMPROVEMENT",
                source_layer=LayerLevel.AXIOMATIC,
                target_layer=LayerLevel.TYPE_0_INDIVIDUAL,
                trigger_conditions=["failure_detected", "error_encountered", "suboptimal_outcome"],
                activation_protocol=ProtocolType.ACTIVATION_TRIGGER,
                message_template={
                    "learning_mode": "disaster_report",
                    "improvement_protocols": ["root_cause_analysis", "wisdom_extraction", "system_enhancement"],
                    "activation_reason": "Learning axiom requires context-specific improvement measures"
                },
                cascade_enabled=True,
                feedback_required=True
            ),
            
            "CONSISTENCY_TRIGGERS_VALIDATION": LayerActivationRule(
                rule_id="CONSISTENCY_TO_VALIDATION",
                source_layer=LayerLevel.AXIOMATIC,
                target_layer=LayerLevel.TYPE_0_INDIVIDUAL,
                trigger_conditions=["rule_combination", "logic_operation", "system_validation"],
                activation_protocol=ProtocolType.ACTIVATION_TRIGGER,
                message_template={
                    "consistency_check": True,
                    "validation_protocols": ["logic_verification", "contradiction_detection", "coherence_validation"],
                    "activation_reason": "Consistency axiom requires logical validation"
                },
                cascade_enabled=True,
                feedback_required=True
            )
        }
    
    def trigger_type0_rules(self, trigger_condition: str, context: Dict) -> List[ProtocolMessage]:
        """Trigger TYPE_0 rules based on axiomatic requirements."""
        
        triggered_messages = []
        
        for trigger_id, activation_rule in self.axiom_triggers.items():
            if trigger_condition in activation_rule.trigger_conditions:
                # Create trigger message
                message = self.create_message(
                    source_layer=LayerLevel.AXIOMATIC,
                    target_layer=LayerLevel.TYPE_0_INDIVIDUAL,
                    trigger_condition=trigger_condition,
                    payload=activation_rule.message_template.copy(),
                    context=context
                )
                
                # Add context-specific information
                message.payload.update({
                    "trigger_rule_id": activation_rule.rule_id,
                    "context_requirements": self._determine_context_requirements(trigger_condition, context)
                })
                
                triggered_messages.append(message)
                self.send_message(message)
        
        return triggered_messages
    
    def _determine_context_requirements(self, trigger_condition: str, context: Dict) -> List[str]:
        """Determine what context-specific rules need to be activated."""
        
        context_requirements = []
        context_str = str(context).lower()
        
        # Map context to required rule activations
        context_mappings = {
            "agile": ["agile_strategic_coordination", "agile_artifact_maintenance"],
            "code": ["development_core_principles", "clean_code_practices"],
            "test": ["test_driven_development", "quality_validation"],
            "git": ["streamlined_git_operations", "version_control_safety"],
            "docs": ["live_documentation_updates", "documentation_excellence"],
            "debug": ["systematic_problem_solving", "error_analysis"]
        }
        
        for context_key, required_rules in context_mappings.items():
            if context_key in context_str:
                context_requirements.extend(required_rules)
        
        return context_requirements

class Type0TriggerProtocol(LayerTriggerProtocol):
    """
    Protocol for TYPE_0 rules triggering TYPE_1 rule sets.
    """
    
    def __init__(self):
        super().__init__(ProtocolType.COMPOSITION_REQUEST)
        self.composition_triggers = self._initialize_composition_triggers()
    
    def _initialize_composition_triggers(self) -> Dict[str, LayerActivationRule]:
        """Initialize how TYPE_0 rules trigger TYPE_1 rule sets."""
        
        return {
            "AGILE_COORDINATION_TRIGGERS_ARTIFACTS": LayerActivationRule(
                rule_id="AGILE_COORD_TO_ARTIFACTS",
                source_layer=LayerLevel.TYPE_0_INDIVIDUAL,
                target_layer=LayerLevel.TYPE_1_RULE_SETS,
                trigger_conditions=["user_story_created", "sprint_started", "agile_work_initiated"],
                activation_protocol=ProtocolType.COMPOSITION_REQUEST,
                message_template={
                    "composition_type": "agile_artifact_maintenance",
                    "required_artifacts": ["story_documentation", "sprint_planning", "progress_tracking"],
                    "coordination_patterns": ["stakeholder_communication", "progress_transparency"]
                },
                cascade_enabled=True
            ),
            
            "CODE_DEVELOPMENT_TRIGGERS_QUALITY": LayerActivationRule(
                rule_id="CODE_DEV_TO_QUALITY",
                source_layer=LayerLevel.TYPE_0_INDIVIDUAL,
                target_layer=LayerLevel.TYPE_1_RULE_SETS,
                trigger_conditions=["code_implementation", "development_task", "programming_work"],
                activation_protocol=ProtocolType.COMPOSITION_REQUEST,
                message_template={
                    "composition_type": "code_quality_ensemble",
                    "required_practices": ["clean_code", "test_coverage", "code_review"],
                    "coordination_patterns": ["development_harmony", "quality_assurance"]
                },
                cascade_enabled=True
            ),
            
            "MULTIPLE_CONTEXTS_TRIGGER_ORCHESTRATION": LayerActivationRule(
                rule_id="MULTI_CONTEXT_TO_ORCHESTRAL",
                source_layer=LayerLevel.TYPE_0_INDIVIDUAL,
                target_layer=LayerLevel.TYPE_1_RULE_SETS,
                trigger_conditions=["multiple_contexts_detected", "cross_domain_work", "integration_required"],
                activation_protocol=ProtocolType.COMPOSITION_REQUEST,
                message_template={
                    "composition_type": "divine_harmony_integration",
                    "orchestral_coordination": True,
                    "integration_patterns": ["cross_context_harmony", "unified_coordination"]
                },
                cascade_enabled=True
            )
        }
    
    def trigger_type1_rule_sets(self, active_type0_rules: List[str], context: Dict) -> List[ProtocolMessage]:
        """Trigger TYPE_1 rule sets based on active TYPE_0 rules."""
        
        triggered_messages = []
        
        # Detect trigger conditions from active rules
        for trigger_id, activation_rule in self.composition_triggers.items():
            should_trigger = self._should_trigger_composition(activation_rule, active_type0_rules, context)
            
            if should_trigger:
                message = self.create_message(
                    source_layer=LayerLevel.TYPE_0_INDIVIDUAL,
                    target_layer=LayerLevel.TYPE_1_RULE_SETS,
                    trigger_condition=f"composition_required_{activation_rule.rule_id}",
                    payload=activation_rule.message_template.copy(),
                    context=context
                )
                
                message.payload.update({
                    "trigger_rule_id": activation_rule.rule_id,
                    "source_rules": active_type0_rules,
                    "composition_justification": self._generate_composition_justification(activation_rule, active_type0_rules)
                })
                
                triggered_messages.append(message)
                self.send_message(message)
        
        return triggered_messages
    
    def _should_trigger_composition(self, activation_rule: LayerActivationRule, 
                                  active_rules: List[str], context: Dict) -> bool:
        """Determine if rule composition should be triggered."""
        
        # Check if context indicates need for this composition
        context_str = str(context).lower()
        
        composition_conditions = {
            "agile_artifact_maintenance": ["agile", "user story", "sprint"],
            "code_quality_ensemble": ["code", "implement", "develop"],
            "divine_harmony_integration": ["multiple", "integration", "coordination"]
        }
        
        composition_type = activation_rule.message_template.get("composition_type", "")
        required_indicators = composition_conditions.get(composition_type, [])
        
        # Check if context contains required indicators
        context_match = any(indicator in context_str for indicator in required_indicators)
        
        # Check if multiple TYPE_0 rules are active (indicates need for composition)
        multiple_rules_active = len(active_rules) >= 2
        
        return context_match and multiple_rules_active

class Type1TriggerProtocol(LayerTriggerProtocol):
    """
    Protocol for TYPE_1 rule sets triggering TYPE_2 meta-rules.
    """
    
    def __init__(self):
        super().__init__(ProtocolType.CONTEXT_SIGNAL)
        self.meta_triggers = self._initialize_meta_triggers()
    
    def _initialize_meta_triggers(self) -> Dict[str, LayerActivationRule]:
        """Initialize how TYPE_1 rule sets trigger TYPE_2 meta-rules."""
        
        return {
            "RULE_SET_COORDINATION_TRIGGERS_CONTEXT_AWARENESS": LayerActivationRule(
                rule_id="RULESET_TO_CONTEXT_AWARE",
                source_layer=LayerLevel.TYPE_1_RULE_SETS,
                target_layer=LayerLevel.TYPE_2_META_RULES,
                trigger_conditions=["rule_set_complexity", "context_ambiguity", "selection_needed"],
                activation_protocol=ProtocolType.CONTEXT_SIGNAL,
                message_template={
                    "meta_rule_type": "intelligent_context_aware_rule_system",
                    "selection_assistance": True,
                    "optimization_required": ["rule_selection", "context_detection", "efficiency_improvement"]
                },
                cascade_enabled=True
            ),
            
            "LINGUISTIC_COMPLEXITY_TRIGGERS_ARCHITECTURE": LayerActivationRule(
                rule_id="LINGUISTIC_TO_ARCHITECTURE",
                source_layer=LayerLevel.TYPE_1_RULE_SETS,
                target_layer=LayerLevel.TYPE_2_META_RULES,
                trigger_conditions=["language_game_coordination", "semantic_complexity", "communication_issues"],
                activation_protocol=ProtocolType.CONTEXT_SIGNAL,
                message_template={
                    "meta_rule_type": "formal_linguistic_rule_architecture",
                    "linguistic_coordination": True,
                    "architecture_support": ["semantic_resolution", "communication_protocols", "language_games"]
                },
                cascade_enabled=True
            )
        }
    
    def trigger_type2_meta_rules(self, active_rule_sets: List[str], context: Dict) -> List[ProtocolMessage]:
        """Trigger TYPE_2 meta-rules based on rule set complexity."""
        
        triggered_messages = []
        
        # Analyze complexity and trigger meta-rules as needed
        complexity_analysis = self._analyze_rule_set_complexity(active_rule_sets, context)
        
        for trigger_id, activation_rule in self.meta_triggers.items():
            should_trigger = self._should_trigger_meta_rule(activation_rule, complexity_analysis, context)
            
            if should_trigger:
                message = self.create_message(
                    source_layer=LayerLevel.TYPE_1_RULE_SETS,
                    target_layer=LayerLevel.TYPE_2_META_RULES,
                    trigger_condition=f"meta_assistance_required_{activation_rule.rule_id}",
                    payload=activation_rule.message_template.copy(),
                    context=context
                )
                
                message.payload.update({
                    "complexity_analysis": complexity_analysis,
                    "source_rule_sets": active_rule_sets,
                    "meta_assistance_justification": self._generate_meta_justification(activation_rule, complexity_analysis)
                })
                
                triggered_messages.append(message)
                self.send_message(message)
        
        return triggered_messages
    
    def _analyze_rule_set_complexity(self, active_rule_sets: List[str], context: Dict) -> Dict:
        """Analyze complexity of active rule sets."""
        
        return {
            "rule_set_count": len(active_rule_sets),
            "context_complexity": len(str(context)) / 100,  # Rough measure
            "coordination_required": len(active_rule_sets) > 2,
            "linguistic_complexity": self._assess_linguistic_complexity(context),
            "selection_difficulty": len(active_rule_sets) > 3
        }
    
    def _assess_linguistic_complexity(self, context: Dict) -> float:
        """Assess linguistic complexity of context."""
        
        context_str = str(context).lower()
        complexity_indicators = ["multiple", "complex", "integration", "coordination", "various", "different"]
        
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in context_str)
        return min(complexity_score / len(complexity_indicators), 1.0)

class Type2TriggerProtocol(LayerTriggerProtocol):
    """
    Protocol for TYPE_2 meta-rules triggering TYPE_3 system rules.
    """
    
    def __init__(self):
        super().__init__(ProtocolType.GOVERNANCE_DIRECTIVE)
        self.system_triggers = self._initialize_system_triggers()
    
    def _initialize_system_triggers(self) -> Dict[str, LayerActivationRule]:
        """Initialize how TYPE_2 meta-rules trigger TYPE_3 system rules."""
        
        return {
            "META_OPTIMIZATION_TRIGGERS_SYSTEM_LEARNING": LayerActivationRule(
                rule_id="META_OPT_TO_SYSTEM_LEARN",
                source_layer=LayerLevel.TYPE_2_META_RULES,
                target_layer=LayerLevel.TYPE_3_SYSTEM,
                trigger_conditions=["optimization_opportunity", "system_improvement_needed", "learning_pattern_detected"],
                activation_protocol=ProtocolType.GOVERNANCE_DIRECTIVE,
                message_template={
                    "system_rule_type": "self_optimizing_learning_system",
                    "optimization_directive": True,
                    "learning_protocols": ["pattern_recognition", "system_evolution", "optimization_implementation"]
                },
                cascade_enabled=True
            ),
            
            "RULE_VIOLATIONS_TRIGGER_ENFORCEMENT": LayerActivationRule(
                rule_id="VIOLATIONS_TO_ENFORCEMENT",
                source_layer=LayerLevel.TYPE_2_META_RULES,
                target_layer=LayerLevel.TYPE_3_SYSTEM,
                trigger_conditions=["rule_violation_detected", "system_inconsistency", "enforcement_needed"],
                activation_protocol=ProtocolType.GOVERNANCE_DIRECTIVE,
                message_template={
                    "system_rule_type": "automatic_rule_enforcement_system",
                    "enforcement_directive": True,
                    "enforcement_protocols": ["violation_detection", "automatic_correction", "system_healing"]
                },
                cascade_enabled=False  # System enforcement is terminal
            )
        }
    
    def trigger_type3_system_rules(self, meta_rule_analysis: Dict, context: Dict) -> List[ProtocolMessage]:
        """Trigger TYPE_3 system rules based on meta-rule analysis."""
        
        triggered_messages = []
        
        for trigger_id, activation_rule in self.system_triggers.items():
            should_trigger = self._should_trigger_system_rule(activation_rule, meta_rule_analysis, context)
            
            if should_trigger:
                message = self.create_message(
                    source_layer=LayerLevel.TYPE_2_META_RULES,
                    target_layer=LayerLevel.TYPE_3_SYSTEM,
                    trigger_condition=f"system_governance_required_{activation_rule.rule_id}",
                    payload=activation_rule.message_template.copy(),
                    context=context
                )
                
                message.payload.update({
                    "meta_analysis": meta_rule_analysis,
                    "governance_justification": self._generate_governance_justification(activation_rule, meta_rule_analysis)
                })
                
                triggered_messages.append(message)
                self.send_message(message)
        
        return triggered_messages

class LayeredRuleTriggerSystem:
    """
    Main system orchestrating layered rule triggering through communication protocols.
    """
    
    def __init__(self):
        self.axiomatic_protocol = AxiomaticTriggerProtocol()
        self.type0_protocol = Type0TriggerProtocol()
        self.type1_protocol = Type1TriggerProtocol()
        self.type2_protocol = Type2TriggerProtocol()
        
        self.active_rules_by_layer: Dict[LayerLevel, List[str]] = {
            LayerLevel.AXIOMATIC: [],
            LayerLevel.TYPE_0_INDIVIDUAL: [],
            LayerLevel.TYPE_1_RULE_SETS: [],
            LayerLevel.TYPE_2_META_RULES: [],
            LayerLevel.TYPE_3_SYSTEM: []
        }
        
        self.trigger_cascade_log: List[Dict] = []
    
    async def execute_layered_cascade(self, initial_trigger: str, context: Dict) -> Dict:
        """Execute complete layered rule cascade from axioms to system rules."""
        
        cascade_result = {
            "initial_trigger": initial_trigger,
            "context": context,
            "cascade_steps": [],
            "active_rules_by_layer": {},
            "total_messages": 0,
            "cascade_success": True
        }
        
        try:
            # STEP 1: Axiomatic Layer → TYPE_0 Individual Rules
            step1_messages = self.axiomatic_protocol.trigger_type0_rules(initial_trigger, context)
            cascade_result["cascade_steps"].append({
                "step": 1,
                "layer_transition": "AXIOMATIC → TYPE_0",
                "messages_sent": len(step1_messages),
                "triggered_rules": [msg.payload.get("context_requirements", []) for msg in step1_messages]
            })
            
            # Simulate TYPE_0 rule activation
            activated_type0_rules = self._extract_activated_rules(step1_messages)
            self.active_rules_by_layer[LayerLevel.TYPE_0_INDIVIDUAL] = activated_type0_rules
            
            # STEP 2: TYPE_0 Individual Rules → TYPE_1 Rule Sets
            step2_messages = self.type0_protocol.trigger_type1_rule_sets(activated_type0_rules, context)
            cascade_result["cascade_steps"].append({
                "step": 2,
                "layer_transition": "TYPE_0 → TYPE_1",
                "messages_sent": len(step2_messages),
                "triggered_rule_sets": [msg.payload.get("composition_type") for msg in step2_messages]
            })
            
            # Simulate TYPE_1 rule set activation
            activated_type1_sets = [msg.payload.get("composition_type") for msg in step2_messages]
            self.active_rules_by_layer[LayerLevel.TYPE_1_RULE_SETS] = activated_type1_sets
            
            # STEP 3: TYPE_1 Rule Sets → TYPE_2 Meta-Rules
            step3_messages = self.type1_protocol.trigger_type2_meta_rules(activated_type1_sets, context)
            cascade_result["cascade_steps"].append({
                "step": 3,
                "layer_transition": "TYPE_1 → TYPE_2",
                "messages_sent": len(step3_messages),
                "triggered_meta_rules": [msg.payload.get("meta_rule_type") for msg in step3_messages]
            })
            
            # Simulate TYPE_2 meta-rule activation
            activated_type2_rules = [msg.payload.get("meta_rule_type") for msg in step3_messages]
            self.active_rules_by_layer[LayerLevel.TYPE_2_META_RULES] = activated_type2_rules
            
            # STEP 4: TYPE_2 Meta-Rules → TYPE_3 System Rules (if needed)
            if step3_messages:  # Only if meta-rules were activated
                meta_analysis = {"optimization_opportunities": len(step3_messages), "system_coordination_needed": True}
                step4_messages = self.type2_protocol.trigger_type3_system_rules(meta_analysis, context)
                cascade_result["cascade_steps"].append({
                    "step": 4,
                    "layer_transition": "TYPE_2 → TYPE_3",
                    "messages_sent": len(step4_messages),
                    "triggered_system_rules": [msg.payload.get("system_rule_type") for msg in step4_messages]
                })
                
                activated_type3_rules = [msg.payload.get("system_rule_type") for msg in step4_messages]
                self.active_rules_by_layer[LayerLevel.TYPE_3_SYSTEM] = activated_type3_rules
            
            # Final summary
            cascade_result["active_rules_by_layer"] = {
                layer.name: rules for layer, rules in self.active_rules_by_layer.items()
            }
            cascade_result["total_messages"] = sum(step.get("messages_sent", 0) for step in cascade_result["cascade_steps"])
            
        except Exception as e:
            cascade_result["cascade_success"] = False
            cascade_result["error"] = str(e)
        
        self.trigger_cascade_log.append(cascade_result)
        return cascade_result
    
    def _extract_activated_rules(self, messages: List[ProtocolMessage]) -> List[str]:
        """Extract activated rule names from protocol messages."""
        
        activated_rules = []
        for message in messages:
            context_requirements = message.payload.get("context_requirements", [])
            activated_rules.extend(context_requirements)
        
        return list(set(activated_rules))  # Remove duplicates
    
    def generate_cascade_report(self, cascade_result: Dict) -> str:
        """Generate comprehensive cascade execution report."""
        
        report = f"""
🏗️ LAYERED RULE TRIGGER CASCADE REPORT
{'=' * 60}

🎯 INITIAL TRIGGER: {cascade_result['initial_trigger']}
📋 CONTEXT: {cascade_result['context']}
✅ CASCADE SUCCESS: {cascade_result['cascade_success']}
📨 TOTAL MESSAGES: {cascade_result['total_messages']}

🔄 CASCADE EXECUTION STEPS:
"""
        
        for step in cascade_result["cascade_steps"]:
            report += f"""
  STEP {step['step']}: {step['layer_transition']}
    Messages Sent: {step['messages_sent']}
    Triggered Rules: {step.get('triggered_rules', step.get('triggered_rule_sets', step.get('triggered_meta_rules', step.get('triggered_system_rules', []))))}
"""
        
        report += f"""
🎼 FINAL ACTIVE RULES BY LAYER:
"""
        
        for layer_name, rules in cascade_result["active_rules_by_layer"].items():
            if rules:
                report += f"  {layer_name}: {rules}\n"
        
        report += f"""
{'=' * 60}
🏗️ LAYERED TRIGGER CASCADE COMPLETE
"""
        
        return report

# Global layered trigger system
layered_trigger_system = LayeredRuleTriggerSystem()

async def execute_rule_cascade(trigger: str, context: Dict) -> Dict:
    """Execute complete layered rule cascade."""
    return await layered_trigger_system.execute_layered_cascade(trigger, context)

def generate_cascade_report(cascade_result: Dict) -> str:
    """Generate cascade execution report."""
    return layered_trigger_system.generate_cascade_report(cascade_result)

if __name__ == "__main__":
    # Demo the layered trigger system
    import asyncio
    
    async def demo():
        print("🏗️ LAYERED RULE TRIGGER SYSTEM DEMO")
        print("=" * 50)
        
        # Test cascade with agile context
        test_context = {
            "user_message": "@agile implement user authentication with comprehensive testing",
            "files": ["auth.py", "test_auth.py"],
            "keywords": ["@agile", "@code", "@test"]
        }
        
        result = await execute_rule_cascade("user_operation", test_context)
        
        report = generate_cascade_report(result)
        print(report)
        
        print("\n🏗️ Layered Rule Trigger System Demo Complete!")
    
    asyncio.run(demo())
