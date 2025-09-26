#!/usr/bin/env python3
"""
Unified Keyword Detection System
===============================

Single, stable, production-ready keyword detection system that:
- Loads configuration from optimized_context_rule_mappings.yaml
- Replaces all scattered hardcoded keyword implementations
- Provides consistent, reliable keyword detection and context switching
- Integrates with universal agent tracker for complete transparency

This is the ONLY keyword detection system - all others are deprecated.
"""

import yaml
import logging
import sqlite3
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

logger = logging.getLogger(__name__)

class UnifiedKeywordDetector:
    """
    The unified, authoritative keyword detection system.
    
    This replaces all other keyword detection implementations and provides:
    - YAML-based configuration
    - Complete keyword coverage
    - Consistent context switching
    - Proper agent tracking
    - Real-time logging
    """
    
    def __init__(self):
        """Initialize the unified keyword detection system."""
        self.config_path = ".cursor/rules/config/optimized_context_rule_mappings.yaml"
        self.db_path = "utils/universal_agent_tracking.db"
        
        # Load configuration
        self.config = self._load_yaml_config()
        self.keywords_map = self._build_complete_keyword_map()
        
        # Session tracking
        self.session_id = str(uuid.uuid4())
        self.current_context = "DEFAULT"
        self.context_history = []
        
        # Initialize database
        self._ensure_database_ready()
        
        logger.info(f"✅ Unified Keyword Detector initialized: {len(self.keywords_map)} keywords loaded")
        
    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load the authoritative YAML configuration."""
        try:
            config_file = Path(self.config_path)
            
            if not config_file.exists():
                logger.error(f"❌ YAML config not found: {self.config_path}")
                raise FileNotFoundError(f"Required config file missing: {self.config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Validate required sections
            required_sections = ['contexts', 'foundation_rules']
            for section in required_sections:
                if section not in config:
                    raise ValueError(f"Missing required section in YAML: {section}")
            
            logger.info(f"✅ Loaded authoritative YAML config: {len(config.get('contexts', {}))} contexts")
            return config
            
        except Exception as e:
            logger.error(f"❌ Failed to load YAML config: {e}")
            raise RuntimeError(f"Cannot initialize without valid YAML config: {e}")
    
    def _build_complete_keyword_map(self) -> Dict[str, Dict[str, Any]]:
        """Build the complete, authoritative keyword mapping."""
        keywords_map = {}
        
        contexts = self.config.get('contexts', {})
        foundation_rules = self.config.get('foundation_rules', {})
        
        for context_name, context_config in contexts.items():
            detection_patterns = context_config.get('detection_patterns', {})
            keywords = detection_patterns.get('keywords', [])
            
            if not keywords:
                logger.warning(f"⚠️ No keywords defined for context: {context_name}")
                continue
            
            # Get complete rule set
            rules_config = context_config.get('rules', {})
            foundation_rule_names = rules_config.get('foundation', [])
            context_rule_names = rules_config.get('context', [])
            tool_rule_names = rules_config.get('tools', [])
            
            # Combine all rules
            all_rules = foundation_rule_names + context_rule_names + tool_rule_names
            
            # Create keyword configuration
            keyword_config = {
                'context': context_name,
                'agent_type': context_config.get('agent_future', 'GeneralAgent'),
                'rules': all_rules,
                'description': context_config.get('description', f'{context_name} context'),
                'confidence_threshold': detection_patterns.get('confidence_threshold', 0.7),
                'message_patterns': detection_patterns.get('message', []),
                'file_patterns': detection_patterns.get('files', []),
                'directory_patterns': detection_patterns.get('directories', []),
                'priority': context_config.get('priority', 1)
            }
            
            # Map each keyword to this configuration
            for keyword in keywords:
                if keyword in keywords_map:
                    logger.warning(f"⚠️ Duplicate keyword definition: {keyword}")
                
                keywords_map[keyword] = keyword_config.copy()
                logger.debug(f"📝 Mapped {keyword} → {context_name}")
        
        # Add any missing critical keywords
        self._add_critical_missing_keywords(keywords_map)
        
        return keywords_map
    
    def _add_critical_missing_keywords(self, keywords_map: Dict[str, Dict[str, Any]]):
        """Add any critical keywords that might be missing from the YAML."""
        
        # Critical keywords that must exist
        critical_keywords = {
            '@analyze': {
                'context': 'ANALYSIS',
                'agent_type': 'AnalysisAgent',
                'rules': ['systematic_analysis', 'evidence_based_reasoning'],
                'description': 'Analysis and investigation tasks',
                'confidence_threshold': 0.8,
                'message_patterns': ['analyze', 'investigation', 'examine'],
                'priority': 2
            }
        }
        
        for keyword, config in critical_keywords.items():
            if keyword not in keywords_map:
                keywords_map[keyword] = config
                logger.info(f"✅ Added critical missing keyword: {keyword}")
    
    def _ensure_database_ready(self):
        """Ensure database connection is ready for logging."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.close()
            logger.debug("✅ Database connection verified")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a message for keyword detection and context switching.
        
        This is the main entry point for all keyword detection.
        
        Args:
            message: The message to process
            
        Returns:
            Processing result with detected keywords and context switches
        """
        try:
            logger.info(f"🔍 Processing message: {message[:100]}...")
            
            # Detect keywords
            detected_keywords = self._detect_keywords(message)
            
            # Process context switches
            context_switches = []
            for keyword_data in detected_keywords:
                context_switch = self._process_context_switch(keyword_data, message)
                if context_switch:
                    context_switches.append(context_switch)
            
            # Log to database
            self._log_detection_results(detected_keywords, context_switches, message)
            
            result = {
                'success': True,
                'message_processed': True,
                'detected_keywords': detected_keywords,
                'context_switches': context_switches,
                'current_context': self.current_context,
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'detector_version': 'unified_v1.0'
            }
            
            # Log summary
            if detected_keywords:
                keyword_list = [kw['keyword'] for kw in detected_keywords]
                logger.info(f"✅ Detected keywords: {keyword_list}")
            else:
                logger.info("📋 No keywords detected")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Message processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_processed': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def _detect_keywords(self, message: str) -> List[Dict[str, Any]]:
        """Detect all keywords in the message."""
        detected = []
        message_lower = message.lower()
        
        for keyword, config in self.keywords_map.items():
            if self._keyword_matches(keyword, config, message, message_lower):
                keyword_data = {
                    'keyword': keyword,
                    'context': config['context'],
                    'agent_type': config['agent_type'],
                    'rules': config['rules'],
                    'rules_count': len(config['rules']),
                    'confidence_threshold': config['confidence_threshold'],
                    'priority': config['priority'],
                    'detection_method': self._get_detection_method(keyword, config, message, message_lower),
                    'event_id': str(uuid.uuid4()),
                    'timestamp': datetime.now().isoformat()
                }
                detected.append(keyword_data)
        
        # Sort by priority (higher priority first)
        detected.sort(key=lambda x: x['priority'], reverse=True)
        
        return detected
    
    def _keyword_matches(self, keyword: str, config: Dict[str, Any], message: str, message_lower: str) -> bool:
        """Check if keyword matches using multiple detection methods."""
        
        # Direct keyword match (highest confidence)
        if keyword.lower() in message_lower:
            return True
        
        # Message pattern matching
        message_patterns = config.get('message_patterns', [])
        for pattern in message_patterns:
            if pattern.lower() in message_lower:
                # Check confidence threshold for pattern matches
                threshold = config.get('confidence_threshold', 0.7)
                if threshold <= 0.8:  # Allow pattern matches for reasonable thresholds
                    return True
        
        return False
    
    def _get_detection_method(self, keyword: str, config: Dict[str, Any], message: str, message_lower: str) -> str:
        """Determine how the keyword was detected."""
        if keyword.lower() in message_lower:
            return 'direct_keyword'
        
        message_patterns = config.get('message_patterns', [])
        for pattern in message_patterns:
            if pattern.lower() in message_lower:
                return f'pattern_match:{pattern}'
        
        return 'unknown'
    
    def _process_context_switch(self, keyword_data: Dict[str, Any], message: str) -> Optional[Dict[str, Any]]:
        """Process context switch for detected keyword."""
        try:
            new_context = keyword_data['context']
            
            # Skip if already in this context
            if new_context == self.current_context:
                logger.debug(f"Already in context {new_context}, skipping switch")
                return None
            
            # Record context switch
            context_switch = {
                'switch_id': str(uuid.uuid4()),
                'from_context': self.current_context,
                'to_context': new_context,
                'trigger_keyword': keyword_data['keyword'],
                'agent_type': keyword_data['agent_type'],
                'rules_activated': keyword_data['rules'],
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                'message_snippet': message[:100]
            }
            
            # Update current context
            previous_context = self.current_context
            self.current_context = new_context
            
            # Add to history
            self.context_history.append(context_switch)
            
            # Trigger universal tracker update
            self._trigger_universal_tracker_update(context_switch)
            
            logger.info(f"🔄 Context switch: {previous_context} → {new_context} (triggered by {keyword_data['keyword']})")
            
            return context_switch
            
        except Exception as e:
            logger.error(f"❌ Context switch failed: {e}")
            return None
    
    def _trigger_universal_tracker_update(self, context_switch: Dict[str, Any]):
        """Update universal tracker with context switch and rule activations."""
        try:
            from utils.system.universal_agent_tracker import get_universal_tracker
            
            tracker = get_universal_tracker()
            
            # Record context switch
            tracker.record_context_switch(
                session_id=self.session_id,
                new_context=context_switch['to_context'],
                trigger_type='unified_keyword_detection',
                trigger_details={
                    'keyword': context_switch['trigger_keyword'],
                    'agent_type': context_switch['agent_type'],
                    'message_snippet': context_switch['message_snippet'],
                    'detection_system': 'unified_v1.0',
                    'switch_id': context_switch['switch_id']
                }
            )
            
            # Record rule activations
            for rule in context_switch['rules_activated']:
                tracker.record_rule_activation(
                    session_id=self.session_id,
                    rule_name=rule,
                    activation_reason=f"Activated by {context_switch['trigger_keyword']} keyword (unified detector)",
                    performance_impact=0.9
                )
            
            logger.debug(f"✅ Universal tracker updated for context switch: {context_switch['switch_id']}")
            
        except Exception as e:
            logger.error(f"❌ Universal tracker update failed: {e}")
    
    def _log_detection_results(self, detected_keywords: List[Dict[str, Any]], 
                             context_switches: List[Dict[str, Any]], message: str):
        """Log detection results to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Log each detected keyword
            for keyword_data in detected_keywords:
                cursor.execute("""
                    INSERT OR IGNORE INTO agent_events 
                    (event_id, session_id, event_type, timestamp, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    keyword_data['event_id'],
                    self.session_id,
                    'unified_keyword_detection',
                    keyword_data['timestamp'],
                    f"Keyword: {keyword_data['keyword']} → Context: {keyword_data['context']} (Unified Detector v1.0)"
                ))
            
            # Log each context switch
            for switch in context_switches:
                cursor.execute("""
                    INSERT OR IGNORE INTO agent_events 
                    (event_id, session_id, event_type, timestamp, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    switch['switch_id'],
                    self.session_id,
                    'unified_context_switch',
                    switch['timestamp'],
                    f"Context Switch: {switch['from_context']} → {switch['to_context']} (triggered by {switch['trigger_keyword']})"
                ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"✅ Logged {len(detected_keywords)} keywords and {len(context_switches)} context switches")
            
        except Exception as e:
            logger.error(f"❌ Database logging failed: {e}")
    
    def get_available_keywords(self) -> List[str]:
        """Get all available keywords."""
        return sorted(list(self.keywords_map.keys()))
    
    def get_contexts(self) -> List[str]:
        """Get all available contexts."""
        contexts = set(config['context'] for config in self.keywords_map.values())
        return sorted(list(contexts))
    
    def get_keyword_info(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific keyword."""
        return self.keywords_map.get(keyword)
    
    def get_context_history(self) -> List[Dict[str, Any]]:
        """Get context switch history for this session."""
        return self.context_history.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and configuration summary."""
        return {
            'status': 'active',
            'detector_version': 'unified_v1.0',
            'config_file': self.config_path,
            'total_keywords': len(self.keywords_map),
            'total_contexts': len(self.get_contexts()),
            'current_context': self.current_context,
            'session_id': self.session_id,
            'context_switches_count': len(self.context_history),
            'yaml_config_loaded': True,
            'database_ready': True
        }

# Global instance - single source of truth
_unified_detector = None

def get_unified_keyword_detector() -> UnifiedKeywordDetector:
    """Get the unified keyword detector instance."""
    global _unified_detector
    
    if _unified_detector is None:
        _unified_detector = UnifiedKeywordDetector()
        logger.info("🎯 Unified Keyword Detector initialized as global instance")
    
    return _unified_detector

def process_message_unified(message: str) -> Dict[str, Any]:
    """Process a message with the unified keyword detection system."""
    detector = get_unified_keyword_detector()
    return detector.process_message(message)

def get_available_keywords() -> List[str]:
    """Get all available keywords from the unified system."""
    detector = get_unified_keyword_detector()
    return detector.get_available_keywords()

def get_system_status() -> Dict[str, Any]:
    """Get unified system status."""
    detector = get_unified_keyword_detector()
    return detector.get_system_status()
