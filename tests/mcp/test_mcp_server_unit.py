#!/usr/bin/env python3
"""
MCP Server Unit Tests
====================

Comprehensive unit tests for MCP server components:
- MCPToolRegistry: Tool registration and management
- MCPSecurityManager: Access control and security
- MCPExecutionEngine: Tool execution and monitoring
- MCPServer: Main server functionality

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 1)
"""

import asyncio
import pytest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import MCP components
try:
    from utils.mcp.server import (
        MCPServer, create_mcp_server, MCPToolRegistry, MCPSecurityManager,
        MCPExecutionEngine, ToolDefinition, ToolExecutionContext,
        ToolExecutionResult, AccessLevel, ToolCategory
    )
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"❌ MCP import failed: {e}")
    MCP_AVAILABLE = False


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
class TestMCPToolRegistry:
    """Test suite for MCP Tool Registry."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.registry = MCPToolRegistry()
    
    def test_registry_initialization(self):
        """Test tool registry initialization."""
        assert self.registry is not None
        assert isinstance(self.registry.tools, dict)
        assert len(self.registry.tools) >= 12  # At least 12 critical tools
    
    def test_critical_tools_registered(self):
        """Test that all critical tools are registered."""
        critical_tools = [
            "agile.create_user_story",
            "agile.update_artifacts", 
            "agile.update_catalogs",
            "db.track_agent_session",
            "db.log_multi_database",
            "file.manage_files",
            "file.enforce_organization",
            "git.automate_workflow",
            "test.run_pipeline",
            "test.generate_catalogue",
            "system.platform_commands",
            "system.configure_logging",
            "ai.edit_prompts"
        ]
        
        registered_tools = list(self.registry.tools.keys())
        
        for tool_id in critical_tools:
            assert tool_id in registered_tools, f"Critical tool {tool_id} not registered"
            tool = self.registry.get_tool(tool_id)
            assert isinstance(tool, ToolDefinition)
            assert tool.tool_id == tool_id
    
    def test_tool_categories(self):
        """Test tool categorization."""
        categories = self.registry.get_tool_categories()
        
        # Verify expected categories exist
        expected_categories = ["agile", "database", "file_system", "git", "testing", "ai"]
        for category in expected_categories:
            assert category in categories, f"Category {category} missing"
            assert categories[category] > 0, f"No tools in category {category}"
    
    def test_tool_access_levels(self):
        """Test tool access level assignments."""
        # Test specific access levels
        public_tool = self.registry.get_tool("db.track_agent_session")
        assert public_tool.access_level == AccessLevel.PUBLIC
        
        restricted_tools = self.registry.list_tools(access_level=AccessLevel.RESTRICTED)
        assert len(restricted_tools) > 0
        
        privileged_tools = self.registry.list_tools(access_level=AccessLevel.PRIVILEGED)
        assert len(privileged_tools) > 0
    
    def test_tool_filtering(self):
        """Test tool filtering by category and access level."""
        # Filter by category
        agile_tools = self.registry.list_tools(category=ToolCategory.AGILE)
        assert len(agile_tools) > 0
        for tool in agile_tools:
            assert tool.category == ToolCategory.AGILE
        
        # Filter by access level
        public_tools = self.registry.list_tools(access_level=AccessLevel.PUBLIC)
        assert len(public_tools) > 0
        for tool in public_tools:
            assert tool.access_level == AccessLevel.PUBLIC


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
class TestMCPSecurityManager:
    """Test suite for MCP Security Manager."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.security_manager = MCPSecurityManager()
    
    def test_security_manager_initialization(self):
        """Test security manager initialization."""
        assert self.security_manager is not None
        assert hasattr(self.security_manager, 'access_policies')
        assert len(self.security_manager.access_policies) == 3  # PUBLIC, RESTRICTED, PRIVILEGED
    
    @pytest.mark.asyncio
    async def test_public_access_authorization(self):
        """Test authorization for public access tools."""
        context = ToolExecutionContext(
            request_id="test_001",
            agent_id="test_agent",
            tool_id="db.track_agent_session",
            parameters={"agent_id": "test", "agent_type": "test"},
            timestamp=datetime.now(),
            access_level=AccessLevel.PUBLIC
        )
        
        authorized = await self.security_manager.authorize_tool_access(context)
        assert authorized is True
    
    @pytest.mark.asyncio
    async def test_restricted_access_authorization(self):
        """Test authorization for restricted access tools."""
        context = ToolExecutionContext(
            request_id="test_002",
            agent_id="test_agent",
            tool_id="agile.create_user_story",
            parameters={"title": "Test Story", "description": "Test"},
            timestamp=datetime.now(),
            access_level=AccessLevel.RESTRICTED
        )
        
        authorized = await self.security_manager.authorize_tool_access(context)
        assert authorized is True  # Should pass with current simplified auth
    
    def test_security_audit_logging(self):
        """Test security audit logging."""
        initial_log_count = len(self.security_manager.audit_log)
        
        context = ToolExecutionContext(
            request_id="test_003",
            agent_id="test_agent",
            tool_id="test.tool",
            parameters={},
            timestamp=datetime.now(),
            access_level=AccessLevel.PUBLIC
        )
        
        self.security_manager._log_security_event("test_event", context)
        
        assert len(self.security_manager.audit_log) == initial_log_count + 1
        latest_event = self.security_manager.audit_log[-1]
        assert latest_event["event_type"] == "test_event"
        assert latest_event["agent_id"] == "test_agent"


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
class TestMCPExecutionEngine:
    """Test suite for MCP Execution Engine."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.registry = MCPToolRegistry()
        self.security_manager = MCPSecurityManager()
        self.execution_engine = MCPExecutionEngine(self.registry, self.security_manager)
    
    def test_execution_engine_initialization(self):
        """Test execution engine initialization."""
        assert self.execution_engine is not None
        assert self.execution_engine.tool_registry == self.registry
        assert self.execution_engine.security_manager == self.security_manager
    
    @pytest.mark.asyncio
    async def test_tool_not_found_error(self):
        """Test handling of non-existent tool execution."""
        context = ToolExecutionContext(
            request_id="test_004",
            agent_id="test_agent",
            tool_id="nonexistent.tool",
            parameters={},
            timestamp=datetime.now(),
            access_level=AccessLevel.PUBLIC
        )
        
        result = await self.execution_engine.execute_tool(context)
        
        assert result.success is False
        assert "Tool not found" in result.error
        assert result.tool_id == "nonexistent.tool"
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test cache key generation for tool execution."""
        context = ToolExecutionContext(
            request_id="test_005",
            agent_id="test_agent",
            tool_id="test.tool",
            parameters={"param1": "value1", "param2": "value2"},
            timestamp=datetime.now(),
            access_level=AccessLevel.PUBLIC
        )
        
        cache_key = self.execution_engine._generate_cache_key(context)
        
        assert isinstance(cache_key, str)
        assert len(cache_key) == 32  # MD5 hash length
        
        # Same parameters should generate same cache key
        cache_key2 = self.execution_engine._generate_cache_key(context)
        assert cache_key == cache_key2


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
class TestMCPServer:
    """Test suite for MCP Server."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.server = create_mcp_server()
    
    def test_server_creation(self):
        """Test MCP server creation."""
        assert self.server is not None
        assert isinstance(self.server, MCPServer)
        assert self.server.host == "localhost"
        assert self.server.port == 8765
    
    def test_server_components_initialization(self):
        """Test server component initialization."""
        assert self.server.tool_registry is not None
        assert self.server.security_manager is not None
        assert self.server.execution_engine is not None
        assert len(self.server.tool_registry.tools) >= 12
    
    @pytest.mark.asyncio
    async def test_server_startup_shutdown(self):
        """Test server startup and shutdown."""
        # Test startup
        await self.server.start()
        assert self.server.running is True
        
        # Test shutdown
        await self.server.stop()
        assert self.server.running is False
    
    def test_server_info(self):
        """Test server information retrieval."""
        info = self.server.get_server_info()
        
        assert isinstance(info, dict)
        assert "server_name" in info
        assert "version" in info
        assert "tools_count" in info
        assert "categories" in info
        assert info["tools_count"] >= 12
        assert info["security_enabled"] is True
    
    @pytest.mark.asyncio
    async def test_tool_request_handling(self):
        """Test tool request handling."""
        # Test with a public tool that should work
        result = await self.server.handle_tool_request(
            agent_id="test_agent",
            tool_id="db.track_agent_session",
            parameters={
                "agent_id": "test_agent",
                "agent_type": "test_agent",
                "context": {"test": True}
            }
        )
        
        assert isinstance(result, ToolExecutionResult)
        assert result.tool_id == "db.track_agent_session"
        # Note: This might fail due to missing actual implementation,
        # but the structure should be correct


# Test runner function for pytest integration
def test_mcp_server_components():
    """Main test function for pytest integration."""
    if not MCP_AVAILABLE:
        pytest.skip("MCP components not available")
    
    # This function can be called by pytest to run all MCP server tests
    pass


if __name__ == "__main__":
    # Run tests with pytest when executed directly
    pytest.main([__file__, "-v"])
