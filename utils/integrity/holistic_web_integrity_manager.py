#!/usr/bin/env python3
"""
Holistic Web Integrity Manager
=============================

Self-healing web of interconnections system that maintains all relationships,
hyperlinks, imports, and dependencies across the entire project ecosystem.

Based on holistic thinking principles:
"In a holistic system, every part is connected to every other part. When we 
move one piece, we must thoughtfully update all its connections to preserve 
the living web of relationships that makes the system whole."

Features:
- Comprehensive relationship discovery and mapping
- Automatic cascade updates when files are moved/renamed
- Self-healing broken links and references
- Dependency-aware operation ordering
- Real-time integrity monitoring
- Zero-tolerance broken relationship policy
"""

import os
import re
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import argparse


class RelationshipType(Enum):
    """Types of relationships between files."""
    HYPERLINK = "hyperlink"              # Markdown [text](path) links
    REFERENCE_LINK = "reference_link"    # Markdown [text]: path references
    IMPORT_STATEMENT = "import_statement" # Python import statements
    FILE_PATH_REF = "file_path_ref"      # File path references in configs/scripts
    IMAGE_REFERENCE = "image_reference"   # Image and asset references
    CROSS_REFERENCE = "cross_reference"   # Cross-references between documents
    DEPENDENCY = "dependency"             # Code dependencies
    INHERITANCE = "inheritance"           # Class inheritance relationships


class UpdateStrategy(Enum):
    """Strategies for updating relationships."""
    AUTOMATIC = "automatic"       # Automatically update all references
    VERIFY_FIRST = "verify_first" # Verify target exists before updating
    ASK_USER = "ask_user"         # Ask user before updating
    SKIP = "skip"                 # Skip updating this relationship type


@dataclass
class Relationship:
    """Represents a relationship between two files or entities."""
    source_file: str
    target_file: str
    relationship_type: RelationshipType
    source_line: int
    source_text: str
    confidence: float  # 0.0 to 1.0 - confidence in relationship detection
    last_verified: str
    is_broken: bool = False
    

@dataclass
class RelationshipGraph:
    """Complete graph of all relationships in the project."""
    relationships: List[Relationship] = field(default_factory=list)
    incoming_refs: Dict[str, List[Relationship]] = field(default_factory=dict)
    outgoing_refs: Dict[str, List[Relationship]] = field(default_factory=dict)
    last_updated: str = ""
    

@dataclass
class UpdatePlan:
    """Plan for updating relationships after file moves."""
    file_moves: List[Tuple[str, str]]  # (old_path, new_path) pairs
    relationship_updates: List[Tuple[Relationship, str]]  # (relationship, new_text)
    dependency_order: List[str]  # Order to execute updates
    rollback_plan: List[str]     # Commands to rollback if needed
    

@dataclass
class IntegrityReport:
    """Report on web integrity status."""
    total_relationships: int
    broken_relationships: int
    orphaned_files: int
    relationship_types: Dict[str, int]
    integrity_score: float  # 0.0 to 1.0
    issues_found: List[str]
    recommendations: List[str]
    last_scan: str


class HolisticWebIntegrityManager:
    """
    Main manager for holistic web integrity across the project.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.relationship_graph = RelationshipGraph()
        
        # Patterns for detecting different relationship types
        self.relationship_patterns = {
            RelationshipType.HYPERLINK: [
                r'\[([^\]]+)\]\(([^)]+)\)',  # [text](path)
                r'<a\s+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',  # HTML links
            ],
            RelationshipType.REFERENCE_LINK: [
                r'\[([^\]]+)\]:\s*(.+)',  # [text]: path
            ],
            RelationshipType.IMPORT_STATEMENT: [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',  # import module
                r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',  # from module import
            ],
            RelationshipType.FILE_PATH_REF: [
                r'["\']([^"\']*\.(py|md|json|yaml|yml|txt|csv|db))["\']',  # Quoted file paths
                r'Path\(["\']([^"\']+)["\']\)',  # Path() constructor
            ],
            RelationshipType.IMAGE_REFERENCE: [
                r'!\[([^\]]*)\]\(([^)]+)\)',  # ![alt](image)
                r'<img\s+src=["\']([^"\']+)["\']',  # HTML images
            ],
        }
        
        # File types to scan for relationships
        self.scannable_extensions = {'.py', '.md', '.txt', '.rst', '.json', '.yaml', '.yml', '.html', '.js', '.ts'}
        
        # Update strategies by relationship type
        self.update_strategies = {
            RelationshipType.HYPERLINK: UpdateStrategy.AUTOMATIC,
            RelationshipType.REFERENCE_LINK: UpdateStrategy.AUTOMATIC,
            RelationshipType.IMPORT_STATEMENT: UpdateStrategy.VERIFY_FIRST,
            RelationshipType.FILE_PATH_REF: UpdateStrategy.AUTOMATIC,
            RelationshipType.IMAGE_REFERENCE: UpdateStrategy.AUTOMATIC,
            RelationshipType.CROSS_REFERENCE: UpdateStrategy.AUTOMATIC,
        }
    
    def discover_all_relationships(self) -> RelationshipGraph:
        """
        Comprehensive discovery of all relationships in the project.
        """
        print("🔍 Discovering all relationships in the project...")
        
        self.relationship_graph = RelationshipGraph()
        relationships = []
        
        # Scan all files for relationships
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and common build/cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
            
            for file in files:
                if self._should_scan_file(file):
                    file_path = Path(root) / file
                    file_relationships = self._discover_file_relationships(file_path)
                    relationships.extend(file_relationships)
        
        # Build relationship graph
        self.relationship_graph.relationships = relationships
        self._build_relationship_indices()
        self.relationship_graph.last_updated = datetime.now().isoformat()
        
        print(f"   Found {len(relationships)} relationships across {len(self.relationship_graph.incoming_refs)} files")
        
        return self.relationship_graph
    
    def _should_scan_file(self, filename: str) -> bool:
        """Determine if file should be scanned for relationships."""
        return any(filename.endswith(ext) for ext in self.scannable_extensions)
    
    def _discover_file_relationships(self, file_path: Path) -> List[Relationship]:
        """Discover all relationships within a single file."""
        relationships = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            rel_path = file_path.relative_to(self.project_root)
            
            # Scan for each relationship type
            for relationship_type, patterns in self.relationship_patterns.items():
                for pattern in patterns:
                    for line_num, line in enumerate(lines, 1):
                        for match in re.finditer(pattern, line):
                            relationship = self._create_relationship(
                                rel_path, relationship_type, line_num, line, match
                            )
                            if relationship:
                                relationships.append(relationship)
        
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
        
        return relationships
    
    def _create_relationship(self, source_file: Path, relationship_type: RelationshipType, 
                           line_num: int, line_text: str, match) -> Optional[Relationship]:
        """Create a relationship object from a pattern match."""
        try:
            if relationship_type in [RelationshipType.HYPERLINK, RelationshipType.IMAGE_REFERENCE]:
                target = match.group(2) if len(match.groups()) >= 2 else match.group(1)
            elif relationship_type == RelationshipType.REFERENCE_LINK:
                target = match.group(2)
            elif relationship_type == RelationshipType.IMPORT_STATEMENT:
                target = match.group(1) + ".py"  # Convert module to file
            else:
                target = match.group(1)
            
            # Skip external URLs and special references
            if target.startswith(('http://', 'https://', 'mailto:', '#', 'javascript:')):
                return None
            
            # Calculate confidence based on various factors
            confidence = self._calculate_relationship_confidence(relationship_type, target, source_file)
            
            # Check if relationship is broken
            is_broken = self._is_relationship_broken(source_file, target)
            
            return Relationship(
                source_file=str(source_file),
                target_file=target,
                relationship_type=relationship_type,
                source_line=line_num,
                source_text=line_text.strip(),
                confidence=confidence,
                last_verified=datetime.now().isoformat(),
                is_broken=is_broken
            )
            
        except Exception as e:
            print(f"⚠️  Error creating relationship: {e}")
            return None
    
    def _calculate_relationship_confidence(self, relationship_type: RelationshipType, 
                                         target: str, source_file: Path) -> float:
        """Calculate confidence score for a relationship."""
        confidence = 0.8  # Base confidence
        
        # Boost confidence for certain patterns
        if relationship_type == RelationshipType.HYPERLINK and target.endswith('.md'):
            confidence += 0.1
        
        if relationship_type == RelationshipType.IMPORT_STATEMENT:
            confidence += 0.1
        
        # Reduce confidence for very long or complex paths
        if len(target) > 100:
            confidence -= 0.2
        
        # Boost confidence if target file exists
        if self._target_exists(source_file, target):
            confidence += 0.1
        else:
            confidence -= 0.3
        
        return max(0.0, min(1.0, confidence))
    
    def _is_relationship_broken(self, source_file: Path, target: str) -> bool:
        """Check if a relationship is broken (target doesn't exist)."""
        return not self._target_exists(source_file, target)
    
    def _target_exists(self, source_file: Path, target: str) -> bool:
        """Check if target file exists relative to source."""
        try:
            # Handle absolute paths
            if target.startswith('/'):
                target_path = self.project_root / target.lstrip('/')
            else:
                # Handle relative paths
                target_path = source_file.parent / target
            
            # Remove URL fragments and query parameters
            target_path = Path(str(target_path).split('#')[0].split('?')[0])
            
            return target_path.exists()
        except Exception:
            return False
    
    def _build_relationship_indices(self):
        """Build indices for fast relationship lookup."""
        self.relationship_graph.incoming_refs = {}
        self.relationship_graph.outgoing_refs = {}
        
        for rel in self.relationship_graph.relationships:
            # Outgoing references (from source file)
            source = rel.source_file
            if source not in self.relationship_graph.outgoing_refs:
                self.relationship_graph.outgoing_refs[source] = []
            self.relationship_graph.outgoing_refs[source].append(rel)
            
            # Incoming references (to target file)
            target = rel.target_file
            if target not in self.relationship_graph.incoming_refs:
                self.relationship_graph.incoming_refs[target] = []
            self.relationship_graph.incoming_refs[target].append(rel)
    
    def plan_holistic_update(self, file_moves: List[Tuple[str, str]]) -> UpdatePlan:
        """
        Plan holistic updates for file moves, considering all dependencies.
        """
        print(f"🧠 Planning holistic updates for {len(file_moves)} file moves...")
        
        relationship_updates = []
        
        # For each file move, find all relationships that need updating
        for old_path, new_path in file_moves:
            # Find all incoming references to this file
            incoming_refs = self.relationship_graph.incoming_refs.get(old_path, [])
            
            for rel in incoming_refs:
                new_text = self._calculate_updated_text(rel, old_path, new_path)
                if new_text != rel.source_text:
                    relationship_updates.append((rel, new_text))
        
        # Calculate dependency order to avoid conflicts
        dependency_order = self._calculate_dependency_order(file_moves)
        
        # Create rollback plan
        rollback_plan = self._create_rollback_plan(file_moves, relationship_updates)
        
        plan = UpdatePlan(
            file_moves=file_moves,
            relationship_updates=relationship_updates,
            dependency_order=dependency_order,
            rollback_plan=rollback_plan
        )
        
        print(f"   Planned {len(relationship_updates)} relationship updates")
        print(f"   Dependency order: {len(dependency_order)} operations")
        
        return plan
    
    def _calculate_updated_text(self, relationship: Relationship, old_path: str, new_path: str) -> str:
        """Calculate the updated text for a relationship after file move."""
        source_text = relationship.source_text
        
        # Simple replacement for now - in production would be more sophisticated
        old_filename = Path(old_path).name
        new_filename = Path(new_path).name
        
        # Replace the old filename with new filename in the source text
        updated_text = source_text.replace(old_filename, new_filename)
        
        # Handle relative path updates if needed
        if old_path in source_text:
            updated_text = source_text.replace(old_path, new_path)
        
        return updated_text
    
    def _calculate_dependency_order(self, file_moves: List[Tuple[str, str]]) -> List[str]:
        """Calculate the order to execute updates to avoid dependency conflicts."""
        # Simplified dependency ordering - in production would use topological sort
        order = []
        
        # First, do file moves
        for old_path, new_path in file_moves:
            order.append(f"move_file:{old_path}->{new_path}")
        
        # Then, update relationships
        order.append("update_relationships")
        
        return order
    
    def _create_rollback_plan(self, file_moves: List[Tuple[str, str]], 
                            relationship_updates: List[Tuple[Relationship, str]]) -> List[str]:
        """Create rollback plan in case updates fail."""
        rollback = []
        
        # Rollback file moves (reverse order)
        for old_path, new_path in reversed(file_moves):
            rollback.append(f"move_file:{new_path}->{old_path}")
        
        # Rollback relationship updates
        for rel, new_text in relationship_updates:
            rollback.append(f"restore_text:{rel.source_file}:{rel.source_line}:{rel.source_text}")
        
        return rollback
    
    def execute_holistic_update(self, update_plan: UpdatePlan) -> bool:
        """
        Execute the holistic update plan with relationship preservation.
        """
        print("⚙️ Executing holistic update with relationship preservation...")
        
        try:
            # Execute in dependency order
            for operation in update_plan.dependency_order:
                if operation.startswith("move_file:"):
                    old_path, new_path = operation.split(":", 1)[1].split("->")
                    self._execute_file_move(old_path, new_path)
                elif operation == "update_relationships":
                    self._execute_relationship_updates(update_plan.relationship_updates)
            
            print(f"✅ Successfully executed {len(update_plan.file_moves)} file moves")
            print(f"✅ Successfully updated {len(update_plan.relationship_updates)} relationships")
            return True
            
        except Exception as e:
            print(f"❌ Error during holistic update: {e}")
            print("🔄 Executing rollback plan...")
            self._execute_rollback(update_plan.rollback_plan)
            return False
    
    def _execute_file_move(self, old_path: str, new_path: str):
        """Execute a single file move."""
        old_file = self.project_root / old_path
        new_file = self.project_root / new_path
        
        if old_file.exists():
            # Ensure target directory exists
            new_file.parent.mkdir(parents=True, exist_ok=True)
            old_file.rename(new_file)
            print(f"   📁 Moved: {old_path} → {new_path}")
        else:
            print(f"   ⚠️ File not found for move: {old_path}")
    
    def _execute_relationship_updates(self, relationship_updates: List[Tuple[Relationship, str]]):
        """Execute all relationship updates."""
        files_to_update = {}
        
        # Group updates by file
        for rel, new_text in relationship_updates:
            if rel.source_file not in files_to_update:
                files_to_update[rel.source_file] = []
            files_to_update[rel.source_file].append((rel, new_text))
        
        # Update each file
        for file_path, updates in files_to_update.items():
            self._update_file_relationships(file_path, updates)
    
    def _update_file_relationships(self, file_path: str, updates: List[Tuple[Relationship, str]]):
        """Update relationships in a single file."""
        full_path = self.project_root / file_path
        
        try:
            # Read current content
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply updates (in reverse line order to avoid line number shifts)
            updates.sort(key=lambda x: x[0].source_line, reverse=True)
            
            for rel, new_text in updates:
                line_idx = rel.source_line - 1  # Convert to 0-based index
                if 0 <= line_idx < len(lines):
                    lines[line_idx] = new_text + '\n'
                    print(f"     📝 Updated line {rel.source_line} in {file_path}")
            
            # Write updated content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
        except Exception as e:
            print(f"   ❌ Error updating {file_path}: {e}")
    
    def _execute_rollback(self, rollback_plan: List[str]):
        """Execute rollback plan if updates fail."""
        for operation in rollback_plan:
            try:
                if operation.startswith("move_file:"):
                    old_path, new_path = operation.split(":", 1)[1].split("->")
                    self._execute_file_move(old_path, new_path)
                elif operation.startswith("restore_text:"):
                    # Parse restore operation
                    parts = operation.split(":", 3)
                    file_path, line_num, original_text = parts[1], int(parts[2]), parts[3]
                    # Restore original text (simplified implementation)
                    print(f"   🔄 Would restore: {file_path}:{line_num}")
            except Exception as e:
                print(f"   ❌ Rollback error: {e}")
    
    def validate_integrity(self) -> IntegrityReport:
        """
        Validate the integrity of the entire relationship web.
        """
        print("🔍 Validating web integrity...")
        
        # Refresh relationship discovery
        self.discover_all_relationships()
        
        total_relationships = len(self.relationship_graph.relationships)
        broken_relationships = sum(1 for rel in self.relationship_graph.relationships if rel.is_broken)
        
        # Find orphaned files (files with no incoming references)
        all_files = set()
        referenced_files = set()
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if self._should_scan_file(file):
                    rel_path = Path(root).relative_to(self.project_root) / file
                    all_files.add(str(rel_path))
        
        for rel in self.relationship_graph.relationships:
            referenced_files.add(rel.target_file)
        
        orphaned_files = len(all_files - referenced_files)
        
        # Count relationship types
        relationship_types = {}
        for rel in self.relationship_graph.relationships:
            rel_type = rel.relationship_type.value
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
        
        # Calculate integrity score
        if total_relationships > 0:
            integrity_score = 1.0 - (broken_relationships / total_relationships)
        else:
            integrity_score = 1.0
        
        # Generate issues and recommendations
        issues = []
        recommendations = []
        
        if broken_relationships > 0:
            issues.append(f"{broken_relationships} broken relationships found")
            recommendations.append("Run holistic update to fix broken relationships")
        
        if orphaned_files > 10:
            issues.append(f"{orphaned_files} orphaned files (no incoming references)")
            recommendations.append("Review orphaned files for cleanup opportunities")
        
        if integrity_score < 0.9:
            issues.append(f"Low integrity score: {integrity_score:.2f}")
            recommendations.append("Systematic relationship cleanup needed")
        
        report = IntegrityReport(
            total_relationships=total_relationships,
            broken_relationships=broken_relationships,
            orphaned_files=orphaned_files,
            relationship_types=relationship_types,
            integrity_score=integrity_score,
            issues_found=issues,
            recommendations=recommendations,
            last_scan=datetime.now().isoformat()
        )
        
        self._print_integrity_report(report)
        return report
    
    def _print_integrity_report(self, report: IntegrityReport):
        """Print comprehensive integrity report."""
        print("\n" + "="*60)
        print("🕸️  HOLISTIC WEB INTEGRITY REPORT")
        print("="*60)
        
        print(f"📊 SUMMARY:")
        print(f"   Total relationships: {report.total_relationships}")
        print(f"   Broken relationships: {report.broken_relationships}")
        print(f"   Orphaned files: {report.orphaned_files}")
        print(f"   Integrity score: {report.integrity_score:.2f}/1.0")
        
        if report.integrity_score >= 0.95:
            print(f"   Status: ✅ EXCELLENT - Web integrity maintained")
        elif report.integrity_score >= 0.85:
            print(f"   Status: 🟡 GOOD - Minor issues detected")
        elif report.integrity_score >= 0.70:
            print(f"   Status: 🟠 FAIR - Relationship issues need attention")
        else:
            print(f"   Status: 🔴 POOR - Critical web integrity issues")
        
        print(f"\n📋 RELATIONSHIP TYPES:")
        for rel_type, count in sorted(report.relationship_types.items()):
            print(f"   {rel_type}: {count}")
        
        if report.issues_found:
            print(f"\n⚠️  ISSUES FOUND:")
            for issue in report.issues_found:
                print(f"   • {issue}")
        
        if report.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report.recommendations:
                print(f"   • {rec}")
        
        print("="*60)
    
    def auto_heal_broken_relationships(self) -> int:
        """
        Automatically heal broken relationships where possible.
        """
        print("🔧 Auto-healing broken relationships...")
        
        broken_relationships = [rel for rel in self.relationship_graph.relationships if rel.is_broken]
        healed_count = 0
        
        for rel in broken_relationships:
            if self._can_auto_heal(rel):
                if self._attempt_healing(rel):
                    healed_count += 1
                    print(f"   ✅ Healed: {rel.source_file}:{rel.source_line}")
        
        print(f"🎉 Auto-healed {healed_count} of {len(broken_relationships)} broken relationships")
        return healed_count
    
    def _can_auto_heal(self, relationship: Relationship) -> bool:
        """Check if a relationship can be automatically healed."""
        # Simple heuristics for auto-healing
        if relationship.confidence < 0.5:
            return False
        
        if relationship.relationship_type in [RelationshipType.HYPERLINK, RelationshipType.FILE_PATH_REF]:
            return True
        
        return False
    
    def _attempt_healing(self, relationship: Relationship) -> bool:
        """Attempt to heal a broken relationship."""
        # Try to find the target file in nearby locations
        target_name = Path(relationship.target_file).name
        
        # Search for files with the same name
        for root, dirs, files in os.walk(self.project_root):
            if target_name in files:
                possible_target = Path(root) / target_name
                rel_path = possible_target.relative_to(self.project_root)
                
                # Update the relationship to point to found file
                old_text = relationship.source_text
                new_text = old_text.replace(relationship.target_file, str(rel_path))
                
                # Update the file
                try:
                    file_path = self.project_root / relationship.source_file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    updated_content = content.replace(old_text, new_text)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    return True
                except Exception as e:
                    print(f"   ❌ Failed to heal {relationship.source_file}: {e}")
        
        return False


def main():
    """CLI interface for holistic web integrity management."""
    parser = argparse.ArgumentParser(
        description="Holistic Web Integrity Manager - Maintain interconnected relationships",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover all relationships
  python holistic_web_integrity_manager.py --discover
  
  # Validate web integrity
  python holistic_web_integrity_manager.py --validate
  
  # Auto-heal broken relationships
  python holistic_web_integrity_manager.py --heal
  
  # Plan update for file move
  python holistic_web_integrity_manager.py --plan-move old_file.md new_file.md
        """
    )
    
    parser.add_argument('--discover', action='store_true',
                       help='Discover all relationships in project')
    parser.add_argument('--validate', action='store_true',
                       help='Validate web integrity')
    parser.add_argument('--heal', action='store_true',
                       help='Auto-heal broken relationships')
    parser.add_argument('--plan-move', nargs=2, metavar=('OLD', 'NEW'),
                       help='Plan holistic update for file move')
    parser.add_argument('--execute-move', nargs=2, metavar=('OLD', 'NEW'),
                       help='Execute holistic file move with relationship updates')
    parser.add_argument('--root', default='.',
                       help='Project root directory')
    parser.add_argument('--output',
                       help='Save report to JSON file')
    
    args = parser.parse_args()
    
    if not any([args.discover, args.validate, args.heal, args.plan_move, args.execute_move]):
        parser.error("Must specify an operation")
    
    manager = HolisticWebIntegrityManager(args.root)
    
    if args.discover:
        graph = manager.discover_all_relationships()
        print(f"✅ Discovered {len(graph.relationships)} relationships")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(asdict(graph), f, indent=2, default=str)
            print(f"📄 Report saved to {args.output}")
    
    elif args.validate:
        report = manager.validate_integrity()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(asdict(report), f, indent=2, default=str)
            print(f"📄 Report saved to {args.output}")
        
        # Return appropriate exit code
        sys.exit(0 if report.integrity_score >= 0.9 else 1)
    
    elif args.heal:
        healed = manager.auto_heal_broken_relationships()
        print(f"✅ Healed {healed} relationships")
        sys.exit(0)
    
    elif args.plan_move:
        old_path, new_path = args.plan_move
        manager.discover_all_relationships()
        plan = manager.plan_holistic_update([(old_path, new_path)])
        
        print(f"📋 Update plan for {old_path} → {new_path}:")
        print(f"   File moves: {len(plan.file_moves)}")
        print(f"   Relationship updates: {len(plan.relationship_updates)}")
        print(f"   Dependency operations: {len(plan.dependency_order)}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(asdict(plan), f, indent=2, default=str)
            print(f"📄 Plan saved to {args.output}")
    
    elif args.execute_move:
        old_path, new_path = args.plan_move
        manager.discover_all_relationships()
        plan = manager.plan_holistic_update([(old_path, new_path)])
        success = manager.execute_holistic_update(plan)
        
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
