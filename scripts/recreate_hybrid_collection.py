#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recreate Qdrant collection with proper hybrid search support.
This ensures names and exact terms are findable via BM25.
"""

import sys
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def recreate_collection():
    """Delete old collection and create new one with hybrid search."""
    
    qdrant_path = Path(__file__).parent.parent / "context_db" / "qdrant_storage"
    client = QdrantClient(path=str(qdrant_path))
    
    collection_name = "ai_dev_agent_codebase"
    
    # Detect embedding dimensions from environment
    # Default to 768 for Gemini embeddings (currently configured)
    # Use 384 if GEMINI_API_KEY not set (will fall back to HuggingFace)
    gemini_available = os.environ.get("GEMINI_API_KEY") is not None
    embedding_dim = 768 if gemini_available else 384
    embedding_model = "Gemini (768-dim)" if gemini_available else "HuggingFace (384-dim)"
    
    print("=" * 80)
    print("RECREATING QDRANT COLLECTION WITH HYBRID SEARCH")
    print("=" * 80)
    print(f"\nDetected embedding model: {embedding_model}")
    print(f"Vector dimensions: {embedding_dim}")
    
    # Check if collection exists
    collections = client.get_collections().collections
    collection_exists = any(c.name == collection_name for c in collections)
    
    if collection_exists:
        print(f"\n[X] Deleting old collection '{collection_name}'...")
        client.delete_collection(collection_name=collection_name)
        print(f"[OK] Old collection deleted")
    else:
        print(f"\n[INFO] Collection '{collection_name}' doesn't exist yet")
    
    print(f"\n[OK] Creating new collection with HYBRID search support...")
    
    # Create collection with dense + sparse vectors
    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "dense": VectorParams(size=embedding_dim, distance=Distance.COSINE)
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams()
        }
    )
    
    print(f"[OK] Collection '{collection_name}' created with:")
    print(f"   - Dense vectors ({embedding_dim}-dim, COSINE) for semantic search")
    print(f"   - Sparse vectors (BM25) for exact keyword/name matching")
    
    print("\n" + "=" * 80)
    print("[OK] READY FOR RE-INDEXING")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Go to RAG Management UI")
    print("2. Re-upload your documents or re-scrape websites")
    print("3. Test with a query containing a name - it will now be found via BM25!")
    print("=" * 80)

if __name__ == "__main__":
    recreate_collection()

