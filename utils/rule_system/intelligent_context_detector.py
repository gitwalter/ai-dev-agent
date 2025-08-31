"""
Intelligent Context-Aware Rule System
Implementation of US-E0-010: Context detection and rule selection

This module provides the foundation for both current AI assistant efficiency
and future agent swarm coordination.
"""

import yaml
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ContextResult:
    """Result of context detection analysis."""
    context: str
    method: str  # "explicit_keyword", "auto_detected", "fallback"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    rules: List[str]
    agent_future: str


@dataclass
class RuleApplicationResult:
    """Result of rule application with efficiency metrics."""
    context: str
    active_rules: List[str]
    total_rules_available: int
    efficiency_improvement: float
    agent_future: str
    detection_confidence: float
    session_id: Optional[str] = None


class IntelligentContextDetector:
    """
    Intelligent context detection system for automated rule selection.
    
    This system serves as the foundation for future agent swarm coordination,
    where context detection becomes agent selection logic.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the context detector with configuration."""
        if config_path is None:
            config_path = ".cursor/rules/config/context_rule_mappings.yaml"
        
        self.config_path = config_path
        self.config = self._load_configuration()
        self.contexts = self.config["contexts"]
        self.detection_config = self.config["detection"]
        
        # Build keyword mapping for fast lookup
        self.keyword_map = self._build_keyword_map()
        
        # Performance tracking
        self.session_stats = {
            "contexts_detected": {},
            "accuracy_feedback": [],
            "performance_metrics": []
        }
    
    def _load_configuration(self) -> Dict:
        """Load context rule mappings configuration."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Fallback to minimal configuration
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict:
        """Provide fallback configuration if config file not found."""
        return {
            "contexts": {
                "DEFAULT": {
                    "description": "General development work",
                    "keywords": ["@default"],
                    "rules": ["safety_first_principle", "no_premature_victory_declaration_rule"],
                    "agent_future": "GeneralCoordinatorAgent"
                }
            },
            "detection": {
                "confidence_threshold": 0.7,
                "fallback_context": "DEFAULT",
                "keyword_priority": True
            }
        }
    
    def _build_keyword_map(self) -> Dict[str, str]:
        """Build keyword to context mapping for fast lookup."""
        keyword_map = {}
        for context_name, context_config in self.contexts.items():
            keywords = context_config.get("keywords", [])
            for keyword in keywords:
                keyword_map[keyword.lower()] = context_name
        return keyword_map
    
    def detect_context(self, user_message: str, open_files: List[str] = None, 
                      current_directory: str = None) -> ContextResult:
        """
        Detect development context using dual detection system.
        
        Args:
            user_message: User's input message
            open_files: List of currently open files (optional)
            current_directory: Current working directory (optional)
            
        Returns:
            ContextResult with detected context and confidence
        """
        if open_files is None:
            open_files = []
        if current_directory is None:
            current_directory = ""
        
        # Step 1: Check for explicit keywords (highest priority)
        explicit_context = self._check_explicit_keywords(user_message)
        if explicit_context:
            context_config = self.contexts[explicit_context]
            return ContextResult(
                context=explicit_context,
                method="explicit_keyword",
                confidence=1.0,
                reasoning=f"User specified {explicit_context} with keyword",
                rules=context_config["rules"],
                agent_future=context_config["agent_future"]
            )
        
        # Step 2: Automatic detection using pattern matching
        auto_context, confidence = self._auto_detect_context(
            user_message, open_files, current_directory
        )
        
        context_config = self.contexts[auto_context]
        
        if confidence >= self.detection_config["confidence_threshold"]:
            return ContextResult(
                context=auto_context,
                method="auto_detected",
                confidence=confidence,
                reasoning=f"Auto-detected based on patterns (confidence: {confidence:.1f})",
                rules=context_config["rules"],
                agent_future=context_config["agent_future"]
            )
        else:
            # Fallback to DEFAULT
            fallback_context = self.detection_config["fallback_context"]
            fallback_config = self.contexts[fallback_context]
            return ContextResult(
                context=fallback_context,
                method="fallback",
                confidence=0.5,
                reasoning="Low confidence in detection, using DEFAULT mode",
                rules=fallback_config["rules"],
                agent_future=fallback_config["agent_future"]
            )
    
    def _check_explicit_keywords(self, message: str) -> Optional[str]:
        """Check for explicit @keywords in user message."""
        message_lower = message.lower()
        
        # Check each keyword in our mapping
        for keyword, context in self.keyword_map.items():
            if keyword in message_lower:
                return context
        
        return None
    
    def _auto_detect_context(self, message: str, files: List[str], 
                           directory: str) -> Tuple[str, float]:
        """
        Automatically detect context using pattern matching.
        
        Returns:
            Tuple of (context_name, confidence_score)
        """
        context_scores = {}
        weights = self.detection_config.get("scoring_weights", {
            "message_patterns": 2,
            "file_patterns": 1,
            "directory_patterns": 1
        })
        
        # Initialize scores
        for context_name in self.contexts.keys():
            context_scores[context_name] = 0
        
        # Analyze message patterns
        message_lower = message.lower()
        for context_name, context_config in self.contexts.items():
            auto_detect = context_config.get("auto_detect_patterns", {})
            message_patterns = auto_detect.get("message", [])
            
            for pattern in message_patterns:
                if pattern.lower() in message_lower:
                    context_scores[context_name] += weights["message_patterns"]
        
        # Analyze file patterns
        for file_path in files:
            file_lower = file_path.lower()
            for context_name, context_config in self.contexts.items():
                auto_detect = context_config.get("auto_detect_patterns", {})
                file_patterns = auto_detect.get("files", [])
                
                for pattern in file_patterns:
                    if self._match_pattern(pattern.lower(), file_lower):
                        context_scores[context_name] += weights["file_patterns"]
        
        # Analyze directory patterns
        directory_lower = directory.lower()
        for context_name, context_config in self.contexts.items():
            auto_detect = context_config.get("auto_detect_patterns", {})
            dir_patterns = auto_detect.get("directories", [])
            
            for pattern in dir_patterns:
                if pattern.lower() in directory_lower:
                    context_scores[context_name] += weights["directory_patterns"]
        
        # Find best context
        if not context_scores or max(context_scores.values()) == 0:
            return self.detection_config["fallback_context"], 0.0
        
        best_context = max(context_scores.items(), key=lambda x: x[1])
        max_possible_score = self.detection_config.get("normalization", {}).get("max_score", 5)
        confidence = min(best_context[1] / max_possible_score, 1.0)
        
        return best_context[0], confidence
    
    def _match_pattern(self, pattern: str, text: str) -> bool:
        """Simple pattern matching with wildcard support."""
        if "*" in pattern:
            # Simple wildcard matching
            if pattern.startswith("*") and pattern.endswith("*"):
                return pattern[1:-1] in text
            elif pattern.startswith("*"):
                return text.endswith(pattern[1:])
            elif pattern.endswith("*"):
                return text.startswith(pattern[:-1])
        return pattern in text
    
    def apply_context_rules(self, context_result: ContextResult) -> RuleApplicationResult:
        """
        Apply rules based on detected context and return metrics.
        
        Args:
            context_result: Result from context detection
            
        Returns:
            RuleApplicationResult with efficiency metrics
        """
        total_available_rules = self.config.get("total_available_rules", 39)
        active_rule_count = len(context_result.rules)
        efficiency_improvement = ((total_available_rules - active_rule_count) / total_available_rules) * 100
        
        # Create result
        result = RuleApplicationResult(
            context=context_result.context,
            active_rules=context_result.rules,
            total_rules_available=total_available_rules,
            efficiency_improvement=efficiency_improvement,
            agent_future=context_result.agent_future,
            detection_confidence=context_result.confidence
        )
        
        # Update session statistics
        self._update_session_stats(context_result, result)
        
        return result
    
    def _update_session_stats(self, context_result: ContextResult, 
                            rule_result: RuleApplicationResult):
        """Update session statistics for monitoring and learning."""
        context = context_result.context
        
        # Track context usage
        if context not in self.session_stats["contexts_detected"]:
            self.session_stats["contexts_detected"][context] = 0
        self.session_stats["contexts_detected"][context] += 1
        
        # Track performance metrics
        self.session_stats["performance_metrics"].append({
            "context": context,
            "method": context_result.method,
            "confidence": context_result.confidence,
            "efficiency_improvement": rule_result.efficiency_improvement,
            "rule_count": len(rule_result.active_rules)
        })
    
    def get_session_summary(self) -> Dict:
        """Get summary of session performance and statistics."""
        total_detections = sum(self.session_stats["contexts_detected"].values())
        avg_efficiency = 0
        avg_confidence = 0
        
        if self.session_stats["performance_metrics"]:
            metrics = self.session_stats["performance_metrics"]
            avg_efficiency = sum(m["efficiency_improvement"] for m in metrics) / len(metrics)
            avg_confidence = sum(m["confidence"] for m in metrics) / len(metrics)
        
        return {
            "total_context_detections": total_detections,
            "context_distribution": self.session_stats["contexts_detected"],
            "average_efficiency_improvement": avg_efficiency,
            "average_detection_confidence": avg_confidence,
            "agent_swarm_readiness": self._calculate_agent_readiness()
        }
    
    def _calculate_agent_readiness(self) -> float:
        """Calculate readiness score for agent swarm transition."""
        if not self.session_stats["performance_metrics"]:
            return 0.0
        
        metrics = self.session_stats["performance_metrics"]
        
        # Factors for agent swarm readiness
        avg_confidence = sum(m["confidence"] for m in metrics) / len(metrics)
        context_diversity = len(self.session_stats["contexts_detected"])
        efficiency_score = sum(m["efficiency_improvement"] for m in metrics) / len(metrics) / 100
        
        # Weighted readiness score
        readiness = (avg_confidence * 0.4 + 
                    min(context_diversity / 5, 1.0) * 0.3 + 
                    efficiency_score * 0.3)
        
        return min(readiness, 1.0)
    
    def display_context_result(self, context_result: ContextResult, 
                             rule_result: RuleApplicationResult):
        """Display context detection and rule application results."""
        print(f"🎯 **Context Detected**: {context_result.context}")
        print(f"📋 **Detection Method**: {context_result.method}")
        print(f"🔍 **Reasoning**: {context_result.reasoning}")
        print(f"📊 **Rules Active**: {len(rule_result.active_rules)} rules loaded")
        print(f"⚡ **Efficiency**: {rule_result.efficiency_improvement:.0f}% reduction from full rule set")
        print(f"🤖 **Future Agent**: {context_result.agent_future}")
        print(f"📝 **Active Rules**: {', '.join(rule_result.active_rules)}")
        
        if context_result.confidence < 0.8:
            print(f"⚠️  **Note**: Detection confidence is {context_result.confidence:.1f}. Consider using explicit @keywords for better accuracy.")


# Convenience function for easy usage
def detect_and_apply_context(user_message: str, open_files: List[str] = None, 
                           current_directory: str = None) -> Tuple[ContextResult, RuleApplicationResult]:
    """
    Convenience function to detect context and apply rules in one call.
    
    Args:
        user_message: User's input message
        open_files: List of currently open files (optional)
        current_directory: Current working directory (optional)
        
    Returns:
        Tuple of (ContextResult, RuleApplicationResult)
    """
    detector = IntelligentContextDetector()
    context_result = detector.detect_context(user_message, open_files, current_directory)
    rule_result = detector.apply_context_rules(context_result)
    detector.display_context_result(context_result, rule_result)
    
    return context_result, rule_result


if __name__ == "__main__":
    # Example usage and testing
    detector = IntelligentContextDetector()
    
    # Test cases
    test_cases = [
        ("@code Let's implement the authentication system", [], ""),
        ("I need to debug this failing test", ["test_auth.py"], "tests/"),
        ("Let's design the system architecture", [], "docs/architecture/"),
        ("@agile Update the sprint backlog", ["sprint_1.md"], "docs/agile/"),
        ("Help me with the project", [], "")
    ]
    
    print("🧪 **Testing Intelligent Context Detection System**\n")
    
    for i, (message, files, directory) in enumerate(test_cases, 1):
        print(f"**Test Case {i}:**")
        print(f"Message: '{message}'")
        print(f"Files: {files}")
        print(f"Directory: '{directory}'")
        print()
        
        context_result, rule_result = detect_and_apply_context(message, files, directory)
        print("\n" + "="*60 + "\n")
    
    # Display session summary
    summary = detector.get_session_summary()
    print("📊 **Session Summary:**")
    for key, value in summary.items():
        print(f"   {key}: {value}")
