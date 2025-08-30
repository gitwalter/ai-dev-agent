"""
Prompt Management Module
========================

Provides functionality for storing, retrieving, and managing prompts used by AI agents.
Integrates with the prompt database and provides execution tracking capabilities.

Author: AI-Dev-Agent System
Version: 1.0
Last Updated: Current Session
"""

import logging
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages prompt storage, retrieval, and execution tracking."""
    
    def __init__(self, db_path: str = "prompts/prompt_templates.db"):
        """
        Initialize the prompt manager.
        
        Args:
            db_path: Path to the prompt database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the prompt database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create prompt storage table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stored_prompts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_type TEXT NOT NULL,
                        prompt_text TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        version INTEGER DEFAULT 1,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Create execution tracking table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prompt_executions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_type TEXT NOT NULL,
                        prompt_id INTEGER,
                        success BOOLEAN NOT NULL,
                        execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        error_message TEXT,
                        performance_metrics TEXT,
                        FOREIGN KEY (prompt_id) REFERENCES stored_prompts (id)
                    )
                """)
                
                conn.commit()
                logger.info("Prompt database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize prompt database: {e}")
            raise
    
    def store_prompt(self, agent_type: str, prompt_text: str) -> int:
        """
        Store a prompt for an agent type.
        
        Args:
            agent_type: Type of agent (e.g., 'requirements_analyst', 'code_generator')
            prompt_text: The prompt content to store
            
        Returns:
            int: The ID of the stored prompt
            
        Raises:
            ValueError: If agent_type or prompt_text is empty
            RuntimeError: If database operation fails
        """
        if not agent_type or not agent_type.strip():
            raise ValueError("Agent type cannot be empty")
        
        if not prompt_text or not prompt_text.strip():
            raise ValueError("Prompt text cannot be empty")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Deactivate previous prompts for this agent type
                cursor.execute("""
                    UPDATE stored_prompts 
                    SET is_active = FALSE 
                    WHERE agent_type = ? AND is_active = TRUE
                """, (agent_type,))
                
                # Store new prompt
                cursor.execute("""
                    INSERT INTO stored_prompts (agent_type, prompt_text, is_active)
                    VALUES (?, ?, TRUE)
                """, (agent_type, prompt_text))
                
                prompt_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Stored prompt for {agent_type} with ID {prompt_id}")
                return prompt_id
                
        except Exception as e:
            logger.error(f"Failed to store prompt for {agent_type}: {e}")
            raise RuntimeError(f"Database operation failed: {e}")
    
    def get_active_prompt(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """
        Get the active prompt for an agent type.
        
        Args:
            agent_type: Type of agent to get prompt for
            
        Returns:
            Dict containing prompt data or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, prompt_text, created_at, version
                    FROM stored_prompts 
                    WHERE agent_type = ? AND is_active = TRUE
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (agent_type,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "prompt_text": row[1],
                        "created_at": row[2],
                        "version": row[3]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Failed to get active prompt for {agent_type}: {e}")
            return None
    
    def get_simplified_prompt(self, agent_type: str) -> Optional[str]:
        """
        Get a simplified prompt for an agent type.
        
        Args:
            agent_type: Type of agent to get prompt for
            
        Returns:
            str: Simplified prompt text or None if not found
        """
        # For now, return the active prompt as simplified
        # This can be enhanced later to store different prompt types
        prompt_data = self.get_active_prompt(agent_type)
        return prompt_data["prompt_text"] if prompt_data else None
    
    def get_enhanced_prompt(self, agent_type: str) -> Optional[str]:
        """
        Get an enhanced prompt for an agent type.
        
        Args:
            agent_type: Type of agent to get prompt for
            
        Returns:
            str: Enhanced prompt text or None if not found
        """
        # For now, return the active prompt as enhanced
        # This can be enhanced later to store different prompt types
        prompt_data = self.get_active_prompt(agent_type)
        return prompt_data["prompt_text"] if prompt_data else None
    
    def get_best_prompt(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """
        Get the best available prompt for an agent type.
        
        Args:
            agent_type: Type of agent to get prompt for
            
        Returns:
            Dict containing prompt data or None if not found
        """
        return self.get_active_prompt(agent_type)
    
    def record_execution(self, agent_type: str, success: bool, 
                        error_message: Optional[str] = None,
                        performance_metrics: Optional[Dict[str, Any]] = None) -> bool:
        """
        Record the result of a prompt execution.
        
        Args:
            agent_type: Type of agent that executed the prompt
            success: Whether the execution was successful
            error_message: Error message if execution failed
            performance_metrics: Performance metrics from execution
            
        Returns:
            bool: True if recording was successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get the active prompt ID for this agent type
                prompt_data = self.get_active_prompt(agent_type)
                prompt_id = prompt_data["id"] if prompt_data else None
                
                # Serialize performance metrics
                metrics_json = json.dumps(performance_metrics) if performance_metrics else None
                
                cursor.execute("""
                    INSERT INTO prompt_executions 
                    (agent_type, prompt_id, success, error_message, performance_metrics)
                    VALUES (?, ?, ?, ?, ?)
                """, (agent_type, prompt_id, success, error_message, metrics_json))
                
                conn.commit()
                logger.info(f"Recorded execution for {agent_type}: success={success}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to record execution for {agent_type}: {e}")
            return False
    
    def get_execution_history(self, agent_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get execution history for an agent type.
        
        Args:
            agent_type: Type of agent to get history for
            limit: Maximum number of records to return
            
        Returns:
            List of execution records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT execution_time, success, error_message, performance_metrics
                    FROM prompt_executions 
                    WHERE agent_type = ?
                    ORDER BY execution_time DESC
                    LIMIT ?
                """, (agent_type, limit))
                
                rows = cursor.fetchall()
                history = []
                
                for row in rows:
                    metrics = json.loads(row[3]) if row[3] else None
                    history.append({
                        "execution_time": row[0],
                        "success": bool(row[1]),
                        "error_message": row[2],
                        "performance_metrics": metrics
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Failed to get execution history for {agent_type}: {e}")
            return []

    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """
        Get all stored prompts.
        
        Returns:
            List of all prompts
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM stored_prompts ORDER BY created_at DESC")
                
                columns = [description[0] for description in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    result = dict(zip(columns, row))
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to get all prompts: {e}")
            return []


# Global prompt manager instance
_prompt_manager = None

def get_prompt_manager() -> PromptManager:
    """Get the global prompt manager instance."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager

def store_agent_prompt(agent_type: str, prompt: str) -> int:
    """
    Store a prompt for an agent type.
    
    Args:
        agent_type: Type of agent
        prompt: Prompt content to store
        
    Returns:
        int: ID of stored prompt
    """
    manager = get_prompt_manager()
    return manager.store_prompt(agent_type, prompt)

def record_prompt_execution(agent_type: str, success: bool, 
                           error_message: Optional[str] = None,
                           performance_metrics: Optional[Dict[str, Any]] = None) -> bool:
    """
    Record the result of a prompt execution.
    
    Args:
        agent_type: Type of agent that executed the prompt
        success: Whether execution was successful
        error_message: Error message if execution failed
        performance_metrics: Performance metrics from execution
        
    Returns:
        bool: True if recording was successful
    """
    manager = get_prompt_manager()
    return manager.record_execution(agent_type, success, error_message, performance_metrics)

def get_agent_prompt(agent_type: str) -> Optional[str]:
    """
    Get the active prompt for an agent type.
    
    Args:
        agent_type: Type of agent
        
    Returns:
        str: Active prompt text or None if not found
    """
    manager = get_prompt_manager()
    prompt_data = manager.get_active_prompt(agent_type)
    return prompt_data["prompt_text"] if prompt_data else None

def get_prompt_execution_history(agent_type: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get execution history for an agent type.
    
    Args:
        agent_type: Type of agent
        limit: Maximum records to return
        
    Returns:
        List of execution records
    """
    manager = get_prompt_manager()
    return manager.get_execution_history(agent_type, limit)
