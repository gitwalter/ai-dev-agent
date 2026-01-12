"""LangGraph MCP Agent - LangChain 1.x compatible MCP tool integration.

This module provides a clean integration between FastMCP servers and LangGraph agents.
Inspired by DeepMCPAgent but rewritten for LangChain 1.x / LangGraph 1.x compatibility.

Usage:
    from utils.mcp.langgraph_mcp_agent import build_mcp_agent, MCPServerConfig

    servers = {
        "dev_repo": MCPServerConfig(url="http://127.0.0.1:8100/mcp"),
    }
    
    graph, loader = await build_mcp_agent(
        servers=servers,
        model=llm,
        instructions="You are a helpful assistant."
    )
    
    result = await graph.ainvoke({"messages": [{"role": "user", "content": "..."}]})
"""
from __future__ import annotations

import contextlib
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal, cast

from fastmcp import Client as FastMCPClient
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain.agents import create_agent
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, create_model


# =============================================================================
# Configuration Models
# =============================================================================

class MCPServerConfig(BaseModel):
    """Configuration for an MCP server connection.
    
    Attributes:
        url: Full endpoint URL for the MCP server (e.g., http://127.0.0.1:8000/mcp)
        transport: The transport mechanism ("http", "streamable-http", or "sse")
        headers: Optional request headers (e.g., Authorization tokens)
    """
    model_config = ConfigDict(extra="forbid")
    
    url: str
    transport: Literal["http", "streamable-http", "sse"] = "streamable-http"
    headers: dict[str, str] = Field(default_factory=dict)


# =============================================================================
# Tool Discovery and Conversion
# =============================================================================

@dataclass(frozen=True)
class ToolInfo:
    """Human-friendly metadata for a discovered MCP tool."""
    server_name: str
    name: str
    description: str
    input_schema: dict[str, Any]


class MCPClientError(RuntimeError):
    """Raised when communicating with the MCP client fails."""
    pass


# Callback types for tracing tool calls
OnBefore = Callable[[str, dict[str, Any]], None]
OnAfter = Callable[[str, Any], None]
OnError = Callable[[str, Exception], None]


def _clean_schema(schema: dict[str, Any] | None) -> dict[str, Any]:
    """Recursively clean JSON Schema to remove None values and fix compatibility.
    
    This is essential for Gemini/Google GenAI which fails if schema contains:
    - null values (like pattern: None or default: None)
    - anyOf with null type (common in MCP tools for optional parameters)
    
    Args:
        schema: Raw JSON schema from MCP tool
        
    Returns:
        Cleaned schema with None values removed and anyOf simplified
    """
    if schema is None:
        return {}
    if not isinstance(schema, dict):
        return schema  # type: ignore
    
    cleaned: dict[str, Any] = {}
    for key, value in schema.items():
        # Skip None values entirely - Gemini doesn't handle them
        if value is None:
            continue
        
        # Handle anyOf with null type - simplify to non-null type
        if key == "anyOf" and isinstance(value, list):
            non_null_types = [
                item for item in value
                if isinstance(item, dict) and item.get("type") != "null"
            ]
            if len(non_null_types) == 1:
                # Replace anyOf with the single non-null type's properties
                cleaned.update(_clean_schema(non_null_types[0]))
            elif non_null_types:
                # Keep anyOf but without null types
                cleaned[key] = [_clean_schema(item) for item in non_null_types]
            # If no non-null types, skip entirely
            continue
        
        # Recursively clean nested dicts
        if isinstance(value, dict):
            cleaned_value = _clean_schema(value)
            if cleaned_value:  # Only add non-empty dicts
                cleaned[key] = cleaned_value
        # Recursively clean lists
        elif isinstance(value, list):
            cleaned_list = [
                _clean_schema(item) if isinstance(item, dict) else item
                for item in value
                if item is not None
            ]
            if cleaned_list:
                cleaned[key] = cleaned_list
        else:
            cleaned[key] = value
    return cleaned


def _jsonschema_to_pydantic(
    schema: dict[str, Any],
    *,
    model_name: str = "Args"
) -> type[BaseModel]:
    """Convert JSON Schema to a Pydantic model for tool arguments.
    
    Args:
        schema: JSON Schema dict with 'properties' and 'required' keys
        model_name: Name for the generated Pydantic model
        
    Returns:
        A dynamically created Pydantic model class
    """
    # Clean schema to remove None values that break Gemini
    clean = _clean_schema(schema)
    props = clean.get("properties", {}) or {}
    required = set(clean.get("required", []) or [])
    
    def field_spec(name: str, prop: dict[str, Any]) -> tuple[type[Any], Any]:
        """Convert a single JSON Schema property to a Pydantic field."""
        # Handle type - may be direct or from anyOf
        t = prop.get("type")
        
        # If no direct type, check if we have anyOf (already cleaned by _clean_schema)
        if t is None and "anyOf" not in prop:
            # The property was simplified from anyOf to direct type
            t = prop.get("type")
        
        desc = prop.get("description")
        default = prop.get("default")
        is_required = name in required
        
        # Don't use None as default for Pydantic - causes schema issues with Gemini
        # Use special marker instead
        if default is None and not is_required:
            default = ""  # Use empty string as default for optional string fields
        
        def default_val() -> Any:
            if is_required:
                return ...
            return default if default is not None else ""
        
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        py_type = type_mapping.get(t, str)  # Default to str instead of Any
        return (py_type, Field(default_val(), description=desc))
    
    fields: dict[str, tuple[type[Any], Any]] = {
        name: field_spec(name, spec or {})
        for name, spec in props.items()
    } or {"payload": (dict, Field(None, description="Raw payload"))}
    
    # Sanitize model name for Python identifier
    safe_name = re.sub(r"[^0-9a-zA-Z_]", "_", model_name) or "Args"
    
    model = create_model(safe_name, **cast(dict[str, Any], fields))
    return cast(type[BaseModel], model)


class _FastMCPTool(BaseTool):
    """LangChain BaseTool wrapper that invokes a FastMCP tool by name.
    
    This tool wrapper creates a fresh connection for each invocation,
    which is essential for HTTP/SSE transport in async contexts.
    """
    name: str
    description: str
    args_schema: type[BaseModel]
    
    _tool_name: str = PrivateAttr()
    _server_config: dict[str, Any] = PrivateAttr()
    _on_before: OnBefore | None = PrivateAttr(default=None)
    _on_after: OnAfter | None = PrivateAttr(default=None)
    _on_error: OnError | None = PrivateAttr(default=None)
    
    def __init__(
        self,
        *,
        name: str,
        description: str,
        args_schema: type[BaseModel],
        tool_name: str,
        server_config: dict[str, Any],
        on_before: OnBefore | None = None,
        on_after: OnAfter | None = None,
        on_error: OnError | None = None,
    ) -> None:
        super().__init__(name=name, description=description, args_schema=args_schema)
        self._tool_name = tool_name
        self._server_config = server_config
        self._on_before = on_before
        self._on_after = on_after
        self._on_error = on_error
    
    async def _arun(self, **kwargs: Any) -> Any:
        """Asynchronously execute the MCP tool via FastMCP client.
        
        Creates a fresh client connection for each invocation to avoid
        stale connection issues with HTTP/SSE transport.
        """
        if self._on_before:
            with contextlib.suppress(Exception):
                self._on_before(self.name, kwargs)
        
        try:
            # Create fresh client for each call
            client = FastMCPClient({"mcpServers": self._server_config})
            async with client:
                res = await client.call_tool(self._tool_name, kwargs)
        except Exception as exc:
            if self._on_error:
                with contextlib.suppress(Exception):
                    self._on_error(self.name, exc)
            raise MCPClientError(
                f"Failed to call MCP tool '{self._tool_name}': {exc}"
            ) from exc
        
        if self._on_after:
            with contextlib.suppress(Exception):
                self._on_after(self.name, res)
        
        return res
    
    def _run(self, **kwargs: Any) -> Any:
        """Synchronous execution path (uses anyio for sync-to-async bridge)."""
        import anyio
        return anyio.from_thread.run(self._arun, **kwargs)


class MCPToolLoader:
    """Discover MCP tools from FastMCP servers and convert to LangChain tools.
    
    This loader handles:
    - Connecting to multiple MCP servers
    - Discovering available tools
    - Converting JSON Schema to Pydantic models
    - Creating LangChain-compatible BaseTool instances
    """
    
    def __init__(
        self,
        servers: Mapping[str, MCPServerConfig],
        *,
        on_before: OnBefore | None = None,
        on_after: OnAfter | None = None,
        on_error: OnError | None = None,
    ) -> None:
        """Initialize the tool loader.
        
        Args:
            servers: Mapping of server name to configuration
            on_before: Optional callback before tool invocation
            on_after: Optional callback after tool invocation
            on_error: Optional callback on tool error
        """
        self._servers = servers
        self._on_before = on_before
        self._on_after = on_after
        self._on_error = on_error
        self._mcp_config = self._build_mcp_config()
    
    def _build_mcp_config(self) -> dict[str, dict[str, Any]]:
        """Build FastMCP configuration dict from server specs."""
        cfg: dict[str, dict[str, Any]] = {}
        for name, spec in self._servers.items():
            entry: dict[str, Any] = {
                "transport": spec.transport,
                "url": spec.url,
            }
            if spec.headers:
                entry["headers"] = spec.headers
            cfg[name] = entry
        return cfg
    
    async def _list_tools_raw(self) -> list[Any]:
        """Fetch raw tool descriptors from all configured MCP servers."""
        client = FastMCPClient({"mcpServers": self._mcp_config})
        try:
            async with client:
                tools = await client.list_tools()
        except Exception as exc:
            raise MCPClientError(
                f"Failed to list tools from MCP servers: {exc}. "
                "Check server URLs and network connectivity."
            ) from exc
        return list(tools or [])
    
    async def get_all_tools(self) -> list[BaseTool]:
        """Return all available tools as LangChain BaseTool instances.
        
        Returns:
            List of BaseTool instances ready for use with LangGraph agents
        """
        tools_raw = await self._list_tools_raw()
        out: list[BaseTool] = []
        
        for t in tools_raw:
            name = t.name
            desc = getattr(t, "description", "") or ""
            schema = getattr(t, "inputSchema", None) or {}
            
            # Convert JSON Schema to Pydantic model
            model = _jsonschema_to_pydantic(schema, model_name=f"Args_{name}")
            
            out.append(
                _FastMCPTool(
                    name=name,
                    description=desc,
                    args_schema=model,
                    tool_name=name,
                    server_config=self._mcp_config,
                    on_before=self._on_before,
                    on_after=self._on_after,
                    on_error=self._on_error,
                )
            )
        
        return out
    
    async def list_tool_info(self) -> list[ToolInfo]:
        """Return human-readable tool metadata for introspection.
        
        Returns:
            List of ToolInfo dataclass instances
        """
        tools_raw = await self._list_tools_raw()
        return [
            ToolInfo(
                server_name=getattr(t, "server", "") or getattr(t, "serverName", "") or "",
                name=t.name,
                description=getattr(t, "description", "") or "",
                input_schema=getattr(t, "inputSchema", None) or {},
            )
            for t in tools_raw
        ]


# =============================================================================
# Agent Builder
# =============================================================================

async def build_mcp_agent(
    *,
    servers: Mapping[str, MCPServerConfig],
    model: BaseChatModel | Runnable[Any, Any],
    instructions: str | None = None,
    trace_tools: bool = False,
) -> tuple[Runnable[Any, Any], MCPToolLoader]:
    """Build a LangGraph ReAct agent with MCP tools.
    
    This function:
    1. Discovers tools from the configured MCP servers
    2. Converts them into LangChain tools
    3. Creates a LangGraph ReAct agent
    
    Args:
        servers: Mapping of server name to MCPServerConfig
        model: LangChain chat model or Runnable
        instructions: Optional system prompt for the agent
        trace_tools: If True, print each tool invocation and result
        
    Returns:
        Tuple of (graph, loader) where:
        - graph is a LangGraph runnable with .ainvoke()
        - loader can be used to introspect tools
        
    Example:
        servers = {"dev_repo": MCPServerConfig(url="http://127.0.0.1:8100/mcp")}
        graph, loader = await build_mcp_agent(servers=servers, model=llm)
        result = await graph.ainvoke({"messages": [...]})
    """
    
    # Tracing callbacks
    def _before(name: str, kwargs: dict[str, Any]) -> None:
        if trace_tools:
            print(f"[TOOL] Invoking: {name} with {kwargs}")
    
    def _after(name: str, res: Any) -> None:
        if not trace_tools:
            return
        # Try to extract a readable result
        pretty = res
        for attr in ("data", "text", "content", "result"):
            try:
                val = getattr(res, attr, None)
                if val not in (None, ""):
                    pretty = val
                    break
            except Exception:
                continue
        print(f"[TOOL] Result from {name}: {pretty}")
    
    def _error(name: str, exc: Exception) -> None:
        if trace_tools:
            print(f"[TOOL] Error in {name}: {exc}")
    
    # Create loader and discover tools
    loader = MCPToolLoader(
        servers,
        on_before=_before if trace_tools else None,
        on_after=_after if trace_tools else None,
        on_error=_error if trace_tools else None,
    )
    
    try:
        tools = await loader.get_all_tools()
    except MCPClientError as exc:
        raise RuntimeError(
            f"Failed to initialize agent - tool discovery failed: {exc}"
        ) from exc
    
    if not tools:
        print("[WARNING] No tools discovered from MCP servers; agent will run without tools.")
    
    # Build agent using LangChain v1 create_agent (replaces langgraph create_react_agent)
    kwargs: dict[str, Any] = {"model": model, "tools": tools}
    
    if instructions:
        kwargs["system_prompt"] = instructions
    
    graph = cast(Runnable[Any, Any], create_agent(**kwargs))
    
    return graph, loader
