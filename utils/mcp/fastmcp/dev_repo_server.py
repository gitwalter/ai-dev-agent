"""
Development MCP Server: dev_repo (FastMCP)
=========================================

Read-only repository inspection tools for development agents.

Transport:
- streamable-http (HTTP) at /mcp

Port:
- 8100

Tools (wrapping existing internal MCP tools):
- file.list_directory
- file.read
- file.search_content
- file.get_info
- file.exists
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fastmcp import FastMCP

# Ensure the project root is on sys.path when running as a script (stdio transport).
# Otherwise `import utils...` fails because the script lives under utils/mcp/fastmcp/.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


mcp = FastMCP("dev_repo")


@mcp.tool(name="file.list_directory")
def file_list_directory(directory: str = ".", pattern: str | None = None, recursive: bool = False):
    from utils.mcp.tools.file_access_tools import list_directory_mcp

    return list_directory_mcp(directory=directory, pattern=pattern, recursive=recursive)


@mcp.tool(name="file.read")
def file_read(file_path: str, start_line: int | None = None, end_line: int | None = None, max_size_mb: int = 10):
    from utils.mcp.tools.file_access_tools import read_file_mcp

    return read_file_mcp(
        file_path=file_path,
        start_line=start_line,
        end_line=end_line,
        max_size_mb=max_size_mb,
    )


@mcp.tool(name="file.search_content")
def file_search_content(query: str, directory: str = ".", file_pattern: str | None = None, max_results: int = 20):
    from utils.mcp.tools.file_access_tools import search_content_mcp

    return search_content_mcp(
        search_text=query,
        directory=directory,
        file_pattern=file_pattern or "*.py",
        max_results=max_results,
    )


@mcp.tool(name="file.get_info")
def file_get_info(file_path: str):
    from utils.mcp.tools.file_access_tools import get_file_info_mcp

    return get_file_info_mcp(file_path=file_path)


@mcp.tool(name="file.exists")
def file_exists(file_path: str):
    from utils.mcp.tools.file_access_tools import file_exists_mcp

    return file_exists_mcp(file_path=file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Development MCP server: dev_repo")
    parser.add_argument(
        "--transport",
        choices=["streamable-http", "stdio"],
        default="streamable-http",
        help="Transport protocol to use.",
    )
    parser.add_argument("--port", type=int, default=8100, help="Port for streamable-http transport.")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio", show_banner=False)
    else:
        # FastMCP uses "/mcp" by default for streamable-http transport.
        mcp.run(transport="streamable-http", port=args.port, show_banner=False)


