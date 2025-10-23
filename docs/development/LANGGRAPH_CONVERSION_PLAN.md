# LangGraph Conversion Plan

## Status: Converting all agents to LangGraph compatibility

### ✅ Completed (Already LangGraph Compatible)
- [x] requirements_analyst_langgraph.py (Pydantic BaseModel ✓)
- [x] architecture_designer_langgraph.py (Pydantic BaseModel ✓)
- [x] code_generator_langgraph.py (Pydantic BaseModel ✓)
- [x] rag_swarm_langgraph.py (needs Pydantic verification)
- [x] web_research_swarm.py (needs Pydantic verification)

### 🔄 In Progress (Need Pydantic BaseModel Conversion)
- [ ] test_generator_langgraph.py
- [ ] code_reviewer_langgraph.py
- [ ] documentation_generator_langgraph.py
- [ ] development_workflow_langgraph.py

### 📝 To Create (Individual Research Agents)
- [ ] query_planner_langgraph.py
- [ ] web_search_langgraph.py
- [ ] content_parser_langgraph.py
- [ ] verification_langgraph.py
- [ ] synthesis_langgraph.py
- [ ] comprehensive_research_langgraph.py

### 📝 To Create (Individual RAG Agents)
- [ ] query_analyst_langgraph.py
- [ ] retrieval_specialist_langgraph.py
- [ ] re_ranker_langgraph.py
- [ ] writer_langgraph.py
- [ ] quality_assurance_langgraph.py
- [ ] web_scraping_specialist_langgraph.py

### 📝 To Create (Management Agents)
- [ ] project_manager_langgraph.py
- [ ] self_optimizing_validation_langgraph.py

### 📝 To Create (Security Agents)
- [ ] security_analyst_langgraph.py
- [ ] ethical_ai_protection_langgraph.py

### 📝 To Create (MCP Agent)
- [ ] mcp_enhanced_langgraph.py

### 📝 To Create (Specialized Teams)
- [ ] specialized_subagent_team_langgraph.py
- [ ] workflow_orchestration_team_langgraph.py
- [ ] test_recovery_specialist_team_langgraph.py
- [ ] database_cleanup_specialist_team_langgraph.py

## Strategy
1. **Phase 1**: Complete Pydantic conversion for existing LangGraph agents (4 agents)
2. **Phase 2**: Create swarm graphs for major workflows (3 swarms)
3. **Phase 3**: Expose top 10 most useful agents in langgraph.json
4. **Phase 4**: Gradually add remaining agents as needed

## langgraph.json Update Strategy
Expose in order of importance:
1. Development Workflow (full SDLC)
2. Requirements Analyst (standalone)
3. Architecture Designer (standalone)
4. Code Generator (standalone)
5. RAG Swarm (information retrieval)
6. Research Swarm (web research)
7. Test Generator (standalone)
8. Code Reviewer (standalone)
9. Documentation Generator (standalone)
10. Project Manager (coordination)

