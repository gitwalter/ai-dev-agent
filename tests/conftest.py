"""
Pytest configuration for automatic cleanup
Wu wei approach - runs cleanup automatically before tests
"""

import pytest
import shutil
import sys
import gc
import sqlite3
import tempfile
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def pytest_sessionstart(session):
    """Clean up before test session starts."""
    cleanup_databases()
    cleanup_generated_projects()


def pytest_sessionfinish(session, exitstatus):
    """Clean up after test session ends."""
    cleanup_databases()


def cleanup_databases():
    """Clean up database files and connections to prevent Windows locking issues."""
    print("Cleaning up database connections and files...")
    
    # Force close all SQLite connections
    gc.collect()
    if hasattr(sqlite3, '_connections'):
        sqlite3._connections.clear()
    
    # Remove test database files
    patterns = ["*.db", "*.sqlite", "*.sqlite3", "*test*.db", "*temp*.db"]
    test_dirs = [
        Path("tests"),
        Path(tempfile.gettempdir()),
        Path("cache"),
        Path("analytics"),
        Path("templates"),
        Path("prompts")
    ]
    
    removed_count = 0
    for test_dir in test_dirs:
        if test_dir.exists():
            for pattern in patterns:
                for db_file in test_dir.rglob(pattern):
                    try:
                        if db_file.is_file():
                            db_file.unlink()
                            removed_count += 1
                    except PermissionError:
                        pass  # Skip locked files
                    except Exception:
                        pass  # Skip other errors
    
    if removed_count > 0:
        print(f"   Cleaned up {removed_count} database files")


def cleanup_generated_projects():
    """Clean up the generated_projects folder."""
    generated_dir = Path("generated_projects")
    
    if generated_dir.exists():
        try:
            shutil.rmtree(generated_dir)
            print(f"Cleaned up {generated_dir} before tests")
        except Exception as e:
            print(f"Could not fully clean {generated_dir}: {e}")
    
    # Recreate empty directory
    generated_dir.mkdir(exist_ok=True)