"""
Workspace location utilities for finding generated code files.

Helps locate where DeepAgents stores files after code generation.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def find_code_generation_workspaces(project_root: Optional[Path] = None) -> Dict[str, List[str]]:
    """
    Find all possible workspace locations where code files might be stored.
    
    Args:
        project_root: Project root directory (defaults to current working directory)
        
    Returns:
        Dictionary mapping workspace type to list of paths
    """
    if project_root is None:
        project_root = Path.cwd()
    
    workspaces = {
        "dedicated_workspace": [],
        "agile_workspace": [],
        "deepagents_workspace": [],
        "current_directory": []
    }
    
    # Check dedicated agile_factory_workspace
    dedicated_ws = project_root / "agile_factory_workspace"
    if dedicated_ws.exists():
        for subdir in dedicated_ws.iterdir():
            if subdir.is_dir():
                workspaces["dedicated_workspace"].append(str(subdir))
    
    # Check agile_workspace (from agile_swarm_agent)
    agile_ws = project_root / "agile_workspace"
    if agile_ws.exists():
        workspaces["agile_workspace"].append(str(agile_ws))
        # Check subdirectories
        for item in agile_ws.iterdir():
            if item.is_dir():
                workspaces["agile_workspace"].append(str(item))
    
    # Check DeepAgents default locations
    deepagents_locations = [
        project_root / ".deepagents" / "workspace",
        Path.home() / ".deepagents" / "workspace",
        Path.cwd() / ".deepagents" / "workspace"
    ]
    
    for location in deepagents_locations:
        if location.exists():
            workspaces["deepagents_workspace"].append(str(location))
            # Check subdirectories
            if location.is_dir():
                for item in location.iterdir():
                    if item.is_dir():
                        workspaces["deepagents_workspace"].append(str(item))
    
    # Check current directory for any code files
    code_extensions = ['.py', '.html', '.css', '.js', '.json', '.txt', '.md']
    for file_path in project_root.rglob('*'):
        if file_path.is_file() and file_path.suffix in code_extensions:
            # Skip files in known directories (agents/, tests/, etc.)
            parts = file_path.parts
            if 'agents' not in parts and 'tests' not in parts and 'docs' not in parts:
                parent = str(file_path.parent)
                if parent not in workspaces["current_directory"]:
                    workspaces["current_directory"].append(parent)
    
    return workspaces


def list_files_in_workspace(workspace_path: str) -> List[Dict[str, str]]:
    """
    List all files in a workspace directory.
    
    Args:
        workspace_path: Path to workspace directory
        
    Returns:
        List of dictionaries with file information
    """
    files = []
    workspace = Path(workspace_path)
    
    if not workspace.exists() or not workspace.is_dir():
        return files
    
    try:
        for file_path in workspace.rglob('*'):
            if file_path.is_file():
                # Skip hidden files
                if file_path.name.startswith('.'):
                    continue
                
                try:
                    # Get file size
                    size = file_path.stat().st_size
                    files.append({
                        "path": str(file_path.relative_to(workspace)),
                        "full_path": str(file_path),
                        "size": size,
                        "extension": file_path.suffix
                    })
                except Exception as e:
                    logger.debug(f"Error getting file info for {file_path}: {e}")
    except Exception as e:
        logger.error(f"Error listing workspace {workspace_path}: {e}")
    
    return files


def get_workspace_info(thread_id: Optional[str] = None) -> Dict[str, any]:
    """
    Get comprehensive workspace information for a specific thread or all workspaces.
    
    Args:
        thread_id: Optional thread ID to filter workspaces
        
    Returns:
        Dictionary with workspace information
    """
    project_root = Path(__file__).parent.parent.parent.parent
    
    info = {
        "project_root": str(project_root),
        "workspaces": find_code_generation_workspaces(project_root),
        "files_by_workspace": {}
    }
    
    # List files in each workspace
    for ws_type, paths in info["workspaces"].items():
        info["files_by_workspace"][ws_type] = {}
        for path in paths:
            if thread_id is None or thread_id in path:
                files = list_files_in_workspace(path)
                if files:
                    info["files_by_workspace"][ws_type][path] = files
    
    return info

