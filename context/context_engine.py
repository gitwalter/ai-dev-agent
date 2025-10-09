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

# LangChain imports for semantic search - Using Qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, SparseVectorParams
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    # Try new QdrantVectorStore (langchain-qdrant >= 0.1.0)
    QDRANT_NEW_API = False
    try:
        from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
        QDRANT_NEW_API = True
    except ImportError:
        # Fallback to old Qdrant wrapper
        from langchain_qdrant import Qdrant
        QDRANT_NEW_API = False
    
    # Try OpenAI embeddings first (NumPy 2.0 compatible)
    try:
        from langchain_openai import OpenAIEmbeddings
        OPENAI_EMBEDDINGS_AVAILABLE = True
    except ImportError:
        OPENAI_EMBEDDINGS_AVAILABLE = False
    
    # Use HuggingFace embeddings - try multiple import paths
    HUGGINGFACE_EMBEDDINGS_AVAILABLE = False
    HuggingFaceEmbeddings = None
    
    try:
        # Try direct import from embeddings module
        from langchain_huggingface.embeddings import HuggingFaceEmbeddings
        HUGGINGFACE_EMBEDDINGS_AVAILABLE = True
    except ImportError:
        try:
            # Fallback to community package
            from langchain_community.embeddings import HuggingFaceEmbeddings
            HUGGINGFACE_EMBEDDINGS_AVAILABLE = True
        except ImportError:
            pass
    
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LangChain/Qdrant not available for semantic search: {e}")
    SEMANTIC_SEARCH_AVAILABLE = False
    OPENAI_EMBEDDINGS_AVAILABLE = False
    HUGGINGFACE_EMBEDDINGS_AVAILABLE = False
    QdrantClient = None
    Qdrant = None
    OpenAIEmbeddings = None
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
        
        # Semantic search components - Using Qdrant
        self.qdrant_client: Optional[QdrantClient] = None
        self.vector_store: Optional[Qdrant] = None
        self.embeddings = None  # Will be OpenAIEmbeddings or HuggingFaceEmbeddings
        self.text_splitter: Optional[RecursiveCharacterTextSplitter] = None
        self.documents: List[Document] = []
        self.collection_name = "ai_dev_agent_codebase"
        
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
        """Initialize semantic search components with free, local embeddings."""
        try:
            # Use HuggingFace embeddings (free, local, no API key required)
            if HUGGINGFACE_EMBEDDINGS_AVAILABLE:
                try:
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name="all-MiniLM-L6-v2",  # Fast, lightweight, free model
                        model_kwargs={'device': 'cpu'},
                        encode_kwargs={'normalize_embeddings': True}
                    )
                    self.logger.info("✅ Semantic search initialized with free HuggingFace embeddings (all-MiniLM-L6-v2)")
                except Exception as e:
                    self.logger.error(f"❌ HuggingFace embeddings failed: {e}")
                    self.embeddings = None
            else:
                self.logger.warning("⚠️ HuggingFace embeddings not available")
                self.embeddings = None
            
            # Initialize Qdrant client (local, embedded - no API key needed)
            # Initialize this even if embeddings failed, so we can still manage collections
            qdrant_path = Path(self.config.vector_db_path) / "qdrant_storage"
            qdrant_path.mkdir(parents=True, exist_ok=True)
            
            self.qdrant_client = QdrantClient(path=str(qdrant_path))
            self.logger.info(f"✅ Qdrant initialized (local storage: {qdrant_path})")
            
            if self.embeddings is None:
                self.logger.warning("⚠️ No embedding provider available - semantic search disabled")
                return
            
            # Initialize sparse embeddings for hybrid search (BM25) - only if new API available
            self.sparse_embeddings = None
            if QDRANT_NEW_API:
                try:
                    self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/BM25")
                    self.logger.info("✅ BM25 sparse embeddings initialized for hybrid search")
                except Exception as e:
                    self.logger.warning(f"⚠️ BM25 initialization failed: {e} - will use dense-only search")
                    self.sparse_embeddings = None
            else:
                self.logger.info("ℹ️ Using legacy Qdrant API (dense-only search). Upgrade langchain-qdrant for hybrid search.")
            
            # Initialize retriever (will be set when vector store is created)
            self.retriever = None
            
            # Check if collection exists, don't load yet (will be created on first use)
            try:
                collections = self.qdrant_client.get_collections().collections
                if any(c.name == self.collection_name for c in collections):
                    self.logger.info(f"✅ Found existing Qdrant collection: {self.collection_name}")
                else:
                    self.logger.info(f"Collection {self.collection_name} will be created on first use")
            except Exception as e:
                self.logger.info(f"Qdrant collection check: {e}")
            
            # Initialize text splitter with optimal settings based on RAG best practices
            # Research shows 512 tokens with 20-50 token overlap works best
            # Source: https://masteringllm.medium.com/best-practices-for-rag-pipeline-8c12a8096453
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=512,  # Optimal chunk size (175-512 tokens, 512 provides better context)
                chunk_overlap=50,  # 20-50 token overlap for continuity
                separators=["\n\n", "\n", ". ", " ", ""],  # Sentence-level chunking
                length_function=len
            )
            
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
            
            # Build Qdrant vector store if available
            if self.embeddings and self.documents and self.qdrant_client:
                try:
                    # Create collection if it doesn't exist
                    collections = self.qdrant_client.get_collections().collections
                    collection_exists = any(c.name == self.collection_name for c in collections)
                    
                    if not collection_exists:
                        # Create collection
                        if QDRANT_NEW_API and self.sparse_embeddings:
                            # New API with hybrid search support
                            vectors_config = {
                                "dense": VectorParams(size=384, distance=Distance.COSINE)
                            }
                            self.qdrant_client.create_collection(
                                collection_name=self.collection_name,
                                vectors_config=vectors_config,
                                sparse_vectors_config={"sparse": SparseVectorParams()}
                            )
                            self.logger.info(f"✅ Collection created with HYBRID search support")
                        else:
                            # Legacy API or dense-only
                            self.qdrant_client.create_collection(
                                collection_name=self.collection_name,
                                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                            )
                            self.logger.info(f"✅ Collection created (dense-only)")
                    
                    # Create vector store based on API version
                    if QDRANT_NEW_API:
                        # Use new QdrantVectorStore API
                        if self.sparse_embeddings:
                            self.vector_store = QdrantVectorStore(
                                client=self.qdrant_client,
                                collection_name=self.collection_name,
                                embedding=self.embeddings,  # Singular! Modern API
                                sparse_embedding=self.sparse_embeddings,
                                retrieval_mode=RetrievalMode.HYBRID
                            )
                            self.logger.info("✅ Using HYBRID search (BM25 + semantic)")
                        else:
                            self.vector_store = QdrantVectorStore(
                                client=self.qdrant_client,
                                collection_name=self.collection_name,
                                embedding=self.embeddings,
                                retrieval_mode=RetrievalMode.DENSE
                            )
                            self.logger.info("✅ Using DENSE search (new API)")
                    else:
                        # Use legacy Qdrant API
                        self.vector_store = Qdrant(
                            client=self.qdrant_client,
                            collection_name=self.collection_name,
                            embeddings=self.embeddings  # Plural! Legacy API
                        )
                        self.logger.info("✅ Using legacy Qdrant API (dense-only)")
                    
                    # Add documents
                    self.vector_store.add_documents(self.documents)
                    
                    # Create retriever (MMR if new API, similarity if legacy)
                    if QDRANT_NEW_API:
                        self.retriever = self.vector_store.as_retriever(
                            search_type="mmr",
                            search_kwargs={
                                "k": 15,
                                "fetch_k": 50,
                                "lambda_mult": 0.5
                            }
                        )
                        self.logger.info("✅ MMR retriever configured for diverse results")
                    else:
                        self.retriever = self.vector_store.as_retriever(
                            search_kwargs={"k": 15}
                        )
                        self.logger.info("✅ Similarity retriever configured")
                    
                    self.logger.info(f"🎯 Qdrant vector store built with {len(self.documents)} documents (persistent)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to create Qdrant vector store: {e}")
                    import traceback
                    self.logger.warning(traceback.format_exc())
                    self.vector_store = None
                    self.retriever = None
            
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
        - Robust encoding detection
        
        Args:
            file_path: Path to the file to index
        """
        try:
            # Try multiple encodings for robust file reading
            content = None
            encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                # Skip binary files or files with unsupported encodings
                self.logger.debug(f"⚠️ Skipping file with unsupported encoding: {file_path}")
                return
                
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
        HYBRID SEARCH - Combines semantic and keyword search for best results.
        
        Features:
        - Semantic search using vector embeddings
        - Keyword/lexical search for exact matches
        - Reciprocal Rank Fusion (RRF) for combining results
        - Rich metadata return
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant context with metadata and scores (hybrid ranked)
        """
        semantic_results = []
        keyword_results = []
        
        # 1. Semantic search (if available)
        if self.vector_store:
            try:
                semantic_results = self._semantic_search(query, max_results * 2)  # Get more for fusion
                self.logger.info(f"🎯 Semantic search found {len(semantic_results)} results")
            except Exception as e:
                self.logger.error(f"⚠️ Semantic search failed: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
        else:
            self.logger.warning(f"⚠️ Vector store not initialized - skipping semantic search")
        
        # 2. Keyword search (always run for hybrid)
        try:
            keyword_results = self._keyword_search(query, max_results * 2)  # Get more for fusion
            self.logger.info(f"🔍 Keyword search found {len(keyword_results)} results")
        except Exception as e:
            self.logger.error(f"⚠️ Keyword search failed: {e}")
        
        # 3. HYBRID: Combine using Reciprocal Rank Fusion (RRF)
        if semantic_results and keyword_results:
            self.logger.info(f"🔀 Combining semantic + keyword results using RRF...")
            results = self._reciprocal_rank_fusion(semantic_results, keyword_results, max_results)
            self.logger.info(f"✅ Hybrid search returned {len(results)} results")
        elif semantic_results:
            self.logger.info(f"✅ Using semantic-only results")
            results = semantic_results[:max_results]
        elif keyword_results:
            self.logger.info(f"✅ Using keyword-only results")
            results = keyword_results[:max_results]
        else:
            self.logger.warning(f"⚠️ No results from any search method")
            results = []
        
        return results
    
    async def semantic_search(self, query: str, limit: int = 10, context_filter: str = None) -> Dict[str, Any]:
        """
        Public semantic search method for RAG integration.
        
        Args:
            query: Search query
            limit: Maximum number of results
            context_filter: Optional context filter
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Use existing search_context method
            results = self.search_context(query, limit)
            
            # Format results for RAG integration
            formatted_results = []
            for result in results:
                formatted_result = {
                    "content": result.get("content", ""),
                    "metadata": result.get("metadata", {}),
                    "relevance_score": result.get("relevance_score", 0.0),
                    "search_type": result.get("search_type", "unknown"),
                    "file_path": result.get("file_path", "unknown")
                }
                formatted_results.append(formatted_result)
            
            return {
                "results": formatted_results,
                "total_found": len(formatted_results),
                "query": query,
                "search_type": "semantic" if self.vector_store else "keyword",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Semantic search error: {e}")
            return {
                "results": [],
                "total_found": 0,
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _semantic_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform semantic search using vector store - FIXED for better retrieval."""
        try:
            # FIXED: Use similarity_search without score filtering
            # The with_relevance_scores method was filtering out too many results
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query, k=max_results
            )
            
            self.logger.info(f"🔍 Semantic search for '{query[:50]}...' returned {len(docs_with_scores)} results")
            
            results = []
            for doc, score in docs_with_scores:
                # Qdrant uses distance, convert to similarity (lower distance = higher similarity)
                similarity_score = 1.0 - score if score < 1.0 else 1.0 / (1.0 + score)
                
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": similarity_score,
                    "search_type": "semantic",
                    "file_path": doc.metadata.get("file_path", "unknown"),
                    "chunk_index": doc.metadata.get("chunk_index", 0)
                }
                results.append(result)
            
            self.logger.info(f"✅ Formatted {len(results)} semantic search results")
            return results
            
        except Exception as e:
            self.logger.error(f"Semantic search error: {e}")
            return []
    
    def _reciprocal_rank_fusion(
        self, 
        semantic_results: List[Dict], 
        keyword_results: List[Dict],
        max_results: int,
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion (RRF) - Combines multiple ranked result lists.
        
        Formula: RRF_score = sum(1 / (k + rank_i)) for each result list
        
        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from keyword search
            max_results: Maximum results to return
            k: Constant for RRF (typically 60)
            
        Returns:
            Fused and re-ranked results
        """
        # Create a mapping of content hash to result
        result_map = {}
        rrf_scores = {}
        
        # Process semantic results
        for rank, result in enumerate(semantic_results, 1):
            content_hash = hash(result['content'][:100])  # Use first 100 chars as key
            if content_hash not in result_map:
                result_map[content_hash] = result.copy()
                result_map[content_hash]['fusion_sources'] = []
                rrf_scores[content_hash] = 0.0
            
            # Add RRF score from semantic ranking
            rrf_scores[content_hash] += 1.0 / (k + rank)
            result_map[content_hash]['fusion_sources'].append('semantic')
            result_map[content_hash]['semantic_rank'] = rank
        
        # Process keyword results
        for rank, result in enumerate(keyword_results, 1):
            content_hash = hash(result['content'][:100])
            if content_hash not in result_map:
                result_map[content_hash] = result.copy()
                result_map[content_hash]['fusion_sources'] = []
                rrf_scores[content_hash] = 0.0
            
            # Add RRF score from keyword ranking
            rrf_scores[content_hash] += 1.0 / (k + rank)
            result_map[content_hash]['fusion_sources'].append('keyword')
            result_map[content_hash]['keyword_rank'] = rank
        
        # Sort by RRF score
        sorted_results = sorted(
            result_map.items(), 
            key=lambda x: rrf_scores[x[0]], 
            reverse=True
        )
        
        # Build final result list with RRF scores
        fused_results = []
        for content_hash, result in sorted_results[:max_results]:
            result['relevance_score'] = rrf_scores[content_hash]
            result['search_type'] = 'hybrid'
            result['rrf_score'] = rrf_scores[content_hash]
            fused_results.append(result)
        
        # Log fusion stats
        both_sources = sum(1 for r in fused_results if len(r.get('fusion_sources', [])) > 1)
        self.logger.info(f"🔀 RRF: {both_sources}/{len(fused_results)} results found by BOTH methods")
        
        return fused_results
    
    def _keyword_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Keyword/lexical search - finds exact term matches.
        Improved to handle multi-term queries with BM25-like scoring.
        """
        results = []
        query_lower = query.lower()
        query_terms = query_lower.split()  # Split into terms
        
        # Search through documents (use indexed files if vector store not available)
        if self.documents:
            # Search in document chunks
            for doc in self.documents:
                content_lower = doc.page_content.lower()
                
                # Calculate match score
                exact_match = query_lower in content_lower
                term_matches = sum(1 for term in query_terms if term in content_lower)
                
                if exact_match or term_matches >= len(query_terms) * 0.5:  # At least 50% terms match
                    # BM25-like scoring
                    occurrences = content_lower.count(query_lower) if exact_match else 0
                    term_frequency = sum(content_lower.count(term) for term in query_terms)
                    
                    # Score: exact match bonus + term frequency
                    score = (2.0 if exact_match else 0) + (term_matches / max(len(query_terms), 1)) + (term_frequency * 0.1)
                    score = min(score, 5.0) / 5.0  # Normalize to 0-1
                    
                    result = {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "relevance_score": score,
                        "search_type": "keyword",
                        "file_path": doc.metadata.get("source", "unknown"),
                        "chunk_index": doc.metadata.get("chunk_index", 0),
                        "exact_match": exact_match,
                        "term_matches": term_matches
                    }
                    results.append(result)
        else:
            # Fallback to indexed_files
            for file_path, content in self.indexed_files.items():
                content_lower = content.lower()
                
                exact_match = query_lower in content_lower
                term_matches = sum(1 for term in query_terms if term in content_lower)
                
                if exact_match or term_matches >= len(query_terms) * 0.5:
                    occurrences = content_lower.count(query_lower) if exact_match else 0
                    term_frequency = sum(content_lower.count(term) for term in query_terms)
                    
                    score = (2.0 if exact_match else 0) + (term_matches / max(len(query_terms), 1)) + (term_frequency * 0.1)
                    score = min(score, 5.0) / 5.0
                    
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
                        "chunk_index": 0,
                        "exact_match": exact_match,
                        "term_matches": term_matches
                    }
                    results.append(result)
        
        # Sort by relevance score (exact matches first, then by score)
        results.sort(key=lambda x: (x.get("exact_match", False), x["relevance_score"]), reverse=True)
        return results[:max_results]
    
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
            "file_types_indexed": list(self._get_file_type_distribution().keys()),
            "vector_store_path": self.config.vector_db_path
        }
    
    # Qdrant handles persistence automatically - no manual save/load needed!
