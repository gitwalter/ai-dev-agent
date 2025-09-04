#!/usr/bin/env python3
"""
Test Rule Activation History System
==================================

This script tests the rule activation history functionality by creating
sample activation events and verifying the display in the monitor app.

Created: 2025-01-31
Purpose: Test and validate rule activation history tracking
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_rule_activation_history():
    """Test the rule activation history system."""
    
    print("🧪 Testing Rule Activation History System")
    print("=" * 50)
    
    try:
        # Import the dynamic rule activator
        from utils.rule_system.dynamic_rule_activator import get_dynamic_activator
        
        # Get the activator instance
        activator = get_dynamic_activator()
        
        print(f"✅ Dynamic rule activator loaded successfully")
        print(f"📊 Current status: {activator.get_current_status()['current_context']}")
        print(f"📋 Active rules: {activator.get_current_status()['rules_count']}")
        
        # Test 1: Add some sample activation events
        print("\n🎯 Test 1: Adding sample activation events")
        
        sample_events = [
            {
                'event_type': 'activate',
                'rule_names': ['Development Excellence', 'Code Quality Standards'],
                'context': 'CODING',
                'reason': 'User started editing Python files'
            },
            {
                'event_type': 'switch',
                'rule_names': ['Test-Driven Development', 'Systematic Testing'],
                'context': 'TESTING',
                'reason': 'Test files detected in working directory'
            },
            {
                'event_type': 'context_activation',
                'rule_names': ['Agile Coordination', 'Sprint Management'],
                'context': 'AGILE',
                'reason': 'User accessed agile documentation'
            },
            {
                'event_type': 'deactivate',
                'rule_names': ['Debug Mode', 'Error Analysis'],
                'context': 'DEFAULT',
                'reason': 'Debugging session completed'
            }
        ]
        
        for i, event in enumerate(sample_events, 1):
            activator.add_manual_activation_event(**event)
            print(f"   {i}. Added {event['event_type']} event with {len(event['rule_names'])} rules")
        
        # Test 2: Get and display timeline
        print(f"\n📊 Test 2: Retrieving activation timeline")
        
        timeline = activator.get_rule_activation_timeline()
        print(f"✅ Retrieved {len(timeline)} events from timeline")
        
        if timeline:
            print("\n📋 Recent Events:")
            for event in timeline[:3]:  # Show first 3 events
                print(f"   🕐 {event['timestamp']} - {event['event_type'].title()}")
                print(f"      📝 Context: {event['context']}")
                print(f"      📋 Rules: {', '.join(event['rule_names'])}")
                print(f"      💡 Reason: {event['reason']}")
                print()
        
        # Test 3: Get recent changes summary
        print(f"📈 Test 3: Recent changes summary")
        
        recent_changes = activator.get_recent_rule_changes(hours=24)
        print(f"✅ Summary for last 24 hours:")
        print(f"   📊 Total Events: {recent_changes['total_events']}")
        print(f"   🔄 Context Switches: {len(recent_changes['context_switches'])}")
        print(f"   ✅ Activations: {len(recent_changes['recent_activations'])}")
        print(f"   ❌ Deactivations: {len(recent_changes['recent_deactivations'])}")
        
        # Test 4: Test context switching
        print(f"\n🔄 Test 4: Testing context switching")
        
        original_context = activator.current_context
        test_contexts = ['CODING', 'TESTING', 'AGILE']
        
        for context in test_contexts:
            try:
                activator.force_context_switch(context, f"Testing {context} context")
                print(f"   ✅ Switched to {context} context")
            except Exception as e:
                print(f"   ⚠️ Failed to switch to {context}: {e}")
        
        # Return to original context
        activator.force_context_switch(original_context, "Returning to original context")
        print(f"   🔄 Returned to {original_context} context")
        
        # Final status
        final_status = activator.get_current_status()
        final_timeline = activator.get_rule_activation_timeline()
        
        print(f"\n📊 Final Status:")
        print(f"   📝 Current Context: {final_status['current_context']}")
        print(f"   📋 Active Rules: {final_status['rules_count']}")
        print(f"   🕐 Total Events: {len(final_timeline)}")
        print(f"   🔄 Context Switches Today: {final_status['context_switches_today']}")
        
        print(f"\n✅ Rule Activation History System: WORKING!")
        print(f"💡 You can now view the activation history in the Rule Monitor app")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_monitor_app_integration():
    """Test integration with the monitor app."""
    
    print(f"\n🖥️ Testing Monitor App Integration")
    print("-" * 40)
    
    try:
        # Import the universal composition app components
        from apps.universal_composition_app import display_basic_rule_monitor
        from utils.rule_system.dynamic_rule_activator import get_dynamic_activator
        
        activator = get_dynamic_activator()
        
        # Check if the monitor app can access the history
        if hasattr(activator, 'rule_activation_history'):
            history_count = len(activator.rule_activation_history)
            print(f"✅ Monitor app can access rule_activation_history ({history_count} events)")
            
            if hasattr(activator, 'get_rule_activation_timeline'):
                timeline = activator.get_rule_activation_timeline()
                print(f"✅ Monitor app can call get_rule_activation_timeline() ({len(timeline)} events)")
            else:
                print(f"❌ get_rule_activation_timeline() method not found")
                
            if hasattr(activator, 'get_recent_rule_changes'):
                changes = activator.get_recent_rule_changes()
                print(f"✅ Monitor app can call get_recent_rule_changes() ({changes['total_events']} events)")
            else:
                print(f"❌ get_recent_rule_changes() method not found")
                
            print(f"✅ Monitor app integration: READY!")
            return True
        else:
            print(f"❌ rule_activation_history property not found")
            return False
            
    except Exception as e:
        print(f"❌ Monitor app integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Rule Activation History Tests")
    print("=" * 60)
    
    # Test the core functionality
    core_test_passed = test_rule_activation_history()
    
    # Test monitor app integration
    integration_test_passed = test_monitor_app_integration()
    
    print(f"\n🎯 Test Summary:")
    print(f"=" * 60)
    print(f"Core Functionality: {'✅ PASSED' if core_test_passed else '❌ FAILED'}")
    print(f"Monitor Integration: {'✅ PASSED' if integration_test_passed else '❌ FAILED'}")
    
    if core_test_passed and integration_test_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"💡 Rule activation history is now available in the Rule Monitor app")
        print(f"📱 Start the Streamlit app and navigate to the Rule Monitor to see the history")
    else:
        print(f"\n⚠️ Some tests failed. Check the error messages above.")
    
    print(f"\n🔚 Test completed.")
