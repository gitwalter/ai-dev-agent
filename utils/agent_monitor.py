#!/usr/bin/env python3
"""
Professional Agent Activity Monitor
==================================

Professional, production-ready agent monitoring system with NO fake data.
Only displays real agent activities, lifecycle events, and performance metrics.
"""

import sqlite3
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ProfessionalAgentMonitor:
    """
    Professional agent monitoring system that shows only real data.
    
    Features:
    - Real agent lifecycle tracking (active/inactive/completed/error)
    - Actual database queries with proper schema handling
    - Professional metrics without simulation
    - Proper agent session management
    - Real-time activity monitoring
    """
    
    def __init__(self, db_path: str = "utils/universal_agent_tracking.db"):
        self.db_path = db_path
        self.available_tables = {}
        self.available_columns = {}
        self._discover_database_schema()
    
    def _discover_database_schema(self):
        """Discover actual database schema to avoid column errors."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                self.available_tables[table_name] = True
                
                # Get columns for each table
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                self.available_columns[table_name] = [col[1] for col in columns]
                logger.info(f"📊 Table {table_name}: {len(columns)} columns")
            
            conn.close()
            logger.info(f"✅ Discovered {len(self.available_tables)} tables in database")
            
        except Exception as e:
            logger.error(f"❌ Schema discovery failed: {e}")
            self.available_tables = {}
            self.available_columns = {}
    
    def get_real_agent_statistics(self) -> Dict[str, Any]:
        """Get REAL agent statistics with no fake data."""
        stats = {
            'active_agents': 0,
            'total_agents': 0,
            'activities_today': 0,
            'context_switches_today': 0,
            'communications_today': 0,
            'rule_activations_today': 0,
            'last_activity': 'None',
            'database_status': 'disconnected'
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            today = date.today().isoformat()
            
            # REAL agent session counts
            if 'agent_sessions' in self.available_tables:
                # Count by actual status
                cursor.execute("SELECT status, COUNT(*) FROM agent_sessions GROUP BY status")
                status_counts = cursor.fetchall()
                
                for status, count in status_counts:
                    if status == 'active':
                        stats['active_agents'] = count
                    stats['total_agents'] += count
                
                # If no status column or all NULL, count total
                if stats['total_agents'] == 0:
                    cursor.execute("SELECT COUNT(*) FROM agent_sessions")
                    stats['total_agents'] = cursor.fetchone()[0]
            
            # REAL activity counts (using correct column names)
            if 'agent_events' in self.available_tables:
                timestamp_col = self._get_timestamp_column('agent_events')
                if timestamp_col:
                    cursor.execute(f"SELECT COUNT(*) FROM agent_events WHERE {timestamp_col} LIKE ?", (f"{today}%",))
                    stats['activities_today'] = cursor.fetchone()[0]
            
            # REAL context switch counts
            if 'context_switches' in self.available_tables:
                timestamp_col = self._get_timestamp_column('context_switches')
                if timestamp_col:
                    cursor.execute(f"SELECT COUNT(*) FROM context_switches WHERE {timestamp_col} LIKE ?", (f"{today}%",))
                    stats['context_switches_today'] = cursor.fetchone()[0]
            
            # REAL communication counts
            if 'agent_communications' in self.available_tables:
                timestamp_col = self._get_timestamp_column('agent_communications')
                if timestamp_col:
                    cursor.execute(f"SELECT COUNT(*) FROM agent_communications WHERE {timestamp_col} LIKE ?", (f"{today}%",))
                    stats['communications_today'] = cursor.fetchone()[0]
            
            # REAL rule activation counts
            if 'rule_activations' in self.available_tables:
                timestamp_col = self._get_timestamp_column('rule_activations')
                if timestamp_col:
                    cursor.execute(f"SELECT COUNT(*) FROM rule_activations WHERE {timestamp_col} LIKE ?", (f"{today}%",))
                    stats['rule_activations_today'] = cursor.fetchone()[0]
            
            # REAL last activity
            if 'agent_events' in self.available_tables:
                timestamp_col = self._get_timestamp_column('agent_events')
                if timestamp_col:
                    cursor.execute(f"SELECT {timestamp_col} FROM agent_events ORDER BY {timestamp_col} DESC LIMIT 1")
                    result = cursor.fetchone()
                    stats['last_activity'] = result[0] if result else 'None'
            
            stats['database_status'] = 'connected'
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Database query failed: {e}")
            stats['last_activity'] = f'Database Error: {e}'
            stats['database_status'] = 'error'
        
        return stats
    
    def _get_timestamp_column(self, table_name: str) -> Optional[str]:
        """Get the correct timestamp column name for a table."""
        if table_name not in self.available_columns:
            return None
        
        columns = self.available_columns[table_name]
        
        # Priority order for timestamp columns
        timestamp_candidates = ['timestamp', 'created_at', 'start_time', 'time', 'date']
        
        for candidate in timestamp_candidates:
            if candidate in columns:
                return candidate
        
        return None
    
    def cleanup_stale_agents(self, hours_threshold: int = 24) -> int:
        """
        Clean up stale agent sessions that should no longer be 'active'.
        
        Args:
            hours_threshold: Hours after which inactive agents are marked as 'inactive'
            
        Returns:
            Number of agents cleaned up
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(hours=hours_threshold)).isoformat()
            
            # Mark old 'active' agents as 'inactive'
            if 'agent_sessions' in self.available_tables:
                columns = self.available_columns.get('agent_sessions', [])
                
                if 'status' in columns and 'last_activity' in columns:
                    cursor.execute("""
                        UPDATE agent_sessions 
                        SET status = 'inactive' 
                        WHERE status = 'active' 
                        AND (last_activity IS NULL OR last_activity < ?)
                    """, (cutoff_time,))
                    
                    cleanup_count = cursor.rowcount
                    conn.commit()
                    
                elif 'status' in columns and 'start_time' in columns:
                    cursor.execute("""
                        UPDATE agent_sessions 
                        SET status = 'inactive' 
                        WHERE status = 'active' 
                        AND start_time < ?
                    """, (cutoff_time,))
                    
                    cleanup_count = cursor.rowcount
                    conn.commit()
                    
                else:
                    cleanup_count = 0
                    logger.warning("⚠️ Cannot cleanup agents - no suitable columns found")
            
            conn.close()
            
            if cleanup_count > 0:
                logger.info(f"✅ Cleaned up {cleanup_count} stale agent sessions")
            
            return cleanup_count
            
        except Exception as e:
            logger.error(f"❌ Agent cleanup failed: {e}")
            return 0
    
    def get_agent_lifecycle_summary(self) -> Dict[str, Any]:
        """Get professional summary of agent lifecycle states."""
        summary = {
            'total_sessions': 0,
            'status_breakdown': {},
            'recent_activations': [],
            'active_session_details': [],
            'performance_health': 'unknown'
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if 'agent_sessions' in self.available_tables:
                # Total sessions
                cursor.execute("SELECT COUNT(*) FROM agent_sessions")
                summary['total_sessions'] = cursor.fetchone()[0]
                
                # Status breakdown
                if 'status' in self.available_columns.get('agent_sessions', []):
                    cursor.execute("SELECT status, COUNT(*) FROM agent_sessions GROUP BY status")
                    for status, count in cursor.fetchall():
                        summary['status_breakdown'][status or 'unspecified'] = count
                
                # Recent activations (last 24 hours)
                timestamp_col = self._get_timestamp_column('agent_sessions')
                if timestamp_col:
                    yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
                    cursor.execute(f"""
                        SELECT agent_id, agent_type, {timestamp_col}
                        FROM agent_sessions 
                        WHERE {timestamp_col} > ?
                        ORDER BY {timestamp_col} DESC LIMIT 10
                    """, (yesterday,))
                    
                    for row in cursor.fetchall():
                        summary['recent_activations'].append({
                            'agent_id': row[0],
                            'agent_type': row[1],
                            'timestamp': row[2]
                        })
                
                # Currently active session details
                if 'status' in self.available_columns.get('agent_sessions', []):
                    cursor.execute("""
                        SELECT agent_id, agent_type, context, start_time
                        FROM agent_sessions 
                        WHERE status = 'active'
                        ORDER BY start_time DESC LIMIT 20
                    """)
                    
                    for row in cursor.fetchall():
                        summary['active_session_details'].append({
                            'agent_id': row[0][:12] + '...' if row[0] and len(row[0]) > 12 else row[0],
                            'agent_type': row[1],
                            'context': row[2],
                            'start_time': row[3]
                        })
            
            # Calculate performance health
            active_count = summary['status_breakdown'].get('active', 0)
            total_count = summary['total_sessions']
            
            if total_count == 0:
                summary['performance_health'] = 'no_data'
            elif active_count > 100:
                summary['performance_health'] = 'concerning'  # Too many active agents
            elif active_count > 50:
                summary['performance_health'] = 'monitoring'
            else:
                summary['performance_health'] = 'healthy'
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Lifecycle summary failed: {e}")
            summary['error'] = str(e)
        
        return summary
    
    def get_real_activity_timeline(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get real activity timeline with no fake data."""
        timeline = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            # Get real agent events
            if 'agent_events' in self.available_tables:
                timestamp_col = self._get_timestamp_column('agent_events')
                event_type_col = 'event_type' if 'event_type' in self.available_columns.get('agent_events', []) else 'activity_type'
                
                if timestamp_col:
                    cursor.execute(f"""
                        SELECT {timestamp_col}, {event_type_col}, session_id, details
                        FROM agent_events 
                        WHERE {timestamp_col} > ?
                        ORDER BY {timestamp_col} DESC LIMIT 50
                    """, (cutoff_time,))
                    
                    for row in cursor.fetchall():
                        timeline.append({
                            'timestamp': row[0],
                            'event_type': row[1],
                            'session_id': row[2][:12] + '...' if row[2] else 'unknown',
                            'details': row[3],
                            'source': 'agent_events'
                        })
            
            # Get real context switches
            if 'context_switches' in self.available_tables:
                timestamp_col = self._get_timestamp_column('context_switches')
                
                if timestamp_col:
                    cursor.execute(f"""
                        SELECT {timestamp_col}, new_context, session_id, trigger_event
                        FROM context_switches 
                        WHERE {timestamp_col} > ?
                        ORDER BY {timestamp_col} DESC LIMIT 20
                    """, (cutoff_time,))
                    
                    for row in cursor.fetchall():
                        timeline.append({
                            'timestamp': row[0],
                            'event_type': 'context_switch',
                            'session_id': row[2][:12] + '...' if row[2] else 'unknown',
                            'details': f"→ {row[1]} (trigger: {row[3]})",
                            'source': 'context_switches'
                        })
            
            # Get real rule activations
            if 'rule_activations' in self.available_tables:
                timestamp_col = self._get_timestamp_column('rule_activations')
                
                if timestamp_col:
                    cursor.execute(f"""
                        SELECT {timestamp_col}, rule_name, session_id, trigger_details
                        FROM rule_activations 
                        WHERE {timestamp_col} > ?
                        ORDER BY {timestamp_col} DESC LIMIT 20
                    """, (cutoff_time,))
                    
                    for row in cursor.fetchall():
                        timeline.append({
                            'timestamp': row[0],
                            'event_type': 'rule_activation',
                            'session_id': row[2][:12] + '...' if row[2] else 'unknown',
                            'details': f"Rule: {row[1]} ({row[3]})",
                            'source': 'rule_activations'
                        })
            
            # Sort timeline by timestamp
            timeline.sort(key=lambda x: x['timestamp'], reverse=True)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Activity timeline failed: {e}")
            timeline = [{'error': str(e), 'timestamp': datetime.now().isoformat()}]
        
        return timeline[:50]  # Limit to 50 most recent
