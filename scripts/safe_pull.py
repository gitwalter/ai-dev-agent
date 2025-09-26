#!/usr/bin/env python3
"""
Safe Git Pull Script

This script handles the common issue where database files are staged
and conflict with git pull operations. It safely stashes changes,
pulls, and restores development database.
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple, Optional


class SafePull:
    """
    Safely handles git pull operations when database files are staged.
    """
    
    def __init__(self):
        """Initialize the safe pull utility."""
        self.project_root = Path(__file__).parent.parent
        self.database_files = [
            "prompts/prompt_templates.db",
            "prompts/prompt_templates_backup.db", 
            "prompts/prompt_templates_development.db",
            "prompts/prompt_templates_clean.db",
            ".gitignore"
        ]
    
    def run_safe_pull(self, restore_dev_db: bool = True) -> bool:
        """
        Perform a safe git pull with automatic stash/unstash.
        
        Args:
            restore_dev_db: Whether to restore development database after pull
            
        Returns:
            True if successful, False otherwise
        """
        print("🔄 Starting safe git pull...")
        
        try:
            # Check if we have any staged changes
            if self._has_staged_changes():
                print("📋 Staged changes detected - stashing before pull...")
                if not self._stash_changes():
                    return False
                    
                stashed = True
            else:
                stashed = False
                print("✅ No staged changes detected")
            
            # Perform the git pull
            print("⬇️  Pulling from remote...")
            if not self._git_pull():
                print("❌ Git pull failed")
                if stashed:
                    print("🔄 Attempting to restore stashed changes...")
                    self._unstash_changes()
                return False
            
            print("✅ Git pull completed successfully")
            
            # Restore development database if requested
            if restore_dev_db:
                print("🔄 Restoring development database...")
                if not self._restore_development_database():
                    print("⚠️  Failed to restore development database")
                    print("   You may need to run: python utils/git/github_database_automation.py restore")
                else:
                    print("✅ Development database restored")
            
            # Restore stashed changes if we had any
            if stashed:
                print("🔄 Restoring previously stashed changes...")
                if not self._unstash_changes():
                    print("⚠️  Failed to restore stashed changes")
                    print("   You may need to manually run: git stash pop")
                else:
                    print("✅ Stashed changes restored")
            
            print("🎉 Safe pull completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error during safe pull: {e}")
            return False
    
    def _has_staged_changes(self) -> bool:
        """Check if there are any staged changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False
    
    def _get_staged_files(self) -> List[str]:
        """Get list of staged files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return [f.strip() for f in result.stdout.split('\n') if f.strip()]
        except subprocess.CalledProcessError:
            return []
    
    def _stash_changes(self) -> bool:
        """Stash current changes including staged files."""
        try:
            # Stash staged and unstaged changes
            result = subprocess.run(
                ["git", "stash", "push", "-m", "Auto-stash before safe pull"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stash changes: {e}")
            return False
    
    def _unstash_changes(self) -> bool:
        """Restore stashed changes."""
        try:
            # Check if there are any stashes
            result = subprocess.run(
                ["git", "stash", "list"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                print("ℹ️  No stashes to restore")
                return True
            
            # Pop the most recent stash
            result = subprocess.run(
                ["git", "stash", "pop"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to restore stashed changes: {e}")
            return False
    
    def _git_pull(self) -> bool:
        """Perform git pull."""
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Git pull failed: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            return False
    
    def _restore_development_database(self) -> bool:
        """Restore the development database after pull."""
        try:
            # Import here to avoid circular imports
            sys.path.append(str(self.project_root))
            from utils.git.github_database_automation import GitHubDatabaseAutomation
            
            automation = GitHubDatabaseAutomation()
            return automation.restore_development_database()
        except Exception as e:
            print(f"❌ Failed to restore development database: {e}")
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Safely pull from Git with database automation")
    parser.add_argument(
        "--no-restore-db", 
        action="store_true",
        help="Skip restoring development database after pull"
    )
    
    args = parser.parse_args()
    
    safe_pull = SafePull()
    success = safe_pull.run_safe_pull(restore_dev_db=not args.no_restore_db)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
