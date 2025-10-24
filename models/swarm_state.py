"""
Software Development Swarm State Models
========================================

State definitions for software development agent swarm.
Following LangGraph patterns with TypedDict and Annotated reducers.

Focus: Software Development Workflow
- Requirements → Architecture → Code → Tests → Review → Documentation
"""

from __future__ import annotations

from typing import TypedDict, Annotated, List, Dict, Any, Optional
import operator


# ============================================================================
# SOFTWARE DEVELOPMENT SWARM STATE
# ============================================================================

class SoftwareDevSwarmState(TypedDict):
    """
    State for software development agent swarm.
    
    **Development Flow**:
    Requirements → Architecture → Code → Tests → Review → Security → Documentation
    
    **Agent Outputs**:
    Each specialist agent has dedicated field(s) to prevent data conflicts.
    
    **Supervisor Control**:
    Complexity analysis and agent routing managed by supervisor nodes.
    """
    
    # ========================================================================
    # INPUT & CONTEXT
    # ========================================================================
    project_context: str                    # Project description and requirements
    project_complexity: str                 # simple, medium, complex (set by analyzer)
    user_preferences: Dict[str, Any]        # User preferences for tech stack, style, etc.
    
    # ========================================================================
    # ROUTING & COORDINATION (Supervisor Layer)
    # ========================================================================
    required_agents: List[str]              # Which agents to run (set by selector)
    next_agent: str                         # Which agent runs next (set by router)
    current_step: str                       # Current workflow step name
    workflow_phase: str                     # analysis, design, implementation, testing, review
    
    # ========================================================================
    # MESSAGES (Accumulated with operator.add)
    # ========================================================================
    messages: Annotated[List[Dict[str, Any]], operator.add]  # Agent communications
    
    # ========================================================================
    # SPECIALIST AGENT OUTPUTS (Each agent has dedicated fields)
    # ========================================================================
    
    # Requirements Analyst Output
    requirements: Dict[str, Any]            # Detailed requirements specification
    requirements_metadata: Dict[str, Any]   # User stories, acceptance criteria, constraints
    
    # Architecture Designer Output
    architecture: Dict[str, Any]            # System architecture design
    architecture_diagrams: Dict[str, Any]   # Component diagrams, data flow
    tech_stack: Dict[str, Any]             # Technology choices and justifications
    
    # Code Generator Output
    code_files: Dict[str, Any]             # Generated source code files
    code_structure: Dict[str, Any]         # Project structure and organization
    dependencies: Dict[str, Any]            # Dependencies (requirements.txt, package.json, etc.)
    build_config: Dict[str, Any]           # Build configuration files
    
    # Test Generator Output
    test_files: Dict[str, Any]             # Generated test files
    test_coverage_plan: Dict[str, Any]     # Test coverage strategy
    test_data: Dict[str, Any]              # Test fixtures and mock data
    
    # Code Reviewer Output
    code_review: Dict[str, Any]            # Code review findings and feedback
    review_suggestions: Dict[str, Any]     # Specific improvement suggestions
    quality_metrics: Dict[str, Any]        # Code quality scores and metrics
    refactoring_needed: List[str]          # Areas requiring refactoring
    
    # Security Analyst Output (Optional - for complex projects)
    security_analysis: Dict[str, Any]      # Security vulnerability assessment
    security_recommendations: Dict[str, Any]  # Security hardening recommendations
    compliance_check: Dict[str, Any]       # Compliance with security standards
    
    # Documentation Generator Output
    documentation: Dict[str, Any]          # README, design docs, architecture docs
    api_documentation: Dict[str, Any]      # API reference documentation
    user_guide: Dict[str, Any]             # User guides and tutorials
    developer_guide: Dict[str, Any]        # Setup and contribution guide
    
    # ========================================================================
    # PROJECT ARTIFACTS (Compiled Results)
    # ========================================================================
    final_codebase: Dict[str, Any]         # Complete codebase ready for deployment
    deployment_instructions: Dict[str, Any]  # How to deploy and run the project
    project_summary: Dict[str, Any]        # Executive summary of the project
    
    # ========================================================================
    # TRACKING & MONITORING
    # ========================================================================
    completed_agents: Annotated[List[str], operator.add]  # Successfully completed agents
    failed_agents: Annotated[List[str], operator.add]     # Failed agents
    errors: Annotated[List[str], operator.add]            # Error messages
    warnings: Annotated[List[str], operator.add]          # Warning messages
    
    # Performance metrics
    agent_execution_times: Dict[str, float]  # Execution time per agent (seconds)
    total_tokens_used: int                   # Total LLM tokens consumed
    
    # Workflow control
    should_continue: bool                    # Whether workflow should continue
    iteration_count: int                     # Current iteration number
    max_iterations_reached: bool             # Safety limit check
    human_feedback_needed: bool              # Whether to pause for human input


# ============================================================================
# STATE INITIALIZATION HELPERS
# ============================================================================

def create_initial_software_dev_state(
    project_context: str,
    user_preferences: Optional[Dict[str, Any]] = None
) -> SoftwareDevSwarmState:
    """
    Create initial software development swarm state with all fields initialized.
    
    Args:
        project_context: Project description and requirements
        user_preferences: Optional user preferences (tech stack, coding style, etc.)
    
    Returns:
        Fully initialized SoftwareDevSwarmState
    """
    return {
        # Input & Context
        "project_context": project_context,
        "project_complexity": "medium",
        "user_preferences": user_preferences or {},
        
        # Routing & Coordination
        "required_agents": [],
        "next_agent": "",
        "current_step": "start",
        "workflow_phase": "analysis",
        
        # Messages
        "messages": [],
        
        # Specialist Agent Outputs
        "requirements": {},
        "requirements_metadata": {},
        "architecture": {},
        "architecture_diagrams": {},
        "tech_stack": {},
        "code_files": {},
        "code_structure": {},
        "dependencies": {},
        "build_config": {},
        "test_files": {},
        "test_coverage_plan": {},
        "test_data": {},
        "code_review": {},
        "review_suggestions": {},
        "quality_metrics": {},
        "refactoring_needed": [],
        "security_analysis": {},
        "security_recommendations": {},
        "compliance_check": {},
        "documentation": {},
        "api_documentation": {},
        "user_guide": {},
        "developer_guide": {},
        
        # Project Artifacts
        "final_codebase": {},
        "deployment_instructions": {},
        "project_summary": {},
        
        # Tracking & Monitoring
        "completed_agents": [],
        "failed_agents": [],
        "errors": [],
        "warnings": [],
        "agent_execution_times": {},
        "total_tokens_used": 0,
        "should_continue": True,
        "iteration_count": 0,
        "max_iterations_reached": False,
        "human_feedback_needed": False,
    }


def get_software_dev_agent_fields() -> Dict[str, List[str]]:
    """
    Get mapping of software development agent names to their output field names.
    
    This ensures each agent writes to dedicated fields without conflicts.
    
    Returns:
        Dictionary mapping agent names to list of state fields they write to
    """
    return {
        "requirements_analyst": [
            "requirements",
            "requirements_metadata"
        ],
        "architecture_designer": [
            "architecture",
            "architecture_diagrams",
            "tech_stack"
        ],
        "code_generator": [
            "code_files",
            "code_structure",
            "dependencies",
            "build_config"
        ],
        "test_generator": [
            "test_files",
            "test_coverage_plan",
            "test_data"
        ],
        "code_reviewer": [
            "code_review",
            "review_suggestions",
            "quality_metrics",
            "refactoring_needed"
        ],
        "security_analyst": [
            "security_analysis",
            "security_recommendations",
            "compliance_check"
        ],
        "documentation_generator": [
            "documentation",
            "api_documentation",
            "user_guide",
            "developer_guide"
        ],
    }


# Alias for backward compatibility
SwarmState = SoftwareDevSwarmState
create_initial_swarm_state = create_initial_software_dev_state

