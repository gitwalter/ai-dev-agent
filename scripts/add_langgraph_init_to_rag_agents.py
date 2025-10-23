"""
Add LangGraph initialization to RAG agent __init__ methods.
"""

import re
from pathlib import Path

def add_langgraph_init_to_agent(file_path: Path) -> bool:
    """Add LangGraph initialization to agent __init__ method."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already has LangGraph init
        if '# Build LangGraph workflow if available' in content:
            print(f"  {file_path.name}: Already has LangGraph init")
            return False
        
        # Pattern: find logger.info at the end of __init__
        pattern = r'(        logger\.info\(f"✅ \{self\.name\} initialized"\))'
        
        if re.search(pattern, content):
            langgraph_init = '''        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_langgraph_workflow()
            self.app = self.workflow.compile()
            logger.info("✅ LangGraph workflow compiled and ready")
        else:
            self.workflow = None
            self.app = None
            logger.info("⚠️ LangGraph not available - using legacy mode")
        
        logger.info(f"✅ {self.name} initialized")'''
            
            content = re.sub(pattern, langgraph_init, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  {file_path.name}: Added LangGraph init")
            return True
        else:
            print(f"  {file_path.name}: Could not find pattern")
            return False
        
    except Exception as e:
        print(f"  {file_path.name}: Error - {e}")
        return False

def main():
    """Fix remaining RAG agent files."""
    rag_dir = Path('agents/rag')
    fixed_count = 0
    
    files_to_fix = [
        'writer_agent.py',
        'web_scraping_specialist_agent.py',
        'quality_assurance_agent.py'
    ]
    
    print("Adding LangGraph init to RAG agents...")
    for filename in files_to_fix:
        file_path = rag_dir / filename
        if file_path.exists():
            if add_langgraph_init_to_agent(file_path):
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} agents")

if __name__ == '__main__':
    main()

