"""
Automatic File Organization Enforcer - Sacred Rule Implementation
================================================================

CRITICAL: This module implements automatic file organization enforcement for ALL agents
to prevent violations of our SACRED file organization rule. This is a core system
component that ensures file placement excellence.

Created: 2025-01-31
Priority: CRITICAL (Sacred Rule Enforcement)
Purpose: Prevent file organization violations across all agent operations
"""

import os
import shutil
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileCategory(Enum):
    """File categories for organization."""
    AGENT = "agents"
    UTIL = "utils"
    TEST = "tests"
    SCRIPT = "scripts"
    APP = "apps"
    MODEL = "models"
    WORKFLOW = "workflow"
    CONTEXT = "context"
    PROMPT = "prompts"
    DOC = "docs"
    LOG = "logs"
    MONITORING = "monitoring"
    UI = "ui"
    TOOL = "tools"
    CONFIG = "."  # Root level configs only
    TEMP = "temp"
    GENERATED = "generated_projects"
    BACKUP = "backups"


@dataclass
class FileOrganizationRule:
    """Rule for file organization."""
    pattern: str
    category: FileCategory
    subcategory: Optional[str] = None
    description: str = ""


class FileOrganizationEnforcer:
    """
    @file_organization_enforcer: Automatic enforcement of sacred file organization rules.
    
    This class ensures that ALL files are placed in their correct locations
    automatically, preventing any violations of our sacred file organization rule.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.violations_detected = []
        self.corrections_made = []
        
        # Load file organization rules
        self.rules = self._initialize_organization_rules()
        
        logger.info(f"🗂️ File Organization Enforcer initialized for {self.project_root}")
    
    def _initialize_organization_rules(self) -> List[FileOrganizationRule]:
        """Initialize comprehensive file organization rules."""
        return [
            # Agent files
            FileOrganizationRule(
                pattern=r".*_agent\.py$",
                category=FileCategory.AGENT,
                description="AI agent implementation files"
            ),
            FileOrganizationRule(
                pattern=r".*_team\.py$",
                category=FileCategory.AGENT,
                description="Agent team implementation files"
            ),
            FileOrganizationRule(
                pattern=r".*agent.*\.py$",
                category=FileCategory.AGENT,
                description="Agent-related files"
            ),
            
            # Test files - CRITICAL: These must NEVER be in root
            FileOrganizationRule(
                pattern=r"test_.*\.py$",
                category=FileCategory.TEST,
                description="Test files - SACRED: Never in root!"
            ),
            FileOrganizationRule(
                pattern=r".*_test\.py$",
                category=FileCategory.TEST,
                description="Test files - SACRED: Never in root!"
            ),
            FileOrganizationRule(
                pattern=r".*test.*\.py$",
                category=FileCategory.TEST,
                description="Test-related files - SACRED: Never in root!"
            ),
            
            # Utility files
            FileOrganizationRule(
                pattern=r".*_util.*\.py$",
                category=FileCategory.UTIL,
                description="Utility implementation files"
            ),
            FileOrganizationRule(
                pattern=r".*helper.*\.py$",
                category=FileCategory.UTIL,
                description="Helper utility files"
            ),
            FileOrganizationRule(
                pattern=r".*_tools?\.py$",
                category=FileCategory.UTIL,
                description="Tool utility files"
            ),
            
            # Script files
            FileOrganizationRule(
                pattern=r".*_script\.py$",
                category=FileCategory.SCRIPT,
                description="Script files"
            ),
            FileOrganizationRule(
                pattern=r"run_.*\.py$",
                category=FileCategory.SCRIPT,
                description="Executable script files"
            ),
            FileOrganizationRule(
                pattern=r"setup.*\.py$",
                category=FileCategory.SCRIPT,
                description="Setup script files"
            ),
            
            # App files
            FileOrganizationRule(
                pattern=r".*_app\.py$",
                category=FileCategory.APP,
                description="Application files"
            ),
            FileOrganizationRule(
                pattern=r"streamlit.*\.py$",
                category=FileCategory.APP,
                description="Streamlit application files"
            ),
            FileOrganizationRule(
                pattern=r"main\.py$",
                category=FileCategory.APP,
                description="Main application entry points"
            ),
            
            # Model files
            FileOrganizationRule(
                pattern=r".*_model\.py$",
                category=FileCategory.MODEL,
                description="Model definition files"
            ),
            FileOrganizationRule(
                pattern=r".*model.*\.py$",
                category=FileCategory.MODEL,
                description="Model-related files"
            ),
            
            # Workflow files
            FileOrganizationRule(
                pattern=r".*workflow.*\.py$",
                category=FileCategory.WORKFLOW,
                description="Workflow implementation files"
            ),
            FileOrganizationRule(
                pattern=r".*_workflow\.py$",
                category=FileCategory.WORKFLOW,
                description="Workflow files"
            ),
            
            # Context files
            FileOrganizationRule(
                pattern=r".*context.*\.py$",
                category=FileCategory.CONTEXT,
                description="Context management files"
            ),
            
            # Prompt files
            FileOrganizationRule(
                pattern=r".*prompt.*\.py$",
                category=FileCategory.PROMPT,
                description="Prompt management files"
            ),
            
            # UI files
            FileOrganizationRule(
                pattern=r".*_ui\.py$",
                category=FileCategory.UI,
                description="User interface files"
            ),
            FileOrganizationRule(
                pattern=r".*interface.*\.py$",
                category=FileCategory.UI,
                description="Interface files"
            ),
            
            # Documentation files
            FileOrganizationRule(
                pattern=r".*\.md$",
                category=FileCategory.DOC,
                description="Documentation files"
            ),
            
            # Log files
            FileOrganizationRule(
                pattern=r".*\.log$",
                category=FileCategory.LOG,
                description="Log files"
            ),
            
            # Monitoring files
            FileOrganizationRule(
                pattern=r".*monitor.*\.py$",
                category=FileCategory.MONITORING,
                description="Monitoring files"
            ),
            FileOrganizationRule(
                pattern=r".*health.*\.py$",
                category=FileCategory.MONITORING,
                description="Health monitoring files"
            ),
            
            # Config files (allowed in root)
            FileOrganizationRule(
                pattern=r"requirements\.txt$",
                category=FileCategory.CONFIG,
                description="Requirements file - allowed in root"
            ),
            FileOrganizationRule(
                pattern=r"README\.md$",
                category=FileCategory.CONFIG,
                description="README file - allowed in root"
            ),
            FileOrganizationRule(
                pattern=r"\..*",
                category=FileCategory.CONFIG,
                description="Hidden config files - allowed in root"
            ),
        ]
    
    def scan_for_violations(self) -> List[Dict[str, Any]]:
        """Scan project for file organization violations."""
        violations = []
        
        # Scan root directory for misplaced files
        for file_path in self.project_root.iterdir():
            if file_path.is_file():
                violation = self._check_file_placement(file_path)
                if violation:
                    violations.append(violation)
        
        self.violations_detected = violations
        return violations
    
    def _check_file_placement(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Check if a file is in the correct location."""
        file_name = file_path.name
        current_location = file_path.parent.relative_to(self.project_root)
        
        # Find matching rule
        for rule in self.rules:
            if re.match(rule.pattern, file_name, re.IGNORECASE):
                correct_category = rule.category.value
                
                # Check if file is in correct location
                if str(current_location) != correct_category and current_location != Path("."):
                    continue  # File is already in correct subdirectory
                elif str(current_location) == correct_category:
                    continue  # File is correctly placed
                elif current_location == Path(".") and correct_category == ".":
                    continue  # Config file correctly in root
                elif current_location == Path(".") and correct_category != ".":
                    # File is in root but should be in subdirectory
                    return {
                        "file": str(file_path),
                        "current_location": str(current_location),
                        "correct_location": correct_category,
                        "rule": rule.description,
                        "severity": "CRITICAL" if "test" in file_name.lower() else "HIGH"
                    }
        
        # If no rule matches and file is in root, it might be misplaced
        if current_location == Path(".") and not file_name.startswith(".") and file_name.endswith(".py"):
            return {
                "file": str(file_path),
                "current_location": str(current_location),
                "correct_location": "UNKNOWN - needs manual review",
                "rule": "Unknown Python file in root directory",
                "severity": "MEDIUM"
            }
        
        return None
    
    def auto_fix_violations(self, dry_run: bool = True) -> List[Dict[str, Any]]:
        """Automatically fix file organization violations."""
        violations = self.scan_for_violations()
        corrections = []
        
        for violation in violations:
            if violation["correct_location"] == "UNKNOWN - needs manual review":
                continue  # Skip unknown files
            
            correction = self._fix_violation(violation, dry_run)
            if correction:
                corrections.append(correction)
        
        self.corrections_made = corrections
        return corrections
    
    def _fix_violation(self, violation: Dict[str, Any], dry_run: bool) -> Optional[Dict[str, Any]]:
        """Fix a single file organization violation."""
        source_path = Path(violation["file"])
        target_dir = self.project_root / violation["correct_location"]
        target_path = target_dir / source_path.name
        
        # Ensure target directory exists
        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
        
        correction = {
            "source": str(source_path),
            "target": str(target_path),
            "action": "move",
            "severity": violation["severity"],
            "dry_run": dry_run
        }
        
        if not dry_run:
            try:
                shutil.move(str(source_path), str(target_path))
                logger.info(f"✅ Moved {source_path.name} to {violation['correct_location']}/")
                correction["status"] = "SUCCESS"
            except Exception as e:
                logger.error(f"❌ Failed to move {source_path.name}: {e}")
                correction["status"] = "FAILED"
                correction["error"] = str(e)
        else:
            logger.info(f"🔍 Would move {source_path.name} to {violation['correct_location']}/")
            correction["status"] = "SIMULATED"
        
        return correction
    
    def enforce_on_file_creation(self, file_path: str, content: str = None) -> str:
        """Enforce organization when creating a new file."""
        original_path = Path(file_path)
        
        # Check if file should be in a different location
        violation = self._check_file_placement(original_path)
        if violation and violation["correct_location"] != "UNKNOWN - needs manual review":
            # Calculate correct path
            correct_dir = self.project_root / violation["correct_location"]
            correct_path = correct_dir / original_path.name
            
            # Ensure directory exists
            correct_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"🗂️ Auto-organizing: {original_path.name} → {violation['correct_location']}/")
            return str(correct_path)
        
        return file_path
    
    def generate_enforcement_report(self) -> Dict[str, Any]:
        """Generate comprehensive enforcement report."""
        violations = self.scan_for_violations()
        
        report = {
            "timestamp": "2025-01-31",
            "project_root": str(self.project_root),
            "total_violations": len(violations),
            "critical_violations": len([v for v in violations if v["severity"] == "CRITICAL"]),
            "violations_by_severity": {
                "CRITICAL": [v for v in violations if v["severity"] == "CRITICAL"],
                "HIGH": [v for v in violations if v["severity"] == "HIGH"],
                "MEDIUM": [v for v in violations if v["severity"] == "MEDIUM"]
            },
            "rules_total": len(self.rules),
            "enforcement_status": "ACTIVE" if violations else "COMPLIANT"
        }
        
        return report
    
    def create_pre_commit_hook(self) -> str:
        """Create pre-commit hook to prevent violations."""
        hook_content = '''#!/usr/bin/env python3
"""
Pre-commit hook to enforce file organization rules.
CRITICAL: Prevents violations of sacred file organization rule.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_organization_enforcer import FileOrganizationEnforcer

def main():
    enforcer = FileOrganizationEnforcer()
    violations = enforcer.scan_for_violations()
    
    if violations:
        print("🚨 CRITICAL: File organization violations detected!")
        print("Sacred file organization rule violations must be fixed before commit:")
        
        for violation in violations:
            print(f"  ❌ {violation['file']} should be in {violation['correct_location']}/")
        
        print("\\nRun: python -m utils.file_organization_enforcer --fix")
        return 1
    
    print("✅ File organization compliance verified")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
        
        hook_path = self.project_root / ".git" / "hooks" / "pre-commit"
        
        # Create hooks directory if it doesn't exist
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write hook
        with open(hook_path, "w") as f:
            f.write(hook_content)
        
        # Make executable (on Unix systems)
        if os.name != 'nt':
            os.chmod(hook_path, 0o755)
        
        return str(hook_path)


def enforce_file_organization(file_path: str, content: str = None) -> str:
    """
    Global function to enforce file organization for ANY file creation.
    This should be called by ALL agents before creating files.
    """
    enforcer = FileOrganizationEnforcer()
    return enforcer.enforce_on_file_creation(file_path, content)


def scan_and_fix_violations(dry_run: bool = True) -> Dict[str, Any]:
    """
    Scan for and fix file organization violations.
    Use dry_run=False to actually move files.
    """
    enforcer = FileOrganizationEnforcer()
    
    # Scan for violations
    violations = enforcer.scan_for_violations()
    
    # Fix violations
    corrections = enforcer.auto_fix_violations(dry_run=dry_run)
    
    # Generate report
    report = enforcer.generate_enforcement_report()
    report["corrections_made"] = corrections
    
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="File Organization Enforcer")
    parser.add_argument("--scan", action="store_true", help="Scan for violations")
    parser.add_argument("--fix", action="store_true", help="Fix violations")
    parser.add_argument("--dry-run", action="store_true", help="Simulate fixes without moving files")
    parser.add_argument("--create-hook", action="store_true", help="Create pre-commit hook")
    
    args = parser.parse_args()
    
    enforcer = FileOrganizationEnforcer()
    
    if args.create_hook:
        hook_path = enforcer.create_pre_commit_hook()
        print(f"✅ Pre-commit hook created: {hook_path}")
    
    if args.scan or args.fix:
        report = scan_and_fix_violations(dry_run=args.dry_run or not args.fix)
        
        print(f"📊 File Organization Report:")
        print(f"   Total violations: {report['total_violations']}")
        print(f"   Critical violations: {report['critical_violations']}")
        print(f"   Status: {report['enforcement_status']}")
        
        if report['total_violations'] > 0:
            print(f"\\n🚨 Violations found:")
            for severity, violations in report['violations_by_severity'].items():
                if violations:
                    print(f"   {severity}: {len(violations)} violations")
                    for violation in violations:
                        print(f"     ❌ {violation['file']} → should be in {violation['correct_location']}/")
        
        if args.fix and not args.dry_run:
            print(f"\\n✅ Corrections made: {len(report.get('corrections_made', []))}")
