#!/usr/bin/env python3
"""
MCP Client Implementation for AI-Dev-Agent
==========================================

Model Context Protocol client library for agent integration.
Enables agents to discover, connect to, and execute tools through MCP servers.

Features:
- Automatic server discovery and connection
- Tool capability negotiation
- Asynchronous tool execution with monitoring
- Universal Agent Tracker integration
- Error handling and recovery
- Connection pooling and management

Architecture:
- MCPClient: Main client interface for agents
- MCPConnection: Individual server connection management
- MCPToolProxy: Tool execution proxy with caching
- MCPAgentIntegration: Integration with existing agent framework

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 1)
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from abc import ABC, abstractmethod

# Import MCP server components
from .server import (
    MCPServer, ToolDefinition, ToolExecutionResult, 
    AccessLevel, ToolCategory, create_mcp_server
)

# Universal Agent Tracker integration
try:
    from utils.system.universal_agent_tracker import get_universal_tracker, AgentType, ContextType
    UNIVERSAL_TRACKING_AVAILABLE = True
except ImportError:
    UNIVERSAL_TRACKING_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """MCP connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class MCPServerInfo:
    """Information about an MCP server."""
    server_id: str
    name: str
    host: str
    port: int
    capabilities: List[str]
    tool_count: int
    categories: Dict[str, int]
    status: ConnectionState = ConnectionState.DISCONNECTED


@dataclass
class MCPToolRequest:
    """MCP tool execution request."""
    request_id: str
    agent_id: str
    tool_id: str
    parameters: Dict[str, Any]
    timeout: int = 30
    priority: int = 1  # 1=high, 2=medium, 3=low
    callback: Optional[Callable] = None


@dataclass
class MCPClientConfig:
    """Configuration for MCP client."""
    agent_id: str
    agent_type: str = "ai_agent"
    auto_discover: bool = True
    connection_timeout: int = 10
    request_timeout: int = 30
    max_concurrent_requests: int = 5
    retry_attempts: int = 3
    enable_caching: bool = True
    cache_ttl: int = 300


class MCPConnection:
    """Manages connection to a single MCP server."""
    
    def __init__(self, server_info: MCPServerInfo, client_config: MCPClientConfig):
        """
        Initialize MCP connection.
        
        Args:
            server_info: Information about the MCP server
            client_config: Client configuration
        """
        self.server_info = server_info
        self.config = client_config
        self.state = ConnectionState.DISCONNECTED
        self.server_instance: Optional[MCPServer] = None
        self.available_tools: Dict[str, ToolDefinition] = {}
        self.connection_time: Optional[datetime] = None
        self.last_error: Optional[str] = None
        
    async def connect(self) -> bool:
        """
        Connect to the MCP server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.state = ConnectionState.CONNECTING
            logger.info(f"🔌 Connecting to MCP server: {self.server_info.name}")
            
            # For local server, create server instance
            if self.server_info.host == "localhost":
                self.server_instance = create_mcp_server(
                    host=self.server_info.host,
                    port=self.server_info.port
                )
                await self.server_instance.start()
            
            # Discover available tools
            await self._discover_tools()
            
            self.state = ConnectionState.CONNECTED
            self.connection_time = datetime.now()
            self.last_error = None
            
            logger.info(f"✅ Connected to MCP server: {len(self.available_tools)} tools available")
            return True
            
        except Exception as e:
            self.state = ConnectionState.ERROR
            self.last_error = str(e)
            logger.error(f"❌ Failed to connect to MCP server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        try:
            if self.server_instance:
                await self.server_instance.stop()
            
            self.state = ConnectionState.DISCONNECTED
            self.connection_time = None
            logger.info(f"🔌 Disconnected from MCP server: {self.server_info.name}")
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting from MCP server: {e}")
    
    async def _discover_tools(self):
        """Discover available tools from the server."""
        if not self.server_instance:
            return
        
        # Get tools from server registry
        for tool_id, tool_def in self.server_instance.tool_registry.tools.items():
            self.available_tools[tool_id] = tool_def
        
        # Update server info
        self.server_info.tool_count = len(self.available_tools)
        self.server_info.categories = self.server_instance.tool_registry.get_tool_categories()
    
    async def execute_tool(self, request: MCPToolRequest) -> ToolExecutionResult:
        """
        Execute a tool through this connection.
        
        Args:
            request: Tool execution request
            
        Returns:
            Tool execution result
        """
        if self.state != ConnectionState.CONNECTED or not self.server_instance:
            return ToolExecutionResult(
                request_id=request.request_id,
                tool_id=request.tool_id,
                success=False,
                error="Not connected to MCP server"
            )
        
        try:
            # Execute tool through server
            result = await self.server_instance.handle_tool_request(
                agent_id=request.agent_id,
                tool_id=request.tool_id,
                parameters=request.parameters
            )
            
            # Call callback if provided
            if request.callback:
                try:
                    await request.callback(result)
                except Exception as e:
                    logger.warning(f"Tool callback error: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Tool execution error: {e}")
            return ToolExecutionResult(
                request_id=request.request_id,
                tool_id=request.tool_id,
                success=False,
                error=str(e)
            )
    
    def get_tool_info(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get information about a specific tool."""
        return self.available_tools.get(tool_id)
    
    def list_tools(self, category: Optional[ToolCategory] = None) -> List[ToolDefinition]:
        """List available tools, optionally filtered by category."""
        tools = list(self.available_tools.values())
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        return tools


class MCPClient:
    """
    Main MCP client for agent integration.
    
    Provides high-level interface for agents to discover and use MCP tools.
    """
    
    def __init__(self, config: MCPClientConfig):
        """
        Initialize MCP client.
        
        Args:
            config: Client configuration
        """
        self.config = config
        self.connections: Dict[str, MCPConnection] = {}
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.active_requests: Dict[str, MCPToolRequest] = {}
        self.tool_cache: Dict[str, Any] = {}
        
        # Universal Agent Tracker integration
        self.universal_tracker = None
        if UNIVERSAL_TRACKING_AVAILABLE:
            try:
                self.universal_tracker = get_universal_tracker()
                logger.info("✅ Universal Agent Tracker integration active")
            except Exception as e:
                logger.warning(f"Universal Agent Tracker integration failed: {e}")
        
        # Start background task processor
        self._processor_task = None
        self._running = False
    
    async def start(self) -> bool:
        """
        Start the MCP client.
        
        Returns:
            True if client started successfully, False otherwise
        """
        try:
            self._running = True
            
            # Auto-discover servers if enabled
            if self.config.auto_discover:
                await self._discover_servers()
            
            # Start request processor
            self._processor_task = asyncio.create_task(self._process_requests())
            
            # Check if we have at least one active connection
            if not self.connections:
                logger.error("❌ No MCP server connections established")
                return False
            
            logger.info(f"🚀 MCP Client started for agent: {self.config.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start MCP client: {e}")
            self._running = False
            return False
    
    async def stop(self):
        """Stop the MCP client."""
        self._running = False
        
        # Stop request processor
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect from all servers
        for connection in self.connections.values():
            await connection.disconnect()
        
        logger.info(f"🛑 MCP Client stopped for agent: {self.config.agent_id}")
    
    async def _discover_servers(self):
        """Discover available MCP servers."""
        # For now, just connect to local server
        local_server = MCPServerInfo(
            server_id="local_mcp_server",
            name="AI-Dev-Agent MCP Server",
            host="localhost",
            port=8765,
            capabilities=["tool_execution", "capability_negotiation"],
            tool_count=0,
            categories={}
        )
        
        success = await self.connect_to_server(local_server)
        if not success:
            logger.warning(f"⚠️  Failed to connect to local MCP server")
    
    async def connect_to_server(self, server_info: MCPServerInfo) -> bool:
        """
        Connect to an MCP server.
        
        Args:
            server_info: Information about the server to connect to
            
        Returns:
            True if connection successful, False otherwise
        """
        connection = MCPConnection(server_info, self.config)
        
        if await connection.connect():
            self.connections[server_info.server_id] = connection
            logger.info(f"✅ Connected to MCP server: {server_info.name}")
            
            # Track connection with Universal Agent Tracker
            if self.universal_tracker:
                try:
                    await self.universal_tracker.record_context_switch(
                        session_id=self.config.agent_id,
                        new_context=f"mcp_connected_{server_info.server_id}",
                        from_context="agent_initialization",
                        trigger_type="mcp_connection",
                        trigger_details={
                            "server_id": server_info.server_id,
                            "server_name": server_info.name,
                            "tool_count": connection.server_info.tool_count
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to track MCP connection: {e}")
            
            return True
        else:
            logger.error(f"❌ Failed to connect to MCP server: {server_info.name}")
            return False
    
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any], 
                         timeout: int = None, priority: int = 1,
                         callback: Optional[Callable] = None) -> ToolExecutionResult:
        """
        Execute an MCP tool.
        
        Args:
            tool_id: ID of tool to execute
            parameters: Tool parameters
            timeout: Execution timeout (uses config default if None)
            priority: Request priority (1=high, 2=medium, 3=low)
            callback: Optional callback function for result
            
        Returns:
            Tool execution result
        """
        # Create request
        request = MCPToolRequest(
            request_id=str(uuid.uuid4()),
            agent_id=self.config.agent_id,
            tool_id=tool_id,
            parameters=parameters,
            timeout=timeout or self.config.request_timeout,
            priority=priority,
            callback=callback
        )
        
        # Check cache first
        if self.config.enable_caching:
            cache_key = self._generate_cache_key(tool_id, parameters)
            if cache_key in self.tool_cache:
                cached_result = self.tool_cache[cache_key]
                if time.time() - cached_result['timestamp'] < self.config.cache_ttl:
                    logger.debug(f"Cache hit for tool: {tool_id}")
                    result = cached_result['result']
                    result.cached = True
                    return result
        
        # Find appropriate connection
        connection = self._find_tool_connection(tool_id)
        if not connection:
            return ToolExecutionResult(
                request_id=request.request_id,
                tool_id=tool_id,
                success=False,
                error=f"No connection available for tool: {tool_id}"
            )
        
        # Execute tool
        try:
            result = await connection.execute_tool(request)
            
            # Cache successful results
            if self.config.enable_caching and result.success:
                cache_key = self._generate_cache_key(tool_id, parameters)
                self.tool_cache[cache_key] = {
                    'result': result,
                    'timestamp': time.time()
                }
            
            # Track execution with Universal Agent Tracker
            if self.universal_tracker and result.success:
                try:
                    await self.universal_tracker.record_context_switch(
                        session_id=self.config.agent_id,
                        new_context=f"tool_executed_{tool_id}",
                        from_context="agent_operation",
                        trigger_type="mcp_tool_execution",
                        trigger_details={
                            "tool_id": tool_id,
                            "success": result.success,
                            "execution_time": result.execution_time,
                            "parameters": parameters
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to track tool execution: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Tool execution failed: {e}")
            return ToolExecutionResult(
                request_id=request.request_id,
                tool_id=tool_id,
                success=False,
                error=str(e)
            )
    
    def _find_tool_connection(self, tool_id: str) -> Optional[MCPConnection]:
        """Find connection that provides the specified tool."""
        for connection in self.connections.values():
            if connection.state == ConnectionState.CONNECTED:
                if tool_id in connection.available_tools:
                    return connection
        return None
    
    def _generate_cache_key(self, tool_id: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key for tool execution."""
        import hashlib
        key_data = f"{tool_id}:{json.dumps(parameters, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _process_requests(self):
        """Background task to process tool requests."""
        while self._running:
            try:
                # Process queued requests (for future async queue implementation)
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Request processor error: {e}")
    
    def get_available_tools(self, category: Optional[ToolCategory] = None) -> List[ToolDefinition]:
        """
        Get list of available tools across all connections.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of available tool definitions
        """
        tools = []
        for connection in self.connections.values():
            if connection.state == ConnectionState.CONNECTED:
                tools.extend(connection.list_tools(category))
        return tools
    
    def get_server_info(self) -> List[MCPServerInfo]:
        """Get information about connected servers."""
        return [conn.server_info for conn in self.connections.values()]
    
    def get_client_stats(self) -> Dict[str, Any]:
        """Get client statistics and status."""
        connected_servers = sum(1 for conn in self.connections.values() 
                              if conn.state == ConnectionState.CONNECTED)
        total_tools = sum(len(conn.available_tools) for conn in self.connections.values())
        
        return {
            "agent_id": self.config.agent_id,
            "agent_type": self.config.agent_type,
            "connected_servers": connected_servers,
            "total_servers": len(self.connections),
            "total_tools": total_tools,
            "cache_size": len(self.tool_cache),
            "universal_tracking": UNIVERSAL_TRACKING_AVAILABLE,
            "running": self._running
        }


# Factory function for easy client creation
def create_mcp_client(agent_id: str, agent_type: str = "ai_agent", **kwargs) -> MCPClient:
    """
    Create and configure MCP client instance.
    
    Args:
        agent_id: Unique identifier for the agent
        agent_type: Type of agent (for tracking)
        **kwargs: Additional configuration options
        
    Returns:
        Configured MCP client instance
    """
    config = MCPClientConfig(
        agent_id=agent_id,
        agent_type=agent_type,
        **kwargs
    )
    return MCPClient(config)


# Main execution for testing
if __name__ == "__main__":
    async def main():
        """Test MCP client functionality."""
        # Create client
        client = create_mcp_client("test_agent", "testing_agent")
        
        # Start client
        await client.start()
        
        try:
            # Get available tools
            tools = client.get_available_tools()
            logger.info(f"Available tools: {len(tools)}")
            
            # Test tool execution
            if tools:
                test_tool = tools[0]
                logger.info(f"Testing tool: {test_tool.tool_id}")
                
                # Execute with minimal parameters
                result = await client.execute_tool(
                    tool_id=test_tool.tool_id,
                    parameters={}  # Minimal parameters for testing
                )
                
                logger.info(f"Test execution result: {result.success}")
            
            # Show client stats
            stats = client.get_client_stats()
            logger.info(f"Client stats: {json.dumps(stats, indent=2)}")
            
        finally:
            # Stop client
            await client.stop()
    
    # Run test
    asyncio.run(main())
