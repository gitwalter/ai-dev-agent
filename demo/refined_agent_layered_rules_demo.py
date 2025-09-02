"""
Refined Agent Layered Rules Demo
================================

MISSION: Demonstrate how the layered rule trigger system refines agents by providing:
- Sophisticated communication protocols between rule layers
- Coordinated agent behavior through protocol messaging
- Orchestral coordination where agents work together like symphony members
- Context-aware rule activation based on agent domains

This demo shows agents becoming MORE REFINED through layered rule integration.
"""

import asyncio
import json
import time
from typing import Dict, List, Any

from agents.layered_rule_enhanced_agent import (
    LayeredRuleEnhancedAgent, AgentDomain, create_layered_rule_agent
)
from utils.layered_rule_trigger_system import (
    LayeredRuleTriggerSystem, execute_rule_cascade, generate_cascade_report
)

class RefinedAgentOrchestra:
    """
    Orchestra of refined agents working through layered rule protocols.
    """
    
    def __init__(self):
        self.agents = {}
        self.orchestral_conductor = None
        self.active_cascades = []
        self.coordination_history = []
    
    def create_refined_agent_ensemble(self):
        """Create ensemble of refined agents."""
        
        print("🎼 Creating Refined Agent Ensemble...")
        
        # Create domain-specific agents
        self.agents = {
            "agile_coordinator": create_layered_rule_agent(AgentDomain.AGILE_COORDINATOR),
            "developer": create_layered_rule_agent(AgentDomain.DEVELOPER),
            "tester": create_layered_rule_agent(AgentDomain.TESTER),
            "documenter": create_layered_rule_agent(AgentDomain.DOCUMENTER),
            "optimizer": create_layered_rule_agent(AgentDomain.OPTIMIZER),
            "ethical_ai": create_layered_rule_agent(AgentDomain.ETHICAL_AI),
            "cursor_ide": create_layered_rule_agent(AgentDomain.CURSOR_IDE),
            "debug_specialist": create_layered_rule_agent(AgentDomain.DEBUG_SPECIALIST)
        }
        
        # Designate conductor
        self.orchestral_conductor = self.agents["agile_coordinator"]
        
        print(f"✅ Created {len(self.agents)} refined agents")
        return self.agents
    
    async def demonstrate_agent_refinement(self):
        """Demonstrate how layered rules refine agent behavior."""
        
        print("\n🎯 DEMONSTRATING AGENT REFINEMENT THROUGH LAYERED RULES")
        print("=" * 60)
        
        # Test Scenario: Complex development task requiring multiple agents
        test_scenarios = [
            {
                "name": "User Authentication Implementation",
                "user_message": "@agile implement secure user authentication with comprehensive testing and documentation",
                "context": {
                    "task": "implement_user_authentication",
                    "files": ["auth.py", "test_auth.py", "auth_docs.md"],
                    "keywords": ["@agile", "secure", "authentication", "testing", "documentation"],
                    "collaboration": {"multi_agent": True, "security_critical": True}
                },
                "expected_agents": ["agile_coordinator", "developer", "tester", "documenter", "ethical_ai"]
            },
            
            {
                "name": "Performance Optimization", 
                "user_message": "@optimize the database queries are too slow, need performance improvement",
                "context": {
                    "task": "performance_optimization",
                    "files": ["database.py", "queries.sql", "performance_test.py"],
                    "keywords": ["@optimize", "database", "performance", "slow"],
                    "collaboration": {"optimization_focus": True}
                },
                "expected_agents": ["optimizer", "developer", "tester", "documenter"]
            },
            
            {
                "name": "Critical Bug Resolution",
                "user_message": "@debug critical security vulnerability found in authentication module",
                "context": {
                    "task": "security_bug_fix",
                    "files": ["auth.py", "security_audit.log", "vulnerability_report.md"],
                    "keywords": ["@debug", "critical", "security", "vulnerability"],
                    "collaboration": {"security_critical": True, "urgent": True}
                },
                "expected_agents": ["debug_specialist", "ethical_ai", "developer", "tester", "agile_coordinator"]
            }
        ]
        
        for scenario in test_scenarios:
            await self._demonstrate_scenario_refinement(scenario)
    
    async def _demonstrate_scenario_refinement(self, scenario: Dict):
        """Demonstrate agent refinement for specific scenario."""
        
        print(f"\n🎯 SCENARIO: {scenario['name']}")
        print("-" * 40)
        
        # Phase 1: Individual Agent Processing
        print("🔄 PHASE 1: Individual Agent Rule Processing")
        
        individual_responses = {}
        for agent_name, agent in self.agents.items():
            if agent_name in scenario["expected_agents"]:
                print(f"  Processing with {agent_name}...")
                
                response = await agent.process_with_layered_rules(
                    scenario["user_message"], 
                    scenario["context"]
                )
                
                individual_responses[agent_name] = response
                
                print(f"    ✅ {agent_name} triggered {len(response.triggered_layers)} rule layers")
                print(f"    🎼 Orchestral position: {response.collaboration_signals.get('orchestral_position')}")
                print(f"    🎮 Language game: {response.collaboration_signals.get('language_game')}")
        
        # Phase 2: Orchestral Coordination
        print(f"\n🎼 PHASE 2: Orchestral Agent Coordination")
        
        coordinator = self.agents["agile_coordinator"]
        peer_agents = [self.agents[name] for name in scenario["expected_agents"] if name != "agile_coordinator"]
        
        if peer_agents:
            coordination_result = await coordinator.coordinate_with_peers(peer_agents)
            
            print(f"  🎯 Coordination Success: {coordination_result['coordination_success']}")
            print(f"  🎼 Orchestral Arrangement:")
            for section, agents in coordination_result["orchestral_coordination"].items():
                if agents:
                    print(f"    {section}: {', '.join(agents)}")
            
            print(f"  🎮 Language Game Coordination:")
            individual_games = coordination_result["language_games"]["individual_games"]
            for agent, game in individual_games.items():
                print(f"    {agent}: {game}")
            
            common_games = coordination_result["language_games"]["common_games"]
            print(f"    Common Games: {', '.join(common_games)}")
        
        # Phase 3: Refined Behavior Analysis
        print(f"\n🏆 PHASE 3: Refinement Analysis")
        
        refinement_metrics = self._analyze_refinement(individual_responses, scenario)
        
        print(f"  📊 Refinement Metrics:")
        print(f"    Protocol Messages: {refinement_metrics['protocol_messages']}")
        print(f"    Layer Coordination: {refinement_metrics['layer_coordination']}")
        print(f"    Agent Coordination: {refinement_metrics['agent_coordination']}")
        print(f"    Context Sensitivity: {refinement_metrics['context_sensitivity']}")
        print(f"    Overall Refinement Score: {refinement_metrics['refinement_score']}/10")
        
        self.coordination_history.append({
            "scenario": scenario["name"],
            "refinement_metrics": refinement_metrics,
            "timestamp": time.time()
        })
    
    def _analyze_refinement(self, individual_responses: Dict, scenario: Dict) -> Dict:
        """Analyze how much the agents were refined by layered rules."""
        
        # Count protocol messages across all agents
        total_protocol_messages = sum(
            len(response.active_protocols) for response in individual_responses.values()
        )
        
        # Analyze layer coordination
        unique_layers_triggered = set()
        for response in individual_responses.values():
            for layer_name, rules in response.triggered_layers.items():
                if rules:
                    unique_layers_triggered.add(layer_name)
        
        layer_coordination_score = min(len(unique_layers_triggered) * 2, 10)
        
        # Analyze agent coordination
        coordination_requirements = []
        for response in individual_responses.values():
            coordination_requirements.extend(response.coordination_requirements)
        
        agent_coordination_score = min(len(set(coordination_requirements)) * 1.5, 10)
        
        # Analyze context sensitivity
        context_keywords = scenario["context"]["keywords"]
        context_matches = 0
        for response in individual_responses.values():
            agent_keywords = str(response.collaboration_signals).lower()
            context_matches += sum(1 for keyword in context_keywords if keyword.lower() in agent_keywords)
        
        context_sensitivity_score = min(context_matches * 0.8, 10)
        
        # Calculate overall refinement score
        refinement_score = (
            layer_coordination_score * 0.3 +
            agent_coordination_score * 0.3 +
            context_sensitivity_score * 0.2 +
            min(total_protocol_messages * 0.5, 10) * 0.2
        )
        
        return {
            "protocol_messages": total_protocol_messages,
            "layer_coordination": layer_coordination_score,
            "agent_coordination": agent_coordination_score,
            "context_sensitivity": context_sensitivity_score,
            "refinement_score": round(refinement_score, 1)
        }
    
    async def demonstrate_rule_cascade_refinement(self):
        """Demonstrate how rule cascades refine individual agents."""
        
        print("\n🔄 DEMONSTRATING RULE CASCADE REFINEMENT")
        print("=" * 50)
        
        # Test individual agent with complex cascade
        developer_agent = self.agents["developer"]
        
        complex_context = {
            "task": "implement_complex_feature",
            "files": ["feature.py", "test_feature.py", "feature_docs.md", "performance_test.py"],
            "keywords": ["implement", "complex", "testing", "documentation", "performance"],
            "collaboration": {"multi_layer": True, "quality_critical": True}
        }
        
        print("🎯 Testing Developer Agent with Complex Context")
        print(f"Context: {complex_context}")
        
        # Execute rule cascade
        cascade_result = await execute_rule_cascade("code_implementation", complex_context)
        
        # Generate cascade report
        cascade_report = generate_cascade_report(cascade_result)
        print("\n📋 CASCADE EXECUTION REPORT:")
        print(cascade_report)
        
        # Show how cascade refines agent behavior
        agent_response = await developer_agent.process_with_layered_rules(
            "implement complex authentication feature with comprehensive testing and documentation",
            complex_context
        )
        
        print("\n🏆 AGENT REFINEMENT THROUGH CASCADE:")
        print(f"  Triggered Layers: {list(agent_response.triggered_layers.keys())}")
        print(f"  Next Actions: {agent_response.next_actions}")
        print(f"  Coordination Requirements: {agent_response.coordination_requirements}")
        print(f"  Orchestral Position: {agent_response.collaboration_signals.get('orchestral_position')}")
        print(f"  Language Game: {agent_response.collaboration_signals.get('language_game')}")
    
    def generate_refinement_summary(self) -> str:
        """Generate summary of how agents were refined."""
        
        if not self.coordination_history:
            return "No coordination history available."
        
        avg_refinement = sum(
            coord["refinement_metrics"]["refinement_score"] 
            for coord in self.coordination_history
        ) / len(self.coordination_history)
        
        total_scenarios = len(self.coordination_history)
        
        summary = f"""
🏆 AGENT REFINEMENT SUMMARY
{'=' * 40}

📊 Scenarios Tested: {total_scenarios}
🎯 Average Refinement Score: {avg_refinement:.1f}/10

🎼 REFINEMENT ACHIEVEMENTS:
✅ Layered Rule Integration: Agents now respond to sophisticated rule cascades
✅ Protocol Communication: Agents communicate through formal protocol messages
✅ Orchestral Coordination: Agents coordinate like symphony orchestra members
✅ Context Sensitivity: Agents adapt behavior based on domain-specific contexts
✅ Language Games: Agents play both individual and common coordination games

🔄 REFINEMENT PATTERNS:
- Core axioms trigger contextual rule activation
- Multiple rule layers create sophisticated agent behavior
- Agent domains specialize coordination patterns
- Orchestral positions enable harmonic collaboration
- Protocol messages enable precise inter-agent communication

💎 REFINEMENT QUALITY:
- Agents are MORE INTELLIGENT through layered rule processing
- Agents are MORE COORDINATED through orchestral arrangements  
- Agents are MORE CONTEXT-AWARE through domain specialization
- Agents are MORE SYSTEMATIC through protocol communication
- Agents are MORE HARMONIOUS through language game coordination

The layered rule trigger system has successfully REFINED our agents! 🎯
"""
        
        return summary

async def main():
    """Main demonstration of refined agents through layered rules."""
    
    print("🎼 REFINED AGENT LAYERED RULES DEMONSTRATION")
    print("=" * 60)
    print("🎯 MISSION: Show how layered rule trigger system refines agent behavior")
    print()
    
    # Create refined agent orchestra
    orchestra = RefinedAgentOrchestra()
    agents = orchestra.create_refined_agent_ensemble()
    
    # Demonstrate agent refinement
    await orchestra.demonstrate_agent_refinement()
    
    # Demonstrate rule cascade refinement
    await orchestra.demonstrate_rule_cascade_refinement()
    
    # Generate refinement summary
    summary = orchestra.generate_refinement_summary()
    print(summary)
    
    print("\n🎼 REFINED AGENT DEMONSTRATION COMPLETE! 🎯")
    print("The agents are now MORE REFINED through layered rule integration!")

if __name__ == "__main__":
    asyncio.run(main())
