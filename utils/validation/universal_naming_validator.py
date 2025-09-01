#!/usr/bin/env python3
"""
Universal Naming Convention Validator
Based on Fowler/Carnap/Quine philosophical principles.

This utility provides universal validation for ALL project artifacts.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class ValidationResult:
    """Result of naming validation."""
    is_compliant: bool
    violation_type: str
    suggested_name: str
    philosophical_reasoning: str

class UniversalNamingValidator:
    """
    Universal validator for all naming conventions in the project.
    
    Based on Fowler/Carnap/Quine philosophical principles:
    - Fowler: Pragmatic utility for development velocity
    - Carnap: Systematic clarity for logical organization
    - Quine: Ontological consistency for universal framework
    """
    
    def __init__(self):
        self.conventions = self._load_naming_conventions()
    
    def validate_file_naming(self, file_path: str) -> ValidationResult:
        """
        Validate file naming against universal conventions.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            ValidationResult with compliance status and suggestions
        """
        
        path = Path(file_path)
        file_name = path.name
        category = self._categorize_file(path)
        
        # Apply category-specific validation
        if category == "epic_files":
            return self._validate_epic_file(file_name)
        elif category == "user_stories":
            return self._validate_user_story(file_name)
        elif category == "sprint_files":
            return self._validate_sprint_file(file_name)
        elif category == "agent_modules":
            return self._validate_agent_module(file_name)
        else:
            return self._validate_general_file(file_name, category)
    
    def _categorize_file(self, file_path: Path) -> str:
        """Categorize file based on path and extension."""
        # Implementation similar to above
        pass
    
    def _validate_epic_file(self, filename: str) -> ValidationResult:
        """Validate epic file naming."""
        if re.match(r'^epic-[a-z0-9-]+\.md$', filename):
            return ValidationResult(True, "", "", "Compliant epic naming")
        
        suggested = self._suggest_epic_name(filename)
        return ValidationResult(
            False,
            "Epic file must use format: epic-topic.md",
            suggested,
            "Fowler: Clear epic identification; Carnap: Systematic hierarchy; Quine: Epic ontology"
        )
    
    def _load_naming_conventions(self) -> Dict:
        """Load all naming convention patterns."""
        return {
            "epic_files": r'^epic-[a-z0-9-]+\.md$',
            "user_stories": r'^US-[A-Z0-9-]+\.md$',
            "sprint_files": r'^sprint_\d+_[a-z_]+\.md$',
            "agent_modules": r'^[a-z][a-z0-9_]*_(agent|team|specialist)\.py$'
        }
    
    # Additional validation methods...
