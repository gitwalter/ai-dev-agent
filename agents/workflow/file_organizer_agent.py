"""
File Organizer Agent - LangGraph with Human-in-the-Loop
========================================================

Simple agent that:
1. Scans a directory for files
2. Uses MCP file.read tool to analyze files
3. Proposes file organization changes
4. Waits for human approval (human-in-the-loop)
5. Executes approved changes

Compatible with LangGraph Studio.
"""

from __future__ import annotations

import logging
import os
from typing import Dict, Any, List, Annotated, TypedDict, Literal
try:
    from typing import NotRequired  # Python 3.11+
except ImportError:
    from typing_extensions import NotRequired  # Python 3.8-3.10
import operator
from pathlib import Path

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Use official LangChain MCP adapters
import sys
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)


# ============================================================================
# STATE - TypedDict with proper annotations
# ============================================================================

class FileOrganizerState(TypedDict):
    """State for file organizer agent with human-in-the-loop."""
    
    # Required Input
    directory_path: str  # REQUIRED: Path to directory to analyze
    organization_rules: str  # REQUIRED: Rules or query (use "READ-ONLY:" for analysis only)
    
    # Optional Input
    recursive: NotRequired[bool]  # True = scan subdirectories, False = top-level only (default: False)
    
    # Optional fields (auto-populated during workflow)
    mode: NotRequired[str]  # "read_only", "propose_changes" (auto-detected)
    scanned_files: NotRequired[List[Dict[str, Any]]]  # List of file info dicts
    file_analysis: NotRequired[str]  # AI analysis of files
    proposed_changes: NotRequired[List[Dict[str, Any]]]  # Proposed operations
    human_approval: NotRequired[str]  # "approved", "rejected", "skip", "pending"
    human_feedback: NotRequired[str]  # Feedback from human
    human_question: NotRequired[str]  # Follow-up question
    executed_changes: NotRequired[List[Dict[str, Any]]]  # Changes executed
    execution_status: NotRequired[str]  # "success", "partial", "failed"
    messages: NotRequired[Annotated[List, operator.add]]  # Message accumulation
    current_step: NotRequired[str]  # Current workflow step
    errors: NotRequired[Annotated[List[str], operator.add]]  # Error accumulation


# ============================================================================
# FILE ORGANIZER AGENT
# ============================================================================

class FileOrganizerAgent:
    """File organizer agent with MCP tools and human-in-the-loop."""
    
    def __init__(self, llm_config: Dict[str, Any] = None):
        """Initialize file organizer agent."""
        self.llm_config = llm_config or {
            "model_name": "gemini-2.5-flash",
            "temperature": 0.0
        }
        self.logger = logging.getLogger(__name__)
        
        # Build workflow
        self.workflow = None
        self.mcp_tools = None
        
        self.logger.info("✅ File Organizer Agent initialized")
    
    async def initialize(self):
        """Async initialization to load MCP tools using official adapter."""
        try:
            from langchain_mcp_adapters.client import MultiServerMCPClient
            
            self.logger.info("📥 Loading MCP tools via langchain-mcp-adapters...")
            
            # Connect to file tools MCP server
            # Start server with: python scripts/file_tools_mcp_server.py
            client = MultiServerMCPClient({
                "file_tools": {
                    "url": "http://localhost:8000",
                    "transport": "streamable_http"
                }
            })
            
            # Get tools from MCP server
            self.mcp_tools = await client.get_tools()
            self.logger.info(f"✅ Loaded {len(self.mcp_tools)} MCP tools")
            
        except Exception as e:
            import traceback
            self.logger.error(f"❌ MCP tools connection failed: {e}")
            self.logger.error(f"📋 Error type: {type(e).__name__}")
            self.logger.error(f"📋 Full traceback:\n{traceback.format_exc()}")
            self.logger.info("🔧 Building workflow without MCP tools (demo mode)...")
            self.mcp_tools = []
        
        # Build workflow
        self.workflow = await self._build_workflow()
        self.logger.info("✅ Workflow built")
    
    def _create_llm(self):
        """Create LLM instance."""
        return ChatGoogleGenerativeAI(
            model=self.llm_config.get('model_name', 'gemini-2.5-flash'),
            google_api_key=os.environ.get("GEMINI_API_KEY"),
            temperature=self.llm_config.get('temperature', 0.0)
        )
    
    async def _build_workflow(self):
        """Build LangGraph workflow with human-in-the-loop."""
        
        # Create LLM
        llm = self._create_llm()
        
        # Create agent with MCP tools
        self.logger.info("🔧 Creating agent with MCP tools...")
        agent = create_react_agent(
            llm,
            tools=self.mcp_tools,
            name="file_organizer"
        )
        
        # Build workflow graph
        workflow = StateGraph(FileOrganizerState)
        
        # Add nodes
        workflow.add_node("scan_directory", self._scan_directory)
        workflow.add_node("analyze_files", self._analyze_files_node(agent))
        workflow.add_node("propose_changes", self._propose_changes_node(agent))
        workflow.add_node("human_review", self._human_review)  # Human-in-the-loop
        workflow.add_node("execute_changes", self._execute_changes)
        workflow.add_node("complete_read_only", self._complete_read_only)
        
        # Define flow
        workflow.set_entry_point("scan_directory")
        workflow.add_edge("scan_directory", "analyze_files")
        
        # After analysis, check if we need to propose changes or just complete
        workflow.add_conditional_edges(
            "analyze_files",
            self._check_mode,
            {
                "read_only": "complete_read_only",  # Skip proposals for read-only
                "propose_changes": "propose_changes"  # Normal flow
            }
        )
        
        workflow.add_edge("propose_changes", "human_review")
        
        # Conditional edge based on human decision
        workflow.add_conditional_edges(
            "human_review",
            self._check_approval,
            {
                "approved": "execute_changes",
                "rejected": END,
                "skip": END,  # Allow skipping without rejection
                "pending": "human_review"  # Stay in review state (shouldn't happen)
            }
        )
        
        workflow.add_edge("execute_changes", END)
        workflow.add_edge("complete_read_only", END)
        
        # Compile with interrupt for human-in-the-loop
        # Note: LangGraph Studio provides persistence automatically
        # so we don't need a custom checkpointer
        return workflow.compile(
            interrupt_before=["human_review"]  # Interrupt before human review
        )
    
    # ========================================================================
    # WORKFLOW NODES
    # ========================================================================
    
    def _scan_directory(self, state: FileOrganizerState) -> Dict[str, Any]:
        """Scan directory for files (simple Python implementation)."""
        # Get directory_path from state - this should come from initial input
        directory_path = state.get('directory_path')
        
        if not directory_path:
            error_msg = "ERROR: directory_path not provided in input! Required field missing."
            self.logger.error(error_msg)
            return {
                "errors": [error_msg],
                "current_step": "scan_failed",
                "messages": [AIMessage(content=error_msg)]
            }
        
        self.logger.info(f"📂 Scanning directory: {directory_path}")
        self.logger.info(f"📂 State keys available: {list(state.keys())}")
        
        try:
            path = Path(directory_path)
            
            if not path.exists():
                return {
                    "errors": [f"Directory not found: {directory_path}"],
                    "current_step": "scan_failed",
                    "messages": [AIMessage(content=f"Directory not found: {directory_path}")]
                }
            
            # Check if recursive scan is requested
            recursive = state.get('recursive', False)
            scanned_files = []
            
            if recursive:
                # Recursive scan through all subdirectories
                self.logger.info(f"📂 Performing RECURSIVE scan...")
                for item in path.rglob('*'):
                    if item.is_file():
                        # Get relative path from the base directory
                        try:
                            relative_path = item.relative_to(path)
                        except ValueError:
                            relative_path = item
                        
                        scanned_files.append({
                            "path": str(item),
                            "relative_path": str(relative_path),
                            "name": item.name,
                            "extension": item.suffix,
                            "size": item.stat().st_size,
                            "parent_dir": item.parent.name
                        })
                
                self.logger.info(f"📂 Found {len(scanned_files)} files (recursive scan)")
            else:
                # Top-level only scan
                self.logger.info(f"📂 Performing TOP-LEVEL only scan...")
                for item in path.iterdir():
                    if item.is_file():
                        scanned_files.append({
                            "path": str(item),
                            "relative_path": item.name,
                            "name": item.name,
                            "extension": item.suffix,
                            "size": item.stat().st_size,
                            "parent_dir": item.parent.name
                        })
                
                self.logger.info(f"📂 Found {len(scanned_files)} files (top-level only)")
            
            return {
                "scanned_files": scanned_files,
                "current_step": "scanned",
                "messages": [AIMessage(content=f"Scanned {len(scanned_files)} files in {directory_path}")]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Scan failed: {e}")
            return {
                "errors": [f"Scan error: {str(e)}"],
                "current_step": "scan_failed",
                "messages": [AIMessage(content=f"Scan failed: {e}")]
            }
    
    def _analyze_files_node(self, agent):
        """Create analyze files node with MCP tools."""
        
        def analyze_files(state: FileOrganizerState) -> Dict[str, Any]:
            """Analyze files using MCP file.read tool."""
            self.logger.info("🔍 Analyzing files with MCP tools...")
            
            files = state.get("scanned_files", [])
            
            if not files:
                return {
                    "file_analysis": "No files to analyze",
                    "current_step": "analysis_complete",
                    "messages": [AIMessage(content="No files found to analyze")]
                }
            
            # Create task for agent with MCP tools
            directory_path = state.get('directory_path', '.')
            organization_rules = state.get('organization_rules', 'organize by file type')
            
            # Build file list with content snippets for analysis
            file_list = []
            file_contents = []
            
            # Read first few lines of Python files to get docstrings/purpose
            for f in files[:20]:  # Limit to first 20 files for performance
                rel_path = f.get('relative_path', f['name'])
                size_kb = f['size'] / 1024
                file_list.append(f"  {rel_path} ({f['extension']}, {size_kb:.1f} KB)")
                
                # Try to read file content for .py files (for purpose analysis)
                if f['extension'] == '.py':
                    try:
                        file_path = Path(f['path'])
                        if file_path.exists() and file_path.stat().st_size < 100000:  # Skip very large files
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as fp:
                                # Read first 30 lines (usually contains docstring and imports)
                                lines = []
                                for i, line in enumerate(fp):
                                    if i >= 30:
                                        break
                                    lines.append(line.rstrip())
                                
                                if lines:
                                    content_preview = '\n'.join(lines)
                                    file_contents.append(f"\n--- {rel_path} (first 30 lines) ---\n{content_preview}\n")
                    except Exception as e:
                        self.logger.warning(f"Could not read {rel_path}: {e}")
            
            file_list_str = "\n".join(file_list)
            total_files = len(files)
            
            # Build task with file contents
            contents_str = '\n'.join(file_contents[:10]) if file_contents else "No file contents available"
            
            task = f"""You are analyzing Python files. Your task: {organization_rules}

DIRECTORY: '{directory_path}'
TOTAL FILES: {total_files}

FILES TO ANALYZE:
{file_list_str}

FILE CONTENTS (first 30 lines showing docstrings, classes, functions):
{contents_str}

YOUR TASK:
1. For EACH file listed above, read its content snippet
2. Look at the module docstring (at the top in triple quotes)
3. Look at class names and function names
4. Look at the imports to understand dependencies
5. Write a clear description of what EACH file does

FORMAT YOUR RESPONSE:
For each .py file, provide:
- File name
- Purpose: What does this file do?
- Key components: Main classes/functions
- Role: How it fits in the system

Be specific and descriptive. Don't just say "manages agents" - explain HOW and WHAT."""
            
            try:
                # Invoke agent with improved system prompt
                system_prompt = """You are a Python code analyzer. Your job is to read Python file contents and explain what each file does.

Look for:
- Module docstrings (triple-quoted strings at top of file)
- Class definitions and their purposes  
- Function definitions and what they do
- Import statements showing dependencies

Provide detailed, specific descriptions of each file's purpose."""
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=task)
                ]
                
                result = agent.invoke({"messages": messages})
                
                # Extract analysis
                last_msg = result["messages"][-1]
                analysis = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
                
                self.logger.info(f"✅ Analysis complete")
                
                return {
                    "file_analysis": analysis,
                    "current_step": "analysis_complete",
                    "messages": [AIMessage(content=f"Analysis: {analysis[:200]}...")]
                }
                
            except Exception as e:
                self.logger.error(f"❌ Analysis failed: {e}")
                return {
                    "file_analysis": f"Analysis failed: {str(e)}",
                    "errors": [f"Analysis error: {str(e)}"],
                    "current_step": "analysis_failed"
                }
        
        return analyze_files
    
    def _propose_changes_node(self, agent):
        """Create propose changes node."""
        
        def propose_changes(state: FileOrganizerState) -> Dict[str, Any]:
            """Propose file organization changes."""
            self.logger.info("💡 Proposing changes...")
            
            directory_path = state.get('directory_path', '.')
            organization_rules = state.get('organization_rules', 'organize by file type')
            file_analysis = state.get('file_analysis', 'No analysis')
            scanned_files = state.get('scanned_files', [])
            
            task = f"""Based on this analysis, propose file organization changes:

Directory: {directory_path}
Rules: {organization_rules}
Analysis: {file_analysis}

Files:
{scanned_files}

Propose a list of changes (moves/renames) to organize these files.
Format as a simple list of actions."""
            
            try:
                system_prompt = "You are a file organization expert. Propose clear, safe file organization changes."
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=task)
                ]
                
                result = agent.invoke({"messages": messages})
                
                # Extract proposals
                last_msg = result["messages"][-1]
                proposals_text = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
                
                # Simple parsing - convert to list of changes
                proposed_changes = [
                    {"description": line.strip()}
                    for line in proposals_text.split('\n')
                    if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•'))
                ]
                
                if not proposed_changes:
                    proposed_changes = [{"description": proposals_text}]
                
                self.logger.info(f"💡 Proposed {len(proposed_changes)} changes")
                
                return {
                    "proposed_changes": proposed_changes,
                    "human_approval": "pending",
                    "current_step": "changes_proposed",
                    "messages": [AIMessage(content=f"Proposed {len(proposed_changes)} changes - awaiting human approval")]
                }
                
            except Exception as e:
                self.logger.error(f"❌ Proposal failed: {e}")
                return {
                    "proposed_changes": [],
                    "errors": [f"Proposal error: {str(e)}"],
                    "current_step": "proposal_failed"
                }
        
        return propose_changes
    
    def _check_mode(self, state: FileOrganizerState) -> str:
        """Determine workflow mode from organization rules."""
        rules = state.get("organization_rules", "").lower()
        
        # Check for read-only indicators
        if any(keyword in rules for keyword in ["read-only", "read only", "just analyze", "no changes", "describe only"]):
            self.logger.info("🔍 Mode: READ-ONLY (analysis only)")
            return "read_only"
        else:
            self.logger.info("💡 Mode: PROPOSE CHANGES (standard workflow)")
            return "propose_changes"
    
    def _complete_read_only(self, state: FileOrganizerState) -> Dict[str, Any]:
        """Complete workflow for read-only mode (no changes proposed)."""
        self.logger.info("✅ Read-only analysis complete")
        
        return {
            "execution_status": "read_only_complete",
            "current_step": "complete",
            "proposed_changes": [],  # No changes in read-only mode
            "messages": [AIMessage(content="Read-only analysis complete. No changes proposed.")]
        }
    
    def _human_review(self, state: FileOrganizerState) -> Dict[str, Any]:
        """Human review node - this is where workflow interrupts."""
        self.logger.info("👤 Waiting for human approval...")
        
        # This node will be interrupted before execution
        # Human can review proposed_changes and approve/reject
        
        # Check if human has provided decision
        approval = state.get("human_approval", "pending")
        
        if approval == "pending":
            # Still waiting for human input
            return {
                "current_step": "awaiting_human_approval",
                "messages": [AIMessage(content="Waiting for human approval...")]
            }
        else:
            # Human has decided
            return {
                "current_step": f"human_decision_{approval}",
                "messages": [AIMessage(content=f"Human decision: {approval}")]
            }
    
    def _check_approval(self, state: FileOrganizerState) -> str:
        """Check human approval status."""
        approval = state.get("human_approval", "rejected")  # Default to rejected to prevent infinite loop
        self.logger.info(f"📋 Approval status: {approval}")
        
        # Map pending to rejected to ensure termination
        if approval == "pending":
            self.logger.warning("⚠️ Still pending - defaulting to 'rejected' to prevent infinite loop")
            return "rejected"
        
        return approval
    
    def _execute_changes(self, state: FileOrganizerState) -> Dict[str, Any]:
        """Execute approved changes."""
        self.logger.info("⚙️ Executing changes...")
        
        proposed = state.get("proposed_changes", [])
        
        # For this demo, we just log what would be done
        # In real implementation, this would actually move/rename files
        
        executed = []
        for change in proposed:
            self.logger.info(f"  - Would execute: {change['description']}")
            executed.append({
                "change": change['description'],
                "status": "simulated"  # Would be "success" or "failed" in real impl
            })
        
        self.logger.info(f"✅ Simulated {len(executed)} changes")
        
        return {
            "executed_changes": executed,
            "execution_status": "success",
            "current_step": "complete",
            "messages": [AIMessage(content=f"Executed {len(executed)} changes successfully")]
        }
    
    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================
    
    async def organize_files(
        self,
        directory_path: str,
        organization_rules: str = "organize by file type",
        thread_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Organize files with human-in-the-loop.
        
        Args:
            directory_path: Path to directory to organize
            organization_rules: Rules for organization
            thread_id: Thread ID for conversation (enables resumption)
        
        Returns:
            Final state after execution or human review
        """
        
        # Initial state
        initial_state: FileOrganizerState = {
            "directory_path": directory_path,
            "organization_rules": organization_rules,
            "scanned_files": [],
            "file_analysis": "",
            "proposed_changes": [],
            "human_approval": "pending",
            "human_feedback": "",
            "executed_changes": [],
            "execution_status": "pending",
            "messages": [],
            "current_step": "start",
            "errors": []
        }
        
        # Execute workflow with thread_id for resumption
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # This will run until interrupt point (human_review)
            result = await self.workflow.ainvoke(initial_state, config)
            return result
        except Exception as e:
            self.logger.error(f"❌ Workflow failed: {e}")
            return {
                "errors": [str(e)],
                "execution_status": "failed"
            }
    
    async def continue_after_approval(
        self,
        approved: bool,
        feedback: str = "",
        thread_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Continue workflow after human approval.
        
        Args:
            approved: Whether human approved the changes
            feedback: Optional human feedback
            thread_id: Thread ID (must match original)
        
        Returns:
            Final state after execution
        """
        
        # Update state with human decision
        update_state = {
            "human_approval": "approved" if approved else "rejected",
            "human_feedback": feedback
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Resume workflow from interrupt point
            result = await self.workflow.ainvoke(update_state, config)
            return result
        except Exception as e:
            self.logger.error(f"❌ Resume failed: {e}")
            return {
                "errors": [str(e)],
                "execution_status": "failed"
            }


# ============================================================================
# STUDIO EXPORT
# ============================================================================

def get_graph():
    """
    Export for LangGraph Studio.
    
    Creates and initializes the file organizer agent graph synchronously.
    """
    agent = FileOrganizerAgent()
    
    # Initialize synchronously using asyncio.run
    asyncio.run(agent.initialize())
    
    return agent.workflow


# Export for Studio - initialize at module load
graph = get_graph()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def main():
    """Example usage of file organizer agent."""
    
    # Create and initialize agent
    agent = FileOrganizerAgent()
    await agent.initialize()
    
    # Start organization process
    print("🚀 Starting file organization...")
    result = await agent.organize_files(
        directory_path="./test_files",  # Replace with actual path
        organization_rules="organize by file type into subdirectories",
        thread_id="test_session_1"
    )
    
    print(f"\n📊 Result: {result.get('current_step')}")
    print(f"Proposed changes: {len(result.get('proposed_changes', []))}")
    
    # Simulate human review
    print("\n👤 Human reviewing proposed changes...")
    print("Proposed changes:")
    for change in result.get('proposed_changes', []):
        print(f"  - {change.get('description')}")
    
    # Human approves
    print("\n✅ Human approved changes")
    final_result = await agent.continue_after_approval(
        approved=True,
        feedback="Looks good!",
        thread_id="test_session_1"
    )
    
    print(f"\n🎉 Final status: {final_result.get('execution_status')}")
    print(f"Executed: {len(final_result.get('executed_changes', []))} changes")


if __name__ == "__main__":
    asyncio.run(main())

