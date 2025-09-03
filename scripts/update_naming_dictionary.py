#!/usr/bin/env python3
"""
🔍 Naming Dictionary Maintenance Script

Purpose: Automatically scan codebase and suggest new entries for the PROJECT_NAMING_DICTIONARY.md
Philosophy: Honor our Hilbert consistency by making all naming choices explicit and documented
Benefit: Keep the dictionary comprehensive and up-to-date with minimal manual effort
"""

import re
import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class NamingDictionaryUpdater:
    """
    🧮 Systematic scanner for discovering and documenting naming choices.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.dictionary_path = self.project_root / "docs" / "reference" / "PROJECT_NAMING_DICTIONARY.md"
        
        # Categories for classification
        self.naming_categories = {
            "mathematical": ["hilbert", "euler", "fibonacci", "gauss", "newton", "leibniz"],
            "philosophical": ["ancestors", "wisdom", "logical", "ancestral", "ancient"],
            "practical": ["manager", "factory", "handler", "processor", "analyzer", "generator"],
            "aspirational": ["divine", "sacred", "beautiful", "elegant", "harmony", "excellence"],
            "protective": ["secure", "safe", "guard", "protect", "validate", "verify", "resistant"]
        }
        
        # Current dictionary entries (to avoid duplicates)
        self.existing_entries = self._load_existing_entries()
    
    def _load_existing_entries(self) -> Set[str]:
        """Load entries that already exist in the dictionary."""
        existing = set()
        
        if self.dictionary_path.exists():
            content = self.dictionary_path.read_text(encoding='utf-8')
            # Extract entries using regex for #### **`name`**
            pattern = r'####\s*\*\*`([^`]+)`\*\*'
            matches = re.findall(pattern, content)
            existing.update(matches)
        
        return existing
    
    def scan_codebase(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """
        🔍 Scan entire codebase for naming patterns.
        Returns: {category: [(name, type, file_path), ...]}
        """
        discoveries = defaultdict(list)
        
        # Scan Python files
        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files:
            if self._should_scan_file(py_file):
                names = self._scan_python_file(py_file)
                for name, name_type in names:
                    if name not in self.existing_entries:
                        category = self._categorize_name(name)
                        discoveries[category].append((name, name_type, str(py_file.relative_to(self.project_root))))
        
        # Scan Markdown files for important concepts
        md_files = list(self.project_root.rglob("*.md"))
        for md_file in md_files:
            if self._should_scan_file(md_file):
                concepts = self._scan_markdown_file(md_file)
                for concept in concepts:
                    if concept not in self.existing_entries:
                        category = self._categorize_name(concept)
                        discoveries[category].append((concept, "concept", str(md_file.relative_to(self.project_root))))
        
        return dict(discoveries)
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """Determine if we should scan this file."""
        # Skip certain directories
        skip_dirs = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}
        if any(part in skip_dirs for part in file_path.parts):
            return False
        
        # Skip certain files
        skip_files = {"__init__.py", "setup.py"}
        if file_path.name in skip_files:
            return False
        
        return True
    
    def _scan_python_file(self, file_path: Path) -> List[Tuple[str, str]]:
        """
        🐍 Extract class names, function names, and important variables from Python files.
        """
        names = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    names.append((node.name, "class"))
                elif isinstance(node, ast.FunctionDef):
                    # Only include significant functions (not private/magic methods)
                    if not node.name.startswith('_'):
                        names.append((node.name, "function"))
                elif isinstance(node, ast.Assign):
                    # Extract important variable assignments
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id.isupper() or len(target.id) > 15:  # Constants or long descriptive names
                                names.append((target.id, "variable"))
        
        except Exception as e:
            print(f"⚠️ Could not parse {file_path}: {e}")
        
        return names
    
    def _scan_markdown_file(self, file_path: Path) -> List[str]:
        """
        📝 Extract important concepts from Markdown files.
        """
        concepts = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract concepts from headers
            header_pattern = r'^#+\s*\*\*([^*]+)\*\*'
            headers = re.findall(header_pattern, content, re.MULTILINE)
            concepts.extend(headers)
            
            # Extract concepts from bold text that looks like naming
            bold_pattern = r'\*\*([A-Z][A-Za-z_]+(?:\s+[A-Z][A-Za-z_]+)*)\*\*'
            bold_concepts = re.findall(bold_pattern, content)
            concepts.extend(bold_concepts)
            
            # Filter out common words and keep only significant concepts
            significant_concepts = []
            for concept in concepts:
                if len(concept) > 5 and not concept.lower() in ['purpose', 'status', 'example', 'note']:
                    significant_concepts.append(concept.replace(' ', '_').lower())
            
            return significant_concepts
        
        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")
            return []
    
    def _categorize_name(self, name: str) -> str:
        """
        🏷️ Categorize a name based on its content and pattern.
        """
        name_lower = name.lower()
        
        # Check each category
        for category, keywords in self.naming_categories.items():
            if any(keyword in name_lower for keyword in keywords):
                return category
        
        # Default categorization based on patterns
        if name.endswith('Agent') or name.endswith('Manager') or name.endswith('Factory'):
            return "practical"
        elif name.startswith('get_') or name.startswith('create_') or name.startswith('update_'):
            return "practical"
        elif any(word in name_lower for word in ['beautiful', 'elegant', 'divine', 'sacred']):
            return "aspirational"
        elif any(word in name_lower for word in ['validate', 'verify', 'secure', 'protect']):
            return "protective"
        else:
            return "uncategorized"
    
    def generate_dictionary_entries(self, discoveries: Dict[str, List[Tuple[str, str, str]]]) -> str:
        """
        📝 Generate formatted dictionary entries for new discoveries.
        """
        entries = []
        
        for category, items in discoveries.items():
            if not items:
                continue
            
            entries.append(f"\n## 🔍 **NEW {category.upper()} ENTRIES**\n")
            
            for name, name_type, file_path in sorted(items):
                entry = self._generate_single_entry(name, name_type, file_path, category)
                entries.append(entry)
        
        return "\n".join(entries)
    
    def _generate_single_entry(self, name: str, name_type: str, file_path: str, category: str) -> str:
        """
        📄 Generate a single dictionary entry with placeholders for manual completion.
        """
        # Determine category symbols
        category_symbols = {
            "mathematical": "🧮 Mathematical",
            "philosophical": "🏛️ Philosophical", 
            "practical": "⚡ Practical",
            "aspirational": "🌟 Aspirational",
            "protective": "🛡️ Protective",
            "uncategorized": "❓ Uncategorized"
        }
        
        category_symbol = category_symbols.get(category, "❓ Uncategorized")
        
        return f"""#### **`{name}`**
- **Type**: {name_type.title()}
- **Category**: {category_symbol}
- **File**: `{file_path}`
- **Intent**: [TODO: Describe the purpose and functionality]
- **Why This Name**: 
  - [TODO: Explain the naming choice]
  - [TODO: Connect to our philosophical or practical principles]
- **Ancestral Logic**: [TODO: Which ancestors/principles influenced this name?]
- **Usage**: [TODO: How is this used in the system?]

"""
    
    def generate_report(self) -> str:
        """
        📊 Generate a comprehensive report of naming discoveries.
        """
        discoveries = self.scan_codebase()
        
        # Statistics
        total_new = sum(len(items) for items in discoveries.values())
        total_existing = len(self.existing_entries)
        
        report = f"""# 🔍 **NAMING DICTIONARY UPDATE REPORT**

**Generated**: {self._get_timestamp()}  
**Project Root**: {self.project_root}  
**Dictionary Path**: {self.dictionary_path}  

## 📊 **STATISTICS**

- **Existing Entries**: {total_existing}
- **New Discoveries**: {total_new}
- **Coverage Increase**: {((total_new / (total_existing + total_new)) * 100):.1f}%

## 📈 **DISCOVERIES BY CATEGORY**

"""
        
        for category, items in sorted(discoveries.items()):
            report += f"- **{category.title()}**: {len(items)} new entries\n"
        
        report += "\n" + "=" * 60 + "\n"
        
        # Generate entries
        if total_new > 0:
            report += self.generate_dictionary_entries(discoveries)
        else:
            report += "\n✅ **No new entries found - dictionary is up to date!**\n"
        
        return report
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for the report."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def update_dictionary_file(self, append_new_entries: bool = True) -> None:
        """
        📝 Update the actual dictionary file with new entries.
        """
        if not append_new_entries:
            print("📋 Generating report only (not updating file)")
            return
        
        discoveries = self.scan_codebase()
        total_new = sum(len(items) for items in discoveries.values())
        
        if total_new == 0:
            print("✅ Dictionary is up to date - no new entries needed")
            return
        
        # Generate new entries
        new_entries = self.generate_dictionary_entries(discoveries)
        
        # Append to dictionary file
        with open(self.dictionary_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n---\n\n# 🆕 **AUTOMATICALLY DISCOVERED ENTRIES**\n")
            f.write(f"**Added**: {self._get_timestamp()}\n")
            f.write(new_entries)
        
        print(f"📝 Added {total_new} new entries to {self.dictionary_path}")
        print("⚠️ Note: New entries contain placeholders - please review and complete manually")


def main():
    """
    🚀 Main entry point for naming dictionary maintenance.
    """
    print("🔍 Naming Dictionary Maintenance Tool")
    print("=" * 50)
    
    updater = NamingDictionaryUpdater()
    
    # Generate and display report
    report = updater.generate_report()
    print(report)
    
    # Ask if user wants to update the file
    response = input("\n📝 Update dictionary file with new entries? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        updater.update_dictionary_file(append_new_entries=True)
        print("\n✅ Dictionary updated successfully!")
        print("📋 Next steps:")
        print("  1. Review the new entries in the dictionary file")
        print("  2. Complete the [TODO] placeholders with actual descriptions")
        print("  3. Ensure all entries follow our Hilbert consistency principles")
    else:
        print("\n📋 Report generated - dictionary file unchanged")


if __name__ == "__main__":
    main()
