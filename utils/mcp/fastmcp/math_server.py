"""
math_server.py

This module defines simple math-related tools that can be served using the FastMCP framework.
It provides basic operations such as addition and multiplication, accessible via the MCP server.
"""

from fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")