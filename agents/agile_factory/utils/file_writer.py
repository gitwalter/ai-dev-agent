"""
File Writing Utility for Agile Factory Workflow.

This module provides deterministic file writing from state without LLM calls.
Files are written programmatically after agents produce structured output.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional
from agents.agile_factory.state.agile_state import AgileFactoryState

logger = logging.getLogger(__name__)


def sanitize_file_path(file_path: str) -> Optional[str]:
    """
    Sanitize file path to ensure it's safe for writing.
    
    Args:
        file_path: Original file path (may be relative or absolute)
        
    Returns:
        Sanitized relative path, or None if invalid
    """
    if not file_path or not isinstance(file_path, str):
        return None
    
    # Remove leading slashes and dots
    cleaned = file_path.strip().lstrip("./\\")
    
    # Remove any absolute path components
    if ":" in cleaned and cleaned[1] == ":":
        # Windows absolute path (C:\...)
        cleaned = "/".join(cleaned.split("\\")[1:])
    
    # Remove any remaining absolute path markers
    cleaned = cleaned.lstrip("/")
    
    # Replace backslashes with forward slashes
    cleaned = cleaned.replace("\\", "/")
    
    # Remove any dangerous path components
    dangerous = ["..", "~", "//"]
    for danger in dangerous:
        if danger in cleaned:
            logger.warning(f"Removed dangerous path component: {danger}")
            cleaned = cleaned.replace(danger, "")
    
    # Remove any non-printable characters
    cleaned = re.sub(r'[^\x20-\x7E/]', '', cleaned)
    
    # Ensure path is not empty
    if not cleaned or cleaned == "/":
        return None
    
    return cleaned


def write_state_files_to_disk(
    state: AgileFactoryState,
    output_dir: Path,
    file_type: str = "code_files",
    subdirectory: Optional[str] = None
) -> Dict[str, Path]:
    """
    Write files from state to disk WITHOUT LLM calls.
    
    This is called AFTER each agent completes to persist file content
    that was generated as structured output (JSON) in the state.
    
    Args:
        state: Current workflow state containing file content
        output_dir: Base directory for writing files
        file_type: State field name containing files dict ("code_files" or "documentation_files")
        subdirectory: Optional subdirectory within output_dir (e.g., "code", "docs")
        
    Returns:
        Dictionary mapping original file paths to written file paths
    """
    files_dict = state.get(file_type, {})
    
    if not files_dict:
        logger.info(f"No {file_type} found in state - skipping file write")
        return {}
    
    # Determine target directory
    if subdirectory:
        target_dir = output_dir / subdirectory
    else:
        target_dir = output_dir
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    written_files = {}
    errors = []
    
    logger.info(f"Writing {len(files_dict)} files from {file_type} to {target_dir}")
    
    for file_path, content in files_dict.items():
        try:
            # Sanitize path
            safe_path = sanitize_file_path(file_path)
            if not safe_path:
                logger.warning(f"Invalid file path skipped: {file_path[:100]}")
                errors.append(f"Invalid path: {file_path}")
                continue
            
            # Resolve full path
            full_path = target_dir / safe_path
            
            # Ensure parent directories exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file (deterministic, no LLM)
            if not isinstance(content, str):
                # Convert to string if needed
                content = str(content)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            written_files[file_path] = full_path
            logger.info(f"[OK] Wrote {file_path} -> {full_path.relative_to(output_dir)} ({len(content)} bytes)")
            
        except Exception as e:
            error_msg = f"Failed to write {file_path}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    if errors:
        logger.warning(f"File writing completed with {len(errors)} errors out of {len(files_dict)} files")
        # Add errors to state
        if "errors" not in state:
            state["errors"] = []
        state["errors"].extend(errors)
    else:
        logger.info(f"[OK] Successfully wrote {len(written_files)}/{len(files_dict)} files")
    
    return written_files


def get_workspace_dir(state: AgileFactoryState, node_type: str = "code") -> Path:
    """
    Get workspace directory for a specific node type.
    
    Args:
        state: Current workflow state
        node_type: Type of node ("code", "docs", "tests")
        
    Returns:
        Path to workspace directory
    """
    project_root = Path(__file__).parent.parent.parent.parent
    thread_id = state.get("thread_id", "default")
    
    workspace_map = {
        "code": f"code_gen_{thread_id}",
        "docs": f"doc_gen_{thread_id}",
        "tests": f"test_gen_{thread_id}"
    }
    
    workspace_name = workspace_map.get(node_type, f"{node_type}_{thread_id}")
    workspace_dir = project_root / "agile_factory_workspace" / workspace_name
    
    return workspace_dir


