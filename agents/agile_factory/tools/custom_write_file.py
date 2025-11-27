"""
Custom write_file tool for Agile Factory.

This tool writes files directly to the specified workspace directory,
ensuring files are always accessible even if DeepAgents uses a different location.
"""

import logging
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


def create_write_file_tool(workspace_dir: Path):
    """
    Create a write_file tool that writes to a specific workspace directory.
    
    Args:
        workspace_dir: Directory where files should be written
        
    Returns:
        LangChain tool for writing files
    """
    workspace_dir = Path(workspace_dir)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    @tool
    def write_file(file_path: str, content: str) -> str:
        """
        Write content to a file in the workspace directory.
        
        This tool creates files in the workspace directory. Use this to create
        all code files, configuration files, and documentation files.
        
        Args:
            file_path: Relative path to the file (e.g., "app.py", "index.html", "src/utils.py")
            content: Content to write to the file
            
        Returns:
            Success message with file path
        """
        try:
            # Resolve file path relative to workspace
            target_file = workspace_dir / file_path
            
            # Ensure parent directory exists
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"write_file: Created {target_file} ({len(content)} bytes)")
            
            return f"Successfully wrote file: {file_path} ({len(content)} bytes)"
            
        except Exception as e:
            error_msg = f"Failed to write file {file_path}: {str(e)}"
            logger.error(f"write_file error: {error_msg}")
            return error_msg
    
    # Update tool metadata
    write_file.name = "write_file"
    write_file.description = f"""Write content to a file in the workspace directory ({workspace_dir}).

Use this tool to create all code files, configuration files, and documentation files.
Files will be written to: {workspace_dir}

Example usage:
- write_file("app.py", "# Python code here")
- write_file("index.html", "<html>...</html>")
- write_file("src/utils.py", "def helper(): pass")
"""
    
    return write_file

