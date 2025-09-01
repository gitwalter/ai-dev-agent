#!/usr/bin/env python3
"""
GEM 1: Smart Code Reviewer with Ontological Perspective Switching
=================================================================

REAL VALUE: Automatically reviews code with different perspectives:
- @engineering: Checks functionality, tests, performance
- @architecture: Checks design patterns, maintainability  
- @security: Checks vulnerabilities, best practices

IMMEDIATE USE: Drop this into any project for instant intelligent code review.

Usage:
    python gem_1_smart_code_reviewer.py path/to/code.py
    python gem_1_smart_code_reviewer.py --directory src/
    python gem_1_smart_code_reviewer.py --ci-mode  # For CI pipelines
"""

import sys
import os
import argparse
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add utils to path for ontological framework
utils_path = Path(__file__).parent.parent / "utils"
sys.path.append(str(utils_path))

from context.ontological_framework_system import OntologicalSwitchingSystem


class IssueLevel(Enum):
    """Issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CodeIssue:
    """Represents a code issue found during review."""
    file_path: str
    line_number: int
    issue_type: str
    severity: IssueLevel
    message: str
    suggestion: str
    perspective: str  # Which ontological framework found this


class SmartCodeReviewer:
    """
    Intelligent code reviewer using ontological perspective switching.
    
    Each perspective provides different insights:
    - Engineering: Functionality, testing, performance
    - Architecture: Design patterns, structure, maintainability
    - Security: Vulnerabilities, secure coding practices
    """
    
    def __init__(self):
        self.ontology_system = OntologicalSwitchingSystem()
        self.issues_found = []
        self.review_stats = {
            "files_reviewed": 0,
            "total_issues": 0,
            "critical_issues": 0,
            "perspectives_used": []
        }
    
    def review_file(self, file_path: str) -> List[CodeIssue]:
        """
        Review a single file from multiple ontological perspectives.
        Returns list of issues found.
        """
        
        if not os.path.exists(file_path):
            return [CodeIssue(
                file_path=file_path,
                line_number=0,
                issue_type="file_not_found",
                severity=IssueLevel.ERROR,
                message="File not found",
                suggestion="Check file path",
                perspective="system"
            )]
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_issues = []
        
        # Review from engineering perspective
        engineering_issues = self._review_from_engineering_perspective(file_path, content)
        all_issues.extend(engineering_issues)
        
        # Review from architecture perspective  
        architecture_issues = self._review_from_architecture_perspective(file_path, content)
        all_issues.extend(architecture_issues)
        
        # Review from security perspective
        security_issues = self._review_from_security_perspective(file_path, content)
        all_issues.extend(security_issues)
        
        self.issues_found.extend(all_issues)
        self.review_stats["files_reviewed"] += 1
        self.review_stats["total_issues"] += len(all_issues)
        
        return all_issues
    
    def _review_from_engineering_perspective(self, file_path: str, content: str) -> List[CodeIssue]:
        """Review code from engineering perspective: functionality, tests, performance."""
        
        print("🔧 Reviewing from engineering perspective...")
        self.ontology_system.switch_perspective("engineering", f"Review {file_path} for implementation quality")
        
        issues = []
        lines = content.split('\n')
        
        # Check for missing tests
        if 'test_' not in content and 'def test' not in content:
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=1,
                issue_type="missing_tests",
                severity=IssueLevel.WARNING,
                message="No test functions found in file",
                suggestion="Add unit tests to verify functionality",
                perspective="engineering"
            ))
        
        # Check for TODO comments (engineering debt)
        for i, line in enumerate(lines, 1):
            if 'TODO' in line or 'FIXME' in line or 'HACK' in line:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="technical_debt",
                    severity=IssueLevel.INFO,
                    message=f"Technical debt marker found: {line.strip()}",
                    suggestion="Address technical debt before production",
                    perspective="engineering"
                ))
        
        # Check for long functions (performance/maintainability)
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno + 1
                    if func_lines > 50:
                        issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=node.lineno,
                            issue_type="long_function",
                            severity=IssueLevel.WARNING,
                            message=f"Function '{node.name}' is {func_lines} lines long",
                            suggestion="Consider breaking down into smaller functions",
                            perspective="engineering"
                        ))
        except SyntaxError:
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=1,
                issue_type="syntax_error",
                severity=IssueLevel.ERROR,
                message="File contains syntax errors",
                suggestion="Fix syntax errors before review",
                perspective="engineering"
            ))
        
        # Check for missing error handling
        if 'try:' not in content and 'except' not in content:
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=1,
                issue_type="missing_error_handling",
                severity=IssueLevel.INFO,
                message="No exception handling found",
                suggestion="Consider adding try/except blocks for robust error handling",
                perspective="engineering"
            ))
        
        return issues
    
    def _review_from_architecture_perspective(self, file_path: str, content: str) -> List[CodeIssue]:
        """Review code from architecture perspective: design patterns, structure."""
        
        print("📐 Reviewing from architecture perspective...")
        self.ontology_system.switch_perspective("architecture", f"Review {file_path} for design quality")
        
        issues = []
        lines = content.split('\n')
        
        # Check for god classes (too many methods)
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    method_count = sum(1 for child in node.body if isinstance(child, ast.FunctionDef))
                    if method_count > 20:
                        issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=node.lineno,
                            issue_type="god_class",
                            severity=IssueLevel.WARNING,
                            message=f"Class '{node.name}' has {method_count} methods",
                            suggestion="Consider splitting into smaller, focused classes",
                            perspective="architecture"
                        ))
        except SyntaxError:
            pass  # Already reported in engineering perspective
        
        # Check for magic numbers
        for i, line in enumerate(lines, 1):
            # Look for numeric literals that aren't 0, 1, or -1
            magic_numbers = re.findall(r'\b(?<![\w.])[2-9]\d+(?![\w.])\b', line)
            if magic_numbers:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="magic_number",
                    severity=IssueLevel.INFO,
                    message=f"Magic numbers found: {magic_numbers}",
                    suggestion="Consider using named constants for better readability",
                    perspective="architecture"
                ))
        
        # Check for missing docstrings
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=node.lineno,
                            issue_type="missing_docstring",
                            severity=IssueLevel.INFO,
                            message=f"{type(node).__name__} '{node.name}' missing docstring",
                            suggestion="Add docstring to document purpose and usage",
                            perspective="architecture"
                        ))
        except SyntaxError:
            pass
        
        # Check for deep nesting
        for i, line in enumerate(lines, 1):
            indent_level = (len(line) - len(line.lstrip())) // 4
            if indent_level > 6:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="deep_nesting",
                    severity=IssueLevel.WARNING,
                    message=f"Deep nesting detected (level {indent_level})",
                    suggestion="Consider extracting nested logic into separate functions",
                    perspective="architecture"
                ))
        
        return issues
    
    def _review_from_security_perspective(self, file_path: str, content: str) -> List[CodeIssue]:
        """Review code from security perspective: vulnerabilities, secure practices."""
        
        print("🔒 Reviewing from security perspective...")
        # Note: We don't have a security framework in our system yet, so we'll simulate
        
        issues = []
        lines = content.split('\n')
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type="hardcoded_secret",
                        severity=IssueLevel.CRITICAL,
                        message="Potential hardcoded secret found",
                        suggestion="Use environment variables or secure configuration",
                        perspective="security"
                    ))
        
        # Check for SQL injection vulnerabilities
        sql_patterns = [
            r'execute\s*\(\s*["\'].*%.*["\']',
            r'query\s*\(\s*["\'].*\+.*["\']'
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type="sql_injection_risk",
                        severity=IssueLevel.ERROR,
                        message="Potential SQL injection vulnerability",
                        suggestion="Use parameterized queries or ORM",
                        perspective="security"
                    ))
        
        # Check for eval usage
        if 'eval(' in content:
            for i, line in enumerate(lines, 1):
                if 'eval(' in line:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type="dangerous_function",
                        severity=IssueLevel.ERROR,
                        message="Use of dangerous eval() function",
                        suggestion="Avoid eval() - use safer alternatives",
                        perspective="security"
                    ))
        
        return issues
    
    def generate_report(self, output_format: str = "text") -> str:
        """Generate a comprehensive review report."""
        
        if output_format == "json":
            import json
            return json.dumps({
                "stats": self.review_stats,
                "issues": [
                    {
                        "file": issue.file_path,
                        "line": issue.line_number,
                        "type": issue.issue_type,
                        "severity": issue.severity.value,
                        "message": issue.message,
                        "suggestion": issue.suggestion,
                        "perspective": issue.perspective
                    }
                    for issue in self.issues_found
                ]
            }, indent=2)
        
        # Text format
        report = []
        report.append("🎯 SMART CODE REVIEW REPORT")
        report.append("=" * 40)
        
        # Summary statistics
        critical_count = sum(1 for issue in self.issues_found if issue.severity == IssueLevel.CRITICAL)
        error_count = sum(1 for issue in self.issues_found if issue.severity == IssueLevel.ERROR)
        warning_count = sum(1 for issue in self.issues_found if issue.severity == IssueLevel.WARNING)
        info_count = sum(1 for issue in self.issues_found if issue.severity == IssueLevel.INFO)
        
        report.append(f"Files Reviewed: {self.review_stats['files_reviewed']}")
        report.append(f"Total Issues: {len(self.issues_found)}")
        report.append(f"Critical: {critical_count}, Errors: {error_count}, Warnings: {warning_count}, Info: {info_count}")
        report.append("")
        
        # Group issues by file
        issues_by_file = {}
        for issue in self.issues_found:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
        
        # Report issues for each file
        for file_path, issues in issues_by_file.items():
            report.append(f"📄 {file_path}")
            report.append("-" * 60)
            
            for issue in sorted(issues, key=lambda x: (x.line_number, x.severity.value)):
                severity_emoji = {
                    IssueLevel.CRITICAL: "🚨",
                    IssueLevel.ERROR: "❌", 
                    IssueLevel.WARNING: "⚠️",
                    IssueLevel.INFO: "ℹ️"
                }
                
                report.append(f"  {severity_emoji[issue.severity]} Line {issue.line_number}: {issue.message}")
                report.append(f"     [{issue.perspective}] {issue.suggestion}")
                report.append("")
            
            report.append("")
        
        # Summary by perspective
        perspectives = {}
        for issue in self.issues_found:
            if issue.perspective not in perspectives:
                perspectives[issue.perspective] = 0
            perspectives[issue.perspective] += 1
        
        report.append("🔍 PERSPECTIVE ANALYSIS")
        report.append("-" * 25)
        for perspective, count in perspectives.items():
            report.append(f"  {perspective}: {count} issues")
        
        report.append("")
        report.append("✨ Review completed using ontological perspective switching!")
        
        return "\n".join(report)


def main():
    """Command-line interface for smart code reviewer."""
    
    parser = argparse.ArgumentParser(
        description="Smart Code Reviewer with Ontological Perspective Switching",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gem_1_smart_code_reviewer.py file.py
  python gem_1_smart_code_reviewer.py --directory src/
  python gem_1_smart_code_reviewer.py --ci-mode *.py
        """
    )
    
    parser.add_argument('files', nargs='*', help='Files to review')
    parser.add_argument('--directory', '-d', help='Review all Python files in directory')
    parser.add_argument('--output-format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--ci-mode', action='store_true',
                       help='CI mode: exit with non-zero code if critical issues found')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output with ontological switching details')
    
    args = parser.parse_args()
    
    if not args.files and not args.directory:
        parser.print_help()
        return 1
    
    print("🎯 SMART CODE REVIEWER")
    print("=" * 30)
    print("Using ontological perspective switching for comprehensive analysis")
    print()
    
    reviewer = SmartCodeReviewer()
    
    # Collect files to review
    files_to_review = []
    
    if args.directory:
        directory = Path(args.directory)
        if directory.is_dir():
            files_to_review.extend(directory.glob('**/*.py'))
        else:
            print(f"❌ Directory not found: {args.directory}")
            return 1
    
    for file_pattern in args.files:
        file_path = Path(file_pattern)
        if file_path.is_file():
            files_to_review.append(file_path)
        else:
            # Try glob pattern
            files_to_review.extend(Path('.').glob(file_pattern))
    
    if not files_to_review:
        print("❌ No files found to review")
        return 1
    
    print(f"📋 Reviewing {len(files_to_review)} files...")
    print()
    
    # Review each file
    for file_path in files_to_review:
        if args.verbose:
            print(f"🔍 Reviewing: {file_path}")
        
        issues = reviewer.review_file(str(file_path))
        
        if args.verbose:
            print(f"   Found {len(issues)} issues")
            print()
    
    # Generate and display report
    report = reviewer.generate_report(args.output_format)
    print(report)
    
    # CI mode: exit with error code if critical issues found
    if args.ci_mode:
        critical_issues = [issue for issue in reviewer.issues_found 
                          if issue.severity == IssueLevel.CRITICAL]
        if critical_issues:
            print(f"\n❌ CI FAILURE: {len(critical_issues)} critical issues found")
            return 1
        else:
            print(f"\n✅ CI SUCCESS: No critical issues found")
            return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
