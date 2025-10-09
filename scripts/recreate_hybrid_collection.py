#!/usr/bin/env python3
"""
Recreate Qdrant collection with proper hybrid search support.
This ensures names and exact terms are findable via BM25.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams
from pathlib import Path

def recreate_collection():
    """Delete old collection and create new one with hybrid search."""
    
    qdrant_path = Path(__file__).parent.parent / "context_db" / "qdrant_storage"
    client = QdrantClient(path=str(qdrant_path))
    
    collection_name = "ai_dev_agent_codebase"
    
    print("=" * 80)
    print("RECREATING QDRANT COLLECTION WITH HYBRID SEARCH")
    print("=" * 80)
    
    # Check if collection exists
    collections = client.get_collections().collections
    collection_exists = any(c.name == collection_name for c in collections)
    
    if collection_exists:
        print(f"\n❌ Deleting old collection '{collection_name}'...")
        client.delete_collection(collection_name=collection_name)
        print(f"✅ Old collection deleted")
    else:
        print(f"\nℹ️  Collection '{collection_name}' doesn't exist yet")
    
    print(f"\n✅ Creating new collection with HYBRID search support...")
    
    # Create collection with dense + sparse vectors
    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "dense": VectorParams(size=384, distance=Distance.COSINE)
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams()
        }
    )
    
    print(f"✅ Collection '{collection_name}' created with:")
    print(f"   - Dense vectors (384-dim, COSINE) for semantic search")
    print(f"   - Sparse vectors (BM25) for exact keyword/name matching")
    
    print("\n" + "=" * 80)
    print("✅ READY FOR RE-INDEXING")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Go to RAG Management UI")
    print("2. Re-upload your documents or re-scrape websites")
    print("3. Test with a query containing a name - it will now be found via BM25!")
    print("=" * 80)

if __name__ == "__main__":
    recreate_collection()

