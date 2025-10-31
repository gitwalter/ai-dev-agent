#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Qdrant collection dimensions to match actual embeddings.

This script:
1. Detects which embedding model is configured
2. Gets the actual dimensions from the embedding model
3. Recreates the collection with matching dimensions
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams

def get_actual_embedding_dimensions():
    """Detect and return actual embedding dimensions being used."""
    
    print("[INFO] Detecting embedding configuration...")
    
    # Try to initialize embeddings the same way context_engine does
    try:
        # Check for Gemini first
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        
        if gemini_api_key:
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                
                print("[OK] Initializing Gemini embeddings...")
                embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/gemini-embedding-001",
                    google_api_key=gemini_api_key,
                    task_type="retrieval_document"
                    # Gemini natively uses 3072 dimensions
                )
                
                # Test embedding to get actual dimensions
                test_embedding = embeddings.embed_query("test")
                dimensions = len(test_embedding)
                
                print(f"[OK] Gemini embeddings detected: {dimensions} dimensions")
                return dimensions, "Gemini (gemini-embedding-001)"
                
            except Exception as e:
                print(f"[ERROR] Gemini initialization failed: {e}")
        
        # Fallback to HuggingFace
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            
            print("[INFO] Falling back to HuggingFace embeddings...")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # Test embedding to get actual dimensions
            test_embedding = embeddings.embed_query("test")
            dimensions = len(test_embedding)
            
            print(f"[OK] HuggingFace embeddings detected: {dimensions} dimensions")
            return dimensions, "HuggingFace (all-MiniLM-L6-v2)"
            
        except Exception as e:
            print(f"[ERROR] HuggingFace initialization failed: {e}")
            
    except Exception as e:
        print(f"[ERROR] Could not detect embeddings: {e}")
    
    # Default fallback
    print("[WARNING] Could not detect embeddings, using default 384 dimensions")
    return 384, "Unknown (defaulting to 384)"


def fix_collection_dimensions():
    """Fix Qdrant collection dimensions to match actual embeddings."""
    
    # Get actual embedding dimensions
    dimensions, model_name = get_actual_embedding_dimensions()
    
    print("\n" + "=" * 80)
    print("FIXING QDRANT COLLECTION DIMENSIONS")
    print("=" * 80)
    print(f"\nDetected embedding model: {model_name}")
    print(f"Vector dimensions: {dimensions}")
    
    # Connect to Qdrant
    qdrant_path = project_root / "context_db" / "qdrant_storage"
    client = QdrantClient(path=str(qdrant_path))
    
    collection_name = "ai_dev_agent_codebase"
    
    # Check if collection exists
    collections = client.get_collections().collections
    collection_exists = any(c.name == collection_name for c in collections)
    
    if collection_exists:
        # Check current dimensions
        collection_info = client.get_collection(collection_name)
        
        try:
            # Try to get dimensions from collection config
            vectors_config = collection_info.config.params.vectors
            if isinstance(vectors_config, dict):
                # Named vectors (hybrid mode)
                current_dim = vectors_config.get('dense', {}).get('size') or vectors_config.get('size')
            else:
                # Single vector config
                current_dim = vectors_config.size
            
            if current_dim:
                print(f"\n[INFO] Current collection dimensions: {current_dim}")
                
                if current_dim == dimensions:
                    print(f"[OK] Collection already has correct dimensions ({dimensions})")
                    return
                else:
                    print(f"[WARNING] Dimension mismatch! Current: {current_dim}, Required: {dimensions}")
        except Exception as e:
            print(f"[WARNING] Could not determine current dimensions: {e}")
        
        print(f"\n[X] Deleting old collection '{collection_name}'...")
        client.delete_collection(collection_name=collection_name)
        print(f"[OK] Old collection deleted")
    else:
        print(f"\n[INFO] Collection '{collection_name}' doesn't exist yet")
    
    print(f"\n[OK] Creating new collection with {dimensions} dimensions...")
    
    # Create collection with correct dimensions
    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "dense": VectorParams(size=dimensions, distance=Distance.COSINE)
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams()
        }
    )
    
    print(f"[OK] Collection '{collection_name}' created with:")
    print(f"   - Dense vectors ({dimensions}-dim, COSINE) for semantic search")
    print(f"   - Sparse vectors (BM25) for exact keyword/name matching")
    
    print("\n" + "=" * 80)
    print("[OK] COLLECTION FIXED - READY FOR USE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Start the RAG Management UI")
    print("2. Re-upload your documents or re-scrape websites")
    print("3. The dimension mismatch warning should be gone!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        fix_collection_dimensions()
    except Exception as e:
        print(f"\n[ERROR] Failed to fix collection: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

