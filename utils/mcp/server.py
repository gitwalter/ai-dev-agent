#!/usr/bin/env python3
"""
MCP Server Implementation for AI-Dev-Agent
==========================================

Clean, dynamic MCP server that loads tools automatically from tool modules.
No hardcoded tool definitions - everything is discovered dynamically.

Created: 2025-10-10 (Cleaned up version)
"""

import asyncio
import json
import logging
import time
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

# Import MCP tool definitions
from utils.mcp.mcp_tool import AccessLevel, ToolCategory, ToolDefinition, get_all_mcp_tools_from_module

# Universal Agent Tracker integration
try:
    from utils.system.universal_agent_tracker import get_universal_tracker, AgentType, ContextType
    UNIVERSAL_TRACKING_AVAILABLE = True
except ImportError:
    UNIVERSAL_TRACKING_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ToolExecutionContext:
    """Context for tool execution."""
    request_id: str
    agent_id: str
    tool_id: str
    parameters: Dict[str, Any]
    timestamp: datetime
    access_level: AccessLevel = AccessLevel.PUBLIC


@dataclass
class ToolExecutionResult:
    """Result of tool execution."""
    request_id: str
    tool_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    error_details: Optional[Dict] = None
    execution_time: float = 0.0
    cached: bool = False


class MCPSecurityManager:
    """Security manager for MCP tools."""
    
    def __init__(self):
        self.audit_log = []
        self.blocked_agents = set()
    
    def validate_access(self, context: ToolExecutionContext, tool: ToolDefinition) -> bool:
        """Validate agent access to tool."""
        if context.agent_id in self.blocked_agents:
            self._log_security_event("access_denied_blocked_agent", context)
            return False
        
        # Simple access level check
        if tool.access_level == AccessLevel.PRIVILEGED:
            # In production, implement proper authorization
            self._log_security_event("privileged_access", context)
        
        return True
    
    def _log_security_event(self, event_type: str, context: ToolExecutionContext, **kwargs):
        """Log security event."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'agent_id': context.agent_id,
            'tool_id': context.tool_id,
            **kwargs
        }
        self.audit_log.append(event)
        logger.info(f"Security event: {event_type} - Agent: {context.agent_id}, Tool: {context.tool_id}")


class MCPToolRegistry:
    """Dynamic tool registry that loads tools from modules."""
    
    def __init__(self):
        """Initialize tool registry and load all tools dynamically."""
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_functions: Dict[str, Callable] = {}
        self._load_all_tools()
    
    def _load_all_tools(self):
        """Load all MCP tools dynamically from tool modules."""
        tool_modules = [
            'utils.mcp.tools.file_access_tools',
            'utils.mcp.tools.database_tools',
            'utils.mcp.tools.agile_tools',
            'utils.mcp.tools.rag_swarm_tools',
            'utils.mcp.tools.research_swarm_tools',
            'utils.mcp.tools.google_drive_tools',
            'utils.mcp.tools.link_integrity_tools',
        ]
        
        total_loaded = 0
        
        for module_name in tool_modules:
            try:
                # Import module
                module_parts = module_name.split('.')
                module = __import__(module_name, fromlist=[module_parts[-1]])
                
                # Extract all MCP tools from module
                tools = get_all_mcp_tools_from_module(module)
                
                # Register each tool
                for tool_id, (func, tool_def) in tools.items():
                    self.tools[tool_id] = tool_def
                    self.tool_functions[tool_id] = func
                    total_loaded += 1
                
                logger.info(f"✅ Loaded {len(tools)} tools from {module_name.split('.')[-1]}")
                
            except ImportError as e:
                logger.warning(f"⚠️ Could not load {module_name}: {e}")
            except Exception as e:
                logger.error(f"❌ Error loading {module_name}: {e}")
        
        logger.info(f"🚀 Total tools loaded: {total_loaded}")
    
    def get_tool(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get tool definition by ID."""
        return self.tools.get(tool_id)
    
    def get_tool_function(self, tool_id: str) -> Optional[Callable]:
        """Get tool function by ID."""
        return self.tool_functions.get(tool_id)
    
    def list_tools(self, category: Optional[ToolCategory] = None, 
                   access_level: Optional[AccessLevel] = None) -> List[ToolDefinition]:
        """List tools by category and/or access level."""
        tools = list(self.tools.values())
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        if access_level:
            tools = [t for t in tools if t.access_level == access_level]
        
        return tools
    
    def get_tool_categories(self) -> Dict[str, int]:
        """Get tool count by category."""
        categories = {}
        for tool in self.tools.values():
            category = tool.category.value
            categories[category] = categories.get(category, 0) + 1
        return categories


class MCPExecutionEngine:
    """Execution engine for MCP tools."""
    
    def __init__(self, tool_registry: MCPToolRegistry, security_manager: MCPSecurityManager):
        self.tool_registry = tool_registry
        self.security_manager = security_manager
        self.execution_cache = {}
    
    async def execute_tool(self, context: ToolExecutionContext) -> ToolExecutionResult:
        """Execute a tool with the given context."""
        start_time = time.time()
        
        try:
            # Get tool definition
            tool = self.tool_registry.get_tool(context.tool_id)
            if not tool:
                return ToolExecutionResult(
                    request_id=context.request_id,
                    tool_id=context.tool_id,
                    success=False,
                    error=f"Tool not found: {context.tool_id}",
                    execution_time=time.time() - start_time
                )
            
            # Security check
            if not self.security_manager.validate_access(context, tool):
                return ToolExecutionResult(
                    request_id=context.request_id,
                    tool_id=context.tool_id,
                    success=False,
                    error="Access denied",
                    execution_time=time.time() - start_time
                )
            
            # Check cache
            if tool.cache_ttl > 0:
                cache_key = self._generate_cache_key(context)
                if cache_key in self.execution_cache:
                    cached_result, cached_time = self.execution_cache[cache_key]
                    if time.time() - cached_time < tool.cache_ttl:
                        logger.info(f"Cache hit for {context.tool_id}")
                        return ToolExecutionResult(
                            request_id=context.request_id,
                            tool_id=context.tool_id,
                            success=True,
                            result=cached_result,
                            execution_time=time.time() - start_time,
                            cached=True
                        )
            
            # Execute tool
            result = await self._execute_tool_function(tool, context)
            
            # Cache result if successful
            if result.success and tool.cache_ttl > 0:
                cache_key = self._generate_cache_key(context)
                self.execution_cache[cache_key] = (result.result, time.time())
            
            result.execution_time = time.time() - start_time
            return result
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return ToolExecutionResult(
                request_id=context.request_id,
                tool_id=context.tool_id,
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _execute_tool_function(self, tool: ToolDefinition, 
                                   context: ToolExecutionContext) -> ToolExecutionResult:
        """Execute the actual tool function."""
        try:
            # Get function from registry
            func = self.tool_registry.get_tool_function(context.tool_id)
            
            if not func:
                return ToolExecutionResult(
                    request_id=context.request_id,
                    tool_id=context.tool_id,
                    success=False,
                    error=f"Function not found for {context.tool_id}"
                )
            
            # Execute function with timeout
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await asyncio.wait_for(
                        func(**context.parameters),
                        timeout=tool.execution_timeout
                    )
                else:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(func, **context.parameters),
                        timeout=tool.execution_timeout
                    )
                
                return ToolExecutionResult(
                    request_id=context.request_id,
                    tool_id=context.tool_id,
                    success=True,
                    result=result
                )
                
            except asyncio.TimeoutError:
                return ToolExecutionResult(
                    request_id=context.request_id,
                    tool_id=context.tool_id,
                    success=False,
                    error=f"Tool execution timeout ({tool.execution_timeout}s)"
                )
                
        except Exception as e:
            return ToolExecutionResult(
                request_id=context.request_id,
                tool_id=context.tool_id,
                success=False,
                error=str(e)
            )
    
    def _generate_cache_key(self, context: ToolExecutionContext) -> str:
        """Generate cache key for result caching."""
        key_data = f"{context.tool_id}:{json.dumps(context.parameters, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()


class MCPServer:
    """Main MCP Server - clean, dynamic tool loading."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        """Initialize MCP server with dynamic tool loading."""
        self.host = host
        self.port = port
        
        # Initialize components
        self.tool_registry = MCPToolRegistry()
        self.security_manager = MCPSecurityManager()
        self.execution_engine = MCPExecutionEngine(self.tool_registry, self.security_manager)
        
        # Server state
        self.running = False
        self.connections = {}
        
        logger.info(f"🚀 MCP Server initialized with {len(self.tool_registry.tools)} tools")
        logger.info(f"📊 Tool categories: {self.tool_registry.get_tool_categories()}")
    
    async def start(self):
        """Start the MCP server."""
        self.running = True
        logger.info(f"🌟 MCP Server starting on {self.host}:{self.port}")
        logger.info("✅ MCP Server started successfully")
        
        # Log available tools
        logger.info("🔧 Available tools by category:")
        for category, count in self.tool_registry.get_tool_categories().items():
            logger.info(f"  {category}: {count} tools")
    
    async def stop(self):
        """Stop the MCP server."""
        self.running = False
        logger.info("🛑 MCP Server stopped")
    
    async def handle_tool_request(self, agent_id: str, tool_id: str, 
                                parameters: Dict[str, Any]) -> ToolExecutionResult:
        """Handle a tool execution request."""
        context = ToolExecutionContext(
            request_id=str(uuid.uuid4()),
            agent_id=agent_id,
            tool_id=tool_id,
            parameters=parameters,
            timestamp=datetime.now(),
            access_level=self._determine_access_level(tool_id)
        )
        
        result = await self.execution_engine.execute_tool(context)
        logger.info(f"Tool executed: {tool_id} by {agent_id} - Success: {result.success}")
        
        return result
    
    def _determine_access_level(self, tool_id: str) -> AccessLevel:
        """Determine access level for tool."""
        tool = self.tool_registry.get_tool(tool_id)
        return tool.access_level if tool else AccessLevel.PUBLIC
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information and statistics."""
        return {
            "server_name": "AI-Dev-Agent MCP Server",
            "version": "2.0.0",
            "status": "running" if self.running else "stopped",
            "host": self.host,
            "port": self.port,
            "tools_count": len(self.tool_registry.tools),
            "categories": self.tool_registry.get_tool_categories(),
            "security_enabled": True,
            "dynamic_loading": True
        }


def create_mcp_server(host: str = "localhost", port: int = 8765) -> MCPServer:
    """Factory function for creating MCP server."""
    return MCPServer(host=host, port=port)


def get_mcp_server() -> MCPServer:
    """Get singleton MCP server instance."""
    if not hasattr(get_mcp_server, '_instance'):
        get_mcp_server._instance = create_mcp_server()
    return get_mcp_server._instance
