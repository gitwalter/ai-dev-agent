#!/usr/bin/env python3
"""
YAML-Based Comprehensive Keyword Detection System
================================================

Uses optimized_context_rule_mappings.yaml to create comprehensive keyword detection
with proper context switches, rule activations, and agent logging.

This integrates our official YAML configuration with real-time keyword detection.
"""

import yaml
import logging
import sqlite3
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class YamlBasedKeywordDetector:
    """
    Comprehensive keyword detection system based on YAML configuration.
    
    Loads configuration from optimized_context_rule_mappings.yaml and creates
    a complete keyword detection system with context switching and rule activation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with YAML configuration."""
        self.config_path = config_path or ".cursor/rules/config/optimized_context_rule_mappings.yaml"
        self.config = self._load_yaml_config()
        self.keywords_map = self._build_keywords_from_config()
        self.current_context = "DEFAULT"
        self.context_history = []
        self.session_id = str(uuid.uuid4())
        
        # Initialize database connection
        self.db_path = "utils/universal_agent_tracking.db"
        self._ensure_database_connection()
        
        logger.info(f"🎯 YAML-Based Keyword Detector initialized with {len(self.keywords_map)} keywords from config")
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load the YAML configuration file."""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                logger.error(f"❌ Config file not found: {self.config_path}")
                return self._get_fallback_config()
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"✅ Loaded YAML config from {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"❌ Failed to load YAML config: {e}")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration if YAML loading fails."""
        return {
            'contexts': {
                'DEFAULT': {
                    'description': 'Default context',
                    'detection_patterns': {'keywords': ['@default']},
                    'rules': {'foundation': ['ethical_dna_core', 'safety_first_principle']},
                    'agent_future': 'GeneralAgent'
                }
            }
        }
    
    def _build_keywords_from_config(self) -> Dict[str, Dict[str, Any]]:
        """Build comprehensive keyword mapping from YAML configuration."""
        keywords_map = {}
        
        contexts = self.config.get('contexts', {})
        
        for context_name, context_config in contexts.items():
            detection_patterns = context_config.get('detection_patterns', {})
            keywords = detection_patterns.get('keywords', [])
            
            # Get rules for this context
            rules_config = context_config.get('rules', {})
            foundation_rules = rules_config.get('foundation', [])
            context_rules = rules_config.get('context', [])
            tool_rules = rules_config.get('tools', [])
            
            all_rules = foundation_rules + context_rules + tool_rules
            
            # Create keyword entries
            for keyword in keywords:
                keywords_map[keyword] = {
                    'context': context_name,
                    'agent_type': context_config.get('agent_future', 'GeneralAgent'),
                    'rules': all_rules,
                    'description': context_config.get('description', f'{context_name} context'),
                    'confidence_threshold': detection_patterns.get('confidence_threshold', 0.7),
                    'message_patterns': detection_patterns.get('message', []),
                    'file_patterns': detection_patterns.get('files', []),
                    'directory_patterns': detection_patterns.get('directories', [])
                }
        
        # Add missing essential keywords that should be included
        self._add_missing_essential_keywords(keywords_map)
        
        return keywords_map
    
    def _add_missing_essential_keywords(self, keywords_map: Dict[str, Dict[str, Any]]):
        """Add essential keywords that might be missing from the config."""
        essential_keywords = {
            '@analyze': {
                'context': 'ANALYSIS',
                'agent_type': 'AnalysisAgent', 
                'rules': ['systematic_analysis', 'evidence_based_reasoning', 'critical_thinking'],
                'description': 'Analysis and investigation tasks'
            },
            '@investigate': {
                'context': 'RESEARCH',
                'agent_type': 'ResearchAgent',
                'rules': ['systematic_research', 'evidence_based_development'],
                'description': 'Investigation and research tasks'
            },
            '@monitor': {
                'context': 'MONITORING',
                'agent_type': 'MonitoringAgent',
                'rules': ['system_monitoring', 'health_checks', 'observability'],
                'description': 'System monitoring and observability'
            },
            '@deploy': {
                'context': 'DEPLOYMENT',
                'agent_type': 'DevOpsAgent',
                'rules': ['deployment_automation', 'release_management'],
                'description': 'Deployment and release management'
            }
        }
        
        for keyword, config in essential_keywords.items():
            if keyword not in keywords_map:
                keywords_map[keyword] = config
                logger.info(f"✅ Added missing essential keyword: {keyword}")
    
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
            if self._matches_keyword(keyword, config, message):
                event = self._process_keyword_detection(keyword, config, message)
                detected_events.append(event)
                
                # Log to database
                self._log_to_database(event)
                
                # Trigger context switch
                self._trigger_context_switch(keyword, config, message)
                
                print(f"🎯 DETECTED: {keyword} → {config['context']} context with {len(config['rules'])} rules")
        
        return detected_events
    
    def _matches_keyword(self, keyword: str, config: Dict[str, Any], message: str) -> bool:
        """Check if keyword matches the message using multiple detection methods."""
        message_lower = message.lower()
        
        # Direct keyword match (highest priority)
        if keyword.lower() in message_lower:
            return True
        
        # Message pattern matching
        message_patterns = config.get('message_patterns', [])
        for pattern in message_patterns:
            if pattern.lower() in message_lower:
                confidence_threshold = config.get('confidence_threshold', 0.7)
                # For pattern matches, use a lower threshold since it's less direct
                if confidence_threshold <= 0.8:  # Adjust threshold for pattern matching
                    return True
        
        return False
    
    def _process_keyword_detection(self, keyword: str, config: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Process a detected keyword and create event data."""
        event = {
            'event_id': str(uuid.uuid4()),
            'keyword': keyword,
            'context': config['context'],
            'agent_type': config['agent_type'],
            'rules': config['rules'],
            'rules_count': len(config['rules']),
            'message_snippet': message[:100],
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'previous_context': self.current_context,
            'detection_method': 'yaml_config',
            'confidence_threshold': config.get('confidence_threshold', 0.7)
        }
        
        # Update current context
        self.current_context = config['context']
        
        # Add to context history
        self.context_history.append({
            'timestamp': event['timestamp'],
            'from_context': event['previous_context'],
            'to_context': event['context'],
            'trigger': keyword,
            'event_id': event['event_id']
        })
        
        return event
    
    def _trigger_context_switch(self, keyword: str, config: Dict[str, Any], message: str):
        """Trigger actual context switch in the universal tracker."""
        try:
            from utils.system.universal_agent_tracker import get_universal_tracker
            
            tracker = get_universal_tracker()
            
            # Create context switch record
            context_switch_id = tracker.record_context_switch(
                session_id=self.session_id,
                new_context=config['context'],
                trigger_type='yaml_keyword_detection',
                trigger_details={
                    'keyword': keyword,
                    'agent_type': config['agent_type'],
                    'message_snippet': message[:100],
                    'rules_activated': config['rules'],
                    'config_source': 'optimized_context_rule_mappings.yaml',
                    'confidence_threshold': config.get('confidence_threshold', 0.7)
                }
            )
            
            # Record rule activations for each rule
            for rule in config['rules']:
                tracker.record_rule_activation(
                    session_id=self.session_id,
                    rule_name=rule,
                    activation_reason=f"Triggered by {keyword} keyword (YAML config)",
                    performance_impact=0.9  # High impact for keyword triggers
                )
            
            logger.info(f"✅ Context switch triggered: {keyword} → {config['context']} (YAML-based)")
            
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
                'yaml_keyword_detection',
                event['timestamp'],
                f"Keyword: {event['keyword']} → Context: {event['new_context']} (YAML-based)"
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Logged {event['keyword']} to database successfully (YAML-based)")
            
        except Exception as e:
            logger.error(f"❌ Database logging failed: {e}")
    
    def process_live_message(self, message: str) -> Dict[str, Any]:
        """
        Process a live message for keyword detection.
        Main entry point for real-time processing.
        """
        print(f"🔍 YAML-BASED SCANNING: {message[:100]}...")
        
        detected = self.detect_and_process_keywords(message)
        
        if detected:
            print(f"🎯 YAML PROCESSED {len(detected)} KEYWORD(S)")
            for event in detected:
                print(f"  • {event['keyword']} → {event['new_context']} ({event['rules_count']} rules) [YAML]")
        else:
            print("  No YAML keywords detected")
        
        return {
            'detected_keywords': detected,
            'message_processed': True,
            'session_id': self.session_id,
            'current_context': self.current_context,
            'detection_method': 'yaml_based',
            'config_source': self.config_path
        }
    
    def get_available_keywords(self) -> List[str]:
        """Get list of all available keywords from YAML config."""
        return list(self.keywords_map.keys())
    
    def get_context_for_keyword(self, keyword: str) -> Optional[str]:
        """Get context that a keyword would trigger."""
        config = self.keywords_map.get(keyword)
        return config['context'] if config else None
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of loaded configuration."""
        contexts = set(config['context'] for config in self.keywords_map.values())
        agent_types = set(config['agent_type'] for config in self.keywords_map.values())
        
        return {
            'total_keywords': len(self.keywords_map),
            'contexts_available': len(contexts),
            'agent_types_available': len(agent_types),
            'config_file': self.config_path,
            'keywords_by_context': self._group_keywords_by_context(),
            'yaml_config_version': self.config.get('version', 'unknown'),
            'system_type': self.config.get('system', 'unknown')
        }
    
    def _group_keywords_by_context(self) -> Dict[str, List[str]]:
        """Group keywords by their target context."""
        grouped = {}
        for keyword, config in self.keywords_map.items():
            context = config['context']
            if context not in grouped:
                grouped[context] = []
            grouped[context].append(keyword)
        return grouped
    
    def get_context_history(self) -> List[Dict[str, Any]]:
        """Get the context switch history for this session."""
        return self.context_history.copy()

# Global detector instance
_global_yaml_detector = None

def get_yaml_keyword_detector() -> YamlBasedKeywordDetector:
    """Get or create the global YAML-based keyword detector."""
    global _global_yaml_detector
    
    if _global_yaml_detector is None:
        _global_yaml_detector = YamlBasedKeywordDetector()
        print("🎯 YAML-Based Keyword Detector initialized from configuration")
    
    return _global_yaml_detector

def process_message_with_yaml_detection(message: str) -> Dict[str, Any]:
    """Process a message with YAML-based keyword detection."""
    detector = get_yaml_keyword_detector()
    return detector.process_live_message(message)

def get_yaml_config_summary() -> Dict[str, Any]:
    """Get summary of the YAML configuration."""
    detector = get_yaml_keyword_detector()
    return detector.get_config_summary()
