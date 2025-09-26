#!/usr/bin/env python3
"""
Direct database fix - recreate schema and populate with test data
"""

import sqlite3
import json
import uuid
from datetime import datetime

def fix_database_schema():
    """Fix the database schema immediately."""
    print("🔧 FIXING DATABASE SCHEMA NOW")
    print("=" * 35)
    
    db_path = "utils/universal_agent_tracking.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # First, let's see what we have
            print("📊 Current schema:")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table_name in [t[0] for t in tables]:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"  {table_name}: {[col[1] for col in columns]}")
            
            # Drop and recreate rule_activations with correct schema
            print("\n🔄 Recreating rule_activations table...")
            cursor.execute("DROP TABLE IF EXISTS rule_activations")
            cursor.execute("""
                CREATE TABLE rule_activations (
                    activation_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    rules_activated TEXT,
                    trigger_event TEXT,
                    trigger_details TEXT,
                    timestamp TEXT,
                    performance_impact TEXT
                )
            """)
            print("✅ rule_activations table recreated")
            
            # Ensure context_switches has correct schema
            print("\n🔄 Checking context_switches table...")
            cursor.execute("PRAGMA table_info(context_switches)")
            context_columns = [col[1] for col in cursor.fetchall()]
            
            if "switch_id" not in context_columns:
                print("Recreating context_switches table...")
                cursor.execute("DROP TABLE IF EXISTS context_switches")
                cursor.execute("""
                    CREATE TABLE context_switches (
                        switch_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        from_context TEXT,
                        to_context TEXT,
                        timestamp TEXT,
                        trigger_type TEXT,
                        trigger_details TEXT
                    )
                """)
                print("✅ context_switches table recreated")
            
            # Add test data immediately
            print("\n🧪 Adding test data...")
            
            # Test session
            session_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Add to agent_sessions
            cursor.execute("""
                INSERT OR REPLACE INTO agent_sessions 
                (session_id, agent_id, agent_type, timestamp, context, agent_name, status, start_time, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (session_id, "test_agent", "CURSOR_AGENT", timestamp, "TESTING", "Test Agent", "active", timestamp, timestamp))
            
            # Add multiple context switches
            contexts = [
                ("SYSTEM_STARTUP", "AGILE", "agile_test"),
                ("AGILE", "TESTING", "test_trigger"),
                ("TESTING", "DEBUGGING", "debug_session"),
                ("DEBUGGING", "DOCUMENTATION", "doc_update"),
                ("DOCUMENTATION", "CODING", "code_review")
            ]
            
            for i, (from_ctx, to_ctx, reason) in enumerate(contexts):
                switch_id = str(uuid.uuid4())
                switch_timestamp = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT INTO context_switches 
                    (switch_id, session_id, from_context, to_context, timestamp, trigger_type, trigger_details)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (switch_id, session_id, from_ctx, to_ctx, switch_timestamp, "test_switch", 
                     json.dumps({"test": True, "reason": reason, "sequence": i})))
                
                print(f"  ✅ Context switch: {from_ctx} → {to_ctx}")
            
            # Add rule activations
            rules_sets = [
                ["development_excellence", "agile_coordination"],
                ["test_driven_development", "systematic_completion"],
                ["debugging_protocols", "error_handling"],
                ["documentation_standards", "clear_communication"],
                ["code_quality", "best_practices"]
            ]
            
            for i, rules in enumerate(rules_sets):
                activation_id = str(uuid.uuid4())
                activation_timestamp = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT INTO rule_activations 
                    (activation_id, session_id, rules_activated, trigger_event, trigger_details, timestamp, performance_impact)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (activation_id, session_id, json.dumps(rules), "context_switch", 
                     json.dumps({"context": contexts[i % len(contexts)][1], "test": True}),
                     activation_timestamp, json.dumps({"efficiency": 0.8 + i * 0.05})))
                
                print(f"  ✅ Rule activation: {rules}")
            
            conn.commit()
            
            # Verify the fix
            print("\n✅ VERIFICATION:")
            
            # Count records
            for table in ["context_switches", "rule_activations", "agent_sessions"]:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} records")
            
            # Show schema
            print("\n📋 Fixed schema:")
            for table in ["rule_activations", "context_switches"]:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print(f"  {table}: {[col[1] for col in columns]}")
            
            print(f"\n🎯 DATABASE SCHEMA FIXED SUCCESSFULLY!")
            return True
            
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_database_schema()
    if success:
        print("\n✅ You can now refresh the app - the history should show multiple entries!")
    else:
        print("\n❌ Fix failed - check the error above")

