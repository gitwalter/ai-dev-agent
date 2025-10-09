#!/usr/bin/env python3
"""
File Organization Validation Script
==================================

Validates that all files in the repository follow the Sacred File Organization Rule.
This script is called by Cursor rules and git hooks to enforce organization standards.

Author: AI Development Agent
Created: 2025-01-02
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class FileOrganizationValidator:
    """Validates file organization according to sacred standards."""
    
    def __init__(self):
        self.project_root = project_root
        self.violations = []
        self.organization_rules = self._load_organization_rules()
    
    def _load_organization_rules(self) -> Dict[str, str]:
        """Load file organization rules."""
        return {
            # Test files
            r'^test_.*\.py$': 'tests/{category}/',
            r'.*_test\.py$': 'tests/{category}/',
            
            # Agent files
            r'.*agent.*\.py$': 'agents/{category}/',
            
            # Utility files (non-app Python files)
            r'^(?!app).*\.py$': 'utils/{category}/',
            
            # Documentation
            r'^(?!README).*\.md$': 'docs/{category}/',
            r'^README\.md$': '{root_or_module}/',
            
            # Scripts
            r'.*script.*\.py$': 'scripts/',
            
            # Configuration
            r'.*\.(toml|ini|cfg)$': '{root}/',
            r'.*\.(yaml|yml)$': 'workflow/ OR templates/',
            
            # Rule files
            r'.*\.mdc$': '.cursor/rules/{category}/',
        }
    
    def determine_correct_path(self, filename: str, current_path: str) -> str:
        """Determine the correct path for a file based on its name and content."""
        
        # Test files
        if filename.startswith('test_') or filename.endswith('_test.py'):
            if 'mcp' in filename.lower():
                return f"tests/mcp/{filename}"
            elif 'integration' in filename.lower():
                return f"tests/integration/{filename}"
            elif 'unit' in filename.lower():
                return f"tests/unit/{filename}"
            elif 'agile' in filename.lower():
                return f"tests/agile/{filename}"
            else:
                return f"tests/{filename}"
        
        # Agent files
        if 'agent' in filename.lower() and filename.endswith('.py'):
            if 'mcp' in current_path:
                return f"agents/mcp/{filename}"
            elif 'swarm' in current_path:
                return f"agents/swarm/{filename}"
            elif 'development' in current_path:
                return f"agents/development/{filename}"
            else:
                return f"agents/core/{filename}"
        
        # Utility files
        if filename.endswith('.py') and not filename.startswith('app') and not self._is_script_file(filename):
            if 'mcp' in current_path:
                return f"utils/mcp/{filename}"
            elif 'system' in current_path:
                return f"utils/system/{filename}"
            elif 'agile' in current_path:
                return f"utils/agile/{filename}"
            else:
                return f"utils/core/{filename}"
        
        # Documentation
        if filename.endswith('.md'):
            if filename == 'README.md':
                return current_path  # README can be in root or module root
            elif 'agile' in current_path:
                return f"docs/agile/{filename}"
            elif 'architecture' in current_path:
                return f"docs/architecture/{filename}"
            else:
                return f"docs/{filename}"
        
        # Scripts
        if self._is_script_file(filename):
            return f"scripts/{filename}"
        
        # Rule files
        if filename.endswith('.mdc'):
            return f".cursor/rules/core/{filename}"
        
        # Configuration files
        if filename.endswith(('.toml', '.ini', '.cfg')):
            return filename  # Root level
        
        # Default: current location is acceptable
        return current_path
    
    def _is_script_file(self, filename: str) -> bool:
        """Check if file is a script."""
        script_indicators = [
            'script', 'automation', 'setup', 'install', 'deploy', 
            'build', 'test_runner', 'validate', 'check'
        ]
        return any(indicator in filename.lower() for indicator in script_indicators)
    
    def validate_file(self, file_path: str) -> Optional[str]:
        """
        Validate a single file's organization.
        
        Returns:
            None if file is correctly placed, error message if violation detected
        """
        file_path = Path(file_path)
        filename = file_path.name
        current_dir = str(file_path.parent)
        
        # Skip certain files/directories
        if self._should_skip_file(file_path):
            return None
        
        correct_path = self.determine_correct_path(filename, current_dir)
        current_full_path = str(file_path)
        
        # Normalize paths for comparison
        if correct_path != current_full_path and not self._is_acceptable_location(file_path, correct_path):
            return f"File '{filename}' should be in '{correct_path}' but is in '{current_full_path}'"
        
        return None
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped from validation."""
        skip_patterns = [
            '.git/', '__pycache__/', '.pytest_cache/', 'node_modules/',
            '.venv/', 'venv/', 'env/', '.env', 'generated_projects/',
            'backups/', 'logs/', 'monitoring/', 'prompt_backups/'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _is_acceptable_location(self, current_path: Path, suggested_path: str) -> bool:
        """Check if current location is acceptable even if not optimal."""
        # Some files have multiple acceptable locations
        filename = current_path.name
        current_str = str(current_path)
        
        # README files can be in root or module directories
        if filename == 'README.md':
            return True
        
        # Configuration files in root are acceptable
        if filename.endswith(('.toml', '.ini', '.cfg', '.json')) and current_path.parent == self.project_root:
            return True
        
        # Temporary files during development
        if filename.startswith(('temp_', 'debug_', 'test_')) and current_path.parent == self.project_root:
            return True  # Temporary allowance
        
        return False
    
    def validate_repository(self) -> List[str]:
        """Validate entire repository file organization."""
        violations = []
        
        # Walk through all files
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.project_root)
                
                violation = self.validate_file(str(relative_path))
                if violation:
                    violations.append(violation)
        
        return violations
    
    def generate_fix_suggestions(self, violations: List[str]) -> List[Dict[str, str]]:
        """Generate fix suggestions for violations."""
        suggestions = []
        
        for violation in violations:
            # Parse violation message to extract file and correct path
            # This is a simplified parser - could be enhanced
            if "should be in" in violation:
                parts = violation.split("'")
                if len(parts) >= 4:
                    filename = parts[1]
                    correct_path = parts[3]
                    current_path = parts[5] if len(parts) > 5 else "unknown"
                    
                    suggestions.append({
                        'filename': filename,
                        'current_path': current_path,
                        'correct_path': correct_path,
                        'action': f"Move {filename} from {current_path} to {correct_path}"
                    })
        
        return suggestions

def main():
    """Main validation function."""
    print("🛡️ File Organization Validation")
    print("=" * 40)
    
    validator = FileOrganizationValidator()
    violations = validator.validate_repository()
    
    if not violations:
        print("✅ All files are properly organized!")
        print("🛡️ Sacred File Organization Rule: COMPLIANT")
        return 0
    
    print(f"🚨 Found {len(violations)} file organization violations:")
    print()
    
    for i, violation in enumerate(violations, 1):
        print(f"{i:2d}. {violation}")
    
    print()
    print("🛡️ Sacred File Organization Rule: VIOLATIONS DETECTED")
    
    # Generate fix suggestions
    suggestions = validator.generate_fix_suggestions(violations)
    if suggestions:
        print("\n💡 Fix Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i:2d}. {suggestion['action']}")
    
    print("\n🔧 To fix these violations:")
    print("   1. Move files to their correct locations")
    print("   2. Run this script again to verify")
    print("   3. Commit changes once all violations are resolved")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
