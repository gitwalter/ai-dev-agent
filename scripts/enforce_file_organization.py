#!/usr/bin/env python3
"""
File Organization Enforcement Script
===================================

CRITICAL: Automatic enforcement of file organization rules.
Full focus, zero tolerance, immediate correction.
"""

import os
import shutil
import glob
from pathlib import Path
from typing import List, Dict, Tuple

class FileOrganizationEnforcer:
    """Full enforcement of file organization standards."""
    
    def __init__(self):
        self.violations = []
        self.fixes_applied = []
        
    def enforce_all(self) -> None:
        """Execute full enforcement scan and fix."""
        print("🔒 FULL ENFORCEMENT ACTIVE")
        
        # 1. Scan for violations
        self._scan_violations()
        
        # 2. Apply automatic fixes
        self._apply_fixes()
        
        # 3. Report results
        self._report_enforcement()
        
    def _scan_violations(self) -> None:
        """Scan for all file organization violations."""
        
        # Check root-level example files
        root_examples = glob.glob("example_*.py")
        for file in root_examples:
            self.violations.append({
                "type": "misplaced_example",
                "file": file,
                "should_be": f"examples/{file.replace('example_', '').replace('.py', '')}/{file}"
            })
        
        # Check root-level gem files  
        root_gems = glob.glob("gem_*.py")
        for file in root_gems:
            self.violations.append({
                "type": "misplaced_gem", 
                "file": file,
                "should_be": f"examples/community_gems/{file.replace('gem_', '').replace('.py', '')}/{file}"
            })
            
        # Check for empty files
        for pattern in ["*.py", "*.md", "*.txt"]:
            for file in glob.glob(f"**/{pattern}", recursive=True):
                if os.path.getsize(file) == 0:
                    self.violations.append({
                        "type": "empty_file",
                        "file": file,
                        "should_be": "DELETED"
                    })
    
    def _apply_fixes(self) -> None:
        """Apply automatic fixes for violations."""
        
        for violation in self.violations:
            try:
                if violation["type"] == "misplaced_example":
                    self._fix_misplaced_example(violation)
                elif violation["type"] == "misplaced_gem":
                    self._fix_misplaced_gem(violation)
                elif violation["type"] == "empty_file":
                    self._fix_empty_file(violation)
                    
                self.fixes_applied.append(violation)
                
            except Exception as e:
                print(f"❌ Failed to fix {violation['file']}: {e}")
    
    def _fix_misplaced_example(self, violation: Dict) -> None:
        """Fix misplaced example file."""
        source = violation["file"]
        target_dir = os.path.dirname(violation["should_be"])
        
        # Create target directory structure
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(f"{target_dir}/src", exist_ok=True)
        os.makedirs(f"{target_dir}/tests", exist_ok=True)
        os.makedirs(f"{target_dir}/docs", exist_ok=True)
        
        # Move file to src directory
        target_file = f"{target_dir}/src/{os.path.basename(source)}"
        shutil.move(source, target_file)
        
        # Create basic structure files
        self._create_basic_structure(target_dir, os.path.basename(source))
        
        print(f"📁 Moved {source} → {target_file}")
    
    def _fix_misplaced_gem(self, violation: Dict) -> None:
        """Fix misplaced gem file."""
        source = violation["file"]
        target_dir = os.path.dirname(violation["should_be"])
        
        # Create gem directory structure
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(f"{target_dir}/src", exist_ok=True)
        os.makedirs(f"{target_dir}/tests", exist_ok=True)
        os.makedirs(f"{target_dir}/docs", exist_ok=True)
        os.makedirs(f"{target_dir}/agile", exist_ok=True)
        
        # Move file to src directory
        target_file = f"{target_dir}/src/{os.path.basename(source)}"
        shutil.move(source, target_file)
        
        # Create gem structure
        self._create_gem_structure(target_dir, os.path.basename(source))
        
        print(f"💎 Organized gem {source} → {target_file}")
    
    def _fix_empty_file(self, violation: Dict) -> None:
        """Delete empty file."""
        os.remove(violation["file"])
        print(f"🗑️ Deleted empty file: {violation['file']}")
    
    def _create_basic_structure(self, target_dir: str, filename: str) -> None:
        """Create basic project structure."""
        
        # README.md
        with open(f"{target_dir}/README.md", "w") as f:
            f.write(f"# {filename.replace('.py', '').replace('_', ' ').title()}\n\n")
            f.write("## Quick Start\n\n")
            f.write(f"```bash\npython src/{filename}\n```\n")
        
        # requirements.txt
        with open(f"{target_dir}/requirements.txt", "w") as f:
            f.write("# Dependencies\n")
    
    def _create_gem_structure(self, target_dir: str, filename: str) -> None:
        """Create complete gem structure."""
        
        gem_name = filename.replace('gem_', '').replace('.py', '')
        
        # README.md
        with open(f"{target_dir}/README.md", "w") as f:
            f.write(f"# {gem_name.replace('_', ' ').title()} - Community Gem\n\n")
            f.write("Production-ready component for AI-Dev-Agent system.\n\n")
            f.write("## Quick Start\n\n")
            f.write(f"```bash\npython src/{filename}\n```\n")
        
        # Basic user story
        os.makedirs(f"{target_dir}/agile/user_stories", exist_ok=True)
        with open(f"{target_dir}/agile/user_stories/US-{gem_name.upper()}-001.md", "w") as f:
            f.write(f"# User Story: {gem_name.replace('_', ' ').title()}\n\n")
            f.write("**As a** developer\n")
            f.write("**I want** to use this gem\n") 
            f.write("**So that** I can build better software\n")
    
    def _report_enforcement(self) -> None:
        """Report enforcement results."""
        
        print(f"\n🔒 ENFORCEMENT COMPLETE")
        print(f"   Violations Found: {len(self.violations)}")
        print(f"   Fixes Applied: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            print(f"\n✅ FIXES APPLIED:")
            for fix in self.fixes_applied:
                print(f"   - {fix['type']}: {fix['file']}")
        
        remaining = len(self.violations) - len(self.fixes_applied)
        if remaining > 0:
            print(f"\n⚠️ {remaining} violations require manual attention")
        else:
            print(f"\n🎯 ALL VIOLATIONS CORRECTED")

def main():
    """Execute file organization enforcement."""
    enforcer = FileOrganizationEnforcer()
    enforcer.enforce_all()

if __name__ == "__main__":
    main()
