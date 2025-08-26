#!/usr/bin/env python3
"""
Setup script for test environment and organization.
Helps developers set up the test environment and follow test organization rules.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict


class TestEnvironmentSetup:
    """Setup and validate test environment."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / "tests"
        
    def setup_test_environment(self):
        """Setup the complete test environment."""
        print("Setting up test environment...")
        
        # Create test directory structure
        self.create_test_structure()
        
        # Install test dependencies
        self.install_test_dependencies()
        
        # Validate test organization
        self.validate_test_organization()
        
        # Generate test index
        self.generate_test_index()
        
        print("Test environment setup complete!")
        
    def create_test_structure(self):
        """Create the recommended test directory structure."""
        print("Creating test directory structure...")
        
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
        
        print("Test directory structure created")
        
    def install_test_dependencies(self):
        """Install test dependencies."""
        print("Installing test dependencies...")
        
        test_dependencies = [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "pytest-xdist>=3.0.0",
            "coverage>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "mypy>=1.3.0"
        ]
        
        for dep in test_dependencies:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
                print(f"  ✓ Installed {dep}")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ Failed to install {dep}: {e}")
                
    def validate_test_organization(self):
        """Validate test organization."""
        print("Validating test organization...")
        
        try:
            result = subprocess.run([
                sys.executable, "tests/organize_tests.py", "--validate"
            ], capture_output=True, text=True, check=True)
            print("  ✓ Test organization is valid")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Test organization validation failed:")
            print(e.stdout)
            print(e.stderr)
            
    def generate_test_index(self):
        """Generate test index."""
        print("Generating test index...")
        
        try:
            subprocess.run([
                sys.executable, "tests/organize_tests.py", "--generate-index"
            ], check=True, capture_output=True)
            print("  ✓ Test index generated")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to generate test index: {e}")
            
    def run_tests(self, category: str = None):
        """Run tests with optional category filter."""
        print("Running tests...")
        
        cmd = [sys.executable, "-m", "pytest", "tests/"]
        
        if category:
            cmd.extend([f"tests/{category}/"])
            
        try:
            subprocess.run(cmd, check=True)
            print("  ✓ All tests passed")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Some tests failed")
            return False
            
        return True
        
    def show_test_help(self):
        """Show help information for test organization."""
        help_text = """
Test Organization Help
=====================

Core Rules:
1. All test files must be in the tests/ directory
2. Test files must follow naming: test_*.py or *_test.py
3. Test functions must start with "test_"
4. Test classes must start with "Test"

Directory Structure:
- tests/unit/ - Unit tests for individual components
- tests/integration/ - Integration tests for component interactions
- tests/system/ - System-wide tests
- tests/performance/ - Performance and load tests
- tests/security/ - Security and vulnerability tests

Commands:
- python tests/setup_test_environment.py --setup
- python tests/organize_tests.py --validate
- python tests/organize_tests.py --create-structure
- pytest tests/ --cov=. --cov-report=html

For more information, see tests/TEST_ORGANIZATION_RULES.md
"""
        print(help_text)


def main():
    """Main function for test environment setup."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup test environment and organization")
    parser.add_argument("--setup", action="store_true", help="Setup complete test environment")
    parser.add_argument("--validate", action="store_true", help="Validate test organization")
    parser.add_argument("--run-tests", action="store_true", help="Run all tests")
    parser.add_argument("--run-unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--run-integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--help-info", action="store_true", help="Show test organization help")
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    setup = TestEnvironmentSetup(project_root)
    
    if args.setup:
        setup.setup_test_environment()
    elif args.validate:
        setup.validate_test_organization()
    elif args.run_tests:
        setup.run_tests()
    elif args.run_unit:
        setup.run_tests("unit")
    elif args.run_integration:
        setup.run_tests("integration")
    elif args.help_info:
        setup.show_test_help()
    else:
        # Default: show help
        setup.show_test_help()


if __name__ == "__main__":
    main()
