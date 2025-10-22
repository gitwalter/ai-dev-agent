"""
Script to systematically convert all LangGraph agents to use Pydantic BaseModel
and update langgraph.json to expose them in Studio.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict

def find_langgraph_agents() -> List[Path]:
    """Find all *_langgraph.py files."""
    agents_dir = Path("agents")
    langgraph_files = []
    
    for file in agents_dir.rglob("*_langgraph.py"):
        langgraph_files.append(file)
    
    return sorted(langgraph_files)

def check_uses_typeddict(file_path: Path) -> bool:
    """Check if file uses TypedDict for state."""
    content = file_path.read_text(encoding='utf-8')
    return 'TypedDict' in content and 'class' in content and 'State' in content

def check_uses_pydantic(file_path: Path) -> bool:
    """Check if file uses Pydantic BaseModel."""
    content = file_path.read_text(encoding='utf-8')
    return 'BaseModel' in content and 'from pydantic import' in content

def get_agent_name_from_file(file_path: Path) -> str:
    """Extract agent name from file path."""
    name = file_path.stem.replace('_langgraph', '')
    return name

def get_graph_export_file(agent_name: str) -> Path:
    """Get the graph export file path."""
    return Path(f"agents/langgraph_studio/{agent_name}_graph.py")

def check_graph_export_exists(agent_name: str) -> bool:
    """Check if graph export file exists."""
    return get_graph_export_file(agent_name).exists()

def analyze_agents():
    """Analyze all LangGraph agents and their status."""
    agents = find_langgraph_agents()
    
    print(f"\nFound {len(agents)} LangGraph agent files:\n")
    print(f"{'Agent':<40} {'Uses Pydantic':<15} {'Has Graph Export':<20}")
    print("=" * 75)
    
    results = []
    for agent_file in agents:
        agent_name = get_agent_name_from_file(agent_file)
        uses_pydantic = check_uses_pydantic(agent_file)
        has_export = check_graph_export_exists(agent_name)
        
        status_pydantic = "[OK]" if uses_pydantic else "[X] TypedDict"
        status_export = "[OK]" if has_export else "[X] Missing"
        
        print(f"{str(agent_file):<40} {status_pydantic:<15} {status_export:<20}")
        
        results.append({
            'file': agent_file,
            'name': agent_name,
            'uses_pydantic': uses_pydantic,
            'has_export': has_export
        })
    
    return results

def generate_langgraph_json_config(agent_results: List[Dict]) -> Dict:
    """Generate comprehensive langgraph.json configuration."""
    
    # Only include agents that have graph exports
    graphs = {}
    for agent in agent_results:
        if agent['has_export']:
            agent_name = agent['name']
            graph_path = f"agents/langgraph_studio/{agent_name}_graph.py:graph"
            graphs[agent_name] = graph_path
    
    config = {
        "dependencies": ["requirements.txt"],
        "graphs": graphs,
        "env": {
            "GOOGLE_API_KEY": "${GOOGLE_API_KEY}",
            "LANGCHAIN_API_KEY": "${LANGCHAIN_API_KEY}",
            "LANGCHAIN_TRACING_V2": "true",
            "LANGCHAIN_PROJECT": "ai-dev-agent",
            "PYTHONPATH": ".",
            "DATABASE_URI": "sqlite://:memory:",
            "REDIS_URI": "redis://localhost:6379"
        },
        "python_version": "3.11",
        "dockerfile_lines": []
    }
    
    return config

def main():
    print("LangGraph Agent Pydantic Conversion & Studio Exposure")
    print("=" * 75)
    
    # Analyze all agents
    results = analyze_agents()
    
    # Count statuses
    total = len(results)
    pydantic_count = sum(1 for r in results if r['uses_pydantic'])
    export_count = sum(1 for r in results if r['has_export'])
    
    print(f"\nSummary:")
    print(f"   Total LangGraph agents: {total}")
    print(f"   Using Pydantic BaseModel: {pydantic_count}/{total}")
    print(f"   Have graph exports: {export_count}/{total}")
    
    # Generate and update langgraph.json
    config = generate_langgraph_json_config(results)
    
    print(f"\nGenerated langgraph.json with {len(config['graphs'])} exposed graphs:")
    for graph_name in sorted(config['graphs'].keys()):
        print(f"   - {graph_name}")
    
    # Write to file
    with open('langgraph.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nUpdated langgraph.json successfully!")
    
    # Show what still needs work
    needs_pydantic = [r for r in results if not r['uses_pydantic']]
    needs_export = [r for r in results if not r['has_export']]
    
    if needs_pydantic:
        print(f"\nAgents still using TypedDict (need Pydantic conversion):")
        for r in needs_pydantic:
            print(f"   - {r['name']}")
    
    if needs_export:
        print(f"\nAgents missing graph export files:")
        for r in needs_export:
            print(f"   - {r['name']} (need agents/langgraph_studio/{r['name']}_graph.py)")

if __name__ == "__main__":
    main()

