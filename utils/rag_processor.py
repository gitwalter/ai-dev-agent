"""
RAG Processor - Simple interface for the Streamlit UI
Provides basic RAG document processing capabilities.
"""

import requests
from urllib.parse import urlparse


def get_rag_processor():
    """Get a simple RAG processor interface."""
    return SimpleRAGProcessor()


class SimpleRAGProcessor:
    """Simple RAG processor for basic UI operations."""
    
    def __init__(self):
        """Initialize the RAG processor."""
        pass
    
    def validate_url(self, url: str) -> bool:
        """Validate if a URL is accessible."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Simple connectivity check
            response = requests.head(url, timeout=10, allow_redirects=True)
            return response.status_code < 400
            
        except Exception:
            return False
    
    def process_url(self, url: str) -> dict:
        """Process content from a URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Simple content extraction
            content = response.text
            
            # Extract title from HTML if possible
            title = url
            if '<title>' in content and '</title>' in content:
                start = content.find('<title>') + 7
                end = content.find('</title>', start)
                if end > start:
                    title = content[start:end].strip()
            
            # Clean up content (remove HTML tags for demo)
            import re
            clean_content = re.sub(r'<[^>]+>', ' ', content)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            
            # Limit content length for demo
            if len(clean_content) > 5000:
                clean_content = clean_content[:5000] + "..."
            
            return {
                'success': True,
                'title': title,
                'content': clean_content,
                'url': url
            }
            
        except Exception as e:
            return {
                'success': False,
                'content': str(e)
            }
    
    def chunk_text(self, text: str, chunk_size: int = 500) -> list:
        """Split text into chunks for processing."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
