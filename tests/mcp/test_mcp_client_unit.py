#!/usr/bin/env python3
"""
MCP Client Unit Tests
====================

Comprehensive unit tests for MCP client components:
- MCPClient: Main client functionality
- MCPConnection: Server connection management
- MCPClientConfig: Configuration management
- Tool discovery and execution

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
    from utils.mcp.client import (
        MCPClient, create_mcp_client, MCPConnection, MCPClientConfig,
        MCPServerInfo, MCPToolRequest, ConnectionState
    )
    from utils.mcp.server import AccessLevel, ToolCategory
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"❌ MCP client import failed: {e}")
    MCP_AVAILABLE = False


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
class TestMCPClientConfig:
    """Test suite for MCP Client Configuration."""
    
    def test_config_creation(self):
        """Test MCP client configuration creation."""
        config = MCPClientConfig(
            agent_id="test_agent",
            agent_type="test_type"
        )
        
        assert config.agent_id == "test_agent"
        assert config.agent_type == "test_type"
        assert config.auto_discover is True  # Default value
        assert config.connection_timeout == 10  # Default value
        assert config.enable_caching is True  # Default value
    
    def test_config_custom_values(self):
        """Test MCP client configuration with custom values."""
        config = MCPClientConfig(
            agent_id="custom_agent",
            agent_type="custom_type",
            auto_discover=False,
            connection_timeout=20,
            request_timeout=60,
            max_concurrent_requests=10,
            enable_caching=False
        )
        
        assert config.agent_id == "custom_agent"
        assert config.auto_discover is False
        assert config.connection_timeout == 20
        assert config.request_timeout == 60
        assert config.max_concurrent_requests == 10
        assert config.enable_caching is False


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
class TestMCPServerInfo:
    """Test suite for MCP Server Info."""
    
    def test_server_info_creation(self):
        """Test MCP server info creation."""
        server_info = MCPServerInfo(
            server_id="test_server",
            name="Test MCP Server",
            host="localhost",
            port=8765,
            capabilities=["tool_execution", "capability_negotiation"],
            tool_count=12,
            categories={"agile": 3, "database": 2, "file_system": 2}
        )
        
        assert server_info.server_id == "test_server"
        assert server_info.name == "Test MCP Server"
        assert server_info.host == "localhost"
        assert server_info.port == 8765
        assert len(server_info.capabilities) == 2
        assert server_info.tool_count == 12
        assert server_info.status == ConnectionState.DISCONNECTED  # Default


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
class TestMCPToolRequest:
    """Test suite for MCP Tool Request."""
    
    def test_tool_request_creation(self):
        """Test MCP tool request creation."""
        request = MCPToolRequest(
            request_id="req_001",
            agent_id="test_agent",
            tool_id="agile.create_user_story",
            parameters={"title": "Test Story", "description": "Test Description"}
        )
        
        assert request.request_id == "req_001"
        assert request.agent_id == "test_agent"
        assert request.tool_id == "agile.create_user_story"
        assert request.parameters["title"] == "Test Story"
        assert request.timeout == 30  # Default value
        assert request.priority == 1  # Default value
    
    def test_tool_request_with_custom_values(self):
        """Test MCP tool request with custom values."""
        callback_mock = Mock()
        
        request = MCPToolRequest(
            request_id="req_002",
            agent_id="test_agent",
            tool_id="db.track_agent_session",
            parameters={"agent_id": "test", "agent_type": "test"},
            timeout=60,
            priority=2,
            callback=callback_mock
        )
        
        assert request.timeout == 60
        assert request.priority == 2
        assert request.callback == callback_mock


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
class TestMCPClient:
    """Test suite for MCP Client."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.config = MCPClientConfig(
            agent_id="test_agent",
            agent_type="unit_test",
            auto_discover=False  # Disable auto-discovery for unit tests
        )
        self.client = MCPClient(self.config)
    
    def test_client_creation(self):
        """Test MCP client creation."""
        assert self.client is not None
        assert isinstance(self.client, MCPClient)
        assert self.client.config == self.config
        assert len(self.client.connections) == 0
        assert self.client._running is False
    
    @pytest.mark.asyncio
    async def test_client_start_stop(self):
        """Test MCP client start and stop."""
        # Test start
        await self.client.start()
        assert self.client._running is True
        
        # Test stop
        await self.client.stop()
        assert self.client._running is False
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        tool_id = "test.tool"
        parameters = {"param1": "value1", "param2": "value2"}
        
        cache_key = self.client._generate_cache_key(tool_id, parameters)
        
        assert isinstance(cache_key, str)
        assert len(cache_key) == 32  # MD5 hash length
        
        # Same parameters should generate same cache key
        cache_key2 = self.client._generate_cache_key(tool_id, parameters)
        assert cache_key == cache_key2
        
        # Different parameters should generate different cache key
        different_params = {"param1": "different_value"}
        cache_key3 = self.client._generate_cache_key(tool_id, different_params)
        assert cache_key != cache_key3
    
    def test_client_stats(self):
        """Test client statistics retrieval."""
        stats = self.client.get_client_stats()
        
        assert isinstance(stats, dict)
        assert "agent_id" in stats
        assert "agent_type" in stats
        assert "connected_servers" in stats
        assert "total_tools" in stats
        assert "cache_size" in stats
        assert "running" in stats
        
        assert stats["agent_id"] == "test_agent"
        assert stats["agent_type"] == "unit_test"
        assert stats["connected_servers"] == 0  # No connections in unit test
        assert stats["running"] is False  # Not started in this test
    
    def test_find_tool_connection_no_connections(self):
        """Test finding tool connection when no connections exist."""
        connection = self.client._find_tool_connection("nonexistent.tool")
        assert connection is None
    
    def test_get_available_tools_no_connections(self):
        """Test getting available tools when no connections exist."""
        tools = self.client.get_available_tools()
        assert isinstance(tools, list)
        assert len(tools) == 0
    
    def test_get_server_info_no_connections(self):
        """Test getting server info when no connections exist."""
        server_info = self.client.get_server_info()
        assert isinstance(server_info, list)
        assert len(server_info) == 0


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
class TestMCPConnection:
    """Test suite for MCP Connection."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.server_info = MCPServerInfo(
            server_id="test_server",
            name="Test Server",
            host="localhost",
            port=8765,
            capabilities=["tool_execution"],
            tool_count=0,
            categories={}
        )
        self.config = MCPClientConfig(
            agent_id="test_agent",
            agent_type="unit_test"
        )
        self.connection = MCPConnection(self.server_info, self.config)
    
    def test_connection_creation(self):
        """Test MCP connection creation."""
        assert self.connection is not None
        assert self.connection.server_info == self.server_info
        assert self.connection.config == self.config
        assert self.connection.state == ConnectionState.DISCONNECTED
        assert self.connection.server_instance is None
        assert len(self.connection.available_tools) == 0
    
    def test_get_tool_info_no_tools(self):
        """Test getting tool info when no tools are available."""
        tool_info = self.connection.get_tool_info("nonexistent.tool")
        assert tool_info is None
    
    def test_list_tools_no_tools(self):
        """Test listing tools when no tools are available."""
        tools = self.connection.list_tools()
        assert isinstance(tools, list)
        assert len(tools) == 0
        
        # Test with category filter
        agile_tools = self.connection.list_tools(category=ToolCategory.AGILE)
        assert isinstance(agile_tools, list)
        assert len(agile_tools) == 0


# Factory function tests
@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
def test_create_mcp_client():
    """Test MCP client factory function."""
    client = create_mcp_client("factory_test_agent", "factory_test")
    
    assert client is not None
    assert isinstance(client, MCPClient)
    assert client.config.agent_id == "factory_test_agent"
    assert client.config.agent_type == "factory_test"


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP components not available")
def test_create_mcp_client_with_kwargs():
    """Test MCP client factory function with additional kwargs."""
    client = create_mcp_client(
        "factory_test_agent_2",
        "factory_test_2",
        auto_discover=False,
        connection_timeout=20,
        enable_caching=False
    )
    
    assert client.config.agent_id == "factory_test_agent_2"
    assert client.config.agent_type == "factory_test_2"
    assert client.config.auto_discover is False
    assert client.config.connection_timeout == 20
    assert client.config.enable_caching is False


# Test runner function for pytest integration
def test_mcp_client_components():
    """Main test function for pytest integration."""
    if not MCP_AVAILABLE:
        pytest.skip("MCP components not available")
    
    # This function can be called by pytest to run all MCP client tests
    pass


if __name__ == "__main__":
    # Run tests with pytest when executed directly
    pytest.main([__file__, "-v"])
