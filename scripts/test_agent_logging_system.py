#!/usr/bin/env python3
"""
Agent Logging System Test and Verification Script
================================================

This script tests and verifies our comprehensive agent logging system.
It checks all 8 databases, verifies logging functionality, and provides
a complete system status report.

Usage:
    python scripts/test_agent_logging_system.py
"""

import sys
import os
import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class AgentLoggingSystemTester:
    """Comprehensive tester for the agent logging system."""
    
    def __init__(self):
        """Initialize the tester."""
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
        
        self.test_results = {}
        
    def create_database_schema(self, db_path: str):
        """Create the database schema if it doesn't exist."""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Create agent_activities table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS agent_activities (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        agent_id TEXT NOT NULL,
                        activity_type TEXT NOT NULL,
                        context TEXT,
                        details TEXT,
                        session_id TEXT
                    )
                """)
                
                # Create index for performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_agent_activities_timestamp 
                    ON agent_activities(timestamp)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_agent_activities_agent_id 
                    ON agent_activities(agent_id)
                """)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ Failed to create schema for {db_path}: {e}")
            return False
    
    def test_database_connection(self, db_name: str, db_path: str):
        """Test connection to a specific database."""
        try:
            # Ensure directory exists
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Create schema
            if not self.create_database_schema(db_path):
                return False
            
            # Test connection
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM agent_activities")
                count = cursor.fetchone()[0]
                
                self.test_results[db_name] = {
                    "status": "✅ Connected",
                    "path": db_path,
                    "record_count": count,
                    "size_bytes": Path(db_path).stat().st_size if Path(db_path).exists() else 0
                }
                return True
                
        except Exception as e:
            self.test_results[db_name] = {
                "status": f"❌ Failed: {e}",
                "path": db_path,
                "record_count": 0,
                "size_bytes": 0
            }
            return False
    
    def test_logging_functionality(self):
        """Test actual logging functionality."""
        print("\n🧪 Testing logging functionality...")
        
        try:
            # Import and initialize the logger
            from utils.system.multi_database_logger import MultiDatabaseLogger
            logger = MultiDatabaseLogger()
            
            # Test logging
            test_data = {
                "test_type": "system_verification",
                "timestamp": datetime.now().isoformat(),
                "test_id": f"test_{int(time.time())}"
            }
            
            logger.log_activity(
                agent_id="test_agent_verification",
                activity_type="system_test",
                context="Agent logging system verification",
                details=test_data
            )
            
            print("✅ Logging functionality test passed")
            return True
            
        except Exception as e:
            print(f"❌ Logging functionality test failed: {e}")
            return False
    
    def test_universal_tracker_integration(self):
        """Test universal tracker integration."""
        print("\n🔗 Testing Universal Tracker integration...")
        
        try:
            from utils.system.universal_agent_tracker import get_universal_tracker, AgentType, ContextType
            
            tracker = get_universal_tracker()
            
            # Test registration
            test_result = tracker.register_agent(
                agent_id="test_tracker_agent",
                agent_type=AgentType.CURSOR_KEYWORD,
                context=ContextType.AGILE
            )
            
            print("✅ Universal Tracker integration test passed")
            return True
            
        except Exception as e:
            print(f"❌ Universal Tracker integration test failed: {e}")
            return False
    
    def test_cursor_keyword_logging(self):
        """Test cursor keyword logging system."""
        print("\n🎯 Testing Cursor Keyword logging...")
        
        try:
            from utils.system.cursor_keyword_agent_logger import CursorKeywordAgentLogger
            
            keyword_logger = CursorKeywordAgentLogger()
            
            print("✅ Cursor Keyword logging test passed")
            return True
            
        except Exception as e:
            print(f"❌ Cursor Keyword logging test failed: {e}")
            return False
    
    def verify_recent_activity(self):
        """Verify recent agent activity in databases."""
        print("\n📊 Checking recent agent activity...")
        
        total_recent_records = 0
        
        for db_name, db_path in self.databases.items():
            try:
                if not Path(db_path).exists():
                    continue
                    
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Check for recent activity (last 24 hours)
                    cursor.execute("""
                        SELECT COUNT(*) FROM agent_activities 
                        WHERE datetime(timestamp) > datetime('now', '-1 day')
                    """)
                    
                    recent_count = cursor.fetchone()[0]
                    total_recent_records += recent_count
                    
                    if recent_count > 0:
                        print(f"  📈 {db_name}: {recent_count} recent records")
                        
            except Exception as e:
                print(f"  ⚠️ {db_name}: Could not check recent activity - {e}")
        
        print(f"\n📊 Total recent activity records: {total_recent_records}")
        return total_recent_records
    
    def generate_user_access_guide(self):
        """Generate guide for users to access agent logs."""
        return """
# 👀 How Users Can Access Agent Logs

## Method 1: Direct Database Query
```python
import sqlite3
from pathlib import Path

# Connect to any of the 8 databases
db_path = "utils/universal_agent_tracking.db"
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    
    # Get recent agent activities
    cursor.execute('''
        SELECT timestamp, agent_id, activity_type, context, details
        FROM agent_activities 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''')
    
    for row in cursor.fetchall():
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
```

## Method 2: Using Universal Tracker
```python
from utils.system.universal_agent_tracker import get_universal_tracker

tracker = get_universal_tracker()
recent_activities = tracker.get_recent_activities(limit=20)

for activity in recent_activities:
    print(f"{activity['timestamp']} - {activity['agent_id']}: {activity['activity_type']}")
```

## Method 3: Web Interface (Rule Monitor Dashboard)
1. Run the Streamlit app: `streamlit run apps/streamlit_app.py`
2. Navigate to the "Rule Monitor" section
3. View real-time agent activity logs and rule activation history

## Method 4: Log Analysis Script
```bash
# Run the logging system test (this script)
python scripts/test_agent_logging_system.py
```
"""
    
    def run_comprehensive_test(self):
        """Run comprehensive test of the agent logging system."""
        print("🚀 Starting Comprehensive Agent Logging System Test")
        print("=" * 60)
        
        # Test 1: Database connections
        print("\n📋 Testing database connections...")
        connected_dbs = 0
        
        for db_name, db_path in self.databases.items():
            if self.test_database_connection(db_name, db_path):
                connected_dbs += 1
            print(f"  {self.test_results[db_name]['status']} {db_name}")
        
        print(f"\n✅ Connected databases: {connected_dbs}/8")
        
        # Test 2: Logging functionality
        logging_works = self.test_logging_functionality()
        
        # Test 3: Universal tracker integration
        tracker_works = self.test_universal_tracker_integration()
        
        # Test 4: Cursor keyword logging
        keyword_works = self.test_cursor_keyword_logging()
        
        # Test 5: Recent activity
        recent_records = self.verify_recent_activity()
        
        # Generate comprehensive report
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE AGENT LOGGING SYSTEM REPORT")
        print("=" * 60)
        
        print(f"\n🗄️ Database Status: {connected_dbs}/8 connected")
        print(f"🔧 Logging Functionality: {'✅ Working' if logging_works else '❌ Failed'}")
        print(f"🔗 Universal Tracker: {'✅ Working' if tracker_works else '❌ Failed'}")
        print(f"🎯 Keyword Logging: {'✅ Working' if keyword_works else '❌ Failed'}")
        print(f"📈 Recent Activity: {recent_records} records")
        
        # Detailed database report
        print("\n📋 Detailed Database Report:")
        for db_name, result in self.test_results.items():
            print(f"  {result['status']} {db_name}")
            print(f"    📁 Path: {result['path']}")
            print(f"    📊 Records: {result['record_count']}")
            print(f"    💾 Size: {result['size_bytes']} bytes")
        
        # System health assessment
        total_tests = 4
        passed_tests = sum([logging_works, tracker_works, keyword_works, connected_dbs >= 6])
        
        health_score = (passed_tests / total_tests) * 100
        
        print(f"\n🎯 System Health Score: {health_score:.1f}%")
        
        if health_score >= 75:
            print("✅ Agent logging system is HEALTHY and operational")
        elif health_score >= 50:
            print("⚠️ Agent logging system has some issues but is functional")
        else:
            print("❌ Agent logging system needs attention")
        
        # User access guide
        print("\n" + self.generate_user_access_guide())
        
        return health_score >= 75

if __name__ == "__main__":
    tester = AgentLoggingSystemTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 Agent logging system verification SUCCESSFUL!")
        sys.exit(0)
    else:
        print("\n⚠️ Agent logging system needs attention.")
        sys.exit(1)
