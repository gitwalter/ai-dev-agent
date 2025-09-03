#!/usr/bin/env python3
"""
Demo: IDE-Triggered Rule Selection
"""

import sys
sys.path.append('.')
from utils.ide_triggered_rule_selector import trigger_rule_selection, get_analytics

def demo_ide_trigger():
    """Demonstrate IDE-triggered rule selection."""
    
    print("🎯 **IDE-TRIGGERED RULE SELECTION DEMO**\n")
    
    # Your current message
    message = "@agile the ide must always trigger the rule selection after the user sends a chat message"
    
    # Trigger rule selection (simulating IDE behavior)
    result = trigger_rule_selection(message)
    
    print(f"User Message: {message}")
    print(f"Context Detected: {result['context']}")
    print(f"Rules Selected: {result['rule_count']} rules")
    print(f"Generation Speed: {result['generation_time_ms']:.1f}ms")
    print(f"Token Count: {result['token_count']} tokens")
    print(f"Cursor Rules Updated: {result['cursor_rules_updated']}")
    print(f"Efficiency: {result['efficiency_note']}")
    
    print("\n📊 **SYSTEM ANALYTICS:**")
    analytics = get_analytics()
    print(f"Total Messages Processed: {analytics['total_messages_processed']}")
    print(f"Current Context: {analytics['current_context']}")
    print(f"Efficiency: {analytics['compression_efficiency']['efficiency_percentage']:.0f}%")
    
    print("\n✅ **IDE INTEGRATION COMPLETE**")
    print("   - Message detected → Context analyzed → Rules selected → .cursor-rules updated")
    print("   - LLM now has optimal rule set for AGILE context")
    print("   - System ready for next message trigger")

if __name__ == "__main__":
    demo_ide_trigger()
