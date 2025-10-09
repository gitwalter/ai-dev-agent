#!/usr/bin/env python3
"""
RAG System Persistence Layer
============================

Comprehensive persistence layer for the RAG (Retrieval-Augmented Generation) system.
Stores vector embeddings, indexed documents, metadata, and usage statistics.

Features:
- SQLite database for metadata and statistics
- FAISS index persistence for vector embeddings
- Document chunk storage with metadata
- Query history and analytics
- Automatic cleanup and maintenance

Database Location: data/rag_system.db
Vector Store Location: data/rag_vectors/

Created: 2025-01-08
"""

import sqlite3
import json
import pickle
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class IndexedDocument:
    """Represents an indexed document in the RAG system."""
    doc_id: str
    file_path: str
    content_hash: str
    chunk_count: int
    file_size: int
    file_type: str
    indexed_at: str
    last_accessed: Optional[str] = None
    access_count: int = 0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""
    chunk_id: str
    doc_id: str
    chunk_index: int
    content: str
    content_length: int
    embedding_vector: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class QueryLog:
    """Represents a query execution log."""
    query_id: str
    query_text: str
    query_type: str  # 'semantic', 'keyword', 'hybrid'
    results_count: int
    retrieval_time: float
    executed_at: str
    agent_id: Optional[str] = None
    user_id: Optional[str] = None


class RAGPersistence:
    """
    Comprehensive persistence layer for RAG system.
    
    Manages:
    - Document metadata and indexing history
    - Vector embeddings (FAISS)
    - Query logs and analytics
    - System configuration
    """
    
    def __init__(self, db_path: str = "data/rag_system.db", vector_store_path: str = "data/rag_vectors"):
        """
        Initialize RAG persistence layer.
        
        Args:
            db_path: Path to SQLite database
            vector_store_path: Path to vector store directory
        """
        self.db_path = Path(db_path)
        self.vector_store_path = Path(vector_store_path)
        
        # Create directories
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"RAG Persistence initialized: {self.db_path}")
    
    def _init_database(self):
        """Initialize database schema."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Indexed documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS indexed_documents (
                    doc_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_type TEXT NOT NULL,
                    indexed_at TEXT NOT NULL,
                    last_accessed TEXT,
                    access_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # Document chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    content_length INTEGER NOT NULL,
                    embedding_vector BLOB,
                    metadata TEXT,
                    FOREIGN KEY (doc_id) REFERENCES indexed_documents(doc_id) ON DELETE CASCADE
                )
            """)
            
            # Query logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_logs (
                    query_id TEXT PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    results_count INTEGER NOT NULL,
                    retrieval_time REAL NOT NULL,
                    executed_at TEXT NOT NULL,
                    agent_id TEXT,
                    user_id TEXT
                )
            """)
            
            # System configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_config (
                    config_key TEXT PRIMARY KEY,
                    config_value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_file_path ON indexed_documents(file_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_hash ON indexed_documents(content_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunk_doc_id ON document_chunks(doc_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_executed_at ON query_logs(executed_at)")
            
            conn.commit()
            logger.info("Database schema initialized")
    
    # Document Management
    
    def save_document(self, document: IndexedDocument) -> bool:
        """
        Save indexed document metadata.
        
        Args:
            document: Indexed document to save
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                metadata_json = json.dumps(document.metadata) if document.metadata else None
                
                cursor.execute("""
                    INSERT OR REPLACE INTO indexed_documents 
                    (doc_id, file_path, content_hash, chunk_count, file_size, file_type, 
                     indexed_at, last_accessed, access_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    document.doc_id,
                    document.file_path,
                    document.content_hash,
                    document.chunk_count,
                    document.file_size,
                    document.file_type,
                    document.indexed_at,
                    document.last_accessed,
                    document.access_count,
                    metadata_json
                ))
                
                conn.commit()
                logger.debug(f"Saved document: {document.doc_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            return False
    
    def get_document(self, doc_id: str) -> Optional[IndexedDocument]:
        """Get indexed document by ID."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM indexed_documents WHERE doc_id = ?", (doc_id,))
                row = cursor.fetchone()
                
                if row:
                    metadata = json.loads(row[9]) if row[9] else None
                    return IndexedDocument(
                        doc_id=row[0],
                        file_path=row[1],
                        content_hash=row[2],
                        chunk_count=row[3],
                        file_size=row[4],
                        file_type=row[5],
                        indexed_at=row[6],
                        last_accessed=row[7],
                        access_count=row[8],
                        metadata=metadata
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            return None
    
    def get_document_by_path(self, file_path: str) -> Optional[IndexedDocument]:
        """Get indexed document by file path."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM indexed_documents WHERE file_path = ?", (file_path,))
                row = cursor.fetchone()
                
                if row:
                    metadata = json.loads(row[9]) if row[9] else None
                    return IndexedDocument(
                        doc_id=row[0],
                        file_path=row[1],
                        content_hash=row[2],
                        chunk_count=row[3],
                        file_size=row[4],
                        file_type=row[5],
                        indexed_at=row[6],
                        last_accessed=row[7],
                        access_count=row[8],
                        metadata=metadata
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to get document by path: {e}")
            return None
    
    def update_document_access(self, doc_id: str):
        """Update document last accessed time and count."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE indexed_documents 
                    SET last_accessed = ?, access_count = access_count + 1
                    WHERE doc_id = ?
                """, (datetime.now().isoformat(), doc_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update document access: {e}")
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document and all its chunks."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM indexed_documents WHERE doc_id = ?", (doc_id,))
                conn.commit()
                logger.info(f"Deleted document: {doc_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def list_documents(self, limit: int = 100, offset: int = 0) -> List[IndexedDocument]:
        """List all indexed documents."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM indexed_documents 
                    ORDER BY indexed_at DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                documents = []
                for row in cursor.fetchall():
                    metadata = json.loads(row[9]) if row[9] else None
                    documents.append(IndexedDocument(
                        doc_id=row[0],
                        file_path=row[1],
                        content_hash=row[2],
                        chunk_count=row[3],
                        file_size=row[4],
                        file_type=row[5],
                        indexed_at=row[6],
                        last_accessed=row[7],
                        access_count=row[8],
                        metadata=metadata
                    ))
                
                return documents
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    # Chunk Management
    
    def save_chunk(self, chunk: DocumentChunk) -> bool:
        """Save document chunk."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                metadata_json = json.dumps(chunk.metadata) if chunk.metadata else None
                
                cursor.execute("""
                    INSERT OR REPLACE INTO document_chunks 
                    (chunk_id, doc_id, chunk_index, content, content_length, embedding_vector, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id,
                    chunk.doc_id,
                    chunk.chunk_index,
                    chunk.content,
                    chunk.content_length,
                    chunk.embedding_vector,
                    metadata_json
                ))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save chunk: {e}")
            return False
    
    def get_document_chunks(self, doc_id: str) -> List[DocumentChunk]:
        """Get all chunks for a document."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM document_chunks 
                    WHERE doc_id = ? 
                    ORDER BY chunk_index
                """, (doc_id,))
                
                chunks = []
                for row in cursor.fetchall():
                    metadata = json.loads(row[6]) if row[6] else None
                    chunks.append(DocumentChunk(
                        chunk_id=row[0],
                        doc_id=row[1],
                        chunk_index=row[2],
                        content=row[3],
                        content_length=row[4],
                        embedding_vector=row[5],
                        metadata=metadata
                    ))
                
                return chunks
        except Exception as e:
            logger.error(f"Failed to get chunks: {e}")
            return []
    
    # Query Logs
    
    def log_query(self, query_log: QueryLog) -> bool:
        """Log a query execution."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO query_logs 
                    (query_id, query_text, query_type, results_count, retrieval_time, 
                     executed_at, agent_id, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    query_log.query_id,
                    query_log.query_text,
                    query_log.query_type,
                    query_log.results_count,
                    query_log.retrieval_time,
                    query_log.executed_at,
                    query_log.agent_id,
                    query_log.user_id
                ))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            return False
    
    def get_query_history(self, limit: int = 100) -> List[QueryLog]:
        """Get recent query history."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM query_logs 
                    ORDER BY executed_at DESC 
                    LIMIT ?
                """, (limit,))
                
                logs = []
                for row in cursor.fetchall():
                    logs.append(QueryLog(
                        query_id=row[0],
                        query_text=row[1],
                        query_type=row[2],
                        results_count=row[3],
                        retrieval_time=row[4],
                        executed_at=row[5],
                        agent_id=row[6],
                        user_id=row[7]
                    ))
                
                return logs
        except Exception as e:
            logger.error(f"Failed to get query history: {e}")
            return []
    
    # Vector Store Management
    
    def save_vector_store(self, vector_store: Any, name: str = "faiss_index") -> bool:
        """
        Save FAISS vector store to disk.
        
        Args:
            vector_store: FAISS vector store object
            name: Name for the vector store
            
        Returns:
            True if successful
        """
        try:
            store_path = self.vector_store_path / name
            vector_store.save_local(str(store_path))
            
            # Update config
            self.set_config("vector_store_path", str(store_path))
            self.set_config("vector_store_updated_at", datetime.now().isoformat())
            
            logger.info(f"Vector store saved to {store_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")
            return False
    
    def load_vector_store(self, embeddings: Any, name: str = "faiss_index") -> Optional[Any]:
        """
        Load FAISS vector store from disk.
        
        Args:
            embeddings: Embeddings object for loading
            name: Name of the vector store
            
        Returns:
            FAISS vector store or None
        """
        try:
            from langchain_community.vectorstores import FAISS
            
            store_path = self.vector_store_path / name
            
            if not store_path.exists():
                logger.warning(f"Vector store not found at {store_path}")
                return None
            
            vector_store = FAISS.load_local(
                str(store_path),
                embeddings,
                allow_dangerous_deserialization=True
            )
            
            logger.info(f"Vector store loaded from {store_path}")
            return vector_store
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            return None
    
    # Configuration Management
    
    def set_config(self, key: str, value: str) -> bool:
        """Set configuration value."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO rag_config (config_key, config_value, updated_at)
                    VALUES (?, ?, ?)
                """, (key, value, datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to set config: {e}")
            return False
    
    def get_config(self, key: str, default: str = None) -> Optional[str]:
        """Get configuration value."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT config_value FROM rag_config WHERE config_key = ?", (key,))
                row = cursor.fetchone()
                return row[0] if row else default
        except Exception as e:
            logger.error(f"Failed to get config: {e}")
            return default
    
    # Statistics and Analytics
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Document statistics
                cursor.execute("SELECT COUNT(*), SUM(chunk_count), SUM(file_size) FROM indexed_documents")
                doc_stats = cursor.fetchone()
                
                # Query statistics
                cursor.execute("""
                    SELECT COUNT(*), AVG(retrieval_time), AVG(results_count)
                    FROM query_logs
                    WHERE executed_at >= datetime('now', '-7 days')
                """)
                query_stats = cursor.fetchone()
                
                # Most accessed documents
                cursor.execute("""
                    SELECT file_path, access_count 
                    FROM indexed_documents 
                    ORDER BY access_count DESC 
                    LIMIT 10
                """)
                top_docs = cursor.fetchall()
                
                return {
                    "total_documents": doc_stats[0] or 0,
                    "total_chunks": doc_stats[1] or 0,
                    "total_bytes": doc_stats[2] or 0,
                    "queries_last_7_days": query_stats[0] or 0,
                    "avg_retrieval_time": query_stats[1] or 0,
                    "avg_results_count": query_stats[2] or 0,
                    "top_accessed_documents": [
                        {"file_path": row[0], "access_count": row[1]}
                        for row in top_docs
                    ],
                    "database_path": str(self.db_path),
                    "vector_store_path": str(self.vector_store_path)
                }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    # Maintenance
    
    def cleanup_old_queries(self, days: int = 30) -> int:
        """Delete query logs older than specified days."""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM query_logs WHERE executed_at < ?", (cutoff,))
                deleted = cursor.rowcount
                conn.commit()
                logger.info(f"Deleted {deleted} old query logs")
                return deleted
        except Exception as e:
            logger.error(f"Failed to cleanup queries: {e}")
            return 0
    
    def vacuum_database(self):
        """Optimize database by vacuuming."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("VACUUM")
                logger.info("Database vacuumed successfully")
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
    
    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """Create database backup."""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{self.db_path}.backup_{timestamp}"
            
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return False

