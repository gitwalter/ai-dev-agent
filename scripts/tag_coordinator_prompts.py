#!/usr/bin/env python3
"""Tag RAG Coordinator Prompts"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
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
    except Exception:
        pass

if not api_key:
    print("No API key found!")
    sys.exit(1)

from langsmith import Client

PROMPTS_WITH_TAGS = {
    "document_grader_v1": ["rag", "agentic-rag", "document-grading", "relevance-scoring", "retrieval-quality", "coordinator", "agent"],
    "query_rewriter_v1": ["rag", "agentic-rag", "query-rewriting", "query-optimization", "retrieval-enhancement", "coordinator", "agent"],
    "answer_generator_v1": ["rag", "agentic-rag", "answer-generation", "response-synthesis", "question-answering", "coordinator", "agent"],
}

client = Client(api_key=api_key)

print("Tagging RAG coordinator prompts...")
print("="*70)

for prompt_name, tags in PROMPTS_WITH_TAGS.items():
    try:
        result = client.update_prompt(prompt_name, tags=tags)
        print(f"\n{prompt_name}:")
        print(f"  Status: SUCCESS")
        print(f"  Tags: {', '.join(tags)}")
    except Exception as e:
        print(f"\n{prompt_name}:")
        print(f"  Status: FAILED - {e}")

print("\n" + "="*70)
print("Done!")

