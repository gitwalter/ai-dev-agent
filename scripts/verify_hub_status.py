#!/usr/bin/env python3
"""
Verify LangSmith Hub Prompt Status
===================================

Check which prompts are in the hub and their tag status.
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
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# All prompts we've worked with
PROMPTS_TO_CHECK = [
    # Supervisor/Coordinator prompts
    ("complexity_analyzer_v1", "Supervisor", "⚠️  NEEDS TAGS"),
    ("agent_selector_v1", "Supervisor", "⚠️  NEEDS TAGS"),
    ("router_v1", "Supervisor", "⚠️  NEEDS TAGS"),
    
    # RAG prompts
    ("query_analyst_v1", "RAG", "✅ Has tags"),
    ("retrieval_specialist_v1", "RAG", "✅ Has tags"),
    ("re_ranker_v1", "RAG", "✅ Has tags"),
    ("quality_assurance_v1", "RAG", "✅ Has tags"),
    ("writer_v1", "RAG", "⚠️  NEEDS TAGS"),
    ("web_scraping_specialist_v1", "RAG", "⚠️  NEEDS TAGS"),
    
    # Development workflow prompts
    ("requirements_analyst_v1", "Development", "✅ Has tags"),
    ("architecture_designer_v1", "Development", "✅ Has tags"),
    ("code_generator_v1", "Development", "✅ Has tags"),
    ("test_generator_v1", "Development", "✅ Has tags"),
    ("code_reviewer_v1", "Development", "✅ Has tags"),
    ("documentation_generator_v1", "Development", "✅ Has tags"),
]

def check_prompt_status(client: Client, prompt_name: str, category: str, expected_status: str):
    """Check if prompt exists and has tags."""
    
    try:
        # Pull the prompt
        prompt = client.pull_prompt(prompt_name)
        
        # Check for tags
        has_tags = False
        tags = []
        
        if hasattr(prompt, 'metadata'):
            metadata = prompt.metadata
            if 'tags' in metadata and metadata['tags']:
                has_tags = True
                tags = metadata['tags']
        
        if hasattr(prompt, 'tags') and prompt.tags:
            has_tags = True
            tags = prompt.tags
        
        # Status
        if has_tags and tags:
            status = f"✅ HAS TAGS ({len(tags)} tags)"
            tag_list = ", ".join(tags[:5])  # Show first 5 tags
            if len(tags) > 5:
                tag_list += f", ... (+{len(tags)-5} more)"
        else:
            status = "⚠️  NO TAGS"
            tag_list = expected_status
        
        return {
            "exists": True,
            "has_tags": has_tags,
            "tag_count": len(tags) if tags else 0,
            "tags": tags,
            "status": status,
            "tag_preview": tag_list
        }
        
    except Exception as e:
        return {
            "exists": False,
            "has_tags": False,
            "tag_count": 0,
            "tags": [],
            "status": f"❌ NOT FOUND",
            "tag_preview": str(e)
        }

def main():
    """Main function."""
    print("\n" + "="*90)
    print("🔍 LangSmith Hub Prompt Status Verification")
    print("="*90 + "\n")
    
    client = Client(api_key=api_key)
    print("✅ Connected to LangSmith Hub\n")
    
    # Check each prompt
    results_by_category = {}
    
    for prompt_name, category, expected_status in PROMPTS_TO_CHECK:
        if category not in results_by_category:
            results_by_category[category] = []
        
        result = check_prompt_status(client, prompt_name, category, expected_status)
        result['prompt_name'] = prompt_name
        result['category'] = category
        result['expected_status'] = expected_status
        results_by_category[category].append(result)
    
    # Display results by category
    for category, results in results_by_category.items():
        print(f"\n{'='*90}")
        print(f"📦 {category} Prompts")
        print(f"{'='*90}")
        
        for result in results:
            prompt_name = result['prompt_name']
            status = result['status']
            tag_preview = result['tag_preview']
            
            print(f"\n🔷 {prompt_name}")
            print(f"   Status: {status}")
            
            if result['exists']:
                print(f"   URL: https://smith.langchain.com/prompts/{prompt_name}")
                
                if result['has_tags']:
                    print(f"   Tags: {tag_preview}")
                else:
                    print(f"   Action Required: {tag_preview}")
            else:
                print(f"   Error: {tag_preview}")
    
    # Summary
    print(f"\n{'='*90}")
    print("📊 Summary")
    print(f"{'='*90}")
    
    total = len(PROMPTS_TO_CHECK)
    exists = sum(1 for cat_results in results_by_category.values() for r in cat_results if r['exists'])
    has_tags = sum(1 for cat_results in results_by_category.values() for r in cat_results if r['has_tags'])
    needs_tags = exists - has_tags
    
    print(f"\n✅ Total prompts checked: {total}")
    print(f"✅ Prompts in hub: {exists}")
    print(f"✅ Prompts with tags: {has_tags}")
    print(f"⚠️  Prompts needing tags: {needs_tags}")
    
    if needs_tags > 0:
        print(f"\n{'='*90}")
        print("⚠️  MANUAL ACTION REQUIRED")
        print(f"{'='*90}")
        print(f"\nThe following {needs_tags} prompts need tags added manually:")
        print("Go to: https://smith.langchain.com/hub\n")
        
        for category, results in results_by_category.items():
            prompts_without_tags = [r for r in results if r['exists'] and not r['has_tags']]
            if prompts_without_tags:
                print(f"\n{category} Prompts:")
                for r in prompts_without_tags:
                    print(f"  • {r['prompt_name']} - {r['expected_status']}")
        
        print(f"\n💡 See docs/LANGSMITH_PROMPT_TAGS_REFERENCE.md for complete tag lists")
    else:
        print(f"\n{'='*90}")
        print("🎉 ALL PROMPTS HAVE TAGS!")
        print(f"{'='*90}")

if __name__ == "__main__":
    main()

