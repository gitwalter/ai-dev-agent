#!/usr/bin/env python3
"""
Clean up generated_projects folder before tests
Wu wei approach - simple, effective, no fuss
"""

import shutil
from pathlib import Path


def cleanup_generated_projects():
    """Clean up the generated_projects folder."""
    generated_dir = Path("generated_projects")
    
    if generated_dir.exists():
        try:
            shutil.rmtree(generated_dir)
            print(f"✅ Cleaned up {generated_dir}")
        except Exception as e:
            print(f"⚠️ Could not fully clean {generated_dir}: {e}")
    
    # Recreate empty directory
    generated_dir.mkdir(exist_ok=True)
    print(f"📁 Created clean {generated_dir}")


if __name__ == "__main__":
    cleanup_generated_projects()
