#!/usr/bin/env python3
"""Check Qdrant metadata to debug document selection issues."""

from qdrant_client import QdrantClient
from pathlib import Path

def check_metadata():
    """Check what metadata is stored in Qdrant."""
    
    qdrant_path = Path(__file__).parent.parent / "context_db" / "qdrant_storage"
    client = QdrantClient(path=str(qdrant_path))
    
    print("=" * 80)
    print("QDRANT METADATA CHECK")
    print("=" * 80)
    
    # Get sample points
    points, _ = client.scroll(
        collection_name="ai_dev_agent_codebase",
        limit=10,
        with_payload=True,
        with_vectors=False
    )
    
    print(f"\nTotal points retrieved: {len(points)}")
    print("\n" + "=" * 80)
    
    # Group by source
    sources = {}
    for p in points:
        metadata = p.payload.get('metadata', {})
        source = metadata.get('source', 'NO_SOURCE')
        
        if source not in sources:
            sources[source] = []
        
        sources[source].append({
            'chunk_index': metadata.get('chunk_index', 'unknown'),
            'content_preview': p.payload.get('page_content', '')[:150]
        })
    
    # Display by source
    for idx, (source, chunks) in enumerate(sources.items(), 1):
        print(f"\n{idx}. SOURCE: {source}")
        print(f"   Chunks: {len(chunks)}")
        print(f"   Sample content:")
        for i, chunk in enumerate(chunks[:2], 1):
            print(f"      Chunk {chunk['chunk_index']}: {chunk['content_preview']}...")
        print()
    
    print("=" * 80)
    print("\nKEY QUESTIONS:")
    print("1. Is 'https://rlancemartin.github.io/2025/06/23/context_engineering/' present?")
    print("2. Does it have 'context engineering' in the content?")
    print("3. Are chunk_index values correct?")
    print("=" * 80)

if __name__ == "__main__":
    check_metadata()

