#!/usr/bin/env python3
"""
Fix Database TearDown Methods

This script systematically fixes database connection cleanup issues in test files
to prevent SQLite PermissionError on Windows.
"""

import re
from pathlib import Path


def fix_teardown_methods():
    """Fix tearDown methods in test files to properly close database connections."""
    
    # Test files that need fixing
    test_files = [
        "tests/integration/prompts/test_prompt_management_system.py",
        "tests/unit/prompts/test_prompt_management_infrastructure.py"
    ]
    
    # Enhanced tearDown template
    enhanced_teardown_template = '''    def tearDown(self):
        """Clean up test environment."""
        # Close database connections first
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, 'close') and callable(attr.close):
                try:
                    attr.close()
                except Exception:
                    pass  # Best effort cleanup
        
        # Enhanced cleanup for Windows database locking issues
        if hasattr(self, 'temp_dir'):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                import time
                time.sleep(0.1)
                try:
                    shutil.rmtree(self.temp_dir)
                except PermissionError:
                    pass  # Best effort cleanup'''
    
    for test_file in test_files:
        file_path = Path(test_file)
        if not file_path.exists():
            print(f"Skipping non-existent file: {test_file}")
            continue
            
        print(f"Fixing tearDown methods in: {test_file}")
        
        # Read the file content
        content = file_path.read_text(encoding='utf-8')
        
        # Pattern to match simple tearDown methods
        pattern = r'    def tearDown\(self\):\s*\n        """Clean up test environment\."""\s*\n        shutil\.rmtree\(self\.temp_dir\)'
        
        # Replace with enhanced tearDown
        updated_content = re.sub(pattern, enhanced_teardown_template, content)
        
        # Write back if changed
        if updated_content != content:
            file_path.write_text(updated_content, encoding='utf-8')
            print(f"✅ Updated tearDown methods in {test_file}")
        else:
            print(f"⚠️ No simple tearDown patterns found in {test_file}")


if __name__ == "__main__":
    fix_teardown_methods()
