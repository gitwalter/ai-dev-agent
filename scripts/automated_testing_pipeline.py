#!/usr/bin/env python3
"""
Automated Testing Pipeline - US-002 Implementation
=================================================

Comprehensive automated testing pipeline that executes all test categories
with quality gates, reporting, and zero manual intervention.

Features:
- Automated test execution on commits
- Parallel test execution for performance
- Quality gates and failure blocking
- Comprehensive reporting and metrics
- Integration with git workflow
- Test environment automation
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class TestResult:
    """Represents the result of a test execution."""
    category: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    execution_time: float
    success_rate: float
    details: List[str]
    exit_code: int

@dataclass
class PipelineResult:
    """Represents the overall pipeline execution result."""
    timestamp: str
    total_execution_time: float
    test_results: List[TestResult]
    overall_success: bool
    quality_gates_passed: bool
    blocking_issues: List[str]
    summary: Dict[str, any]

class AutomatedTestingPipeline:
    """Comprehensive automated testing pipeline."""
    
    def __init__(self):
        """Initialize the testing pipeline."""
        self.project_root = project_root
        self.results_dir = self.project_root / "test_results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Test categories with quality gates
        self.test_categories = {
            "unit": {
                "command": "pytest tests/unit/ -v --tb=short",
                "timeout": 30,
                "quality_gate": 100,  # 100% pass required
                "parallel": True
            },
            "integration": {
                "command": "pytest tests/integration/ -v --tb=short",
                "timeout": 120,
                "quality_gate": 100,  # 100% pass required
                "parallel": True
            },
            "infrastructure": {
                "command": "pytest tests/infrastructure/ -v --tb=short",
                "timeout": 30,
                "quality_gate": 100,  # 100% pass required
                "parallel": True
            },
            "security": {
                "command": "pytest tests/security/ -v --tb=short",
                "timeout": 60,
                "quality_gate": 100,  # 100% pass required
                "parallel": True
            },
            "system": {
                "command": "pytest tests/system/ -v --tb=short",
                "timeout": 180,
                "quality_gate": 100,  # 100% pass required
                "parallel": False  # System tests run sequentially
            },
            "performance": {
                "command": "pytest tests/performance/ -v --tb=short",
                "timeout": 120,
                "quality_gate": 95,  # 95% pass required
                "parallel": True
            },
            "langgraph": {
                "command": "pytest tests/langgraph/ -v --tb=short",
                "timeout": 180,
                "quality_gate": 90,  # 90% pass required
                "parallel": True
            }
        }
        
        # Quality gates configuration
        self.quality_gates = {
            "overall_pass_rate": 95.0,  # 95% overall pass rate required
            "critical_categories": ["unit", "integration", "infrastructure", "security"],
            "max_execution_time": 600,  # 10 minutes max
            "max_failures_per_category": 1  # Max 1 failure per category
        }
        
        print("🧪 Automated Testing Pipeline initialized")
        print(f"📁 Results directory: {self.results_dir}")
        print(f"🎯 Test categories: {len(self.test_categories)}")
    
    def execute_test_category(self, category: str, config: Dict) -> TestResult:
        """Execute tests for a specific category."""
        print(f"\n🔄 Executing {category} tests...")
        start_time = time.time()
        
        try:
            # Use Anaconda Python for consistency
            command = config["command"].replace("pytest", "C:/App/Anaconda/python.exe -m pytest")
            
            # Execute tests
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=config["timeout"],
                cwd=self.project_root
            )
            
            execution_time = time.time() - start_time
            
            # Parse pytest output to extract test counts
            output_lines = result.stdout.split('\n')
            test_counts = self._parse_pytest_output(output_lines)
            
            # Calculate success rate
            total_tests = test_counts["passed"] + test_counts["failed"] + test_counts["skipped"]
            success_rate = (test_counts["passed"] / total_tests * 100) if total_tests > 0 else 0
            
            # Create result object
            test_result = TestResult(
                category=category,
                total_tests=total_tests,
                passed_tests=test_counts["passed"],
                failed_tests=test_counts["failed"],
                skipped_tests=test_counts["skipped"],
                execution_time=execution_time,
                success_rate=success_rate,
                details=output_lines[-20:] if result.returncode != 0 else [],
                exit_code=result.returncode
            )
            
            # Check quality gate
            quality_gate_passed = success_rate >= config["quality_gate"]
            
            if quality_gate_passed:
                print(f"✅ {category}: {test_counts['passed']}/{total_tests} passed ({success_rate:.1f}%) in {execution_time:.1f}s")
            else:
                print(f"❌ {category}: {test_counts['passed']}/{total_tests} passed ({success_rate:.1f}%) - BELOW QUALITY GATE ({config['quality_gate']}%)")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"⏰ {category}: TIMEOUT after {execution_time:.1f}s")
            
            return TestResult(
                category=category,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                execution_time=execution_time,
                success_rate=0.0,
                details=[f"Test execution timed out after {config['timeout']}s"],
                exit_code=1
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"💥 {category}: ERROR - {e}")
            
            return TestResult(
                category=category,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                execution_time=execution_time,
                success_rate=0.0,
                details=[f"Test execution failed: {e}"],
                exit_code=1
            )
    
    def _parse_pytest_output(self, output_lines: List[str]) -> Dict[str, int]:
        """Parse pytest output to extract test counts."""
        counts = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
        
        for line in output_lines:
            line = line.strip()
            
            # Look for summary line like "=== 45 passed, 2 failed, 1 skipped in 2.34s ==="
            if "passed" in line and ("failed" in line or "skipped" in line or "error" in line):
                # Extract numbers
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit() and i + 1 < len(parts):
                        count = int(part)
                        status = parts[i + 1]
                        
                        if "passed" in status:
                            counts["passed"] = count
                        elif "failed" in status:
                            counts["failed"] = count
                        elif "skipped" in status:
                            counts["skipped"] = count
                        elif "error" in status:
                            counts["errors"] = count
                break
            
            # Alternative format: "45 passed in 2.34s"
            elif line.endswith("passed in"):
                parts = line.split()
                if parts[0].isdigit():
                    counts["passed"] = int(parts[0])
                break
        
        return counts
    
    def execute_parallel_tests(self, parallel_categories: List[str]) -> List[TestResult]:
        """Execute tests in parallel for better performance."""
        results = []
        
        print(f"\n🚀 Executing {len(parallel_categories)} test categories in parallel...")
        
        with ThreadPoolExecutor(max_workers=min(4, len(parallel_categories))) as executor:
            # Submit parallel test executions
            future_to_category = {
                executor.submit(self.execute_test_category, category, self.test_categories[category]): category
                for category in parallel_categories
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_category):
                category = future_to_category[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"💥 Parallel execution failed for {category}: {e}")
                    # Create error result
                    error_result = TestResult(
                        category=category,
                        total_tests=0,
                        passed_tests=0,
                        failed_tests=1,
                        skipped_tests=0,
                        execution_time=0.0,
                        success_rate=0.0,
                        details=[f"Parallel execution failed: {e}"],
                        exit_code=1
                    )
                    results.append(error_result)
        
        return results
    
    def execute_sequential_tests(self, sequential_categories: List[str]) -> List[TestResult]:
        """Execute tests sequentially for categories that require it."""
        results = []
        
        print(f"\n🔄 Executing {len(sequential_categories)} test categories sequentially...")
        
        for category in sequential_categories:
            result = self.execute_test_category(category, self.test_categories[category])
            results.append(result)
        
        return results
    
    def check_quality_gates(self, test_results: List[TestResult]) -> Tuple[bool, List[str]]:
        """Check if all quality gates are passed."""
        blocking_issues = []
        
        # Check overall pass rate
        total_tests = sum(r.total_tests for r in test_results)
        total_passed = sum(r.passed_tests for r in test_results)
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        if overall_pass_rate < self.quality_gates["overall_pass_rate"]:
            blocking_issues.append(
                f"Overall pass rate {overall_pass_rate:.1f}% below required {self.quality_gates['overall_pass_rate']}%"
            )
        
        # Check critical categories
        for category in self.quality_gates["critical_categories"]:
            category_result = next((r for r in test_results if r.category == category), None)
            if category_result:
                required_rate = self.test_categories[category]["quality_gate"]
                if category_result.success_rate < required_rate:
                    blocking_issues.append(
                        f"Critical category '{category}' pass rate {category_result.success_rate:.1f}% below required {required_rate}%"
                    )
        
        # Check execution time
        total_execution_time = sum(r.execution_time for r in test_results)
        if total_execution_time > self.quality_gates["max_execution_time"]:
            blocking_issues.append(
                f"Total execution time {total_execution_time:.1f}s exceeds limit {self.quality_gates['max_execution_time']}s"
            )
        
        # Check failures per category
        for result in test_results:
            if result.failed_tests > self.quality_gates["max_failures_per_category"]:
                blocking_issues.append(
                    f"Category '{result.category}' has {result.failed_tests} failures, exceeds limit {self.quality_gates['max_failures_per_category']}"
                )
        
        quality_gates_passed = len(blocking_issues) == 0
        return quality_gates_passed, blocking_issues
    
    def generate_report(self, pipeline_result: PipelineResult) -> str:
        """Generate comprehensive test report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"test_report_{timestamp}.json"
        
        # Save detailed JSON report
        with open(report_file, 'w') as f:
            json.dump(asdict(pipeline_result), f, indent=2)
        
        # Generate summary report
        summary_report = f"""
# Automated Testing Pipeline Report
**Timestamp**: {pipeline_result.timestamp}
**Execution Time**: {pipeline_result.total_execution_time:.1f} seconds
**Overall Success**: {'✅ PASSED' if pipeline_result.overall_success else '❌ FAILED'}
**Quality Gates**: {'✅ PASSED' if pipeline_result.quality_gates_passed else '❌ FAILED'}

## Test Results Summary
"""
        
        for result in pipeline_result.test_results:
            status = "✅ PASS" if result.exit_code == 0 else "❌ FAIL"
            summary_report += f"""
### {result.category.title()} Tests {status}
- **Total Tests**: {result.total_tests}
- **Passed**: {result.passed_tests}
- **Failed**: {result.failed_tests}
- **Skipped**: {result.skipped_tests}
- **Success Rate**: {result.success_rate:.1f}%
- **Execution Time**: {result.execution_time:.1f}s
"""
        
        if pipeline_result.blocking_issues:
            summary_report += f"""
## 🚫 Blocking Issues
"""
            for issue in pipeline_result.blocking_issues:
                summary_report += f"- {issue}\n"
        
        summary_report += f"""
## 📊 Pipeline Summary
- **Total Tests**: {pipeline_result.summary['total_tests']}
- **Total Passed**: {pipeline_result.summary['total_passed']}
- **Overall Pass Rate**: {pipeline_result.summary['overall_pass_rate']:.1f}%
- **Categories Executed**: {len(pipeline_result.test_results)}

**Report File**: {report_file}
"""
        
        print(summary_report)
        return str(report_file)
    
    def save_results_to_database(self, pipeline_result: PipelineResult):
        """Save pipeline results to tracking database."""
        try:
            db_path = self.project_root / "utils" / "test_pipeline_results.db"
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Create table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pipeline_executions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        total_execution_time REAL,
                        overall_success BOOLEAN,
                        quality_gates_passed BOOLEAN,
                        total_tests INTEGER,
                        total_passed INTEGER,
                        overall_pass_rate REAL,
                        blocking_issues TEXT,
                        details TEXT
                    )
                """)
                
                # Insert pipeline result
                cursor.execute("""
                    INSERT INTO pipeline_executions 
                    (timestamp, total_execution_time, overall_success, quality_gates_passed,
                     total_tests, total_passed, overall_pass_rate, blocking_issues, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pipeline_result.timestamp,
                    pipeline_result.total_execution_time,
                    pipeline_result.overall_success,
                    pipeline_result.quality_gates_passed,
                    pipeline_result.summary['total_tests'],
                    pipeline_result.summary['total_passed'],
                    pipeline_result.summary['overall_pass_rate'],
                    json.dumps(pipeline_result.blocking_issues),
                    json.dumps(asdict(pipeline_result))
                ))
                
                conn.commit()
                print(f"✅ Results saved to database: {db_path}")
                
        except Exception as e:
            print(f"⚠️ Failed to save to database: {e}")
    
    def run_full_pipeline(self) -> PipelineResult:
        """Execute the complete automated testing pipeline."""
        print("🚀 Starting Automated Testing Pipeline")
        print("=" * 60)
        
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        # Separate parallel and sequential categories
        parallel_categories = [cat for cat, config in self.test_categories.items() if config["parallel"]]
        sequential_categories = [cat for cat, config in self.test_categories.items() if not config["parallel"]]
        
        all_results = []
        
        # Execute parallel tests
        if parallel_categories:
            parallel_results = self.execute_parallel_tests(parallel_categories)
            all_results.extend(parallel_results)
        
        # Execute sequential tests
        if sequential_categories:
            sequential_results = self.execute_sequential_tests(sequential_categories)
            all_results.extend(sequential_results)
        
        total_execution_time = time.time() - start_time
        
        # Check quality gates
        quality_gates_passed, blocking_issues = self.check_quality_gates(all_results)
        
        # Calculate overall success
        all_tests_passed = all(r.exit_code == 0 for r in all_results)
        overall_success = all_tests_passed and quality_gates_passed
        
        # Generate summary
        total_tests = sum(r.total_tests for r in all_results)
        total_passed = sum(r.passed_tests for r in all_results)
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": sum(r.failed_tests for r in all_results),
            "total_skipped": sum(r.skipped_tests for r in all_results),
            "overall_pass_rate": overall_pass_rate,
            "categories_executed": len(all_results)
        }
        
        # Create pipeline result
        pipeline_result = PipelineResult(
            timestamp=timestamp,
            total_execution_time=total_execution_time,
            test_results=all_results,
            overall_success=overall_success,
            quality_gates_passed=quality_gates_passed,
            blocking_issues=blocking_issues,
            summary=summary
        )
        
        # Generate reports and save results
        report_file = self.generate_report(pipeline_result)
        self.save_results_to_database(pipeline_result)
        
        # Final status
        print("\n" + "=" * 60)
        if overall_success:
            print("🎉 PIPELINE SUCCESS: All tests passed and quality gates met!")
        else:
            print("💥 PIPELINE FAILURE: Quality gates not met or tests failed!")
            print(f"🚫 Blocking issues: {len(blocking_issues)}")
        
        print(f"📊 Total: {total_passed}/{total_tests} tests passed ({overall_pass_rate:.1f}%)")
        print(f"⏱️ Execution time: {total_execution_time:.1f} seconds")
        print(f"📄 Report: {report_file}")
        
        return pipeline_result

def main():
    """Main entry point for the automated testing pipeline."""
    
    # Command line argument handling
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    pipeline = AutomatedTestingPipeline()
    
    if mode == "full":
        # Full pipeline execution
        result = pipeline.run_full_pipeline()
        sys.exit(0 if result.overall_success else 1)
        
    elif mode == "quick":
        # Quick validation (unit + integration only)
        print("🏃‍♂️ Running quick validation pipeline...")
        pipeline.test_categories = {
            k: v for k, v in pipeline.test_categories.items() 
            if k in ["unit", "integration"]
        }
        result = pipeline.run_full_pipeline()
        sys.exit(0 if result.overall_success else 1)
        
    elif mode == "pre-commit":
        # Pre-commit validation (fast tests only)
        print("🔍 Running pre-commit validation...")
        pipeline.test_categories = {
            k: v for k, v in pipeline.test_categories.items() 
            if k in ["unit"] and v["timeout"] <= 30
        }
        result = pipeline.run_full_pipeline()
        sys.exit(0 if result.overall_success else 1)
        
    else:
        print(f"❌ Unknown mode: {mode}")
        print("Available modes: full, quick, pre-commit")
        sys.exit(1)

if __name__ == "__main__":
    main()
