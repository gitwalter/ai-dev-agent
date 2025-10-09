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
    
    def __init__(self):
        """Initialize document loader with LangChain loaders."""
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
        
        self.load_stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'total_documents': 0,  # LangChain documents (can be multiple per file)
            'total_characters': 0,
            'total_chunks': 0  # After splitting
        }
    
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
    
    async def load_website(self, url: str) -> Dict[str, Any]:
        """
        Load content from a website using LangChain WebBaseLoader.
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dictionary with scraped content and metadata
        """
        try:
            # Use LangChain's WebBaseLoader
            loader = WebBaseLoader(url)
            documents = await asyncio.to_thread(loader.load)
            
            # Calculate statistics before splitting
            total_chars = sum(len(doc.page_content) for doc in documents)
            
            # IMPORTANT: Split documents into chunks for better RAG retrieval
            chunks = self.split_documents(documents, file_type='html')
            
            logger.info(f"✂️ Split website {url} into {len(chunks)} chunks")
            
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
                    'chunk_count': len(chunks)
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
