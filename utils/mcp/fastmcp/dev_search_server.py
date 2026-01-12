"""
Development MCP Server: dev_search (FastMCP)
===========================================

Repository search tools for development agents.

Transport:
- streamable-http (HTTP) at /mcp

Port:
- 8101

Tools (v1):
- file.search_content (baseline grep-like search via existing tool)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fastmcp import FastMCP

# Ensure the project root is on sys.path when running as a script (stdio transport).
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

mcp = FastMCP("dev_search")


@mcp.tool(name="file.search_content")
def file_search_content(query: str, directory: str = ".", file_pattern: str | None = None, max_results: int = 50):
    from utils.mcp.tools.file_access_tools import search_content_mcp

    return search_content_mcp(
        search_text=query,
        directory=directory,
        file_pattern=file_pattern or "*.py",
        max_results=max_results,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Development MCP server: dev_search")
    parser.add_argument(
        "--transport",
        choices=["streamable-http", "stdio"],
        default="streamable-http",
        help="Transport protocol to use.",
    )
    parser.add_argument("--port", type=int, default=8101, help="Port for streamable-http transport.")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio", show_banner=False)
    else:
        mcp.run(transport="streamable-http", port=args.port, show_banner=False)


