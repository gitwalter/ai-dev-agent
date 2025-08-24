"""
Context Engine for AI Development Agent.
Provides codebase indexing and context-aware suggestions.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from models.config import ContextConfig


class ContextEngine:
    """
    Context engine for indexing codebase and providing context-aware suggestions.
    """
    
    def __init__(self, config: ContextConfig):
        """
        Initialize the context engine.
        
        Args:
            config: Context configuration
        """
        self.config = config
        self.logger = logging.getLogger("context_engine")
        self.indexed_files: Dict[str, str] = {}
        self.codebase_context: Dict[str, Any] = {}
        
    async def index_codebase(self, root_path: str) -> None:
        """
        Index the codebase for context-aware suggestions.
        
        Args:
            root_path: Root path of the codebase to index
        """
        self.logger.info(f"Indexing codebase at: {root_path}")
        try:
            root = Path(root_path)
            if not root.exists():
                self.logger.warning(f"Root path does not exist: {root_path}")
                return
                
            # Index Python files
            for py_file in root.rglob("*.py"):
                if self._should_index_file(py_file):
                    await self._index_file(py_file)
                    
            # Index documentation files
            for doc_file in root.rglob("*.md"):
                if self._should_index_file(doc_file):
                    await self._index_file(doc_file)
                    
            # Index configuration files
            for config_file in root.rglob("*.{yml,yaml,json,toml}"):
                if self._should_index_file(config_file):
                    await self._index_file(config_file)
                    
            self.logger.info(f"Indexed {len(self.indexed_files)} files")
            
        except Exception as e:
            self.logger.error(f"Failed to index codebase: {str(e)}")
            
    def _should_index_file(self, file_path: Path) -> bool:
        """
        Check if a file should be indexed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be indexed
        """
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            return False
            
        # Skip common directories to ignore
        ignore_dirs = {'__pycache__', '.git', '.pytest_cache', 'node_modules', 'venv', 'env'}
        if any(part in ignore_dirs for part in file_path.parts):
            return False
            
        # Skip files larger than max size
        try:
            if file_path.stat().st_size > self.config.max_file_size:
                return False
        except OSError:
            return False
            
        return True
        
    async def _index_file(self, file_path: Path) -> None:
        """
        Index a single file.
        
        Args:
            file_path: Path to the file to index
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.indexed_files[str(file_path)] = content
            self.logger.debug(f"Indexed file: {file_path}")
            
        except Exception as e:
            self.logger.warning(f"Failed to index file {file_path}: {str(e)}")
            
    def get_context_for_file(self, file_path: str) -> Optional[str]:
        """
        Get context for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content if indexed, None otherwise
        """
        return self.indexed_files.get(file_path)
        
    def get_codebase_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the indexed codebase.
        
        Returns:
            Codebase summary
        """
        return {
            "total_files": len(self.indexed_files),
            "file_types": self._get_file_type_distribution(),
            "total_size": sum(len(content) for content in self.indexed_files.values()),
            "indexed_files": list(self.indexed_files.keys())
        }
        
    def _get_file_type_distribution(self) -> Dict[str, int]:
        """
        Get distribution of file types in the indexed codebase.
        
        Returns:
            Dictionary mapping file extensions to counts
        """
        distribution = {}
        for file_path in self.indexed_files.keys():
            ext = Path(file_path).suffix
            distribution[ext] = distribution.get(ext, 0) + 1
        return distribution
        
    def search_context(self, query: str) -> List[str]:
        """
        Search for relevant context based on a query.
        
        Args:
            query: Search query
            
        Returns:
            List of relevant file paths
        """
        # Simple keyword-based search
        relevant_files = []
        query_lower = query.lower()
        
        for file_path, content in self.indexed_files.items():
            if query_lower in content.lower():
                relevant_files.append(file_path)
                
        return relevant_files[:self.config.max_search_results]
