#!/usr/bin/env python3
"""
Database cleanup utility for tests.

Systematically closes database connections and removes test database files
to prevent Windows PermissionError [WinError 32] issues.
"""

import os
import sys
import sqlite3
import tempfile
import shutil
import gc
from pathlib import Path


def close_all_sqlite_connections():
    """Force close all SQLite connections."""
    # Force garbage collection to close any lingering connections
    gc.collect()
    
    # Clear any cached connections
    if hasattr(sqlite3, '_connections'):
        sqlite3._connections.clear()


def find_and_remove_test_databases():
    """Find and remove test database files."""
    patterns = [
        "*.db",
        "*.sqlite", 
        "*.sqlite3",
        "*test*.db",
        "*temp*.db"
    ]
    
    removed_count = 0
    
    # Check common test directories
    test_dirs = [
        Path("tests"),
        Path(tempfile.gettempdir()),
        Path("cache"),
        Path("analytics"),
        Path("templates")
    ]
    
    for test_dir in test_dirs:
        if test_dir.exists():
            for pattern in patterns:
                for db_file in test_dir.rglob(pattern):
                    try:
                        if db_file.is_file():
                            db_file.unlink()
                            removed_count += 1
                            print(f"Removed: {db_file}")
                    except PermissionError:
                        print(f"Could not remove (locked): {db_file}")
                    except Exception as e:
                        print(f"Error removing {db_file}: {e}")
    
    return removed_count


def cleanup_temp_directories():
    """Clean up temporary test directories."""
    temp_base = Path(tempfile.gettempdir())
    removed_count = 0
    
    # Look for test-related temp directories
    for temp_dir in temp_base.iterdir():
        if temp_dir.is_dir() and any(x in temp_dir.name.lower() for x in ['test', 'tmp', 'prompt', 'analytics']):
            try:
                shutil.rmtree(temp_dir)
                removed_count += 1
                print(f"Removed temp dir: {temp_dir}")
            except Exception as e:
                print(f"Could not remove temp dir {temp_dir}: {e}")
    
    return removed_count


def main():
    """Main cleanup function."""
    print("Starting database cleanup...")
    
    # Step 1: Close all SQLite connections
    print("1. Closing SQLite connections...")
    close_all_sqlite_connections()
    
    # Step 2: Remove test databases
    print("2. Removing test database files...")
    db_count = find_and_remove_test_databases()
    
    # Step 3: Clean temp directories
    print("3. Cleaning temporary directories...")
    temp_count = cleanup_temp_directories()
    
    # Step 4: Force garbage collection
    print("4. Running garbage collection...")
    gc.collect()
    
    print(f"Cleanup complete!")
    print(f"   - Database files removed: {db_count}")
    print(f"   - Temp directories removed: {temp_count}")
    
    return db_count + temp_count


if __name__ == "__main__":
    sys.exit(0 if main() >= 0 else 1)
