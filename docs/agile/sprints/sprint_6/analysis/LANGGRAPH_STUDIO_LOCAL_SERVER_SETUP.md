# LangGraph Studio Local Server Setup

**Date**: 2025-10-22  
**Status**: ✅ **RUNNING**  
**Epic**: EPIC-4: Developer Experience & Automation  
**User Story**: US-STUDIO-001

---

## 🎯 Server Configuration

### **Installation Complete**

✅ **Packages Installed**:
- `langgraph >= 1.0.1` (Latest version installed!)
- `langgraph-cli[inmem] 0.4.4` (with in-memory support)
- `langgraph-checkpoint 3.0.0`
- `trustcall 0.0.39`
- All dependencies and runtime components

### **Server Details**

- **Host**: `0.0.0.0` (accessible from any network interface)
- **Port**: `8123`
- **Mode**: Development server with hot-reload
- **Runtime**: In-memory (inmem) - perfect for local development
- **Python Path**: Set to project root for imports

---

## 🌐 **Access URLs**

### **LangGraph Studio Web UI**
```
http://localhost:8123
```

### **API Documentation**
```
http://localhost:8123/docs
```

### **OpenAPI Specification**
```
http://localhost:8123/openapi.json
```

### **Health Check**
```
http://localhost:8123/health
```

---

## 📋 **Available Graphs**

The server automatically discovers graphs from `langgraph.json`:

### **1. RAG Pipeline**
- **Path**: `agents.rag.rag_swarm_langgraph:RAGSwarmCoordinator`
- **Description**: 5-agent RAG document retrieval and synthesis pipeline
- **Agents**: QueryAnalyst → Retrieval → ReRanker → QualityAssurance → Writer
- **Use Case**: Document queries, knowledge retrieval, Q&A

### **2. Research Pipeline**
- **Path**: `agents.research.web_research_swarm:WebResearchSwarmCoordinator`
- **Description**: 5-agent web research pipeline
- **Agents**: QueryPlanner → WebSearch → ContentParser → Verification → Synthesis
- **Use Case**: Web research, fact finding, comprehensive reports

---

## 🚀 **Quick Start Guide**

### **Step 1: Access Studio**

Open your browser and navigate to:
```
http://localhost:8123
```

### **Step 2: Select a Graph**

From the dropdown, choose:
- `rag_pipeline` for document queries
- `research_pipeline` for web research

### **Step 3: Provide Input**

Example for RAG pipeline:
```json
{
  "query": "What is LangGraph?",
  "max_results": 5,
  "quality_threshold": 0.45,
  "enable_re_retrieval": true
}
```

Example for Research pipeline:
```json
{
  "query": "Latest developments in AI agent systems",
  "max_sources": 10,
  "research_depth": "standard"
}
```

### **Step 4: Run & Debug**

1. Click **"Run"** to start execution
2. Watch real-time graph visualization
3. Click **"Pause"** at any time to inspect state
4. Click on any node to see:
   - Input state
   - Output state
   - Execution time
   - Agent decisions

### **Step 5: Interact**

- **Modify State**: Edit values mid-execution
- **Retry Node**: Change code and rerun specific nodes
- **Continue**: Resume with modified state
- **Export**: Save execution trace for analysis

---

## 🔧 **Server Management**

### **Check Server Status**

```powershell
Invoke-WebRequest -Uri "http://localhost:8123/health" -UseBasicParsing
```

### **Stop Server**

Press `Ctrl+C` in the terminal where the server is running, or:

```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*langgraph dev*"} | Stop-Process
```

### **Restart Server**

```powershell
# Stop current server (Ctrl+C)
# Then restart:
$env:PYTHONPATH = "."
langgraph dev --host 0.0.0.0 --port 8123
```

### **Server Logs**

The server runs with verbose logging showing:
- Graph discovery and loading
- Request processing
- Agent execution steps
- Errors and warnings

---

## 🎨 **Studio Features**

### **Visual Graph Display**

- **Node Visualization**: See all agents as nodes
- **Edge Flow**: Watch state flow between agents
- **Execution Status**: Color-coded (running/complete/error)
- **Timing Info**: See execution time per node

### **State Inspection**

- **Before/After State**: Compare state changes
- **Full State Tree**: Expand nested objects
- **Type Information**: See data types
- **Search**: Find specific values in state

### **Interactive Debugging**

- **Pause Execution**: Stop at any point
- **Step Forward**: Execute one node at a time
- **Step Backward**: Review previous nodes
- **Modify & Continue**: Edit state and resume

### **Human-in-the-Loop**

- **Review Checkpoints**: Pause for human approval
- **Feedback Injection**: Add human feedback to state
- **Manual Override**: Change agent decisions
- **Fork Execution**: Try different paths

---

## 📊 **Example Workflows**

### **RAG Pipeline Debug Session**

1. Start RAG pipeline with query about LangGraph
2. Pause after QueryAnalyst node
3. Inspect query analysis results
4. Check key concepts extracted
5. Continue to Retrieval
6. Pause and check retrieved chunks
7. Modify quality threshold if needed
8. Resume and watch re-ranking
9. Final response generated

### **Research Pipeline Testing**

1. Start research pipeline with tech query
2. Watch QueryPlanner create search strategy
3. See WebSearch execute searches
4. Pause at ContentParser
5. Inspect parsed content
6. Check verification results
7. Review final synthesis
8. Export complete trace

---

## ⚙️ **Environment Variables**

The server uses these environment variables (configured in `langgraph.json`):

```bash
GOOGLE_API_KEY=your_google_api_key          # For Gemini LLM
LANGCHAIN_API_KEY=your_langsmith_key        # For tracing (optional)
LANGCHAIN_TRACING_V2=true                   # Enable tracing (optional)
LANGCHAIN_PROJECT=ai-dev-agent              # Project name in LangSmith
PYTHONPATH=.                                # Project root for imports
```

### **Set Environment Variables** (if needed)

```powershell
$env:GOOGLE_API_KEY = "your-api-key-here"
$env:LANGCHAIN_API_KEY = "your-langsmith-key"  # Optional
$env:LANGCHAIN_TRACING_V2 = "true"             # Optional
```

---

## 🐛 **Troubleshooting**

### **Server Won't Start**

**Problem**: Port 8123 already in use  
**Solution**:
```powershell
# Use different port
langgraph dev --host 0.0.0.0 --port 8124
```

**Problem**: Import errors  
**Solution**:
```powershell
# Ensure PYTHONPATH is set
$env:PYTHONPATH = "."
langgraph dev --host 0.0.0.0 --port 8123
```

### **Graphs Not Appearing**

**Problem**: No graphs in dropdown  
**Solution**:
- Check `langgraph.json` is in project root
- Verify graph paths are correct
- Check server logs for errors
- Ensure graph classes are importable

### **Execution Errors**

**Problem**: Graph execution fails  
**Solution**:
- Check API keys are set (GOOGLE_API_KEY)
- Verify agent dependencies are installed
- Check server logs for detailed errors
- Try with simpler input first

### **Performance Issues**

**Problem**: Server slow or unresponsive  
**Solution**:
- Reduce max_results for RAG pipeline
- Use "quick" research_depth for research pipeline
- Check system resources
- Restart server if needed

---

## 📚 **Resources**

### **Official Documentation**
- [LangGraph CLI Documentation](https://docs.langchain.com/oss/python/langgraph/local-server)
- [LangGraph Studio Guide](https://blog.langchain.com/langgraph-studio-the-first-agent-ide/)
- [LangSmith Tracing](https://docs.smith.langchain.com/)

### **Project Documentation**
- [Integration Design](./LANGGRAPH_STUDIO_INTEGRATION_DESIGN.md)
- [User Story US-STUDIO-001](../../user_stories/US-STUDIO-001-langgraph-studio-integration.md)
- [Agent README](../../../agents/langgraph_studio/README.md)

---

## 🎯 **Next Steps**

### **Immediate** (Today)
1. ✅ Access Studio at http://localhost:8123
2. ✅ Test RAG pipeline with sample query
3. ✅ Test Research pipeline with sample query
4. ✅ Explore visual debugging features

### **Sprint 7** (Next)
1. Implement Development Pipeline Graph
2. Create single agent wrappers
3. Add human-in-the-loop checkpoints
4. Performance optimization

### **Future**
1. Team coordinator graphs
2. Custom UI components
3. Advanced state persistence
4. Collaborative debugging

---

## 🎉 **Success!**

**LangGraph Studio is now running locally!**

✅ Web-based IDE accessible at: http://localhost:8123  
✅ 2 graphs ready to test (RAG, Research)  
✅ Full visual debugging capabilities  
✅ State inspection and modification  
✅ Human-in-the-loop support  
✅ Real-time execution monitoring  

**This is revolutionary for agent development! 🚀**

---

**Server Started**: 2025-10-22  
**Status**: 🟢 **RUNNING**  
**Host**: 0.0.0.0:8123  
**Mode**: Development (with hot-reload)  
**Ready**: ✅ YES

**Access now**: Open http://localhost:8123 in your browser!

