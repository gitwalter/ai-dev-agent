#!/usr/bin/env python3
"""
Multi-Database Logger - Simple and Direct
========================================

Logs agent activities to ALL 8 database files for complete transparency.
No complex discovery - just direct, reliable logging.
"""

import sqlite3
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class MultiDatabaseLogger:
    """Simple, reliable logger that writes to all databases."""
    
    def __init__(self):
        self.databases = {
            "universal_agent_tracking": "utils/universal_agent_tracking.db",
            "strategic_selection": "utils/strategic_selection.db", 
            "security_events": "utils/security_events.db",
            "rule_optimization": "utils/rule_optimization.db",
            "optimization": "utils/optimization.db",
            "learning_experiences": "utils/learning_experiences.db",
            "backup_tracking": "utils/backup_tracking.db",
            "analytics": "utils/analytics.db"
        }
        
        # Ensure all databases exist
        self._ensure_databases_exist()
    
    def _ensure_databases_exist(self):
        """Ensure all database files exist with basic tables."""
        for db_name, db_path in self.databases.items():
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Create a universal logging table in each database
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS agent_activities (
                            id TEXT PRIMARY KEY,
                            timestamp TEXT,
                            agent_id TEXT,
                            activity_type TEXT,
                            context TEXT,
                            details TEXT,
                            session_id TEXT
                        )
                    """)
                    conn.commit()
                    
            except Exception as e:
                print(f"Warning: Could not setup {db_name}: {e}")
    
    def log_activity(self, agent_id: str, activity_type: str, context: str = None, details: Dict[str, Any] = None):
        """
        Log activity to ALL databases for maximum transparency.
        Logs all activity with proper session tracking
        
        Args:
            agent_id: ID of the agent
            activity_type: Type of activity (keyword, context_switch, registration, etc.)
            context: Context information
            details: Additional details (must include real session_id and activity_id)
        """
        timestamp = datetime.now().isoformat()
        
        # Generate required IDs if not provided
        import uuid
        if not details:
            details = {}
        if 'session_id' not in details:
            details['session_id'] = str(uuid.uuid4())
        if 'activity_id' not in details:
            details['activity_id'] = str(uuid.uuid4())
            
        activity_id = details['activity_id']
        session_id = details['session_id']
        
        # Prepare data
        data = {
            "id": activity_id,
            "timestamp": timestamp,
            "agent_id": agent_id,
            "activity_type": activity_type,
            "context": context or "unknown",
            "details": json.dumps(details or {}),
            "session_id": session_id
        }
        
        # Log to ALL databases
        for db_name, db_path in self.databases.items():
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO agent_activities 
                        (id, timestamp, agent_id, activity_type, context, details, session_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data["id"],
                        data["timestamp"], 
                        data["agent_id"],
                        data["activity_type"],
                        data["context"],
                        data["details"],
                        data["session_id"]
                    ))
                    
                    conn.commit()
                    print(f"✅ Logged to {db_name}: {agent_id} - {activity_type}")
                    
            except Exception as e:
                print(f"⚠️ Failed to log to {db_name}: {e}")
    
    def log_cursor_keyword(self, keyword: str):
        """Log Cursor keyword usage."""
        self.log_activity(
            agent_id="cursor_ai",
            activity_type="keyword_usage",
            context=keyword,
            details={"source": "cursor_chat", "keyword": keyword}
        )
    
    def log_agent_registration(self, agent_id: str, agent_type: str):
        """Log agent registration."""
        self.log_activity(
            agent_id=agent_id,
            activity_type="agent_registration", 
            context=agent_type,
            details={"agent_type": agent_type, "status": "registered"}
        )
    
    def log_context_switch(self, agent_id: str, from_context: str, to_context: str):
        """Log context switch."""
        self.log_activity(
            agent_id=agent_id,
            activity_type="context_switch",
            context=f"{from_context} -> {to_context}",
            details={"from": from_context, "to": to_context}
        )
    
    def get_all_activities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent activities from the main database."""
        activities = []
        
        try:
            with sqlite3.connect(self.databases["universal_agent_tracking"]) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM agent_activities 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                for row in rows:
                    activity = {}
                    for i, col in enumerate(columns):
                        activity[col] = row[i]
                    activities.append(activity)
                    
        except Exception as e:
            print(f"Error getting activities: {e}")
        
        return activities
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get status of all databases."""
        status = {
            "total_databases": len(self.databases),
            "databases": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for db_name, db_path in self.databases.items():
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM agent_activities")
                    count = cursor.fetchone()[0]
                    
                    status["databases"][db_name] = {
                        "path": db_path,
                        "record_count": count,
                        "status": "accessible"
                    }
                    
            except Exception as e:
                status["databases"][db_name] = {
                    "path": db_path,
                    "error": str(e),
                    "status": "error"
                }
        
        return status

# Global instance
_global_logger = None

def get_multi_database_logger() -> MultiDatabaseLogger:
    """Get the global multi-database logger."""
    global _global_logger
    if _global_logger is None:
        _global_logger = MultiDatabaseLogger()
    return _global_logger

# Convenience functions
def log_cursor_keyword(keyword: str):
    """Quick function to log cursor keywords."""
    logger = get_multi_database_logger()
    logger.log_cursor_keyword(keyword)

def log_agent_activity(agent_id: str, activity_type: str, context: str = None, details: Dict[str, Any] = None):
    """Quick function to log agent activities."""
    logger = get_multi_database_logger()
    logger.log_activity(agent_id, activity_type, context, details)

if __name__ == "__main__":
    # Simple test
    print("🧪 Testing Multi-Database Logger")
    
    logger = get_multi_database_logger()
    
    # Test logging
    logger.log_cursor_keyword("@agile")
    logger.log_agent_registration("test_agent", "base_agent")
    logger.log_context_switch("test_agent", "startup", "agile")
    
    # Check status
    status = logger.get_database_status()
    print(f"Database status: {status}")
    
    print("✅ Multi-database logging test complete!")
