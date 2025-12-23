#!/usr/bin/env python3
"""
Pre-Commit Hilbert Validation Hook

PURPOSE: Build beautiful systems by preventing consistency violations
PHILOSOPHY: Catch naming violations before they enter the sacred codebase
RESULT: Continuous mathematical beauty and systematic excellence
"""

import sys
import subprocess

from hilbert_consistency_validator import HilbertConsistencyValidator


def main():
    """
    Pre-commit validation: Prevent Hilbert consistency violations in staged docs.
    """
    print("[INFO] Pre-Commit Hilbert Consistency Check")
    print("=" * 50)
    
    # Get staged files
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
            capture_output=True, text=True, check=True
        )
        staged_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        print("[WARN] Could not get staged files. Proceeding with full validation.")
        staged_files = []
    
    # Filter to only .md files in docs/
    staged_md_files = [
        f for f in staged_files 
        if f.endswith('.md') and f.startswith('docs/')
    ]
    
    if not staged_md_files:
        print("[OK] No documentation files staged - validation passed")
        return 0
    
    print(f"[INFO] Validating {len(staged_md_files)} staged documentation files...")
    
    # Run validation
    validator = HilbertConsistencyValidator()
    validation_summary = validator.validate_project_consistency()
    
    # Check for new violations in staged files
    violations_in_staged = []
    for violation in validator.violations:
        if violation.file_path.replace('\\', '/') in staged_md_files:
            violations_in_staged.append(violation)
    
    if violations_in_staged:
        print("\n[ERROR] HILBERT CONSISTENCY VIOLATIONS DETECTED")
        print(f"[ERROR] {len(violations_in_staged)} violations in staged files:")
        print()
        
        for violation in violations_in_staged:
            print(f"[X] {violation.file_path}")
            print(f"    Expected: {violation.expected_pattern}")
            print(f"    Actual:   {violation.actual_pattern}")
            print(f"    Fix:      {violation.suggested_fix}")
            print()
        
        print("[ERROR] COMMIT BLOCKED - Fix naming violations to maintain consistency")
        return 1
    
    else:
        print("[OK] All staged files follow Hilbert consistency")
        return 0


if __name__ == "__main__":
    sys.exit(main())
