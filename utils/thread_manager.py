"""
Thread ID Management for LangGraph State Persistence

This module provides thread ID management following LangGraph best practices:
- Unique thread_id per user session
- Persistent thread_id across interactions
- Thread history and session management
- Config generation for LangGraph graphs

Based on LangGraph documentation:
https://docs.langchain.com/oss/python/langgraph/add-memory
"""

import uuid
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ThreadSession:
    """Represents a single thread session with metadata."""
    
    thread_id: str
    created_at: datetime
    last_active: datetime
    message_count: int = 0
    session_type: str = "chat"  # "chat", "development", "rag"
    metadata: Dict = field(default_factory=dict)
    name: str = None  # User-friendly name for the thread
    
    def __post_init__(self):
        """Set default name if not provided."""
        if self.name is None:
            self.name = f"New {self.session_type.title()} Session"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "thread_id": self.thread_id,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "message_count": self.message_count,
            "session_type": self.session_type,
            "metadata": self.metadata,
            "name": self.name
        }
    
    def get_display_name(self) -> str:
        """Get display name with message count."""
        return f"{self.name} ({self.message_count} msgs)"


class ThreadManager:
    """
    Manages thread IDs for LangGraph stateful workflows.
    
    Features:
    - Create unique thread IDs per session
    - Maintain thread history
    - Generate LangGraph config with thread_id
    - Session lifecycle management
    
    Usage:
        # Initialize
        manager = ThreadManager(session_type="rag")
        
        # Get current thread config
        config = manager.get_current_config()
        
        # Execute graph with config
        result = await graph.ainvoke({"messages": [...]}, config=config)
        
        # Create new session
        manager.create_new_session()
    """
    
    def __init__(self, session_type: str = "chat", prefix: str = None):
        """
        Initialize thread manager.
        
        Args:
            session_type: Type of session ("chat", "development", "rag")
            prefix: Optional custom prefix for thread IDs
        """
        self.session_type = session_type
        self.prefix = prefix or session_type
        self.current_session: Optional[ThreadSession] = None
        self.session_history: List[ThreadSession] = []
        
        # Create initial session
        self.create_new_session()
        
        logger.info(f"✅ ThreadManager initialized for '{session_type}'")
    
    def create_new_session(self, metadata: Dict = None, name: str = None) -> ThreadSession:
        """
        Create a new thread session with unique ID.
        
        Args:
            metadata: Optional metadata for the session
            name: Optional user-friendly name for the session
            
        Returns:
            New ThreadSession object
        """
        # Generate unique thread ID
        thread_id = f"{self.prefix}_{uuid.uuid4().hex[:8]}"
        
        # Create session
        now = datetime.now()
        session = ThreadSession(
            thread_id=thread_id,
            created_at=now,
            last_active=now,
            session_type=self.session_type,
            metadata=metadata or {},
            name=name or f"New {self.session_type.title()} Session"
        )
        
        # Update current and history
        self.current_session = session
        self.session_history.append(session)
        
        logger.info(f"🆕 Created new session: {thread_id} ({session.name})")
        return session
    
    def get_current_thread_id(self) -> str:
        """Get the current thread ID."""
        if not self.current_session:
            self.create_new_session()
        return self.current_session.thread_id
    
    def get_current_config(self) -> Dict:
        """
        Get LangGraph config with current thread ID.
        
        This is the standard format for LangGraph:
        config = {"configurable": {"thread_id": "..."}}
        
        Returns:
            Config dictionary for LangGraph graph execution
        """
        thread_id = self.get_current_thread_id()
        return {"configurable": {"thread_id": thread_id}}
    
    def update_activity(self, message_count_delta: int = 1):
        """
        Update last activity time and message count.
        
        Args:
            message_count_delta: Number of messages to add (default: 1)
        """
        if self.current_session:
            self.current_session.last_active = datetime.now()
            self.current_session.message_count += message_count_delta
    
    def set_session_name(self, name: str, thread_id: str = None):
        """
        Set a user-friendly name for a session.
        
        Args:
            name: New name for the session
            thread_id: Thread ID (uses current session if None)
        """
        if thread_id is None:
            if self.current_session:
                self.current_session.name = name
                logger.info(f"📝 Renamed session {self.current_session.thread_id} to '{name}'")
        else:
            session = self.get_session_info(thread_id)
            if session:
                session.name = name
                logger.info(f"📝 Renamed session {thread_id} to '{name}'")
    
    def auto_name_from_query(self, query: str, thread_id: str = None, max_length: int = 50):
        """
        Automatically generate a name from the first query.
        
        Args:
            query: The user's query
            thread_id: Thread ID (uses current session if None)
            max_length: Maximum length for the name
        """
        # Clean and truncate query
        clean_query = query.strip().replace('\n', ' ')
        if len(clean_query) > max_length:
            name = clean_query[:max_length] + "..."
        else:
            name = clean_query
        
        self.set_session_name(name, thread_id)
    
    def load_session(self, thread_id: str) -> bool:
        """
        Load a session from history by thread ID.
        
        Args:
            thread_id: Thread ID to load
            
        Returns:
            True if session was found and loaded, False otherwise
        """
        for session in self.session_history:
            if session.thread_id == thread_id:
                self.current_session = session
                self.update_activity(message_count_delta=0)
                logger.info(f"📂 Loaded session: {thread_id}")
                return True
        
        logger.warning(f"⚠️ Session not found: {thread_id}")
        return False
    
    def get_session_history(self) -> List[ThreadSession]:
        """Get list of all sessions in reverse chronological order."""
        return sorted(
            self.session_history,
            key=lambda s: s.last_active,
            reverse=True
        )
    
    def get_session_info(self, thread_id: str) -> Optional[ThreadSession]:
        """Get session info by thread ID."""
        for session in self.session_history:
            if session.thread_id == thread_id:
                return session
        return None
    
    def delete_session(self, thread_id: str) -> bool:
        """
        Delete a session from history.
        
        Args:
            thread_id: Thread ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        for i, session in enumerate(self.session_history):
            if session.thread_id == thread_id:
                self.session_history.pop(i)
                
                # If current session was deleted, create new one
                if self.current_session and self.current_session.thread_id == thread_id:
                    self.create_new_session()
                
                logger.info(f"🗑️ Deleted session: {thread_id}")
                return True
        
        return False
    
    def export_history(self) -> List[Dict]:
        """Export session history as list of dictionaries."""
        return [session.to_dict() for session in self.session_history]
    
    def get_stats(self) -> Dict:
        """Get statistics about thread usage."""
        return {
            "total_sessions": len(self.session_history),
            "current_thread_id": self.get_current_thread_id(),
            "total_messages": sum(s.message_count for s in self.session_history),
            "session_type": self.session_type
        }


def create_thread_manager(session_type: str = "chat", prefix: str = None) -> ThreadManager:
    """
    Factory function to create a ThreadManager.
    
    Args:
        session_type: Type of session ("chat", "development", "rag")
        prefix: Optional custom prefix for thread IDs
        
    Returns:
        ThreadManager instance
    """
    return ThreadManager(session_type=session_type, prefix=prefix)

