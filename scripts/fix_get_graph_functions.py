"""
Fix get_graph() functions that incorrectly pass gemini_client parameter.
"""

import re
from pathlib import Path

def fix_get_graph(file_path: Path) -> bool:
    """Fix get_graph function in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to find get_graph functions with gemini_client parameter
        pattern = r'(def get_graph\(\):.*?)(from utils\.llm\.gemini_client_factory import get_gemini_client\s+)(.*?client = get_gemini_client\(.*?\)\s+)(.*?gemini_client=client)'
        
        def replacement(match):
            """Replace get_gemini_client and gemini_client=client"""
            before = match.group(1)  # Everything before get_gemini_client import
            after_config = match.group(3)  # Everything between get_gemini_client and the instantiation
            instantiation_line = match.group(4)  # The line with gemini_client=client
            
            # Remove the get_gemini_client import line and client assignment
            # Keep everything else but remove gemini_client parameter
            return before + after_config.replace('client = get_gemini_client', '# Removed client =').replace(')\n        _default_instance', ')\n        _default_instance') + instantiation_line.replace(', gemini_client=client', '')
        
        # Check if file has the pattern
        if 'gemini_client=client' in content and 'def get_graph():' in content:
            # Do manual replacement
            lines = content.split('\n')
            new_lines = []
            skip_next = False
            
            for i, line in enumerate(lines):
                if skip_next:
                    skip_next = False
                    continue
                    
                # Remove get_gemini_client import
                if 'from utils.llm.gemini_client_factory import get_gemini_client' in line:
                    continue
                    
                # Remove client = get_gemini_client line
                if 'client = get_gemini_client' in line:
                    continue
                    
                # Remove gemini_client parameter
                if 'gemini_client=client' in line:
                    line = line.replace(', gemini_client=client', '')
                    
                new_lines.append(line)
            
            new_content = '\n'.join(new_lines)
            
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all RAG agent files."""
    rag_dir = Path('agents/rag')
    fixed_count = 0
    
    files_to_fix = [
        'writer_agent.py',
        'web_scraping_specialist_agent.py',
        'retrieval_specialist_agent.py',
        're_ranker_agent.py',
        'quality_assurance_agent.py'
    ]
    
    for filename in files_to_fix:
        file_path = rag_dir / filename
        if file_path.exists():
            if fix_get_graph(file_path):
                print(f"Fixed: {file_path}")
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()

