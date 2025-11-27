# Implementation Plan: US-AGILE-FACTORY-001 - Agile Software Factory (Website/Streamlit Focus)

**User Story**: US-AGILE-FACTORY-001  
**Status**: 📋 Planning  
**Created**: 2025-10-28  
**Updated**: 2025-10-28  
**Approach**: Full Agent System from Start → Incremental Enhancement

## 🎯 Project Focus

**Primary Goal**: Build an agent system capable of creating interactive websites and Streamlit apps for data analysis.

**Initial Languages**: HTML and Python

**Target Outputs**:
- Interactive HTML websites (with CSS, JavaScript)
- Streamlit applications for data analysis
- Complete, tested, documented projects

## 🏗️ Architecture Overview

### Agent Roles (All from Start)

1. **Requirements Analyst** (Regular Agent)
   - Analyzes user story
   - Extracts functional and non-functional requirements
   - Uses existing `requirements_analyst` agent with prompt loader

2. **Architecture Designer** (Regular Agent)
   - Designs system architecture
   - Creates component structure
   - Uses existing `architecture_designer` agent with prompt loader

3. **Code Generator** (Regular Agent with Tools)
   - Generates code files (HTML, Python, CSS, JS)
   - Uses custom `write_file` tool for artifact creation
   - Uses Python REPL tool for code execution/testing
   - Uses website test tool for HTML validation

4. **Code Reviewer** (Regular Agent)
   - Reviews generated code
   - Provides feedback for improvements
   - Uses existing `code_reviewer` agent with prompt loader
   - **Feedback Loop**: Can request code revisions (with loop prevention)

5. **Testing Agent** (Regular Agent with Tools)
   - Generates and executes tests
   - Uses Python REPL tool for test execution
   - Uses website test tool for HTML/Streamlit testing
   - **Feedback Loop**: Can request code fixes based on test failures (with loop prevention)

6. **Documentation Generator** (Regular Agent with Tools)
   - Generates comprehensive documentation
   - Uses custom `write_file` tool for documentation files
   - Creates README, API docs, user guides

### Tools Required

1. **Python REPL Tool**
   - Execute Python code snippets
   - Run Streamlit apps
   - Execute tests
   - Validate code syntax

2. **Website Test Tool**
   - Test HTML pages (load, validate structure)
   - Test Streamlit apps (start, interact, validate)
   - Check for broken links, accessibility
   - Validate responsive design

3. **File Operations** (via Custom Tools)
   - `write_file`: Create code and documentation files (custom tool)
   - `read_file`: Read existing files for context (custom tool)
   - `list_files`: Browse project structure (custom tool)

4. **Additional Useful Tools**
   - Code analysis tool (linting, formatting)
   - Dependency checker (requirements.txt validation)
   - Git operations (optional, for later phases)

## 📊 Phase 0: Minimum Viable Agent System (Week 1-2)

### Goal
Build complete agent system with all roles, HITL checkpoints, feedback loops, and tools.

### Complete Workflow (With HITL and Feedback Loops)

```
START
  ↓
[HITL #1] Story Input & Review
  ↓ (approved)
[1] Requirements Analyst Node
  ↓
[HITL #2] Requirements Review
  ↓ (approved)
[2] Architecture Designer Node
  ↓
[HITL #3] Architecture Review
  ↓ (approved)
[3] Code Generator Node (Regular Agent with write_file, Python REPL, website test tools)
  ↓
[HITL #4] Code Generation Review
  ↓ (approved)
[4] Code Reviewer Node
  ↓
[5] Review Decision Router
  ├→ [3] Code Generator (if needs_revision, max 3 iterations)
  └→ [6] Testing Agent (if approved)
  ↓
[6] Testing Agent Node (Regular Agent with Python REPL, website test tools)
  ↓
[7] Test Decision Router
  ├→ [3] Code Generator (if tests fail, max 3 iterations)
  └→ [8] Documentation Generator (if tests pass)
  ↓
[8] Documentation Generator Node (Regular Agent with write_file tool)
  ↓
[HITL #5] Final Review & Approval
  ↓ (approved)
END
```

**Key Features**:
- ✅ All 6 agent roles from start
- ✅ HITL between each major step
- ✅ Feedback loops: Code Reviewer ↔ Code Generator, Testing Agent ↔ Code Generator
- ✅ Loop prevention: Max 3 iterations per feedback loop
- ✅ LangGraph checkpointers at all relevant nodes
- ✅ Tools: Python REPL, website test, file operations

### Acceptance Criteria - Phase 0

#### Infrastructure
- [ ] **AC-0.1**: Create `agents/agile_factory/` directory structure
- [ ] **AC-0.2**: Define complete LangGraph state schema with all agent outputs
- [ ] **AC-0.3**: Set up LangGraph checkpointer (SqliteSaver) for state persistence
- [ ] **AC-0.4**: Implement prompt loading system using existing `get_agent_prompt_loader`

#### Tools Implementation
- [ ] **AC-0.5**: Create Python REPL tool (execute Python code, run Streamlit apps)
- [ ] **AC-0.6**: Create website test tool (test HTML pages, Streamlit apps)
- [ ] **AC-0.7**: Create custom write_file tool for file operations

#### Agent Nodes
- [ ] **AC-0.8**: Implement Requirements Analyst Node (using existing agent + prompt loader)
- [ ] **AC-0.9**: Implement Architecture Designer Node (using existing agent + prompt loader)
- [ ] **AC-0.10**: Implement Code Generator Node (Regular Agent with write_file, Python REPL, website test tools)
- [ ] **AC-0.11**: Implement Code Reviewer Node (using existing agent + prompt loader)
- [ ] **AC-0.12**: Implement Testing Agent Node (Regular Agent with Python REPL, website test tools)
- [ ] **AC-0.13**: Implement Documentation Generator Node (Regular Agent with write_file tool)

#### HITL Implementation
- [ ] **AC-0.14**: Implement HITL Story Input & Review checkpoint
- [ ] **AC-0.15**: Implement HITL Requirements Review checkpoint
- [ ] **AC-0.16**: Implement HITL Architecture Review checkpoint
- [ ] **AC-0.17**: Implement HITL Code Generation Review checkpoint
- [ ] **AC-0.18**: Implement HITL Final Review & Approval checkpoint

#### Feedback Loops with Loop Prevention
- [x] **AC-0.19**: Implement Review Decision Router (Code Reviewer → Code Generator loop, max 3 iterations)
- [x] **AC-0.20**: Implement Test Decision Router (Testing Agent → Code Generator loop, max 3 iterations)
- [x] **AC-0.21**: Add iteration counters to state for loop prevention
- [x] **AC-0.22**: Add max_iterations check before allowing feedback loops

#### Workflow Integration
- [ ] **AC-0.23**: Build complete LangGraph workflow with all nodes and edges
- [ ] **AC-0.24**: Integrate checkpointers at relevant nodes (after each major step)
- [ ] **AC-0.25**: Test end-to-end: User story → Complete website/Streamlit app

### Technical Implementation - Phase 0

#### Directory Structure
```
agents/agile_factory/
├── __init__.py
├── workflow.py                    # Main LangGraph workflow
├── state/
│   └── agile_state.py             # Complete state schema
├── nodes/
│   ├── requirements_node.py       # Requirements Analyst
│   ├── architecture_node.py       # Architecture Designer
│   ├── code_generator_node.py     # Code Generator (Regular Agent with tools)
│   ├── code_reviewer_node.py      # Code Reviewer
│   ├── testing_node.py            # Testing Agent (Regular Agent with tools)
│   ├── documentation_node.py       # Documentation Generator (Regular Agent with tools)
│   └── routers.py                 # Decision routers for feedback loops
├── tools/
│   ├── python_repl_tool.py        # Python REPL execution tool
│   ├── website_test_tool.py       # Website/Streamlit testing tool
│   └── file_extraction.py         # Extract files from workspace directory
└── hitl/
    ├── hitl_checkpoints.py        # HITL checkpoint implementations
    └── hitl_ui.py                 # HITL user interface (console/Streamlit)
```

#### Complete State Schema
```python
from typing import TypedDict, Dict, Any, List, Optional

class AgileFactoryState(TypedDict, total=False):
    """Complete state for Agile Factory workflow."""
    
    # Input
    user_story: str                    # Raw user story text
    project_type: str                  # "website" or "streamlit_app"
    
    # Agent Outputs
    requirements: Dict[str, Any]       # From requirements_analyst
    architecture: Dict[str, Any]       # From architecture_designer
    code_files: Dict[str, str]         # From code_generator (path → content)
    code_review: Dict[str, Any]        # From code_reviewer
    test_results: Dict[str, Any]       # From testing_agent
    documentation_files: Dict[str, str] # From documentation_generator
    
    # Feedback Loop Control
    code_review_iteration_count: int   # Iterations for code_reviewer ↔ coder loop
    test_iteration_count: int          # Iterations for testing_agent ↔ coder loop
    max_iterations: int                # Safety limit (default: 3)
    
    # HITL State
    hitl_approvals: Dict[str, bool]    # Track approvals at each checkpoint
    hitl_feedback: Dict[str, str]      # Store feedback at each checkpoint
    current_checkpoint: str            # Current HITL checkpoint name
    
    # Control
    status: str                        # "processing", "complete", "error", "needs_revision"
    errors: List[str]
    thread_id: str                     # For checkpointer persistence
    current_node: str                  # Track current workflow node
```

#### Prompt Loading Pattern
```python
from prompts import get_agent_prompt_loader

def requirements_node(state: AgileFactoryState) -> AgileFactoryState:
    """Requirements Analyst Node using existing agent with prompt loader."""
    from agents.development.requirements_analyst import RequirementsAnalyst
    
    # Load prompt using existing system
    prompt_loader = get_agent_prompt_loader("requirements_analyst_v1")
    system_prompt = prompt_loader.get_system_prompt()
    
    # Create agent with loaded prompt
    agent = RequirementsAnalyst(
        config=config,
        gemini_client=gemini_client,
        system_prompt=system_prompt  # Use loaded prompt
    )
    
    # Execute agent
    agent_state = {
        "project_context": state.get("user_story", ""),
        "project_type": state.get("project_type", "website")
    }
    
    result = await agent.execute(agent_state)
    state["requirements"] = result.get("requirements", {})
    
    return state
```

#### Python REPL Tool Implementation
```python
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any

class PythonREPLTool:
    """Tool for executing Python code and running Streamlit apps."""
    
    def __init__(self, python_executable: str = "C:\\App\\Anaconda\\python.exe"):
        self.python_executable = python_executable
    
    def execute_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute Python code snippet.
        
        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Execution result with stdout, stderr, return_code
        """
        try:
            result = subprocess.run(
                [self.python_executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(Path.cwd())
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutError:
            return {
                "success": False,
                "error": f"Execution timeout after {timeout}s"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_streamlit_app(self, app_file: str, port: int = 8501, timeout: int = 60) -> Dict[str, Any]:
        """
        Run Streamlit app and validate it starts.
        
        Args:
            app_file: Path to Streamlit app file
            port: Port to run app on
            timeout: Timeout for app startup
            
        Returns:
            Validation result
        """
        try:
            # Start Streamlit app in background
            process = subprocess.Popen(
                [self.python_executable, "-m", "streamlit", "run", app_file, "--server.port", str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait briefly to check if it starts
            import time
            time.sleep(5)
            
            # Check if process is still running
            if process.poll() is None:
                # App started successfully
                process.terminate()
                return {
                    "success": True,
                    "message": f"Streamlit app started successfully on port {port}"
                }
            else:
                # App failed to start
                stdout, stderr = process.communicate()
                return {
                    "success": False,
                    "error": stderr or stdout,
                    "return_code": process.returncode
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

#### Website Test Tool Implementation
```python
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict, Any, List

class WebsiteTestTool:
    """Tool for testing HTML websites and Streamlit apps."""
    
    def test_html_file(self, html_file: str) -> Dict[str, Any]:
        """
        Test HTML file for structure and validity.
        
        Args:
            html_file: Path to HTML file
            
        Returns:
            Test results with validation status
        """
        try:
            html_path = Path(html_file)
            if not html_path.exists():
                return {
                    "success": False,
                    "error": f"HTML file not found: {html_file}"
                }
            
            # Read and parse HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Basic validation
            issues = []
            
            # Check for required elements
            if not soup.find('html'):
                issues.append("Missing <html> tag")
            if not soup.find('head'):
                issues.append("Missing <head> tag")
            if not soup.find('body'):
                issues.append("Missing <body> tag")
            
            # Check for broken links (if any)
            links = soup.find_all('a', href=True)
            broken_links = []
            for link in links:
                href = link['href']
                if href.startswith('http'):
                    try:
                        response = requests.head(href, timeout=5)
                        if response.status_code >= 400:
                            broken_links.append(href)
                    except:
                        broken_links.append(href)
            
            return {
                "success": len(issues) == 0,
                "issues": issues,
                "broken_links": broken_links,
                "link_count": len(links),
                "has_title": soup.find('title') is not None,
                "has_meta_charset": soup.find('meta', charset=True) is not None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_streamlit_app(self, app_file: str) -> Dict[str, Any]:
        """
        Validate Streamlit app file structure.
        
        Args:
            app_file: Path to Streamlit app file
            
        Returns:
            Validation results
        """
        try:
            app_path = Path(app_file)
            if not app_path.exists():
                return {
                    "success": False,
                    "error": f"Streamlit app not found: {app_file}"
                }
            
            # Read file and check for Streamlit imports
            with open(app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            
            # Check for Streamlit import
            if 'import streamlit' not in content and 'from streamlit' not in content:
                issues.append("Missing Streamlit import")
            
            # Check for basic Streamlit usage
            if 'st.' not in content:
                issues.append("No Streamlit components found (st.*)")
            
            return {
                "success": len(issues) == 0,
                "issues": issues,
                "file_size": len(content),
                "has_streamlit_import": 'import streamlit' in content or 'from streamlit' in content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

#### Code Generator Node (Regular Agent with Tools)
```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from prompts import get_agent_prompt_loader
from agents.agile_factory.tools.custom_write_file import create_write_file_tool
from agents.agile_factory.tools.langchain_tools import get_agile_factory_tools
from pathlib import Path

def code_generator_node(state: AgileFactoryState) -> AgileFactoryState:
    """Code Generator Node using regular LangChain agent with tools."""
    
    # Load prompt using existing system
    prompt_loader = get_agent_prompt_loader("code_generator_v1")
    system_prompt = prompt_loader.get_system_prompt()
    
    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        convert_system_message_to_human=True
    )
    
    # Create workspace directory
    project_root = Path(__file__).parent.parent.parent.parent
    thread_id = state.get("thread_id", "default")
    workspace_dir = project_root / "agile_factory_workspace" / f"code_gen_{thread_id}"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    # Create tools
    custom_tools = get_agile_factory_tools()  # Python REPL, website test tools
    write_file_tool = create_write_file_tool(workspace_dir)  # Custom write_file tool
    all_tools = custom_tools + [write_file_tool]
    
    # Create agent with tools using LangChain's agent framework
    # Use create_react_agent or similar pattern
    from langchain.agents import create_react_agent
    from langchain import hub
    
    # Create agent executor
    agent = create_react_agent(llm, all_tools)
    agent_executor = AgentExecutor(agent=agent, tools=all_tools, verbose=True)
    
    # Prepare task message
    task_message = f"""Generate code for a {state.get('project_type', 'website')} based on:
    
Requirements: {state.get('requirements', {})}
Architecture: {state.get('architecture', {})}

Use write_file to create all code files.
Use Python REPL tool to test Python code.
Use website test tool to validate HTML/Streamlit apps."""
    
    # Invoke agent
    result = agent_executor.invoke({
        "input": task_message,
        "system": system_prompt
    })
    
    # Extract generated files from workspace directory
    from agents.agile_factory.tools.file_extraction import extract_files_from_directory
    state["code_files"] = extract_files_from_directory(
        str(workspace_dir),
        extensions=['.py', '.html', '.css', '.js', '.json', '.txt', '.md']
    )
    
    return state
```

#### Feedback Loop Router (With Loop Prevention)
```python
def review_decision_router(state: AgileFactoryState) -> str:
    """
    Route after code review: loop back to code generator or continue.
    
    Prevents infinite loops with max_iterations check.
    """
    code_review = state.get("code_review", {})
    iteration_count = state.get("code_review_iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    
    # Check if review passed
    review_passed = code_review.get("quality_gate_passed", False)
    
    if review_passed:
        # Review passed, continue to testing
        return "testing_agent"
    
    # Review failed, check iteration limit
    if iteration_count >= max_iterations:
        logger.warning(f"Max iterations ({max_iterations}) reached for code review loop")
        # Force continue despite failures (with warning)
        return "testing_agent"
    
    # Loop back to code generator for revision
    logger.info(f"Code review failed, looping back to code generator (iteration {iteration_count + 1}/{max_iterations})")
    return "code_generator"

def test_decision_router(state: AgileFactoryState) -> str:
    """
    Route after testing: loop back to code generator or continue.
    
    Prevents infinite loops with max_iterations check.
    """
    test_results = state.get("test_results", {})
    iteration_count = state.get("test_iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    
    # Check if tests passed
    tests_passed = test_results.get("all_tests_passed", False)
    
    if tests_passed:
        # Tests passed, continue to documentation
        return "documentation_generator"
    
    # Tests failed, check iteration limit
    if iteration_count >= max_iterations:
        logger.warning(f"Max iterations ({max_iterations}) reached for test loop")
        # Force continue despite failures (with warning)
        return "documentation_generator"
    
    # Loop back to code generator for fixes
    logger.info(f"Tests failed, looping back to code generator (iteration {iteration_count + 1}/{max_iterations})")
    return "code_generator"
```

#### HITL Checkpoint Implementation
```python
def hitl_checkpoint_node(state: AgileFactoryState, checkpoint_name: str) -> AgileFactoryState:
    """
    Generic HITL checkpoint node.
    
    Args:
        state: Current workflow state
        checkpoint_name: Name of checkpoint (e.g., "requirements_review")
    """
    # Create structured summary for human review
    summary = create_checkpoint_summary(state, checkpoint_name)
    
    # Present to human (console for MVP, Streamlit UI later)
    print("\n" + "="*60)
    print(f"HITL CHECKPOINT: {checkpoint_name.upper()}")
    print("="*60)
    print_summary(summary)
    print("\nOptions:")
    print("  [a]pprove - Continue to next step")
    print("  [r]eject - Restart from beginning")
    print("  [e]dit - Provide feedback for revision")
    print("  [s]kip - Skip this checkpoint (not recommended)")
    
    # Get human input
    feedback = input("\nYour decision (a/r/e/s): ").strip().lower()
    
    # Update state based on feedback
    state["current_checkpoint"] = checkpoint_name
    state["hitl_approvals"][checkpoint_name] = feedback == "a"
    state["hitl_feedback"][checkpoint_name] = feedback
    
    if feedback == "a":
        state["status"] = "approved"
    elif feedback == "r":
        state["status"] = "rejected"
        # Will route back to start
    elif feedback == "e":
        edit_notes = input("Provide feedback: ")
        state["hitl_feedback"][checkpoint_name] = {"action": "edit", "notes": edit_notes}
        state["status"] = "needs_revision"
        # Will route back to previous node
    
    return state
```

#### LangGraph Workflow with Checkpointers
```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

def build_agile_factory_workflow():
    """Build complete Agile Factory workflow with all nodes and checkpointers."""
    
    workflow = StateGraph(AgileFactoryState)
    
    # Add nodes
    workflow.add_node("story_input", story_input_node)
    workflow.add_node("hitl_story_review", lambda s: hitl_checkpoint_node(s, "story_review"))
    workflow.add_node("requirements_analyst", requirements_node)
    workflow.add_node("hitl_requirements_review", lambda s: hitl_checkpoint_node(s, "requirements_review"))
    workflow.add_node("architecture_designer", architecture_node)
    workflow.add_node("hitl_architecture_review", lambda s: hitl_checkpoint_node(s, "architecture_review"))
    workflow.add_node("code_generator", code_generator_node)
    workflow.add_node("hitl_code_review", lambda s: hitl_checkpoint_node(s, "code_generation_review"))
    workflow.add_node("code_reviewer", code_reviewer_node)
    workflow.add_node("testing_agent", testing_node)
    workflow.add_node("documentation_generator", documentation_node)
    workflow.add_node("hitl_final_review", lambda s: hitl_checkpoint_node(s, "final_review"))
    
    # Define flow
    workflow.set_entry_point("story_input")
    workflow.add_edge("story_input", "hitl_story_review")
    
    # HITL routing
    workflow.add_conditional_edges(
        "hitl_story_review",
        lambda s: "requirements_analyst" if s.get("hitl_approvals", {}).get("story_review") else END,
        {
            "requirements_analyst": "requirements_analyst",
            END: END
        }
    )
    
    workflow.add_edge("requirements_analyst", "hitl_requirements_review")
    workflow.add_conditional_edges(
        "hitl_requirements_review",
        lambda s: "architecture_designer" if s.get("hitl_approvals", {}).get("requirements_review") else "requirements_analyst",
        {
            "architecture_designer": "architecture_designer",
            "requirements_analyst": "requirements_analyst"
        }
    )
    
    workflow.add_edge("architecture_designer", "hitl_architecture_review")
    workflow.add_conditional_edges(
        "hitl_architecture_review",
        lambda s: "code_generator" if s.get("hitl_approvals", {}).get("architecture_review") else "architecture_designer",
        {
            "code_generator": "code_generator",
            "architecture_designer": "architecture_designer"
        }
    )
    
    workflow.add_edge("code_generator", "hitl_code_review")
    workflow.add_edge("hitl_code_review", "code_reviewer")
    
    # Feedback loop: code_reviewer → code_generator (with loop prevention)
    workflow.add_conditional_edges(
        "code_reviewer",
        review_decision_router,
        {
            "code_generator": "code_generator",
            "testing_agent": "testing_agent"
        }
    )
    
    # Feedback loop: testing_agent → code_generator (with loop prevention)
    workflow.add_conditional_edges(
        "testing_agent",
        test_decision_router,
        {
            "code_generator": "code_generator",
            "documentation_generator": "documentation_generator"
        }
    )
    
    workflow.add_edge("documentation_generator", "hitl_final_review")
    workflow.add_edge("hitl_final_review", END)
    
    # Set up checkpointer for state persistence
    checkpointer = SqliteSaver.from_conn_string("sqlite:///agile_factory.db")
    
    # Compile with checkpointer
    app = workflow.compile(checkpointer=checkpointer)
    
    return app
```

### Deliverables - Phase 0

- ✅ Complete 6-agent workflow (analyst, designer, coder, reviewer, tester, doc generator)
- ✅ HITL checkpoints between each major step
- ✅ Feedback loops: Code Reviewer ↔ Code Generator, Testing Agent ↔ Code Generator
- ✅ Loop prevention: Max 3 iterations per feedback loop
- ✅ LangGraph checkpointers at all relevant nodes
- ✅ Tools: Python REPL, website test, custom write_file tool
- ✅ Prompt loading using existing `get_agent_prompt_loader` system
- ✅ End-to-end: User story → Complete website/Streamlit app

**Estimated Effort**: 13 story points (2 weeks)

---

## 📊 Phase 1: Enhanced Tools & RAG Integration (Week 3)

### Goal
Add RAG integration and enhance tools for better code quality.

### Acceptance Criteria - Phase 1

- [ ] **AC-1.1**: Integrate RAG for project context (reuse RAGSwarmCoordinator pattern)
- [ ] **AC-1.2**: Add code analysis tool (linting, formatting)
- [ ] **AC-1.3**: Add dependency checker tool
- [ ] **AC-1.4**: Enhance Python REPL tool with better error handling
- [ ] **AC-1.5**: Enhance website test tool with accessibility checks

**Estimated Effort**: 5 story points (1 week)

---

## 📊 Phase 2: Methodology & DevOps (Week 4)

### Goal
Add methodology profiles and DevOps integration.

### Acceptance Criteria - Phase 2

- [ ] **AC-2.1**: Add methodology profiles (Scrum, Kanban, TDD)
- [ ] **AC-2.2**: Integrate methodology RAG for rule enforcement
- [ ] **AC-2.3**: Add DevOps node (Git operations, PR creation)
- [ ] **AC-2.4**: Add final release HITL checkpoint

**Estimated Effort**: 5 story points (1 week)

---

## 🔧 Technical Decisions

### Agent Type Selection

**Regular LangChain Agents with Tools** (for all agents):
- ✅ **Code Generator**: Regular agent with write_file, Python REPL, website test tools
- ✅ **Testing Agent**: Regular agent with Python REPL, website test tools
- ✅ **Documentation Generator**: Regular agent with write_file tool
- ✅ **Requirements Analyst**: Regular agent with structured output (existing agent)
- ✅ **Architecture Designer**: Regular agent with structured output (existing agent)
- ✅ **Code Reviewer**: Regular agent with structured analysis output (existing agent)

### Prompt Loading Strategy

**Use Existing System**:
- All agents use `get_agent_prompt_loader(agent_name)` from `prompts` module
- Prompts loaded from LangSmith Hub or fallback to hardcoded
- Consistent with codebase best practices

### Loop Prevention Strategy

**Pattern from Codebase**:
- Add `iteration_count` to state for each feedback loop
- Set `max_iterations = 3` as safety limit
- Check `iteration_count >= max_iterations` before allowing loops
- Increment `iteration_count` when looping back
- Force continue after max iterations (with warning)

### Checkpointer Strategy

**Placement**:
- After each major agent node (requirements, architecture, code, review, test, docs)
- After each HITL checkpoint
- Enables state recovery and resumption

**Implementation**:
- Use `SqliteSaver` for persistent storage
- Use `thread_id` for conversation tracking
- State persists across sessions

### Tools Integration

**Python REPL Tool**:
- Execute Python code snippets
- Run Streamlit apps
- Execute tests
- Validate syntax

**Website Test Tool**:
- Test HTML structure
- Validate Streamlit apps
- Check links and accessibility
- Test responsive design

**Custom write_file Tool**:
- Custom tool that writes to workspace directory
- Files stored in dedicated workspace per thread
- Extract files directly from workspace directory

---

## 🎯 Success Metrics - Phase 0

### Functionality
- ✅ Complete workflow: User story → Website/Streamlit app
- ✅ All 6 agents execute correctly
- ✅ HITL checkpoints work at each step
- ✅ Feedback loops prevent infinite iterations
- ✅ Tools execute code and test websites
- ✅ State persists across sessions

### Quality
- ✅ Generated code is functional
- ✅ Tests execute successfully
- ✅ HTML/Streamlit apps run correctly
- ✅ Documentation is complete

### Performance
- ✅ Full workflow < 10 minutes (for simple project)
- ✅ Each agent node < 2 minutes
- ✅ HITL checkpoints < 30 seconds

---

**Status**: Ready to start Phase 0  
**Approach**: Full agent system from start with HITL, feedback loops, and tools  
**Estimated Total**: 23 story points over 4 weeks
