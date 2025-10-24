"""
Push Supervisor Prompts to LangSmith Hub
=========================================

This script pushes the 6 missing supervisor prompts to LangSmith Hub
using the official LangSmith Client API.
"""

import os
import sys
from pathlib import Path

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


def load_prompt_templates():
    """Load all prompt templates from files."""
    prompts_dir = project_root / "prompts" / "supervisor"
    
    if not prompts_dir.exists():
        print(f"[ERROR] Prompts directory not found: {prompts_dir}")
        print("Run: python scripts/create_missing_supervisor_prompts.py")
        return {}
    
    prompt_files = list(prompts_dir.glob("*_v1.txt"))
    if not prompt_files:
        print(f"[ERROR] No prompt template files found in: {prompts_dir}")
        return {}
    
    templates = {}
    for template_file in prompt_files:
        prompt_name = template_file.stem  # filename without .txt
        with open(template_file, 'r', encoding='utf-8') as f:
            templates[prompt_name] = f.read()
    
    return templates


def push_prompts_to_langsmith():
    """Push all supervisor prompts to LangSmith Hub."""
    
    print("=" * 80)
    print("Pushing Supervisor Prompts to LangSmith Hub")
    print("=" * 80)
    
    # Get API key
    api_key = get_langsmith_api_key()
    if not api_key:
        print("\n[ERROR] No API key found!")
        print("Add LANGSMITH_API_KEY to .streamlit/secrets.toml")
        return False
    
    print(f"\n[OK] API key loaded")
    
    # Initialize LangSmith client
    from langsmith import Client
    from langchain_core.prompts import PromptTemplate
    
    client = Client(api_key=api_key)
    print("[OK] LangSmith client initialized")
    
    # Load prompt templates
    print("\n[OK] Loading prompt templates...")
    templates = load_prompt_templates()
    
    if not templates:
        print("[ERROR] No templates loaded!")
        return False
    
    print(f"[OK] Loaded {len(templates)} prompt templates\n")
    
    # Push each prompt
    success_count = 0
    failed_prompts = []
    
    for prompt_name, template_content in templates.items():
        try:
            print(f"Pushing: {prompt_name}...", end=" ")
            
            # Create PromptTemplate
            prompt_template = PromptTemplate(
                template=template_content,
                input_variables=[]  # Will be inferred from template
            )
            
            # Push to LangSmith Hub
            # Note: The exact method might be push_prompt or something else
            # Let's try the documented method
            result = client.push_prompt(prompt_name, object=prompt_template)
            
            print("[SUCCESS]")
            print(f"   URL: https://smith.langchain.com/hub/{prompt_name}")
            success_count += 1
            
        except Exception as e:
            print(f"[FAILED]")
            print(f"   Error: {str(e)[:100]}")
            failed_prompts.append((prompt_name, str(e)))
    
    # Summary
    print("\n" + "=" * 80)
    print("Push Summary")
    print("=" * 80)
    print(f"\n[SUCCESS] {success_count}/{len(templates)} prompts pushed")
    
    if failed_prompts:
        print(f"\n[FAILED] {len(failed_prompts)} prompts failed:")
        for name, error in failed_prompts:
            print(f"   * {name}: {error[:80]}")
    
    print("\n" + "=" * 80)
    print("Next Steps")
    print("=" * 80)
    print("1. Verify prompts in LangSmith Hub: https://smith.langchain.com/hub")
    print("2. Test with: python scripts/pull_all_langsmith_prompts.py")
    print("3. Test workflow integration")
    
    return success_count == len(templates)


if __name__ == "__main__":
    try:
        success = push_prompts_to_langsmith()
        
        if success:
            print("\n[SUCCESS] All prompts pushed to LangSmith!")
        else:
            print("\n[WARNING] Some prompts failed to push")
            print("You may need to upload them manually via the web UI")
            print("See: prompts/supervisor/UPLOAD_INSTRUCTIONS.md")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        
        print("\n[FALLBACK] Use manual upload:")
        print("1. Go to: https://smith.langchain.com/hub")
        print("2. Follow: prompts/supervisor/UPLOAD_INSTRUCTIONS.md")

