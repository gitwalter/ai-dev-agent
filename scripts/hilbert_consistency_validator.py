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
from typing import Dict, List, Tuple, Set, Optional
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
        self._scope_paths: Optional[List[Path]] = None
        
        # File organization patterns (Sacred File Organization Rule integration)
        self.file_organization_patterns = {
            "test_files": {
                "pattern": r"^test_.*\.py$|.*_test\.py$",
                "required_location": "tests/",
                "description": "Test files must be in tests/ directory"
            },
            "agent_files": {
                "pattern": r".*agent.*\.py$",
                "required_location": "agents/",
                "description": "Agent files must be in agents/ directory"
            },
            "utility_files": {
                "pattern": r"^(?!app|test_).*\.py$",
                "required_location": "utils/",
                "description": "Utility files must be in utils/ directory"
            },
            "rule_files": {
                "pattern": r".*\.mdc$",
                "required_location": ".cursor/rules/",
                "description": "Rule files must be in .cursor/rules/ directory"
            },
            "documentation": {
                "pattern": r"^(?!README).*\.md$",
                "required_location": "docs/",
                "description": "Documentation files must be in docs/ directory"
            }
        }
        
        # Temporary/demo files that can optionally be deleted.
        #
        # Safety First:
        # - deletion is opt-in (see --cleanup-temp-files)
        # - scanning is limited to root + scripts (via `locations`) to avoid noisy matches
        #   in docs/ and other directories
        self.cleanup_patterns = {
            "temporary_scripts": {
                "pattern": r"^(query_|show_|list_|simple_|build_|test_).*\.py$",
                "locations": [".", "scripts/"],
                "description": "Temporary demo/test scripts in root or scripts directory",
                "action": "delete"
            },
            "empty_files": {
                "pattern": r".*\.py$",
                "size_threshold": 50,  # bytes
                "locations": [".", "scripts/"],
                "description": "Empty or nearly empty Python files",
                "action": "delete"
            },
            "demo_files": {
                "pattern": r".*(demo|temp|tmp|sample).*\.py$",
                "locations": [".", "scripts/"],
                "description": "Demo and temporary files",
                "action": "delete"
            }
        }
        
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
            
            "agile_core_documents": {
                # The agile core directory intentionally contains a mix of:
                # - CAPITAL_CASE.md (system-level specs)
                # - lowercase_case.md (operational rules/guides)
                # - lowercase-hyphens.md (guide-style docs)
                "pattern": r"^(?:[A-Z][A-Z0-9_]*|[a-z][a-z0-9_]*|[a-z][a-z0-9\-]*)\.md$",
                "description": "Agile core docs may be CAPITAL_CASE, lowercase_case, or lowercase-hyphens",
                "directories": [
                    "docs/agile/core/",
                ],
                "examples": ["AGILE_COORDINATION_SYSTEM.md", "definition_of_done.md", "agile_workflow.md"]
            },
            
            "operational_documents": {
                "pattern": r"^[a-z][a-z0-9_]*\.md$", 
                "description": "lowercase_case.md for operational documents",
                "directories": [
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
                # These directories contain canonical user story IDs *and* occasional narrative docs.
                "pattern": (
                    r"^(?:"
                    r"(?:US|EPIC|T)-[A-Z0-9]+(?:-[A-Z0-9]+)*(?:[-_][A-Za-z0-9][A-Za-z0-9_-]*)?"
                    r"|[a-z][a-z0-9_]*"
                    r"|[a-z][a-z0-9\-]*"
                    r")\.md$"
                ),
                "description": "User story docs are either ID-based (US-...) or lowercase docs",
                "directories": [
                    "docs/agile/sprints/*/user_stories/",
                    "docs/agile/user_stories/"
                ],
                "examples": ["US-001.md", "US-035-VIBE_CODER_AGENT_BUILDER.md", "story_monitoring_rule_optimization.md"]
            }
        }
        
        # Track validation results
        self.validation_results = []
        self.violations = []
        
    def validate_project_consistency(
        self,
        cleanup_temp_files: bool = False,
        validate_file_organization: bool = False,
        scope_paths: Optional[List[Path]] = None,
    ) -> Dict[str, any]:
        """
        Run a Hilbert consistency validation across the project.

        Args:
            cleanup_temp_files (bool): If True, delete matched temporary/demo files based on
                `self.cleanup_patterns`. This is disabled by default to comply with the
                Safety First rule (no destructive operations without explicit confirmation).
            validate_file_organization (bool): If True, run the file organization checker.
                This is disabled by default because many repositories contain legacy layouts
                that should be migrated deliberately (not enforced by a validator run).
            scope_paths (Optional[List[Path]]): If provided, only validate files under these
                directories/files. Paths may be relative to the project root or absolute.

        Returns:
            Dict[str, Any]: Summary including counts, per-category rates, organization violations,
                and temporary-file scan results.
        """
        self._scope_paths = self._normalize_scope_paths(scope_paths)

        print("[INFO] Starting Hilbert Consistency Validation...")
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
            print(f"\n[CHECK] Validating {category}...")
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
                (validation_summary["consistent_files"] / validation_summary["total_files_checked"]) * 100.0
            )
        
        validation_summary["violations_found"] = validation_summary["total_files_checked"] - validation_summary["consistent_files"]
        
        # Optional: file organization validation
        org_violations: List[str] = []
        if validate_file_organization:
            print("\n[CHECK] Validating File Organization Rule...")
            org_violations = self._validate_file_organization()
            validation_summary["file_organization_violations"] = len(org_violations)
            validation_summary["violations_found"] += len(org_violations)

            if org_violations:
                print(f"[X] Found {len(org_violations)} file organization violations")
                for violation in org_violations:
                    print(f"   - {violation}")
            else:
                print("[OK] All files follow the File Organization Rule")
        else:
            validation_summary["file_organization_violations"] = None
        
        # Temporary/demo file scan (deletion is opt-in)
        print("\n[CHECK] Scanning for temporary and demo files...")
        cleanup_results = self._cleanup_temporary_files(perform_delete=cleanup_temp_files)
        validation_summary["temporary_files_matched"] = cleanup_results["matched_count"]
        validation_summary["temporary_files_deleted"] = cleanup_results["deleted_count"]
        validation_summary["cleanup_summary"] = cleanup_results["summary"]

        if cleanup_results["matched_count"] > 0:
            print(f"[WARN] Matched {cleanup_results['matched_count']} temporary/demo files")
            if cleanup_temp_files:
                print(f"[WARN] Deleted {cleanup_results['deleted_count']} temporary/demo files (explicitly enabled)")
            else:
                print("[INFO] No files were deleted (cleanup disabled by default)")
        else:
            print("[OK] No temporary/demo files matched cleanup rules")
        
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
                        if self._scope_paths is not None and not self._is_in_scope(md_file):
                            continue
                        result = self._validate_single_file(
                            md_file, category, pattern, pattern_info["description"]
                        )
                        results.append(result)
        
        return results

    def _normalize_scope_paths(self, scope_paths: Optional[List[Path]]) -> Optional[List[Path]]:
        """
        Normalize scope paths to absolute paths.

        Args:
            scope_paths: Paths that define the validation scope.

        Returns:
            A list of absolute paths, or None if no scope is provided.
        """
        if not scope_paths:
            return None

        normalized: List[Path] = []
        for raw in scope_paths:
            p = Path(raw)
            if not p.is_absolute():
                p = self.project_root / p
            normalized.append(p.resolve())
        return normalized

    def _is_in_scope(self, file_path: Path) -> bool:
        """
        Determine whether the given path is within the current validation scope.

        Args:
            file_path: Path to check.

        Returns:
            True if in scope, else False.
        """
        if self._scope_paths is None:
            return True

        resolved = file_path.resolve()
        for scope in self._scope_paths:
            if scope.is_file() and resolved == scope:
                return True
            if scope.is_dir():
                try:
                    resolved.relative_to(scope)
                    return True
                except ValueError:
                    pass
        return False
    
    def _validate_file_organization(self) -> List[str]:
        """
        Validate file organization rule compliance.

        Returns:
            List[str]: Human-readable violations.
        """
        violations = []
        
        # Walk through all files in the project
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.project_root)
                
                # Check each file organization pattern
                for category, pattern_info in self.file_organization_patterns.items():
                    if re.match(pattern_info["pattern"], file):
                        required_location = str(pattern_info["required_location"]).replace("\\", "/")
                        current_location = relative_path.parent.as_posix() + "/"
                        
                        # Check if file is in correct location
                        if not current_location.startswith(required_location):
                            # Skip certain acceptable exceptions
                            if self._is_acceptable_file_location(relative_path, required_location):
                                continue
                                
                            violations.append(
                                f"{relative_path.as_posix()} should be in {required_location} "
                                f"(currently in {current_location})"
                            )
                        break  # Only check first matching pattern
        
        return violations
    
    def _cleanup_temporary_files(self, perform_delete: bool = False) -> Dict[str, any]:
        """
        Scan for (and optionally delete) temporary/demo files.

        Args:
            perform_delete (bool): If True, delete matched files. This is destructive and must
                only be enabled intentionally by the caller.

        Returns:
            Dict[str, Any]: Results including match count, delete count, and per-pattern summary.
        """
        cleanup_results = {
            "matched_count": 0,
            "deleted_count": 0,
            "matched_files": [],
            "deleted_files": [],
            "summary": {},
            "skipped_files": []
        }
        
        # Walk through project files
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.project_root)

                # Respect validation scope when present (avoid scanning unrelated areas)
                if self._scope_paths is not None and not self._is_in_scope(file_path):
                    continue
                
                # Check each cleanup pattern
                for pattern_name, pattern_info in self.cleanup_patterns.items():
                    should_delete = False
                    reason = ""
                    
                    # Check pattern match
                    if re.match(pattern_info["pattern"], file):
                        # Check location restrictions if specified
                        if "locations" in pattern_info:
                            current_location = relative_path.parent.as_posix()
                            allowed_locations = [str(loc).replace("\\", "/") for loc in pattern_info["locations"]]
                            if current_location in allowed_locations or current_location == ".":
                                should_delete = True
                                reason = f"Temporary file in {current_location}"
                        else:
                            should_delete = True
                            reason = "Matches cleanup pattern"
                    
                    # Check size threshold for empty files
                    if pattern_name == "empty_files" and file.endswith('.py'):
                        try:
                            if file_path.stat().st_size <= pattern_info.get("size_threshold", 50):
                                should_delete = True
                                reason = f"Empty file ({file_path.stat().st_size} bytes)"
                        except OSError:
                            continue
                    
                    # Skip certain protected files
                    if should_delete and self._is_protected_file(relative_path):
                        cleanup_results["skipped_files"].append(relative_path.as_posix())
                        should_delete = False
                    
                    if should_delete:
                        cleanup_results["matched_files"].append(relative_path.as_posix())
                        cleanup_results["matched_count"] += 1

                    # Delete the file (only if explicitly enabled)
                    if should_delete and perform_delete:
                        try:
                            file_path.unlink()
                            cleanup_results["deleted_files"].append(relative_path.as_posix())
                            cleanup_results["deleted_count"] += 1
                            
                            # Track by pattern
                            if pattern_name not in cleanup_results["summary"]:
                                cleanup_results["summary"][pattern_name] = 0
                            cleanup_results["summary"][pattern_name] += 1
                            
                            break  # Only delete once per file
                            
                        except OSError as e:
                            print(f"[WARN] Could not delete {relative_path.as_posix()}: {e}")
        
        return cleanup_results
    
    def _is_protected_file(self, file_path: Path) -> bool:
        """Check if file should be protected from automatic deletion."""
        protected_patterns = [
            r"setup\.py$",
            r"__init__\.py$", 
            r"conftest\.py$",
            r"requirements.*\.txt$",
            r".*\.toml$",
            r".*\.yml$",
            r".*\.yaml$",
            r"README.*\.md$"
        ]
        
        file_str = str(file_path)
        return any(re.search(pattern, file_str) for pattern in protected_patterns)
    
    def _is_acceptable_file_location(self, file_path: Path, required_location: str) -> bool:
        """Check if file location is acceptable even if not optimal."""
        filename = file_path.name
        current_str = file_path.as_posix()
        
        # README files can be in root or module directories
        if filename == 'README.md':
            return True
        
        # Configuration files in root are acceptable
        if filename.endswith(('.toml', '.ini', '.cfg', '.json')) and file_path.parent == Path('.'):
            return True
        
        # Temporary files during development (should be cleaned up)
        if filename.startswith(('temp_', 'debug_', 'test_')) and file_path.parent == Path('.'):
            return True  # Temporary allowance
        
        # App files in apps/ directory
        if filename.startswith('app') and 'apps/' in current_str:
            return True
            
        return False
    
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
                "validation_command": "python scripts/hilbert_consistency_validator.py --scope docs/agile",
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
    Main entrypoint for Hilbert consistency validation.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Hilbert consistency validation")
    parser.add_argument(
        "--cleanup-temp-files",
        action="store_true",
        help="Delete matched temporary/demo files (destructive; opt-in).",
    )
    parser.add_argument(
        "--validate-file-organization",
        action="store_true",
        help="Run file organization validation (may report legacy layout issues).",
    )
    parser.add_argument(
        "--scope",
        nargs="+",
        default=None,
        help="Limit validation to these paths (files or directories).",
    )
    parser.add_argument(
        "--full-project",
        action="store_true",
        help="Validate the entire repository (may fail due to legacy files outside docs/agile).",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write a markdown report to --report-path.",
    )
    parser.add_argument(
        "--report-path",
        default="docs/agile/validation/hilbert_consistency_report.md",
        help="Path for the markdown report when --write-report is set.",
    )
    parser.add_argument(
        "--write-config",
        action="store_true",
        help="Write automation config JSON to --config-path.",
    )
    parser.add_argument(
        "--config-path",
        default="scripts/validation_config.json",
        help="Path for automation config JSON when --write-config is set.",
    )
    args = parser.parse_args()

    print("[INFO] Hilbert consistency validation")
    print("=" * 60)

    # Default scope: docs/agile (the actively-maintained system).
    # Full-repo validation is opt-in via --full-project.
    if not args.scope and not args.full_project:
        args.scope = ["docs/agile"]

    validator = HilbertConsistencyValidator()
    validation_summary = validator.validate_project_consistency(
        cleanup_temp_files=args.cleanup_temp_files,
        validate_file_organization=args.validate_file_organization,
        scope_paths=[Path(p) for p in args.scope] if args.scope else None,
    )

    report_path = None
    if args.write_report:
        report = validator.generate_beautiful_report()
        report_path = Path(args.report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")

    config_path = None
    if args.write_config:
        config = validator.create_automation_config()
        config_path = Path(args.config_path)
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    print("\n[INFO] Validation complete")
    print(f"[INFO] Consistency score: {validation_summary['overall_consistency_score']:.1f}%")
    print(f"[INFO] Files checked: {validation_summary['total_files_checked']}")
    print(f"[INFO] Violations: {validation_summary['violations_found']}")
    if report_path is not None:
        print(f"[INFO] Report: {report_path}")
    if config_path is not None:
        print(f"[INFO] Config: {config_path}")

    if validation_summary["violations_found"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
