#!/usr/bin/env python3
"""
Script to make all agents LangGraph-native by adding workflow capabilities directly to base agents.

This implements the KISS and DRY principles by:
1. Adding LangGraph support directly to base agents
2. Eliminating unnecessary coordinator wrapper files
3. Making agents work both standalone and in Studio
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Base template for LangGraph additions
LANGGRAPH_IMPORTS = """
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

STATE_CLASS_TEMPLATE = """
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

WORKFLOW_INIT_CODE = """
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

WORKFLOW_METHOD_TEMPLATE = """
    def _build_langgraph_workflow(self) -> StateGraph:
        \"\"\"Build LangGraph workflow for {agent_name}.\"\"\"
        
        workflow = StateGraph({agent_name}State)
        
        # Add nodes
        workflow.add_node("execute", self._langgraph_execute_node)
        
        # Define workflow
        workflow.set_entry_point("execute")
        workflow.add_edge("execute", END)
        
        return workflow
    
    async def _langgraph_execute_node(self, state: {agent_name}State) -> {agent_name}State:
        \"\"\"Execute node for LangGraph workflow.\"\"\"
        import time
        start = time.time()
        
        try:
            # Call the agent's execute method with input_data
            result = await self.execute(state.input_data)
            
            # Update state with results
            state.output_data = result
            state.status = "completed"
            state.metrics["execution_time"] = time.time() - start
            
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            state.errors.append(str(e))
            state.status = "failed"
            state.metrics["execution_time"] = time.time() - start
        
        return state
"""

GRAPH_EXPORT_TEMPLATE = """

# Export for LangGraph Studio
_default_instance = None

def get_graph():
    \"\"\"Get the compiled graph for LangGraph Studio.\"\"\"
    global _default_instance
    if _default_instance is None:
        from models.config import AgentConfig
        from utils.llm.gemini_client_factory import get_gemini_client
        
        config = AgentConfig(
            agent_id='{agent_id}',
            name='{agent_name}',
            description='{agent_name} agent'
        )
        client = get_gemini_client(agent_name='{agent_id}')
        _default_instance = {class_name}(config, gemini_client=client)
    return _default_instance.app

# Studio expects 'graph' variable
graph = get_graph()
"""


def find_class_name(content: str) -> str:
    """Find the main agent class name in the file."""
    # Look for class definition that inherits from base agent classes
    pattern = r'class\s+(\w+)\s*\([^)]*(?:Base|Enhanced|Agent)[^)]*\):'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    
    # Fallback: find any class definition
    pattern = r'class\s+(\w+)\s*\([^)]*\):'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    
    return None


def has_langgraph_support(content: str) -> bool:
    """Check if file already has LangGraph support."""
    return 'LANGGRAPH_AVAILABLE' in content or 'StateGraph' in content


def add_langgraph_to_agent(file_path: Path) -> Tuple[bool, str]:
    """
    Add LangGraph support to an agent file.
    
    Returns:
        (success, message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already has LangGraph
        if has_langgraph_support(content):
            return (False, "Already has LangGraph support")
        
        # Find class name
        class_name = find_class_name(content)
        if not class_name:
            return (False, "Could not find agent class")
        
        agent_id = file_path.stem  # filename without extension
        agent_name = class_name
        
        # 1. Add imports after existing imports
        import_section_end = content.rfind('\nimport ') 
        if import_section_end == -1:
            import_section_end = content.find('\n\n')
        
        if import_section_end != -1:
            # Find the end of that import line
            next_newline = content.find('\n', import_section_end + 1)
            if next_newline != -1:
                content = content[:next_newline + 1] + LANGGRAPH_IMPORTS + content[next_newline + 1:]
        
        # 2. Add State class before agent class
        class_pattern = f'class {class_name}'
        class_pos = content.find(class_pattern)
        if class_pos != -1:
            state_class = STATE_CLASS_TEMPLATE.format(agent_name=agent_name)
            content = content[:class_pos] + state_class + '\n\n' + content[class_pos:]
        
        # 3. Add workflow build to __init__ method
        init_pattern = r'def __init__\(self[^)]*\):'
        match = re.search(init_pattern, content)
        if match:
            # Find the end of __init__ method (next method definition or class end)
            init_start = match.end()
            next_def = content.find('\n    def ', init_start)
            if next_def != -1:
                # Add before next method
                content = content[:next_def] + '\n' + WORKFLOW_INIT_CODE + content[next_def:]
        
        # 4. Add workflow method at end of class
        workflow_method = WORKFLOW_METHOD_TEMPLATE.format(
            agent_name=agent_name,
            class_name=class_name
        )
        
        # Find end of class (look for next class or end of file)
        class_start = content.find(f'class {class_name}')
        if class_start != -1:
            # Find next class or end of file
            next_class = content.find('\nclass ', class_start + 1)
            if next_class == -1:
                next_class = len(content)
            
            # Insert before next class or at end
            content = content[:next_class] + workflow_method + '\n' + content[next_class:]
        
        # 5. Add graph export at end of file
        graph_export = GRAPH_EXPORT_TEMPLATE.format(
            agent_id=agent_id,
            agent_name=agent_name,
            class_name=class_name
        )
        content = content + graph_export
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return (True, "Successfully added LangGraph support")
        
    except Exception as e:
        return (False, f"Error: {str(e)}")


def process_agents_in_folder(folder_path: Path, exclude_files: List[str] = None) -> None:
    """Process all agent files in a folder."""
    if exclude_files is None:
        exclude_files = []
    
    print(f"\n{'='*60}")
    print(f"Processing: {folder_path.name.upper()}")
    print(f"{'='*60}")
    
    agent_files = [
        f for f in folder_path.glob('*.py')
        if not f.name.startswith('__')
        and not f.name.endswith('_langgraph.py')
        and f.name not in exclude_files
    ]
    
    for agent_file in sorted(agent_files):
        print(f"\n{agent_file.name}...")
        success, message = add_langgraph_to_agent(agent_file)
        
        if success:
            print(f"  [OK] {message}")
        else:
            print(f"  [SKIP] {message}")


def main():
    """Main execution."""
    base_path = Path('agents')
    
    print("="*60)
    print("MAKING ALL AGENTS LANGGRAPH-NATIVE")
    print("="*60)
    print("\nApplying KISS and DRY principles:")
    print("- Adding LangGraph directly to base agents")
    print("- Eliminating unnecessary coordinator layers")
    print("- Making agents work both standalone and in Studio")
    
    # Core infrastructure files to skip
    core_excludes = [
        'agent_factory.py',
        'agent_manager.py', 
        'base_agent.py',
        'enhanced_base_agent.py',
        'context_aware_agent.py',
        'masters_rule_integration.py',
        'foundation_practical_compliant_agent.py'
    ]
    
    # Process each folder
    folders_to_process = [
        ('development', []),
        ('rag', []),
        ('research', ['web_research_swarm.py']),  # This is already a swarm
        ('management', []),
        ('mcp', []),
        ('security', ['core_ethical_dna_implementation_team.py', 'quantum_resistant_ethical_dna_core.py']),
        ('supervisor', []),
        ('experts', []),
        ('swarm', []),
        # Teams might already have workflow logic - check case by case
    ]
    
    for folder_name, excludes in folders_to_process:
        folder_path = base_path / folder_name
        if folder_path.exists():
            process_agents_in_folder(folder_path, excludes)
    
    print("\n" + "="*60)
    print("PHASE 1 COMPLETE: All base agents updated")
    print("="*60)
    print("\nNext steps:")
    print("1. Test agents work correctly")
    print("2. Update *_graph.py files to use base agents directly")
    print("3. Delete *_langgraph.py coordinator files")


if __name__ == '__main__':
    main()

