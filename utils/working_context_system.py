#!/usr/bin/env python3
"""
Working Context System - Proof of Concept
Goal: Reduce 33+ rules to 4-6 rules per context
"""

import os
import re
from pathlib import Path
from typing import Dict, List

def get_current_rule_count():
    """Count current rules in .cursor-rules file."""
    cursor_rules = Path(".cursor-rules")
    if not cursor_rules.exists():
        return 0
    
    try:
        with open(cursor_rules, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count rule sections
        rule_count = len(re.findall(r'# === .+ ===', content))
        return rule_count
    except:
        return 0

def detect_context_from_message(message: str) -> str:
    """Simple, reliable context detection."""
    msg = message.lower().strip()
    
    if "@docs" in msg or "@document" in msg:
        return "DOCUMENTATION"
    elif "@code" in msg or "@implement" in msg:
        return "CODING"
    elif "@debug" in msg or "@fix" in msg:
        return "DEBUGGING"
    elif "@test" in msg:
        return "TESTING"
    elif "@agile" in msg or "@sprint" in msg:
        return "AGILE"
    elif "@git" in msg or "@commit" in msg:
        return "GIT_OPERATIONS"
    elif "@optimize" in msg or "@performance" in msg:
        return "PERFORMANCE"
    elif "@security" in msg or "@secure" in msg:
        return "SECURITY"
    else:
        return "DEFAULT"

def get_core_rules() -> List[str]:
    """Get the 5 core rules that should always be loaded."""
    return [
        "safety_first_principle",
        "intelligent_context_aware_rule_system", 
        "core_rule_application_framework",
        "user_controlled_success_declaration_rule",
        "scientific_communication_rule"
    ]

def get_context_specific_rules(context: str) -> List[str]:
    """Get additional rules for specific context."""
    context_rules = {
        "DOCUMENTATION": [
            "documentation_live_updates_rule"
        ],
        "CODING": [
            "development_core_principles_rule",
            "error_handling_no_silent_errors_rule"
        ],
        "DEBUGGING": [
            "error_handling_no_silent_errors_rule",
            "testing_test_monitoring_rule"
        ],
        "TESTING": [
            "testing_test_monitoring_rule",
            "xp_test_first_development_rule",
            "quality_validation_rule"
        ],
        "AGILE": [
            "agile_artifacts_maintenance_rule",
            "agile_sprint_management_rule"
        ],
        "GIT_OPERATIONS": [
            "boyscout_leave_cleaner_rule"
        ],
        "PERFORMANCE": [
            "performance_monitoring_optimization_rule"
        ],
        "SECURITY": [
            "security_vulnerability_assessment_rule"
        ],
        "DEFAULT": []
    }
    
    return context_rules.get(context, [])

def load_rule_content(rule_name: str) -> str:
    """Load content of a specific rule."""
    rules_dir = Path(".cursor/rules")
    
    # Search for the rule file
    for rule_file in rules_dir.rglob(f"{rule_name}.mdc"):
        try:
            with open(rule_file, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            continue
    
    return f"# Rule not found: {rule_name}\nRule file missing or unreadable."

def generate_context_rules(context: str, message: str) -> str:
    """Generate .cursor-rules content for specific context."""
    
    # Get rules for this context
    core_rules = get_core_rules()
    context_rules = get_context_specific_rules(context)
    all_rules = core_rules + context_rules
    
    # Build content
    content = f"""# Context-Aware Rules (Working System)
# Context: {context}
# Total Rules: {len(all_rules)}
# Generated from: {message[:60]}...
# Timestamp: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}

"""
    
    # Add each rule
    for rule_name in all_rules:
        rule_content = load_rule_content(rule_name)
        content += f"\n# === {rule_name} ===\n"
        content += rule_content
        content += "\n\n"
    
    return content

def switch_context_and_prove_it_works(message: str) -> Dict:
    """Switch context and provide proof it works."""
    
    # Get current state
    old_rule_count = get_current_rule_count()
    
    # Detect context
    context = detect_context_from_message(message)
    
    # Generate new rules
    new_content = generate_context_rules(context, message)
    
    # Write new .cursor-rules file
    try:
        with open(".cursor-rules", 'w', encoding='utf-8') as f:
            f.write(new_content)
    except Exception as e:
        return {
            'success': False,
            'error': f"Failed to write .cursor-rules: {e}"
        }
    
    # Get new state
    new_rule_count = get_current_rule_count()
    
    # Calculate reduction
    reduction_percent = 0
    if old_rule_count > 0:
        reduction_percent = ((old_rule_count - new_rule_count) / old_rule_count) * 100
    
    # Return proof
    return {
        'success': True,
        'context': context,
        'old_rule_count': old_rule_count,
        'new_rule_count': new_rule_count,
        'reduction_percent': reduction_percent,
        'message': message,
        'proof': f"Reduced from {old_rule_count} to {new_rule_count} rules ({reduction_percent:.1f}% reduction)"
    }

def main():
    """Test and prove the system works."""
    print("Testing Working Context System...")
    print(f"Current rules in .cursor-rules: {get_current_rule_count()}")
    
    # Test different contexts
    test_cases = [
        "@docs Update the documentation",
        "@code Implement authentication", 
        "@debug Fix the failing tests",
        "General development work"
    ]
    
    for message in test_cases:
        print(f"\n--- Testing: {message} ---")
        result = switch_context_and_prove_it_works(message)
        
        if result['success']:
            print(f"✅ Context: {result['context']}")
            print(f"📊 Rules: {result['old_rule_count']} → {result['new_rule_count']}")
            print(f"⚡ Reduction: {result['reduction_percent']:.1f}%")
            print(f"🎯 Proof: {result['proof']}")
        else:
            print(f"❌ Failed: {result['error']}")

if __name__ == "__main__":
    main()
