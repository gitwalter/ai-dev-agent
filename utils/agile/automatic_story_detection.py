#!/usr/bin/env python3
"""
Automatic User Story Detection and Creation System.

This module automatically detects when development work requires a user story
and creates it seamlessly with zero manual intervention. Integrates with the
context-aware rule system for intelligent story management.
"""

import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .agile_story_automation import AgileStoryAutomation, UserStory, Priority, Status
from .user_story_catalog_manager import UserStoryCatalogManager


class StoryType(Enum):
    """Types of user stories."""
    FEATURE = "feature"
    TECHNICAL = "technical"
    BUG = "bug"
    INTEGRATION = "integration"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class WorkComplexityAssessment:
    """Assessment of work complexity for story creation decisions."""
    complexity_score: int  # 1-10 scale
    reasoning: str
    factors: Dict[str, int]
    files_affected: List[str]
    estimated_effort: str


@dataclass
class StoryRequirement:
    """Determination of whether a user story is required."""
    required: bool
    reasoning: str
    story_type: StoryType
    priority: Priority
    complexity: int
    confidence: float


@dataclass
class ContextDetectionResult:
    """Result from context detection analysis."""
    context: str
    method: str
    confidence: float
    reasoning: str


class AutomaticStoryDetection:
    """
    Automatic detection and creation of user stories based on development context.
    
    This system integrates with the context-aware rule system to automatically
    create user stories when development work meets complexity or impact thresholds.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.story_automation = AgileStoryAutomation(project_root)
        self.catalog_manager = UserStoryCatalogManager(project_root)
        
        # Configuration
        self.complexity_threshold = 5  # Stories required for complexity >= 5
        self.story_required_contexts = ["CODING", "ARCHITECTURE", "AGILE", "INTEGRATION"]
        
        # Trigger patterns for automatic story creation
        self.trigger_patterns = {
            "feature_development": {
                "keywords": ["implement", "create", "build", "add feature", "new functionality", "develop"],
                "story_type": StoryType.FEATURE,
                "base_complexity": 4,
                "priority": Priority.HIGH
            },
            "significant_changes": {
                "keywords": ["refactor", "restructure", "overhaul", "major fix", "rewrite"],
                "story_type": StoryType.TECHNICAL,
                "base_complexity": 5,
                "priority": Priority.MEDIUM
            },
            "integration_work": {
                "keywords": ["integrate", "connect", "api", "service", "external", "plugin"],
                "story_type": StoryType.INTEGRATION,
                "base_complexity": 4,
                "priority": Priority.MEDIUM
            },
            "ui_changes": {
                "keywords": ["dashboard", "interface", "visualization", "user experience", "ui", "frontend"],
                "story_type": StoryType.FEATURE,
                "base_complexity": 3,
                "priority": Priority.HIGH
            },
            "infrastructure": {
                "keywords": ["infrastructure", "deployment", "ci/cd", "build", "pipeline", "docker"],
                "story_type": StoryType.INFRASTRUCTURE,
                "base_complexity": 5,
                "priority": Priority.MEDIUM
            }
        }
        
        print("Automatic Story Detection System initialized")
    
    def analyze_development_request(self, user_request: str, 
                                  open_files: List[str] = None,
                                  current_directory: str = None) -> Dict[str, Any]:
        """
        Analyze development request to determine if user story is needed.
        
        Args:
            user_request: User's development request
            open_files: List of currently open files
            current_directory: Current working directory
            
        Returns:
            Complete analysis with story creation decision
        """
        
        if open_files is None:
            open_files = []
        if current_directory is None:
            current_directory = str(self.project_root)
        
        # Step 1: Detect context
        context_result = self._detect_development_context(user_request, open_files, current_directory)
        
        # Step 2: Assess work complexity
        complexity_assessment = self._assess_work_complexity(user_request, context_result, open_files)
        
        # Step 3: Determine if story is required
        story_requirement = self._determine_story_requirement(user_request, context_result, complexity_assessment)
        
        # Step 4: Create story if required
        created_story = None
        if story_requirement.required:
            created_story = self._create_user_story_automatically(user_request, story_requirement, context_result)
        
        return {
            "context": context_result,
            "complexity": complexity_assessment,
            "story_requirement": story_requirement,
            "created_story": created_story,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _detect_development_context(self, user_request: str, 
                                  open_files: List[str],
                                  current_directory: str) -> ContextDetectionResult:
        """Detect development context from user request and environment."""
        
        # Check for explicit context keywords
        explicit_context = self._check_explicit_context_keywords(user_request)
        if explicit_context:
            return ContextDetectionResult(
                context=explicit_context,
                method="explicit_keyword",
                confidence=1.0,
                reasoning=f"User explicitly specified {explicit_context} context"
            )
        
        # Automatic context detection
        context_scores = {}
        
        # Analyze user request content
        request_lower = user_request.lower()
        context_patterns = {
            "CODING": ["implement", "code", "function", "class", "method", "algorithm"],
            "ARCHITECTURE": ["design", "architecture", "system", "structure", "pattern"],
            "DEBUGGING": ["debug", "fix", "error", "bug", "issue", "problem"],
            "TESTING": ["test", "testing", "validate", "verify", "qa"],
            "AGILE": ["story", "sprint", "backlog", "epic", "user story"],
            "INTEGRATION": ["integrate", "connect", "api", "service", "external"],
            "DOCUMENTATION": ["document", "docs", "readme", "guide", "manual"],
            "INFRASTRUCTURE": ["deploy", "build", "ci/cd", "infrastructure", "pipeline"]
        }
        
        for context, patterns in context_patterns.items():
            score = sum(2 for pattern in patterns if pattern in request_lower)
            context_scores[context] = score
        
        # Analyze file context
        for file_path in open_files:
            file_lower = file_path.lower()
            if "test" in file_lower:
                context_scores["TESTING"] = context_scores.get("TESTING", 0) + 1
            elif file_path.endswith((".py", ".js", ".ts")):
                context_scores["CODING"] = context_scores.get("CODING", 0) + 1
            elif "docs/" in file_path:
                context_scores["DOCUMENTATION"] = context_scores.get("DOCUMENTATION", 0) + 1
        
        # Analyze directory context
        dir_lower = current_directory.lower()
        if "agile" in dir_lower:
            context_scores["AGILE"] = context_scores.get("AGILE", 0) + 2
        elif "tests" in dir_lower:
            context_scores["TESTING"] = context_scores.get("TESTING", 0) + 1
        elif "docs" in dir_lower:
            context_scores["DOCUMENTATION"] = context_scores.get("DOCUMENTATION", 0) + 1
        
        # Select best context
        if context_scores:
            best_context, best_score = max(context_scores.items(), key=lambda x: x[1])
            confidence = min(best_score / 5.0, 1.0)
            
            if confidence >= 0.7:
                return ContextDetectionResult(
                    context=best_context,
                    method="auto_detected",
                    confidence=confidence,
                    reasoning=f"Auto-detected from patterns (confidence: {confidence:.1f})"
                )
        
        # Default fallback
        return ContextDetectionResult(
            context="DEFAULT",
            method="fallback",
            confidence=0.5,
            reasoning="Low confidence in detection, using DEFAULT mode"
        )
    
    def _check_explicit_context_keywords(self, user_request: str) -> Optional[str]:
        """Check for explicit @context keywords in user request."""
        
        request_lower = user_request.lower()
        keyword_map = {
            "@code": "CODING", "@implement": "CODING", "@build": "CODING",
            "@design": "ARCHITECTURE", "@architecture": "ARCHITECTURE",
            "@debug": "DEBUGGING", "@fix": "DEBUGGING", "@solve": "DEBUGGING",
            "@test": "TESTING", "@testing": "TESTING", "@qa": "TESTING",
            "@agile": "AGILE", "@sprint": "AGILE", "@story": "AGILE",
            "@docs": "DOCUMENTATION", "@document": "DOCUMENTATION",
            "@integrate": "INTEGRATION", "@connect": "INTEGRATION"
        }
        
        for keyword, context in keyword_map.items():
            if keyword in request_lower:
                return context
        
        return None
    
    def _assess_work_complexity(self, user_request: str,
                              context_result: ContextDetectionResult,
                              open_files: List[str]) -> WorkComplexityAssessment:
        """Assess work complexity on a scale of 1-10."""
        
        complexity_factors = {}
        total_complexity = 0
        
        # Base complexity from trigger patterns
        request_lower = user_request.lower()
        max_trigger_complexity = 0
        
        for category, config in self.trigger_patterns.items():
            for keyword in config["keywords"]:
                if keyword in request_lower:
                    max_trigger_complexity = max(max_trigger_complexity, config["base_complexity"])
                    complexity_factors[f"trigger_{category}"] = config["base_complexity"]
        
        total_complexity = max_trigger_complexity
        
        # File count impact
        file_count = len(open_files)
        if file_count > 5:
            file_complexity = 3
        elif file_count > 2:
            file_complexity = 2
        elif file_count > 0:
            file_complexity = 1
        else:
            file_complexity = 0
        
        complexity_factors["file_count"] = file_complexity
        total_complexity += file_complexity
        
        # Context-based adjustments
        context_multipliers = {
            "ARCHITECTURE": 1.5,
            "INTEGRATION": 1.3,
            "CODING": 1.2,
            "INFRASTRUCTURE": 1.4,
            "DEBUGGING": 0.9,
            "TESTING": 0.8,
            "DOCUMENTATION": 0.7
        }
        
        multiplier = context_multipliers.get(context_result.context, 1.0)
        complexity_factors["context_multiplier"] = multiplier
        total_complexity = int(total_complexity * multiplier)
        
        # Special indicators
        if any(word in request_lower for word in ["major", "complete", "full", "entire"]):
            complexity_factors["scope_large"] = 2
            total_complexity += 2
        
        if any(word in request_lower for word in ["new", "create", "implement"]):
            complexity_factors["new_work"] = 1
            total_complexity += 1
        
        # Cap at 10
        final_complexity = min(total_complexity, 10)
        
        # Determine effort estimate
        if final_complexity >= 8:
            effort = "2-3 weeks"
        elif final_complexity >= 6:
            effort = "1-2 weeks"
        elif final_complexity >= 4:
            effort = "3-5 days"
        elif final_complexity >= 2:
            effort = "1-2 days"
        else:
            effort = "< 1 day"
        
        reasoning = f"Complexity {final_complexity}/10 based on: " + \
                   ", ".join(f"{k}={v}" for k, v in complexity_factors.items())
        
        return WorkComplexityAssessment(
            complexity_score=final_complexity,
            reasoning=reasoning,
            factors=complexity_factors,
            files_affected=open_files,
            estimated_effort=effort
        )
    
    def _determine_story_requirement(self, user_request: str,
                                   context_result: ContextDetectionResult,
                                   complexity_assessment: WorkComplexityAssessment) -> StoryRequirement:
        """Determine if user story creation is required."""
        
        # Rule 1: Complexity threshold
        if complexity_assessment.complexity_score >= self.complexity_threshold:
            return StoryRequirement(
                required=True,
                reasoning=f"High complexity ({complexity_assessment.complexity_score}/10) requires story tracking",
                story_type=self._determine_story_type_from_request(user_request),
                priority=Priority.HIGH if complexity_assessment.complexity_score >= 7 else Priority.MEDIUM,
                complexity=complexity_assessment.complexity_score,
                confidence=0.9
            )
        
        # Rule 2: Context-based requirements
        if context_result.context in self.story_required_contexts:
            # Check for trigger patterns
            request_lower = user_request.lower()
            for category, config in self.trigger_patterns.items():
                for keyword in config["keywords"]:
                    if keyword in request_lower:
                        return StoryRequirement(
                            required=True,
                            reasoning=f"Detected {category} trigger: '{keyword}' in {context_result.context} context",
                            story_type=config["story_type"],
                            priority=config["priority"],
                            complexity=complexity_assessment.complexity_score,
                            confidence=0.8
                        )
        
        # Rule 3: Multi-file impact
        if len(complexity_assessment.files_affected) > 3:
            return StoryRequirement(
                required=True,
                reasoning=f"Multi-file impact ({len(complexity_assessment.files_affected)} files) requires coordination",
                story_type=StoryType.TECHNICAL,
                priority=Priority.MEDIUM,
                complexity=complexity_assessment.complexity_score,
                confidence=0.7
            )
        
        # Rule 4: User-facing changes
        if self._detect_user_facing_changes(user_request):
            return StoryRequirement(
                required=True,
                reasoning="User-facing changes require business value tracking",
                story_type=StoryType.FEATURE,
                priority=Priority.HIGH,
                complexity=complexity_assessment.complexity_score,
                confidence=0.8
            )
        
        return StoryRequirement(
            required=False,
            reasoning="Simple maintenance work, no story required",
            story_type=StoryType.TECHNICAL,
            priority=Priority.LOW,
            complexity=complexity_assessment.complexity_score,
            confidence=0.6
        )
    
    def _determine_story_type_from_request(self, user_request: str) -> StoryType:
        """Determine story type from request content."""
        
        request_lower = user_request.lower()
        
        # Check for specific type indicators
        if any(word in request_lower for word in ["feature", "functionality", "user", "interface", "dashboard"]):
            return StoryType.FEATURE
        elif any(word in request_lower for word in ["integrate", "connect", "api", "service", "external"]):
            return StoryType.INTEGRATION
        elif any(word in request_lower for word in ["infrastructure", "deploy", "build", "pipeline"]):
            return StoryType.INFRASTRUCTURE
        elif any(word in request_lower for word in ["bug", "fix", "error", "issue"]):
            return StoryType.BUG
        else:
            return StoryType.TECHNICAL
    
    def _detect_user_facing_changes(self, user_request: str) -> bool:
        """Detect if request involves user-facing changes."""
        
        user_facing_indicators = [
            "ui", "interface", "dashboard", "visualization", "frontend",
            "user experience", "user interface", "display", "view",
            "screen", "page", "form", "button", "menu"
        ]
        
        request_lower = user_request.lower()
        return any(indicator in request_lower for indicator in user_facing_indicators)
    
    def _create_user_story_automatically(self, user_request: str,
                                       story_requirement: StoryRequirement,
                                       context_result: ContextDetectionResult) -> UserStory:
        """Create user story automatically with all required fields."""
        
        # Extract story components
        story_components = self._extract_story_components(user_request, context_result, story_requirement)
        
        # Create story using existing automation
        story = self.story_automation.create_user_story(
            title=story_components["title"],
            description=story_components["description"],
            business_justification=story_components["business_justification"],
            story_points=self._complexity_to_story_points(story_requirement.complexity),
            priority=story_requirement.priority,
            epic=story_components["epic"],
            acceptance_criteria=story_components["acceptance_criteria"]
        )
        
        # Add automation-specific metadata
        story.created_by = "automatic_detection"
        story.detection_confidence = story_requirement.confidence
        story.original_request = user_request
        story.detected_context = context_result.context
        story.story_type = story_requirement.story_type.value
        
        # Update all agile artifacts
        self.catalog_manager.update_catalog()
        
        print(f"📋 **Auto-Created User Story**: {story.story_id}")
        print(f"🎯 **Title**: {story.title}")
        print(f"⚡ **Story Points**: {story.story_points}")
        print(f"🔄 **Priority**: {story.priority.value}")
        print(f"📅 **Type**: {story_requirement.story_type.value}")
        print(f"🤖 **Confidence**: {story_requirement.confidence:.1f}")
        
        return story
    
    def _extract_story_components(self, user_request: str,
                                context_result: ContextDetectionResult,
                                story_requirement: StoryRequirement) -> Dict[str, Any]:
        """Extract user story components from request."""
        
        # Generate title
        title = self._generate_story_title(user_request, story_requirement.story_type)
        
        # Generate description
        description = self._generate_story_description(user_request, context_result)
        
        # Generate business justification
        business_justification = self._generate_business_justification(user_request, story_requirement)
        
        # Generate acceptance criteria
        acceptance_criteria = self._generate_acceptance_criteria(user_request, story_requirement.story_type)
        
        # Determine epic
        epic = self._determine_epic(context_result.context, story_requirement.story_type)
        
        return {
            "title": title,
            "description": description,
            "business_justification": business_justification,
            "acceptance_criteria": acceptance_criteria,
            "epic": epic
        }
    
    def _generate_story_title(self, user_request: str, story_type: StoryType) -> str:
        """Generate concise story title from request."""
        
        # Extract key action and object
        request_clean = user_request.strip()
        if len(request_clean) > 60:
            # Truncate and find good breaking point
            truncated = request_clean[:60]
            last_space = truncated.rfind(' ')
            if last_space > 40:
                request_clean = truncated[:last_space] + "..."
            else:
                request_clean = truncated + "..."
        
        # Add type prefix for clarity
        type_prefixes = {
            StoryType.FEATURE: "Feature:",
            StoryType.TECHNICAL: "Technical:",
            StoryType.BUG: "Fix:",
            StoryType.INTEGRATION: "Integration:",
            StoryType.INFRASTRUCTURE: "Infrastructure:"
        }
        
        prefix = type_prefixes.get(story_type, "")
        if prefix:
            return f"{prefix} {request_clean}"
        else:
            return request_clean
    
    def _generate_story_description(self, user_request: str, context_result: ContextDetectionResult) -> str:
        """Generate detailed story description."""
        
        user_types = {
            "CODING": "developer",
            "ARCHITECTURE": "system architect",
            "DEBUGGING": "developer",
            "TESTING": "QA engineer",
            "AGILE": "product owner",
            "INTEGRATION": "system integrator",
            "DOCUMENTATION": "team member"
        }
        
        user_type = user_types.get(context_result.context, "user")
        
        # Extract goal and benefit
        goal = self._extract_goal_from_request(user_request)
        benefit = self._generate_benefit_statement(goal, context_result.context)
        
        description = f"""**As a** {user_type}
**I want** {goal}
**So that** {benefit}

**Original Request**: {user_request}

**Context**: {context_result.context} (detected via {context_result.method})
**Auto-generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        return description
    
    def _extract_goal_from_request(self, user_request: str) -> str:
        """Extract the main goal from user request."""
        
        # Remove common prefixes
        goal = user_request.strip()
        prefixes_to_remove = [
            "please ", "can you ", "could you ", "i need to ", "i want to ",
            "we need to ", "we should ", "let's ", "help me "
        ]
        
        goal_lower = goal.lower()
        for prefix in prefixes_to_remove:
            if goal_lower.startswith(prefix):
                goal = goal[len(prefix):]
                break
        
        return goal.strip()
    
    def _generate_benefit_statement(self, goal: str, context: str) -> str:
        """Generate benefit statement based on goal and context."""
        
        context_benefits = {
            "CODING": "I can deliver working functionality efficiently",
            "ARCHITECTURE": "the system will be well-designed and maintainable",
            "DEBUGGING": "I can resolve issues quickly and prevent future problems",
            "TESTING": "I can ensure quality and prevent regressions",
            "AGILE": "the team can work effectively and deliver value",
            "INTEGRATION": "systems can work together seamlessly",
            "DOCUMENTATION": "team members can understand and contribute effectively"
        }
        
        return context_benefits.get(context, "the project can progress successfully")
    
    def _generate_business_justification(self, user_request: str, story_requirement: StoryRequirement) -> str:
        """Generate business justification for the story."""
        
        justification = f"""**BUSINESS VALUE**: This {story_requirement.story_type.value} work is required to:

- **Primary Goal**: {self._extract_goal_from_request(user_request)}
- **Business Impact**: {self._determine_business_impact(story_requirement)}
- **Priority Rationale**: {story_requirement.reasoning}
- **Complexity Assessment**: {story_requirement.complexity}/10 complexity score

**Automation Decision**: Auto-created because {story_requirement.reasoning.lower()}"""
        
        return justification
    
    def _determine_business_impact(self, story_requirement: StoryRequirement) -> str:
        """Determine business impact based on story type and priority."""
        
        impact_map = {
            (StoryType.FEATURE, Priority.HIGH): "Direct user value delivery",
            (StoryType.FEATURE, Priority.MEDIUM): "User experience improvement",
            (StoryType.TECHNICAL, Priority.HIGH): "Critical system reliability",
            (StoryType.TECHNICAL, Priority.MEDIUM): "Code quality and maintainability",
            (StoryType.INTEGRATION, Priority.HIGH): "Essential system connectivity",
            (StoryType.INTEGRATION, Priority.MEDIUM): "Improved system integration",
            (StoryType.INFRASTRUCTURE, Priority.HIGH): "Critical deployment capability",
            (StoryType.INFRASTRUCTURE, Priority.MEDIUM): "Development efficiency improvement",
            (StoryType.BUG, Priority.HIGH): "Critical issue resolution"
        }
        
        return impact_map.get((story_requirement.story_type, story_requirement.priority), 
                             "System improvement and development progress")
    
    def _generate_acceptance_criteria(self, user_request: str, story_type: StoryType) -> List[str]:
        """Generate acceptance criteria based on request and story type."""
        
        base_criteria = [
            "Implementation is complete and functional",
            "All code changes are tested and validated",
            "Documentation is updated as needed",
            "No existing functionality is broken"
        ]
        
        # Add type-specific criteria
        type_specific_criteria = {
            StoryType.FEATURE: [
                "User interface is intuitive and accessible",
                "Feature meets all specified requirements",
                "User acceptance testing passes"
            ],
            StoryType.TECHNICAL: [
                "Code quality standards are met",
                "Performance requirements are satisfied",
                "Technical debt is minimized"
            ],
            StoryType.INTEGRATION: [
                "Integration works seamlessly",
                "Error handling is robust",
                "System connectivity is reliable"
            ],
            StoryType.INFRASTRUCTURE: [
                "Deployment process is stable",
                "System reliability is maintained",
                "Infrastructure is properly documented"
            ],
            StoryType.BUG: [
                "Bug is completely resolved",
                "Root cause is identified and addressed",
                "Regression tests prevent recurrence"
            ]
        }
        
        specific_criteria = type_specific_criteria.get(story_type, [])
        return base_criteria + specific_criteria
    
    def _determine_epic(self, context: str, story_type: StoryType) -> str:
        """Determine epic based on context and story type."""
        
        epic_map = {
            "CODING": "Development Infrastructure",
            "ARCHITECTURE": "System Architecture",
            "DEBUGGING": "Quality Assurance",
            "TESTING": "Quality Assurance",
            "AGILE": "Project Management",
            "INTEGRATION": "System Integration",
            "DOCUMENTATION": "Documentation & Guides",
            "INFRASTRUCTURE": "Infrastructure & Deployment"
        }
        
        return epic_map.get(context, "Foundation & Core")
    
    def _complexity_to_story_points(self, complexity: int) -> int:
        """Convert complexity score to Fibonacci story points."""
        
        complexity_to_points = {
            1: 1, 2: 1, 3: 2, 4: 3, 5: 5,
            6: 5, 7: 8, 8: 8, 9: 13, 10: 13
        }
        
        return complexity_to_points.get(complexity, 5)


def main():
    """Demonstrate automatic story detection system."""
    
    detector = AutomaticStoryDetection()
    
    # Test cases
    test_requests = [
        "Implement a new health dashboard with real-time monitoring",
        "Fix the NumPy import error in the health monitoring system",
        "Add user authentication to the web application",
        "Refactor the database connection pooling logic",
        "Create documentation for the API endpoints"
    ]
    
    print("Testing Automatic Story Detection\n")
    
    for i, request in enumerate(test_requests, 1):
        print(f"**Test {i}**: {request}")
        
        result = detector.analyze_development_request(
            user_request=request,
            open_files=["src/dashboard.py", "tests/test_health.py"],
            current_directory="/project/src"
        )
        
        print(f"  Context: {result['context'].context} ({result['context'].confidence:.1f})")
        print(f"  Complexity: {result['complexity'].complexity_score}/10")
        print(f"  Story Required: {result['story_requirement'].required}")
        
        if result['story_requirement'].required:
            print(f"  Story Type: {result['story_requirement'].story_type.value}")
            print(f"  Priority: {result['story_requirement'].priority.value}")
            
            if result['created_story']:
                print(f"  Created: {result['created_story'].story_id}")
        
        print(f"  Reasoning: {result['story_requirement'].reasoning}")
        print()


if __name__ == "__main__":
    main()
