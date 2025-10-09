#!/usr/bin/env python3
"""
Anti-Duplication RAG Tools for MCP
==================================

RAG-powered tools to prevent duplicate functionality creation by discovering
existing systems and suggesting integration approaches.

Author: AI Development Agent
Created: 2025-01-02
Purpose: Solve the duplicate functionality problem systematically
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import re
import ast

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

class AntiDuplicationRAGTools:
    """
    RAG-powered tools to prevent duplicate functionality creation.
    
    Core principle: Always discover existing functionality before building new.
    """
    
    def __init__(self):
        """Initialize anti-duplication RAG tools."""
        self.context_engine = None
        self.agent_tracker = UniversalAgentTracker()
        self.tool_usage_stats = {}
        
        # Initialize RAG system if available
        if RAG_AVAILABLE:
            try:
                # Create context configuration for anti-duplication
                context_config = ContextConfig(
                    enable_codebase_indexing=True,
                    index_file_extensions=[".py", ".js", ".ts", ".md", ".mdc", ".yaml", ".yml"],
                    exclude_patterns=["__pycache__", "node_modules", ".git", "venv", "env"],
                    max_context_size=15000,  # Larger context for comprehensive search
                    max_file_size=2 * 1024 * 1024  # 2MB files
                )
                
                self.context_engine = ContextEngine(context_config)
                logger.info("✅ Anti-Duplication RAG Context Engine initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Anti-Duplication RAG Context Engine: {e}")
                self.context_engine = None
        else:
            logger.warning("⚠️ RAG system not available - anti-duplication tools will have limited functionality")
    
    async def discover_existing_functionality(self, proposed_functionality: str, context: str = None) -> Dict[str, Any]:
        """
        Discover existing functionality before building new features.
        
        Args:
            proposed_functionality: Description of what you want to build
            context: Additional context about the use case
            
        Returns:
            Dictionary with existing functionality analysis and recommendations
        """
        try:
            # Track tool usage
            self._track_tool_usage("discover_existing_functionality")
            
            # Perform semantic search for existing functionality
            existing_systems = await self._search_existing_systems(proposed_functionality)
            
            # Analyze integration opportunities
            integration_options = await self._analyze_integration_opportunities(
                proposed_functionality, existing_systems
            )
            
            # Generate recommendations
            recommendations = await self._generate_integration_recommendations(
                proposed_functionality, existing_systems, integration_options
            )
            
            # Check for potential duplicates
            duplicate_risk = await self._assess_duplicate_risk(
                proposed_functionality, existing_systems
            )
            
            result = {
                "success": True,
                "proposed_functionality": proposed_functionality,
                "existing_systems": existing_systems,
                "integration_opportunities": integration_options,
                "recommendations": recommendations,
                "duplicate_risk": duplicate_risk,
                "action_plan": await self._create_action_plan(recommendations, duplicate_risk),
                "timestamp": datetime.now().isoformat()
            }
            
            # Log the discovery
            await self._log_functionality_discovery(result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Existing functionality discovery failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "proposed_functionality": proposed_functionality,
                "timestamp": datetime.now().isoformat()
            }
    
    async def suggest_integration_approach(self, target_system: str, new_feature: str) -> Dict[str, Any]:
        """
        Suggest how to integrate new functionality with existing systems.
        
        Args:
            target_system: Name or description of existing system
            new_feature: Description of feature to integrate
            
        Returns:
            Integration approach suggestions
        """
        try:
            self._track_tool_usage("suggest_integration_approach")
            
            # Find the target system
            system_info = await self._analyze_target_system(target_system)
            
            # Analyze integration points
            integration_points = await self._find_integration_points(system_info, new_feature)
            
            # Generate integration strategy
            integration_strategy = await self._generate_integration_strategy(
                system_info, new_feature, integration_points
            )
            
            # Assess integration complexity
            complexity_assessment = await self._assess_integration_complexity(
                system_info, new_feature, integration_strategy
            )
            
            return {
                "success": True,
                "target_system": target_system,
                "new_feature": new_feature,
                "system_info": system_info,
                "integration_points": integration_points,
                "integration_strategy": integration_strategy,
                "complexity_assessment": complexity_assessment,
                "implementation_steps": await self._create_implementation_steps(integration_strategy),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Integration approach suggestion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "target_system": target_system,
                "new_feature": new_feature,
                "timestamp": datetime.now().isoformat()
            }
    
    async def map_system_dependencies(self, system_name: str) -> Dict[str, Any]:
        """
        Map dependencies and relationships of existing systems.
        
        Args:
            system_name: Name of system to analyze
            
        Returns:
            System dependency map
        """
        try:
            self._track_tool_usage("map_system_dependencies")
            
            # Find system files
            system_files = await self._find_system_files(system_name)
            
            # Analyze imports and dependencies
            dependencies = await self._analyze_dependencies(system_files)
            
            # Map relationships
            relationships = await self._map_relationships(system_files, dependencies)
            
            # Identify extension points
            extension_points = await self._identify_extension_points(system_files)
            
            return {
                "success": True,
                "system_name": system_name,
                "system_files": system_files,
                "dependencies": dependencies,
                "relationships": relationships,
                "extension_points": extension_points,
                "integration_recommendations": await self._suggest_extension_approaches(extension_points),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ System dependency mapping failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "system_name": system_name,
                "timestamp": datetime.now().isoformat()
            }
    
    # Private helper methods
    
    async def _search_existing_systems(self, proposed_functionality: str) -> List[Dict[str, Any]]:
        """Search for existing systems that might provide similar functionality."""
        if not self.context_engine:
            return []
        
        try:
            # Semantic search for similar functionality
            search_results = self.context_engine.search_context(
                query=proposed_functionality,
                max_results=20
            )
            
            existing_systems = []
            for result in search_results:
                system_info = {
                    "file_path": result.get("file_path", ""),
                    "content_snippet": result.get("content", "")[:500],
                    "relevance_score": result.get("score", 0.0),
                    "system_type": self._classify_system_type(result),
                    "functionality": self._extract_functionality_description(result)
                }
                existing_systems.append(system_info)
            
            return existing_systems
            
        except Exception as e:
            logger.error(f"❌ Existing systems search failed: {e}")
            return []
    
    async def _analyze_integration_opportunities(self, proposed_functionality: str, existing_systems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze opportunities to integrate with existing systems."""
        opportunities = []
        
        for system in existing_systems:
            if system["relevance_score"] > 0.7:  # High relevance threshold
                opportunity = {
                    "system_path": system["file_path"],
                    "integration_type": self._determine_integration_type(proposed_functionality, system),
                    "effort_estimate": self._estimate_integration_effort(system),
                    "benefits": self._identify_integration_benefits(proposed_functionality, system),
                    "risks": self._identify_integration_risks(system)
                }
                opportunities.append(opportunity)
        
        return opportunities
    
    async def _generate_integration_recommendations(self, proposed_functionality: str, existing_systems: List[Dict[str, Any]], integration_options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific recommendations for integration."""
        recommendations = []
        
        if not integration_options:
            recommendations.append({
                "type": "new_implementation",
                "priority": "medium",
                "description": f"No existing systems found for '{proposed_functionality}'. Proceed with new implementation.",
                "action": "Create new functionality with proper integration points for future extensions."
            })
        else:
            # Sort by integration effort and benefits
            sorted_options = sorted(integration_options, key=lambda x: x["effort_estimate"])
            
            for i, option in enumerate(sorted_options[:3]):  # Top 3 options
                recommendations.append({
                    "type": "integration",
                    "priority": "high" if i == 0 else "medium",
                    "description": f"Integrate with existing system: {option['system_path']}",
                    "integration_type": option["integration_type"],
                    "effort_estimate": option["effort_estimate"],
                    "benefits": option["benefits"],
                    "action": f"Extend {option['system_path']} to include {proposed_functionality}"
                })
        
        return recommendations
    
    async def _assess_duplicate_risk(self, proposed_functionality: str, existing_systems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the risk of creating duplicate functionality."""
        high_similarity_systems = [
            system for system in existing_systems 
            if system["relevance_score"] > 0.8
        ]
        
        risk_level = "low"
        if len(high_similarity_systems) > 0:
            risk_level = "high"
        elif len([s for s in existing_systems if s["relevance_score"] > 0.6]) > 2:
            risk_level = "medium"
        
        return {
            "risk_level": risk_level,
            "similar_systems_count": len(high_similarity_systems),
            "highly_similar_systems": high_similarity_systems,
            "recommendation": self._get_risk_recommendation(risk_level, high_similarity_systems)
        }
    
    def _classify_system_type(self, search_result: Dict[str, Any]) -> str:
        """Classify the type of system based on search result."""
        file_path = search_result.get("file_path", "")
        content = search_result.get("content", "")
        
        if "test" in file_path.lower():
            return "test_system"
        elif "agent" in file_path.lower() or "agent" in content.lower():
            return "agent_system"
        elif "util" in file_path.lower():
            return "utility_system"
        elif "script" in file_path.lower():
            return "automation_script"
        elif "mcp" in file_path.lower():
            return "mcp_system"
        elif "rag" in file_path.lower() or "context" in file_path.lower():
            return "rag_system"
        else:
            return "general_system"
    
    def _determine_integration_type(self, proposed_functionality: str, system: Dict[str, Any]) -> str:
        """Determine the type of integration possible."""
        system_type = system["system_type"]
        
        if system_type == "mcp_system":
            return "mcp_tool_extension"
        elif system_type == "agent_system":
            return "agent_capability_extension"
        elif system_type == "utility_system":
            return "utility_function_addition"
        elif system_type == "rag_system":
            return "rag_tool_integration"
        else:
            return "module_extension"
    
    def _track_tool_usage(self, tool_name: str):
        """Track usage statistics for anti-duplication tools."""
        if tool_name not in self.tool_usage_stats:
            self.tool_usage_stats[tool_name] = {"count": 0, "last_used": None}
        
        self.tool_usage_stats[tool_name]["count"] += 1
        self.tool_usage_stats[tool_name]["last_used"] = datetime.now().isoformat()
    
    async def _log_functionality_discovery(self, result: Dict[str, Any]):
        """Log functionality discovery for learning and improvement."""
        try:
            self.agent_tracker.record_context_switch(
                session_id="anti_duplication_agent",
                new_context="functionality_discovery",
                trigger_type="duplicate_prevention",
                trigger_details={
                    "proposed_functionality": result["proposed_functionality"],
                    "existing_systems_found": len(result["existing_systems"]),
                    "duplicate_risk": result["duplicate_risk"]["risk_level"]
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log functionality discovery: {e}")

def get_anti_duplication_rag_tools() -> AntiDuplicationRAGTools:
    """Get anti-duplication RAG tools instance."""
    return AntiDuplicationRAGTools()
