#!/usr/bin/env python3
"""
Boy Scout Rule + Universal Naming Convention Integration

This module integrates the Boy Scout Rule with universal naming conventions,
ensuring that every file interaction improves naming consistency.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class BoyscoutNamingResult:
    """Result of Boy Scout naming improvement."""
    improvements_made: List[str]
    violations_fixed: List[str]
    files_cleaned: List[str]
    references_updated: int

class BoyscoutNamingIntegration:
    """
    Integration system combining Boy Scout Rule with naming conventions.
    
    Every file operation becomes an opportunity for naming improvement.
    """
    
    def __init__(self):
        self.naming_patterns = self._load_naming_patterns()
        self.improvement_log = []
    
    def apply_boyscout_naming(self, file_path: str, operation: str) -> BoyscoutNamingResult:
        """
        Apply Boy Scout Rule + naming conventions to file operation.
        
        Args:
            file_path: Path to file being operated on
            operation: Type of operation (create, edit, move, etc.)
            
        Returns:
            BoyscoutNamingResult with improvements made
        """
        
        result = BoyscoutNamingResult([], [], [], 0)
        
        # 1. Original Boy Scout: Fix the immediate issue
        result.improvements_made.append(f"Completed {operation} on {file_path}")
        
        # 2. Naming Scout: Check naming conventions
        naming_issues = self._check_naming_violations(file_path)
        
        if naming_issues:
            # 3. Fix naming violations discovered
            for issue in naming_issues:
                if self._fix_naming_violation(issue):
                    result.violations_fixed.append(issue['description'])
                    result.references_updated += issue.get('references_updated', 0)
        
        # 4. Directory Scout: Check surrounding files
        directory_improvements = self._check_directory_naming(Path(file_path).parent)
        
        for improvement in directory_improvements:
            if self._apply_directory_improvement(improvement):
                result.files_cleaned.append(improvement['file'])
        
        # 5. Log the Scout work
        self._log_boyscout_activity(file_path, result)
        
        return result
    
    def _check_naming_violations(self, file_path: str) -> List[Dict]:
        """Check for naming convention violations."""
        
        violations = []
        path = Path(file_path)
        filename = path.name
        
        # Check against universal naming patterns
        category = self._categorize_file(path)
        pattern = self.naming_patterns.get(category)
        
        if pattern and not re.match(pattern, filename):
            violations.append({
                'file': file_path,
                'category': category,
                'violation': f'Does not match pattern: {pattern}',
                'suggested': self._suggest_correct_name(filename, category),
                'description': f'Naming violation in {category}: {filename}'
            })
        
        return violations
    
    def _check_directory_naming(self, directory: Path) -> List[Dict]:
        """Check directory for naming improvements."""
        
        improvements = []
        
        # Look for obvious naming issues in same directory
        for file_path in directory.glob("*"):
            if file_path.is_file():
                issues = self._check_naming_violations(str(file_path))
                for issue in issues:
                    improvements.append({
                        'file': str(file_path),
                        'type': 'naming_violation',
                        'fix': issue['suggested']
                    })
        
        return improvements
    
    def _fix_naming_violation(self, issue: Dict) -> bool:
        """Fix a naming violation using Boy Scout principle."""
        
        try:
            old_path = Path(issue['file'])
            new_name = issue['suggested']
            new_path = old_path.parent / new_name
            
            if old_path.exists():
                # Rename the file
                old_path.rename(new_path)
                
                # Update references (Boy Scout thoroughness)
                refs_updated = self._update_references(old_path.name, new_name)
                issue['references_updated'] = refs_updated
                
                print(f"🏕️ Boy Scout: Fixed naming {old_path.name} → {new_name}")
                return True
                
        except Exception as e:
            print(f"⚠️ Boy Scout: Could not fix {issue['file']}: {e}")
            
        return False
    
    def _update_references(self, old_name: str, new_name: str) -> int:
        """Update references to renamed file (Boy Scout thoroughness)."""
        
        reference_count = 0
        
        # Search project for references
        for file_path in Path('.').rglob('*.md'):
            try:
                content = file_path.read_text(encoding='utf-8')
                if old_name in content:
                    updated_content = content.replace(old_name, new_name)
                    file_path.write_text(updated_content, encoding='utf-8')
                    reference_count += 1
            except Exception:
                pass
        
        return reference_count
    
    def _log_boyscout_activity(self, file_path: str, result: BoyscoutNamingResult):
        """Log Boy Scout naming activity for metrics."""
        
        activity = {
            'file': file_path,
            'timestamp': datetime.now().isoformat(),
            'improvements': len(result.improvements_made),
            'violations_fixed': len(result.violations_fixed),
            'files_cleaned': len(result.files_cleaned),
            'references_updated': result.references_updated
        }
        
        self.improvement_log.append(activity)
        
        # Also append to project-wide log
        log_path = Path('logs/boyscout_naming_activity.log')
        log_path.parent.mkdir(exist_ok=True)
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{activity['timestamp']}: Boy Scout on {file_path} - "
                   f"{activity['violations_fixed']} violations fixed, "
                   f"{activity['references_updated']} references updated\n")

# Usage Integration
def integrate_with_file_operations():
    """
    Integration point for all file operations.
    
    Add this to any file operation workflow:
    """
    
    scout = BoyscoutNamingIntegration()
    
    # Example integration
    def create_file_with_boyscout(file_path: str, content: str):
        """Create file with Boy Scout naming integration."""
        
        # 1. Create the file (original task)
        Path(file_path).write_text(content, encoding='utf-8')
        
        # 2. Apply Boy Scout + naming improvements
        result = scout.apply_boyscout_naming(file_path, 'create')
        
        # 3. Report improvements
        if result.violations_fixed or result.files_cleaned:
            print(f"🏕️ Boy Scout: Left {len(result.files_cleaned)} files cleaner, "
                 f"fixed {len(result.violations_fixed)} naming violations")
    
    return create_file_with_boyscout

if __name__ == "__main__":
    print("Boy Scout + Naming Convention Integration Ready!")
