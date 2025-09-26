#!/usr/bin/env python3
"""
Database Verification and Repair Tool
====================================

Verifies and repairs the universal_agent_tracking.db to ensure all 7 tables
exist and can be written to properly.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path

def verify_and_repair_database():
    """Verify and repair the universal agent tracking database."""
    
    db_path = "utils/universal_agent_tracking.db"
    
    print("🔍 Verifying universal_agent_tracking.db...")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check what tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            print(f"📋 Existing tables: {existing_tables}")
            
            # Define required tables with their schemas
            required_tables = {
                "agent_communications": """
                    CREATE TABLE IF NOT EXISTS agent_communications (
                        communication_id TEXT PRIMARY KEY,
                        sender_agent TEXT,
                        receiver_agent TEXT,
                        message_type TEXT,
                        message_content TEXT,
                        timestamp TEXT,
                        context TEXT
                    )
                """,
                "agent_events": """
                    CREATE TABLE IF NOT EXISTS agent_events (
                        event_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        agent_id TEXT NOT NULL,
                        agent_type TEXT NOT NULL,
                        context TEXT NOT NULL,
                        details TEXT,
                        rules_affected TEXT,
                        performance_metrics TEXT
                    )
                """,
                "agent_sessions": """
                    CREATE TABLE IF NOT EXISTS agent_sessions (
                        session_id TEXT PRIMARY KEY,
                        agent_id TEXT,
                        agent_type TEXT,
                        timestamp TEXT,
                        context TEXT,
                        agent_name TEXT,
                        status TEXT,
                        metadata TEXT,
                        start_time TEXT,
                        last_activity TEXT
                    )
                """,
                "context_coordination": """
                    CREATE TABLE IF NOT EXISTS context_coordination (
                        coordination_id TEXT PRIMARY KEY,
                        source_context TEXT,
                        target_context TEXT,
                        coordination_type TEXT,
                        details TEXT,
                        timestamp TEXT
                    )
                """,
                "context_switches": """
                    CREATE TABLE IF NOT EXISTS context_switches (
                        switch_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        from_context TEXT,
                        to_context TEXT,
                        timestamp TEXT,
                        trigger_type TEXT,
                        trigger_details TEXT
                    )
                """,
                "performance_metrics": """
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        metric_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        metric_type TEXT,
                        metric_value REAL,
                        context TEXT,
                        timestamp TEXT,
                        details TEXT
                    )
                """,
                "rule_activations": """
                    CREATE TABLE IF NOT EXISTS rule_activations (
                        activation_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        rules_activated TEXT,
                        trigger_event TEXT,
                        trigger_details TEXT,
                        timestamp TEXT,
                        performance_impact TEXT
                    )
                """
            }
            
            # Create missing tables
            for table_name, schema in required_tables.items():
                cursor.execute(schema)
                print(f"✅ Ensured table exists: {table_name}")
            
            conn.commit()
            
            # Test write to each table
            print("\n🧪 Testing write access to all tables...")
            test_results = {}
            
            timestamp = datetime.now().isoformat()
            
            # Test each table
            for table_name in required_tables.keys():
                try:
                    test_id = str(uuid.uuid4())
                    
                    if table_name == "agent_communications":
                        cursor.execute("""
                            INSERT INTO agent_communications 
                            (communication_id, sender_agent, receiver_agent, message_type, message_content, timestamp, context)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (test_id, "test_sender", "test_receiver", "test_message", "test_content", timestamp, "TEST"))
                        
                    elif table_name == "agent_events":
                        cursor.execute("""
                            INSERT INTO agent_events 
                            (event_id, timestamp, event_type, agent_id, agent_type, context, details, rules_affected, performance_metrics)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (test_id, timestamp, "test_event", "test_agent", "test_type", "TEST", "test_details", "[]", "{}"))
                        
                    elif table_name == "agent_sessions":
                        cursor.execute("""
                            INSERT INTO agent_sessions 
                            (session_id, agent_id, agent_type, timestamp, context, agent_name, status, metadata, start_time, last_activity)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (test_id, "test_agent", "test_type", timestamp, "TEST", "test_name", "active", "{}", timestamp, timestamp))
                        
                    elif table_name == "context_coordination":
                        cursor.execute("""
                            INSERT INTO context_coordination 
                            (coordination_id, source_context, target_context, coordination_type, details, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (test_id, "TEST_SOURCE", "TEST_TARGET", "test_type", "{}", timestamp))
                        
                    elif table_name == "context_switches":
                        cursor.execute("""
                            INSERT INTO context_switches 
                            (switch_id, session_id, from_context, to_context, timestamp, trigger_type, trigger_details)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (test_id, "test_session", "FROM_TEST", "TO_TEST", timestamp, "test_trigger", "{}"))
                        
                    elif table_name == "performance_metrics":
                        cursor.execute("""
                            INSERT INTO performance_metrics 
                            (metric_id, session_id, metric_type, metric_value, context, timestamp, details)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (test_id, "test_session", "test_metric", 1.0, "TEST", timestamp, "{}"))
                        
                    elif table_name == "rule_activations":
                        cursor.execute("""
                            INSERT INTO rule_activations 
                            (activation_id, session_id, rules_activated, trigger_event, trigger_details, timestamp, performance_impact)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (test_id, "test_session", "[]", "test_event", "{}", timestamp, "{}"))
                    
                    conn.commit()
                    test_results[table_name] = "✅ PASS"
                    
                except Exception as e:
                    test_results[table_name] = f"❌ FAIL: {e}"
            
            # Show test results
            print("\n📊 Table Write Test Results:")
            for table_name, result in test_results.items():
                print(f"  {table_name}: {result}")
            
            # Get final record counts
            print("\n📈 Final Record Counts:")
            for table_name in required_tables.keys():
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  {table_name}: {count} records")
                
            print("\n✅ Database verification and repair complete!")
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")

if __name__ == "__main__":
    verify_and_repair_database()
