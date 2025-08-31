#!/usr/bin/env python3
"""
Task Analyzer for the Workflow Composition Engine.
Analyzes natural language task descriptions to determine workflow requirements.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime

from workflow.models.workflow_models import (
    TaskAnalysis, Entity, ComplexityLevel, ValidationResult
)

logger = logging.getLogger(__name__)


class TaskAnalyzer:
    """
    Analyzes task requirements to determine needed contexts and workflow patterns.
    
    This class uses natural language processing and pattern matching to:
    1. Extract key entities from task descriptions
    2. Determine task complexity and scope
    3. Identify required @keyword contexts
    4. Estimate execution time and dependencies
    """
    
    def __init__(self):
        """Initialize the task analyzer with pattern libraries."""
        self.context_patterns = self._build_context_patterns()
        self.entity_patterns = self._build_entity_patterns()
        self.complexity_indicators = self._build_complexity_indicators()
        self.duration_estimates = self._build_duration_estimates()
        
    def analyze_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> TaskAnalysis:
        """
        Analyze a task description to determine workflow requirements.
        
        Args:
            task_description: Natural language description of the task
            context: Current project and environment context
            
        Returns:
            TaskAnalysis with workflow requirements and recommendations
        """
        logger.info(f"Analyzing task: {task_description[:100]}...")
        
        # Store current task description for confidence calculation
        self._current_task_description = task_description
        
        # Generate unique task ID
        task_id = self._generate_task_id(task_description)
        
        # Extract entities from task description
        entities = self.extract_entities(task_description)
        
        # Assess task complexity
        complexity = self.assess_complexity(entities, task_description, context or {})
        
        # Identify required contexts
        required_contexts = self.identify_contexts(entities, task_description, complexity)
        
        # Estimate duration
        estimated_duration = self.estimate_duration(complexity, required_contexts, entities)
        
        # Identify dependencies
        dependencies = self.identify_dependencies(entities, task_description)
        
        # Generate success criteria
        success_criteria = self.generate_success_criteria(entities, task_description)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(entities, required_contexts, complexity)
        
        analysis = TaskAnalysis(
            task_id=task_id,
            description=task_description,
            entities=entities,
            complexity=complexity,
            required_contexts=required_contexts,
            estimated_duration=estimated_duration,
            dependencies=dependencies,
            success_criteria=success_criteria,
            confidence=confidence
        )
        
        logger.info(f"Task analysis complete: {len(required_contexts)} contexts, "
                   f"{complexity} complexity, {estimated_duration}min estimated")
        
        return analysis
    
    def extract_entities(self, task_description: str) -> List[Entity]:
        """
        Extract key entities from task description.
        
        Args:
            task_description: Task description to analyze
            
        Returns:
            List of extracted entities with confidence scores
        """
        entities = []
        text_lower = task_description.lower()
        
        # Extract different types of entities
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    entity_name = match.group(1) if match.groups() else match.group(0)
                    confidence = self._calculate_entity_confidence(entity_name, entity_type, text_lower)
                    
                    entities.append(Entity(
                        name=entity_name.strip(),
                        type=entity_type,
                        confidence=confidence,
                        attributes={"position": match.start(), "length": len(entity_name)}
                    ))
        
        # Remove duplicates and sort by confidence
        entities = self._deduplicate_entities(entities)
        entities.sort(key=lambda e: e.confidence, reverse=True)
        
        return entities[:20]  # Limit to top 20 entities
    
    def assess_complexity(self, entities: List[Entity], task_description: str, context: Dict[str, Any]) -> ComplexityLevel:
        """
        Assess task complexity based on entities and context.
        
        Args:
            entities: Extracted entities
            task_description: Original task description
            context: Project and environment context
            
        Returns:
            Assessed complexity level
        """
        complexity_score = 0.0
        
        # Base complexity from entity count and types
        complexity_score += len(entities) * 0.1
        
        # Add complexity based on entity types
        high_complexity_types = {"system", "architecture", "integration", "security", "performance"}
        medium_complexity_types = {"feature", "component", "service", "api"}
        
        for entity in entities:
            if entity.type in high_complexity_types:
                complexity_score += 0.3
            elif entity.type in medium_complexity_types:
                complexity_score += 0.2
            else:
                complexity_score += 0.1
        
        # Check for complexity indicators in text
        text_lower = task_description.lower()
        for indicator, weight in self.complexity_indicators.items():
            if indicator in text_lower:
                # Count occurrences for repeated patterns
                occurrences = text_lower.count(indicator)
                complexity_score += weight * occurrences
        
        # Add complexity based on text length (very long descriptions are complex)
        word_count = len(task_description.split())
        if word_count > 200:
            complexity_score += 1.0  # Significant complexity for very long descriptions
        elif word_count > 100:
            complexity_score += 0.5
        
        # Adjust based on context
        if context.get("project_size") == "large":
            complexity_score += 0.2
        elif context.get("project_size") == "small":
            complexity_score -= 0.1
        
        if context.get("team_experience") == "junior":
            complexity_score += 0.1
        elif context.get("team_experience") == "senior":
            complexity_score -= 0.1
        
        # Convert score to complexity level
        # Much more lenient thresholds for simple tasks
        if complexity_score >= 2.0:
            return ComplexityLevel.COMPLEX
        elif complexity_score >= 1.0:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.SIMPLE
    
    def identify_contexts(self, entities: List[Entity], task_description: str, complexity: ComplexityLevel) -> List[str]:
        """
        Identify required @keyword contexts for the task.
        
        Args:
            entities: Extracted entities
            task_description: Original task description
            complexity: Task complexity level
            
        Returns:
            List of required @keyword contexts
        """
        contexts = set()
        text_lower = task_description.lower()
        
        # Check for explicit context patterns
        for context, patterns in self.context_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    contexts.add(context)
        
        # Add contexts based on entity types
        entity_context_mapping = {
            "feature": ["@agile", "@design", "@code", "@test"],
            "bug": ["@debug", "@test", "@code"],
            "security": ["@security", "@code", "@test"],
            "performance": ["@optimize", "@test", "@code"],
            "documentation": ["@docs"],
            "deployment": ["@git", "@test"],
            "architecture": ["@design", "@code"],
            "api": ["@code", "@test", "@docs"],
            "database": ["@code", "@test", "@security"],
            "ui": ["@code", "@test", "@design"],
            "integration": ["@code", "@test", "@debug"]
        }
        
        for entity in entities:
            if entity.type in entity_context_mapping:
                contexts.update(entity_context_mapping[entity.type])
        
        # Add complexity-based contexts
        if complexity == ComplexityLevel.COMPLEX:
            contexts.update(["@design", "@security", "@test"])
        elif complexity == ComplexityLevel.MEDIUM:
            contexts.update(["@test"])
        
        # Ensure minimum viable workflow
        if not contexts:
            contexts.add("@code")
        
        # Always include @git for deployment unless it's just documentation
        if "@docs" not in contexts or len(contexts) > 1:
            contexts.add("@git")
        
        return sorted(list(contexts))
    
    def estimate_duration(self, complexity: ComplexityLevel, contexts: List[str], entities: List[Entity]) -> int:
        """
        Estimate task duration in minutes.
        
        Args:
            complexity: Task complexity level
            contexts: Required contexts
            entities: Extracted entities
            
        Returns:
            Estimated duration in minutes
        """
        base_duration = self.duration_estimates["complexity"][complexity.value]
        
        # Add time for each context
        context_time = len(contexts) * self.duration_estimates["per_context"]
        
        # Add time based on entity count and types
        entity_time = len(entities) * 2  # 2 minutes per entity
        
        # Add time for high-complexity entity types
        high_complexity_types = {"system", "architecture", "integration", "security"}
        for entity in entities:
            if entity.type in high_complexity_types:
                entity_time += 10
        
        total_duration = base_duration + context_time + entity_time
        
        # Round to nearest 5 minutes
        return max(5, round(total_duration / 5) * 5)
    
    def identify_dependencies(self, entities: List[Entity], task_description: str) -> List[str]:
        """
        Identify task dependencies.
        
        Args:
            entities: Extracted entities
            task_description: Original task description
            
        Returns:
            List of identified dependencies
        """
        dependencies = []
        text_lower = task_description.lower()
        
        # Common dependency patterns
        dependency_patterns = [
            r"depends on ([^,\.]+)",
            r"requires ([^,\.]+)",
            r"needs ([^,\.]+)",
            r"after ([^,\.]+)",
            r"once ([^,\.]+) is complete"
        ]
        
        for pattern in dependency_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                dependency = match.group(1).strip()
                if dependency and len(dependency) < 100:  # Reasonable length
                    dependencies.append(dependency)
        
        # Entity-based dependencies
        for entity in entities:
            if entity.type in ["prerequisite", "dependency", "requirement"]:
                dependencies.append(entity.name)
        
        return list(set(dependencies))  # Remove duplicates
    
    def generate_success_criteria(self, entities: List[Entity], task_description: str) -> List[str]:
        """
        Generate success criteria for the task.
        
        Args:
            entities: Extracted entities
            task_description: Original task description
            
        Returns:
            List of success criteria
        """
        criteria = []
        
        # Default criteria based on task type
        if any(e.type == "feature" for e in entities):
            criteria.extend([
                "Feature implementation is complete and functional",
                "All acceptance criteria are met",
                "Unit tests pass with adequate coverage",
                "Code review is completed and approved"
            ])
        
        if any(e.type == "bug" for e in entities):
            criteria.extend([
                "Bug is reproduced and root cause identified",
                "Fix is implemented and tested",
                "Regression tests pass",
                "No new issues are introduced"
            ])
        
        if any(e.type in ["security", "vulnerability"] for e in entities):
            criteria.extend([
                "Security vulnerability is addressed",
                "Security tests pass",
                "No new security risks are introduced"
            ])
        
        if any(e.type == "performance" for e in entities):
            criteria.extend([
                "Performance requirements are met",
                "Performance tests pass",
                "No performance regressions"
            ])
        
        # Generic criteria if no specific type found
        if not criteria:
            criteria.extend([
                "Implementation meets requirements",
                "All tests pass",
                "Code quality standards are met",
                "Documentation is updated"
            ])
        
        return criteria
    
    def _build_context_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for context detection."""
        return {
            "@code": [
                r"\b(implement|build|create|develop|code|program|write)\b",
                r"\b(function|method|class|module|component|service)\b",
                r"\b(algorithm|logic|functionality)\b"
            ],
            "@debug": [
                r"\b(debug|fix|troubleshoot|resolve|investigate)\b",
                r"\b(bug|error|issue|problem|failure)\b",
                r"\b(broken|failing|not working)\b"
            ],
            "@test": [
                r"\b(test|testing|verify|validate|check)\b",
                r"\b(unit test|integration test|test suite)\b",
                r"\b(coverage|quality assurance|qa)\b",
                r"\b(create|implement|build|dashboard|feature)\b"
            ],
            "@agile": [
                r"\b(user story|sprint|backlog|scrum)\b",
                r"\b(requirements|acceptance criteria)\b",
                r"\b(epic|story points|planning)\b",
                r"\b(feature|dashboard|user)\b"
            ],
            "@design": [
                r"\b(design|architecture|structure|pattern)\b",
                r"\b(system design|architectural|blueprint)\b",
                r"\b(framework|infrastructure|foundation)\b",
                r"\b(dashboard|interface|ui|ux)\b"
            ],
            "@docs": [
                r"\b(document|documentation|readme|guide)\b",
                r"\b(manual|wiki|help|tutorial)\b",
                r"\b(api doc|user guide|specification)\b"
            ],
            "@security": [
                r"\b(security|secure|vulnerability|exploit)\b",
                r"\b(authentication|authorization|encryption)\b",
                r"\b(audit|penetration|compliance)\b"
            ],
            "@optimize": [
                r"\b(optimize|performance|speed|efficiency)\b",
                r"\b(benchmark|profiling|tuning)\b",
                r"\b(scalability|throughput|latency)\b"
            ],
            "@git": [
                r"\b(commit|push|deploy|release)\b",
                r"\b(version control|git|repository)\b",
                r"\b(merge|branch|pull request)\b"
            ]
        }
    
    def _build_entity_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for entity extraction."""
        return {
            "feature": [
                r"\b(feature|functionality|capability)\s+([a-zA-Z0-9\s]+)",
                r"\b(add|create|build)\s+([a-zA-Z0-9\s]+)\s+(feature|function)",
                r"\b([a-zA-Z0-9\s]+)\s+feature\b",
                r"\b(implement|develop)\s+([a-zA-Z0-9\s]+)\s+(dashboard|feature|functionality)"
            ],
            "bug": [
                r"\b(bug|issue|problem|error)\s+([a-zA-Z0-9\s#]+)",
                r"\b(fix|resolve)\s+([a-zA-Z0-9\s]+)\s+(bug|issue)",
                r"\b([a-zA-Z0-9\s]+)\s+(not working|broken|failing)\b"
            ],
            "component": [
                r"\b(component|module|service|class)\s+([a-zA-Z0-9\s]+)",
                r"\b([A-Z][a-zA-Z0-9]*Component|[A-Z][a-zA-Z0-9]*Service)\b",
                r"\b([a-zA-Z0-9\s]+)\s+(component|module)\b"
            ],
            "api": [
                r"\b(api|endpoint|route)\s+([a-zA-Z0-9\s/]+)",
                r"\b([a-zA-Z0-9\s]+)\s+(api|endpoint)\b",
                r"\b(REST|GraphQL|HTTP)\s+([a-zA-Z0-9\s]+)"
            ],
            "database": [
                r"\b(database|table|schema|model)\s+([a-zA-Z0-9\s]+)",
                r"\b([a-zA-Z0-9\s]+)\s+(database|table|model)\b",
                r"\b(SQL|NoSQL|MongoDB|PostgreSQL|MySQL)\s+([a-zA-Z0-9\s]+)"
            ],
            "ui": [
                r"\b(ui|interface|screen|page|form)\s+([a-zA-Z0-9\s]+)",
                r"\b([a-zA-Z0-9\s]+)\s+(ui|interface|screen|page)\b",
                r"\b(frontend|client|web)\s+([a-zA-Z0-9\s]+)",
                r"\b(dashboard|panel|widget|chart)\b"
            ],
            "security": [
                r"\b(security|vulnerability|exploit)\s+([a-zA-Z0-9\s]+)",
                r"\b([a-zA-Z0-9\s]+)\s+(security|vulnerability)\b",
                r"\b(auth|authentication|authorization)\s+([a-zA-Z0-9\s]+)"
            ],
            "performance": [
                r"\b(performance|optimization|speed)\s+([a-zA-Z0-9\s]+)",
                r"\b([a-zA-Z0-9\s]+)\s+(performance|optimization)\b",
                r"\b(slow|fast|efficient)\s+([a-zA-Z0-9\s]+)"
            ]
        }
    
    def _build_complexity_indicators(self) -> Dict[str, float]:
        """Build complexity indicators with weights."""
        return {
            "complex": 0.4,
            "complicated": 0.3,
            "advanced": 0.3,
            "sophisticated": 0.3,
            "enterprise": 0.3,
            "scalable": 0.2,
            "distributed": 0.3,
            "microservice": 0.2,
            "integration": 0.2,
            "migration": 0.3,
            "refactor": 0.2,
            "architecture": 0.15,  # Reduced from 0.2
            "system": 0.05,        # Reduced from 0.2 (common word)
            "authentication": 0.05, # Added - common system component
            "multiple": 0.1,
            "various": 0.1,
            "several": 0.1,
            "many": 0.1,
            "very": 0.2            # Added for very long descriptions
        }
    
    def _build_duration_estimates(self) -> Dict[str, Any]:
        """Build duration estimation parameters."""
        return {
            "complexity": {
                "simple": 30,    # 30 minutes base
                "medium": 90,    # 90 minutes base
                "complex": 240   # 240 minutes base
            },
            "per_context": 15,   # 15 minutes per context
            "per_entity": 2      # 2 minutes per entity
        }
    
    def _generate_task_id(self, task_description: str) -> str:
        """Generate unique task ID."""
        import hashlib
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_part = hashlib.md5(task_description.encode()).hexdigest()[:8]
        random_part = str(uuid.uuid4())[:8]
        return f"task_{timestamp}_{hash_part}_{random_part}"
    
    def _calculate_entity_confidence(self, entity_name: str, entity_type: str, text: str) -> float:
        """Calculate confidence score for extracted entity."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on entity name quality
        if len(entity_name) > 2 and entity_name.isalnum():
            confidence += 0.2
        
        # Increase confidence if entity appears multiple times
        occurrences = text.count(entity_name.lower())
        confidence += min(0.2, occurrences * 0.05)
        
        # Increase confidence based on context
        context_words = {
            "feature": ["implement", "add", "create", "build"],
            "bug": ["fix", "resolve", "debug", "issue"],
            "component": ["module", "service", "class"],
            "api": ["endpoint", "route", "rest", "http"]
        }
        
        if entity_type in context_words:
            for word in context_words[entity_type]:
                if word in text:
                    confidence += 0.1
                    break
        
        return min(1.0, confidence)
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate entities."""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.name.lower(), entity.type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _calculate_confidence(self, entities: List[Entity], contexts: List[str], complexity: ComplexityLevel) -> float:
        """Calculate overall analysis confidence."""
        # Start with lower base confidence
        confidence = 0.3  # Base confidence
        
        # Penalize empty or very short descriptions
        task_description = getattr(self, '_current_task_description', '')
        if not task_description or len(task_description.strip()) < 5:
            confidence = 0.2  # Very low confidence for empty/minimal descriptions
        
        # Increase confidence based on entity quality
        if entities:
            avg_entity_confidence = sum(e.confidence for e in entities) / len(entities)
            confidence += avg_entity_confidence * 0.3
        
        # Increase confidence based on context identification
        if contexts:
            confidence += min(0.2, len(contexts) * 0.05)
        
        # Adjust based on complexity assessment
        if complexity != ComplexityLevel.SIMPLE:
            confidence += 0.1
        
        return min(1.0, confidence)
