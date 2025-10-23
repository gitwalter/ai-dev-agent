"""Fix get_graph() functions in research agents."""

import re
from pathlib import Path

def fix_get_graph(file_path: Path) -> bool:
    """Fix get_graph function in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
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
        
        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
        
    except Exception as e:
        print(f"Error: {file_path.name}: {e}")
        return False

def main():
    research_dir = Path('agents/research')
    files = [
        'comprehensive_research_agent.py',
        'web_search_agent.py',
        'verification_agent.py',
        'synthesis_agent.py',
        'query_planner_agent.py',
        'content_parser_agent.py'
    ]
    
    for filename in files:
        file_path = research_dir / filename
        if file_path.exists():
            fix_get_graph(file_path)

if __name__ == '__main__':
    main()

