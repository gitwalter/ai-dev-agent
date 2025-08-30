#!/usr/bin/env python3
"""
Rule Application CLI - Command Line Interface for Formal Rule System

Provides command-line interface for systematic rule application,
optimization, and validation.
"""

import argparse
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.rule_system.formal_rule_catalog import apply_formal_rule_system, FORMAL_RULES
from utils.rule_system.intelligent_rule_optimizer import IntelligentRuleOptimizer, quick_rule_optimization

def main():
    """Main CLI interface for rule system."""
    
    parser = argparse.ArgumentParser(
        description="Formal Rule System - Systematic Rule Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rule_application_cli.py apply "Create new feature"
  python rule_application_cli.py optimize "Fix critical bug" --complexity complex
  python rule_application_cli.py validate
  python rule_application_cli.py report
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply rules to a task")
    apply_parser.add_argument("task", help="Task description")
    apply_parser.add_argument("--operation-type", default="", help="Operation type")
    apply_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Optimize command
    optimize_parser = subparsers.add_parser("optimize", help="Get rule optimization recommendations")
    optimize_parser.add_argument("task", help="Task description")
    optimize_parser.add_argument("--complexity", choices=["simple", "moderate", "complex", "advanced"], 
                                default="moderate", help="Task complexity")
    optimize_parser.add_argument("--time-pressure", type=float, default=0.5, help="Time pressure (0-1)")
    optimize_parser.add_argument("--quality-req", type=float, default=0.8, help="Quality requirements (0-1)")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate rule system consistency")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate optimization report")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all available rules")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--priority", help="Filter by priority")
    
    args = parser.parse_args()
    
    if args.command == "apply":
        apply_rules_command(args)
    elif args.command == "optimize":
        optimize_rules_command(args)
    elif args.command == "validate":
        validate_rules_command(args)
    elif args.command == "report":
        report_command(args)
    elif args.command == "list":
        list_rules_command(args)
    else:
        parser.print_help()

def apply_rules_command(args):
    """Apply rules to a task."""
    
    print("🎯 FORMAL RULE APPLICATION")
    print("=" * 50)
    print(f"Task: {args.task}")
    print(f"Operation Type: {args.operation_type or 'general'}")
    print()
    
    start_time = time.time()
    
    try:
        results = apply_formal_rule_system(args.task, args.operation_type)
        
        execution_time = time.time() - start_time
        
        print("📊 **APPLICATION RESULTS**")
        print(f"Execution Time: {execution_time:.3f}s")
        print(f"Rules Applied: {results['summary']['total_rules_applied']}")
        print(f"Success Rate: {results['summary']['success_rate']:.1%}")
        print(f"Complete: {'✅' if results['summary']['completeness'] else '❌'}")
        print()
        
        if args.verbose:
            print("📋 **DETAILED RESULTS**")
            print(f"Applicable Rules: {results['rule_application']['applicable_rules']}")
            print(f"Application Sequence: {results['rule_application']['application_sequence']}")
            print()
            
            for rule_id, result in results['rule_application']['application_results'].items():
                print(f"**{rule_id}**")
                print(f"  Success: {'✅' if result['success'] else '❌'}")
                if 'actions_taken' in result:
                    print(f"  Actions: {result['actions_taken']}")
                print()
        
        print("✅ **RULE APPLICATION COMPLETE**")
        
    except Exception as e:
        print(f"❌ **ERROR**: Rule application failed: {e}")
        sys.exit(1)

def optimize_rules_command(args):
    """Get optimization recommendations for a task."""
    
    print("🧠 INTELLIGENT RULE OPTIMIZATION")
    print("=" * 50)
    print(f"Task: {args.task}")
    print(f"Complexity: {args.complexity}")
    print(f"Time Pressure: {args.time_pressure}")
    print(f"Quality Requirements: {args.quality_req}")
    print()
    
    optimizer = IntelligentRuleOptimizer()
    
    context = {
        "task_type": args.task,
        "operation_type": "optimization",
        "time_pressure": args.time_pressure,
        "quality_requirements": args.quality_req
    }
    
    recommendations = optimizer.get_rule_recommendations(args.task)
    
    print("📊 **OPTIMIZATION ANALYSIS**")
    print(f"Task Complexity: {recommendations['task_analysis']['complexity']}")
    print(f"Risk Level: {recommendations['task_analysis']['risk_level']:.2f}")
    print()
    
    print("📋 **RULE RECOMMENDATIONS**")
    print(f"Optimal Rules: {len(recommendations['rule_selection']['optimal_rules'])}")
    for rule in recommendations['rule_selection']['optimal_rules']:
        print(f"  - {rule}")
    print()
    
    print("⚡ **EFFICIENCY INSIGHTS**")
    print(f"Estimated Time: {recommendations['efficiency_insights']['estimated_application_time']:.1f}s")
    print(f"Parallel Opportunities: {recommendations['efficiency_insights']['parallel_opportunities']}")
    print(f"Optimization Potential: {recommendations['efficiency_insights']['optimization_potential']:.1%}")
    print()
    
    print("🌟 **QUALITY INSIGHTS**")
    print(f"Quality Coverage: {recommendations['quality_insights']['quality_coverage']:.1%}")
    print(f"Risk Mitigation: {recommendations['quality_insights']['risk_mitigation']:.1%}")
    print(f"Excellence Score: {recommendations['quality_insights']['excellence_score']:.2f}/10")

def validate_rules_command(args):
    """Validate rule system consistency and completeness."""
    
    print("🔍 FORMAL RULE SYSTEM VALIDATION")
    print("=" * 50)
    
    catalog = FORMAL_RULES
    
    print("📊 **RULE CATALOG STATUS**")
    print(f"Total Rules: {len(catalog.rules)}")
    
    # Count by category
    categories = {}
    priorities = {}
    
    for rule in catalog.rules.values():
        categories[rule.category.value] = categories.get(rule.category.value, 0) + 1
        priorities[rule.priority.value] = priorities.get(rule.priority.value, 0) + 1
    
    print("Categories:")
    for category, count in categories.items():
        print(f"  {category}: {count} rules")
    
    print("Priorities:")
    for priority, count in priorities.items():
        print(f"  Level {priority}: {count} rules")
    print()
    
    print("🔗 **DEPENDENCY ANALYSIS**")
    dependency_count = sum(len(rule.dependencies) for rule in catalog.rules.values())
    print(f"Total Dependencies: {dependency_count}")
    
    # Check for circular dependencies
    try:
        test_context = {"task_type": "test", "operation_type": "validation"}
        applicable_rules = catalog.get_applicable_rules(test_context)
        sequence = catalog.get_rule_application_sequence(applicable_rules)
        print("✅ No circular dependencies detected")
        print(f"Application Phases: {len(sequence)}")
    except ValueError as e:
        print(f"❌ Circular dependency detected: {e}")
    
    print()
    print("✅ **VALIDATION COMPLETE**")

def report_command(args):
    """Generate optimization report."""
    
    print("📈 RULE OPTIMIZATION REPORT")
    print("=" * 50)
    
    optimizer = IntelligentRuleOptimizer()
    report = optimizer.generate_optimization_report()
    
    print(report)

def list_rules_command(args):
    """List all available rules with optional filtering."""
    
    print("📋 FORMAL RULE CATALOG")
    print("=" * 50)
    
    catalog = FORMAL_RULES
    rules_to_show = list(catalog.rules.values())
    
    # Apply filters
    if args.category:
        rules_to_show = [r for r in rules_to_show if r.category.value.lower() == args.category.lower()]
    
    if args.priority:
        rules_to_show = [r for r in rules_to_show if r.priority.name.lower() == args.priority.lower()]
    
    # Sort by priority and category
    rules_to_show.sort(key=lambda r: (r.priority.value, r.category.value))
    
    for rule in rules_to_show:
        print(f"**{rule.name}**")
        print(f"  ID: {rule.id}")
        print(f"  Priority: {rule.priority.name}")
        print(f"  Category: {rule.category.value}")
        print(f"  Scope: {rule.scope.value}")
        print(f"  Description: {rule.description}")
        if rule.dependencies:
            print(f"  Dependencies: {rule.dependencies}")
        print()

if __name__ == "__main__":
    main()
