#!/usr/bin/env python3
"""
Context-Aware Rule Loader - Implements the @keyword functionality
to only load relevant rules based on development context.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import logging

logger = logging.getLogger(__name__)

class ContextAwareRuleLoader:
    """
    Context-aware rule loader that implements @keyword functionality.
    Only loads rules relevant to the current development context.
    """
    
    def __init__(self, rules_directory: Optional[Path] = None):
        """Initialize the context-aware rule loader."""
        self.rules_directory = rules_directory or Path(__file__).parent.parent / ".cursor" / "rules"
        self.context_mappings = self._load_context_mappings()
        self.all_rules_metadata = {}
        self._scan_all_rules()
    
    def _load_context_mappings(self) -> Dict[str, Any]:
        """Load context mappings from configuration."""
        config_file = self.rules_directory / "config" / "context_rule_mappings.yaml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load context mappings: {e}")
        
        # Fallback to hardcoded mappings
        return {
            "contexts": {
                "DEFAULT": {
                    "keywords": ["@default", "@all"],
                    "rules": ["safety_first_principle", "intelligent_context_aware_rule_system", 
                             "core_rule_application_framework", "user_controlled_success_declaration_rule"]
                },
                "DOCUMENTATION": {
                    "keywords": ["@docs", "@document", "@readme"],
                    "rules": ["safety_first_principle", "intelligent_context_aware_rule_system",
                             "core_rule_application_framework", "user_controlled_success_declaration_rule",
                             "documentation_live_updates_rule"]
                },
                "CODING": {
                    "keywords": ["@code", "@implement", "@build"],
                    "rules": ["safety_first_principle", "intelligent_context_aware_rule_system",
                             "core_rule_application_framework", "user_controlled_success_declaration_rule",
                             "development_core_principles_rule", "error_handling_no_silent_errors_rule"]
                }
            }
        }
    
    def _scan_all_rules(self):
        """Scan all rules to build metadata index."""
        for rule_file in self.rules_directory.rglob("*.mdc"):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                metadata = self._parse_rule_metadata(content)
                rule_name = rule_file.stem
                self.all_rules_metadata[rule_name] = {
                    'file_path': rule_file,
                    'metadata': metadata,
                    'content': content
                }
                
            except Exception as e:
                logger.warning(f"Failed to scan rule {rule_file}: {e}")
    
    def _parse_rule_metadata(self, content: str) -> Dict[str, Any]:
        """Parse YAML metadata from rule content."""
        metadata = {}
        
        # Look for YAML frontmatter
        if content.startswith('---'):
            try:
                # Find the end of the frontmatter
                end_match = re.search(r'\n---\s*\n', content)
                if end_match:
                    yaml_content = content[3:end_match.start()]
                    metadata = yaml.safe_load(yaml_content) or {}
            except Exception as e:
                logger.warning(f"Failed to parse YAML metadata: {e}")
        
        return metadata
    
    def detect_context(self, user_message: str) -> str:
        """Detect context from user message."""
        message_lower = user_message.lower()
        
        # Check for explicit @keywords
        for context_name, context_config in self.context_mappings.get("contexts", {}).items():
            keywords = context_config.get("keywords", [])
            for keyword in keywords:
                if keyword in message_lower:
                    return context_name
        
        # Default context
        return "DEFAULT"
    
    def get_rules_for_context(self, context: str) -> Dict[str, str]:
        """Get all rules that should be loaded for a specific context."""
        context_config = self.context_mappings.get("contexts", {}).get(context, {})
        
        if not context_config:
            # Fallback to core rules
            context = "DEFAULT"
            context_config = self.context_mappings.get("contexts", {}).get(context, {})
        
        # Get rules that should always apply
        always_apply_rules = {}
        for rule_name, rule_info in self.all_rules_metadata.items():
            metadata = rule_info['metadata']
            if metadata.get('alwaysApply') == True or metadata.get('alwaysApply') == 'true':
                always_apply_rules[rule_name] = rule_info['content']
        
        # Get context-specific rules
        context_rules = {}
        for rule_name, rule_info in self.all_rules_metadata.items():
            metadata = rule_info['metadata']
            contexts = metadata.get('contexts', [])
            
            # Convert string contexts to list
            if isinstance(contexts, str):
                contexts = [contexts]
            
            if context in contexts:
                context_rules[rule_name] = rule_info['content']
        
        # Combine always-apply and context-specific rules
        all_rules = {**always_apply_rules, **context_rules}
        
        return all_rules
    
    def load_rules_for_message(self, user_message: str) -> Dict[str, str]:
        """Load rules based on user message context."""
        context = self.detect_context(user_message)
        rules = self.get_rules_for_context(context)
        
        logger.info(f"Detected context: {context}")
        logger.info(f"Loading {len(rules)} rules for context")
        
        return rules
    
    def get_context_summary(self, context: str) -> Dict[str, Any]:
        """Get summary information for a context."""
        rules = self.get_rules_for_context(context)
        
        return {
            'context': context,
            'total_rules': len(rules),
            'rule_names': list(rules.keys()),
            'keywords': self.context_mappings.get("contexts", {}).get(context, {}).get("keywords", [])
        }

def create_context_aware_cursor_rules(user_message: str = "@docs") -> None:
    """
    Create a context-aware .cursor-rules file based on user message.
    This replaces the static rule loading with dynamic context-aware loading.
    """
    
    loader = ContextAwareRuleLoader()
    rules = loader.load_rules_for_message(user_message)
    context = loader.detect_context(user_message)
    
    # Create the .cursor-rules content
    cursor_rules_content = f"""# Context-Aware Cursor Rules
# Generated for context: {context}
# Total rules loaded: {len(rules)}
# Generated from user message: {user_message}

"""
    
    # Add each rule content
    for rule_name, rule_content in rules.items():
        cursor_rules_content += f"\n# === {rule_name} ===\n"
        cursor_rules_content += rule_content
        cursor_rules_content += "\n\n"
    
    # Write to .cursor-rules file
    cursor_rules_file = Path(".cursor-rules")
    with open(cursor_rules_file, 'w', encoding='utf-8') as f:
        f.write(cursor_rules_content)
    
    print(f"Generated .cursor-rules for context: {context}")
    print(f"Rules loaded: {len(rules)}")
    print(f"Rule names: {list(rules.keys())}")

def main():
    """Test the context-aware rule loader."""
    print("🔍 Testing Context-Aware Rule Loader...")
    
    loader = ContextAwareRuleLoader()
    
    # Test different contexts
    test_messages = [
        "@docs Update the documentation",
        "@code Implement the feature", 
        "@default General work"
    ]
    
    for message in test_messages:
        print(f"\n📝 Message: {message}")
        context = loader.detect_context(message)
        rules = loader.get_rules_for_context(context)
        
        print(f"   Context: {context}")
        print(f"   Rules: {len(rules)}")
        print(f"   Rule names: {list(rules.keys())}")

if __name__ == "__main__":
    main()
