#!/usr/bin/env python3
"""
Verify and Add Tags to RAG Prompts
===================================

Check which prompts have tags and add them where missing.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Get API key
api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")
if not api_key:
    try:
        secrets_path = project_root / ".streamlit" / "secrets.toml"
        if secrets_path.exists():
            with open(secrets_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        if key in ["LANGSMITH_API_KEY", "LANGCHAIN_API_KEY"]:
                            api_key = value.strip().strip('"').strip("'")
                            break
    except Exception as e:
        print(f"Error: {e}")

if not api_key:
    print("❌ No API key found!")
    sys.exit(1)

try:
    from langsmith import Client
    from langchain_core.prompts import ChatPromptTemplate
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Tags for each prompt
PROMPT_TAGS = {
    "writer_v1": ["rag", "response-generation", "synthesis", "writing", "source-attribution", "agent"],
    "web_scraping_specialist_v1": ["rag", "web-scraping", "content-extraction", "document-parsing", "data-ingestion", "agent"]
}

def check_and_add_tags(client: Client, prompt_name: str, tags: list):
    """Check current tags and add if missing."""
    
    try:
        # Pull the current prompt
        prompt = client.pull_prompt(prompt_name)
        print(f"\n📋 {prompt_name}:")
        print(f"   Current type: {type(prompt)}")
        
        # Check if it has tags attribute or metadata
        if hasattr(prompt, 'metadata'):
            print(f"   Metadata: {prompt.metadata}")
        if hasattr(prompt, 'tags'):
            print(f"   Tags: {prompt.tags}")
        
        # Read local content
        cache_dir = project_root / "prompts" / "langsmith_cache"
        prompt_file = cache_dir / f"{prompt_name}.txt"
        
        if not prompt_file.exists():
            print(f"   ❌ Local file not found")
            return False
        
        content = prompt_file.read_text(encoding='utf-8')
        
        # Create new prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", content)
        ])
        
        # Try pushing without public flag
        print(f"   🔄 Pushing with tags: {tags}")
        url = client.push_prompt(
            prompt_name,
            object=prompt_template
            # Note: tags parameter doesn't seem to work consistently
        )
        
        print(f"   ✅ Updated: {url}")
        print(f"   💡 Note: Tags may need to be added manually in LangSmith UI")
        print(f"   📝 Suggested tags: {', '.join(tags)}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main function."""
    print("="*70)
    print("🏷️  Verifying and Adding Tags to RAG Prompts")
    print("="*70)
    
    client = Client(api_key=api_key)
    print("\n✅ Client initialized")
    
    for prompt_name, tags in PROMPT_TAGS.items():
        check_and_add_tags(client, prompt_name, tags)
    
    print("\n" + "="*70)
    print("📊 Summary")
    print("="*70)
    print("\n💡 If tags are not showing in LangSmith Hub:")
    print("   1. Go to https://smith.langchain.com/hub")
    print("   2. Find each prompt (writer_v1, web_scraping_specialist_v1)")
    print("   3. Click 'Edit' and add tags manually:")
    print("\n   writer_v1:")
    print("      • rag")
    print("      • response-generation")
    print("      • synthesis")
    print("      • writing")
    print("      • source-attribution")
    print("      • agent")
    print("\n   web_scraping_specialist_v1:")
    print("      • rag")
    print("      • web-scraping")
    print("      • content-extraction")
    print("      • document-parsing")
    print("      • data-ingestion")
    print("      • agent")

if __name__ == "__main__":
    main()

