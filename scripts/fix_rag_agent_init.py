"""
Fix RAG agents where LangGraph workflow initialization is missing from __init__ method.
"""

import re
from pathlib import Path

def add_langgraph_init(file_path: Path) -> bool:
    """Add LangGraph initialization to __init__ method."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if LangGraph init code is already in __init__
        if 'self.workflow = self._build_langgraph_workflow()' in content:
            print(f"  Skipping {file_path.name} - already has LangGraph init in __init__")
            return False
        
        # Find logger.info at the end of __init__ (just before the method closes)
        pattern = r'(        logger\.info\(f"✅ \{self\.name\} initialized"\))'
        
        if re.search(pattern, content):
            # Add LangGraph workflow initialization before the final logger.info
            replacement = '''        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_langgraph_workflow()
            self.app = self.workflow.compile()
            logger.info("✅ LangGraph workflow compiled and ready")
        else:
            self.workflow = None
            self.app = None
            logger.info("⚠️ LangGraph not available - using legacy mode")
        
        logger.info(f"✅ {self.name} initialized")'''
            
            content = re.sub(pattern, replacement, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  Fixed {file_path.name}")
            return True
        else:
            print(f"  Could not find pattern in {file_path.name}")
            return False
        
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False

def main():
    """Fix all RAG agent files."""
    rag_dir = Path('agents/rag')
    fixed_count = 0
    
    files_to_fix = [
        'retrieval_specialist_agent.py',
        're_ranker_agent.py',
        'writer_agent.py',
        'web_scraping_specialist_agent.py',
        'quality_assurance_agent.py'
    ]
    
    print("Fixing RAG agents __init__ methods...")
    for filename in files_to_fix:
        file_path = rag_dir / filename
        if file_path.exists():
            if add_langgraph_init(file_path):
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} agents")

if __name__ == '__main__':
    main()

