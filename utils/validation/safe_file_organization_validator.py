#!/usr/bin/env python3
"""
Safe File Organization Validator

This script SAFELY validates file organization without moving any files.
It only reports issues and suggests manual fixes - NO AUTOMATIC FILE MOVING.

SAFETY PRINCIPLES:
1. NEVER move files automatically
2. ONLY report and suggest
3. Always require human approval
4. Provide clear explanations
5. Include rollback instructions
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json

class SafeFileOrganizationValidator:
    """Safe file organization validator that never moves files automatically."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues = []
        self.suggestions = []
        
        # Define safe organization rules (read-only)
        self.organization_rules = {
            "agents/": {
                "description": "AI agent implementations",
                "allowed_extensions": [".py"],
                "required_files": ["__init__.py"],
                "forbidden_patterns": ["test_", "temp_", "tmp_"]
            },
            "utils/": {
                "description": "Utility functions and helpers",
                "allowed_extensions": [".py"],
                "required_files": ["__init__.py"],
                "forbidden_patterns": ["main_", "app_"]
            },
            "tests/": {
                "description": "Test files and test utilities",
                "allowed_extensions": [".py", ".md"],
                "required_patterns": ["test_"],
                "forbidden_patterns": ["main_", "app_"]
            },
            "workflow/": {
                "description": "Workflow and process management",
                "allowed_extensions": [".py", ".md"],
                "required_files": ["__init__.py"],
                "forbidden_patterns": ["test_", "temp_"]
            },
            "docs/": {
                "description": "Documentation files",
                "allowed_extensions": [".md", ".rst", ".txt"],
                "forbidden_patterns": ["temp_", "draft_"]
            },
            "scripts/": {
                "description": "Utility scripts and automation",
                "allowed_extensions": [".py", ".sh", ".bat", ".ps1"],
                "forbidden_patterns": ["main_", "app_"]
            },
            "prompts/": {
                "description": "Prompt templates and databases",
                "allowed_extensions": [".py", ".db", ".sqlite", ".json"],
                "required_files": ["__init__.py"],
                "forbidden_patterns": ["temp_", "backup_"]
            }
        }
        
        # Files that should NEVER be in root
        self.root_forbidden_files = [
            "*.py",  # No Python files in root
            "*.md",  # No markdown files in root (except README)
            "*.json",  # No JSON files in root
            "*.yaml",  # No YAML files in root
            "*.yml",   # No YML files in root
            "*.txt",   # No text files in root
            "*.log",   # No log files in root
            "*.tmp",   # No temp files in root
            "*.temp",  # No temp files in root
        ]
        
        # Root exceptions (files that CAN be in root)
        self.root_allowed_files = [
            "README.md",
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            ".gitignore",
            ".env.example",
            "LICENSE",
            "CHANGELOG.md"
        ]

    def validate_project_structure(self) -> Dict[str, any]:
        """Validate the entire project structure and return a report."""
        
        print("🔍 SAFE FILE ORGANIZATION VALIDATION")
        print("=" * 50)
        print("⚠️  This validator NEVER moves files automatically")
        print("📋 Only reports issues and suggests manual fixes")
        print()
        
        report = {
            "timestamp": str(Path().cwd()),
            "issues": [],
            "suggestions": [],
            "summary": {}
        }
        
        # Check root directory
        root_issues = self._validate_root_directory()
        report["issues"].extend(root_issues)
        
        # Check each directory
        for directory, rules in self.organization_rules.items():
            dir_path = self.project_root / directory
            if dir_path.exists():
                dir_issues = self._validate_directory(directory, dir_path, rules)
                report["issues"].extend(dir_issues)
            else:
                report["issues"].append({
                    "type": "missing_directory",
                    "severity": "medium",
                    "location": directory,
                    "description": f"Directory '{directory}' is missing",
                    "suggestion": f"Create directory '{directory}' for {rules['description']}"
                })
        
        # Generate summary
        report["summary"] = {
            "total_issues": len(report["issues"]),
            "critical_issues": len([i for i in report["issues"] if i["severity"] == "critical"]),
            "high_issues": len([i for i in report["issues"] if i["severity"] == "high"]),
            "medium_issues": len([i for i in report["issues"] if i["severity"] == "medium"]),
            "low_issues": len([i for i in report["issues"] if i["severity"] == "low"])
        }
        
        return report

    def _validate_root_directory(self) -> List[Dict]:
        """Validate files in the root directory."""
        
        issues = []
        root_path = self.project_root
        
        for file_path in root_path.iterdir():
            if file_path.is_file():
                file_name = file_path.name
                
                # Check if file should not be in root
                if self._should_not_be_in_root(file_name):
                    issues.append({
                        "type": "file_in_wrong_location",
                        "severity": "high",
                        "location": f"root/{file_name}",
                        "description": f"File '{file_name}' should not be in root directory",
                        "suggestion": f"Move '{file_name}' to appropriate subdirectory",
                        "file_path": str(file_path)
                    })
        
        return issues

    def _validate_directory(self, dir_name: str, dir_path: Path, rules: Dict) -> List[Dict]:
        """Validate files in a specific directory."""
        
        issues = []
        
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.project_root)
                
                # Check file extension
                if "allowed_extensions" in rules:
                    if not self._has_allowed_extension(file_path, rules["allowed_extensions"]):
                        issues.append({
                            "type": "wrong_file_type",
                            "severity": "medium",
                            "location": str(relative_path),
                            "description": f"File '{file_path.name}' has wrong extension for {dir_name}/",
                            "suggestion": f"Move '{file_path.name}' to appropriate directory or change extension",
                            "file_path": str(file_path)
                        })
                
                # Check forbidden patterns
                if "forbidden_patterns" in rules:
                    if self._matches_forbidden_pattern(file_path.name, rules["forbidden_patterns"]):
                        issues.append({
                            "type": "forbidden_pattern",
                            "severity": "low",
                            "location": str(relative_path),
                            "description": f"File '{file_path.name}' matches forbidden pattern in {dir_name}/",
                            "suggestion": f"Rename '{file_path.name}' to avoid forbidden pattern",
                            "file_path": str(file_path)
                        })
        
        return issues

    def _should_not_be_in_root(self, file_name: str) -> bool:
        """Check if a file should not be in the root directory."""
        
        # Check if it's an allowed file
        if file_name in self.root_allowed_files:
            return False
        
        # Check if it matches forbidden patterns
        for pattern in self.root_forbidden_files:
            if self._matches_pattern(file_name, pattern):
                return True
        
        return False

    def _has_allowed_extension(self, file_path: Path, allowed_extensions: List[str]) -> bool:
        """Check if file has an allowed extension."""
        return file_path.suffix in allowed_extensions

    def _matches_forbidden_pattern(self, file_name: str, forbidden_patterns: List[str]) -> bool:
        """Check if file name matches any forbidden pattern."""
        return any(pattern in file_name for pattern in forbidden_patterns)

    def _matches_pattern(self, file_name: str, pattern: str) -> bool:
        """Check if file name matches a pattern."""
        if pattern.startswith("*"):
            return file_name.endswith(pattern[1:])
        return pattern in file_name

    def generate_fix_script(self, report: Dict) -> str:
        """Generate a safe fix script that requires manual review."""
        
        script_lines = [
            "#!/bin/bash",
            "# SAFE FILE ORGANIZATION FIX SCRIPT",
            "# This script was generated by the safe file organization validator",
            "# REVIEW CAREFULLY BEFORE RUNNING - NO AUTOMATIC EXECUTION",
            "#",
            "# Generated from validation report:",
            f"# - Total issues: {report['summary']['total_issues']}",
            f"# - Critical issues: {report['summary']['critical_issues']}",
            f"# - High issues: {report['summary']['high_issues']}",
            "#",
            "# MANUAL STEPS REQUIRED:",
            "# 1. Review each move command",
            "# 2. Test in a separate branch first",
            "# 3. Have a backup of your repository",
            "# 4. Run commands one by one",
            "#",
            "echo '⚠️  SAFETY WARNING: Review all commands before running!'",
            "echo '📋 This script will move files - ensure you have a backup!'",
            "echo ''",
            "read -p 'Press Enter to continue or Ctrl+C to abort...'",
            ""
        ]
        
        for issue in report["issues"]:
            if issue["type"] == "file_in_wrong_location":
                script_lines.append(f"# {issue['description']}")
                script_lines.append(f"# Suggestion: {issue['suggestion']}")
                script_lines.append(f"# mv '{issue['file_path']}' <destination>")
                script_lines.append("")
        
        script_lines.extend([
            "echo '✅ File organization fix script completed'",
            "echo '📋 Remember to:'",
            "echo '   - Test the changes'",
            "echo '   - Update imports if needed'",
            "echo '   - Commit the changes'",
            "echo '   - Push to repository'"
        ])
        
        return "\n".join(script_lines)

    def print_report(self, report: Dict):
        """Print a formatted validation report."""
        
        print(f"📊 VALIDATION SUMMARY:")
        print(f"   Total Issues: {report['summary']['total_issues']}")
        print(f"   Critical: {report['summary']['critical_issues']}")
        print(f"   High: {report['summary']['high_issues']}")
        print(f"   Medium: {report['summary']['medium_issues']}")
        print(f"   Low: {report['summary']['low_issues']}")
        print()
        
        if report["issues"]:
            print("🚨 ISSUES FOUND:")
            print("-" * 50)
            
            for i, issue in enumerate(report["issues"], 1):
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠", 
                    "medium": "🟡",
                    "low": "🟢"
                }.get(issue["severity"], "⚪")
                
                print(f"{i}. {severity_icon} {issue['severity'].upper()}: {issue['description']}")
                print(f"   📍 Location: {issue['location']}")
                print(f"   💡 Suggestion: {issue['suggestion']}")
                print()
        else:
            print("✅ No issues found! Project structure is well-organized.")
        
        print("🛡️  SAFETY REMINDER:")
        print("   - This validator NEVER moves files automatically")
        print("   - All fixes require manual review and approval")
        print("   - Always test changes in a separate branch first")

def main():
    """Main function to run the safe file organization validator."""
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python safe_file_organization_validator.py validate  - Run validation")
        print("  python safe_file_organization_validator.py report     - Generate detailed report")
        print("  python safe_file_organization_validator.py fix-script - Generate fix script")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    validator = SafeFileOrganizationValidator()
    
    if command == "validate":
        report = validator.validate_project_structure()
        validator.print_report(report)
        
        if report["summary"]["total_issues"] > 0:
            sys.exit(1)  # Exit with error if issues found
        else:
            sys.exit(0)  # Exit successfully if no issues
    
    elif command == "report":
        report = validator.validate_project_structure()
        print(json.dumps(report, indent=2))
    
    elif command == "fix-script":
        report = validator.validate_project_structure()
        fix_script = validator.generate_fix_script(report)
        
        script_path = Path("safe_file_organization_fix.sh")
        with open(script_path, "w") as f:
            f.write(fix_script)
        
        print(f"📝 Fix script generated: {script_path}")
        print("⚠️  Review the script carefully before running!")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
