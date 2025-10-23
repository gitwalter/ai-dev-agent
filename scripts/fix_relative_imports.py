"""
Fix relative imports in all agent files to be absolute imports.
This is required for LangGraph Studio compatibility.
"""

import os
import re
from pathlib import Path

def fix_relative_imports(file_path: Path) -> bool:
    """Fix relative imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix relative imports from ..core
        content = re.sub(
            r'from \.\.core\.(\w+) import',
            r'from agents.core.\1 import',
            content
        )
        
        # Fix relative imports from ..development
        content = re.sub(
            r'from \.\.development\.(\w+) import',
            r'from agents.development.\1 import',
            content
        )
        
        # Fix relative imports from ..rag
        content = re.sub(
            r'from \.\.rag\.(\w+) import',
            r'from agents.rag.\1 import',
            content
        )
        
        # Fix relative imports from ..research
        content = re.sub(
            r'from \.\.research\.(\w+) import',
            r'from agents.research.\1 import',
            content
        )
        
        # Fix relative imports from ..security
        content = re.sub(
            r'from \.\.security\.(\w+) import',
            r'from agents.security.\1 import',
            content
        )
        
        # Fix relative imports from ..management
        content = re.sub(
            r'from \.\.management\.(\w+) import',
            r'from agents.management.\1 import',
            content
        )
        
        # Fix relative imports from ..supervisor
        content = re.sub(
            r'from \.\.supervisor\.(\w+) import',
            r'from agents.supervisor.\1 import',
            content
        )
        
        # Fix relative imports from ..mcp
        content = re.sub(
            r'from \.\.mcp\.(\w+) import',
            r'from agents.mcp.\1 import',
            content
        )
        
        # Fix relative imports from ..swarm
        content = re.sub(
            r'from \.\.swarm\.(\w+) import',
            r'from agents.swarm.\1 import',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all agent files."""
    agents_dir = Path('agents')
    fixed_count = 0
    
    # Process all Python files in agents directory
    for py_file in agents_dir.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        if py_file.name == '__init__.py':
            continue
            
        if fix_relative_imports(py_file):
            print(f"Fixed: {py_file}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files with relative imports")

if __name__ == '__main__':
    main()

