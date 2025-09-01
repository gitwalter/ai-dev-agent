#!/usr/bin/env python3
"""
Git Workflow Enforcement System
===============================

Implements automated git workflow enforcement to prevent work loss and ensure
GitHub synchronization. Integrates with @agile coordination to block operations
when git hygiene thresholds are exceeded.

Features:
- Real-time git status monitoring
- Intelligent commit message generation
- Automated blocking of development when thresholds exceeded
- Integration with agile coordination system
- Stakeholder visibility through commit tracking
"""

import os
import subprocess
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import time
import re


@dataclass
class GitWorkflowStatus:
    """Represents current git workflow status."""
    
    status: str  # CLEAN, WARNING, BLOCKED
    uncommitted_files: List[str]
    uncommitted_count: int
    unpushed_commits: List[str]
    unpushed_count: int
    last_commit_time: Optional[str]
    time_since_last_commit: Optional[int]  # minutes
    requires_commit: bool
    requires_push: bool
    blocking: bool
    recommended_actions: List[str]
    commit_message_suggestion: Optional[str]


@dataclass 
class CommitAnalysis:
    """Analysis of changes for intelligent commit message generation."""
    
    new_features: List[str]
    bug_fixes: List[str]
    documentation: List[str]
    tests: List[str]
    configuration: List[str]
    refactoring: List[str]
    other: List[str]
    commit_type: str  # feat, fix, docs, test, chore, refactor
    scope: Optional[str]
    description: str
    body: str


class GitWorkflowEnforcer:
    """Enforces git workflow compliance and prevents work accumulation."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.git_dir = self.project_root / ".git"
        
        # Configuration thresholds
        self.max_uncommitted_files = 5  # Block at >5 uncommitted files
        self.max_time_since_commit = 30  # Minutes before warning
        self.max_unpushed_commits = 3   # Warning at >3 unpushed commits
        
        # Monitoring state
        self.last_status_check = None
        self.monitoring_active = True
        
    def get_git_workflow_status(self) -> GitWorkflowStatus:
        """Get comprehensive git workflow status."""
        
        if not self._is_git_repository():
            return GitWorkflowStatus(
                status="ERROR",
                uncommitted_files=[],
                uncommitted_count=0,
                unpushed_commits=[],
                unpushed_count=0,
                last_commit_time=None,
                time_since_last_commit=None,
                requires_commit=False,
                requires_push=False,
                blocking=True,
                recommended_actions=["Initialize git repository: git init"],
                commit_message_suggestion=None
            )
        
        # Get uncommitted changes
        uncommitted_files = self._get_uncommitted_files()
        uncommitted_count = len(uncommitted_files)
        
        # Get unpushed commits
        unpushed_commits = self._get_unpushed_commits()
        unpushed_count = len(unpushed_commits)
        
        # Get last commit time
        last_commit_time, time_since_last = self._get_last_commit_info()
        
        # Determine status and requirements
        status, requires_commit, requires_push, blocking = self._analyze_workflow_status(
            uncommitted_count, unpushed_count, time_since_last
        )
        
        # Generate recommendations
        recommended_actions = self._generate_recommendations(
            uncommitted_count, unpushed_count, time_since_last
        )
        
        # Generate commit message suggestion
        commit_message_suggestion = None
        if requires_commit and uncommitted_files:
            commit_message_suggestion = self._generate_intelligent_commit_message(uncommitted_files)
        
        return GitWorkflowStatus(
            status=status,
            uncommitted_files=uncommitted_files,
            uncommitted_count=uncommitted_count,
            unpushed_commits=unpushed_commits,
            unpushed_count=unpushed_count,
            last_commit_time=last_commit_time,
            time_since_last_commit=time_since_last,
            requires_commit=requires_commit,
            requires_push=requires_push,
            blocking=blocking,
            recommended_actions=recommended_actions,
            commit_message_suggestion=commit_message_suggestion
        )
    
    def enforce_workflow_compliance(self) -> Tuple[bool, Dict]:
        """Enforce git workflow compliance. Returns (allowed_to_proceed, status_info)."""
        
        status = self.get_git_workflow_status()
        
        if status.blocking:
            return False, {
                "enforcement_result": "BLOCKED",
                "reason": f"Git workflow violation: {status.status}",
                "details": asdict(status),
                "required_actions": status.recommended_actions
            }
        
        if status.status == "WARNING":
            return True, {
                "enforcement_result": "WARNING", 
                "reason": "Git workflow concerns detected",
                "details": asdict(status),
                "recommended_actions": status.recommended_actions
            }
        
        return True, {
            "enforcement_result": "CLEAN",
            "reason": "Git workflow is clean",
            "details": asdict(status)
        }
    
    def _is_git_repository(self) -> bool:
        """Check if current directory is a git repository."""
        return self.git_dir.exists() and self.git_dir.is_dir()
    
    def _get_uncommitted_files(self) -> List[str]:
        """Get list of uncommitted files."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            uncommitted = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # Parse git status format: XY filename
                    status_code = line[:2]
                    filename = line[3:].strip()
                    uncommitted.append(f"{status_code} {filename}")
            
            return uncommitted
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return []
    
    def _get_unpushed_commits(self) -> List[str]:
        """Get list of unpushed commits."""
        try:
            # First check if we have a remote
            remote_result = subprocess.run(
                ["git", "remote"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if not remote_result.stdout.strip():
                return []  # No remote configured
            
            # Get unpushed commits
            result = subprocess.run(
                ["git", "log", "--oneline", "@{u}..HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    commits.append(line.strip())
            
            return commits
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return []
    
    def _get_last_commit_info(self) -> Tuple[Optional[str], Optional[int]]:
        """Get last commit time and minutes since."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                return None, None
            
            # Parse commit timestamp
            commit_time_str = result.stdout.strip()
            commit_time = datetime.datetime.fromisoformat(commit_time_str.replace(' ', 'T', 1))
            
            # Calculate minutes since
            now = datetime.datetime.now(commit_time.tzinfo)
            time_diff = now - commit_time
            minutes_since = int(time_diff.total_seconds() / 60)
            
            return commit_time_str, minutes_since
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError):
            return None, None
    
    def _analyze_workflow_status(self, uncommitted_count: int, unpushed_count: int, 
                               time_since_last: Optional[int]) -> Tuple[str, bool, bool, bool]:
        """Analyze workflow status and determine requirements."""
        
        requires_commit = uncommitted_count >= self.max_uncommitted_files
        requires_push = unpushed_count > self.max_unpushed_commits
        
        # Blocking conditions
        blocking = (
            uncommitted_count > self.max_uncommitted_files or
            (time_since_last and time_since_last > 60)  # 1 hour absolute limit
        )
        
        # Status determination
        if blocking:
            status = "BLOCKED"
        elif (uncommitted_count > 2 or unpushed_count > 0 or 
              (time_since_last and time_since_last > self.max_time_since_commit)):
            status = "WARNING"
        else:
            status = "CLEAN"
        
        return status, requires_commit, requires_push, blocking
    
    def _generate_recommendations(self, uncommitted_count: int, unpushed_count: int,
                                time_since_last: Optional[int]) -> List[str]:
        """Generate actionable recommendations."""
        
        recommendations = []
        
        if uncommitted_count > 0:
            recommendations.append(f"📋 Review {uncommitted_count} uncommitted files: git status")
            recommendations.append("📝 Stage changes: git add .")
            
            if uncommitted_count > self.max_uncommitted_files:
                recommendations.append("🚨 REQUIRED: Commit changes before proceeding")
                recommendations.append("💡 Use suggested commit message or write descriptive one")
            else:
                recommendations.append("💡 Consider committing current progress")
        
        if unpushed_count > 0:
            recommendations.append(f"📤 Push {unpushed_count} unpushed commits: git push")
            
            if unpushed_count > self.max_unpushed_commits:
                recommendations.append("⚠️  HIGH: Many unpushed commits - backup to GitHub")
        
        if time_since_last and time_since_last > self.max_time_since_commit:
            hours = time_since_last // 60
            minutes = time_since_last % 60
            
            if hours > 0:
                time_str = f"{hours}h {minutes}m"
            else:
                time_str = f"{minutes}m"
            
            recommendations.append(f"⏰ Last commit {time_str} ago - consider committing progress")
        
        if not recommendations:
            recommendations.append("✅ Git workflow is clean - ready for development")
        
        return recommendations
    
    def _generate_intelligent_commit_message(self, uncommitted_files: List[str]) -> str:
        """Generate intelligent commit message based on changes."""
        
        analysis = self._analyze_changes(uncommitted_files)
        
        # Build commit message
        commit_parts = []
        
        # Type and scope
        if analysis.scope:
            commit_parts.append(f"{analysis.commit_type}({analysis.scope}): {analysis.description}")
        else:
            commit_parts.append(f"{analysis.commit_type}: {analysis.description}")
        
        # Add body if significant
        if analysis.body:
            commit_parts.append("")
            commit_parts.append(analysis.body)
        
        return "\n".join(commit_parts)
    
    def _analyze_changes(self, uncommitted_files: List[str]) -> CommitAnalysis:
        """Analyze uncommitted changes to categorize and describe them."""
        
        categories = {
            'new_features': [],
            'bug_fixes': [], 
            'documentation': [],
            'tests': [],
            'configuration': [],
            'refactoring': [],
            'other': []
        }
        
        # Categorize files
        for file_line in uncommitted_files:
            if len(file_line) < 3:
                continue
            
            status_code = file_line[:2].strip()
            filename = file_line[3:].strip()
            
            # Categorize based on filename patterns
            if any(pattern in filename.lower() for pattern in ['test', 'spec']):
                categories['tests'].append(filename)
            elif filename.endswith(('.md', '.txt', '.rst', '.adoc')):
                categories['documentation'].append(filename)
            elif filename.endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.cfg')):
                categories['configuration'].append(filename)
            elif any(pattern in filename.lower() for pattern in ['fix', 'bug', 'patch']):
                categories['bug_fixes'].append(filename)
            elif status_code in ['A', 'A ']:  # New files
                categories['new_features'].append(filename)
            elif status_code in ['M', 'M ']:  # Modified files
                # Could be refactoring or features - check content if possible
                if any(pattern in filename.lower() for pattern in ['refactor', 'cleanup']):
                    categories['refactoring'].append(filename)
                else:
                    categories['new_features'].append(filename)
            else:
                categories['other'].append(filename)
        
        # Determine primary commit type
        commit_type = self._determine_commit_type(categories)
        
        # Generate description
        description = self._generate_commit_description(categories, commit_type)
        
        # Generate scope (if applicable)
        scope = self._determine_scope(categories)
        
        # Generate body
        body = self._generate_commit_body(categories)
        
        return CommitAnalysis(
            new_features=categories['new_features'],
            bug_fixes=categories['bug_fixes'],
            documentation=categories['documentation'],
            tests=categories['tests'],
            configuration=categories['configuration'],
            refactoring=categories['refactoring'],
            other=categories['other'],
            commit_type=commit_type,
            scope=scope,
            description=description,
            body=body
        )
    
    def _determine_commit_type(self, categories: Dict[str, List[str]]) -> str:
        """Determine primary commit type based on changes."""
        
        # Priority order for commit types
        if categories['bug_fixes']:
            return "fix"
        elif categories['new_features']:
            return "feat"
        elif categories['documentation']:
            return "docs"
        elif categories['tests']:
            return "test"
        elif categories['refactoring']:
            return "refactor"
        elif categories['configuration']:
            return "chore"
        else:
            return "chore"
    
    def _determine_scope(self, categories: Dict[str, List[str]]) -> Optional[str]:
        """Determine scope based on file patterns."""
        
        all_files = []
        for file_list in categories.values():
            all_files.extend(file_list)
        
        # Common scope patterns
        if any('agile' in f.lower() for f in all_files):
            return "agile"
        elif any('test' in f.lower() for f in all_files):
            return "tests"
        elif any('doc' in f.lower() for f in all_files):
            return "docs"
        elif any('api' in f.lower() for f in all_files):
            return "api"
        elif any('ui' in f.lower() or 'interface' in f.lower() for f in all_files):
            return "ui"
        elif any('config' in f.lower() for f in all_files):
            return "config"
        
        return None
    
    def _generate_commit_description(self, categories: Dict[str, List[str]], 
                                   commit_type: str) -> str:
        """Generate concise commit description."""
        
        total_files = sum(len(files) for files in categories.values())
        
        if commit_type == "feat":
            if categories['new_features']:
                primary_feature = categories['new_features'][0]
                feature_name = Path(primary_feature).stem.replace('_', ' ')
                return f"implement {feature_name}"
            return "add new functionality"
        
        elif commit_type == "fix":
            if len(categories['bug_fixes']) == 1:
                return f"resolve issue in {Path(categories['bug_fixes'][0]).stem}"
            return f"fix {len(categories['bug_fixes'])} issues"
        
        elif commit_type == "docs":
            if len(categories['documentation']) == 1:
                doc_name = Path(categories['documentation'][0]).stem.replace('_', ' ')
                return f"update {doc_name}"
            return f"update documentation ({len(categories['documentation'])} files)"
        
        elif commit_type == "test":
            return f"add/update tests ({len(categories['tests'])} files)"
        
        elif commit_type == "refactor":
            return f"refactor code structure"
        
        else:
            return f"update project files ({total_files} files)"
    
    def _generate_commit_body(self, categories: Dict[str, List[str]]) -> str:
        """Generate detailed commit body."""
        
        body_parts = []
        
        # Add details for significant categories
        if categories['new_features'] and len(categories['new_features']) > 1:
            body_parts.append(f"New features:")
            for feature in categories['new_features'][:5]:  # Limit to top 5
                feature_name = Path(feature).stem.replace('_', ' ')
                body_parts.append(f"- {feature_name}")
        
        if categories['bug_fixes']:
            body_parts.append(f"Bug fixes:")
            for fix in categories['bug_fixes']:
                fix_name = Path(fix).stem.replace('_', ' ')
                body_parts.append(f"- {fix_name}")
        
        if categories['tests']:
            body_parts.append(f"Test updates: {len(categories['tests'])} files")
        
        if categories['documentation']:
            body_parts.append(f"Documentation: {len(categories['documentation'])} files updated")
        
        return "\n".join(body_parts) if body_parts else ""


def main():
    """CLI for git workflow enforcement."""
    import sys
    
    enforcer = GitWorkflowEnforcer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        # Get and display status
        status = enforcer.get_git_workflow_status()
        print(json.dumps(asdict(status), indent=2))
    
    elif len(sys.argv) > 1 and sys.argv[1] == "enforce":
        # Enforce workflow compliance
        allowed, info = enforcer.enforce_workflow_compliance()
        print(json.dumps(info, indent=2))
        sys.exit(0 if allowed else 1)
    
    else:
        print("Usage:")
        print("  python -m utils.git.workflow_enforcer status   # Show status")
        print("  python -m utils.git.workflow_enforcer enforce  # Enforce compliance")


if __name__ == "__main__":
    main()
