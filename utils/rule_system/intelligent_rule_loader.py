#!/usr/bin/env python3
"""
Intelligent Rule Loader

Dynamic rule selection system that loads only the most relevant rules based on
task context, complexity, and requirements. This replaces the inefficient
"load all rules" approach with intelligent, context-aware selection.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Task type classification for intelligent rule selection."""
    FILE_OPERATION = "file_operation"
    CODE_IMPLEMENTATION = "code_implementation"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    REFACTORING = "refactoring"
    DEBUGGING = "debugging"
    DEPLOYMENT = "deployment"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    INTEGRATION = "integration"
    ANALYSIS = "analysis"
    SETUP = "setup"

class TaskComplexity(Enum):
    """Task complexity levels for rule selection."""
    TRIVIAL = 1      # Single file operations, simple changes
    SIMPLE = 2       # Basic implementation tasks
    MODERATE = 3     # Multi-file changes, moderate complexity
    COMPLEX = 4      # System-wide changes, architectural modifications
    CRITICAL = 5     # Major refactoring, system overhauls

@dataclass
class TaskContext:
    """Context information for intelligent rule selection."""
    task_type: TaskType
    complexity: TaskComplexity
    domain: str = "general"
    file_types: List[str] = field(default_factory=list)
    project_size: str = "medium"
    team_size: int = 1
    time_pressure: float = 0.5  # 0.0 (no pressure) to 1.0 (urgent)
    quality_requirements: float = 0.8  # 0.0 (minimum) to 1.0 (maximum)
    security_requirements: float = 0.5  # 0.0 (low) to 1.0 (high)
    performance_requirements: float = 0.5  # 0.0 (low) to 1.0 (high)

@dataclass
class RuleSelection:
    """Result of intelligent rule selection."""
    selected_rules: List[str]
    excluded_rules: List[str]
    selection_reasoning: Dict[str, str]
    confidence_score: float
    estimated_token_savings: int
    expected_effectiveness: float

class IntelligentRuleLoader:
    """
    Intelligent rule selection system that dynamically loads only relevant rules.
    
    This system analyzes task context and selects the most appropriate rules,
    dramatically reducing token usage while maintaining excellence standards.
    """
    
    def __init__(self):
        self.rule_definitions = self._load_rule_definitions()
        self.selection_history = {}
        self.performance_metrics = {}
        
    def select_rules_for_task(self, task_description: str, context: TaskContext) -> RuleSelection:
        """
        Select optimal rules for a given task and context.
        
        Args:
            task_description: Natural language description of the task
            context: Structured context information
            
        Returns:
            Intelligent rule selection with reasoning and metrics
        """
        # Analyze task description
        task_analysis = self._analyze_task_description(task_description)
        
        # Get all available rules
        available_rules = list(self.rule_definitions.keys())
        
        # Score rules for relevance
        rule_scores = {}
        for rule_name in available_rules:
            score = self._calculate_rule_relevance(rule_name, task_analysis, context)
            rule_scores[rule_name] = score
        
        # Select rules above relevance threshold
        relevance_threshold = self._get_relevance_threshold(context)
        selected_rules = [
            rule for rule, score in rule_scores.items() 
            if score >= relevance_threshold
        ]
        
        # Ensure critical foundation rules are always included
        critical_rules = self._get_critical_foundation_rules()
        for rule in critical_rules:
            if rule not in selected_rules:
                selected_rules.append(rule)
        
        # Calculate excluded rules
        excluded_rules = [rule for rule in available_rules if rule not in selected_rules]
        
        # Generate selection reasoning
        reasoning = self._generate_selection_reasoning(selected_rules, excluded_rules, task_analysis, context)
        
        # Calculate metrics
        confidence_score = self._calculate_confidence_score(selected_rules, task_analysis)
        token_savings = self._calculate_token_savings(selected_rules, available_rules)
        effectiveness = self._calculate_expected_effectiveness(selected_rules, context)
        
        # Record selection for learning
        self._record_selection(task_description, context, selected_rules, excluded_rules)
        
        return RuleSelection(
            selected_rules=selected_rules,
            excluded_rules=excluded_rules,
            selection_reasoning=reasoning,
            confidence_score=confidence_score,
            estimated_token_savings=token_savings,
            expected_effectiveness=effectiveness
        )
    
    def _load_rule_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive rule definitions with selection criteria."""
        return {
            # CRITICAL FOUNDATION RULES (Always included)
            "SAFETY FIRST PRINCIPLE": {
                "priority": "CRITICAL",
                "always_include": True,
                "keywords": ["safety", "security", "protection", "harm", "danger"],
                "task_types": ["ALL"],
                "complexity_levels": ["ALL"],
                "token_cost": 150
            },
            
            "Context Awareness and Excellence Rule": {
                "priority": "CRITICAL",
                "always_include": True,
                "keywords": ["context", "read", "understand", "documentation", "excellence"],
                "task_types": ["ALL"],
                "complexity_levels": ["ALL"],
                "token_cost": 200
            },
            
            "No Premature Victory Declaration Rule": {
                "priority": "CRITICAL",
                "always_include": True,
                "keywords": ["success", "complete", "victory", "evidence", "validation"],
                "task_types": ["ALL"],
                "complexity_levels": ["ALL"],
                "token_cost": 180
            },
            
            # FILE OPERATION RULES
            "File Organization Rule": {
                "priority": "HIGH",
                "always_include": False,
                "keywords": ["file", "organize", "structure", "move", "directory", "folder"],
                "task_types": [TaskType.FILE_OPERATION, TaskType.SETUP],
                "complexity_levels": ["ALL"],
                "token_cost": 120
            },
            
            "Clean Repository Focus Rule": {
                "priority": "HIGH",
                "always_include": False,
                "keywords": ["clean", "repository", "temporary", "cleanup", "organize"],
                "task_types": [TaskType.FILE_OPERATION, TaskType.CODE_IMPLEMENTATION],
                "complexity_levels": ["ALL"],
                "token_cost": 100
            },
            
            # CODE IMPLEMENTATION RULES
            "Test-Driven Development Rule": {
                "priority": "HIGH",
                "always_include": False,
                "keywords": ["test", "testing", "tdd", "unit", "integration", "verify"],
                "task_types": [TaskType.CODE_IMPLEMENTATION, TaskType.TESTING, TaskType.REFACTORING],
                "complexity_levels": [TaskComplexity.SIMPLE, TaskComplexity.MODERATE, TaskComplexity.COMPLEX, TaskComplexity.CRITICAL],
                "token_cost": 250
            },
            
            "Best Practices and Standard Libraries Rule": {
                "priority": "HIGH",
                "always_include": False,
                "keywords": ["best", "practice", "standard", "library", "framework", "pattern"],
                "task_types": [TaskType.CODE_IMPLEMENTATION, TaskType.REFACTORING, TaskType.ARCHITECTURE],
                "complexity_levels": ["ALL"],
                "token_cost": 180
            },
            
            "Object-Oriented Programming Rule": {
                "priority": "MEDIUM",
                "always_include": False,
                "keywords": ["class", "object", "oop", "design", "pattern", "architecture"],
                "task_types": [TaskType.CODE_IMPLEMENTATION, TaskType.ARCHITECTURE, TaskType.REFACTORING],
                "complexity_levels": [TaskComplexity.MODERATE, TaskComplexity.COMPLEX, TaskComplexity.CRITICAL],
                "token_cost": 300
            },
            
            "Don't Repeat Yourself (DRY) Rule": {
                "priority": "HIGH",
                "always_include": False,
                "keywords": ["dry", "repeat", "duplicate", "refactor", "extract", "reuse"],
                "task_types": [TaskType.CODE_IMPLEMENTATION, TaskType.REFACTORING],
                "complexity_levels": ["ALL"],
                "token_cost": 120
            },
            
            # DOCUMENTATION RULES
            "Live Documentation Updates Rule": {
                "priority": "HIGH",
                "always_include": False,
                "keywords": ["document", "documentation", "readme", "update", "comment"],
                "task_types": [TaskType.DOCUMENTATION, TaskType.CODE_IMPLEMENTATION],
                "complexity_levels": ["ALL"],
                "token_cost": 200
            },
            
            "Clear Documentation Rule": {
                "priority": "HIGH",
                "always_include": False,
                "keywords": ["document", "clear", "explain", "comment", "readme"],
                "task_types": [TaskType.DOCUMENTATION, TaskType.CODE_IMPLEMENTATION],
                "complexity_levels": ["ALL"],
                "token_cost": 150
            },
            
            # SECURITY RULES
            "Streamlit Secrets Management Rule": {
                "priority": "HIGH",
                "always_include": False,
                "keywords": ["secret", "api", "key", "password", "security", "streamlit"],
                "task_types": [TaskType.SECURITY, TaskType.CONFIGURATION, TaskType.CODE_IMPLEMENTATION],
                "complexity_levels": ["ALL"],
                "token_cost": 120
            },
            
            "No Silent Errors and Mock Fallbacks Rule": {
                "priority": "HIGH",
                "always_include": False,
                "keywords": ["error", "silent", "fallback", "mock", "exception", "fail"],
                "task_types": [TaskType.CODE_IMPLEMENTATION, TaskType.DEBUGGING, TaskType.TESTING],
                "complexity_levels": ["ALL"],
                "token_cost": 180
            },
            
            # QUALITY RULES
            "Keep It Small and Simple (KISS) Rule": {
                "priority": "MEDIUM",
                "always_include": False,
                "keywords": ["simple", "small", "kiss", "complex", "over", "engineer"],
                "task_types": [TaskType.CODE_IMPLEMENTATION, TaskType.REFACTORING, TaskType.ARCHITECTURE],
                "complexity_levels": ["ALL"],
                "token_cost": 100
            },
            
            "Philosophy of Excellence": {
                "priority": "HIGH",
                "always_include": False,
                "keywords": ["excellence", "quality", "best", "perfect", "optimize", "improve"],
                "task_types": ["ALL"],
                "complexity_levels": ["ALL"],
                "token_cost": 250
            },
            
            # PERFORMANCE RULES
            "Active Knowledge Extension and Research Rule": {
                "priority": "MEDIUM",
                "always_include": False,
                "keywords": ["research", "knowledge", "learn", "study", "investigate", "analyze"],
                "task_types": [TaskType.ANALYSIS, TaskType.ARCHITECTURE, TaskType.CODE_IMPLEMENTATION],
                "complexity_levels": [TaskComplexity.MODERATE, TaskComplexity.COMPLEX, TaskComplexity.CRITICAL],
                "token_cost": 400
            },
            
            # META RULES
            "Meta-Rule: Systematic Rule Application Coordination": {
                "priority": "MEDIUM",
                "always_include": False,
                "keywords": ["rule", "systematic", "coordination", "meta", "framework"],
                "task_types": ["ALL"],
                "complexity_levels": [TaskComplexity.MODERATE, TaskComplexity.COMPLEX, TaskComplexity.CRITICAL],
                "token_cost": 300
            }
        }
    
    def _analyze_task_description(self, description: str) -> Dict[str, Any]:
        """Analyze task description to extract intent and keywords."""
        analysis = {
            'keywords': self._extract_keywords(description),
            'intent': self._classify_intent(description),
            'urgency': self._assess_urgency(description),
            'scope': self._assess_scope(description),
            'complexity_indicators': self._identify_complexity_indicators(description)
        }
        return analysis
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from task description."""
        keyword_patterns = {
            'file_ops': r'\b(move|copy|delete|organize|structure|file|directory|folder)\b',
            'code_ops': r'\b(implement|create|write|develop|build|code|function|class)\b',
            'testing': r'\b(test|testing|verify|validate|check|ensure|confirm|assert)\b',
            'documentation': r'\b(document|documentation|readme|changelog|update|doc|write|comment)\b',
            'quality': r'\b(quality|improve|refactor|clean|optimize|excellent|best)\b',
            'security': r'\b(secure|encrypt|auth|authentication|permission|access|key|vulnerability)\b',
            'performance': r'\b(fast|slow|performance|optimize|efficiency|speed|bottleneck)\b',
            'debugging': r'\b(debug|fix|error|problem|issue|bug|troubleshoot)\b',
            'deployment': r'\b(deploy|release|launch|publish|install|configure)\b',
            'integration': r'\b(integrate|connect|api|service|endpoint|interface)\b',
            'research': r'\b(research|learn|study|investigate|analyze|understand)\b',
            'simple': r'\b(simple|easy|basic|straightforward|clear)\b',
            'complex': r'\b(complex|complicated|difficult|advanced|sophisticated)\b'
        }
        
        extracted = []
        text_lower = text.lower()
        
        for category, pattern in keyword_patterns.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                extracted.extend([category] + matches)
        
        return list(set(extracted))
    
    def _classify_intent(self, text: str) -> str:
        """Classify task intent for rule selection."""
        intent_patterns = {
            'create': r'\b(create|add|new|build|implement|develop|generate)\b',
            'modify': r'\b(change|update|modify|edit|alter|fix|improve)\b',
            'organize': r'\b(organize|structure|arrange|move|place|sort|order)\b',
            'validate': r'\b(test|check|verify|validate|ensure|confirm|review)\b',
            'optimize': r'\b(optimize|improve|enhance|refactor|speed|efficiency)\b',
            'debug': r'\b(debug|fix|error|problem|issue|bug|troubleshoot)\b',
            'deploy': r'\b(deploy|release|launch|publish|install|configure)\b',
            'secure': r'\b(secure|protect|encrypt|auth|permission|access)\b'
        }
        
        text_lower = text.lower()
        intent_scores = {}
        
        for intent, pattern in intent_patterns.items():
            matches = len(re.findall(pattern, text_lower))
            intent_scores[intent] = matches
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return 'general'
    
    def _assess_urgency(self, text: str) -> float:
        """Assess urgency level from task description."""
        urgency_indicators = [
            r'\b(urgent|asap|immediately|now|quick|fast|hurry)\b',
            r'\b(critical|important|priority|deadline)\b',
            r'\b(fix|broken|error|fail|crash)\b'
        ]
        
        text_lower = text.lower()
        urgency_score = 0.0
        
        for pattern in urgency_indicators:
            matches = len(re.findall(pattern, text_lower))
            urgency_score += matches * 0.2
        
        return min(urgency_score, 1.0)
    
    def _assess_scope(self, text: str) -> str:
        """Assess task scope from description."""
        scope_indicators = {
            'small': [r'\b(single|one|simple|basic|minor)\b'],
            'medium': [r'\b(few|several|moderate|standard)\b'],
            'large': [r'\b(many|multiple|major|comprehensive|full)\b'],
            'system': [r'\b(system|entire|all|complete|overall)\b']
        }
        
        text_lower = text.lower()
        scope_scores = {}
        
        for scope, patterns in scope_indicators.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            scope_scores[scope] = score
        
        if scope_scores:
            return max(scope_scores, key=scope_scores.get)
        return 'medium'
    
    def _identify_complexity_indicators(self, text: str) -> List[str]:
        """Identify complexity indicators in task description."""
        complexity_indicators = []
        
        simple_indicators = [r'\b(simple|easy|basic|straightforward|quick)\b']
        complex_indicators = [r'\b(complex|complicated|difficult|advanced|sophisticated)\b']
        
        text_lower = text.lower()
        
        for pattern in simple_indicators:
            if re.search(pattern, text_lower):
                complexity_indicators.append('simple')
        
        for pattern in complex_indicators:
            if re.search(pattern, text_lower):
                complexity_indicators.append('complex')
        
        return complexity_indicators
    
    def _calculate_rule_relevance(self, rule_name: str, task_analysis: Dict[str, Any], context: TaskContext) -> float:
        """Calculate relevance score for a rule based on task analysis and context."""
        rule_def = self.rule_definitions[rule_name]
        
        # Always include critical rules
        if rule_def.get("always_include", False):
            return 1.0
        
        # Check task type compatibility
        if not self._is_task_type_compatible(rule_def, context.task_type):
            return 0.0
        
        # Check complexity compatibility
        if not self._is_complexity_compatible(rule_def, context.complexity):
            return 0.0
        
        # Calculate keyword relevance
        keyword_relevance = self._calculate_keyword_relevance(rule_def, task_analysis['keywords'])
        
        # Calculate intent relevance
        intent_relevance = self._calculate_intent_relevance(rule_def, task_analysis['intent'])
        
        # Calculate context relevance
        context_relevance = self._calculate_context_relevance(rule_def, context)
        
        # Combine scores with weights
        relevance_score = (
            keyword_relevance * 0.4 +
            intent_relevance * 0.3 +
            context_relevance * 0.3
        )
        
        return relevance_score
    
    def _is_task_type_compatible(self, rule_def: Dict[str, Any], task_type: TaskType) -> bool:
        """Check if rule is compatible with task type."""
        task_types = rule_def.get("task_types", [])
        return "ALL" in task_types or task_type in task_types
    
    def _is_complexity_compatible(self, rule_def: Dict[str, Any], complexity: TaskComplexity) -> bool:
        """Check if rule is compatible with task complexity."""
        complexity_levels = rule_def.get("complexity_levels", [])
        return "ALL" in complexity_levels or complexity in complexity_levels
    
    def _calculate_keyword_relevance(self, rule_def: Dict[str, Any], task_keywords: List[str]) -> float:
        """Calculate keyword relevance score."""
        rule_keywords = rule_def.get("keywords", [])
        
        if not rule_keywords:
            return 0.5  # Neutral score if no keywords defined
        
        matches = 0
        for task_keyword in task_keywords:
            for rule_keyword in rule_keywords:
                # More flexible matching
                if (task_keyword.lower() in rule_keyword.lower() or 
                    rule_keyword.lower() in task_keyword.lower() or
                    task_keyword.lower() == rule_keyword.lower()):
                    matches += 1
        
        # Boost score for better matches
        relevance = min(matches / len(rule_keywords), 1.0)
        
        # Additional boost for exact matches
        exact_matches = sum(1 for tk in task_keywords for rk in rule_keywords if tk.lower() == rk.lower())
        if exact_matches > 0:
            relevance += 0.2
        
        return min(relevance, 1.0)
    
    def _calculate_intent_relevance(self, rule_def: Dict[str, Any], intent: str) -> float:
        """Calculate intent relevance score."""
        # This is a simplified implementation
        # In a more sophisticated system, you could have intent-specific relevance scores
        return 0.7  # Default moderate relevance
    
    def _calculate_context_relevance(self, rule_def: Dict[str, Any], context: TaskContext) -> float:
        """Calculate context relevance score."""
        relevance = 0.5  # Base relevance
        
        # Adjust based on quality requirements
        if context.quality_requirements > 0.8:
            relevance += 0.2
        
        # Adjust based on security requirements
        if context.security_requirements > 0.7 and "security" in rule_def.get("keywords", []):
            relevance += 0.2
        
        # Adjust based on performance requirements
        if context.performance_requirements > 0.7 and "performance" in rule_def.get("keywords", []):
            relevance += 0.2
        
        return min(relevance, 1.0)
    
    def _get_relevance_threshold(self, context: TaskContext) -> float:
        """Get relevance threshold based on context."""
        # Higher quality requirements = lower threshold (include more rules)
        # Higher time pressure = higher threshold (include fewer rules)
        
        base_threshold = 0.2  # Lower base threshold to include more relevant rules
        quality_adjustment = (1.0 - context.quality_requirements) * 0.15
        time_adjustment = context.time_pressure * 0.15
        
        threshold = base_threshold + quality_adjustment + time_adjustment
        return max(0.05, min(0.6, threshold))  # Lower max threshold
    
    def _get_critical_foundation_rules(self) -> List[str]:
        """Get list of critical foundation rules that should always be included."""
        return [
            "SAFETY FIRST PRINCIPLE",
            "Context Awareness and Excellence Rule", 
            "No Premature Victory Declaration Rule"
        ]
    
    def _generate_selection_reasoning(self, selected_rules: List[str], excluded_rules: List[str], 
                                    task_analysis: Dict[str, Any], context: TaskContext) -> Dict[str, str]:
        """Generate reasoning for rule selection decisions."""
        reasoning = {}
        
        for rule in selected_rules:
            rule_def = self.rule_definitions[rule]
            if rule_def.get("always_include", False):
                reasoning[rule] = "Critical foundation rule - always included"
            else:
                reasoning[rule] = f"Selected based on {context.task_type.value} task type and {context.complexity.value} complexity"
        
        for rule in excluded_rules:
            rule_def = self.rule_definitions[rule]
            reasoning[rule] = f"Excluded - not relevant for {context.task_type.value} task or below relevance threshold"
        
        return reasoning
    
    def _calculate_confidence_score(self, selected_rules: List[str], task_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for rule selection."""
        # Simplified confidence calculation
        # In a more sophisticated system, this could use historical performance data
        
        base_confidence = 0.7
        
        # Increase confidence if we have good keyword matches
        if len(task_analysis['keywords']) > 3:
            base_confidence += 0.1
        
        # Increase confidence if intent is clear
        if task_analysis['intent'] != 'general':
            base_confidence += 0.1
        
        # Increase confidence if we have critical rules
        critical_rules = self._get_critical_foundation_rules()
        if any(rule in selected_rules for rule in critical_rules):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _calculate_token_savings(self, selected_rules: List[str], available_rules: List[str]) -> int:
        """Calculate estimated token savings from intelligent selection."""
        total_tokens = sum(self.rule_definitions[rule].get("token_cost", 0) for rule in available_rules)
        selected_tokens = sum(self.rule_definitions[rule].get("token_cost", 0) for rule in selected_rules)
        
        return total_tokens - selected_tokens
    
    def _calculate_expected_effectiveness(self, selected_rules: List[str], context: TaskContext) -> float:
        """Calculate expected effectiveness of selected rules."""
        # Simplified effectiveness calculation
        # In a more sophisticated system, this could use historical performance data
        
        base_effectiveness = 0.8
        
        # Adjust based on rule count (more rules = potentially higher effectiveness)
        rule_count_factor = min(len(selected_rules) / 10, 1.0) * 0.1
        base_effectiveness += rule_count_factor
        
        # Adjust based on quality requirements
        quality_factor = context.quality_requirements * 0.1
        base_effectiveness += quality_factor
        
        return min(base_effectiveness, 1.0)
    
    def _record_selection(self, task_description: str, context: TaskContext, 
                         selected_rules: List[str], excluded_rules: List[str]) -> None:
        """Record rule selection for learning and optimization."""
        selection_record = {
            'timestamp': str(datetime.now()),
            'task_description': task_description,
            'context': {
                'task_type': context.task_type.value,
                'complexity': context.complexity.value,
                'domain': context.domain,
                'quality_requirements': context.quality_requirements,
                'time_pressure': context.time_pressure
            },
            'selected_rules': selected_rules,
            'excluded_rules': excluded_rules,
            'rule_count': len(selected_rules),
            'exclusion_count': len(excluded_rules)
        }
        
        # Store in selection history
        task_hash = hash(task_description + str(context))
        self.selection_history[task_hash] = selection_record
        
        logger.info(f"Recorded rule selection: {len(selected_rules)} selected, {len(excluded_rules)} excluded")
    
    def get_selection_summary(self) -> Dict[str, Any]:
        """Get summary of rule selection performance."""
        if not self.selection_history:
            return {"message": "No selection history available"}
        
        total_selections = len(self.selection_history)
        avg_rules_selected = sum(record['rule_count'] for record in self.selection_history.values()) / total_selections
        avg_rules_excluded = sum(record['exclusion_count'] for record in self.selection_history.values()) / total_selections
        
        return {
            "total_selections": total_selections,
            "average_rules_selected": round(avg_rules_selected, 2),
            "average_rules_excluded": round(avg_rules_excluded, 2),
            "average_exclusion_rate": round(avg_rules_excluded / (avg_rules_selected + avg_rules_excluded) * 100, 1)
        }

# Global instance for easy access
INTELLIGENT_RULE_LOADER = IntelligentRuleLoader()
