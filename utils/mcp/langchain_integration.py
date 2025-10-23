#!/usr/bin/env python3
"""
LangChain-MCP Integration Layer
==============================

Integrates Model Context Protocol (MCP) with LangChain agents and tools.
Provides seamless tool access for LangChain agents through MCP server.

Features:
- MCPTool: LangChain tool wrapper for MCP tools
- MCPToolkit: Collection of MCP tools for agents
- MCPAgentMixin: Mixin for agents to use MCP tools
- Automatic tool discovery and registration
- Performance monitoring and caching
- Error handling and recovery

Architecture:
- LangChain Tool Interface ↔ MCP Client ↔ MCP Server ↔ Actual Tools
- Universal Agent Tracker integration for monitoring
- Async/sync compatibility for different LangChain versions

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 2)
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Type, Union, Callable
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# LangChain imports
try:
    from langchain.tools import BaseTool
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.schema import AgentAction, AgentFinish
    from langchain_core.tools import ToolException
    from langchain_core.callbacks import CallbackManagerForToolRun
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] LangChain not available: {e}")
    # Create minimal fallback classes
    class BaseTool:
        def __init__(self, **kwargs): pass
    class ToolException(Exception): pass
    class BaseModel: pass
    class CallbackManagerForToolRun: pass
    def Field(**kwargs): return None
    LANGCHAIN_AVAILABLE = False

# MCP imports
try:
    from .client import create_mcp_client, MCPClient, MCPClientConfig
    from .server import ToolDefinition, ToolExecutionResult, AccessLevel, ToolCategory
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] MCP components not available: {e}")
    MCP_AVAILABLE = False

# Universal Agent Tracker integration
try:
    from utils.system.universal_agent_tracker import get_universal_tracker
    UNIVERSAL_TRACKING_AVAILABLE = True
except ImportError:
    UNIVERSAL_TRACKING_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


class MCPToolInput(BaseModel):
    """Input schema for MCP tools."""
    parameters: Dict[str, Any] = Field(description="Tool parameters as key-value pairs")


class MCPTool(BaseTool):
    """
    LangChain tool wrapper for MCP tools.
    
    Bridges LangChain's tool interface with MCP tool execution.
    """
    
    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    args_schema: Type[BaseModel] = MCPToolInput
    
    def __init__(self, tool_definition: ToolDefinition, mcp_client: MCPClient, **kwargs):
        """
        Initialize MCP tool wrapper.
        
        Args:
            tool_definition: MCP tool definition
            mcp_client: MCP client instance
            **kwargs: Additional LangChain tool parameters
        """
        self.tool_definition = tool_definition
        self.mcp_client = mcp_client
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.last_execution_time = None
        
        # Set LangChain tool properties
        super().__init__(
            name=tool_definition.tool_id,
            description=tool_definition.description,
            **kwargs
        )
        
        logger.info(f"🔧 Created LangChain wrapper for MCP tool: {self.name}")
    
    def _run(
        self,
        parameters: Dict[str, Any],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """
        Synchronous tool execution (LangChain interface).
        
        Args:
            parameters: Tool parameters
            run_manager: LangChain callback manager
            
        Returns:
            Tool execution result as string
        """
        # Run async method in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._arun(parameters, run_manager))
            return result
        finally:
            loop.close()
    
    async def _arun(
        self,
        parameters: Dict[str, Any],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """
        Asynchronous tool execution (LangChain interface).
        
        Args:
            parameters: Tool parameters
            run_manager: LangChain callback manager
            
        Returns:
            Tool execution result as string
        """
        start_time = time.time()
        
        try:
            # Execute tool through MCP client
            result = await self.mcp_client.execute_tool(
                tool_id=self.tool_definition.tool_id,
                parameters=parameters,
                timeout=self.tool_definition.execution_timeout or 30
            )
            
            execution_time = time.time() - start_time
            
            # Update metrics
            self.execution_count += 1
            self.total_execution_time += execution_time
            self.last_execution_time = datetime.now()
            
            # Log execution
            logger.info(f"🔧 MCP tool '{self.name}' executed in {execution_time:.2f}s - Success: {result.success}")
            
            # Handle result
            if result.success:
                # Return formatted result
                if isinstance(result.result, dict):
                    return f"Tool execution successful. Result: {result.result}"
                else:
                    return str(result.result)
            else:
                # Raise LangChain tool exception
                raise ToolException(f"MCP tool execution failed: {result.error}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ MCP tool '{self.name}' failed after {execution_time:.2f}s: {e}")
            raise ToolException(f"MCP tool execution error: {str(e)}")
    
    def get_tool_metrics(self) -> Dict[str, Any]:
        """Get tool execution metrics."""
        avg_execution_time = (
            self.total_execution_time / self.execution_count 
            if self.execution_count > 0 else 0.0
        )
        
        return {
            "tool_id": self.tool_definition.tool_id,
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": avg_execution_time,
            "last_execution": self.last_execution_time.isoformat() if self.last_execution_time else None,
            "category": self.tool_definition.category.value if hasattr(self.tool_definition.category, 'value') else str(self.tool_definition.category),
            "access_level": self.tool_definition.access_level.value if hasattr(self.tool_definition.access_level, 'value') else str(self.tool_definition.access_level)
        }


class MCPToolkit:
    """
    Collection of MCP tools for LangChain agents.
    
    Manages tool discovery, registration, and lifecycle.
    """
    
    def __init__(self, agent_id: str, agent_type: str = "langchain_agent"):
        """
        Initialize MCP toolkit.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent using the toolkit
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.mcp_client: Optional[MCPClient] = None
        self.tools: List[MCPTool] = []
        self.tool_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Universal tracking
        self.universal_tracker = None
        if UNIVERSAL_TRACKING_AVAILABLE:
            try:
                self.universal_tracker = get_universal_tracker()
            except Exception as e:
                logger.warning(f"Universal tracking initialization failed: {e}")
        
        logger.info(f"🧰 MCP Toolkit initialized for agent: {agent_id}")
    
    async def initialize(self, auto_discover: bool = True) -> bool:
        """
        Initialize MCP client and discover tools.
        
        Args:
            auto_discover: Automatically discover available tools
            
        Returns:
            True if initialization successful
        """
        try:
            # Create MCP client
            self.mcp_client = create_mcp_client(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                auto_discover=auto_discover
            )
            
            # Start client
            await self.mcp_client.start()
            
            # Wait for connection
            await asyncio.sleep(1)
            
            # Discover and register tools
            if auto_discover:
                await self._discover_and_register_tools()
            
            # Track initialization
            if self.universal_tracker:
                try:
                    await self.universal_tracker.record_context_switch(
                        session_id=self.agent_id,
                        new_context="mcp_toolkit_initialized",
                        from_context="agent_setup",
                        trigger_type="mcp_integration",
                        trigger_details={
                            "tools_discovered": len(self.tools),
                            "agent_type": self.agent_type
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to track toolkit initialization: {e}")
            
            logger.info(f"✅ MCP Toolkit initialized with {len(self.tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"❌ MCP Toolkit initialization failed: {e}")
            return False
    
    async def _discover_and_register_tools(self):
        """Discover and register available MCP tools."""
        if not self.mcp_client:
            return
        
        # Get available tools from MCP client
        available_tools = self.mcp_client.get_available_tools()
        
        # Create LangChain tool wrappers
        for tool_def in available_tools:
            try:
                mcp_tool = MCPTool(tool_def, self.mcp_client)
                self.tools.append(mcp_tool)
                logger.info(f"🔧 Registered MCP tool: {tool_def.tool_id}")
            except Exception as e:
                logger.warning(f"Failed to register tool {tool_def.tool_id}: {e}")
        
        logger.info(f"🧰 Discovered and registered {len(self.tools)} MCP tools")
    
    def get_tools(self, category: Optional[ToolCategory] = None) -> List[MCPTool]:
        """
        Get tools, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of MCP tools
        """
        if category is None:
            return self.tools
        
        return [
            tool for tool in self.tools 
            if tool.tool_definition.category == category
        ]
    
    def get_tool_by_name(self, tool_name: str) -> Optional[MCPTool]:
        """Get tool by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def get_toolkit_metrics(self) -> Dict[str, Any]:
        """Get comprehensive toolkit metrics."""
        tool_metrics = {}
        total_executions = 0
        total_execution_time = 0.0
        
        for tool in self.tools:
            metrics = tool.get_tool_metrics()
            tool_metrics[tool.name] = metrics
            total_executions += metrics["execution_count"]
            total_execution_time += metrics["total_execution_time"]
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "total_tools": len(self.tools),
            "total_executions": total_executions,
            "total_execution_time": total_execution_time,
            "average_execution_time": (
                total_execution_time / total_executions 
                if total_executions > 0 else 0.0
            ),
            "tool_metrics": tool_metrics,
            "mcp_client_connected": (
                self.mcp_client is not None and 
                self.mcp_client._running
            )
        }
    
    async def shutdown(self):
        """Shutdown MCP toolkit and client."""
        if self.mcp_client:
            await self.mcp_client.stop()
        
        logger.info(f"🛑 MCP Toolkit shutdown for agent: {self.agent_id}")


class MCPAgentMixin:
    """
    Mixin class to add MCP tool capabilities to existing agents.
    
    Can be mixed into any agent class to provide MCP tool access.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize MCP capabilities."""
        super().__init__(*args, **kwargs)
        
        # Initialize MCP toolkit
        agent_id = getattr(self, 'config', {}).get('agent_id', 'unknown_agent')
        agent_type = getattr(self, 'config', {}).get('agent_type', 'mcp_enhanced_agent')
        
        self.mcp_toolkit = MCPToolkit(agent_id, agent_type)
        self.mcp_initialized = False
        
        logger.info(f"🔌 MCP capabilities added to agent: {agent_id}")
    
    async def initialize_mcp(self, auto_discover: bool = True) -> bool:
        """
        Initialize MCP toolkit for this agent.
        
        Args:
            auto_discover: Automatically discover available tools
            
        Returns:
            True if initialization successful
        """
        success = await self.mcp_toolkit.initialize(auto_discover)
        self.mcp_initialized = success
        
        if success:
            logger.info(f"✅ MCP initialized for agent with {len(self.mcp_toolkit.tools)} tools")
        else:
            logger.error("❌ MCP initialization failed")
        
        return success
    
    def get_mcp_tools(self, category: Optional[ToolCategory] = None) -> List[MCPTool]:
        """Get MCP tools for this agent."""
        if not self.mcp_initialized:
            logger.warning("MCP not initialized. Call initialize_mcp() first.")
            return []
        
        return self.mcp_toolkit.get_tools(category)
    
    def get_all_tools(self) -> List[Any]:
        """Get all tools (existing + MCP tools)."""
        tools = []
        
        # Add existing tools if available
        if hasattr(super(), 'get_tools'):
            tools.extend(super().get_tools())
        
        # Add MCP tools
        if self.mcp_initialized:
            tools.extend(self.mcp_toolkit.get_tools())
        
        return tools
    
    async def shutdown_mcp(self):
        """Shutdown MCP toolkit."""
        if hasattr(self, 'mcp_toolkit'):
            await self.mcp_toolkit.shutdown()


# Factory functions for easy integration
def create_mcp_toolkit(agent_id: str, agent_type: str = "langchain_agent") -> MCPToolkit:
    """Create MCP toolkit instance."""
    return MCPToolkit(agent_id, agent_type)


async def create_mcp_tools_for_agent(agent_id: str, agent_type: str = "langchain_agent") -> List[MCPTool]:
    """
    Create MCP tools for a LangChain agent.
    
    Args:
        agent_id: Agent identifier
        agent_type: Agent type
        
    Returns:
        List of MCP tools ready for LangChain use
    """
    toolkit = create_mcp_toolkit(agent_id, agent_type)
    
    if await toolkit.initialize():
        return toolkit.get_tools()
    else:
        logger.error("Failed to create MCP tools for agent")
        return []


# Compatibility check function
def check_langchain_mcp_compatibility() -> Dict[str, bool]:
    """Check compatibility of LangChain and MCP components."""
    return {
        "langchain_available": LANGCHAIN_AVAILABLE,
        "mcp_available": MCP_AVAILABLE,
        "universal_tracking_available": UNIVERSAL_TRACKING_AVAILABLE,
        "integration_ready": LANGCHAIN_AVAILABLE and MCP_AVAILABLE
    }


# Main execution for testing
if __name__ == "__main__":
    async def main():
        """Test LangChain-MCP integration."""
        print("🧪 Testing LangChain-MCP Integration...")
        
        # Check compatibility
        compatibility = check_langchain_mcp_compatibility()
        print(f"Compatibility: {compatibility}")
        
        if not compatibility["integration_ready"]:
            print("[ERROR] Integration not ready - missing components")
            return
        
        # Create toolkit
        toolkit = create_mcp_toolkit("test_langchain_agent", "integration_test")
        
        try:
            # Initialize toolkit
            success = await toolkit.initialize()
            if success:
                print(f"[OK] Toolkit initialized with {len(toolkit.tools)} tools")
                
                # Show metrics
                metrics = toolkit.get_toolkit_metrics()
                print(f"📊 Toolkit metrics: {metrics}")
            else:
                print("[ERROR] Toolkit initialization failed")
        
        finally:
            # Cleanup
            await toolkit.shutdown()
    
    # Run test
    asyncio.run(main())
