"""
Software Engineering Masters Rule Integration
============================================

CRITICAL: Integrates Uncle Bob, Martin Fowler, Steve McConnell, and Kent Beck
principles into all development agents automatically.

This module provides the integration layer that embeds masters principles
into agent behavior, ensuring every line of generated code follows the
collective wisdom of software engineering masters.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MastersViolation:
    """Represents a violation of software engineering masters principles."""
    principle: str  # 'uncle_bob', 'fowler', 'mcconnell', 'kent_beck'
    category: str  # 'clean_code', 'refactoring', 'construction', 'xp'
    violation_type: str
    description: str
    suggestion: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    line_number: Optional[int] = None
    file_path: Optional[str] = None


@dataclass
class MastersCompliance:
    """Represents compliance status with masters principles."""
    overall_score: float  # 0.0 to 1.0
    uncle_bob_score: float
    fowler_score: float
    mcconnell_score: float
    kent_beck_score: float
    violations: List[MastersViolation]
    suggestions: List[str]
    compliant: bool


class MastersRuleEnforcer:
    """Enforces software engineering masters principles in generated code."""
    
    def __init__(self):
        self.enforcers = {
            'uncle_bob': UncleBobEnforcer(),
            'fowler': FowlerEnforcer(),
            'mcconnell': McConnellEnforcer(),
            'kent_beck': KentBeckEnforcer()
        }
        self.compliance_threshold = 0.85  # 85% compliance required
    
    def enforce_masters_principles(self, code: str, context: Dict[str, Any] = None) -> MastersCompliance:
        """Enforce all masters principles on generated code."""
        
        violations = []
        suggestions = []
        scores = {}
        
        # Run all enforcement checks
        for master_name, enforcer in self.enforcers.items():
            try:
                result = enforcer.enforce(code, context or {})
                scores[f"{master_name}_score"] = result.score
                violations.extend(result.violations)
                suggestions.extend(result.suggestions)
                
            except Exception as e:
                logger.error(f"Error enforcing {master_name} principles: {e}")
                scores[f"{master_name}_score"] = 0.0
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores) if scores else 0.0
        
        # Determine compliance
        compliant = overall_score >= self.compliance_threshold and len([v for v in violations if v.severity == 'critical']) == 0
        
        return MastersCompliance(
            overall_score=overall_score,
            uncle_bob_score=scores.get('uncle_bob_score', 0.0),
            fowler_score=scores.get('fowler_score', 0.0),
            mcconnell_score=scores.get('mcconnell_score', 0.0),
            kent_beck_score=scores.get('kent_beck_score', 0.0),
            violations=violations,
            suggestions=suggestions,
            compliant=compliant
        )
    
    def get_improvement_suggestions(self, violations: List[MastersViolation]) -> List[str]:
        """Generate specific improvement suggestions based on violations."""
        
        suggestions = []
        
        # Group violations by category
        violation_categories = {}
        for violation in violations:
            category = violation.category
            if category not in violation_categories:
                violation_categories[category] = []
            violation_categories[category].append(violation)
        
        # Generate category-specific suggestions
        for category, category_violations in violation_categories.items():
            if category == 'clean_code':
                suggestions.extend(self._get_clean_code_suggestions(category_violations))
            elif category == 'refactoring':
                suggestions.extend(self._get_refactoring_suggestions(category_violations))
            elif category == 'construction':
                suggestions.extend(self._get_construction_suggestions(category_violations))
            elif category == 'xp':
                suggestions.extend(self._get_xp_suggestions(category_violations))
        
        return suggestions
    
    def _get_clean_code_suggestions(self, violations: List[MastersViolation]) -> List[str]:
        """Get Uncle Bob clean code suggestions."""
        suggestions = []
        
        violation_types = {v.violation_type for v in violations}
        
        if 'function_too_long' in violation_types:
            suggestions.append("Break large functions into smaller, focused functions (max 20 lines)")
        
        if 'poor_naming' in violation_types:
            suggestions.append("Use intention-revealing names that clearly express purpose")
        
        if 'too_many_parameters' in violation_types:
            suggestions.append("Reduce function parameters to 3 or fewer, consider parameter objects")
        
        if 'obvious_comments' in violation_types:
            suggestions.append("Remove obvious comments, let code be self-documenting")
        
        return suggestions
    
    def _get_refactoring_suggestions(self, violations: List[MastersViolation]) -> List[str]:
        """Get Fowler refactoring suggestions."""
        suggestions = []
        
        violation_types = {v.violation_type for v in violations}
        
        if 'code_duplication' in violation_types:
            suggestions.append("Extract common functionality to eliminate duplication")
        
        if 'long_method' in violation_types:
            suggestions.append("Apply Extract Method refactoring to break down long methods")
        
        if 'large_class' in violation_types:
            suggestions.append("Apply Extract Class refactoring to separate responsibilities")
        
        if 'switch_statements' in violation_types:
            suggestions.append("Replace conditional logic with polymorphism")
        
        return suggestions
    
    def _get_construction_suggestions(self, violations: List[MastersViolation]) -> List[str]:
        """Get McConnell construction suggestions."""
        suggestions = []
        
        violation_types = {v.violation_type for v in violations}
        
        if 'poor_error_handling' in violation_types:
            suggestions.append("Implement comprehensive error handling with specific exception types")
        
        if 'missing_validation' in violation_types:
            suggestions.append("Add input validation and defensive programming practices")
        
        if 'no_documentation' in violation_types:
            suggestions.append("Add comprehensive documentation with examples")
        
        return suggestions
    
    def _get_xp_suggestions(self, violations: List[MastersViolation]) -> List[str]:
        """Get Kent Beck XP suggestions.""" 
        suggestions = []
        
        violation_types = {v.violation_type for v in violations}
        
        if 'no_tests' in violation_types:
            suggestions.append("Write tests first following TDD red-green-refactor cycle")
        
        if 'complex_solution' in violation_types:
            suggestions.append("Simplify: Do the simplest thing that could possibly work")
        
        if 'poor_communication' in violation_types:
            suggestions.append("Improve code communication through better naming and structure")
        
        return suggestions


class MastersPrincipleEnforcer(ABC):
    """Abstract base class for individual masters principle enforcers."""
    
    @abstractmethod
    def enforce(self, code: str, context: Dict[str, Any]) -> 'EnforcementResult':
        """Enforce specific master's principles on code."""
        pass


@dataclass 
class EnforcementResult:
    """Result of enforcement check."""
    score: float
    violations: List[MastersViolation]
    suggestions: List[str]
    compliant: bool


class UncleBobEnforcer(MastersPrincipleEnforcer):
    """Enforces Uncle Bob's Clean Code principles."""
    
    def enforce(self, code: str, context: Dict[str, Any]) -> EnforcementResult:
        """Enforce Uncle Bob's clean code principles."""
        
        violations = []
        suggestions = []
        score = 1.0
        
        # Check function length
        violations.extend(self._check_function_length(code))
        
        # Check naming conventions
        violations.extend(self._check_naming_conventions(code))
        
        # Check function parameters
        violations.extend(self._check_function_parameters(code))
        
        # Check comments
        violations.extend(self._check_comments(code))
        
        # Calculate score based on violations
        critical_violations = len([v for v in violations if v.severity == 'critical'])
        high_violations = len([v for v in violations if v.severity == 'high'])
        
        if critical_violations > 0:
            score -= 0.5
        score -= (high_violations * 0.1)
        score = max(0.0, score)
        
        return EnforcementResult(
            score=score,
            violations=violations,
            suggestions=suggestions,
            compliant=score >= 0.8 and critical_violations == 0
        )
    
    def _check_function_length(self, code: str) -> List[MastersViolation]:
        """Check if functions are too long (Uncle Bob: max 20 lines)."""
        violations = []
        
        lines = code.split('\n')
        in_function = False
        function_start = 0
        function_name = ""
        indent_level = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Detect function start
            if stripped.startswith('def ') and ':' in stripped:
                if in_function and (i - function_start) > 20:
                    violations.append(MastersViolation(
                        principle='uncle_bob',
                        category='clean_code',
                        violation_type='function_too_long',
                        description=f"Function '{function_name}' is {i - function_start} lines (max: 20)",
                        suggestion="Break into smaller, focused functions",
                        severity='high',
                        line_number=function_start + 1
                    ))
                
                in_function = True
                function_start = i
                function_name = stripped.split('(')[0].replace('def ', '')
                indent_level = len(line) - len(line.lstrip())
            
            # Detect function end
            elif in_function and line.strip() and len(line) - len(line.lstrip()) <= indent_level and not line.startswith(' '):
                if stripped and not stripped.startswith('#'):
                    if (i - function_start) > 20:
                        violations.append(MastersViolation(
                            principle='uncle_bob',
                            category='clean_code',
                            violation_type='function_too_long',
                            description=f"Function '{function_name}' is {i - function_start} lines (max: 20)",
                            suggestion="Break into smaller, focused functions",
                            severity='high',
                            line_number=function_start + 1
                        ))
                    in_function = False
        
        return violations
    
    def _check_naming_conventions(self, code: str) -> List[MastersViolation]:
        """Check naming conventions (intention-revealing names)."""
        violations = []
        
        # Check for short, non-descriptive variable names
        import re
        
        # Find variable assignments
        var_pattern = r'(\w+)\s*='
        matches = re.finditer(var_pattern, code)
        
        for match in matches:
            var_name = match.group(1)
            if len(var_name) < 3 and var_name not in ['i', 'j', 'k', 'x', 'y', 'z']:
                violations.append(MastersViolation(
                    principle='uncle_bob',
                    category='clean_code',
                    violation_type='poor_naming',
                    description=f"Variable name '{var_name}' is too short and non-descriptive",
                    suggestion="Use intention-revealing names",
                    severity='medium'
                ))
        
        return violations
    
    def _check_function_parameters(self, code: str) -> List[MastersViolation]:
        """Check function parameter count (Uncle Bob: max 3)."""
        violations = []
        
        import re
        
        # Find function definitions
        func_pattern = r'def\s+(\w+)\s*\(([^)]*)\)'
        matches = re.finditer(func_pattern, code)
        
        for match in matches:
            func_name = match.group(1)
            params = match.group(2)
            
            if params.strip():
                param_count = len([p for p in params.split(',') if p.strip() and not p.strip().startswith('*')])
                
                # Exclude 'self' from count
                if 'self' in params:
                    param_count -= 1
                
                if param_count > 3:
                    violations.append(MastersViolation(
                        principle='uncle_bob',
                        category='clean_code',
                        violation_type='too_many_parameters',
                        description=f"Function '{func_name}' has {param_count} parameters (max: 3)",
                        suggestion="Consider parameter objects or reduce function scope",
                        severity='medium'
                    ))
        
        return violations
    
    def _check_comments(self, code: str) -> List[MastersViolation]:
        """Check for obvious/redundant comments."""
        violations = []
        
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#'):
                comment = stripped[1:].strip().lower()
                
                # Check for obvious comments
                obvious_patterns = [
                    'initialize', 'set to', 'increment', 'decrement',
                    'return the', 'loop through', 'check if'
                ]
                
                for pattern in obvious_patterns:
                    if pattern in comment:
                        violations.append(MastersViolation(
                            principle='uncle_bob',
                            category='clean_code',
                            violation_type='obvious_comments',
                            description=f"Comment states the obvious: '{comment}'",
                            suggestion="Remove obvious comments, let code be self-documenting",
                            severity='low',
                            line_number=i + 1
                        ))
                        break
        
        return violations


class FowlerEnforcer(MastersPrincipleEnforcer):
    """Enforces Martin Fowler's refactoring principles."""
    
    def enforce(self, code: str, context: Dict[str, Any]) -> EnforcementResult:
        """Enforce Fowler's refactoring principles."""
        
        violations = []
        suggestions = []
        score = 1.0
        
        # Check for code smells
        violations.extend(self._check_code_duplication(code))
        violations.extend(self._check_long_methods(code))
        violations.extend(self._check_large_classes(code))
        violations.extend(self._check_switch_statements(code))
        
        # Advanced Fowler refactoring patterns
        violations.extend(self._check_fowler_advanced_patterns(code))
        
        # Calculate score
        critical_violations = len([v for v in violations if v.severity == 'critical'])
        high_violations = len([v for v in violations if v.severity == 'high'])
        
        if critical_violations > 0:
            score -= 0.4
        score -= (high_violations * 0.1)
        score = max(0.0, score)
        
        return EnforcementResult(
            score=score,
            violations=violations,
            suggestions=suggestions,
            compliant=score >= 0.8
        )
    
    def _check_code_duplication(self, code: str) -> List[MastersViolation]:
        """Check for code duplication."""
        violations = []
        
        lines = code.split('\n')
        line_counts = {}
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                if stripped in line_counts:
                    line_counts[stripped].append(i + 1)
                else:
                    line_counts[stripped] = [i + 1]
        
        for line_content, line_numbers in line_counts.items():
            if len(line_numbers) > 2:  # Appears more than twice
                violations.append(MastersViolation(
                    principle='fowler',
                    category='refactoring',
                    violation_type='code_duplication',
                    description=f"Duplicated line appears {len(line_numbers)} times: '{line_content[:50]}...'",
                    suggestion="Extract common functionality to eliminate duplication",
                    severity='high'
                ))
        
        return violations
    
    def _check_long_methods(self, code: str) -> List[MastersViolation]:
        """Check for long methods that need extraction."""
        # This is similar to Uncle Bob's function length check but with different thresholds
        violations = []
        
        lines = code.split('\n')
        in_function = False
        function_start = 0
        function_name = ""
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if stripped.startswith('def ') and ':' in stripped:
                if in_function and (i - function_start) > 15:  # Fowler: 15 lines
                    violations.append(MastersViolation(
                        principle='fowler',
                        category='refactoring',
                        violation_type='long_method',
                        description=f"Method '{function_name}' is {i - function_start} lines (consider refactoring at 15+)",
                        suggestion="Apply Extract Method refactoring",
                        severity='medium',
                        line_number=function_start + 1
                    ))
                
                in_function = True
                function_start = i
                function_name = stripped.split('(')[0].replace('def ', '')
        
        return violations
    
    def _check_large_classes(self, code: str) -> List[MastersViolation]:
        """Check for large classes that need extraction."""
        violations = []
        
        import re
        
        # Find class definitions and count their methods
        class_pattern = r'class\s+(\w+).*?:'
        method_pattern = r'\s+def\s+\w+\s*\('
        
        classes = re.finditer(class_pattern, code)
        
        for class_match in classes:
            class_name = class_match.group(1)
            class_start = class_match.end()
            
            # Count methods in this class
            remaining_code = code[class_start:]
            next_class = re.search(class_pattern, remaining_code)
            
            if next_class:
                class_code = remaining_code[:next_class.start()]
            else:
                class_code = remaining_code
            
            methods = re.findall(method_pattern, class_code)
            
            if len(methods) > 10:  # More than 10 methods
                violations.append(MastersViolation(
                    principle='fowler',
                    category='refactoring',
                    violation_type='large_class',
                    description=f"Class '{class_name}' has {len(methods)} methods (consider refactoring at 10+)",
                    suggestion="Apply Extract Class refactoring to separate responsibilities",
                    severity='medium'
                ))
        
        return violations
    
    def _check_switch_statements(self, code: str) -> List[MastersViolation]:
        """Check for switch statements that could be polymorphism."""
        violations = []
        
        # Check for if-elif chains that could be polymorphism
        lines = code.split('\n')
        elif_count = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('if '):
                elif_count = 0
            elif stripped.startswith('elif '):
                elif_count += 1
                if elif_count >= 3:  # 3+ elif statements
                    violations.append(MastersViolation(
                        principle='fowler',
                        category='refactoring',
                        violation_type='switch_statements',
                        description=f"Long if-elif chain detected ({elif_count + 1} conditions)",
                        suggestion="Replace conditional logic with polymorphism",
                        severity='medium',
                        line_number=i + 1
                    ))
                    elif_count = 0  # Reset to avoid duplicate reports
        
        return violations
    
    def _check_fowler_advanced_patterns(self, code: str) -> List[MastersViolation]:
        """Check advanced Fowler refactoring patterns and design improvements."""
        violations = []
        lines = code.split('\n')
        
        # 1. Feature Envy - method uses more data from another class
        violations.extend(self._check_feature_envy(lines))
        
        # 2. Data Clumps - groups of data that always appear together  
        violations.extend(self._check_data_clumps(lines))
        
        # 3. Primitive Obsession - overuse of primitives
        violations.extend(self._check_primitive_obsession(code))
        
        # 4. Divergent Change - class changed for different reasons
        violations.extend(self._check_divergent_change(code))
        
        return violations
    
    def _check_feature_envy(self, lines: List[str]) -> List[MastersViolation]:
        """Check for Feature Envy code smell (Fowler)."""
        violations = []
        
        for i, line in enumerate(lines):
            if 'def ' in line and not line.strip().startswith('def __'):
                # Analyze next 15 lines for data access patterns
                method_lines = lines[i:i+15]
                own_data_refs = sum(1 for l in method_lines if 'self.' in l and l.count('.') == 1)
                external_data_refs = sum(1 for l in method_lines if l.count('.') > 1 and 'self.' not in l)
                
                if external_data_refs > own_data_refs and own_data_refs > 0:
                    method_name = line.split('def ')[1].split('(')[0] if 'def ' in line else 'unknown'
                    violations.append(MastersViolation(
                        principle='fowler',
                        category='refactoring',
                        violation_type='feature_envy',
                        description=f"Method '{method_name}' shows feature envy - prefers external data",
                        suggestion="Move method to the class it envies (Fowler: Move Method)",
                        severity='medium',
                        line_number=i + 1
                    ))
        
        return violations
    
    def _check_data_clumps(self, lines: List[str]) -> List[MastersViolation]:
        """Check for Data Clumps code smell (Fowler)."""
        violations = []
        
        param_patterns = {}
        for i, line in enumerate(lines):
            if 'def ' in line and '(' in line and ')' in line:
                # Extract parameters
                params_section = line[line.find('(')+1:line.find(')')]
                params = [p.strip().split(':')[0].strip() for p in params_section.split(',') 
                         if p.strip() and p.strip() != 'self']
                
                if len(params) > 3:  # Methods with many parameters
                    param_signature = tuple(sorted(params))
                    param_patterns[param_signature] = param_patterns.get(param_signature, 0) + 1
        
        for params, count in param_patterns.items():
            if count > 1 and len(params) > 3:
                violations.append(MastersViolation(
                    principle='fowler',
                    category='refactoring',
                    violation_type='data_clumps',
                    description=f"Parameter group appears {count} times: {', '.join(params[:3])}...",
                    suggestion="Introduce Parameter Object (Fowler: Introduce Parameter Object)",
                    severity='low',
                    line_number=1
                ))
        
        return violations
    
    def _check_primitive_obsession(self, code: str) -> List[MastersViolation]:
        """Check for Primitive Obsession code smell (Fowler)."""
        violations = []
        
        # Count primitive type usage
        primitives = ['str', 'int', 'float', 'bool', 'list', 'dict', 'tuple']
        primitive_count = sum(code.count(f': {ptype}') + code.count(f'-> {ptype}') for ptype in primitives)
        
        if primitive_count > 12:  # High primitive usage
            violations.append(MastersViolation(
                principle='fowler',
                category='refactoring',
                violation_type='primitive_obsession',
                description=f"Heavy use of primitive types ({primitive_count} annotations)",
                suggestion="Replace primitives with domain objects (Fowler: Replace Type Code with Class)",
                severity='low',
                line_number=1
            ))
        
        return violations
    
    def _check_divergent_change(self, code: str) -> List[MastersViolation]:
        """Check for Divergent Change code smell (Fowler)."""
        violations = []
        
        if 'class ' in code:
            # Extract method names and analyze responsibilities
            method_names = re.findall(r'def\s+(\w+)', code)
            if len(method_names) > 6:
                responsibilities = set()
                
                for method in method_names:
                    method_lower = method.lower()
                    # Categorize by responsibility indicators
                    if any(word in method_lower for word in ['save', 'store', 'persist', 'write']):
                        responsibilities.add('persistence')
                    if any(word in method_lower for word in ['validate', 'check', 'verify']):
                        responsibilities.add('validation')  
                    if any(word in method_lower for word in ['format', 'display', 'render']):
                        responsibilities.add('presentation')
                    if any(word in method_lower for word in ['calculate', 'compute', 'process']):
                        responsibilities.add('computation')
                    if any(word in method_lower for word in ['send', 'notify', 'email']):
                        responsibilities.add('communication')
                
                if len(responsibilities) > 2:
                    violations.append(MastersViolation(
                        principle='fowler',
                        category='refactoring',
                        violation_type='divergent_change',
                        description=f"Class handles {len(responsibilities)} different responsibilities",
                        suggestion="Extract classes by responsibility (Fowler: Extract Class)",
                        severity='medium',
                        line_number=1
                    ))
        
        return violations


class McConnellEnforcer(MastersPrincipleEnforcer):
    """Enforces Steve McConnell's Code Complete practices."""
    
    def enforce(self, code: str, context: Dict[str, Any]) -> EnforcementResult:
        """Enforce McConnell's construction practices."""
        
        violations = []
        suggestions = []
        score = 1.0
        
        # Check construction quality
        violations.extend(self._check_error_handling(code))
        violations.extend(self._check_input_validation(code))
        violations.extend(self._check_documentation(code))
        
        # Advanced McConnell construction practices
        violations.extend(self._check_mcconnell_advanced_practices(code))
        
        # Calculate score
        critical_violations = len([v for v in violations if v.severity == 'critical'])
        high_violations = len([v for v in violations if v.severity == 'high'])
        
        if critical_violations > 0:
            score -= 0.6
        score -= (high_violations * 0.15)
        score = max(0.0, score)
        
        return EnforcementResult(
            score=score,
            violations=violations,
            suggestions=suggestions,
            compliant=score >= 0.8
        )
    
    def _check_error_handling(self, code: str) -> List[MastersViolation]:
        """Check for proper error handling."""
        violations = []
        
        # Check for try-except blocks
        has_try_except = 'try:' in code and 'except' in code
        
        # Check for functions that should have error handling
        import re
        
        # Functions that typically need error handling
        risky_patterns = [
            r'open\s*\(',  # File operations
            r'\.read\s*\(',  # File reading
            r'\.write\s*\(',  # File writing
            r'requests\.',  # HTTP requests
            r'json\.loads',  # JSON parsing
            r'int\s*\(',  # Type conversion
            r'float\s*\(',  # Type conversion
        ]
        
        has_risky_operations = any(re.search(pattern, code) for pattern in risky_patterns)
        
        if has_risky_operations and not has_try_except:
            violations.append(MastersViolation(
                principle='mcconnell',
                category='construction',
                violation_type='poor_error_handling',
                description="Code contains risky operations without error handling",
                suggestion="Add comprehensive error handling with specific exception types",
                severity='high'
            ))
        
        return violations
    
    def _check_input_validation(self, code: str) -> List[MastersViolation]:
        """Check for input validation."""
        violations = []
        
        # Check for functions with parameters but no validation
        import re
        
        func_pattern = r'def\s+(\w+)\s*\(([^)]+)\):'
        matches = re.finditer(func_pattern, code)
        
        for match in matches:
            func_name = match.group(1)
            params = match.group(2)
            
            if 'self' not in params:  # Skip methods with only self
                # Look for validation in function body
                func_start = match.end()
                func_lines = code[func_start:].split('\n')
                
                # Look for validation patterns
                validation_patterns = [
                    r'if\s+not\s+\w+',  # if not param
                    r'if\s+\w+\s+is\s+None',  # if param is None
                    r'isinstance\s*\(',  # type checking
                    r'raise\s+ValueError',  # value validation
                ]
                
                has_validation = any(
                    any(re.search(pattern, line) for pattern in validation_patterns)
                    for line in func_lines[:10]  # Check first 10 lines
                )
                
                if not has_validation:
                    violations.append(MastersViolation(
                        principle='mcconnell',
                        category='construction',
                        violation_type='missing_validation',
                        description=f"Function '{func_name}' lacks input validation",
                        suggestion="Add input validation and defensive programming",
                        severity='medium'
                    ))
        
        return violations
    
    def _check_documentation(self, code: str) -> List[MastersViolation]:
        """Check for proper documentation."""
        violations = []
        
        import re
        
        # Check for functions without docstrings
        func_pattern = r'def\s+(\w+)\s*\([^)]*\):\s*(?:\n\s*""".*?""")?'
        functions = re.finditer(r'def\s+(\w+)\s*\([^)]*\):', code)
        
        for func_match in functions:
            func_name = func_match.group(1)
            
            # Skip private methods and special methods
            if func_name.startswith('_'):
                continue
            
            # Check if function has docstring
            func_start = func_match.end()
            following_lines = code[func_start:].split('\n')[:3]
            
            has_docstring = any('"""' in line or "'''" in line for line in following_lines)
            
            if not has_docstring:
                violations.append(MastersViolation(
                    principle='mcconnell',
                    category='construction',
                    violation_type='no_documentation',
                    description=f"Public function '{func_name}' lacks documentation",
                    suggestion="Add comprehensive documentation with examples",
                    severity='medium'
                ))
        
        return violations
    
    def _check_mcconnell_advanced_practices(self, code: str) -> List[MastersViolation]:
        """Check advanced McConnell construction practices."""
        violations = []
        
        # 1. Defensive Programming - Assertions and Preconditions
        violations.extend(self._check_defensive_programming(code))
        
        # 2. Resource Management - Proper cleanup and context managers
        violations.extend(self._check_resource_management(code))
        
        # 3. Debugging Aids - Logging and debugging support
        violations.extend(self._check_debugging_aids(code))
        
        # 4. Performance Considerations - Algorithmic efficiency
        violations.extend(self._check_performance_practices(code))
        
        return violations
    
    def _check_defensive_programming(self, code: str) -> List[MastersViolation]:
        """Check for defensive programming practices (McConnell)."""
        violations = []
        
        # Check for assertion usage
        assertion_count = code.count('assert ')
        func_count = code.count('def ')
        
        if func_count > 3 and assertion_count == 0:
            violations.append(MastersViolation(
                principle='mcconnell',
                category='construction',
                violation_type='missing_assertions',
                description="No assertions found - consider adding precondition checks",
                suggestion="Add assertions for critical preconditions (McConnell: Defensive Programming)",
                severity='low',
                line_number=1
            ))
        
        # Check for parameter validation patterns
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if 'def ' in line and '(' in line:
                # Look for validation in next few lines
                validation_found = False
                for j in range(i+1, min(i+5, len(lines))):
                    if any(keyword in lines[j].lower() for keyword in ['if not', 'assert', 'raise', 'check']):
                        validation_found = True
                        break
                
                if not validation_found and 'self' not in line:
                    func_name = line.split('def ')[1].split('(')[0]
                    violations.append(MastersViolation(
                        principle='mcconnell',
                        category='construction',
                        violation_type='missing_parameter_validation',
                        description=f"Function '{func_name}' lacks parameter validation",
                        suggestion="Add parameter validation at function entry (McConnell: Defensive Programming)",
                        severity='medium',
                        line_number=i + 1
                    ))
        
        return violations
    
    def _check_resource_management(self, code: str) -> List[MastersViolation]:
        """Check for proper resource management (McConnell)."""
        violations = []
        
        # Check for file operations without context managers
        if 'open(' in code and 'with open(' not in code:
            violations.append(MastersViolation(
                principle='mcconnell',
                category='construction',
                violation_type='poor_resource_management',
                description="File operations without context managers detected",
                suggestion="Use 'with open()' for automatic resource cleanup (McConnell: Resource Management)",
                severity='medium',
                line_number=1
            ))
        
        # Check for database connections without proper cleanup
        db_patterns = ['connect(', 'cursor(', 'execute(']
        if any(pattern in code for pattern in db_patterns) and 'close()' not in code:
            violations.append(MastersViolation(
                principle='mcconnell',
                category='construction',
                violation_type='database_resource_leak',
                description="Database operations without explicit cleanup",
                suggestion="Ensure database connections are properly closed (McConnell: Resource Management)",
                severity='high',
                line_number=1
            ))
        
        return violations
    
    def _check_debugging_aids(self, code: str) -> List[MastersViolation]:
        """Check for debugging and logging support (McConnell)."""
        violations = []
        
        # Check for logging in complex functions
        func_count = code.count('def ')
        total_lines = len([l for l in code.split('\n') if l.strip()])
        
        if total_lines > 50 and func_count > 3:
            logging_indicators = ['logging.', 'logger.', 'log.', 'print(']
            has_logging = any(indicator in code for indicator in logging_indicators)
            
            if not has_logging:
                violations.append(MastersViolation(
                    principle='mcconnell',
                    category='construction',
                    violation_type='missing_logging',
                    description="Complex code without logging or debugging support",
                    suggestion="Add logging for debugging and monitoring (McConnell: Debugging Aids)",
                    severity='low',
                    line_number=1
                ))
        
        return violations
    
    def _check_performance_practices(self, code: str) -> List[MastersViolation]:
        """Check for performance considerations (McConnell)."""
        violations = []
        
        # Check for inefficient patterns
        lines = code.split('\n')
        
        # Check for loops with inefficient operations
        for i, line in enumerate(lines):
            if 'for ' in line and 'in ' in line:
                # Look for expensive operations in loops
                loop_body = lines[i:i+10]  # Check next 10 lines
                expensive_ops = ['.append(', '.extend(', '+= ', 'print(']
                
                for j, loop_line in enumerate(loop_body):
                    if any(op in loop_line for op in expensive_ops):
                        violations.append(MastersViolation(
                            principle='mcconnell',
                            category='construction',
                            violation_type='inefficient_loop_operation',
                            description=f"Potentially expensive operation in loop at line {i+j+1}",
                            suggestion="Consider optimizing loop operations (McConnell: Performance)",
                            severity='low',
                            line_number=i + j + 1
                        ))
                        break
        
        # Check for repeated expensive operations
        expensive_patterns = ['re.compile(', 'json.loads(', 'requests.get(']
        for pattern in expensive_patterns:
            if code.count(pattern) > 2:
                violations.append(MastersViolation(
                    principle='mcconnell',
                    category='construction',
                    violation_type='repeated_expensive_operation',
                    description=f"Repeated expensive operation: {pattern}",
                    suggestion="Cache expensive operations outside loops (McConnell: Performance)",
                    severity='low',
                    line_number=1
                ))
        
        return violations


class KentBeckEnforcer(MastersPrincipleEnforcer):
    """Enforces Kent Beck's Extreme Programming principles."""
    
    def enforce(self, code: str, context: Dict[str, Any]) -> EnforcementResult:
        """Enforce Kent Beck's XP principles."""
        
        violations = []
        suggestions = []
        score = 1.0
        
        # Check XP practices
        violations.extend(self._check_test_presence(code, context))
        violations.extend(self._check_simplicity(code))
        violations.extend(self._check_communication(code))
        
        # Calculate score
        critical_violations = len([v for v in violations if v.severity == 'critical'])
        high_violations = len([v for v in violations if v.severity == 'high'])
        
        if critical_violations > 0:
            score -= 0.5
        score -= (high_violations * 0.2)
        score = max(0.0, score)
        
        return EnforcementResult(
            score=score,
            violations=violations,
            suggestions=suggestions,
            compliant=score >= 0.8
        )
    
    def _check_test_presence(self, code: str, context: Dict[str, Any]) -> List[MastersViolation]:
        """Check for test-first development."""
        violations = []
        
        # If this is production code, check if tests exist
        is_test_file = 'test' in context.get('file_path', '').lower()
        
        if not is_test_file:
            # Check if there are corresponding test functions
            import re
            
            functions = re.findall(r'def\s+(\w+)\s*\(', code)
            public_functions = [f for f in functions if not f.startswith('_')]
            
            if public_functions and not any('test' in f for f in functions):
                violations.append(MastersViolation(
                    principle='kent_beck',
                    category='xp',
                    violation_type='no_tests',
                    description=f"Code has {len(public_functions)} public functions but no tests",
                    suggestion="Write tests first following TDD red-green-refactor cycle",
                    severity='high'
                ))
        
        return violations
    
    def _check_simplicity(self, code: str) -> List[MastersViolation]:
        """Check for simplicity (YAGNI principle)."""
        violations = []
        
        # Check for overly complex solutions
        complexity_indicators = [
            ('class.*Factory', 'Factory pattern may be over-engineering'),
            ('class.*Builder', 'Builder pattern may be over-engineering'),
            ('class.*Strategy', 'Strategy pattern may be premature'),
            ('class.*Observer', 'Observer pattern may be premature'),
            ('abstract.*class', 'Abstract classes may be over-engineering'),
        ]
        
        for pattern, message in complexity_indicators:
            import re
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(MastersViolation(
                    principle='kent_beck',
                    category='xp',
                    violation_type='complex_solution',
                    description=f"Potentially over-engineered solution detected: {message}",
                    suggestion="Simplify: Do the simplest thing that could possibly work",
                    severity='low'
                ))
        
        return violations
    
    def _check_communication(self, code: str) -> List[MastersViolation]:
        """Check for clear communication through code."""
        violations = []
        
        # Check for unclear variable names
        import re
        
        unclear_names = re.findall(r'\b([a-z]{1,2}|data\d*|temp\d*|val\d*)\b', code)
        
        if unclear_names:
            violations.append(MastersViolation(
                principle='kent_beck',
                category='xp',
                violation_type='poor_communication',
                description=f"Unclear variable names found: {set(unclear_names)}",
                suggestion="Use communicative names that express intent clearly",
                severity='medium'
            ))
        
        return violations


class MastersIntegratedAgent:
    """Mixin class to integrate masters principles into agents."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.masters_enforcer = MastersRuleEnforcer()
        self.masters_enabled = True
    
    def apply_masters_principles(self, generated_code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Apply software engineering masters principles to generated code."""
        
        if not self.masters_enabled:
            return {
                'code': generated_code,
                'masters_compliance': None,
                'improvements_applied': False
            }
        
        try:
            # Enforce masters principles
            compliance = self.masters_enforcer.enforce_masters_principles(generated_code, context)
            
            # Generate improvement suggestions
            if not compliance.compliant:
                improved_code = self._apply_automatic_improvements(generated_code, compliance)
                
                # Re-check compliance after improvements
                improved_compliance = self.masters_enforcer.enforce_masters_principles(improved_code, context)
                
                return {
                    'code': improved_code,
                    'masters_compliance': improved_compliance,
                    'improvements_applied': True,
                    'original_compliance': compliance
                }
            
            return {
                'code': generated_code,
                'masters_compliance': compliance,
                'improvements_applied': False
            }
            
        except Exception as e:
            logger.error(f"Error applying masters principles: {e}")
            return {
                'code': generated_code,
                'masters_compliance': None,
                'improvements_applied': False,
                'error': str(e)
            }
    
    def _apply_automatic_improvements(self, code: str, compliance: MastersCompliance) -> str:
        """Apply automatic improvements based on violations."""
        
        improved_code = code
        
        # Apply improvements for specific violation types
        for violation in compliance.violations:
            if violation.severity in ['critical', 'high']:
                improved_code = self._fix_violation(improved_code, violation)
        
        return improved_code
    
    def _fix_violation(self, code: str, violation: MastersViolation) -> str:
        """Attempt to automatically fix a specific violation."""
        
        # This is a simplified example - in practice, you'd have more sophisticated fixes
        if violation.violation_type == 'obvious_comments':
            # Remove obvious comments
            lines = code.split('\n')
            if violation.line_number:
                line_idx = violation.line_number - 1
                if 0 <= line_idx < len(lines):
                    line = lines[line_idx]
                    if line.strip().startswith('#'):
                        lines[line_idx] = ''  # Remove the comment line
            return '\n'.join(lines)
        
        # For other violations, return original code
        # In a full implementation, you'd add more automatic fixes
        return code
    
    def get_masters_prompt_enhancement(self) -> str:
        """Get prompt enhancement text for masters principles."""
        
        return """
CRITICAL: Apply Software Engineering Masters Principles

Your code must embody the collective wisdom of:

🎯 **Uncle Bob's Clean Code:**
- Functions ≤ 20 lines, do one thing well
- Intention-revealing names, no abbreviations  
- ≤ 3 function parameters
- Comments explain WHY, not WHAT

🔄 **Martin Fowler's Refactoring:**
- Eliminate code duplication immediately
- Extract methods for complex logic
- Replace conditionals with polymorphism
- Apply systematic refactoring patterns

🏗️ **Steve McConnell's Construction:**
- Comprehensive error handling with specific exceptions
- Input validation and defensive programming
- Complete documentation with examples
- Engineering discipline in all construction

⚡ **Kent Beck's XP:**
- Write tests first (TDD red-green-refactor)
- Do the simplest thing that could possibly work
- Communicate intent clearly through code
- Practice courage, simplicity, feedback, communication

Generate code that would make these masters proud!
"""


# Export the main integration components
__all__ = [
    'MastersRuleEnforcer',
    'MastersIntegratedAgent', 
    'MastersCompliance',
    'MastersViolation'
]
