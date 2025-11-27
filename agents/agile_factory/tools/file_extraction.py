"""
File extraction utilities for DeepAgents workspace.

DeepAgents stores files in its workspace directory when using write_file tool.
This module provides utilities to extract files from the workspace after
agent execution.
"""

import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def extract_files_from_deep_agent_workspace(agent=None, workspace_path: Optional[str] = None) -> Dict[str, str]:
    """
    Extract files from DeepAgents workspace.
    
    DeepAgents stores files in a workspace directory when using write_file tool.
    This function reads all files from the workspace and returns them as a dictionary.
    
    Args:
        agent: DeepAgent instance (may have workspace attribute) - optional if workspace_path provided
        workspace_path: Optional explicit workspace path (takes precedence)
        
    Returns:
        Dictionary mapping file paths (relative to workspace) to file contents
    """
    files = {}
    
    try:
        # Try to get workspace from agent if workspace_path not provided
        if workspace_path is None and agent is not None:
            if hasattr(agent, 'workspace'):
                workspace_path = agent.workspace
                logger.debug(f"Found workspace from agent.workspace: {workspace_path}")
            elif hasattr(agent, 'filesystem_middleware'):
                # DeepAgents may store workspace in filesystem middleware
                middleware = agent.filesystem_middleware
                if hasattr(middleware, 'workspace'):
                    workspace_path = middleware.workspace
                    logger.debug(f"Found workspace from filesystem_middleware.workspace: {workspace_path}")
                elif hasattr(middleware, 'base_path'):
                    workspace_path = middleware.base_path
                    logger.debug(f"Found workspace from filesystem_middleware.base_path: {workspace_path}")
        
        if workspace_path is None:
            logger.warning("Could not determine DeepAgents workspace path")
            return files
        
        # Convert to Path object
        workspace = Path(workspace_path)
        
        # Resolve absolute path
        if not workspace.is_absolute():
            workspace = workspace.resolve()
        
        logger.debug(f"Extracting files from workspace: {workspace}")
        
        if not workspace.exists():
            logger.warning(f"Workspace path does not exist: {workspace}")
            return files
        
        if not workspace.is_dir():
            logger.warning(f"Workspace path is not a directory: {workspace}")
            return files
        
        # Walk through workspace directory
        for root, dirs, filenames in os.walk(workspace):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in filenames:
                # Skip hidden files
                if filename.startswith('.'):
                    continue
                
                file_path = Path(root) / filename
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Store relative path
                    relative_path = file_path.relative_to(workspace)
                    files[str(relative_path)] = content
                    
                except UnicodeDecodeError:
                    # Skip binary files
                    logger.debug(f"Skipping binary file: {file_path}")
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {e}")
        
        logger.info(f"Extracted {len(files)} files from DeepAgents workspace")
        
    except Exception as e:
        logger.error(f"Error extracting files from workspace: {e}")
    
    return files


def extract_files_from_directory(directory_path: str, extensions: Optional[list] = None) -> Dict[str, str]:
    """
    Extract files from a directory (fallback method).
    
    Args:
        directory_path: Path to directory
        extensions: Optional list of file extensions to include (e.g., ['.py', '.html'])
        
    Returns:
        Dictionary mapping file paths to file contents
    """
    files = {}
    directory = Path(directory_path)
    
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory_path}")
        return files
    
    try:
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                # Filter by extension if specified
                if extensions and file_path.suffix not in extensions:
                    continue
                
                # Skip hidden files
                if file_path.name.startswith('.'):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    relative_path = file_path.relative_to(directory)
                    files[str(relative_path)] = content
                    
                except UnicodeDecodeError:
                    logger.debug(f"Skipping binary file: {file_path}")
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {e}")
        
        logger.info(f"Extracted {len(files)} files from directory")
        
    except Exception as e:
        logger.error(f"Error extracting files from directory: {e}")
    
    return files

