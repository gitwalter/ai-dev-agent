#!/usr/bin/env python3
"""
Self-Healing Naming Convention Validator
========================================

Automated Boy Scout Rule implementation for naming convention compliance.
Detects, reports, and optionally fixes naming violations across the entire project.

Based on Universal Naming Conventions Reference Guide:
- Epic files: epic-{number}-{topic}.md
- User stories: US-{XXX}.md
- Sprint files: sprint_{N}_{type}.md
- Code files: {name}_{type}.py
- And all other established patterns

Features:
- Real-time validation during development
- Automatic fixing with --fix flag
- Integration with git hooks
- Comprehensive reporting
- Boy Scout Rule automation
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class NamingViolation:
    """Represents a naming convention violation."""
    file_path: str
    violation_type: str
    current_name: str
    suggested_name: str
    rule_reference: str
    severity: str  # "ERROR", "WARNING", "INFO"
    auto_fixable: bool
    

@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    total_files_scanned: int
    violations_found: int
    violations_fixed: int
    violations_by_type: Dict[str, int]
    violations_by_severity: Dict[str, int]
    scan_duration: float
    timestamp: str
    violations: List[NamingViolation]


class NamingConventionPatterns:
    """
    Centralized naming convention patterns based on Universal Naming Conventions.
    """
    
    # Agile Artifacts
    EPIC_PATTERN = re.compile(r'^epic-(\d+)-([a-z0-9-]+)\.md$')
    USER_STORY_PATTERN = re.compile(r'^US-[A-Z0-9-]+\.md$')
    SPRINT_PATTERN = re.compile(r'^sprint_\d+_[a-z_]+\.md$')
    CATALOG_PATTERN = re.compile(r'^[a-z_]+_catalog\.md$')
    
    # Code Artifacts
    AGENT_PATTERN = re.compile(r'^[a-z0-9_]+(agent|team|specialist)\.py$')
    MODEL_PATTERN = re.compile(r'^[a-z0-9_]+(model|state|schema|config)\.py$')
    UTILS_PATTERN = re.compile(r'^[a-z0-9_]+(utils|helper|manager)\.py$')
    WORKFLOW_PATTERN = re.compile(r'^[a-z0-9_]+(workflow|orchestrator)\.py$')
    APP_PATTERN = re.compile(r'^[a-z0-9_]+(app|ui)\.py$')
    
    # Test Artifacts
    TEST_PATTERN = re.compile(r'^test_[a-z0-9_]+\.py$')
    
    # Documentation
    GUIDE_PATTERN = re.compile(r'^[a-z0-9_]+_guide\.md$')
    RULE_PATTERN = re.compile(r'^[a-z0-9_]+_rule\.(md|mdc)$')
    ARCHITECTURE_PATTERN = re.compile(r'^[a-z0-9_]+(architecture|overview)\.md$')
    
    # Configuration
    JSON_CONFIG_PATTERN = re.compile(r'^[a-z0-9_]+\.json$')
    YAML_CONFIG_PATTERN = re.compile(r'^[a-z0-9_]+\.(yaml|yml)$')
    ENV_PATTERN = re.compile(r'^\.env(\.[a-z]+)?$')
    REQUIREMENTS_PATTERN = re.compile(r'^requirements(_[a-z]+)?\.txt$')
    
    # Data Files
    DATABASE_PATTERN = re.compile(r'^[a-z0-9_]+\.(db|sqlite)$')
    DATA_JSON_PATTERN = re.compile(r'^[a-z0-9_]+\.json$')
    CSV_PATTERN = re.compile(r'^[a-z0-9_]+\.csv$')
    LOG_PATTERN = re.compile(r'^[a-z0-9_]+(_\d{8})?\.log$')


class SelfHealingNamingValidator:
    """
    Main validator class implementing Boy Scout Rule for naming conventions.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.patterns = NamingConventionPatterns()
        self.violations: List[NamingViolation] = []
        
        # File type categorization rules
        self.file_type_rules = {
            # Agile artifacts
            "docs/agile/epics/": {
                "pattern": self.patterns.EPIC_PATTERN,
                "type": "epic",
                "severity": "ERROR",
                "auto_fixable": True
            },
            "docs/agile/sprints/": {
                "pattern": self.patterns.USER_STORY_PATTERN,
                "type": "user_story", 
                "severity": "ERROR",
                "auto_fixable": True,
                "file_filter": lambda f: f.startswith("US-")
            },
            "docs/agile/catalogs/": {
                "pattern": self.patterns.CATALOG_PATTERN,
                "type": "catalog",
                "severity": "WARNING", 
                "auto_fixable": True
            },
            
            # Code artifacts
            "agents/": {
                "pattern": self.patterns.AGENT_PATTERN,
                "type": "agent",
                "severity": "ERROR",
                "auto_fixable": True
            },
            "models/": {
                "pattern": self.patterns.MODEL_PATTERN,
                "type": "model",
                "severity": "ERROR",
                "auto_fixable": True
            },
            "utils/": {
                "pattern": self.patterns.UTILS_PATTERN,
                "type": "utils",
                "severity": "ERROR",
                "auto_fixable": True
            },
            "workflow/": {
                "pattern": self.patterns.WORKFLOW_PATTERN,
                "type": "workflow",
                "severity": "ERROR",
                "auto_fixable": True
            },
            "apps/": {
                "pattern": self.patterns.APP_PATTERN,
                "type": "app",
                "severity": "ERROR",
                "auto_fixable": True
            },
            
            # Test artifacts
            "tests/": {
                "pattern": self.patterns.TEST_PATTERN,
                "type": "test",
                "severity": "ERROR",
                "auto_fixable": True
            },
            
            # Documentation
            "docs/guides/": {
                "pattern": self.patterns.GUIDE_PATTERN,
                "type": "guide",
                "severity": "WARNING",
                "auto_fixable": True
            },
            "docs/rules/": {
                "pattern": self.patterns.RULE_PATTERN,
                "type": "rule",
                "severity": "ERROR",
                "auto_fixable": True
            }
        }
    
    def scan_project(self, exclude_patterns: Optional[List[str]] = None) -> ValidationReport:
        """
        Scan entire project for naming convention violations.
        """
        start_time = datetime.now()
        
        if exclude_patterns is None:
            exclude_patterns = [
                ".git/", "__pycache__/", "node_modules/", ".pytest_cache/",
                "venv/", "env/", ".vscode/", ".idea/", "*.pyc", "*.pyo"
            ]
        
        total_files = 0
        self.violations = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern.rstrip('/') in str(Path(root) / d) for pattern in exclude_patterns)]
            
            rel_root = Path(root).relative_to(self.project_root)
            
            for file in files:
                # Skip excluded files
                if any(self._matches_exclude_pattern(file, pattern) for pattern in exclude_patterns):
                    continue
                
                total_files += 1
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_root)
                
                self._validate_file(rel_path)
        
        end_time = datetime.now()
        scan_duration = (end_time - start_time).total_seconds()
        
        return self._generate_report(total_files, scan_duration)
    
    def _matches_exclude_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches exclude pattern."""
        if pattern.endswith('/'):
            return False  # Directory pattern
        if '*' in pattern:
            import fnmatch
            return fnmatch.fnmatch(filename, pattern)
        return pattern in filename
    
    def _validate_file(self, file_path: Path) -> None:
        """
        Validate a single file against naming conventions.
        """
        file_str = str(file_path).replace('\\', '/')
        filename = file_path.name
        
        # Find applicable rule
        for path_pattern, rule in self.file_type_rules.items():
            if file_str.startswith(path_pattern):
                # Apply file filter if specified
                if "file_filter" in rule and not rule["file_filter"](filename):
                    continue
                
                # Check pattern
                if not rule["pattern"].match(filename):
                    suggested_name = self._suggest_fix(filename, rule["type"], file_path)
                    
                    violation = NamingViolation(
                        file_path=file_str,
                        violation_type=rule["type"],
                        current_name=filename,
                        suggested_name=suggested_name,
                        rule_reference=f"Universal Naming Conventions - {rule['type']}",
                        severity=rule["severity"],
                        auto_fixable=rule["auto_fixable"]
                    )
                    
                    self.violations.append(violation)
                break
    
    def _suggest_fix(self, filename: str, file_type: str, file_path: Path) -> str:
        """
        Suggest corrected filename based on naming conventions.
        """
        base_name = file_path.stem
        extension = file_path.suffix
        
        # Convert to lowercase with underscores
        suggested_base = re.sub(r'[^a-z0-9_-]', '_', base_name.lower())
        suggested_base = re.sub(r'[_-]+', '_', suggested_base)
        suggested_base = suggested_base.strip('_')
        
        # Apply type-specific rules
        if file_type == "epic":
            # Extract number if present
            number_match = re.search(r'(\d+)', suggested_base)
            if number_match:
                number = number_match.group(1)
                topic = re.sub(r'\d+', '', suggested_base).strip('_-')
                return f"epic-{number}-{topic}{extension}"
            else:
                return f"epic-0-{suggested_base}{extension}"
        
        elif file_type in ["agent", "model", "utils", "workflow", "app"]:
            if not suggested_base.endswith(f"_{file_type}"):
                suggested_base = f"{suggested_base}_{file_type}"
        
        elif file_type == "test":
            if not suggested_base.startswith("test_"):
                suggested_base = f"test_{suggested_base}"
        
        elif file_type in ["guide", "rule"]:
            if not suggested_base.endswith(f"_{file_type}"):
                suggested_base = f"{suggested_base}_{file_type}"
        
        return f"{suggested_base}{extension}"
    
    def fix_violations(self, severity_filter: Optional[str] = None) -> int:
        """
        Automatically fix violations that are auto-fixable.
        """
        fixed_count = 0
        
        for violation in self.violations:
            if not violation.auto_fixable:
                continue
            
            if severity_filter and violation.severity != severity_filter:
                continue
            
            old_path = self.project_root / violation.file_path
            new_path = old_path.parent / violation.suggested_name
            
            try:
                # Check if target already exists
                if new_path.exists():
                    print(f"⚠️  Cannot fix {violation.file_path}: {violation.suggested_name} already exists")
                    continue
                
                # Rename file
                old_path.rename(new_path)
                print(f"✅ Fixed: {violation.current_name} → {violation.suggested_name}")
                fixed_count += 1
                
            except Exception as e:
                print(f"❌ Failed to fix {violation.file_path}: {e}")
        
        return fixed_count
    
    def _generate_report(self, total_files: int, scan_duration: float) -> ValidationReport:
        """
        Generate comprehensive validation report.
        """
        violations_by_type = {}
        violations_by_severity = {}
        
        for violation in self.violations:
            violations_by_type[violation.violation_type] = violations_by_type.get(violation.violation_type, 0) + 1
            violations_by_severity[violation.severity] = violations_by_severity.get(violation.severity, 0) + 1
        
        return ValidationReport(
            total_files_scanned=total_files,
            violations_found=len(self.violations),
            violations_fixed=0,  # Will be updated if fix is run
            violations_by_type=violations_by_type,
            violations_by_severity=violations_by_severity,
            scan_duration=scan_duration,
            timestamp=datetime.now().isoformat(),
            violations=self.violations
        )
    
    def generate_html_report(self, report: ValidationReport, output_file: str = "naming_validation_report.html") -> None:
        """
        Generate detailed HTML report for stakeholders.
        """
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Naming Convention Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .metric {{ text-align: center; }}
        .metric h3 {{ margin: 0; color: #333; }}
        .metric .value {{ font-size: 2em; font-weight: bold; color: #007acc; }}
        .violations {{ margin-top: 30px; }}
        .violation {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .error {{ border-left: 5px solid #d73027; }}
        .warning {{ border-left: 5px solid #fc8d59; }}
        .info {{ border-left: 5px solid #91bfdb; }}
        .suggestion {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧹 Self-Healing Naming Convention Validation Report</h1>
        <p><strong>Generated:</strong> {report.timestamp}</p>
        <p><strong>Scan Duration:</strong> {report.scan_duration:.2f} seconds</p>
        <p><strong>Project Root:</strong> {self.project_root}</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>Files Scanned</h3>
            <div class="value">{report.total_files_scanned}</div>
        </div>
        <div class="metric">
            <h3>Violations Found</h3>
            <div class="value">{report.violations_found}</div>
        </div>
        <div class="metric">
            <h3>Auto-Fixable</h3>
            <div class="value">{sum(1 for v in report.violations if v.auto_fixable)}</div>
        </div>
    </div>
    
    <h2>📊 Violations by Type</h2>
    <ul>
        {self._generate_type_breakdown_html(report.violations_by_type)}
    </ul>
    
    <h2>⚠️ Violations by Severity</h2>
    <ul>
        {self._generate_severity_breakdown_html(report.violations_by_severity)}
    </ul>
    
    <div class="violations">
        <h2>🔍 Detailed Violations</h2>
        {self._generate_violations_html(report.violations)}
    </div>
    
    <div style="margin-top: 50px; padding: 20px; background-color: #e8f4f8; border-radius: 5px;">
        <h3>🤖 Boy Scout Rule Integration</h3>
        <p>This validator implements the Boy Scout Rule: "Always leave the codebase cleaner than you found it."</p>
        <p><strong>Auto-fix command:</strong> <code>python utils/validation/self_healing_naming_validator.py --fix</code></p>
        <p><strong>Git hook integration:</strong> Add to pre-commit hooks for automatic validation</p>
    </div>
</body>
</html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 HTML report generated: {output_file}")
    
    def _generate_type_breakdown_html(self, violations_by_type: Dict[str, int]) -> str:
        """Generate HTML for violation type breakdown."""
        items = []
        for vtype, count in violations_by_type.items():
            items.append(f"<li><strong>{vtype}</strong>: {count} violations</li>")
        return "\n".join(items)
    
    def _generate_severity_breakdown_html(self, violations_by_severity: Dict[str, int]) -> str:
        """Generate HTML for violation severity breakdown.""" 
        items = []
        for severity, count in violations_by_severity.items():
            items.append(f"<li><strong>{severity}</strong>: {count} violations</li>")
        return "\n".join(items)
    
    def _generate_violations_html(self, violations: List[NamingViolation]) -> str:
        """Generate HTML for individual violations."""
        html_parts = []
        
        for violation in violations:
            severity_class = violation.severity.lower()
            auto_fix_badge = "🔧 Auto-fixable" if violation.auto_fixable else "🔍 Manual review needed"
            
            html = f"""
            <div class="violation {severity_class}">
                <h4>{violation.severity}: {violation.violation_type.replace('_', ' ').title()}</h4>
                <p><strong>File:</strong> {violation.file_path}</p>
                <p><strong>Current name:</strong> <code>{violation.current_name}</code></p>
                <div class="suggestion">
                    <strong>Suggested name:</strong> <code>{violation.suggested_name}</code>
                </div>
                <p><strong>Rule reference:</strong> {violation.rule_reference}</p>
                <p><strong>Status:</strong> {auto_fix_badge}</p>
            </div>
            """
            html_parts.append(html)
        
        return "\n".join(html_parts)


def main():
    """
    CLI interface for the self-healing naming validator.
    """
    parser = argparse.ArgumentParser(
        description="Self-Healing Naming Convention Validator - Boy Scout Rule Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan and report violations
  python self_healing_naming_validator.py --scan
  
  # Auto-fix all violations
  python self_healing_naming_validator.py --fix
  
  # Fix only ERROR level violations
  python self_healing_naming_validator.py --fix --severity ERROR
  
  # Generate HTML report
  python self_healing_naming_validator.py --scan --html-report
  
  # Scan specific directory
  python self_healing_naming_validator.py --scan --root docs/agile
        """
    )
    
    parser.add_argument('--scan', action='store_true', 
                       help='Scan project for naming violations')
    parser.add_argument('--fix', action='store_true',
                       help='Automatically fix violations (Boy Scout Rule)')
    parser.add_argument('--severity', choices=['ERROR', 'WARNING', 'INFO'],
                       help='Filter by severity level')
    parser.add_argument('--root', default='.',
                       help='Project root directory (default: current directory)')
    parser.add_argument('--html-report', action='store_true',
                       help='Generate HTML report')
    parser.add_argument('--json-output', 
                       help='Save JSON report to file')
    parser.add_argument('--exclude', nargs='*', default=[],
                       help='Additional exclude patterns')
    
    args = parser.parse_args()
    
    if not (args.scan or args.fix):
        parser.error("Must specify either --scan or --fix")
    
    # Initialize validator
    validator = SelfHealingNamingValidator(args.root)
    
    # Scan for violations
    print("🔍 Scanning project for naming convention violations...")
    report = validator.scan_project(exclude_patterns=args.exclude or None)
    
    # Print summary
    print(f"\n📊 Scan Results:")
    print(f"   Files scanned: {report.total_files_scanned}")
    print(f"   Violations found: {report.violations_found}")
    print(f"   Scan duration: {report.scan_duration:.2f}s")
    
    if report.violations_found == 0:
        print("✅ No naming violations found! Project follows Boy Scout principles.")
        return 0
    
    # Print violations by severity
    print(f"\n⚠️  Violations by severity:")
    for severity, count in sorted(report.violations_by_severity.items()):
        print(f"   {severity}: {count}")
    
    # Print violations by type
    print(f"\n📋 Violations by type:")
    for vtype, count in sorted(report.violations_by_type.items()):
        print(f"   {vtype}: {count}")
    
    # Show detailed violations (limit to first 10)
    print(f"\n🔍 Sample violations:")
    for i, violation in enumerate(report.violations[:10]):
        print(f"   {i+1}. {violation.file_path}")
        print(f"      Current: {violation.current_name}")
        print(f"      Suggested: {violation.suggested_name}")
        print(f"      Severity: {violation.severity} | Auto-fixable: {violation.auto_fixable}")
        print()
    
    if len(report.violations) > 10:
        print(f"   ... and {len(report.violations) - 10} more violations")
    
    # Fix violations if requested
    if args.fix:
        print(f"\n🔧 Applying Boy Scout Rule - fixing violations...")
        fixed_count = validator.fix_violations(args.severity)
        print(f"✅ Fixed {fixed_count} violations")
        report.violations_fixed = fixed_count
    
    # Generate reports
    if args.html_report:
        validator.generate_html_report(report)
    
    if args.json_output:
        with open(args.json_output, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        print(f"📄 JSON report saved: {args.json_output}")
    
    # Return appropriate exit code
    return 1 if report.violations_found > 0 and not args.fix else 0


if __name__ == "__main__":
    sys.exit(main())
