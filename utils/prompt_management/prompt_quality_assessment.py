"""
Prompt Quality Assessment System

Provides automated quality assessment for prompts including:
- Quality scoring algorithms
- Automated improvement suggestions
- Quality trend monitoring
- Benchmarking against best practices

This module implements the automated prompt quality assessment for US-PE-02.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import re
from textblob import TextBlob

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Quality dimensions for prompt assessment."""
    CLARITY = "clarity"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    SPECIFICITY = "specificity"
    STRUCTURE = "structure"
    LANGUAGE = "language"


class QualityLevel(Enum):
    """Quality levels for prompts."""
    EXCELLENT = "excellent"  # 0.9-1.0
    GOOD = "good"           # 0.7-0.89
    AVERAGE = "average"     # 0.5-0.69
    POOR = "poor"           # 0.3-0.49
    UNACCEPTABLE = "unacceptable"  # 0.0-0.29


@dataclass
class QualityScore:
    """Quality score for a specific dimension."""
    dimension: QualityDimension
    score: float  # 0.0 to 1.0
    weight: float  # Weight for overall calculation
    reasoning: str  # Explanation for the score
    suggestions: List[str]  # Improvement suggestions


@dataclass
class OverallQualityAssessment:
    """Overall quality assessment for a prompt."""
    prompt_id: str
    overall_score: float  # 0.0 to 1.0
    quality_level: QualityLevel
    dimension_scores: Dict[QualityDimension, QualityScore]
    strengths: List[str]  # What's working well
    weaknesses: List[str]  # Areas for improvement
    improvement_priority: str  # "low", "medium", "high", "critical"
    assessment_date: datetime
    metadata: Dict[str, Any] = None


@dataclass
class QualityBenchmark:
    """Quality benchmark for comparison."""
    benchmark_name: str
    benchmark_type: str  # "industry", "internal", "best_practice"
    score_threshold: float
    description: str
    created_at: datetime


class PromptQualityAssessor:
    """
    Automated prompt quality assessment system.
    """
    
    def __init__(self, db_path: str = "prompts/analytics/prompt_quality.db"):
        """Initialize the quality assessor."""
        self.db_path = db_path
        self._init_database()
        self._load_benchmarks()
        
        # Quality dimension weights
        self.dimension_weights = {
            QualityDimension.CLARITY: 0.25,
            QualityDimension.RELEVANCE: 0.20,
            QualityDimension.COMPLETENESS: 0.20,
            QualityDimension.CONSISTENCY: 0.15,
            QualityDimension.SPECIFICITY: 0.10,
            QualityDimension.STRUCTURE: 0.05,
            QualityDimension.LANGUAGE: 0.05
        }
    
    def _init_database(self):
        """Initialize the quality assessment database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Quality assessments table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS quality_assessments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_id TEXT NOT NULL,
                        overall_score REAL NOT NULL,
                        quality_level TEXT NOT NULL,
                        dimension_scores TEXT NOT NULL,
                        strengths TEXT,
                        weaknesses TEXT,
                        improvement_priority TEXT NOT NULL,
                        assessment_date TEXT NOT NULL,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Quality benchmarks table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS quality_benchmarks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        benchmark_name TEXT NOT NULL,
                        benchmark_type TEXT NOT NULL,
                        score_threshold REAL NOT NULL,
                        description TEXT,
                        created_at TEXT NOT NULL
                    )
                """)
                
                # Quality trends table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS quality_trends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_id TEXT NOT NULL,
                        assessment_date TEXT NOT NULL,
                        overall_score REAL NOT NULL,
                        quality_level TEXT NOT NULL,
                        trend_direction TEXT,
                        change_percentage REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize quality assessment database: {e}")
    
    def _load_benchmarks(self):
        """Load quality benchmarks."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM quality_benchmarks")
                rows = cursor.fetchall()
                
                if not rows:
                    # Create default benchmarks
                    self._create_default_benchmarks()
                    
        except Exception as e:
            logger.error(f"Failed to load benchmarks: {e}")
    
    def _create_default_benchmarks(self):
        """Create default quality benchmarks."""
        default_benchmarks = [
            QualityBenchmark(
                benchmark_name="Industry Standard",
                benchmark_type="industry",
                score_threshold=0.7,
                description="Minimum acceptable quality for production use",
                created_at=datetime.now()
            ),
            QualityBenchmark(
                benchmark_name="Best Practice",
                benchmark_type="best_practice",
                score_threshold=0.85,
                description="High-quality prompts following best practices",
                created_at=datetime.now()
            ),
            QualityBenchmark(
                benchmark_name="Internal Standard",
                benchmark_type="internal",
                score_threshold=0.75,
                description="Our internal quality standard",
                created_at=datetime.now()
            )
        ]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for benchmark in default_benchmarks:
                    cursor.execute("""
                        INSERT INTO quality_benchmarks 
                        (benchmark_name, benchmark_type, score_threshold, description, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        benchmark.benchmark_name,
                        benchmark.benchmark_type,
                        benchmark.score_threshold,
                        benchmark.description,
                        benchmark.created_at.isoformat()
                    ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to create default benchmarks: {e}")
    
    def assess_prompt_quality(self, prompt_id: str, prompt_text: str, 
                             context: Dict[str, Any] = None) -> OverallQualityAssessment:
        """
        Assess the quality of a prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            prompt_text: The prompt text to assess
            context: Additional context for assessment
            
        Returns:
            OverallQualityAssessment with quality scores and recommendations
        """
        try:
            # Assess each quality dimension
            dimension_scores = {}
            for dimension in QualityDimension:
                score = self._assess_dimension(dimension, prompt_text, context)
                dimension_scores[dimension] = score
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(dimension_scores)
            quality_level = self._determine_quality_level(overall_score)
            
            # Identify strengths and weaknesses
            strengths = self._identify_strengths(dimension_scores)
            weaknesses = self._identify_weaknesses(dimension_scores)
            
            # Determine improvement priority
            improvement_priority = self._determine_improvement_priority(overall_score, weaknesses)
            
            # Create assessment
            assessment = OverallQualityAssessment(
                prompt_id=prompt_id,
                overall_score=overall_score,
                quality_level=quality_level,
                dimension_scores=dimension_scores,
                strengths=strengths,
                weaknesses=weaknesses,
                improvement_priority=improvement_priority,
                assessment_date=datetime.now(),
                metadata=context
            )
            
            # Save assessment
            self._save_assessment(assessment)
            
            # Update trends
            self._update_quality_trends(prompt_id, overall_score, quality_level)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Failed to assess prompt quality: {e}")
            raise
    
    def _assess_dimension(self, dimension: QualityDimension, prompt_text: str, 
                          context: Dict[str, Any] = None) -> QualityScore:
        """Assess a specific quality dimension."""
        
        if dimension == QualityDimension.CLARITY:
            return self._assess_clarity(prompt_text)
        elif dimension == QualityDimension.RELEVANCE:
            return self._assess_relevance(prompt_text, context)
        elif dimension == QualityDimension.COMPLETENESS:
            return self._assess_completeness(prompt_text, context)
        elif dimension == QualityDimension.CONSISTENCY:
            return self._assess_consistency(prompt_text)
        elif dimension == QualityDimension.SPECIFICITY:
            return self._assess_specificity(prompt_text)
        elif dimension == QualityDimension.STRUCTURE:
            return self._assess_structure(prompt_text)
        elif dimension == QualityDimension.LANGUAGE:
            return self._assess_language(prompt_text)
        else:
            raise ValueError(f"Unknown quality dimension: {dimension}")
    
    def _assess_clarity(self, prompt_text: str) -> QualityScore:
        """Assess prompt clarity."""
        score = 0.0
        reasoning = []
        suggestions = []
        
        # Check sentence length
        sentences = prompt_text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        if avg_sentence_length <= 15:
            score += 0.3
            reasoning.append("Sentence length is appropriate")
        elif avg_sentence_length <= 25:
            score += 0.2
            reasoning.append("Sentence length is acceptable")
            suggestions.append("Consider breaking down long sentences")
        else:
            reasoning.append("Sentences are too long")
            suggestions.append("Break down long sentences into shorter ones")
        
        # Check for clear instructions
        instruction_words = ['please', 'should', 'must', 'need to', 'require']
        has_clear_instructions = any(word in prompt_text.lower() for word in instruction_words)
        
        if has_clear_instructions:
            score += 0.4
            reasoning.append("Clear instructions provided")
        else:
            reasoning.append("Missing clear instructions")
            suggestions.append("Add clear instructions using words like 'please', 'should', 'must'")
        
        # Check for ambiguity
        ambiguous_words = ['it', 'this', 'that', 'they', 'them']
        ambiguous_count = sum(1 for word in ambiguous_words if word in prompt_text.lower())
        
        if ambiguous_count == 0:
            score += 0.3
            reasoning.append("No ambiguous references found")
        elif ambiguous_count <= 2:
            score += 0.2
            reasoning.append("Few ambiguous references")
            suggestions.append("Clarify ambiguous references")
        else:
            reasoning.append("Multiple ambiguous references")
            suggestions.append("Replace ambiguous references with specific terms")
        
        return QualityScore(
            dimension=QualityDimension.CLARITY,
            score=min(score, 1.0),
            weight=self.dimension_weights[QualityDimension.CLARITY],
            reasoning="; ".join(reasoning),
            suggestions=suggestions
        )
    
    def _assess_relevance(self, prompt_text: str, context: Dict[str, Any] = None) -> QualityScore:
        """Assess prompt relevance."""
        score = 0.0
        reasoning = []
        suggestions = []
        
        # Check for context-specific terms
        if context and 'domain' in context:
            domain_terms = self._get_domain_terms(context['domain'])
            relevant_terms = sum(1 for term in domain_terms if term.lower() in prompt_text.lower())
            
            if relevant_terms >= 3:
                score += 0.5
                reasoning.append("Contains relevant domain-specific terms")
            elif relevant_terms >= 1:
                score += 0.3
                reasoning.append("Contains some domain-specific terms")
                suggestions.append("Include more domain-specific terminology")
            else:
                reasoning.append("Missing domain-specific terms")
                suggestions.append("Add relevant domain-specific terminology")
        
        # Check for task-specific language
        task_words = ['analyze', 'create', 'generate', 'explain', 'summarize', 'compare']
        has_task_language = any(word in prompt_text.lower() for word in task_words)
        
        if has_task_language:
            score += 0.5
            reasoning.append("Clear task language used")
        else:
            reasoning.append("Missing clear task language")
            suggestions.append("Use specific task verbs like 'analyze', 'create', 'generate'")
        
        return QualityScore(
            dimension=QualityDimension.RELEVANCE,
            score=min(score, 1.0),
            weight=self.dimension_weights[QualityDimension.RELEVANCE],
            reasoning="; ".join(reasoning),
            suggestions=suggestions
        )
    
    def _assess_completeness(self, prompt_text: str, context: Dict[str, Any] = None) -> QualityScore:
        """Assess prompt completeness."""
        score = 0.0
        reasoning = []
        suggestions = []
        
        # Check for required components
        required_components = ['context', 'task', 'output_format']
        component_scores = {}
        
        # Context check
        if len(prompt_text) > 100:
            component_scores['context'] = 0.3
            reasoning.append("Adequate context provided")
        else:
            component_scores['context'] = 0.0
            reasoning.append("Insufficient context")
            suggestions.append("Provide more context for better understanding")
        
        # Task check
        if any(word in prompt_text.lower() for word in ['analyze', 'create', 'generate', 'explain']):
            component_scores['task'] = 0.3
            reasoning.append("Clear task defined")
        else:
            component_scores['task'] = 0.0
            reasoning.append("Task not clearly defined")
            suggestions.append("Clearly define the task to be performed")
        
        # Output format check
        if any(word in prompt_text.lower() for word in ['format', 'output', 'result', 'response']):
            component_scores['output_format'] = 0.4
            reasoning.append("Output format specified")
        else:
            component_scores['output_format'] = 0.0
            reasoning.append("Output format not specified")
            suggestions.append("Specify the expected output format")
        
        score = sum(component_scores.values())
        
        return QualityScore(
            dimension=QualityDimension.COMPLETENESS,
            score=min(score, 1.0),
            weight=self.dimension_weights[QualityDimension.COMPLETENESS],
            reasoning="; ".join(reasoning),
            suggestions=suggestions
        )
    
    def _assess_consistency(self, prompt_text: str) -> QualityScore:
        """Assess prompt consistency."""
        score = 0.0
        reasoning = []
        suggestions = []
        
        # Check for consistent terminology
        words = prompt_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Check for consistent capitalization
        lines = prompt_text.split('\n')
        capitalization_consistent = all(
            line.strip() == '' or line.strip()[0].isupper() or line.strip()[0].isdigit()
            for line in lines
        )
        
        if capitalization_consistent:
            score += 0.5
            reasoning.append("Consistent capitalization")
        else:
            reasoning.append("Inconsistent capitalization")
            suggestions.append("Maintain consistent capitalization throughout")
        
        # Check for consistent formatting
        has_consistent_formatting = len(set(len(line.strip()) for line in lines if line.strip())) <= 3
        
        if has_consistent_formatting:
            score += 0.5
            reasoning.append("Consistent formatting")
        else:
            reasoning.append("Inconsistent formatting")
            suggestions.append("Maintain consistent formatting and structure")
        
        return QualityScore(
            dimension=QualityDimension.CONSISTENCY,
            score=min(score, 1.0),
            weight=self.dimension_weights[QualityDimension.CONSISTENCY],
            reasoning="; ".join(reasoning),
            suggestions=suggestions
        )
    
    def _assess_specificity(self, prompt_text: str) -> QualityScore:
        """Assess prompt specificity."""
        score = 0.0
        reasoning = []
        suggestions = []
        
        # Check for specific numbers/quantities
        specific_numbers = re.findall(r'\d+', prompt_text)
        if len(specific_numbers) >= 2:
            score += 0.4
            reasoning.append("Contains specific quantities")
        elif len(specific_numbers) >= 1:
            score += 0.2
            reasoning.append("Contains some specific quantities")
            suggestions.append("Add more specific quantities where appropriate")
        else:
            reasoning.append("Missing specific quantities")
            suggestions.append("Include specific numbers, quantities, or measurements")
        
        # Check for specific examples
        example_indicators = ['for example', 'such as', 'like', 'including']
        has_examples = any(indicator in prompt_text.lower() for indicator in example_indicators)
        
        if has_examples:
            score += 0.3
            reasoning.append("Contains examples")
        else:
            reasoning.append("Missing examples")
            suggestions.append("Include specific examples to clarify requirements")
        
        # Check for specific constraints
        constraint_words = ['must', 'should', 'cannot', 'only', 'exactly']
        has_constraints = any(word in prompt_text.lower() for word in constraint_words)
        
        if has_constraints:
            score += 0.3
            reasoning.append("Contains specific constraints")
        else:
            reasoning.append("Missing specific constraints")
            suggestions.append("Specify constraints and limitations")
        
        return QualityScore(
            dimension=QualityDimension.SPECIFICITY,
            score=min(score, 1.0),
            weight=self.dimension_weights[QualityDimension.SPECIFICITY],
            reasoning="; ".join(reasoning),
            suggestions=suggestions
        )
    
    def _assess_structure(self, prompt_text: str) -> QualityScore:
        """Assess prompt structure."""
        score = 0.0
        reasoning = []
        suggestions = []
        
        # Check for logical organization
        paragraphs = [p.strip() for p in prompt_text.split('\n\n') if p.strip()]
        
        if len(paragraphs) >= 2:
            score += 0.5
            reasoning.append("Well-structured with multiple paragraphs")
        elif len(paragraphs) == 1:
            score += 0.3
            reasoning.append("Single paragraph structure")
            suggestions.append("Consider breaking into logical paragraphs")
        else:
            reasoning.append("Poor structure")
            suggestions.append("Organize content into logical paragraphs")
        
        # Check for clear sections
        section_indicators = ['context:', 'task:', 'requirements:', 'output:']
        has_sections = any(indicator in prompt_text.lower() for indicator in section_indicators)
        
        if has_sections:
            score += 0.5
            reasoning.append("Clear section organization")
        else:
            reasoning.append("Missing clear section organization")
            suggestions.append("Use section headers to organize content")
        
        return QualityScore(
            dimension=QualityDimension.STRUCTURE,
            score=min(score, 1.0),
            weight=self.dimension_weights[QualityDimension.STRUCTURE],
            reasoning="; ".join(reasoning),
            suggestions=suggestions
        )
    
    def _assess_language(self, prompt_text: str) -> QualityScore:
        """Assess prompt language quality."""
        score = 0.0
        reasoning = []
        suggestions = []
        
        # Check for grammar and spelling
        blob = TextBlob(prompt_text)
        language_score = blob.sentiment.polarity
        
        if language_score >= 0:
            score += 0.5
            reasoning.append("Positive and clear language")
        else:
            score += 0.2
            reasoning.append("Language could be more positive")
            suggestions.append("Use more positive and clear language")
        
        # Check for professional tone
        professional_words = ['please', 'kindly', 'would you', 'could you']
        has_professional_tone = any(word in prompt_text.lower() for word in professional_words)
        
        if has_professional_tone:
            score += 0.5
            reasoning.append("Professional tone maintained")
        else:
            reasoning.append("Could use more professional tone")
            suggestions.append("Use polite and professional language")
        
        return QualityScore(
            dimension=QualityDimension.LANGUAGE,
            score=min(score, 1.0),
            weight=self.dimension_weights[QualityDimension.LANGUAGE],
            reasoning="; ".join(reasoning),
            suggestions=suggestions
        )
    
    def _calculate_overall_score(self, dimension_scores: Dict[QualityDimension, QualityScore]) -> float:
        """Calculate overall quality score."""
        total_score = 0.0
        total_weight = 0.0
        
        for dimension, score in dimension_scores.items():
            total_score += score.score * score.weight
            total_weight += score.weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """Determine quality level based on overall score."""
        if overall_score >= 0.9:
            return QualityLevel.EXCELLENT
        elif overall_score >= 0.7:
            return QualityLevel.GOOD
        elif overall_score >= 0.5:
            return QualityLevel.AVERAGE
        elif overall_score >= 0.3:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE
    
    def _identify_strengths(self, dimension_scores: Dict[QualityDimension, QualityScore]) -> List[str]:
        """Identify prompt strengths."""
        strengths = []
        for dimension, score in dimension_scores.items():
            if score.score >= 0.8:
                strengths.append(f"Strong {dimension.value}")
        return strengths
    
    def _identify_weaknesses(self, dimension_scores: Dict[QualityDimension, QualityScore]) -> List[str]:
        """Identify prompt weaknesses."""
        weaknesses = []
        for dimension, score in dimension_scores.items():
            if score.score < 0.6:
                weaknesses.append(f"Needs improvement in {dimension.value}")
        return weaknesses
    
    def _determine_improvement_priority(self, overall_score: float, weaknesses: List[str]) -> str:
        """Determine improvement priority."""
        if overall_score < 0.5 or len(weaknesses) >= 4:
            return "critical"
        elif overall_score < 0.7 or len(weaknesses) >= 2:
            return "high"
        elif overall_score < 0.8 or len(weaknesses) >= 1:
            return "medium"
        else:
            return "low"
    
    def _get_domain_terms(self, domain: str) -> List[str]:
        """Get domain-specific terms for relevance assessment."""
        domain_terms = {
            "software_development": ["code", "function", "class", "method", "algorithm", "database", "API"],
            "data_science": ["data", "analysis", "model", "algorithm", "visualization", "statistics"],
            "business": ["strategy", "market", "customer", "revenue", "growth", "analysis"],
            "education": ["learning", "teaching", "curriculum", "assessment", "student", "knowledge"],
            "healthcare": ["patient", "treatment", "diagnosis", "medical", "health", "care"]
        }
        return domain_terms.get(domain, [])
    
    def _save_assessment(self, assessment: OverallQualityAssessment):
        """Save quality assessment to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quality_assessments 
                    (prompt_id, overall_score, quality_level, dimension_scores,
                     strengths, weaknesses, improvement_priority, assessment_date, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    assessment.prompt_id,
                    assessment.overall_score,
                    assessment.quality_level.value,
                    json.dumps({dim.value: {
                        'score': score.score,
                        'weight': score.weight,
                        'reasoning': score.reasoning,
                        'suggestions': score.suggestions
                    } for dim, score in assessment.dimension_scores.items()}),
                    json.dumps(assessment.strengths),
                    json.dumps(assessment.weaknesses),
                    assessment.improvement_priority,
                    assessment.assessment_date.isoformat(),
                    json.dumps(assessment.metadata) if assessment.metadata else None
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save quality assessment: {e}")
    
    def _update_quality_trends(self, prompt_id: str, overall_score: float, quality_level: QualityLevel):
        """Update quality trends for a prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get previous assessment
                cursor.execute("""
                    SELECT overall_score, quality_level FROM quality_assessments 
                    WHERE prompt_id = ? ORDER BY assessment_date DESC LIMIT 2
                """, (prompt_id,))
                rows = cursor.fetchall()
                
                if len(rows) >= 2:
                    previous_score = rows[1][0]
                    change_percentage = ((overall_score - previous_score) / previous_score) * 100
                    
                    if change_percentage > 5:
                        trend_direction = "improving"
                    elif change_percentage < -5:
                        trend_direction = "declining"
                    else:
                        trend_direction = "stable"
                else:
                    change_percentage = 0.0
                    trend_direction = "new"
                
                # Insert trend data
                cursor.execute("""
                    INSERT INTO quality_trends 
                    (prompt_id, assessment_date, overall_score, quality_level, 
                     trend_direction, change_percentage)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    prompt_id,
                    datetime.now().isoformat(),
                    overall_score,
                    quality_level.value,
                    trend_direction,
                    change_percentage
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to update quality trends: {e}")
    
    def get_quality_history(self, prompt_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get quality assessment history for a prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT overall_score, quality_level, assessment_date, strengths, weaknesses
                    FROM quality_assessments 
                    WHERE prompt_id = ? AND assessment_date >= ?
                    ORDER BY assessment_date DESC
                """, (prompt_id, (datetime.now() - timedelta(days=days)).isoformat()))
                
                rows = cursor.fetchall()
                history = []
                for row in rows:
                    history.append({
                        "overall_score": row[0],
                        "quality_level": row[1],
                        "assessment_date": row[2],
                        "strengths": json.loads(row[3]) if row[3] else [],
                        "weaknesses": json.loads(row[4]) if row[4] else []
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Failed to get quality history: {e}")
            return []
    
    def get_quality_benchmarks(self) -> List[QualityBenchmark]:
        """Get all quality benchmarks."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM quality_benchmarks")
                rows = cursor.fetchall()
                
                benchmarks = []
                for row in rows:
                    benchmarks.append(QualityBenchmark(
                        benchmark_name=row[1],
                        benchmark_type=row[2],
                        score_threshold=row[3],
                        description=row[4],
                        created_at=datetime.fromisoformat(row[5])
                    ))
                
                return benchmarks
                
        except Exception as e:
            logger.error(f"Failed to get quality benchmarks: {e}")
            return []
    
    def compare_to_benchmarks(self, overall_score: float) -> Dict[str, Any]:
        """Compare quality score to benchmarks."""
        benchmarks = self.get_quality_benchmarks()
        comparison = {}
        
        for benchmark in benchmarks:
            if overall_score >= benchmark.score_threshold:
                comparison[benchmark.benchmark_name] = {
                    "status": "meets",
                    "threshold": benchmark.score_threshold,
                    "margin": overall_score - benchmark.score_threshold
                }
            else:
                comparison[benchmark.benchmark_name] = {
                    "status": "below",
                    "threshold": benchmark.score_threshold,
                    "gap": benchmark.score_threshold - overall_score
                }
        
        return comparison


# Factory function
def get_quality_assessor(db_path: str = "prompts/analytics/prompt_quality.db") -> PromptQualityAssessor:
    """Get a quality assessor instance."""
    return PromptQualityAssessor(db_path)
