# LangSmith Prompt Tags Reference

**Date**: 2025-10-28  
**Status**: Manual Tag Addition Required

## Overview

All prompts have been successfully pushed to LangSmith Hub. However, the LangSmith Python API doesn't support programmatic tag addition - tags must be added manually through the web UI.

## How to Add Tags

1. Go to: https://smith.langchain.com/hub
2. Search for the prompt name (e.g., "complexity_analyzer_v1")
3. Click on the prompt to open it
4. Click the "Edit" button
5. Add the tags in the tags field (comma-separated or as chips)
6. Click "Save" to apply changes

## Prompts Requiring Tags

### 🎯 Supervisor/Coordinator Prompts (3 prompts)

These prompts orchestrate the development workflow and coordinate between specialist agents.

#### **complexity_analyzer_v1**
**URL**: https://smith.langchain.com/prompts/complexity_analyzer_v1  
**Description**: Analyzes project complexity and classifies as simple, medium, or complex to guide workflow orchestration

**Tags**:
- `supervisor`
- `coordination`
- `complexity-analysis`
- `project-planning`
- `workflow-orchestration`
- `decision-making`
- `agent`

---

#### **agent_selector_v1**
**URL**: https://smith.langchain.com/prompts/agent_selector_v1  
**Description**: Selects which specialist agents are needed based on project requirements and complexity

**Tags**:
- `supervisor`
- `coordination`
- `agent-selection`
- `workflow-planning`
- `orchestration`
- `team-composition`
- `agent`

---

#### **router_v1**
**URL**: https://smith.langchain.com/prompts/router_v1  
**Description**: Routes workflow to the next appropriate agent based on completion status and requirements

**Tags**:
- `supervisor`
- `coordination`
- `routing`
- `workflow-control`
- `orchestration`
- `state-management`
- `agent`

---

### 🤖 RAG Agent Prompts (2 prompts)

These prompts are part of the RAG (Retrieval Augmented Generation) system.

#### **writer_v1**
**URL**: https://smith.langchain.com/prompts/writer_v1  
**Description**: Expert Writer Agent for RAG systems - synthesizes information from multiple sources and generates accurate, well-structured responses with proper attribution

**Tags**:
- `rag`
- `response-generation`
- `synthesis`
- `writing`
- `source-attribution`
- `agent`

---

#### **web_scraping_specialist_v1**
**URL**: https://smith.langchain.com/prompts/web_scraping_specialist_v1  
**Description**: Expert Web Scraping Specialist for RAG systems - extracts and processes web content for knowledge base enrichment

**Tags**:
- `rag`
- `web-scraping`
- `content-extraction`
- `document-parsing`
- `data-ingestion`
- `agent`

---

## Prompts Already Tagged

The following prompts already have tags applied (either manually or through previous processes):

### ✅ RAG Agent Prompts (4 prompts)
- `query_analyst_v1` - rag, query-analysis, query-expansion, intent-classification, search-optimization, agent, retrieval
- `retrieval_specialist_v1` - rag, retrieval, semantic-search, vector-search, multi-query, hybrid-search, agent
- `re_ranker_v1` - rag, reranking, relevance-scoring, document-ranking, quality-assessment, agent
- `quality_assurance_v1` - rag, quality-assurance, validation, hallucination-detection, accuracy-check, agent

### ✅ Development Workflow Agents
- `requirements_analyst_v1`
- `architecture_designer_v1`
- `code_generator_v1`
- `test_generator_v1`
- `code_reviewer_v1`
- `documentation_generator_v1`

---

## Tag Categories and Usage

### Supervisor/Coordination Tags
- `supervisor` - Main orchestrator or coordinator agents
- `coordination` - Manages workflow between agents
- `orchestration` - Workflow control and sequencing
- `routing` - Determines next agent in workflow
- `decision-making` - Makes strategic decisions
- `workflow-control` - Controls execution flow
- `state-management` - Manages workflow state
- `complexity-analysis` - Analyzes project complexity
- `agent-selection` - Selects appropriate agents
- `project-planning` - Plans project execution
- `workflow-planning` - Plans workflow sequence
- `team-composition` - Determines agent team structure

### RAG System Tags
- `rag` - Retrieval Augmented Generation system
- `query-analysis` - Analyzes and optimizes queries
- `query-expansion` - Generates query variations
- `intent-classification` - Classifies user intent
- `search-optimization` - Optimizes search strategies
- `retrieval` - Retrieves relevant information
- `semantic-search` - Vector-based semantic search
- `vector-search` - Vector similarity search
- `multi-query` - Multiple query strategies
- `hybrid-search` - Combined semantic + keyword search
- `reranking` - Re-orders results by relevance
- `relevance-scoring` - Scores document relevance
- `document-ranking` - Ranks documents by quality
- `quality-assessment` - Assesses result quality
- `quality-assurance` - Validates output quality
- `validation` - Validates responses
- `hallucination-detection` - Detects AI hallucinations
- `accuracy-check` - Checks factual accuracy
- `response-generation` - Generates final responses
- `synthesis` - Synthesizes multiple sources
- `writing` - Content writing and generation
- `source-attribution` - Cites information sources
- `web-scraping` - Web content extraction
- `content-extraction` - Extracts structured content
- `document-parsing` - Parses various document formats
- `data-ingestion` - Ingests data into knowledge base

### Universal Tags
- `agent` - Used on all agent prompts for easy filtering

---

## Tag Statistics

### By Category
- **Total Prompts**: 16 (in LangSmith Hub)
- **Supervisor/Coordinator**: 3 prompts (need tagging)
- **RAG Agents**: 6 prompts (2 need tagging, 4 already tagged)
- **Development Workflow**: 6 prompts (already tagged)
- **Other**: 1 prompt (test_prompt)

### Unique Tags
- **Total Unique Tags**: ~40 distinct tags across all prompts
- **Most Common**: `agent` (used on all agent prompts)
- **Category Leaders**: 
  - RAG: 25+ tags
  - Supervisor: 15+ tags
  - Development: varies by agent

---

## Quick Action Checklist

### Immediate Actions Required
- [ ] **complexity_analyzer_v1** - Add 7 supervisor tags
- [ ] **agent_selector_v1** - Add 7 supervisor tags
- [ ] **router_v1** - Add 7 supervisor tags
- [ ] **writer_v1** - Add 6 RAG tags
- [ ] **web_scraping_specialist_v1** - Add 6 RAG tags

**Total**: 5 prompts need manual tagging (33 tags total)

---

## Notes

### Why Manual Tagging?
The LangSmith Python API (`langsmith.Client`) doesn't provide a method to update tags on existing prompts. While `push_prompt()` accepts various parameters, tags are not persisted through the API. Tags can only be added/edited through the LangSmith Hub web interface.

### Tag Format
- Use lowercase with hyphens for multi-word tags (e.g., `workflow-orchestration`)
- Keep tags descriptive but concise
- Use consistent terminology across related prompts
- Group related functionality with shared tags

### Future Improvements
- Monitor LangSmith API updates for programmatic tag support
- Consider creating a GitHub Action to validate tags
- Maintain this document as new prompts are added
- Consider creating tag taxonomies for better organization

---

**Last Updated**: 2025-10-28  
**Next Review**: When adding new prompts to LangSmith Hub

