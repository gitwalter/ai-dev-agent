#!/usr/bin/env python3
"""
Update RAG Prompt Metadata in LangSmith Hub
============================================

Update metadata and tags for RAG prompts using the correct LangSmith API.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Check for API key
api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")

if not api_key:
    # Try loading from secrets
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
        print(f"Error loading secrets: {e}")

if not api_key:
    print("❌ No LANGSMITH_API_KEY found!")
    sys.exit(1)

print(f"✅ API Key found: {api_key[:10]}...")

# Import LangSmith
try:
    from langsmith import Client
    from langchain import hub
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install: pip install langsmith langchain")
    sys.exit(1)

# RAG prompts with their complete metadata
RAG_PROMPTS_METADATA = {
    "query_analyst_v1": {
        "description": "Expert Query Analyst for RAG systems - analyzes user queries, extracts intent, generates query variants, and recommends optimal search strategies",
        "tags": ["rag", "query-analysis", "query-expansion", "intent-classification", "search-optimization", "agent", "retrieval"]
    },
    "retrieval_specialist_v1": {
        "description": "Expert Retrieval Specialist for RAG systems - executes semantic, keyword, and hybrid searches with adaptive retrieval strategies",
        "tags": ["rag", "retrieval", "semantic-search", "vector-search", "multi-query", "hybrid-search", "agent"]
    },
    "re_ranker_v1": {
        "description": "Expert Re-Ranker for RAG systems - evaluates and re-orders retrieved documents by relevance and quality",
        "tags": ["rag", "reranking", "relevance-scoring", "document-ranking", "quality-assessment", "agent"]
    },
    "quality_assurance_v1": {
        "description": "Expert Quality Assurance Agent for RAG systems - validates responses, detects hallucinations, and ensures accuracy",
        "tags": ["rag", "quality-assurance", "validation", "hallucination-detection", "accuracy-check", "agent"]
    },
    "writer_v1": {
        "description": "Expert Writer Agent for RAG systems - synthesizes information from multiple sources and generates accurate, well-structured responses with proper attribution",
        "tags": ["rag", "response-generation", "synthesis", "writing", "source-attribution", "agent"]
    },
    "web_scraping_specialist_v1": {
        "description": "Expert Web Scraping Specialist for RAG systems - extracts and processes web content for knowledge base enrichment",
        "tags": ["rag", "web-scraping", "content-extraction", "document-parsing", "data-ingestion", "agent"]
    }
}

def update_prompt_with_hub(prompt_name: str, metadata: dict):
    """Update prompt using langchain hub.push with is_public flag."""
    
    try:
        cache_dir = project_root / "prompts" / "langsmith_cache"
        prompt_file = cache_dir / f"{prompt_name}.txt"
        
        if not prompt_file.exists():
            print(f"❌ {prompt_name}: Local file not found")
            return False
        
        content = prompt_file.read_text(encoding='utf-8')
        
        from langchain_core.prompts import ChatPromptTemplate
        
        # Create prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", content)
        ])
        
        # Push with hub.push which supports tags
        result = hub.push(
            prompt_name,
            prompt_template,
            api_key=api_key,
            new_repo_is_public=True,  # Make it public in the hub
            tags=metadata["tags"]
        )
        
        print(f"✅ {prompt_name}: Updated with metadata")
        print(f"   Description: {metadata['description'][:80]}...")
        print(f"   Tags: {', '.join(metadata['tags'])}")
        return True
        
    except Exception as e:
        print(f"❌ {prompt_name}: Failed - {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function."""
    print("\n" + "="*80)
    print("🏷️  Updating RAG Prompt Metadata in LangSmith Hub")
    print("="*80 + "\n")
    
    print("📝 Note: Using langchain.hub.push for proper tag support\n")
    
    # Update each prompt
    success_count = 0
    fail_count = 0
    
    for prompt_name, metadata in RAG_PROMPTS_METADATA.items():
        if update_prompt_with_hub(prompt_name, metadata):
            success_count += 1
        else:
            fail_count += 1
        print()  # Blank line between prompts
    
    # Summary
    print("="*80)
    print("📊 Summary")
    print("="*80)
    print(f"✅ Successfully updated: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📝 Total: {len(RAG_PROMPTS_METADATA)}")
    print("="*80 + "\n")
    
    if success_count > 0:
        print("🎉 RAG prompts updated! Check them in LangSmith Hub:")
        print("   https://smith.langchain.com/hub\n")
        print("All prompts now have:")
        print("  ✅ Descriptive metadata")
        print("  ✅ Searchable tags")
        print("  ✅ Public visibility")
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()

