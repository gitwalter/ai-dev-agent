"""
Pytest configuration for automatic cleanup
Wu wei approach - runs cleanup automatically before tests
"""

import pytest
import shutil
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def pytest_sessionstart(session):
    """Clean up generated_projects before test session starts."""
    cleanup_generated_projects()


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