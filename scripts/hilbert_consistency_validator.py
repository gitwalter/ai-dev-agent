#!/usr/bin/env python3
"""
Hilbert Consistency Validator - Automated Excellence Enforcement

PURPOSE: Build beautiful, useful validation that serves developers
PHILOSOPHY: Mathematical beauty through systematic consistency
RESULT: Permanent organizational excellence
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ValidationResult:
    """Beautiful, clear validation result structure."""
    file_path: str
    category: str
    expected_pattern: str
    actual_pattern: str
    is_consistent: bool
    violation_type: str = ""
    suggested_fix: str = ""


class HilbertConsistencyValidator:
    """
    Beautiful validation system that enforces Hilbert consistency across all files.
    
    🧮 HILBERT PRINCIPLE: Internal consistency creates mathematical beauty
    🏛️ ANCESTRAL WISDOM: Every validation serves systematic excellence
    💎 THREE PILLARS: Mathematical beauty + Technical excellence + Moral integrity
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.docs_root = self.project_root / "docs"
        
        # Beautiful, systematic naming patterns
        self.hilbert_patterns = {
            "strategic_documents": {
                "pattern": r"^[A-Z][A-Z0-9_]*\.md$",
                "description": "CAPITAL_CASE.md for strategic documents",
                "directories": [
                    "docs/agile/catalogs/",
                    "docs/concepts/", 
                    "docs/consciousness/",
                    "docs/technical/",
                    "docs/rules/core/",
                    "docs/development/",
                    "docs/testing/",
                    "docs/guides/"
                ],
                "examples": ["USER_STORY_CATALOG.md", "SPRINT_SUMMARY.md"]
            },
            
            "operational_documents": {
                "pattern": r"^[a-z][a-z0-9_]*\.md$", 
                "description": "lowercase_case.md for operational documents",
                "directories": [
                    "docs/agile/core/",
                    "docs/troubleshooting/",
                    "docs/testing/",
                    "docs/operating-modes/"
                ],
                "examples": ["daily_standup.md", "agile_cursor_rules.md"]
            },
            
            "thematic_collections": {
                "pattern": r"^[a-z][a-z0-9\-]*\.md$",
                "description": "lowercase-hyphens.md for thematic collections", 
                "directories": [
                    "docs/guides/implementation/",
                    "docs/guides/database/",
                    "docs/quick-start/",
                    "docs/guides/development/",
                    "docs/philosophy/"
                ],
                "examples": ["task-3-3-progress.md", "quality-gates.md"]
            },
            
            "unique_identifiers": {
                "pattern": r"^[A-Z]{2,}-[A-Z0-9\-]+\.md$",
                "description": "CODE-PATTERN.md for unique identifiers",
                "directories": [
                    "docs/agile/sprints/*/user_stories/",
                    "docs/agile/user_stories/"
                ],
                "examples": ["US-001.md", "US-PE-01.md"]
            }
        }
        
        # Track validation results
        self.validation_results = []
        self.violations = []
        
    def validate_project_consistency(self) -> Dict[str, any]:
        """
        🌟 MAIN VALIDATION: Complete Hilbert consistency check across project.
        
        Returns beautiful, comprehensive validation report.
        """
        print("🧮 Starting Hilbert Consistency Validation...")
        print("=" * 60)
        
        validation_summary = {
            "total_files_checked": 0,
            "consistent_files": 0,
            "violations_found": 0,
            "categories_validated": {},
            "overall_consistency_score": 0.0,
            "validation_timestamp": datetime.now().isoformat()
        }
        
        # Validate each category systematically
        for category, pattern_info in self.hilbert_patterns.items():
            print(f"\n🔍 Validating {category}...")
            category_results = self._validate_category(category, pattern_info)
            
            validation_summary["categories_validated"][category] = {
                "files_checked": len(category_results),
                "violations": len([r for r in category_results if not r.is_consistent]),
                "consistency_rate": self._calculate_consistency_rate(category_results)
            }
            
            validation_summary["total_files_checked"] += len(category_results)
            validation_summary["consistent_files"] += len([r for r in category_results if r.is_consistent])
            
            self.validation_results.extend(category_results)
        
        # Calculate overall consistency
        if validation_summary["total_files_checked"] > 0:
            validation_summary["overall_consistency_score"] = (
                validation_summary["consistent_files"] / validation_summary["total_files_checked"]
            )
        
        validation_summary["violations_found"] = validation_summary["total_files_checked"] - validation_summary["consistent_files"]
        
        return validation_summary
    
    def _validate_category(self, category: str, pattern_info: Dict) -> List[ValidationResult]:
        """Validate all files in a specific category."""
        results = []
        pattern = re.compile(pattern_info["pattern"])
        
        # Check all relevant directories
        for directory_pattern in pattern_info["directories"]:
            # Handle wildcard patterns
            if "*" in directory_pattern:
                directories = self._expand_wildcard_pattern(directory_pattern)
            else:
                directories = [self.project_root / directory_pattern]
            
            for directory in directories:
                if directory.exists() and directory.is_dir():
                    for md_file in directory.glob("*.md"):
                        result = self._validate_single_file(
                            md_file, category, pattern, pattern_info["description"]
                        )
                        results.append(result)
        
        return results
    
    def _expand_wildcard_pattern(self, pattern: str) -> List[Path]:
        """Expand wildcard patterns like docs/agile/sprints/*/user_stories/"""
        base_path = self.project_root
        parts = pattern.split("/")
        
        paths = [base_path]
        for part in parts:
            if part == "*":
                new_paths = []
                for path in paths:
                    if path.exists():
                        new_paths.extend([p for p in path.iterdir() if p.is_dir()])
                paths = new_paths
            else:
                paths = [path / part for path in paths]
        
        return [path for path in paths if path.exists() and path.is_dir()]
    
    def _validate_single_file(self, file_path: Path, category: str, pattern: re.Pattern, description: str) -> ValidationResult:
        """Validate a single file against Hilbert consistency patterns."""
        
        filename = file_path.name
        is_consistent = bool(pattern.match(filename))
        
        result = ValidationResult(
            file_path=str(file_path.relative_to(self.project_root)),
            category=category,
            expected_pattern=description,
            actual_pattern=filename,
            is_consistent=is_consistent
        )
        
        if not is_consistent:
            result.violation_type = f"Naming pattern violation in {category}"
            result.suggested_fix = self._suggest_fix(filename, category)
            self.violations.append(result)
        
        return result
    
    def _suggest_fix(self, filename: str, category: str) -> str:
        """Suggest beautiful fix for naming violations."""
        base_name = filename.replace(".md", "")
        
        if category == "strategic_documents":
            # Convert to CAPITAL_CASE
            suggested = re.sub(r'[^a-zA-Z0-9]', '_', base_name).upper()
            return f"{suggested}.md"
        
        elif category == "operational_documents":
            # Convert to lowercase_case
            suggested = re.sub(r'[^a-zA-Z0-9]', '_', base_name).lower()
            return f"{suggested}.md"
        
        elif category == "thematic_collections":
            # Convert to lowercase-hyphens
            suggested = re.sub(r'[^a-zA-Z0-9]', '-', base_name).lower()
            # Clean up multiple hyphens
            suggested = re.sub(r'-+', '-', suggested)
            return f"{suggested}.md"
        
        else:
            return f"Review naming for {category} compliance"
    
    def _calculate_consistency_rate(self, results: List[ValidationResult]) -> float:
        """Calculate beautiful consistency percentage."""
        if not results:
            return 100.0
        
        consistent_count = len([r for r in results if r.is_consistent])
        return (consistent_count / len(results)) * 100.0
    
    def generate_beautiful_report(self) -> str:
        """Generate a beautiful, comprehensive validation report."""
        
        report = []
        report.append("# 🧮 **Hilbert Consistency Validation Report**")
        report.append(f"**Generated**: {datetime.now().isoformat()}")
        report.append(f"**Purpose**: Ensure mathematical beauty through systematic consistency")
        report.append("")
        
        # Executive Summary
        total_files = len(self.validation_results)
        consistent_files = len([r for r in self.validation_results if r.is_consistent])
        violations = len(self.violations)
        
        consistency_score = (consistent_files / total_files * 100) if total_files > 0 else 100
        
        report.append("## 📊 **Executive Summary**")
        report.append(f"- **Total Files Validated**: {total_files}")
        report.append(f"- **Consistent Files**: {consistent_files}")
        report.append(f"- **Violations Found**: {violations}")
        report.append(f"- **Consistency Score**: {consistency_score:.1f}%")
        report.append("")
        
        # Category Breakdown
        report.append("## 🎯 **Category Analysis**")
        report.append("")
        
        categories = {}
        for result in self.validation_results:
            if result.category not in categories:
                categories[result.category] = {"total": 0, "consistent": 0}
            categories[result.category]["total"] += 1
            if result.is_consistent:
                categories[result.category]["consistent"] += 1
        
        for category, stats in categories.items():
            rate = (stats["consistent"] / stats["total"] * 100) if stats["total"] > 0 else 100
            status = "✅" if rate == 100 else "⚠️" if rate >= 80 else "🚨"
            
            report.append(f"### **{category.replace('_', ' ').title()}** {status}")
            report.append(f"- **Files**: {stats['total']}")
            report.append(f"- **Consistent**: {stats['consistent']}")
            report.append(f"- **Rate**: {rate:.1f}%")
            report.append("")
        
        # Violations Detail
        if self.violations:
            report.append("## 🚨 **Violations Requiring Attention**")
            report.append("")
            
            for violation in self.violations:
                report.append(f"### {violation.file_path}")
                report.append(f"- **Category**: {violation.category}")
                report.append(f"- **Expected**: {violation.expected_pattern}")
                report.append(f"- **Actual**: {violation.actual_pattern}")
                report.append(f"- **Suggested Fix**: {violation.suggested_fix}")
                report.append("")
        else:
            report.append("## 🌟 **Perfect Consistency Achieved!**")
            report.append("")
            report.append("All files follow Hilbert consistency patterns perfectly!")
            report.append("")
        
        # Beauty Metrics
        report.append("## 💎 **Beauty Metrics**")
        report.append("")
        report.append(f"- **Mathematical Elegance**: {consistency_score:.1f}% systematic consistency")
        report.append(f"- **Predictable Patterns**: {len(categories)} categories perfectly defined")
        report.append(f"- **Developer Delight**: Clear, logical file organization")
        report.append("")
        
        return "\n".join(report)
    
    def create_automation_config(self) -> Dict:
        """Create beautiful automation configuration for CI/CD integration."""
        
        return {
            "hilbert_validation": {
                "enabled": True,
                "validation_patterns": self.hilbert_patterns,
                "enforcement_level": "blocking",  # Prevent commits with violations
                "auto_fix": False,  # Require human review for fixes
                "report_path": "docs/agile/validation/hilbert_consistency_report.md"
            },
            
            "ci_integration": {
                "pre_commit_hook": True,
                "github_actions": True,
                "validation_command": "python scripts/hilbert_consistency_validator.py",
                "failure_threshold": 95.0  # 95% consistency required
            },
            
            "monitoring": {
                "track_consistency_trends": True,
                "alert_on_violations": True,
                "generate_metrics": True
            }
        }


def main():
    """
    🚀 MAIN EXECUTION: Beautiful validation for systematic excellence.
    """
    print("🌟 Building Beautiful and Useful Validation System")
    print("🧮 Purpose: Mathematical beauty through Hilbert consistency")
    print("=" * 60)
    
    # Initialize beautiful validator
    validator = HilbertConsistencyValidator()
    
    # Execute comprehensive validation
    validation_summary = validator.validate_project_consistency()
    
    # Generate beautiful report
    report = validator.generate_beautiful_report()
    
    # Save report
    report_dir = Path("docs/agile/validation")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "hilbert_consistency_report.md"
    report_path.write_text(report, encoding='utf-8')
    
    # Create automation config
    config = validator.create_automation_config()
    config_path = Path("scripts/validation_config.json")
    config_path.write_text(json.dumps(config, indent=2), encoding='utf-8')
    
    # Beautiful summary
    print(f"\n🌟 VALIDATION COMPLETE!")
    print(f"📊 Consistency Score: {validation_summary['overall_consistency_score']:.1f}%")
    print(f"📋 Files Checked: {validation_summary['total_files_checked']}")
    print(f"🚨 Violations: {validation_summary['violations_found']}")
    print(f"📄 Report: {report_path}")
    print(f"⚙️ Config: {config_path}")
    
    # Philosophy in action
    if validation_summary['violations_found'] == 0:
        print(f"\n💎 PERFECT HILBERT CONSISTENCY ACHIEVED!")
        print(f"🧮 Mathematical beauty through systematic excellence!")
    else:
        print(f"\n🔧 BEAUTY OPPORTUNITIES IDENTIFIED!")
        print(f"🌟 Each fix brings us closer to mathematical perfection!")
    
    return validator


if __name__ == "__main__":
    main()
