#!/usr/bin/env python3
"""
Cursor Keyword Agent Logger
===========================

Specialized logger for tracking Cursor AI keyword usage and context switches.
This module provides comprehensive logging of @agile, @debug, @test, and other
keyword-triggered agent activations.

Created: 2024
Purpose: Transparent tracking of Cursor keyword-based agent interactions
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
module_logger = logging.getLogger(__name__)

class CursorKeywordAgentLogger:
    """
    Logger for Cursor keyword-based agent activations.
    
    Tracks usage of keywords like @agile, @debug, @test, @research, etc.
    and logs all associated context switches and agent activations.
    """
    
    def __init__(self):
        self.universal_tracker = None
        self.session_id = None
        self.keyword_history = []
        self.context_switches = []
        
        # Keyword to context mapping - MUST be defined BEFORE universal tracking
        self.keyword_contexts = {
            '@agile': 'agile_workflow',
            '@debug': 'debugging',
            '@test': 'testing',
            '@research': 'research',
            '@optimize': 'optimization',
            '@security': 'security',
            '@docs': 'documentation',
            '@code': 'coding',
            '@review': 'code_review',
            '@deploy': 'deployment',
            '@monitor': 'monitoring',
            '@fix': 'bug_fixing',
            '@refactor': 'refactoring',
            '@analyze': 'analysis'
        }
        
        # Initialize connection to universal tracker AFTER keyword_contexts is defined
        self._initialize_universal_tracking()
        
        module_logger.info("🔍 Cursor Keyword Agent Logger: INITIALIZED")
    
    def _initialize_universal_tracking(self):
        """Initialize connection to universal agent tracker."""
        try:
            from utils.system.universal_agent_tracker import get_universal_tracker, AgentType, ContextType
            self.universal_tracker = get_universal_tracker()
            
            # Register Cursor keyword session
            self.session_id = self.universal_tracker.register_agent(
                agent_id=f"cursor_keyword_logger_{int(time.time())}",
                agent_type=AgentType.CURSOR_AI,
                initial_context=ContextType.MONITORING,
                metadata={
                    "component": "keyword_logger",
                    "tracking_keywords": list(self.keyword_contexts.keys()),
                    "auto_detection": True
                }
            )
            
            module_logger.info(f"✅ Cursor keyword logger registered: {self.session_id}")
            
        except Exception as e:
            module_logger.error(f"❌ Failed to initialize universal tracking: {e}")
            self.universal_tracker = None
    
    def log_keyword_usage(self, keyword: str, context: str = None, metadata: Dict = None) -> bool:
        """
        Log usage of a Cursor keyword.
        
        Args:
            keyword: The keyword used (e.g., '@agile', '@debug')
            context: Additional context information
            metadata: Additional metadata about the usage
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            # Normalize keyword
            if not keyword.startswith('@'):
                keyword = f'@{keyword}'
            
            # Get context from keyword mapping
            detected_context = self.keyword_contexts.get(keyword, 'general')
            
            # Create usage record
            usage_record = {
                'keyword': keyword,
                'detected_context': detected_context,
                'user_context': context,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Add to history
            self.keyword_history.append(usage_record)
            
            # Log to universal tracker if available
            if self.universal_tracker and self.session_id:
                # Map to ContextType enum
                from utils.system.universal_agent_tracker import ContextType
                context_enum = getattr(ContextType, detected_context.upper(), ContextType.CODING)
                
                # Record context switch
                self.universal_tracker.record_context_switch(
                    session_id=self.session_id,
                    new_context=context_enum,
                    trigger_type="cursor_keyword",
                    trigger_details={
                        "keyword": keyword,
                        "context": context,
                        "metadata": metadata
                    }
                )
                
                # Record rule activation
                self.universal_tracker.record_rule_activation(
                    session_id=self.session_id,
                    rule_name=f"Cursor Keyword: {keyword}",
                    activation_reason=f"Keyword {keyword} detected in user input",
                    performance_impact=0.9
                )
            
            module_logger.info(f"📝 Logged keyword usage: {keyword} -> {detected_context}")
            return True
            
        except Exception as e:
            module_logger.error(f"❌ Failed to log keyword usage: {e}")
            return False
    
    def log_context_switch(self, from_context: str, to_context: str, trigger: str = None) -> bool:
        """
        Log a context switch triggered by keyword usage.
        
        Args:
            from_context: Previous context
            to_context: New context
            trigger: What triggered the switch
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            switch_record = {
                'from_context': from_context,
                'to_context': to_context,
                'trigger': trigger,
                'timestamp': datetime.now().isoformat()
            }
            
            self.context_switches.append(switch_record)
            
            # Log to universal tracker
            if self.universal_tracker and self.session_id:
                from utils.system.universal_agent_tracker import ContextType
                
                from_enum = getattr(ContextType, from_context.upper(), ContextType.CODING)
                to_enum = getattr(ContextType, to_context.upper(), ContextType.CODING)
                
                self.universal_tracker.record_context_switch(
                    session_id=self.session_id,
                    from_context=from_enum,
                    to_context=to_enum,
                    reason=f"Context switch: {trigger}",
                    triggered_by="cursor_keyword_detection"
                )
            
            module_logger.info(f"🔄 Context switch logged: {from_context} -> {to_context}")
            return True
            
        except Exception as e:
            module_logger.error(f"❌ Failed to log context switch: {e}")
            return False
    
    def get_keyword_history(self, limit: int = 50) -> List[Dict]:
        """
        Get recent keyword usage history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of keyword usage records
        """
        return self.keyword_history[-limit:] if self.keyword_history else []
    
    def get_context_switches(self, limit: int = 50) -> List[Dict]:
        """
        Get recent context switches.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of context switch records
        """
        return self.context_switches[-limit:] if self.context_switches else []
    
    def get_keyword_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about keyword usage.
        
        Returns:
            Dictionary with usage statistics
        """
        if not self.keyword_history:
            return {
                'total_keywords': 0,
                'unique_keywords': 0,
                'most_used': None,
                'context_distribution': {}
            }
        
        # Count keyword usage
        keyword_counts = {}
        context_counts = {}
        
        for record in self.keyword_history:
            keyword = record['keyword']
            context = record['detected_context']
            
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            context_counts[context] = context_counts.get(context, 0) + 1
        
        # Find most used keyword
        most_used = max(keyword_counts.items(), key=lambda x: x[1]) if keyword_counts else None
        
        return {
            'total_keywords': len(self.keyword_history),
            'unique_keywords': len(keyword_counts),
            'most_used': most_used,
            'keyword_distribution': keyword_counts,
            'context_distribution': context_counts,
            'session_duration': self._calculate_session_duration()
        }
    
    def _calculate_session_duration(self) -> float:
        """Calculate session duration in minutes."""
        if not self.keyword_history:
            return 0.0
        
        first_record = self.keyword_history[0]
        last_record = self.keyword_history[-1]
        
        try:
            first_time = datetime.fromisoformat(first_record['timestamp'])
            last_time = datetime.fromisoformat(last_record['timestamp'])
            duration = (last_time - first_time).total_seconds() / 60
            return round(duration, 2)
        except:
            return 0.0
    
    def detect_keywords_in_text(self, text: str) -> List[str]:
        """
        Detect keywords in given text.
        
        Args:
            text: Text to analyze for keywords
            
        Returns:
            List of detected keywords
        """
        detected = []
        text_lower = text.lower()
        
        for keyword in self.keyword_contexts.keys():
            if keyword.lower() in text_lower:
                detected.append(keyword)
        
        return detected
    
    def auto_log_from_text(self, text: str, context: str = None) -> List[str]:
        """
        Automatically detect and log keywords from text.
        
        Args:
            text: Text to analyze
            context: Additional context
            
        Returns:
            List of keywords that were logged
        """
        detected_keywords = self.detect_keywords_in_text(text)
        logged_keywords = []
        
        for keyword in detected_keywords:
            if self.log_keyword_usage(keyword, context, {'source_text': text[:100]}):
                logged_keywords.append(keyword)
        
        return logged_keywords
    
    def get_session_status(self) -> Dict[str, Any]:
        """
        Get current session status.
        
        Returns:
            Dictionary with session information
        """
        return {
            'session_id': self.session_id,
            'universal_tracker_connected': self.universal_tracker is not None,
            'keywords_logged': len(self.keyword_history),
            'context_switches': len(self.context_switches),
            'supported_keywords': list(self.keyword_contexts.keys()),
            'session_active': True
        }

# Global instance
_cursor_keyword_logger = None

def get_cursor_keyword_logger() -> CursorKeywordAgentLogger:
    """Get the global Cursor keyword logger instance."""
    global _cursor_keyword_logger
    if _cursor_keyword_logger is None:
        _cursor_keyword_logger = CursorKeywordAgentLogger()
    return _cursor_keyword_logger

def log_cursor_keyword(keyword: str, context: str = None, metadata: Dict = None) -> bool:
    """
    Convenience function to log a Cursor keyword.
    
    Args:
        keyword: The keyword to log
        context: Additional context
        metadata: Additional metadata
        
    Returns:
        bool: True if logged successfully
    """
    logger = get_cursor_keyword_logger()
    return logger.log_keyword_usage(keyword, context, metadata)

def detect_and_log_keywords(text: str, context: str = None) -> List[str]:
    """
    Convenience function to detect and log keywords from text.
    
    Args:
        text: Text to analyze
        context: Additional context
        
    Returns:
        List of keywords that were logged
    """
    logger = get_cursor_keyword_logger()
    return logger.auto_log_from_text(text, context)

if __name__ == "__main__":
    # Test the keyword logger
    print("🧪 Testing Cursor Keyword Agent Logger")
    
    logger = get_cursor_keyword_logger()
    
    # Test keyword logging
    test_keywords = ['@agile', '@debug', '@test', '@research']
    for keyword in test_keywords:
        success = logger.log_keyword_usage(keyword, f"Testing {keyword}")
        print(f"Logged {keyword}: {success}")
    
    # Test text detection
    test_text = "Let's use @agile methodology to @debug this issue and @test the solution"
    detected = logger.auto_log_from_text(test_text, "test_context")
    print(f"Detected keywords: {detected}")
    
    # Get statistics
    stats = logger.get_keyword_statistics()
    print(f"Statistics: {stats}")
    
    # Get session status
    status = logger.get_session_status()
    print(f"Session status: {status}")
    
    print("✅ Cursor Keyword Agent Logger: TESTED!")
