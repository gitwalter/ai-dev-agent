#!/usr/bin/env python3
"""
Smart Prompt Sync Script
=========================

Intelligent synchronization between local prompts and LangSmith Hub.

Key Principles:
- Hub = Source of Truth
- Only push if explicitly edited locally AND different from hub
- Always pull hub changes unless local edits exist
- Track all changes with metadata

Usage Examples:
    # Sync all prompts (pull updates from hub)
    python scripts/sync_prompts.py --all
    
    # Sync specific prompt
    python scripts/sync_prompts.py --prompt test_generator_v1
    
    # Mark prompt as locally edited (before editing)
    python scripts/sync_prompts.py --mark-edited test_generator_v1
    
    # Sync and auto-push local changes
    python scripts/sync_prompts.py --all --auto-push
    
    # Dry run (see what would happen)
    python scripts/sync_prompts.py --all --dry-run
    
    # Check sync status of all prompts
    python scripts/sync_prompts.py --status
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.prompt_management.prompt_sync_manager import PromptSyncManager


def print_sync_result(result: dict):
    """Print sync result in readable format."""
    prompt_name = result['prompt_name']
    action = result['action']
    message = result['message']
    
    # Emoji indicators
    if result['conflict']:
        icon = "⚠️"
    elif not result['success']:
        icon = "❌"
    elif action == "pushed_to_hub":
        icon = "⬆️"
    elif action == "pulled_from_hub" or action == "updated_from_hub":
        icon = "⬇️"
    else:
        icon = "✅"
    
    print(f"{icon} {prompt_name}: {message}")


def print_status_table(status_list: list):
    """Print prompt status as a table."""
    print("\n📊 Prompt Sync Status")
    print("=" * 100)
    print(f"{'Prompt Name':<30} {'Modified':<10} {'Last Sync':<25} {'Direction':<10}")
    print("-" * 100)
    
    for status in status_list:
        name = status['prompt_name'][:28]
        modified = "✏️ YES" if status['locally_modified'] else "📥 No"
        last_sync = status['last_sync'][:23] if status['last_sync'] else "Never"
        direction = status['sync_direction'] or "-"
        
        print(f"{name:<30} {modified:<10} {last_sync:<25} {direction:<10}")
    
    print("=" * 100)


def main():
    parser = argparse.ArgumentParser(
        description="Smart Prompt Sync - Hub as Source of Truth",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync all prompts from hub
  python scripts/sync_prompts.py --all
  
  # Mark prompt as edited before editing locally
  python scripts/sync_prompts.py --mark-edited test_generator_v1
  
  # Sync specific prompt
  python scripts/sync_prompts.py --prompt code_generator_v1
  
  # Auto-push local changes
  python scripts/sync_prompts.py --all --auto-push
  
  # Check current status
  python scripts/sync_prompts.py --status
  
  # Dry run to see what would happen
  python scripts/sync_prompts.py --all --dry-run
        """
    )
    
    parser.add_argument("--all", "-a", action="store_true",
                       help="Sync all prompts")
    parser.add_argument("--prompt", "-p", type=str,
                       help="Sync specific prompt")
    parser.add_argument("--mark-edited", "-m", type=str,
                       help="Mark prompt as locally edited (do this BEFORE editing)")
    parser.add_argument("--auto-push", action="store_true",
                       help="Automatically push local changes to hub")
    parser.add_argument("--dry-run", action="store_true",
                       help="Dry run - show what would happen without making changes")
    parser.add_argument("--status", "-s", action="store_true",
                       help="Show sync status of all prompts")
    
    args = parser.parse_args()
    
    # Create sync manager
    manager = PromptSyncManager()
    
    # Handle status command
    if args.status:
        status_list = manager.get_sync_status()
        print_status_table(status_list)
        
        # Summary
        modified_count = sum(1 for s in status_list if s['locally_modified'])
        print(f"\n📝 Summary: {len(status_list)} prompts, {modified_count} locally modified")
        return 0
    
    # Handle mark-edited command
    if args.mark_edited:
        print(f"📝 Marking {args.mark_edited} as locally edited...")
        manager.mark_as_locally_edited(args.mark_edited)
        print(f"✅ Done! Now you can safely edit prompts/langsmith_cache/{args.mark_edited}.txt")  # noqa
        return 0
    
    # Handle sync commands
    if args.dry_run:
        print("🔍 DRY RUN MODE - No actual changes will be made\n")
    
    if args.all:
        print("🔄 Syncing all prompts...")
        if args.auto_push:
            print("⚠️  Auto-push enabled - local changes will be pushed to hub")
        print()
        
        results = manager.sync_all_prompts(auto_push=args.auto_push, dry_run=args.dry_run)
        
        # Print individual results
        for result in results['details']:
            print_sync_result(result)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Sync Summary")
        print("=" * 60)
        print(f"Total prompts:     {results['total']}")
        print(f"Pulled from hub:   {results['pulled']}")
        print(f"Updated from hub:  {results['updated']}")
        print(f"Pushed to hub:     {results['pushed']}")
        print(f"Conflicts:         {results['conflicts']}")
        print(f"Errors:            {results['errors']}")
        print("=" * 60)
        
        if results['conflicts'] > 0:
            print("\n⚠️  There are conflicts that need manual resolution")
            print("Run with --status to see which prompts need attention")
        
        return 0 if results['errors'] == 0 else 1
        
    elif args.prompt:
        print(f"🔄 Syncing {args.prompt}...")
        if args.auto_push:
            print("⚠️  Auto-push enabled - local changes will be pushed if different")
        print()
        
        result = manager.sync_prompt(args.prompt, auto_push=args.auto_push, dry_run=args.dry_run)
        print_sync_result(result)
        
        if result['conflict']:
            print("\n⚠️  Manual resolution needed:")
            print(f"   Local: prompts/langsmith_cache/{args.prompt}.txt")
            print(f"   Hub: View in LangSmith UI")
            print(f"   Choose: Edit local and run with --auto-push, or accept hub version")
        
        return 0 if result['success'] else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

