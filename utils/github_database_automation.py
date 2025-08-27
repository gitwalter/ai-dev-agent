#!/usr/bin/env python3
"""
GitHub Database Automation System.

This module automates the process of preparing the prompt database for GitHub distribution
by creating a clean version and updating gitignore accordingly.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.database_cleaner import DatabaseCleaner

logger = logging.getLogger(__name__)


class GitHubDatabaseAutomation:
    """
    Automates the process of preparing the database for GitHub distribution.
    """
    
    def __init__(self):
        """Initialize the automation system."""
        self.project_root = Path(__file__).parent.parent
        self.source_db_path = self.project_root / "prompts" / "prompt_templates.db"
        self.clean_db_path = self.project_root / "prompts" / "prompt_templates_clean.db"
        self.gitignore_path = self.project_root / ".gitignore"
        
    def run_full_automation(self) -> bool:
        """
        Run the complete automation process.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("🚀 Starting GitHub database automation...")
            
            # Step 1: Create clean database
            if not self._create_clean_database():
                return False
            
            # Step 2: Update .gitignore
            if not self._update_gitignore():
                return False
            
            # Step 3: Rename clean database to main database for GitHub
            if not self._prepare_for_github():
                return False
            
            # Step 4: Backup original database
            if not self._backup_original_database():
                return False
            
            logger.info("✅ GitHub database automation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Automation failed: {e}")
            return False
    
    def _create_clean_database(self) -> bool:
        """
        Create a clean version of the database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("📋 Creating clean database...")
            
            if not self.source_db_path.exists():
                logger.error(f"❌ Source database not found: {self.source_db_path}")
                return False
            
            cleaner = DatabaseCleaner(str(self.source_db_path))
            clean_db_path = cleaner.create_clean_database(str(self.clean_db_path))
            
            if not clean_db_path or not Path(clean_db_path).exists():
                logger.error("❌ Failed to create clean database")
                return False
            
            # Validate the clean database
            if not cleaner.validate_clean_database(clean_db_path):
                logger.error("❌ Clean database validation failed")
                return False
            
            logger.info(f"✅ Clean database created: {clean_db_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create clean database: {e}")
            return False
    
    def _update_gitignore(self) -> bool:
        """
        Update .gitignore to exclude development database but include clean database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("📝 Updating .gitignore...")
            
            if not self.gitignore_path.exists():
                logger.error(f"❌ .gitignore not found: {self.gitignore_path}")
                return False
            
            # Read current .gitignore
            with open(self.gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove the old database exclusion
            lines = content.split('\n')
            updated_lines = []
            
            for line in lines:
                # Keep all lines except the specific database exclusions we want to modify
                if line.strip() not in ['prompt_templates.db', '*.db', '*.sqlite', '*.sqlite3']:
                    updated_lines.append(line)
            
            # Add specific exclusions for development database
            updated_lines.extend([
                '',
                '# Database files - exclude development database with user data',
                'prompts/prompt_templates.db',
                '',
                '# Include clean database for GitHub distribution',
                '!prompts/prompt_templates_clean.db',
                '',
                '# Other database files',
                '*.sqlite',
                '*.sqlite3',
                'chroma.sqlite3',
                ''
            ])
            
            # Write updated .gitignore
            with open(self.gitignore_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(updated_lines))
            
            logger.info("✅ .gitignore updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update .gitignore: {e}")
            return False
    
    def _prepare_for_github(self) -> bool:
        """
        Prepare the clean database for GitHub by renaming it to the main database name.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("🔄 Preparing database for GitHub...")
            
            # Create a backup of the original database
            backup_path = self.project_root / "prompts" / "prompt_templates_backup.db"
            if self.source_db_path.exists():
                shutil.copy2(self.source_db_path, backup_path)
                logger.info(f"📦 Original database backed up to: {backup_path}")
            
            # Rename clean database to main database name
            if self.clean_db_path.exists():
                shutil.move(self.clean_db_path, self.source_db_path)
                logger.info("✅ Clean database renamed to main database name")
                return True
            else:
                logger.error("❌ Clean database not found for renaming")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to prepare database for GitHub: {e}")
            return False
    
    def _backup_original_database(self) -> bool:
        """
        Create a backup of the original database with user data.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = self.project_root / "prompts" / "prompt_templates_development.db"
            
            # If we have a backup from the previous step, use it
            temp_backup = self.project_root / "prompts" / "prompt_templates_backup.db"
            if temp_backup.exists():
                shutil.move(temp_backup, backup_path)
                logger.info(f"📦 Development database backed up to: {backup_path}")
                return True
            
            # If no backup exists, create one from current database
            if self.source_db_path.exists():
                shutil.copy2(self.source_db_path, backup_path)
                logger.info(f"📦 Development database backed up to: {backup_path}")
                return True
            
            logger.warning("⚠️ No database found to backup")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to backup original database: {e}")
            return False
    
    def restore_development_database(self) -> bool:
        """
        Restore the development database with user data.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("🔄 Restoring development database...")
            
            # Try to find the backup file
            backup_path = self.project_root / "prompts" / "prompt_templates_backup.db"
            
            if not backup_path.exists():
                # Try alternative backup name
                backup_path = self.project_root / "prompts" / "prompt_templates_development.db"
                
            if not backup_path.exists():
                logger.error(f"❌ Development database backup not found")
                logger.error(f"   Looked for: prompt_templates_backup.db and prompt_templates_development.db")
                return False
            
            # Restore the development database
            shutil.copy2(backup_path, self.source_db_path)
            logger.info("✅ Development database restored")
            
            # Update .gitignore to exclude the main database again
            self._update_gitignore_for_development()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to restore development database: {e}")
            return False
    
    def _update_gitignore_for_development(self) -> bool:
        """
        Update .gitignore for development mode (exclude main database).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("📝 Updating .gitignore for development...")
            
            if not self.gitignore_path.exists():
                return False
            
            # Read current .gitignore
            with open(self.gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove the clean database inclusion
            lines = content.split('\n')
            updated_lines = []
            
            for line in lines:
                if line.strip() not in ['!prompts/prompt_templates_clean.db']:
                    updated_lines.append(line)
            
            # Add back the main database exclusion
            updated_lines.extend([
                '',
                '# Database files - exclude main database with user data',
                'prompts/prompt_templates.db',
                ''
            ])
            
            # Write updated .gitignore
            with open(self.gitignore_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(updated_lines))
            
            logger.info("✅ .gitignore updated for development")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update .gitignore for development: {e}")
            return False
    
    def get_status(self) -> dict:
        """
        Get the current status of the database automation.
        
        Returns:
            Dictionary with status information
        """
        status = {
            'source_db_exists': self.source_db_path.exists(),
            'clean_db_exists': self.clean_db_path.exists(),
            'backup_exists': (self.project_root / "prompts" / "prompt_templates_development.db").exists(),
            'gitignore_exists': self.gitignore_path.exists(),
            'source_db_size': self.source_db_path.stat().st_size if self.source_db_path.exists() else 0,
            'clean_db_size': self.clean_db_path.stat().st_size if self.clean_db_path.exists() else 0,
        }
        
        return status


def run_github_preparation():
    """
    Run the complete GitHub preparation process.
    
    This function should be called before committing to GitHub.
    """
    automation = GitHubDatabaseAutomation()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting GitHub database preparation...")
    print("=" * 50)
    
    # Run automation
    success = automation.run_full_automation()
    
    if success:
        print("\n🎉 GitHub preparation completed successfully!")
        print("\n📋 Summary:")
        print("  ✅ Clean database created and prepared for GitHub")
        print("  ✅ .gitignore updated to exclude development data")
        print("  ✅ Original database backed up")
        print("\n📝 Next steps:")
        print("  1. Review the changes")
        print("  2. Commit the clean database to GitHub")
        print("  3. Push to repository")
        print("\n⚠️  Note: The main database now contains only clean templates")
        print("   To restore development database, run: restore_development_database()")
    else:
        print("\n❌ GitHub preparation failed!")
        print("Please check the logs for details.")
        return False
    
    return True


def restore_development_environment():
    """
    Restore the development environment with user data.
    
    This function should be called after pulling from GitHub to restore
    the development database with user data.
    """
    automation = GitHubDatabaseAutomation()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🔄 Restoring development environment...")
    print("=" * 50)
    
    # Restore development database
    success = automation.restore_development_database()
    
    if success:
        print("\n🎉 Development environment restored successfully!")
        print("\n📋 Summary:")
        print("  ✅ Development database restored with user data")
        print("  ✅ .gitignore updated for development")
        print("\n📝 You can now continue development with your data")
    else:
        print("\n❌ Development environment restoration failed!")
        print("Please check the logs for details.")
        return False
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Database Automation")
    parser.add_argument(
        'action',
        choices=['prepare', 'restore', 'status'],
        help='Action to perform: prepare (for GitHub), restore (development), or status'
    )
    
    args = parser.parse_args()
    
    automation = GitHubDatabaseAutomation()
    
    if args.action == 'prepare':
        run_github_preparation()
    elif args.action == 'restore':
        restore_development_environment()
    elif args.action == 'status':
        status = automation.get_status()
        print("Database Automation Status:")
        print(f"  Source DB exists: {status['source_db_exists']}")
        print(f"  Clean DB exists: {status['clean_db_exists']}")
        print(f"  Backup exists: {status['backup_exists']}")
        print(f"  Gitignore exists: {status['gitignore_exists']}")
        print(f"  Source DB size: {status['source_db_size']} bytes")
        print(f"  Clean DB size: {status['clean_db_size']} bytes")
