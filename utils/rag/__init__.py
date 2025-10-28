"""
RAG Utilities Module
===================

Utilities for RAG (Retrieval-Augmented Generation) system including:
- Document loading (PDF, DOCX, TXT, MD, HTML, code files)
- Website scraping
- Batch processing
- Progress tracking
- Adaptive chunk retrieval
- Query analysis

All built on LangChain for maximum compatibility and robustness.
"""

# Import core components (always available)
from .query_analyzer import QueryAnalyzer, QueryAnalysis
from .adaptive_retrieval_strategy import AdaptiveRetrievalStrategy, RetrievalContext

# Import document loader conditionally (requires langchain-community)
try:
    from .document_loader import (
        DocumentLoader,
        load_document,
        load_documents,
        load_website,
        load_directory
    )
    DOCUMENT_LOADER_AVAILABLE = True
except ImportError:
    # Document loader not available - provide graceful fallback
    DocumentLoader = None
    load_document = None
    load_documents = None
    load_website = None
    load_directory = None
    DOCUMENT_LOADER_AVAILABLE = False

__all__ = [
    'DocumentLoader',
    'load_document',
    'load_documents',
    'load_website',
    'load_directory',
    'QueryAnalyzer',
    'QueryAnalysis',
    'AdaptiveRetrievalStrategy',
    'RetrievalContext',
    'DOCUMENT_LOADER_AVAILABLE'
]
