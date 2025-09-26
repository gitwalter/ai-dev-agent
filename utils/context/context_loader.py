#!/usr/bin/env python3
"""
Simple context-aware rule loader.
Focus: Make it work, not make it fancy.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

class ContextLoader:
    """Simple context loader that actually works."""
    
    def __init__(self):
        self.rules_dir = Path(__file__).parent.parent.parent / ".cursor" / "rules"
        self.current_rules = 0
        
    def detect_context(self, message: str) -> str:
        """Detect context from message."""
        msg = message.lower()
        
        # Simple keyword detection
        if "@docs" in msg:
            return "DOCUMENTATION"
        elif "@code" in msg:
            return "CODING"  
        elif "@debug" in msg:
            return "DEBUGGING"
        elif "@test" in msg:
            return "TESTING"
        else:
            return "DEFAULT"
    
    def get_core_rules(self) -> List[str]:
        """Get rules that should always be loaded."""
        core_rules = []
        
        for rule_file in self.rules_dir.rglob("*.mdc"):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "alwaysApply: true" in content:
                    core_rules.append(rule_file.stem)
                    
            except Exception:
                continue
        
        return core_rules
    
    def get_context_rules(self, context: str) -> List[str]:
        """Get rules for specific context."""
        context_rules = []
        
        for rule_file in self.rules_dir.rglob("*.mdc"):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if f"'{context}'" in content and "contexts:" in content:
                    context_rules.append(rule_file.stem)
                    
            except Exception:
                continue
        
        return context_rules
    
    def load_rules_for_context(self, context: str) -> Dict[str, str]:
        """Load all rules for a context."""
        rules = {}
        
        # Get core rules (always loaded)
        core_rules = self.get_core_rules()
        
        # Get context-specific rules
        context_rules = self.get_context_rules(context)
        
        # Combine and load content
        all_rule_names = list(set(core_rules + context_rules))
        
        for rule_name in all_rule_names:
            rule_file = None
            
            # Find the rule file
            for potential_file in self.rules_dir.rglob(f"{rule_name}.mdc"):
                rule_file = potential_file
                break
            
            if rule_file and rule_file.exists():
                try:
                    with open(rule_file, 'r', encoding='utf-8') as f:
                        rules[rule_name] = f.read()
                except Exception:
                    continue
        
        return rules
    
    def switch_to_context(self, message: str) -> Dict:
        """Switch to context based on message."""
        context = self.detect_context(message)
        rules = self.load_rules_for_context(context)
        
        # Update current state
        old_count = self.current_rules
        self.current_rules = len(rules)
        
        # Generate .cursor-rules file
        self._write_cursor_rules(context, rules, message)
        
        return {
            'context': context,
            'old_rule_count': old_count,
            'new_rule_count': len(rules),
            'rule_names': list(rules.keys())
        }
    
    def _write_cursor_rules(self, context: str, rules: Dict[str, str], message: str):
        """Write .cursor-rules file."""
        try:
            content = f"# Context: {context}\n# Rules: {len(rules)}\n# Message: {message[:50]}...\n\n"
            
            for rule_name, rule_content in rules.items():
                content += f"# === {rule_name} ===\n"
                content += rule_content + "\n\n"
            
            with open(".cursor-rules", 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Failed to write .cursor-rules: {e}")

def test_context_loader():
    """Test the context loader."""
    loader = ContextLoader()
    
    test_messages = [
        "@docs Update the documentation",
        "@code Implement feature",
        "General work"
    ]
    
    for message in test_messages:
        print(f"\nMessage: {message}")
        result = loader.switch_to_context(message)
        print(f"Context: {result['context']}")
        print(f"Rules: {result['new_rule_count']}")
        print(f"Rule names: {result['rule_names'][:3]}...")

if __name__ == "__main__":
    test_context_loader()
