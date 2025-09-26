"""
Context Engine for AI Development Agent.
Provides codebase indexing and context-aware suggestions with semantic search capabilities.

Enhanced for US-RAG-001: RAG-Enhanced IDE Integration
- Semantic search using vector embeddings
- LangChain integration for advanced retrieval
- Project-specific pattern learning
- Real-time context awareness
"""

import os
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from models.config import ContextConfig

# LangChain imports for semantic search
try:
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LangChain not available for semantic search: {e}")
    SEMANTIC_SEARCH_AVAILABLE = False
    FAISS = None
    HuggingFaceEmbeddings = None
    Document = None
    RecursiveCharacterTextSplitter = None


class ContextEngine:
    """
    Enhanced context engine for indexing codebase and providing context-aware suggestions.
    
    Features:
    - Semantic search using vector embeddings
    - Project-specific pattern learning
    - Real-time context awareness
    - LangChain integration for advanced retrieval
    """
    
    def __init__(self, config: ContextConfig):
        """
        Initialize the enhanced context engine with semantic search capabilities.
        
        Args:
            config: Context configuration
        """
        self.config = config
        self.logger = logging.getLogger("context_engine")
        
        # Legacy keyword-based storage (for fallback)
        self.indexed_files: Dict[str, str] = {}
        self.codebase_context: Dict[str, Any] = {}
        
        # Semantic search components
        self.vector_store: Optional[FAISS] = None
        self.embeddings: Optional[HuggingFaceEmbeddings] = None
        self.text_splitter: Optional[RecursiveCharacterTextSplitter] = None
        self.documents: List[Document] = []
        
        # Pattern learning storage
        self.import_patterns: Dict[str, List[str]] = {}
        self.error_solutions: Dict[str, str] = {}
        self.successful_commands: List[str] = []
        
        # Initialize semantic search if available
        if SEMANTIC_SEARCH_AVAILABLE:
            self._initialize_semantic_search()
        else:
            self.logger.warning("Semantic search not available - using keyword-based search only")
    
    def _initialize_semantic_search(self) -> None:
        """Initialize semantic search components."""
        try:
            # Use lightweight, free embedding model
            self.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",  # Fast, lightweight model
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # Initialize vector store (will be created when documents are added)
            self.vector_store = None  # FAISS requires documents to initialize
            
            # Initialize text splitter for better chunking
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )
            
            self.logger.info("✅ Semantic search initialized with all-MiniLM-L6-v2 embeddings")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize semantic search: {e}")
            self.vector_store = None
            self.embeddings = None
        
    async def index_codebase(self, root_path: str) -> None:
        """
        Enhanced codebase indexing with semantic search capabilities.
        
        Features:
        - Semantic search via vector embeddings
        - Import pattern learning
        - Git history pattern extraction
        - Error solution memory
        
        Args:
            root_path: Root path of the codebase to index
        """
        self.logger.info(f"🔍 Enhanced indexing starting for: {root_path}")
        start_time = datetime.now()
        
        try:
            root = Path(root_path)
            if not root.exists():
                self.logger.warning(f"Root path does not exist: {root_path}")
                return
                
            # Collect all files for batch processing
            files_to_index = []
            
            # Collect Python files
            for py_file in root.rglob("*.py"):
                if self._should_index_file(py_file):
                    files_to_index.append(py_file)
                    
            # Collect documentation files
            for doc_file in root.rglob("*.md"):
                if self._should_index_file(doc_file):
                    files_to_index.append(doc_file)
                    
            # Collect configuration files
            for pattern in ["*.yml", "*.yaml", "*.json", "*.toml"]:
                for config_file in root.rglob(pattern):
                    if self._should_index_file(config_file):
                        files_to_index.append(config_file)
            
            self.logger.info(f"📁 Found {len(files_to_index)} files to index")
            
            # Process files in batches for better performance
            batch_size = 50
            for i in range(0, len(files_to_index), batch_size):
                batch = files_to_index[i:i + batch_size]
                await self._process_file_batch(batch)
                
                # Progress update
                progress = min(i + batch_size, len(files_to_index))
                self.logger.info(f"📊 Indexed {progress}/{len(files_to_index)} files")
            
            # Build semantic search index if available
            if self.embeddings and self.documents:
                try:
                    self.vector_store = FAISS.from_documents(self.documents, self.embeddings)
                    self.logger.info(f"🎯 FAISS vector store built with {len(self.documents)} documents")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to create FAISS vector store: {e}")
                    self.vector_store = None
            
            # Extract and learn patterns
            await self._extract_project_patterns(root)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"✅ Indexing complete: {len(self.indexed_files)} files, {len(self.documents)} chunks in {duration:.2f}s")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to index codebase: {str(e)}")
    
    async def _process_file_batch(self, file_batch: List[Path]) -> None:
        """Process a batch of files for indexing."""
        for file_path in file_batch:
            await self._index_file(file_path)
    
    async def _extract_project_patterns(self, root_path: Path) -> None:
        """Extract and learn project-specific patterns."""
        try:
            # Extract import patterns from Python files
            for file_path, content in self.indexed_files.items():
                if file_path.endswith('.py'):
                    self._learn_import_patterns(file_path, content)
            
            # Learn from git history if available
            git_dir = root_path / '.git'
            if git_dir.exists():
                await self._learn_from_git_history(root_path)
            
            self.logger.info(f"📚 Learned {len(self.import_patterns)} import patterns")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Pattern extraction failed: {e}")
    
    def _learn_import_patterns(self, file_path: str, content: str) -> None:
        """Learn import patterns from Python files."""
        import re
        
        # Extract imports
        import_lines = re.findall(r'^(?:from\s+[\w.]+\s+)?import\s+.*$', content, re.MULTILINE)
        
        # Categorize by file location
        path_parts = Path(file_path).parts
        if len(path_parts) > 1:
            directory = path_parts[-2]  # Parent directory
            if directory not in self.import_patterns:
                self.import_patterns[directory] = []
            self.import_patterns[directory].extend(import_lines)
    
    async def _learn_from_git_history(self, root_path: Path) -> None:
        """Learn patterns from git commit history."""
        try:
            import subprocess
            
            # Get recent commits with file changes
            result = subprocess.run(
                ['git', 'log', '--oneline', '--name-only', '-n', '100'],
                cwd=root_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Process git log for successful patterns
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'fix' in line.lower() or 'resolve' in line.lower():
                        # Store successful solution patterns
                        self.error_solutions[line] = f"Successful resolution at {datetime.now()}"
            
        except Exception as e:
            self.logger.debug(f"Git history learning skipped: {e}")
            
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
        Enhanced file indexing with semantic search support.
        
        Features:
        - Text chunking for better retrieval
        - Vector embedding creation
        - Metadata preservation
        - Pattern extraction
        
        Args:
            file_path: Path to the file to index
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Store in legacy format for fallback
            self.indexed_files[str(file_path)] = content
            
            # Create vector embeddings if semantic search is available
            if self.text_splitter and SEMANTIC_SEARCH_AVAILABLE:
                await self._create_vector_embeddings(file_path, content)
            
            self.logger.debug(f"✅ Indexed file: {file_path}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to index file {file_path}: {str(e)}")
    
    async def _create_vector_embeddings(self, file_path: Path, content: str) -> None:
        """Create vector embeddings for semantic search."""
        try:
            # Split content into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Create documents with metadata
            for i, chunk in enumerate(chunks):
                metadata = {
                    "file_path": str(file_path),
                    "file_type": file_path.suffix,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_size": len(content),
                    "indexed_at": datetime.now().isoformat()
                }
                
                # Add file-specific metadata
                if file_path.suffix == '.py':
                    metadata.update(self._extract_python_metadata(chunk))
                elif file_path.suffix == '.md':
                    metadata.update(self._extract_markdown_metadata(chunk))
                
                document = Document(
                    page_content=chunk,
                    metadata=metadata
                )
                
                self.documents.append(document)
                
        except Exception as e:
            self.logger.debug(f"Vector embedding creation failed for {file_path}: {e}")
    
    def _extract_python_metadata(self, chunk: str) -> Dict[str, Any]:
        """Extract Python-specific metadata from code chunk."""
        import re
        
        metadata = {}
        
        # Extract function definitions
        functions = re.findall(r'def\s+(\w+)\s*\(', chunk)
        if functions:
            metadata['functions'] = functions
        
        # Extract class definitions
        classes = re.findall(r'class\s+(\w+)\s*[:(]', chunk)
        if classes:
            metadata['classes'] = classes
        
        # Extract imports
        imports = re.findall(r'(?:from\s+[\w.]+\s+)?import\s+[\w., ]+', chunk)
        if imports:
            metadata['imports'] = imports
        
        # Detect common patterns
        if 'async def' in chunk:
            metadata['has_async'] = True
        if '@' in chunk and ('def' in chunk or 'class' in chunk):
            metadata['has_decorators'] = True
        
        return metadata
    
    def _extract_markdown_metadata(self, chunk: str) -> Dict[str, Any]:
        """Extract Markdown-specific metadata from content chunk."""
        import re
        
        metadata = {}
        
        # Extract headings
        headings = re.findall(r'^#+\s+(.+)$', chunk, re.MULTILINE)
        if headings:
            metadata['headings'] = headings
        
        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)?', chunk)
        if code_blocks:
            metadata['code_languages'] = [lang for lang in code_blocks if lang]
        
        # Check for common document types
        if any(word in chunk.lower() for word in ['user story', 'acceptance criteria']):
            metadata['document_type'] = 'user_story'
        elif any(word in chunk.lower() for word in ['api', 'endpoint', 'request']):
            metadata['document_type'] = 'api_documentation'
        
        return metadata
            
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
        
    def search_context(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Enhanced context search with semantic similarity.
        
        Features:
        - Semantic search using vector embeddings
        - Relevance scoring
        - Rich metadata return
        - Fallback to keyword search
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant context with metadata and scores
        """
        results = []
        
        # Try semantic search first
        if self.vector_store:
            try:
                results = self._semantic_search(query, max_results)
                self.logger.debug(f"🎯 Semantic search found {len(results)} results")
            except Exception as e:
                self.logger.warning(f"⚠️ Semantic search failed: {e}")
        
        # Fallback to keyword search if semantic search fails or finds few results
        if len(results) < max_results // 2:
            keyword_results = self._keyword_search(query, max_results - len(results))
            results.extend(keyword_results)
            self.logger.debug(f"🔍 Added {len(keyword_results)} keyword search results")
        
        return results[:max_results]
    
    def _semantic_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform semantic search using vector store."""
        try:
            # Perform similarity search with relevance scores
            docs_with_scores = self.vector_store.similarity_search_with_relevance_scores(
                query, k=max_results
            )
            
            results = []
            for doc, score in docs_with_scores:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score,
                    "search_type": "semantic",
                    "file_path": doc.metadata.get("file_path", "unknown"),
                    "chunk_index": doc.metadata.get("chunk_index", 0)
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Semantic search error: {e}")
            return []
    
    def _keyword_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback keyword-based search."""
        results = []
        query_lower = query.lower()
        
        for file_path, content in self.indexed_files.items():
            if query_lower in content.lower():
                # Calculate simple relevance score based on frequency
                occurrences = content.lower().count(query_lower)
                score = min(occurrences / 10.0, 1.0)  # Normalize to 0-1
                
                result = {
                    "content": content[:500] + "..." if len(content) > 500 else content,
                    "metadata": {
                        "file_path": file_path,
                        "file_type": Path(file_path).suffix,
                        "search_type": "keyword"
                    },
                    "relevance_score": score,
                    "search_type": "keyword",
                    "file_path": file_path,
                    "chunk_index": 0
                }
                results.append(result)
                
                if len(results) >= max_results:
                    break
        
        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results
    
    def get_import_suggestions(self, file_path: str) -> List[str]:
        """Get import suggestions based on learned patterns."""
        suggestions = []
        
        # Get directory context
        path_parts = Path(file_path).parts
        if len(path_parts) > 1:
            directory = path_parts[-2]
            
            # Return learned patterns for this directory
            if directory in self.import_patterns:
                suggestions = list(set(self.import_patterns[directory][:10]))
        
        return suggestions
    
    def get_error_solutions(self, error_message: str) -> List[str]:
        """Get solutions for errors based on learned patterns."""
        solutions = []
        
        error_lower = error_message.lower()
        for solution_key, solution_value in self.error_solutions.items():
            if any(word in solution_key.lower() for word in error_lower.split()):
                solutions.append(f"{solution_key}: {solution_value}")
        
        return solutions[:5]
    
    def get_project_intelligence_summary(self) -> Dict[str, Any]:
        """Get a summary of project-specific intelligence learned."""
        return {
            "total_files_indexed": len(self.indexed_files),
            "vector_documents": len(self.documents),
            "import_patterns_learned": len(self.import_patterns),
            "error_solutions_stored": len(self.error_solutions),
            "successful_commands": len(self.successful_commands),
            "semantic_search_available": self.vector_store is not None,
            "directories_analyzed": list(self.import_patterns.keys()),
            "file_types_indexed": list(self._get_file_type_distribution().keys())
        }
