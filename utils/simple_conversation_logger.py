#!/usr/bin/env python3
"""
Simple Conversation Logger
=========================

ONE FUNCTION. ONE PURPOSE. NO COMPLEXITY.
Logs conversation messages with keywords directly to database.

USAGE:
    log_message("@agile your message here")
"""

import sqlite3
import uuid
import json
from datetime import datetime
from typing import Dict, List

def log_message(message: str) -> bool:
    """
    Log a conversation message with keyword detection.
    
    Args:
        message: The message to log
        
    Returns:
        True if logged successfully, False otherwise
    """
    if not message.strip():
        return False
    
    # Simple keyword detection
    keywords = []
    keyword_map = {
        "@agile": "AGILE",
        "@test": "TESTING", 
        "@code": "CODING",
        "@debug": "DEBUGGING",
        "@docs": "DOCUMENTATION",
        "@research": "RESEARCH",
        "@analyze": "ANALYSIS"
    }
    
    message_lower = message.lower()
    for keyword, context in keyword_map.items():
        if keyword in message_lower:
            keywords.append((keyword, context))
    
    if not keywords:
        print(f"📝 No keywords found in: {message[:50]}...")
        return False
    
    # Log to database
    try:
        conn = sqlite3.connect('utils/universal_agent_tracking.db')
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_switches (
                switch_id TEXT PRIMARY KEY,
                session_id TEXT,
                from_context TEXT,
                to_context TEXT,
                timestamp TEXT,
                trigger_type TEXT,
                trigger_details TEXT
            )
        ''')
        
        timestamp = datetime.now().isoformat()
        session_id = str(uuid.uuid4())
        
        # Log each keyword
        for keyword, context in keywords:
            switch_id = str(uuid.uuid4())
            
            cursor.execute('''
                INSERT INTO context_switches 
                (switch_id, session_id, from_context, to_context, timestamp, trigger_type, trigger_details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                switch_id,
                session_id,
                "DEFAULT",
                context,
                timestamp,
                "conversation_direct",
                json.dumps({
                    "keyword": keyword,
                    "message": message[:100],
                    "method": "simple_direct"
                })
            ))
            
            print(f"✅ LOGGED: {keyword} → {context}")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def log_todays_messages():
    """Log all your messages from today's conversation."""
    
    messages = [
        "@agile test message",
        "@agile we want real agent logging also for the cursor keywords....look in our user story and reopen it....",
        "@agile the monitor is showing still old data implement the real cursor conversation integration but have a look and analyze what we already have first.",
        "@agile can we implement this for every conversation? till now we have no monitoring only fake....",
        "@agile the messages are doubled....strange...how do you log in cursor or do you inject into the database using a script?",
        "@agile solve the root problem first. go for a simple but working solution and delete all the other mess."
    ]
    
    print("🚀 Logging today's conversation...")
    for i, msg in enumerate(messages, 1):
        print(f"\n{i}. Processing: {msg[:50]}...")
        log_message(msg)
    
    print("\n✅ All messages processed!")

def show_todays_data():
    """Show what's actually in the database for today."""
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect('utils/universal_agent_tracking.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, to_context, trigger_details 
            FROM context_switches 
            WHERE timestamp LIKE ? 
            ORDER BY timestamp DESC
        ''', (f"{today}%",))
        
        rows = cursor.fetchall()
        conn.close()
        
        print(f"📊 Today's logged data ({len(rows)} entries):")
        for i, (ts, context, details) in enumerate(rows[:10], 1):
            time_only = ts.split('T')[1][:8]
            try:
                detail_dict = json.loads(details)
                keyword = detail_dict.get('keyword', 'unknown')
            except:
                keyword = 'unknown'
            
            print(f"  {i}. {time_only} | {keyword} → {context}")
        
        return len(rows)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

if __name__ == "__main__":
    print("🧪 Simple Conversation Logger Test")
    
    # Test single message
    test_result = log_message("@agile test the simple logger")
    print(f"Test result: {test_result}")
    
    # Show current data
    count = show_todays_data()
    
    if count == 0:
        print("\n💡 No data found. Run log_todays_messages() to populate with your conversation!")
    else:
        print(f"\n✅ Found {count} logged entries!")

