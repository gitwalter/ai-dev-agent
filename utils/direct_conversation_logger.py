#!/usr/bin/env python3
"""
Direct Conversation Logger
==========================

Simple, direct injection of conversation messages into the database
without multiple layers that cause doubling.

PHILOSOPHY: One function, one database write, no duplication.
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Any
import json
import re

def log_conversation_message_direct(message: str) -> Dict[str, Any]:
    """
    Directly log a conversation message to the database.
    
    This is the ONLY function that should write conversation data.
    No middleware, no doubling, just clean database injection.
    """
    
    if not message or not message.strip():
        return {"logged": False, "reason": "empty_message"}
    
    # Clean the message
    clean_message = message.strip()
    timestamp = datetime.now().isoformat()
    session_id = str(uuid.uuid4())
    
    # Detect keywords
    keywords = detect_keywords_simple(clean_message)
    
    result = {
        "logged": False,
        "message": clean_message,
        "timestamp": timestamp,
        "session_id": session_id,
        "keywords_found": keywords,
        "database_entries": []
    }
    
    try:
        # Connect to database
        conn = sqlite3.connect('utils/universal_agent_tracking.db')
        cursor = conn.cursor()
        
        # For each keyword found, create ONE context switch entry
        for keyword_data in keywords:
            keyword = keyword_data["keyword"]
            context = keyword_data["context"]
            
            # Create unique switch_id
            switch_id = str(uuid.uuid4())
            
            # Insert into context_switches table
            cursor.execute("""
                INSERT INTO context_switches 
                (switch_id, session_id, from_context, to_context, timestamp, trigger_type, trigger_details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                switch_id,
                session_id,
                "DEFAULT",  # from_context
                context,    # to_context  
                timestamp,
                "cursor_conversation_direct",
                json.dumps({
                    "keyword": keyword,
                    "message_snippet": clean_message[:100],
                    "method": "direct_injection",
                    "source": "real_cursor_conversation"
                })
            ))
            
            result["database_entries"].append({
                "table": "context_switches",
                "switch_id": switch_id,
                "keyword": keyword,
                "context": context
            })
            
            print(f"✅ LOGGED: {keyword} → {context} (Direct injection)")
        
        # Commit all changes at once
        conn.commit()
        conn.close()
        
        result["logged"] = True
        result["entries_created"] = len(keywords)
        
        return result
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        result["error"] = str(e)
        return result

def detect_keywords_simple(message: str) -> List[Dict[str, str]]:
    """Simple keyword detection without complex systems."""
    
    # Define keywords and their contexts
    keyword_map = {
        "@agile": "AGILE",
        "@test": "TESTING", 
        "@code": "CODING",
        "@debug": "DEBUGGING",
        "@docs": "DOCUMENTATION",
        "@research": "RESEARCH",
        "@analyze": "ANALYSIS",
        "@optimize": "OPTIMIZATION",
        "@security": "SECURITY",
        "@deploy": "DEPLOYMENT"
    }
    
    found_keywords = []
    message_lower = message.lower()
    
    for keyword, context in keyword_map.items():
        if keyword in message_lower:
            found_keywords.append({
                "keyword": keyword,
                "context": context
            })
    
    return found_keywords

def log_todays_conversation(messages: List[str]) -> Dict[str, Any]:
    """Log a list of today's conversation messages."""
    
    results = []
    total_keywords = 0
    
    print(f"🚀 Logging {len(messages)} conversation messages directly to database...")
    
    for i, message in enumerate(messages, 1):
        print(f"\n📝 Message {i}: {message[:50]}...")
        result = log_conversation_message_direct(message)
        results.append(result)
        
        if result["logged"]:
            keywords_count = len(result["keywords_found"])
            total_keywords += keywords_count
            print(f"  ✅ Logged {keywords_count} keywords")
        else:
            print(f"  ❌ Failed: {result.get('reason', 'unknown')}")
    
    summary = {
        "messages_processed": len(messages),
        "messages_logged": sum(1 for r in results if r["logged"]),
        "total_keywords": total_keywords,
        "results": results
    }
    
    print(f"\n📊 SUMMARY:")
    print(f"  Messages processed: {summary['messages_processed']}")
    print(f"  Messages logged: {summary['messages_logged']}")
    print(f"  Keywords logged: {summary['total_keywords']}")
    
    return summary

def verify_todays_data() -> Dict[str, Any]:
    """Verify what data exists in the database for today."""
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        conn = sqlite3.connect('utils/universal_agent_tracking.db')
        cursor = conn.cursor()
        
        # Check context switches for today
        cursor.execute("""
            SELECT timestamp, to_context, trigger_details 
            FROM context_switches 
            WHERE timestamp LIKE ? 
            ORDER BY timestamp DESC
        """, (f"{today}%",))
        
        switches = cursor.fetchall()
        conn.close()
        
        print(f"📊 Database verification for {today}:")
        print(f"  Context switches found: {len(switches)}")
        
        # Show recent entries
        for i, (ts, context, details) in enumerate(switches[:5]):
            time_part = ts.split('T')[1][:8]  # Get HH:MM:SS
            try:
                detail_dict = json.loads(details)
                keyword = detail_dict.get('keyword', 'unknown')
                method = detail_dict.get('method', 'unknown')
            except:
                keyword = 'parse_error'
                method = 'unknown'
            
            print(f"  {i+1}. {time_part} | {keyword} → {context} ({method})")
        
        return {
            "date": today,
            "context_switches": len(switches),
            "recent_switches": switches[:10]
        }
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("🧪 Testing Direct Conversation Logger...")
    
    # Test with your actual messages from today
    todays_messages = [
        "@agile test message",
        "@agile we want real agent logging also for the cursor keywords....look in our user story and reopen it....",
        "@agile the monitor is showing still old data implement the real cursor conversation integration but have a look and analyze what we already have first.",
        "@agile can we implement this for every conversation? till now we have no monitoring only fake....",
        "@agile the messages are doubled....strange...how do you log in cursor or do you inject into the database using a script?"
    ]
    
    # Clear any previous data first? (optional)
    # log_todays_conversation(todays_messages)
    
    # Verify current state
    verify_todays_data()
    
    print("\n✅ Use log_conversation_message_direct(message) for single messages")
    print("✅ Use log_todays_conversation(messages) for batch logging")

