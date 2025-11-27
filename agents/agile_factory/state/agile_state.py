"""
State schema for Agile Factory LangGraph workflow.

This defines the complete state structure for the workflow, including:
- Input data (user story, project type)
- Agent outputs (requirements, architecture, code, reviews, tests, docs)
- Feedback loop control (iteration counters, max iterations)
- HITL state (approvals, feedback, current checkpoint)
- Control fields (status, errors, thread_id, current_node)
"""

try:d
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict  # Python 3.12+
from typing import Dict, Any, List, Optional


class AgileFactoryState(TypedDict, total=False):
    """
    Complete state for Agile Factory workflow.
    
    This state is used throughout the LangGraph workflow to pass data
    between nodes and maintain conversation context via checkpointers.
    """
    
    # ========================================================================
    # INPUT DATA
    # ========================================================================
    user_story: str                    # Raw user story text
    project_type: str                  # "website" or "streamlit_app"
    
    # ========================================================================
    # AGENT OUTPUTS
    # ========================================================================
    requirements: Dict[str, Any]       # From requirements_analyst
    architecture: Dict[str, Any]       # From architecture_designer
    code_files: Dict[str, str]         # From code_generator (path → content)
    code_review: Dict[str, Any]        # From code_reviewer
    test_files: Dict[str, str]         # From testing_agent (path → content)
    test_results: Dict[str, Any]       # From testing_agent (execution results)
    documentation_files: Dict[str, str] # From documentation_generator
    
    # ========================================================================
    # FEEDBACK LOOP CONTROL
    # ========================================================================
    code_review_iteration_count: int   # Iterations for code_reviewer ↔ coder loop
    test_iteration_count: int          # Iterations for testing_agent ↔ coder loop
    max_iterations: int                # Safety limit (default: 2)
    review_rigidity: float             # Code review strictness: 0.0 (skip/very lenient) to 1.0 (very strict), default: 0.3
    skip_code_review: bool             # Skip code review entirely if True, default: False
    
    # ========================================================================
    # HITL STATE
    # ========================================================================
    hitl_approvals: Dict[str, bool]    # Track approvals at each checkpoint
    hitl_feedback: Dict[str, str]      # Store feedback at each checkpoint
    current_checkpoint: str            # Current HITL checkpoint name
    
    # ========================================================================
    # WORKSPACE LOCATIONS
    # ========================================================================
    workspace_locations: Dict[str, str]  # Track where files are stored (for debugging)
    
    # ========================================================================
    # CONTROL FIELDS
    # ========================================================================
    status: str                        # "processing", "complete", "error", "needs_revision"
    errors: List[str]                  # List of error messages
    thread_id: str                     # For checkpointer persistence
    current_node: str                  # Track current workflow node
    llm_model: str                     # LLM model to use: "gemini-2.5-flash" or "gemini-2.5-flash-lite" (default: flash-lite)

