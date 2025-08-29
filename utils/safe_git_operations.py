#!/usr/bin/env python3
"""
Safe Git Operations for Database Automation.

This module provides utilities for safely handling git operations
when database files might be staged or modified.
"""

import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Tuple


logger = logging.getLogger(__name__)


class SafeGitOperations:
    """
    Provides safe git operations for database automation.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize safe git operations.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self.database_files = [
            "prompts/prompt_templates.db",
            "prompts/prompt_templates_backup.db",
            "prompts/prompt_templates_development.db", 
            "prompts/prompt_templates_clean.db",
            ".gitignore"
        ]
    
    def check_git_status(self) -> Tuple[bool, List[str], List[str]]:
        """
        Check the current git status.
        
        Returns:
            Tuple of (has_changes, staged_files, unstaged_files)
        """
        try:
            # Get staged files
            staged_result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            staged_files = [f.strip() for f in staged_result.stdout.split('\n') if f.strip()]
            
            # Get unstaged files
            unstaged_result = subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            unstaged_files = [f.strip() for f in unstaged_result.stdout.split('\n') if f.strip()]
            
            has_changes = bool(staged_files or unstaged_files)
            
            return has_changes, staged_files, unstaged_files
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to check git status: {e}")
            return False, [], []
    
    def has_database_files_staged(self) -> bool:
        """
        Check if any database files are currently staged.
        
        Returns:
            True if database files are staged, False otherwise
        """
        _, staged_files, _ = self.check_git_status()
        
        for db_file in self.database_files:
            if db_file in staged_files:
                return True
        
        return False
    
    def get_staged_database_files(self) -> List[str]:
        """
        Get list of staged database files.
        
        Returns:
            List of staged database file paths
        """
        _, staged_files, _ = self.check_git_status()
        
        staged_db_files = []
        for db_file in self.database_files:
            if db_file in staged_files:
                staged_db_files.append(db_file)
        
        return staged_db_files
    
    def unstage_database_files(self) -> bool:
        """
        Unstage any staged database files.
        
        Returns:
            True if successful, False otherwise
        """
        staged_db_files = self.get_staged_database_files()
        
        if not staged_db_files:
            logger.info("No database files staged")
            return True
        
        try:
            logger.info(f"Unstaging database files: {staged_db_files}")
            
            for db_file in staged_db_files:
                subprocess.run(
                    ["git", "reset", "HEAD", db_file],
                    cwd=self.project_root,
                    check=True,
                    capture_output=True
                )
            
            logger.info("✅ Database files unstaged successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to unstage database files: {e}")
            return False
    
    def stash_database_changes(self, message: str = "Auto-stash database changes") -> bool:
        """
        Stash changes to database files only.
        
        Args:
            message: Commit message for the stash
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if we have any database file changes
            _, staged_files, unstaged_files = self.check_git_status()
            all_changed_files = set(staged_files + unstaged_files)
            
            db_changes = []
            for db_file in self.database_files:
                if db_file in all_changed_files:
                    db_changes.append(db_file)
            
            if not db_changes:
                logger.info("No database file changes to stash")
                return True
            
            logger.info(f"Stashing database file changes: {db_changes}")
            
            # Stash only the database files
            cmd = ["git", "stash", "push", "-m", message] + db_changes
            subprocess.run(
                cmd,
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            
            logger.info("✅ Database changes stashed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to stash database changes: {e}")
            return False
    
    def restore_stashed_changes(self) -> bool:
        """
        Restore the most recent stash.
        
        Returns:
            True if successful, False otherwise
        """
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
                logger.info("No stashes to restore")
                return True
            
            # Pop the most recent stash
            subprocess.run(
                ["git", "stash", "pop"],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )
            
            logger.info("✅ Stashed changes restored successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to restore stashed changes: {e}")
            return False
    
    def prepare_for_pull(self) -> Tuple[bool, bool]:
        """
        Prepare repository for a safe git pull by handling staged database files.
        
        Returns:
            Tuple of (success, stashed_changes)
        """
        try:
            logger.info("🔧 Preparing for safe git pull...")
            
            # Check if we have staged database files
            if not self.has_database_files_staged():
                logger.info("✅ No staged database files detected")
                return True, False
            
            # Stash database file changes
            if not self.stash_database_changes("Auto-stash before pull"):
                logger.error("Failed to stash database changes")
                return False, False
            
            logger.info("✅ Repository prepared for pull")
            return True, True
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare for pull: {e}")
            return False, False
    
    def cleanup_after_pull(self, had_stashed_changes: bool) -> bool:
        """
        Clean up after git pull by restoring stashed changes if any.
        
        Args:
            had_stashed_changes: Whether we stashed changes before pull
            
        Returns:
            True if successful, False otherwise
        """
        if not had_stashed_changes:
            logger.info("No cleanup needed after pull")
            return True
        
        try:
            logger.info("🔧 Cleaning up after pull...")
            
            # Restore stashed changes
            if not self.restore_stashed_changes():
                logger.warning("Failed to restore stashed changes - manual intervention may be needed")
                logger.warning("Run 'git stash pop' manually to restore your changes")
                return False
            
            logger.info("✅ Cleanup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup after pull: {e}")
            return False


def main():
    """Main entry point for testing."""
    logging.basicConfig(level=logging.INFO)
    
    safe_git = SafeGitOperations()
    
    # Check current status
    has_changes, staged, unstaged = safe_git.check_git_status()
    
    print(f"Has changes: {has_changes}")
    print(f"Staged files: {staged}")
    print(f"Unstaged files: {unstaged}")
    print(f"Database files staged: {safe_git.has_database_files_staged()}")
    print(f"Staged database files: {safe_git.get_staged_database_files()}")


if __name__ == "__main__":
    main()
