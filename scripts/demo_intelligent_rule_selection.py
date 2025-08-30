#!/usr/bin/env python3
"""
Intelligent Rule Selection Demo

Demonstrates the difference between checking rule applicability and selective application.
Shows how the system intelligently selects only the most relevant rules for each task.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.rule_system.intelligent_rule_loader import (
    IntelligentRuleLoader, 
    TaskType, 
    TaskComplexity, 
    TaskContext
)

def print_selection_results(selection, task_description, context):
    """Print detailed selection results."""
    print(f"\n{'='*80}")
    print(f"TASK: {task_description}")
    print(f"CONTEXT: {context.task_type.value} | {context.complexity.value} | Quality: {context.quality_requirements}")
    print(f"{'='*80}")
    
    print(f"\n📊 SELECTION METRICS:")
    print(f"   Selected Rules: {len(selection.selected_rules)}")
    print(f"   Excluded Rules: {len(selection.excluded_rules)}")
    print(f"   Confidence Score: {selection.confidence_score:.2f}")
    print(f"   Token Savings: {selection.estimated_token_savings}")
    print(f"   Expected Effectiveness: {selection.expected_effectiveness:.2f}")
    
    print(f"\n✅ SELECTED RULES ({len(selection.selected_rules)}):")
    for i, rule in enumerate(selection.selected_rules, 1):
        reasoning = selection.selection_reasoning.get(rule, "No reasoning provided")
        print(f"   {i:2d}. {rule}")
        print(f"       └─ {reasoning}")
    
    print(f"\n❌ EXCLUDED RULES ({len(selection.excluded_rules)}):")
    for i, rule in enumerate(selection.excluded_rules, 1):
        reasoning = selection.selection_reasoning.get(rule, "No reasoning provided")
        print(f"   {i:2d}. {rule}")
        print(f"       └─ {reasoning}")

def demo_file_operation():
    """Demonstrate rule selection for file operations."""
    print("\n" + "="*80)
    print("DEMO 1: FILE OPERATION TASK")
    print("="*80)
    
    loader = IntelligentRuleLoader()
    
    # Simple file operation
    task_description = "Move files to organize project structure and clean up temporary files"
    context = TaskContext(
        task_type=TaskType.FILE_OPERATION,
        complexity=TaskComplexity.SIMPLE,
        time_pressure=0.3,
        quality_requirements=0.7
    )
    
    selection = loader.select_rules_for_task(task_description, context)
    print_selection_results(selection, task_description, context)

def demo_code_implementation():
    """Demonstrate rule selection for code implementation."""
    print("\n" + "="*80)
    print("DEMO 2: CODE IMPLEMENTATION TASK")
    print("="*80)
    
    loader = IntelligentRuleLoader()
    
    # Complex code implementation
    task_description = "Implement a secure authentication system with comprehensive unit tests and proper error handling"
    context = TaskContext(
        task_type=TaskType.CODE_IMPLEMENTATION,
        complexity=TaskComplexity.COMPLEX,
        time_pressure=0.6,
        quality_requirements=0.9,
        security_requirements=0.8
    )
    
    selection = loader.select_rules_for_task(task_description, context)
    print_selection_results(selection, task_description, context)

def demo_documentation_task():
    """Demonstrate rule selection for documentation tasks."""
    print("\n" + "="*80)
    print("DEMO 3: DOCUMENTATION TASK")
    print("="*80)
    
    loader = IntelligentRuleLoader()
    
    # Documentation task
    task_description = "Update README with comprehensive installation instructions and add detailed API documentation"
    context = TaskContext(
        task_type=TaskType.DOCUMENTATION,
        complexity=TaskComplexity.MODERATE,
        time_pressure=0.4,
        quality_requirements=0.8
    )
    
    selection = loader.select_rules_for_task(task_description, context)
    print_selection_results(selection, task_description, context)

def demo_security_task():
    """Demonstrate rule selection for security tasks."""
    print("\n" + "="*80)
    print("DEMO 4: SECURITY TASK")
    print("="*80)
    
    loader = IntelligentRuleLoader()
    
    # Security task
    task_description = "Implement secure API key management using Streamlit secrets and add vulnerability assessment"
    context = TaskContext(
        task_type=TaskType.SECURITY,
        complexity=TaskComplexity.MODERATE,
        time_pressure=0.7,
        quality_requirements=0.9,
        security_requirements=0.9
    )
    
    selection = loader.select_rules_for_task(task_description, context)
    print_selection_results(selection, task_description, context)

def demo_comparison():
    """Demonstrate how different contexts affect rule selection."""
    print("\n" + "="*80)
    print("DEMO 5: CONTEXT COMPARISON")
    print("="*80)
    
    loader = IntelligentRuleLoader()
    
    # Same task, different contexts
    task_description = "Create a new function"
    
    # Low quality, high time pressure
    low_quality_context = TaskContext(
        task_type=TaskType.CODE_IMPLEMENTATION,
        complexity=TaskComplexity.SIMPLE,
        time_pressure=0.9,
        quality_requirements=0.3
    )
    
    low_quality_selection = loader.select_rules_for_task(task_description, low_quality_context)
    
    # High quality, low time pressure
    high_quality_context = TaskContext(
        task_type=TaskType.CODE_IMPLEMENTATION,
        complexity=TaskComplexity.SIMPLE,
        time_pressure=0.2,
        quality_requirements=0.9
    )
    
    high_quality_selection = loader.select_rules_for_task(task_description, high_quality_context)
    
    print(f"\nTASK: {task_description}")
    print(f"\nLOW QUALITY / HIGH PRESSURE:")
    print(f"   Selected: {len(low_quality_selection.selected_rules)} rules")
    print(f"   Excluded: {len(low_quality_selection.excluded_rules)} rules")
    print(f"   Token Savings: {low_quality_selection.estimated_token_savings}")
    
    print(f"\nHIGH QUALITY / LOW PRESSURE:")
    print(f"   Selected: {len(high_quality_selection.selected_rules)} rules")
    print(f"   Excluded: {len(high_quality_selection.excluded_rules)} rules")
    print(f"   Token Savings: {high_quality_selection.estimated_token_savings}")
    
    print(f"\nDIFFERENCE:")
    print(f"   Rules selected: {len(high_quality_selection.selected_rules) - len(low_quality_selection.selected_rules)} more for high quality")
    print(f"   Token savings: {low_quality_selection.estimated_token_savings - high_quality_selection.estimated_token_savings} more for low quality")

def demo_critical_rules_always_included():
    """Demonstrate that critical rules are always included."""
    print("\n" + "="*80)
    print("DEMO 6: CRITICAL RULES ALWAYS INCLUDED")
    print("="*80)
    
    loader = IntelligentRuleLoader()
    
    critical_rules = [
        "SAFETY FIRST PRINCIPLE",
        "Context Awareness and Excellence Rule", 
        "No Premature Victory Declaration Rule"
    ]
    
    test_contexts = [
        ("Simple file move", TaskContext(TaskType.FILE_OPERATION, TaskComplexity.TRIVIAL)),
        ("Complex system design", TaskContext(TaskType.ARCHITECTURE, TaskComplexity.CRITICAL)),
        ("Quick bug fix", TaskContext(TaskType.DEBUGGING, TaskComplexity.SIMPLE)),
        ("Security audit", TaskContext(TaskType.SECURITY, TaskComplexity.COMPLEX))
    ]
    
    for task_desc, context in test_contexts:
        selection = loader.select_rules_for_task(task_desc, context)
        
        print(f"\nTask: {task_desc}")
        print(f"Context: {context.task_type.value} | {context.complexity.value}")
        
        missing_critical = []
        for rule in critical_rules:
            if rule not in selection.selected_rules:
                missing_critical.append(rule)
        
        if missing_critical:
            print(f"❌ MISSING CRITICAL RULES: {missing_critical}")
        else:
            print(f"✅ ALL CRITICAL RULES INCLUDED")
        
        print(f"   Total selected: {len(selection.selected_rules)}")
        print(f"   Total excluded: {len(selection.excluded_rules)}")

def demo_performance_summary():
    """Show performance summary of the intelligent rule selection."""
    print("\n" + "="*80)
    print("DEMO 7: PERFORMANCE SUMMARY")
    print("="*80)
    
    loader = IntelligentRuleLoader()
    
    # Run multiple selections to build history
    test_tasks = [
        ("File organization", TaskContext(TaskType.FILE_OPERATION, TaskComplexity.SIMPLE)),
        ("Code implementation", TaskContext(TaskType.CODE_IMPLEMENTATION, TaskComplexity.MODERATE)),
        ("Documentation update", TaskContext(TaskType.DOCUMENTATION, TaskComplexity.SIMPLE)),
        ("Security implementation", TaskContext(TaskType.SECURITY, TaskComplexity.COMPLEX)),
        ("Testing setup", TaskContext(TaskType.TESTING, TaskComplexity.MODERATE))
    ]
    
    total_tokens_saved = 0
    total_rules_selected = 0
    total_rules_excluded = 0
    
    for task_desc, context in test_tasks:
        selection = loader.select_rules_for_task(task_desc, context)
        total_tokens_saved += selection.estimated_token_savings
        total_rules_selected += len(selection.selected_rules)
        total_rules_excluded += len(selection.excluded_rules)
    
    summary = loader.get_selection_summary()
    
    print(f"\n📈 PERFORMANCE METRICS:")
    print(f"   Total selections: {summary['total_selections']}")
    print(f"   Average rules selected: {summary['average_rules_selected']}")
    print(f"   Average rules excluded: {summary['average_rules_excluded']}")
    print(f"   Average exclusion rate: {summary['average_exclusion_rate']}%")
    print(f"   Total token savings: {total_tokens_saved}")
    print(f"   Average token savings per task: {total_tokens_saved / len(test_tasks):.0f}")

def main():
    """Run all demonstrations."""
    print("🧠 INTELLIGENT RULE SELECTION DEMONSTRATION")
    print("="*80)
    print("This demo shows the difference between:")
    print("✅ CHECKING rule applicability (always done)")
    print("🎯 SELECTIVE application (only relevant rules)")
    print("="*80)
    
    # Run all demos
    demo_file_operation()
    demo_code_implementation()
    demo_documentation_task()
    demo_security_task()
    demo_comparison()
    demo_critical_rules_always_included()
    demo_performance_summary()
    
    print("\n" + "="*80)
    print("🎉 DEMONSTRATION COMPLETE")
    print("="*80)
    print("Key Takeaways:")
    print("1. Rules are ALWAYS checked for applicability")
    print("2. Only the most relevant rules are selected for application")
    print("3. Critical foundation rules are always included")
    print("4. Context (quality, time pressure, security) affects selection")
    print("5. Significant token savings are achieved through intelligent selection")
    print("6. Reasoning is provided for all selection decisions")
    print("="*80)

if __name__ == "__main__":
    main()
