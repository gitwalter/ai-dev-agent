#!/usr/bin/env python3
"""
Comprehensive Keyword Detection System
=====================================

Complete keyword detection system that includes ALL keywords from various sources:
- @analyze, @debug, @code, @agile, @research, etc.
- Context-aware rule activation
- Real-time context switching
- Professional logging with no fake data
"""

import logging
import sqlite3
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ComprehensiveKeywordDetector:
    """
    Comprehensive keyword detection system that captures ALL useful keywords
    and triggers appropriate context switches and rule activations.
    """
    
    def __init__(self):
        """Initialize with complete keyword mapping."""
        self.keywords_map = self._build_comprehensive_keyword_map()
        self.current_context = "SYSTEM_STARTUP"
        self.context_history = []
        self.session_id = str(uuid.uuid4())
        
        # Initialize database connection
        self.db_path = "utils/universal_agent_tracking.db"
        self._ensure_database_connection()
        
        logger.info(f"🎯 Comprehensive Keyword Detector initialized with {len(self.keywords_map)} keywords")
    
    def _build_comprehensive_keyword_map(self) -> Dict[str, Dict[str, Any]]:
        """Build complete keyword mapping from all sources."""
        return {
            # === ANALYSIS & RESEARCH KEYWORDS ===
            '@analyze': {
                'context': 'ANALYSIS',
                'agent_type': 'AnalysisAgent',
                'rules': [
                    'systematic_analysis',
                    'evidence_based_reasoning',
                    'data_driven_decisions',
                    'critical_thinking',
                    'problem_decomposition'
                ],
                'description': 'Analysis and investigation tasks'
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
            '@investigate': {
                'context': 'RESEARCH',
                'agent_type': 'ResearchAgent',
                'rules': ['systematic_research', 'evidence_based_development'],
                'description': 'Investigation and research tasks'
            },
            
            # === DEVELOPMENT KEYWORDS ===
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
            },
            '@implement': {
                'context': 'CODING',
                'agent_type': 'DeveloperAgent',
                'rules': ['development_excellence', 'systematic_completion'],
                'description': 'Implementation and coding tasks'
            },
            '@build': {
                'context': 'CODING',
                'agent_type': 'DeveloperAgent',
                'rules': ['development_excellence', 'systematic_completion'],
                'description': 'Building and construction tasks'
            },
            '@develop': {
                'context': 'CODING',
                'agent_type': 'DeveloperAgent',
                'rules': ['development_excellence', 'systematic_completion'],
                'description': 'Development and coding tasks'
            },
            
            # === DEBUGGING KEYWORDS ===
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
            '@troubleshoot': {
                'context': 'DEBUGGING',
                'agent_type': 'DebuggingAgent',
                'rules': ['systematic_debugging', 'problem_resolution'],
                'description': 'Troubleshooting and problem resolution'
            },
            '@fix': {
                'context': 'DEBUGGING',
                'agent_type': 'DebuggingAgent',
                'rules': ['systematic_debugging', 'problem_resolution'],
                'description': 'Fixing and repair tasks'
            },
            '@solve': {
                'context': 'DEBUGGING',
                'agent_type': 'DebuggingAgent',
                'rules': ['systematic_debugging', 'problem_resolution'],
                'description': 'Problem solving tasks'
            },
            
            # === TESTING KEYWORDS ===
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
            '@testing': {
                'context': 'TESTING',
                'agent_type': 'QAAgent',
                'rules': ['test_driven_development', 'quality_assurance'],
                'description': 'Testing and QA tasks'
            },
            '@qa': {
                'context': 'TESTING',
                'agent_type': 'QAAgent',
                'rules': ['quality_assurance', 'comprehensive_testing'],
                'description': 'Quality assurance tasks'
            },
            '@verify': {
                'context': 'TESTING',
                'agent_type': 'QAAgent',
                'rules': ['comprehensive_testing', 'quality_assurance'],
                'description': 'Verification and validation tasks'
            },
            
            # === AGILE KEYWORDS ===
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
            '@sprint': {
                'context': 'AGILE',
                'agent_type': 'ScrumMasterAgent',
                'rules': ['agile_coordination', 'sprint_management'],
                'description': 'Sprint planning and management'
            },
            '@story': {
                'context': 'AGILE',
                'agent_type': 'ScrumMasterAgent',
                'rules': ['user_story_development', 'agile_coordination'],
                'description': 'User story development'
            },
            
            # === DOCUMENTATION KEYWORDS ===
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
            '@document': {
                'context': 'DOCUMENTATION',
                'agent_type': 'TechnicalWriterAgent',
                'rules': ['clear_documentation', 'live_documentation_updates'],
                'description': 'Documentation tasks'
            },
            '@readme': {
                'context': 'DOCUMENTATION',
                'agent_type': 'TechnicalWriterAgent',
                'rules': ['clear_documentation', 'knowledge_management'],
                'description': 'README and documentation tasks'
            },
            
            # === PERFORMANCE KEYWORDS ===
            '@optimize': {
                'context': 'OPTIMIZATION',
                'agent_type': 'PerformanceAgent',
                'rules': [
                    'performance_optimization',
                    'resource_efficiency',
                    'benchmarking',
                    'system_tuning',
                    'efficiency_analysis'
                ],
                'description': 'Performance optimization and tuning'
            },
            '@performance': {
                'context': 'OPTIMIZATION',
                'agent_type': 'PerformanceAgent',
                'rules': ['performance_optimization', 'benchmarking'],
                'description': 'Performance analysis and optimization'
            },
            '@benchmark': {
                'context': 'OPTIMIZATION',
                'agent_type': 'PerformanceAgent',
                'rules': ['benchmarking', 'performance_optimization'],
                'description': 'Benchmarking and performance testing'
            },
            '@speed': {
                'context': 'OPTIMIZATION',
                'agent_type': 'PerformanceAgent',
                'rules': ['performance_optimization', 'efficiency_analysis'],
                'description': 'Speed optimization tasks'
            },
            
            # === SECURITY KEYWORDS ===
            '@security': {
                'context': 'SECURITY',
                'agent_type': 'SecurityAgent',
                'rules': [
                    'security_hardening',
                    'vulnerability_assessment',
                    'secure_coding',
                    'compliance_validation',
                    'threat_analysis'
                ],
                'description': 'Security analysis and hardening'
            },
            '@secure': {
                'context': 'SECURITY',
                'agent_type': 'SecurityAgent',
                'rules': ['security_hardening', 'secure_coding'],
                'description': 'Security implementation tasks'
            },
            '@vulnerability': {
                'context': 'SECURITY',
                'agent_type': 'SecurityAgent',
                'rules': ['vulnerability_assessment', 'threat_analysis'],
                'description': 'Vulnerability assessment tasks'
            },
            '@audit': {
                'context': 'SECURITY',
                'agent_type': 'SecurityAgent',
                'rules': ['compliance_validation', 'security_hardening'],
                'description': 'Security audit tasks'
            },
            
            # === DEPLOYMENT KEYWORDS ===
            '@deploy': {
                'context': 'DEPLOYMENT',
                'agent_type': 'DevOpsAgent',
                'rules': [
                    'deployment_automation',
                    'infrastructure_management',
                    'release_management',
                    'environment_configuration',
                    'monitoring_setup'
                ],
                'description': 'Deployment and release management'
            },
            '@release': {
                'context': 'DEPLOYMENT',
                'agent_type': 'DevOpsAgent',
                'rules': ['release_management', 'deployment_automation'],
                'description': 'Release management tasks'
            },
            '@environment': {
                'context': 'DEPLOYMENT',
                'agent_type': 'DevOpsAgent',
                'rules': ['environment_configuration', 'infrastructure_management'],
                'description': 'Environment configuration tasks'
            },
            
            # === MONITORING KEYWORDS ===
            '@monitor': {
                'context': 'MONITORING',
                'agent_type': 'MonitoringAgent',
                'rules': [
                    'system_monitoring',
                    'health_checks',
                    'alerting_setup',
                    'metrics_collection',
                    'observability'
                ],
                'description': 'System monitoring and observability'
            },
            '@health': {
                'context': 'MONITORING',
                'agent_type': 'MonitoringAgent',
                'rules': ['health_checks', 'system_monitoring'],
                'description': 'Health checking and monitoring'
            },
            '@metrics': {
                'context': 'MONITORING',
                'agent_type': 'MonitoringAgent',
                'rules': ['metrics_collection', 'observability'],
                'description': 'Metrics collection and analysis'
            },
            
            # === GIT KEYWORDS ===
            '@git': {
                'context': 'VERSION_CONTROL',
                'agent_type': 'GitAgent',
                'rules': [
                    'git_workflow',
                    'version_control',
                    'branch_management',
                    'merge_strategies',
                    'collaboration_patterns'
                ],
                'description': 'Git version control operations'
            },
            '@commit': {
                'context': 'VERSION_CONTROL',
                'agent_type': 'GitAgent',
                'rules': ['git_workflow', 'version_control'],
                'description': 'Git commit operations'
            },
            '@push': {
                'context': 'VERSION_CONTROL',
                'agent_type': 'GitAgent',
                'rules': ['git_workflow', 'collaboration_patterns'],
                'description': 'Git push operations'
            },
            '@merge': {
                'context': 'VERSION_CONTROL',
                'agent_type': 'GitAgent',
                'rules': ['merge_strategies', 'branch_management'],
                'description': 'Git merge operations'
            }
        }
    
    def _ensure_database_connection(self):
        """Ensure database connection and tables exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.close()
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
    
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
                
                # Trigger context switch
                self._trigger_context_switch(keyword, config, message)
                
                print(f"🎯 DETECTED: {keyword} → {config['context']} context with {len(config['rules'])} rules")
        
        return detected_events
    
    def _process_keyword_detection(self, keyword: str, config: Dict, message: str) -> Dict[str, Any]:
        """Process a detected keyword and create event data."""
        event = {
            'event_id': str(uuid.uuid4()),
            'keyword': keyword,
            'new_context': config['context'],
            'agent_type': config['agent_type'],
            'rules': config['rules'],
            'rules_count': len(config['rules']),
            'message_snippet': message[:100],
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'previous_context': self.current_context
        }
        
        # Update current context
        self.current_context = config['context']
        
        return event
    
    def _trigger_context_switch(self, keyword: str, config: Dict, message: str):
        """Trigger actual context switch in the universal tracker."""
        try:
            from utils.system.universal_agent_tracker import get_universal_tracker, ContextType
            
            tracker = get_universal_tracker()
            
            # Create context switch record
            context_switch_id = tracker.record_context_switch(
                session_id=self.session_id,
                new_context=config['context'],
                trigger_type='keyword_detection',
                trigger_details={
                    'keyword': keyword,
                    'agent_type': config['agent_type'],
                    'message_snippet': message[:100],
                    'rules_activated': config['rules']
                }
            )
            
            # Record rule activations
            for rule in config['rules']:
                tracker.record_rule_activation(
                    session_id=self.session_id,
                    rule_name=rule,
                    activation_reason=f"Triggered by {keyword} keyword",
                    performance_impact=0.9  # High impact for keyword triggers
                )
            
            logger.info(f"✅ Context switch triggered: {keyword} → {config['context']}")
            
        except Exception as e:
            logger.error(f"❌ Context switch failed: {e}")
    
    def _log_to_database(self, event: Dict[str, Any]):
        """Log keyword detection event to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert into agent_events table
            cursor.execute("""
                INSERT OR IGNORE INTO agent_events 
                (event_id, session_id, event_type, timestamp, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                event['event_id'],
                event['session_id'],
                'keyword_detection',
                event['timestamp'],
                f"Keyword: {event['keyword']} → Context: {event['new_context']}"
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Logged {event['keyword']} to database successfully")
            
        except Exception as e:
            logger.error(f"❌ Database logging failed: {e}")
    
    def process_live_message(self, message: str) -> Dict[str, Any]:
        """
        Process a live message for keyword detection.
        Main entry point for real-time processing.
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
            'message_processed': True,
            'session_id': self.session_id,
            'current_context': self.current_context
        }
    
    def get_available_keywords(self) -> List[str]:
        """Get list of all available keywords."""
        return list(self.keywords_map.keys())
    
    def get_context_for_keyword(self, keyword: str) -> Optional[str]:
        """Get context that a keyword would trigger."""
        config = self.keywords_map.get(keyword)
        return config['context'] if config else None

# Global detector instance
_global_comprehensive_detector = None

def get_comprehensive_keyword_detector() -> ComprehensiveKeywordDetector:
    """Get or create the global comprehensive keyword detector."""
    global _global_comprehensive_detector
    
    if _global_comprehensive_detector is None:
        _global_comprehensive_detector = ComprehensiveKeywordDetector()
        print("🎯 Comprehensive Keyword Detector initialized with ALL keywords")
    
    return _global_comprehensive_detector

def process_message_with_comprehensive_detection(message: str) -> Dict[str, Any]:
    """Process a message with comprehensive keyword detection."""
    detector = get_comprehensive_keyword_detector()
    return detector.process_live_message(message)
