#!/usr/bin/env python3
"""
Helper script to add LangGraph support to a single agent.
This creates the standard pattern we established with requirements_analyst.
"""

import sys
import re
from pathlib import Path

def add_langgraph_to_agent(agent_file: Path, agent_name: str, agent_id: str):
    """Add LangGraph support to an agent file."""
    
    print(f"\n{'='*60}")
    print(f"Adding LangGraph to: {agent_file.name}")
    print(f"Agent Name: {agent_name}")
    print(f"Agent ID: {agent_id}")
    print(f"{'='*60}")
    
    # Read the file
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has LangGraph
    if 'LANGGRAPH_AVAILABLE' in content:
        print("  [SKIP] Already has LangGraph support")
        return False
    
    # 1. Ensure List is in typing imports
    if 'from typing import' in content and 'List' not in content.split('from typing import')[1].split('\n')[0]:
        content = content.replace('from typing import', 'from typing import List, ', 1)
        print("  [OK] Added List to typing imports")
    
    # 2. Add LangGraph imports after other imports
    import_additions = """
# LangGraph integration check
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from pydantic import BaseModel, Field
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available - agent will work in legacy mode only")
"""
    
    # Find the last import statement
    import_pattern = r'((?:^import |^from ).*\n)(?!(?:import |from ))'
    match = re.search(import_pattern, content, re.MULTILINE)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + "\n" + import_additions + content[insert_pos:]
        print("  [OK] Added LangGraph imports")
    else:
        print("  [ERROR] Could not find import section")
        return False
    
    # 2. Add State class before agent class definition
    state_class = f"""

class {agent_name}State(BaseModel):
    \"\"\"State for {agent_name} LangGraph workflow using Pydantic BaseModel.\"\"\"
    
    # Input fields
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data")
    
    # Output fields
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output data")
    
    # Control fields
    errors: List[str] = Field(default_factory=list, description="Error messages")
    status: str = Field(default="initialized", description="Current status")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Execution metrics")
    
    class Config:
        \"\"\"Pydantic configuration.\"\"\"
        arbitrary_types_allowed = True

"""
    
    # Find class definition
    class_pattern = f'class {agent_name}'
    class_pos = content.find(class_pattern)
    if class_pos != -1:
        content = content[:class_pos] + state_class + content[class_pos:]
        print("  [OK] Added State class")
    else:
        print(f"  [ERROR] Could not find class {agent_name}")
        return False
    
    # 3. Add workflow initialization to __init__
    init_addition = """
        
        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_langgraph_workflow()
            self.app = self.workflow.compile()
            self.logger.info("✅ LangGraph workflow compiled and ready")
        else:
            self.workflow = None
            self.app = None
            self.logger.info("⚠️ LangGraph not available - using legacy mode")
"""
    
    # Find end of __init__ (look for next method definition)
    init_pattern = r'def __init__\(self[^)]*\):.*?(?=\n    def |\nclass |\Z)'
    match = re.search(init_pattern, content, re.DOTALL)
    if match:
        init_end = match.end()
        # Insert before next method
        content = content[:init_end] + init_addition + content[init_end:]
        print("  [OK] Added workflow initialization to __init__")
    else:
        print("  [WARNING] Could not find __init__ method, skipping workflow init")
    
    # 4. Add workflow methods before end of class
    workflow_methods = f"""
    
    def _build_langgraph_workflow(self) -> StateGraph:
        \"\"\"Build LangGraph workflow for {agent_name}.\"\"\"
        workflow = StateGraph({agent_name}State)
        
        # Simple workflow: just execute the agent
        workflow.add_node("execute", self._langgraph_execute_node)
        workflow.set_entry_point("execute")
        workflow.add_edge("execute", END)
        
        return workflow
    
    async def _langgraph_execute_node(self, state: {agent_name}State) -> {agent_name}State:
        \"\"\"Execute agent in LangGraph workflow.\"\"\"
        import time
        start = time.time()
        
        try:
            # Call the agent's execute method
            result = await self.execute(state.input_data)
            
            # Update state with results
            state.output_data = result
            state.status = "completed"
            state.metrics["execution_time"] = time.time() - start
            
        except Exception as e:
            self.logger.error(f"LangGraph execution failed: {{e}}")
            state.errors.append(str(e))
            state.status = "failed"
            state.metrics["execution_time"] = time.time() - start
        
        return state
"""
    
    # Find end of class (look for next class or end of file)
    # Insert methods before the last few lines of the class
    # Find the last method in the class
    last_method_pattern = r'(    def \w+.*?\n(?:        .*\n)*?)(?=\nclass |\n\n# |\Z)'
    matches = list(re.finditer(last_method_pattern, content, re.DOTALL))
    if matches:
        last_match = matches[-1]
        insert_pos = last_match.end()
        content = content[:insert_pos] + workflow_methods + content[insert_pos:]
        print("  [OK] Added workflow methods")
    else:
        print("  [WARNING] Could not find good insertion point for workflow methods")
    
    # 5. Add graph export at end
    graph_export = f"""

# Export for LangGraph Studio
_default_instance = None

def get_graph():
    \"\"\"Get the compiled graph for LangGraph Studio.\"\"\"
    global _default_instance
    if _default_instance is None and LANGGRAPH_AVAILABLE:
        from models.config import AgentConfig
        from utils.llm.gemini_client_factory import get_gemini_client
        
        config = AgentConfig(
            agent_id='{agent_id}',
            name='{agent_name}',
            description='{agent_name} agent',
            model_name='gemini-2.5-flash'
        )
        client = get_gemini_client(agent_name='{agent_id}')
        _default_instance = {agent_name}(config, gemini_client=client)
    return _default_instance.app if _default_instance else None

# Studio expects 'graph' variable
graph = get_graph()
"""
    
    # Add at the very end
    content = content.rstrip() + "\n" + graph_export
    print("  [OK] Added graph export")
    
    # Write back
    with open(agent_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  [SUCCESS] {agent_file.name} updated with LangGraph support")
    return True


def update_studio_graph(graph_file: Path, agent_module: str, agent_name: str):
    """Update Studio graph file to use base agent."""
    
    print(f"\nUpdating Studio graph: {graph_file.name}")
    
    new_content = f'''"""
{agent_name} Graph for LangGraph Studio.

Uses the base agent directly (no coordinator needed) - KISS & DRY principles.
"""

from agents.{agent_module} import graph

# Export the compiled graph for LangGraph Studio
# (graph is already defined in the base agent module)
'''
    
    with open(graph_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  [SUCCESS] {graph_file.name} updated")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python add_langgraph_to_agent.py <agent_file> <agent_name> <agent_id>")
        print("Example: python add_langgraph_to_agent.py agents/development/architecture_designer.py ArchitectureDesigner architecture_designer")
        sys.exit(1)
    
    agent_file = Path(sys.argv[1])
    agent_name = sys.argv[2]
    agent_id = sys.argv[3]
    
    if not agent_file.exists():
        print(f"Error: File not found: {agent_file}")
        sys.exit(1)
    
    success = add_langgraph_to_agent(agent_file, agent_name, agent_id)
    
    if success:
        # Also update the studio graph file
        graph_file = Path(f"agents/langgraph_studio/{agent_id}_graph.py")
        if graph_file.exists():
            module_path = str(agent_file.parent).replace('\\', '.').replace('/', '.').replace('agents.', '')
            update_studio_graph(graph_file, f"{module_path}.{agent_id}", agent_name)
        
        print(f"\n[SUCCESS] {agent_name} is now LangGraph-native")
        print(f"\nNext steps:")
        print(f"1. Test: python -c \"from {agent_file.stem} import {agent_name}\"")
        print(f"2. Test: python -c \"from agents.langgraph_studio.{agent_id}_graph import graph\"")
        print(f"3. If tests pass, delete: agents/development/{agent_id}_langgraph.py")
    else:
        print(f"\n[FAILED] Could not add LangGraph to {agent_name}")
        sys.exit(1)

