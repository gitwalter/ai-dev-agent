#!/usr/bin/env python3
"""
Database Cleanup Git Hook
=========================

Comprehensive database cleanup for Git operations to prevent sensitive
runtime data from being committed to GitHub.

This script is designed to run as a git pre-commit hook.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Any
import sqlite3

class DatabaseCleanupHook:
    """Git hook for comprehensive database cleanup."""
    
    def __init__(self):
        self.project_root = Path().resolve()
        
        # Database cleanup policy based on analysis
        self.runtime_databases = [
            # Core agent tracking (69.18 MB, 163k+ records)
            "utils/universal_agent_tracking.db",
            "utils/database/universal_agent_tracking.db",
            
            # Analytics and monitoring databases
            "utils/analytics.db",
            "utils/database/analytics.db",
            "utils/optimization.db", 
            "utils/database/optimization.db",
            "utils/rule_optimization.db",
            "utils/database/rule_optimization.db",
            "utils/strategic_selection.db",
            "utils/database/strategic_selection.db",
            
            # Security and backup tracking
            "utils/security_events.db",
            "utils/database/security_events.db",
            "utils/backup_tracking.db",
            "utils/database/backup_tracking.db",
            "prompt_backups/backup_tracking.db",
            
            # Learning and experience databases
            "utils/learning_experiences.db",
            "utils/database/learning_experiences.db",
            
            # Test and cache databases
            "utils/test_pipeline_results.db",
            "data/research_cache.db"
        ]
        
        # Temporary files that shouldn't be committed
        self.temp_file_patterns = [
            "*.tmp",
            "*.temp", 
            "*.bak",
            "*.backup",
            "*_temp.py",
            "test_*.py",  # root level test files
            "analyze_*.py",  # root level analysis files
            "verify_*.py",  # root level verification files
            "fix_*.py",  # root level fix files
            "emergency_*.py"  # root level emergency files
        ]
        
    def run_cleanup(self) -> bool:
        """Run comprehensive database cleanup."""
        print("🧹 Running Database Cleanup Hook")
        print("=" * 50)
        
        success = True
        
        # 1. Clean runtime databases
        success &= self.clean_runtime_databases()
        
        # 2. Clean temporary files
        success &= self.clean_temporary_files()
        
        # 3. Verify .gitignore is up to date
        success &= self.verify_gitignore()
        
        # 4. Check for large files
        success &= self.check_large_files()
        
        if success:
            print("\n✅ Database cleanup completed successfully")
        else:
            print("\n❌ Database cleanup failed - commit blocked")
            
        return success
    
    def clean_runtime_databases(self) -> bool:
        """Clean or remove runtime databases."""
        print("\n🗄️ Cleaning runtime databases...")
        
        cleaned_count = 0
        
        for db_path in self.runtime_databases:
            full_path = self.project_root / db_path
            
            if full_path.exists():
                size_mb = full_path.stat().st_size / (1024 * 1024)
                
                if size_mb > 0.1:  # Only report significant databases
                    print(f"  🧹 Cleaning {db_path} ({size_mb:.2f} MB)")
                    
                    # For very large databases, just remove them
                    if size_mb > 10:
                        full_path.unlink()
                        print(f"    ❌ Removed large database")
                    else:
                        # For smaller databases, clean them
                        self.clean_database_content(full_path)
                        print(f"    🧽 Cleaned database content")
                    
                    cleaned_count += 1
        
        print(f"  📊 Cleaned {cleaned_count} runtime databases")
        return True
    
    def clean_database_content(self, db_path: Path) -> None:
        """Clean the content of a database file."""
        try:
            # Create empty database with same schema
            backup_path = db_path.with_suffix('.db.backup')
            shutil.copy2(db_path, backup_path)
            
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                
                # Get all table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Clear all data but keep schema
                for table in tables:
                    cursor.execute(f"DELETE FROM {table}")
                
                conn.commit()
                
        except Exception as e:
            print(f"    ⚠️ Warning: Could not clean {db_path}: {e}")
    
    def clean_temporary_files(self) -> bool:
        """Clean temporary files from root directory."""
        print("\n🗑️ Cleaning temporary files...")
        
        cleaned_count = 0
        
        # Check for specific temporary files in root
        temp_files = [
            "analyze_databases.py",
            "emergency_agent_cleanup.py", 
            "fix_agent_bug.py",
            "test_integration.py",
            "test_live_logging.py",
            "verify_fix.py",
            "temp_agent_check.py"
        ]
        
        for temp_file in temp_files:
            file_path = self.project_root / temp_file
            if file_path.exists():
                print(f"  🗑️ Removing {temp_file}")
                file_path.unlink()
                cleaned_count += 1
        
        print(f"  📊 Cleaned {cleaned_count} temporary files")
        return True
    
    def verify_gitignore(self) -> bool:
        """Verify .gitignore includes database exclusions."""
        print("\n📝 Verifying .gitignore...")
        
        gitignore_path = self.project_root / ".gitignore"
        
        if not gitignore_path.exists():
            print("  ❌ .gitignore not found")
            return False
        
        content = gitignore_path.read_text()
        
        # Check for key exclusions
        required_patterns = [
            "*.db",
            "utils/universal_agent_tracking.db",
            "utils/analytics.db"
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"  ⚠️ Missing .gitignore patterns: {missing_patterns}")
            return False
        
        print("  ✅ .gitignore is properly configured")
        return True
    
    def check_large_files(self) -> bool:
        """Check for large files that shouldn't be committed."""
        print("\n📏 Checking for large files...")
        
        large_files = []
        
        # Check for files larger than 10MB
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    if size_mb > 10:
                        large_files.append((file_path, size_mb))
                except (OSError, PermissionError):
                    pass
        
        if large_files:
            print("  ❌ Large files found:")
            for file_path, size_mb in large_files:
                rel_path = file_path.relative_to(self.project_root)
                print(f"    📁 {rel_path} ({size_mb:.2f} MB)")
            print("  💡 Consider adding these to .gitignore")
            return False
        
        print("  ✅ No large files found")
        return True

def main():
    """Main entry point for git hook."""
    hook = DatabaseCleanupHook()
    
    if not hook.run_cleanup():
        print("\n🚫 COMMIT BLOCKED: Database cleanup failed")
        print("💡 Fix the issues above and try again")
        sys.exit(1)
    
    print("\n🎉 All checks passed - commit allowed")
    sys.exit(0)

if __name__ == "__main__":
    main()
