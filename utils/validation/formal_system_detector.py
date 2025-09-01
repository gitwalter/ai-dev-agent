#!/usr/bin/env python3
"""
Formal System Detection and Validation Engine

This module provides automatic detection and validation of:
1. File correctness against formal system rules
2. Rule applicability determination
3. Real-time compliance monitoring
4. Systematic enforcement across all system layers

Based on our formal system mathematics and organization rules.
"""

import os
import re
import ast
import yaml
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Import our formal system foundation
from utils.validation.mathematical_system_foundation import (
    MathematicalSystemFoundation,
    Operation,
    LayerIndex,
    MathematicalValidationResult
)


class ValidationLevel(Enum):
    """Validation levels for formal system compliance."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ADVISORY = "advisory"


class RuleCategory(Enum):
    """Categories of formal system rules."""
    NAMING_CONVENTIONS = "naming_conventions"
    FILE_ORGANIZATION = "file_organization"
    DOCUMENTATION_CONSISTENCY = "documentation_consistency"
    SEMANTIC_COHERENCE = "semantic_coherence"
    MATHEMATICAL_FOUNDATION = "mathematical_foundation"
    ETHICAL_COMPLIANCE = "ethical_compliance"
    DIVINE_ALIGNMENT = "divine_alignment"
    HARMONIC_INTEGRATION = "harmonic_integration"


@dataclass
class ValidationIssue:
    """Represents a validation issue found during formal system analysis."""
    rule_id: str
    category: RuleCategory
    level: ValidationLevel
    file_path: str
    line_number: Optional[int]
    message: str
    suggestion: str
    auto_fixable: bool
    mathematical_basis: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FileAnalysisResult:
    """Results of formal system analysis for a single file."""
    file_path: str
    is_compliant: bool
    compliance_score: float
    applicable_rules: List[str]
    validation_issues: List[ValidationIssue]
    mathematical_validation: Optional[MathematicalValidationResult]
    layer_assignment: LayerIndex
    semantic_category: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SystemComplianceReport:
    """Comprehensive system-wide compliance report."""
    overall_compliance_score: float
    total_files_analyzed: int
    compliant_files: int
    non_compliant_files: int
    file_results: List[FileAnalysisResult]
    rule_violation_summary: Dict[str, int]
    layer_compliance_scores: Dict[str, float]
    recommendations: List[str]
    mathematical_foundation_health: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class FormalSystemDetector:
    """
    Formal System Detection and Validation Engine.
    
    Provides automatic detection of:
    - File correctness against formal system rules
    - Rule applicability determination
    - Real-time compliance monitoring
    - Systematic enforcement
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger("formal_system_detector")
        
        # Initialize mathematical foundation
        self.math_foundation = MathematicalSystemFoundation()
        
        # Load formal system rules
        self.rules = self._load_formal_system_rules()
        
        # File pattern mappings
        self.file_patterns = self._initialize_file_patterns()
        
        # Layer mappings
        self.layer_mappings = self._initialize_layer_mappings()
        
        # Semantic categories
        self.semantic_categories = self._initialize_semantic_categories()
        
        # Performance tracking
        self.performance_metrics = {
            "files_analyzed": 0,
            "total_analysis_time_ms": 0.0,
            "average_analysis_time_ms": 0.0,
            "validation_cache_hits": 0,
            "validation_cache_misses": 0
        }
        
        # Validation cache for performance
        self.validation_cache: Dict[str, FileAnalysisResult] = {}
        
        self.logger.info(f"Formal System Detector initialized for {project_root}")
    
    def _load_formal_system_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load all formal system rules from .mdc files."""
        rules = {}
        cursor_rules_path = self.project_root / ".cursor" / "rules"
        
        if not cursor_rules_path.exists():
            self.logger.warning(f"Cursor rules directory not found: {cursor_rules_path}")
            return rules
        
        # Recursively load all .mdc files
        for mdc_file in cursor_rules_path.rglob("*.mdc"):
            try:
                rule_data = self._parse_mdc_file(mdc_file)
                rules[rule_data["id"]] = rule_data
            except Exception as e:
                self.logger.error(f"Failed to load rule {mdc_file}: {e}")
        
        self.logger.info(f"Loaded {len(rules)} formal system rules")
        return rules
    
    def _parse_mdc_file(self, mdc_file: Path) -> Dict[str, Any]:
        """Parse a .mdc rule file and extract metadata."""
        with open(mdc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                rule_content = parts[2].strip()
            else:
                frontmatter = {}
                rule_content = content
        else:
            frontmatter = {}
            rule_content = content
        
        # Extract rule title
        title_match = re.search(r'^#\s+(.+)$', rule_content, re.MULTILINE)
        title = title_match.group(1) if title_match else mdc_file.stem
        
        return {
            "id": mdc_file.stem,
            "file_path": str(mdc_file),
            "title": title,
            "metadata": frontmatter,
            "content": rule_content,
            "priority": frontmatter.get("priority", "medium"),
            "always_apply": frontmatter.get("alwaysApply", False),
            "globs": frontmatter.get("globs", ["**/*"]),
            "tags": frontmatter.get("tags", []),
            "category": frontmatter.get("category", "general"),
            "enforcement": frontmatter.get("enforcement", "advisory"),
            "auto_fix": frontmatter.get("autoFix", False),
            "contexts": frontmatter.get("contexts", ["ALL"])
        }
    
    def _initialize_file_patterns(self) -> Dict[str, List[str]]:
        """Initialize file patterns for different categories."""
        return {
            "python_code": ["*.py"],
            "documentation": ["*.md", "*.rst", "*.txt"],
            "configuration": ["*.yml", "*.yaml", "*.json", "*.toml", "*.ini"],
            "scripts": ["*.sh", "*.bat", "*.ps1"],
            "agile_artifacts": ["US-*.md", "EPIC-*.md", "*SPRINT*.md", "*CATALOG*.md"],
            "test_files": ["test_*.py", "*_test.py", "tests/*.py"],
            "cursor_rules": [".cursor/rules/*.mdc"],
            "docker_files": ["Dockerfile", "docker-compose.yml", "*.dockerfile"],
            "requirements": ["requirements*.txt", "pyproject.toml", "setup.py"]
        }
    
    def _initialize_layer_mappings(self) -> Dict[str, LayerIndex]:
        """Initialize directory to layer mappings."""
        return {
            "agents": LayerIndex.DEVELOPMENT_CORE,
            "apps": LayerIndex.PRACTICAL_IMPLEMENTATION_CORE,
            "context": LayerIndex.PHILOSOPHICAL_FOUNDATION,
            "docs": LayerIndex.PHILOSOPHICAL_FOUNDATION,
            "models": LayerIndex.SOFTWARE_ARCHITECTURE_CORE,
            "monitoring": LayerIndex.DEVOPS_CORE,
            "prompts": LayerIndex.DEVELOPMENT_CORE,
            "scripts": LayerIndex.DEVOPS_CORE,
            "tests": LayerIndex.TESTING_CORE,
            "utils": LayerIndex.DEVELOPMENT_CORE,
            "workflow": LayerIndex.DEVOPS_CORE,
            "examples": LayerIndex.PRACTICAL_IMPLEMENTATION_CORE,
            ".cursor": LayerIndex.SOFTWARE_ARCHITECTURE_CORE
        }
    
    def _initialize_semantic_categories(self) -> Dict[str, str]:
        """Initialize semantic categories for files."""
        return {
            "agent": "AI agent implementation",
            "utility": "Utility function or class",
            "test": "Test implementation",
            "documentation": "Documentation or guide",
            "configuration": "System configuration",
            "script": "Automation script",
            "model": "Data model definition",
            "workflow": "Process workflow definition",
            "rule": "Formal system rule",
            "example": "Demonstration or example code",
            "app": "Application implementation"
        }
    
    def analyze_file(self, file_path: Union[str, Path]) -> FileAnalysisResult:
        """
        Analyze a single file for formal system compliance.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            FileAnalysisResult with comprehensive analysis
        """
        start_time = time.time()
        file_path = Path(file_path)
        
        # Check cache first
        cache_key = f"{file_path}:{file_path.stat().st_mtime}"
        if cache_key in self.validation_cache:
            self.performance_metrics["validation_cache_hits"] += 1
            return self.validation_cache[cache_key]
        
        self.performance_metrics["validation_cache_misses"] += 1
        
        try:
            # Determine applicable rules
            applicable_rules = self._determine_applicable_rules(file_path)
            
            # Determine layer assignment
            layer_assignment = self._determine_layer_assignment(file_path)
            
            # Determine semantic category
            semantic_category = self._determine_semantic_category(file_path)
            
            # Validate against applicable rules
            validation_issues = []
            for rule_id in applicable_rules:
                rule = self.rules.get(rule_id)
                if rule:
                    issues = self._validate_against_rule(file_path, rule)
                    validation_issues.extend(issues)
            
            # Perform mathematical validation if applicable
            mathematical_validation = None
            if self._should_perform_mathematical_validation(file_path):
                operation = self._create_operation_from_file(file_path, layer_assignment)
                mathematical_validation = self.math_foundation.validate_operation_mathematically(operation)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(validation_issues, mathematical_validation)
            is_compliant = compliance_score >= 0.8  # 80% threshold
            
            # Create analysis result
            result = FileAnalysisResult(
                file_path=str(file_path),
                is_compliant=is_compliant,
                compliance_score=compliance_score,
                applicable_rules=applicable_rules,
                validation_issues=validation_issues,
                mathematical_validation=mathematical_validation,
                layer_assignment=layer_assignment,
                semantic_category=semantic_category
            )
            
            # Cache result
            self.validation_cache[cache_key] = result
            
            # Update performance metrics
            analysis_time_ms = (time.time() - start_time) * 1000
            self.performance_metrics["files_analyzed"] += 1
            self.performance_metrics["total_analysis_time_ms"] += analysis_time_ms
            self.performance_metrics["average_analysis_time_ms"] = (
                self.performance_metrics["total_analysis_time_ms"] / 
                self.performance_metrics["files_analyzed"]
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze file {file_path}: {e}")
            return FileAnalysisResult(
                file_path=str(file_path),
                is_compliant=False,
                compliance_score=0.0,
                applicable_rules=[],
                validation_issues=[ValidationIssue(
                    rule_id="analysis_error",
                    category=RuleCategory.MATHEMATICAL_FOUNDATION,
                    level=ValidationLevel.CRITICAL,
                    file_path=str(file_path),
                    line_number=None,
                    message=f"Analysis failed: {e}",
                    suggestion="Check file format and content",
                    auto_fixable=False,
                    mathematical_basis="Error handling principle"
                )],
                mathematical_validation=None,
                layer_assignment=LayerIndex.PRACTICAL_IMPLEMENTATION_CORE,
                semantic_category="unknown"
            )
    
    def _determine_applicable_rules(self, file_path: Path) -> List[str]:
        """Determine which rules apply to a given file."""
        applicable_rules = []
        
        for rule_id, rule in self.rules.items():
            if self._rule_applies_to_file(rule, file_path):
                applicable_rules.append(rule_id)
        
        return applicable_rules
    
    def _rule_applies_to_file(self, rule: Dict[str, Any], file_path: Path) -> bool:
        """Check if a rule applies to a specific file."""
        # Always apply rules
        if rule.get("always_apply", False):
            return True
        
        # Check glob patterns
        globs = rule.get("globs", ["**/*"])
        for glob_pattern in globs:
            if file_path.match(glob_pattern):
                return True
        
        # Check contexts
        contexts = rule.get("contexts", ["ALL"])
        if "ALL" in contexts:
            return True
        
        # Check specific context matches
        file_context = self._determine_file_context(file_path)
        return any(context.lower() in file_context.lower() for context in contexts)
    
    def _determine_file_context(self, file_path: Path) -> str:
        """Determine the context of a file based on its path and content."""
        # Check directory context
        parts = file_path.parts
        if len(parts) > 1:
            return parts[0]  # Top-level directory
        
        # Check file extension context
        suffix = file_path.suffix.lower()
        if suffix == ".py":
            return "python"
        elif suffix in [".md", ".rst"]:
            return "documentation"
        elif suffix in [".yml", ".yaml"]:
            return "configuration"
        
        return "general"
    
    def _determine_layer_assignment(self, file_path: Path) -> LayerIndex:
        """Determine which layer a file belongs to."""
        parts = file_path.parts
        if len(parts) > 0:
            top_dir = parts[0].lower()
            return self.layer_mappings.get(top_dir, LayerIndex.PRACTICAL_IMPLEMENTATION_CORE)
        
        return LayerIndex.PRACTICAL_IMPLEMENTATION_CORE
    
    def _determine_semantic_category(self, file_path: Path) -> str:
        """Determine the semantic category of a file."""
        file_name = file_path.name.lower()
        
        # Check specific patterns
        if file_name.startswith("test_") or file_name.endswith("_test.py"):
            return "test"
        elif file_name.startswith("us-") or file_name.startswith("epic-"):
            return "agile_artifact"
        elif file_path.suffix == ".mdc":
            return "rule"
        elif file_path.suffix == ".py" and "agent" in file_name:
            return "agent"
        elif file_path.suffix == ".py":
            return "utility"
        elif file_path.suffix in [".md", ".rst"]:
            return "documentation"
        elif file_path.suffix in [".yml", ".yaml", ".json"]:
            return "configuration"
        elif file_path.suffix in [".sh", ".bat", ".ps1"]:
            return "script"
        
        return "general"
    
    def _validate_against_rule(self, file_path: Path, rule: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate a file against a specific rule."""
        issues = []
        
        try:
            # Get rule category
            category_name = rule.get("category", "general")
            try:
                category = RuleCategory(category_name.lower().replace("-", "_"))
            except ValueError:
                category = RuleCategory.SEMANTIC_COHERENCE
            
            # Get validation level
            priority = rule.get("priority", "medium")
            try:
                level = ValidationLevel(priority.lower())
            except ValueError:
                level = ValidationLevel.MEDIUM
            
            # Perform specific validations based on rule category
            if "naming" in rule["id"].lower():
                issues.extend(self._validate_naming_conventions(file_path, rule, category, level))
            elif "organization" in rule["id"].lower():
                issues.extend(self._validate_file_organization(file_path, rule, category, level))
            elif "documentation" in rule["id"].lower():
                issues.extend(self._validate_documentation_consistency(file_path, rule, category, level))
            elif "formal" in rule["id"].lower():
                issues.extend(self._validate_formal_compliance(file_path, rule, category, level))
            
        except Exception as e:
            self.logger.error(f"Failed to validate {file_path} against rule {rule['id']}: {e}")
            issues.append(ValidationIssue(
                rule_id=rule["id"],
                category=RuleCategory.MATHEMATICAL_FOUNDATION,
                level=ValidationLevel.CRITICAL,
                file_path=str(file_path),
                line_number=None,
                message=f"Validation error: {e}",
                suggestion="Check rule implementation",
                auto_fixable=False,
                mathematical_basis="Error handling principle"
            ))
        
        return issues
    
    def _validate_naming_conventions(self, file_path: Path, rule: Dict[str, Any], 
                                   category: RuleCategory, level: ValidationLevel) -> List[ValidationIssue]:
        """Validate naming conventions."""
        issues = []
        
        # Check file name patterns
        file_name = file_path.name
        
        # Agile artifacts naming
        if file_path.parent.name == "user_stories":
            if not re.match(r"US-[A-Z]+-\d{3}\.md$", file_name):
                issues.append(ValidationIssue(
                    rule_id=rule["id"],
                    category=category,
                    level=level,
                    file_path=str(file_path),
                    line_number=None,
                    message="User story file name doesn't follow US-XXX-NNN.md pattern",
                    suggestion="Rename to US-{COMPONENT}-{NUMBER}.md format",
                    auto_fixable=True,
                    mathematical_basis="Formal naming function N(A) → {valid, invalid}"
                ))
        
        # Epic naming
        elif file_path.parent.name == "epics":
            if not re.match(r"(EPIC-|epic-)[A-Z-]+-[a-z-]+\.md$", file_name):
                issues.append(ValidationIssue(
                    rule_id=rule["id"],
                    category=category,
                    level=level,
                    file_path=str(file_path),
                    line_number=None,
                    message="Epic file name doesn't follow EPIC-{NAME}.md pattern",
                    suggestion="Rename to EPIC-{DESCRIPTIVE-NAME}.md format",
                    auto_fixable=True,
                    mathematical_basis="Formal naming function N(A) → {valid, invalid}"
                ))
        
        # Python file naming
        elif file_path.suffix == ".py":
            if not re.match(r"^[a-z][a-z0-9_]*\.py$", file_name):
                issues.append(ValidationIssue(
                    rule_id=rule["id"],
                    category=category,
                    level=level,
                    file_path=str(file_path),
                    line_number=None,
                    message="Python file name should use snake_case",
                    suggestion="Rename to snake_case format (lowercase with underscores)",
                    auto_fixable=True,
                    mathematical_basis="Python naming conventions in formal system"
                ))
        
        return issues
    
    def _validate_file_organization(self, file_path: Path, rule: Dict[str, Any], 
                                  category: RuleCategory, level: ValidationLevel) -> List[ValidationIssue]:
        """Validate file organization."""
        issues = []
        
        # Check if file is in correct directory
        expected_location = self._get_expected_location(file_path)
        if expected_location and str(file_path) != str(expected_location):
            issues.append(ValidationIssue(
                rule_id=rule["id"],
                category=category,
                level=level,
                file_path=str(file_path),
                line_number=None,
                message=f"File is not in expected location. Expected: {expected_location}",
                suggestion=f"Move file to {expected_location}",
                auto_fixable=True,
                mathematical_basis="File organization hierarchy L(F) = CanonicalDirectory(type(F))"
            ))
        
        # Check for empty files (Boy Scout Rule violation)
        if file_path.exists() and file_path.stat().st_size == 0:
            issues.append(ValidationIssue(
                rule_id=rule["id"],
                category=category,
                level=ValidationLevel.CRITICAL,
                file_path=str(file_path),
                line_number=None,
                message="Empty file violates Boy Scout Rule",
                suggestion="Add content or delete file",
                auto_fixable=True,
                mathematical_basis="Boy Scout Rule: Improved(F, neighborhood(F))"
            ))
        
        return issues
    
    def _validate_documentation_consistency(self, file_path: Path, rule: Dict[str, Any], 
                                          category: RuleCategory, level: ValidationLevel) -> List[ValidationIssue]:
        """Validate documentation consistency."""
        issues = []
        
        if file_path.suffix == ".md":
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for broken links
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                links = re.findall(link_pattern, content)
                
                for link_text, link_url in links:
                    if link_url.startswith(('./', '../', '/')):
                        # Relative link - check if target exists
                        if link_url.startswith('/'):
                            target_path = self.project_root / link_url[1:]
                        else:
                            target_path = (file_path.parent / link_url).resolve()
                        
                        if not target_path.exists():
                            issues.append(ValidationIssue(
                                rule_id=rule["id"],
                                category=category,
                                level=level,
                                file_path=str(file_path),
                                line_number=None,
                                message=f"Broken link: {link_url}",
                                suggestion=f"Fix link target or update path",
                                auto_fixable=False,
                                mathematical_basis="Documentation consistency invariant Consistent(D)"
                            ))
                
            except Exception as e:
                self.logger.error(f"Failed to validate documentation {file_path}: {e}")
        
        return issues
    
    def _validate_formal_compliance(self, file_path: Path, rule: Dict[str, Any], 
                                  category: RuleCategory, level: ValidationLevel) -> List[ValidationIssue]:
        """Validate formal system compliance."""
        issues = []
        
        # Check if formal system compliant agent is used for Python files
        if file_path.suffix == ".py" and "agent" in str(file_path).lower():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to check inheritance
                tree = ast.parse(content)
                
                # Check for agent classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if "agent" in node.name.lower():
                            # Check if inherits from FormalSystemCompliantAgent
                            inherits_formal = any(
                                isinstance(base, ast.Name) and "FormalSystemCompliantAgent" in base.id
                                for base in node.bases
                            )
                            
                            if not inherits_formal:
                                issues.append(ValidationIssue(
                                    rule_id=rule["id"],
                                    category=category,
                                    level=ValidationLevel.CRITICAL,
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    message=f"Agent class {node.name} must inherit from FormalSystemCompliantAgent",
                                    suggestion="Change inheritance to FormalSystemCompliantAgent",
                                    auto_fixable=True,
                                    mathematical_basis="Formal system compliance requirement"
                                ))
                
            except SyntaxError:
                # File has syntax errors
                issues.append(ValidationIssue(
                    rule_id=rule["id"],
                    category=category,
                    level=ValidationLevel.HIGH,
                    file_path=str(file_path),
                    line_number=None,
                    message="Python file has syntax errors",
                    suggestion="Fix syntax errors",
                    auto_fixable=False,
                    mathematical_basis="Syntactic correctness requirement"
                ))
            except Exception as e:
                self.logger.error(f"Failed to parse Python file {file_path}: {e}")
        
        return issues
    
    def _get_expected_location(self, file_path: Path) -> Optional[Path]:
        """Get the expected location for a file based on formal organization rules."""
        file_name = file_path.name
        
        # User stories should be in docs/agile/sprints/*/user_stories/
        if file_name.startswith("US-") and file_name.endswith(".md"):
            return self.project_root / "docs" / "agile" / "sprints" / "sprint_current" / "user_stories" / file_name
        
        # Epics should be in docs/agile/epics/
        elif file_name.startswith(("EPIC-", "epic-")) and file_name.endswith(".md"):
            return self.project_root / "docs" / "agile" / "epics" / file_name
        
        # Test files should be in tests/
        elif file_name.startswith("test_") or file_name.endswith("_test.py"):
            return self.project_root / "tests" / file_name
        
        # No specific expected location
        return None
    
    def _should_perform_mathematical_validation(self, file_path: Path) -> bool:
        """Determine if mathematical validation should be performed."""
        # Perform mathematical validation for:
        # - Agent files
        # - Critical system components
        # - Formal system rules
        
        file_name = file_path.name.lower()
        return (
            "agent" in file_name or
            "formal" in file_name or
            file_path.suffix == ".mdc" or
            "critical" in str(file_path).lower()
        )
    
    def _create_operation_from_file(self, file_path: Path, layer: LayerIndex) -> Operation:
        """Create Operation object from file for mathematical validation."""
        operation_id = f"file_validation_{file_path.stem}_{int(time.time() * 1000)}"
        
        return Operation(
            operation_id=operation_id,
            operation_type="file_validation",
            parameters={
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size if file_path.exists() else 0,
                "file_extension": file_path.suffix
            },
            context={
                "validation_type": "formal_system_compliance",
                "layer": layer.name,
                "semantic_category": self._determine_semantic_category(file_path)
            },
            timestamp=datetime.now(),
            layer=layer
        )
    
    def _calculate_compliance_score(self, validation_issues: List[ValidationIssue], 
                                  mathematical_validation: Optional[MathematicalValidationResult]) -> float:
        """Calculate overall compliance score for a file."""
        # Start with perfect score
        score = 1.0
        
        # Deduct points for validation issues
        for issue in validation_issues:
            if issue.level == ValidationLevel.CRITICAL:
                score -= 0.3
            elif issue.level == ValidationLevel.HIGH:
                score -= 0.2
            elif issue.level == ValidationLevel.MEDIUM:
                score -= 0.1
            elif issue.level == ValidationLevel.LOW:
                score -= 0.05
            else:  # ADVISORY
                score -= 0.02
        
        # Factor in mathematical validation if available
        if mathematical_validation:
            if mathematical_validation.mathematically_sound:
                score *= 1.1  # Bonus for mathematical soundness
            else:
                score *= 0.7  # Penalty for mathematical issues
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def analyze_system(self, include_patterns: List[str] = None, 
                      exclude_patterns: List[str] = None) -> SystemComplianceReport:
        """
        Analyze the entire system for formal compliance.
        
        Args:
            include_patterns: File patterns to include (default: all)
            exclude_patterns: File patterns to exclude
            
        Returns:
            SystemComplianceReport with comprehensive system analysis
        """
        start_time = time.time()
        
        # Default patterns
        if include_patterns is None:
            include_patterns = ["**/*.py", "**/*.md", "**/*.mdc", "**/*.yml", "**/*.yaml"]
        
        if exclude_patterns is None:
            exclude_patterns = [
                "**/__pycache__/**",
                "**/.git/**",
                "**/node_modules/**",
                "**/.venv/**",
                "**/venv/**"
            ]
        
        # Find all files to analyze
        files_to_analyze = []
        for pattern in include_patterns:
            for file_path in self.project_root.rglob(pattern.replace("**/", "")):
                if file_path.is_file():
                    # Check exclusions
                    excluded = False
                    for exclude_pattern in exclude_patterns:
                        if file_path.match(exclude_pattern):
                            excluded = True
                            break
                    
                    if not excluded:
                        files_to_analyze.append(file_path)
        
        self.logger.info(f"Analyzing {len(files_to_analyze)} files for formal system compliance")
        
        # Analyze each file
        file_results = []
        compliant_files = 0
        rule_violation_summary = {}
        layer_compliance_scores = {}
        layer_file_counts = {}
        
        for file_path in files_to_analyze:
            try:
                result = self.analyze_file(file_path)
                file_results.append(result)
                
                if result.is_compliant:
                    compliant_files += 1
                
                # Track rule violations
                for issue in result.validation_issues:
                    rule_violation_summary[issue.rule_id] = rule_violation_summary.get(issue.rule_id, 0) + 1
                
                # Track layer compliance
                layer_name = result.layer_assignment.name
                if layer_name not in layer_compliance_scores:
                    layer_compliance_scores[layer_name] = 0.0
                    layer_file_counts[layer_name] = 0
                
                layer_compliance_scores[layer_name] += result.compliance_score
                layer_file_counts[layer_name] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to analyze {file_path}: {e}")
        
        # Calculate layer averages
        for layer_name in layer_compliance_scores:
            if layer_file_counts[layer_name] > 0:
                layer_compliance_scores[layer_name] /= layer_file_counts[layer_name]
        
        # Calculate overall compliance score
        total_files = len(file_results)
        overall_compliance_score = sum(r.compliance_score for r in file_results) / max(1, total_files)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(file_results, rule_violation_summary)
        
        # Get mathematical foundation health
        mathematical_foundation_health = self.math_foundation.get_performance_metrics()
        
        analysis_time = time.time() - start_time
        self.logger.info(f"System analysis completed in {analysis_time:.2f}s")
        
        return SystemComplianceReport(
            overall_compliance_score=overall_compliance_score,
            total_files_analyzed=total_files,
            compliant_files=compliant_files,
            non_compliant_files=total_files - compliant_files,
            file_results=file_results,
            rule_violation_summary=rule_violation_summary,
            layer_compliance_scores=layer_compliance_scores,
            recommendations=recommendations,
            mathematical_foundation_health=mathematical_foundation_health
        )
    
    def _generate_recommendations(self, file_results: List[FileAnalysisResult], 
                                rule_violation_summary: Dict[str, int]) -> List[str]:
        """Generate actionable recommendations based on analysis results."""
        recommendations = []
        
        # Most common violations
        if rule_violation_summary:
            most_common = max(rule_violation_summary.items(), key=lambda x: x[1])
            recommendations.append(
                f"Priority: Address '{most_common[0]}' rule violations ({most_common[1]} files affected)"
            )
        
        # Empty files
        empty_files = [r for r in file_results if any(
            "empty file" in issue.message.lower() for issue in r.validation_issues
        )]
        if empty_files:
            recommendations.append(
                f"Delete or populate {len(empty_files)} empty files (Boy Scout Rule violation)"
            )
        
        # Naming convention issues
        naming_issues = [r for r in file_results if any(
            issue.category == RuleCategory.NAMING_CONVENTIONS for issue in r.validation_issues
        )]
        if naming_issues:
            recommendations.append(
                f"Fix naming conventions for {len(naming_issues)} files to improve discoverability"
            )
        
        # Documentation consistency
        doc_issues = [r for r in file_results if any(
            issue.category == RuleCategory.DOCUMENTATION_CONSISTENCY for issue in r.validation_issues
        )]
        if doc_issues:
            recommendations.append(
                f"Fix documentation consistency for {len(doc_issues)} files (broken links, etc.)"
            )
        
        # Low compliance files
        low_compliance = [r for r in file_results if r.compliance_score < 0.5]
        if low_compliance:
            recommendations.append(
                f"Prioritize {len(low_compliance)} files with compliance score < 50%"
            )
        
        return recommendations
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detector performance metrics."""
        return {
            **self.performance_metrics,
            "cache_size": len(self.validation_cache),
            "cache_hit_rate": (
                self.performance_metrics["validation_cache_hits"] / 
                max(1, self.performance_metrics["validation_cache_hits"] + 
                    self.performance_metrics["validation_cache_misses"])
            )
        }
    
    def clear_cache(self):
        """Clear validation cache."""
        self.validation_cache.clear()
        self.logger.info("Validation cache cleared")


# Utility functions for easy access
def create_formal_system_detector(project_root: str = ".") -> FormalSystemDetector:
    """Create a formal system detector instance."""
    return FormalSystemDetector(project_root)


def quick_file_check(file_path: str) -> bool:
    """Quick check if a file is formally compliant."""
    detector = create_formal_system_detector()
    result = detector.analyze_file(file_path)
    return result.is_compliant


def quick_system_check() -> float:
    """Quick check of overall system compliance."""
    detector = create_formal_system_detector()
    report = detector.analyze_system()
    return report.overall_compliance_score


if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)
    
    detector = create_formal_system_detector()
    
    # Test single file analysis
    test_file = Path("utils/validation/formal_system_detector.py")
    if test_file.exists():
        result = detector.analyze_file(test_file)
        print(f"✅ File analysis: {result.file_path}")
        print(f"   Compliant: {result.is_compliant}")
        print(f"   Score: {result.compliance_score:.3f}")
        print(f"   Issues: {len(result.validation_issues)}")
        
        for issue in result.validation_issues[:3]:  # Show first 3 issues
            print(f"   - {issue.level.value}: {issue.message}")
    
    # Test system analysis (sample)
    print(f"\n🔍 System compliance check:")
    sample_patterns = ["*.py", "*.md"]  # Sample for speed
    report = detector.analyze_system(include_patterns=sample_patterns)
    print(f"   Overall Score: {report.overall_compliance_score:.3f}")
    print(f"   Files Analyzed: {report.total_files_analyzed}")
    print(f"   Compliant: {report.compliant_files}")
    print(f"   Non-Compliant: {report.non_compliant_files}")
    
    if report.recommendations:
        print(f"   Top Recommendation: {report.recommendations[0]}")
