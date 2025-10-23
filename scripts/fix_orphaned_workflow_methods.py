"""Fix orphaned workflow methods in agent files."""

import re
from pathlib import Path

def fix_agent_workflow_methods(file_path: Path) -> bool:
    """Fix orphaned workflow methods by moving them inside the class."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the orphaned workflow methods (after if __name__)
        orphaned_pattern = r'(if __name__ == "__main__":.*?)\n\n    \n    (def _build_langgraph_workflow\(self\).*?return state\n)'
        
        match = re.search(orphaned_pattern, content, re.DOTALL)
        if not match:
            print(f"  {file_path.name}: No orphaned methods found")
            return False
        
        orphaned_methods = match.group(2)
        
        # Find where to insert (before the main() or test function)
        # Look for the last method of the class (before main())
        class_end_pattern = r'(class \w+.*?)(    return [^\n]+\n\n)(def main\(\)|async def test_|if __name__)'
        
        class_match = re.search(class_end_pattern, content, re.DOTALL)
        if not class_match:
            # Try alternative pattern
            class_end_pattern2 = r'(""".*?""")\n        return \w+\n\n(def main\(\)|if __name__)'
            class_match = re.search(class_end_pattern2, content, re.DOTALL)
        
        if not class_match:
            print(f"  {file_path.name}: Could not find class end")
            return False
        
        # Insert methods before main()
        content_before_orphaned = content[:match.start(2)]
        content_after_orphaned = content[match.end(2):]
        
        # Remove the orphaned block
        content = content_before_orphaned + '\n' + content_after_orphaned
        
        # Now insert methods at the class end
        insertion_point = class_match.end(1)
        content = content[:insertion_point] + '\n' + orphaned_methods + content[insertion_point:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ {file_path.name}: Fixed orphaned workflow methods")
        return True
        
    except Exception as e:
        print(f"✗ {file_path.name}: Error - {e}")
        return False

# Fix the two remaining agents
agents_to_fix = [
    Path('agents/mcp/mcp_enhanced_agent.py'),
    Path('agents/swarm/swarm_coordinator.py'),
]

print("Fixing orphaned workflow methods...\n")
for agent_path in agents_to_fix:
    fix_agent_workflow_methods(agent_path)

