#!/usr/bin/env python3
"""
Database MCP Tools
==================

MCP tools for accessing project databases for agent state tracking, analytics,
and system monitoring. Exposes all 12 project databases through MCP interface.

Created: 2025-10-10
Sprint: US-RAG-001 Phase 5 Enhancement
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# MCP Tool Integration
try:
    from utils.mcp.mcp_tool import mcp_tool, AccessLevel, ToolCategory
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    
logger = logging.getLogger(__name__)


# ============================================================================
# Database Registry
# ============================================================================

DATABASE_REGISTRY = {
    "agent_tracking": {
        "path": "utils/universal_agent_tracking.db",
        "description": "Agent sessions, events, and context switches",
        "tables": ["agent_sessions", "agent_events", "context_switches", "agent_activities"],
        "primary_use": "Agent state tracking and lifecycle management"
    },
    "rag_system": {
        "path": "data/rag_system.db",
        "description": "RAG document indexing and query logs",
        "tables": ["indexed_documents", "document_chunks", "query_logs", "rag_config"],
        "primary_use": "RAG system analytics and document tracking"
    },
    "optimization": {
        "path": "utils/optimization.db",
        "description": "General system optimization tracking",
        "tables": ["agent_activities"],
        "primary_use": "Performance optimization and monitoring"
    },
    "prompt_optimization": {
        "path": "prompts/optimization/optimization.db",
        "description": "Prompt optimization and performance",
        "tables": ["prompt_metrics", "optimization_results"],
        "primary_use": "Prompt engineering and optimization"
    },
    "prompt_templates": {
        "path": "prompts/prompt_templates.db",
        "description": "Prompt template storage and versioning",
        "tables": ["templates", "versions"],
        "primary_use": "Prompt template management"
    },
    "analytics": {
        "path": "utils/analytics.db",
        "description": "General system analytics",
        "tables": ["agent_activities"],
        "primary_use": "System-wide analytics and metrics"
    },
    "security_events": {
        "path": "utils/security_events.db",
        "description": "Security event logging",
        "tables": ["agent_activities", "security_events"],
        "primary_use": "Security monitoring and audit trails"
    },
    "learning_experiences": {
        "path": "utils/learning_experiences.db",
        "description": "Learning and pattern detection",
        "tables": ["agent_activities", "patterns"],
        "primary_use": "Machine learning and pattern recognition"
    },
    "test_results": {
        "path": "utils/test_pipeline_results.db",
        "description": "Test execution results",
        "tables": ["test_runs", "test_results"],
        "primary_use": "Test tracking and quality assurance"
    },
    "research_cache": {
        "path": "data/research_cache.db",
        "description": "Research data caching",
        "tables": ["cache_entries"],
        "primary_use": "Research data persistence"
    },
    "strategic_selection": {
        "path": "utils/strategic_selection.db",
        "description": "Rule selection and strategy tracking",
        "tables": ["agent_activities", "rule_selections"],
        "primary_use": "Rule optimization and strategic decision making"
    },
    "rule_optimization": {
        "path": "utils/rule_optimization.db",
        "description": "Rule performance optimization",
        "tables": ["agent_activities", "rule_metrics"],
        "primary_use": "Rule system performance tracking"
    }
}


# ============================================================================
# Core Database Access Functions
# ============================================================================

def get_database_connection(db_name: str) -> Optional[sqlite3.Connection]:
    """
    Get database connection by name.
    
    Args:
        db_name: Database name from registry
        
    Returns:
        Database connection or None if not found
    """
    db_info = DATABASE_REGISTRY.get(db_name)
    if not db_info:
        logger.error(f"Unknown database: {db_name}")
        return None
    
    db_path = Path(db_info["path"])
    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return None
    
    try:
        return sqlite3.connect(str(db_path))
    except Exception as e:
        logger.error(f"Failed to connect to {db_name}: {e}")
        return None


def execute_query(db_name: str, query: str, params: tuple = ()) -> Dict[str, Any]:
    """
    Execute SQL query on specified database.
    
    Args:
        db_name: Database name from registry
        query: SQL query to execute
        params: Query parameters
        
    Returns:
        Query results with metadata
    """
    conn = get_database_connection(db_name)
    if not conn:
        return {"error": f"Cannot connect to database: {db_name}"}
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        conn.close()
        
        return {
            "success": True,
            "database": db_name,
            "results": results,
            "row_count": len(results),
            "columns": columns,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        conn.close()
        return {
            "success": False,
            "error": str(e),
            "database": db_name,
            "query": query
        }


# ============================================================================
# MCP Tools - Database Access
# ============================================================================

if MCP_AVAILABLE:
    
    @mcp_tool(
        "db.list_databases",
        "List all available project databases with their descriptions",
        AccessLevel.UNRESTRICTED,
        ToolCategory.SYSTEM
    )
    def list_databases_mcp() -> Dict[str, Any]:
        """
        List all available databases in the project.
        
        Returns:
            Dictionary with database information
        """
        databases = []
        
        for db_name, db_info in DATABASE_REGISTRY.items():
            db_path = Path(db_info["path"])
            exists = db_path.exists()
            
            # Get size if exists
            size = db_path.stat().st_size if exists else 0
            
            databases.append({
                "name": db_name,
                "path": db_info["path"],
                "description": db_info["description"],
                "primary_use": db_info["primary_use"],
                "tables": db_info["tables"],
                "exists": exists,
                "size_bytes": size,
                "size_mb": round(size / 1024 / 1024, 2)
            })
        
        return {
            "total_databases": len(databases),
            "databases": databases,
            "timestamp": datetime.now().isoformat()
        }
    
    
    @mcp_tool(
        "db.get_schema",
        "Get schema information for a specific database",
        AccessLevel.UNRESTRICTED,
        ToolCategory.SYSTEM
    )
    def get_database_schema_mcp(database_name: str) -> Dict[str, Any]:
        """
        Get schema information for a database.
        
        Args:
            database_name: Name of database from registry
            
        Returns:
            Schema information including tables and columns
        """
        conn = get_database_connection(database_name)
        if not conn:
            return {"error": f"Cannot connect to database: {database_name}"}
        
        try:
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get schema for each table
            table_schemas = {}
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = []
                for col in cursor.fetchall():
                    columns.append({
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "default_value": col[4],
                        "primary_key": bool(col[5])
                    })
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                
                table_schemas[table] = {
                    "columns": columns,
                    "row_count": row_count
                }
            
            conn.close()
            
            return {
                "database": database_name,
                "tables": tables,
                "table_count": len(tables),
                "schemas": table_schemas,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            conn.close()
            return {"error": str(e), "database": database_name}
    
    
    @mcp_tool(
        "db.query_agent_activities",
        "Query agent activities across all databases",
        AccessLevel.UNRESTRICTED,
        ToolCategory.SYSTEM
    )
    def query_agent_activities_mcp(
        agent_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Query agent activities from tracking databases.
        
        Args:
            agent_id: Filter by agent ID (optional)
            activity_type: Filter by activity type (optional)
            limit: Maximum results to return
            
        Returns:
            Combined agent activities from all databases
        """
        all_activities = []
        
        # Databases with agent_activities table
        db_names = ["agent_tracking", "optimization", "analytics", "security_events", 
                   "learning_experiences", "strategic_selection", "rule_optimization"]
        
        for db_name in db_names:
            conn = get_database_connection(db_name)
            if not conn:
                continue
            
            try:
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_activities'")
                if not cursor.fetchone():
                    conn.close()
                    continue
                
                # Build query
                query = "SELECT * FROM agent_activities WHERE 1=1"
                params = []
                
                if agent_id:
                    query += " AND agent_id = ?"
                    params.append(agent_id)
                
                if activity_type:
                    query += " AND activity_type = ?"
                    params.append(activity_type)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, tuple(params))
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                for row in rows:
                    activity = dict(zip(columns, row))
                    activity["source_database"] = db_name
                    all_activities.append(activity)
                
                conn.close()
                
            except Exception as e:
                logger.error(f"Error querying {db_name}: {e}")
                if conn:
                    conn.close()
        
        # Sort by timestamp
        all_activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "total_activities": len(all_activities),
            "activities": all_activities[:limit],
            "filters": {
                "agent_id": agent_id,
                "activity_type": activity_type,
                "limit": limit
            },
            "timestamp": datetime.now().isoformat()
        }
    
    
    @mcp_tool(
        "db.get_agent_timeline",
        "Get comprehensive timeline of agent activities",
        AccessLevel.UNRESTRICTED,
        ToolCategory.SYSTEM
    )
    def get_agent_timeline_mcp(agent_id: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """
        Get timeline of agent activities from agent_tracking database.
        
        Args:
            agent_id: Filter by agent ID (optional)
            hours: Time window in hours
            
        Returns:
            Agent timeline with events and context switches
        """
        conn = get_database_connection("agent_tracking")
        if not conn:
            return {"error": "Cannot connect to agent_tracking database"}
        
        try:
            cursor = conn.cursor()
            
            # Calculate time threshold
            time_threshold = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            # Get agent events
            query = "SELECT * FROM agent_events WHERE timestamp > ?"
            params = [time_threshold]
            
            if agent_id:
                query += " AND agent_id = ?"
                params.append(agent_id)
            
            query += " ORDER BY timestamp DESC LIMIT 100"
            
            cursor.execute(query, tuple(params))
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            events = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Get context switches
            query = "SELECT * FROM context_switches WHERE timestamp > ?"
            params = [time_threshold]
            
            query += " ORDER BY timestamp DESC LIMIT 50"
            
            cursor.execute(query, tuple(params))
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            switches = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                "agent_id": agent_id,
                "time_window_hours": hours,
                "events_count": len(events),
                "context_switches_count": len(switches),
                "events": events,
                "context_switches": switches,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            conn.close()
            return {"error": str(e)}
    
    
    @mcp_tool(
        "db.get_rag_statistics",
        "Get RAG system statistics and usage metrics",
        AccessLevel.UNRESTRICTED,
        ToolCategory.SYSTEM
    )
    def get_rag_statistics_mcp() -> Dict[str, Any]:
        """
        Get statistics from RAG system database.
        
        Returns:
            RAG system statistics
        """
        conn = get_database_connection("rag_system")
        if not conn:
            return {"error": "Cannot connect to rag_system database"}
        
        try:
            cursor = conn.cursor()
            stats = {}
            
            # Indexed documents
            cursor.execute("SELECT COUNT(*), SUM(chunk_count), SUM(file_size) FROM indexed_documents")
            row = cursor.fetchone()
            stats["indexed_documents"] = {
                "total_documents": row[0] if row[0] else 0,
                "total_chunks": row[1] if row[1] else 0,
                "total_size_bytes": row[2] if row[2] else 0,
                "total_size_mb": round(row[2] / 1024 / 1024, 2) if row[2] else 0
            }
            
            # Query logs (last 24 hours)
            time_threshold = (datetime.now() - timedelta(hours=24)).isoformat()
            cursor.execute(
                "SELECT COUNT(*), AVG(retrieval_time), AVG(results_count) FROM query_logs WHERE executed_at > ?",
                (time_threshold,)
            )
            row = cursor.fetchone()
            stats["recent_queries"] = {
                "total_queries_24h": row[0] if row[0] else 0,
                "avg_retrieval_time": round(row[1], 3) if row[1] else 0,
                "avg_results_count": round(row[2], 1) if row[2] else 0
            }
            
            # Query types
            cursor.execute(
                "SELECT query_type, COUNT(*) FROM query_logs WHERE executed_at > ? GROUP BY query_type",
                (time_threshold,)
            )
            stats["query_types_24h"] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Most accessed documents
            cursor.execute(
                "SELECT file_path, access_count FROM indexed_documents ORDER BY access_count DESC LIMIT 10"
            )
            stats["most_accessed_documents"] = [
                {"file_path": row[0], "access_count": row[1]} for row in cursor.fetchall()
            ]
            
            conn.close()
            
            stats["timestamp"] = datetime.now().isoformat()
            return stats
            
        except Exception as e:
            conn.close()
            return {"error": str(e)}
    
    
    @mcp_tool(
        "db.execute_custom_query",
        "Execute custom SQL query on specified database (read-only)",
        AccessLevel.RESTRICTED,
        ToolCategory.SYSTEM
    )
    def execute_custom_query_mcp(database_name: str, query: str) -> Dict[str, Any]:
        """
        Execute custom read-only SQL query.
        
        Args:
            database_name: Name of database from registry
            query: SQL SELECT query
            
        Returns:
            Query results
        """
        # Security: Only allow SELECT queries
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            return {"error": "Only SELECT queries are allowed"}
        
        if any(keyword in query_upper for keyword in ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE"]):
            return {"error": "Modifying queries are not allowed"}
        
        return execute_query(database_name, query)


# ============================================================================
# Agent State Integration
# ============================================================================

class AgentStateTracker:
    """
    Unified agent state tracker that logs to databases.
    Integrates with ContextAwareAgent for comprehensive tracking.
    """
    
    def __init__(self):
        """Initialize agent state tracker."""
        try:
            from utils.system.multi_database_logger import get_multi_database_logger
            self.logger = get_multi_database_logger()
            self.enabled = True
        except Exception as e:
            logger.error(f"Failed to initialize multi-database logger: {e}")
            self.enabled = False
    
    def log_agent_start(self, agent_id: str, agent_type: str, context: str) -> None:
        """Log agent start event."""
        if not self.enabled:
            return
        
        self.logger.log_activity(
            agent_id=agent_id,
            activity_type="agent_start",
            context=context,
            details={
                "agent_type": agent_type,
                "start_time": datetime.now().isoformat()
            }
        )
    
    def log_context_search(self, agent_id: str, query: str, results_count: int, retrieval_time: float) -> None:
        """Log context search event."""
        if not self.enabled:
            return
        
        self.logger.log_activity(
            agent_id=agent_id,
            activity_type="context_search",
            context="rag_retrieval",
            details={
                "query": query,
                "results_count": results_count,
                "retrieval_time": retrieval_time,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_task_execution(self, agent_id: str, task_type: str, status: str, duration: float) -> None:
        """Log task execution event."""
        if not self.enabled:
            return
        
        self.logger.log_activity(
            agent_id=agent_id,
            activity_type="task_execution",
            context=task_type,
            details={
                "status": status,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
        )


# Singleton instance
_agent_state_tracker = None

def get_agent_state_tracker() -> AgentStateTracker:
    """Get singleton agent state tracker."""
    global _agent_state_tracker
    if _agent_state_tracker is None:
        _agent_state_tracker = AgentStateTracker()
    return _agent_state_tracker


if __name__ == "__main__":
    # Test database tools
    print("🧪 Testing Database MCP Tools")
    
    # List databases
    result = list_databases_mcp()
    print(f"\n📊 Found {result['total_databases']} databases")
    for db in result['databases'][:3]:
        print(f"   - {db['name']}: {db['description']}")
    
    # Get agent activities
    result = query_agent_activities_mcp(limit=5)
    print(f"\n📋 Found {result['total_activities']} agent activities")
    
    # Get RAG statistics
    result = get_rag_statistics_mcp()
    if "indexed_documents" in result:
        print(f"\n📚 RAG Statistics:")
        print(f"   - Indexed documents: {result['indexed_documents']['total_documents']}")
        print(f"   - Total chunks: {result['indexed_documents']['total_chunks']}")
    
    print("\n✅ Database tools test complete!")

