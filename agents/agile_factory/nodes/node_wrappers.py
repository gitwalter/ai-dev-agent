"""
Node Wrappers for Automatic File Writing.

These wrappers automatically write files to disk after each agent node completes,
eliminating the need for LLM tool calls for file writing operations.
"""

import logging
from agents.agile_factory.state.agile_state import AgileFactoryState
from agents.agile_factory.utils.file_writer import write_state_files_to_disk, get_workspace_dir
from agents.agile_factory.nodes.code_generator_node import code_generator_node
from agents.agile_factory.nodes.documentation_node import documentation_node
from agents.agile_factory.nodes.testing_node import testing_node

logger = logging.getLogger(__name__)


def code_generator_node_with_auto_write(state: AgileFactoryState) -> dict:
    """
    Code Generator Node wrapper with automatic file writing.
    
    This wrapper:
    1. Calls code_generator_node to generate files (structured JSON output)
    2. Automatically writes files from state.code_files to disk (NO LLM calls)
    3. Returns updates dict (LangGraph pattern)
    
    Args:
        state: Current workflow state
        
    Returns:
        Updates dict with files written to disk
    """
    # Step 1: Generate code files (structured JSON output, NO tool calls)
    logger.info("Step 1: Generating code files via structured JSON output...")
    updates = code_generator_node(state)
    
    # Merge updates into state for file writing
    merged_state = {**state, **updates}
    
    # Step 2: Write files programmatically (NO LLM calls)
    code_files = updates.get("code_files", {})
    if code_files:
        logger.info(f"Step 2: Writing {len(code_files)} code files to disk (programmatic, NO LLM)...")
        workspace_dir = get_workspace_dir(merged_state, "code")
        written_files = write_state_files_to_disk(
            merged_state,
            workspace_dir,
            file_type="code_files",
            subdirectory=None
        )
        
        if written_files:
            logger.info(f"[OK] Successfully wrote {len(written_files)} code files to {workspace_dir}")
            # Update workspace locations in updates dict
            if "workspace_locations" not in updates:
                updates["workspace_locations"] = state.get("workspace_locations", {}).copy()
            updates["workspace_locations"]["code_files_written_to"] = str(workspace_dir)
        else:
            logger.warning("No files were written to disk")
    else:
        logger.warning("No code files in updates to write")
    
    return updates


def documentation_node_with_auto_write(state: AgileFactoryState) -> dict:
    """
    Documentation Generator Node wrapper with automatic file writing.
    
    This wrapper:
    1. Calls documentation_node to generate files (structured JSON output)
    2. Automatically writes files from state.documentation_files to disk (NO LLM calls)
    3. Returns updates dict (LangGraph pattern)
    
    Args:
        state: Current workflow state
        
    Returns:
        Updates dict with files written to disk
    """
    # Step 1: Generate documentation files (structured JSON output, NO tool calls)
    logger.info("Step 1: Generating documentation files via structured JSON output...")
    updates = documentation_node(state)
    
    # Merge updates into state for file writing
    merged_state = {**state, **updates}
    
    # Step 2: Write files programmatically (NO LLM calls)
    documentation_files = updates.get("documentation_files", {})
    if documentation_files:
        logger.info(f"Step 2: Writing {len(documentation_files)} documentation files to disk (programmatic, NO LLM)...")
        workspace_dir = get_workspace_dir(merged_state, "docs")
        written_files = write_state_files_to_disk(
            merged_state,
            workspace_dir,
            file_type="documentation_files",
            subdirectory=None
        )
        
        if written_files:
            logger.info(f"[OK] Successfully wrote {len(written_files)} documentation files to {workspace_dir}")
            # Update workspace locations in updates dict
            if "workspace_locations" not in updates:
                updates["workspace_locations"] = state.get("workspace_locations", {}).copy()
            updates["workspace_locations"]["documentation_files_written_to"] = str(workspace_dir)
        else:
            logger.warning("No files were written to disk")
    else:
        logger.warning("No documentation files in updates to write")
    
    return updates


def testing_node_with_auto_write(state: AgileFactoryState) -> dict:
    """
    Testing Agent Node wrapper with automatic file writing.
    
    This wrapper:
    1. Calls testing_node to generate test files (structured JSON output)
    2. Automatically writes files from state.test_files to disk (NO LLM calls)
    3. Returns updates dict (LangGraph pattern)
    
    Args:
        state: Current workflow state
        
    Returns:
        Updates dict with files written to disk
    """
    # Step 1: Generate test files (structured JSON output, NO tool calls)
    logger.info("Step 1: Generating test files via structured JSON output...")
    updates = testing_node(state)
    
    # Merge updates into state for file writing
    merged_state = {**state, **updates}
    
    # Step 2: Write files programmatically (NO LLM calls)
    test_files = updates.get("test_files", {})
    if test_files:
        logger.info(f"Step 2: Writing {len(test_files)} test files to disk (programmatic, NO LLM)...")
        workspace_dir = get_workspace_dir(merged_state, "tests")
        written_files = write_state_files_to_disk(
            merged_state,
            workspace_dir,
            file_type="test_files",
            subdirectory=None
        )
        
        if written_files:
            logger.info(f"[OK] Successfully wrote {len(written_files)} test files to {workspace_dir}")
            # Update workspace locations in updates dict
            if "workspace_locations" not in updates:
                updates["workspace_locations"] = state.get("workspace_locations", {}).copy()
            updates["workspace_locations"]["test_files_written_to"] = str(workspace_dir)
        else:
            logger.warning("No files were written to disk")
    else:
        logger.warning("No test files in updates to write")
    
    return updates

