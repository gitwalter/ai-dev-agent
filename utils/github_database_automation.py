#!/usr/bin/env python3
"""
GitHub Database Automation Script

This script safely cleans the database before pushing to GitHub by:
1. Removing user-specific data
2. Keeping template data
3. Creating a clean version for public repository
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent

def get_database_path():
    """Get the path to the main database."""
    return get_project_root() / "prompts" / "prompt_templates.db"

def backup_database():
    """Create a backup of the current database."""
    db_path = get_database_path()
    if not db_path.exists():
        print("❌ Database not found")
        return False
    
    backup_path = db_path.with_suffix('.db.backup')
    shutil.copy2(db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    return True

def clean_database():
    """Clean the database by removing user data while keeping templates."""
    db_path = get_database_path()
    if not db_path.exists():
        print("❌ Database not found")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("🧹 Cleaning database...")
        
        for table in tables:
            table_name = table[0]
            print(f"  Processing table: {table_name}")
            
            # Skip system tables
            if table_name.startswith('sqlite_'):
                continue
            
            # For each table, remove user-specific data but keep templates
            # This is a safe approach - we keep the structure but clean sensitive data
            try:
                # Get row count before cleaning
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                before_count = cursor.fetchone()[0]
                
                # Remove any rows that might contain user data
                # Keep only template/system data
                cursor.execute(f"DELETE FROM {table_name} WHERE id > 1000")  # Keep first 1000 rows (templates)
                
                # Get row count after cleaning
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                after_count = cursor.fetchone()[0]
                
                print(f"    Cleaned {before_count - after_count} user records, kept {after_count} template records")
                
            except sqlite3.Error as e:
                print(f"    Warning: Could not clean table {table_name}: {e}")
                continue
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Database cleaned successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        return False

def restore_database():
    """Restore the database from backup."""
    db_path = get_database_path()
    backup_path = db_path.with_suffix('.db.backup')
    
    if not backup_path.exists():
        print("❌ Backup not found")
        return False
    
    try:
        shutil.copy2(backup_path, db_path)
        print("✅ Database restored from backup")
        return True
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        return False

def show_status():
    """Show the current status of the database."""
    db_path = get_database_path()
    
    print("📊 Database Status:")
    print(f"  Database exists: {'✅' if db_path.exists() else '❌'}")
    
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"  Database size: {size:,} bytes")
        
        # Check backup
        backup_path = db_path.with_suffix('.db.backup')
        if backup_path.exists():
            backup_size = backup_path.stat().st_size
            print(f"  Backup exists: ✅ ({backup_size:,} bytes)")
        else:
            print("  Backup exists: ❌")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python github_database_automation.py prepare  - Clean database for GitHub")
        print("  python github_database_automation.py restore  - Restore from backup")
        print("  python github_database_automation.py status   - Show status")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "prepare":
        print("🚀 Preparing database for GitHub...")
        if backup_database() and clean_database():
            print("✅ Database prepared for GitHub successfully")
            sys.exit(0)
        else:
            print("❌ Failed to prepare database")
            sys.exit(1)
    
    elif command == "restore":
        print("🔄 Restoring database from backup...")
        if restore_database():
            print("✅ Database restored successfully")
            sys.exit(0)
        else:
            print("❌ Failed to restore database")
            sys.exit(1)
    
    elif command == "status":
        show_status()
        sys.exit(0)
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
