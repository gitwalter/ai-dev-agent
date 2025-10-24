"""
Pull All LangSmith Prompts
===========================

This script pulls all prompts from LangSmith and displays their details.
Uses official LangSmith Client API.
"""

import os
import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Streamlit for secrets management
import streamlit as st

def get_langsmith_api_key():
    """Get LangSmith API key from st.secrets."""
    try:
        if 'LANGSMITH_API_KEY' in st.secrets:
            return st.secrets['LANGSMITH_API_KEY']
        elif 'LANGCHAIN_API_KEY' in st.secrets:
            return st.secrets['LANGCHAIN_API_KEY']
    except:
        pass
    
    # Fallback to environment
    return os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGCHAIN_API_KEY")


def pull_all_prompts():
    """Pull all prompts from LangSmith."""
    
    print("=" * 80)
    print("Pulling All Prompts from LangSmith")
    print("=" * 80)
    
    # Get API key
    api_key = get_langsmith_api_key()
    if not api_key:
        print("\n[ERROR] No API key found!")
        print("Add LANGSMITH_API_KEY to .streamlit/secrets.toml")
        return {}
    
    print(f"\n[OK] API key loaded from st.secrets")
    
    # Initialize LangSmith client
    from langsmith import Client
    client = Client(api_key=api_key)
    print("[OK] LangSmith client initialized")
    
    # List of all possible prompts for our agents
    all_prompts = [
        # Specialist Agents
        "requirements_analyst_v1",
        "architecture_designer_v1",
        "code_generator_v1",
        "test_generator_v1",
        "code_reviewer_v1",
        "security_analyst_v1",
        "documentation_generator_v1",
        
        # Supervisor/Coordinator Agents
        "complexity_analyzer_v1",
        "agent_selector_v1",
        "router_v1",
        "project_manager_supervisor_v1",
        "quality_control_supervisor_v1",
        "task_router_supervisor_v1"
    ]
    
    found_prompts = {}
    missing_prompts = []
    
    print(f"\nChecking {len(all_prompts)} prompts...\n")
    
    for prompt_name in all_prompts:
        try:
            print(f"Pulling: {prompt_name}...", end=" ")
            
            # Use official API: client.pull_prompt()
            prompt = client.pull_prompt(prompt_name, include_model=True)
            
            found_prompts[prompt_name] = prompt
            print("[FOUND]")
            
            # Display details
            print(f"   Type: {type(prompt).__name__}")
            
            if hasattr(prompt, 'messages'):
                print(f"   Messages: {len(prompt.messages)}")
                for i, msg in enumerate(prompt.messages[:2]):  # Show first 2
                    msg_type = type(msg).__name__
                    if hasattr(msg, 'content'):
                        content_preview = str(msg.content)[:80]
                        print(f"      [{i}] {msg_type}: {content_preview}...")
            
            if hasattr(prompt, 'input_variables'):
                vars_list = prompt.input_variables if prompt.input_variables else []
                print(f"   Variables: {', '.join(vars_list) if vars_list else 'None'}")
            
            if hasattr(prompt, 'template'):
                template = prompt.template
                print(f"   Template length: {len(template)} chars")
                lines = template.split('\n')[:3]
                print(f"   Preview:")
                for line in lines:
                    if line.strip():
                        print(f"      {line[:70]}...")
                        break
            
            print()
            
        except Exception as e:
            missing_prompts.append(prompt_name)
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                print("[NOT FOUND]")
            else:
                print(f"[ERROR]: {error_msg[:60]}")
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"\n[FOUND] {len(found_prompts)}/{len(all_prompts)} prompts")
    
    if found_prompts:
        print("\nExisting Prompts:")
        for name in sorted(found_prompts.keys()):
            prompt = found_prompts[name]
            if hasattr(prompt, 'template'):
                length = len(prompt.template)
            else:
                length = "N/A"
            print(f"   * {name} ({length} chars)")
    
    print(f"\n[MISSING] {len(missing_prompts)}/{len(all_prompts)} prompts")
    if missing_prompts:
        print("\nMissing Prompts:")
        for name in sorted(missing_prompts):
            print(f"   * {name}")
    
    return found_prompts, missing_prompts


def save_prompts_to_file(found_prompts):
    """Save found prompts to JSON for reference."""
    output = {}
    
    for name, prompt in found_prompts.items():
        output[name] = {
            "type": type(prompt).__name__,
            "template_length": len(prompt.template) if hasattr(prompt, 'template') else 0,
            "variables": prompt.input_variables if hasattr(prompt, 'input_variables') else [],
            "has_model": hasattr(prompt, 'model')
        }
    
    output_file = project_root / "docs" / "architecture" / "langsmith_prompts_inventory.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[OK] Saved inventory to: {output_file}")
    return output_file


if __name__ == "__main__":
    try:
        found, missing = pull_all_prompts()
        
        if found:
            output_file = save_prompts_to_file(found)
            print(f"\nInventory saved to: {output_file}")
        
        print("\n" + "=" * 80)
        print("Done!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

