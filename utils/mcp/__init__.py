"""
MCP (Model Context Protocol) Integration Module
==============================================

This module provides Model Context Protocol integration for AI-Dev-Agent,
enabling agents to access external tools through standardized interfaces.

Components:
- server.py: Core MCP server implementation
- client.py: MCP client library (Phase 1)
- tool_registry.py: Tool registration system (Phase 1)
- security.py: Security and access control (Phase 1)

Features:
- 47 tools across 6 categories (Agile, Database, File, Git, Testing, AI)
- 3-tier security access control (Public/Restricted/Privileged)
- Universal Agent Tracker integration
- RAG-enhanced intelligent tool routing (Phase 2)
- Performance monitoring and caching

Usage:
    from utils.mcp.server import create_mcp_server
    
    # Create and start MCP server
    server = create_mcp_server()
    await server.start()

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 1)
"""

from .server import MCPServer, create_mcp_server, ToolDefinition, AccessLevel, ToolCategory

__version__ = "1.0.0"
__author__ = "AI Development Agent"

# Export main classes and functions
__all__ = [
    "MCPServer",
    "create_mcp_server", 
    "ToolDefinition",
    "AccessLevel",
    "ToolCategory"
]
