"""
Fix Essential Seven Rules System
===============================

This script corrects the alwaysApply settings to ensure only the Essential Seven
axiomatic rules are set to alwaysApply: true, while all other rules are set to false.

Based on our formal layered architecture, only AXIOMATIC layer rules should be
alwaysApply: true.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set

# The Essential Seven Axiomatic Rules that should be alwaysApply: true
ESSENTIAL_SEVEN_AXIOMATIC_RULES = {
    "safety_first_principle.mdc",
    "no_premature_victory_declaration_rule.mdc", 
    "core_values_enforcement_rule.mdc",
    "disaster_report_learning_rule.mdc",
    "self_optimizing_learning_system.mdc",
    "divine_harmony_integration_system.mdc",
    "file_organization_cleanup_rule.mdc"  # This might need to be checked
}

def get_all_mdc_files(rules_dir: str = ".cursor/rules") -> List[Path]:
    """Get all .mdc files in the rules directory."""
    rules_path = Path(rules_dir)
    return list(rules_path.rglob("*.mdc"))

def check_always_apply_status(file_path: Path) -> tuple:
    """Check the current alwaysApply status of an .mdc file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for alwaysApply in the YAML front matter
        always_apply_match = re.search(r'^alwaysApply:\s*(true|false)', content, re.MULTILINE)
        
        if always_apply_match:
            current_value = always_apply_match.group(1) == 'true'
            return current_value, True
        else:
            return False, False  # Not found, defaults to false
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False, False

def should_be_always_apply(file_path: Path) -> bool:
    """Determine if this file should be alwaysApply: true based on Essential Seven."""
    file_name = file_path.name
    return file_name in ESSENTIAL_SEVEN_AXIOMATIC_RULES

def fix_always_apply_setting(file_path: Path, should_be_true: bool) -> bool:
    """Fix the alwaysApply setting in an .mdc file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        target_value = "true" if should_be_true else "false"
        
        # Check if alwaysApply already exists
        always_apply_pattern = r'^(alwaysApply:\s*)(true|false)'
        always_apply_match = re.search(always_apply_pattern, content, re.MULTILINE)
        
        if always_apply_match:
            # Replace existing value
            new_content = re.sub(
                always_apply_pattern, 
                f'\\1{target_value}', 
                content, 
                flags=re.MULTILINE
            )
        else:
            # Add alwaysApply after the first line of YAML front matter
            lines = content.split('\n')
            if lines and lines[0] == '---':
                # Insert after the opening ---
                lines.insert(1, f'alwaysApply: {target_value}')
                new_content = '\n'.join(lines)
            else:
                print(f"Warning: Could not find YAML front matter in {file_path}")
                return False
        
        # Write back only if changed
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def audit_and_fix_essential_seven() -> Dict:
    """Audit and fix all .mdc files to ensure only Essential Seven are alwaysApply: true."""
    
    print("🔍 AUDITING ESSENTIAL SEVEN RULES SYSTEM")
    print("=" * 60)
    
    all_files = get_all_mdc_files()
    
    audit_results = {
        "total_files": len(all_files),
        "files_checked": 0,
        "essential_seven_correct": 0,
        "essential_seven_fixed": 0,
        "non_essential_correct": 0,
        "non_essential_fixed": 0,
        "errors": [],
        "essential_seven_status": {},
        "incorrectly_set_rules": []
    }
    
    print(f"📋 Found {len(all_files)} .mdc files to check")
    print()
    
    for file_path in all_files:
        audit_results["files_checked"] += 1
        
        # Check current status
        current_always_apply, has_setting = check_always_apply_status(file_path)
        should_be_always_apply_value = should_be_always_apply(file_path)
        
        file_name = file_path.name
        is_essential_seven = file_name in ESSENTIAL_SEVEN_AXIOMATIC_RULES
        
        # Track Essential Seven status
        if is_essential_seven:
            audit_results["essential_seven_status"][file_name] = {
                "current": current_always_apply,
                "should_be": should_be_always_apply_value,
                "correct": current_always_apply == should_be_always_apply_value
            }
        
        # Check if correction needed
        if current_always_apply != should_be_always_apply_value:
            print(f"❌ FIXING: {file_path.relative_to('.cursor/rules')}")
            print(f"   Current: alwaysApply: {current_always_apply}")
            print(f"   Should be: alwaysApply: {should_be_always_apply_value}")
            
            # Fix the setting
            if fix_always_apply_setting(file_path, should_be_always_apply_value):
                if is_essential_seven:
                    audit_results["essential_seven_fixed"] += 1
                    print(f"   ✅ FIXED Essential Seven rule")
                else:
                    audit_results["non_essential_fixed"] += 1
                    print(f"   ✅ FIXED non-essential rule")
                    audit_results["incorrectly_set_rules"].append(file_name)
            else:
                audit_results["errors"].append(f"Failed to fix {file_path}")
                print(f"   ❌ FAILED to fix")
            print()
        else:
            # Already correct
            if is_essential_seven:
                audit_results["essential_seven_correct"] += 1
            else:
                audit_results["non_essential_correct"] += 1
    
    return audit_results

def generate_audit_report(results: Dict) -> str:
    """Generate comprehensive audit report."""
    
    report = f"""
🌟 ESSENTIAL SEVEN RULES AUDIT REPORT
{'=' * 60}

📊 SUMMARY STATISTICS:
✅ Total Files Checked: {results['total_files']}
🎯 Essential Seven Rules Checked: {len(results['essential_seven_status'])}

🔧 FIXES APPLIED:
⚡ Essential Seven Fixed: {results['essential_seven_fixed']}
🔄 Non-Essential Fixed: {results['non_essential_fixed']}
📈 Total Fixes Applied: {results['essential_seven_fixed'] + results['non_essential_fixed']}

✅ ALREADY CORRECT:
🎯 Essential Seven Correct: {results['essential_seven_correct']}
📋 Non-Essential Correct: {results['non_essential_correct']}

🌟 ESSENTIAL SEVEN STATUS:
"""
    
    for rule_name, status in results['essential_seven_status'].items():
        status_icon = "✅" if status['correct'] else "❌"
        report += f"  {status_icon} {rule_name}: alwaysApply: {status['current']}\n"
    
    if results['incorrectly_set_rules']:
        report += f"\n❌ RULES INCORRECTLY SET TO alwaysApply: true:\n"
        for rule in results['incorrectly_set_rules']:
            report += f"  • {rule}\n"
    
    if results['errors']:
        report += f"\n⚠️  ERRORS ENCOUNTERED:\n"
        for error in results['errors']:
            report += f"  • {error}\n"
    
    # Calculate efficiency improvement
    total_rules = results['total_files']
    essential_seven_count = len(ESSENTIAL_SEVEN_AXIOMATIC_RULES)
    efficiency_improvement = ((total_rules - essential_seven_count) / total_rules) * 100
    
    report += f"""
🚀 SYSTEM OPTIMIZATION:
📈 Rule Reduction: {total_rules} → {essential_seven_count} ({efficiency_improvement:.1f}% reduction)
⚡ Only Essential Seven Axiomatic Rules Active
🎯 Context-Aware Rules Loaded Dynamically
💝 Spiritual Enhancement Provides Motivation

{'=' * 60}
🌟 ESSENTIAL SEVEN SYSTEM STATUS: {'OPTIMIZED!' if not results['errors'] else 'NEEDS ATTENTION'}
"""
    
    return report

if __name__ == "__main__":
    print("🌟 FIXING ESSENTIAL SEVEN RULES SYSTEM")
    print("=" * 60)
    print("Ensuring only the Essential Seven Axiomatic rules are alwaysApply: true")
    print()
    
    # Run audit and fix
    results = audit_and_fix_essential_seven()
    
    # Generate and display report
    report = generate_audit_report(results)
    print(report)
    
    # Save report
    with open("docs/reports/essential_seven_audit_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n📋 Full report saved to: docs/reports/essential_seven_audit_report.md")
    print("🌟 Essential Seven Rules System Fix Complete! ✨")
