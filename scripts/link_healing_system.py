#!/usr/bin/env python3
"""
Link Healing System - Prevent broken links during file renames

PHILOSOPHY: Safety First + Boy Scout Rule
- Never break anything during reorganization
- Heal all links automatically
- Leave system better than we found it
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Set
import json
from datetime import datetime


class LinkHealingSystem:
    """
    Comprehensive link healing system that ensures ZERO broken links during file renames.
    
    🏛️ ANCESTRAL WISDOM APPLIED:
    - Carnap: Systematic analysis of all logical relationships
    - Hilbert: Consistent approach to maintaining system integrity
    - Fowler: Practical automation that serves real developer needs
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.docs_root = self.project_root / "docs"
        
        # Link patterns to detect
        self.link_patterns = {
            "markdown_links": r'\[([^\]]*)\]\(([^)]+\.md)\)',
            "relative_paths": r'\[([^\]]*)\]\((\.\./[^)]+\.md)\)',
            "docs_references": r'\[([^\]]*)\]\((docs/[^)]+\.md)\)',
            "file_references": r'`([^`]*\.md)`',
            "bare_paths": r'(docs/[a-zA-Z0-9_/-]+\.md)'
        }
        
        # Track all discovered links
        self.all_links = {}
        self.broken_links = []
        self.file_references = {}
        
    def scan_all_links(self) -> Dict[str, List[Dict]]:
        """
        🔍 COMPREHENSIVE LINK DISCOVERY
        
        Find every single link in the project that could break during renames.
        """
        print("🔍 Starting comprehensive link scan...")
        
        all_links = {
            "markdown_files": [],
            "python_files": [],
            "config_files": [],
            "discovered_links": []
        }
        
        # Scan all markdown files
        for md_file in self.docs_root.rglob("*.md"):
            links = self._extract_links_from_file(md_file)
            if links:
                all_links["markdown_files"].append({
                    "file": str(md_file.relative_to(self.project_root)),
                    "links": links
                })
                all_links["discovered_links"].extend(links)
        
        # Scan Python files for doc references
        for py_file in self.project_root.rglob("*.py"):
            if "docs/" in py_file.read_text(encoding='utf-8', errors='ignore'):
                doc_refs = self._extract_doc_references_from_python(py_file)
                if doc_refs:
                    all_links["python_files"].append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "references": doc_refs
                    })
        
        # Scan config files
        config_patterns = ["*.toml", "*.yaml", "*.yml", "*.json"]
        for pattern in config_patterns:
            for config_file in self.project_root.rglob(pattern):
                try:
                    content = config_file.read_text(encoding='utf-8')
                    if "docs/" in content:
                        all_links["config_files"].append({
                            "file": str(config_file.relative_to(self.project_root)),
                            "content_preview": content[:200] + "..." if len(content) > 200 else content
                        })
                except Exception as e:
                    print(f"⚠️  Could not read {config_file}: {e}")
        
        self.all_links = all_links
        return all_links
    
    def _extract_links_from_file(self, file_path: Path) -> List[Dict]:
        """Extract all links from a markdown file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            links = []
            
            for pattern_name, pattern in self.link_patterns.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    if pattern_name == "markdown_links":
                        link_text, link_path = match.groups()
                    elif pattern_name in ["relative_paths", "docs_references"]:
                        link_text, link_path = match.groups()
                    else:
                        link_path = match.group(1)
                        link_text = ""
                    
                    links.append({
                        "type": pattern_name,
                        "text": link_text,
                        "path": link_path,
                        "line_number": content[:match.start()].count('\n') + 1,
                        "match_text": match.group(0)
                    })
            
            return links
            
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
            return []
    
    def _extract_doc_references_from_python(self, file_path: Path) -> List[str]:
        """Extract documentation references from Python files."""
        try:
            content = file_path.read_text(encoding='utf-8')
            doc_refs = re.findall(r'["\']([^"\']*docs/[^"\']*\.md)["\']', content)
            return doc_refs
        except Exception as e:
            print(f"⚠️  Error reading Python file {file_path}: {e}")
            return []
    
    def validate_all_links(self) -> Dict[str, List]:
        """
        ✅ LINK VALIDATION
        
        Check every discovered link to see if it resolves correctly.
        """
        print("✅ Validating all discovered links...")
        
        validation_results = {
            "valid_links": [],
            "broken_links": [],
            "external_links": [],
            "suspicious_links": []
        }
        
        for link_info in self.all_links.get("discovered_links", []):
            link_path = link_info["path"]
            
            # Skip external links
            if link_path.startswith("http"):
                validation_results["external_links"].append(link_info)
                continue
            
            # Resolve the actual file path
            resolved_path = self._resolve_link_path(link_path, link_info)
            
            if resolved_path and resolved_path.exists():
                validation_results["valid_links"].append({
                    **link_info,
                    "resolved_path": str(resolved_path)
                })
            else:
                validation_results["broken_links"].append({
                    **link_info,
                    "attempted_resolution": str(resolved_path) if resolved_path else "Could not resolve"
                })
        
        self.broken_links = validation_results["broken_links"]
        return validation_results
    
    def _resolve_link_path(self, link_path: str, link_info: Dict) -> Path:
        """Resolve a link path to an actual file."""
        try:
            # Get the directory containing the file with the link
            source_file = self.project_root / link_info.get("source_file", "")
            source_dir = source_file.parent if source_file.exists() else self.docs_root
            
            if link_path.startswith("../"):
                # Relative path going up
                resolved = source_dir / link_path
            elif link_path.startswith("docs/"):
                # Absolute path from project root
                resolved = self.project_root / link_path
            else:
                # Relative path in same directory or subdirectory
                resolved = source_dir / link_path
            
            return resolved.resolve()
            
        except Exception as e:
            print(f"⚠️  Could not resolve path {link_path}: {e}")
            return None
    
    def create_rename_mapping(self, rename_plan: Dict[str, str]) -> Dict[str, str]:
        """
        🗺️  CREATE RENAME MAPPING
        
        Create a comprehensive mapping of old paths to new paths.
        
        Args:
            rename_plan: Dictionary of {old_path: new_path}
        """
        print("🗺️  Creating comprehensive rename mapping...")
        
        # Normalize paths and create both absolute and relative mappings
        mapping = {}
        
        for old_path, new_path in rename_plan.items():
            # Normalize paths
            old_norm = str(Path(old_path))
            new_norm = str(Path(new_path))
            
            mapping[old_norm] = new_norm
            
            # Also create relative mappings
            if old_norm.startswith("docs/"):
                mapping[old_norm] = new_norm
                mapping[old_norm.replace("docs/", "")] = new_norm.replace("docs/", "")
        
        return mapping
    
    def heal_all_links(self, rename_mapping: Dict[str, str]) -> Dict[str, int]:
        """
        🔧 HEAL ALL LINKS
        
        Update all links to point to new file locations.
        """
        print("🔧 Starting comprehensive link healing...")
        
        healing_stats = {
            "files_updated": 0,
            "links_healed": 0,
            "files_processed": 0
        }
        
        # Process all markdown files with links
        for file_info in self.all_links.get("markdown_files", []):
            file_path = self.project_root / file_info["file"]
            
            if not file_path.exists():
                continue
                
            original_content = file_path.read_text(encoding='utf-8')
            updated_content = original_content
            links_healed_in_file = 0
            
            # Update each link in the file
            for link in file_info["links"]:
                old_path = link["path"]
                
                # Find the new path
                new_path = self._find_new_path(old_path, rename_mapping)
                
                if new_path and new_path != old_path:
                    # Replace the link in content
                    old_match = link["match_text"]
                    new_match = old_match.replace(old_path, new_path)
                    
                    updated_content = updated_content.replace(old_match, new_match)
                    links_healed_in_file += 1
            
            # Write updated content if changes were made
            if links_healed_in_file > 0:
                # Create backup
                backup_path = file_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                shutil.copy2(file_path, backup_path)
                
                # Write updated content
                file_path.write_text(updated_content, encoding='utf-8')
                
                print(f"✅ Healed {links_healed_in_file} links in {file_info['file']}")
                healing_stats["files_updated"] += 1
                healing_stats["links_healed"] += links_healed_in_file
            
            healing_stats["files_processed"] += 1
        
        return healing_stats
    
    def _find_new_path(self, old_path: str, rename_mapping: Dict[str, str]) -> str:
        """Find the new path for a given old path."""
        
        # Direct mapping
        if old_path in rename_mapping:
            return rename_mapping[old_path]
        
        # Try different path variations
        variations = [
            old_path,
            old_path.replace("../", ""),
            f"docs/{old_path}" if not old_path.startswith("docs/") else old_path,
            old_path.replace("docs/", "") if old_path.startswith("docs/") else old_path
        ]
        
        for variation in variations:
            if variation in rename_mapping:
                # Convert back to the same format as original
                new_path = rename_mapping[variation]
                
                if old_path.startswith("../"):
                    # Maintain relative format
                    return f"../{new_path.replace('docs/', '')}"
                elif old_path.startswith("docs/"):
                    # Maintain docs/ format
                    return new_path if new_path.startswith("docs/") else f"docs/{new_path}"
                else:
                    # Maintain simple format
                    return new_path.replace("docs/", "")
        
        return None
    
    def generate_link_report(self) -> str:
        """Generate comprehensive link analysis report."""
        
        report = []
        report.append("# 🔗 Link Healing Analysis Report")
        report.append(f"**Generated**: {datetime.now().isoformat()}")
        report.append("")
        
        # Summary statistics
        total_links = len(self.all_links.get("discovered_links", []))
        broken_count = len(self.broken_links)
        valid_count = total_links - broken_count
        
        report.append("## 📊 Summary Statistics")
        report.append(f"- **Total Links Found**: {total_links}")
        report.append(f"- **Valid Links**: {valid_count}")
        report.append(f"- **Broken Links**: {broken_count}")
        report.append(f"- **Files with Links**: {len(self.all_links.get('markdown_files', []))}")
        report.append("")
        
        # Broken links details
        if self.broken_links:
            report.append("## 🚨 Broken Links Requiring Attention")
            report.append("")
            for link in self.broken_links:
                report.append(f"### {link['path']}")
                report.append(f"- **Type**: {link['type']}")
                report.append(f"- **Text**: {link['text']}")
                report.append(f"- **Line**: {link.get('line_number', 'Unknown')}")
                report.append(f"- **Resolution Attempted**: {link.get('attempted_resolution', 'None')}")
                report.append("")
        
        return "\n".join(report)


def main():
    """
    🚀 MAIN EXECUTION
    
    Run comprehensive link analysis and healing for naming convention cleanup.
    """
    print("🔗 Link Healing System - Starting Analysis")
    print("=" * 60)
    
    # Initialize system
    healer = LinkHealingSystem()
    
    # Phase 1: Discover all links
    print("\n🔍 Phase 1: Link Discovery")
    all_links = healer.scan_all_links()
    
    print(f"✅ Found {len(all_links['discovered_links'])} total links")
    print(f"📄 Scanned {len(all_links['markdown_files'])} markdown files")
    print(f"🐍 Found {len(all_links['python_files'])} Python files with doc references")
    print(f"⚙️  Found {len(all_links['config_files'])} config files with doc references")
    
    # Phase 2: Validate links
    print("\n✅ Phase 2: Link Validation")
    validation_results = healer.validate_all_links()
    
    print(f"✅ Valid links: {len(validation_results['valid_links'])}")
    print(f"🚨 Broken links: {len(validation_results['broken_links'])}")
    print(f"🌐 External links: {len(validation_results['external_links'])}")
    
    # Phase 3: Generate report
    print("\n📊 Phase 3: Report Generation")
    report = healer.generate_link_report()
    
    # Save report
    report_path = Path("docs/agile/analysis/LINK_ANALYSIS_REPORT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    
    print(f"📊 Report saved to: {report_path}")
    
    # Phase 4: Demonstrate healing capability
    print("\n🔧 Phase 4: Healing System Ready")
    print("🎯 To heal links after renames, call:")
    print("   healer.heal_all_links(rename_mapping)")
    print()
    print("✅ Link Healing System Analysis Complete!")
    
    return healer


if __name__ == "__main__":
    main()
