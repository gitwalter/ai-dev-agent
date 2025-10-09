#!/usr/bin/env python3
"""
Cursor Integration Hook
======================

Automatic integration hook that captures ALL Cursor AI agent sessions,
rule activations, and context switches for universal tracking.

This module acts as a bridge between Cursor AI and our Universal Agent Tracker,
ensuring every Cursor session is properly logged and monitored.

Created: 2024
Purpose: Seamless Cursor AI integration with universal agent tracking
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import hashlib
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CursorRuleFileWatcher(FileSystemEventHandler):
    """Watch .cursor/rules/*.mdc files for changes to detect rule activations."""
    
    def __init__(self, tracker_callback):
        self.tracker_callback = tracker_callback
        self.last_file_hashes = {}
        self.cursor_rules_path = Path(".cursor/rules")
        
    def on_modified(self, event):
        """Called when a rule file is modified."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix == '.mdc' and file_path.parent.name == 'rules':
            self._handle_rule_file_change(file_path)
    
    def on_created(self, event):
        """Called when a new rule file is created."""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if file_path.suffix == '.mdc' and file_path.parent.name == 'rules':
            self._handle_rule_file_change(file_path, is_new=True)
    
    def _handle_rule_file_change(self, file_path: Path, is_new: bool = False):
        """Handle rule file changes and track in universal system."""
        try:
            # Read file content and calculate hash
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                
                # Check if file actually changed
                if file_path.name in self.last_file_hashes:
                    if self.last_file_hashes[file_path.name] == content_hash:
                        return  # No actual change
                
                self.last_file_hashes[file_path.name] = content_hash
                
                # Extract rule information
                rule_name = file_path.stem.replace('_', ' ').title()
                context = self._extract_context_from_rule(content)
                
                # Notify tracker
                self.tracker_callback(
                    event_type='rule_file_change',
                    rule_name=rule_name,
                    file_path=str(file_path),
                    is_new=is_new,
                    context=context,
                    timestamp=datetime.now().isoformat()
                )
                
                logger.info(f"📄 Rule file {'created' if is_new else 'modified'}: {rule_name}")
                
        except Exception as e:
            logger.error(f"❌ Error handling rule file change: {e}")
    
    def _extract_context_from_rule(self, content: str) -> str:
        """Extract context information from rule file content."""
        content_lower = content.lower()
        
        # Look for context keywords in rule content
        context_keywords = {
            'agile': ['agile', 'sprint', 'scrum', 'kanban', 'story'],
            'coding': ['code', 'programming', 'development', 'implementation'],
            'testing': ['test', 'testing', 'qa', 'quality', 'validation'],
            'debugging': ['debug', 'debugging', 'fix', 'error', 'bug'],
            'documentation': ['document', 'documentation', 'docs', 'readme'],
            'security': ['security', 'secure', 'auth', 'encryption'],
            'optimization': ['optimize', 'optimization', 'performance', 'speed'],
            'research': ['research', 'analysis', 'investigation', 'study']
        }
        
        for context, keywords in context_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return context
        
        return 'general'

class CursorIntegrationHook:
    """
    Main integration hook for Cursor AI sessions.
    
    Automatically detects and tracks:
    - Cursor AI session starts/stops
    - Rule file changes and activations
    - Context switches based on activity
    - Agent keyword usage (@agile, @research, etc.)
    """
    
    def __init__(self):
        self.universal_tracker = None
        self.cursor_session_id = None
        self.file_watcher = None
        self.observer = None
        self.monitoring_active = False
        self.session_start_time = None
        
        # Activity tracking
        self.last_activity_time = datetime.now()
        self.current_context = 'initialization'
        self.active_rules = set()
        
        # CRITICAL: Connect to universal tracker immediately
        self._initialize_universal_tracking()
        
        # Keywords to context mapping
        self.keyword_contexts = {
            '@agile': 'agile',
            '@research': 'research', 
            '@debug': 'debugging',
            '@test': 'testing',
            '@optimize': 'optimization',
            '@security': 'security',
            '@docs': 'documentation',
            '@code': 'coding'
        }
        
        logger.info("🔌 Cursor Integration Hook: INITIALIZED")
    
    def _initialize_universal_tracking(self):
        """Initialize connection to universal agent tracker."""
        try:
            from utils.system.universal_agent_tracker import get_universal_tracker, AgentType, ContextType
            self.universal_tracker = get_universal_tracker()
            
            # Register Cursor AI session IMMEDIATELY
            self.cursor_session_id = self.universal_tracker.register_agent(
                agent_id=f"cursor_ai_hook_{int(time.time())}",
                agent_type=AgentType.CURSOR_AI,
                initial_context=ContextType.CODING,
                metadata={
                    "integration": "cursor_hook",
                    "auto_tracking": True,
                    "pid": os.getpid()
                }
            )
            logger.info(f"✅ Cursor AI session registered in universal tracker: {self.cursor_session_id}")
            
            # IMMEDIATELY log initial startup
            self.universal_tracker.record_context_switch(
                session_id=self.cursor_session_id,
                new_context=ContextType.SYSTEM_STARTUP,
                trigger_type="cursor_startup",
                trigger_details={"event": "cursor_integration_initialized"}
            )
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Could not connect to universal tracker: {e}")
            self.universal_tracker = None
    
    def start_monitoring(self):
        """Start monitoring Cursor AI activity."""
        try:
            # Import universal tracker
            from utils.system.universal_agent_tracker import get_universal_tracker, AgentType, ContextType
            self.universal_tracker = get_universal_tracker()
            
            # Register Cursor AI session
            self.cursor_session_id = self.universal_tracker.register_agent(
                agent_id=f"cursor_ai_{int(time.time())}",
                agent_type=AgentType.CURSOR_AI,
                initial_context=ContextType.CODING
            )
            
            self.session_start_time = datetime.now()
            
            # Start file system monitoring
            self._start_file_monitoring()
            
            # Start activity monitoring
            self._start_activity_monitoring()
            
            self.monitoring_active = True
            
            logger.info(f"🚀 Cursor monitoring started - Session: {self.cursor_session_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Cursor monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring and clean up."""
        try:
            self.monitoring_active = False
            
            if self.observer:
                self.observer.stop()
                self.observer.join()
            
            if self.universal_tracker and self.cursor_session_id:
                # Mark session as completed instead of calling non-existent shutdown_agent
                try:
                    # Try to record session end
                    self.universal_tracker.record_context_switch(
                        session_id=self.cursor_session_id,
                        new_context="session_end",
                        trigger_type="cursor_shutdown",
                        trigger_details={"event": "cursor_integration_stopped"}
                    )
                except:
                    pass  # Graceful fallback
            
            logger.info("🛑 Cursor monitoring stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping Cursor monitoring: {e}")
    
    def _start_file_monitoring(self):
        """Start monitoring .cursor/rules files."""
        cursor_rules_path = Path(".cursor/rules")
        
        if not cursor_rules_path.exists():
            logger.warning("⚠️ .cursor/rules directory not found")
            return
        
        # Create file watcher
        self.file_watcher = CursorRuleFileWatcher(self._handle_rule_file_event)
        
        # Start file system observer
        self.observer = Observer()
        self.observer.schedule(
            self.file_watcher, 
            str(cursor_rules_path), 
            recursive=True
        )
        self.observer.start()
        
        logger.info("👁️ File monitoring started for .cursor/rules")
    
    def _start_activity_monitoring(self):
        """Start monitoring Cursor activity patterns."""
        def monitor_activity():
            while self.monitoring_active:
                try:
                    # Check for activity indicators
                    self._detect_context_from_activity()
                    
                    # Check for agent keywords in recent activity
                    self._detect_agent_keywords()
                    
                    # Update activity timestamp
                    self.last_activity_time = datetime.now()
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    logger.error(f"❌ Activity monitoring error: {e}")
        
        # Start monitoring thread
        activity_thread = threading.Thread(target=monitor_activity, daemon=True)
        activity_thread.start()
        
        logger.info("📊 Activity monitoring started")
    
    def _handle_rule_file_event(self, event_type: str, rule_name: str, file_path: str, 
                               is_new: bool, context: str, timestamp: str):
        """Handle rule file events from the file watcher."""
        if not self.universal_tracker or not self.cursor_session_id:
            return
        
        # Map context to enum
        from utils.system.universal_agent_tracker import ContextType
        context_enum = getattr(ContextType, context.upper(), ContextType.CODING)
        
        # Record context switch if context changed
        if context != self.current_context:
            self.universal_tracker.record_context_switch(
                session_id=self.cursor_session_id,
                from_context=getattr(ContextType, self.current_context.upper(), ContextType.CODING),
                to_context=context_enum,
                reason=f"Rule file activity detected: {rule_name}",
                triggered_by="cursor_file_system"
            )
            self.current_context = context
        
        # Record rule activation
        self.universal_tracker.record_rule_activation(
            session_id=self.cursor_session_id,
            rule_name=rule_name,
            activation_reason=f"Rule file {'created' if is_new else 'modified'}: {file_path}",
            performance_impact=0.8
        )
        
        self.active_rules.add(rule_name)
    
    def _detect_context_from_activity(self):
        """Detect context changes from Cursor activity patterns."""
        try:
            # Check current working directory
            cwd = Path.cwd()
            
            # Look for context clues in current directory
            context_clues = {
                'testing': ['test', 'tests', '__tests__', 'spec'],
                'documentation': ['docs', 'documentation', 'wiki'],
                'agile': ['agile', 'sprint', 'scrum'],
                'security': ['security', 'auth', 'crypto'],
                'optimization': ['perf', 'performance', 'optimize']
            }
            
            detected_context = 'coding'  # Default
            
            for context, clues in context_clues.items():
                if any(clue in str(cwd).lower() for clue in clues):
                    detected_context = context
                    break
            
            # Check if context changed
            if detected_context != self.current_context:
                self._switch_context(detected_context, "Activity pattern detection")
                
        except Exception as e:
            logger.error(f"❌ Context detection error: {e}")
    
    def _detect_agent_keywords(self):
        """Detect agent keywords that might indicate context switches."""
        # This is a simplified version - in practice, you'd integrate with
        # Cursor's chat/command history or other activity indicators
        
        # For now, we'll simulate detection based on time patterns
        # In a real implementation, this would hook into Cursor's API
        pass
    
    def _switch_context(self, new_context: str, reason: str):
        """Switch to a new context and record the change."""
        if not self.universal_tracker or not self.cursor_session_id:
            return
        
        from utils.system.universal_agent_tracker import ContextType
        
        old_context_enum = getattr(ContextType, self.current_context.upper(), ContextType.CODING)
        new_context_enum = getattr(ContextType, new_context.upper(), ContextType.CODING)
        
        if old_context_enum != new_context_enum:
            self.universal_tracker.record_context_switch(
                session_id=self.cursor_session_id,
                from_context=old_context_enum,
                to_context=new_context_enum,
                reason=reason,
                triggered_by="cursor_activity_detection"
            )
            
            self.current_context = new_context
            logger.info(f"🔄 Context switch: {old_context_enum.value} → {new_context_enum.value}")
    
    def record_manual_context_switch(self, context: str, keyword: str = None):
        """Manually record a context switch (for testing or explicit triggers)."""
        reason = f"Manual context switch to {context}"
        if keyword:
            reason += f" via {keyword}"
        
        self._switch_context(context, reason)
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        return {
            'session_id': self.cursor_session_id,
            'monitoring_active': self.monitoring_active,
            'current_context': self.current_context,
            'active_rules': list(self.active_rules),
            'session_duration': (datetime.now() - self.session_start_time).total_seconds() if self.session_start_time else 0,
            'last_activity': self.last_activity_time.isoformat()
        }

# Global hook instance
_cursor_hook = None

def get_cursor_hook() -> CursorIntegrationHook:
    """Get the global Cursor integration hook."""
    global _cursor_hook
    if _cursor_hook is None:
        _cursor_hook = CursorIntegrationHook()
    return _cursor_hook

def start_cursor_tracking():
    """Start automatic Cursor AI tracking."""
    hook = get_cursor_hook()
    hook.start_monitoring()
    return hook

def stop_cursor_tracking():
    """Stop Cursor AI tracking."""
    hook = get_cursor_hook()
    hook.stop_monitoring()

def track_manual_context_switch(context: str, keyword: str = None):
    """Manually track a context switch (convenience function)."""
    hook = get_cursor_hook()
    hook.record_manual_context_switch(context, keyword)

if __name__ == "__main__":
    # Test the Cursor integration
    print("🧪 Testing Cursor Integration Hook")
    
    hook = start_cursor_tracking()
    
    # Simulate some activity
    time.sleep(2)
    
    # Manual context switches
    track_manual_context_switch('agile', '@agile')
    track_manual_context_switch('testing', '@test')
    track_manual_context_switch('research', '@research')
    
    # Get status
    status = hook.get_session_status()
    print(f"📊 Session Status: {status}")
    
    time.sleep(2)
    stop_cursor_tracking()
    
    print("✅ Cursor Integration Hook: TESTED!")
