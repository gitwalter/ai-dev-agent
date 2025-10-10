#!/usr/bin/env python3
"""
Cursor Rules Validation System
===============================

Validates that Cursor rules are properly configured for context delivery.
Ensures rules will load correctly based on their assertions.

Features:
- Validates YAML frontmatter structure
- Checks context trigger definitions
- Validates dependency chains
- Ensures tier hierarchy is correct
- Verifies enforcement levels are appropriate

Usage:
    python scripts/validate_cursor_rules.py
    
Author: AI Development Agent
Created: 2025-10-10
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class CursorRuleValidator:
    """Validate Cursor rule configuration for proper context delivery."""
    
    VALID_TIERS = ['0', '1', '2', '3']
    VALID_CONTEXTS = ['ALL', 'AGILE', 'TESTING', 'PERFORMANCE', 'SECURITY', 'ARCHITECTURE']
    VALID_ENFORCEMENT = ['error', 'warning', 'blocking', 'info']
    
    def __init__(self):
        self.rules_dir = project_root / ".cursor" / "rules"
        self.rules = {}
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_all_rules(self) -> Dict[str, Any]:
        """Validate all Cursor rules in the .cursor/rules directory."""
        
        print("[INFO] Validating Cursor rules for context delivery...")
        print("=" * 60)
        
        # Discover all .mdc files
        rule_files = list(self.rules_dir.rglob("*.mdc"))
        print(f"[INFO] Found {len(rule_files)} rule files\n")
        
        # Validate each rule
        for rule_file in rule_files:
            self._validate_rule_file(rule_file)
        
        # Validate cross-rule dependencies
        self._validate_dependencies()
        
        # Generate report
        return self._generate_validation_report()
    
    def _validate_rule_file(self, rule_file: Path):
        """Validate a single rule file."""
        
        try:
            content = rule_file.read_text(encoding='utf-8')
            
            # Extract YAML frontmatter
            frontmatter = self._extract_frontmatter(content)
            
            if not frontmatter:
                self.validation_errors.append({
                    "file": str(rule_file.relative_to(project_root)),
                    "error": "Missing YAML frontmatter"
                })
                return
            
            # Parse frontmatter
            rule_config = self._parse_frontmatter(frontmatter)
            rule_name = rule_file.stem
            
            # Store rule
            self.rules[rule_name] = {
                "file": rule_file,
                "config": rule_config
            }
            
            # Validate rule configuration
            self._validate_rule_config(rule_name, rule_config, rule_file)
            
        except Exception as e:
            self.validation_errors.append({
                "file": str(rule_file.relative_to(project_root)),
                "error": f"Failed to read/parse: {e}"
            })
    
    def _extract_frontmatter(self, content: str) -> Optional[str]:
        """Extract YAML frontmatter from rule file."""
        
        # Match --- ... --- pattern
        match = re.search(r'^---\s*\n(.*?)\n---', content, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1)
        return None
    
    def _parse_frontmatter(self, frontmatter: str) -> Dict[str, Any]:
        """Parse YAML frontmatter into dictionary."""
        
        config = {}
        
        # Simple YAML parser (just for validation)
        for line in frontmatter.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Handle boolean values
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                # Handle list values (simplified)
                elif value.startswith('[') and value.endswith(']'):
                    value = [v.strip() for v in value[1:-1].split(',')]
                # Handle quoted strings
                elif value.startswith('"') or value.startswith("'"):
                    value = value.strip('"\'')
                
                config[key] = value
        
        return config
    
    def _validate_rule_config(self, rule_name: str, config: Dict, rule_file: Path):
        """Validate rule configuration assertions."""
        
        file_rel = str(rule_file.relative_to(project_root))
        
        # Required fields
        required_fields = ['alwaysApply', 'contexts', 'enforcement', 'tier']
        for field in required_fields:
            if field not in config:
                self.validation_errors.append({
                    "file": file_rel,
                    "rule": rule_name,
                    "error": f"Missing required field: {field}"
                })
        
        # Validate alwaysApply
        if 'alwaysApply' in config:
            if not isinstance(config['alwaysApply'], bool):
                self.validation_errors.append({
                    "file": file_rel,
                    "rule": rule_name,
                    "error": f"alwaysApply must be boolean, got: {config['alwaysApply']}"
                })
        
        # Validate contexts
        if 'contexts' in config:
            contexts = config['contexts']
            if isinstance(contexts, str):
                contexts = [contexts]
            
            for context in contexts:
                if context not in self.VALID_CONTEXTS:
                    self.validation_warnings.append({
                        "file": file_rel,
                        "rule": rule_name,
                        "warning": f"Non-standard context: {context}"
                    })
        
        # Validate enforcement
        if 'enforcement' in config:
            if config['enforcement'] not in self.VALID_ENFORCEMENT:
                self.validation_errors.append({
                    "file": file_rel,
                    "rule": rule_name,
                    "error": f"Invalid enforcement: {config['enforcement']}"
                })
        
        # Validate tier
        if 'tier' in config:
            tier = str(config['tier'])
            if tier not in self.VALID_TIERS:
                self.validation_errors.append({
                    "file": file_rel,
                    "rule": rule_name,
                    "error": f"Invalid tier: {tier} (must be 0-3)"
                })
            
            # Tier 0 should always apply
            if tier == '0' and not config.get('alwaysApply', False):
                self.validation_warnings.append({
                    "file": file_rel,
                    "rule": rule_name,
                    "warning": "Tier 0 rules should have alwaysApply: true"
                })
    
    def _validate_dependencies(self):
        """Validate dependency chains are correct."""
        
        for rule_name, rule_data in self.rules.items():
            config = rule_data['config']
            dependencies = config.get('dependencies', [])
            
            if isinstance(dependencies, str):
                dependencies = [dependencies]
            
            for dep in dependencies:
                if dep and dep not in self.rules:
                    self.validation_warnings.append({
                        "rule": rule_name,
                        "warning": f"Dependency '{dep}' not found in rule set"
                    })
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)
        
        # Summary
        total_rules = len(self.rules)
        total_errors = len(self.validation_errors)
        total_warnings = len(self.validation_warnings)
        
        print(f"\n[SUMMARY]")
        print(f"  Total Rules: {total_rules}")
        print(f"  Errors: {total_errors}")
        print(f"  Warnings: {total_warnings}")
        
        # Errors
        if self.validation_errors:
            print(f"\n[ERRORS] {total_errors} found:")
            for error in self.validation_errors:
                print(f"  [ERROR] {error.get('file', error.get('rule', 'Unknown'))}")
                print(f"          {error['error']}")
        
        # Warnings
        if self.validation_warnings:
            print(f"\n[WARNINGS] {total_warnings} found:")
            for warning in self.validation_warnings:
                print(f"  [WARNING] {warning.get('file', warning.get('rule', 'Unknown'))}")
                print(f"            {warning['warning']}")
        
        # Rule statistics
        print(f"\n[RULE STATISTICS]")
        always_apply = sum(1 for r in self.rules.values() if r['config'].get('alwaysApply'))
        context_triggered = total_rules - always_apply
        
        print(f"  Always Apply (Tier 0-1): {always_apply}")
        print(f"  Context Triggered (Tier 2-3): {context_triggered}")
        
        # Context distribution
        context_count = {}
        for rule_data in self.rules.values():
            contexts = rule_data['config'].get('contexts', [])
            if isinstance(contexts, str):
                contexts = [contexts]
            for context in contexts:
                context_count[context] = context_count.get(context, 0) + 1
        
        print(f"\n[CONTEXT DISTRIBUTION]")
        for context, count in sorted(context_count.items()):
            print(f"  {context}: {count} rules")
        
        # Overall status
        print("\n" + "=" * 60)
        if total_errors == 0:
            print("[OK] All Cursor rules are properly configured for context delivery")
            print("=" * 60)
            return {"success": True, "errors": [], "warnings": self.validation_warnings}
        else:
            print("[FAILED] Cursor rules have configuration errors")
            print("=" * 60)
            return {"success": False, "errors": self.validation_errors, "warnings": self.validation_warnings}


def main():
    """Main entry point for Cursor rules validation."""
    
    validator = CursorRuleValidator()
    result = validator.validate_all_rules()
    
    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()

