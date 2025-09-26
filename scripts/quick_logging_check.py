#!/usr/bin/env python3
"""Quick check of existing agent logging system."""

import sqlite3
import sys
from pathlib import Path

# Check universal agent tracking database
db_path = "utils/universal_agent_tracking.db"

if Path(db_path).exists():
    print(f"✅ Database exists: {db_path}")
    print(f"📁 Size: {Path(db_path).stat().st_size} bytes")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"🗄️ Tables: {[t[0] for t in tables]}")
            
            # Check each table
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  📊 {table_name}: {count} records")
                
                # Show recent records if any
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 3")
                    recent = cursor.fetchall()
                    print(f"  🔍 Recent records: {len(recent)} shown")
                    for record in recent:
                        print(f"    {record}")
                        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        
else:
    print(f"❌ Database not found: {db_path}")

print("\nChecking other databases...")
db_names = [
    "analytics.db", "backup_tracking.db", "learning_experiences.db",
    "optimization.db", "rule_optimization.db", "security_events.db",
    "strategic_selection.db"
]

for db_name in db_names:
    db_path = f"utils/{db_name}"
    if Path(db_path).exists():
        size = Path(db_path).stat().st_size
        print(f"✅ {db_name}: {size} bytes")
    else:
        print(f"❌ {db_name}: Not found")
