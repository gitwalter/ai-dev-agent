"""
Prompt A/B Testing Framework
============================

Provides comprehensive A/B testing capabilities for AI agent prompts, including
test creation, execution, statistical analysis, and result reporting. This is
a core component of the prompt engineering system for US-PE-01.

Author: AI-Dev-Agent System
Version: 1.0
Last Updated: Current Session
"""

import logging
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from pathlib import Path

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """A/B test status."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TestType(Enum):
    """Types of A/B tests."""
    PROMPT_VARIATION = "prompt_variation"
    TEMPLATE_COMPARISON = "template_comparison"
    OPTIMIZATION_TEST = "optimization_test"
    PERFORMANCE_TEST = "performance_test"


@dataclass
class ABTest:
    """Represents an A/B test configuration."""
    test_id: str
    name: str
    description: str
    test_type: TestType
    status: TestStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Test variants
    variant_a: Dict[str, Any] = None
    variant_b: Dict[str, Any] = None
    
    # Test parameters
    traffic_split: float = 0.5  # Percentage of traffic to variant B
    sample_size: int = 100  # Target sample size
    confidence_level: float = 0.95  # Statistical confidence level
    min_detectable_effect: float = 0.1  # Minimum detectable effect size
    
    # Results
    results: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.variant_a is None:
            self.variant_a = {}
        if self.variant_b is None:
            self.variant_b = {}
        if self.results is None:
            self.results = {}


@dataclass
class TestResult:
    """Represents a single test result."""
    test_id: str
    variant: str  # 'A' or 'B'
    prompt_id: str
    execution_time: float
    token_count: int
    response_quality: float
    success: bool
    user_satisfaction: Optional[float] = None
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class StatisticalResult:
    """Statistical analysis result."""
    test_id: str
    variant_a_stats: Dict[str, float]
    variant_b_stats: Dict[str, float]
    p_value: float
    confidence_interval: Tuple[float, float]
    effect_size: float
    is_significant: bool
    winner: Optional[str] = None  # 'A', 'B', or None
    recommendation: str = ""


class PromptABTesting:
    """Core A/B testing framework for prompts."""
    
    def __init__(self, tests_dir: str = "prompts/ab_tests"):
        """
        Initialize the A/B testing framework.
        
        Args:
            tests_dir: Directory to store test configurations and results
        """
        self.tests_dir = Path(tests_dir)
        self.tests_dir.mkdir(parents=True, exist_ok=True)
        self.tests: Dict[str, ABTest] = {}
        self.results: List[TestResult] = []
        self._load_tests()
    
    def create_test(self, name: str, description: str, test_type: TestType,
                   variant_a: Dict[str, Any], variant_b: Dict[str, Any],
                   traffic_split: float = 0.5, sample_size: int = 100) -> str:
        """
        Create a new A/B test.
        
        Args:
            name: Test name
            description: Test description
            test_type: Type of test
            variant_a: Configuration for variant A
            variant_b: Configuration for variant B
            traffic_split: Percentage of traffic to variant B (0.0-1.0)
            sample_size: Target sample size
            
        Returns:
            str: Test ID
        """
        test_id = self._generate_test_id(name)
        
        test = ABTest(
            test_id=test_id,
            name=name,
            description=description,
            test_type=test_type,
            status=TestStatus.DRAFT,
            created_at=datetime.utcnow(),
            variant_a=variant_a,
            variant_b=variant_b,
            traffic_split=traffic_split,
            sample_size=sample_size
        )
        
        self.tests[test_id] = test
        self._save_test(test)
        
        logger.info(f"Created A/B test {test_id}: {name}")
        return test_id
    
    def start_test(self, test_id: str) -> bool:
        """
        Start an A/B test.
        
        Args:
            test_id: Test ID
            
        Returns:
            bool: True if test started successfully
        """
        test = self.get_test(test_id)
        if not test:
            return False
        
        if test.status != TestStatus.DRAFT:
            logger.warning(f"Test {test_id} cannot be started from status {test.status}")
            return False
        
        test.status = TestStatus.RUNNING
        test.started_at = datetime.utcnow()
        
        self._save_test(test)
        logger.info(f"Started A/B test {test_id}")
        return True
    
    def pause_test(self, test_id: str) -> bool:
        """
        Pause an A/B test.
        
        Args:
            test_id: Test ID
            
        Returns:
            bool: True if test paused successfully
        """
        test = self.get_test(test_id)
        if not test or test.status != TestStatus.RUNNING:
            return False
        
        test.status = TestStatus.PAUSED
        self._save_test(test)
        logger.info(f"Paused A/B test {test_id}")
        return True
    
    def complete_test(self, test_id: str) -> bool:
        """
        Complete an A/B test.
        
        Args:
            test_id: Test ID
            
        Returns:
            bool: True if test completed successfully
        """
        test = self.get_test(test_id)
        if not test or test.status not in [TestStatus.RUNNING, TestStatus.PAUSED]:
            return False
        
        test.status = TestStatus.COMPLETED
        test.completed_at = datetime.utcnow()
        
        # Analyze results
        try:
            analysis = self.analyze_test(test_id)
            test.results = asdict(analysis)
        except Exception as e:
            logger.warning(f"Could not analyze test results: {e}")
            test.results = {"error": str(e)}
        
        self._save_test(test)
        logger.info(f"Completed A/B test {test_id}")
        return True
    
    def get_test(self, test_id: str) -> Optional[ABTest]:
        """
        Get a test by ID.
        
        Args:
            test_id: Test ID
            
        Returns:
            ABTest or None if not found
        """
        return self.tests.get(test_id)
    
    def get_active_tests(self) -> List[ABTest]:
        """
        Get all active tests.
        
        Returns:
            List of active tests
        """
        return [test for test in self.tests.values() 
                if test.status == TestStatus.RUNNING]
    
    def assign_variant(self, test_id: str, user_id: str = None) -> str:
        """
        Assign a variant to a user for testing.
        
        Args:
            test_id: Test ID
            user_id: User ID (optional)
            
        Returns:
            str: Variant assignment ('A' or 'B')
        """
        test = self.get_test(test_id)
        if not test or test.status != TestStatus.RUNNING:
            raise ValueError(f"Test {test_id} is not running")
        
        # Use user_id for consistent assignment if provided
        if user_id:
            # Hash user_id for consistent assignment
            hash_value = hash(user_id + test_id) % 100
            if hash_value < test.traffic_split * 100:
                return 'B'
            else:
                return 'A'
        else:
            # Random assignment
            return 'B' if random.random() < test.traffic_split else 'A'
    
    def record_result(self, test_id: str, variant: str, prompt_id: str,
                     execution_time: float, token_count: int,
                     response_quality: float, success: bool,
                     user_satisfaction: float = None,
                     metadata: Dict[str, Any] = None) -> str:
        """
        Record a test result.
        
        Args:
            test_id: Test ID
            variant: Variant ('A' or 'B')
            prompt_id: Prompt ID used
            execution_time: Execution time in seconds
            token_count: Number of tokens used
            response_quality: Quality score (0-1)
            success: Whether execution was successful
            user_satisfaction: User satisfaction score (0-1)
            metadata: Additional metadata
            
        Returns:
            str: Result ID
        """
        result = TestResult(
            test_id=test_id,
            variant=variant,
            prompt_id=prompt_id,
            execution_time=execution_time,
            token_count=token_count,
            response_quality=response_quality,
            success=success,
            user_satisfaction=user_satisfaction,
            metadata=metadata or {}
        )
        
        self.results.append(result)
        self._save_result(result)
        
        logger.debug(f"Recorded result for test {test_id}, variant {variant}")
        return result.test_id
    
    def get_test_results(self, test_id: str) -> List[TestResult]:
        """
        Get all results for a test.
        
        Args:
            test_id: Test ID
            
        Returns:
            List of test results
        """
        return [result for result in self.results if result.test_id == test_id]
    
    def analyze_test(self, test_id: str) -> StatisticalResult:
        """
        Perform statistical analysis on test results.
        
        Args:
            test_id: Test ID
            
        Returns:
            StatisticalResult: Analysis results
        """
        test = self.get_test(test_id)
        if not test:
            raise ValueError(f"Test {test_id} not found")
        
        results = self.get_test_results(test_id)
        if len(results) < 10:  # Minimum sample size
            raise ValueError(f"Insufficient data for analysis: {len(results)} results")
        
        return self._perform_statistical_analysis(test, results)
    
    def get_test_summary(self, test_id: str) -> Dict[str, Any]:
        """
        Get a summary of test results.
        
        Args:
            test_id: Test ID
            
        Returns:
            Test summary
        """
        test = self.get_test(test_id)
        if not test:
            return {}
        
        results = self.get_test_results(test_id)
        variant_a_results = [r for r in results if r.variant == 'A']
        variant_b_results = [r for r in results if r.variant == 'B']
        
        summary = {
            "test_id": test_id,
            "name": test.name,
            "status": test.status.value,
            "total_results": len(results),
            "variant_a_results": len(variant_a_results),
            "variant_b_results": len(variant_b_results),
            "completion_percentage": min(100, (len(results) / test.sample_size) * 100)
        }
        
        if variant_a_results:
            summary["variant_a_stats"] = {
                "avg_execution_time": statistics.mean(r.execution_time for r in variant_a_results),
                "avg_token_count": statistics.mean(r.token_count for r in variant_a_results),
                "avg_quality": statistics.mean(r.response_quality for r in variant_a_results),
                "success_rate": sum(1 for r in variant_a_results if r.success) / len(variant_a_results)
            }
        
        if variant_b_results:
            summary["variant_b_stats"] = {
                "avg_execution_time": statistics.mean(r.execution_time for r in variant_b_results),
                "avg_token_count": statistics.mean(r.token_count for r in variant_b_results),
                "avg_quality": statistics.mean(r.response_quality for r in variant_b_results),
                "success_rate": sum(1 for r in variant_b_results if r.success) / len(variant_b_results)
            }
        
        return summary
    
    def _generate_test_id(self, name: str) -> str:
        """Generate a unique test ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = name.lower().replace(' ', '_').replace('-', '_').replace('/', '_')
        return f"ab_test_{safe_name}_{timestamp}"
    
    def _save_test(self, test: ABTest):
        """Save test configuration to file."""
        # Ensure directory exists
        self.tests_dir.mkdir(parents=True, exist_ok=True)
        test_file = self.tests_dir / f"{test.test_id}.json"
        with open(test_file, 'w') as f:
            json.dump(asdict(test), f, indent=2, default=str)
    
    def _save_result(self, result: TestResult):
        """Save test result to file."""
        # Ensure directory exists
        self.tests_dir.mkdir(parents=True, exist_ok=True)
        results_file = self.tests_dir / f"results_{result.test_id}.json"
        
        # Load existing results
        existing_results = []
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    existing_results = json.load(f)
            except json.JSONDecodeError:
                existing_results = []
        
        # Add new result
        existing_results.append(asdict(result))
        
        # Save updated results
        with open(results_file, 'w') as f:
            json.dump(existing_results, f, indent=2, default=str)
    
    def _load_tests(self):
        """Load all tests from files."""
        for test_file in self.tests_dir.glob("*.json"):
            if test_file.name.startswith("results_"):
                continue  # Skip result files
            
            try:
                with open(test_file, 'r') as f:
                    data = json.load(f)
                
                # Convert string values back to enums
                data['test_type'] = TestType(data['test_type'])
                data['status'] = TestStatus(data['status'])
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                
                if data.get('started_at'):
                    data['started_at'] = datetime.fromisoformat(data['started_at'])
                if data.get('completed_at'):
                    data['completed_at'] = datetime.fromisoformat(data['completed_at'])
                
                test = ABTest(**data)
                self.tests[test.test_id] = test
                
            except Exception as e:
                logger.error(f"Failed to load test from {test_file}: {e}")
    
    def _perform_statistical_analysis(self, test: ABTest, results: List[TestResult]) -> StatisticalResult:
        """Perform statistical analysis on test results."""
        variant_a_results = [r for r in results if r.variant == 'A']
        variant_b_results = [r for r in results if r.variant == 'B']
        
        if not variant_a_results or not variant_b_results:
            raise ValueError("Both variants must have results for analysis")
        
        # Calculate statistics for each variant
        variant_a_stats = self._calculate_variant_stats(variant_a_results)
        variant_b_stats = self._calculate_variant_stats(variant_b_results)
        
        # Perform t-test for quality scores
        a_quality_scores = [r.response_quality for r in variant_a_results]
        b_quality_scores = [r.response_quality for r in variant_b_results]
        
        p_value = self._calculate_p_value(a_quality_scores, b_quality_scores)
        effect_size = self._calculate_effect_size(a_quality_scores, b_quality_scores)
        confidence_interval = self._calculate_confidence_interval(a_quality_scores, b_quality_scores, test.confidence_level)
        
        # Determine significance and winner
        is_significant = p_value < (1 - test.confidence_level)
        winner = None
        
        if is_significant:
            if variant_b_stats['avg_quality'] > variant_a_stats['avg_quality']:
                winner = 'B'
            else:
                winner = 'A'
        
        # Generate recommendation
        recommendation = self._generate_recommendation(test, is_significant, winner, effect_size)
        
        return StatisticalResult(
            test_id=test.test_id,
            variant_a_stats=variant_a_stats,
            variant_b_stats=variant_b_stats,
            p_value=p_value,
            confidence_interval=confidence_interval,
            effect_size=effect_size,
            is_significant=is_significant,
            winner=winner,
            recommendation=recommendation
        )
    
    def _calculate_variant_stats(self, results: List[TestResult]) -> Dict[str, float]:
        """Calculate statistics for a variant."""
        if not results:
            return {}
        
        return {
            "avg_execution_time": statistics.mean(r.execution_time for r in results),
            "avg_token_count": statistics.mean(r.token_count for r in results),
            "avg_quality": statistics.mean(r.response_quality for r in results),
            "success_rate": sum(1 for r in results if r.success) / len(results),
            "std_execution_time": statistics.stdev(r.execution_time for r in results) if len(results) > 1 else 0,
            "std_quality": statistics.stdev(r.response_quality for r in results) if len(results) > 1 else 0
        }
    
    def _calculate_p_value(self, group_a: List[float], group_b: List[float]) -> float:
        """Calculate p-value using t-test."""
        try:
            # Simple t-test implementation
            mean_a = statistics.mean(group_a)
            mean_b = statistics.mean(group_b)
            
            var_a = statistics.variance(group_a) if len(group_a) > 1 else 0
            var_b = statistics.variance(group_b) if len(group_b) > 1 else 0
            
            n_a = len(group_a)
            n_b = len(group_b)
            
            # Pooled standard error
            pooled_se = ((var_a / n_a) + (var_b / n_b)) ** 0.5
            
            if pooled_se == 0:
                return 1.0
            
            # t-statistic
            t_stat = (mean_b - mean_a) / pooled_se
            
            # Approximate p-value (simplified)
            if abs(t_stat) > 2.0:
                return 0.05  # Significant
            elif abs(t_stat) > 1.5:
                return 0.1   # Marginally significant
            else:
                return 0.5   # Not significant
                
        except Exception:
            return 1.0  # Default to not significant
    
    def _calculate_effect_size(self, group_a: List[float], group_b: List[float]) -> float:
        """Calculate Cohen's d effect size."""
        try:
            mean_a = statistics.mean(group_a)
            mean_b = statistics.mean(group_b)
            
            pooled_std = statistics.stdev(group_a + group_b) if len(group_a + group_b) > 1 else 1
            
            if pooled_std == 0:
                return 0.0
            
            return (mean_b - mean_a) / pooled_std
        except Exception:
            return 0.0
    
    def _calculate_confidence_interval(self, group_a: List[float], group_b: List[float], 
                                     confidence_level: float) -> Tuple[float, float]:
        """Calculate confidence interval for difference in means."""
        try:
            mean_a = statistics.mean(group_a)
            mean_b = statistics.mean(group_b)
            
            var_a = statistics.variance(group_a) if len(group_a) > 1 else 0
            var_b = statistics.variance(group_b) if len(group_b) > 1 else 0
            
            n_a = len(group_a)
            n_b = len(group_b)
            
            pooled_se = ((var_a / n_a) + (var_b / n_b)) ** 0.5
            
            # Z-score for confidence level (simplified)
            z_score = 1.96 if confidence_level == 0.95 else 1.645
            
            margin_of_error = z_score * pooled_se
            difference = mean_b - mean_a
            
            return (difference - margin_of_error, difference + margin_of_error)
        except Exception:
            return (0.0, 0.0)
    
    def _generate_recommendation(self, test: ABTest, is_significant: bool, 
                               winner: Optional[str], effect_size: float) -> str:
        """Generate recommendation based on test results."""
        if not is_significant:
            return "No significant difference found. Consider running the test longer or with more samples."
        
        if winner == 'B':
            if effect_size > 0.5:
                return f"Strong evidence that variant B is better (effect size: {effect_size:.2f}). Recommend adopting variant B."
            else:
                return f"Variant B is better but effect is small (effect size: {effect_size:.2f}). Consider the practical significance."
        elif winner == 'A':
            if effect_size > 0.5:
                return f"Strong evidence that variant A is better (effect size: {effect_size:.2f}). Recommend keeping variant A."
            else:
                return f"Variant A is better but effect is small (effect size: {effect_size:.2f}). Consider the practical significance."
        else:
            return "No clear winner despite statistical significance. Consider other factors in decision making."


# Global A/B testing instance
_ab_testing = None

def get_ab_testing() -> PromptABTesting:
    """Get the global A/B testing instance."""
    global _ab_testing
    if _ab_testing is None:
        _ab_testing = PromptABTesting()
    return _ab_testing
