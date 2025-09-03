#!/usr/bin/env python3
"""
Architectural Layer Separation Validator
========================================

Validates that architectural layers maintain strict separation
with appropriate language for each layer and proper translation
interfaces between layers.
"""

import sys
import os
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set

# Layer-specific language rules
LAYER_LANGUAGE_RULES = {
    'technical': {
        'allowed_terms': {
            'performance', 'efficiency', 'optimization', 'implementation', 
            'validation', 'algorithm', 'architecture', 'framework',
            'interface', 'module', 'function', 'class', 'method',
            'database', 'api', 'service', 'component', 'system'
        },
        'prohibited_terms': {
            'divine', 'sacred', 'blessed', 'holy', 'spiritual',
            'celestial', 'transcendent', 'mystical', 'enlightened'
        },
        'file_patterns': ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.h']
    },
    'business': {
        'allowed_terms': {
            'requirement', 'stakeholder', 'value', 'benefit', 'outcome',
            'process', 'workflow', 'user story', 'acceptance criteria',
            'business rule', 'compliance', 'regulation', 'market'
        },
        'prohibited_terms': {
            'divine', 'sacred', 'blessed', 'holy', 'spiritual',
            'celestial', 'transcendent', 'mystical', 'enlightened'
        },
        'file_patterns': ['requirements/*.md', 'business/*.md', 'user_stories/*.md']
    },
    'philosophical': {
        'allowed_terms': {
            'principle', 'value', 'purpose', 'vision', 'mission',
            'inspiration', 'philosophy', 'ethics', 'culture',
            'excellence', 'integrity', 'growth', 'harmony'
        },
        'prohibited_terms': set(),  # Philosophical layer can use spiritual terms
        'file_patterns': ['philosophy/*.md', 'vision/*.md', 'culture/*.md']
    }
}

class LayerSeparationValidator:
    """Validates architectural layer separation rules."""
    
    def __init__(self, layer: str):
        self.layer = layer
        self.rules = LAYER_LANGUAGE_RULES.get(layer, {})
        self.violations = []
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate a single file for layer separation compliance."""
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            return self._validate_content(content, str(file_path))
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return True
    
    def _validate_content(self, content: str, file_path: str) -> bool:
        """Validate content for layer-appropriate language."""
        
        content_lower = content.lower()
        violations_found = False
        
        # Check for prohibited terms
        prohibited = self.rules.get('prohibited_terms', set())
        for term in prohibited:
            if re.search(r'\b' + re.escape(term.lower()) + r'\b', content_lower):
                self.violations.append({
                    'file': file_path,
                    'violation': f"Prohibited term '{term}' found in {self.layer} layer",
                    'type': 'language_mixing'
                })
                violations_found = True
        
        # Check for proper cross-layer references (if any)
        self._validate_cross_layer_references(content, file_path)
        
        return not violations_found
    
    def _validate_cross_layer_references(self, content: str, file_path: str):
        """Validate that cross-layer references use proper translation pattern."""
        
        # Look for references to other layers
        reference_patterns = [
            r'philosophical[_\s]+principle',
            r'business[_\s]+requirement',
            r'technical[_\s]+implementation'
        ]
        
        for pattern in reference_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Check if it's a proper translation reference
                context = content[max(0, match.start()-100):match.end()+100]
                if not self._is_proper_translation_reference(context):
                    self.violations.append({
                        'file': file_path,
                        'violation': f"Improper cross-layer reference: {match.group()}",
                        'type': 'improper_reference',
                        'context': context.strip()
                    })
    
    def _is_proper_translation_reference(self, context: str) -> bool:
        """Check if cross-layer reference uses proper translation pattern."""
        
        # Look for translation interface indicators
        translation_indicators = [
            'translate', 'reference', 'derive', 'map', 'convert',
            'interface', 'bridge', 'adapter'
        ]
        
        context_lower = context.lower()
        return any(indicator in context_lower for indicator in translation_indicators)
    
    def validate_directory(self, directory: Path) -> bool:
        """Validate all files in a directory."""
        
        if not directory.exists():
            print(f"Warning: Directory {directory} does not exist")
            return True
        
        file_patterns = self.rules.get('file_patterns', ['*'])
        all_valid = True
        
        for pattern in file_patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    if not self.validate_file(file_path):
                        all_valid = False
        
        return all_valid
    
    def get_violations_report(self) -> str:
        """Generate a detailed violations report."""
        
        if not self.violations:
            return f"✅ No layer separation violations found in {self.layer} layer"
        
        report = [f"❌ Layer separation violations found in {self.layer} layer:"]
        report.append("")
        
        for i, violation in enumerate(self.violations, 1):
            report.append(f"{i}. {violation['violation']}")
            report.append(f"   File: {violation['file']}")
            if 'context' in violation:
                report.append(f"   Context: {violation['context'][:100]}...")
            report.append("")
        
        return "\n".join(report)

def main():
    """Main validation function."""
    
    parser = argparse.ArgumentParser(description='Validate architectural layer separation')
    parser.add_argument('--layer', required=True, 
                       choices=['technical', 'business', 'philosophical'],
                       help='Layer to validate')
    parser.add_argument('--path', required=True, help='Path to validate')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    validator = LayerSeparationValidator(args.layer)
    path = Path(args.path)
    
    if args.verbose:
        print(f"🏗️ Validating {args.layer} layer separation in {path}")
    
    if path.is_file():
        is_valid = validator.validate_file(path)
    else:
        is_valid = validator.validate_directory(path)
    
    # Print report
    print(validator.get_violations_report())
    
    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
