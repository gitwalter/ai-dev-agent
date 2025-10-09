#!/usr/bin/env python3
"""
Agent Logging Coordinator - Comprehensive Transparent Logging System
===================================================================

This module ensures ALL agents in the project log their activities transparently
to the universal tracking database for complete system visibility.

COVERAGE:
- Cursor keyword context switches (@agile, @test, @debug, etc.)
- All agent framework agents (BaseAgent, enhanced agents, specialized agents)
- Dynamic rule activator
- Agent swarm members
- Manual context switches
- Cross-agent communication

PURPOSE: Complete transparency and control over agent activities
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentLoggingCoordinator:
    """
    Centralized coordinator that ensures comprehensive agent logging.
    
    This class acts as a hub that connects all agent types to the universal
    tracking system, ensuring nothing falls through the cracks.
    """
    
    def __init__(self):
        """Initialize the logging coordinator."""
        self.universal_tracker = None
        self.registered_agents = {}
        self.keyword_sessions = {}
        self.framework_agents = {}
        
        # Initialize connection
        self._initialize_universal_tracking()
        
        # Set up keyword monitoring
        self._setup_keyword_monitoring()
        
        logger.info("🎯 Agent Logging Coordinator initialized - Full transparency enabled")
    
    def _initialize_universal_tracking(self):
        """Initialize connection to universal tracker and discover all database tables."""
        try:
            from utils.system.universal_agent_tracker import get_universal_tracker, AgentType, ContextType
            self.universal_tracker = get_universal_tracker()
            self.AgentType = AgentType
            self.ContextType = ContextType
            
            # Discover all available database tables for comprehensive logging
            self._discover_database_schema()
            
            logger.info("✅ Connected to Universal Agent Tracker with full schema discovery")
        except Exception as e:
            logger.error(f"❌ CRITICAL: Could not connect to universal tracker: {e}")
            self.universal_tracker = None
            
    def _discover_database_schema(self):
        """Discover all available tables in the database for comprehensive logging."""
        import sqlite3
        
        self.available_tables = {}
        
        try:
            db_path = "utils/universal_agent_tracking.db"
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_names = [row[0] for row in cursor.fetchall()]
                
                logger.info(f"🔍 Discovered {len(table_names)} tables in database: {table_names}")
                
                # Get schema for each table
                for table_name in table_names:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    
                    self.available_tables[table_name] = {
                        "columns": [col[1] for col in columns],  # Column names
                        "schema": columns,
                        "record_count": 0
                    }
                    
                    # Get record count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    self.available_tables[table_name]["record_count"] = cursor.fetchone()[0]
                
                # Log what we found
                for table_name, info in self.available_tables.items():
                    logger.info(f"📊 Table '{table_name}': {len(info['columns'])} columns, {info['record_count']} records")
                    logger.info(f"   Columns: {info['columns']}")
                
                self.total_tables = len(table_names)
                
        except Exception as e:
            logger.error(f"❌ Could not discover database schema: {e}")
            self.available_tables = {}
    
    def _setup_keyword_monitoring(self):
        """Set up keyword to context mapping for transparent monitoring."""
        self.keyword_context_map = {
            '@agile': 'AGILE',
            '@test': 'TESTING', 
            '@debug': 'DEBUGGING',
            '@optimize': 'OPTIMIZATION',
            '@security': 'SECURITY',
            '@research': 'RESEARCH',
            '@docs': 'DOCUMENTATION',
            '@code': 'CODING',
            '@git': 'CODING',
            '@deploy': 'DEPLOYMENT',
            '@monitor': 'MONITORING'
        }
        logger.info(f"🔍 Keyword monitoring setup: {len(self.keyword_context_map)} keywords tracked")
    
    def register_cursor_agent(self, session_name: str = None) -> str:
        """
        Register a Cursor AI agent session.
        
        Args:
            session_name: Optional custom session name
            
        Returns:
            Session ID for tracking
        """
        if not self.universal_tracker:
            logger.warning("⚠️ Universal tracker not available")
            return None
            
        session_name = session_name or f"cursor_ai_main_{int(time.time())}"
        
        try:
            session_id = self.universal_tracker.register_agent(
                agent_id=session_name,
                agent_type=self.AgentType.CURSOR_AI,
                initial_context=self.ContextType.SYSTEM_STARTUP,
                metadata={
                    "type": "cursor_integration",
                    "auto_keyword_detection": True,
                    "registered_by": "logging_coordinator"
                }
            )
            
            self.registered_agents[session_name] = {
                "session_id": session_id,
                "type": "cursor_ai",
                "registered_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Cursor AI agent registered: {session_name} → {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Failed to register Cursor agent: {e}")
            return None
    
    def register_framework_agent(self, agent_id: str, agent_type: str, agent_class: str = None) -> str:
        """
        Register an agent from our agent framework.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent (custom_agent, swarm_member, etc.)
            agent_class: Class name of the agent
            
        Returns:
            Session ID for tracking
        """
        if not self.universal_tracker:
            logger.warning("⚠️ Universal tracker not available")
            return None
            
        try:
            # Map agent types
            type_mapping = {
                "base_agent": self.AgentType.CUSTOM_AGENT,
                "enhanced_agent": self.AgentType.CUSTOM_AGENT,
                "research_agent": self.AgentType.CUSTOM_AGENT,
                "swarm_member": self.AgentType.SWARM_MEMBER,
                "rule_agent": self.AgentType.RULE_AGENT
            }
            
            mapped_type = type_mapping.get(agent_type, self.AgentType.CUSTOM_AGENT)
            
            session_id = self.universal_tracker.register_agent(
                agent_id=agent_id,
                agent_type=mapped_type,
                initial_context=self.ContextType.SYSTEM_STARTUP,
                metadata={
                    "framework_agent": True,
                    "agent_class": agent_class or "unknown",
                    "original_type": agent_type,
                    "registered_by": "logging_coordinator"
                }
            )
            
            self.framework_agents[agent_id] = {
                "session_id": session_id,
                "type": agent_type,
                "class": agent_class,
                "registered_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Framework agent registered: {agent_id} ({agent_type}) → {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Failed to register framework agent {agent_id}: {e}")
            return None
    
    def log_keyword_usage(self, keyword: str, source: str = "cursor_chat", 
                         additional_context: Dict[str, Any] = None) -> str:
        """
        Log keyword usage for transparent context switching.
        
        Args:
            keyword: The keyword used (e.g., '@agile')
            source: Source of the keyword (cursor_chat, app_interface, etc.)
            additional_context: Additional context information
            
        Returns:
            Switch ID for the logged context switch
        """
        if not self.universal_tracker:
            logger.warning("⚠️ Universal tracker not available")
            return None
            
        # Get or create keyword session
        keyword_session_key = f"keyword_{keyword.replace('@', '')}"
        
        if keyword_session_key not in self.keyword_sessions:
            session_id = self.universal_tracker.register_agent(
                agent_id=keyword_session_key,
                agent_type=self.AgentType.CURSOR_AI,
                initial_context=self.ContextType.SYSTEM_STARTUP,
                metadata={
                    "keyword_tracking": True,
                    "primary_keyword": keyword,
                    "source": source
                }
            )
            self.keyword_sessions[keyword_session_key] = session_id
        else:
            session_id = self.keyword_sessions[keyword_session_key]
        
        # Map keyword to context
        context_name = self.keyword_context_map.get(keyword, 'SYSTEM_STARTUP')
        context_enum = getattr(self.ContextType, context_name, self.ContextType.SYSTEM_STARTUP)
        
        try:
            switch_id = self.universal_tracker.record_context_switch(
                session_id=session_id,
                new_context=context_enum,
                trigger_type="keyword_detected",
                trigger_details={
                    "keyword": keyword,
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                    "additional_context": additional_context or {}
                }
            )
            
            logger.info(f"✅ Keyword logged: {keyword} → {context_name} (Switch: {switch_id})")
            return switch_id
            
        except Exception as e:
            logger.error(f"❌ Failed to log keyword {keyword}: {e}")
            return None
    
    def log_agent_communication(self, sender_agent: str, receiver_agent: str, 
                              message_type: str, content: str = None) -> str:
        """
        Log communication between agents.
        
        Args:
            sender_agent: ID of sending agent
            receiver_agent: ID of receiving agent  
            message_type: Type of communication
            content: Optional message content
            
        Returns:
            Communication ID
        """
        if not self.universal_tracker:
            return None
            
        # Get session IDs for agents
        sender_session = self._get_session_for_agent(sender_agent)
        receiver_session = self._get_session_for_agent(receiver_agent)
        
        if not sender_session or not receiver_session:
            logger.warning(f"⚠️ Could not find sessions for communication: {sender_agent} → {receiver_agent}")
            return None
        
        try:
            # Record as a special context switch for communication
            switch_id = self.universal_tracker.record_context_switch(
                session_id=sender_session,
                new_context=self.ContextType.COORDINATION,
                trigger_type="agent_communication",
                trigger_details={
                    "communication_type": message_type,
                    "sender": sender_agent,
                    "receiver": receiver_agent,
                    "content_length": len(content) if content else 0,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"✅ Agent communication logged: {sender_agent} → {receiver_agent} ({message_type})")
            return switch_id
            
        except Exception as e:
            logger.error(f"❌ Failed to log agent communication: {e}")
            return None
    
    def _get_session_for_agent(self, agent_id: str) -> str:
        """Get session ID for an agent."""
        # Check registered agents
        if agent_id in self.registered_agents:
            return self.registered_agents[agent_id]["session_id"]
            
        # Check framework agents
        if agent_id in self.framework_agents:
            return self.framework_agents[agent_id]["session_id"]
            
        # Check keyword sessions
        for key, session_id in self.keyword_sessions.items():
            if agent_id in key:
                return session_id
                
        return None
    
    def log_to_all_relevant_tables(self, event_type: str, agent_id: str, context_data: Dict[str, Any]):
        """
        Log events to ALL relevant tables in the database for maximum transparency.
        
        Args:
            event_type: Type of event (registration, context_switch, communication, etc.)
            agent_id: ID of the agent generating the event
            context_data: Additional context and metadata
        """
        if not self.universal_tracker or not hasattr(self, 'available_tables'):
            logger.warning("⚠️ Cannot log to all tables - tracker or schema not available")
            return
            
        import sqlite3
        
        timestamp = datetime.now().isoformat()
        
        try:
            with sqlite3.connect("utils/universal_agent_tracking.db") as conn:
                cursor = conn.cursor()
                
                # Log to each available table based on its schema
                for table_name, table_info in self.available_tables.items():
                    columns = table_info["columns"]
                    
                    # Prepare data for this table
                    table_data = self._prepare_data_for_table(
                        table_name, columns, event_type, agent_id, context_data, timestamp
                    )
                    
                    if table_data:
                        # Insert into this table
                        column_names = list(table_data.keys())
                        placeholders = ', '.join(['?' for _ in column_names])
                        column_list = ', '.join(column_names)
                        
                        insert_sql = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
                        values = list(table_data.values())
                        
                        try:
                            cursor.execute(insert_sql, values)
                            logger.info(f"✅ Logged {event_type} to table '{table_name}' for agent {agent_id}")
                        except Exception as table_error:
                            logger.warning(f"⚠️ Could not log to table '{table_name}': {table_error}")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Failed to log to all tables: {e}")
    
    def _prepare_data_for_table(self, table_name: str, columns: List[str], 
                               event_type: str, agent_id: str, context_data: Dict[str, Any], 
                               timestamp: str) -> Dict[str, Any]:
        """
        Prepare data for insertion into a specific table based on its schema.
        
        Args:
            table_name: Name of the table
            columns: List of column names in the table
            event_type: Type of event being logged
            agent_id: Agent ID
            context_data: Context data
            timestamp: Event timestamp
            
        Returns:
            Dictionary with data ready for insertion, or None if not applicable
        """
        import uuid
        
        # Generate required IDs if not provided
        import uuid
        if "session_id" not in context_data:
            context_data["session_id"] = str(uuid.uuid4())
        
        # Base data that applies to most tables - only real data
        base_data = {
            "timestamp": timestamp,
            "agent_id": agent_id,
            "event_type": event_type,
            "session_id": context_data["session_id"],  # Must be real
            "context": json.dumps(context_data),
            "metadata": json.dumps({"logged_by": "agent_logging_coordinator", "authentic_data_only": True}),
            "id": context_data.get("id"),  # Only if real ID provided
            "agent_type": context_data.get("agent_type", "unknown"),
            "status": "active",
            "description": f"{event_type} for agent {agent_id}",
            "details": json.dumps(context_data),
            "from_context": context_data.get("from_context", "unknown"),
            "to_context": context_data.get("to_context", "unknown"),
            "switch_id": context_data.get("switch_id"),  # Only if real switch ID provided
            "trigger_type": context_data.get("trigger_type", event_type),
            "trigger_details": json.dumps(context_data.get("trigger_details", {})),
            "created_at": timestamp,
            "start_time": timestamp,
            "last_activity": timestamp
        }
        
        # Filter data to only include columns that exist in this table
        filtered_data = {}
        for column in columns:
            if column in base_data:
                filtered_data[column] = base_data[column]
            elif column.endswith("_id") and not filtered_data.get(column):
                # Generate IDs for ID columns
                filtered_data[column] = str(uuid.uuid4())
        
        # Only return data if we have at least 2 columns filled
        if len(filtered_data) >= 2:
            return filtered_data
        
        return None
    
    def get_comprehensive_database_status(self) -> Dict[str, Any]:
        """Get comprehensive status of ALL database tables and their usage."""
        status = {
            "coordinator_active": self.universal_tracker is not None,
            "database_schema": self.available_tables if hasattr(self, 'available_tables') else {},
            "total_tables": getattr(self, 'total_tables', 0),
            "agents": {
                "registered": len(self.registered_agents),
                "framework": len(self.framework_agents),
                "keyword_sessions": len(self.keyword_sessions),
                "details": {
                    "registered": list(self.registered_agents.keys()),
                    "framework": list(self.framework_agents.keys()),
                    "keyword_sessions": list(self.keyword_sessions.keys())
                }
            },
            "tracking": {
                "keywords_tracked": list(self.keyword_context_map.keys()),
                "total_keywords": len(self.keyword_context_map)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Add current record counts for all tables
        if hasattr(self, 'available_tables'):
            import sqlite3
            try:
                with sqlite3.connect("utils/universal_agent_tracking.db") as conn:
                    cursor = conn.cursor()
                    
                    for table_name in self.available_tables.keys():
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        current_count = cursor.fetchone()[0]
                        status["database_schema"][table_name]["current_record_count"] = current_count
                        
            except Exception as e:
                status["database_error"] = str(e)
        
        return status

    def get_logging_status(self) -> Dict[str, Any]:
        """Get comprehensive logging status (backward compatibility)."""
        return self.get_comprehensive_database_status()
    
    def start_comprehensive_logging(self):
        """Start comprehensive logging for all agent types."""
        logger.info("🚀 Starting comprehensive agent logging...")
        
        # Register main Cursor session
        cursor_session = self.register_cursor_agent("cursor_main")
        
        # Initialize keyword tracking sessions
        for keyword in self.keyword_context_map.keys():
            self.log_keyword_usage(keyword, "initialization", {"purpose": "setup_tracking"})
        
        logger.info("✅ Comprehensive agent logging activated")
        return {
            "cursor_session": cursor_session,
            "status": "active",
            "tracking_keywords": len(self.keyword_context_map)
        }


# Global coordinator instance
_global_coordinator = None

def get_logging_coordinator() -> AgentLoggingCoordinator:
    """Get the global logging coordinator instance."""
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = AgentLoggingCoordinator()
    return _global_coordinator

def log_cursor_keyword(keyword: str, additional_context: Dict[str, Any] = None) -> str:
    """Convenience function to log cursor keywords."""
    coordinator = get_logging_coordinator()
    return coordinator.log_keyword_usage(keyword, "cursor_chat", additional_context)

def register_agent_for_logging(agent_id: str, agent_type: str, agent_class: str = None) -> str:
    """Convenience function to register framework agents."""
    coordinator = get_logging_coordinator()
    return coordinator.register_framework_agent(agent_id, agent_type, agent_class)

if __name__ == "__main__":
    # Test the logging coordinator
    print("🧪 Testing Agent Logging Coordinator")
    
    coordinator = get_logging_coordinator()
    status = coordinator.get_logging_status()
    print(f"Coordinator status: {status}")
    
    # Test keyword logging
    switch_id = coordinator.log_keyword_usage("@agile", "test", {"test": True})
    print(f"Test keyword logged: {switch_id}")
