"""
RAG Document Processor for AI Development Agent System.

This module provides utilities for processing and managing RAG documents
including URL scraping, file processing, and text chunking.
"""

import requests
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse
import logging
from bs4 import BeautifulSoup
import hashlib

logger = logging.getLogger(__name__)


class RAGProcessor:
    """
    Processor for RAG documents including URL scraping and file processing.
    """
    
    def __init__(self):
        """Initialize the RAG processor."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def process_url(self, url: str, max_length: int = 10000) -> Dict[str, Any]:
        """
        Process a URL and extract its content.
        
        Args:
            url: URL to process
            max_length: Maximum content length to extract
            
        Returns:
            Dictionary with processed content
        """
        try:
            logger.info(f"Processing URL: {url}")
            
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL format")
            
            # Fetch content
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            # Extract title
            title = soup.title.string if soup.title else parsed_url.netloc
            
            # Extract metadata
            metadata = {
                'url': url,
                'title': title,
                'domain': parsed_url.netloc,
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(text),
                'status_code': response.status_code
            }
            
            return {
                'title': title,
                'content': text,
                'metadata': metadata,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            return {
                'title': f"Error: {url}",
                'content': f"Failed to process URL: {str(e)}",
                'metadata': {'url': url, 'error': str(e)},
                'success': False
            }
    
    def process_file(self, file_path: str, max_length: int = 10000) -> Dict[str, Any]:
        """
        Process a file and extract its content.
        
        Args:
            file_path: Path to the file
            max_length: Maximum content length to extract
            
        Returns:
            Dictionary with processed content
        """
        try:
            logger.info(f"Processing file: {file_path}")
            
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Determine file type and process accordingly
            file_extension = file_path.suffix.lower()
            
            if file_extension in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']:
                # Text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
            elif file_extension in ['.pdf']:
                # PDF files (would need PyPDF2 or similar)
                content = f"[PDF content from {file_path.name} - PDF processing not implemented]"
                
            elif file_extension in ['.docx']:
                # Word documents (would need python-docx)
                content = f"[Word document content from {file_path.name} - DOCX processing not implemented]"
                
            else:
                # Unknown file type
                content = f"[Binary file: {file_path.name} - Content not extractable]"
            
            # Truncate if too long
            if len(content) > max_length:
                content = content[:max_length] + "..."
            
            # Extract metadata
            metadata = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'file_extension': file_extension,
                'content_length': len(content)
            }
            
            return {
                'title': file_path.name,
                'content': content,
                'metadata': metadata,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return {
                'title': f"Error: {file_path}",
                'content': f"Failed to process file: {str(e)}",
                'metadata': {'file_path': str(file_path), 'error': str(e)},
                'success': False
            }
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_endings = ['. ', '! ', '? ', '\n\n']
                for ending in sentence_endings:
                    pos = text.rfind(ending, start, end)
                    if pos > start:
                        end = pos + len(ending)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to analyze
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction (could be enhanced with NLP libraries)
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:max_keywords]]
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """
        Generate a summary of the text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summary text
        """
        # Simple summary generation (could be enhanced with NLP)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Take first few sentences
        summary = ". ".join(sentences[:3])
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if a URL is accessible.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid and accessible
        """
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return False
            
            # Try a HEAD request first
            response = self.session.head(url, timeout=10)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate if a file exists and is readable.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is valid and readable
        """
        try:
            file_path = Path(file_path)
            return file_path.exists() and file_path.is_file()
        except Exception:
            return False


# Global RAG processor instance
_rag_processor = None


def get_rag_processor() -> RAGProcessor:
    """Get the global RAG processor instance."""
    global _rag_processor
    if _rag_processor is None:
        _rag_processor = RAGProcessor()
    return _rag_processor
