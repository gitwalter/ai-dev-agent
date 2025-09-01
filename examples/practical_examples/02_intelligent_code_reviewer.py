#!/usr/bin/env python3
"""
Practical Example 2: Intelligent Code Reviewer  
==============================================

WHAT THIS DOES:
- Automatically reviews code for issues, security, performance
- Shows how to use AI-Dev-Agent for quality assurance automation
- Provides actionable suggestions and fixes

TIME TO VALUE: 1 minute
LEARNING FOCUS: Code analysis, security scanning, best practices

REAL-WORLD USE CASE:
"I need to review existing code for quality, security, and performance issues"
"""

import sys
import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

class IssueSeverity(Enum):
    """Severity levels for code issues."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM" 
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class CodeIssue:
    """Represents a code quality issue."""
    severity: IssueSeverity
    category: str
    description: str
    line_number: int
    column: int
    code_snippet: str
    fix_suggestion: str
    rule_id: str
    confidence: float  # 0.0 to 1.0

@dataclass
class SecurityIssue:
    """Represents a security vulnerability."""
    severity: IssueSeverity
    vulnerability_type: str
    description: str
    line_number: int
    cwe_id: Optional[str]
    fix_suggestion: str
    risk_level: str

@dataclass
class PerformanceIssue:
    """Represents a performance concern."""
    severity: IssueSeverity
    issue_type: str
    description: str
    line_number: int
    impact: str
    fix_suggestion: str
    estimated_improvement: str

@dataclass
class ReviewResult:
    """Complete code review result."""
    file_path: str
    overall_score: int  # 0-100
    issues: List[CodeIssue]
    security_issues: List[SecurityIssue]
    performance_issues: List[PerformanceIssue]
    metrics: Dict[str, Any]
    suggestions: List[str]
    review_time: float
    timestamp: str

class IntelligentCodeReviewer:
    """
    Intelligent code reviewer that analyzes code for quality, security, and performance.
    
    This example demonstrates:
    - Static code analysis
    - Security vulnerability detection
    - Performance bottleneck identification
    - Best practice validation
    - Automated fix suggestions
    """
    
    def __init__(self):
        """Initialize the intelligent code reviewer."""
        self.security_patterns = self._load_security_patterns()
        self.performance_patterns = self._load_performance_patterns()
        self.quality_rules = self._load_quality_rules()
        
    def review_file(self, file_path: str) -> ReviewResult:
        """
        Perform comprehensive code review on a single file.
        
        Args:
            file_path: Path to the Python file to review
            
        Returns:
            Comprehensive review result with issues and suggestions
        """
        
        start_time = datetime.now()
        print(f"🔍 Reviewing file: {file_path}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return self._create_error_result(file_path, str(e))
        
        # Parse AST for analysis
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"❌ Syntax error in file: {e}")
            return self._create_syntax_error_result(file_path, str(e))
        
        # Perform analysis
        lines = content.split('\n')
        
        print("  📊 Analyzing code quality...")
        quality_issues = self._analyze_code_quality(content, tree, lines)
        
        print("  🔒 Scanning for security issues...")
        security_issues = self._analyze_security(content, tree, lines)
        
        print("  ⚡ Checking performance...")
        performance_issues = self._analyze_performance(content, tree, lines)
        
        print("  📈 Calculating metrics...")
        metrics = self._calculate_metrics(content, tree)
        
        print("  💡 Generating suggestions...")
        suggestions = self._generate_suggestions(quality_issues, security_issues, performance_issues)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            quality_issues, security_issues, performance_issues, metrics
        )
        
        end_time = datetime.now()
        review_time = (end_time - start_time).total_seconds()
        
        result = ReviewResult(
            file_path=file_path,
            overall_score=overall_score,
            issues=quality_issues,
            security_issues=security_issues,
            performance_issues=performance_issues,
            metrics=metrics,
            suggestions=suggestions,
            review_time=review_time,
            timestamp=end_time.isoformat()
        )
        
        self._display_review_results(result)
        return result
    
    def review_directory(self, directory_path: str) -> List[ReviewResult]:
        """
        Review all Python files in a directory.
        
        Args:
            directory_path: Path to directory containing Python files
            
        Returns:
            List of review results for all files
        """
        
        print(f"📁 Reviewing directory: {directory_path}")
        
        directory = Path(directory_path)
        python_files = list(directory.rglob("*.py"))
        
        if not python_files:
            print("❌ No Python files found in directory")
            return []
        
        print(f"Found {len(python_files)} Python files to review")
        
        results = []
        for file_path in python_files:
            result = self.review_file(str(file_path))
            results.append(result)
            print()  # Add spacing between files
        
        # Generate directory summary
        self._display_directory_summary(results)
        
        return results
    
    def _load_security_patterns(self) -> Dict[str, Any]:
        """Load security vulnerability patterns."""
        return {
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ],
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'cursor\.execute\s*\(\s*f["\']',
                r'query\s*=\s*["\'].*\+.*["\']'
            ],
            'command_injection': [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'subprocess\.run\s*\([^,\)]*shell\s*=\s*True'
            ],
            'path_traversal': [
                r'open\s*\(\s*.*\+',
                r'file\s*=\s*.*\+.*\.\.'
            ]
        }
    
    def _load_performance_patterns(self) -> Dict[str, Any]:
        """Load performance anti-patterns."""
        return {
            'inefficient_loops': [
                r'for.*in.*range\(len\(',
                r'while.*len\('
            ],
            'inefficient_data_structures': [
                r'list\(\).*append.*for',
                r'\[\].*append.*for'
            ],
            'blocking_operations': [
                r'time\.sleep\(',
                r'requests\.get\(',
                r'urllib\.request'
            ]
        }
    
    def _load_quality_rules(self) -> Dict[str, Any]:
        """Load code quality rules."""
        return {
            'naming_conventions': {
                'class_names': r'^[A-Z][a-zA-Z0-9]*$',
                'function_names': r'^[a-z_][a-z0-9_]*$',
                'constant_names': r'^[A-Z_][A-Z0-9_]*$'
            },
            'complexity_limits': {
                'max_function_length': 50,
                'max_class_methods': 20,
                'max_parameters': 5
            },
            'documentation': {
                'function_docstring': True,
                'class_docstring': True,
                'module_docstring': True
            }
        }
    
    def _analyze_code_quality(self, content: str, tree: ast.AST, lines: List[str]) -> List[CodeIssue]:
        """Analyze code quality issues."""
        issues = []
        
        # Check naming conventions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not re.match(self.quality_rules['naming_conventions']['class_names'], node.name):
                    issues.append(CodeIssue(
                        severity=IssueSeverity.MEDIUM,
                        category="Naming Convention",
                        description=f"Class name '{node.name}' should follow PascalCase convention",
                        line_number=node.lineno,
                        column=node.col_offset,
                        code_snippet=lines[node.lineno-1] if node.lineno <= len(lines) else "",
                        fix_suggestion=f"Rename to '{self._to_pascal_case(node.name)}'",
                        rule_id="naming-class",
                        confidence=0.9
                    ))
            
            elif isinstance(node, ast.FunctionDef):
                # Check function naming
                if not re.match(self.quality_rules['naming_conventions']['function_names'], node.name):
                    issues.append(CodeIssue(
                        severity=IssueSeverity.MEDIUM,
                        category="Naming Convention",
                        description=f"Function name '{node.name}' should follow snake_case convention",
                        line_number=node.lineno,
                        column=node.col_offset,
                        code_snippet=lines[node.lineno-1] if node.lineno <= len(lines) else "",
                        fix_suggestion=f"Rename to '{self._to_snake_case(node.name)}'",
                        rule_id="naming-function",
                        confidence=0.9
                    ))
                
                # Check function length
                if hasattr(node, 'end_lineno'):
                    function_length = node.end_lineno - node.lineno
                    if function_length > self.quality_rules['complexity_limits']['max_function_length']:
                        issues.append(CodeIssue(
                            severity=IssueSeverity.HIGH,
                            category="Complexity",
                            description=f"Function '{node.name}' is too long ({function_length} lines)",
                            line_number=node.lineno,
                            column=node.col_offset,
                            code_snippet=lines[node.lineno-1] if node.lineno <= len(lines) else "",
                            fix_suggestion="Break into smaller functions with single responsibilities",
                            rule_id="complexity-function-length",
                            confidence=0.95
                        ))
                
                # Check parameter count
                param_count = len(node.args.args)
                if param_count > self.quality_rules['complexity_limits']['max_parameters']:
                    issues.append(CodeIssue(
                        severity=IssueSeverity.MEDIUM,
                        category="Complexity",
                        description=f"Function '{node.name}' has too many parameters ({param_count})",
                        line_number=node.lineno,
                        column=node.col_offset,
                        code_snippet=lines[node.lineno-1] if node.lineno <= len(lines) else "",
                        fix_suggestion="Use a data class or dictionary to group related parameters",
                        rule_id="complexity-parameter-count",
                        confidence=0.8
                    ))
                
                # Check for missing docstring
                if not ast.get_docstring(node):
                    issues.append(CodeIssue(
                        severity=IssueSeverity.LOW,
                        category="Documentation",
                        description=f"Function '{node.name}' is missing a docstring",
                        line_number=node.lineno,
                        column=node.col_offset,
                        code_snippet=lines[node.lineno-1] if node.lineno <= len(lines) else "",
                        fix_suggestion="Add a docstring describing purpose, parameters, and return value",
                        rule_id="documentation-function-docstring",
                        confidence=0.7
                    ))
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(CodeIssue(
                    severity=IssueSeverity.LOW,
                    category="Style",
                    description=f"Line too long ({len(line)} characters)",
                    line_number=i,
                    column=120,
                    code_snippet=line,
                    fix_suggestion="Break line or refactor to reduce length",
                    rule_id="style-line-length",
                    confidence=1.0
                ))
        
        return issues
    
    def _analyze_security(self, content: str, tree: ast.AST, lines: List[str]) -> List[SecurityIssue]:
        """Analyze security vulnerabilities."""
        security_issues = []
        
        # Check for hardcoded secrets
        for pattern in self.security_patterns['hardcoded_secrets']:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    security_issues.append(SecurityIssue(
                        severity=IssueSeverity.CRITICAL,
                        vulnerability_type="Hardcoded Secret",
                        description="Potential hardcoded password/secret found",
                        line_number=i,
                        cwe_id="CWE-798",
                        fix_suggestion="Use environment variables or secure configuration management",
                        risk_level="HIGH"
                    ))
        
        # Check for SQL injection patterns
        for pattern in self.security_patterns['sql_injection']:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    security_issues.append(SecurityIssue(
                        severity=IssueSeverity.HIGH,
                        vulnerability_type="SQL Injection",
                        description="Potential SQL injection vulnerability",
                        line_number=i,
                        cwe_id="CWE-89",
                        fix_suggestion="Use parameterized queries or ORM methods",
                        risk_level="HIGH"
                    ))
        
        # Check for command injection
        for pattern in self.security_patterns['command_injection']:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    security_issues.append(SecurityIssue(
                        severity=IssueSeverity.HIGH,
                        vulnerability_type="Command Injection",
                        description="Potential command injection vulnerability",
                        line_number=i,
                        cwe_id="CWE-78",
                        fix_suggestion="Validate input and use subprocess with shell=False",
                        risk_level="HIGH"
                    ))
        
        # Check for path traversal
        for pattern in self.security_patterns['path_traversal']:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    security_issues.append(SecurityIssue(
                        severity=IssueSeverity.MEDIUM,
                        vulnerability_type="Path Traversal",
                        description="Potential path traversal vulnerability",
                        line_number=i,
                        cwe_id="CWE-22",
                        fix_suggestion="Validate and sanitize file paths",
                        risk_level="MEDIUM"
                    ))
        
        return security_issues
    
    def _analyze_performance(self, content: str, tree: ast.AST, lines: List[str]) -> List[PerformanceIssue]:
        """Analyze performance issues."""
        performance_issues = []
        
        # Check for inefficient loops
        for pattern in self.performance_patterns['inefficient_loops']:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    performance_issues.append(PerformanceIssue(
                        severity=IssueSeverity.MEDIUM,
                        issue_type="Inefficient Loop",
                        description="Inefficient iteration pattern detected",
                        line_number=i,
                        impact="O(n) instead of direct iteration",
                        fix_suggestion="Use direct iteration: 'for item in items:' instead of 'for i in range(len(items)):'",
                        estimated_improvement="20-50% faster iteration"
                    ))
        
        # Check for inefficient data structure usage
        for pattern in self.performance_patterns['inefficient_data_structures']:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    performance_issues.append(PerformanceIssue(
                        severity=IssueSeverity.MEDIUM,
                        issue_type="Inefficient Data Structure",
                        description="Inefficient list building pattern",
                        line_number=i,
                        impact="Multiple memory allocations",
                        fix_suggestion="Use list comprehension or generator expression",
                        estimated_improvement="30-80% faster execution"
                    ))
        
        # Check for blocking operations
        for pattern in self.performance_patterns['blocking_operations']:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    performance_issues.append(PerformanceIssue(
                        severity=IssueSeverity.LOW,
                        issue_type="Blocking Operation",
                        description="Blocking operation that could impact performance",
                        line_number=i,
                        impact="Thread blocking, reduced concurrency",
                        fix_suggestion="Consider using async/await or threading for I/O operations",
                        estimated_improvement="Significant improvement in concurrent scenarios"
                    ))
        
        return performance_issues
    
    def _calculate_metrics(self, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Calculate code metrics."""
        lines = content.split('\n')
        
        # Basic metrics
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        # Function and class counts
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        
        # Complexity metrics (simplified)
        complexity_score = self._calculate_complexity(tree)
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'comment_ratio': comment_lines / total_lines if total_lines > 0 else 0,
            'function_count': function_count,
            'class_count': class_count,
            'complexity_score': complexity_score,
            'avg_function_length': code_lines / function_count if function_count > 0 else 0
        }
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity (simplified)."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _generate_suggestions(self, quality_issues: List[CodeIssue], 
                            security_issues: List[SecurityIssue],
                            performance_issues: List[PerformanceIssue]) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        # Priority suggestions based on critical issues
        critical_count = len([i for i in security_issues if i.severity == IssueSeverity.CRITICAL])
        if critical_count > 0:
            suggestions.append(f"🚨 URGENT: Fix {critical_count} critical security issue(s) immediately")
        
        high_security_count = len([i for i in security_issues if i.severity == IssueSeverity.HIGH])
        if high_security_count > 0:
            suggestions.append(f"🔒 HIGH PRIORITY: Address {high_security_count} high-severity security issue(s)")
        
        # Quality suggestions
        naming_issues = len([i for i in quality_issues if i.category == "Naming Convention"])
        if naming_issues > 0:
            suggestions.append(f"📝 Improve code readability by fixing {naming_issues} naming convention issue(s)")
        
        complexity_issues = len([i for i in quality_issues if i.category == "Complexity"])
        if complexity_issues > 0:
            suggestions.append(f"🔧 Reduce code complexity by refactoring {complexity_issues} complex function(s)")
        
        # Performance suggestions
        if performance_issues:
            suggestions.append(f"⚡ Optimize performance by addressing {len(performance_issues)} performance issue(s)")
        
        # Documentation suggestions
        doc_issues = len([i for i in quality_issues if i.category == "Documentation"])
        if doc_issues > 0:
            suggestions.append(f"📚 Improve maintainability by adding {doc_issues} missing docstring(s)")
        
        return suggestions
    
    def _calculate_overall_score(self, quality_issues: List[CodeIssue],
                               security_issues: List[SecurityIssue],
                               performance_issues: List[PerformanceIssue],
                               metrics: Dict[str, Any]) -> int:
        """Calculate overall code quality score (0-100)."""
        
        score = 100
        
        # Deduct points for security issues
        for issue in security_issues:
            if issue.severity == IssueSeverity.CRITICAL:
                score -= 20
            elif issue.severity == IssueSeverity.HIGH:
                score -= 10
            elif issue.severity == IssueSeverity.MEDIUM:
                score -= 5
        
        # Deduct points for quality issues
        for issue in quality_issues:
            if issue.severity == IssueSeverity.HIGH:
                score -= 5
            elif issue.severity == IssueSeverity.MEDIUM:
                score -= 3
            elif issue.severity == IssueSeverity.LOW:
                score -= 1
        
        # Deduct points for performance issues
        for issue in performance_issues:
            if issue.severity == IssueSeverity.HIGH:
                score -= 5
            elif issue.severity == IssueSeverity.MEDIUM:
                score -= 3
            elif issue.severity == IssueSeverity.LOW:
                score -= 1
        
        # Bonus points for good practices
        if metrics['comment_ratio'] > 0.1:  # Good comment ratio
            score += 5
        
        return max(0, min(100, score))
    
    def _display_review_results(self, result: ReviewResult) -> None:
        """Display comprehensive review results."""
        
        print(f"\n{'='*80}")
        print(f"📋 CODE REVIEW RESULTS: {Path(result.file_path).name}")
        print(f"{'='*80}")
        
        # Overall score with color coding
        score_emoji = "🟢" if result.overall_score >= 80 else "🟡" if result.overall_score >= 60 else "🔴"
        print(f"\n{score_emoji} Overall Score: {result.overall_score}/100")
        
        # Issue summary
        total_issues = len(result.issues) + len(result.security_issues) + len(result.performance_issues)
        print(f"📊 Total Issues Found: {total_issues}")
        
        if result.security_issues:
            critical_security = len([i for i in result.security_issues if i.severity == IssueSeverity.CRITICAL])
            high_security = len([i for i in result.security_issues if i.severity == IssueSeverity.HIGH])
            print(f"🔒 Security Issues: {len(result.security_issues)} (🚨 {critical_security} critical, ⚠️ {high_security} high)")
        
        if result.performance_issues:
            print(f"⚡ Performance Issues: {len(result.performance_issues)}")
        
        if result.issues:
            print(f"📝 Quality Issues: {len(result.issues)}")
        
        # Key metrics
        print(f"\n📈 Key Metrics:")
        print(f"  Lines of Code: {result.metrics['code_lines']}")
        print(f"  Functions: {result.metrics['function_count']}")
        print(f"  Classes: {result.metrics['class_count']}")
        print(f"  Comment Ratio: {result.metrics['comment_ratio']:.1%}")
        print(f"  Complexity Score: {result.metrics['complexity_score']}")
        
        # Top issues (first 3 most severe)
        all_issues = []
        for issue in result.security_issues:
            all_issues.append((issue.severity, "SECURITY", issue.description, issue.line_number))
        for issue in result.issues:
            all_issues.append((issue.severity, "QUALITY", issue.description, issue.line_number))
        for issue in result.performance_issues:
            all_issues.append((issue.severity, "PERFORMANCE", issue.description, issue.line_number))
        
        # Sort by severity (Critical, High, Medium, Low, Info)
        severity_order = {IssueSeverity.CRITICAL: 0, IssueSeverity.HIGH: 1, 
                         IssueSeverity.MEDIUM: 2, IssueSeverity.LOW: 3, IssueSeverity.INFO: 4}
        all_issues.sort(key=lambda x: severity_order[x[0]])
        
        if all_issues:
            print(f"\n🎯 Top Issues to Address:")
            for i, (severity, category, description, line_no) in enumerate(all_issues[:5], 1):
                severity_emoji = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "📋", "LOW": "💡", "INFO": "ℹ️"}
                emoji = severity_emoji.get(severity.value, "📋")
                print(f"  {i}. {emoji} Line {line_no}: {description} [{category}]")
        
        # Suggestions
        if result.suggestions:
            print(f"\n💡 Recommendations:")
            for i, suggestion in enumerate(result.suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        print(f"\n⏱️ Review completed in {result.review_time:.2f} seconds")
        print(f"{'='*80}")
    
    def _display_directory_summary(self, results: List[ReviewResult]) -> None:
        """Display summary for directory review."""
        
        if not results:
            return
        
        print(f"\n{'='*80}")
        print(f"📁 DIRECTORY REVIEW SUMMARY")
        print(f"{'='*80}")
        
        total_files = len(results)
        avg_score = sum(r.overall_score for r in results) / total_files
        total_issues = sum(len(r.issues) + len(r.security_issues) + len(r.performance_issues) for r in results)
        
        print(f"📊 Files Reviewed: {total_files}")
        print(f"📈 Average Score: {avg_score:.1f}/100")
        print(f"🔍 Total Issues: {total_issues}")
        
        # Security summary
        critical_security = sum(len([i for i in r.security_issues if i.severity == IssueSeverity.CRITICAL]) for r in results)
        high_security = sum(len([i for i in r.security_issues if i.severity == IssueSeverity.HIGH]) for r in results)
        
        if critical_security > 0 or high_security > 0:
            print(f"🚨 URGENT: {critical_security} critical and {high_security} high-severity security issues found!")
        
        # Best and worst files
        best_file = max(results, key=lambda r: r.overall_score)
        worst_file = min(results, key=lambda r: r.overall_score)
        
        print(f"\n🏆 Best File: {Path(best_file.file_path).name} ({best_file.overall_score}/100)")
        print(f"🎯 Needs Attention: {Path(worst_file.file_path).name} ({worst_file.overall_score}/100)")
        
        print(f"{'='*80}")
    
    def _create_error_result(self, file_path: str, error: str) -> ReviewResult:
        """Create error result for files that couldn't be read."""
        return ReviewResult(
            file_path=file_path,
            overall_score=0,
            issues=[],
            security_issues=[],
            performance_issues=[],
            metrics={},
            suggestions=[f"❌ File could not be analyzed: {error}"],
            review_time=0.0,
            timestamp=datetime.now().isoformat()
        )
    
    def _create_syntax_error_result(self, file_path: str, error: str) -> ReviewResult:
        """Create result for files with syntax errors."""
        return ReviewResult(
            file_path=file_path,
            overall_score=0,
            issues=[],
            security_issues=[],
            performance_issues=[],
            metrics={},
            suggestions=[f"🔧 Fix syntax error first: {error}"],
            review_time=0.0,
            timestamp=datetime.now().isoformat()
        )
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        # Insert underscore before uppercase letters
        result = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        return result

def main():
    """Main function demonstrating intelligent code review."""
    
    print("🤖 AI-Dev-Agent Intelligent Code Reviewer")
    print("=" * 60)
    print("Analyzing code for quality, security, and performance...")
    print()
    
    # Initialize reviewer
    reviewer = IntelligentCodeReviewer()
    
    # Example 1: Review this file itself
    print("📍 Example 1: Self-Review")
    current_file = __file__
    result1 = reviewer.review_file(current_file)
    
    print("\n" + "-"*60 + "\n")
    
    # Example 2: Review the smart code generator
    print("📍 Example 2: Review Smart Code Generator")
    generator_file = Path(__file__).parent / "01_smart_code_generator.py"
    if generator_file.exists():
        result2 = reviewer.review_file(str(generator_file))
    else:
        print("❌ Smart code generator file not found")
        result2 = None
    
    # Example 3: Review entire examples directory (if requested)
    examples_dir = Path(__file__).parent.parent
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        print("\n" + "-"*60 + "\n")
        print("📍 Example 3: Full Directory Review")
        directory_results = reviewer.review_directory(str(examples_dir))
    
    # Summary
    print(f"\n{'='*80}")
    print("🎯 REVIEW SESSION SUMMARY")
    print(f"{'='*80}")
    
    files_reviewed = 1 + (1 if result2 else 0)
    avg_score = result1.overall_score
    if result2:
        avg_score = (result1.overall_score + result2.overall_score) / 2
    
    print(f"Files Reviewed: {files_reviewed}")
    print(f"Average Quality Score: {avg_score:.1f}/100")
    
    # Action items
    action_items = []
    if result1.security_issues:
        action_items.append(f"Fix {len(result1.security_issues)} security issue(s) in reviewer")
    if result2 and result2.security_issues:
        action_items.append(f"Fix {len(result2.security_issues)} security issue(s) in generator")
    
    if action_items:
        print(f"\n🎯 Priority Action Items:")
        for i, item in enumerate(action_items, 1):
            print(f"  {i}. {item}")
    else:
        print(f"\n✅ No critical issues found!")
    
    print(f"\n🚀 Code quality review complete!")

if __name__ == "__main__":
    main()
