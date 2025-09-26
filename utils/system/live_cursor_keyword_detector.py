#!/usr/bin/env python3
"""
Live Cursor Keyword Detector
===========================

Detects keywords like @agile, @docs, @research in real-time Cursor conversations
and triggers actual context switches and rule activations.
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LiveCursorKeywordDetector:
    """Detect and process keywords from live Cursor conversations."""
    
    def __init__(self):
        """Initialize the live keyword detector."""
        self.keywords_map = {
            '@agile': {
                'context': 'AGILE',
                'agent_type': 'ScrumMasterAgent',
                'rules': [
                    'agile_coordination',
                    'sprint_management',
                    'user_story_development',
                    'agile_ceremonies',
                    'team_collaboration'
                ],
                'description': 'Agile development methodology and project management'
            },
            '@docs': {
                'context': 'DOCUMENTATION',
                'agent_type': 'TechnicalWriterAgent',
                'rules': [
                    'clear_documentation',
                    'api_documentation',
                    'live_documentation_updates',
                    'technical_writing_standards',
                    'knowledge_management'
                ],
                'description': 'Documentation creation and maintenance'
            },
            '@research': {
                'context': 'RESEARCH',
                'agent_type': 'ResearchAgent',
                'rules': [
                    'systematic_research',
                    'evidence_based_development',
                    'technology_evaluation',
                    'best_practices_research',
                    'innovation_exploration'
                ],
                'description': 'Research and investigation tasks'
            },
            '@debug': {
                'context': 'DEBUGGING',
                'agent_type': 'DebuggingAgent',
                'rules': [
                    'systematic_debugging',
                    'error_analysis',
                    'root_cause_analysis',
                    'debugging_methodology',
                    'problem_resolution'
                ],
                'description': 'Debugging and problem-solving'
            },
            '@test': {
                'context': 'TESTING',
                'agent_type': 'QAAgent',
                'rules': [
                    'test_driven_development',
                    'comprehensive_testing',
                    'test_automation',
                    'quality_assurance',
                    'regression_testing'
                ],
                'description': 'Testing and quality assurance'
            },
            '@code': {
                'context': 'CODING',
                'agent_type': 'DeveloperAgent',
                'rules': [
                    'development_excellence',
                    'clean_code_principles',
                    'code_quality_standards',
                    'best_practices',
                    'software_craftsmanship'
                ],
                'description': 'Code development and implementation'
            }
        }
        
        # Track context switches
        self.current_context = "SYSTEM_STARTUP"
        self.context_history = []
        self.session_id = str(uuid.uuid4())
        
    def detect_and_process_keywords(self, message: str) -> List[Dict[str, Any]]:
        """
        Detect keywords in a message and process context switches.
        
        Args:
            message: The message to scan for keywords
            
        Returns:
            List of processed keyword events
        """
        detected_events = []
        
        # Check for each keyword
        for keyword, config in self.keywords_map.items():
            if keyword.lower() in message.lower():
                event = self._process_keyword_detection(keyword, config, message)
                detected_events.append(event)
                
                # Log to database
                self._log_to_database(event)
                
                print(f"🎯 DETECTED: {keyword} → {config['context']} context with {len(config['rules'])} rules")
        
        return detected_events
    
    def _process_keyword_detection(self, keyword: str, config: Dict, message: str) -> Dict[str, Any]:
        """Process a detected keyword and create context switch."""
        timestamp = datetime.now().isoformat()
        
        # Create context switch event
        event = {
            'keyword': keyword,
            'previous_context': self.current_context,
            'new_context': config['context'],
            'agent_type': config['agent_type'],
            'rules_activated': config['rules'],
            'rules_count': len(config['rules']),
            'timestamp': timestamp,
            'session_id': self.session_id,
            'switch_id': str(uuid.uuid4()),
            'activation_id': str(uuid.uuid4()),
            'message_context': message[:200] + "..." if len(message) > 200 else message,
            'description': config['description']
        }
        
        # Update current context
        self.current_context = config['context']
        self.context_history.append(event)
        
        return event
    
    def _log_to_database(self, event: Dict[str, Any]):
        """Log the event to the universal agent tracking database."""
        try:
            import sqlite3
            
            with sqlite3.connect("utils/universal_agent_tracking.db") as conn:
                cursor = conn.cursor()
                
                # 1. Log to context_switches
                cursor.execute("""
                    INSERT INTO context_switches 
                    (switch_id, session_id, from_context, to_context, timestamp, trigger_type, trigger_details)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event['switch_id'],
                    event['session_id'],
                    event['previous_context'],
                    event['new_context'],
                    event['timestamp'],
                    "cursor_keyword_detection",
                    json.dumps({
                        'keyword': event['keyword'],
                        'agent_type': event['agent_type'],
                        'message_context': event['message_context']
                    })
                ))
                
                # 2. Log to rule_activations (adapt to existing schema)
                cursor.execute("PRAGMA table_info(rule_activations)")
                rule_columns = [col[1] for col in cursor.fetchall()]
                
                if 'activation_id' in rule_columns:
                    # Use expected schema
                    cursor.execute("""
                        INSERT INTO rule_activations 
                        (activation_id, session_id, rules_activated, trigger_event, trigger_details, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        event['activation_id'],
                        event['session_id'],
                        json.dumps(event['rules_activated']),
                        "keyword_detection",
                        json.dumps({
                            'keyword': event['keyword'],
                            'context': event['new_context'],
                            'agent_type': event['agent_type']
                        }),
                        event['timestamp']
                    ))
                else:
                    # Adapt to actual schema
                    try:
                        cursor.execute("""
                            INSERT INTO rule_activations 
                            (session_id, rules_activated, trigger_event, trigger_details, timestamp)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            event['session_id'],
                            json.dumps(event['rules_activated']),
                            "keyword_detection",
                            json.dumps({
                                'keyword': event['keyword'],
                                'context': event['new_context'],
                                'agent_type': event['agent_type']
                            }),
                            event['timestamp']
                        ))
                    except sqlite3.Error:
                        # If even that fails, try minimal insert
                        cursor.execute("""
                            INSERT INTO rule_activations (timestamp) VALUES (?)
                        """, (event['timestamp'],))
                
                # 3. Log to agent_events
                try:
                    cursor.execute("""
                        INSERT INTO agent_events 
                        (event_id, timestamp, event_type, agent_id, agent_type, context, details)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(uuid.uuid4()),
                        event['timestamp'],
                        "keyword_detection",
                        "cursor_live_detector",
                        event['agent_type'],
                        event['new_context'],
                        json.dumps(event)
                    ))
                except sqlite3.Error:
                    # Minimal agent event logging
                    pass
                
                # 4. Update agent_sessions
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO agent_sessions 
                        (session_id, agent_id, agent_type, timestamp, context, agent_name, status, start_time, last_activity)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        event['session_id'],
                        "live_cursor_detector",
                        event['agent_type'],
                        event['timestamp'],
                        event['new_context'],
                        f"Live_{event['agent_type']}",
                        "active",
                        event['timestamp'],
                        event['timestamp']
                    ))
                except sqlite3.Error:
                    pass
                
                conn.commit()
                print(f"✅ Logged {event['keyword']} to database successfully")
                
        except Exception as e:
            print(f"❌ Database logging failed: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current detection status."""
        return {
            'current_context': self.current_context,
            'session_id': self.session_id,
            'total_switches': len(self.context_history),
            'recent_keywords': [event['keyword'] for event in self.context_history[-5:]],
            'available_keywords': list(self.keywords_map.keys())
        }
    
    def process_live_message(self, message: str) -> Dict[str, Any]:
        """
        Process a live message for keyword detection.
        
        This is the main method to call when processing user messages.
        """
        print(f"🔍 SCANNING MESSAGE: {message[:100]}...")
        
        detected = self.detect_and_process_keywords(message)
        
        if detected:
            print(f"🎯 PROCESSED {len(detected)} KEYWORD(S)")
            for event in detected:
                print(f"  • {event['keyword']} → {event['new_context']} ({event['rules_count']} rules)")
        else:
            print("  No keywords detected")
        
        return {
            'detected_keywords': detected,
            'current_context': self.current_context,
            'session_id': self.session_id
        }

# Global detector instance
_global_detector = None

def get_live_keyword_detector() -> LiveCursorKeywordDetector:
    """Get or create the global live keyword detector."""
    global _global_detector
    
    if _global_detector is None:
        _global_detector = LiveCursorKeywordDetector()
        print("🎯 Live Cursor Keyword Detector initialized")
    
    return _global_detector

def process_cursor_message(message: str) -> Dict[str, Any]:
    """
    Convenience function to process a Cursor message for keywords.
    
    Args:
        message: The message content
        
    Returns:
        Detection results
    """
    detector = get_live_keyword_detector()
    return detector.process_live_message(message)

if __name__ == "__main__":
    # Test the detector
    detector = LiveCursorKeywordDetector()
    
    # Test messages
    test_messages = [
        "@agile let's start working on user stories",
        "@docs we need to update the documentation",
        "@research investigate the best practices for this",
        "@debug there's an issue with the logging system",
        "@test let's write comprehensive tests"
    ]
    
    print("🧪 TESTING LIVE KEYWORD DETECTOR")
    print("=" * 40)
    
    for message in test_messages:
        result = detector.process_live_message(message)
        print()
    
    print(f"\n📊 FINAL STATUS:")
    status = detector.get_current_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

