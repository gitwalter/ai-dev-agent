"""
Adaptive Learning Rule System - Living Rules in Agent Communication
================================================================

REVOLUTIONARY CONCEPT: Rules as living, learning entities that evolve through agent communication.

Core Principles:
- Rules learn from every agent interaction
- Rule system adapts and evolves continuously  
- Agents and rules co-evolve together
- Communication flow shapes rule intelligence
- Meta-learning at the system level

Philosophy: "Rules are not static instructions but living wisdom that grows 
through collective agent intelligence and shared experience."

Architecture: Rules + Agents = Living Adaptive Intelligence Ecosystem
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pathlib import Path
import hashlib
from collections import deque, defaultdict

class LearningMode(Enum):
    """How rules learn from interactions."""
    PASSIVE = "passive"          # Observe and record patterns
    ACTIVE = "active"            # Actively suggest adaptations
    COLLABORATIVE = "collaborative"  # Co-evolve with agents
    AUTONOMOUS = "autonomous"    # Self-modify and evolve

class AdaptationTrigger(Enum):
    """What triggers rule adaptation."""
    PATTERN_RECOGNITION = "pattern_recognition"
    SUCCESS_FAILURE = "success_failure"
    AGENT_FEEDBACK = "agent_feedback"
    CONTEXT_SHIFT = "context_shift"
    PERFORMANCE_METRICS = "performance_metrics"
    USER_BEHAVIOR = "user_behavior"

@dataclass
class AgentInteraction:
    """Record of agent communication and context."""
    timestamp: float
    agent_type: str
    message_content: str
    context_detected: str
    rules_active: List[str]
    success_indicators: List[str]
    failure_indicators: List[str]
    performance_metrics: Dict[str, float]
    user_satisfaction: Optional[float] = None

@dataclass
class RuleLearningEvent:
    """Event that teaches rules new patterns."""
    timestamp: float
    rule_name: str
    learning_type: AdaptationTrigger
    observation: str
    pattern_detected: str
    confidence: float
    suggested_adaptation: str

@dataclass
class RuleEvolution:
    """Record of how a rule has evolved."""
    rule_name: str
    original_form: str
    current_form: str
    evolution_history: List[str]
    learning_events: List[RuleLearningEvent]
    adaptation_count: int
    success_rate: float

class LivingRule:
    """
    A rule that lives, learns, and evolves through agent communication.
    
    Each rule maintains its own memory, learning patterns, and adaptation logic.
    """
    
    def __init__(self, name: str, initial_essence: str, learning_mode: LearningMode = LearningMode.COLLABORATIVE):
        self.name = name
        self.essence = initial_essence
        self.original_essence = initial_essence
        self.learning_mode = learning_mode
        
        # Learning system
        self.interaction_memory = deque(maxlen=1000)  # Remember last 1000 interactions
        self.pattern_library = defaultdict(int)       # Pattern frequency tracking
        self.adaptation_history = []                  # How rule has evolved
        self.success_patterns = defaultdict(list)     # What works well
        self.failure_patterns = defaultdict(list)     # What doesn't work
        
        # Performance metrics
        self.application_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.learning_confidence = 0.5
        
        # Adaptation parameters
        self.adaptation_threshold = 0.8  # Confidence required for adaptation
        self.learning_rate = 0.1         # How quickly to adapt
        self.memory_decay = 0.95         # How much to weight recent vs old learning
        
    def observe_interaction(self, interaction: AgentInteraction):
        """Observe and learn from agent interaction."""
        
        self.interaction_memory.append(interaction)
        self.application_count += 1
        
        # Learn patterns from successful interactions
        if interaction.success_indicators:
            self._learn_success_patterns(interaction)
            self.success_count += 1
            
        # Learn from failures
        if interaction.failure_indicators:
            self._learn_failure_patterns(interaction)
            self.failure_count += 1
            
        # Update success rate
        if self.application_count > 0:
            self.success_rate = self.success_count / self.application_count
            
        # Detect patterns and adapt if confidence is high enough
        if self.application_count % 10 == 0:  # Every 10 interactions
            self._analyze_patterns_and_adapt()
    
    def _learn_success_patterns(self, interaction: AgentInteraction):
        """Learn what patterns lead to success."""
        
        context = interaction.context_detected
        for indicator in interaction.success_indicators:
            pattern_key = f"{context}:{indicator}"
            self.success_patterns[pattern_key].append({
                "timestamp": interaction.timestamp,
                "message": interaction.message_content[:100],  # First 100 chars
                "metrics": interaction.performance_metrics
            })
            self.pattern_library[f"success:{pattern_key}"] += 1
    
    def _learn_failure_patterns(self, interaction: AgentInteraction):
        """Learn what patterns lead to failure."""
        
        context = interaction.context_detected
        for indicator in interaction.failure_indicators:
            pattern_key = f"{context}:{indicator}"
            self.failure_patterns[pattern_key].append({
                "timestamp": interaction.timestamp,
                "message": interaction.message_content[:100],
                "metrics": interaction.performance_metrics
            })
            self.pattern_library[f"failure:{pattern_key}"] += 1
    
    def _analyze_patterns_and_adapt(self):
        """Analyze learned patterns and adapt rule if confidence is high."""
        
        # Find most frequent success patterns
        success_patterns = {k: v for k, v in self.pattern_library.items() if k.startswith("success:")}
        if not success_patterns:
            return
            
        most_successful_pattern = max(success_patterns.items(), key=lambda x: x[1])
        pattern_strength = most_successful_pattern[1] / max(1, self.application_count)
        
        # Adapt if pattern is strong enough
        if pattern_strength > self.adaptation_threshold:
            self._evolve_rule_essence(most_successful_pattern[0], pattern_strength)
    
    def _evolve_rule_essence(self, successful_pattern: str, confidence: float):
        """Evolve the rule's essence based on learned patterns."""
        
        # Extract pattern information
        pattern_parts = successful_pattern.replace("success:", "").split(":")
        if len(pattern_parts) >= 2:
            context, success_indicator = pattern_parts[0], pattern_parts[1]
            
            # Generate evolved essence
            evolved_essence = self._generate_evolved_essence(context, success_indicator, confidence)
            
            if evolved_essence != self.essence:
                # Record evolution
                evolution_record = {
                    "timestamp": time.time(),
                    "previous_essence": self.essence,
                    "new_essence": evolved_essence,
                    "learning_pattern": successful_pattern,
                    "confidence": confidence,
                    "adaptation_reason": f"Learned from {self.application_count} interactions"
                }
                
                self.adaptation_history.append(evolution_record)
                self.essence = evolved_essence
                self.learning_confidence = min(1.0, self.learning_confidence + self.learning_rate)
                
                print(f"🧠 **RULE EVOLUTION**: {self.name}")
                print(f"   Old: {evolution_record['previous_essence'][:60]}...")
                print(f"   New: {evolved_essence[:60]}...")
                print(f"   Confidence: {confidence:.2f}")
    
    def _generate_evolved_essence(self, context: str, success_indicator: str, confidence: float) -> str:
        """Generate evolved rule essence based on learning."""
        
        # Simple evolution: incorporate successful patterns into essence
        if "agile" in context.lower() and "coordination" in success_indicator:
            return f"{self.essence} | Learned: Excel at {context} coordination through {success_indicator}"
        elif "test" in context.lower() and "pass" in success_indicator:
            return f"{self.essence} | Learned: Ensure {success_indicator} in {context} context"
        elif "code" in context.lower() and "clean" in success_indicator:
            return f"{self.essence} | Learned: Prioritize {success_indicator} in {context} development"
        else:
            return f"{self.essence} | Learned: Apply effectively in {context} with {success_indicator}"
    
    def get_current_intelligence(self) -> Dict[str, Any]:
        """Get current intelligence and learning state of the rule."""
        
        return {
            "name": self.name,
            "essence": self.essence,
            "learning_mode": self.learning_mode.value,
            "intelligence_metrics": {
                "applications": self.application_count,
                "success_rate": self.success_rate,
                "learning_confidence": self.learning_confidence,
                "adaptations": len(self.adaptation_history)
            },
            "top_success_patterns": dict(list(sorted(
                {k: v for k, v in self.pattern_library.items() if k.startswith("success:")}.items(),
                key=lambda x: x[1], reverse=True
            ))[:5]),
            "evolution_count": len(self.adaptation_history),
            "is_actively_learning": self.learning_mode in [LearningMode.ACTIVE, LearningMode.COLLABORATIVE]
        }

class AdaptiveLearningRuleSystem:
    """
    Living rule system that learns and adapts through agent communication.
    
    This system treats rules as intelligent entities that evolve through
    collective agent intelligence and shared learning experiences.
    """
    
    def __init__(self):
        self.living_rules: Dict[str, LivingRule] = {}
        self.agent_interaction_log = deque(maxlen=10000)
        self.system_learning_metrics = {}
        self.communication_patterns = defaultdict(list)
        
        # Initialize core living rules
        self._initialize_living_rules()
        
        # Communication integration
        self.is_integrated_with_agents = False
        self.agent_message_handlers = {}
        
        # Meta-learning system
        self.meta_learning_active = True
        self.system_adaptation_history = []
        
    def _initialize_living_rules(self):
        """Initialize core rules as living, learning entities."""
        
        core_rules = {
            "safety_first_principle": {
                "essence": "Safety > speed. Always prioritize user and system safety in all decisions.",
                "mode": LearningMode.COLLABORATIVE
            },
            "agile_strategic_coordination": {
                "essence": "Transform user requests into managed agile work with stakeholder coordination.",
                "mode": LearningMode.ACTIVE
            },
            "test_driven_development": {
                "essence": "Tests first → implementation → validation. Red-Green-Refactor cycle.",
                "mode": LearningMode.COLLABORATIVE
            },
            "systematic_problem_solving": {
                "essence": "Analyze → hypothesize → test → validate → document systematic approach.",
                "mode": LearningMode.ACTIVE
            },
            "clean_code_standards": {
                "essence": "Write readable, maintainable, well-structured code following SOLID principles.",
                "mode": LearningMode.COLLABORATIVE
            },
            "scientific_verification": {
                "essence": "Evidence-based claims only. No premature victory declarations without proof.",
                "mode": LearningMode.ACTIVE
            }
        }
        
        for name, config in core_rules.items():
            self.living_rules[name] = LivingRule(
                name=name,
                initial_essence=config["essence"],
                learning_mode=config["mode"]
            )
    
    def integrate_with_agent_communication(self, agent_message_handler: Callable):
        """Integrate rule system into agent communication flow."""
        
        self.agent_message_handlers["default"] = agent_message_handler
        self.is_integrated_with_agents = True
        
        print("🔗 **RULE SYSTEM INTEGRATED INTO AGENT COMMUNICATION**")
        print("   Rules now learn from every agent interaction")
        print("   Adaptive intelligence active in communication flow")
    
    async def process_agent_message(self, agent_type: str, message: str, 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process agent message through living rule system.
        
        This is called during agent communication to enable learning.
        """
        
        # Detect context and select active rules
        active_rules = self._select_active_rules_for_context(message, context)
        
        # Create interaction record
        interaction = AgentInteraction(
            timestamp=time.time(),
            agent_type=agent_type,
            message_content=message,
            context_detected=context.get("detected_context", "general"),
            rules_active=[rule.name for rule in active_rules],
            success_indicators=self._detect_success_indicators(message),
            failure_indicators=self._detect_failure_indicators(message),
            performance_metrics=context.get("performance_metrics", {})
        )
        
        # Let each active rule observe and learn
        for rule in active_rules:
            rule.observe_interaction(interaction)
        
        # Log interaction for system-level learning
        self.agent_interaction_log.append(interaction)
        
        # Generate adaptive response based on living rules
        adaptive_response = self._generate_adaptive_response(active_rules, interaction)
        
        # Meta-learning: Learn about the system itself
        if self.meta_learning_active:
            await self._meta_learn_from_interaction(interaction, adaptive_response)
        
        return adaptive_response
    
    def _select_active_rules_for_context(self, message: str, context: Dict[str, Any]) -> List[LivingRule]:
        """Select rules that should be active for this context."""
        
        message_lower = message.lower()
        active_rules = []
        
        # Always include safety
        if "safety_first_principle" in self.living_rules:
            active_rules.append(self.living_rules["safety_first_principle"])
        
        # Context-based selection with learning
        if any(word in message_lower for word in ["agile", "coordination", "team", "stakeholder"]):
            if "agile_strategic_coordination" in self.living_rules:
                active_rules.append(self.living_rules["agile_strategic_coordination"])
        
        if any(word in message_lower for word in ["test", "testing", "validate", "verify"]):
            if "test_driven_development" in self.living_rules:
                active_rules.append(self.living_rules["test_driven_development"])
        
        if any(word in message_lower for word in ["problem", "solve", "debug", "issue"]):
            if "systematic_problem_solving" in self.living_rules:
                active_rules.append(self.living_rules["systematic_problem_solving"])
        
        if any(word in message_lower for word in ["code", "develop", "implement", "build"]):
            if "clean_code_standards" in self.living_rules:
                active_rules.append(self.living_rules["clean_code_standards"])
        
        # Always include verification for critical decisions
        if any(word in message_lower for word in ["complete", "done", "success", "finished"]):
            if "scientific_verification" in self.living_rules:
                active_rules.append(self.living_rules["scientific_verification"])
        
        return active_rules
    
    def _detect_success_indicators(self, message: str) -> List[str]:
        """Detect indicators of successful outcomes in message."""
        
        success_indicators = []
        message_lower = message.lower()
        
        success_patterns = {
            "task_completion": ["completed", "finished", "done", "success"],
            "quality_achievement": ["excellent", "clean", "well-structured", "high quality"],
            "coordination_success": ["aligned", "coordinated", "collaborative", "harmonious"],
            "problem_resolution": ["solved", "resolved", "fixed", "working"],
            "test_success": ["passing", "validated", "verified", "tested"]
        }
        
        for category, patterns in success_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                success_indicators.append(category)
        
        return success_indicators
    
    def _detect_failure_indicators(self, message: str) -> List[str]:
        """Detect indicators of failures or problems in message."""
        
        failure_indicators = []
        message_lower = message.lower()
        
        failure_patterns = {
            "task_failure": ["failed", "broken", "not working", "error"],
            "quality_issues": ["messy", "unclear", "complex", "confusing"],
            "coordination_problems": ["misaligned", "conflicted", "chaotic", "disconnected"],
            "technical_problems": ["bug", "exception", "crash", "failure"],
            "test_failures": ["failing", "broken test", "test error", "not passing"]
        }
        
        for category, patterns in failure_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                failure_indicators.append(category)
        
        return failure_indicators
    
    def _generate_adaptive_response(self, active_rules: List[LivingRule], 
                                  interaction: AgentInteraction) -> Dict[str, Any]:
        """Generate response based on living rules and their learned intelligence."""
        
        # Gather intelligence from all active rules
        rule_intelligence = {}
        for rule in active_rules:
            rule_intelligence[rule.name] = rule.get_current_intelligence()
        
        # Generate adaptive recommendations
        adaptive_recommendations = []
        for rule in active_rules:
            if rule.learning_confidence > 0.7:  # High confidence rules give recommendations
                recommendation = f"Apply {rule.name}: {rule.essence[:100]}..."
                adaptive_recommendations.append(recommendation)
        
        return {
            "active_rules": [rule.name for rule in active_rules],
            "rule_intelligence": rule_intelligence,
            "adaptive_recommendations": adaptive_recommendations,
            "system_learning_status": {
                "total_interactions": len(self.agent_interaction_log),
                "active_learning_rules": len([r for r in active_rules if r.learning_mode != LearningMode.PASSIVE]),
                "system_adaptation_level": self._calculate_system_adaptation_level()
            },
            "communication_integrated": self.is_integrated_with_agents
        }
    
    async def _meta_learn_from_interaction(self, interaction: AgentInteraction, 
                                         response: Dict[str, Any]):
        """Meta-learning: Learn about the system's own learning patterns."""
        
        # Analyze system-level patterns
        if len(self.agent_interaction_log) % 50 == 0:  # Every 50 interactions
            system_patterns = self._analyze_system_patterns()
            
            if system_patterns["adaptation_needed"]:
                await self._adapt_system_architecture(system_patterns)
    
    def _analyze_system_patterns(self) -> Dict[str, Any]:
        """Analyze patterns across the entire system."""
        
        recent_interactions = list(self.agent_interaction_log)[-100:]  # Last 100 interactions
        
        # Analyze context distribution
        context_distribution = defaultdict(int)
        for interaction in recent_interactions:
            context_distribution[interaction.context_detected] += 1
        
        # Analyze rule effectiveness
        rule_effectiveness = {}
        for rule_name, rule in self.living_rules.items():
            rule_effectiveness[rule_name] = rule.success_rate
        
        # Determine if adaptation is needed
        adaptation_needed = any(rate < 0.6 for rate in rule_effectiveness.values())
        
        return {
            "context_distribution": dict(context_distribution),
            "rule_effectiveness": rule_effectiveness,
            "adaptation_needed": adaptation_needed,
            "total_interactions": len(self.agent_interaction_log),
            "learning_velocity": self._calculate_learning_velocity()
        }
    
    async def _adapt_system_architecture(self, patterns: Dict[str, Any]):
        """Adapt the system architecture based on learned patterns."""
        
        print("🧠 **SYSTEM META-LEARNING**: Adapting system architecture...")
        
        # Example adaptations based on patterns
        if patterns["context_distribution"].get("agile_coordination", 0) > 30:
            # If agile coordination is dominant, create specialized agile learning rules
            await self._create_specialized_rule("agile_coordination_specialist", 
                                              "Specialized agile coordination based on learned patterns")
        
        # Record system adaptation
        adaptation_record = {
            "timestamp": time.time(),
            "trigger_patterns": patterns,
            "adaptations_made": ["Analyzed system patterns for meta-learning"],
            "system_intelligence_level": self._calculate_system_adaptation_level()
        }
        
        self.system_adaptation_history.append(adaptation_record)
    
    async def _create_specialized_rule(self, name: str, essence: str):
        """Create new specialized rule based on system learning."""
        
        if name not in self.living_rules:
            self.living_rules[name] = LivingRule(
                name=name,
                initial_essence=essence,
                learning_mode=LearningMode.AUTONOMOUS  # New rules start autonomous
            )
            
            print(f"🌟 **NEW RULE EVOLVED**: {name}")
            print(f"   Essence: {essence}")
            print(f"   Learning Mode: Autonomous")
    
    def _calculate_system_adaptation_level(self) -> float:
        """Calculate overall system adaptation level."""
        
        if not self.living_rules:
            return 0.0
        
        total_learning_confidence = sum(rule.learning_confidence for rule in self.living_rules.values())
        average_confidence = total_learning_confidence / len(self.living_rules)
        
        total_adaptations = sum(len(rule.adaptation_history) for rule in self.living_rules.values())
        adaptation_factor = min(1.0, total_adaptations / 10)  # Normalize to 0-1
        
        return (average_confidence + adaptation_factor) / 2
    
    def _calculate_learning_velocity(self) -> float:
        """Calculate how quickly the system is learning and adapting."""
        
        recent_adaptations = []
        current_time = time.time()
        one_hour_ago = current_time - 3600  # 1 hour
        
        for rule in self.living_rules.values():
            recent_rule_adaptations = [
                adaptation for adaptation in rule.adaptation_history
                if adaptation["timestamp"] > one_hour_ago
            ]
            recent_adaptations.extend(recent_rule_adaptations)
        
        return len(recent_adaptations) / max(1, len(self.living_rules))
    
    def get_system_intelligence_report(self) -> Dict[str, Any]:
        """Get comprehensive report on system intelligence and learning."""
        
        rule_intelligence = {}
        for name, rule in self.living_rules.items():
            rule_intelligence[name] = rule.get_current_intelligence()
        
        return {
            "system_overview": {
                "total_living_rules": len(self.living_rules),
                "total_interactions": len(self.agent_interaction_log),
                "system_adaptation_level": self._calculate_system_adaptation_level(),
                "learning_velocity": self._calculate_learning_velocity(),
                "meta_learning_active": self.meta_learning_active,
                "communication_integrated": self.is_integrated_with_agents
            },
            "rule_intelligence": rule_intelligence,
            "system_adaptations": len(self.system_adaptation_history),
            "learning_status": "ACTIVELY_EVOLVING" if self._calculate_system_adaptation_level() > 0.7 else "LEARNING"
        }
    
    def save_system_state(self, filepath: str = "system_intelligence_state.json"):
        """Save current system intelligence state."""
        
        state = {
            "timestamp": time.time(),
            "intelligence_report": self.get_system_intelligence_report(),
            "adaptation_history": self.system_adaptation_history,
            "rule_states": {
                name: {
                    "essence": rule.essence,
                    "original_essence": rule.original_essence,
                    "learning_confidence": rule.learning_confidence,
                    "success_rate": rule.success_rate,
                    "adaptation_count": len(rule.adaptation_history)
                }
                for name, rule in self.living_rules.items()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        
        print(f"💾 **SYSTEM INTELLIGENCE SAVED**: {filepath}")

# Global adaptive learning rule system
adaptive_rule_system = AdaptiveLearningRuleSystem()

async def process_agent_communication(agent_type: str, message: str, 
                                    context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main function to process agent communication through learning rule system.
    
    This integrates the living rule system into agent communication flow.
    """
    context = context or {}
    return await adaptive_rule_system.process_agent_message(agent_type, message, context)

def get_current_system_intelligence() -> Dict[str, Any]:
    """Get current system intelligence and learning status."""
    return adaptive_rule_system.get_system_intelligence_report()

def integrate_with_agents():
    """Integrate the rule system with agent communication."""
    
    def agent_handler(message):
        # This would be called by agents during communication
        return f"Processed through living rules: {message}"
    
    adaptive_rule_system.integrate_with_agent_communication(agent_handler)
    return "Rule system integrated into agent communication flow"

# Demonstration
if __name__ == "__main__":
    print("🧠 **ADAPTIVE LEARNING RULE SYSTEM DEMONSTRATION**\n")
    
    # Simulate agent communication with learning
    async def demo_learning_system():
        # Integrate with agent communication
        integrate_with_agents()
        
        # Simulate agent messages that teach the system
        test_messages = [
            ("agile_agent", "We need to coordinate the sprint planning for user story management", 
             {"detected_context": "agile_coordination", "performance_metrics": {"success": 0.9}}),
            
            ("code_agent", "Implementing clean code standards for the new feature module",
             {"detected_context": "code_development", "performance_metrics": {"quality": 0.8}}),
            
            ("test_agent", "All tests are passing, validation complete for the sprint delivery",
             {"detected_context": "testing_validation", "performance_metrics": {"test_success": 1.0}}),
            
            ("debug_agent", "Successfully resolved the integration issue using systematic problem solving",
             {"detected_context": "debugging_fixing", "performance_metrics": {"resolution": 0.95}})
        ]
        
        print("🔄 **SIMULATING AGENT COMMUNICATION WITH LEARNING:**\n")
        
        for agent_type, message, context in test_messages:
            print(f"Agent: {agent_type}")
            print(f"Message: {message}")
            
            # Process through learning system
            response = await process_agent_communication(agent_type, message, context)
            
            print(f"Active Rules: {', '.join(response['active_rules'])}")
            print(f"Learning Status: {response['system_learning_status']}")
            print()
        
        # Show system intelligence after learning
        print("🧠 **SYSTEM INTELLIGENCE AFTER LEARNING:**")
        intelligence = get_current_system_intelligence()
        
        print(f"System Adaptation Level: {intelligence['system_overview']['system_adaptation_level']:.2f}")
        print(f"Learning Velocity: {intelligence['system_overview']['learning_velocity']:.2f}")
        print(f"Total Interactions: {intelligence['system_overview']['total_interactions']}")
        print(f"Learning Status: {intelligence['learning_status']}")
        
        # Save system state
        adaptive_rule_system.save_system_state("demo_system_intelligence.json")
        
        print("\n🌟 **LIVING RULE SYSTEM IS LEARNING AND EVOLVING!**")
        print("   Rules adapt through every agent interaction")
        print("   System intelligence grows with experience") 
        print("   Agents and rules co-evolve together")
    
    # Run the demonstration
    asyncio.run(demo_learning_system())
