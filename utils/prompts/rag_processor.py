"""
RAG Processor - Simple interface for the Streamlit UI
Provides basic RAG document processing capabilities.
"""

import streamlit as st
from pathlib import Path
from typing import List, Dict, Any, Optional
import os

class RAGProcessor:
    """Simple RAG processor for document ingestion and retrieval."""
    
    def __init__(self, docs_dir: str = "data/rag_documents"):
        """Initialize the RAG processor with documents directory."""
        self.docs_dir = Path(docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
    def ingest_document(self, content: str, doc_name: str, metadata: Optional[Dict] = None) -> bool:
        """Ingest a document into the RAG system."""
        try:
            doc_file = self.docs_dir / f"{doc_name}.txt"
            
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Save metadata if provided
            if metadata:
                metadata_file = self.docs_dir / f"{doc_name}_metadata.json"
                import json
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Error ingesting document '{doc_name}': {e}")
            return False
    
    def search_documents(self, query: str, max_results: int = 5) -> List[Dict]:
        """Simple text search in documents."""
        results = []
        
        try:
            doc_files = list(self.docs_dir.glob("*.txt"))
            
            for doc_file in doc_files:
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Simple keyword matching
                    query_lower = query.lower()
                    content_lower = content.lower()
                    
                    if query_lower in content_lower:
                        # Simple relevance scoring
                        relevance = content_lower.count(query_lower) / len(content_lower.split())
                        
                        results.append({
                            'document': doc_file.stem,
                            'content': content[:500] + "..." if len(content) > 500 else content,
                            'relevance': relevance
                        })
                        
                except Exception as e:
                    st.warning(f"Error reading document {doc_file.name}: {e}")
                    continue
            
            # Sort by relevance and return top results
            results.sort(key=lambda x: x['relevance'], reverse=True)
            return results[:max_results]
            
        except Exception as e:
            st.error(f"Error searching documents: {e}")
            return []
    
    def list_documents(self) -> List[str]:
        """List all available documents."""
        try:
            doc_files = list(self.docs_dir.glob("*.txt"))
            return [f.stem for f in doc_files]
        except Exception as e:
            st.error(f"Error listing documents: {e}")
            return []
    
    def delete_document(self, doc_name: str) -> bool:
        """Delete a document from the RAG system."""
        try:
            doc_file = self.docs_dir / f"{doc_name}.txt"
            metadata_file = self.docs_dir / f"{doc_name}_metadata.json"
            
            if doc_file.exists():
                doc_file.unlink()
            
            if metadata_file.exists():
                metadata_file.unlink()
            
            return True
        except Exception as e:
            st.error(f"Error deleting document '{doc_name}': {e}")
            return False
    
    def render_rag_ui(self):
        """Render the RAG processor UI in Streamlit."""
        st.header("📚 RAG Document Processor")
        
        # Tabs for different operations
        tab1, tab2, tab3 = st.tabs(["🔍 Search", "📝 Add Document", "📋 Manage"])
        
        with tab1:
            st.subheader("🔍 Search Documents")
            
            query = st.text_input(
                "Enter your search query:",
                placeholder="What are you looking for?",
                key="rag_search_query"
            )
            
            max_results = st.slider("Max results:", 1, 20, 5)
            
            if st.button("🔍 Search") and query:
                with st.spinner("Searching documents..."):
                    results = self.search_documents(query, max_results)
                
                if results:
                    st.success(f"Found {len(results)} relevant documents:")
                    
                    for i, result in enumerate(results, 1):
                        with st.expander(f"📄 {result['document']} (Relevance: {result['relevance']:.4f})"):
                            st.text(result['content'])
                else:
                    st.info("No relevant documents found.")
        
        with tab2:
            st.subheader("📝 Add New Document")
            
            doc_name = st.text_input(
                "Document name:",
                placeholder="my_document",
                key="rag_doc_name"
            )
            
            doc_content = st.text_area(
                "Document content:",
                height=200,
                placeholder="Enter the document content here...",
                key="rag_doc_content"
            )
            
            # Metadata
            with st.expander("📋 Metadata (Optional)"):
                author = st.text_input("Author:", key="rag_doc_author")
                tags = st.text_input("Tags (comma-separated):", key="rag_doc_tags")
                description = st.text_area("Description:", key="rag_doc_description")
            
            if st.button("💾 Add Document"):
                if doc_name and doc_content:
                    metadata = {}
                    if author:
                        metadata['author'] = author
                    if tags:
                        metadata['tags'] = [tag.strip() for tag in tags.split(',')]
                    if description:
                        metadata['description'] = description
                    
                    if self.ingest_document(doc_content, doc_name, metadata):
                        st.success(f"✅ Added document: {doc_name}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add document")
                else:
                    st.error("Please provide both name and content")
        
        with tab3:
            st.subheader("📋 Manage Documents")
            
            documents = self.list_documents()
            
            if documents:
                st.write(f"**Total documents:** {len(documents)}")
                
                for doc in documents:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"📄 {doc}")
                    
                    with col2:
                        if st.button(f"🗑️ Delete", key=f"delete_{doc}"):
                            if self.delete_document(doc):
                                st.success(f"✅ Deleted: {doc}")
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to delete: {doc}")
            else:
                st.info("No documents found. Add some documents to get started!")


def get_rag_processor():
    """Get RAG processor instance."""
    return RAGProcessor()


def main():
    """Main function for standalone RAG processor."""
    processor = RAGProcessor()
    processor.render_rag_ui()


if __name__ == "__main__":
    main()
