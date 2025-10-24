"""
Push prompts to LangSmith Hub

⚠️  IMPORTANT: This script is ONLY used when you've edited prompts locally and want
   to push changes to LangSmith Hub. Normal workflow is to PULL from LangSmith.

Usage:
    # Push a single prompt (after editing it locally)
    python scripts/push_prompts_to_langsmith.py --prompt test_generator_v1
    
    # Push all prompts (after editing multiple locally)
    python scripts/push_prompts_to_langsmith.py --all
    
    # Push specific prompts with updates
    python scripts/push_prompts_to_langsmith.py --prompt code_generator_v1 --prompt test_generator_v1

Normal Workflow:
    1. ✅ PULL from LangSmith (done automatically in workflow)
    2. ✅ Edit prompts in LangSmith UI (preferred) OR edit locally
    3. ✅ If edited locally, use this script to PUSH changes back to LangSmith
"""
import argparse
import os
from pathlib import Path

def push_prompt_to_langsmith(prompt_name: str, prompt_text: str, api_key: str) -> bool:
    """
    Push a prompt to LangSmith Hub.
    
    Args:
        prompt_name: Name of the prompt (e.g., "test_generator_v1")
        prompt_text: Full prompt content
        api_key: LangSmith API key
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from langsmith import Client
        from langchain_core.prompts import ChatPromptTemplate
        
        # Create LangSmith client
        client = Client(api_key=api_key)
        
        # Create ChatPromptTemplate from the prompt text
        # For system prompts, wrap in system message
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", prompt_text)
        ])
        
        # Push to LangSmith
        url = client.push_prompt(prompt_name, object=prompt_template)
        
        print(f"[OK] Successfully pushed {prompt_name} to LangSmith")
        print(f"     URL: {url}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to push {prompt_name}: {e}")
        return False


def get_api_key() -> str:
    """Get LangSmith API key from Streamlit secrets or environment."""
    try:
        import streamlit as st
        api_key = st.secrets.get('LANGSMITH_API_KEY') or st.secrets.get('LANGCHAIN_API_KEY')
        if api_key:
            return api_key
    except:
        pass
    
    # Try environment variables
    api_key = os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGCHAIN_API_KEY")
    if api_key:
        return api_key
    
    raise ValueError("LANGSMITH_API_KEY not found in secrets or environment")


def find_prompt_file(prompt_name: str) -> Path:
    """Find the prompt file for a given prompt name."""
    # Try different locations
    locations = [
        Path(f"prompts/langsmith_cache/{prompt_name}.txt"),
        Path(f"prompts/supervisor/{prompt_name}.txt"),
        Path(f"prompts/{prompt_name}.txt"),
    ]
    
    for location in locations:
        if location.exists():
            return location
    
    raise FileNotFoundError(f"Could not find prompt file for {prompt_name}")


def get_all_prompts() -> list[str]:
    """Get all available prompt names."""
    prompts = []
    
    # Check langsmith_cache
    cache_dir = Path("prompts/langsmith_cache")
    if cache_dir.exists():
        for file in cache_dir.glob("*.txt"):
            prompts.append(file.stem)
    
    # Check supervisor
    supervisor_dir = Path("prompts/supervisor")
    if supervisor_dir.exists():
        for file in supervisor_dir.glob("*.txt"):
            prompts.append(file.stem)
    
    return sorted(set(prompts))


def update_test_generator_prompt(prompt_text: str) -> str:
    """
    Update test_generator prompt to explicitly require test_files array.
    
    This adds a section to ensure the agent generates actual test code files.
    """
    # Check if already has test_files requirement
    if "test_files" in prompt_text and '"path"' in prompt_text:
        print("  [INFO] Prompt already includes test_files requirement")
        return prompt_text
    
    # Add test_files requirement after the OUTPUT FORMAT section
    addition = """

CRITICAL REQUIREMENT FOR TEST FILES:
Your output MUST include a "test_files" array with actual, executable test code files:

"test_files": [
  {"path": "tests/test_example.py", "content": "import pytest\\n\\ndef test_example():\\n    assert True"},
  {"path": "tests/test_another.py", "content": "import unittest\\n\\nclass TestAnother(unittest.TestCase):\\n    def test_something(self):\\n        self.assertTrue(True)"}
]

Each test file must contain:
- Full, executable test code (not placeholders or comments)
- Proper test framework imports (pytest, unittest, etc.)
- Complete test functions/methods with assertions
- Proper file paths relative to project root

DO NOT generate test descriptions or test plans without actual code.
"""
    
    # Insert after EXPECTED OUTPUT FORMAT section
    if "EXPECTED OUTPUT FORMAT" in prompt_text:
        parts = prompt_text.split("EXPECTED OUTPUT FORMAT")
        if len(parts) == 2:
            # Find the end of the JSON example
            json_end = parts[1].find("```\n") + 4
            if json_end > 4:
                return parts[0] + "EXPECTED OUTPUT FORMAT" + parts[1][:json_end] + addition + parts[1][json_end:]
    
    # If we couldn't find the right place, append at the end
    return prompt_text + addition


def main():
    parser = argparse.ArgumentParser(description="Push prompts to LangSmith Hub")
    parser.add_argument("--prompt", "-p", action="append", help="Prompt name to push (can be used multiple times)")
    parser.add_argument("--all", "-a", action="store_true", help="Push all available prompts")
    parser.add_argument("--update-test-generator", action="store_true", 
                       help="Update test_generator prompt with test_files requirement")
    
    args = parser.parse_args()
    
    # Get API key
    try:
        api_key = get_api_key()
        print(f"[OK] Found LangSmith API key")
    except ValueError as e:
        print(f"[ERROR] {e}")
        return 1
    
    # Determine which prompts to push
    if args.all:
        prompt_names = get_all_prompts()
        print(f"Found {len(prompt_names)} prompts to push")
    elif args.prompt:
        prompt_names = args.prompt
    else:
        print("[ERROR] Specify --prompt NAME or --all")
        parser.print_help()
        return 1
    
    # Push prompts
    success_count = 0
    fail_count = 0
    
    for prompt_name in prompt_names:
        try:
            print(f"\nProcessing {prompt_name}...")
            
            # Find and read prompt file
            prompt_file = find_prompt_file(prompt_name)
            prompt_text = prompt_file.read_text(encoding='utf-8')
            print(f"  Read from {prompt_file}")
            
            # Special handling for test_generator
            if args.update_test_generator and "test_generator" in prompt_name:
                print(f"  Updating test_generator with test_files requirement")
                prompt_text = update_test_generator_prompt(prompt_text)
            
            # Push to LangSmith
            if push_prompt_to_langsmith(prompt_name, prompt_text, api_key):
                success_count += 1
            else:
                fail_count += 1
                
        except Exception as e:
            print(f"[ERROR] Error processing {prompt_name}: {e}")
            fail_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Successfully pushed: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"{'='*60}")
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    exit(main())

