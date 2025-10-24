"""
Inspect LangSmith Prompts
=========================

This script connects to LangSmith and lists all available prompts,
showing their details and comparing with required prompts.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Streamlit for secrets management
import streamlit as st

def get_api_key_from_secrets():
    """Get API key from Streamlit secrets using st.secrets."""
    try:
        # Use st.secrets to read from .streamlit/secrets.toml
        # LangSmith and LangChain both work with the same API key
        if 'LANGSMITH_API_KEY' in st.secrets:
            return st.secrets['LANGSMITH_API_KEY']
        elif 'LANGCHAIN_API_KEY' in st.secrets:
            return st.secrets['LANGCHAIN_API_KEY']
        
        # Check nested structures
        if 'langchain' in st.secrets and 'api_key' in st.secrets['langchain']:
            return st.secrets['langchain']['api_key']
        elif 'langsmith' in st.secrets and 'api_key' in st.secrets['langsmith']:
            return st.secrets['langsmith']['api_key']
            
    except Exception as e:
        print(f"   Note: Could not read from st.secrets: {e}")
    return None

def check_langsmith_setup():
    """Check if LangSmith is properly configured."""
    # Try multiple sources for API key
    api_key = None
    api_key_source = None
    
    # 1. Try Streamlit secrets FIRST (preferred method)
    api_key = get_api_key_from_secrets()
    if api_key:
        api_key_source = "Streamlit Secrets (st.secrets)"
        # Set it in environment for other code (both names for compatibility)
        os.environ["LANGCHAIN_API_KEY"] = api_key
        os.environ["LANGSMITH_API_KEY"] = api_key
    
    # 2. Fall back to environment variables
    if not api_key:
        api_key = os.environ.get("LANGCHAIN_API_KEY") or os.environ.get("LANGSMITH_API_KEY")
        if api_key:
            api_key_source = "Environment Variable"
    
    # Get project and tracing settings (try st.secrets first, then env)
    try:
        project = st.secrets.get("LANGSMITH_PROJECT") or st.secrets.get("LANGCHAIN_PROJECT", "ai-dev-agent")
        tracing = st.secrets.get("LANGSMITH_TRACING") or st.secrets.get("LANGCHAIN_TRACING_V2", "false")
    except:
        project = os.environ.get("LANGCHAIN_PROJECT") or os.environ.get("LANGSMITH_PROJECT") or "ai-dev-agent"
        tracing = os.environ.get("LANGCHAIN_TRACING_V2") or os.environ.get("LANGSMITH_TRACING") or "false"
    
    print("=" * 80)
    print("LangSmith Configuration Check")
    print("=" * 80)
    print(f"API KEY: {'[SET]' if api_key else '[NOT SET]'}")
    if api_key_source:
        print(f"   Source: {api_key_source}")
    print(f"PROJECT: {project}")
    print(f"TRACING: {tracing}")
    print()
    
    if not api_key:
        print("WARNING: LangSmith API KEY not found!")
        print("   Tried:")
        print("   1. Streamlit secrets (st.secrets['LANGSMITH_API_KEY'])")
        print("   2. Environment variable LANGCHAIN_API_KEY or LANGSMITH_API_KEY")
        print()
        print("   To fix:")
        print("   - Add to .streamlit/secrets.toml:")
        print("     LANGSMITH_API_KEY = \"your-key-here\"")
        print("   - Or set environment: export LANGCHAIN_API_KEY='your-key-here'")
        return False
    
    return True


def list_prompts_from_hub():
    """List all prompts from LangSmith Hub using LangSmith Client."""
    print("=" * 80)
    print("Prompts in LangSmith Hub")
    print("=" * 80)
    
    try:
        from langsmith import Client
        
        # Get API key from environment
        api_key = os.environ.get("LANGCHAIN_API_KEY")
        if not api_key:
            print("\n[ERROR] LANGCHAIN_API_KEY not set")
            return [], []
        
        # Create LangSmith client
        client = Client(api_key=api_key)
        print("\n[OK] LangSmith client initialized")
        
        # List of required prompts
        required_prompts = [
            "requirements_analyst_v1",
            "code_generator_v1", 
            "documentation_generator_v1",
            "complexity_analyzer_v1",
            "agent_selector_v1"
        ]
        
        found_prompts = []
        missing_prompts = []
        
        print("\nFetching prompts from LangSmith...")
        
        for prompt_name in required_prompts:
            try:
                print(f"\nChecking: {prompt_name}")
                
                # Use correct method: client.pull_prompt()
                prompt = client.pull_prompt(prompt_name, include_model=True)
                
                found_prompts.append(prompt_name)
                print(f"   [FOUND]")
                print(f"   Type: {type(prompt).__name__}")
                
                # Get prompt details
                if hasattr(prompt, 'messages'):
                    print(f"   Messages: {len(prompt.messages)}")
                    for i, msg in enumerate(prompt.messages[:3]):  # Show first 3
                        msg_type = type(msg).__name__
                        if hasattr(msg, 'content'):
                            content = str(msg.content)
                            content_preview = content[:100]
                            print(f"      [{i}] {msg_type}: {content_preview}...")
                        else:
                            print(f"      [{i}] {msg_type}")
                
                if hasattr(prompt, 'input_variables'):
                    print(f"   Variables: {prompt.input_variables}")
                
                if hasattr(prompt, 'template'):
                    template = prompt.template
                    print(f"   Template length: {len(template)} chars")
                    print(f"   First 150 chars: {template[:150]}...")
                
                # Check if model is included
                if hasattr(prompt, 'model'):
                    print(f"   Model: {prompt.model}")
                    
            except Exception as e:
                missing_prompts.append(prompt_name)
                error_msg = str(e)
                print(f"   [NOT FOUND]: {error_msg[:100]}")
        
        print("\n" + "=" * 80)
        print("Summary")
        print("=" * 80)
        print(f"Found: {len(found_prompts)}/{len(required_prompts)}")
        if found_prompts:
            for name in found_prompts:
                print(f"   * {name}")
        
        print(f"\nMissing: {len(missing_prompts)}/{len(required_prompts)}")
        if missing_prompts:
            for name in missing_prompts:
                print(f"   * {name}")
        
        return found_prompts, missing_prompts
        
    except ImportError:
        print("[ERROR] langsmith package not available")
        print("   Install with: pip install langsmith")
        return [], required_prompts
    except Exception as e:
        print(f"[ERROR] accessing LangSmith: {e}")
        import traceback
        traceback.print_exc()
        return [], []


def list_prompts_via_client():
    """List prompts using LangSmith client directly."""
    print("\n" + "=" * 80)
    print("Attempting to list prompts via LangSmith Client")
    print("=" * 80)
    
    try:
        from langsmith import Client
        
        client = Client()
        print("[OK] LangSmith client connected")
        
        # Try to get organization info
        try:
            # Note: API methods vary by langsmith version
            print("\nAttempting to list prompts...")
            
            # This may not work depending on the API version
            # We're exploring the client capabilities
            
            print("   LangSmith client methods:")
            client_methods = [m for m in dir(client) if not m.startswith('_')]
            for method in client_methods[:20]:  # Show first 20
                print(f"      * {method}")
            
            if len(client_methods) > 20:
                print(f"      ... and {len(client_methods) - 20} more")
                
        except Exception as e:
            print(f"   [WARNING] Could not list: {e}")
        
    except ImportError:
        print("[ERROR] langsmith package not available")
        print("   Install with: pip install langsmith")
    except Exception as e:
        print(f"[ERROR] with LangSmith client: {e}")


def check_prompts_in_workflow():
    """Check which prompts are loaded in the workflow."""
    print("\n" + "=" * 80)
    print("Prompts Currently Used in Workflow")
    print("=" * 80)
    
    try:
        # Set dummy API key for testing
        os.environ.setdefault('GEMINI_API_KEY', 'test-key-for-inspection')
        
        from workflow.langgraph_workflow import AgentSwarm
        
        print("\nInitializing AgentSwarm...")
        swarm = AgentSwarm({'model_name': 'gemini-2.5-flash', 'temperature': 0})
        
        print(f"\n[OK] Workflow initialized")
        print(f"   Total agents: {len(swarm.agents)}")
        print(f"   Total prompts loaded: {len(swarm.agent_prompts)}")
        
        print("\nLoaded Prompts:")
        for agent_name, prompt in swarm.agent_prompts.items():
            print(f"\n   Agent: {agent_name}")
            print(f"      Type: {type(prompt).__name__}")
            
            if hasattr(prompt, 'template'):
                template = prompt.template
                print(f"      Template length: {len(template)} chars")
                
                # Count variables in template
                import re
                variables = re.findall(r'\{(\w+)\}', template)
                if variables:
                    print(f"      Variables: {', '.join(set(variables))}")
                
                # Show first few lines
                lines = template.split('\n')[:5]
                print(f"      Preview:")
                for line in lines:
                    if line.strip():
                        print(f"         {line[:70]}...")
                        
            elif hasattr(prompt, 'messages'):
                print(f"      Messages: {len(prompt.messages)}")
        
        return swarm.agent_prompts
        
    except Exception as e:
        print(f"[ERROR] loading workflow: {e}")
        import traceback
        traceback.print_exc()
        return {}


def generate_prompt_creation_guide(missing_prompts):
    """Generate guide for creating missing prompts."""
    if not missing_prompts:
        print("\n[OK] All required prompts are available!")
        return
    
    print("\n" + "=" * 80)
    print("Guide: Creating Missing Prompts in LangSmith")
    print("=" * 80)
    
    print(f"\nYou need to create {len(missing_prompts)} prompts:")
    for i, prompt_name in enumerate(missing_prompts, 1):
        print(f"\n{i}. {prompt_name}")
        print(f"   URL: https://smith.langchain.com/hub")
        print(f"   Steps:")
        print(f"      1. Click '+ New Prompt'")
        print(f"      2. Name: {prompt_name}")
        print(f"      3. Copy template from: docs/architecture/LANGSMITH_PROMPTS_REQUIRED.md")
        print(f"      4. Test with sample inputs")
        print(f"      5. Commit and publish")


def main():
    """Main inspection function."""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "LangSmith Prompts Inspector")
    print("=" * 80)
    print()
    
    # Check configuration
    if not check_langsmith_setup():
        print("\n[WARNING] Configure LangSmith first, then run this script again.")
        return
    
    # Try different methods to list prompts
    found_prompts, missing_prompts = list_prompts_from_hub()
    
    # Try client method
    list_prompts_via_client()
    
    # Check workflow
    workflow_prompts = check_prompts_in_workflow()
    
    # Generate creation guide
    generate_prompt_creation_guide(missing_prompts)
    
    print("\n" + "=" * 80)
    print("[OK] Inspection Complete")
    print("=" * 80)
    print(f"\nNext Steps:")
    print(f"1. Review the findings above")
    print(f"2. Create missing prompts in LangSmith Hub")
    print(f"3. Reference: docs/architecture/LANGSMITH_PROMPTS_REQUIRED.md")
    print(f"4. Test prompts with the workflow")
    print()


if __name__ == "__main__":
    main()

