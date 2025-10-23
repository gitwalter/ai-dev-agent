"""Move orphaned _build_langgraph_workflow methods inside the class."""

import re
from pathlib import Path

def fix_agent(file_path: Path) -> bool:
    """Move workflow methods inside the class."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the orphaned workflow block
        orphaned_pattern = r'\n\n\n    \n    def _build_langgraph_workflow\(self\).*?return state\n'
        
        orphaned_match = re.search(orphaned_pattern, content, re.DOTALL)
        if not orphaned_match:
            print(f"  {file_path.name}: No orphaned workflow methods found")
            return False
        
        orphaned_code = orphaned_match.group(0)
        
        # Remove the leading blank lines and one level of indentation
        cleaned_code = orphaned_code.lstrip('\n').replace('    def ', '    def ', 1)
        
        # Find where to insert (before "if __name__ == "__main__":")
        insert_pattern = r'\n\n\nif __name__ == "__main__":'
        
        if re.search(insert_pattern, content):
            # Insert the workflow methods before __main__
            content = re.sub(insert_pattern, '\n' + cleaned_code + '\n\nif __name__ == "__main__":', content, count=1)
            
            # Remove the orphaned version
            content = re.sub(orphaned_pattern, '\n', content, count=1)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  {file_path.name}: Fixed")
            return True
        else:
            print(f"  {file_path.name}: Could not find insertion point")
            return False
            
    except Exception as e:
        print(f"  {file_path.name}: Error - {e}")
        return False

def main():
    research_dir = Path('agents/research')
    
    agents_to_fix = [
        'synthesis_agent.py',
        'verification_agent.py',
        'web_search_agent.py'
    ]
    
    for agent_file in agents_to_fix:
        file_path = research_dir / agent_file
        if file_path.exists():
            fix_agent(file_path)

if __name__ == '__main__':
    main()

