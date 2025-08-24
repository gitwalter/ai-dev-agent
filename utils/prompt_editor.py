"""
Prompt Editor for AI Development Agent System.

This module provides utilities for editing and managing system prompts
for different agents and the overall system.
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PromptEditor:
    """
    Editor for managing and editing system prompts.
    """
    
    def __init__(self, db_path: str = "prompts/prompt_templates.db"):
        """
        Initialize the prompt editor.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create system_prompts table for overall system prompts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_name TEXT UNIQUE NOT NULL,
                    prompt_template TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create rag_documents table for RAG documents
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_url TEXT,
                    file_path TEXT,
                    agent_name TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create rag_embeddings table for document embeddings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    embedding_data TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES rag_documents (id)
                )
            """)
            
            conn.commit()
    
    def get_agent_prompts(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all prompts for a specific agent."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, prompt_template, prompt_variables, created_at, 
                       updated_at, usage_count, success_rate, is_active
                FROM prompts 
                WHERE agent_name = ? AND is_active = 1
                ORDER BY created_at DESC
            """, (agent_name,))
            
            prompts = []
            for row in cursor.fetchall():
                try:
                    variables = json.loads(row[2]) if row[2] else {}
                except:
                    variables = {}
                    
                prompts.append({
                    'id': row[0],
                    'template': row[1],
                    'variables': variables,
                    'created_at': row[3],
                    'updated_at': row[4],
                    'usage_count': row[5],
                    'success_rate': row[6],
                    'is_active': row[7]
                })
            
            return prompts
    
    def get_system_prompts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get system prompts, optionally filtered by category."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT id, prompt_name, prompt_template, description, 
                           category, is_active, created_at, updated_at
                    FROM system_prompts 
                    WHERE category = ? AND is_active = 1
                    ORDER BY prompt_name
                """, (category,))
            else:
                cursor.execute("""
                    SELECT id, prompt_name, prompt_template, description, 
                           category, is_active, created_at, updated_at
                    FROM system_prompts 
                    WHERE is_active = 1
                    ORDER BY category, prompt_name
                """)
            
            prompts = []
            for row in cursor.fetchall():
                prompts.append({
                    'id': row[0],
                    'name': row[1],
                    'template': row[2],
                    'description': row[3],
                    'category': row[4],
                    'is_active': row[5],
                    'created_at': row[6],
                    'updated_at': row[7]
                })
            
            return prompts
    
    def update_agent_prompt(self, prompt_id: int, new_template: str, 
                           description: str = None) -> bool:
        """
        Update an existing agent prompt.
        
        Args:
            prompt_id: ID of the prompt to update
            new_template: New prompt template
            description: Optional description of the change
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update the prompt template
                cursor.execute("""
                    UPDATE prompts 
                    SET prompt_template = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_template, prompt_id))
                
                # Add a note about the update in variables
                cursor.execute("""
                    UPDATE prompts 
                    SET prompt_variables = json_set(
                        prompt_variables, 
                        '$.last_edit', ?,
                        '$.edit_description', ?
                    )
                    WHERE id = ?
                """, (datetime.now().isoformat(), description or "Updated via prompt editor", prompt_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating agent prompt {prompt_id}: {e}")
            return False
    
    def create_system_prompt(self, name: str, template: str, category: str, 
                           description: str = None) -> int:
        """
        Create a new system prompt.
        
        Args:
            name: Name of the prompt
            template: Prompt template
            category: Category (e.g., 'workflow', 'general', 'error_handling')
            description: Optional description
            
        Returns:
            Prompt ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO system_prompts 
                    (prompt_name, prompt_template, description, category, created_at, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (name, template, description, category))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Error creating system prompt {name}: {e}")
            return -1
    
    def update_system_prompt(self, prompt_id: int, template: str, 
                           description: str = None) -> bool:
        """
        Update an existing system prompt.
        
        Args:
            prompt_id: ID of the prompt to update
            template: New prompt template
            description: Optional description
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE system_prompts 
                    SET prompt_template = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (template, description, prompt_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating system prompt {prompt_id}: {e}")
            return False
    
    def delete_system_prompt(self, prompt_id: int) -> bool:
        """
        Soft delete a system prompt.
        
        Args:
            prompt_id: ID of the prompt to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE system_prompts 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (prompt_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error deleting system prompt {prompt_id}: {e}")
            return False
    
    def add_rag_document(self, title: str, content: str, source_type: str,
                        source_url: str = None, file_path: str = None,
                        agent_name: str = None, tags: List[str] = None) -> int:
        """
        Add a RAG document.
        
        Args:
            title: Document title
            content: Document content
            source_type: Type of source ('url', 'file', 'text')
            source_url: Source URL if applicable
            file_path: File path if applicable
            agent_name: Associated agent if applicable
            tags: List of tags
            
        Returns:
            Document ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO rag_documents 
                    (title, content, source_type, source_url, file_path, 
                     agent_name, tags, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    title, content, source_type, source_url, file_path,
                    agent_name, json.dumps(tags) if tags else None
                ))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Error adding RAG document {title}: {e}")
            return -1
    
    def get_rag_documents(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get RAG documents, optionally filtered by agent.
        
        Args:
            agent_name: Optional agent name to filter by
            
        Returns:
            List of RAG documents
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if agent_name:
                cursor.execute("""
                    SELECT id, title, content, source_type, source_url, 
                           file_path, agent_name, tags, created_at, updated_at
                    FROM rag_documents 
                    WHERE agent_name = ? AND is_active = 1
                    ORDER BY created_at DESC
                """, (agent_name,))
            else:
                cursor.execute("""
                    SELECT id, title, content, source_type, source_url, 
                           file_path, agent_name, tags, created_at, updated_at
                    FROM rag_documents 
                    WHERE is_active = 1
                    ORDER BY created_at DESC
                """)
            
            documents = []
            for row in cursor.fetchall():
                try:
                    tags = json.loads(row[7]) if row[7] else []
                except:
                    tags = []
                    
                documents.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'source_type': row[3],
                    'source_url': row[4],
                    'file_path': row[5],
                    'agent_name': row[6],
                    'tags': tags,
                    'created_at': row[8],
                    'updated_at': row[9]
                })
            
            return documents
    
    def delete_rag_document(self, document_id: int) -> bool:
        """
        Soft delete a RAG document.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE rag_documents 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (document_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error deleting RAG document {document_id}: {e}")
            return False
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """Get statistics about prompts and documents."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Agent prompts statistics
            cursor.execute("""
                SELECT COUNT(*) as total_agent_prompts,
                       COUNT(DISTINCT agent_name) as unique_agents,
                       AVG(success_rate) as avg_success_rate
                FROM prompts 
                WHERE is_active = 1
            """)
            
            agent_stats = cursor.fetchone()
            
            # System prompts statistics
            cursor.execute("""
                SELECT COUNT(*) as total_system_prompts,
                       COUNT(DISTINCT category) as unique_categories
                FROM system_prompts 
                WHERE is_active = 1
            """)
            
            system_stats = cursor.fetchone()
            
            # RAG documents statistics
            cursor.execute("""
                SELECT COUNT(*) as total_rag_documents,
                       COUNT(DISTINCT agent_name) as agents_with_docs,
                       COUNT(DISTINCT source_type) as unique_source_types
                FROM rag_documents 
                WHERE is_active = 1
            """)
            
            rag_stats = cursor.fetchone()
            
            return {
                'agent_prompts': {
                    'total': agent_stats[0],
                    'unique_agents': agent_stats[1],
                    'avg_success_rate': agent_stats[2] or 0.0
                },
                'system_prompts': {
                    'total': system_stats[0],
                    'unique_categories': system_stats[1]
                },
                'rag_documents': {
                    'total': rag_stats[0],
                    'agents_with_docs': rag_stats[1],
                    'unique_source_types': rag_stats[2]
                }
            }


# Global prompt editor instance
_prompt_editor = None


def get_prompt_editor() -> PromptEditor:
    """Get the global prompt editor instance."""
    global _prompt_editor
    if _prompt_editor is None:
        _prompt_editor = PromptEditor()
    return _prompt_editor
