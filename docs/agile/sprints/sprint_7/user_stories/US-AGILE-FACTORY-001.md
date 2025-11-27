# User Story: US-AGILE-FACTORY-001 - Agile Software Factory Agent System

**Epic**: EPIC-2: Software Development Agents  
**Sprint**: Sprint 7  
**Story Points**: 21  
**Priority**: 🔴 **CRITICAL**  
**Status**: 📋 **BACKLOG**  
**Created**: 2025-10-28  
**Assignee**: AI Development Team

## Story Overview

**As a** development team lead  
**I want** an Agile Software Factory Agent system that creates interactive websites and Streamlit apps for data analysis  
**So that** I can automate the complete development lifecycle from user story to production-ready code with human oversight, quality gates, and feedback loops

**Focus**: HTML and Python (websites and Streamlit apps)

## Business Value

Create an Agile Software Factory Agent system that:
- **Generates** interactive HTML websites and Streamlit apps for data analysis
- **Uses** HTML and Python as primary languages
- **Provides** HITL checkpoints between each major step (requirements, architecture, code, review, test, docs)
- **Implements** feedback loops: Code Reviewer ↔ Code Generator, Testing Agent ↔ Code Generator
- **Prevents** infinite loops with max iteration limits (3 iterations per feedback loop)
- **Coordinates** 6 specialized agent roles: Requirements Analyst, Architecture Designer, Code Generator, Code Reviewer, Testing Agent, Documentation Generator
- **Persists** state using LangGraph checkpointers at relevant nodes
- **Uses** existing prompt loading system (`get_agent_prompt_loader`)
- **Integrates** tools: Python REPL, website test tool, file operations

**Problem We're Solving**: 
- Need for automated generation of websites and Streamlit apps
- Requirement for human oversight at critical decision points
- Need for quality gates and feedback loops to ensure code quality
- Coordination of multiple specialized agents with proper handoffs
- Integration with code execution and testing tools

## Architecture Overview

Based on: [Agile Software Factory Agent Architecture](https://sites.google.com/view/agile-software-factory-agent/startseite)

### Two Operational Modes

1. **Program Manager Mode**: Long-running, human-in-the-loop (HITL) agile projects
   - Full epic → story → task workflow
   - Agile ceremonies (planning, refinement, standups, retro)
   - HITL checkpoints at critical gates
   - State persistence across weeks/months

2. **Code Mechanic Mode**: Near-fully automated small changes / bugfixes
   - Fast, autonomous workflow
   - Minimal HITL intervention
   - Swarm pattern for agent handoffs
   - Quick turnaround for simple fixes

### Core Requirements

1. **Long-Running Projects**
   - Epics, user stories, tasks, sprints
   - Agile ceremonies (planning, refinement, standups, retro)
   - Persistence of state and artifacts across weeks/months

2. **HITL at Relevant Steps**
   - Confirm plans, estimates, designs
   - Allow humans to edit tickets, prompts, code diffs
   - "Safe lanes" vs "autonomous lanes" (simple bugfixes)

3. **Selectable Methodology + Rules**
   - Methodology chosen at project/thread creation (Scrum vs Kanban, TDD, coding standards)
   - Rules must actually constrain behavior: naming conventions, test-first, branching strategy, review policy

4. **Real Software Work**
   - Understand repos, tickets, ADRs
   - Generate/modify code and tests
   - Coordinate multiple roles: Product, Architect, Dev, QA, DevOps

5. **Adaptable Tech Stack**
   - Analyze LangChain (DeepAgents, Swarm, state, memory, tooling)
   - Consider alternatives: n8n, CrewAI, AutoGen, Semantic Kernel, LlamaIndex Agents

## Acceptance Criteria

### Phase 0: Minimum Viable Agent System (All Roles from Start)
- [ ] **AC-0.1**: Create `agents/agile_factory/` directory structure
- [ ] **AC-0.2**: Define complete LangGraph state schema with all agent outputs and loop prevention
- [ ] **AC-0.3**: Set up LangGraph checkpointer (SqliteSaver) for state persistence
- [ ] **AC-0.4**: Implement prompt loading using existing `get_agent_prompt_loader` system
- [ ] **AC-0.5**: Create Python REPL tool (execute Python code, run Streamlit apps)
- [ ] **AC-0.6**: Create website test tool (test HTML pages, Streamlit apps)
- [ ] **AC-0.7**: Implement Requirements Analyst Node (using existing agent + prompt loader)
- [ ] **AC-0.8**: Implement Architecture Designer Node (using existing agent + prompt loader)
- [ ] **AC-0.9**: Implement Code Generator Node (Regular Agent with write_file, Python REPL, website test tools)
- [ ] **AC-0.10**: Implement Code Reviewer Node (using existing agent + prompt loader)
- [ ] **AC-0.11**: Implement Testing Agent Node (Regular Agent with Python REPL, website test tools)
- [ ] **AC-0.12**: Implement Documentation Generator Node (Regular Agent with write_file tool)
- [ ] **AC-0.13**: Implement HITL checkpoints between each major step (5 checkpoints)
- [x] **AC-0.14**: Implement Review Decision Router (Code Reviewer → Code Generator loop, max 3 iterations)
- [x] **AC-0.15**: Implement Test Decision Router (Testing Agent → Code Generator loop, max 3 iterations)
- [ ] **AC-0.16**: Build complete LangGraph workflow with all nodes, edges, and checkpointers
- [ ] **AC-0.17**: Test end-to-end: User story → Complete website/Streamlit app

### Phase 3: HITL Checkpoint System
- [ ] **AC-3.1**: Create HITL gate infrastructure with structured summaries
- [ ] **AC-3.2**: Implement approval options (approve, edit, reject, ask question)
- [ ] **AC-3.3**: Add HITL checkpoints after epic/story breakdown
- [ ] **AC-3.4**: Add HITL checkpoints after architecture/ADR proposal
- [ ] **AC-3.5**: Add HITL checkpoints after implementation plan
- [ ] **AC-3.6**: Add HITL checkpoints after large code change diffs
- [ ] **AC-3.7**: Add HITL checkpoints before release plan
- [ ] **AC-3.8**: Implement state updates based on HITL feedback

### Phase 4: Methodology & DoD Enforcement
- [ ] **AC-4.1**: Create methodology_profile model (Scrum, Kanban, TDD, custom)
- [ ] **AC-4.2**: Implement DoD model with machine-checkable clauses
- [ ] **AC-4.3**: Create rule enforcement system (naming conventions, test-first, branching strategy)
- [ ] **AC-4.4**: Implement GovernanceNode DoD checking logic
- [ ] **AC-4.5**: Add methodology-specific prompt loading based on methodology_profile
- [ ] **AC-4.6**: Create rule violation reporting and remediation paths

### Phase 5: RAG Integration
- [ ] **AC-5.1**: Initialize ContextEngine with Qdrant vector store and Gemini embeddings (free, consistent)
- [ ] **AC-5.2**: Create Project RAG coordinator using RAGSwarmCoordinator pattern (repo, docs, tickets, ADRs)
- [ ] **AC-5.3**: Create Methodology RAG coordinator using RAGSwarmCoordinator pattern (Scrum guide, coding guidelines, DoD)
- [ ] **AC-5.4**: Index project documents with metadata filters (type:adr, type:architecture, project:XYZ)
- [ ] **AC-5.5**: Index methodology documents with metadata filters (type:scrum, type:rule, type:dod)
- [ ] **AC-5.6**: Integrate Project RAG in ArchitectNode (ADRs and architecture patterns)
- [ ] **AC-5.7**: Integrate Methodology RAG in DeveloperPlanNode (coding standards, TDD rules)
- [ ] **AC-5.8**: Integrate Methodology RAG in GovernanceNode (DoD enforcement)
- [ ] **AC-5.9**: Set up RAG persistence layer for document tracking and analytics
- [ ] **AC-5.10**: Use MessagesState-compatible RAG queries (LangGraph integration)

### Phase 6: State Persistence & Long-Running Support
- [ ] **AC-6.1**: Verify LangGraph checkpointer state persistence across sessions (already in Phase 0)
- [ ] **AC-6.2**: Create project state storage (DB/graph store) - using SqliteSaver checkpointer
- [ ] **AC-6.3**: Support epic → stories → tasks hierarchical structure persistence
- [ ] **AC-6.4**: Implement state recovery and resume functionality
- [ ] **AC-6.5**: Add state versioning and history tracking
- [ ] **AC-6.6**: Implement workspace file extraction utilities

### Phase 7: Integration & Testing
- [ ] **AC-7.1**: Integrate with existing architecture_designer.py agent
- [ ] **AC-7.2**: Integrate code_generator with write_file tool (regular LangChain agent)
- [ ] **AC-7.3**: Integrate documentation_generator with write_file tool (regular LangChain agent)
- [ ] **AC-7.4**: Integrate with existing test_generator.py agent
- [ ] **AC-7.5**: End-to-end workflow testing (story → implementation → QA → documentation → release)
- [ ] **AC-7.6**: HITL checkpoint testing
- [ ] **AC-7.7**: Methodology enforcement testing
- [ ] **AC-7.8**: LangGraph checkpointer state persistence testing
- [ ] **AC-7.9**: write_file tool artifact generation testing

## Technical Implementation

### Architecture Design

```
agents/agile_factory/
├── __init__.py
├── factory_coordinator.py      # Main coordinator for agile factory
├── state/
│   ├── agile_state.py          # LangGraph state schema
│   └── methodology_profile.py  # Methodology and DoD models
├── agents/
│   ├── product_owner_agent.py  # POA - Story refinement
│   ├── architect_agent.py      # AA - Solution design
│   ├── developer_agent.py      # DA - Planning & implementation
│   ├── qa_agent.py             # QAA - Test planning & execution
│   ├── devops_agent.py         # DOA - CI/CD & release
│   └── governance_agent.py     # GA - Methodology enforcement
├── nodes/
│   ├── story_refinement_node.py
│   ├── architect_node.py
│   ├── developer_plan_node.py
│   ├── developer_implement_node.py
│   ├── code_generator_node.py      # Regular Agent with write_file tool
│   ├── documentation_generator_node.py  # Regular Agent with write_file tool
│   ├── qa_node.py
│   ├── governance_node.py
│   ├── hitl_node.py
│   └── devops_node.py
├── rag/
│   ├── project_rag_coordinator.py    # Project RAG using RAGSwarmCoordinator
│   ├── methodology_rag_coordinator.py # Methodology RAG using RAGSwarmCoordinator
│   └── rag_initialization.py         # ContextEngine setup and document indexing
└── persistence/
    ├── state_store.py          # State persistence
    └── artifact_store.py       # Artifact storage
```

### LangGraph State Schema

```python
class AgileFactoryState(TypedDict, total=False):
    """State for Agile Software Factory LangGraph workflow."""
    
    # Methodology & Project Context
    methodology_profile: Dict[str, Any]  # Scrum/Kanban/TDD, rules, DoD
    project_context: Dict[str, Any]      # Project info, repo, tickets
    
    # Story & Requirements
    story: Dict[str, Any]                # Current story with ACs, status, risk
    acceptance_criteria: List[Dict[str, Any]]
    
    # Architecture & Design
    design_notes: Dict[str, Any]
    adr_candidates: List[Dict[str, Any]]
    
    # Implementation
    implementation_plan: List[Dict[str, Any]]  # TODOs from DeepAgents
    current_change: Dict[str, Any]             # Diff, LOC, files
    test_status: Dict[str, Any]
    
    # QA & Review
    qa_report: Dict[str, Any]
    review_report: Dict[str, Any]
    requires_hitl: bool
    
    # HITL
    hitl_feedback: Dict[str, Any]
    hitl_approved: bool
    requested_changes: List[str]
    
    # DevOps
    integration_status: str  # ci_pass/ci_fail/pending
    pr_url: Optional[str]
    
    # Control
    errors: List[str]
    status: str
```

### Node Implementation Pattern

Each node follows this pattern:
1. **Inputs**: Specific state fields
2. **Agent**: Specialized agent (POA, AA, DA, etc.)
3. **Tools**: RAG, file ops, test runner, etc.
4. **Prompt Focus**: Node-specific instructions
5. **Output**: Updates to state
6. **Handover**: Conditional routing to next node

Example: **ArchitectNode**

```python
def architect_node(state: AgileFactoryState) -> AgileFactoryState:
    """
    Node 2: ArchitectNode (AA)
    
    Inputs: refined story with ACs
    Agent: Architect Agent
    Tools: RAG over ADRs, architecture docs; optional structural repo overview
    Prompt focus:
    - Propose high-level design solution
    - Identify impacted components
    - Suggest new/updated ADR if meaningful
    Output to state:
    - design_notes
    - adr_candidates (structured objects)
    - maybe story.risk_level elevation if necessary
    """
    # Load methodology-specific prompt
    prompt_manager = PromptManager()
    prompt = prompt_manager.load_prompt(
        "architect_agent",
        context={
            "methodology": state["methodology_profile"],
            "story": state["story"],
            "ac": state["acceptance_criteria"]
        }
    )
    
    # Use RAG for ADRs and architecture docs
    rag_context = project_rag.query(
        query=f"Architecture patterns for {state['story']['type']}",
        filters={"type": "adr", "project": state["project_context"]["name"]}
    )
    
    # Architect agent reasoning
    architect_agent = ArchitectAgent()
    design_result = architect_agent.design(
        story=state["story"],
        rag_context=rag_context,
        prompt=prompt.content
    )
    
    # Update state
    state["design_notes"] = design_result.design_notes
    state["adr_candidates"] = design_result.adr_candidates
    if design_result.risk_elevation:
        state["story"]["risk_level"] = design_result.risk_elevation
    
    return state
```

### HITL Checkpoint Pattern

```python
def hitl_node(state: AgileFactoryState) -> AgileFactoryState:
    """
    Node 7: HitlNode (Human)
    
    Creates structured summary for human review:
    - What changed
    - Why
    - How it was tested
    - Known limitations/questions
    
    Human actions:
    - Approve (possibly with notes)
    - Request changes (with comments)
    - Reject (terminate / redo story)
    """
    summary = create_hitl_summary(state)
    
    # Present to human (via UI, Slack, Jira, etc.)
    human_feedback = await present_for_approval(summary)
    
    state["hitl_feedback"] = human_feedback
    state["hitl_approved"] = human_feedback.action == "approve"
    
    if human_feedback.action == "request_changes":
        state["requested_changes"] = human_feedback.comments
        state["hitl_approved"] = False
    
    return state
```

### DoD Enforcement Pattern

```python
def governance_node(state: AgileFactoryState) -> AgileFactoryState:
    """
    Node 6: GovernanceNode (GA)
    
    Enforces methodology profile & DoD:
    - Check each DoD clause: met / not_met
    - Evaluate overall compliance
    - Determine if automation is allowed
    """
    methodology = state["methodology_profile"]
    dod_clauses = methodology["dod"]
    
    compliance_report = {}
    for clause in dod_clauses:
        clause_result = evaluate_dod_clause(
            clause=clause,
            qa_report=state["qa_report"],
            diff=state["current_change"],
            test_results=state["test_status"]
        )
        compliance_report[clause] = clause_result
    
    all_met = all(r["met"] for r in compliance_report.values())
    requires_hitl = determine_hitl_requirement(
        risk=state["story"]["risk_level"],
        loc=state["current_change"]["loc"],
        touched_components=state["current_change"]["files"]
    )
    
    state["review_report"] = {
        "compliance": compliance_report,
        "all_met": all_met,
        "requires_hitl": requires_hitl,
        "auto_safe": all_met and not requires_hitl
    }
    state["requires_hitl"] = requires_hitl
    
    return state
```

## Dependencies

### External Dependencies
- LangGraph for workflow orchestration
- LangGraph checkpointers (SqliteSaver/MemorySaver) for state persistence
- LangChain for agent creation, tooling, and RAG
- Custom write_file tool for file operations
- **Qdrant** vector store for RAG (following codebase best practice)
- **Google Gemini Embeddings** (gemini-embedding-001) - free, consistent with LLM
- **ContextEngine** from codebase for semantic search
- **RAGSwarmCoordinator** pattern from codebase (5-agent RAG workflow)
- Git tools for DevOps integration
- CI/CD APIs (GitHub Actions, GitLab CI, etc.)

### Internal Dependencies
- Existing agents (`architecture_designer.py`, `code_generator.py`, `test_generator.py`)
- Prompt management system (for methodology-specific prompts)
- RAG system (for project and methodology knowledge)
- State persistence system

## Technical Considerations

### Framework Selection
- **Core**: LangChain + LangGraph + DeepAgents (recommended)
- **Orchestration**: Consider n8n for external integrations
- **Alternatives**: CrewAI, AutoGen, Semantic Kernel, LlamaIndex Agents

### Performance
- Efficient state management
- RAG query optimization
- Parallel agent execution where possible
- State persistence optimization

### Reliability
- State recovery mechanisms
- Error handling at each node
- Rollback capabilities
- HITL timeout handling

## Testing Strategy

### Unit Tests
- Each agent node independently
- DoD clause evaluation
- State transitions
- RAG queries

### Integration Tests
- End-to-end workflow (story → release)
- HITL checkpoint flow
- Methodology enforcement
- State persistence

### Performance Tests
- Workflow execution time
- RAG query performance
- State persistence performance

## Success Metrics

### Functionality
- ✅ Complete workflow from story refinement to release
- ✅ HITL checkpoints working correctly
- ✅ Methodology enforcement functional
- ✅ State persistence across sessions
- ✅ All agent roles coordinated

### Performance
- Story refinement < 2 minutes
- Architecture design < 5 minutes
- Implementation planning < 3 minutes
- Full workflow < 30 minutes (without HITL waits)

### Quality
- DoD enforcement > 95% accuracy
- HITL approval rate > 80%
- State recovery success rate 100%

## Risks & Mitigation

### Risk 1: Complexity of Multi-Agent Coordination
**Impact**: High | **Probability**: High  
**Mitigation**: Start with simple workflow, add complexity incrementally, comprehensive testing

### Risk 2: State Management Complexity
**Impact**: High | **Probability**: Medium  
**Mitigation**: Use LangGraph's built-in checkpointing, design clear state schema, test persistence thoroughly

### Risk 3: HITL Integration Complexity
**Impact**: Medium | **Probability**: Medium  
**Mitigation**: Start with simple UI, use existing systems (Slack/Jira), clear approval workflows

### Risk 4: Methodology Enforcement Accuracy
**Impact**: Medium | **Probability**: Medium  
**Mitigation**: Start with simple rules, test extensively, allow manual overrides

## Related Stories

- **US-RAG-005**: RAG system needed for project and methodology knowledge
- **US-RAG-006**: HITL architecture patterns
- **US-PROMPT-001**: Methodology-specific prompt loading
- Future: Integration with external tools (Jira, GitHub, CI/CD)

## Notes

**Reference**: [Agile Software Factory Agent Architecture](https://sites.google.com/view/agile-software-factory-agent/startseite)

**Implementation Priority**: Critical - Foundation for long-running agile projects

**Estimated Effort**: 21 story points (3-4 weeks)

**Starting Point**: Begin with LangGraph state schema and basic node structure, then implement agents incrementally

---

**Status**: Ready for implementation planning  
**Next Steps**: Create detailed implementation plan, start with Phase 1 - Multi-Agent Role System

