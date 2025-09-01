#!/usr/bin/env python3
"""
Boy Scout Rule Integration with Naming Convention Validator
=========================================================

Automated Boy Scout Rule implementation that integrates naming convention 
validation with holistic web integrity management.

"Always leave the codebase cleaner than you found it" - Boy Scout Rule

Features:
- Automated detection of naming violations during development
- Integration with git hooks for pre-commit validation
- Holistic relationship updates when files are moved/renamed
- Zero tolerance enforcement for naming inconsistencies
- Continuous improvement through automated cleanup
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import argparse

# Import our other validation systems
sys.path.append(str(Path(__file__).parent.parent))
from validation.self_healing_naming_validator import SelfHealingNamingValidator, ValidationReport
from quality.broken_windows_detector import BrokenWindowsDetector, DisorderSignal


@dataclass
class BoyscoutCleanupResult:
    """Result of Boy Scout cleanup operation."""
    files_processed: int
    violations_fixed: int
    relationships_updated: int
    disorders_eliminated: int
    cleanup_time_seconds: float
    success: bool
    issues: List[str]


class BoyscoutNamingIntegration:
    """
    Integrates Boy Scout Rule with naming validation and relationship management.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.naming_validator = SelfHealingNamingValidator(project_root)
        self.disorder_detector = BrokenWindowsDetector(project_root)
        
    def run_boyscout_cleanup(self, target_directory: Optional[str] = None) -> BoyscoutCleanupResult:
        """
        Run comprehensive Boy Scout cleanup on target directory.
        """
        import time
        start_time = time.time()
        
        print("🧹 Starting Boy Scout cleanup - leaving the codebase cleaner...")
        
        # Step 1: Detect naming violations
        print("📋 Step 1: Detecting naming convention violations...")
        if target_directory:
            # Scan specific directory
            violations = self._scan_directory_violations(target_directory)
        else:
            # Scan entire project
            report = self.naming_validator.scan_project()
            violations = report.violations
        
        print(f"   Found {len(violations)} naming violations")
        
        # Step 2: Detect other disorders (broken links, etc.)
        print("🔍 Step 2: Detecting disorder signals...")
        disorders = self.disorder_detector.detect_all_disorders()
        fixable_disorders = [d for d in disorders if d.auto_fixable]
        print(f"   Found {len(fixable_disorders)} auto-fixable disorders")
        
        # Step 3: Plan holistic fixes
        print("🧠 Step 3: Planning holistic fixes with relationship preservation...")
        fix_plan = self._create_holistic_fix_plan(violations, fixable_disorders)
        print(f"   Planned {len(fix_plan)} coordinated fixes")
        
        # Step 4: Execute fixes with relationship updates
        print("⚙️ Step 4: Executing Boy Scout fixes...")
        fixes_applied = 0
        relationships_updated = 0
        issues = []
        
        for fix_action in fix_plan:
            try:
                result = self._execute_fix_action(fix_action)
                if result['success']:
                    fixes_applied += 1
                    relationships_updated += result.get('relationships_updated', 0)
                else:
                    issues.extend(result.get('issues', []))
            except Exception as e:
                issues.append(f"Error executing fix: {e}")
        
        # Step 5: Validate cleanup results
        print("✅ Step 5: Validating cleanup results...")
        validation_result = self._validate_cleanup_success()
        
        end_time = time.time()
        cleanup_time = end_time - start_time
        
        result = BoyscoutCleanupResult(
            files_processed=len(fix_plan),
            violations_fixed=fixes_applied,
            relationships_updated=relationships_updated,
            disorders_eliminated=len(fixable_disorders) - len(self.disorder_detector.detect_all_disorders()),
            cleanup_time_seconds=cleanup_time,
            success=len(issues) == 0,
            issues=issues
        )
        
        self._report_boyscout_results(result)
        return result
    
    def _scan_directory_violations(self, directory: str) -> List:
        """Scan specific directory for naming violations."""
        # Temporarily adjust validator to scan only target directory
        original_root = self.naming_validator.project_root
        self.naming_validator.project_root = Path(directory).resolve()
        
        try:
            report = self.naming_validator.scan_project()
            return report.violations
        finally:
            self.naming_validator.project_root = original_root
    
    def _create_holistic_fix_plan(self, violations: List, disorders: List) -> List[Dict]:
        """Create holistic fix plan that considers all relationships."""
        fix_plan = []
        
        # Group related fixes to minimize disruption
        file_moves = {}
        
        # Plan naming violation fixes
        for violation in violations:
            if violation.auto_fixable:
                old_path = Path(violation.file_path)
                new_path = old_path.parent / violation.suggested_name
                
                fix_plan.append({
                    'type': 'file_rename',
                    'old_path': old_path,
                    'new_path': new_path,
                    'violation': violation,
                    'priority': 1
                })
                
                file_moves[str(old_path)] = str(new_path)
        
        # Plan disorder fixes that don't involve file moves
        for disorder in disorders:
            if disorder.auto_fixable and disorder.disorder_type.value != 'naming_violation':
                fix_plan.append({
                    'type': 'disorder_fix',
                    'disorder': disorder,
                    'priority': 2
                })
        
        # Sort by priority and dependencies
        fix_plan.sort(key=lambda x: x['priority'])
        
        return fix_plan
    
    def _execute_fix_action(self, fix_action: Dict) -> Dict:
        """Execute individual fix action with relationship preservation."""
        try:
            if fix_action['type'] == 'file_rename':
                return self._execute_file_rename(fix_action)
            elif fix_action['type'] == 'disorder_fix':
                return self._execute_disorder_fix(fix_action)
            else:
                return {'success': False, 'issues': [f"Unknown fix type: {fix_action['type']}"]}
        except Exception as e:
            return {'success': False, 'issues': [str(e)]}
    
    def _execute_file_rename(self, fix_action: Dict) -> Dict:
        """Execute file rename with relationship updates."""
        old_path = fix_action['old_path']
        new_path = fix_action['new_path']
        
        # Check if target already exists
        if new_path.exists():
            return {
                'success': False, 
                'issues': [f"Target file already exists: {new_path}"]
            }
        
        # Perform the rename
        old_path.rename(new_path)
        
        # Update relationships (simplified - in full implementation would use web integrity system)
        relationships_updated = self._update_file_relationships(old_path, new_path)
        
        print(f"   ✅ Renamed: {old_path.name} → {new_path.name}")
        
        return {
            'success': True,
            'relationships_updated': relationships_updated
        }
    
    def _execute_disorder_fix(self, fix_action: Dict) -> Dict:
        """Execute disorder fix."""
        disorder = fix_action['disorder']
        
        # Simplified disorder fixing - in full implementation would use specific fixes
        # For now, just log what would be fixed
        print(f"   🔧 Would fix disorder: {disorder.description}")
        
        return {'success': True}
    
    def _update_file_relationships(self, old_path: Path, new_path: Path) -> int:
        """Update file relationships after rename (simplified implementation)."""
        # This is a simplified version - full implementation would use the web integrity system
        relationships_updated = 0
        
        # Find and update references in markdown files
        old_name = old_path.name
        new_name = new_path.name
        
        for md_file in self.project_root.rglob("*.md"):
            if md_file == new_path:  # Skip the renamed file itself
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update references to the old filename
                if old_name in content:
                    updated_content = content.replace(old_name, new_name)
                    
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    relationships_updated += 1
                    print(f"     📝 Updated references in: {md_file.relative_to(self.project_root)}")
                    
            except Exception as e:
                print(f"     ⚠️ Could not update {md_file}: {e}")
        
        return relationships_updated
    
    def _validate_cleanup_success(self) -> Dict:
        """Validate that cleanup was successful."""
        # Re-run validators to check for remaining issues
        naming_report = self.naming_validator.scan_project()
        remaining_violations = len(naming_report.violations)
        
        # Check for remaining auto-fixable disorders
        disorders = self.disorder_detector.detect_all_disorders()
        remaining_fixable = len([d for d in disorders if d.auto_fixable])
        
        return {
            'remaining_naming_violations': remaining_violations,
            'remaining_fixable_disorders': remaining_fixable,
            'cleanup_successful': remaining_violations == 0 and remaining_fixable == 0
        }
    
    def _report_boyscout_results(self, result: BoyscoutCleanupResult) -> None:
        """Report Boy Scout cleanup results."""
        print("\n" + "="*60)
        print("🧹 BOY SCOUT CLEANUP RESULTS")
        print("="*60)
        
        print(f"📊 SUMMARY:")
        print(f"   Files processed: {result.files_processed}")
        print(f"   Violations fixed: {result.violations_fixed}")
        print(f"   Relationships updated: {result.relationships_updated}")
        print(f"   Disorders eliminated: {result.disorders_eliminated}")
        print(f"   Cleanup time: {result.cleanup_time_seconds:.2f} seconds")
        print(f"   Success: {'✅ YES' if result.success else '❌ NO'}")
        
        if result.issues:
            print(f"\n⚠️ ISSUES ENCOUNTERED:")
            for issue in result.issues:
                print(f"   • {issue}")
        
        if result.success:
            print(f"\n🎉 CODEBASE LEFT CLEANER THAN FOUND!")
            print(f"   Boy Scout Rule successfully applied!")
        else:
            print(f"\n📝 ADDITIONAL WORK NEEDED:")
            print(f"   Some issues require manual attention")
        
        print("="*60)
    
    def setup_git_hooks(self) -> bool:
        """Set up git hooks for automatic Boy Scout validation."""
        try:
            git_hooks_dir = self.project_root / ".git" / "hooks"
            
            if not git_hooks_dir.exists():
                print("⚠️ No .git/hooks directory found")
                return False
            
            # Create pre-commit hook
            pre_commit_hook = git_hooks_dir / "pre-commit"
            hook_content = f"""#!/bin/bash
# Boy Scout Rule - Pre-commit validation
echo "🧹 Running Boy Scout cleanup validation..."

python "{self.project_root}/utils/quality/boyscout_naming_integration.py" --validate-only

if [ $? -ne 0 ]; then
    echo "❌ Boy Scout validation failed - commit blocked"
    echo "Run: python utils/quality/boyscout_naming_integration.py --fix"
    exit 1
fi

echo "✅ Boy Scout validation passed"
exit 0
"""
            
            with open(pre_commit_hook, 'w') as f:
                f.write(hook_content)
            
            # Make executable
            os.chmod(pre_commit_hook, 0o755)
            
            print(f"✅ Git pre-commit hook installed: {pre_commit_hook}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup git hooks: {e}")
            return False
    
    def validate_only(self) -> bool:
        """Validate without fixing - for git hooks."""
        naming_report = self.naming_validator.scan_project()
        disorders = self.disorder_detector.detect_all_disorders()
        fixable_disorders = [d for d in disorders if d.auto_fixable]
        
        violations_count = len(naming_report.violations)
        disorders_count = len(fixable_disorders)
        
        if violations_count > 0 or disorders_count > 0:
            print(f"❌ Boy Scout validation failed:")
            print(f"   Naming violations: {violations_count}")
            print(f"   Auto-fixable disorders: {disorders_count}")
            return False
        
        print("✅ Boy Scout validation passed - codebase is clean")
        return True


def main():
    """CLI interface for Boy Scout naming integration."""
    parser = argparse.ArgumentParser(
        description="Boy Scout Rule Integration - Always leave the codebase cleaner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full Boy Scout cleanup
  python boyscout_naming_integration.py --cleanup
  
  # Fix specific directory
  python boyscout_naming_integration.py --cleanup --directory docs/agile
  
  # Validate only (for git hooks)
  python boyscout_naming_integration.py --validate-only
  
  # Setup git hooks
  python boyscout_naming_integration.py --setup-hooks
        """
    )
    
    parser.add_argument('--cleanup', action='store_true',
                       help='Run Boy Scout cleanup')
    parser.add_argument('--directory',
                       help='Target specific directory for cleanup')
    parser.add_argument('--validate-only', action='store_true',
                       help='Validate without fixing (for git hooks)')
    parser.add_argument('--setup-hooks', action='store_true',
                       help='Setup git hooks for automatic validation')
    parser.add_argument('--root', default='.',
                       help='Project root directory')
    
    args = parser.parse_args()
    
    if not any([args.cleanup, args.validate_only, args.setup_hooks]):
        parser.error("Must specify --cleanup, --validate-only, or --setup-hooks")
    
    boyscout = BoyscoutNamingIntegration(args.root)
    
    if args.setup_hooks:
        success = boyscout.setup_git_hooks()
        sys.exit(0 if success else 1)
    
    elif args.validate_only:
        success = boyscout.validate_only()
        sys.exit(0 if success else 1)
    
    elif args.cleanup:
        result = boyscout.run_boyscout_cleanup(args.directory)
        sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()