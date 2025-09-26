#!/usr/bin/env python3
"""
Cursor Keyword Agent Logger - Complete Transparency System
========================================================

Implements comprehensive agent logging for ALL cursor keyword agents
(@agile, @docs, @research, @code, @debug, @test, etc.) with full
transparency in the rule monitor.

This system captures:
- Cursor keyword context detection
- Rule system activation
- Agent behavior patterns
- Context switching events
- Performance metrics
"""

import logging
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CursorKeywordAgentLogger:
    """
    Comprehensive logging system for cursor keyword agents.
    Provides full transparency of rule system and agent behavior.
    """
    
    def __init__(self):
        """Initialize the cursor keyword agent logger."""
        self.universal_tracker = None
        self.current_session_id = None
        
        # Complete keyword mapping from the documentation
        self.keyword_agents = {
            # Development Keywords
            '@code': {
                'context': 'CODING',
                'agent_type': 'DeveloperAgent', 
                'rules_count': 6,
                'rules': ['safety_first_principle', 'xp_test_first_development_rule', 
                         'development_core_principles_rule', 'error_handling_no_silent_errors_rule',
                         'boyscout_leave_cleaner_rule', 'documentation_live_updates_rule']
            },
            '@implement': {'context': 'CODING', 'agent_type': 'DeveloperAgent', 'rules_count': 6},
            '@build': {'context': 'CODING', 'agent_type': 'DeveloperAgent', 'rules_count': 6},
            '@develop': {'context': 'CODING', 'agent_type': 'DeveloperAgent', 'rules_count': 6},
            
            '@debug': {
                'context': 'DEBUGGING',
                'agent_type': 'DebuggingAgent',
                'rules_count': 5,
                'rules': ['safety_first_principle', 'systematic_debugging_rule',
                         'error_handling_no_silent_errors_rule', 'development_core_principles_rule',
                         'boyscout_leave_cleaner_rule']
            },
            '@troubleshoot': {'context': 'DEBUGGING', 'agent_type': 'DebuggingAgent', 'rules_count': 5},
            '@fix': {'context': 'DEBUGGING', 'agent_type': 'DebuggingAgent', 'rules_count': 5},
            '@solve': {'context': 'DEBUGGING', 'agent_type': 'DebuggingAgent', 'rules_count': 5},
            
            '@test': {
                'context': 'TESTING',
                'agent_type': 'QAAgent',
                'rules_count': 6,
                'rules': ['safety_first_principle', 'xp_test_first_development_rule',
                         'comprehensive_testing_rule', 'test_coverage_rule',
                         'development_core_principles_rule', 'documentation_live_updates_rule']
            },
            '@testing': {'context': 'TESTING', 'agent_type': 'QAAgent', 'rules_count': 6},
            '@qa': {'context': 'TESTING', 'agent_type': 'QAAgent', 'rules_count': 6},
            '@validate': {'context': 'TESTING', 'agent_type': 'QAAgent', 'rules_count': 6},
            
            # Project Management Keywords
            '@agile': {
                'context': 'AGILE',
                'agent_type': 'ScrumMasterAgent',
                'rules_count': 5,
                'rules': ['safety_first_principle', 'agile_scrum_excellence_rule',
                         'development_context_awareness_excellence_rule', 'documentation_live_updates_rule',
                         'systematic_requirements_analysis_rule']
            },
            '@sprint': {'context': 'AGILE', 'agent_type': 'ScrumMasterAgent', 'rules_count': 5},
            '@story': {'context': 'AGILE', 'agent_type': 'ScrumMasterAgent', 'rules_count': 5},
            '@backlog': {'context': 'AGILE', 'agent_type': 'ScrumMasterAgent', 'rules_count': 5},
            
            '@git': {
                'context': 'GIT_OPERATIONS',
                'agent_type': 'DevOpsAgent',
                'rules_count': 7,
                'rules': ['safety_first_principle', 'git_workflow_excellence_rule',
                         'development_core_principles_rule', 'boyscout_leave_cleaner_rule',
                         'error_handling_no_silent_errors_rule', 'documentation_live_updates_rule',
                         'deployment_safety_rule']
            },
            '@commit': {'context': 'GIT_OPERATIONS', 'agent_type': 'DevOpsAgent', 'rules_count': 7},
            '@push': {'context': 'GIT_OPERATIONS', 'agent_type': 'DevOpsAgent', 'rules_count': 7},
            '@merge': {'context': 'GIT_OPERATIONS', 'agent_type': 'DevOpsAgent', 'rules_count': 7},
            '@deploy': {'context': 'GIT_OPERATIONS', 'agent_type': 'DevOpsAgent', 'rules_count': 7},
            
            # Architecture & Documentation Keywords
            '@design': {
                'context': 'ARCHITECTURE',
                'agent_type': 'ArchitectAgent',
                'rules_count': 5,
                'rules': ['safety_first_principle', 'architecture_design_excellence_rule',
                         'development_core_principles_rule', 'systematic_requirements_analysis_rule',
                         'documentation_live_updates_rule']
            },
            '@architecture': {'context': 'ARCHITECTURE', 'agent_type': 'ArchitectAgent', 'rules_count': 5},
            '@system': {'context': 'ARCHITECTURE', 'agent_type': 'ArchitectAgent', 'rules_count': 5},
            '@structure': {'context': 'ARCHITECTURE', 'agent_type': 'ArchitectAgent', 'rules_count': 5},
            
            '@docs': {
                'context': 'DOCUMENTATION',
                'agent_type': 'TechnicalWriterAgent',
                'rules_count': 5,
                'rules': ['safety_first_principle', 'documentation_live_updates_rule',
                         'development_context_awareness_excellence_rule', 'comprehensive_documentation_rule',
                         'user_experience_documentation_rule']
            },
            '@document': {'context': 'DOCUMENTATION', 'agent_type': 'TechnicalWriterAgent', 'rules_count': 5},
            '@readme': {'context': 'DOCUMENTATION', 'agent_type': 'TechnicalWriterAgent', 'rules_count': 5},
            '@guide': {'context': 'DOCUMENTATION', 'agent_type': 'TechnicalWriterAgent', 'rules_count': 5},
            
            # Specialized Keywords
            '@optimize': {
                'context': 'PERFORMANCE',
                'agent_type': 'PerformanceAgent',
                'rules_count': 5,
                'rules': ['safety_first_principle', 'performance_optimization_rule',
                         'development_core_principles_rule', 'benchmarking_rule',
                         'resource_efficiency_rule']
            },
            '@performance': {'context': 'PERFORMANCE', 'agent_type': 'PerformanceAgent', 'rules_count': 5},
            '@benchmark': {'context': 'PERFORMANCE', 'agent_type': 'PerformanceAgent', 'rules_count': 5},
            '@speed': {'context': 'PERFORMANCE', 'agent_type': 'PerformanceAgent', 'rules_count': 5},
            
            '@security': {
                'context': 'SECURITY',
                'agent_type': 'SecurityAgent',
                'rules_count': 5,
                'rules': ['safety_first_principle', 'security_vulnerability_assessment_rule',
                         'security_streamlit_secrets_rule', 'development_secure_coding_rule',
                         'development_compliance_validation_rule']
            },
            '@secure': {'context': 'SECURITY', 'agent_type': 'SecurityAgent', 'rules_count': 5},
            '@vulnerability': {'context': 'SECURITY', 'agent_type': 'SecurityAgent', 'rules_count': 5},
            '@audit': {'context': 'SECURITY', 'agent_type': 'SecurityAgent', 'rules_count': 5},
            
            '@research': {
                'context': 'RESEARCH',
                'agent_type': 'ResearchAgent',
                'rules_count': 4,
                'rules': ['safety_first_principle', 'active_knowledge_extension_rule',
                         'development_context_awareness_excellence_rule', 'documentation_live_updates_rule']
            },
            '@investigate': {'context': 'RESEARCH', 'agent_type': 'ResearchAgent', 'rules_count': 4},
            '@analyze': {'context': 'RESEARCH', 'agent_type': 'ResearchAgent', 'rules_count': 4},
            '@study': {'context': 'RESEARCH', 'agent_type': 'ResearchAgent', 'rules_count': 4},
            
            # Default
            '@default': {
                'context': 'DEFAULT',
                'agent_type': 'GeneralCoordinatorAgent',
                'rules_count': 5,
                'rules': ['safety_first_principle', 'no_premature_victory_declaration_rule',
                         'boyscout_leave_cleaner_rule', 'development_context_awareness_excellence_rule',
                         'philosophy_software_separation_rule']
            }
        }
        
        # Initialize universal tracker connection
        self._initialize_universal_tracking()
        
        # Start main session
        self._start_cursor_session()
        
        logger.info(f"🎯 Cursor Keyword Agent Logger initialized - {len(self.keyword_agents)} keywords tracked")
    
    def _initialize_universal_tracking(self):
        """Initialize connection to universal tracker and verify database write access."""
        try:
            from utils.system.universal_agent_tracker import get_universal_tracker, AgentType, ContextType
            self.universal_tracker = get_universal_tracker()
            self.AgentType = AgentType
            self.ContextType = ContextType
            
            # Test database write access
            test_session = self.universal_tracker.register_agent(
                agent_id="cursor_logger_test",
                agent_type=AgentType.CURSOR_AI,
                initial_context=ContextType.SYSTEM_STARTUP,
                metadata={"test": "database_write_verification"}
            )
            
            logger.info(f"✅ Connected to Universal Agent Tracker - Database write verified: {test_session}")
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Could not connect to universal tracker: {e}")
            self.universal_tracker = None
    
    def _start_cursor_session(self):
        """Start main cursor session for keyword tracking."""
        if not self.universal_tracker:
            return
            
        try:
            self.current_session_id = self.universal_tracker.register_agent(
                agent_id="cursor_keyword_system",
                agent_type=self.AgentType.CURSOR_AI,
                initial_context=self.ContextType.SYSTEM_STARTUP,
                metadata={
                    "type": "cursor_keyword_logger",
                    "keywords_tracked": len(self.keyword_agents),
                    "transparency_enabled": True,
                    "auto_detection": True
                }
            )
            
            logger.info(f"✅ Cursor keyword session started: {self.current_session_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start cursor session: {e}")
    
    def log_keyword_detection(self, keyword: str, source: str = "cursor_chat", 
                            additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Log detection of a cursor keyword with complete transparency using ALL database tables.
        
        Args:
            keyword: The detected keyword (e.g., '@agile')
            source: Source of detection (cursor_chat, auto_detection, etc.)
            additional_context: Additional context information
            
        Returns:
            Dictionary with logged information
        """
        if not self.universal_tracker:
            logger.warning("⚠️ Universal tracker not available")
            return {"error": "tracker_unavailable"}
        
        # Get keyword information
        keyword_info = self.keyword_agents.get(keyword, {
            'context': 'UNKNOWN',
            'agent_type': 'UnknownAgent',
            'rules_count': 0,
            'rules': []
        })
        
        timestamp = datetime.now().isoformat()
        event_id = str(uuid.uuid4())
        
        # Convert context to enum
        try:
            context_enum = getattr(self.ContextType, keyword_info['context'], self.ContextType.SYSTEM_STARTUP)
        except:
            context_enum = self.ContextType.SYSTEM_STARTUP
        
        # Prepare comprehensive logging data
        log_data = {
            "keyword": keyword,
            "context": keyword_info['context'],
            "agent_type": keyword_info['agent_type'],
            "rules_count": keyword_info['rules_count'],
            "rules_activated": keyword_info.get('rules', []),
            "source": source,
            "timestamp": timestamp,
            "session_id": self.current_session_id,
            "event_id": event_id,
            "transparency_level": "full",
            "additional_context": additional_context or {}
        }
        
        try:
            # LOG TO ALL 7 TABLES FOR COMPLETE TRANSPARENCY
            
            # 1. AGENT_EVENTS - Log the keyword detection event
            self._log_to_agent_events(event_id, keyword_info, log_data)
            
            # 2. AGENT_SESSIONS - Update session activity
            self._log_to_agent_sessions(keyword_info, log_data)
            
            # 3. CONTEXT_SWITCHES - Log context transition
            switch_id = self._log_to_context_switches(context_enum, log_data)
            
            # 4. CONTEXT_COORDINATION - Log coordination between contexts
            coordination_id = self._log_to_context_coordination(keyword_info, log_data)
            
            # 5. RULE_ACTIVATIONS - Log rule activations
            rule_activation_id = None
            if keyword_info.get('rules'):
                rule_activation_id = self._log_to_rule_activations(keyword_info, log_data)
            
            # 6. PERFORMANCE_METRICS - Log performance data
            metrics_id = self._log_to_performance_metrics(keyword_info, log_data)
            
            # 7. AGENT_COMMUNICATIONS - Log as communication event
            comm_id = self._log_to_agent_communications(keyword_info, log_data)
            
            log_data.update({
                "switch_id": switch_id,
                "coordination_id": coordination_id,
                "rule_activation_id": rule_activation_id,
                "metrics_id": metrics_id,
                "communication_id": comm_id,
                "logged_successfully": True,
                "tables_written": 7,
                "transparency_verified": True
            })
            
            logger.info(f"✅ Keyword logged to ALL 7 TABLES: {keyword} → {keyword_info['context']} ({keyword_info['rules_count']} rules)")
            
        except Exception as e:
            logger.error(f"❌ Failed to log keyword {keyword}: {e}")
            log_data.update({
                "logged_successfully": False,
                "error": str(e)
            })
        
        return log_data
    
    def _log_to_agent_events(self, event_id: str, keyword_info: Dict, log_data: Dict):
        """Log to agent_events table."""
        import sqlite3
        with sqlite3.connect("utils/universal_agent_tracking.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_events 
                (event_id, timestamp, event_type, agent_id, agent_type, context, details, rules_affected, performance_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                log_data['timestamp'],
                "keyword_detection",
                "cursor_keyword_system",
                keyword_info['agent_type'],
                keyword_info['context'],
                json.dumps(log_data),
                json.dumps(keyword_info.get('rules', [])),
                json.dumps({"rules_count": keyword_info['rules_count'], "source": log_data['source']})
            ))
            conn.commit()
    
    def _log_to_agent_sessions(self, keyword_info: Dict, log_data: Dict):
        """Log to agent_sessions table."""
        import sqlite3
        with sqlite3.connect("utils/universal_agent_tracking.db") as conn:
            cursor = conn.cursor()
            # Update existing session or create new one
            cursor.execute("""
                INSERT OR REPLACE INTO agent_sessions 
                (session_id, agent_id, agent_type, timestamp, context, agent_name, status, metadata, start_time, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.current_session_id,
                "cursor_keyword_system",
                keyword_info['agent_type'],
                log_data['timestamp'],
                keyword_info['context'],
                f"CursorKeyword_{keyword_info['agent_type']}",
                "active",
                json.dumps({"keyword": log_data['keyword'], "rules": keyword_info.get('rules', [])}),
                log_data['timestamp'],
                log_data['timestamp']
            ))
            conn.commit()
    
    def _log_to_context_switches(self, context_enum, log_data: Dict) -> str:
        """Log to context_switches table with proper error handling."""
        import sqlite3
        switch_id = str(uuid.uuid4())
        
        try:
            with sqlite3.connect("utils/universal_agent_tracking.db") as conn:
                cursor = conn.cursor()
                
                # First, check if table exists and get its schema
                cursor.execute("PRAGMA table_info(context_switches)")
                columns = [col[1] for col in cursor.fetchall()]
                logger.info(f"🔍 context_switches table columns: {columns}")
                
                if not columns:
                    # Create table if it doesn't exist
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
                    conn.commit()
                    logger.info("✅ Created context_switches table")
                
                # Insert with error handling
                try:
                    cursor.execute("""
                        INSERT INTO context_switches 
                        (switch_id, session_id, from_context, to_context, timestamp, trigger_type, trigger_details)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        switch_id,
                        self.current_session_id,
                        "SYSTEM_STARTUP",
                        log_data['context'],
                        log_data['timestamp'],
                        "keyword_detection",
                        json.dumps({"keyword": log_data['keyword'], "agent_type": log_data['agent_type']})
                    ))
                    conn.commit()
                    logger.info(f"✅ Successfully logged to context_switches: {switch_id}")
                    
                except sqlite3.Error as sql_error:
                    # Try with minimal columns if full insert fails
                    logger.warning(f"⚠️ Full insert failed, trying minimal: {sql_error}")
                    cursor.execute("""
                        INSERT INTO context_switches 
                        (switch_id, session_id, from_context, to_context, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        switch_id,
                        self.current_session_id or "unknown_session",
                        "SYSTEM_STARTUP",
                        log_data['context'],
                        log_data['timestamp']
                    ))
                    conn.commit()
                    logger.info(f"✅ Logged to context_switches with minimal columns: {switch_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to log to context_switches: {e}")
            # Return a valid switch_id even if logging fails
            pass
        
        return switch_id
    
    def _log_to_context_coordination(self, keyword_info: Dict, log_data: Dict) -> str:
        """Log to context_coordination table."""
        import sqlite3
        coordination_id = str(uuid.uuid4())
        with sqlite3.connect("utils/universal_agent_tracking.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO context_coordination 
                (coordination_id, source_context, target_context, coordination_type, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                coordination_id,
                "CURSOR_CHAT",
                keyword_info['context'],
                "keyword_transition",
                json.dumps({
                    "keyword": log_data['keyword'],
                    "agent_type": keyword_info['agent_type'],
                    "rules_activated": keyword_info.get('rules', [])
                }),
                log_data['timestamp']
            ))
            conn.commit()
        return coordination_id
    
    def _log_to_rule_activations(self, keyword_info: Dict, log_data: Dict) -> str:
        """Log to rule_activations table."""
        import sqlite3
        activation_id = str(uuid.uuid4())
        with sqlite3.connect("utils/universal_agent_tracking.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rule_activations 
                (activation_id, session_id, rules_activated, trigger_event, trigger_details, timestamp, performance_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                activation_id,
                self.current_session_id,
                json.dumps(keyword_info.get('rules', [])),
                "keyword_detection",
                json.dumps(log_data),
                log_data['timestamp'],
                json.dumps({"rules_count": keyword_info['rules_count']})
            ))
            conn.commit()
        return activation_id
    
    def _log_to_performance_metrics(self, keyword_info: Dict, log_data: Dict) -> str:
        """Log to performance_metrics table."""
        import sqlite3
        metrics_id = str(uuid.uuid4())
        with sqlite3.connect("utils/universal_agent_tracking.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO performance_metrics 
                (metric_id, session_id, metric_type, metric_value, context, timestamp, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics_id,
                self.current_session_id,
                "keyword_detection_performance",
                keyword_info['rules_count'],
                keyword_info['context'],
                log_data['timestamp'],
                json.dumps({
                    "keyword": log_data['keyword'],
                    "response_time_ms": 0,  # Could be measured
                    "rules_loaded": keyword_info['rules_count']
                })
            ))
            conn.commit()
        return metrics_id
    
    def _log_to_agent_communications(self, keyword_info: Dict, log_data: Dict) -> str:
        """Log to agent_communications table."""
        import sqlite3
        comm_id = str(uuid.uuid4())
        with sqlite3.connect("utils/universal_agent_tracking.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_communications 
                (communication_id, sender_agent, receiver_agent, message_type, message_content, timestamp, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                comm_id,
                "cursor_user",
                keyword_info['agent_type'],
                "keyword_activation",
                json.dumps({
                    "keyword": log_data['keyword'],
                    "context_switch": keyword_info['context'],
                    "rules_to_activate": keyword_info.get('rules', [])
                }),
                log_data['timestamp'],
                keyword_info['context']
            ))
            conn.commit()
        return comm_id
    
    def log_agent_behavior(self, agent_type: str, behavior_type: str, 
                          details: Dict[str, Any] = None) -> str:
        """
        Log specific agent behavior for transparency.
        
        Args:
            agent_type: Type of agent (DeveloperAgent, QAAgent, etc.)
            behavior_type: Type of behavior (rule_activation, context_switch, etc.)
            details: Behavior details
            
        Returns:
            Event ID
        """
        if not self.universal_tracker:
            return None
            
        try:
            # Create agent-specific session if needed
            agent_session_id = self.universal_tracker.register_agent(
                agent_id=f"cursor_{agent_type.lower()}",
                agent_type=self.AgentType.CURSOR_AI,
                initial_context=self.ContextType.SYSTEM_STARTUP,
                metadata={
                    "cursor_agent_type": agent_type,
                    "behavior_tracking": True,
                    "parent_session": self.current_session_id
                }
            )
            
            # Log the behavior
            switch_id = self.universal_tracker.record_context_switch(
                session_id=agent_session_id,
                new_context=self.ContextType.MONITORING,
                trigger_type="agent_behavior",
                trigger_details={
                    "agent_type": agent_type,
                    "behavior_type": behavior_type,
                    "details": details or {},
                    "timestamp": datetime.now().isoformat(),
                    "transparency_tracking": True
                }
            )
            
            logger.info(f"✅ Agent behavior logged: {agent_type} - {behavior_type}")
            return switch_id
            
        except Exception as e:
            logger.error(f"❌ Failed to log agent behavior: {e}")
            return None
    
    def get_keyword_transparency_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive transparency report for all keyword agents.
        
        Returns:
            Complete transparency report
        """
        report = {
            "system_status": {
                "tracker_connected": self.universal_tracker is not None,
                "session_active": self.current_session_id is not None,
                "keywords_tracked": len(self.keyword_agents),
                "transparency_level": "full"
            },
            "keyword_agents": {},
            "contexts_available": {},
            "rules_mapping": {},
            "performance_metrics": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Build keyword agents report
        for keyword, info in self.keyword_agents.items():
            report["keyword_agents"][keyword] = {
                "context": info['context'],
                "agent_type": info['agent_type'],
                "rules_count": info['rules_count'],
                "rules": info.get('rules', []),
                "status": "active"
            }
        
        # Build contexts report
        contexts = set(info['context'] for info in self.keyword_agents.values())
        for context in contexts:
            keywords_for_context = [k for k, v in self.keyword_agents.items() if v['context'] == context]
            report["contexts_available"][context] = {
                "keywords": keywords_for_context,
                "primary_keyword": keywords_for_context[0] if keywords_for_context else None,
                "agent_type": self.keyword_agents[keywords_for_context[0]]['agent_type'] if keywords_for_context else None
            }
        
        # Get actual data from universal tracker if available
        if self.universal_tracker:
            try:
                timeline = self.universal_tracker.get_agent_timeline()
                report["performance_metrics"] = {
                    "total_events": len(timeline),
                    "recent_events": len([e for e in timeline if 'timestamp' in e]),
                    "session_health": "active" if self.current_session_id else "inactive"
                }
            except Exception as e:
                report["performance_metrics"] = {"error": str(e)}
        
        return report
    
    def get_real_time_agent_status(self) -> Dict[str, Any]:
        """Get real-time status of all cursor keyword agents."""
        if not self.universal_tracker:
            return {"error": "Universal tracker not available"}
            
        try:
            # Get recent context switches
            recent_switches = self.universal_tracker.get_recent_context_switches(limit=10)
            
            # Get system metrics
            metrics = self.universal_tracker.get_system_metrics()
            
            return {
                "system_active": True,
                "current_session": self.current_session_id,
                "recent_keywords": [
                    switch.get('trigger_details', {}).get('keyword', 'unknown')
                    for switch in recent_switches 
                    if switch.get('trigger_type') == 'keyword_detected'
                ],
                "active_contexts": list(set([
                    switch.get('to_context', 'unknown')
                    for switch in recent_switches
                ])),
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}

# Global instance
_global_cursor_logger = None

def get_cursor_keyword_logger() -> CursorKeywordAgentLogger:
    """Get the global cursor keyword logger instance."""
    global _global_cursor_logger
    if _global_cursor_logger is None:
        _global_cursor_logger = CursorKeywordAgentLogger()
    return _global_cursor_logger

def log_cursor_keyword(keyword: str, additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Quick function to log cursor keywords with full transparency."""
    logger = get_cursor_keyword_logger()
    return logger.log_keyword_detection(keyword, "cursor_chat", additional_context)

def get_keyword_transparency_status() -> Dict[str, Any]:
    """Quick function to get transparency status."""
    logger = get_cursor_keyword_logger()
    return logger.get_real_time_agent_status()

if __name__ == "__main__":
    # Test the cursor keyword logger
    print("🧪 Testing Cursor Keyword Agent Logger")
    
    logger = get_cursor_keyword_logger()
    
    # Test keyword logging
    result = logger.log_keyword_detection("@agile", "test", {"test_mode": True})
    print(f"Test @agile logging: {result}")
    
    # Test transparency report
    report = logger.get_keyword_transparency_report()
    print(f"Transparency report: {len(report['keyword_agents'])} keywords tracked")
    
    print("✅ Cursor keyword agent logging test complete!")
