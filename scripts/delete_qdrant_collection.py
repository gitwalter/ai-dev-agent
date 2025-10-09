#!/usr/bin/env python3
"""
Delete Qdrant Collection
========================

Quick script to delete the existing Qdrant collection and start fresh
with hybrid search support.

Usage:
    python scripts/delete_qdrant_collection.py
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from qdrant_client import QdrantClient

def delete_collection():
    """Delete the ai_dev_agent_codebase collection."""
    
    # Connect to local Qdrant
    qdrant_path = project_root / "context_db" / "qdrant_storage"
    
    if not qdrant_path.exists():
        print("❌ Qdrant storage not found - no collections to delete")
        return
    
    client = QdrantClient(path=str(qdrant_path))
    collection_name = "ai_dev_agent_codebase"
    
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if collection_name in collection_names:
            # Get collection info
            collection_info = client.get_collection(collection_name)
            point_count = collection_info.points_count
            
            print(f"📊 Found collection: {collection_name}")
            print(f"📚 Contains {point_count} document chunks")
            
            # Confirm deletion
            response = input("\n⚠️  Delete this collection? (yes/no): ")
            
            if response.lower() == 'yes':
                client.delete_collection(collection_name)
                print(f"✅ Deleted collection: {collection_name}")
                print(f"\n🎉 Next time you upload documents, a NEW collection will be created with:")
                print(f"   ✨ HYBRID search (BM25 + semantic)")
                print(f"   ✨ Better retrieval accuracy")
                print(f"   ✨ MMR for diverse results")
            else:
                print("❌ Deletion cancelled")
        else:
            print(f"ℹ️  Collection '{collection_name}' not found")
            print(f"Available collections: {collection_names}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    delete_collection()

