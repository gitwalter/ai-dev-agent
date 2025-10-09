#!/usr/bin/env python3
"""
RAG Document Loader
===================

Comprehensive document loading system for RAG using LangChain loaders.

Supports:
- PDF files (LangChain PyPDFLoader, PDFPlumberLoader)
- DOCX files (LangChain Docx2txtLoader)
- Text files (LangChain TextLoader)
- Markdown (LangChain UnstructuredMarkdownLoader)
- HTML (LangChain UnstructuredHTMLLoader)
- Code files (LangChain TextLoader with language detection)
- Web scraping (LangChain WebBaseLoader)
- Batch processing with progress tracking

Author: AI Development Agent
Created: 2025-01-02
Purpose: US-RAG-001 - Document Loading System (LangChain-based)
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import asyncio

# LangChain document loaders
try:
    from langchain_community.document_loaders import (
        PyPDFLoader,
        PDFPlumberLoader,
        Docx2txtLoader,
        TextLoader,
        UnstructuredMarkdownLoader,
        UnstructuredHTMLLoader,
        WebBaseLoader,
        DirectoryLoader,
    )
    from langchain.schema import Document
    from langchain.text_splitter import (
        RecursiveCharacterTextSplitter,
        HTMLHeaderTextSplitter,
        MarkdownHeaderTextSplitter,
    )
    LANGCHAIN_LOADERS_AVAILABLE = True
except ImportError:
    LANGCHAIN_LOADERS_AVAILABLE = False
    Document = None
    RecursiveCharacterTextSplitter = None
    HTMLHeaderTextSplitter = None
    MarkdownHeaderTextSplitter = None

logger = logging.getLogger(__name__)


class DocumentLoader:
    """
    Comprehensive document loader for RAG system using LangChain loaders.
    
    Uses LangChain's robust document loaders with fallback support.
    """
    
    def __init__(self, qdrant_client=None):
        """
        Initialize document loader with LangChain loaders and duplicate detection.
        
        Args:
            qdrant_client: Optional Qdrant client for duplicate detection
        """
        if not LANGCHAIN_LOADERS_AVAILABLE:
            raise ImportError("LangChain document loaders not available. Install: pip install langchain-community unstructured")
        
        # Map file extensions to LangChain loader classes
        self.loader_map = {
            'pdf': (PyPDFLoader, PDFPlumberLoader),  # Primary, fallback
            'docx': (Docx2txtLoader,),
            'doc': (Docx2txtLoader,),
            'txt': (TextLoader,),
            'md': (UnstructuredMarkdownLoader, TextLoader),  # Primary, fallback
            'html': (UnstructuredHTMLLoader, TextLoader),
            'py': (TextLoader,),
            'js': (TextLoader,),
            'ts': (TextLoader,),
            'java': (TextLoader,),
            'cpp': (TextLoader,),
            'c': (TextLoader,),
            'h': (TextLoader,),
            'css': (TextLoader,),
            'json': (TextLoader,),
            'yaml': (TextLoader,),
            'yml': (TextLoader,),
        }
        
        # Initialize text splitters for different document types
        self._initialize_splitters()
        
        # Qdrant client for duplicate detection
        self.qdrant_client = qdrant_client
        
        self.load_stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'total_documents': 0,  # LangChain documents (can be multiple per file)
            'total_characters': 0,
            'total_chunks': 0,  # After splitting
            'duplicates_detected': 0,  # NEW: Duplicate tracking
            'duplicates_skipped': 0   # NEW: Duplicates not indexed
        }
    
    async def _extract_document_metadata(self, document: Optional[Document], source: str) -> Dict[str, Any]:
        """
        INTELLIGENT metadata extraction using LLM for optimal RAG retrieval.
        
        Based on RAG best practices:
        - Uses LLM to understand document semantics
        - Generates query-relevant summaries
        - Extracts semantic keywords
        - Classifies document type intelligently
        
        Args:
            document: LangChain Document object
            source: Document source (URL or file path)
            
        Returns:
            Dictionary with intelligent metadata
        """
        import re
        from bs4 import BeautifulSoup
        import json
        
        # Default metadata (fallback)
        metadata = {
            'source': source,
            'title': None,
            'description': None,
            'summary': None,
            'keywords': [],
            'doc_type': None,
            'author': None,
            'date': None
        }
        
        if not document or not document.page_content:
            return metadata
        
        try:
            # Clean content for LLM processing
            content = document.page_content
            text_content = BeautifulSoup(content, 'html.parser').get_text()
            
            # Limit content for LLM (first 3000 chars to capture essence)
            content_sample = text_content[:3000]
            
            # Use LLM for intelligent metadata extraction
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain.schema import SystemMessage, HumanMessage
                
                # Get API key
                api_key = self._get_gemini_api_key()
                if not api_key:
                    logger.warning("No Gemini API key, falling back to regex extraction")
                    return self._extract_metadata_fallback(content, source)
                
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-lite",  # Fast and cheap
                    google_api_key=api_key,
                    temperature=0.3,  # Low temperature for factual extraction
                    convert_system_message_to_human=True
                )
                
                system_prompt = """You are a metadata extraction expert for RAG systems.
Your task is to analyze document content and extract key metadata for optimal retrieval.

Extract and return JSON with:
- title: Clear, descriptive title (max 100 chars)
- summary: 2-3 sentence summary highlighting main topic and key points (max 300 chars)
- keywords: List of 5-8 most relevant keywords/phrases for search
- doc_type: One of [tutorial, documentation, blog, research, guide, reference, article]
- topics: List of 3-5 main topics/themes covered

Focus on query-relevant information that helps match this document to user questions."""

                user_prompt = f"""Extract metadata from this document:

{content_sample}

Respond with ONLY valid JSON (no markdown, no explanations)."""

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                
                response = await llm.ainvoke(messages)
                
                # Parse LLM response
                response_text = response.content.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith('```'):
                    response_text = re.sub(r'```(?:json)?\n?', '', response_text)
                    response_text = response_text.strip()
                
                llm_metadata = json.loads(response_text)
                
                # Update metadata with LLM results
                metadata.update({
                    'title': llm_metadata.get('title'),
                    'summary': llm_metadata.get('summary'),
                    'description': llm_metadata.get('summary', '')[:200],  # Shorter version
                    'keywords': llm_metadata.get('keywords', [])[:8],
                    'doc_type': llm_metadata.get('doc_type', 'article'),
                    'topics': llm_metadata.get('topics', [])
                })
                
                logger.info(f"🤖 LLM extracted metadata: title='{metadata['title'][:50]}...', "
                           f"keywords={len(metadata['keywords'])}, type={metadata['doc_type']}")
                
            except Exception as llm_error:
                logger.warning(f"LLM metadata extraction failed: {llm_error}, using fallback")
                return self._extract_metadata_fallback(content, source)
            
            # Extract author and date with regex (LLM not needed for these)
            author_patterns = [
                r'(?:by|author|written by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            ]
            for pattern in author_patterns:
                author_match = re.search(pattern, content, re.IGNORECASE)
                if author_match:
                    metadata['author'] = author_match.group(1).strip()
                    break
            
            date_patterns = [
                r'(\w+ \d{1,2},? \d{4})',
                r'(\d{4}-\d{2}-\d{2})',
            ]
            for pattern in date_patterns:
                date_match = re.search(pattern, content)
                if date_match:
                    metadata['date'] = date_match.group(1)
                    break
            
        except Exception as e:
            logger.error(f"Metadata extraction error: {e}")
            return self._extract_metadata_fallback(content if 'content' in locals() else '', source)
        
        return metadata
    
    def _extract_metadata_fallback(self, content: str, source: str) -> Dict[str, Any]:
        """Fallback regex-based metadata extraction if LLM fails."""
        import re
        from bs4 import BeautifulSoup
        
        metadata = {'source': source, 'keywords': []}
        
        try:
            # Extract title from H1
            h1_match = re.search(r'<h1[^>]*>(.+?)</h1>', content, re.IGNORECASE | re.DOTALL)
            if h1_match:
                metadata['title'] = BeautifulSoup(h1_match.group(1), 'html.parser').get_text().strip()
            
            # Extract summary from first paragraph
            text_content = BeautifulSoup(content, 'html.parser').get_text()
            paragraphs = [p.strip() for p in text_content.split('\n') if len(p.strip()) > 100]
            if paragraphs:
                metadata['summary'] = paragraphs[0][:300]
            
            # Basic document type inference
            content_lower = content.lower()
            if 'tutorial' in content_lower:
                metadata['doc_type'] = 'tutorial'
            elif 'blog' in source.lower():
                metadata['doc_type'] = 'blog'
            else:
                metadata['doc_type'] = 'article'
                
        except Exception as e:
            logger.warning(f"Fallback extraction error: {e}")
        
        return metadata
    
    def _get_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key from environment or secrets."""
        import os
        from pathlib import Path
        
        # Try environment variable
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            return api_key
        
        # Try Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                return st.secrets['GEMINI_API_KEY']
        except:
            pass
        
        return None
    
    def check_duplicate(self, source: str, content: str) -> Dict[str, Any]:
        """
        Check if document is a duplicate using hash-based detection.
        
        RAG Best Practice: Prevent duplicate documents from degrading search quality.
        
        Args:
            source: Document source (URL or file path)
            content: Document content for hashing
            
        Returns:
            Dictionary with duplicate detection results:
            {
                'is_duplicate': bool,
                'duplicate_type': 'exact'|'source'|None,
                'existing_doc': Dict or None
            }
        """
        import hashlib
        
        result = {
            'is_duplicate': False,
            'duplicate_type': None,
            'existing_doc': None
        }
        
        if not self.qdrant_client:
            logger.debug("No Qdrant client provided, skipping duplicate detection")
            return result
        
        try:
            collection_name = "ai_dev_agent_codebase"
            
            # Check if collection exists
            collections = self.qdrant_client.get_collections().collections
            if not any(c.name == collection_name for c in collections):
                logger.debug(f"Collection {collection_name} doesn't exist yet, no duplicates")
                return result
            
            # Strategy 1: Check for exact source match (URL or filename)
            # This catches re-uploads of the same file/URL
            source_name = Path(source).name if not source.startswith('http') else source
            
            # Query Qdrant for documents with matching source
            scroll_result = self.qdrant_client.scroll(
                collection_name=collection_name,
                scroll_filter={
                    "must": [
                        {
                            "key": "metadata.source",
                            "match": {
                                "value": source
                            }
                        }
                    ]
                },
                limit=1,
                with_payload=True,
                with_vectors=False
            )
            
            existing_points = scroll_result[0]
            
            if existing_points:
                result['is_duplicate'] = True
                result['duplicate_type'] = 'source'
                result['existing_doc'] = {
                    'source': source,
                    'chunks': len(existing_points)
                }
                logger.info(f"🔍 Duplicate detected: {source} (source match, {len(existing_points)} existing chunks)")
                self.load_stats['duplicates_detected'] += 1
                return result
            
            # Strategy 2: Content hash check (for renamed files with same content)
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Note: We don't store content_hash in metadata yet, so this is a future enhancement
            # For now, source matching is sufficient
            
            logger.debug(f"✅ No duplicate found for {source}")
            
        except Exception as e:
            logger.warning(f"Duplicate detection failed: {e}")
        
        return result
    
    def _initialize_splitters(self):
        """Initialize specialized text splitters for different content types."""
        # Universal splitter for PDFs and general text
        self.general_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
        logger.info("✅ General text splitter initialized (512/50)")
        
        # HTML-specific splitter (preserves document structure)
        self.html_splitter = HTMLHeaderTextSplitter(
            headers_to_split_on=[
                ("h1", "Header 1"),
                ("h2", "Header 2"),
                ("h3", "Header 3"),
            ]
        )
        logger.info("✅ HTML header splitter initialized")
        
        # Markdown-specific splitter
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        )
        logger.info("✅ Markdown header splitter initialized")
        
        # Code-aware splitters
        self.code_splitters = {}
        for language in ['python', 'js', 'ts', 'java', 'cpp', 'go']:
            try:
                self.code_splitters[language] = RecursiveCharacterTextSplitter.from_language(
                    language=language,
                    chunk_size=512,
                    chunk_overlap=50
                )
            except Exception as e:
                logger.warning(f"Could not create {language} splitter: {e}")
        
        logger.info(f"✅ Code-aware splitters initialized ({len(self.code_splitters)} languages)")
    
    async def load_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load a single document using LangChain loaders.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Dictionary with LangChain documents and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'success': False,
                'error': f'File not found: {file_path}',
                'file_path': str(file_path)
            }
        
        # Get file extension
        ext = file_path.suffix.lstrip('.').lower()
        
        if ext not in self.loader_map:
            return {
                'success': False,
                'error': f'Unsupported format: {ext}',
                'file_path': str(file_path),
                'supported_formats': list(self.loader_map.keys())
            }
        
        # Get loader classes (primary and fallbacks)
        loader_classes = self.loader_map[ext]
        
        # Try each loader in order
        for loader_class in loader_classes:
            try:
                # Create loader instance
                loader = loader_class(str(file_path))
                
                # Load documents (LangChain returns list of Document objects)
                documents = await asyncio.to_thread(loader.load)
                
                # Calculate statistics BEFORE splitting
                total_chars = sum(len(doc.page_content) for doc in documents)
                
                # CRITICAL: Split documents into chunks for better RAG retrieval
                chunks = self.split_documents(documents, file_type=ext)
                
                logger.info(f"✂️ Split {file_path.name} into {len(chunks)} chunks (type: {ext})")
                
                # Update stats
                self.load_stats['total_files'] += 1
                self.load_stats['successful'] += 1
                self.load_stats['total_documents'] += len(documents)
                self.load_stats['total_characters'] += total_chars
                # total_chunks is updated by split_documents()
                
                return {
                    'success': True,
                    'documents': chunks,  # Return SPLIT chunks, not raw documents
                    'document_count': len(chunks),  # Count of chunks
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'file_type': ext,
                    'file_size': file_path.stat().st_size,
                    'character_count': total_chars,
                    'chunk_count': len(chunks),
                    'loader_used': loader_class.__name__,
                    'loaded_at': datetime.now().isoformat(),
                    'metadata': self._extract_file_metadata(file_path, documents)
                }
                
            except Exception as e:
                logger.warning(f"{loader_class.__name__} failed for {file_path}: {e}")
                continue
        
        # All loaders failed
        self.load_stats['total_files'] += 1
        self.load_stats['failed'] += 1
        
        logger.error(f"All loaders failed for {file_path}")
        return {
            'success': False,
            'error': f'All loaders failed for {ext} file',
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_type': ext,
            'loaders_tried': [cls.__name__ for cls in loader_classes]
        }
    
    async def load_batch(self, file_paths: List[Union[str, Path]], 
                        progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Load multiple documents with progress tracking.
        
        Args:
            file_paths: List of file paths to load
            progress_callback: Optional callback function(current, total, file_name)
            
        Returns:
            Dictionary with batch results and statistics
        """
        results = []
        total = len(file_paths)
        
        for i, file_path in enumerate(file_paths):
            # Load document
            result = await self.load_document(file_path)
            results.append(result)
            
            # Call progress callback
            if progress_callback:
                progress_callback(i + 1, total, Path(file_path).name)
        
        # Calculate statistics
        successful = sum(1 for r in results if r['success'])
        failed = sum(1 for r in results if not r['success'])
        
        return {
            'total_files': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'results': results,
            'statistics': self.load_stats.copy()
        }
    
    async def load_website(self, url: str, skip_duplicates: bool = True) -> Dict[str, Any]:
        """
        Load content from a website using LangChain WebBaseLoader with rich metadata extraction and duplicate detection.
        
        Args:
            url: Website URL to scrape
            skip_duplicates: If True, skip duplicate URLs (default: True)
            
        Returns:
            Dictionary with scraped content and metadata
        """
        try:
            # Use LangChain's WebBaseLoader
            loader = WebBaseLoader(url)
            documents = await asyncio.to_thread(loader.load)
            
            # Calculate statistics before splitting
            total_chars = sum(len(doc.page_content) for doc in documents)
            
            # CRITICAL: Check for duplicates BEFORE processing
            if skip_duplicates:
                content_sample = documents[0].page_content[:1000] if documents else ""
                dup_check = self.check_duplicate(url, content_sample)
                
                if dup_check['is_duplicate']:
                    self.load_stats['duplicates_skipped'] += 1
                    logger.warning(f"⚠️ Skipping duplicate: {url}")
                    return {
                        'success': False,
                        'skipped': True,
                        'reason': 'duplicate',
                        'duplicate_info': dup_check,
                        'url': url
                    }
            
            # CRITICAL: Extract document-level metadata for intelligent selection (LLM-powered)
            doc_metadata = await self._extract_document_metadata(documents[0] if documents else None, url)
            
            # IMPORTANT: Split documents into chunks for better RAG retrieval
            chunks = self.split_documents(documents, file_type='html')
            
            # CRITICAL: Enrich each chunk with document-level metadata
            for chunk in chunks:
                chunk.metadata.update(doc_metadata)
            
            logger.info(f"✂️ Split website {url} into {len(chunks)} chunks")
            logger.info(f"📋 Extracted metadata: title='{doc_metadata.get('title', 'N/A')[:50]}...', "
                       f"summary='{doc_metadata.get('summary', 'N/A')[:50]}...'")
            
            # Update stats
            self.load_stats['total_files'] += 1
            self.load_stats['successful'] += 1
            self.load_stats['total_documents'] += len(documents)
            self.load_stats['total_characters'] += total_chars
            # total_chunks is updated by split_documents()
            
            return {
                'success': True,
                'documents': chunks,  # Return SPLIT chunks, not raw documents
                'document_count': len(chunks),  # Count of chunks, not documents
                'url': url,
                'character_count': total_chars,
                'loader_used': 'WebBaseLoader',
                'loaded_at': datetime.now().isoformat(),
                'metadata': {
                    'source': url,
                    'source_type': 'web',
                    'character_count': total_chars,
                    'chunk_count': len(chunks),
                    **doc_metadata  # Include document-level metadata
                }
            }
            
        except Exception as e:
            self.load_stats['total_files'] += 1
            self.load_stats['failed'] += 1
            
            logger.error(f"Failed to load website {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    async def load_directory(self, directory_path: Union[str, Path], 
                           glob_pattern: str = "**/*",
                           progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Load all documents from a directory using LangChain DirectoryLoader.
        
        Args:
            directory_path: Path to directory
            glob_pattern: Glob pattern for file matching (default: all files)
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary with all loaded documents and statistics
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            return {
                'success': False,
                'error': f'Directory not found: {directory_path}',
                'directory_path': str(directory_path)
            }
        
        try:
            # Use LangChain's DirectoryLoader
            loader = DirectoryLoader(
                str(directory_path),
                glob=glob_pattern,
                show_progress=True
            )
            
            documents = await asyncio.to_thread(loader.load)
            
            # Calculate statistics
            total_chars = sum(len(doc.page_content) for doc in documents)
            
            # Update stats
            self.load_stats['total_files'] += len(documents)
            self.load_stats['successful'] += len(documents)
            self.load_stats['total_documents'] += len(documents)
            self.load_stats['total_characters'] += total_chars
            
            return {
                'success': True,
                'documents': documents,
                'document_count': len(documents),
                'directory_path': str(directory_path),
                'glob_pattern': glob_pattern,
                'character_count': total_chars,
                'loader_used': 'DirectoryLoader',
                'loaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to load directory {directory_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'directory_path': str(directory_path)
            }
    
    def _extract_file_metadata(self, file_path: Path, documents: List[Document]) -> Dict[str, Any]:
        """Extract metadata from LangChain documents."""
        metadata = {
            'file_name': file_path.name,
            'file_type': file_path.suffix.lstrip('.'),
            'file_size': file_path.stat().st_size,
            'document_count': len(documents),
        }
        
        # Aggregate metadata from all documents
        if documents:
            # Get metadata from first document
            first_doc_meta = documents[0].metadata
            metadata.update({
                'source': first_doc_meta.get('source', str(file_path)),
                'page_count': len(documents) if 'page' in first_doc_meta else 1
            })
        
        # Add format-specific metadata
        if file_path.suffix == '.md':
            metadata['is_markdown'] = True
        elif file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h']:
            metadata['is_code'] = True
            metadata['language'] = file_path.suffix.lstrip('.')
        
        return metadata
    
    def split_documents(self, documents: List[Document], file_type: str = 'txt') -> List[Document]:
        """
        Split documents intelligently based on document type.
        
        Args:
            documents: List of LangChain Document objects
            file_type: File extension (pdf, html, md, py, etc.)
            
        Returns:
            List of split Document objects with metadata preserved
        """
        if not documents:
            return []
        
        try:
            # Choose splitter based on file type
            if file_type == 'html':
                # For HTML, use TWO-STAGE splitting for better results
                chunks = []
                for doc in documents:
                    try:
                        # Stage 1: Try to split by HTML headers first
                        html_chunks = self.html_splitter.split_text(doc.page_content)
                        
                        # Stage 2: Apply RecursiveCharacterTextSplitter to each section
                        # This ensures proper chunking even if HTML has few/no headers
                        temp_docs = [Document(page_content=chunk, metadata=doc.metadata) 
                                    for chunk in html_chunks]
                        
                        final_chunks = self.general_splitter.split_documents(temp_docs)
                        
                        for chunk in final_chunks:
                            chunk.metadata['splitter'] = 'html_two_stage'
                        
                        chunks.extend(final_chunks)
                        
                        logger.info(f"HTML two-stage split: {len(html_chunks)} sections → {len(final_chunks)} chunks")
                        
                    except Exception as e:
                        logger.warning(f"HTML splitting failed, using general splitter: {e}")
                        # Fallback to general splitter only
                        general_chunks = self.general_splitter.split_documents([doc])
                        for chunk in general_chunks:
                            chunk.metadata['splitter'] = 'general_fallback'
                        chunks.extend(general_chunks)
                        
            elif file_type == 'md':
                # For Markdown, preserve header structure
                chunks = []
                for doc in documents:
                    try:
                        md_chunks = self.markdown_splitter.split_text(doc.page_content)
                        for chunk in md_chunks:
                            chunks.append(Document(
                                page_content=chunk,
                                metadata={**doc.metadata, 'splitter': 'markdown_header'}
                            ))
                    except Exception as e:
                        logger.warning(f"Markdown splitting failed, using general splitter: {e}")
                        general_chunks = self.general_splitter.split_documents([doc])
                        for chunk in general_chunks:
                            chunk.metadata['splitter'] = 'general_fallback'
                        chunks.extend(general_chunks)
                        
            elif file_type in ['py', 'js', 'ts', 'java', 'cpp', 'go']:
                # For code, use language-aware splitting
                language = file_type
                if language in self.code_splitters:
                    chunks = []
                    for doc in documents:
                        code_chunks = self.code_splitters[language].split_documents([doc])
                        for chunk in code_chunks:
                            chunk.metadata['splitter'] = f'code_{language}'
                            chunk.metadata['language'] = language
                        chunks.extend(code_chunks)
                else:
                    # Fallback to general
                    chunks = self.general_splitter.split_documents(documents)
                    for chunk in chunks:
                        chunk.metadata['splitter'] = 'general'
                        
            else:
                # For PDF and general text
                chunks = self.general_splitter.split_documents(documents)
                for chunk in chunks:
                    chunk.metadata['splitter'] = 'general'
            
            # CRITICAL: Add chunk_index metadata for proper source tracking
            for i, chunk in enumerate(chunks):
                chunk.metadata['chunk_index'] = i
            
            # Update statistics
            self.load_stats['total_chunks'] += len(chunks)
            
            logger.info(f"✂️ Split {len(documents)} documents into {len(chunks)} chunks (type: {file_type})")
            return chunks
            
        except Exception as e:
            logger.error(f"Document splitting failed: {e}")
            # Return unsplit documents on error
            return documents
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get loading statistics."""
        return {
            **self.load_stats,
            'success_rate': (self.load_stats['successful'] / self.load_stats['total_files'] * 100) 
                           if self.load_stats['total_files'] > 0 else 0
        }
    
    def reset_statistics(self):
        """Reset loading statistics."""
        self.load_stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'total_pages': 0,
            'total_characters': 0
        }


# Convenience functions for easy import
async def load_document(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Convenience function to load a single document using LangChain loaders.
    
    Args:
        file_path: Path to document
        
    Returns:
        Dictionary with LangChain documents and metadata
    """
    loader = DocumentLoader()
    return await loader.load_document(file_path)


async def load_documents(file_paths: List[Union[str, Path]], 
                        progress_callback: Optional[callable] = None) -> Dict[str, Any]:
    """
    Convenience function to load multiple documents.
    
    Args:
        file_paths: List of file paths
        progress_callback: Optional progress callback
        
    Returns:
        Batch results with all documents
    """
    loader = DocumentLoader()
    return await loader.load_batch(file_paths, progress_callback)


async def load_website(url: str) -> Dict[str, Any]:
    """
    Convenience function to load website content.
    
    Args:
        url: Website URL
        
    Returns:
        Dictionary with scraped content
    """
    loader = DocumentLoader()
    return await loader.load_website(url)


async def load_directory(directory_path: Union[str, Path], glob_pattern: str = "**/*") -> Dict[str, Any]:
    """
    Convenience function to load all documents from a directory.
    
    Args:
        directory_path: Directory path
        glob_pattern: File matching pattern
        
    Returns:
        Dictionary with all documents
    """
    loader = DocumentLoader()
    return await loader.load_directory(directory_path, glob_pattern)
