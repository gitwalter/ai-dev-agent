#!/usr/bin/env python3
"""
Comprehensive Logging Fix - Debug and repair agent logging system
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ComprehensiveLoggingFix:
    """Fix and validate the comprehensive logging system."""
    
    def __init__(self):
        self.db_path = Path("utils/universal_agent_tracking.db")
        self.issues_found = []
        self.fixes_applied = []
    
    def diagnose_logging_issues(self) -> Dict[str, Any]:
        """Comprehensive diagnosis of logging issues."""
        print("🔍 DIAGNOSING LOGGING SYSTEM ISSUES")
        print("=" * 50)
        
        diagnosis = {
            "database_exists": self.db_path.exists(),
            "table_counts": {},
            "schema_issues": [],
            "sample_data": {},
            "missing_columns": []
        }
        
        if not self.db_path.exists():
            self.issues_found.append("Database file does not exist")
            return diagnosis
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check all tables and counts
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                print("📊 TABLE ANALYSIS:")
                for table in tables:
                    table_name = table[0]
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        diagnosis["table_counts"][table_name] = count
                        print(f"  {table_name}: {count} records")
                        
                        # Check schema for important tables
                        if table_name in ["context_switches", "rule_activations", "agent_sessions"]:
                            cursor.execute(f"PRAGMA table_info({table_name})")
                            schema = cursor.fetchall()
                            print(f"    Schema: {[col[1] for col in schema]}")
                            
                            # Sample data
                            cursor.execute(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 3")
                            sample = cursor.fetchall()
                            diagnosis["sample_data"][table_name] = sample
                            
                    except Exception as e:
                        print(f"  ERROR with {table_name}: {e}")
                        self.issues_found.append(f"Table {table_name} error: {e}")
                
                # Check for missing activation_id column in rule_activations
                try:
                    cursor.execute("PRAGMA table_info(rule_activations)")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    if "activation_id" not in column_names:
                        self.issues_found.append("rule_activations table missing activation_id column")
                        diagnosis["missing_columns"].append("activation_id in rule_activations")
                        
                except Exception as e:
                    self.issues_found.append(f"Could not check rule_activations schema: {e}")
        
        except Exception as e:
            self.issues_found.append(f"Database connection error: {e}")
        
        return diagnosis
    
    def fix_database_schema(self):
        """Fix database schema issues."""
        print("\n🔧 FIXING DATABASE SCHEMA")
        print("-" * 30)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create complete rule_activations table if needed
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rule_activations (
                        activation_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        rules_activated TEXT,
                        trigger_event TEXT,
                        trigger_details TEXT,
                        timestamp TEXT,
                        performance_impact TEXT
                    )
                """)
                
                # Ensure context_switches table exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS context_switches (
                        switch_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        from_context TEXT,
                        to_context TEXT,
                        timestamp TEXT,
                        trigger_type TEXT,
                        trigger_details TEXT
                    )
                """)
                
                # Ensure all other required tables exist
                required_tables = {
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
                    "agent_events": """
                        CREATE TABLE IF NOT EXISTS agent_events (
                            event_id TEXT PRIMARY KEY,
                            timestamp TEXT,
                            event_type TEXT,
                            agent_id TEXT,
                            agent_type TEXT,
                            context TEXT,
                            details TEXT
                        )
                    """,
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
                    "performance_metrics": """
                        CREATE TABLE IF NOT EXISTS performance_metrics (
                            metric_id TEXT PRIMARY KEY,
                            session_id TEXT,
                            metric_type TEXT,
                            metric_value TEXT,
                            context TEXT,
                            timestamp TEXT,
                            details TEXT
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
                    """
                }
                
                for table_name, create_sql in required_tables.items():
                    cursor.execute(create_sql)
                    print(f"✅ Ensured {table_name} table exists")
                
                conn.commit()
                self.fixes_applied.append("Database schema fixed")
                
        except Exception as e:
            self.issues_found.append(f"Schema fix failed: {e}")
            print(f"❌ Schema fix failed: {e}")
    
    def create_test_data(self):
        """Create test data to verify logging works."""
        print("\n🧪 CREATING TEST DATA")
        print("-" * 25)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create test session
                session_id = str(uuid.uuid4())
                timestamp = datetime.now().isoformat()
                
                # Test agent session
                cursor.execute("""
                    INSERT INTO agent_sessions 
                    (session_id, agent_id, agent_type, timestamp, context, agent_name, status, start_time, last_activity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (session_id, "test_agent", "CURSOR_AGENT", timestamp, "TESTING", "Test Agent", "active", timestamp, timestamp))
                
                # Test context switch
                switch_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO context_switches 
                    (switch_id, session_id, from_context, to_context, timestamp, trigger_type, trigger_details)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (switch_id, session_id, "SYSTEM_STARTUP", "TESTING", timestamp, "manual_test", 
                     json.dumps({"test": True, "keyword": "@test"})))
                
                # Test rule activation
                activation_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO rule_activations 
                    (activation_id, session_id, rules_activated, trigger_event, trigger_details, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (activation_id, session_id, 
                     json.dumps(["development_excellence", "test_driven_development"]),
                     "context_switch", 
                     json.dumps({"keyword": "@test", "context": "TESTING"}),
                     timestamp))
                
                # Test agent event
                event_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO agent_events 
                    (event_id, timestamp, event_type, agent_id, agent_type, context, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (event_id, timestamp, "keyword_detection", "test_agent", "CURSOR_AGENT", "TESTING",
                     json.dumps({"keyword": "@test", "test_mode": True})))
                
                conn.commit()
                print("✅ Test data created successfully")
                self.fixes_applied.append("Test data created")
                
        except Exception as e:
            self.issues_found.append(f"Test data creation failed: {e}")
            print(f"❌ Test data creation failed: {e}")
    
    def verify_logging_system(self) -> bool:
        """Verify the logging system is working."""
        print("\n✅ VERIFYING LOGGING SYSTEM")
        print("-" * 30)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if we can read from all tables
                tables_to_check = ["context_switches", "rule_activations", "agent_sessions", "agent_events"]
                
                for table in tables_to_check:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  {table}: {count} records")
                    
                    if count == 0:
                        print(f"    ⚠️  No records in {table}")
                
                # Test if we can successfully insert and read
                test_id = str(uuid.uuid4())
                timestamp = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT INTO context_switches 
                    (switch_id, session_id, from_context, to_context, timestamp, trigger_type, trigger_details)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (test_id, "verification_test", "TEST", "VERIFIED", timestamp, "verification", 
                     json.dumps({"verification": True})))
                
                # Try to read it back
                cursor.execute("SELECT * FROM context_switches WHERE switch_id = ?", (test_id,))
                result = cursor.fetchone()
                
                if result:
                    print("✅ Database write/read test successful")
                    conn.commit()
                    return True
                else:
                    print("❌ Database write/read test failed")
                    return False
                    
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive repair report."""
        report = []
        report.append("🔧 COMPREHENSIVE LOGGING SYSTEM REPAIR REPORT")
        report.append("=" * 55)
        report.append("")
        
        if self.issues_found:
            report.append("❌ ISSUES FOUND:")
            for issue in self.issues_found:
                report.append(f"  • {issue}")
            report.append("")
        
        if self.fixes_applied:
            report.append("✅ FIXES APPLIED:")
            for fix in self.fixes_applied:
                report.append(f"  • {fix}")
            report.append("")
        
        # Current status
        diagnosis = self.diagnose_logging_issues()
        report.append("📊 CURRENT STATUS:")
        for table, count in diagnosis["table_counts"].items():
            report.append(f"  • {table}: {count} records")
        
        return "\n".join(report)

def main():
    """Main repair function."""
    fixer = ComprehensiveLoggingFix()
    
    # 1. Diagnose issues
    diagnosis = fixer.diagnose_logging_issues()
    
    # 2. Fix schema issues
    fixer.fix_database_schema()
    
    # 3. Create test data
    fixer.create_test_data()
    
    # 4. Verify system works
    verification_success = fixer.verify_logging_system()
    
    # 5. Generate report
    report = fixer.generate_comprehensive_report()
    print("\n" + report)
    
    return verification_success

if __name__ == "__main__":
    success = main()
    print(f"\n🎯 REPAIR {'SUCCESSFUL' if success else 'FAILED'}")
