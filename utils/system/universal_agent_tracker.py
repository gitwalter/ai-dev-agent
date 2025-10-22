"""
Universal Agent Tracker - Minimal Working Version
"""
import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum


class AgentType(Enum):
    """Agent types."""
    CURSOR_AI = "cursor_ai"
    USER_INTERFACE = "user_interface"
    PROJECT_AGENT = "project_agent"
    CUSTOM_AGENT = "custom_agent"
    SWARM_MEMBER = "swarm_member"
    RULE_AGENT = "rule_agent"
    BASE_AGENT = "base_agent"
    ENHANCED_AGENT = "enhanced_agent"
    RESEARCH_AGENT = "research_agent"


class ContextType(Enum):
    """Context types."""
    SYSTEM_STARTUP = "system_startup"
    AGILE = "agile"
    TESTING = "testing"
    DEBUGGING = "debugging"
    MONITORING = "monitoring"
    COORDINATION = "coordination"
    CODING = "coding"
    RESEARCH = "research"
    DOCUMENTATION = "documentation"
    OPTIMIZATION = "optimization"


class EventType(Enum):
    """Event types."""
    CONTEXT_SWITCH = "context_switch"
    SESSION_START = "session_start"


class UniversalAgentTracker:
    """Minimal working tracker."""
    
    def __init__(self, db_path: str = "utils/universal_agent_tracking.db"):
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize database - backward compatible."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check existing schema first
            cursor.execute("PRAGMA table_info(agent_sessions)")
            existing_cols = [row[1] for row in cursor.fetchall()]
            
            if not existing_cols:
                # Create new table only if it doesn't exist
                cursor.execute("""
                    CREATE TABLE agent_sessions (
                        session_id TEXT PRIMARY KEY,
                        agent_id TEXT,
                        agent_type TEXT,
                        timestamp TEXT,
                        context TEXT
                    )
                """)
            
            # Store column info for use in other methods
            cursor.execute("PRAGMA table_info(agent_sessions)")
            self.session_columns = [row[1] for row in cursor.fetchall()]
            
            # Context switches table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_switches (
                    switch_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    from_context TEXT,
                    to_context TEXT,
                    timestamp TEXT
                )
            """)
            conn.commit()
    
    def register_agent(self, agent_id: str, agent_type, initial_context=None, **kwargs) -> str:
        """Register an agent - adapts to existing schema."""
        session_id = f"{agent_id}_{int(time.time())}"
        
        # Convert enums to strings
        agent_type_str = agent_type.value if hasattr(agent_type, 'value') else str(agent_type)
        context_str = initial_context.value if hasattr(initial_context, 'value') else str(initial_context or "system_startup")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build insert query based on existing columns
            available_cols = ['session_id']
            values = [session_id]
            
            if 'agent_id' in self.session_columns:
                available_cols.append('agent_id')
                values.append(agent_id)
            
            if 'agent_type' in self.session_columns:
                available_cols.append('agent_type')
                values.append(agent_type_str)
                
            if 'timestamp' in self.session_columns:
                available_cols.append('timestamp')
                values.append(datetime.now().isoformat())
            elif 'start_time' in self.session_columns:
                available_cols.append('start_time')
                values.append(datetime.now().isoformat())
                
            if 'context' in self.session_columns:
                available_cols.append('context')
                values.append(context_str)
            
            # Build dynamic query
            placeholders = ', '.join(['?' for _ in values])
            cols_str = ', '.join(available_cols)
            
            cursor.execute(f"""
                INSERT OR REPLACE INTO agent_sessions ({cols_str})
                VALUES ({placeholders})
            """, values)
            conn.commit()
        
        return session_id
    
    def record_context_switch(self, session_id: str, new_context, **kwargs) -> str:
        """Record context switch."""
        import uuid
        switch_id = f"switch_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        to_context = new_context.value if hasattr(new_context, 'value') else str(new_context)
        
        # Extract additional parameters
        from_context = kwargs.get('from_context', 'unknown')
        if hasattr(from_context, 'value'):
            from_context = from_context.value
        
        trigger_type = kwargs.get('trigger_type', 'manual')
        trigger_details = kwargs.get('trigger_details', {})
        
        # Convert trigger_details to JSON string if it's a dict
        if isinstance(trigger_details, dict):
            import json
            trigger_details = json.dumps(trigger_details)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO context_switches 
                (switch_id, session_id, from_context, to_context, timestamp, trigger_type, trigger_details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (switch_id, session_id, str(from_context), to_context, datetime.now().isoformat(), trigger_type, trigger_details))
            conn.commit()
        
        return switch_id
    
    def get_recent_context_switches(self, **kwargs) -> List[Dict]:
        """Get recent context switches."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM context_switches ORDER BY timestamp DESC LIMIT 50")
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        return {
            "active_sessions": 1,
            "total_sessions": 1,
            "recent_context_switches": 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_agent_timeline(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get agent timeline for the specified time period."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            timeline = []
            
            # PRIMARY: Get agent_events (main event table with rich data)
            try:
                cursor.execute("SELECT * FROM agent_events ORDER BY timestamp DESC LIMIT 50")
                events = cursor.fetchall()
                event_columns = [desc[0] for desc in cursor.description]
                
                for event in events:
                    event_dict = dict(zip(event_columns, event))
                    # Parse JSON fields safely
                    try:
                        details = json.loads(event_dict.get("details", "{}")) if event_dict.get("details") else {}
                        rules_affected = json.loads(event_dict.get("rules_affected", "[]")) if event_dict.get("rules_affected") else []
                        performance_metrics = json.loads(event_dict.get("performance_metrics", "{}")) if event_dict.get("performance_metrics") else {}
                        related_agents = json.loads(event_dict.get("related_agents", "[]")) if event_dict.get("related_agents") else []
                    except (json.JSONDecodeError, TypeError):
                        details = {}
                        rules_affected = []
                        performance_metrics = {}
                        related_agents = []
                    
                    timeline.append({
                        "timestamp": event_dict.get("timestamp", ""),
                        "event_type": event_dict.get("event_type", "unknown"),
                        "agent_id": event_dict.get("agent_id", "unknown"),
                        "agent_type": event_dict.get("agent_type", "unknown"),
                        "context": event_dict.get("context", "unknown"),
                        "session_id": event_dict.get("session_id", ""),
                        "details": details,
                        "rules_affected": rules_affected,
                        "performance_metrics": performance_metrics,
                        "related_agents": related_agents,
                        "event_id": event_dict.get("event_id", "")
                    })
            except sqlite3.OperationalError:
                # agent_events table might not exist yet
                pass
            
            # SECONDARY: Add context switch events  
            try:
                cursor.execute("SELECT * FROM context_switches ORDER BY timestamp DESC LIMIT 20")
                switches = cursor.fetchall()
                switch_columns = [desc[0] for desc in cursor.description]
                
                for switch in switches:
                    switch_dict = dict(zip(switch_columns, switch))
                    try:
                        trigger_details = json.loads(switch_dict.get("trigger_details", "{}")) if switch_dict.get("trigger_details") else {}
                    except (json.JSONDecodeError, TypeError):
                        trigger_details = {}
                    
                    timeline.append({
                        "timestamp": switch_dict.get("timestamp", ""),
                        "event_type": "context_switch",
                        "agent_id": "context_system",
                        "agent_type": "system",
                        "context": switch_dict.get("to_context", "unknown"),
                        "session_id": switch_dict.get("session_id", ""),
                        "details": {
                            "from_context": switch_dict.get("from_context", ""),
                            "to_context": switch_dict.get("to_context", ""),
                            "trigger_type": switch_dict.get("trigger_type", ""),
                            **trigger_details
                        },
                        "rules_affected": [],
                        "performance_metrics": {},
                        "related_agents": [],
                        "switch_id": switch_dict.get("switch_id", "")
                    })
            except sqlite3.OperationalError:
                pass
            
            # TERTIARY: Add rule activations
            try:
                cursor.execute("SELECT * FROM rule_activations ORDER BY timestamp DESC LIMIT 20")
                activations = cursor.fetchall()
                activation_columns = [desc[0] for desc in cursor.description]
                
                for activation in activations:
                    activation_dict = dict(zip(activation_columns, activation))
                    try:
                        rules_activated = json.loads(activation_dict.get("rules_activated", "[]")) if activation_dict.get("rules_activated") else []
                        trigger_details = json.loads(activation_dict.get("trigger_details", "{}")) if activation_dict.get("trigger_details") else {}
                        performance_impact = json.loads(activation_dict.get("performance_impact", "{}")) if activation_dict.get("performance_impact") else {}
                    except (json.JSONDecodeError, TypeError):
                        rules_activated = []
                        trigger_details = {}
                        performance_impact = {}
                    
                    timeline.append({
                        "timestamp": activation_dict.get("timestamp", ""),
                        "event_type": "rule_activation",
                        "agent_id": "rule_system",
                        "agent_type": "system",
                        "context": trigger_details.get("context", "unknown"),
                        "session_id": activation_dict.get("session_id", ""),
                        "details": {
                            "trigger_event": activation_dict.get("trigger_event", ""),
                            **trigger_details
                        },
                        "rules_affected": rules_activated,
                        "performance_metrics": performance_impact,
                        "related_agents": [],
                        "activation_id": activation_dict.get("activation_id", "")
                    })
            except sqlite3.OperationalError:
                pass
            
            # Sort by timestamp (newest first)
            timeline.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return timeline[:50]  # Return last 50 events
    
    def record_rule_activation(self, session_id: str, rule_name: str, **kwargs) -> str:
        """Record a rule activation event."""
        # For now, just record as a context switch with special type
        import uuid
        activation_id = f"rule_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Extract additional parameters
        activation_reason = kwargs.get('activation_reason', 'Rule activated')
        performance_impact = kwargs.get('performance_impact', 1.0)
        
        # Create trigger details
        trigger_details = {
            'activation_reason': activation_reason,
            'performance_impact': performance_impact,
            'rule_type': 'dynamic_rule'
        }
        
        import json
        trigger_details_json = json.dumps(trigger_details)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO context_switches 
                (switch_id, session_id, from_context, to_context, timestamp, trigger_type, trigger_details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (activation_id, session_id, "rule_activation", rule_name, datetime.now().isoformat(), "rule_activation", trigger_details_json))
            conn.commit()
        
        return activation_id
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get swarm status information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count different agent types
            cursor.execute("SELECT agent_type, COUNT(*) FROM agent_sessions GROUP BY agent_type")
            agent_counts = dict(cursor.fetchall())
            
            # Count recent activity
            cursor.execute("SELECT COUNT(*) FROM context_switches")
            total_switches = cursor.fetchone()[0]
            
            return {
                "total_agents": sum(agent_counts.values()),
                "agent_types": agent_counts,
                "total_context_switches": total_switches,
                "swarm_health": "active" if total_switches > 0 else "idle",
                "timestamp": datetime.now().isoformat()
            }


# Global tracker instance
_tracker = None

def get_universal_tracker() -> UniversalAgentTracker:
    """Get global tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = UniversalAgentTracker()
    return _tracker
