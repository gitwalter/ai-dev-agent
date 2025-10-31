# User Story: US-RAG-005 - Sophisticated Multi-Agent RAG Workflow Restoration

**Epic**: EPIC-1: RAG System Enhancement  
**Sprint**: Sprint 7  
**Story Points**: 13  
**Priority**: 🔴 **CRITICAL**  
**Status**: 🟢 **IN PROGRESS**  
**Created**: 2025-10-28  
**Started**: 2025-10-28

## Story Overview

**As a** developer using the RAG system  
**I want** the sophisticated 5-agent workflow restored with all specialized agents  
**So that** I get high-quality, thoroughly processed answers instead of simple tool-based retrieval

## Business Value

Restore the sophisticated multi-agent architecture that was replaced by the simplified tool-based approach:
- **QueryAnalystAgent**: Deep query understanding and intent classification
- **RetrievalSpecialistAgent**: Multi-source retrieval orchestration
- **ReRankerAgent**: Relevance scoring and quality filtering
- **QualityAssuranceAgent**: Comprehensive quality validation
- **WriterAgent**: Sophisticated answer synthesis with citations

**Problem We're Solving**: The workflow was over-simplified when adding HITL, losing all sophisticated agent processing.

## Acceptance Criteria

### Phase 1: Agent Node Implementation ✅
- [x] **AC-1.1**: Implement `_query_analyst_node` calling QueryAnalystAgent.execute()
- [x] **AC-1.2**: Implement `_retrieval_specialist_node` calling RetrievalSpecialistAgent.execute()
- [x] **AC-1.3**: Implement `_re_ranker_node` calling ReRankerAgent.execute()
- [x] **AC-1.4**: Implement `_quality_assurance_node` calling QualityAssuranceAgent.execute()
- [x] **AC-1.5**: Implement `_writer_node` calling WriterAgent.execute()

### Phase 2: Graph Structure Restoration ✅
- [x] **AC-2.1**: Rebuild `_build_graph()` with 5-agent flow
- [x] **AC-2.2**: Add conditional routing based on quality checks
- [x] **AC-2.3**: Add rewrite loop back to query_analyst
- [x] **AC-2.4**: Integrate with existing HITL checkpoints

### Phase 3: Testing & Validation
- [ ] **AC-3.1**: Test complete 5-agent flow in LangSmith (show all agents)
- [ ] **AC-3.2**: Verify each agent's work is visible in trace
- [ ] **AC-3.3**: Validate answer quality improvement vs. simple mode
- [ ] **AC-3.4**: Test rewrite loop when quality is insufficient

## Technical Implementation

### Graph Structure
```python
START
  ↓
query_analyst (QueryAnalystAgent)
  ↓
retrieval_specialist (RetrievalSpecialistAgent)
  ↓
re_ranker (ReRankerAgent)
  ↓
quality_assurance (QualityAssuranceAgent)
  ↓
writer (WriterAgent)
  ↓
END

With conditional loops:
- If quality low → rewrite_question → back to query_analyst
```

### Files Modified
- `agents/rag/rag_swarm_coordinator.py` - Graph rebuild, agent node implementations
- `docs/architecture/RAG_WORKFLOW_RESTORATION.md` - Design documentation

## Testing Strategy

1. **Agent Execution Test**: Verify each agent executes and produces output
2. **LangSmith Trace Test**: Confirm all 5 agents visible in trace
3. **Quality Comparison**: Compare answers vs. simple retrieval mode
4. **Rewrite Loop Test**: Trigger quality-based rewrite and validate loop

## Definition of Done

- [x] All 5 agent nodes implemented
- [x] Graph structure restored with all agents
- [ ] LangSmith trace shows all agent work
- [ ] Answer quality measurably improved
- [ ] All tests passing
- [ ] Documentation updated

## Dependencies

- Depends on: US-RAG-004 (Agentic RAG foundation)
- Blocks: US-RAG-006 (HITL-First Architecture)

## Notes

**Why This Was Needed**: When implementing HITL, we simplified the workflow to basic tool calling, losing all the sophisticated agent processing. This story restores the professional-grade multi-agent architecture.

**Key Insight**: HITL and sophisticated agents are NOT mutually exclusive - we can have both!

