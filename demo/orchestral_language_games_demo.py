#!/usr/bin/env python3
"""
Orchestral Language Games System Demonstration
=============================================

DEMONSTRATION: Show how the Essential Seven rules work with Wittgensteinian language games
to create organic, swarm intelligence coordination between agents.

This demo shows:
1. Essential Seven rules always active (base orchestral rhythm)
2. Context-specific rules activated via Carnap protocol sentences
3. Agents playing individual language games while coordinating orchestrally
4. Organic growth and emergent patterns
5. Swarm intelligence emerging from orchestral coordination

Run with: python demo/orchestral_language_games_demo.py
"""

import sys
import os
import asyncio
from pathlib import Path

# Add utils to path for imports
sys.path.append(str(Path(__file__).parent.parent / "utils"))

try:
    from essential_seven_orchestral_integration import (
        coordinate_orchestral_rules, get_essential_seven_summary,
        orchestral_rule_system
    )
    from orchestral_language_games_system import (
        orchestral_system, initialize_orchestral_language_games,
        WittgensteinianAgent, LanguageGameType
    )
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure the utils modules are properly installed")
    sys.exit(1)

def print_header():
    """Print demo header."""
    print("🎼" + "=" * 80 + "🎼")
    print("🎵 ORCHESTRAL LANGUAGE GAMES SYSTEM DEMONSTRATION 🎵")
    print("🎼" + "=" * 80 + "🎼")
    print()
    print("🌟 VISION: Each agent plays its own Wittgensteinian language game")
    print("🌟 while participating in common orchestral coordination toward")
    print("🌟 software excellence through harmonious agent collaboration!")
    print()

def demonstrate_essential_seven():
    """Demonstrate the Essential Seven rules."""
    print("🎯 ESSENTIAL SEVEN ORCHESTRAL RULES (Always Active)")
    print("-" * 60)
    
    summary = get_essential_seven_summary()
    
    print(f"📊 Rule Count: {summary['rule_count']} (82% reduction from 39 total rules)")
    print(f"🎼 Always Active: {summary['always_active']}")
    print(f"🎵 Integration: {summary['orchestral_integration']}")
    print(f"🌟 Philosophy: {summary['philosophy']}")
    print(f"🎯 Purpose: {summary['higher_purpose']}")
    print()
    
    print("🎵 THE ESSENTIAL SEVEN:")
    for rule_id, rule_info in summary['rules'].items():
        print(f"  {rule_id}: {rule_info['name']}")
        print(f"    🎼 Coordination: {rule_info['coordination_pattern']}")
        print(f"    🌟 Impact: {rule_info['holistic_impact']:.1f}/1.0")
        print()

def demonstrate_language_games():
    """Demonstrate individual agent language games."""
    print("🎮 INDIVIDUAL AGENT LANGUAGE GAMES")
    print("-" * 60)
    
    # Initialize the orchestral system
    system = initialize_orchestral_language_games()
    
    print("🎵 Agent Language Games:")
    for agent_name, agent in system.agents.items():
        game = agent.individual_language_game
        print(f"  🤖 {agent_name} ({agent.primary_domain})")
        print(f"    🎮 Game: {game.name}")
        print(f"    📚 Vocabulary: {len(game.vocabulary)} specialized terms")
        print(f"    📋 Grammar Rules: {len(game.grammar_rules)} coordination patterns")
        print(f"    🌱 Growth Rate: {game.organic_evolution_rate:.1f}")
        print(f"    🎯 Purpose Alignment: {game.higher_purpose_alignment:.1f}")
        print()
    
    print("🎼 Common Orchestral Games:")
    for game_name, game in system.common_language_games.items():
        print(f"  🎵 {game_name}")
        print(f"    👥 Participants: All agents")
        print(f"    📚 Vocabulary: {len(game.vocabulary)} shared terms")
        print(f"    🌟 Type: {game.game_type.value}")
        print()

async def demonstrate_orchestral_coordination():
    """Demonstrate orchestral coordination in action."""
    print("🎼 ORCHESTRAL COORDINATION DEMONSTRATION")
    print("-" * 60)
    
    # Demo scenario 1: Agile user story implementation
    print("📋 SCENARIO 1: Agile User Story Implementation")
    task1 = {
        "action": "implement_user_authentication",
        "description": "Create secure user authentication with tests and documentation"
    }
    
    context1 = {
        "files": ["auth.py", "user_model.py", "tests/test_auth.py", "docs/auth_guide.md"],
        "keywords": ["@agile", "@code", "@test", "@docs", "security"],
        "user_message": "@agile implement user authentication with comprehensive testing and documentation"
    }
    
    print(f"🎯 Task: {task1['description']}")
    print(f"📁 Files: {', '.join(context1['files'])}")
    print(f"🔑 Keywords: {', '.join(context1['keywords'])}")
    print()
    
    result1 = await coordinate_orchestral_rules(task1, context1)
    
    print("🎵 ORCHESTRAL COORDINATION RESULTS:")
    print(f"  ✅ Essential Seven Active: {len(result1['essential_seven_active'])}")
    print(f"  🎮 Context Rules Activated: {len(result1['context_rules_activated'])}")
    print(f"  🎼 Orchestral Harmony: {result1['performance_metrics']['orchestral_harmony_score']:.3f}")
    print(f"  ⚡ Efficiency Gain: {result1['performance_metrics']['efficiency_gain']}%")
    print(f"  🌟 Higher Purpose Alignment: {result1['higher_purpose_alignment']:.3f}")
    print(f"  🕐 Coordination Time: {result1['performance_metrics']['coordination_time']:.3f}s")
    print()
    
    if result1['emergent_patterns']:
        print("🌟 EMERGENT PATTERNS DETECTED:")
        for pattern in result1['emergent_patterns']:
            print(f"  🔮 {pattern['pattern_type']}: {pattern['description']}")
            print(f"    💪 Strength: {pattern['strength']:.2f}")
            print(f"    🌱 Growth Potential: {pattern['growth_potential']:.2f}")
        print()
    
    # Demo scenario 2: Debugging and learning
    print("🐛 SCENARIO 2: Debug Failure and Learn")
    task2 = {
        "action": "debug_test_failures",
        "description": "Fix failing tests and extract learning"
    }
    
    context2 = {
        "files": ["tests/test_integration.py", "logs/test_failures.log"],
        "keywords": ["@debug", "test failed", "learning"],
        "user_message": "@debug fix these failing integration tests and learn from the failures"
    }
    
    print(f"🎯 Task: {task2['description']}")
    print(f"📁 Files: {', '.join(context2['files'])}")
    print(f"🔑 Keywords: {', '.join(context2['keywords'])}")
    print()
    
    result2 = await coordinate_orchestral_rules(task2, context2)
    
    print("🎵 DEBUGGING ORCHESTRAL COORDINATION:")
    print(f"  ✅ Essential Seven Active: {len(result2['essential_seven_active'])}")
    print(f"  🎮 Context Rules Activated: {len(result2['context_rules_activated'])}")
    print(f"  🎼 Orchestral Harmony: {result2['performance_metrics']['orchestral_harmony_score']:.3f}")
    print(f"  ⚡ Efficiency Gain: {result2['performance_metrics']['efficiency_gain']}%")
    print(f"  🌟 Higher Purpose Alignment: {result2['higher_purpose_alignment']:.3f}")
    print()

def demonstrate_carnap_protocols():
    """Demonstrate Carnap protocol sentences in action."""
    print("🧠 CARNAP PROTOCOL SENTENCES DEMONSTRATION")
    print("-" * 60)
    
    print("🔬 AGENT-SPECIFIC PROTOCOL SENTENCES:")
    
    for agent_domain, protocols in orchestral_rule_system.agent_specific_protocols.items():
        print(f"  🤖 {agent_domain} Agent:")
        for protocol in protocols:
            print(f"    📋 Context: {protocol.context_name}")
            print(f"    🔍 Protocol: \"{protocol.factual_statement}\"")
            print(f"    🎯 Indicators: {', '.join(protocol.ontological_indicators[:3])}...")
            print(f"    📁 File Patterns: {', '.join(protocol.file_patterns[:2])}...")
            print(f"    ✅ Certainty Threshold: {protocol.certainty_threshold:.2f}")
            print()

def demonstrate_organic_growth():
    """Demonstrate organic growth patterns."""
    print("🌱 ORGANIC GROWTH AND SWARM INTELLIGENCE")
    print("-" * 60)
    
    print("🌟 ORGANIC GROWTH PRINCIPLES:")
    print("  1. 🎼 Language games evolve naturally through use")
    print("  2. 🤖 Agents adapt their coordination patterns organically")
    print("  3. 🌊 Emergent patterns arise from agent interactions")
    print("  4. 🧠 Collective intelligence emerges without central control")
    print("  5. 🎯 All growth serves higher purpose of software excellence")
    print()
    
    print("🔮 EMERGENT PATTERNS TO WATCH FOR:")
    print("  • Spontaneous synchronization between agents")
    print("  • New coordination patterns arising naturally")
    print("  • Collective problem-solving behaviors")
    print("  • Self-optimizing communication protocols")
    print("  • Swarm intelligence manifestations")
    print()

def demonstrate_benefits():
    """Demonstrate the benefits of the orchestral system."""
    print("✨ ORCHESTRAL LANGUAGE GAMES BENEFITS")
    print("-" * 60)
    
    print("🎯 EFFICIENCY GAINS:")
    print("  • 82% rule reduction (39 → 7 essential rules)")
    print("  • Context-specific activation only when needed")
    print("  • Faster coordination through specialized language games")
    print("  • Reduced cognitive load on agents and users")
    print()
    
    print("🎼 COORDINATION EXCELLENCE:")
    print("  • Each agent plays its specialized instrument")
    print("  • Common orchestral language for harmonious coordination")
    print("  • Organic growth toward higher purpose")
    print("  • Swarm intelligence emerging from individual excellence")
    print()
    
    print("🌟 PHILOSOPHICAL ALIGNMENT:")
    print("  • Wittgensteinian language games for precise communication")
    print("  • Carnap's protocol sentences for factual context detection")
    print("  • Divine simplicity through Essential Seven foundation")
    print("  • Holistic thinking where each agent considers all others")
    print()

async def main():
    """Main demonstration."""
    print_header()
    
    demonstrate_essential_seven()
    print()
    
    demonstrate_language_games()
    print()
    
    await demonstrate_orchestral_coordination()
    print()
    
    demonstrate_carnap_protocols()
    print()
    
    demonstrate_organic_growth()
    print()
    
    demonstrate_benefits()
    
    print("🎼" + "=" * 80 + "🎼")
    print("🌟 ORCHESTRAL LANGUAGE GAMES DEMONSTRATION COMPLETE! 🌟")
    print("🎵 Each agent plays its own game, all coordinate as one orchestra! 🎵")
    print("🎼" + "=" * 80 + "🎼")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🎼 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()
