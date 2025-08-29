#!/usr/bin/env python3
"""
Setup Daily Build Git Hooks

This script sets up Git hooks to support the Agile Daily Deployed Build Rule
by automatically triggering builds on certain Git operations.

Usage:
    python scripts/setup_daily_build_hooks.py [options]
    
Options:
    --dry-run: Show what would be done without making changes
    --force: Overwrite existing hooks
"""

import argparse
import stat
import sys
from pathlib import Path


def setup_daily_build_hooks(project_root: Path, dry_run: bool = False, force: bool = False) -> None:
    """Set up Git hooks for daily build automation."""
    
    git_hooks_dir = project_root / ".git" / "hooks"
    
    if not git_hooks_dir.exists():
        print("❌ Git hooks directory not found. Is this a Git repository?")
        sys.exit(1)
    
    hooks_to_create = {
        "pre-push": create_pre_push_hook(),
        "post-commit": create_post_commit_hook(),
        "post-merge": create_post_merge_hook()
    }
    
    for hook_name, hook_content in hooks_to_create.items():
        hook_file = git_hooks_dir / hook_name
        
        if hook_file.exists() and not force:
            print(f"⚠️  Hook {hook_name} already exists. Use --force to overwrite.")
            continue
        
        if dry_run:
            print(f"🔍 Would create/update hook: {hook_file}")
            continue
        
        # Create the hook
        with open(hook_file, 'w') as f:
            f.write(hook_content)
        
        # Make it executable
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
        
        print(f"✅ Created hook: {hook_name}")
    
    print("\n🎉 Daily build Git hooks setup complete!")
    print("\nHooks created:")
    print("- pre-push: Validates daily build completion before push")
    print("- post-commit: Triggers daily build check after commits")
    print("- post-merge: Triggers daily build after merges")


def create_pre_push_hook() -> str:
    """Create pre-push hook script."""
    
    return '''#!/bin/bash
#
# Pre-push hook for Daily Build validation
# 
# This hook ensures that daily build requirements are met before pushing to main/develop branches.
#

set -e

# Get the current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Only apply to main and develop branches
if [[ "$current_branch" == "main" || "$current_branch" == "develop" ]]; then
    echo "🔍 Validating daily build requirements for branch: $current_branch"
    
    # Check if daily build was completed today
    if ! python scripts/daily_build_automation.py --trigger-type manual --dry-run; then
        echo "❌ Daily build validation failed!"
        echo "💡 Run: python scripts/daily_build_automation.py --trigger-type manual"
        exit 1
    fi
    
    echo "✅ Daily build requirements validated"
fi

# Allow the push to proceed
exit 0
'''


def create_post_commit_hook() -> str:
    """Create post-commit hook script."""
    
    return '''#!/bin/bash
#
# Post-commit hook for Daily Build automation
#
# This hook checks if a daily build should be triggered after commits.
#

set -e

# Get the current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Only trigger for main and develop branches
if [[ "$current_branch" == "main" || "$current_branch" == "develop" ]]; then
    echo "🔍 Checking daily build status after commit..."
    
    # Check if daily build was already completed today
    build_status_file="monitoring/daily_build_status.json"
    
    if [[ -f "$build_status_file" ]]; then
        today=$(date +%Y-%m-%d)
        last_build_date=$(python -c "
import json
import datetime
try:
    with open('$build_status_file', 'r') as f:
        data = json.load(f)
    last_build = data.get('last_build', {}).get('timestamp', '')
    if last_build:
        build_date = datetime.datetime.fromisoformat(last_build.replace('Z', '+00:00')).date()
        print(build_date)
    else:
        print('1970-01-01')
except:
    print('1970-01-01')
        ")
        
        if [[ "$last_build_date" == "$today" ]]; then
            echo "✅ Daily build already completed today"
            exit 0
        fi
    fi
    
    echo "🚀 Triggering daily build for branch: $current_branch"
    
    # Trigger daily build in background
    nohup python scripts/daily_build_automation.py --trigger-type commit > /dev/null 2>&1 &
    
    echo "📋 Daily build triggered in background"
fi

exit 0
'''


def create_post_merge_hook() -> str:
    """Create post-merge hook script."""
    
    return '''#!/bin/bash
#
# Post-merge hook for Daily Build automation
#
# This hook triggers a daily build after merges to ensure integration quality.
#

set -e

# Get the current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)

echo "🔄 Post-merge hook triggered on branch: $current_branch"

# Always trigger build after merges to main/develop
if [[ "$current_branch" == "main" || "$current_branch" == "develop" ]]; then
    echo "🚀 Triggering daily build after merge to $current_branch"
    
    # Trigger daily build
    python scripts/daily_build_automation.py --trigger-type commit
    
    echo "✅ Daily build completed after merge"
else
    echo "ℹ️  Merge to feature branch, skipping daily build"
fi

exit 0
'''


def main():
    """Main entry point for daily build hooks setup."""
    
    parser = argparse.ArgumentParser(
        description="Setup Git hooks for daily build automation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing hooks"
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    print("🔧 Setting up daily build Git hooks...")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    try:
        setup_daily_build_hooks(project_root, args.dry_run, args.force)
    except Exception as e:
        print(f"❌ Failed to setup daily build hooks: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
