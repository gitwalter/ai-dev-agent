"""
RAG Utilities Module
===================

Utilities for RAG (Retrieval-Augmented Generation) system including:
- Document loading (PDF, DOCX, TXT, MD, HTML, code files)
- Website scraping
- Batch processing
- Progress tracking

All built on LangChain for maximum compatibility and robustness.
"""

from .document_loader import (
    DocumentLoader,
    load_document,
    load_documents,
    load_website,
    load_directory
)

__all__ = [
    'DocumentLoader',
    'load_document',
    'load_documents',
    'load_website',
    'load_directory'
]
