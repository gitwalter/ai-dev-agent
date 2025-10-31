#!/usr/bin/env python3
"""
RAG-Enhanced Development Workflow App
======================================

Streamlit app for testing RAG-integrated development agents.

Features:
- Agent proactively asks for guidelines/documents
- Interactive document selection
- RAG-enhanced architecture design
- Human-in-the-loop decision points
"""

import sys
from pathlib import Path
import asyncio
import streamlit as st

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Initialize page config
st.set_page_config(
    page_title="RAG-Enhanced Development",
    page_icon="🛠️",
    layout="wide"
)

# Apply custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #1f77b4;
}
.sync-point {
    background-color: #f0f8ff;
    border-left: 4px solid #1f77b4;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0.25rem;
}
.agent-message {
    background-color: #e8f4f8;
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 0.5rem 0;
}
.human-response {
    background-color: #f0f0f0;
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 0.5rem 0;
}
.source-badge {
    display: inline-block;
    background-color: #4CAF50;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    margin: 0.25rem;
    font-size: 0.875rem;
}
</style>
""", unsafe_allow_html=True)


def main():
    """Main app entry point."""
    
    st.markdown('<div class="main-header">🛠️ RAG-Enhanced Development Workflow</div>', unsafe_allow_html=True)
    
    st.markdown("""
    **Test the RAG-integrated development workflow where agents proactively ask for guidelines.**
    
    This app demonstrates:
    - ✅ Agent asks proactively: "Which guidelines should I follow?"
    - ✅ You specify documents/frameworks
    - ✅ Agent retrieves relevant context using RAG
    - ✅ Agent generates architecture aligned with your standards
    """)
    
    # Initialize session state
    if 'stage' not in st.session_state:
        st.session_state.stage = 'task_input'
        st.session_state.task = ""
        st.session_state.user_story = ""
        st.session_state.guidelines_prompt = ""
        st.session_state.user_guidelines = ""
        st.session_state.loaded_sources = {}
        st.session_state.architecture_proposal = ""
        st.session_state.sources_used = []
    
    # Sidebar: Progress & Active Sources
    with st.sidebar:
        st.header("📊 Progress")
        
        stages = {
            'task_input': '1️⃣ Task Definition',
            'guideline_selection': '2️⃣ Guideline Selection',
            'architecture_design': '3️⃣ Architecture Design',
            'review': '4️⃣ Review & Refine'
        }
        
        for stage_id, stage_name in stages.items():
            if st.session_state.stage == stage_id:
                st.markdown(f"**▶️ {stage_name}**")
            else:
                st.markdown(f"⚪ {stage_name}")
        
        st.markdown("---")
        
        st.header("📚 Active Sources")
        if st.session_state.loaded_sources:
            for category, sources in st.session_state.loaded_sources.items():
                st.markdown(f"**{category}**")
                for source in sources:
                    st.markdown(f"- {source.get('source', 'Unknown')}")
        else:
            st.info("No sources loaded yet")
        
        st.markdown("---")
        
        if st.button("🔄 Reset Workflow"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main workflow stages
    if st.session_state.stage == 'task_input':
        show_task_input_stage()
    elif st.session_state.stage == 'guideline_selection':
        show_guideline_selection_stage()
    elif st.session_state.stage == 'architecture_design':
        show_architecture_design_stage()
    elif st.session_state.stage == 'review':
        show_review_stage()


def show_task_input_stage():
    """Stage 1: Define the development task."""
    st.markdown('<div class="sync-point">', unsafe_allow_html=True)
    st.markdown("### 🎯 STAGE 1: Define Your Development Task")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("**What are we building?**")
    
    task = st.text_area(
        "Task Description",
        value=st.session_state.task,
        height=100,
        help="Describe what you want to build",
        placeholder="Example: Design architecture for a user authentication system with JWT tokens and role-based access control"
    )
    
    user_story = st.text_input(
        "User Story ID (optional)",
        value=st.session_state.user_story,
        help="E.g., US-DEV-001",
        placeholder="US-DEV-001"
    )
    
    if st.button("▶️ Start Development", type="primary", disabled=not task):
        st.session_state.task = task
        st.session_state.user_story = user_story
        st.session_state.stage = 'guideline_selection'
        st.rerun()


def show_guideline_selection_stage():
    """Stage 2: Agent asks for guidelines proactively."""
    st.markdown('<div class="sync-point">', unsafe_allow_html=True)
    st.markdown("### 🤝 STAGE 2: Guideline Selection (Agent Asks You)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.info("🤖 **The Architecture Designer agent is asking you proactively:**")
    
    # Generate agent's prompt (simulate)
    if not st.session_state.guidelines_prompt:
        from workflow.knowledge_source_manager import DocumentSelectionPrompt
        
        st.session_state.guidelines_prompt = DocumentSelectionPrompt.generate_selection_prompt(
            task_description=st.session_state.task,
            agent_role="architecture_designer"
        )
    
    # Display agent's question
    st.markdown('<div class="agent-message">', unsafe_allow_html=True)
    st.markdown(st.session_state.guidelines_prompt)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 💬 Your Response:")
    
    # Quick selection options
    st.markdown("**Quick Options:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Use Defaults"):
            st.session_state.user_guidelines = "use defaults"
    
    with col2:
        if st.button("📐 Architecture + Agile"):
            st.session_state.user_guidelines = """
Please use:
- docs/architecture/ (all architecture documents)
- docs/agile/sprints/sprint_6/user_stories/US-DEV-001.md
- docs/guides/python_standards.md
"""
    
    with col3:
        if st.button("📚 Full Context"):
            st.session_state.user_guidelines = """
Please use:
- docs/architecture/ (architecture guidelines)
- docs/agile/ (sprint and user story context)
- docs/guides/ (coding standards)
- https://python.langchain.com/docs/ (LangChain framework docs)
"""
    
    # Custom response
    user_response = st.text_area(
        "Or specify custom documents/guidelines:",
        value=st.session_state.user_guidelines,
        height=150,
        help="Specify file paths, URLs, or say 'use defaults'",
        placeholder="""Examples:
- Use defaults
- docs/architecture/onion_architecture.md
- docs/agile/sprints/sprint_6/user_stories/US-DEV-001.md
- https://python.langchain.com/docs/
"""
    )
    
    if st.button("✅ Submit Guidelines", type="primary", disabled=not user_response):
        st.session_state.user_guidelines = user_response
        
        # Simulate loading sources
        with st.spinner("📚 Loading documents..."):
            # In real implementation, this would call knowledge_manager
            st.session_state.loaded_sources = {
                "architecture": [{"source": "docs/architecture/*.md", "count": 15}],
                "agile": [{"source": "docs/agile/sprints/sprint_6/*.md", "count": 8}],
                "coding_guidelines": [{"source": "docs/guides/*.md", "count": 5}]
            }
            st.success("✅ Documents loaded successfully!")
        
        st.session_state.stage = 'architecture_design'
        st.rerun()


def show_architecture_design_stage():
    """Stage 3: Agent designs architecture using RAG."""
    st.markdown('<div class="sync-point">', unsafe_allow_html=True)
    st.markdown("### 🏗️ STAGE 3: Architecture Design (RAG-Enhanced)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.info("🤖 **The Architecture Designer is working...**")
    
    with st.spinner("🧠 Retrieving relevant architecture patterns from your documents..."):
        # Simulate RAG retrieval
        import time
        time.sleep(1)
        
        st.markdown("**📚 Retrieved Guidelines:**")
        st.markdown("""
        - Onion Architecture pattern (from docs/architecture/onion_architecture.md)
        - Security best practices (from docs/guides/security_guidelines.md)
        - LangChain integration patterns (from docs/guides/langchain_patterns.md)
        """)
    
    with st.spinner("🎨 Generating architecture proposal..."):
        time.sleep(1.5)
        
        # Simulate architecture generation
        if not st.session_state.architecture_proposal:
            st.session_state.architecture_proposal = f"""
# Architecture Proposal: {st.session_state.task}

## Overview
Based on the project's **Onion Architecture** pattern and security guidelines, I propose a layered authentication system.

## Architecture Components

### 1. Core Domain Layer (Inner)
**Location**: `models/auth/`
- `User` entity
- `Role` entity  
- `Permission` value objects

**Rationale**: Following onion architecture, domain entities are at the center, independent of external concerns.

### 2. Application Layer
**Location**: `utils/auth/`
- `TokenManager` service - JWT token generation/validation
- `PasswordHasher` service - Secure password hashing (bcrypt)
- `RoleValidator` service - Role-based access control logic

**Rationale**: Application layer contains business logic, referencing domain but not infrastructure.

### 3. Infrastructure Layer (Outer)
**Location**: `agents/security/`
- `AuthMiddleware` - HTTP middleware for authentication
- `SessionStore` - Session persistence (Redis/SQLite)
- `AuditLogger` - Security event logging

**Rationale**: Infrastructure concerns are external, can be swapped without affecting core logic.

## Key Design Decisions

### ✅ Decision 1: JWT Token Strategy
**Choice**: Stateless JWT tokens with refresh token rotation
**Rationale**: 
- Aligns with LangChain's stateless agent patterns (from docs/guides/langchain_patterns.md)
- Reduces database load
- Supports distributed deployment

**Source**: `docs/guides/security_guidelines.md` - "Prefer stateless authentication for scalability"

### ✅ Decision 2: Role-Based Access Control (RBAC)
**Choice**: Hierarchical roles with permission inheritance
**Rationale**:
- Flexible and extensible
- Follows security best practices
- Easy to audit

**Source**: `docs/architecture/security_patterns.md` - "Use RBAC for fine-grained access control"

### ✅ Decision 3: Middleware Pattern
**Choice**: Authentication as LangGraph-compatible middleware
**Rationale**:
- Integrates with existing LangGraph workflows
- Separates auth concerns from agent logic
- Reusable across all agents

**Source**: `docs/guides/langchain_patterns.md` - "Use middleware for cross-cutting concerns"

## Scalability Considerations
- Stateless tokens enable horizontal scaling
- Redis session store for shared state
- Async/await for non-blocking operations

## Security Features
✅ Password hashing with bcrypt (cost factor: 12)
✅ JWT token expiration (15min access, 7day refresh)
✅ CSRF protection via SameSite cookies
✅ Audit logging for all auth events
✅ Rate limiting on auth endpoints

## Testing Strategy
- Unit tests for each service (TokenManager, PasswordHasher, etc.)
- Integration tests for complete auth flow
- Security tests for common vulnerabilities (SQL injection, XSS)

## Dependencies
- `python-jose[cryptography]` - JWT handling
- `passlib[bcrypt]` - Password hashing
- `redis` - Session storage (optional)

## Alignment with User Story
{f"✅ Addresses acceptance criteria in {st.session_state.user_story}" if st.session_state.user_story else "N/A"}

## Sources Referenced
- docs/architecture/onion_architecture.md (architectural pattern)
- docs/guides/security_guidelines.md (security requirements)
- docs/guides/langchain_patterns.md (LangChain integration)
- docs/agile/sprints/sprint_6/user_stories/{st.session_state.user_story}.md (requirements)
"""
        
        st.markdown('<div class="agent-message">', unsafe_allow_html=True)
        st.markdown("**🤖 Architecture Designer Proposal:**")
        st.markdown(st.session_state.architecture_proposal)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show sources used
        st.markdown("**📚 Sources Used:**")
        sources = [
            "docs/architecture/onion_architecture.md",
            "docs/guides/security_guidelines.md",
            "docs/guides/langchain_patterns.md"
        ]
        if st.session_state.user_story:
            sources.append(f"docs/agile/sprints/sprint_6/user_stories/{st.session_state.user_story}.md")
        
        for source in sources:
            st.markdown(f'<span class="source-badge">📄 {source}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🤝 Your Decision:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Approve & Continue", type="primary"):
            st.session_state.stage = 'review'
            st.rerun()
    
    with col2:
        if st.button("🔄 Request Changes"):
            st.info("Refinement feature coming soon!")
    
    with col3:
        if st.button("📚 Consult More Docs"):
            st.session_state.stage = 'guideline_selection'
            st.rerun()


def show_review_stage():
    """Stage 4: Final review and summary."""
    st.markdown('<div class="sync-point">', unsafe_allow_html=True)
    st.markdown("### ✅ STAGE 4: Review & Summary")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.success("🎉 **Architecture design complete!**")
    
    st.markdown("### 📋 Summary")
    
    st.markdown(f"""
    **Task**: {st.session_state.task}
    
    **User Story**: {st.session_state.user_story or "N/A"}
    
    **Guidelines Used**: {st.session_state.user_guidelines}
    
    **Documents Loaded**: {sum(len(srcs) for srcs in st.session_state.loaded_sources.values())} sources across {len(st.session_state.loaded_sources)} categories
    
    **Architecture Status**: ✅ Approved
    """)
    
    st.markdown("### 🚀 Next Steps")
    st.markdown("""
    In a complete workflow, you would now:
    1. ✅ Code Generation (with coding guidelines)
    2. ✅ Test Generation (with testing guidelines)
    3. ✅ Code Review (with review guidelines)
    4. ✅ Deployment Planning
    
    Each stage would have similar RAG-enhanced proactive guidance!
    """)
    
    if st.button("🔄 Start New Task"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


if __name__ == "__main__":
    main()

