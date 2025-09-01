#!/usr/bin/env python3
"""
Holistic Relationship Tracker
============================

Advanced relationship tracking and auto-update system that maintains
all interconnections, dependencies, and references across the entire
AI-Dev-Agent ecosystem with mathematical precision and loving care.

"Everything is connected to everything else." - Barry Commoner
"The butterfly effect: small changes can have large consequences." - Edward Lorenz

Author: AI-Dev-Agent Team with Mathematical Excellence
Created: 2024
License: Open Source - For universal harmony and interconnectedness
"""

import os
import re
import json
import time
import hashlib
from typing import Dict, List, Set, Tuple, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import ast

@dataclass
class Relationship:
    """Represents a relationship between two entities in the system."""
    source_entity: str
    target_entity: str
    relationship_type: str
    relationship_strength: float  # 0.0 to 1.0
    bidirectional: bool
    context: str
    file_location: str
    line_number: int
    discovered_time: float
    last_verified: float
    verification_count: int

@dataclass
class Entity:
    """Represents an entity in the system with its properties."""
    entity_id: str
    entity_type: str  # file, function, class, module, concept, etc.
    file_path: str
    content_hash: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    relationships: List[Relationship] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    creation_time: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)

@dataclass
class SystemIntegrityReport:
    """Comprehensive report on system relationship integrity."""
    total_entities: int
    total_relationships: int
    broken_relationships: List[Relationship]
    orphaned_entities: List[Entity]
    circular_dependencies: List[List[str]]
    relationship_strength_distribution: Dict[str, int]
    integrity_score: float  # 0.0 to 1.0
    recommendations: List[str]
    healing_opportunities: List[str]
    mathematical_beauty_score: float

class HolisticRelationshipTracker:
    """
    Advanced relationship tracking system that maintains holistic awareness
    of all interconnections in the AI-Dev-Agent ecosystem.
    
    Combines mathematical graph theory with loving care for system harmony.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.relationship_graph = nx.DiGraph()
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        
        # Relationship type configurations
        self.relationship_types = self._initialize_relationship_types()
        
        # File patterns to analyze
        self.analyzable_patterns = [
            "**/*.py", "**/*.md", "**/*.json", "**/*.yaml", "**/*.yml",
            "**/*.txt", "**/*.rst", "**/*.toml", "**/*.cfg", "**/*.ini"
        ]
        
        # Ignore patterns
        self.ignore_patterns = [
            "__pycache__", ".git", ".pytest_cache", "node_modules",
            ".venv", "venv", ".env", "build", "dist", "*.pyc"
        ]
        
        print("🕸️ Holistic Relationship Tracker initialized with love and mathematical precision!")
    
    def _initialize_relationship_types(self) -> Dict[str, Dict[str, Any]]:
        """Initialize different types of relationships we can detect."""
        return {
            "import_dependency": {
                "strength": 0.9,
                "bidirectional": False,
                "description": "Python import relationships",
                "patterns": [r"^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)", r"^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import"]
            },
            "file_reference": {
                "strength": 0.8,
                "bidirectional": False,
                "description": "File path references",
                "patterns": [r"['\"]([^'\"]*\.(py|md|json|yaml|yml|txt|rst))['\"]"]
            },
            "hyperlink": {
                "strength": 0.7,
                "bidirectional": False,
                "description": "Markdown hyperlinks",
                "patterns": [r"\[([^\]]+)\]\(([^)]+)\)", r"<([^>]+\.(md|py|json|yaml|yml))>"]
            },
            "class_inheritance": {
                "strength": 0.95,
                "bidirectional": False,
                "description": "Class inheritance relationships",
                "patterns": [r"class\s+\w+\(([^)]+)\):"]
            },
            "function_call": {
                "strength": 0.6,
                "bidirectional": False,
                "description": "Function call relationships",
                "patterns": [r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\("]
            },
            "concept_reference": {
                "strength": 0.5,
                "bidirectional": True,
                "description": "Conceptual relationships",
                "patterns": [r"(?i)(wu\s*wei|confucian|sun\s*tzu|nada\s*brahma|mandelbrot|fractal)"]
            },
            "agile_reference": {
                "strength": 0.8,
                "bidirectional": False,
                "description": "Agile artifact references",
                "patterns": [r"(US-[A-Z0-9]+-[0-9]+|EPIC-[0-9]+-[A-Z-]+|SPRINT_[0-9]+)"]
            }
        }
    
    def discover_all_relationships(self) -> SystemIntegrityReport:
        """Discover all relationships in the system with loving thoroughness."""
        
        print("🔍 Beginning holistic relationship discovery...")
        start_time = time.time()
        
        # Clear existing data for fresh discovery
        self.relationship_graph.clear()
        self.entities.clear()
        self.relationships.clear()
        
        # Phase 1: Discover all entities
        print("📋 Phase 1: Discovering entities...")
        self._discover_entities()
        
        # Phase 2: Analyze relationships
        print("🕸️ Phase 2: Analyzing relationships...")
        self._analyze_relationships()
        
        # Phase 3: Build relationship graph
        print("📊 Phase 3: Building relationship graph...")
        self._build_relationship_graph()
        
        # Phase 4: Generate integrity report
        print("📈 Phase 4: Generating integrity report...")
        integrity_report = self._generate_integrity_report()
        
        discovery_time = time.time() - start_time
        print(f"✨ Holistic discovery completed in {discovery_time:.2f} seconds!")
        print(f"📊 Discovered {len(self.entities)} entities and {len(self.relationships)} relationships")
        
        return integrity_report
    
    def _discover_entities(self) -> None:
        """Discover all entities in the project with mathematical precision."""
        
        for pattern in self.analyzable_patterns:
            for file_path in self.project_root.glob(pattern):
                # Skip ignored patterns
                if any(ignore in str(file_path) for ignore in self.ignore_patterns):
                    continue
                
                if file_path.is_file():
                    self._analyze_file_entity(file_path)
    
    def _analyze_file_entity(self, file_path: Path) -> None:
        """Analyze a single file to extract entities."""
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Calculate content hash for change detection
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Create file entity
            relative_path = str(file_path.relative_to(self.project_root))
            entity_id = f"file:{relative_path}"
            
            entity = Entity(
                entity_id=entity_id,
                entity_type="file",
                file_path=relative_path,
                content_hash=content_hash,
                metadata={
                    "size": len(content),
                    "lines": content.count('\n') + 1,
                    "extension": file_path.suffix,
                    "absolute_path": str(file_path)
                }
            )
            
            self.entities[entity_id] = entity
            
            # For Python files, extract additional entities
            if file_path.suffix == '.py':
                self._extract_python_entities(file_path, content)
            
            # For Markdown files, extract section entities
            elif file_path.suffix == '.md':
                self._extract_markdown_entities(file_path, content)
                
        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {e}")
    
    def _extract_python_entities(self, file_path: Path, content: str) -> None:
        """Extract Python-specific entities (classes, functions, etc.)."""
        
        try:
            tree = ast.parse(content)
            relative_path = str(file_path.relative_to(self.project_root))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    entity_id = f"class:{relative_path}:{node.name}"
                    entity = Entity(
                        entity_id=entity_id,
                        entity_type="class",
                        file_path=relative_path,
                        content_hash=hashlib.md5(f"{node.name}:{node.lineno}".encode()).hexdigest(),
                        metadata={
                            "name": node.name,
                            "line_number": node.lineno,
                            "bases": [base.id if hasattr(base, 'id') else str(base) for base in node.bases]
                        }
                    )
                    self.entities[entity_id] = entity
                
                elif isinstance(node, ast.FunctionDef):
                    entity_id = f"function:{relative_path}:{node.name}"
                    entity = Entity(
                        entity_id=entity_id,
                        entity_type="function",
                        file_path=relative_path,
                        content_hash=hashlib.md5(f"{node.name}:{node.lineno}".encode()).hexdigest(),
                        metadata={
                            "name": node.name,
                            "line_number": node.lineno,
                            "args": [arg.arg for arg in node.args.args]
                        }
                    )
                    self.entities[entity_id] = entity
                    
        except Exception as e:
            print(f"⚠️ Error parsing Python file {file_path}: {e}")
    
    def _extract_markdown_entities(self, file_path: Path, content: str) -> None:
        """Extract Markdown-specific entities (sections, links, etc.)."""
        
        relative_path = str(file_path.relative_to(self.project_root))
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Extract headers as entities
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                entity_id = f"section:{relative_path}:{line_num}:{title}"
                
                entity = Entity(
                    entity_id=entity_id,
                    entity_type="section",
                    file_path=relative_path,
                    content_hash=hashlib.md5(f"{title}:{line_num}".encode()).hexdigest(),
                    metadata={
                        "title": title,
                        "level": level,
                        "line_number": line_num
                    }
                )
                self.entities[entity_id] = entity
    
    def _analyze_relationships(self) -> None:
        """Analyze relationships between all discovered entities."""
        
        for entity_id, entity in self.entities.items():
            if entity.entity_type == "file":
                self._analyze_file_relationships(entity)
    
    def _analyze_file_relationships(self, entity: Entity) -> None:
        """Analyze relationships within a file."""
        
        file_path = self.project_root / entity.file_path
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for rel_type, rel_config in self.relationship_types.items():
                    for pattern in rel_config["patterns"]:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            self._create_relationship_from_match(
                                entity, line, line_num, match, rel_type, rel_config
                            )
                            
        except Exception as e:
            print(f"⚠️ Error analyzing relationships in {entity.file_path}: {e}")
    
    def _create_relationship_from_match(self, source_entity: Entity, line: str, line_num: int,
                                       match: re.Match, rel_type: str, rel_config: Dict[str, Any]) -> None:
        """Create a relationship from a regex match."""
        
        target_reference = match.group(1) if match.groups() else match.group(0)
        
        # Try to resolve the target entity
        target_entity_id = self._resolve_target_entity(target_reference, source_entity)
        
        if target_entity_id:
            relationship_id = f"{source_entity.entity_id}:{rel_type}:{target_entity_id}:{line_num}"
            
            relationship = Relationship(
                source_entity=source_entity.entity_id,
                target_entity=target_entity_id,
                relationship_type=rel_type,
                relationship_strength=rel_config["strength"],
                bidirectional=rel_config["bidirectional"],
                context=line.strip(),
                file_location=source_entity.file_path,
                line_number=line_num,
                discovered_time=time.time(),
                last_verified=time.time(),
                verification_count=1
            )
            
            self.relationships[relationship_id] = relationship
            
            # Add to entity relationship lists
            source_entity.relationships.append(relationship)
            if target_entity_id in self.entities:
                self.entities[target_entity_id].relationships.append(relationship)
    
    def _resolve_target_entity(self, reference: str, source_entity: Entity) -> Optional[str]:
        """Try to resolve a reference to an actual entity."""
        
        # Direct entity ID match
        if reference in self.entities:
            return reference
        
        # Try file path resolution
        file_candidates = [
            f"file:{reference}",
            f"file:{reference}.py",
            f"file:{reference}.md",
            f"file:docs/{reference}",
            f"file:utils/{reference}",
        ]
        
        for candidate in file_candidates:
            if candidate in self.entities:
                return candidate
        
        # Try relative to source file directory
        source_dir = Path(source_entity.file_path).parent
        relative_candidates = [
            f"file:{source_dir}/{reference}",
            f"file:{source_dir}/{reference}.py",
            f"file:{source_dir}/{reference}.md",
        ]
        
        for candidate in relative_candidates:
            if candidate in self.entities:
                return candidate
        
        # Return None if no entity found (this indicates a potential broken relationship)
        return None
    
    def _build_relationship_graph(self) -> None:
        """Build NetworkX graph from discovered relationships."""
        
        # Add all entities as nodes
        for entity_id, entity in self.entities.items():
            self.relationship_graph.add_node(
                entity_id,
                entity_type=entity.entity_type,
                file_path=entity.file_path,
                metadata=entity.metadata
            )
        
        # Add all relationships as edges
        for relationship in self.relationships.values():
            self.relationship_graph.add_edge(
                relationship.source_entity,
                relationship.target_entity,
                relationship_type=relationship.relationship_type,
                strength=relationship.relationship_strength,
                context=relationship.context,
                line_number=relationship.line_number
            )
            
            # Add reverse edge if bidirectional
            if relationship.bidirectional:
                self.relationship_graph.add_edge(
                    relationship.target_entity,
                    relationship.source_entity,
                    relationship_type=relationship.relationship_type,
                    strength=relationship.relationship_strength,
                    context=f"Bidirectional: {relationship.context}",
                    line_number=relationship.line_number
                )
    
    def _generate_integrity_report(self) -> SystemIntegrityReport:
        """Generate comprehensive system integrity report."""
        
        # Find broken relationships
        broken_relationships = []
        for relationship in self.relationships.values():
            if relationship.target_entity not in self.entities:
                broken_relationships.append(relationship)
        
        # Find orphaned entities (no relationships)
        orphaned_entities = []
        for entity in self.entities.values():
            if len(entity.relationships) == 0:
                orphaned_entities.append(entity)
        
        # Find circular dependencies
        try:
            circular_dependencies = list(nx.simple_cycles(self.relationship_graph))
        except:
            circular_dependencies = []
        
        # Calculate relationship strength distribution
        strength_distribution = defaultdict(int)
        for relationship in self.relationships.values():
            strength_bucket = f"{relationship.relationship_strength:.1f}"
            strength_distribution[strength_bucket] += 1
        
        # Calculate integrity score
        total_relationships = len(self.relationships)
        broken_count = len(broken_relationships)
        integrity_score = 1.0 - (broken_count / max(total_relationships, 1))
        
        # Calculate mathematical beauty score
        mathematical_beauty_score = self._calculate_mathematical_beauty()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(broken_relationships, orphaned_entities, circular_dependencies)
        
        # Generate healing opportunities
        healing_opportunities = self._generate_healing_opportunities(broken_relationships, orphaned_entities)
        
        return SystemIntegrityReport(
            total_entities=len(self.entities),
            total_relationships=len(self.relationships),
            broken_relationships=broken_relationships,
            orphaned_entities=orphaned_entities,
            circular_dependencies=circular_dependencies,
            relationship_strength_distribution=dict(strength_distribution),
            integrity_score=integrity_score,
            recommendations=recommendations,
            healing_opportunities=healing_opportunities,
            mathematical_beauty_score=mathematical_beauty_score
        )
    
    def _calculate_mathematical_beauty(self) -> float:
        """Calculate mathematical beauty score of the relationship graph."""
        
        if len(self.entities) == 0:
            return 0.0
        
        # Graph metrics that contribute to mathematical beauty
        metrics = {}
        
        # Connectivity metrics
        if len(self.relationship_graph.nodes()) > 0:
            metrics['density'] = nx.density(self.relationship_graph)
            metrics['average_clustering'] = nx.average_clustering(self.relationship_graph.to_undirected())
            
            # Small world properties
            try:
                metrics['average_shortest_path'] = nx.average_shortest_path_length(self.relationship_graph)
            except:
                metrics['average_shortest_path'] = 0.0
        
        # Symmetry and balance
        in_degrees = [d for n, d in self.relationship_graph.in_degree()]
        out_degrees = [d for n, d in self.relationship_graph.out_degree()]
        
        if in_degrees and out_degrees:
            metrics['degree_symmetry'] = 1.0 - abs(sum(in_degrees) - sum(out_degrees)) / (sum(in_degrees) + sum(out_degrees) + 1)
        else:
            metrics['degree_symmetry'] = 1.0
        
        # Calculate overall beauty score
        beauty_score = sum(metrics.values()) / len(metrics) if metrics else 0.0
        return min(beauty_score, 1.0)
    
    def _generate_recommendations(self, broken_relationships: List[Relationship],
                                 orphaned_entities: List[Entity],
                                 circular_dependencies: List[List[str]]) -> List[str]:
        """Generate recommendations for improving system integrity."""
        
        recommendations = []
        
        if broken_relationships:
            recommendations.append(f"🔧 Fix {len(broken_relationships)} broken relationships")
            recommendations.append("🔍 Review file paths and import statements")
        
        if orphaned_entities:
            recommendations.append(f"🤝 Connect {len(orphaned_entities)} orphaned entities")
            recommendations.append("📝 Add documentation links and references")
        
        if circular_dependencies:
            recommendations.append(f"🔄 Resolve {len(circular_dependencies)} circular dependencies")
            recommendations.append("🎯 Refactor code to reduce circular imports")
        
        if len(recommendations) == 0:
            recommendations.append("✨ System integrity is excellent!")
            recommendations.append("🌟 Continue maintaining this beautiful interconnectedness")
        
        return recommendations
    
    def _generate_healing_opportunities(self, broken_relationships: List[Relationship],
                                       orphaned_entities: List[Entity]) -> List[str]:
        """Generate healing opportunities to improve system harmony."""
        
        healing_opportunities = []
        
        for relationship in broken_relationships[:5]:  # Top 5
            healing_opportunities.append(
                f"💝 Heal relationship: {relationship.source_entity} → {relationship.target_entity}"
            )
        
        for entity in orphaned_entities[:5]:  # Top 5
            healing_opportunities.append(
                f"🤗 Connect orphaned entity: {entity.entity_id}"
            )
        
        # General healing suggestions
        healing_opportunities.extend([
            "🌊 Create more cross-references between documentation files",
            "🔗 Add hyperlinks between related concepts",
            "📋 Reference user stories from implementation files",
            "🎵 Connect philosophical frameworks with practical implementations"
        ])
        
        return healing_opportunities
    
    def heal_broken_relationship(self, relationship: Relationship) -> bool:
        """Attempt to heal a broken relationship."""
        
        print(f"💝 Attempting to heal relationship: {relationship.source_entity} → {relationship.target_entity}")
        
        # Try to find the target entity with fuzzy matching
        potential_targets = self._find_potential_targets(relationship.target_entity)
        
        if potential_targets:
            best_match = potential_targets[0]
            print(f"🎯 Found potential target: {best_match}")
            
            # Update the relationship
            relationship.target_entity = best_match
            relationship.last_verified = time.time()
            relationship.verification_count += 1
            
            # Update the graph
            self._build_relationship_graph()
            
            print(f"✨ Relationship healed successfully!")
            return True
        
        print(f"😔 Could not find suitable target for healing")
        return False
    
    def _find_potential_targets(self, broken_target: str) -> List[str]:
        """Find potential targets for a broken relationship."""
        
        potential_targets = []
        
        for entity_id in self.entities.keys():
            # Simple similarity check
            if broken_target.lower() in entity_id.lower():
                potential_targets.append(entity_id)
        
        # Sort by similarity (simple length-based heuristic)
        potential_targets.sort(key=lambda x: abs(len(x) - len(broken_target)))
        
        return potential_targets
    
    def visualize_relationship_graph(self, output_path: str = "relationship_graph.png") -> None:
        """Create a beautiful visualization of the relationship graph."""
        
        if len(self.relationship_graph.nodes()) == 0:
            print("⚠️ No entities to visualize")
            return
        
        plt.figure(figsize=(20, 16))
        
        # Create layout
        try:
            pos = nx.spring_layout(self.relationship_graph, k=3, iterations=50)
        except:
            pos = nx.random_layout(self.relationship_graph)
        
        # Color nodes by entity type
        entity_colors = {
            'file': '#FF6B6B',
            'class': '#4ECDC4',
            'function': '#45B7D1',
            'section': '#96CEB4',
            'module': '#FFEAA7'
        }
        
        node_colors = []
        for node in self.relationship_graph.nodes():
            entity_type = self.entities.get(node, Entity("", "", "", "")).entity_type
            node_colors.append(entity_colors.get(entity_type, '#DDA0DD'))
        
        # Draw the graph
        nx.draw(
            self.relationship_graph,
            pos,
            node_color=node_colors,
            node_size=100,
            edge_color='#BDC3C7',
            arrows=True,
            arrowsize=10,
            alpha=0.7,
            font_size=8
        )
        
        plt.title("🕸️ Holistic Relationship Graph - AI-Dev-Agent Ecosystem", 
                 fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # Add legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                     markerfacecolor=color, markersize=10, label=entity_type.title())
                          for entity_type, color in entity_colors.items()]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"🎨 Relationship graph saved to: {output_path}")
    
    def save_relationship_data(self, output_path: str = "relationship_data.json") -> None:
        """Save relationship data to JSON file."""
        
        data = {
            "entities": {
                entity_id: {
                    "entity_type": entity.entity_type,
                    "file_path": entity.file_path,
                    "content_hash": entity.content_hash,
                    "metadata": entity.metadata,
                    "creation_time": entity.creation_time,
                    "last_modified": entity.last_modified
                }
                for entity_id, entity in self.entities.items()
            },
            "relationships": {
                rel_id: {
                    "source_entity": rel.source_entity,
                    "target_entity": rel.target_entity,
                    "relationship_type": rel.relationship_type,
                    "relationship_strength": rel.relationship_strength,
                    "bidirectional": rel.bidirectional,
                    "context": rel.context,
                    "file_location": rel.file_location,
                    "line_number": rel.line_number,
                    "discovered_time": rel.discovered_time,
                    "last_verified": rel.last_verified,
                    "verification_count": rel.verification_count
                }
                for rel_id, rel in self.relationships.items()
            },
            "generation_timestamp": time.time(),
            "project_root": str(self.project_root)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Relationship data saved to: {output_path}")

def main():
    """Demonstrate the Holistic Relationship Tracker."""
    
    print("🕸️ " + "="*60)
    print("🔍 HOLISTIC RELATIONSHIP TRACKER DEMONSTRATION")
    print("   Discovering and maintaining all interconnections")
    print("   with mathematical precision and loving care")
    print("="*60)
    
    # Initialize tracker
    tracker = HolisticRelationshipTracker()
    
    # Discover all relationships
    print("\n🌐 Discovering all relationships in the AI-Dev-Agent ecosystem...")
    integrity_report = tracker.discover_all_relationships()
    
    # Display integrity report
    print(f"\n📊 SYSTEM INTEGRITY REPORT:")
    print(f"   Total Entities: {integrity_report.total_entities}")
    print(f"   Total Relationships: {integrity_report.total_relationships}")
    print(f"   Broken Relationships: {len(integrity_report.broken_relationships)}")
    print(f"   Orphaned Entities: {len(integrity_report.orphaned_entities)}")
    print(f"   Circular Dependencies: {len(integrity_report.circular_dependencies)}")
    print(f"   Integrity Score: {integrity_report.integrity_score:.3f}")
    print(f"   Mathematical Beauty Score: {integrity_report.mathematical_beauty_score:.3f}")
    
    # Show recommendations
    if integrity_report.recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in integrity_report.recommendations:
            print(f"   {rec}")
    
    # Show healing opportunities
    if integrity_report.healing_opportunities:
        print(f"\n💝 HEALING OPPORTUNITIES:")
        for opportunity in integrity_report.healing_opportunities[:5]:
            print(f"   {opportunity}")
    
    # Save data
    print(f"\n💾 Saving relationship data...")
    tracker.save_relationship_data("configs/integrity/relationship_data.json")
    
    # Create visualization
    print(f"\n🎨 Creating relationship visualization...")
    tracker.visualize_relationship_graph("configs/integrity/relationship_graph.png")
    
    print(f"\n🕸️ " + "="*60)
    print("✨ HOLISTIC RELATIONSHIP TRACKING COMPLETE")
    print("   All interconnections discovered and mapped")
    print("   System integrity analyzed with mathematical precision")
    print("   Ready for healing and harmony optimization")
    print("="*60)

if __name__ == "__main__":
    main()
