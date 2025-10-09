#!/usr/bin/env python3
"""
Software Catalog RAG Tools for MCP
==================================

Comprehensive software catalog system integrated with RAG for anti-duplication,
agent swarm intelligence, and Cursor rule system enhancement.

Author: AI Development Agent
Created: 2025-01-02
Purpose: Build intelligent software catalog for RAG-powered systems
"""

import asyncio
import logging
import ast
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from datetime import datetime
import re
import hashlib

# RAG system imports
try:
    from context.context_engine import ContextEngine
    from models.config import ContextConfig
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# MCP integration imports
from utils.mcp.server import MCPServer
from utils.system.universal_agent_tracker import UniversalAgentTracker

logger = logging.getLogger(__name__)

class SoftwareCatalogEntry:
    """Represents a cataloged software component."""
    
    def __init__(self, file_path: str, component_type: str, name: str, 
                 description: str, capabilities: List[str], dependencies: List[str],
                 interfaces: List[str], metadata: Dict[str, Any]):
        self.file_path = file_path
        self.component_type = component_type  # agent, utility, mcp_tool, rule, etc.
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.dependencies = dependencies
        self.interfaces = interfaces
        self.metadata = metadata
        self.catalog_id = self._generate_catalog_id()
        self.last_updated = datetime.now()
    
    def _generate_catalog_id(self) -> str:
        """Generate unique catalog ID for this component."""
        content = f"{self.file_path}:{self.component_type}:{self.name}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage and retrieval."""
        return {
            "catalog_id": self.catalog_id,
            "file_path": self.file_path,
            "component_type": self.component_type,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "interfaces": self.interfaces,
            "metadata": self.metadata,
            "last_updated": self.last_updated.isoformat()
        }

class SoftwareCatalogRAGTools:
    """
    RAG-powered software catalog tools for comprehensive project analysis.
    
    Provides intelligent cataloging, search, and analysis capabilities for:
    - Anti-duplication enforcement
    - Agent swarm context
    - Cursor rule system intelligence
    """
    
    def __init__(self):
        """Initialize software catalog RAG tools."""
        self.context_engine = None
        self.agent_tracker = UniversalAgentTracker()
        self.catalog_entries: Dict[str, SoftwareCatalogEntry] = {}
        self.tool_usage_stats = {}
        self.project_root = Path(".")
        
        # Initialize RAG system if available
        if RAG_AVAILABLE:
            try:
                # Create context configuration for software cataloging
                context_config = ContextConfig(
                    enable_codebase_indexing=True,
                    index_file_extensions=[".py", ".js", ".ts", ".md", ".mdc", ".yaml", ".yml", ".json"],
                    exclude_patterns=["__pycache__", "node_modules", ".git", "venv", "env", "generated_projects"],
                    max_context_size=20000,  # Large context for comprehensive analysis
                    max_file_size=5 * 1024 * 1024  # 5MB files
                )
                
                self.context_engine = ContextEngine(context_config)
                logger.info("✅ Software Catalog RAG Context Engine initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Software Catalog RAG Context Engine: {e}")
                self.context_engine = None
        else:
            logger.warning("⚠️ RAG system not available - software catalog will have limited functionality")
    
    async def build_comprehensive_catalog(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        Build comprehensive software catalog of the entire project.
        
        Args:
            force_rebuild: Whether to rebuild catalog from scratch
            
        Returns:
            Catalog build results and statistics
        """
        try:
            self._track_tool_usage("build_comprehensive_catalog")
            
            if not force_rebuild and self.catalog_entries:
                logger.info("Using existing catalog. Use force_rebuild=True to rebuild.")
                return await self._get_catalog_summary()
            
            logger.info("🏗️ Building comprehensive software catalog...")
            
            # Clear existing catalog if rebuilding
            if force_rebuild:
                self.catalog_entries.clear()
            
            # Catalog different component types
            catalog_stats = {
                "agents": await self._catalog_agents(),
                "utilities": await self._catalog_utilities(),
                "mcp_tools": await self._catalog_mcp_tools(),
                "cursor_rules": await self._catalog_cursor_rules(),
                "scripts": await self._catalog_scripts(),
                "tests": await self._catalog_tests(),
                "documentation": await self._catalog_documentation(),
                "workflows": await self._catalog_workflows()
            }
            
            # Build relationships and dependencies
            await self._build_component_relationships()
            
            # Create RAG embeddings for semantic search
            await self._create_catalog_embeddings()
            
            # Index the codebase for semantic search
            if self.context_engine:
                try:
                    await self.context_engine.index_codebase(str(self.project_root))
                    logger.info("✅ Codebase indexed for semantic search")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to index codebase: {e}")
            
            # Generate catalog summary
            summary = await self._generate_catalog_summary(catalog_stats)
            
            logger.info(f"✅ Software catalog built: {len(self.catalog_entries)} components cataloged")
            
            return {
                "success": True,
                "total_components": len(self.catalog_entries),
                "catalog_stats": catalog_stats,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Software catalog build failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def search_catalog_semantic(self, query: str, component_types: List[str] = None, 
                                    limit: int = 10) -> Dict[str, Any]:
        """
        Perform semantic search across the software catalog.
        
        Args:
            query: Search query describing desired functionality
            component_types: Filter by component types (agent, utility, mcp_tool, etc.)
            limit: Maximum number of results
            
        Returns:
            Semantic search results with relevance scores
        """
        try:
            self._track_tool_usage("search_catalog_semantic")
            
            # Use RAG system for semantic search if available
            if self.context_engine:
                search_results = self.context_engine.search_context(
                    query=query,
                    max_results=limit * 2  # Get more results for filtering
                )
            else:
                search_results = []
            
            # Filter and enhance results with catalog information
            enhanced_results = []
            for result in search_results:
                file_path = result.get("file_path", "")
                
                # Find matching catalog entries
                matching_entries = [
                    entry for entry in self.catalog_entries.values()
                    if entry.file_path in file_path or file_path in entry.file_path
                ]
                
                for entry in matching_entries:
                    # Apply component type filter
                    if component_types and entry.component_type not in component_types:
                        continue
                    
                    enhanced_result = {
                        "catalog_id": entry.catalog_id,
                        "component_type": entry.component_type,
                        "name": entry.name,
                        "description": entry.description,
                        "capabilities": entry.capabilities,
                        "file_path": entry.file_path,
                        "relevance_score": result.get("score", 0.0),
                        "content_snippet": result.get("content", "")[:300],
                        "interfaces": entry.interfaces,
                        "dependencies": entry.dependencies
                    }
                    enhanced_results.append(enhanced_result)
            
            # Sort by relevance and limit results
            enhanced_results.sort(key=lambda x: x["relevance_score"], reverse=True)
            enhanced_results = enhanced_results[:limit]
            
            return {
                "success": True,
                "query": query,
                "component_types_filter": component_types,
                "results": enhanced_results,
                "total_found": len(enhanced_results),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Catalog semantic search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    async def find_similar_components(self, component_description: str, 
                                    exclude_types: List[str] = None) -> Dict[str, Any]:
        """
        Find components similar to a described functionality.
        
        Args:
            component_description: Description of desired component
            exclude_types: Component types to exclude from search
            
        Returns:
            Similar components with similarity scores
        """
        try:
            self._track_tool_usage("find_similar_components")
            
            # Perform semantic search
            search_results = await self.search_catalog_semantic(
                query=component_description,
                limit=20
            )
            
            if not search_results["success"]:
                return search_results
            
            # Filter out excluded types
            filtered_results = []
            for result in search_results["results"]:
                if exclude_types and result["component_type"] in exclude_types:
                    continue
                filtered_results.append(result)
            
            # Analyze similarity and suggest integration approaches
            similarity_analysis = []
            for result in filtered_results:
                analysis = {
                    "component": result,
                    "similarity_score": result["relevance_score"],
                    "integration_potential": await self._assess_integration_potential(
                        component_description, result
                    ),
                    "extension_points": await self._identify_extension_points(result),
                    "integration_effort": self._estimate_integration_effort(result)
                }
                similarity_analysis.append(analysis)
            
            return {
                "success": True,
                "component_description": component_description,
                "similar_components": similarity_analysis,
                "recommendations": await self._generate_similarity_recommendations(similarity_analysis),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Similar components search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "component_description": component_description,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_component_dependencies(self, component_id: str) -> Dict[str, Any]:
        """
        Get comprehensive dependency information for a component.
        
        Args:
            component_id: Catalog ID of the component
            
        Returns:
            Dependency analysis and relationship map
        """
        try:
            self._track_tool_usage("get_component_dependencies")
            
            if component_id not in self.catalog_entries:
                return {
                    "success": False,
                    "error": f"Component {component_id} not found in catalog",
                    "component_id": component_id
                }
            
            component = self.catalog_entries[component_id]
            
            # Analyze dependencies
            dependency_analysis = {
                "direct_dependencies": component.dependencies,
                "dependents": await self._find_dependents(component),
                "transitive_dependencies": await self._find_transitive_dependencies(component),
                "circular_dependencies": await self._detect_circular_dependencies(component),
                "dependency_graph": await self._build_dependency_graph(component)
            }
            
            return {
                "success": True,
                "component_id": component_id,
                "component_name": component.name,
                "component_type": component.component_type,
                "dependency_analysis": dependency_analysis,
                "integration_impact": await self._assess_integration_impact(component),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Component dependency analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "component_id": component_id,
                "timestamp": datetime.now().isoformat()
            }
    
    # Private helper methods for cataloging different component types
    
    async def _catalog_agents(self) -> Dict[str, Any]:
        """Catalog all agent components."""
        agents_found = 0
        agents_path = self.project_root / "agents"
        
        if not agents_path.exists():
            return {"count": 0, "types": []}
        
        agent_types = set()
        
        for agent_file in agents_path.rglob("*.py"):
            if agent_file.name.startswith("__"):
                continue
            
            try:
                # Analyze agent file
                agent_info = await self._analyze_python_file(agent_file, "agent")
                if agent_info:
                    entry = SoftwareCatalogEntry(
                        file_path=str(agent_file.relative_to(self.project_root)),
                        component_type="agent",
                        name=agent_info["name"],
                        description=agent_info["description"],
                        capabilities=agent_info["capabilities"],
                        dependencies=agent_info["dependencies"],
                        interfaces=agent_info["interfaces"],
                        metadata=agent_info["metadata"]
                    )
                    self.catalog_entries[entry.catalog_id] = entry
                    agents_found += 1
                    agent_types.add(agent_info["metadata"].get("agent_type", "general"))
                    
            except Exception as e:
                logger.warning(f"Failed to catalog agent {agent_file}: {e}")
        
        return {"count": agents_found, "types": list(agent_types)}
    
    async def _catalog_utilities(self) -> Dict[str, Any]:
        """Catalog all utility components."""
        utilities_found = 0
        utils_path = self.project_root / "utils"
        
        if not utils_path.exists():
            return {"count": 0, "categories": []}
        
        utility_categories = set()
        
        for util_file in utils_path.rglob("*.py"):
            if util_file.name.startswith("__"):
                continue
            
            try:
                # Analyze utility file
                util_info = await self._analyze_python_file(util_file, "utility")
                if util_info:
                    entry = SoftwareCatalogEntry(
                        file_path=str(util_file.relative_to(self.project_root)),
                        component_type="utility",
                        name=util_info["name"],
                        description=util_info["description"],
                        capabilities=util_info["capabilities"],
                        dependencies=util_info["dependencies"],
                        interfaces=util_info["interfaces"],
                        metadata=util_info["metadata"]
                    )
                    self.catalog_entries[entry.catalog_id] = entry
                    utilities_found += 1
                    
                    # Determine category from path
                    category = util_file.parent.name if util_file.parent != utils_path else "core"
                    utility_categories.add(category)
                    
            except Exception as e:
                logger.warning(f"Failed to catalog utility {util_file}: {e}")
        
        return {"count": utilities_found, "categories": list(utility_categories)}
    
    async def _catalog_mcp_tools(self) -> Dict[str, Any]:
        """Catalog all MCP tools."""
        mcp_tools_found = 0
        mcp_path = self.project_root / "utils" / "mcp" / "tools"
        
        if not mcp_path.exists():
            return {"count": 0, "tool_types": []}
        
        tool_types = set()
        
        for tool_file in mcp_path.rglob("*.py"):
            if tool_file.name.startswith("__"):
                continue
            
            try:
                # Analyze MCP tool file
                tool_info = await self._analyze_python_file(tool_file, "mcp_tool")
                if tool_info:
                    entry = SoftwareCatalogEntry(
                        file_path=str(tool_file.relative_to(self.project_root)),
                        component_type="mcp_tool",
                        name=tool_info["name"],
                        description=tool_info["description"],
                        capabilities=tool_info["capabilities"],
                        dependencies=tool_info["dependencies"],
                        interfaces=tool_info["interfaces"],
                        metadata=tool_info["metadata"]
                    )
                    self.catalog_entries[entry.catalog_id] = entry
                    mcp_tools_found += 1
                    tool_types.add(tool_info["metadata"].get("tool_category", "general"))
                    
            except Exception as e:
                logger.warning(f"Failed to catalog MCP tool {tool_file}: {e}")
        
        return {"count": mcp_tools_found, "tool_types": list(tool_types)}
    
    async def _catalog_cursor_rules(self) -> Dict[str, Any]:
        """Catalog all Cursor rules."""
        rules_found = 0
        rules_path = self.project_root / ".cursor" / "rules"
        
        if not rules_path.exists():
            return {"count": 0, "categories": []}
        
        rule_categories = set()
        
        for rule_file in rules_path.rglob("*.mdc"):
            try:
                # Analyze Cursor rule file
                rule_info = await self._analyze_cursor_rule(rule_file)
                if rule_info:
                    entry = SoftwareCatalogEntry(
                        file_path=str(rule_file.relative_to(self.project_root)),
                        component_type="cursor_rule",
                        name=rule_info["name"],
                        description=rule_info["description"],
                        capabilities=rule_info["capabilities"],
                        dependencies=rule_info["dependencies"],
                        interfaces=rule_info["interfaces"],
                        metadata=rule_info["metadata"]
                    )
                    self.catalog_entries[entry.catalog_id] = entry
                    rules_found += 1
                    rule_categories.add(rule_info["metadata"].get("category", "general"))
                    
            except Exception as e:
                logger.warning(f"Failed to catalog rule {rule_file}: {e}")
        
        return {"count": rules_found, "categories": list(rule_categories)}
    
    def _track_tool_usage(self, tool_name: str):
        """Track usage statistics for catalog tools."""
        if tool_name not in self.tool_usage_stats:
            self.tool_usage_stats[tool_name] = {"count": 0, "last_used": None}
        
        self.tool_usage_stats[tool_name]["count"] += 1
        self.tool_usage_stats[tool_name]["last_used"] = datetime.now().isoformat()

    async def _analyze_python_file(self, file_path: Path, component_type: str) -> Optional[Dict[str, Any]]:
        """Analyze a Python file to extract component information."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Parse AST for detailed analysis
            tree = ast.parse(content)
            
            # Extract basic information
            name = file_path.stem
            description = self._extract_docstring(tree) or f"{component_type.title()} component"
            
            # Extract capabilities from class methods and functions
            capabilities = []
            dependencies = []
            interfaces = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    capabilities.extend([f"class:{node.name}"])
                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            capabilities.append(f"method:{item.name}")
                
                elif isinstance(node, ast.FunctionDef):
                    capabilities.append(f"function:{node.name}")
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)
            
            # Extract interfaces (public methods/functions)
            interfaces = [cap for cap in capabilities if not cap.split(':')[-1].startswith('_')]
            
            metadata = {
                "file_size": file_path.stat().st_size,
                "lines_of_code": len(content.splitlines()),
                "component_category": self._determine_component_category(file_path, content),
                "complexity_score": self._calculate_complexity_score(tree)
            }
            
            return {
                "name": name,
                "description": description,
                "capabilities": capabilities,
                "dependencies": dependencies,
                "interfaces": interfaces,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.warning(f"Failed to analyze Python file {file_path}: {e}")
            return None
    
    async def _analyze_cursor_rule(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a Cursor rule file to extract rule information."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract rule name from filename or content
            name = file_path.stem.replace('_', ' ').title()
            
            # Extract description from first heading or comment
            description = "Cursor development rule"
            lines = content.splitlines()
            for line in lines[:10]:  # Check first 10 lines
                if line.startswith('#') and len(line.strip()) > 2:
                    description = line.strip('#').strip()
                    break
            
            # Extract capabilities from rule content
            capabilities = []
            if "CRITICAL" in content.upper():
                capabilities.append("critical_rule")
            if "MANDATORY" in content.upper():
                capabilities.append("mandatory_enforcement")
            if "REQUIRED" in content.upper():
                capabilities.append("required_behavior")
            
            # Extract rule category from path
            category = "general"
            if "core" in str(file_path):
                category = "core"
            elif "context" in str(file_path):
                category = "context"
            elif "tools" in str(file_path):
                category = "tools"
            
            metadata = {
                "file_size": file_path.stat().st_size,
                "category": category,
                "rule_type": "cursor_rule",
                "enforcement_level": self._determine_enforcement_level(content)
            }
            
            return {
                "name": name,
                "description": description,
                "capabilities": capabilities,
                "dependencies": [],
                "interfaces": capabilities,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.warning(f"Failed to analyze Cursor rule {file_path}: {e}")
            return None
    
    def _extract_docstring(self, tree: ast.AST) -> Optional[str]:
        """Extract docstring from AST."""
        if isinstance(tree, ast.Module) and tree.body:
            first = tree.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                if isinstance(first.value.value, str):
                    return first.value.value.strip()
        return None
    
    def _determine_component_category(self, file_path: Path, content: str) -> str:
        """Determine component category from path and content."""
        path_str = str(file_path).lower()
        
        if "agent" in path_str:
            return "agent"
        elif "mcp" in path_str and "tool" in path_str:
            return "mcp_tool"
        elif "util" in path_str:
            return "utility"
        elif "test" in path_str:
            return "test"
        elif "script" in path_str:
            return "script"
        else:
            return "general"
    
    def _calculate_complexity_score(self, tree: ast.AST) -> float:
        """Calculate complexity score for code."""
        complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                complexity += 0.5
            elif isinstance(node, ast.ClassDef):
                complexity += 1
        
        return complexity
    
    def _determine_enforcement_level(self, content: str) -> str:
        """Determine enforcement level from rule content."""
        content_upper = content.upper()
        
        if "CRITICAL" in content_upper or "MANDATORY" in content_upper:
            return "critical"
        elif "REQUIRED" in content_upper or "MUST" in content_upper:
            return "high"
        elif "SHOULD" in content_upper:
            return "medium"
        else:
            return "low"
    
    async def _catalog_scripts(self) -> Dict[str, Any]:
        """Catalog all script components."""
        scripts_found = 0
        scripts_path = self.project_root / "scripts"
        
        if not scripts_path.exists():
            return {"count": 0, "types": []}
        
        script_types = set()
        
        for script_file in scripts_path.rglob("*.py"):
            if script_file.name.startswith("__"):
                continue
            
            try:
                script_info = await self._analyze_python_file(script_file, "script")
                if script_info:
                    entry = SoftwareCatalogEntry(
                        file_path=str(script_file.relative_to(self.project_root)),
                        component_type="script",
                        name=script_info["name"],
                        description=script_info["description"],
                        capabilities=script_info["capabilities"],
                        dependencies=script_info["dependencies"],
                        interfaces=script_info["interfaces"],
                        metadata=script_info["metadata"]
                    )
                    self.catalog_entries[entry.catalog_id] = entry
                    scripts_found += 1
                    script_types.add(script_info["metadata"].get("component_category", "general"))
                    
            except Exception as e:
                logger.warning(f"Failed to catalog script {script_file}: {e}")
        
        return {"count": scripts_found, "types": list(script_types)}
    
    async def _catalog_tests(self) -> Dict[str, Any]:
        """Catalog all test components."""
        tests_found = 0
        tests_path = self.project_root / "tests"
        
        if not tests_path.exists():
            return {"count": 0, "categories": []}
        
        test_categories = set()
        
        for test_file in tests_path.rglob("*.py"):
            if test_file.name.startswith("__"):
                continue
            
            try:
                test_info = await self._analyze_python_file(test_file, "test")
                if test_info:
                    entry = SoftwareCatalogEntry(
                        file_path=str(test_file.relative_to(self.project_root)),
                        component_type="test",
                        name=test_info["name"],
                        description=test_info["description"],
                        capabilities=test_info["capabilities"],
                        dependencies=test_info["dependencies"],
                        interfaces=test_info["interfaces"],
                        metadata=test_info["metadata"]
                    )
                    self.catalog_entries[entry.catalog_id] = entry
                    tests_found += 1
                    
                    # Determine category from path
                    category = test_file.parent.name if test_file.parent != tests_path else "unit"
                    test_categories.add(category)
                    
            except Exception as e:
                logger.warning(f"Failed to catalog test {test_file}: {e}")
        
        return {"count": tests_found, "categories": list(test_categories)}
    
    async def _catalog_documentation(self) -> Dict[str, Any]:
        """Catalog all documentation components."""
        docs_found = 0
        docs_path = self.project_root / "docs"
        
        if not docs_path.exists():
            return {"count": 0, "types": []}
        
        doc_types = set()
        
        for doc_file in docs_path.rglob("*.md"):
            try:
                content = doc_file.read_text(encoding='utf-8')
                
                # Extract basic information
                name = doc_file.stem.replace('_', ' ').title()
                description = f"Documentation: {name}"
                
                # Extract first heading as description
                lines = content.splitlines()
                for line in lines[:5]:
                    if line.startswith('#'):
                        description = line.strip('#').strip()
                        break
                
                capabilities = ["documentation"]
                if "agile" in str(doc_file):
                    capabilities.append("agile_artifact")
                if "architecture" in str(doc_file):
                    capabilities.append("architecture_doc")
                
                metadata = {
                    "file_size": doc_file.stat().st_size,
                    "doc_type": self._determine_doc_type(doc_file),
                    "word_count": len(content.split())
                }
                
                entry = SoftwareCatalogEntry(
                    file_path=str(doc_file.relative_to(self.project_root)),
                    component_type="documentation",
                    name=name,
                    description=description,
                    capabilities=capabilities,
                    dependencies=[],
                    interfaces=capabilities,
                    metadata=metadata
                )
                self.catalog_entries[entry.catalog_id] = entry
                docs_found += 1
                doc_types.add(metadata["doc_type"])
                
            except Exception as e:
                logger.warning(f"Failed to catalog documentation {doc_file}: {e}")
        
        return {"count": docs_found, "types": list(doc_types)}
    
    async def _catalog_workflows(self) -> Dict[str, Any]:
        """Catalog all workflow components."""
        workflows_found = 0
        workflow_paths = [
            self.project_root / "workflow",
            self.project_root / ".github" / "workflows"
        ]
        
        workflow_types = set()
        
        for workflow_path in workflow_paths:
            if not workflow_path.exists():
                continue
            
            for workflow_file in workflow_path.rglob("*.yml"):
                try:
                    content = workflow_file.read_text(encoding='utf-8')
                    
                    name = workflow_file.stem.replace('_', ' ').title()
                    description = f"Workflow: {name}"
                    
                    capabilities = ["workflow"]
                    if "github" in str(workflow_file):
                        capabilities.append("github_action")
                    
                    metadata = {
                        "file_size": workflow_file.stat().st_size,
                        "workflow_type": "github_action" if "github" in str(workflow_file) else "general"
                    }
                    
                    entry = SoftwareCatalogEntry(
                        file_path=str(workflow_file.relative_to(self.project_root)),
                        component_type="workflow",
                        name=name,
                        description=description,
                        capabilities=capabilities,
                        dependencies=[],
                        interfaces=capabilities,
                        metadata=metadata
                    )
                    self.catalog_entries[entry.catalog_id] = entry
                    workflows_found += 1
                    workflow_types.add(metadata["workflow_type"])
                    
                except Exception as e:
                    logger.warning(f"Failed to catalog workflow {workflow_file}: {e}")
        
        return {"count": workflows_found, "types": list(workflow_types)}
    
    def _determine_doc_type(self, doc_file: Path) -> str:
        """Determine documentation type from path."""
        path_str = str(doc_file).lower()
        
        if "agile" in path_str:
            return "agile"
        elif "architecture" in path_str:
            return "architecture"
        elif "api" in path_str:
            return "api"
        elif "user" in path_str or "guide" in path_str:
            return "user_guide"
        elif "readme" in path_str:
            return "readme"
        else:
            return "general"
    
    # Placeholder methods for advanced functionality
    async def _build_component_relationships(self):
        """Build relationships between components."""
        # TODO: Implement dependency graph construction
        pass
    
    async def _create_catalog_embeddings(self):
        """Create RAG embeddings for catalog entries."""
        if not self.context_engine:
            return
        
        # TODO: Create embeddings for each catalog entry
        pass
    
    async def _generate_catalog_summary(self, catalog_stats: Dict) -> str:
        """Generate human-readable catalog summary."""
        total_components = sum(stats.get("count", 0) for stats in catalog_stats.values())
        
        summary_parts = [
            f"Software Catalog Summary: {total_components} components discovered",
            f"- Agents: {catalog_stats.get('agents', {}).get('count', 0)}",
            f"- Utilities: {catalog_stats.get('utilities', {}).get('count', 0)}",
            f"- MCP Tools: {catalog_stats.get('mcp_tools', {}).get('count', 0)}",
            f"- Cursor Rules: {catalog_stats.get('cursor_rules', {}).get('count', 0)}",
            f"- Scripts: {catalog_stats.get('scripts', {}).get('count', 0)}",
            f"- Tests: {catalog_stats.get('tests', {}).get('count', 0)}",
            f"- Documentation: {catalog_stats.get('documentation', {}).get('count', 0)}",
            f"- Workflows: {catalog_stats.get('workflows', {}).get('count', 0)}"
        ]
        
        return "\n".join(summary_parts)
    
    async def _get_catalog_summary(self) -> Dict[str, Any]:
        """Get summary of existing catalog."""
        component_counts = {}
        for entry in self.catalog_entries.values():
            component_type = entry.component_type
            if component_type not in component_counts:
                component_counts[component_type] = 0
            component_counts[component_type] += 1
        
        return {
            "success": True,
            "total_components": len(self.catalog_entries),
            "component_counts": component_counts,
            "summary": await self._generate_catalog_summary({"total": {"count": len(self.catalog_entries)}}),
            "timestamp": datetime.now().isoformat()
        }
    
    # Placeholder methods for similarity analysis
    async def _assess_integration_potential(self, description: str, component: Dict) -> str:
        """Assess integration potential between description and component."""
        return "high"  # Placeholder
    
    async def _identify_extension_points(self, component: Dict) -> List[str]:
        """Identify extension points in a component."""
        return ["method_override", "interface_implementation"]  # Placeholder
    
    def _estimate_integration_effort(self, component: Dict) -> str:
        """Estimate effort required for integration."""
        return "medium"  # Placeholder
    
    async def _generate_similarity_recommendations(self, analysis: List[Dict]) -> List[str]:
        """Generate recommendations based on similarity analysis."""
        return ["Consider extending existing component", "Evaluate integration opportunities"]
    
    # Placeholder methods for dependency analysis
    async def _find_dependents(self, component: SoftwareCatalogEntry) -> List[str]:
        """Find components that depend on this component."""
        return []  # Placeholder
    
    async def _find_transitive_dependencies(self, component: SoftwareCatalogEntry) -> List[str]:
        """Find transitive dependencies."""
        return []  # Placeholder
    
    async def _detect_circular_dependencies(self, component: SoftwareCatalogEntry) -> List[str]:
        """Detect circular dependencies."""
        return []  # Placeholder
    
    async def _build_dependency_graph(self, component: SoftwareCatalogEntry) -> Dict:
        """Build dependency graph for component."""
        return {"nodes": [], "edges": []}  # Placeholder
    
    async def _assess_integration_impact(self, component: SoftwareCatalogEntry) -> Dict:
        """Assess impact of integrating with this component."""
        return {"risk_level": "low", "effort": "medium"}  # Placeholder


def get_software_catalog_rag_tools() -> SoftwareCatalogRAGTools:
    """Get software catalog RAG tools instance."""
    return SoftwareCatalogRAGTools()
