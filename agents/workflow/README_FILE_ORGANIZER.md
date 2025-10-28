# File Organizer Agent

A demonstration agent that showcases:
- **MCP Tool Integration**: Uses MCP `file.read` tool to analyze files
- **Human-in-the-Loop**: Interrupts workflow for human approval before executing changes
- **LangGraph Studio**: Compatible with LangGraph Studio for visual debugging

## Features

### 1. MCP Tools Integration

The agent uses MCP tools (specifically `file.read`) to:
- Read and analyze file contents
- Gather information for intelligent file organization
- Access 27 available MCP tools including file system, database, and cloud storage tools

### 2. Human-in-the-Loop Pattern

The workflow implements LangGraph's interrupt pattern:
```python
workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]  # Pause before human review
)
```

This allows:
- **Review before action**: Human reviews proposed changes before execution
- **Resumption**: Workflow can be resumed after human decision
- **Thread persistence**: Uses thread_id to maintain conversation state

### 3. Workflow Steps

```
1. scan_directory      → Scan files in target directory
2. analyze_files       → Use MCP tools to analyze files
3. propose_changes     → Generate organization proposals
4. human_review        → [INTERRUPT] Wait for human approval
5. execute_changes     → Execute approved changes (if approved)
```

## State Model

```python
class FileOrganizerState(TypedDict):
    # Input
    directory_path: str
    organization_rules: str
    
    # Analysis
    scanned_files: List[Dict[str, Any]]
    file_analysis: str
    
    # Proposed changes
    proposed_changes: List[Dict[str, Any]]
    
    # Human decision
    human_approval: str  # "approved", "rejected", "pending"
    human_feedback: str
    
    # Execution
    executed_changes: List[Dict[str, Any]]
    execution_status: str
    
    # Tracking
    messages: Annotated[List, operator.add]
    current_step: str
    errors: Annotated[List[str], operator.add]
```

## Usage

### Basic Usage

```python
import asyncio
from agents.workflow.file_organizer_agent import FileOrganizerAgent

async def main():
    # Initialize agent
    agent = FileOrganizerAgent()
    await agent.initialize()
    
    # Start organization (interrupts at human_review)
    result = await agent.organize_files(
        directory_path="./my_files",
        organization_rules="organize by file type",
        thread_id="session_1"
    )
    
    # Review proposed changes
    print(f"Proposed: {result['proposed_changes']}")
    
    # Human approves
    final_result = await agent.continue_after_approval(
        approved=True,
        feedback="Looks good!",
        thread_id="session_1"  # Must match original
    )
    
    print(f"Executed: {final_result['executed_changes']}")

asyncio.run(main())
```

### LangGraph Studio

The agent is registered in `langgraph.json`:

```json
{
  "graphs": {
    "file_organizer_agent": "agents/workflow/file_organizer_agent.py:graph"
  }
}
```

To use in LangGraph Studio:
1. Open LangGraph Studio
2. Select "file_organizer_agent" from the graphs list
3. Provide input:
   ```json
   {
     "directory_path": "./test_files",
     "organization_rules": "organize by file type"
   }
   ```
4. Run and observe the workflow
5. Approve/reject at the human review step

## Testing

Run the test script:

```bash
python tests/workflow/test_file_organizer_agent.py
```

This will:
1. Initialize the agent with MCP tools
2. Scan a directory
3. Analyze files using MCP `file.read` tool
4. Propose changes
5. Wait for your approval (human-in-the-loop)
6. Execute changes if approved

## MCP Tools Available

The agent has access to 27 MCP tools across categories:
- **File System** (6 tools): `file.read`, `file.write`, `file.exists`, etc.
- **Database** (6 tools): Database query and management
- **RAG** (4 tools): Document retrieval and search
- **Web Research** (5 tools): Web scraping and search
- **Cloud Storage** (6 tools): Google Drive integration

## Implementation Details

### Async Initialization

MCP tools must be loaded asynchronously:

```python
async def initialize(self):
    """Async initialization to load MCP tools."""
    self.mcp_tools = await create_mcp_tools_for_agent(
        agent_id="file_organizer",
        agent_type="workflow_agent"
    )
    self.workflow = await self._build_workflow()
```

### Checkpointer for Interrupts

Uses `MemorySaver` to enable interrupts and resumption:

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]
)
```

### Thread ID for State Persistence

Thread ID maintains conversation state across interrupts:

```python
config = {"configurable": {"thread_id": "session_1"}}

# First call - runs until interrupt
result = await workflow.ainvoke(initial_state, config)

# Second call - resumes from interrupt
result = await workflow.ainvoke(update_state, config)
```

## Key Concepts Demonstrated

1. **MCP Tool Integration**: Real tool usage in LangGraph agents
2. **Human-in-the-Loop**: Interrupts for human review
3. **State Management**: TypedDict with proper annotations
4. **Error Handling**: Graceful failure handling
5. **Studio Compatibility**: Works with LangGraph Studio

## Next Steps

This pattern can be extended to:
- Add more sophisticated file analysis
- Implement actual file operations (move/rename)
- Add undo/redo functionality
- Support batch operations
- Integrate with more MCP tools
- Add safety checks and validations

## References

- LangGraph Human-in-the-Loop: https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/
- LangGraph Checkpoints: https://langchain-ai.github.io/langgraph/concepts/#checkpoints
- MCP Integration: `utils/mcp/langchain_integration.py`

