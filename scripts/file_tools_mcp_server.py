#!/usr/bin/env python3
"""
File Tools MCP Server
=====================

Simple MCP server that provides file system tools for the file organizer agent.
Follows the official MCP documentation pattern using FastMCP.

Run with: python scripts/file_tools_mcp_server.py
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
from typing import Optional
import json

# Initialize FastMCP server
mcp = FastMCP("FileTools")


@mcp.tool()
def list_directory(directory_path: str) -> str:
    """
    List all files in a directory.
    
    Args:
        directory_path: Path to directory to list
        
    Returns:
        JSON string with file information
    """
    try:
        path = Path(directory_path)
        
        if not path.exists():
            return json.dumps({"error": f"Directory not found: {directory_path}"})
        
        if not path.is_dir():
            return json.dumps({"error": f"Not a directory: {directory_path}"})
        
        files = []
        for item in path.iterdir():
            if item.is_file():
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "extension": item.suffix,
                    "size": item.stat().st_size
                })
        
        return json.dumps({
            "directory": directory_path,
            "file_count": len(files),
            "files": files
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def read_file(file_path: str, max_lines: Optional[int] = None) -> str:
    """
    Read contents of a text file.
    
    Args:
        file_path: Path to file to read
        max_lines: Optional maximum number of lines to read
        
    Returns:
        File contents or error message
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return json.dumps({"error": f"File not found: {file_path}"})
        
        if not path.is_file():
            return json.dumps({"error": f"Not a file: {file_path}"})
        
        with open(path, 'r', encoding='utf-8') as f:
            if max_lines:
                lines = [f.readline() for _ in range(max_lines)]
                content = ''.join(lines)
            else:
                content = f.read()
        
        return json.dumps({
            "file": file_path,
            "size": path.stat().st_size,
            "content": content,
            "lines_read": len(content.split('\n')) if content else 0
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_file_info(file_path: str) -> str:
    """
    Get information about a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        JSON string with file metadata
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return json.dumps({"error": f"Path not found: {file_path}"})
        
        stat = path.stat()
        
        return json.dumps({
            "path": str(path),
            "name": path.name,
            "extension": path.suffix,
            "size": stat.st_size,
            "is_file": path.is_file(),
            "is_directory": path.is_dir(),
            "created": stat.st_ctime,
            "modified": stat.st_mtime
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def analyze_directory_structure(directory_path: str) -> str:
    """
    Analyze directory structure and file types.
    
    Args:
        directory_path: Path to directory to analyze
        
    Returns:
        JSON string with analysis results
    """
    try:
        path = Path(directory_path)
        
        if not path.exists():
            return json.dumps({"error": f"Directory not found: {directory_path}"})
        
        if not path.is_dir():
            return json.dumps({"error": f"Not a directory: {directory_path}"})
        
        # Analyze file types
        file_types = {}
        total_size = 0
        file_count = 0
        
        for item in path.iterdir():
            if item.is_file():
                ext = item.suffix.lower() or "no_extension"
                size = item.stat().st_size
                
                if ext not in file_types:
                    file_types[ext] = {"count": 0, "total_size": 0, "files": []}
                
                file_types[ext]["count"] += 1
                file_types[ext]["total_size"] += size
                file_types[ext]["files"].append(item.name)
                
                total_size += size
                file_count += 1
        
        return json.dumps({
            "directory": directory_path,
            "total_files": file_count,
            "total_size": total_size,
            "file_types": file_types,
            "analysis": {
                "unique_extensions": len(file_types),
                "avg_file_size": total_size / file_count if file_count > 0 else 0
            }
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    # Run server with Streamable HTTP transport (required for langchain-mcp-adapters)
    print("=" * 50)
    print("Starting File Tools MCP Server...")
    print("Server will run on http://localhost:8000/mcp")
    print("Tools available:")
    print("  - list_directory")
    print("  - read_file") 
    print("  - get_file_info")
    print("  - analyze_directory_structure")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Use FastMCP's built-in server for streamable-http
    # This properly sets up the MCP protocol endpoints
    mcp.run(transport="streamable-http")

