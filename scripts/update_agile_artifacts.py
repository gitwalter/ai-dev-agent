#!/usr/bin/env python3
"""
Agile Artifacts Auto-Update Script

This script provides a command-line interface for the Agile Artifacts Automation System.
Integrates with the Live Documentation Updates Rule for zero-manual-intervention updates.

Usage:
    python scripts/update_agile_artifacts.py --story-id US-002 --title "Testing Pipeline" --points 13
    python scripts/update_agile_artifacts.py --story-id US-003 --title "Database Cleanup" --points 5 --notes "Perfect implementation"
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.agile.artifacts_automation import (
    AgileArtifactsAutomator,
    StoryCompletion,
    update_agile_artifacts_for_story
)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Automatically update all agile artifacts when a story is completed",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete US-002 with basic information
  python scripts/update_agile_artifacts.py --story-id US-002 --title "Testing Pipeline" --points 13

  # Complete story with additional details
  python scripts/update_agile_artifacts.py \\
    --story-id US-003 \\
    --title "Database Cleanup Automation" \\
    --points 5 \\
    --notes "Perfect TDD implementation with 15/15 tests passing" \\
    --method "TDD" \\
    --test-results "15/15 passing"

  # Complete story with custom completion date
  python scripts/update_agile_artifacts.py \\
    --story-id US-001 \\
    --title "Health Monitoring" \\
    --points 8 \\
    --completion-date "2024-08-30"
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--story-id',
        required=True,
        help='Story ID (e.g., US-002, US-003)'
    )
    
    parser.add_argument(
        '--title',
        required=True,
        help='Story title (e.g., "Fully Automated Testing Pipeline")'
    )
    
    parser.add_argument(
        '--points',
        type=int,
        required=True,
        help='Story points value (e.g., 13, 5, 8)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--completion-date',
        help='Completion date (defaults to today, format: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--notes',
        default="",
        help='Additional completion notes'
    )
    
    parser.add_argument(
        '--method',
        default="",
        help='Implementation method (e.g., "TDD", "Agile")'
    )
    
    parser.add_argument(
        '--test-results',
        default="",
        help='Test results summary (e.g., "22/22 passing")'
    )
    
    parser.add_argument(
        '--acceptance-criteria',
        nargs='+',
        default=[],
        help='List of acceptance criteria (space-separated strings)'
    )
    
    parser.add_argument(
        '--tasks-completed',
        type=int,
        default=0,
        help='Number of tasks completed'
    )
    
    parser.add_argument(
        '--tasks-total',
        type=int,
        default=0,
        help='Total number of tasks'
    )
    
    # Options
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create backup before updating (recommended for production)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        default=True,
        help='Validate artifact consistency after updates (default: True)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without making changes'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    return parser.parse_args()


def print_story_summary(completion: StoryCompletion):
    """Print a summary of the story completion."""
    print("\n" + "="*60)
    print("📋 STORY COMPLETION SUMMARY")
    print("="*60)
    print(f"📌 Story ID: {completion.story_id}")
    print(f"📝 Title: {completion.title}")
    print(f"🎯 Story Points: {completion.story_points}")
    print(f"📅 Completion Date: {completion.completion_date}")
    print(f"✅ Status: {completion.status}")
    
    if completion.acceptance_criteria:
        print(f"📋 Acceptance Criteria ({len(completion.acceptance_criteria)}):")
        for i, criteria in enumerate(completion.acceptance_criteria, 1):
            print(f"   {i}. {criteria}")
    
    if completion.tasks_completed and completion.tasks_total:
        print(f"📊 Tasks: {completion.tasks_completed}/{completion.tasks_total} completed")
    
    if completion.notes:
        print(f"📝 Notes: {completion.notes}")
    
    if completion.implementation_method:
        print(f"🔧 Implementation Method: {completion.implementation_method}")
    
    if completion.test_results:
        print(f"🧪 Test Results: {completion.test_results}")
    
    print("="*60)


def print_update_results(result):
    """Print the results of the artifact updates."""
    print("\n" + "="*60)
    print("🚀 AGILE ARTIFACTS UPDATE RESULTS")
    print("="*60)
    
    if result.success:
        print("✅ **SUCCESSFUL UPDATE**")
        print(f"📊 Artifacts Updated: {result.artifacts_updated}/5")
        print(f"⏰ Timestamp: {result.timestamp}")
        
        # Show which artifacts were updated
        artifacts = [
            ("Daily Standup", result.daily_standup_updated),
            ("Sprint Progress", result.sprint_progress_updated),
            ("Velocity Tracking", result.velocity_tracking_updated),
            ("Sprint Backlog", result.sprint_backlog_updated),
            ("User Stories", result.user_stories_updated)
        ]
        
        print("\n📋 Updated Artifacts:")
        for artifact_name, updated in artifacts:
            status = "✅" if updated else "❌"
            print(f"   {status} {artifact_name}")
        
        if result.backup_created:
            print(f"\n💾 Backup Created: {result.backup_location}")
        
    else:
        print("❌ **UPDATE FAILED**")
        print(f"📊 Artifacts Updated: {result.artifacts_updated}/5")
        
        if result.errors:
            print("\n🚨 Errors:")
            for error in result.errors:
                print(f"   • {error}")
    
    print("="*60)


def main():
    """Main entry point for the agile artifacts update script."""
    args = parse_arguments()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
    # Set completion date
    completion_date = args.completion_date or datetime.now().strftime("%Y-%m-%d")
    
    # Create story completion object
    completion = StoryCompletion(
        story_id=args.story_id,
        title=args.title,
        story_points=args.points,
        completion_date=completion_date,
        status="completed",
        acceptance_criteria=args.acceptance_criteria,
        tasks_completed=args.tasks_completed,
        tasks_total=args.tasks_total,
        notes=args.notes,
        implementation_method=args.method,
        test_results=args.test_results
    )
    
    # Print story summary
    print_story_summary(completion)
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")
        print("✅ Story information validated successfully")
        print("🚀 Would update all 5 agile artifacts")
        return 0
    
    try:
        # Find docs directory
        docs_dir = project_root / "docs" / "agile"
        if not docs_dir.exists():
            logger.error(f"❌ Docs directory not found: {docs_dir}")
            print(f"\n❌ ERROR: Docs directory not found: {docs_dir}")
            return 1
        
        logger.info(f"📁 Using docs directory: {docs_dir}")
        
        # Initialize automator
        automator = AgileArtifactsAutomator(
            docs_dir=docs_dir,
            enable_backup=args.backup,
            enable_locking=True  # Always use locking for safety
        )
        
        # Update all artifacts
        logger.info(f"🚀 Updating agile artifacts for {completion.story_id}")
        result = automator.update_all_artifacts(completion, include_timestamps=True)
        
        # Print results
        print_update_results(result)
        
        # Validate if requested
        if args.validate and result.success:
            print("\n🔍 Validating artifact consistency...")
            validation_result = automator.validate_artifact_consistency(completion)
            
            if validation_result.is_consistent:
                print("✅ All artifacts are consistent")
            else:
                print("⚠️  Inconsistencies detected:")
                for inconsistency in validation_result.inconsistencies:
                    print(f"   • {inconsistency}")
        
        # Return appropriate exit code
        return 0 if result.success else 1
        
    except Exception as e:
        logger.exception("❌ Unexpected error occurred")
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
