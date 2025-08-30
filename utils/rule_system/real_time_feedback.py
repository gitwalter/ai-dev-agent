#!/usr/bin/env python3
"""
Real-Time Rule Application Feedback System

Advanced system for providing real-time feedback on rule application,
detecting issues immediately, and providing corrective guidance.
"""

import time
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from threading import Thread, Event
import queue

@dataclass
class FeedbackMessage:
    """Real-time feedback message."""
    timestamp: str
    severity: str  # INFO, WARNING, ERROR, CRITICAL
    rule_name: str
    message: str
    suggested_action: str
    context: Dict[str, Any]

@dataclass
class RuleApplicationEvent:
    """Event for rule application tracking."""
    rule_name: str
    event_type: str  # start, progress, complete, error
    timestamp: str
    data: Dict[str, Any]

class RealTimeFeedbackSystem:
    """
    Real-time feedback system for rule application monitoring.
    
    This system provides immediate feedback on rule application progress,
    detects issues as they occur, and provides corrective guidance to
    ensure optimal rule application and system performance.
    """
    
    def __init__(self, feedback_file: Path = None):
        self.feedback_file = feedback_file or Path('monitoring/real_time_feedback.json')
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
        self.feedback_history = self._load_feedback_history()
        self.active_monitoring = False
        self.feedback_queue = queue.Queue()
        self.monitoring_thread = None
        self.stop_event = Event()
        
    def start_monitoring(self) -> None:
        """Start real-time monitoring."""
        if not self.active_monitoring:
            self.active_monitoring = True
            self.stop_event.clear()
            self.monitoring_thread = Thread(target=self._monitoring_loop)
            self.monitoring_thread.start()
            print("🔄 Real-time rule monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop real-time monitoring."""
        if self.active_monitoring:
            self.active_monitoring = False
            self.stop_event.set()
            if self.monitoring_thread:
                self.monitoring_thread.join()
            print("⏹️ Real-time rule monitoring stopped")
    
    def record_rule_event(self, event: RuleApplicationEvent) -> None:
        """Record a rule application event."""
        if self.active_monitoring:
            self.feedback_queue.put(event)
        
        # Always save to history
        self.feedback_history.append(asdict(event))
        self._save_feedback_history()
    
    def provide_feedback(self, 
                        rule_name: str,
                        context: Dict[str, Any],
                        performance_metrics: Dict[str, float] = None) -> FeedbackMessage:
        """
        Provide immediate feedback on rule application.
        
        Args:
            rule_name: Name of the rule being applied
            context: Current application context
            performance_metrics: Optional performance data
            
        Returns:
            Feedback message with guidance
        """
        # Analyze current application
        analysis = self._analyze_rule_application(rule_name, context, performance_metrics)
        
        # Generate feedback based on analysis
        feedback = self._generate_feedback(rule_name, analysis, context)
        
        # Record feedback
        self.feedback_history.append(asdict(feedback))
        self._save_feedback_history()
        
        return feedback
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop for real-time feedback."""
        while self.active_monitoring and not self.stop_event.is_set():
            try:
                # Process queued events
                while not self.feedback_queue.empty():
                    event = self.feedback_queue.get_nowait()
                    self._process_event(event)
                
                # Check for performance issues
                self._check_performance_thresholds()
                
                # Check for stuck rules
                self._check_for_stuck_rules()
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"🚨 Monitoring error: {e}")
                time.sleep(5)  # Back off on errors
    
    def _process_event(self, event: RuleApplicationEvent) -> None:
        """Process a rule application event."""
        if event.event_type == 'error':
            self._handle_rule_error(event)
        elif event.event_type == 'start':
            self._track_rule_start(event)
        elif event.event_type == 'complete':
            self._track_rule_completion(event)
    
    def _analyze_rule_application(self, 
                                rule_name: str,
                                context: Dict[str, Any],
                                metrics: Optional[Dict[str, float]]) -> Dict[str, Any]:
        """Analyze current rule application for feedback."""
        analysis = {
            'rule_appropriateness': self._assess_rule_appropriateness(rule_name, context),
            'expected_duration': self._estimate_rule_duration(rule_name, context),
            'potential_issues': self._identify_potential_issues(rule_name, context),
            'optimization_suggestions': self._generate_optimization_suggestions(rule_name, context)
        }
        
        if metrics:
            analysis.update({
                'performance_score': self._calculate_performance_score(metrics),
                'efficiency_rating': self._calculate_efficiency_rating(metrics)
            })
        
        return analysis
    
    def _generate_feedback(self, 
                         rule_name: str,
                         analysis: Dict[str, Any],
                         context: Dict[str, Any]) -> FeedbackMessage:
        """Generate feedback message based on analysis."""
        
        # Determine severity
        appropriateness = analysis.get('rule_appropriateness', 0.5)
        potential_issues = analysis.get('potential_issues', [])
        
        if appropriateness < 0.3 or len(potential_issues) > 2:
            severity = "ERROR"
            message = f"Rule '{rule_name}' may not be appropriate for this context"
            suggested_action = "Consider using alternative rules or modifying approach"
        elif appropriateness < 0.6 or len(potential_issues) > 0:
            severity = "WARNING" 
            message = f"Rule '{rule_name}' has moderate appropriateness"
            suggested_action = "Monitor application closely and be prepared to adjust"
        else:
            severity = "INFO"
            message = f"Rule '{rule_name}' is well-suited for this context"
            suggested_action = "Proceed with standard application"
        
        return FeedbackMessage(
            timestamp=datetime.now().isoformat(),
            severity=severity,
            rule_name=rule_name,
            message=message,
            suggested_action=suggested_action,
            context=context
        )
    
    def _assess_rule_appropriateness(self, rule_name: str, context: Dict[str, Any]) -> float:
        """Assess how appropriate a rule is for the context."""
        # Simplified appropriateness scoring
        task_type = context.get('task_type', 'unknown')
        
        appropriateness_map = {
            'file_operation': {
                'File Organization Rule': 0.95,
                'Clean Repository Focus Rule': 0.9
            },
            'testing': {
                'Test-Driven Development Rule': 0.95,
                'No Premature Victory Declaration Rule': 0.9
            },
            'documentation': {
                'Live Documentation Updates Rule': 0.95,
                'Clear Documentation Rule': 0.9
            }
        }
        
        return appropriateness_map.get(task_type, {}).get(rule_name, 0.7)
    
    def _estimate_rule_duration(self, rule_name: str, context: Dict[str, Any]) -> float:
        """Estimate expected duration for rule application."""
        # Base durations in seconds
        base_durations = {
            'File Organization Rule': 30,
            'Clean Repository Focus Rule': 15,
            'Live Documentation Updates Rule': 45,
            'Test-Driven Development Rule': 120,
            'Boy Scout Rule': 60
        }
        
        base_time = base_durations.get(rule_name, 30)
        
        # Adjust for complexity
        complexity = context.get('complexity', 'medium')
        if complexity == 'complex':
            base_time *= 1.5
        elif complexity == 'simple':
            base_time *= 0.7
        
        return base_time
    
    def _identify_potential_issues(self, rule_name: str, context: Dict[str, Any]) -> List[str]:
        """Identify potential issues with rule application."""
        issues = []
        
        # Context-based issue detection
        if context.get('time_pressure', 0) > 0.8:
            if 'comprehensive' in rule_name.lower() or 'thorough' in rule_name.lower():
                issues.append("High time pressure conflicts with thorough rule application")
        
        if context.get('complexity', 'medium') == 'simple':
            if 'Object-Oriented Programming' in rule_name:
                issues.append("OOP rule may be overkill for simple tasks")
        
        return issues
    
    def _generate_optimization_suggestions(self, rule_name: str, context: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions for rule application."""
        suggestions = []
        
        # Context-specific suggestions
        if context.get('task_type') == 'file_operation':
            if rule_name == 'File Organization Rule':
                suggestions.append("Consider batching file operations for efficiency")
        
        if context.get('quality_requirements', 0) > 0.9:
            suggestions.append("Apply Boy Scout Rule for additional quality improvements")
        
        return suggestions
    
    def _check_performance_thresholds(self) -> None:
        """Check if performance thresholds are exceeded."""
        # This would check actual performance metrics
        pass
    
    def _check_for_stuck_rules(self) -> None:
        """Check for rules that appear to be stuck."""
        # This would detect rules taking too long
        pass
    
    def _handle_rule_error(self, event: RuleApplicationEvent) -> None:
        """Handle rule application errors."""
        print(f"🚨 Rule error detected: {event.rule_name}")
        print(f"   Error: {event.data.get('error', 'Unknown error')}")
    
    def _track_rule_start(self, event: RuleApplicationEvent) -> None:
        """Track rule start."""
        print(f"🟡 Rule started: {event.rule_name}")
    
    def _track_rule_completion(self, event: RuleApplicationEvent) -> None:
        """Track rule completion."""
        print(f"✅ Rule completed: {event.rule_name}")
    
    def _calculate_performance_score(self, metrics: Dict[str, float]) -> float:
        """Calculate performance score from metrics."""
        return metrics.get('success_rate', 0.0) * metrics.get('efficiency', 0.0)
    
    def _calculate_efficiency_rating(self, metrics: Dict[str, float]) -> float:
        """Calculate efficiency rating from metrics."""
        return min(1.0, metrics.get('speed_factor', 1.0) * metrics.get('quality_factor', 1.0))
    
    def _load_feedback_history(self) -> List[Dict[str, Any]]:
        """Load feedback history."""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_feedback_history(self) -> None:
        """Save feedback history."""
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback_history, f, indent=2)

def demo_real_time_feedback():
    """Demonstrate the real-time feedback system."""
    print("📡 REAL-TIME FEEDBACK SYSTEM DEMO")
    print("=" * 50)
    
    feedback_system = RealTimeFeedbackSystem()
    
    # Start monitoring
    feedback_system.start_monitoring()
    
    # Simulate rule applications
    test_context = {
        'task_type': 'file_operation',
        'complexity': 'simple',
        'quality_requirements': 0.9
    }
    
    # Test feedback for different rules
    test_rules = [
        "File Organization Rule",
        "Test-Driven Development Rule",
        "Object-Oriented Programming Rule"  # This might generate warning for simple task
    ]
    
    for rule in test_rules:
        feedback = feedback_system.provide_feedback(rule, test_context)
        print(f"📢 **{feedback.severity}**: {feedback.message}")
        print(f"   Action: {feedback.suggested_action}")
        print()
    
    # Stop monitoring
    time.sleep(2)
    feedback_system.stop_monitoring()

if __name__ == "__main__":
    demo_real_time_feedback()
