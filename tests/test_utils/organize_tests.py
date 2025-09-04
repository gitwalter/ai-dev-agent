#!/usr/bin/env python3
"""
Test organization script for AI Development Agent.
Automatically moves test files to the tests directory and organizes them.
"""

import os
import sys
import shutil
import re
from pathlib import Path
from typing import List, Dict, Set
import argparse


class TestOrganizer:
    """Organizes test files and enforces test directory structure."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / "tests"
        self.test_patterns = [
            r"^test_.*\.py$",
            r".*_test\.py$",
            r"test_.*\.py$"
        ]
        
    def find_test_files(self, directory: Path) -> List[Path]:
        """Find all test files in a directory."""
        test_files = []
        
        for pattern in self.test_patterns:
            for file_path in directory.rglob("*.py"):
                if re.match(pattern, file_path.name):
                    test_files.append(file_path)
        
        return test_files
    
    def should_move_file(self, file_path: Path) -> bool:
        """Determine if a file should be moved to tests directory."""
        # Don't move files that are already in tests directory
        if "tests" in file_path.parts:
            return False
        
        # Don't move files in generated_projects directory (these are generated test files)
        if "generated_projects" in file_path.parts:
            return False
        
        # Don't move files that are part of the test infrastructure
        if file_path.name in ["__init__.py", "conftest.py", "test_utils.py"]:
            return False
        
        # Don't move agent files (like test_generator.py)
        if "agents" in file_path.parts and file_path.name == "test_generator.py":
            return False
        
        # Check if it matches test patterns
        for pattern in self.test_patterns:
            if re.match(pattern, file_path.name):
                return True
        
        return False
    
    def get_target_path(self, file_path: Path) -> Path:
        """Get the target path for a test file in the tests directory."""
        # Create a relative path from project root
        relative_path = file_path.relative_to(self.project_root)
        
        # If it's in a subdirectory, maintain the structure
        if len(relative_path.parts) > 1:
            # Create subdirectory structure in tests
            subdir = relative_path.parent
            target_dir = self.tests_dir / subdir
            target_dir.mkdir(parents=True, exist_ok=True)
            return target_dir / file_path.name
        else:
            # Move to root of tests directory
            return self.tests_dir / file_path.name
    
    def move_test_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """Move a test file to the tests directory."""
        if not self.should_move_file(file_path):
            return False
        
        target_path = self.get_target_path(file_path)
        
        # Check if target already exists
        if target_path.exists():
            print(f"Warning: Target file {target_path} already exists, skipping {file_path}")
            return False
        
        if dry_run:
            print(f"Would move: {file_path} -> {target_path}")
            return True
        
        try:
            # Create target directory if it doesn't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            shutil.move(str(file_path), str(target_path))
            print(f"Moved: {file_path} -> {target_path}")
            return True
            
        except Exception as e:
            print(f"Error moving {file_path}: {e}")
            return False
    
    def organize_tests(self, dry_run: bool = False) -> Dict[str, int]:
        """Organize all test files in the project."""
        stats = {
            "moved": 0,
            "skipped": 0,
            "errors": 0
        }
        
        # Find all test files
        test_files = self.find_test_files(self.project_root)
        
        print(f"Found {len(test_files)} test files")
        
        for file_path in test_files:
            if self.move_test_file(file_path, dry_run):
                stats["moved"] += 1
            else:
                stats["skipped"] += 1
        
        return stats
    
    def create_test_structure(self):
        """Create the recommended test directory structure."""
        structure = {
            "unit": "Unit tests for individual components",
            "integration": "Integration tests for component interactions",
            "system": "System-wide tests",
            "performance": "Performance and load tests",
            "security": "Security and vulnerability tests",
            "fixtures": "Test fixtures and data",
            "mocks": "Mock objects and test doubles"
        }
        
        for category, description in structure.items():
            category_dir = self.tests_dir / category
            category_dir.mkdir(exist_ok=True)
            
            # Create __init__.py
            init_file = category_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text(f'"""Tests: {description}"""\n')
            
            # Create README
            readme_file = category_dir / "README.md"
            if not readme_file.exists():
                readme_file.write_text(f"# {category.title()} Tests\n\n{description}\n")
    
    def validate_test_structure(self) -> List[str]:
        """Validate the test directory structure and return issues."""
        issues = []
        
        # Check if tests directory exists
        if not self.tests_dir.exists():
            issues.append("Tests directory does not exist")
            return issues
        
        # Check for test files outside tests directory
        for pattern in self.test_patterns:
            for file_path in self.project_root.rglob("*.py"):
                # Skip files in tests directory
                if "tests" in file_path.parts:
                    continue
                
                # Skip files in generated_projects directory
                if "generated_projects" in file_path.parts:
                    continue
                
                # Skip agent files (like test_generator.py)
                if "agents" in file_path.parts and file_path.name == "test_generator.py":
                    continue
                
                # Skip __pycache__ directories
                if "__pycache__" in file_path.parts:
                    continue
                
                if re.match(pattern, file_path.name):
                    issues.append(f"Test file found outside tests directory: {file_path}")
        
        # Check for missing __init__.py files (but skip __pycache__)
        for subdir in self.tests_dir.iterdir():
            if subdir.is_dir() and subdir.name != "__pycache__" and not (subdir / "__init__.py").exists():
                issues.append(f"Missing __init__.py in {subdir}")
        
        return issues
    
    def generate_test_index(self):
        """Generate an index of all test files."""
        index_content = ["# Test Index\n"]
        
        for test_file in sorted(self.tests_dir.rglob("*.py")):
            if test_file.name == "__init__.py":
                continue
            
            relative_path = test_file.relative_to(self.tests_dir)
            index_content.append(f"- `{relative_path}`")
        
        index_file = self.tests_dir / "TEST_INDEX.md"
        index_file.write_text("\n".join(index_content))
        print(f"Generated test index: {index_file}")


def main():
    """Main function for test organization."""
    parser = argparse.ArgumentParser(description="Organize test files in AI Development Agent project")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving")
    parser.add_argument("--create-structure", action="store_true", help="Create recommended test directory structure")
    parser.add_argument("--validate", action="store_true", help="Validate test directory structure")
    parser.add_argument("--generate-index", action="store_true", help="Generate test index")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root directory")
    
    args = parser.parse_args()
    
    organizer = TestOrganizer(args.project_root)
    
    if args.create_structure:
        print("Creating test directory structure...")
        organizer.create_test_structure()
        print("Test directory structure created")
    
    if args.validate:
        print("Validating test structure...")
        issues = organizer.validate_test_structure()
        if issues:
            print("Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Test structure is valid")
    
    if args.generate_index:
        print("Generating test index...")
        organizer.generate_test_index()
    
    if not any([args.create_structure, args.validate, args.generate_index]):
        # Default action: organize tests
        print("Organizing test files...")
        stats = organizer.organize_tests(dry_run=args.dry_run)
        
        print(f"\nOrganization complete:")
        print(f"  Moved: {stats['moved']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
