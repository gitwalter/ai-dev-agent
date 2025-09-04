#!/usr/bin/env python3
"""
Context-Aware Story Integration System.

This module integrates automatic user story detection with the context-aware rule system,
providing seamless automation that respects user preferences and development flow.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .automatic_story_detection import AutomaticStoryDetection, StoryRequirement, ContextDetectionResult
from .agile_story_automation import UserStory


@dataclass
class IntegratedWorkflowResult:
    """Result from integrated context-aware workflow with story automation."""
    context_detection: ContextDetectionResult
    story_requirement: StoryRequirement
    created_story: Optional[UserStory]
    active_rules: List[str]
    efficiency_improvement: float
    workflow_recommendations: List[str]


class ContextAwareStoryIntegration:
    """
    Integration system that combines context-aware rule selection with automatic story creation.
    
    This system ensures that user story automation respects development context and user
    preferences while maintaining the efficiency benefits of the context-aware rule system.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.story_detector = AutomaticStoryDetection(project_root)
        
        # Context-to-rules mapping (from intelligent_context_aware_rule_system)
        self.context_rule_mapping = {
            "DEFAULT": ["safety_first", "no_premature_victory", "boyscout", "context_awareness"],
            "CODING": ["safety_first", "tdd", "clean_code", "error_handling", "boyscout", "live_documentation"],
            "ARCHITECTURE": ["safety_first", "foundational_development", "systematic_construction", "documentation_excellence"],
            "DEBUGGING": ["safety_first", "systematic_problem_solving", "no_silent_errors", "error_exposure"],
            "TESTING": ["safety_first", "tdd", "test_monitoring", "no_failing_tests", "quality_validation"],
            "AGILE": ["safety_first", "agile_artifacts_maintenance", "live_documentation_updates", "sprint_management", "user_story_management"],
            "INTEGRATION": ["safety_first", "systematic_integration", "error_handling", "documentation_excellence"],
            "DOCUMENTATION": ["safety_first", "documentation_excellence", "live_documentation_updates", "clear_communication"],
            "INFRASTRUCTURE": ["safety_first", "deployment_safety", "infrastructure_validation", "systematic_construction"]
        }
        
        # Story automation settings per context
        self.context_story_settings = {
            "CODING": {"auto_create": True, "complexity_threshold": 4, "notify": True},
            "ARCHITECTURE": {"auto_create": True, "complexity_threshold": 5, "notify": True},
            "DEBUGGING": {"auto_create": False, "complexity_threshold": 6, "notify": False},  # Usually quick fixes
            "TESTING": {"auto_create": False, "complexity_threshold": 5, "notify": False},   # Usually part of other stories
            "AGILE": {"auto_create": True, "complexity_threshold": 3, "notify": True},
            "INTEGRATION": {"auto_create": True, "complexity_threshold": 4, "notify": True},
            "DOCUMENTATION": {"auto_create": False, "complexity_threshold": 6, "notify": False},  # Usually supporting work
            "INFRASTRUCTURE": {"auto_create": True, "complexity_threshold": 5, "notify": True}
        }
        
        print("🔗 Context-Aware Story Integration System initialized")
    
    def process_development_request(self, user_request: str,
                                  open_files: List[str] = None,
                                  current_directory: str = None,
                                  user_preferences: Dict[str, Any] = None) -> IntegratedWorkflowResult:
        """
        Process development request with integrated context detection and story automation.
        
        Args:
            user_request: User's development request
            open_files: List of currently open files
            current_directory: Current working directory
            user_preferences: User preferences for automation behavior
            
        Returns:
            Complete workflow result with context, rules, and optional story
        """
        
        if open_files is None:
            open_files = []
        if current_directory is None:
            current_directory = str(self.project_root)
        if user_preferences is None:
            user_preferences = {}
        
        print("🔄 **Processing Development Request with Context-Aware Integration**")
        print(f"📝 **Request**: {user_request}")
        
        # Step 1: Comprehensive analysis using story detection system
        analysis_result = self.story_detector.analyze_development_request(
            user_request, open_files, current_directory
        )
        
        context_detection = analysis_result["context"]
        story_requirement = analysis_result["story_requirement"]
        
        print(f"🎯 **Context Detected**: {context_detection.context} ({context_detection.confidence:.1f} confidence)")
        print(f"📊 **Complexity**: {analysis_result['complexity'].complexity_score}/10")
        
        # Step 2: Apply context-specific story automation settings
        context_settings = self.context_story_settings.get(context_detection.context, {})
        auto_create_enabled = context_settings.get("auto_create", True)
        complexity_threshold = context_settings.get("complexity_threshold", 5)
        
        # Step 3: Check user preferences and overrides
        user_auto_create = user_preferences.get("auto_create_stories", auto_create_enabled)
        user_complexity_threshold = user_preferences.get("complexity_threshold", complexity_threshold)
        
        # Step 4: Determine if story should be created
        should_create_story = (
            story_requirement.required and
            user_auto_create and
            analysis_result["complexity"].complexity_score >= user_complexity_threshold
        )
        
        # Step 5: Create story if conditions are met
        created_story = None
        if should_create_story:
            created_story = analysis_result.get("created_story")
            if created_story and context_settings.get("notify", True):
                self._notify_story_creation(created_story, story_requirement, context_detection)
        elif story_requirement.required and not should_create_story:
            print(f"📋 **Story Creation Skipped**: {story_requirement.reasoning}")
            print(f"💡 **Reason**: Context settings or user preferences disabled auto-creation")
        
        # Step 6: Apply context-aware rules
        active_rules = self._get_active_rules_for_context(context_detection.context, created_story)
        efficiency_improvement = self._calculate_efficiency_improvement(active_rules)
        
        # Step 7: Generate workflow recommendations
        recommendations = self._generate_workflow_recommendations(
            context_detection, story_requirement, created_story, active_rules
        )
        
        print(f"📋 **Active Rules**: {len(active_rules)} rules loaded")
        print(f"⚡ **Efficiency**: {efficiency_improvement:.0f}% rule reduction")
        
        if recommendations:
            print("💡 **Workflow Recommendations**:")
            for rec in recommendations:
                print(f"  - {rec}")
        
        return IntegratedWorkflowResult(
            context_detection=context_detection,
            story_requirement=story_requirement,
            created_story=created_story,
            active_rules=active_rules,
            efficiency_improvement=efficiency_improvement,
            workflow_recommendations=recommendations
        )
    
    def _notify_story_creation(self, story: UserStory, 
                             requirement: StoryRequirement,
                             context: ContextDetectionResult) -> None:
        """Notify about story creation with relevant details."""
        
        print("\n📋 **USER STORY AUTO-CREATED**")
        print(f"   🆔 **ID**: {story.story_id}")
        print(f"   🎯 **Title**: {story.title}")
        print(f"   ⚡ **Points**: {story.story_points}")
        print(f"   🔄 **Priority**: {requirement.priority.value}")
        print(f"   📅 **Type**: {requirement.story_type.value}")
        print(f"   🎲 **Context**: {context.context}")
        print(f"   🤖 **Confidence**: {requirement.confidence:.1f}")
        print(f"   💡 **Reason**: {requirement.reasoning}")
        print()
    
    def _get_active_rules_for_context(self, context: str, created_story: Optional[UserStory]) -> List[str]:
        """Get active rules for the detected context, with story-specific additions."""
        
        base_rules = self.context_rule_mapping.get(context, self.context_rule_mapping["DEFAULT"])
        active_rules = base_rules.copy()
        
        # Add story-specific rules if story was created
        if created_story:
            story_rules = ["user_story_management", "agile_artifacts_maintenance", "live_documentation_updates"]
            for rule in story_rules:
                if rule not in active_rules:
                    active_rules.append(rule)
        
        return active_rules
    
    def _calculate_efficiency_improvement(self, active_rules: List[str]) -> float:
        """Calculate efficiency improvement from rule reduction."""
        
        total_available_rules = 39  # Current total rule count
        active_rule_count = len(active_rules)
        
        return ((total_available_rules - active_rule_count) / total_available_rules) * 100
    
    def _generate_workflow_recommendations(self, context: ContextDetectionResult,
                                         requirement: StoryRequirement,
                                         story: Optional[UserStory],
                                         active_rules: List[str]) -> List[str]:
        """Generate workflow recommendations based on analysis."""
        
        recommendations = []
        
        # Context-specific recommendations
        if context.context == "CODING" and story:
            recommendations.append("Consider TDD approach: write tests first for new functionality")
            recommendations.append("Update documentation as you implement features")
        
        elif context.context == "ARCHITECTURE":
            recommendations.append("Document design decisions and architectural patterns")
            recommendations.append("Consider system impact and integration points")
        
        elif context.context == "DEBUGGING":
            recommendations.append("Write regression tests to prevent issue recurrence")
            recommendations.append("Document root cause and resolution approach")
        
        elif context.context == "INTEGRATION":
            recommendations.append("Test integration points thoroughly")
            recommendations.append("Plan rollback strategy for integration changes")
        
        # Story-specific recommendations
        if story:
            if story.story_points >= 8:
                recommendations.append("Consider breaking down large story into smaller tasks")
            
            if requirement.story_type.value == "feature":
                recommendations.append("Plan user acceptance testing for feature validation")
            
            recommendations.append(f"Track progress in {story.story_id} throughout development")
        
        # Rule-specific recommendations
        if "tdd" in active_rules:
            recommendations.append("Follow Red-Green-Refactor cycle for test-driven development")
        
        if "agile_artifacts_maintenance" in active_rules:
            recommendations.append("Update sprint progress and daily standup notes")
        
        return recommendations
    
    def check_story_automation_settings(self, context: str) -> Dict[str, Any]:
        """Check story automation settings for a given context."""
        
        context_settings = self.context_story_settings.get(context, {})
        
        return {
            "context": context,
            "auto_create_enabled": context_settings.get("auto_create", True),
            "complexity_threshold": context_settings.get("complexity_threshold", 5),
            "notifications_enabled": context_settings.get("notify", True),
            "recommended_rules": self.context_rule_mapping.get(context, [])
        }
    
    def update_user_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update user preferences for story automation."""
        
        self.user_preferences = preferences
        print(f"✅ Updated user preferences for story automation")
        
        # Validate preferences
        if "auto_create_stories" in preferences:
            print(f"   📋 Auto-create stories: {preferences['auto_create_stories']}")
        
        if "complexity_threshold" in preferences:
            threshold = preferences["complexity_threshold"]
            print(f"   🔢 Complexity threshold: {threshold}/10")
        
        if "preferred_contexts" in preferences:
            contexts = preferences["preferred_contexts"]
            print(f"   🎯 Preferred contexts: {', '.join(contexts)}")
    
    def generate_session_summary(self, workflow_results: List[IntegratedWorkflowResult]) -> Dict[str, Any]:
        """Generate summary of session with story automation metrics."""
        
        if not workflow_results:
            return {"session_empty": True}
        
        # Calculate metrics
        total_requests = len(workflow_results)
        stories_created = sum(1 for result in workflow_results if result.created_story)
        contexts_detected = [result.context_detection.context for result in workflow_results]
        avg_efficiency = sum(result.efficiency_improvement for result in workflow_results) / total_requests
        
        # Context distribution
        context_counts = {}
        for context in contexts_detected:
            context_counts[context] = context_counts.get(context, 0) + 1
        
        # Story metrics
        story_types = []
        story_points_total = 0
        
        for result in workflow_results:
            if result.created_story:
                story_types.append(result.story_requirement.story_type.value)
                story_points_total += result.created_story.story_points
        
        summary = {
            "session_metrics": {
                "total_requests": total_requests,
                "stories_created": stories_created,
                "story_automation_rate": (stories_created / total_requests) * 100,
                "avg_efficiency_improvement": avg_efficiency,
                "total_story_points": story_points_total
            },
            "context_distribution": context_counts,
            "story_types_created": story_types,
            "session_timestamp": datetime.now().isoformat()
        }
        
        return summary


def main():
    """Demonstrate context-aware story integration system."""
    
    integration = ContextAwareStoryIntegration()
    
    # Test user preferences
    user_prefs = {
        "auto_create_stories": True,
        "complexity_threshold": 4,
        "preferred_contexts": ["CODING", "ARCHITECTURE"]
    }
    
    integration.update_user_preferences(user_prefs)
    
    # Test requests with different contexts
    test_scenarios = [
        {
            "request": "@code Implement a new health monitoring dashboard with real-time updates",
            "files": ["src/dashboard.py", "src/health.py"],
            "directory": "/project/src"
        },
        {
            "request": "@debug Fix the NumPy import error causing test failures",
            "files": ["tests/test_health.py"],
            "directory": "/project/tests"
        },
        {
            "request": "@architecture Design a microservices architecture for the user management system",
            "files": ["docs/architecture/system_design.md"],
            "directory": "/project/docs/architecture"
        }
    ]
    
    print("🔍 **Testing Context-Aware Story Integration**\n")
    
    workflow_results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"**Scenario {i}**:")
        
        result = integration.process_development_request(
            user_request=scenario["request"],
            open_files=scenario["files"],
            current_directory=scenario["directory"],
            user_preferences=user_prefs
        )
        
        workflow_results.append(result)
        print("-" * 80)
    
    # Generate session summary
    summary = integration.generate_session_summary(workflow_results)
    
    print("\n📊 **SESSION SUMMARY**")
    print(f"Total Requests: {summary['session_metrics']['total_requests']}")
    print(f"Stories Created: {summary['session_metrics']['stories_created']}")
    print(f"Automation Rate: {summary['session_metrics']['story_automation_rate']:.1f}%")
    print(f"Avg Efficiency: {summary['session_metrics']['avg_efficiency_improvement']:.1f}%")
    print(f"Context Distribution: {summary['context_distribution']}")


if __name__ == "__main__":
    main()
