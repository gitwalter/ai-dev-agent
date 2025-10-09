#!/usr/bin/env python3
"""
Test Pipeline CLI Interface
==========================

Command-line interface for running the automated testing pipeline
with various modes and configurations.

Usage:
    python scripts/run_test_pipeline.py [mode]
    
Modes:
    full        - Complete test suite (default)
    quick       - Unit + Integration tests only
    pre-commit  - Fast validation for commits
    category    - Run specific test category
    report      - Generate reports from existing results
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.automated_testing_pipeline import AutomatedTestingPipeline

def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Automated Testing Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/run_test_pipeline.py                    # Run full pipeline
    python scripts/run_test_pipeline.py quick              # Quick validation
    python scripts/run_test_pipeline.py pre-commit         # Pre-commit checks
    python scripts/run_test_pipeline.py category unit      # Run only unit tests
    python scripts/run_test_pipeline.py report             # Generate report
        """
    )
    
    parser.add_argument(
        "mode",
        nargs="?",
        default="full",
        choices=["full", "quick", "pre-commit", "category", "report"],
        help="Pipeline execution mode"
    )
    
    parser.add_argument(
        "category",
        nargs="?",
        help="Test category for 'category' mode"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Force parallel execution (override category settings)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        help="Override timeout for test execution (seconds)"
    )
    
    parser.add_argument(
        "--quality-gate",
        type=float,
        help="Override quality gate threshold (percentage)"
    )
    
    parser.add_argument(
        "--output",
        choices=["console", "json", "html"],
        default="console",
        help="Output format for reports"
    )
    
    parser.add_argument(
        "--save-db",
        action="store_true",
        default=True,
        help="Save results to database (default: True)"
    )
    
    return parser

def run_full_pipeline(pipeline, args):
    """Run the complete testing pipeline."""
    print("🚀 Running full automated testing pipeline...")
    result = pipeline.run_full_pipeline()
    return result

def run_quick_pipeline(pipeline, args):
    """Run quick validation pipeline."""
    print("🏃‍♂️ Running quick validation pipeline...")
    pipeline.test_categories = {
        k: v for k, v in pipeline.test_categories.items() 
        if k in ["unit", "integration"]
    }
    result = pipeline.run_full_pipeline()
    return result

def run_pre_commit_pipeline(pipeline, args):
    """Run pre-commit validation pipeline."""
    print("🔍 Running pre-commit validation...")
    pipeline.test_categories = {
        k: v for k, v in pipeline.test_categories.items() 
        if k in ["unit"] and v["timeout"] <= 30
    }
    result = pipeline.run_full_pipeline()
    return result

def run_category_pipeline(pipeline, args):
    """Run specific test category."""
    if not args.category:
        print("❌ Category mode requires specifying a category")
        print(f"Available categories: {list(pipeline.test_categories.keys())}")
        return None
    
    if args.category not in pipeline.test_categories:
        print(f"❌ Unknown category: {args.category}")
        print(f"Available categories: {list(pipeline.test_categories.keys())}")
        return None
    
    print(f"🎯 Running {args.category} tests only...")
    
    # Keep only the specified category
    category_config = pipeline.test_categories[args.category].copy()
    
    # Apply overrides
    if args.parallel is not None:
        category_config["parallel"] = args.parallel
    if args.timeout:
        category_config["timeout"] = args.timeout
    if args.quality_gate:
        category_config["quality_gate"] = args.quality_gate
    
    pipeline.test_categories = {args.category: category_config}
    result = pipeline.run_full_pipeline()
    return result

def generate_report(pipeline, args):
    """Generate report from existing results."""
    print("📊 Generating test results report...")
    
    # TODO: Implement report generation from database
    print("⚠️ Report generation from database not yet implemented")
    print("   This would query the test_pipeline_results.db and generate reports")
    
    return None

def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Initialize pipeline
    try:
        pipeline = AutomatedTestingPipeline()
    except Exception as e:
        print(f"❌ Failed to initialize testing pipeline: {e}")
        sys.exit(1)
    
    # Execute based on mode
    result = None
    
    if args.mode == "full":
        result = run_full_pipeline(pipeline, args)
    elif args.mode == "quick":
        result = run_quick_pipeline(pipeline, args)
    elif args.mode == "pre-commit":
        result = run_pre_commit_pipeline(pipeline, args)
    elif args.mode == "category":
        result = run_category_pipeline(pipeline, args)
    elif args.mode == "report":
        result = generate_report(pipeline, args)
    
    # Handle result
    if result is None:
        print("⚠️ No pipeline execution performed")
        sys.exit(1)
    
    # Exit with appropriate code
    if result.overall_success:
        print(f"\n🎉 Pipeline completed successfully!")
        print(f"📊 {result.summary['total_passed']}/{result.summary['total_tests']} tests passed")
        sys.exit(0)
    else:
        print(f"\n💥 Pipeline failed!")
        print(f"📊 {result.summary['total_passed']}/{result.summary['total_tests']} tests passed")
        if result.blocking_issues:
            print("🚫 Blocking issues:")
            for issue in result.blocking_issues:
                print(f"   - {issue}")
        sys.exit(1)

if __name__ == "__main__":
    main()
