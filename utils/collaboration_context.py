#!/usr/bin/env python3
"""
Collaboration Context Manager for multi-agent collaboration.

This module manages collaboration context between agents, including:
- Shared context and knowledge
- Communication protocols
- Collaboration history
- Context synchronization
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, TypedDict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CollaborationMessage(TypedDict):
    """Represents a message between collaborating agents."""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: str  # "request", "response", "notification", "handoff"
    content: Dict[str, Any]
    timestamp: str
    priority: str  # "low", "normal", "high", "urgent"
    context: Dict[str, Any]
    status: str  # "sent", "delivered", "read", "processed"


class CollaborationContext(TypedDict):
    """Represents collaboration context between agents."""
    context_id: str
    session_id: str
    participating_agents: List[str]
    shared_knowledge: Dict[str, Any]
    communication_history: List[CollaborationMessage]
    collaboration_rules: Dict[str, Any]
    context_state: str  # "active", "paused", "completed", "failed"
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]


class CollaborationContextManager:
    """
    Manages collaboration context between multiple agents.
    
    This class handles:
    - Creating and managing collaboration contexts
    - Facilitating communication between agents
    - Maintaining shared knowledge and state
    - Tracking collaboration history
    - Enforcing collaboration rules
    """
    
    def __init__(self, storage_dir: str = "generated/collaboration"):
        """
        Initialize the collaboration context manager.
        
        Args:
            storage_dir: Directory to store collaboration data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Active collaboration contexts
        self.active_contexts: Dict[str, CollaborationContext] = {}
        
        # Collaboration rules and protocols
        self.collaboration_rules = self._load_default_rules()
        
        logger.info("CollaborationContextManager initialized")
    
    def _load_default_rules(self) -> Dict[str, Any]:
        """Load default collaboration rules."""
        return {
            "communication_protocol": {
                "message_timeout": 300,  # 5 minutes
                "max_retries": 3,
                "priority_levels": ["low", "normal", "high", "urgent"],
                "required_fields": ["message_id", "from_agent", "to_agent", "content"]
            },
            "context_sharing": {
                "auto_sync": True,
                "sync_interval": 60,  # 1 minute
                "max_context_size": 1024 * 1024,  # 1MB
                "compression_enabled": True
            },
            "collaboration_workflow": {
                "handoff_required": True,
                "validation_required": True,
                "approval_threshold": 0.8,
                "max_concurrent_agents": 5
            }
        }
    
    def create_collaboration_context(
        self,
        session_id: str,
        participating_agents: List[str],
        initial_knowledge: Dict[str, Any] = None,
        custom_rules: Dict[str, Any] = None
    ) -> CollaborationContext:
        """
        Create a new collaboration context.
        
        Args:
            session_id: Unique session identifier
            participating_agents: List of agent names participating in collaboration
            initial_knowledge: Initial shared knowledge
            custom_rules: Custom collaboration rules
            
        Returns:
            Created collaboration context
        """
        context_id = str(uuid.uuid4())
        
        context: CollaborationContext = {
            "context_id": context_id,
            "session_id": session_id,
            "participating_agents": participating_agents,
            "shared_knowledge": initial_knowledge or {},
            "communication_history": [],
            "collaboration_rules": {**self.collaboration_rules, **(custom_rules or {})},
            "context_state": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {
                "created_by": "system",
                "version": "1.0",
                "description": f"Collaboration context for session {session_id}"
            }
        }
        
        # Store context
        self.active_contexts[context_id] = context
        self._save_context(context)
        
        logger.info(f"Created collaboration context {context_id} for session {session_id}")
        return context
    
    def send_message(
        self,
        context_id: str,
        from_agent: str,
        to_agent: str,
        message_type: str,
        content: Dict[str, Any],
        priority: str = "normal",
        context: Dict[str, Any] = None
    ) -> CollaborationMessage:
        """
        Send a message between agents in a collaboration context.
        
        Args:
            context_id: Collaboration context ID
            from_agent: Sending agent name
            to_agent: Receiving agent name
            message_type: Type of message
            content: Message content
            priority: Message priority
            context: Additional context
            
        Returns:
            Created message
        """
        if context_id not in self.active_contexts:
            raise ValueError(f"Collaboration context {context_id} not found")
        
        collaboration_context = self.active_contexts[context_id]
        
        # Validate agents are participating
        if from_agent not in collaboration_context["participating_agents"]:
            raise ValueError(f"Agent {from_agent} not in collaboration context")
        if to_agent not in collaboration_context["participating_agents"]:
            raise ValueError(f"Agent {to_agent} not in collaboration context")
        
        # Create message
        message: CollaborationMessage = {
            "message_id": str(uuid.uuid4()),
            "from_agent": from_agent,
            "to_agent": to_agent,
            "message_type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "context": context or {},
            "status": "sent"
        }
        
        # Add to communication history
        collaboration_context["communication_history"].append(message)
        collaboration_context["updated_at"] = datetime.now().isoformat()
        
        # Update active contexts
        self.active_contexts[context_id] = collaboration_context
        self._save_context(collaboration_context)
        
        logger.info(f"Message sent from {from_agent} to {to_agent} in context {context_id}")
        return message
    
    def update_shared_knowledge(
        self,
        context_id: str,
        agent_name: str,
        knowledge_updates: Dict[str, Any],
        merge_strategy: str = "update"
    ) -> Dict[str, Any]:
        """
        Update shared knowledge in collaboration context.
        
        Args:
            context_id: Collaboration context ID
            agent_name: Agent updating the knowledge
            knowledge_updates: Knowledge updates to apply
            merge_strategy: How to merge updates ("update", "append", "replace")
            
        Returns:
            Updated shared knowledge
        """
        if context_id not in self.active_contexts:
            raise ValueError(f"Collaboration context {context_id} not found")
        
        collaboration_context = self.active_contexts[context_id]
        
        # Validate agent is participating
        if agent_name not in collaboration_context["participating_agents"]:
            raise ValueError(f"Agent {agent_name} not in collaboration context")
        
        current_knowledge = collaboration_context["shared_knowledge"]
        
        # Apply updates based on merge strategy
        if merge_strategy == "update":
            current_knowledge.update(knowledge_updates)
        elif merge_strategy == "append":
            for key, value in knowledge_updates.items():
                if key in current_knowledge:
                    if isinstance(current_knowledge[key], list):
                        current_knowledge[key].extend(value if isinstance(value, list) else [value])
                    else:
                        current_knowledge[key] = [current_knowledge[key], value]
                else:
                    current_knowledge[key] = value
        elif merge_strategy == "replace":
            current_knowledge = knowledge_updates
        else:
            raise ValueError(f"Invalid merge strategy: {merge_strategy}")
        
        # Update context
        collaboration_context["shared_knowledge"] = current_knowledge
        collaboration_context["updated_at"] = datetime.now().isoformat()
        
        # Add knowledge update to communication history
        self.send_message(
            context_id=context_id,
            from_agent=agent_name,
            to_agent="all",
            message_type="knowledge_update",
            content={"updates": knowledge_updates, "merge_strategy": merge_strategy},
            priority="normal"
        )
        
        # Update active contexts
        self.active_contexts[context_id] = collaboration_context
        self._save_context(collaboration_context)
        
        logger.info(f"Shared knowledge updated by {agent_name} in context {context_id}")
        return current_knowledge
    
    def get_collaboration_context(self, context_id: str) -> Optional[CollaborationContext]:
        """
        Get collaboration context by ID.
        
        Args:
            context_id: Collaboration context ID
            
        Returns:
            Collaboration context or None if not found
        """
        return self.active_contexts.get(context_id)
    
    def get_agent_context(self, context_id: str, agent_name: str) -> Dict[str, Any]:
        """
        Get context specific to an agent.
        
        Args:
            context_id: Collaboration context ID
            agent_name: Agent name
            
        Returns:
            Agent-specific context
        """
        if context_id not in self.active_contexts:
            raise ValueError(f"Collaboration context {context_id} not found")
        
        collaboration_context = self.active_contexts[context_id]
        
        # Get messages for this agent
        agent_messages = [
            msg for msg in collaboration_context["communication_history"]
            if msg["to_agent"] == agent_name or msg["to_agent"] == "all"
        ]
        
        # Get recent knowledge updates
        recent_updates = [
            msg for msg in agent_messages[-10:]  # Last 10 messages
            if msg["message_type"] == "knowledge_update"
        ]
        
        return {
            "context_id": context_id,
            "session_id": collaboration_context["session_id"],
            "agent_name": agent_name,
            "participating_agents": collaboration_context["participating_agents"],
            "shared_knowledge": collaboration_context["shared_knowledge"],
            "recent_messages": agent_messages[-5:],  # Last 5 messages
            "recent_knowledge_updates": recent_updates,
            "collaboration_rules": collaboration_context["collaboration_rules"],
            "context_state": collaboration_context["context_state"]
        }
    
    def update_message_status(
        self,
        context_id: str,
        message_id: str,
        status: str
    ) -> bool:
        """
        Update message status.
        
        Args:
            context_id: Collaboration context ID
            message_id: Message ID
            status: New status
            
        Returns:
            True if message was updated, False otherwise
        """
        if context_id not in self.active_contexts:
            return False
        
        collaboration_context = self.active_contexts[context_id]
        
        # Find and update message
        for message in collaboration_context["communication_history"]:
            if message["message_id"] == message_id:
                message["status"] = status
                collaboration_context["updated_at"] = datetime.now().isoformat()
                
                # Update active contexts
                self.active_contexts[context_id] = collaboration_context
                self._save_context(collaboration_context)
                
                logger.info(f"Message {message_id} status updated to {status}")
                return True
        
        return False
    
    def close_collaboration_context(
        self,
        context_id: str,
        reason: str = "completed"
    ) -> bool:
        """
        Close a collaboration context.
        
        Args:
            context_id: Collaboration context ID
            reason: Reason for closing
            
        Returns:
            True if context was closed, False otherwise
        """
        if context_id not in self.active_contexts:
            return False
        
        collaboration_context = self.active_contexts[context_id]
        collaboration_context["context_state"] = "completed"
        collaboration_context["updated_at"] = datetime.now().isoformat()
        collaboration_context["metadata"]["close_reason"] = reason
        
        # Save final state
        self._save_context(collaboration_context)
        
        # Remove from active contexts
        del self.active_contexts[context_id]
        
        logger.info(f"Collaboration context {context_id} closed: {reason}")
        return True
    
    def get_collaboration_summary(self, context_id: str) -> Dict[str, Any]:
        """
        Get a summary of collaboration activity.
        
        Args:
            context_id: Collaboration context ID
            
        Returns:
            Collaboration summary
        """
        if context_id not in self.active_contexts:
            raise ValueError(f"Collaboration context {context_id} not found")
        
        collaboration_context = self.active_contexts[context_id]
        
        # Analyze communication history
        message_counts = {}
        for message in collaboration_context["communication_history"]:
            message_type = message["message_type"]
            message_counts[message_type] = message_counts.get(message_type, 0) + 1
        
        # Get agent activity
        agent_activity = {}
        for agent in collaboration_context["participating_agents"]:
            sent_count = len([
                msg for msg in collaboration_context["communication_history"]
                if msg["from_agent"] == agent
            ])
            received_count = len([
                msg for msg in collaboration_context["communication_history"]
                if msg["to_agent"] == agent or msg["to_agent"] == "all"
            ])
            agent_activity[agent] = {
                "messages_sent": sent_count,
                "messages_received": received_count,
                "total_activity": sent_count + received_count
            }
        
        return {
            "context_id": context_id,
            "session_id": collaboration_context["session_id"],
            "participating_agents": collaboration_context["participating_agents"],
            "context_state": collaboration_context["context_state"],
            "created_at": collaboration_context["created_at"],
            "updated_at": collaboration_context["updated_at"],
            "total_messages": len(collaboration_context["communication_history"]),
            "message_counts": message_counts,
            "agent_activity": agent_activity,
            "shared_knowledge_keys": list(collaboration_context["shared_knowledge"].keys()),
            "collaboration_duration": self._calculate_duration(
                collaboration_context["created_at"],
                collaboration_context["updated_at"]
            )
        }
    
    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calculate duration between two timestamps."""
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            duration = end - start
            return str(duration)
        except Exception:
            return "unknown"
    
    def _save_context(self, context: CollaborationContext) -> None:
        """Save collaboration context to storage."""
        try:
            context_file = self.storage_dir / f"context_{context['context_id']}.json"
            with open(context_file, 'w') as f:
                json.dump(context, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save collaboration context: {e}")
    
    def _load_context(self, context_id: str) -> Optional[CollaborationContext]:
        """Load collaboration context from storage."""
        try:
            context_file = self.storage_dir / f"context_{context_id}.json"
            if context_file.exists():
                with open(context_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load collaboration context {context_id}: {e}")
        return None


# Convenience functions for easy integration
def create_collaboration_context(
    session_id: str,
    participating_agents: List[str],
    initial_knowledge: Dict[str, Any] = None
) -> CollaborationContext:
    """Create a new collaboration context."""
    manager = CollaborationContextManager()
    return manager.create_collaboration_context(session_id, participating_agents, initial_knowledge)


def send_collaboration_message(
    context_id: str,
    from_agent: str,
    to_agent: str,
    message_type: str,
    content: Dict[str, Any]
) -> CollaborationMessage:
    """Send a collaboration message."""
    manager = CollaborationContextManager()
    return manager.send_message(context_id, from_agent, to_agent, message_type, content)


def update_collaboration_knowledge(
    context_id: str,
    agent_name: str,
    knowledge_updates: Dict[str, Any]
) -> Dict[str, Any]:
    """Update shared knowledge in collaboration context."""
    manager = CollaborationContextManager()
    return manager.update_shared_knowledge(context_id, agent_name, knowledge_updates)
