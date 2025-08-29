#!/usr/bin/env python3
"""
Test Catalogue Generator
========================

Automatically generates and maintains a comprehensive test catalogue by scanning
all test files and extracting test classes, functions, and documentation.

Features:
- Scans all test files recursively
- Extracts test classes and functions
- Analyzes test categories and types
- Generates comprehensive markdown documentation
- Tracks test coverage and organization
- Validates test naming conventions

Usage:
    python scripts/generate_test_catalogue.py [--output-file] [--validate] [--update]

Author: AI Development Agent
Last Updated: 2025-08-29
"""

import os
import sys
import ast
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import re

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.logging_config import setup_logging

class TestInfo:
    """Container for test information."""
    
    def __init__(self, name: str, docstring: Optional[str] = None, line_number: int = 0):
        self.name = name
        self.docstring = docstring or ""
        self.line_number = line_number
        self.category = self._categorize_test(name)
    
    def _categorize_test(self, name: str) -> str:
        """Categorize test based on name patterns."""
        name_lower = name.lower()
        
        if 'integration' in name_lower or 'api' in name_lower:
            return 'Integration'
        elif 'unit' in name_lower or 'isolated' in name_lower:
            return 'Unit'
        elif 'system' in name_lower or 'workflow' in name_lower or 'complete' in name_lower:
            return 'System'
        elif 'performance' in name_lower or 'load' in name_lower:
            return 'Performance'
        elif 'security' in name_lower or 'auth' in name_lower:
            return 'Security'
        elif 'supervisor' in name_lower:
            return 'Supervisor'
        elif 'langgraph' in name_lower:
            return 'LangGraph'
        elif 'infrastructure' in name_lower:
            return 'Infrastructure'
        else:
            return 'General'

class TestFileInfo:
    """Container for test file information."""
    
    def __init__(self, file_path: Path, relative_path: Path):
        self.file_path = file_path
        self.relative_path = relative_path
        self.classes: List[TestInfo] = []
        self.functions: List[TestInfo] = []
        self.docstring: str = ""
        self.category = self._categorize_file()
        self.size_bytes = file_path.stat().st_size if file_path.exists() else 0
        
    def _categorize_file(self) -> str:
        """Categorize file based on directory structure."""
        parts = self.relative_path.parts
        
        if 'unit' in parts:
            return 'Unit Tests'
        elif 'integration' in parts:
            return 'Integration Tests'
        elif 'system' in parts:
            return 'System Tests'
        elif 'langgraph' in parts:
            return 'LangGraph Tests'
        elif 'supervisor' in parts:
            return 'Supervisor Tests'
        elif 'infrastructure' in parts:
            return 'Infrastructure Tests'
        elif 'agile' in parts:
            return 'Agile Tests'
        elif 'isolated' in parts:
            return 'Isolated Tests'
        elif 'performance' in parts:
            return 'Performance Tests'
        elif 'security' in parts:
            return 'Security Tests'
        else:
            return 'Root Tests'
    
    @property
    def total_tests(self) -> int:
        return len(self.classes) + len(self.functions)

class TestCatalogueGenerator:
    """Generates comprehensive test catalogue documentation."""
    
    def __init__(self, test_root: Optional[Path] = None, output_file: Optional[Path] = None):
        self.logger = setup_logging(__name__)
        self.test_root = test_root or Path(__file__).parent.parent / "tests"
        self.output_file = output_file or Path(__file__).parent.parent / "docs" / "testing" / "TEST_CATALOGUE.md"
        self.timestamp = datetime.now()
        self.test_files: List[TestFileInfo] = []
        
    def scan_test_files(self) -> None:
        """Scan all test files and extract information."""
        
        self.logger.info(f"🔍 Scanning test files in {self.test_root}")
        
        for test_file in self.test_root.rglob("test_*.py"):
            try:
                relative_path = test_file.relative_to(self.test_root)
                file_info = TestFileInfo(test_file, relative_path)
                
                # Extract test information
                self._extract_test_info(test_file, file_info)
                
                self.test_files.append(file_info)
                self.logger.debug(f"   📁 {relative_path} - {file_info.total_tests} tests")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to process {test_file}: {e}")
        
        self.test_files.sort(key=lambda x: (x.category, str(x.relative_path)))
        self.logger.info(f"✅ Scanned {len(self.test_files)} test files")
    
    def _extract_test_info(self, file_path: Path, file_info: TestFileInfo) -> None:
        """Extract test classes and functions from a file."""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant) and 
                isinstance(tree.body[0].value.value, str)):
                file_info.docstring = tree.body[0].value.value.strip()
            
            # Extract test classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                    docstring = ast.get_docstring(node) or ""
                    test_info = TestInfo(node.name, docstring, node.lineno)
                    file_info.classes.append(test_info)
                    
                elif isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    docstring = ast.get_docstring(node) or ""
                    test_info = TestInfo(node.name, docstring, node.lineno)
                    file_info.functions.append(test_info)
                    
        except Exception as e:
            self.logger.error(f"Failed to parse {file_path}: {e}")
    
    def generate_catalogue(self) -> str:
        """Generate comprehensive test catalogue markdown."""
        
        total_files = len(self.test_files)
        total_classes = sum(len(f.classes) for f in self.test_files)
        total_functions = sum(len(f.functions) for f in self.test_files)
        total_tests = total_classes + total_functions
        total_size = sum(f.size_bytes for f in self.test_files)
        
        # Group by category
        categories = {}
        for file_info in self.test_files:
            if file_info.category not in categories:
                categories[file_info.category] = []
            categories[file_info.category].append(file_info)
        
        catalogue = f"""# Test Catalogue - Comprehensive Test Documentation

**Generated**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Generator**: Test Catalogue Generator v1.0  
**Purpose**: Complete inventory and documentation of all test cases

## 📊 **Test Suite Overview**

| Metric | Value |
|--------|--------|
| **Total Test Files** | {total_files} |
| **Total Test Classes** | {total_classes} |
| **Total Test Functions** | {total_functions} |
| **Total Tests** | {total_tests} |
| **Total Size** | {self._format_bytes(total_size)} |
| **Coverage Categories** | {len(categories)} |

## 🎯 **Test Categories**

"""
        
        # Category summary
        for category, files in categories.items():
            file_count = len(files)
            test_count = sum(f.total_tests for f in files)
            catalogue += f"- **{category}**: {file_count} files, {test_count} tests\n"
        
        catalogue += "\n"
        
        # Detailed test inventory by category
        for category, files in categories.items():
            catalogue += f"\n## 📁 **{category}**\n\n"
            
            for file_info in files:
                catalogue += f"### `{file_info.relative_path}` ({file_info.total_tests} tests)\n\n"
                
                if file_info.docstring:
                    catalogue += f"**Description**: {file_info.docstring.split('.')[0]}.\n\n"
                
                catalogue += f"| Metric | Value |\n"
                catalogue += f"|--------|--------|\n"
                catalogue += f"| **File Size** | {self._format_bytes(file_info.size_bytes)} |\n"
                catalogue += f"| **Test Classes** | {len(file_info.classes)} |\n"
                catalogue += f"| **Test Functions** | {len(file_info.functions)} |\n"
                catalogue += f"| **Total Tests** | {file_info.total_tests} |\n\n"
                
                # Test classes
                if file_info.classes:
                    catalogue += "#### Test Classes\n\n"
                    for test_class in file_info.classes:
                        catalogue += f"- **`{test_class.name}`** (Line {test_class.line_number})\n"
                        if test_class.docstring:
                            catalogue += f"  - *{test_class.docstring.split('.')[0]}*\n"
                        catalogue += f"  - Category: {test_class.category}\n"
                    catalogue += "\n"
                
                # Test functions
                if file_info.functions:
                    catalogue += "#### Test Functions\n\n"
                    for test_func in file_info.functions:
                        catalogue += f"- **`{test_func.name}`** (Line {test_func.line_number})\n"
                        if test_func.docstring:
                            catalogue += f"  - *{test_func.docstring.split('.')[0]}*\n"
                        catalogue += f"  - Category: {test_func.category}\n"
                    catalogue += "\n"
                
                catalogue += "---\n\n"
        
        # Test naming validation
        catalogue += self._generate_naming_validation()
        
        # Test organization analysis
        catalogue += self._generate_organization_analysis()
        
        # Recommendations
        catalogue += self._generate_recommendations()
        
        return catalogue
    
    def _generate_naming_validation(self) -> str:
        """Generate test naming convention validation."""
        
        section = "\n## ✅ **Naming Convention Validation**\n\n"
        
        invalid_files = []
        invalid_classes = []
        invalid_functions = []
        
        for file_info in self.test_files:
            # Validate file naming
            if not (file_info.relative_path.name.startswith('test_') or 
                   file_info.relative_path.name.endswith('_test.py')):
                invalid_files.append(str(file_info.relative_path))
            
            # Validate class naming
            for test_class in file_info.classes:
                if not test_class.name.startswith('Test'):
                    invalid_classes.append(f"{file_info.relative_path}::{test_class.name}")
            
            # Validate function naming
            for test_func in file_info.functions:
                if not test_func.name.startswith('test_'):
                    invalid_functions.append(f"{file_info.relative_path}::{test_func.name}")
        
        # Results
        if not any([invalid_files, invalid_classes, invalid_functions]):
            section += "🎉 **All naming conventions are correct!**\n\n"
        else:
            if invalid_files:
                section += f"❌ **Invalid file names** ({len(invalid_files)}):\n"
                for file in invalid_files:
                    section += f"- `{file}`\n"
                section += "\n"
            
            if invalid_classes:
                section += f"❌ **Invalid class names** ({len(invalid_classes)}):\n"
                for cls in invalid_classes:
                    section += f"- `{cls}`\n"
                section += "\n"
            
            if invalid_functions:
                section += f"❌ **Invalid function names** ({len(invalid_functions)}):\n"
                for func in invalid_functions:
                    section += f"- `{func}`\n"
                section += "\n"
        
        return section
    
    def _generate_organization_analysis(self) -> str:
        """Generate test organization analysis."""
        
        section = "\n## 📋 **Test Organization Analysis**\n\n"
        
        # Directory structure
        directories = set()
        for file_info in self.test_files:
            directories.add(file_info.relative_path.parent)
        
        section += f"### Directory Structure ({len(directories)} directories)\n\n"
        for directory in sorted(directories):
            files_in_dir = [f for f in self.test_files if f.relative_path.parent == directory]
            total_tests = sum(f.total_tests for f in files_in_dir)
            section += f"- `{directory}/` - {len(files_in_dir)} files, {total_tests} tests\n"
        
        section += "\n"
        
        # Test distribution
        section += "### Test Distribution by Category\n\n"
        categories = {}
        for file_info in self.test_files:
            if file_info.category not in categories:
                categories[file_info.category] = 0
            categories[file_info.category] += file_info.total_tests
        
        section += "| Category | Test Count | Percentage |\n"
        section += "|----------|------------|------------|\n"
        
        total_tests = sum(categories.values())
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_tests * 100) if total_tests > 0 else 0
            section += f"| {category} | {count} | {percentage:.1f}% |\n"
        
        section += "\n"
        
        return section
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations for test improvements."""
        
        section = "\n## 💡 **Recommendations**\n\n"
        
        recommendations = []
        
        # Check for missing documentation
        undocumented_files = [f for f in self.test_files if not f.docstring]
        if undocumented_files:
            recommendations.append(
                f"📝 **Add documentation** to {len(undocumented_files)} test files without docstrings"
            )
        
        # Check for large test files
        large_files = [f for f in self.test_files if f.size_bytes > 50000]  # 50KB
        if large_files:
            recommendations.append(
                f"🔧 **Consider splitting** {len(large_files)} large test files (>50KB) for better maintainability"
            )
        
        # Check for empty test files
        empty_files = [f for f in self.test_files if f.total_tests == 0]
        if empty_files:
            recommendations.append(
                f"🧹 **Remove or implement** {len(empty_files)} empty test files"
            )
        
        # Check test distribution
        categories = {}
        for file_info in self.test_files:
            if file_info.category not in categories:
                categories[file_info.category] = 0
            categories[file_info.category] += file_info.total_tests
        
        total_tests = sum(categories.values())
        unit_percentage = (categories.get('Unit Tests', 0) / total_tests * 100) if total_tests > 0 else 0
        
        if unit_percentage < 60:
            recommendations.append(
                f"⚖️ **Increase unit test coverage** - Currently {unit_percentage:.1f}%, recommended >60%"
            )
        
        if not recommendations:
            section += "🎉 **No recommendations** - Test suite is well organized!\n\n"
        else:
            section += "### Improvement Opportunities\n\n"
            for i, rec in enumerate(recommendations, 1):
                section += f"{i}. {rec}\n"
            section += "\n"
        
        # Best practices
        section += "### Best Practices Checklist\n\n"
        section += "- ✅ Follow naming conventions (`test_*.py`, `Test*`, `test_*`)\n"
        section += "- ✅ Organize tests by category and functionality\n"
        section += "- ✅ Write descriptive test names and docstrings\n"
        section += "- ✅ Keep test files focused and manageable (<50KB)\n"
        section += "- ✅ Maintain good balance between unit and integration tests\n"
        section += "- ✅ Use appropriate test fixtures and mocking\n"
        section += "- ✅ Regular test catalogue updates\n\n"
        
        return section
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes into human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024
        return f"{bytes_count:.1f} TB"
    
    def save_catalogue(self, content: str) -> None:
        """Save catalogue to file."""
        
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"✅ Test catalogue saved to {self.output_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save catalogue: {e}")
            raise
    
    def validate_tests(self) -> bool:
        """Validate test suite organization and naming."""
        
        self.logger.info("🔍 Validating test suite...")
        
        issues = []
        
        for file_info in self.test_files:
            # Check file naming
            if not (file_info.relative_path.name.startswith('test_') or 
                   file_info.relative_path.name.endswith('_test.py')):
                issues.append(f"Invalid file name: {file_info.relative_path}")
            
            # Check class naming
            for test_class in file_info.classes:
                if not test_class.name.startswith('Test'):
                    issues.append(f"Invalid class name: {file_info.relative_path}::{test_class.name}")
            
            # Check function naming
            for test_func in file_info.functions:
                if not test_func.name.startswith('test_'):
                    issues.append(f"Invalid function name: {file_info.relative_path}::{test_func.name}")
        
        if issues:
            self.logger.error(f"❌ Found {len(issues)} validation issues:")
            for issue in issues:
                self.logger.error(f"   • {issue}")
            return False
        else:
            self.logger.info("✅ All validation checks passed")
            return True
    
    def run(self, validate_only: bool = False) -> bool:
        """Run the test catalogue generation process."""
        
        try:
            self.logger.info("🚀 Starting test catalogue generation...")
            
            # Scan test files
            self.scan_test_files()
            
            if validate_only:
                return self.validate_tests()
            
            # Generate catalogue
            self.logger.info("📝 Generating test catalogue...")
            catalogue_content = self.generate_catalogue()
            
            # Save catalogue
            self.save_catalogue(catalogue_content)
            
            # Validate
            validation_passed = self.validate_tests()
            
            self.logger.info("🎉 Test catalogue generation completed successfully!")
            return validation_passed
            
        except Exception as e:
            self.logger.error(f"❌ Test catalogue generation failed: {e}")
            return False

def main():
    """Main execution function."""
    
    parser = argparse.ArgumentParser(description="Generate comprehensive test catalogue")
    parser.add_argument("--output-file", "-o", type=Path, 
                       help="Output file path (default: docs/testing/TEST_CATALOGUE.md)")
    parser.add_argument("--validate", action="store_true",
                       help="Only validate test naming and organization")
    parser.add_argument("--test-root", type=Path,
                       help="Test root directory (default: tests/)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose logging")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = TestCatalogueGenerator(
        test_root=args.test_root,
        output_file=args.output_file
    )
    
    if args.verbose:
        generator.logger.setLevel("DEBUG")
    
    # Run generation
    success = generator.run(validate_only=args.validate)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
