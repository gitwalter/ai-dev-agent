#!/usr/bin/env python3
"""
MCP Tool Decorator
==================

Decorator for registering MCP tools with metadata.
Automatically extracts parameter schema from function signature.

Usage:
    @mcp_tool("tool.id", "Description", AccessLevel.PUBLIC, ToolCategory.AI)
    def my_tool(param1: str, param2: int = 5) -> Dict[str, Any]:
        ...

Created: 2025-10-10
"""

import inspect
from typing import Any, Callable, Dict, Optional, get_type_hints
from functools import wraps
from dataclasses import dataclass
from enum import Enum


# Re-export enums from server to avoid circular imports
class AccessLevel(Enum):
    """Security access levels for MCP tools."""
    PUBLIC = "public"
    UNRESTRICTED = "unrestricted"  # Alias for PUBLIC
    RESTRICTED = "restricted"
    PRIVILEGED = "privileged"


class ToolCategory(Enum):
    """Tool categories for organization."""
    AGILE_MANAGEMENT = "agile_management"
    AGILE = "agile_management"  # Alias
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    RAG = "rag"
    WEB_RESEARCH = "web_research"
    CLOUD_STORAGE = "cloud_storage"
    GIT = "git"
    TESTING = "testing"
    AI = "ai"
    SYSTEM = "system"


@dataclass
class ToolDefinition:
    """Definition of an MCP tool."""
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    access_level: AccessLevel
    source_module: str
    function_name: str
    parameters_schema: Dict[str, Any]
    returns_schema: Dict[str, Any]
    execution_timeout: int = 30
    cache_ttl: int = 0
    requires_confirmation: bool = False


def _extract_parameter_schema(func: Callable) -> Dict[str, Any]:
    """
    Extract parameter schema from function signature.
    
    Returns flat schema: {"param": {"type": "...", "required": bool, "default": ...}}
    """
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    schema = {}
    
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue
            
        param_schema = {}
        
        # Get type
        if param_name in type_hints:
            py_type = type_hints[param_name]
            # Convert Python types to JSON schema types
            if py_type == str or py_type == 'str':
                param_schema['type'] = 'string'
            elif py_type == int or py_type == 'int':
                param_schema['type'] = 'integer'
            elif py_type == float or py_type == 'float':
                param_schema['type'] = 'number'
            elif py_type == bool or py_type == 'bool':
                param_schema['type'] = 'boolean'
            elif hasattr(py_type, '__origin__'):
                # Handle Optional, List, Dict, etc.
                origin = getattr(py_type, '__origin__', None)
                if origin is list:
                    param_schema['type'] = 'array'
                elif origin is dict:
                    param_schema['type'] = 'object'
                else:
                    param_schema['type'] = 'string'  # Default
            else:
                param_schema['type'] = 'string'  # Default
        else:
            param_schema['type'] = 'string'  # Default
        
        # Check if required
        if param.default == inspect.Parameter.empty:
            param_schema['required'] = True
        else:
            param_schema['required'] = False
            param_schema['default'] = param.default
        
        schema[param_name] = param_schema
    
    return schema


def mcp_tool(
    tool_id: str,
    description: str,
    access_level: AccessLevel = AccessLevel.PUBLIC,
    category: ToolCategory = ToolCategory.AI,
    execution_timeout: int = 30,
    cache_ttl: int = 0,
    requires_confirmation: bool = False
):
    """
    Decorator to register a function as an MCP tool.
    
    Args:
        tool_id: Unique tool identifier (e.g., "file.read")
        description: Human-readable description
        access_level: Security access level
        category: Tool category
        execution_timeout: Execution timeout in seconds
        cache_ttl: Cache time-to-live in seconds (0 = no cache)
        requires_confirmation: Whether tool requires user confirmation
    
    Example:
        @mcp_tool("file.read", "Read file contents", AccessLevel.PUBLIC, ToolCategory.FILE_SYSTEM)
        def read_file(file_path: str, max_size_mb: int = 10) -> Dict[str, Any]:
            return {"content": "..."}
    """
    def decorator(func: Callable) -> Callable:
        # Extract parameter schema from function signature
        parameters_schema = _extract_parameter_schema(func)
        
        # Create tool definition
        tool_def = ToolDefinition(
            tool_id=tool_id,
            name=tool_id.replace(".", " ").title(),  # "file.read" -> "File Read"
            description=description,
            category=category,
            access_level=access_level,
            source_module=func.__module__,
            function_name=func.__name__,
            parameters_schema=parameters_schema,
            returns_schema={"type": "object"},  # Generic return schema
            execution_timeout=execution_timeout,
            cache_ttl=cache_ttl,
            requires_confirmation=requires_confirmation
        )
        
        # Attach tool definition to function
        func._mcp_tool_definition = tool_def
        func._mcp_tool_id = tool_id
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Copy attributes to wrapper
        wrapper._mcp_tool_definition = tool_def
        wrapper._mcp_tool_id = tool_id
        
        return wrapper
    
    return decorator


def get_all_mcp_tools_from_module(module) -> Dict[str, tuple]:
    """
    Extract all MCP tools from a module.
    
    Returns:
        Dict[tool_id, (function, ToolDefinition)]
    """
    tools = {}
    
    for name in dir(module):
        obj = getattr(module, name)
        if callable(obj) and hasattr(obj, '_mcp_tool_definition'):
            tool_def = obj._mcp_tool_definition
            tools[tool_def.tool_id] = (obj, tool_def)
    
    return tools

