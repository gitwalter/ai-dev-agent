"""
Event Bus - Inter-Module Communication System
============================================

Provides publish/subscribe pattern for loose coupling between modules.
Enables modules to communicate without direct dependencies.

Author: AI Development Agent
Created: 2025-01-02
"""

import logging
from typing import Dict, List, Callable, Any
from datetime import datetime
import threading
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Event data structure."""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    source_module: str
    event_id: str


class EventBus:
    """Centralized event bus for inter-module communication."""
    
    def __init__(self):
        """Initialize the event bus."""
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.lock = threading.Lock()
        self._event_counter = 0
        
        logger.info("✅ Event Bus initialized")
    
    def subscribe(self, event_type: str, callback: Callable, module_name: str = "unknown") -> bool:
        """
        Subscribe to specific event types.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
            module_name: Name of subscribing module for logging
            
        Returns:
            bool: True if subscription successful
        """
        try:
            with self.lock:
                if event_type not in self.subscribers:
                    self.subscribers[event_type] = []
                
                self.subscribers[event_type].append(callback)
                
            logger.info(f"📡 Module '{module_name}' subscribed to '{event_type}' events")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to subscribe {module_name} to {event_type}: {e}")
            return False
    
    def unsubscribe(self, event_type: str, callback: Callable, module_name: str = "unknown") -> bool:
        """
        Unsubscribe from specific event types.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to remove from subscribers
            module_name: Name of unsubscribing module for logging
            
        Returns:
            bool: True if unsubscription successful
        """
        try:
            with self.lock:
                if event_type in self.subscribers:
                    if callback in self.subscribers[event_type]:
                        self.subscribers[event_type].remove(callback)
                        
                        # Clean up empty subscriber lists
                        if not self.subscribers[event_type]:
                            del self.subscribers[event_type]
                        
                        logger.info(f"📡 Module '{module_name}' unsubscribed from '{event_type}' events")
                        return True
            
            logger.warning(f"⚠️ Callback not found for {module_name} unsubscribing from {event_type}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to unsubscribe {module_name} from {event_type}: {e}")
            return False
    
    def publish(self, event_type: str, data: Dict[str, Any], source_module: str = "unknown") -> bool:
        """
        Publish events to all subscribers.
        
        Args:
            event_type: Type of event being published
            data: Event data payload
            source_module: Name of module publishing the event
            
        Returns:
            bool: True if event published successfully
        """
        try:
            # Create event object
            with self.lock:
                self._event_counter += 1
                event_id = f"evt_{self._event_counter}_{int(datetime.now().timestamp())}"
            
            event = Event(
                event_type=event_type,
                data=data,
                timestamp=datetime.now(),
                source_module=source_module,
                event_id=event_id
            )
            
            # Store in history
            with self.lock:
                self.event_history.append(event)
                
                # Keep only last 1000 events
                if len(self.event_history) > 1000:
                    self.event_history = self.event_history[-1000:]
            
            # Notify subscribers
            subscribers_notified = 0
            if event_type in self.subscribers:
                for callback in self.subscribers[event_type]:
                    try:
                        callback(event)
                        subscribers_notified += 1
                    except Exception as e:
                        logger.error(f"❌ Error in event callback for {event_type}: {e}")
            
            logger.debug(f"📢 Event '{event_type}' published by '{source_module}' to {subscribers_notified} subscribers")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish event {event_type} from {source_module}: {e}")
            return False
    
    def get_event_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return
            
        Returns:
            List[Event]: List of events
        """
        with self.lock:
            events = self.event_history.copy()
        
        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Return most recent events up to limit
        return events[-limit:] if limit else events
    
    def get_subscribers_count(self, event_type: str = None) -> int:
        """
        Get number of subscribers.
        
        Args:
            event_type: Specific event type (optional)
            
        Returns:
            int: Number of subscribers
        """
        with self.lock:
            if event_type:
                return len(self.subscribers.get(event_type, []))
            else:
                return sum(len(subs) for subs in self.subscribers.values())
    
    def get_event_types(self) -> List[str]:
        """
        Get all event types with subscribers.
        
        Returns:
            List[str]: List of event types
        """
        with self.lock:
            return list(self.subscribers.keys())
    
    def clear_history(self) -> None:
        """Clear event history."""
        with self.lock:
            self.event_history.clear()
        logger.info("🧹 Event history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get event bus statistics.
        
        Returns:
            Dict[str, Any]: Statistics about the event bus
        """
        with self.lock:
            stats = {
                "total_events": len(self.event_history),
                "event_types": len(self.subscribers),
                "total_subscribers": sum(len(subs) for subs in self.subscribers.values()),
                "event_type_breakdown": {
                    event_type: len(subscribers) 
                    for event_type, subscribers in self.subscribers.items()
                },
                "recent_events": [
                    {
                        "type": e.event_type,
                        "source": e.source_module,
                        "timestamp": e.timestamp.isoformat()
                    }
                    for e in self.event_history[-10:]
                ]
            }
        
        return stats


# Global event bus instance
_global_event_bus = None


def get_event_bus() -> EventBus:
    """
    Get the global event bus instance.
    
    Returns:
        EventBus: Global event bus instance
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


# Common event types
class EventTypes:
    """Common event type constants."""
    
    # Agent events
    AGENT_CREATED = "agent_created"
    AGENT_UPDATED = "agent_updated"
    AGENT_DELETED = "agent_deleted"
    AGENT_STATUS_CHANGED = "agent_status_changed"
    
    # Swarm events
    SWARM_CREATED = "swarm_created"
    SWARM_STARTED = "swarm_started"
    SWARM_STOPPED = "swarm_stopped"
    SWARM_TASK_ASSIGNED = "swarm_task_assigned"
    SWARM_TASK_COMPLETED = "swarm_task_completed"
    
    # MCP events
    MCP_SERVER_STATUS_CHANGED = "mcp_server_status_changed"
    MCP_TOOL_REGISTERED = "mcp_tool_registered"
    MCP_TOOL_EXECUTED = "mcp_tool_executed"
    MCP_PROMPT_UPDATED = "mcp_prompt_updated"
    
    # RAG events
    RAG_DOCUMENT_PROCESSED = "rag_document_processed"
    RAG_SEARCH_PERFORMED = "rag_search_performed"
    RAG_KNOWLEDGE_UPDATED = "rag_knowledge_updated"
    
    # Chat events
    CHAT_MESSAGE_SENT = "chat_message_sent"
    CHAT_MESSAGE_RECEIVED = "chat_message_received"
    CHAT_SESSION_STARTED = "chat_session_started"
    CHAT_SESSION_ENDED = "chat_session_ended"
    
    # System events
    MODULE_LOADED = "module_loaded"
    MODULE_ERROR = "module_error"
    SYSTEM_STATUS_CHANGED = "system_status_changed"
    USER_ACTION = "user_action"
