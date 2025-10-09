"""
MCP-Enhanced Agents
==================

Agents with Model Context Protocol (MCP) integration for enhanced tool access.

This module contains agents that demonstrate and utilize the MCP integration
with LangChain, providing seamless access to all MCP tools through the
standard LangChain agent interface.

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 2)
"""

from .mcp_enhanced_agent import MCPEnhancedAgent, create_mcp_enhanced_agent

__all__ = ['MCPEnhancedAgent', 'create_mcp_enhanced_agent']
