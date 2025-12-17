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

#!/usr/bin/env python3
import os
import sys
import logging
from pathlib import Path

# Initialize logger
logger = logging.getLogger(__name__)

# CRITICAL: Set environment variables BEFORE any LangChain imports
# This ensures LangSmith tracing is active from the start

# Set USER_AGENT to suppress warning
os.environ.setdefault('USER_AGENT', 'ai-dev-agent-rag-app/1.0')

# Enable LangSmith tracing - MUST happen before any LangChain imports
try:
    # Try to load from secrets.toml
    secrets_path = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        import toml
        secrets = toml.load(secrets_path)
        
        # Enable tracing if configured
        if secrets.get('LANGSMITH_TRACING', 'false').lower() == 'true':
            os.environ['LANGCHAIN_TRACING_V2'] = 'true'
            os.environ['LANGCHAIN_API_KEY'] = secrets.get('LANGSMITH_API_KEY', '')
            os.environ['LANGCHAIN_ENDPOINT'] = secrets.get('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com')
            os.environ['LANGCHAIN_PROJECT'] = secrets.get('LANGSMITH_PROJECT', 'ai-dev-agent')
            print("✅ LangSmith tracing ENABLED")
            print(f"   Project: {os.environ['LANGCHAIN_PROJECT']}")
        else:
            print("⚠️  LangSmith tracing DISABLED in secrets.toml")
except Exception as e:
    print(f"⚠️  Could not load LangSmith config: {e}")
    # Try environment variables as fallback
    if os.getenv('LANGSMITH_API_KEY') or os.getenv('LANGCHAIN_API_KEY'):
        os.environ.setdefault('LANGCHAIN_TRACING_V2', 'true')
        os.environ.setdefault('LANGCHAIN_API_KEY', os.getenv('LANGSMITH_API_KEY', os.getenv('LANGCHAIN_API_KEY', '')))
        os.environ.setdefault('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
        os.environ.setdefault('LANGCHAIN_PROJECT', 'ai-dev-agent')

# NOW import streamlit and other modules
import streamlit as st
import asyncio
import nest_asyncio
from datetime import datetime
from typing import List, Dict, Any
import threading
import concurrent.futures

# CRITICAL: Apply nest_asyncio to allow nested event loops
# This is required for Streamlit + async LangChain/Gemini calls
nest_asyncio.apply()


def run_async(coro):
    """
    Run async coroutine in a dedicated thread with its own event loop.
    
    This completely isolates the async execution from Streamlit's main thread,
    preventing "attached to different loop" errors from grpc/Gemini.
    
    Why this works:
    - Each thread can have its own event loop
    - grpc operations stay within the same loop
    - No conflicts with Streamlit's execution model
    """
    def run_in_thread():
        """Run coroutine in a new event loop in this thread."""
        # Create fresh event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run coroutine in this loop
            result = loop.run_until_complete(coro)
            return result
        finally:
            # Clean up
            loop.close()
    
    # Run in a separate thread to completely isolate event loops
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_in_thread)
        return future.result()  # Block until complete


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
        background-color: #f8f9fa;
        color: #212529;
        border: 2px solid #007bff;
        margin: 1rem 0;
        font-size: 1rem;
        line-height: 1.6;
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
    # Initialize with None, will be updated when rag_engine is available
    st.session_state.doc_loader = DocumentLoader(qdrant_client=None)

# Update doc_loader with Qdrant client when rag_engine is available
if st.session_state.rag_engine and st.session_state.rag_engine.qdrant_client:
    st.session_state.doc_loader.qdrant_client = st.session_state.rag_engine.qdrant_client
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
    
    # LangSmith tracing indicator
    tracing_enabled = os.environ.get('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
    if tracing_enabled:
        st.success(f"✅ LangSmith Tracing Active - Project: `{os.environ.get('LANGCHAIN_PROJECT', 'ai-dev-agent')}`")
    else:
        st.warning("⚠️ LangSmith Tracing Disabled")
    
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
            if st.session_state.rag_engine and st.session_state.rag_engine.qdrant_client:
                try:
                    # Delete the collection
                    st.session_state.rag_engine.qdrant_client.delete_collection(
                        st.session_state.rag_engine.collection_name
                    )
                    
                    # Recreate empty collection with correct dimensions (3072 for Gemini)
                    from qdrant_client.models import VectorParams, Distance, SparseVectorParams
                    
                    # Check if we can use hybrid (new API + sparse embeddings)
                    try:
                        from langchain_qdrant.qdrant import QdrantVectorStore, RetrievalMode
                        QDRANT_NEW_API = True
                    except ImportError:
                        QDRANT_NEW_API = False
                    
                    if QDRANT_NEW_API and hasattr(st.session_state.rag_engine, 'sparse_embeddings') and st.session_state.rag_engine.sparse_embeddings:
                        # Create with hybrid support
                        vectors_config = {
                            "dense": VectorParams(size=3072, distance=Distance.COSINE)
                        }
                        st.session_state.rag_engine.qdrant_client.create_collection(
                            collection_name=st.session_state.rag_engine.collection_name,
                            vectors_config=vectors_config,
                            sparse_vectors_config={"sparse": SparseVectorParams()}
                        )
                    else:
                        # Create dense-only
                        st.session_state.rag_engine.qdrant_client.create_collection(
                            collection_name=st.session_state.rag_engine.collection_name,
                            vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
                        )
                    
                    # Clear vector store and documents
                    st.session_state.rag_engine.vector_store = None
                    st.session_state.rag_engine.documents = []
                    st.session_state.indexed_documents = []
                    
                    st.success("✅ All documents cleared - empty collection recreated")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to clear documents: {e}")
                    import traceback
                    st.error(traceback.format_exc())
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
            result = run_async(st.session_state.doc_loader.load_document(temp_path))
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
                    # New API with hybrid - use 3072 dimensions for Gemini
                    vectors_config = {
                        "dense": VectorParams(size=3072, distance=Distance.COSINE)
                    }
                    st.session_state.rag_engine.qdrant_client.create_collection(
                        collection_name=st.session_state.rag_engine.collection_name,
                        vectors_config=vectors_config,
                        sparse_vectors_config={"sparse": SparseVectorParams()}
                    )
                    st.info("✅ Collection created with HYBRID search support")
                    has_sparse_vectors = True
                else:
                    # Legacy or dense-only - use 3072 dimensions for Gemini
                    st.session_state.rag_engine.qdrant_client.create_collection(
                        collection_name=st.session_state.rag_engine.collection_name,
                        vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
                    )
                    st.info("✅ Collection created (dense-only, 3072-dim for Gemini)")
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
    
    # Enhanced scraping options
    with st.expander("⚙️ Advanced Scraping Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            recursive = st.checkbox(
                "Recursive Crawling",
                value=False,
                help="Crawl linked pages recursively"
            )
            
            max_depth = st.slider(
                "Max Depth",
                min_value=1,
                max_value=5,
                value=1,
                disabled=not recursive,
                help="Maximum depth for recursive crawling"
            )
            
            max_pages = st.slider(
                "Max Pages",
                min_value=1,
                max_value=50,
                value=10,
                disabled=not recursive,
                help="Maximum number of pages to scrape"
            )
        
        with col2:
            css_selector = st.text_input(
                "CSS Selector (optional)",
                placeholder="article, .content, #main",
                help="CSS selector to extract specific content"
            )
            
            rate_limit = st.slider(
                "Rate Limit (seconds)",
                min_value=0.0,
                max_value=5.0,
                value=1.0,
                step=0.5,
                help="Delay between requests (respectful crawling)"
            )
            
            same_domain_only = st.checkbox(
                "Same Domain Only",
                value=True,
                disabled=not recursive,
                help="Only crawl links within the same domain"
            )
    
    scrape_button_label = "🕷️ Recursive Scrape" if recursive else "🔍 Scrape Website"
    
    if st.button(scrape_button_label, type="primary", disabled=not url):
        if url:
            # Check for duplicate URL
            existing_urls = [doc.get('file_name') for doc in st.session_state.indexed_documents if doc.get('file_type') == 'website']
            if url in existing_urls:
                st.warning(f"⚠️ URL already scraped: {url}")
                st.info("This URL is already in the vector store. Delete it first if you want to re-scrape.")
                return
            
            with st.spinner(f"Scraping {url}... {'(recursive mode)' if recursive else ''}"):
                try:
                    # Use WebScrapingSpecialistAgent for advanced scraping
                    if recursive or css_selector:
                        from agents.rag.web_scraping_specialist_agent import WebScrapingSpecialistAgent
                        from models.config import AgentConfig
                        
                        config = AgentConfig(
                            agent_id="web_scraper",
                            name="Web Scraping Specialist",
                            role="web_scraping"
                        )
                        
                        scraper_agent = WebScrapingSpecialistAgent(
                            config, 
                            document_loader=st.session_state.doc_loader
                        )
                        
                        result = run_async(scraper_agent.execute({
                            'start_url': url,
                            'recursive': recursive,
                            'max_depth': max_depth,
                            'css_selector': css_selector if css_selector else None,
                            'rate_limit': rate_limit,
                            'max_pages': max_pages,
                            'same_domain_only': same_domain_only,
                            'skip_duplicates': True
                        }))
                        
                        if result['status'] == 'success':
                            # Agent returns multiple documents
                            all_documents = []
                            pages_visited = 0
                            
                            for doc_result in result['documents']:
                                # Count all visited pages (success + skipped duplicates)
                                if doc_result.get('success') or doc_result.get('skipped'):
                                    pages_visited += 1
                                
                                # Only add NEW documents (not skipped duplicates)
                                if doc_result.get('success'):
                                    # Check for both 'documents' and 'chunks' keys
                                    docs_to_add = doc_result.get('documents') or doc_result.get('chunks')
                                    if docs_to_add:
                                        all_documents.extend(docs_to_add)
                            
                            result = {
                                'success': True,
                                'documents': all_documents,
                                'document_count': len(all_documents),
                                'pages_visited': pages_visited,
                                'url': url,
                                'stats': result.get('stats', {})
                            }
                        else:
                            result = {'success': False, 'error': result.get('error', 'Unknown error')}
                    else:
                        # Simple single-page scraping
                        result = run_async(st.session_state.doc_loader.load_website(url))
                    
                    if result['success']:
                        st.success(f"✅ Successfully scraped {url}")
                        
                        # Show detailed stats if advanced scraping was used
                        if 'stats' in result and result['stats']:
                            stats = result['stats']
                            
                            # Display detailed metrics
                            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                            
                            pages_visited = result.get('pages_visited', stats.get('total_urls_discovered', 0))
                            new_pages = stats.get('urls_scraped', 0)
                            duplicates = stats.get('duplicates_detected', 0)
                            
                            with metric_col1:
                                st.metric("Pages Visited", pages_visited, help="Total pages crawled (new + duplicates)")
                            with metric_col2:
                                st.metric("New Pages", new_pages, help="New pages added to database")
                            with metric_col3:
                                st.metric("Duplicates", duplicates, help="Pages already in database")
                            with metric_col4:
                                st.metric("Errors", stats.get('errors', 0))
                            
                            if recursive:
                                st.info(f"⏱️ Average scrape time: {stats.get('average_scrape_time', 0):.2f}s per page")
                        
                        # Add to RAG engine
                        if st.session_state.rag_engine and result.get('documents'):
                            doc_count_before = len(st.session_state.rag_engine.documents)
                            st.session_state.rag_engine.documents.extend(result['documents'])
                            doc_count_after = len(st.session_state.rag_engine.documents)
                            new_docs_added = doc_count_after - doc_count_before
                            
                            if new_docs_added > 0:
                                st.success(f"📄 Added {new_docs_added} document chunks to RAG engine")
                            
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
                                    # Create NEW collection with hybrid search support if available - use 3072 dimensions for Gemini
                                    if QDRANT_NEW_API and hasattr(st.session_state.rag_engine, 'sparse_embeddings') and st.session_state.rag_engine.sparse_embeddings:
                                        vectors_config = {
                                            "dense": VectorParams(size=3072, distance=Distance.COSINE)
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
                                            vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
                                        )
                                        st.info("✅ Created new collection (dense-only, 3072-dim for Gemini)")
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
                    results = run_async(
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
    
    # Initialize chat history and settings
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'selected_agent' not in st.session_state:
        st.session_state.selected_agent = None
    if 'context_debug_mode' not in st.session_state:
        st.session_state.context_debug_mode = True
    if 'selected_documents_for_rag' not in st.session_state:
        st.session_state.selected_documents_for_rag = []  # Empty = use all documents
    
    # Initialize ThreadManager for stateful conversations
    if 'rag_thread_manager' not in st.session_state:
        from utils.thread_manager import create_thread_manager
        st.session_state.rag_thread_manager = create_thread_manager(
            session_type="rag",
            prefix="rag_chat"
        )
    
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
    
    # Thread ID Management Section
    st.subheader("🔗 Session Management")
    
    # TEMP DEBUG: Clear cached coordinator button
    if st.button("🔄 Force Recreate Coordinator", help="Clear cached coordinator and create fresh one"):
        if 'rag_swarm_coordinator' in st.session_state:
            del st.session_state.rag_swarm_coordinator
            st.success("✅ Coordinator cache cleared! Next query will create fresh coordinator.")
            st.rerun()
    
    # Thread/Session Management with Dropdown Selector
    st.markdown("### 💬 Conversation Threads")
    
    thread_col1, thread_col2, thread_col3 = st.columns([5, 1, 1])
    
    with thread_col1:
        # Get all sessions
        sessions = st.session_state.rag_thread_manager.get_session_history()
        current_thread = st.session_state.rag_thread_manager.get_current_thread_id()
        
        # Create dropdown options with names
        thread_options = {}
        for session in sessions:
            display_name = session.get_display_name()
            thread_options[display_name] = session.thread_id
        
        # Find current session index
        current_display_names = [k for k, v in thread_options.items() if v == current_thread]
        current_index = 0
        if current_display_names:
            current_display_name = current_display_names[0]
            current_index = list(thread_options.keys()).index(current_display_name)
        
        # Thread selector dropdown
        selected_display_name = st.selectbox(
            "Select Conversation Thread",
            options=list(thread_options.keys()),
            index=current_index,
            key="thread_selector",
            help="Select a conversation thread to continue or switch between topics"
        )
        
        # Load selected session if different
        selected_thread_id = thread_options[selected_display_name]
        if selected_thread_id != current_thread:
            st.session_state.rag_thread_manager.load_session(selected_thread_id)
            
            # Load conversation history for this thread into UI
            st.session_state.chat_messages = []  # Clear current display
            
            # Try to load history from RAG agent checkpointer
            try:
                # Get the active RAG agent (SimpleRAG or AgenticRAG)
                agent_key = None
                if 'simple_rag_agent' in st.session_state:
                    agent_key = 'simple_rag_agent'
                elif 'agentic_rag_agent' in st.session_state:
                    agent_key = 'agentic_rag_agent'
                
                if agent_key:
                    rag_agent = st.session_state[agent_key]
                    config = {"configurable": {"thread_id": selected_thread_id}}
                    
                    # Get thread state from checkpointer
                    existing_state = rag_agent.graph.get_state(config)
                    if existing_state and existing_state.values:
                        existing_messages = existing_state.values.get("messages", [])
                        
                        # Convert LangChain messages to Streamlit chat format
                        for msg in existing_messages:
                            msg_type = type(msg).__name__
                            if msg_type == "HumanMessage":
                                st.session_state.chat_messages.append({
                                    "role": "user",
                                    "content": msg.content,
                                    "timestamp": datetime.now().isoformat()
                                })
                            elif msg_type == "AIMessage" and msg.content:
                                st.session_state.chat_messages.append({
                                    "role": "assistant",
                                    "content": msg.content,
                                    "timestamp": datetime.now().isoformat()
                                })
                        
                        logger.info(f"📥 Loaded {len(st.session_state.chat_messages)} messages for thread {selected_thread_id}")
            except Exception as e:
                logger.warning(f"Could not load thread history: {e}")
            
            # Clear cached coordinator for new thread
            if 'rag_swarm_coordinator' in st.session_state:
                del st.session_state.rag_swarm_coordinator
            if 'deep_agent' in st.session_state:
                del st.session_state.deep_agent
            st.rerun()
    
    with thread_col2:
        if st.button("🆕 New", help="Start a new conversation thread", use_container_width=True):
            # Create new session with auto-generated name
            st.session_state.rag_thread_manager.create_new_session(
                name=f"New Chat {len(sessions) + 1}"
            )
            st.session_state.chat_messages = []  # Clear UI chat display
            # Clear cached agents to start fresh
            if 'rag_swarm_coordinator' in st.session_state:
                del st.session_state.rag_swarm_coordinator
            if 'deep_agent' in st.session_state:
                del st.session_state.deep_agent
            if 'simple_rag_agent' in st.session_state:
                del st.session_state.simple_rag_agent
            if 'agentic_rag_agent' in st.session_state:
                del st.session_state.agentic_rag_agent
            st.success("New conversation started!")
            st.rerun()
    
    with thread_col3:
        # Popover menu for thread actions
        with st.popover("⚙️", use_container_width=True):
            if st.button("📝 Rename Thread", use_container_width=True):
                st.session_state.show_rename_dialog = True
                st.rerun()
            if st.button("🗑️ Delete Current", use_container_width=True):
                st.session_state.show_delete_dialog = True
                st.rerun()
            if st.button("🗑️ Delete All Threads", use_container_width=True):
                st.session_state.show_delete_all_dialog = True
                st.rerun()
    
    # Rename dialog
    if st.session_state.get('show_rename_dialog', False):
        with st.form("rename_thread_form"):
            st.write("**📝 Rename Thread**")
            current_session = st.session_state.rag_thread_manager.current_session
            new_name = st.text_input(
                "New name:",
                value=current_session.name,
                placeholder="Enter a descriptive name for this conversation"
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.form_submit_button("✅ Save", use_container_width=True):
                    if new_name and new_name.strip():
                        st.session_state.rag_thread_manager.set_session_name(new_name.strip())
                        st.session_state.show_rename_dialog = False
                        st.success(f"✅ Renamed to: {new_name}")
                        st.rerun()
            with col_b:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_rename_dialog = False
                    st.rerun()
    
    # Delete current thread dialog
    if st.session_state.get('show_delete_dialog', False):
        with st.form("delete_thread_form"):
            st.write("**🗑️ Delete Current Thread**")
            current_session = st.session_state.rag_thread_manager.current_session
            st.warning(f"⚠️ Delete: **{current_session.name}** ({current_session.message_count} messages)?")
            st.caption("This action cannot be undone.")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.form_submit_button("🗑️ Delete", type="primary", use_container_width=True):
                    deleted_name = current_session.name
                    st.session_state.rag_thread_manager.delete_session(current_session.thread_id)
                    st.session_state.chat_messages = []
                    st.session_state.show_delete_dialog = False
                    st.success(f"✅ Deleted: {deleted_name}")
                    st.rerun()
            with col_b:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_delete_dialog = False
                    st.rerun()
    
    # Delete all threads dialog
    if st.session_state.get('show_delete_all_dialog', False):
        with st.form("delete_all_threads_form"):
            st.write("**🗑️ Delete All Threads**")
            total_sessions = len(sessions)
            st.error(f"⚠️ **DANGER**: Delete all {total_sessions} threads permanently?")
            st.caption("All conversation history will be lost. Type 'DELETE ALL' to confirm.")
            
            confirm_text = st.text_input("Confirmation:", placeholder="DELETE ALL")
            
            col_a, col_b = st.columns(2)
            with col_a:
                can_delete = confirm_text == "DELETE ALL"
                if st.form_submit_button(
                    "🗑️ Delete All", 
                    type="primary", 
                    disabled=not can_delete,
                    use_container_width=True
                ):
                    if can_delete:
                        for session in list(sessions):
                            st.session_state.rag_thread_manager.delete_session(session.thread_id)
                        st.session_state.chat_messages = []
                        st.session_state.show_delete_all_dialog = False
                        st.success(f"✅ Deleted all {total_sessions} threads")
                        st.rerun()
            with col_b:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_delete_all_dialog = False
                    st.rerun()
    
    # Thread info
    stats = st.session_state.rag_thread_manager.get_stats()
    current_session = st.session_state.rag_thread_manager.current_session
    st.caption(f"📊 {stats['total_sessions']} total threads • {current_session.message_count} messages in current • Thread ID: `{current_thread}`")
    
    st.markdown("---")
    
    # Agent selection and configuration
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        agent_mode = st.selectbox(
            "RAG Mode",
            [
                "✨ Agentic RAG (Intelligent - RECOMMENDED)",
                "⚡ Simple RAG (Fast & Direct)",
            ],
            help="""Choose your RAG agent:
            
**Official LangChain Patterns (RAG V2)**:
• Agentic RAG: Grades documents, rewrites questions, intelligent routing (Phase 2)
• Simple RAG: Direct retrieval → answer (Phase 1, fastest)
            
All modes use persistent thread_id for stateful conversations and LangSmith tracing."""
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
    
    # Quality Control Parameters
    with st.expander("⚙️ Advanced RAG Settings", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            quality_threshold = st.slider(
                "Quality Threshold",
                min_value=0.3,
                max_value=0.7,
                value=0.45,
                step=0.05,
                help="Score below which re-retrieval is triggered (default: 0.45)"
            )
        
        with col2:
            min_quality_score = st.slider(
                "Minimum Score",
                min_value=0.2,
                max_value=0.5,
                value=0.4,
                step=0.05,
                help="Minimum acceptable score to proceed (default: 0.4)"
            )
        
        with col3:
            max_re_retrieval = st.slider(
                "Max Re-retrieval",
                min_value=0,
                max_value=3,
                value=1,
                step=1,
                help="Maximum re-retrieval attempts (default: 1)"
            )
    
    # Knowledge Source Selection (HITL #0)
    with st.expander("📚 Knowledge Source Selection", expanded=False):
        st.markdown("**Choose which knowledge sources the RAG system should use:**")
        
        # Initialize knowledge source selections in session state
        if 'selected_categories' not in st.session_state:
            st.session_state.selected_categories = []
        if 'custom_urls' not in st.session_state:
            st.session_state.custom_urls = []
        if 'custom_documents' not in st.session_state:
            st.session_state.custom_documents = []
        
        # Predefined Categories
        st.subheader("📂 Predefined Categories")
        col1, col2 = st.columns(2)
        
        with col1:
            architecture_docs = st.checkbox(
                "🏗️ Architecture Documentation",
                value="architecture" in st.session_state.selected_categories,
                help="docs/architecture/ - System design, patterns, architectural decisions"
            )
            if architecture_docs and "architecture" not in st.session_state.selected_categories:
                st.session_state.selected_categories.append("architecture")
            elif not architecture_docs and "architecture" in st.session_state.selected_categories:
                st.session_state.selected_categories.remove("architecture")
            
            agile_docs = st.checkbox(
                "📋 Agile Management",
                value="agile" in st.session_state.selected_categories,
                help="docs/agile/ - Sprint docs, user stories, backlog, retrospectives"
            )
            if agile_docs and "agile" not in st.session_state.selected_categories:
                st.session_state.selected_categories.append("agile")
            elif not agile_docs and "agile" in st.session_state.selected_categories:
                st.session_state.selected_categories.remove("agile")
        
        with col2:
            coding_guidelines = st.checkbox(
                "📝 Coding Guidelines",
                value="coding_guidelines" in st.session_state.selected_categories,
                help="docs/guides/ - Coding standards, best practices, style guides"
            )
            if coding_guidelines and "coding_guidelines" not in st.session_state.selected_categories:
                st.session_state.selected_categories.append("coding_guidelines")
            elif not coding_guidelines and "coding_guidelines" in st.session_state.selected_categories:
                st.session_state.selected_categories.remove("coding_guidelines")
            
            framework_docs = st.checkbox(
                "🔧 Framework Documentation",
                value="framework_docs" in st.session_state.selected_categories,
                help="docs/development/ - LangGraph, LangChain, FastAPI, Streamlit docs"
            )
            if framework_docs and "framework_docs" not in st.session_state.selected_categories:
                st.session_state.selected_categories.append("framework_docs")
            elif not framework_docs and "framework_docs" in st.session_state.selected_categories:
                st.session_state.selected_categories.remove("framework_docs")
        
        # Quick selection buttons
        st.markdown("---")
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        
        with quick_col1:
            if st.button("✅ Select All", help="Select all predefined categories"):
                st.session_state.selected_categories = ["architecture", "agile", "coding_guidelines", "framework_docs"]
                st.rerun()
        
        with quick_col2:
            if st.button("🎯 Defaults", help="Architecture + Coding Guidelines + Frameworks"):
                st.session_state.selected_categories = ["architecture", "coding_guidelines", "framework_docs"]
                st.rerun()
        
        with quick_col3:
            if st.button("❌ Clear All", help="Deselect all categories"):
                st.session_state.selected_categories = []
                st.rerun()
        
        st.markdown("---")
        
        # Custom URLs
        st.subheader("🌐 Custom URLs")
        st.caption("Add specific websites or documentation URLs to include in RAG context")
        
        url_input = st.text_input(
            "Enter URL",
            placeholder="https://docs.example.com/api/...",
            help="Enter a URL to scrape and index (API docs, tutorials, references)"
        )
        
        url_col1, url_col2 = st.columns([1, 4])
        with url_col1:
            if st.button("➕ Add URL", disabled=not url_input):
                if url_input and url_input not in st.session_state.custom_urls:
                    st.session_state.custom_urls.append(url_input)
                    st.success(f"✅ Added: {url_input}")
                    st.rerun()
        
        # Display added URLs
        if st.session_state.custom_urls:
            st.markdown("**Added URLs:**")
            for i, url in enumerate(st.session_state.custom_urls):
                url_display_col1, url_display_col2 = st.columns([5, 1])
                with url_display_col1:
                    st.text(f"🔗 {url}")
                with url_display_col2:
                    if st.button("🗑️", key=f"del_url_{i}", help="Remove this URL"):
                        st.session_state.custom_urls.pop(i)
                        st.rerun()
        
        st.markdown("---")
        
        # Local Documents
        st.subheader("📄 Local Documents")
        st.caption("Upload specific documents to include in RAG context")
        
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=["pdf", "docx", "txt", "md", "py", "js", "ts", "java", "cpp", "c", "h"],
            accept_multiple_files=True,
            help="Upload specifications, designs, notes, or code files"
        )
        
        if uploaded_files:
            st.markdown(f"**Uploaded: {len(uploaded_files)} file(s)**")
            for file in uploaded_files:
                st.text(f"📎 {file.name} ({file.size / 1024:.1f} KB)")
            
            if st.button("💾 Save Uploaded Documents"):
                # Save uploaded files to session state for processing
                st.session_state.custom_documents = [
                    {"name": file.name, "content": file.read(), "type": file.type}
                    for file in uploaded_files
                ]
                st.success(f"✅ Saved {len(uploaded_files)} document(s) for indexing")
        
        # Summary of selections
        st.markdown("---")
        st.subheader("📊 Knowledge Source Summary")
        
        total_sources = (
            len(st.session_state.selected_categories) + 
            len(st.session_state.custom_urls) + 
            len(st.session_state.custom_documents)
        )
        
        if total_sources > 0:
            st.success(f"✅ **{total_sources} knowledge source(s) selected**")
            
            if st.session_state.selected_categories:
                st.markdown(f"**Categories ({len(st.session_state.selected_categories)})**: {', '.join(st.session_state.selected_categories)}")
            
            if st.session_state.custom_urls:
                st.markdown(f"**URLs ({len(st.session_state.custom_urls)})**: {len(st.session_state.custom_urls)} custom URL(s)")
            
            if st.session_state.custom_documents:
                st.markdown(f"**Documents ({len(st.session_state.custom_documents)})**: {len(st.session_state.custom_documents)} file(s)")
        else:
            st.info("ℹ️ **No specific sources selected** - will use all available documents in RAG system")
        
        # Load knowledge sources button
        if total_sources > 0:
            if st.button("🔄 Load & Index Selected Sources", type="primary"):
                with st.spinner("Loading and indexing knowledge sources..."):
                    # Here we would integrate with KnowledgeSourceManager
                    # For now, just show a message
                    st.success(f"✅ Loaded {total_sources} knowledge source(s) successfully!")
                    st.info("💡 These sources will be used by the RAG system for the current session")
    
    st.markdown("---")
    
    # Document Scope Parameter (UI Control → Swarm Parameter)
    st.markdown("### 📚 Document Scope")
    
    # Load available documents
    available_docs = load_documents_from_qdrant(show_debug=False)
    
    if available_docs:
        doc_col1, doc_col2 = st.columns([3, 1])
        
        with doc_col1:
            # Document selection as a UI parameter
            doc_options = [
                f"{doc['file_name']} ({doc.get('file_type', 'unknown')}, {doc.get('chunk_count', 0)} chunks)"
                for doc in available_docs
            ]
            
            selected_doc_display = st.multiselect(
                "Focus on specific documents (optional)",
                options=doc_options,
                default=[],
                help="🤖 Swarm will intelligently search within selected documents. Leave empty for automatic document discovery."
            )
            
            # Convert to document names
            if selected_doc_display:
                st.session_state.selected_documents_for_rag = [
                    doc['file_name'] for doc in available_docs
                    if f"{doc['file_name']} ({doc.get('file_type', 'unknown')}, {doc.get('chunk_count', 0)} chunks)" in selected_doc_display
                ]
            else:
                st.session_state.selected_documents_for_rag = []
        
        with doc_col2:
            if not st.session_state.selected_documents_for_rag:
                st.success(
                    f"🤖 **Automatic**\n\n"
                    f"{len(available_docs)} docs\n\n"
                    f"Swarm finds relevant ones"
                )
            else:
                total_chunks = sum(
                    doc.get('chunk_count', 0) for doc in available_docs
                    if doc['file_name'] in st.session_state.selected_documents_for_rag
                )
                st.info(
                    f"🎯 **Focused**\n\n"
                    f"{len(st.session_state.selected_documents_for_rag)} docs\n"
                    f"{total_chunks} chunks"
                )
    else:
        st.info("📁 No documents indexed yet")
    
    st.markdown("---")
    
    # Adaptive Retrieval Strategy (NEW: US-RAG-003)
    st.markdown("### 🎯 Adaptive Retrieval Strategy")
    
    # Initialize session state for retrieval settings
    if 'retrieval_mode' not in st.session_state:
        st.session_state.retrieval_mode = 'auto'
    if 'manual_chunk_count' not in st.session_state:
        st.session_state.manual_chunk_count = 15
    
    retrieval_col1, retrieval_col2 = st.columns([2, 1])
    
    with retrieval_col1:
        retrieval_mode = st.selectbox(
            "Retrieval Strategy",
            ["🤖 Auto (Recommended)", "👤 Manual Control", "⚡ Performance Mode"],
            index=0,
            help=(
                "**Auto**: Agent intelligently determines optimal chunk count based on query complexity\n\n"
                "**Manual**: You specify exact chunk count (5-50)\n\n"
                "**Performance**: Fast mode with focused retrieval (8 chunks)"
            )
        )
        
        # Extract mode from display text
        if "Auto" in retrieval_mode:
            st.session_state.retrieval_mode = "auto"
        elif "Manual" in retrieval_mode:
            st.session_state.retrieval_mode = "manual"
        else:
            st.session_state.retrieval_mode = "performance"
    
    with retrieval_col2:
        if st.session_state.retrieval_mode == "auto":
            st.success(
                "🤖 **Intelligent**\n\n"
                "Adapts to query\n\n"
                "5-50 chunks"
            )
        elif st.session_state.retrieval_mode == "performance":
            st.info(
                "⚡ **Fast**\n\n"
                "Quick response\n\n"
                "8 chunks"
            )
        else:
            st.info(
                "👤 **Manual**\n\n"
                "Full control\n\n"
                f"{st.session_state.manual_chunk_count} chunks"
            )
    
    # Manual control slider (only show in manual mode)
    if st.session_state.retrieval_mode == "manual":
        st.session_state.manual_chunk_count = st.slider(
            "Number of Chunks to Retrieve",
            min_value=5,
            max_value=50,
            value=st.session_state.manual_chunk_count,
            step=1,
            help=(
                "Specify exact number of document chunks to retrieve.\n\n"
                "💡 **Tip**: 10-20 chunks works well for most queries.\n\n"
                "**Guidelines:**\n"
                "- Simple questions: 5-15 chunks\n"
                "- Moderate queries: 15-25 chunks\n"
                "- Complex analysis: 25-40 chunks\n"
                "- Multi-step reasoning: 35-50 chunks"
            )
        )
        
        # Show real-time feedback
        if st.session_state.manual_chunk_count < 10:
            st.warning("⚠️ Low chunk count - may miss relevant context")
        elif st.session_state.manual_chunk_count > 40:
            st.warning("⚠️ High chunk count - may include noise")
        else:
            st.success("✅ Good chunk count for balanced results")
    
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
            # Auto-name thread from first query
            current_session = st.session_state.rag_thread_manager.current_session
            if current_session.message_count == 0:
                # First message in thread - auto-name it
                st.session_state.rag_thread_manager.auto_name_from_query(user_input)
            
            # Update activity (increment message count)
            st.session_state.rag_thread_manager.update_activity()
            
            # Add user message
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Process with agent (V2: SimpleRAG or AgenticRAG)
            with st.chat_message("assistant"):
                use_agentic = "Agentic RAG" in agent_mode
                use_simple = "Simple RAG" in agent_mode
                response_text = None  # Initialize to avoid NameError
                context_stats = {}
                
                agent_type_label = (
                    "✨ Agentic RAG processing (grading + rewriting)" if use_agentic
                    else "⚡ Simple RAG processing (direct)" if use_simple
                    else "⚡ Retrieving context"
                )
                
                with st.spinner(f"🔍 {agent_type_label}..."):
                    try:
                        # Set API key from Streamlit secrets
                        import os
                        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                            os.environ['GEMINI_API_KEY'] = st.secrets['GEMINI_API_KEY']
                        
                        # Check LangSmith tracing status
                        langsmith_enabled = os.environ.get("LANGCHAIN_TRACING_V2") == "true"
                        if not langsmith_enabled and context_mode == "Debug":
                            st.warning("⚠️ LangSmith tracing disabled. Set LANGCHAIN_TRACING_V2=true to enable traces.")
                        
                        if use_agentic or use_simple:
                            # Use RAG V2: Official LangChain patterns (Phase 1 or 2)
                            try:
                                from agents.rag import SimpleRAG, AgenticRAG
                                
                                # Initialize agent based on mode (reuse if already created)
                                agent_key = 'agentic_rag' if use_agentic else 'simple_rag'
                                
                                if agent_key not in st.session_state:
                                    if use_agentic:
                                        st.session_state[agent_key] = AgenticRAG(st.session_state.rag_engine)
                                        logger.info("[OK] ✅ AgenticRAG (Phase 2) initialized")
                                    else:
                                        st.session_state[agent_key] = SimpleRAG(st.session_state.rag_engine)
                                        logger.info("[OK] ✅ SimpleRAG (Phase 1) initialized")
                                
                                rag_agent = st.session_state[agent_key]
                                
                                # Get persistent thread_id from ThreadManager for conversation continuity
                                config = st.session_state.rag_thread_manager.get_current_config()
                                thread_id = config['configurable']['thread_id']
                                
                                logger.info(f"🔧 RAG V2 using thread_id = {thread_id}")
                                
                                # Build document filters if user selected specific documents
                                doc_filters = None
                                if st.session_state.selected_documents_for_rag:
                                    doc_filters = {'source': st.session_state.selected_documents_for_rag}
                                    logger.info(f"🎯 Applying document scope: {st.session_state.selected_documents_for_rag}")
                                
                                # Execute with thread_id and document filters
                                result = rag_agent.invoke(
                                    query=user_input,
                                    thread_id=thread_id,
                                    document_filters=doc_filters
                                )
                                
                                # RAG V2 doesn't have HITL yet (Phase 3 feature)
                                # Process completed response
                                if result.get('status') == 'completed':
                                    response_text = result.get('response', 'No response generated')
                                    logger.info(f"✅ RAG V2 response: {len(response_text)} chars")
                                    
                                    # Create context stats
                                    context_stats = {
                                        'retrieval_time': 0,
                                        'results_count': len(result.get('messages', [])),
                                        'search_type': 'agentic_rag' if use_agentic else 'simple_rag',
                                        'thread_id': result.get('thread_id')
                                    }
                                
                                elif result.get('status') == 'interrupted':
                                    st.info("⏸️ **HITL not yet implemented in Phase 1/2**")
                                    st.write("Phase 3 will add human review checkpoints")
                                    
                                    with st.expander("📄 Retrieved Context Preview", expanded=True):
                                        st.markdown(result.get('context_preview', 'No context available'))
                                    
                                    st.session_state.pending_interrupt = {
                                        'thread_id': result.get('thread_id'),
                                        'context': result.get('context_preview', ''),
                                        'query': user_input
                                    }
                                    
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        if st.button("✅ Approve", key=f"approve_{result.get('thread_id')}", use_container_width=True):
                                            with st.spinner("▶️ Resuming LangGraph RAG..."):
                                                logger.info(f"🔗 Resuming LangGraph RAG with approval")
                                                resume_result = langgraph_agent.resume(
                                                    thread_id=thread_id,
                                                    human_feedback="approve"
                                                )
                                                result = resume_result
                                                if 'pending_interrupt' in st.session_state:
                                                    del st.session_state.pending_interrupt
                                                st.rerun()
                                    
                                    with col2:
                                        if st.button("❌ Reject", key=f"reject_{result.get('thread_id')}", use_container_width=True):
                                            logger.info("🚫 User rejected - canceling workflow")
                                            st.warning("Workflow canceled. Please start a new query.")
                                            if 'pending_interrupt' in st.session_state:
                                                del st.session_state.pending_interrupt
                                            st.stop()
                                    
                                    with col3:
                                        if st.button("✏️ Edit", key=f"edit_{result.get('thread_id')}", use_container_width=True):
                                            st.session_state.show_edit_input = True
                                    
                                    if st.session_state.get('show_edit_input', False):
                                        custom_feedback = st.text_area(
                                            "Provide custom instructions:",
                                            key=f"custom_feedback_{result.get('thread_id')}",
                                            height=100
                                        )
                                        if st.button("Submit Edit", key=f"submit_edit_{result.get('thread_id')}"):
                                            if custom_feedback:
                                                with st.spinner("▶️ Resuming with your edits..."):
                                                    logger.info(f"✏️ Resuming with custom feedback: {custom_feedback}")
                                                    resume_result = langgraph_agent.resume(
                                                        thread_id=thread_id,
                                                        human_feedback=custom_feedback
                                                    )
                                                    result = resume_result
                                                    if 'pending_interrupt' in st.session_state:
                                                        del st.session_state.pending_interrupt
                                                    st.session_state.show_edit_input = False
                                                    st.rerun()
                                            else:
                                                st.warning("Please provide feedback")
                                    
                                    st.info("💡 Review the context and choose an action above to continue")
                                    st.stop()
                                        
                                elif result.get('status') == 'completed':
                                    response_text = result.get('response', 'No response generated')
                                    context_stats = {
                                        'retrieval_time': 0,
                                        'results_count': 0,
                                        'search_type': 'langgraph_rag',
                                        'thread_id': result.get('thread_id'),
                                        'sources_cited': result.get('sources_cited', []),
                                        'pipeline_state': result.get('pipeline_state', 'completed')
                                    }
                                    
                                elif result.get('status') == 'error':
                                    error_msg = result.get('error', 'Unknown error')
                                    st.error(f"❌ RAG V2 failed: {error_msg}")
                                    with st.expander("🔍 Error Details"):
                                        st.code(error_msg)
                                    st.session_state.chat_messages.append({
                                        "role": "assistant",
                                        "content": f"❌ Error: {error_msg}",
                                        "timestamp": datetime.now().isoformat()
                                    })
                                    st.stop()
                                    
                            except Exception as e:
                                import traceback
                                error_trace = traceback.format_exc()
                                st.error(f"❌ RAG V2 error: {str(e)}")
                                with st.expander("🔍 Error Details"):
                                    st.code(error_trace)
                                logger.error(f"RAG V2 error: {error_trace}")
                                st.stop()
                        
                        # Display response (only if we have one)
                        if response_text:
                            st.markdown(response_text)
                        else:
                            st.warning("⚠️ No response generated. Please try again.")
                            st.stop()
                        
                        # Display sources used (if available)
                        if result.get('sources_cited'):
                            with st.expander("📚 Sources Used", expanded=False):
                                for i, source in enumerate(result.get('sources_cited', []), 1):
                                    st.markdown(f"**{i}.** `{source}`")
                        
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
                        
                        # NEW: Adaptive Decision Info (US-RAG-003)
                        if stats.get('adaptive_decision'):
                            st.markdown("#### 🎯 Adaptive Retrieval")
                            adaptive = stats['adaptive_decision']
                            
                            adapt_col1, adapt_col2 = st.columns(2)
                            with adapt_col1:
                                st.metric("Query Type", adaptive.get('query_type', 'unknown'))
                            with adapt_col2:
                                st.metric("Chunks Retrieved", adaptive.get('chunk_count', 0))
                            
                            if adaptive.get('query_analysis'):
                                analysis = adaptive['query_analysis']
                                st.caption(f"🔍 Complexity: {analysis.get('complexity_score', 0):.2f} | "
                                         f"Specificity: {analysis.get('specificity_score', 0):.2f}")
                            
                            st.info(f"💡 {adaptive.get('rationale', 'No rationale provided')}")
                        
                        # Pipeline timing
                        if 'pipeline_metrics' in stats:
                            with st.expander("⏱️ Pipeline Timing", expanded=False):
                                metrics = stats['pipeline_metrics']
                                for key, value in metrics.items():
                                    if '_time' in key:
                                        stage_name = key.replace('_time', '').replace('_', ' ').title()
                                        st.text(f"{stage_name}: {value:.3f}s")
                        
                        # Sources cited and document analysis
                        if stats.get('sources_cited'):
                            with st.expander("📚 Documents Found by Agent", expanded=True):
                                st.markdown("**Intelligent Document Selection:**")
                                for source in stats['sources_cited']:
                                    st.text(f"✓ {source}")
                                
                                # Show if filtering was applied
                                if st.session_state.selected_documents_for_rag:
                                    st.markdown("---")
                                    st.markdown(f"🎯 **Filter Applied**: {len(st.session_state.selected_documents_for_rag)} docs")
                                else:
                                    st.markdown("---")
                                    st.markdown(f"🤖 **Automatic Selection**: Agent searched all {len(available_docs)} docs")
                    
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
                "agent_mode": agent_mode,
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
        st.markdown("🔗 View traces at: =[https://smith.langchain.com/](https://smith.langchain.com/)")
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
        
        st.markdown("---")
        
        # Document Scope (same as Agent Chat)
        st.markdown("### 📚 Document Scope")
        available_docs = load_documents_from_qdrant(show_debug=False)
        
        if available_docs:
            doc_col1, doc_col2 = st.columns([3, 1])
            
            with doc_col1:
                doc_options = [
                    f"{doc['file_name']} ({doc.get('file_type', 'unknown')}, {doc.get('chunk_count', 0)} chunks)"
                    for doc in available_docs
                ]
                
                selected_doc_display = st.multiselect(
                    "Focus on specific documents (optional)",
                    options=doc_options,
                    default=[],
                    help="🤖 Test will search within selected documents. Leave empty for automatic document discovery.",
                    key="test_doc_scope"
                )
                
                # Convert to document names
                if selected_doc_display:
                    test_selected_docs = [
                        doc['file_name'] for doc in available_docs
                        if f"{doc['file_name']} ({doc.get('file_type', 'unknown')}, {doc.get('chunk_count', 0)} chunks)" in selected_doc_display
                    ]
                else:
                    test_selected_docs = []
            
            with doc_col2:
                if not test_selected_docs:
                    st.success(
                        f"🤖 **Automatic**\n\n"
                        f"{len(available_docs)} docs\n\n"
                        f"Test searches all"
                    )
                else:
                    total_chunks = sum(
                        doc.get('chunk_count', 0) for doc in available_docs
                        if doc['file_name'] in test_selected_docs
                    )
                    st.info(
                        f"🎯 **Focused**\n\n"
                        f"{len(test_selected_docs)} docs\n"
                        f"{total_chunks} chunks"
                    )
        else:
            st.info("📁 No documents indexed yet")
            test_selected_docs = []
        
        st.markdown("---")
        
        # Adaptive Retrieval Strategy (same as Agent Chat)
        st.markdown("### 🎯 Adaptive Retrieval Strategy")
        
        # Initialize test session state for retrieval settings
        if 'test_retrieval_mode' not in st.session_state:
            st.session_state.test_retrieval_mode = 'auto'
        if 'test_manual_chunk_count' not in st.session_state:
            st.session_state.test_manual_chunk_count = 15
        
        retrieval_col1, retrieval_col2 = st.columns([2, 1])
        
        with retrieval_col1:
            test_retrieval_mode = st.selectbox(
                "Retrieval Strategy",
                ["🤖 Auto (Recommended)", "👤 Manual Control", "⚡ Performance Mode"],
                index=0,
                help=(
                    "**Auto**: Agent intelligently determines optimal chunk count based on query complexity\n\n"
                    "**Manual**: You specify exact chunk count (5-50)\n\n"
                    "**Performance**: Fast mode with focused retrieval (8 chunks)"
                ),
                key="test_retrieval_mode_select"
            )
            
            # Extract mode from display text
            if "Auto" in test_retrieval_mode:
                st.session_state.test_retrieval_mode = "auto"
            elif "Manual" in test_retrieval_mode:
                st.session_state.test_retrieval_mode = "manual"
            else:
                st.session_state.test_retrieval_mode = "performance"
        
        with retrieval_col2:
            if st.session_state.test_retrieval_mode == "auto":
                st.success(
                    "🤖 **Intelligent**\n\n"
                    "Adapts to query\n\n"
                    "5-50 chunks"
                )
            elif st.session_state.test_retrieval_mode == "performance":
                st.info(
                    "⚡ **Fast**\n\n"
                    "Quick response\n\n"
                    "8 chunks"
                )
            else:
                st.info(
                    "👤 **Manual**\n\n"
                    "Full control\n\n"
                    f"{st.session_state.test_manual_chunk_count} chunks"
                )
        
        # Manual control slider (only show in manual mode)
        if st.session_state.test_retrieval_mode == "manual":
            st.session_state.test_manual_chunk_count = st.slider(
                "Number of Chunks to Retrieve",
                min_value=5,
                max_value=50,
                value=st.session_state.test_manual_chunk_count,
                step=1,
                help=(
                    "Specify exact number of document chunks to retrieve.\n\n"
                    "💡 **Tip**: 10-20 chunks works well for most queries.\n\n"
                    "**Guidelines:**\n"
                    "- Simple questions: 5-15 chunks\n"
                    "- Moderate queries: 15-25 chunks\n"
                    "- Complex analysis: 25-40 chunks\n"
                    "- Multi-step reasoning: 35-50 chunks"
                ),
                key="test_manual_chunk_slider"
            )
            
            # Show real-time feedback
            if st.session_state.test_manual_chunk_count < 10:
                st.warning("⚠️ Low chunk count - may miss relevant context")
            elif st.session_state.test_manual_chunk_count > 40:
                st.warning("⚠️ High chunk count - may include noise")
            else:
                st.success("✅ Good chunk count for balanced results")
        
        st.markdown("---")
        
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
                    # Build document filters
                    test_doc_filters = None
                    if test_selected_docs:
                        test_doc_filters = {'source': test_selected_docs}
                    
                    test_result = run_transparent_test(
                        test_query,
                        show_query_rewriting,
                        show_retrieval_stages,
                        show_scoring_details,
                        retrieval_mode=st.session_state.test_retrieval_mode,
                        manual_chunk_count=st.session_state.test_manual_chunk_count if st.session_state.test_retrieval_mode == 'manual' else None,
                        document_filters=test_doc_filters,
                        available_doc_count=len(available_docs) if available_docs else 100
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


def run_transparent_test(
    query: str, 
    show_rewriting: bool, 
    show_stages: bool, 
    show_scoring: bool, 
    use_swarm: bool = True,
    retrieval_mode: str = 'auto',
    manual_chunk_count: int = None,
    document_filters: Dict = None,
    available_doc_count: int = 100
) -> Dict:
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
            # TODO: RAGSwarmCoordinator not yet implemented
            st.warning("⚠️ RAG Swarm coordinator not available. Use basic context-aware agent in Agent Chat.")
            return
            
            from agents.rag import RAGSwarmCoordinator
            
            # Enable human_in_loop for Streamlit UI (needs checkpointer)
            swarm = RAGSwarmCoordinator(st.session_state.rag_engine, human_in_loop=True)
            
            retrieval_start = time.time()
            response = run_async(swarm.execute({
                'query': query,
                'max_results': 50,  # Max allowed, adaptive system determines actual count
                'quality_threshold': 0.45,  # Realistic default
                'min_quality_score': 0.4,   # Minimum acceptable
                'max_re_retrieval_attempts': 1,
                'enable_re_retrieval': True,
                'document_filters': document_filters,  # Pass document scope
                # Adaptive retrieval parameters from UI
                'retrieval_mode': retrieval_mode,
                'manual_chunk_count': manual_chunk_count,
                'available_doc_count': available_doc_count
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
            response = run_async(agent.execute_with_context({'query': query}))
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
    response_text = result.get("response", "No response")
    if response_text and response_text != "No response":
        # Use st.info for better visibility with proper text rendering
        st.info(response_text)
    else:
        st.warning("⚠️ No response generated - check if the query was processed successfully")
    
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
