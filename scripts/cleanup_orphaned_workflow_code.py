"""
Remove orphaned LangGraph workflow code from RAG agents.
The automated tool added workflow code outside __init__ methods.
"""

import re
from pathlib import Path

def remove_orphaned_workflow(file_path: Path) -> bool:
    """Remove orphaned workflow code that's not in __init__."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to find the orphaned workflow block
        # It's usually after a return statement and before the next method def
        pattern = r'\n\s{8}\n\s{8}# Build LangGraph workflow if available\n\s{8}if LANGGRAPH_AVAILABLE:.*?\n\s{12}self\.logger\.info\("⚠️ LangGraph not available - using legacy mode"\)\n'
        
        if re.search(pattern, content, re.DOTALL):
            print(f"  Removing orphaned workflow code from {file_path.name}")
            content = re.sub(pattern, '\n', content, flags=re.DOTALL)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        else:
            print(f"  No orphaned workflow code found in {file_path.name}")
            return False
        
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False

def main():
    """Clean up all RAG agent files."""
    rag_dir = Path('agents/rag')
    fixed_count = 0
    
    files_to_check = [
        're_ranker_agent.py',
        'writer_agent.py',
        'web_scraping_specialist_agent.py',
        'quality_assurance_agent.py'
    ]
    
    print("Removing orphaned LangGraph workflow code...")
    for filename in files_to_check:
        file_path = rag_dir / filename
        if file_path.exists():
            if remove_orphaned_workflow(file_path):
                fixed_count += 1
    
    print(f"\nCleaned {fixed_count} files")

if __name__ == '__main__':
    main()

