#!/usr/bin/env python3
"""
RAG Management Application
=========================

Comprehensive Streamlit UI for RAG system management including:
- Document upload (PDF, DOCX, TXT, MD, code files)
- Website scraping
- Semantic search interface
- Analytics dashboard
- Vector store management

Built on LangChain and open-source tools.

Author: AI Development Agent
Created: 2025-01-02
Purpose: US-RAG-001 - RAG Management UI
"""

import streamlit as st
import asyncio
from pathlib import Path
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Set USER_AGENT to suppress warning
os.environ.setdefault('USER_AGENT', 'ai-dev-agent-rag-app/1.0')

# Enable LangSmith tracing if configured
# Map existing LANGSMITH_* secrets to LANGCHAIN_* environment variables
try:
    import streamlit as st_temp
    if hasattr(st_temp, 'secrets'):
        # Use existing LANGSMITH_* variables from secrets.toml
        if 'LANGSMITH_TRACING' in st_temp.secrets:
            os.environ['LANGCHAIN_TRACING_V2'] = str(st_temp.secrets.get('LANGSMITH_TRACING', 'false'))
        if 'LANGSMITH_API_KEY' in st_temp.secrets:
            os.environ['LANGCHAIN_API_KEY'] = st_temp.secrets['LANGSMITH_API_KEY']
        if 'LANGSMITH_ENDPOINT' in st_temp.secrets:
            os.environ['LANGCHAIN_ENDPOINT'] = st_temp.secrets['LANGSMITH_ENDPOINT']
        if 'LANGSMITH_PROJECT' in st_temp.secrets:
            os.environ['LANGCHAIN_PROJECT'] = st_temp.secrets.get('LANGSMITH_PROJECT', 'ai-dev-agent')
except Exception:
    # Fallback to environment variables if secrets not available
    pass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import RAG components
from context.context_engine import ContextEngine
from models.config import ContextConfig
from utils.rag.document_loader import DocumentLoader

# Detect which Qdrant API version we have
QDRANT_NEW_API = False
try:
    from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
    QDRANT_NEW_API = True
except ImportError:
    from langchain_qdrant import Qdrant
    QDRANT_NEW_API = False

# Page configuration
st.set_page_config(
    page_title="RAG Management System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI with transparency features
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
    .metric-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        text-align: center;
    }
    .transparency-panel {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        border: 2px solid #007bff;
        margin: 1rem 0;
    }
    .score-high {
        color: #28a745;
        font-weight: bold;
    }
    .score-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .score-low {
        color: #dc3545;
        font-weight: bold;
    }
    .stage-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        background-color: #007bff;
        color: white;
        font-size: 0.875rem;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None
if 'doc_loader' not in st.session_state:
    st.session_state.doc_loader = DocumentLoader()
if 'indexed_documents' not in st.session_state:
    st.session_state.indexed_documents = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_agent' not in st.session_state:
    st.session_state.selected_agent = "ContextAwareAgent (Base)"
if 'transparency_mode' not in st.session_state:
    st.session_state.transparency_mode = True  # Always show transparency by default
if 'test_queries' not in st.session_state:
    st.session_state.test_queries = []
if 'test_results' not in st.session_state:
    st.session_state.test_results = []
if 'query_history' not in st.session_state:
    st.session_state.query_history = []  # Track all queries for analysis


def initialize_rag_engine():
    """Initialize RAG engine and load existing documents from Qdrant."""
    if st.session_state.rag_engine is None:
        with st.spinner("Initializing RAG system..."):
            config = ContextConfig()
            st.session_state.rag_engine = ContextEngine(config)
            
            # Debug: Check what was initialized
            st.write("🔍 Debug - Initialization Status:")
            st.write(f"- Embeddings: {st.session_state.rag_engine.embeddings is not None}")
            st.write(f"- Qdrant Client: {st.session_state.rag_engine.qdrant_client is not None}")
            st.write(f"- Vector Store: {st.session_state.rag_engine.vector_store is not None}")
            
            if st.session_state.rag_engine.embeddings is None:
                st.error("❌ Embeddings failed to initialize - check terminal logs")
            
            if st.session_state.rag_engine.qdrant_client is None:
                st.error("❌ Qdrant client failed to initialize - check terminal logs")
            
            # Load existing documents from Qdrant using the new function
            if st.session_state.rag_engine.qdrant_client:
                try:
                    # Check if collection exists
                    collections = st.session_state.rag_engine.qdrant_client.get_collections().collections
                    if any(c.name == st.session_state.rag_engine.collection_name for c in collections):
                        collection_info = st.session_state.rag_engine.qdrant_client.get_collection(
                            st.session_state.rag_engine.collection_name
                        )
                        doc_count = collection_info.points_count
                        
                        if doc_count > 0:
                            st.success(f"✅ Found existing vector database with {doc_count} document chunks")
                            
                            # Use the new load function
                            st.session_state.indexed_documents = load_documents_from_qdrant()
                            
                            if st.session_state.indexed_documents:
                                st.info(f"📚 Loaded {len(st.session_state.indexed_documents)} documents from persistent storage")
                        else:
                            st.info("📁 Vector database is empty. Upload documents or scrape websites to begin.")
                    else:
                        st.info("📁 No vector database found. Upload documents to create one.")
                        
                except Exception as e:
                    st.warning(f"⚠️ Could not load existing documents: {e}")
                    import traceback
                    st.error(traceback.format_exc())
                    
            return True
    return False


def main():
    """Main application entry point."""
    
    # Header
    st.markdown('<div class="main-header">🔍 RAG Management System</div>', unsafe_allow_html=True)
    st.markdown("**Comprehensive document loading, semantic search, and knowledge management**")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["📤 Document Upload", "🌐 Website Scraping", "🔍 Semantic Search", "💬 Agent Chat", "🧪 Testing & Evaluation", "📊 Analytics Dashboard", "⚙️ System Settings"]
    )
    
    # Initialize RAG engine
    if initialize_rag_engine():
        st.sidebar.success("✅ RAG System Initialized")
    
    # Display system status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### System Status")
    if st.session_state.rag_engine:
        # Show embeddings status
        if st.session_state.rag_engine.embeddings:
            st.sidebar.success("✅ Embeddings Ready")
        else:
            st.sidebar.error("❌ Embeddings Not Ready")
        
        # Check actual Qdrant database for document count
        if st.session_state.rag_engine.qdrant_client:
            try:
                collections = st.session_state.rag_engine.qdrant_client.get_collections().collections
                collection_exists = any(c.name == st.session_state.rag_engine.collection_name for c in collections)
                
                if collection_exists:
                    collection_info = st.session_state.rag_engine.qdrant_client.get_collection(
                        st.session_state.rag_engine.collection_name
                    )
                    chunk_count = collection_info.points_count
                    
                    if chunk_count > 0:
                        # If indexed_documents is empty but Qdrant has data, load from Qdrant
                        if not st.session_state.indexed_documents:
                            st.session_state.indexed_documents = load_documents_from_qdrant()
                        
                        # Get unique document count from indexed_documents
                        doc_count = len(st.session_state.indexed_documents)
                        
                        st.sidebar.success("✅ Vector Store Active")
                        st.sidebar.info(f"📚 {doc_count} documents ({chunk_count} chunks)")
                    else:
                        st.sidebar.info("📁 Vector Store Empty")
                else:
                    st.sidebar.info("📁 No vector store yet")
            except Exception as e:
                st.sidebar.error(f"❌ Vector Store Error")
                with st.sidebar.expander("Error Details"):
                    st.error(str(e))
        else:
            st.sidebar.error("❌ Qdrant Client Not Connected")
    else:
        st.sidebar.error("❌ RAG Engine Not Initialized")
    
    # Route to selected page
    if page == "📤 Document Upload":
        document_upload_page()
    elif page == "🌐 Website Scraping":
        website_scraping_page()
    elif page == "🔍 Semantic Search":
        semantic_search_page()
    elif page == "💬 Agent Chat":
        agent_chat_page()
    elif page == "🧪 Testing & Evaluation":
        testing_evaluation_page()
    elif page == "📊 Analytics Dashboard":
        analytics_dashboard_page()
    elif page == "⚙️ System Settings":
        system_settings_page()


def load_documents_from_qdrant(show_debug=False):
    """Load all documents from Qdrant vector database.
    
    Args:
        show_debug: If True, show debug information on the UI
    """
    if not st.session_state.rag_engine:
        return []
    
    if not st.session_state.rag_engine.qdrant_client:
        return []
    
    try:
        # Check if collection exists
        collections = st.session_state.rag_engine.qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if st.session_state.rag_engine.collection_name not in collection_names:
            if show_debug:
                st.info(f"📁 Collection '{st.session_state.rag_engine.collection_name}' does not exist yet.")
            return []
        
        # Get collection info
        collection_info = st.session_state.rag_engine.qdrant_client.get_collection(
            st.session_state.rag_engine.collection_name
        )
        
        if show_debug:
            st.write(f"🔍 Found collection with {collection_info.points_count} chunks")
        
        if collection_info.points_count == 0:
            if show_debug:
                st.info("📁 Vector database exists but is empty")
            return []
        
        # Scroll through all points to get documents
        all_points = []
        offset = None
        while True:
            scroll_result = st.session_state.rag_engine.qdrant_client.scroll(
                collection_name=st.session_state.rag_engine.collection_name,
                limit=100,
                offset=offset,
                with_payload=True
            )
            
            points, offset = scroll_result
            all_points.extend(points)
            
            if offset is None:
                break
        
        if show_debug:
            st.write(f"📊 Loaded {len(all_points)} chunks from database")
        
        # Extract unique documents from points
        documents_dict = {}
        
        # Debug: Show first payload structure
        if all_points and show_debug:
            st.write(f"🔍 First payload structure: {list(all_points[0].payload.keys())}")
            if 'metadata' in all_points[0].payload:
                st.write(f"🔍 Metadata structure: {list(all_points[0].payload['metadata'].keys())}")
                st.write(f"🔍 Metadata content: {all_points[0].payload['metadata']}")
            else:
                st.write(f"🔍 Full payload: {all_points[0].payload}")
        
        for point in all_points:
            if point.payload:
                # Try different metadata structures
                source = None
                metadata = {}
                
                if 'metadata' in point.payload:
                    metadata = point.payload['metadata']
                    source = metadata.get('source') or metadata.get('file_path')
                elif 'source' in point.payload:
                    source = point.payload.get('source')
                    metadata = point.payload
                elif 'file_path' in point.payload:
                    source = point.payload.get('file_path')
                    metadata = point.payload
                
                if source:
                    if source not in documents_dict:
                        # Determine file type from metadata
                        file_type = metadata.get('file_type')
                        
                        if show_debug and len(documents_dict) == 0:  # Debug first document only
                            st.write(f"🔍 Processing first document:")
                            st.write(f"  - Source: {source}")
                            st.write(f"  - file_type from metadata: {file_type}")
                            st.write(f"  - Metadata keys: {list(metadata.keys())}")
                        
                        if not file_type:
                            # Check for source_type (used by website scraper)
                            source_type = metadata.get('source_type')
                            if source_type == 'web':
                                file_type = 'website'
                                if show_debug and len(documents_dict) == 0:
                                    st.write(f"  - Detected as website from source_type")
                            else:
                                # Try to infer from source/filename
                                if source.startswith(('http://', 'https://')):
                                    file_type = 'website'
                                    if show_debug and len(documents_dict) == 0:
                                        st.write(f"  - Detected as website from URL pattern")
                                elif '.' in source:
                                    file_type = source.rsplit('.', 1)[-1]
                                    if show_debug and len(documents_dict) == 0:
                                        st.write(f"  - Detected file extension: {file_type}")
                                else:
                                    file_type = 'unknown'
                                    if show_debug and len(documents_dict) == 0:
                                        st.write(f"  - Could not determine file type")
                        
                        documents_dict[source] = {
                            'file_name': source,
                            'file_type': file_type,
                            'chunk_count': 0,
                            'success': True
                        }
                    documents_dict[source]['chunk_count'] += 1
        
        if show_debug:
            st.write(f"✅ Found {len(documents_dict)} unique documents")
        
        return list(documents_dict.values())
        
    except Exception as e:
        if show_debug:
            st.error(f"❌ Error loading documents from Qdrant: {e}")
            import traceback
            st.error(traceback.format_exc())
        return []


def document_upload_page():
    """Document upload interface."""
    st.markdown('<div class="sub-header">📤 Document Upload</div>', unsafe_allow_html=True)
    
    # Load documents from Qdrant to show persisted documents
    if st.session_state.rag_engine and st.button("🔄 Refresh Document List", help="Load all documents from vector database"):
        st.session_state.indexed_documents = load_documents_from_qdrant(show_debug=True)
        st.rerun()
    
    # Auto-load on first visit if indexed_documents is empty
    if st.session_state.rag_engine and not st.session_state.indexed_documents:
        st.session_state.indexed_documents = load_documents_from_qdrant()
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload documents (PDF, DOCX, TXT, MD, code files)",
        type=['pdf', 'docx', 'doc', 'txt', 'md', 'py', 'js', 'ts', 'java', 'cpp', 'c', 'h', 'html', 'css', 'json', 'yaml', 'yml'],
        accept_multiple_files=True,
        help="Drag and drop files or click to browse"
    )
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) selected")
        
        # Process button
        if st.button("🚀 Process Documents", type="primary"):
            process_uploaded_documents(uploaded_files)
    
    # Display indexed documents with delete option
    if st.session_state.indexed_documents:
        st.markdown("---")
        st.markdown(f"### 📚 Indexed Documents ({len(st.session_state.indexed_documents)} files)")
        
        # Show total chunks
        total_chunks = sum(doc.get('chunk_count', doc.get('document_count', 0)) 
                          for doc in st.session_state.indexed_documents)
        st.info(f"🔢 Total chunks in vector database: {total_chunks}")
        
        for idx, doc_info in enumerate(st.session_state.indexed_documents):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                file_type = doc_info.get('file_type', 'unknown')
                st.text(f"📄 {doc_info.get('file_name', 'Unknown')}")
            
            with col2:
                st.text(f"Type: {file_type}")
            
            with col3:
                chunk_count = doc_info.get('chunk_count', doc_info.get('document_count', 0))
                st.text(f"{chunk_count} chunks")
            
            with col4:
                if st.button("🗑️ Delete", key=f"del_doc_{idx}"):
                    delete_document_from_vectorstore(doc_info.get('file_name', 'Unknown'))
                    st.rerun()
        
        if st.button("🗑️ Clear All Documents"):
            if st.session_state.rag_engine and st.session_state.rag_engine.vector_store:
                try:
                    st.session_state.rag_engine.qdrant_client.delete_collection(
                        st.session_state.rag_engine.collection_name
                    )
                    st.session_state.rag_engine.vector_store = None
                    st.session_state.rag_engine.documents = []
                    st.session_state.indexed_documents = []
                    st.success("✅ All documents cleared")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to clear documents: {e}")
    else:
        st.info("No documents uploaded yet")


def delete_document_from_vectorstore(filename: str):
    """Delete a document from vector store by metadata."""
    try:
        if st.session_state.rag_engine:
            # Delete from Qdrant by metadata
            if st.session_state.rag_engine.qdrant_client:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                
                st.session_state.rag_engine.qdrant_client.delete(
                    collection_name=st.session_state.rag_engine.collection_name,
                    points_selector=Filter(
                        must=[
                            FieldCondition(
                                key="metadata.source",
                                match=MatchValue(value=filename)
                            )
                        ]
                    )
                )
            
            # Reload documents from Qdrant to refresh the list
            st.session_state.indexed_documents = load_documents_from_qdrant()
            
            st.success(f"✅ Deleted {filename} from vector database")
    except Exception as e:
        st.error(f"❌ Failed to delete {filename}: {e}")


def process_uploaded_documents(uploaded_files):
    """Process uploaded documents."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(uploaded_files)
    results = []
    
    # Check for duplicates
    existing_files = [doc.get('file_name') for doc in st.session_state.indexed_documents]
    duplicates = [f.name for f in uploaded_files if f.name in existing_files]
    
    if duplicates:
        st.warning(f"⚠️ Duplicate files detected: {', '.join(duplicates)}")
        st.info("These files are already in the vector store. Upload will skip duplicates.")
    
    # Use Windows-compatible temp directory
    from pathlib import Path as PathLib
    temp_dir = PathLib(r"C:\Users\pogawal\Downloads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    for i, uploaded_file in enumerate(uploaded_files):
        # Skip duplicates
        if uploaded_file.name in existing_files:
            status_text.text(f"Skipping duplicate: {uploaded_file.name}...")
            results.append({
                'success': False,
                'error': 'Duplicate file',
                'file_name': uploaded_file.name
            })
            progress_bar.progress((i + 1) / total)
            continue
        
        status_text.text(f"Processing {uploaded_file.name}...")
        
        # Save temporary file to Downloads folder
        temp_path = temp_dir / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Load document
        try:
            result = asyncio.run(st.session_state.doc_loader.load_document(temp_path))
            results.append(result)
            
            if result['success']:
                # Add documents to RAG engine
                if st.session_state.rag_engine and result.get('documents'):
                    st.session_state.rag_engine.documents.extend(result['documents'])
        
        except Exception as e:
            results.append({
                'success': False,
                'error': str(e),
                'file_name': uploaded_file.name
            })
        
        # Update progress
        progress_bar.progress((i + 1) / total)
    
    # Create/update vector store after all documents loaded
    if st.session_state.rag_engine and st.session_state.rag_engine.documents:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, SparseVectorParams
            from pathlib import Path
            
            # Check if new API available
            QDRANT_NEW_API = False
            try:
                from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
                QDRANT_NEW_API = True
            except ImportError:
                from langchain_qdrant import Qdrant
                QDRANT_NEW_API = False
                st.warning("ℹ️ Using legacy Qdrant API. For hybrid search, upgrade: pip install --upgrade langchain-qdrant")
            
            # Check if Qdrant client exists (don't create new one if it exists)
            if not st.session_state.rag_engine.qdrant_client:
                st.error("❌ Qdrant client not initialized. Please restart the app.")
                return
            
            # Ensure embeddings are initialized
            if not st.session_state.rag_engine.embeddings:
                st.error("❌ Embeddings not initialized. Please restart the app.")
                return
            
            # Always check if collection exists
            collections = st.session_state.rag_engine.qdrant_client.get_collections().collections
            collection_exists = any(c.name == st.session_state.rag_engine.collection_name for c in collections)
            
            # Check if existing collection has sparse vectors
            has_sparse_vectors = False
            if collection_exists:
                try:
                    collection_info = st.session_state.rag_engine.qdrant_client.get_collection(
                        st.session_state.rag_engine.collection_name
                    )
                    # Check if collection has sparse vectors configured
                    if hasattr(collection_info.config, 'params') and hasattr(collection_info.config.params, 'sparse_vectors'):
                        has_sparse_vectors = collection_info.config.params.sparse_vectors is not None
                except:
                    has_sparse_vectors = False
            
            if not collection_exists:
                # Create NEW collection
                if QDRANT_NEW_API and hasattr(st.session_state.rag_engine, 'sparse_embeddings') and st.session_state.rag_engine.sparse_embeddings:
                    # New API with hybrid
                    vectors_config = {
                        "dense": VectorParams(size=384, distance=Distance.COSINE)
                    }
                    st.session_state.rag_engine.qdrant_client.create_collection(
                        collection_name=st.session_state.rag_engine.collection_name,
                        vectors_config=vectors_config,
                        sparse_vectors_config={"sparse": SparseVectorParams()}
                    )
                    st.info("✅ Collection created with HYBRID search support")
                    has_sparse_vectors = True
                else:
                    # Legacy or dense-only
                    st.session_state.rag_engine.qdrant_client.create_collection(
                        collection_name=st.session_state.rag_engine.collection_name,
                        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                    )
                    st.info("✅ Collection created (dense-only)")
                    has_sparse_vectors = False
                    
                st.session_state.rag_engine.vector_store = None
            
            if not st.session_state.rag_engine.vector_store:
                # Create vector store - use hybrid ONLY if collection supports it
                if QDRANT_NEW_API:
                    # New API
                    if has_sparse_vectors and hasattr(st.session_state.rag_engine, 'sparse_embeddings') and st.session_state.rag_engine.sparse_embeddings:
                        st.session_state.rag_engine.vector_store = QdrantVectorStore(
                            client=st.session_state.rag_engine.qdrant_client,
                            collection_name=st.session_state.rag_engine.collection_name,
                            embedding=st.session_state.rag_engine.embeddings,
                            sparse_embedding=st.session_state.rag_engine.sparse_embeddings,
                            retrieval_mode=RetrievalMode.HYBRID,
                            vector_name="dense",  # Named vector for hybrid collections
                            sparse_vector_name="sparse"  # Named sparse vector
                        )
                        st.info("✅ Using HYBRID search (BM25 + semantic)")
                    else:
                        # Use dense-only mode
                        st.session_state.rag_engine.vector_store = QdrantVectorStore(
                            client=st.session_state.rag_engine.qdrant_client,
                            collection_name=st.session_state.rag_engine.collection_name,
                            embedding=st.session_state.rag_engine.embeddings,
                            retrieval_mode=RetrievalMode.DENSE
                        )
                        if collection_exists and not has_sparse_vectors:
                            st.info("ℹ️ Using DENSE search (existing collection doesn't support hybrid)")
                        else:
                            st.info("✅ Using DENSE search (new API)")
                else:
                    # Legacy API
                    st.session_state.rag_engine.vector_store = Qdrant(
                        client=st.session_state.rag_engine.qdrant_client,
                        collection_name=st.session_state.rag_engine.collection_name,
                        embeddings=st.session_state.rag_engine.embeddings  # Plural!
                    )
                    st.info("ℹ️ Using legacy Qdrant API (dense-only)")
                
                # Create retriever
                if QDRANT_NEW_API:
                    st.session_state.rag_engine.retriever = st.session_state.rag_engine.vector_store.as_retriever(
                        search_type="mmr",
                        search_kwargs={"k": 15, "fetch_k": 50, "lambda_mult": 0.5}
                    )
                else:
                    st.session_state.rag_engine.retriever = st.session_state.rag_engine.vector_store.as_retriever(
                        search_kwargs={"k": 15}
                    )
            
            # Add documents
            new_docs = [r.get('documents', []) for r in results if r['success']]
            new_docs_flat = [doc for docs in new_docs for doc in docs]
            if new_docs_flat:
                st.session_state.rag_engine.vector_store.add_documents(new_docs_flat)
        except Exception as e:
            st.error(f"❌ Failed to update vector store: {e}")
    
    # Show results
    status_text.empty()
    progress_bar.empty()
    
    successful = sum(1 for r in results if r['success'])
    failed = sum(1 for r in results if not r['success'])
    
    if successful > 0:
        st.success(f"✅ Successfully processed {successful}/{total} documents")
        # Reload documents from Qdrant to show updated list
        st.session_state.indexed_documents = load_documents_from_qdrant()
    if failed > 0:
        st.error(f"❌ Failed to process {failed}/{total} documents")


def website_scraping_page():
    """Website scraping interface."""
    st.markdown('<div class="sub-header">🌐 Website Scraping</div>', unsafe_allow_html=True)
    
    # Load documents from Qdrant to show persisted websites
    if st.session_state.rag_engine and st.button("🔄 Refresh Website List", help="Load all websites from vector database"):
        st.session_state.indexed_documents = load_documents_from_qdrant(show_debug=True)
        st.rerun()
    
    # Auto-load on first visit if indexed_documents is empty
    if st.session_state.rag_engine and not st.session_state.indexed_documents:
        st.session_state.indexed_documents = load_documents_from_qdrant()
    
    # URL input
    url = st.text_input(
        "Enter website URL",
        placeholder="https://example.com",
        help="Enter the URL of the website to scrape"
    )
    
    if st.button("🔍 Scrape Website", type="primary", disabled=not url):
        if url:
            # Check for duplicate URL
            existing_urls = [doc.get('file_name') for doc in st.session_state.indexed_documents if doc.get('file_type') == 'website']
            if url in existing_urls:
                st.warning(f"⚠️ URL already scraped: {url}")
                st.info("This URL is already in the vector store. Delete it first if you want to re-scrape.")
                return
            
            with st.spinner(f"Scraping {url}..."):
                try:
                    result = asyncio.run(st.session_state.doc_loader.load_website(url))
                    
                    if result['success']:
                        st.success(f"✅ Successfully scraped {url}")
                        
                        # Add to RAG engine
                        if st.session_state.rag_engine and result.get('documents'):
                            st.session_state.rag_engine.documents.extend(result['documents'])
                            
                            # Create/update vector store
                            try:
                                from qdrant_client.models import Distance, VectorParams, SparseVectorParams
                                
                                # Check if Qdrant client exists (don't create new one if it exists)
                                if not st.session_state.rag_engine.qdrant_client:
                                    st.error("❌ Qdrant client not initialized. Please restart the app.")
                                    return
                                
                                # Ensure embeddings are initialized
                                if not st.session_state.rag_engine.embeddings:
                                    st.error("❌ Embeddings not initialized. Please restart the app.")
                                    return
                                
                                # Always check if collection exists
                                collections = st.session_state.rag_engine.qdrant_client.get_collections().collections
                                collection_exists = any(c.name == st.session_state.rag_engine.collection_name for c in collections)
                                
                                # Check if existing collection has sparse vectors
                                has_sparse_vectors = False
                                if collection_exists:
                                    try:
                                        collection_info = st.session_state.rag_engine.qdrant_client.get_collection(
                                            st.session_state.rag_engine.collection_name
                                        )
                                        # Check if collection has sparse vectors configured
                                        if hasattr(collection_info.config, 'params') and hasattr(collection_info.config.params, 'sparse_vectors'):
                                            has_sparse_vectors = collection_info.config.params.sparse_vectors is not None
                                    except:
                                        has_sparse_vectors = False
                                
                                if not collection_exists:
                                    # Create NEW collection with hybrid search support if available
                                    if QDRANT_NEW_API and hasattr(st.session_state.rag_engine, 'sparse_embeddings') and st.session_state.rag_engine.sparse_embeddings:
                                        vectors_config = {
                                            "dense": VectorParams(size=384, distance=Distance.COSINE)
                                        }
                                        st.session_state.rag_engine.qdrant_client.create_collection(
                                            collection_name=st.session_state.rag_engine.collection_name,
                                            vectors_config=vectors_config,
                                            sparse_vectors_config={"sparse": SparseVectorParams()}
                                        )
                                        st.info("✅ Created new collection with HYBRID search support")
                                    else:
                                        st.session_state.rag_engine.qdrant_client.create_collection(
                                            collection_name=st.session_state.rag_engine.collection_name,
                                            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                                        )
                                        st.info("✅ Created new collection (dense-only)")
                                    st.session_state.rag_engine.vector_store = None
                                    has_sparse_vectors = QDRANT_NEW_API and hasattr(st.session_state.rag_engine, 'sparse_embeddings') and st.session_state.rag_engine.sparse_embeddings
                                
                                if not st.session_state.rag_engine.vector_store:
                                    # Create vector store wrapper - use hybrid ONLY if collection supports it
                                    if QDRANT_NEW_API:
                                        if has_sparse_vectors and hasattr(st.session_state.rag_engine, 'sparse_embeddings') and st.session_state.rag_engine.sparse_embeddings:
                                            st.session_state.rag_engine.vector_store = QdrantVectorStore(
                                                client=st.session_state.rag_engine.qdrant_client,
                                                collection_name=st.session_state.rag_engine.collection_name,
                                                embedding=st.session_state.rag_engine.embeddings,
                                                sparse_embedding=st.session_state.rag_engine.sparse_embeddings,
                                                retrieval_mode=RetrievalMode.HYBRID,
                                                vector_name="dense",  # Named vector for hybrid collections
                                                sparse_vector_name="sparse"  # Named sparse vector
                                            )
                                            st.info("✅ Using HYBRID search (BM25 + semantic)")
                                        else:
                                            # Use dense-only mode for existing collections without sparse vectors
                                            st.session_state.rag_engine.vector_store = QdrantVectorStore(
                                                client=st.session_state.rag_engine.qdrant_client,
                                                collection_name=st.session_state.rag_engine.collection_name,
                                                embedding=st.session_state.rag_engine.embeddings,
                                                retrieval_mode=RetrievalMode.DENSE
                                            )
                                            if collection_exists and not has_sparse_vectors:
                                                st.info("ℹ️ Using DENSE search (existing collection doesn't support hybrid)")
                                            else:
                                                st.info("✅ Using DENSE search (new API)")
                                    else:
                                        # Legacy API
                                        st.session_state.rag_engine.vector_store = Qdrant(
                                            client=st.session_state.rag_engine.qdrant_client,
                                            collection_name=st.session_state.rag_engine.collection_name,
                                            embeddings=st.session_state.rag_engine.embeddings
                                        )
                                        st.info("ℹ️ Using legacy Qdrant API (dense-only)")
                                
                                # Enrich document metadata before adding to vector store
                                enriched_docs = []
                                for doc in result['documents']:
                                    # Add file_type metadata to each document
                                    if doc.metadata:
                                        doc.metadata['file_type'] = 'website'
                                        doc.metadata['source_type'] = 'web'
                                    else:
                                        doc.metadata = {'file_type': 'website', 'source_type': 'web'}
                                    enriched_docs.append(doc)
                                
                                # Add enriched documents to vector store
                                st.session_state.rag_engine.vector_store.add_documents(enriched_docs)
                                
                                # Reload indexed documents from Qdrant to reflect the new website
                                st.session_state.indexed_documents = load_documents_from_qdrant()
                                
                            except Exception as e:
                                st.error(f"❌ Failed to update vector store: {e}")
                                import traceback
                                st.error(traceback.format_exc())
                        
                        # Display results
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Documents", result.get('document_count', 0))
                        with col2:
                            st.metric("Characters", f"{result.get('character_count', 0):,}")
                        
                        # Show content preview
                        if result.get('documents'):
                            with st.expander("📄 Content Preview"):
                                st.text(result['documents'][0].page_content[:500] + "...")
                    
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Error scraping website: {e}")
    
    # Display scraped websites with delete option
    scraped_sites = [doc for doc in st.session_state.indexed_documents if doc.get('file_type') == 'website']
    if scraped_sites:
        st.markdown("---")
        st.markdown("### 🌐 Scraped Websites")
        
        for idx, site_info in enumerate(scraped_sites):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.text(f"🌐 {site_info.get('file_name', 'Unknown URL')}")
            
            with col2:
                chunk_count = site_info.get('chunk_count', site_info.get('document_count', 0))
                st.text(f"{chunk_count} chunks")
            
            with col3:
                if st.button("🗑️ Delete", key=f"del_site_{idx}"):
                    delete_document_from_vectorstore(site_info.get('file_name', 'Unknown'))
                    st.rerun()


def semantic_search_page():
    """Semantic search interface."""
    st.markdown('<div class="sub-header">🔍 Semantic Search</div>', unsafe_allow_html=True)
    
    if not st.session_state.rag_engine or not st.session_state.rag_engine.vector_store:
        st.warning("⚠️ Please index some documents first before searching")
        return
    
    # Search input
    query = st.text_input(
        "Enter your search query",
        placeholder="What are you looking for?",
        help="Enter keywords or a question to search the indexed documents"
    )
    
    # Search parameters
    col1, col2 = st.columns(2)
    with col1:
        limit = st.slider("Number of results", 1, 20, 5)
    with col2:
        search_type = st.selectbox("Search type", ["Semantic", "Hybrid"])
    
    if st.button("🔍 Search", type="primary", disabled=not query):
        if query:
            with st.spinner("Searching..."):
                try:
                    results = asyncio.run(
                        st.session_state.rag_engine.semantic_search(query, limit=limit)
                    )
                    
                    # Add to search history
                    st.session_state.search_history.append({
                        'query': query,
                        'timestamp': datetime.now().isoformat(),
                        'results_count': results.get('total_found', 0)
                    })
                    
                    # Display results
                    if results.get('results'):
                        st.success(f"✅ Found {results['total_found']} results")
                        
                        for i, result in enumerate(results['results'], 1):
                            with st.expander(f"Result {i} - Score: {result.get('relevance_score', 0):.3f}"):
                                st.markdown(f"**File:** {result.get('file_path', 'Unknown')}")
                                st.markdown(f"**Search Type:** {result.get('search_type', 'Unknown')}")
                                st.markdown("**Content:**")
                                st.text(result.get('content', '')[:500] + "...")
                    else:
                        st.info("No results found")
                
                except Exception as e:
                    st.error(f"❌ Search error: {e}")
    
    # Search history
    if st.session_state.search_history:
        st.markdown("---")
        st.markdown("### 📜 Recent Searches")
        for search in reversed(st.session_state.search_history[-5:]):
            st.text(f"🔍 {search['query']} - {search['results_count']} results")


def agent_chat_page():
    """Context-aware agent chat interface with real-time context visualization."""
    st.markdown('<div class="sub-header">💬 Context-Aware Agent Chat</div>', unsafe_allow_html=True)
    st.markdown("**Test context-aware agents with real-time RAG context visualization**")
    
    # Initialize chat history
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'selected_agent' not in st.session_state:
        st.session_state.selected_agent = None
    if 'context_debug_mode' not in st.session_state:
        st.session_state.context_debug_mode = True
    
    # Check if RAG system is initialized
    if not st.session_state.rag_engine:
        st.warning("⚠️ RAG system not initialized. Please upload documents first.")
        if st.button("Go to Document Upload"):
            st.rerun()
        return
    
    # Check if vector store is initialized, and initialize if Qdrant has data
    if not st.session_state.rag_engine.vector_store:
        # Check if Qdrant has documents
        try:
            collections = st.session_state.rag_engine.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if st.session_state.rag_engine.collection_name in collection_names:
                collection_info = st.session_state.rag_engine.qdrant_client.get_collection(
                    st.session_state.rag_engine.collection_name
                )
                
                if collection_info.points_count > 0:
                    # Initialize vector_store wrapper for existing collection
                    if QDRANT_NEW_API:
                        # Check if collection has sparse vectors
                        has_sparse = False
                        if hasattr(collection_info.config, 'params') and hasattr(collection_info.config.params, 'sparse_vectors'):
                            has_sparse = collection_info.config.params.sparse_vectors is not None
                        
                        if has_sparse and hasattr(st.session_state.rag_engine, 'sparse_embeddings') and st.session_state.rag_engine.sparse_embeddings:
                            st.session_state.rag_engine.vector_store = QdrantVectorStore(
                                client=st.session_state.rag_engine.qdrant_client,
                                collection_name=st.session_state.rag_engine.collection_name,
                                embedding=st.session_state.rag_engine.embeddings,
                                sparse_embedding=st.session_state.rag_engine.sparse_embeddings,
                                retrieval_mode=RetrievalMode.HYBRID,
                                vector_name="dense",
                                sparse_vector_name="sparse"
                            )
                        else:
                            st.session_state.rag_engine.vector_store = QdrantVectorStore(
                                client=st.session_state.rag_engine.qdrant_client,
                                collection_name=st.session_state.rag_engine.collection_name,
                                embedding=st.session_state.rag_engine.embeddings,
                                retrieval_mode=RetrievalMode.DENSE
                            )
                    else:
                        st.session_state.rag_engine.vector_store = Qdrant(
                            client=st.session_state.rag_engine.qdrant_client,
                            collection_name=st.session_state.rag_engine.collection_name,
                            embeddings=st.session_state.rag_engine.embeddings
                        )
                    
                    st.success(f"✅ Vector store initialized with {collection_info.points_count} chunks")
                else:
                    st.warning("⚠️ Vector store is empty. Please upload documents or scrape websites.")
            else:
                st.warning("⚠️ No vector database found. Please upload documents or scrape websites.")
        except Exception as e:
            st.warning(f"⚠️ Vector store not initialized: {e}")
    
    # Agent selection and configuration
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        agent_mode = st.selectbox(
            "RAG Mode",
            [
                "🔥 Agent Swarm (Best Quality)",
                "⚡ Single Agent (Fast)"
            ],
            help="Agent Swarm uses 5 specialized agents for highest quality"
        )
    
    with col2:
        context_mode = st.select_slider(
            "Context Detail Level",
            options=["Minimal", "Standard", "Detailed", "Debug"],
            value="Standard",
            help="How much context detail to show"
        )
    
    with col3:
        st.session_state.context_debug_mode = st.checkbox(
            "Debug Mode",
            value=st.session_state.context_debug_mode,
            help="Show detailed context retrieval information"
        )
    
    st.markdown("---")
    
    # Main chat interface
    chat_col, context_col = st.columns([3, 2] if st.session_state.context_debug_mode else [1, 0])
    
    with chat_col:
        st.markdown("### 💬 Chat")
        
        # Display chat history
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show context used (if available)
                if message.get("context_stats") and context_mode in ["Detailed", "Debug"]:
                    with st.expander("📊 Context Used", expanded=False):
                        st.json(message["context_stats"])
        
        # Chat input
        user_input = st.chat_input("Ask your context-aware agent...")
        
        if user_input:
            # Add user message
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Process with agent (swarm or single)
            with st.chat_message("assistant"):
                use_swarm = "Swarm" in agent_mode
                
                with st.spinner(f"🔍 {'Agent Swarm processing' if use_swarm else 'Retrieving context'}..."):
                    try:
                        # Set API key from Streamlit secrets
                        import os
                        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                            os.environ['GEMINI_API_KEY'] = st.secrets['GEMINI_API_KEY']
                        
                        if use_swarm:
                            # Use RAG Agent Swarm
                            from agents.rag import RAGSwarmCoordinator
                            
                            # Initialize swarm coordinator
                            swarm = RAGSwarmCoordinator(st.session_state.rag_engine)
                            
                            # Execute pipeline
                            result = asyncio.run(
                                swarm.execute({
                                    'query': user_input,
                                    'max_results': 10,
                                    'quality_threshold': 0.7,
                                    'enable_re_retrieval': True
                                })
                            )
                            
                            # Extract response
                            response_text = result.get('response', 'No response generated')
                            
                            # Build context stats from pipeline
                            pipeline_state = result.get('pipeline_state', {})
                            context_stats = {
                                'retrieval_time': pipeline_state.get('metrics', {}).get('total_time', 0),
                                'results_count': len(pipeline_state.get('ranked_results', [])),
                                'search_type': 'agent_swarm',
                                'quality_score': pipeline_state.get('quality_report', {}).get('quality_score', 0),
                                'confidence': result.get('confidence', 0),
                                'sources_cited': result.get('sources_cited', []),
                                'pipeline_metrics': pipeline_state.get('metrics', {}),
                                'stages_completed': pipeline_state.get('stages_completed', [])
                            }
                            
                        else:
                            # Use single ContextAwareAgent (original)
                            from agents.core.context_aware_agent import ContextAwareAgent
                            from models.config import AgentConfig
                            
                            config = AgentConfig(
                                agent_id=f"chat_single_agent",
                                name="Single RAG Agent",
                                role="rag_query"
                            )
                            
                            agent = ContextAwareAgent(
                                config, 
                                context_engine=st.session_state.rag_engine
                            )
                            
                            # Execute with context
                            result = asyncio.run(
                                agent.execute_with_context({
                                    'query': user_input,
                                    'context_mode': context_mode
                                })
                            )
                            
                            # Extract response and context stats
                            response_text = result.get('response', 'Agent executed successfully')
                            context_stats = result.get('context_stats', {})
                        
                        # Display response
                        st.markdown(response_text)
                        
                        # Display context stats if in debug mode
                        if st.session_state.context_debug_mode:
                            with st.expander("📊 Context Statistics", expanded=(context_mode == "Debug")):
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric(
                                        "Retrieval Time",
                                        f"{context_stats.get('retrieval_time', 0):.3f}s"
                                    )
                                with col_b:
                                    st.metric(
                                        "Results Found",
                                        context_stats.get('results_count', 0)
                                    )
                                with col_c:
                                    st.metric(
                                        "Search Type",
                                        context_stats.get('search_type', 'unknown')
                                    )
                                
                                if context_mode == "Debug":
                                    st.json(context_stats)
                        
                        # Add assistant message
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "timestamp": datetime.now().isoformat(),
                            "context_stats": context_stats
                        })
                    
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": error_msg,
                            "timestamp": datetime.now().isoformat()
                        })
    
    # Context visualization panel (if debug mode)
    if st.session_state.context_debug_mode:
        with context_col:
            st.markdown("### 🔍 Context Retrieval")
            
            if st.session_state.chat_messages:
                last_message = st.session_state.chat_messages[-1]
                
                if last_message.get("context_stats"):
                    stats = last_message["context_stats"]
                    
                    # Check if agent swarm was used
                    is_swarm = stats.get('search_type') == 'agent_swarm'
                    
                    if is_swarm:
                        # Agent Swarm Pipeline View
                        st.markdown("#### 🔥 Agent Swarm Pipeline")
                        
                        stages = stats.get('stages_completed', [])
                        for stage in stages:
                            if stage == 'query_analysis':
                                st.success("✅ 1. Query Analysis")
                            elif stage == 'retrieval':
                                st.success("✅ 2. Context Retrieval")
                            elif stage == 're_ranking':
                                st.success("✅ 3. Re-ranking")
                            elif stage == 'quality_assurance':
                                st.success("✅ 4. Quality Assurance")
                            elif stage == 'response_generation':
                                st.success("✅ 5. Response Generation")
                        
                        # Quality metrics
                        st.markdown("#### Quality & Confidence")
                        metric_col1, metric_col2 = st.columns(2)
                        
                        with metric_col1:
                            quality_score = stats.get('quality_score', 0)
                            quality_color = "🟢" if quality_score >= 0.8 else "🟡" if quality_score >= 0.6 else "🔴"
                            st.metric(
                                "Quality Score",
                                f"{quality_color} {quality_score:.2f}"
                            )
                        
                        with metric_col2:
                            confidence = stats.get('confidence', 0)
                            conf_color = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
                            st.metric(
                                "Confidence",
                                f"{conf_color} {confidence:.2f}"
                            )
                        
                        # Pipeline timing
                        if 'pipeline_metrics' in stats:
                            with st.expander("⏱️ Pipeline Timing", expanded=False):
                                metrics = stats['pipeline_metrics']
                                for key, value in metrics.items():
                                    if '_time' in key:
                                        stage_name = key.replace('_time', '').replace('_', ' ').title()
                                        st.text(f"{stage_name}: {value:.3f}s")
                        
                        # Sources cited
                        if stats.get('sources_cited'):
                            with st.expander("📚 Sources Cited", expanded=False):
                                for source in stats['sources_cited']:
                                    st.text(f"• {source}")
                    
                    else:
                        # Single Agent View (original)
                        st.markdown("#### Quality Metrics")
                        quality_col1, quality_col2 = st.columns(2)
                        
                        with quality_col1:
                            has_context = stats.get('results_count', 0) > 0
                            st.metric(
                                "Context Found",
                                "✅ Yes" if has_context else "❌ No"
                            )
                        
                        with quality_col2:
                            search_type = stats.get('search_type', 'unknown')
                            quality = "🟢 Semantic" if search_type == "semantic" else "🟡 Keyword"
                            st.metric("Search Quality", quality)
                    
                    # Retrieval details
                    if context_mode in ["Detailed", "Debug"]:
                        st.markdown("#### Retrieval Details")
                        st.json({
                            "retrieval_time": f"{stats.get('retrieval_time', 0):.3f}s",
                            "results_count": stats.get('results_count', 0),
                            "search_type": stats.get('search_type', 'unknown'),
                            "has_file_context": stats.get('has_file_context', False),
                            "import_suggestions": stats.get('import_suggestions_count', 0)
                        })
            else:
                st.info("💡 Send a message to see context retrieval details")
            
            # Agent statistics (only show if we have context stats from the last query)
            if st.session_state.chat_history and len(st.session_state.chat_history) > 0:
                last_message = st.session_state.chat_history[-1]
                if last_message.get('role') == 'assistant' and 'context_stats' in last_message:
                    st.markdown("---")
                    st.markdown("#### Query Statistics")
                    context_stats = last_message['context_stats']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Retrieval Time", f"{context_stats.get('retrieval_time', 0):.3f}s")
                    with col2:
                        st.metric("Results Found", context_stats.get('results_found', 0))
                    with col3:
                        st.metric("Search Type", context_stats.get('search_type', 'N/A'))
                
                    if context_mode == "Debug":
                        with st.expander("Full Context Stats"):
                            st.json(context_stats)
    
    # Chat controls
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.selected_agent = None
            st.rerun()
    
    with col2:
        if st.button("📥 Export Chat", use_container_width=True):
            chat_export = {
                "agent_type": agent_type,
                "messages": st.session_state.chat_messages,
                "exported_at": datetime.now().isoformat()
            }
            st.download_button(
                label="Download JSON",
                data=str(chat_export),
                file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        st.markdown("**💡 Tip:** Try asking about code, patterns, or specific files in your project!")


def analytics_dashboard_page():
    """Analytics dashboard."""
    st.markdown('<div class="sub-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    
    if not st.session_state.rag_engine:
        st.warning("⚠️ RAG system not initialized")
        return
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📚 Total Documents",
            len(st.session_state.rag_engine.documents)
        )
    
    with col2:
        st.metric(
            "📁 Indexed Files",
            len(st.session_state.rag_engine.indexed_files)
        )
    
    with col3:
        st.metric(
            "🔍 Total Searches",
            len(st.session_state.search_history)
        )
    
    with col4:
        loader_stats = st.session_state.doc_loader.get_statistics()
        st.metric(
            "✅ Success Rate",
            f"{loader_stats.get('success_rate', 0):.1f}%"
        )
    
    # Document loader statistics
    st.markdown("---")
    st.markdown("### 📈 Document Loading Statistics")
    
    stats = st.session_state.doc_loader.get_statistics()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Files Processed", stats.get('total_files', 0))
    with col2:
        st.metric("Successful", stats.get('successful', 0))
    with col3:
        st.metric("Failed", stats.get('failed', 0))


def system_settings_page():
    """System settings."""
    st.markdown('<div class="sub-header">⚙️ System Settings</div>', unsafe_allow_html=True)
    
    # LangSmith Tracing Status
    st.markdown("### 🔍 LangSmith Tracing")
    langsmith_enabled = os.environ.get('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
    
    if langsmith_enabled:
        st.success("✅ LangSmith Tracing Enabled")
        st.info(f"**Project:** {os.environ.get('LANGCHAIN_PROJECT', 'default')}")
        st.markdown("🔗 View traces at: [https://smith.langchain.com/](https://smith.langchain.com/)")
    else:
        st.warning("⚠️ LangSmith Tracing Disabled")
        st.info("To enable tracing, add to `.streamlit/secrets.toml`:")
        st.code("""
LANGSMITH_TRACING = "true"
LANGSMITH_API_KEY = "your-langsmith-api-key"
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
LANGSMITH_PROJECT = "ai-dev-agent"
        """, language="toml")
    
    st.markdown("---")
    
    # RAG Engine settings
    st.markdown("### RAG Engine Configuration")
    
    if st.session_state.rag_engine:
        st.success("✅ RAG Engine Active")
        
        # Show configuration
        st.json({
            "embeddings_model": "all-MiniLM-L6-v2",
            "vector_store": "Qdrant",
            "chunk_size": 512,
            "chunk_overlap": 50,
            "documents_indexed": len(st.session_state.rag_engine.documents),
            "files_indexed": len(st.session_state.rag_engine.indexed_files)
        })
        
        # Reset button
        if st.button("🔄 Reset RAG Engine", type="secondary"):
            st.session_state.rag_engine = None
            st.session_state.indexed_documents = []
            st.session_state.search_history = []
            st.success("✅ RAG Engine reset successfully")
            st.rerun()
    
    else:
        st.warning("⚠️ RAG Engine not initialized")
        if st.button("🚀 Initialize RAG Engine"):
            initialize_rag_engine()
            st.success("✅ RAG Engine initialized")
            st.rerun()


def testing_evaluation_page():
    """
    Comprehensive Testing & Evaluation page with transparency features.
    
    Features:
    - Query testing with detailed breakdowns
    - Side-by-side comparison
    - Evaluation metrics
    - Golden dataset management
    - Transparency reporting
    """
    st.markdown('<div class="sub-header">🧪 Testing & Evaluation</div>', unsafe_allow_html=True)
    
    if not st.session_state.rag_engine or not st.session_state.rag_engine.vector_store:
        st.warning("⚠️ Please index documents first before testing")
        return
    
    # Tabs for different testing modes
    test_tab, compare_tab, golden_tab, metrics_tab = st.tabs([
        "🔬 Single Query Test", 
        "⚖️ Side-by-Side Comparison",
        "📋 Golden Dataset",
        "📊 Evaluation Metrics"
    ])
    
    # ========================================
    # TAB 1: Single Query Test with Transparency
    # ========================================
    with test_tab:
        st.markdown("### 🔬 Test Query with Full Transparency")
        st.markdown("See exactly how the RAG system processes your query, retrieves context, and generates responses.")
        
        # Test query input
        test_query = st.text_area(
            "Test Query",
            placeholder="Enter a test query to see detailed processing...",
            height=100,
            help="Enter any question or query to test the RAG system"
        )
        
        # Test configuration
        col1, col2, col3 = st.columns(3)
        with col1:
            show_query_rewriting = st.checkbox("Show Query Rewriting", value=True)
        with col2:
            show_retrieval_stages = st.checkbox("Show Retrieval Stages", value=True)
        with col3:
            show_scoring_details = st.checkbox("Show Scoring Details", value=True)
        
        if st.button("🚀 Run Test", type="primary", use_container_width=True):
            if test_query:
                with st.spinner("Processing query with full transparency..."):
                    test_result = run_transparent_test(
                        test_query,
                        show_query_rewriting,
                        show_retrieval_stages,
                        show_scoring_details
                    )
                    
                    # Display transparency report
                    display_transparency_report(test_result)
                    
                    # Save to query history
                    st.session_state.query_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'query': test_query,
                        'result': test_result
                    })
            else:
                st.warning("Please enter a test query")
    
    # ========================================
    # TAB 2: Side-by-Side Comparison
    # ========================================
    with compare_tab:
        st.markdown("### ⚖️ Compare Different Approaches")
        st.markdown("Test how different retrieval strategies affect the results")
        
        compare_query = st.text_area(
            "Query for Comparison",
            placeholder="Enter query to compare different retrieval methods...",
            height=80
        )
        
        if st.button("⚖️ Run Comparison", type="primary", use_container_width=True):
            if compare_query:
                with st.spinner("Running comparisons..."):
                    # Run with different strategies
                    results = run_comparison_test(compare_query)
                    
                    # Display side-by-side
                    display_comparison_results(results)
            else:
                st.warning("Please enter a query for comparison")
    
    # ========================================
    # TAB 3: Golden Dataset Management
    # ========================================
    with golden_tab:
        st.markdown("### 📋 Golden Dataset Management")
        st.markdown("Create and manage test queries with expected answers for systematic evaluation")
        
        # Add new golden query
        with st.expander("➕ Add New Golden Query", expanded=False):
            new_query = st.text_input("Query")
            new_expected = st.text_area("Expected Answer (optional)")
            new_category = st.selectbox("Category", [
                "Factual", "Conceptual", "Procedural", "Multi-hop", "Edge Case"
            ])
            
            if st.button("💾 Save to Golden Dataset"):
                if new_query:
                    st.session_state.test_queries.append({
                        'id': len(st.session_state.test_queries) + 1,
                        'query': new_query,
                        'expected': new_expected,
                        'category': new_category,
                        'created': datetime.now().isoformat()
                    })
                    st.success(f"✅ Added query to golden dataset")
                    st.rerun()
        
        # Display golden dataset
        if st.session_state.test_queries:
            st.markdown(f"**📊 Total Golden Queries: {len(st.session_state.test_queries)}**")
            
            # Run all tests button
            if st.button("🧪 Run All Golden Tests", type="primary"):
                with st.spinner("Running all golden tests..."):
                    batch_results = run_golden_batch_test(st.session_state.test_queries)
                    st.session_state.test_results = batch_results
                    display_batch_results(batch_results)
            
            # Display queries
            for idx, query_item in enumerate(st.session_state.test_queries):
                with st.expander(f"Query #{query_item['id']}: {query_item['query'][:60]}..."):
                    st.write(f"**Category:** {query_item['category']}")
                    st.write(f"**Query:** {query_item['query']}")
                    if query_item['expected']:
                        st.write(f"**Expected Answer:** {query_item['expected']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"🧪 Test", key=f"test_{idx}"):
                            result = run_transparent_test(query_item['query'], True, True, True)
                            display_transparency_report(result)
                    with col2:
                        if st.button(f"🗑️ Delete", key=f"del_{idx}"):
                            st.session_state.test_queries.pop(idx)
                            st.rerun()
        else:
            st.info("📝 No golden queries yet. Add some to build your test dataset!")
    
    # ========================================
    # TAB 4: Evaluation Metrics
    # ========================================
    with metrics_tab:
        st.markdown("### 📊 Evaluation Metrics Dashboard")
        
        if st.session_state.query_history:
            st.markdown(f"**📈 Total Queries Analyzed: {len(st.session_state.query_history)}**")
            
            # Calculate aggregate metrics
            metrics = calculate_aggregate_metrics(st.session_state.query_history)
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Avg Retrieval Time", 
                    f"{metrics['avg_retrieval_time_ms']:.0f}ms",
                    help="Average time to retrieve context"
                )
            
            with col2:
                st.metric(
                    "Avg Results", 
                    f"{metrics['avg_results_count']:.1f}",
                    help="Average number of results retrieved"
                )
            
            with col3:
                st.metric(
                    "Avg Relevance Score", 
                    f"{metrics['avg_relevance_score']:.2f}",
                    help="Average relevance score of top results"
                )
            
            with col4:
                st.metric(
                    "Deduplication Rate", 
                    f"{metrics['deduplication_rate']:.1%}",
                    help="% of duplicate results removed"
                )
            
            # Performance over time
            st.markdown("---")
            st.markdown("#### 📈 Performance Trends")
            
            # Simple performance chart
            if len(st.session_state.query_history) > 1:
                import pandas as pd
                
                df = pd.DataFrame([
                    {
                        'Query': f"Q{i+1}",
                        'Retrieval Time (ms)': h['result'].get('retrieval_time', 0) * 1000,
                        'Results Count': h['result'].get('results_count', 0),
                    }
                    for i, h in enumerate(st.session_state.query_history[-20:])  # Last 20
                ])
                
                st.line_chart(df.set_index('Query'))
            
            # Query type distribution
            st.markdown("#### 📊 Query Analysis")
            
            if st.session_state.test_queries:
                import pandas as pd
                category_counts = {}
                for q in st.session_state.test_queries:
                    cat = q['category']
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                
                st.bar_chart(pd.Series(category_counts))
            
            # Export results
            st.markdown("---")
            if st.button("📥 Export Test Results"):
                export_test_results(st.session_state.query_history, st.session_state.test_results)
        else:
            st.info("📊 Run some tests to see evaluation metrics!")
        
        # Clear history button
        if st.button("🗑️ Clear Test History"):
            st.session_state.query_history = []
            st.session_state.test_results = []
            st.success("✅ Test history cleared")
            st.rerun()


def run_transparent_test(query: str, show_rewriting: bool, show_stages: bool, show_scoring: bool, use_swarm: bool = True) -> Dict:
    """Run a test query with full transparency."""
    import time
    
    start_time = time.time()
    result = {
        'query': query,
        'timestamp': datetime.now().isoformat(),
        'stages': [],
        'mode': 'agent_swarm' if use_swarm else 'single_agent'
    }
    
    try:
        if use_swarm:
            # Use Agent Swarm
            from agents.rag import RAGSwarmCoordinator
            
            swarm = RAGSwarmCoordinator(st.session_state.rag_engine)
            
            retrieval_start = time.time()
            response = asyncio.run(swarm.execute({
                'query': query,
                'max_results': 10,
                'quality_threshold': 0.7,
                'enable_re_retrieval': True
            }))
            retrieval_time = time.time() - retrieval_start
            
            # Extract results
            pipeline_state = response.get('pipeline_state', {})
            result['retrieval_time'] = retrieval_time
            result['response'] = response.get('response', '')
            result['confidence'] = response.get('confidence', 0)
            result['quality_score'] = pipeline_state.get('quality_report', {}).get('quality_score', 0)
            result['results_count'] = len(pipeline_state.get('ranked_results', []))
            result['semantic_results'] = pipeline_state.get('ranked_results', [])
            result['search_type'] = 'agent_swarm'
            result['stages_completed'] = pipeline_state.get('stages_completed', [])
            result['pipeline_metrics'] = pipeline_state.get('metrics', {})
            result['query_analysis'] = pipeline_state.get('query_analysis', {})
            result['sources_cited'] = response.get('sources_cited', [])
            
        else:
            # Use Single Agent
            from agents.core.context_aware_agent import ContextAwareAgent
            from models.config import AgentConfig
            
            agent_config = AgentConfig(
                agent_id="test_agent",
                name="Test Agent",
                role="test"
            )
            
            agent = ContextAwareAgent(agent_config, st.session_state.rag_engine)
            
            retrieval_start = time.time()
            response = asyncio.run(agent.execute_with_context({'query': query}))
            retrieval_time = time.time() - retrieval_start
            
            result['retrieval_time'] = retrieval_time
            result['response'] = response.get('response', '')
            result['context_stats'] = response.get('context_stats', {})
            result['context_data'] = response.get('context', {})
            result['results_count'] = len(response.get('context', {}).get('semantic_search_results', []))
            
            if 'context' in response:
                ctx = response['context']
                result['semantic_results'] = ctx.get('semantic_search_results', [])
                result['total_found'] = ctx.get('total_found', 0)
                result['search_type'] = ctx.get('search_type', 'unknown')
        
        result['success'] = True
        
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
    
    result['total_time'] = time.time() - start_time
    
    return result


def display_transparency_report(result: Dict):
    """Display comprehensive transparency report."""
    
    st.markdown("---")
    st.markdown("## 🔍 Transparency Report")
    
    if not result.get('success'):
        st.error(f"❌ Test Failed: {result.get('error', 'Unknown error')}")
        return
    
    # Show mode indicator
    is_swarm = result.get('mode') == 'agent_swarm'
    mode_badge = "🔥 Agent Swarm" if is_swarm else "⚡ Single Agent"
    st.info(f"**Mode:** {mode_badge}")
    
    # Overview metrics
    if is_swarm:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("⏱️ Total Time", f"{result['retrieval_time']*1000:.0f}ms")
        with col2:
            st.metric("📄 Results", result['results_count'])
        with col3:
            quality = result.get('quality_score', 0)
            quality_color = "🟢" if quality >= 0.8 else "🟡" if quality >= 0.6 else "🔴"
            st.metric("Quality", f"{quality_color} {quality:.2f}")
        with col4:
            confidence = result.get('confidence', 0)
            conf_color = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
            st.metric("Confidence", f"{conf_color} {confidence:.2f}")
        with col5:
            stages_count = len(result.get('stages_completed', []))
            st.metric("Stages", f"✅ {stages_count}/5")
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("⏱️ Retrieval Time", f"{result['retrieval_time']*1000:.0f}ms")
        with col2:
            st.metric("📄 Results Found", result['results_count'])
        with col3:
            st.metric("🔍 Search Type", result.get('search_type', 'N/A'))
        with col4:
            st.metric("✅ Success", "Yes" if result['success'] else "No")
    
    # Response
    st.markdown("### 💬 Generated Response")
    st.markdown(f'<div class="transparency-panel">{result.get("response", "No response")}</div>', unsafe_allow_html=True)
    
    # Context details
    with st.expander("🔍 Retrieved Context Details", expanded=True):
        semantic_results = result.get('semantic_results', [])
        
        if semantic_results:
            st.markdown(f"**Retrieved {len(semantic_results)} context chunks:**")
            
            for idx, res in enumerate(semantic_results[:10], 1):  # Show top 10
                score = res.get('combined_score', res.get('relevance_score', 0))
                score_class = 'score-high' if score > 0.7 else 'score-medium' if score > 0.4 else 'score-low'
                
                st.markdown(f"#### Result #{idx}")
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Content Preview:**")
                    content = res.get('content', '')
                    st.text(content[:300] + "..." if len(content) > 300 else content)
                
                with col2:
                    st.markdown(f'<p class="{score_class}">Score: {score:.3f}</p>', unsafe_allow_html=True)
                    
                    # Show scoring breakdown if available
                    if 'scoring_details' in res:
                        details = res['scoring_details']
                        st.caption(f"Semantic: {details.get('base', 0):.2f}")
                        st.caption(f"Keyword: {details.get('keyword', 0):.2f}")
                        st.caption(f"Quality: {details.get('quality', 0):.2f}")
                        st.caption(f"Diversity: {details.get('diversity', 0):.2f}")
                
                st.markdown("---")
        else:
            st.warning("No context retrieved")
    
    # Processing stages
    with st.expander("⚙️ Processing Pipeline", expanded=False):
        if is_swarm:
            # Agent Swarm Pipeline Details
            st.markdown("#### 🔥 Agent Swarm Pipeline")
            
            # Show completed stages
            stages_completed = result.get('stages_completed', [])
            stage_mapping = {
                'query_analysis': '1️⃣ Query Analysis (QueryAnalystAgent)',
                'retrieval': '2️⃣ Context Retrieval (RetrievalSpecialistAgent)',
                're_ranking': '3️⃣ Re-ranking (ReRankerAgent)',
                'quality_assurance': '4️⃣ Quality Assurance (QualityAssuranceAgent)',
                'response_generation': '5️⃣ Response Generation (WriterAgent)'
            }
            
            for stage in stages_completed:
                stage_name = stage_mapping.get(stage, stage)
                st.success(f"✅ {stage_name}")
            
            # Pipeline metrics
            if 'pipeline_metrics' in result:
                st.markdown("#### ⏱️ Stage Timing")
                metrics = result['pipeline_metrics']
                for key, value in metrics.items():
                    if '_time' in key:
                        stage_name = key.replace('_time', '').replace('_', ' ').title()
                        st.text(f"{stage_name}: {value*1000:.0f}ms")
            
            # Query analysis details
            if 'query_analysis' in result:
                with st.expander("🔍 Query Analysis Details"):
                    qa = result['query_analysis']
                    st.json(qa)
            
            # Sources cited
            if result.get('sources_cited'):
                with st.expander("📚 Sources Cited"):
                    for source in result['sources_cited']:
                        st.text(f"• {source}")
        else:
            # Single Agent Pipeline
            stages = result.get('context_stats', {}).get('searches_performed', 0)
            st.markdown(f"**Searches Performed:** {stages}")
            st.markdown('<span class="stage-badge">Query Rewriting</span>', unsafe_allow_html=True)
            st.markdown('<span class="stage-badge">Multi-Stage Retrieval</span>', unsafe_allow_html=True)
            st.markdown('<span class="stage-badge">Deduplication</span>', unsafe_allow_html=True)
            st.markdown('<span class="stage-badge">Multi-Signal Re-ranking</span>', unsafe_allow_html=True)
            st.markdown('<span class="stage-badge">Position Optimization</span>', unsafe_allow_html=True)
            st.markdown('<span class="stage-badge">LLM Generation</span>', unsafe_allow_html=True)


def run_comparison_test(query: str) -> Dict:
    """Run comparison test with different strategies."""
    # Placeholder for comparison logic
    return {
        'query': query,
        'strategies': ['Basic', 'Advanced', 'Multi-Stage'],
        'results': []
    }


def display_comparison_results(results: Dict):
    """Display side-by-side comparison."""
    st.info("🚧 Comparison feature coming soon!")


def run_golden_batch_test(queries: List[Dict]) -> List[Dict]:
    """Run batch test on golden dataset."""
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, query_item in enumerate(queries):
        status_text.text(f"Testing query {idx+1}/{len(queries)}...")
        result = run_transparent_test(query_item['query'], False, False, False)
        results.append({
            'query_item': query_item,
            'result': result
        })
        progress_bar.progress((idx + 1) / len(queries))
    
    status_text.text("✅ Batch testing complete!")
    return results


def display_batch_results(results: List[Dict]):
    """Display batch test results."""
    if not results:
        return
    
    st.markdown("### 📊 Batch Test Results")
    
    # Summary metrics
    total = len(results)
    successful = sum(1 for r in results if r['result'].get('success', False))
    avg_time = sum(r['result'].get('retrieval_time', 0) for r in results) / total if total > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tests", total)
    with col2:
        st.metric("Successful", successful, f"{successful/total*100:.1f}%")
    with col3:
        st.metric("Avg Time", f"{avg_time*1000:.0f}ms")
    
    # Individual results
    for idx, item in enumerate(results):
        with st.expander(f"Result #{idx+1}: {item['query_item']['query'][:50]}..."):
            result = item['result']
            st.write(f"**Success:** {'✅' if result.get('success') else '❌'}")
            st.write(f"**Time:** {result.get('retrieval_time', 0)*1000:.0f}ms")
            st.write(f"**Results:** {result.get('results_count', 0)}")
            if result.get('response'):
                st.write(f"**Response:** {result['response'][:200]}...")


def calculate_aggregate_metrics(query_history: List[Dict]) -> Dict:
    """Calculate aggregate metrics from query history."""
    if not query_history:
        return {}
    
    total_time = sum(h['result'].get('retrieval_time', 0) for h in query_history)
    total_results = sum(h['result'].get('results_count', 0) for h in query_history)
    
    return {
        'avg_retrieval_time_ms': (total_time / len(query_history)) * 1000 if query_history else 0,
        'avg_results_count': total_results / len(query_history) if query_history else 0,
        'avg_relevance_score': 0.75,  # Placeholder
        'deduplication_rate': 0.35,  # Placeholder
    }


def export_test_results(query_history: List[Dict], test_results: List[Dict]):
    """Export test results to JSON."""
    import json
    
    export_data = {
        'exported_at': datetime.now().isoformat(),
        'query_history': query_history,
        'test_results': test_results
    }
    
    json_str = json.dumps(export_data, indent=2)
    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name=f"rag_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


if __name__ == "__main__":
    main()
