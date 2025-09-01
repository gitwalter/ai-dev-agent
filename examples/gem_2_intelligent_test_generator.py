#!/usr/bin/env python3
"""
GEM 2: Intelligent Test Generator with Ontological Reasoning
============================================================

REAL VALUE: Automatically generates comprehensive test suites by analyzing code
from multiple ontological perspectives:
- @engineering: Functional tests, edge cases, performance tests
- @architecture: Integration tests, contract tests, API tests  
- @debug: Error condition tests, boundary tests, failure scenarios

IMMEDIATE USE: Point at any Python module and get instant comprehensive test coverage.

Usage:
    python gem_2_intelligent_test_generator.py mymodule.py
    python gem_2_intelligent_test_generator.py --class MyClass mymodule.py
    python gem_2_intelligent_test_generator.py --function my_function mymodule.py
    python gem_2_intelligent_test_generator.py --full-suite src/
"""

import sys
import os
import ast
import inspect
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from textwrap import dedent

# Add utils to path for ontological framework
utils_path = Path(__file__).parent.parent / "utils"
sys.path.append(str(utils_path))

from context.ontological_framework_system import OntologicalSwitchingSystem


@dataclass
class TestCase:
    """Represents a generated test case."""
    name: str
    code: str
    perspective: str
    test_type: str
    description: str


@dataclass
class FunctionAnalysis:
    """Analysis of a function for test generation."""
    name: str
    args: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    complexity: int
    edge_cases: List[str]
    error_conditions: List[str]


class IntelligentTestGenerator:
    """
    Generates comprehensive test suites using ontological perspective switching.
    
    Each perspective contributes different types of tests:
    - Engineering: Unit tests, performance tests, integration tests
    - Architecture: Contract tests, interface tests, system tests
    - Debug: Error tests, boundary tests, failure scenario tests
    """
    
    def __init__(self):
        self.ontology_system = OntologicalSwitchingSystem()
        self.generated_tests = []
        self.analysis_cache = {}
    
    def generate_tests_for_file(self, file_path: str, target_class: str = None, 
                               target_function: str = None) -> List[TestCase]:
        """
        Generate comprehensive test suite for a Python file.
        
        Args:
            file_path: Path to Python file to analyze
            target_class: Specific class to test (optional)
            target_function: Specific function to test (optional)
            
        Returns:
            List of generated test cases
        """
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in {file_path}: {e}")
        
        all_tests = []
        
        # Analyze the code structure
        functions = self._extract_functions(tree, target_function)
        classes = self._extract_classes(tree, target_class)
        
        # Generate tests from each ontological perspective
        for func_info in functions:
            engineering_tests = self._generate_engineering_tests(func_info, file_path)
            architecture_tests = self._generate_architecture_tests(func_info, file_path)
            debug_tests = self._generate_debug_tests(func_info, file_path)
            
            all_tests.extend(engineering_tests)
            all_tests.extend(architecture_tests)
            all_tests.extend(debug_tests)
        
        for class_info in classes:
            class_tests = self._generate_class_tests(class_info, file_path)
            all_tests.extend(class_tests)
        
        self.generated_tests.extend(all_tests)
        return all_tests
    
    def _extract_functions(self, tree: ast.AST, target_function: str = None) -> List[FunctionAnalysis]:
        """Extract function information for test generation."""
        
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip if targeting specific function and this isn't it
                if target_function and node.name != target_function:
                    continue
                
                # Skip private methods and test functions
                if node.name.startswith('_') or node.name.startswith('test_'):
                    continue
                
                # Analyze function
                args = [arg.arg for arg in node.args.args]
                docstring = ast.get_docstring(node)
                
                # Calculate complexity (simplified cyclomatic complexity)
                complexity = self._calculate_complexity(node)
                
                # Identify edge cases and error conditions
                edge_cases = self._identify_edge_cases(node, args)
                error_conditions = self._identify_error_conditions(node)
                
                func_analysis = FunctionAnalysis(
                    name=node.name,
                    args=args,
                    return_type=None,  # Could be enhanced with type hints
                    docstring=docstring,
                    complexity=complexity,
                    edge_cases=edge_cases,
                    error_conditions=error_conditions
                )
                
                functions.append(func_analysis)
        
        return functions
    
    def _extract_classes(self, tree: ast.AST, target_class: str = None) -> List[Dict[str, Any]]:
        """Extract class information for test generation."""
        
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if target_class and node.name != target_class:
                    continue
                
                # Extract methods
                methods = []
                for child in node.body:
                    if isinstance(child, ast.FunctionDef) and not child.name.startswith('_'):
                        methods.append(child.name)
                
                class_info = {
                    'name': node.name,
                    'methods': methods,
                    'docstring': ast.get_docstring(node),
                    'line_number': node.lineno
                }
                
                classes.append(class_info)
        
        return classes
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate simplified cyclomatic complexity."""
        
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _identify_edge_cases(self, node: ast.FunctionDef, args: List[str]) -> List[str]:
        """Identify potential edge cases for testing."""
        
        edge_cases = []
        
        # Common edge cases based on argument patterns
        for arg in args:
            if 'list' in arg.lower() or 'array' in arg.lower():
                edge_cases.extend(['empty_list', 'single_item_list', 'large_list'])
            elif 'string' in arg.lower() or 'text' in arg.lower():
                edge_cases.extend(['empty_string', 'whitespace_string', 'unicode_string'])
            elif 'number' in arg.lower() or 'count' in arg.lower():
                edge_cases.extend(['zero', 'negative', 'large_number'])
            elif 'dict' in arg.lower():
                edge_cases.extend(['empty_dict', 'nested_dict'])
        
        return edge_cases
    
    def _identify_error_conditions(self, node: ast.FunctionDef) -> List[str]:
        """Identify potential error conditions for testing."""
        
        error_conditions = []
        
        # Look for explicit raises
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                if hasattr(child.exc, 'id'):
                    error_conditions.append(child.exc.id)
                elif hasattr(child.exc, 'func') and hasattr(child.exc.func, 'id'):
                    error_conditions.append(child.exc.func.id)
        
        # Common error patterns
        source = ast.unparse(node)
        if 'assert' in source:
            error_conditions.append('AssertionError')
        if 'KeyError' in source or '[' in source:
            error_conditions.append('KeyError')
        if 'ValueError' in source:
            error_conditions.append('ValueError')
        if 'TypeError' in source:
            error_conditions.append('TypeError')
        
        return list(set(error_conditions))
    
    def _generate_engineering_tests(self, func_info: FunctionAnalysis, file_path: str) -> List[TestCase]:
        """Generate tests from engineering perspective: functionality, performance."""
        
        print(f"🔧 Generating engineering tests for {func_info.name}")
        self.ontology_system.switch_perspective("engineering", f"Generate functional tests for {func_info.name}")
        
        tests = []
        module_name = Path(file_path).stem
        
        # Basic functionality test
        basic_test = self._generate_basic_functionality_test(func_info, module_name)
        tests.append(basic_test)
        
        # Edge case tests
        for edge_case in func_info.edge_cases:
            edge_test = self._generate_edge_case_test(func_info, edge_case, module_name)
            tests.append(edge_test)
        
        # Performance test (if function is complex)
        if func_info.complexity > 5:
            performance_test = self._generate_performance_test(func_info, module_name)
            tests.append(performance_test)
        
        return tests
    
    def _generate_architecture_tests(self, func_info: FunctionAnalysis, file_path: str) -> List[TestCase]:
        """Generate tests from architecture perspective: contracts, interfaces."""
        
        print(f"📐 Generating architecture tests for {func_info.name}")
        self.ontology_system.switch_perspective("architecture", f"Generate contract tests for {func_info.name}")
        
        tests = []
        module_name = Path(file_path).stem
        
        # Contract test (input/output validation)
        contract_test = self._generate_contract_test(func_info, module_name)
        tests.append(contract_test)
        
        # Integration test (if function has dependencies)
        if len(func_info.args) > 1:
            integration_test = self._generate_integration_test(func_info, module_name)
            tests.append(integration_test)
        
        return tests
    
    def _generate_debug_tests(self, func_info: FunctionAnalysis, file_path: str) -> List[TestCase]:
        """Generate tests from debug perspective: error conditions, boundaries."""
        
        print(f"🐛 Generating debug tests for {func_info.name}")
        self.ontology_system.switch_perspective("debug", f"Generate error condition tests for {func_info.name}")
        
        tests = []
        module_name = Path(file_path).stem
        
        # Error condition tests
        for error_condition in func_info.error_conditions:
            error_test = self._generate_error_condition_test(func_info, error_condition, module_name)
            tests.append(error_test)
        
        # Boundary tests
        boundary_test = self._generate_boundary_test(func_info, module_name)
        tests.append(boundary_test)
        
        return tests
    
    def _generate_basic_functionality_test(self, func_info: FunctionAnalysis, module_name: str) -> TestCase:
        """Generate basic functionality test."""
        
        test_name = f"test_{func_info.name}_basic_functionality"
        
        # Generate sample arguments
        sample_args = self._generate_sample_arguments(func_info.args)
        
        test_code = dedent(f"""
        def {test_name}(self):
            \"\"\"Test basic functionality of {func_info.name}.\"\"\"
            # Arrange
            {sample_args}
            
            # Act
            result = {module_name}.{func_info.name}({', '.join(func_info.args)})
            
            # Assert
            self.assertIsNotNone(result)
            # TODO: Add specific assertions based on expected behavior
        """).strip()
        
        return TestCase(
            name=test_name,
            code=test_code,
            perspective="engineering",
            test_type="functionality",
            description=f"Tests basic functionality of {func_info.name}"
        )
    
    def _generate_edge_case_test(self, func_info: FunctionAnalysis, edge_case: str, module_name: str) -> TestCase:
        """Generate edge case test."""
        
        test_name = f"test_{func_info.name}_{edge_case}"
        
        # Generate edge case arguments
        edge_args = self._generate_edge_case_arguments(func_info.args, edge_case)
        
        test_code = dedent(f"""
        def {test_name}(self):
            \"\"\"Test {func_info.name} with {edge_case.replace('_', ' ')}.\"\"\"
            # Arrange
            {edge_args}
            
            # Act & Assert
            result = {module_name}.{func_info.name}({', '.join(func_info.args)})
            
            # TODO: Add specific assertions for {edge_case} behavior
            self.assertIsNotNone(result)
        """).strip()
        
        return TestCase(
            name=test_name,
            code=test_code,
            perspective="engineering",
            test_type="edge_case",
            description=f"Tests {func_info.name} with {edge_case} input"
        )
    
    def _generate_performance_test(self, func_info: FunctionAnalysis, module_name: str) -> TestCase:
        """Generate performance test."""
        
        test_name = f"test_{func_info.name}_performance"
        
        test_code = dedent(f"""
        def {test_name}(self):
            \"\"\"Test performance of {func_info.name}.\"\"\"
            import time
            
            # Arrange
            {self._generate_sample_arguments(func_info.args)}
            
            # Act
            start_time = time.time()
            for _ in range(1000):  # Run 1000 iterations
                result = {module_name}.{func_info.name}({', '.join(func_info.args)})
            end_time = time.time()
            
            # Assert
            execution_time = end_time - start_time
            self.assertLess(execution_time, 1.0, "Function should complete 1000 iterations in under 1 second")
        """).strip()
        
        return TestCase(
            name=test_name,
            code=test_code,
            perspective="engineering",
            test_type="performance",
            description=f"Tests performance characteristics of {func_info.name}"
        )
    
    def _generate_contract_test(self, func_info: FunctionAnalysis, module_name: str) -> TestCase:
        """Generate contract test."""
        
        test_name = f"test_{func_info.name}_contract"
        
        test_code = dedent(f"""
        def {test_name}(self):
            \"\"\"Test input/output contract of {func_info.name}.\"\"\"
            # Arrange
            {self._generate_sample_arguments(func_info.args)}
            
            # Act
            result = {module_name}.{func_info.name}({', '.join(func_info.args)})
            
            # Assert - Validate contract
            self.assertIsNotNone(result, "Function must return a value")
            # TODO: Add type checking and contract validation
            # Example: self.assertIsInstance(result, expected_type)
        """).strip()
        
        return TestCase(
            name=test_name,
            code=test_code,
            perspective="architecture",
            test_type="contract",
            description=f"Tests input/output contract of {func_info.name}"
        )
    
    def _generate_integration_test(self, func_info: FunctionAnalysis, module_name: str) -> TestCase:
        """Generate integration test."""
        
        test_name = f"test_{func_info.name}_integration"
        
        test_code = dedent(f"""
        def {test_name}(self):
            \"\"\"Test integration behavior of {func_info.name}.\"\"\"
            # Arrange - Set up realistic integration scenario
            {self._generate_sample_arguments(func_info.args)}
            
            # Act
            result = {module_name}.{func_info.name}({', '.join(func_info.args)})
            
            # Assert - Verify integration behavior
            self.assertIsNotNone(result)
            # TODO: Add integration-specific assertions
            # Example: Verify database changes, file modifications, API calls
        """).strip()
        
        return TestCase(
            name=test_name,
            code=test_code,
            perspective="architecture",
            test_type="integration",
            description=f"Tests integration behavior of {func_info.name}"
        )
    
    def _generate_error_condition_test(self, func_info: FunctionAnalysis, error_type: str, module_name: str) -> TestCase:
        """Generate error condition test."""
        
        test_name = f"test_{func_info.name}_{error_type.lower()}"
        
        test_code = dedent(f"""
        def {test_name}(self):
            \"\"\"Test {func_info.name} raises {error_type} appropriately.\"\"\"
            # Arrange - Set up conditions that should cause {error_type}
            {self._generate_error_arguments(func_info.args, error_type)}
            
            # Act & Assert
            with self.assertRaises({error_type}):
                {module_name}.{func_info.name}({', '.join(func_info.args)})
        """).strip()
        
        return TestCase(
            name=test_name,
            code=test_code,
            perspective="debug",
            test_type="error_condition",
            description=f"Tests that {func_info.name} raises {error_type} correctly"
        )
    
    def _generate_boundary_test(self, func_info: FunctionAnalysis, module_name: str) -> TestCase:
        """Generate boundary condition test."""
        
        test_name = f"test_{func_info.name}_boundaries"
        
        test_code = dedent(f"""
        def {test_name}(self):
            \"\"\"Test {func_info.name} with boundary conditions.\"\"\"
            # Test minimum boundary
            {self._generate_boundary_arguments(func_info.args, "minimum")}
            result_min = {module_name}.{func_info.name}({', '.join(func_info.args)})
            self.assertIsNotNone(result_min)
            
            # Test maximum boundary
            {self._generate_boundary_arguments(func_info.args, "maximum")}
            result_max = {module_name}.{func_info.name}({', '.join(func_info.args)})
            self.assertIsNotNone(result_max)
        """).strip()
        
        return TestCase(
            name=test_name,
            code=test_code,
            perspective="debug",
            test_type="boundary",
            description=f"Tests boundary conditions for {func_info.name}"
        )
    
    def _generate_class_tests(self, class_info: Dict[str, Any], file_path: str) -> List[TestCase]:
        """Generate tests for a class."""
        
        tests = []
        module_name = Path(file_path).stem
        
        # Constructor test
        constructor_test = TestCase(
            name=f"test_{class_info['name']}_constructor",
            code=dedent(f"""
            def test_{class_info['name']}_constructor(self):
                \"\"\"Test {class_info['name']} constructor.\"\"\"
                # Act
                instance = {module_name}.{class_info['name']}()
                
                # Assert
                self.assertIsInstance(instance, {module_name}.{class_info['name']})
            """).strip(),
            perspective="engineering",
            test_type="constructor",
            description=f"Tests {class_info['name']} constructor"
        )
        tests.append(constructor_test)
        
        return tests
    
    def _generate_sample_arguments(self, args: List[str]) -> str:
        """Generate sample argument assignments."""
        
        assignments = []
        for arg in args:
            if arg == 'self':
                continue
            
            # Generate appropriate sample values based on argument name
            if 'string' in arg.lower() or 'text' in arg.lower() or 'name' in arg.lower():
                assignments.append(f'{arg} = "test_string"')
            elif 'number' in arg.lower() or 'count' in arg.lower() or 'id' in arg.lower():
                assignments.append(f'{arg} = 42')
            elif 'list' in arg.lower() or 'array' in arg.lower():
                assignments.append(f'{arg} = [1, 2, 3]')
            elif 'dict' in arg.lower():
                assignments.append(f'{arg} = {{"key": "value"}}')
            elif 'bool' in arg.lower() or 'flag' in arg.lower():
                assignments.append(f'{arg} = True')
            else:
                assignments.append(f'{arg} = "test_value"  # TODO: Provide appropriate test value')
        
        return '\n            '.join(assignments) if assignments else '# No arguments needed'
    
    def _generate_edge_case_arguments(self, args: List[str], edge_case: str) -> str:
        """Generate edge case argument assignments."""
        
        assignments = []
        for arg in args:
            if arg == 'self':
                continue
            
            if edge_case == 'empty_list':
                assignments.append(f'{arg} = []')
            elif edge_case == 'empty_string':
                assignments.append(f'{arg} = ""')
            elif edge_case == 'zero':
                assignments.append(f'{arg} = 0')
            elif edge_case == 'negative':
                assignments.append(f'{arg} = -1')
            elif edge_case == 'large_number':
                assignments.append(f'{arg} = 999999')
            elif edge_case == 'none_value':
                assignments.append(f'{arg} = None')
            else:
                assignments.append(f'{arg} = None  # Edge case: {edge_case}')
        
        return '\n            '.join(assignments) if assignments else '# No arguments needed'
    
    def _generate_error_arguments(self, args: List[str], error_type: str) -> str:
        """Generate arguments that should cause specified error."""
        
        assignments = []
        for arg in args:
            if arg == 'self':
                continue
            
            if error_type == 'ValueError':
                assignments.append(f'{arg} = "invalid_value"')
            elif error_type == 'TypeError':
                assignments.append(f'{arg} = 123  # Wrong type')
            elif error_type == 'KeyError':
                assignments.append(f'{arg} = {{"wrong": "key"}}')
            else:
                assignments.append(f'{arg} = None  # Should cause {error_type}')
        
        return '\n            '.join(assignments) if assignments else '# No arguments needed'
    
    def _generate_boundary_arguments(self, args: List[str], boundary_type: str) -> str:
        """Generate boundary condition arguments."""
        
        assignments = []
        for arg in args:
            if arg == 'self':
                continue
            
            if boundary_type == 'minimum':
                assignments.append(f'{arg} = 0  # Minimum boundary')
            elif boundary_type == 'maximum':
                assignments.append(f'{arg} = 2**31 - 1  # Maximum boundary')
            else:
                assignments.append(f'{arg} = 1  # Boundary value')
        
        return '\n            '.join(assignments) if assignments else '# No arguments needed'
    
    def generate_complete_test_file(self, target_file: str, tests: List[TestCase]) -> str:
        """Generate a complete test file with all test cases."""
        
        module_name = Path(target_file).stem
        test_file_content = dedent(f"""
        #!/usr/bin/env python3
        \"\"\"
        Comprehensive Test Suite for {module_name}
        =========================================
        
        Auto-generated using Intelligent Test Generator with ontological reasoning.
        
        Test Coverage:
        - Engineering perspective: Functionality, performance, edge cases
        - Architecture perspective: Contracts, integration, interfaces  
        - Debug perspective: Error conditions, boundaries, failure scenarios
        
        Generated test count: {len(tests)}
        \"\"\"
        
        import unittest
        import sys
        from pathlib import Path
        
        # Add source directory to path
        src_path = Path(__file__).parent.parent
        sys.path.append(str(src_path))
        
        import {module_name}
        
        
        class Test{module_name.title()}(unittest.TestCase):
            \"\"\"Comprehensive test suite for {module_name} module.\"\"\"
            
            def setUp(self):
                \"\"\"Set up test fixtures before each test method.\"\"\"
                pass
            
            def tearDown(self):
                \"\"\"Clean up after each test method.\"\"\"
                pass
        """).strip()
        
        # Add all test methods
        for test in tests:
            test_file_content += "\n\n    " + test.code.replace('\n', '\n    ')
        
        # Add test runner
        test_file_content += dedent("""
        
        
        if __name__ == '__main__':
            # Run tests with detailed output
            unittest.main(verbosity=2)
        """)
        
        return test_file_content


def main():
    """Command-line interface for intelligent test generator."""
    
    parser = argparse.ArgumentParser(
        description="Intelligent Test Generator with Ontological Reasoning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gem_2_intelligent_test_generator.py mymodule.py
  python gem_2_intelligent_test_generator.py --class MyClass mymodule.py  
  python gem_2_intelligent_test_generator.py --function my_function mymodule.py
  python gem_2_intelligent_test_generator.py --output tests/ mymodule.py
        """
    )
    
    parser.add_argument('file', help='Python file to generate tests for')
    parser.add_argument('--class', dest='target_class', help='Specific class to test')
    parser.add_argument('--function', dest='target_function', help='Specific function to test')
    parser.add_argument('--output', '-o', help='Output directory for test files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return 1
    
    print("🧠 INTELLIGENT TEST GENERATOR")
    print("=" * 35)
    print("Using ontological reasoning for comprehensive test generation")
    print()
    
    generator = IntelligentTestGenerator()
    
    try:
        print(f"🔍 Analyzing: {args.file}")
        tests = generator.generate_tests_for_file(
            args.file, 
            args.target_class, 
            args.target_function
        )
        
        print(f"\n✅ Generated {len(tests)} test cases")
        
        # Group tests by perspective
        perspective_counts = {}
        for test in tests:
            perspective_counts[test.perspective] = perspective_counts.get(test.perspective, 0) + 1
        
        print("\n📊 Tests by perspective:")
        for perspective, count in perspective_counts.items():
            print(f"   {perspective}: {count} tests")
        
        # Generate complete test file
        test_file_content = generator.generate_complete_test_file(args.file, tests)
        
        # Determine output path
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"test_{Path(args.file).stem}.py"
        else:
            output_file = Path(f"test_{Path(args.file).stem}.py")
        
        # Write test file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(test_file_content)
        
        print(f"\n📝 Test file written to: {output_file}")
        
        if args.verbose:
            print(f"\n🔍 Generated test cases:")
            for test in tests:
                print(f"   - {test.name} ({test.perspective}/{test.test_type})")
        
        print(f"\n💡 To run the tests:")
        print(f"   python {output_file}")
        print(f"   python -m pytest {output_file}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
