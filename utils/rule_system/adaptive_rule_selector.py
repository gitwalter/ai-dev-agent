#!/usr/bin/env python3
"""
Adaptive Rule Selector

AI-powered intelligent rule selection system that analyzes context, task type,
and historical patterns to automatically select and prioritize the most appropriate
rules for any given development situation.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
import statistics

@dataclass
class RuleContext:
    """Context information for rule selection."""
    task_type: str
    complexity: str
    domain: str
    file_types: List[str]
    project_size: str
    team_size: int
    time_pressure: float  # 0.0 (no pressure) to 1.0 (urgent)
    quality_requirements: float  # 0.0 (minimum) to 1.0 (maximum)

@dataclass
class RuleMatch:
    """Rule matching result with confidence score."""
    rule_name: str
    confidence_score: float
    relevance_reasons: List[str]
    application_priority: int
    estimated_impact: float

class AdaptiveRuleSelector:
    """
    Intelligent rule selection system using context analysis and machine learning.
    
    This system automatically selects the most appropriate rules for any given
    development task based on context analysis, historical performance data,
    and intelligent pattern recognition.
    """
    
    def __init__(self, analytics_file: Path = None):
        self.analytics_file = analytics_file or Path('monitoring/rule_selection_analytics.json')
        self.analytics_file.parent.mkdir(parents=True, exist_ok=True)
        self.selection_history = self._load_selection_history()
        self.rule_definitions = self._load_rule_definitions()
        
    def select_optimal_rules(self, 
                           task_description: str,
                           context: RuleContext) -> List[RuleMatch]:
        """
        Select optimal rules for a given task and context.
        
        Args:
            task_description: Natural language description of the task
            context: Structured context information
            
        Returns:
            List of matched rules with confidence scores and priorities
        """
        # Analyze task description for keywords and intent
        task_analysis = self._analyze_task_description(task_description)
        
        # Get all available rules
        available_rules = self._get_available_rules()
        
        # Score each rule for relevance
        rule_matches = []
        for rule_name in available_rules:
            confidence = self._calculate_rule_confidence(
                rule_name, task_analysis, context
            )
            
            if confidence > 0.3:  # Only include rules with reasonable confidence
                match = RuleMatch(
                    rule_name=rule_name,
                    confidence_score=confidence,
                    relevance_reasons=self._explain_rule_relevance(rule_name, task_analysis, context),
                    application_priority=self._calculate_priority(rule_name, confidence, context),
                    estimated_impact=self._estimate_rule_impact(rule_name, context)
                )
                rule_matches.append(match)
        
        # Sort by priority and confidence
        rule_matches.sort(key=lambda x: (x.application_priority, x.confidence_score), reverse=True)
        
        # Record selection for learning
        self._record_selection(task_description, context, rule_matches)
        
        return rule_matches
    
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
        """Extract relevant keywords from text."""
        # Define keyword categories
        keyword_patterns = {
            'file_operations': r'\b(move|copy|delete|organize|structure|file|directory)\b',
            'documentation': r'\b(document|readme|changelog|update|doc|write)\b',
            'testing': r'\b(test|verify|validate|check|ensure|confirm)\b',
            'quality': r'\b(quality|improve|refactor|clean|optimize|excellent)\b',
            'organization': r'\b(organize|structure|arrange|order|sort|place)\b',
            'automation': r'\b(automate|automatic|script|pipeline|process)\b',
            'security': r'\b(secure|encrypt|auth|permission|access|key)\b',
            'performance': r'\b(fast|slow|performance|optimize|efficiency|speed)\b'
        }
        
        extracted_keywords = []
        text_lower = text.lower()
        
        for category, pattern in keyword_patterns.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                extracted_keywords.extend([category] + matches)
        
        return list(set(extracted_keywords))
    
    def _classify_intent(self, text: str) -> str:
        """Classify the intent of the task description."""
        intent_patterns = {
            'create': r'\b(create|add|new|build|implement|develop)\b',
            'modify': r'\b(change|update|modify|edit|alter|fix)\b',
            'organize': r'\b(organize|structure|arrange|move|place)\b',
            'optimize': r'\b(optimize|improve|enhance|refactor|speed)\b',
            'validate': r'\b(test|check|verify|validate|ensure)\b',
            'document': r'\b(document|write|update|changelog|readme)\b',
            'debug': r'\b(debug|fix|error|problem|issue|bug)\b',
            'deploy': r'\b(deploy|release|launch|publish|install)\b'
        }
        
        text_lower = text.lower()
        intent_scores = {}
        
        for intent, pattern in intent_patterns.items():
            matches = len(re.findall(pattern, text_lower))
            intent_scores[intent] = matches
        
        # Return the intent with highest score
        return max(intent_scores.items(), key=lambda x: x[1])[0] if intent_scores else 'general'
    
    def _assess_urgency(self, text: str) -> float:
        """Assess urgency level from text (0.0 to 1.0)."""
        urgency_indicators = {
            'high': r'\b(urgent|critical|immediate|asap|emergency|now)\b',
            'medium': r'\b(soon|priority|important|needed)\b',
            'low': r'\b(later|when|eventually|someday)\b'
        }
        
        text_lower = text.lower()
        high_matches = len(re.findall(urgency_indicators['high'], text_lower))
        medium_matches = len(re.findall(urgency_indicators['medium'], text_lower))
        low_matches = len(re.findall(urgency_indicators['low'], text_lower))
        
        if high_matches > 0:
            return 0.9
        elif medium_matches > 0:
            return 0.6
        elif low_matches > 0:
            return 0.3
        else:
            return 0.5  # Default medium urgency
    
    def _calculate_rule_confidence(self, 
                                 rule_name: str,
                                 task_analysis: Dict[str, Any],
                                 context: RuleContext) -> float:
        """Calculate confidence score for rule applicability."""
        confidence_factors = []
        
        # Keyword matching confidence
        keyword_confidence = self._calculate_keyword_confidence(rule_name, task_analysis['keywords'])
        confidence_factors.append(('keywords', keyword_confidence, 0.3))
        
        # Intent matching confidence
        intent_confidence = self._calculate_intent_confidence(rule_name, task_analysis['intent'])
        confidence_factors.append(('intent', intent_confidence, 0.25))
        
        # Context matching confidence
        context_confidence = self._calculate_context_confidence(rule_name, context)
        confidence_factors.append(('context', context_confidence, 0.25))
        
        # Historical performance confidence
        historical_confidence = self._calculate_historical_confidence(rule_name, context)
        confidence_factors.append(('historical', historical_confidence, 0.2))
        
        # Calculate weighted confidence
        total_confidence = sum(
            factor_score * weight 
            for name, factor_score, weight in confidence_factors
        )
        
        return min(1.0, max(0.0, total_confidence))
    
    def _calculate_keyword_confidence(self, rule_name: str, keywords: List[str]) -> float:
        """Calculate confidence based on keyword matching."""
        rule_keywords = {
            'file_organization': ['file', 'move', 'organize', 'structure', 'directory', 'place'],
            'documentation': ['document', 'readme', 'changelog', 'update', 'doc', 'write'],
            'clean_repository': ['clean', 'temp', 'artifact', 'cleanup', 'remove'],
            'test_driven': ['test', 'verify', 'validate', 'check', 'ensure'],
            'boy_scout': ['improve', 'refactor', 'quality', 'optimize', 'excellent'],
            'courage': ['complete', 'finish', 'systematic', 'thorough', 'comprehensive'],
            'no_premature_victory': ['verify', 'confirm', 'evidence', 'proof', 'validate'],
            'context_awareness': ['read', 'understand', 'analyze', 'context', 'readme'],
            'model_selection': ['model', 'llm', 'ai', 'gemini', 'selection'],
            'secrets_management': ['secret', 'key', 'config', 'environment', 'secure']
        }
        
        rule_key = rule_name.lower().replace(' ', '_').replace('-', '_')
        relevant_keywords = set(rule_keywords.get(rule_key, []))
        
        if not relevant_keywords:
            return 0.5  # Default confidence for unknown rules
        
        keyword_set = set(k.lower() for k in keywords)
        overlap = len(keyword_set & relevant_keywords)
        
        return min(1.0, overlap / len(relevant_keywords)) if relevant_keywords else 0.5
    
    def _calculate_intent_confidence(self, rule_name: str, intent: str) -> float:
        """Calculate confidence based on intent matching."""
        rule_intents = {
            'file_organization': ['organize', 'create', 'modify'],
            'documentation': ['document', 'create', 'modify'],
            'clean_repository': ['organize', 'optimize', 'modify'],
            'test_driven': ['validate', 'create', 'debug'],
            'boy_scout': ['optimize', 'modify', 'organize'],
            'courage': ['validate', 'create', 'optimize'],
            'no_premature_victory': ['validate', 'debug'],
            'context_awareness': ['create', 'modify', 'validate'],
            'model_selection': ['create', 'optimize'],
            'secrets_management': ['create', 'modify']
        }
        
        rule_key = rule_name.lower().replace(' ', '_').replace('-', '_')
        supported_intents = rule_intents.get(rule_key, [])
        
        return 0.9 if intent in supported_intents else 0.4
    
    def _calculate_context_confidence(self, rule_name: str, context: RuleContext) -> float:
        """Calculate confidence based on context matching."""
        confidence_score = 0.5  # Base confidence
        
        # Adjust based on task type
        task_rule_mapping = {
            'file_operation': ['file_organization', 'clean_repository', 'boy_scout'],
            'documentation': ['documentation', 'context_awareness', 'live_updates'],
            'code_implementation': ['test_driven', 'boy_scout', 'model_selection'],
            'testing': ['test_driven', 'no_premature_victory', 'courage'],
            'deployment': ['clean_repository', 'secrets_management', 'courage']
        }
        
        rule_key = rule_name.lower().replace(' ', '_').replace('-', '_')
        relevant_tasks = [task for task, rules in task_rule_mapping.items() 
                         if any(rule_key in rule for rule in rules)]
        
        if context.task_type in relevant_tasks:
            confidence_score += 0.3
        
        # Adjust based on complexity
        if context.complexity == 'complex' and 'courage' in rule_key:
            confidence_score += 0.2
        elif context.complexity == 'simple' and 'kiss' in rule_key:
            confidence_score += 0.2
        
        # Adjust based on quality requirements
        if context.quality_requirements > 0.8:
            if any(keyword in rule_key for keyword in ['excellence', 'boy_scout', 'test_driven']):
                confidence_score += 0.2
        
        return min(1.0, confidence_score)
    
    def _calculate_historical_confidence(self, rule_name: str, context: RuleContext) -> float:
        """Calculate confidence based on historical performance."""
        # Look for similar past applications
        similar_contexts = [
            record for record in self.selection_history
            if record.get('context', {}).get('task_type') == context.task_type
        ]
        
        if not similar_contexts:
            return 0.5  # Default when no history
        
        # Find applications of this rule in similar contexts
        rule_applications = [
            record for record in similar_contexts
            if rule_name in [match['rule_name'] for match in record.get('selected_rules', [])]
        ]
        
        if not rule_applications:
            return 0.4  # Slightly lower when rule hasn't been used in this context
        
        # Calculate average success rate for this rule in similar contexts
        success_rates = []
        for record in rule_applications:
            rule_matches = record.get('selected_rules', [])
            for match in rule_matches:
                if match['rule_name'] == rule_name:
                    success_rates.append(match.get('success_rate', 0.5))
        
        return statistics.mean(success_rates) if success_rates else 0.5
    
    def _explain_rule_relevance(self, 
                              rule_name: str,
                              task_analysis: Dict[str, Any],
                              context: RuleContext) -> List[str]:
        """Generate human-readable explanations for why a rule is relevant."""
        reasons = []
        
        # Keyword-based reasons
        keywords = task_analysis.get('keywords', [])
        rule_key = rule_name.lower().replace(' ', '_').replace('-', '_')
        
        if 'file' in keywords and 'organization' in rule_key:
            reasons.append("Task involves file operations that require organization")
        
        if 'test' in keywords and 'test_driven' in rule_key:
            reasons.append("Task requires testing and validation")
        
        if 'document' in keywords and 'documentation' in rule_key:
            reasons.append("Task involves documentation updates")
        
        # Context-based reasons
        if context.quality_requirements > 0.8:
            if any(keyword in rule_key for keyword in ['excellence', 'boy_scout']):
                reasons.append("High quality requirements justify excellence-focused rules")
        
        if context.complexity == 'complex':
            if 'courage' in rule_key:
                reasons.append("Complex tasks benefit from systematic completion approaches")
        
        # Intent-based reasons
        intent = task_analysis.get('intent', '')
        if intent == 'organize' and 'organization' in rule_key:
            reasons.append("Organization intent aligns with file organization rules")
        
        return reasons if reasons else ["General applicability based on context"]
    
    def _calculate_priority(self, rule_name: str, confidence: float, context: RuleContext) -> int:
        """Calculate application priority (1-10, higher is more important)."""
        base_priority = int(confidence * 10)
        
        # Foundation rules get higher priority
        foundation_rules = ['context_awareness', 'no_premature_victory', 'clean_repository']
        rule_key = rule_name.lower().replace(' ', '_').replace('-', '_')
        
        if any(foundation in rule_key for foundation in foundation_rules):
            base_priority += 2
        
        # Quality rules get higher priority for high-quality contexts
        if context.quality_requirements > 0.8:
            quality_rules = ['excellence', 'boy_scout', 'test_driven']
            if any(quality in rule_key for quality in quality_rules):
                base_priority += 1
        
        return min(10, max(1, base_priority))
    
    def _estimate_rule_impact(self, rule_name: str, context: RuleContext) -> float:
        """Estimate the potential impact of applying this rule."""
        # Base impact scores for different rule types
        rule_impacts = {
            'file_organization': 0.7,
            'documentation': 0.8,
            'test_driven': 0.9,
            'boy_scout': 0.8,
            'courage': 0.9,
            'excellence': 0.95,
            'clean_repository': 0.6,
            'context_awareness': 0.85
        }
        
        rule_key = rule_name.lower().replace(' ', '_').replace('-', '_')
        base_impact = 0.5  # Default impact
        
        for rule_type, impact in rule_impacts.items():
            if rule_type in rule_key:
                base_impact = impact
                break
        
        # Adjust based on context
        if context.quality_requirements > 0.8:
            base_impact *= 1.1  # Higher impact in quality-focused contexts
        
        if context.complexity == 'complex':
            base_impact *= 1.05  # Slightly higher impact for complex tasks
        
        return min(1.0, base_impact)
    
    def _get_available_rules(self) -> List[str]:
        """Get list of available rules."""
        # This would typically load from a rule registry
        # For now, return common rules
        return [
            "File Organization Rule",
            "Live Documentation Updates Rule", 
            "Clean Repository Focus Rule",
            "Context Awareness and Excellence Rule",
            "No Premature Victory Declaration Rule",
            "Boy Scout Rule",
            "Courage Rule",
            "Test-Driven Development Rule",
            "Model Selection Rule",
            "Streamlit Secrets Management Rule",
            "Best Practices and Standard Libraries Rule",
            "Don't Repeat Yourself (DRY) Rule",
            "Keep It Small and Simple (KISS) Rule",
            "Object-Oriented Programming Rule",
            "Clear Documentation Rule",
            "No Silent Errors and Mock Fallbacks Rule"
        ]
    
    def _record_selection(self, 
                        task_description: str,
                        context: RuleContext,
                        selected_rules: List[RuleMatch]) -> None:
        """Record rule selection for machine learning."""
        record = {
            'timestamp': datetime.now().isoformat(),
            'task_description': task_description,
            'context': asdict(context),
            'selected_rules': [asdict(rule) for rule in selected_rules],
            'selection_hash': hashlib.md5(
                (task_description + str(asdict(context))).encode()
            ).hexdigest()
        }
        
        self.selection_history.append(record)
        self._save_selection_history()
    
    def _load_selection_history(self) -> List[Dict[str, Any]]:
        """Load selection history for machine learning."""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_selection_history(self) -> None:
        """Save selection history."""
        with open(self.analytics_file, 'w') as f:
            json.dump(self.selection_history, f, indent=2)
    
    def _load_rule_definitions(self) -> Dict[str, Any]:
        """Load rule definitions and metadata."""
        # This would typically load from rule files
        # For now, return empty dict
        return {}
    
    def generate_selection_report(self, task_description: str, context: RuleContext) -> str:
        """Generate a comprehensive rule selection report."""
        matches = self.select_optimal_rules(task_description, context)
        
        report = []
        report.append("🧠 ADAPTIVE RULE SELECTION REPORT")
        report.append("=" * 50)
        report.append("")
        report.append(f"**Task**: {task_description}")
        report.append(f"**Context**: {context.task_type} | {context.complexity} | Quality: {context.quality_requirements}")
        report.append("")
        
        if matches:
            report.append("📋 **RECOMMENDED RULES** (by priority)")
            for i, match in enumerate(matches[:10], 1):
                report.append(f"{i}. **{match.rule_name}**")
                report.append(f"   Confidence: {match.confidence_score:.1%}")
                report.append(f"   Priority: {match.application_priority}/10")
                report.append(f"   Impact: {match.estimated_impact:.1%}")
                report.append(f"   Reasons: {', '.join(match.relevance_reasons)}")
                report.append("")
        else:
            report.append("⚠️ **No highly relevant rules identified**")
            report.append("Consider general best practices and project standards")
        
        return "\n".join(report)

def demo_adaptive_selector():
    """Demonstrate the adaptive rule selector."""
    print("🧠 ADAPTIVE RULE SELECTOR DEMO")
    print("=" * 50)
    
    selector = AdaptiveRuleSelector()
    
    # Test scenarios
    scenarios = [
        {
            'description': "Move Python files from root directory to correct locations",
            'context': RuleContext(
                task_type='file_operation',
                complexity='simple',
                domain='project_management',
                file_types=['py', 'json'],
                project_size='medium',
                team_size=1,
                time_pressure=0.3,
                quality_requirements=0.95
            )
        },
        {
            'description': "Implement comprehensive test coverage for all agents",
            'context': RuleContext(
                task_type='testing',
                complexity='complex',
                domain='software_testing',
                file_types=['py'],
                project_size='large',
                team_size=1,
                time_pressure=0.8,
                quality_requirements=1.0
            )
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"🎯 **SCENARIO {i}**")
        print(selector.generate_selection_report(
            scenario['description'], 
            scenario['context']
        ))
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    demo_adaptive_selector()
