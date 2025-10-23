"""Fix get_graph() calls in research agents to match __init__ signatures."""

from pathlib import Path
import re

def fix_get_graph_call(file_path: Path) -> bool:
    """Fix get_graph to call __init__ correctly."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check __init__ signature
        init_match = re.search(r'def __init__\(self(?:, ([^)]+))?\)', content)
        if not init_match:
            return False
        
        params = init_match.group(1) if init_match.group(1) else ""
        
        # Get class name
        class_match = re.search(r'class (\w+)\(', content)
        if not class_match:
            return False
        class_name = class_match.group(1)
        
        # Find and fix get_graph
        if "__init__() takes 1 positional" in params or not params:
            # No params needed
            pattern = rf'_default_instance = {class_name}\(config\)'
            replacement = f'_default_instance = {class_name}()'
            if pattern in content:
                content = content.replace(pattern, replacement)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        
        return False
        
    except Exception as e:
        print(f"Error {file_path.name}: {e}")
        return False

def main():
    research_dir = Path('agents/research')
    
    for py_file in research_dir.glob('*.py'):
        if py_file.name == '__init__.py':
            continue
        fix_get_graph_call(py_file)

if __name__ == '__main__':
    main()

