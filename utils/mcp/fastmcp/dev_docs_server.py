"""
Development MCP Server: dev_docs (FastMCP)
=========================================

Documentation and link-integrity tools for development agents.

Transport:
- streamable-http (HTTP) at /mcp

Port:
- 8104

Tools (wrapping existing internal MCP tools):
- link.scan_all
- link.validate
- link.generate_report
- link.heal (requires explicit human approval in agent layer; exposed for manual testing)
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

mcp = FastMCP("dev_docs")


@mcp.tool(name="link.scan_all")
def link_scan_all(target_directory: str = "."):
    from utils.mcp.tools.link_integrity_tools import scan_all_links

    return scan_all_links(target_directory=target_directory)


@mcp.tool(name="link.validate")
def link_validate(target_directory: str = "."):
    from utils.mcp.tools.link_integrity_tools import validate_all_links

    return validate_all_links(target_directory=target_directory)


@mcp.tool(name="link.generate_report")
def link_generate_report(target_directory: str = ".", output_path: str | None = None):
    from utils.mcp.tools.link_integrity_tools import generate_link_report

    return generate_link_report(target_directory=target_directory, output_path=output_path)


@mcp.tool(name="link.heal")
def link_heal(rename_mapping: dict[str, str], target_directory: str = "."):
    """
    Heal links after file renames.

    Notes:
    - This is a write operation (edits files). In agent workflows it MUST be HITL-gated.
    - Exposed here so you can manually test the server end-to-end in a notebook.
    """
    from utils.mcp.tools.link_integrity_tools import heal_links_after_rename

    return heal_links_after_rename(rename_mapping=rename_mapping, target_directory=target_directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Development MCP server: dev_docs")
    parser.add_argument(
        "--transport",
        choices=["streamable-http", "stdio"],
        default="streamable-http",
        help="Transport protocol to use.",
    )
    parser.add_argument("--port", type=int, default=8104, help="Port for streamable-http transport.")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio", show_banner=False)
    else:
        mcp.run(transport="streamable-http", port=args.port, show_banner=False)


