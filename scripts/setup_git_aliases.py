#!/usr/bin/env python3
"""
Setup Git aliases for safe database operations.

This script configures useful Git aliases to handle database-related operations safely.
"""

import subprocess
import sys
from pathlib import Path


def setup_git_aliases():
    """Set up useful Git aliases for safe database operations."""
    
    print("🔧 Setting up Git aliases for safe database operations...")
    
    project_root = Path(__file__).parent.parent
    
    aliases = {
        "safe-pull": f"!python {project_root}/scripts/safe_pull.py",
        "db-status": f"!python {project_root}/utils/git/github_database_automation.py status",
        "db-prepare": f"!python {project_root}/utils/git/github_database_automation.py prepare",
        "db-restore": f"!python {project_root}/utils/git/github_database_automation.py restore",
    }
    
    for alias, command in aliases.items():
        try:
            subprocess.run(
                ["git", "config", "--global", f"alias.{alias}", command],
                check=True,
                capture_output=True
            )
            print(f"✅ Created alias: git {alias}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create alias {alias}: {e}")
            return False
    
    print("\n🎉 Git aliases created successfully!")
    print("\nYou can now use:")
    print("  git safe-pull    # Safely pull with database automation")
    print("  git db-status    # Check database automation status")
    print("  git db-prepare   # Manually prepare database for GitHub")
    print("  git db-restore   # Manually restore development database")
    
    return True


def main():
    """Main entry point."""
    if not setup_git_aliases():
        sys.exit(1)


if __name__ == "__main__":
    main()
