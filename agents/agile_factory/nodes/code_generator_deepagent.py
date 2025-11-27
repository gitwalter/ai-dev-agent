"""
Code Generator Node using DeepAgents for Agile Factory workflow.

This version uses DeepAgents library with FilesystemBackend for file operations.
"""

import logging
import os
from pathlib import Path
from agents.agile_factory.state.agile_state import AgileFactoryState
# Note: We don't use LangSmith prompt for DeepAgent - it instructs JSON output which conflicts with tools
# from prompts import get_agent_prompt_loader
from langchain_google_genai import ChatGoogleGenerativeAI
# Messages imported but not directly used - DeepAgent handles message formatting internally
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from agents.agile_factory.tools.langchain_tools import get_agile_factory_tools
from agents.agile_factory.tools.file_extraction import extract_files_from_directory
from agents.agile_factory.tools.custom_write_file import create_write_file_tool

logger = logging.getLogger(__name__)


def code_generator_node_deepagent(state: AgileFactoryState) -> AgileFactoryState:
    """
    Code Generator Node using DeepAgents with FilesystemBackend.
    
    This version leverages DeepAgents' built-in FilesystemBackend for file operations,
    eliminating the need for custom write_file tool.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with generated code files
    """
    try:
        # Get API key
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable must be set")
        
        # NOTE: We don't use the LangSmith prompt (code_generator_v1) because it instructs JSON output
        # which conflicts with tool usage. DeepAgent needs to call tools, not output JSON.
        # We'll create a tool-focused prompt instead.
        
        # Create LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0,
            convert_system_message_to_human=True
        )
        
        # Create dedicated workspace directory for this code generation session
        project_root = Path(__file__).parent.parent.parent.parent
        thread_id = state.get("thread_id", "default")
        workspace_dir = project_root / "agile_factory_workspace" / f"code_gen_deepagent_{thread_id}"
        workspace_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DeepAgent code generator workspace: {workspace_dir}")
        
        # Create custom write_file tool that writes directly to our workspace
        # This ensures files are written even if FilesystemBackend doesn't expose tools properly
        custom_write_file_tool = create_write_file_tool(workspace_dir)
        
        # Get custom tools and add our write_file tool
        custom_tools = get_agile_factory_tools()
        # Add our custom write_file tool (this ensures files go to our workspace)
        all_tools = custom_tools + [custom_write_file_tool]
        
        # Prepare context for code generation
        user_story = state.get("user_story", "")
        requirements = state.get("requirements", {})
        architecture = state.get("architecture", {})
        project_type = state.get("project_type", "website")
        
        # Create a completely new prompt that doesn't mention JSON at all
        # The LangSmith prompt has JSON output instructions that conflict with tool usage
        # We'll create a tool-focused prompt instead
        enhanced_prompt = f"""You are a Code Generator Agent. Your job is to generate production-ready code by CALLING THE write_file TOOL.

CRITICAL: You MUST call tools - do NOT output text descriptions or JSON plans. You MUST use the write_file tool to create files.

You have access to tools - you MUST use them to create files. Do not describe files or create plans - actually call the tools!

PROJECT CONTEXT:
User Story: {user_story}
Project Type: {project_type}

REQUIREMENTS:
{requirements}

ARCHITECTURE:
{architecture}

WORKSPACE DIRECTORY:
{workspace_dir}

YOUR TOOLS:
1. write_file(file_path: str, content: str) - CRITICAL! Use this to create ALL code files
   - file_path: Relative path like "index.html", "app.py", "styles.css"
   - content: Full file content as a string
   - Example: write_file("index.html", "<html><body>Hello</body></html>")
   - Example: write_file("app.py", "import streamlit as st\\nst.title('Hello')")

2. python_repl - Execute Python code to test your generated code
3. html_test_file - Test HTML files
4. streamlit_validate_app - Validate Streamlit apps
5. streamlit_run_app - Run Streamlit apps

YOUR TASK:
Generate code for a {project_type} project by CALLING write_file tool for each file.

FOR WEBSITE PROJECTS:
- Call write_file("index.html", "<complete HTML content>")
- Call write_file("about.html", "<complete HTML content>")
- Call write_file("contact.html", "<complete HTML content>")
- Call write_file("styles.css", "<complete CSS content>")
- Create any other needed files

FOR STREAMLIT APPS:
- Call write_file("app.py", "<complete Python code>")
- Call write_file("requirements.txt", "<dependencies>")
- Create any other needed files

CRITICAL RULES:
1. You MUST call write_file tool - do not describe files!
2. Start calling write_file immediately - no planning phase!
3. Write complete, working code - not placeholders
4. Each file requires a separate write_file call
5. Do not output JSON or describe what you would do - actually do it!

START NOW: Call write_file("index.html", "...") or write_file("app.py", "...") immediately!"""
        
        logger.info("Creating DeepAgent with FilesystemBackend and custom write_file tool...")
        logger.info(f"Number of custom tools: {len(custom_tools)}")
        logger.info(f"Total tools (including write_file): {len(all_tools)}")
        logger.info(f"Tool names: {[getattr(t, 'name', str(t)) for t in all_tools]}")
        logger.info(f"write_file tool included: {any(getattr(t, 'name', '') == 'write_file' for t in all_tools)}")
        logger.info(f"System prompt length: {len(enhanced_prompt)} characters")
        logger.info(f"Workspace directory: {workspace_dir}")
        
        # Create DeepAgent with FilesystemBackend for workspace management
        # Also include custom write_file tool to ensure files are written
        try:
            # Configure FilesystemBackend with our workspace directory
            filesystem_backend = FilesystemBackend(root_dir=str(workspace_dir))
            
            # DeepAgent handles tool binding internally - pass raw LLM
            # DeepAgent will bind tools and execute them automatically
            deep_agent = create_deep_agent(
                model=llm,  # Pass raw LLM - DeepAgent handles tool binding
                tools=all_tools,  # Include custom write_file tool + other tools
                system_prompt=enhanced_prompt,  # Use 'system_prompt' parameter
                backend=filesystem_backend  # FilesystemBackend for additional file operations
            )
            logger.info("DeepAgent created successfully")
            
            if deep_agent is None:
                raise ValueError("create_deep_agent returned None")
                
        except Exception as e:
            logger.error(f"Failed to create DeepAgent: {e}", exc_info=True)
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"Failed to create DeepAgent code generator: {str(e)}")
            state["status"] = "error"
            return state
        
        # Invoke agent with comprehensive error handling
        task_message = f"""Generate code for a {project_type} based on the requirements and architecture provided.

CRITICAL INSTRUCTIONS - YOU MUST USE TOOLS:
1. DO NOT output JSON or describe files - you have write_file tool, USE IT!
2. You MUST call the write_file tool to create ALL code files - START CALLING IT NOW!
3. Create at least one main file (e.g., index.html for websites, app.py for Streamlit) by calling write_file
4. Include all necessary supporting files (CSS, JS, requirements.txt, etc.) by calling write_file for each
5. Write complete, working code - not just placeholders
6. ACTUALLY CALL write_file tool for each file - do not just describe what you would create!

EXAMPLE OF WHAT TO DO:
- Call: write_file("index.html", "<html><head>...</head><body>...</body></html>")
- Call: write_file("styles.css", "body {{ margin: 0; }}")
- Call: write_file("about.html", "<html>...</html>")

EXAMPLE OF WHAT NOT TO DO:
- DO NOT say: "I would create index.html with..."
- DO NOT output: {{"plan": "...", "files": [...]}}
- DO NOT describe files - CALL write_file TOOL INSTEAD!

Focus on:
- Creating production-ready, well-structured code
- Following the architecture design
- Implementing all functional requirements
- Using appropriate technologies for {project_type}
- Including proper error handling and documentation

START CALLING write_file TOOL NOW - DO NOT CREATE A PLAN FIRST!"""
        
        logger.info("Invoking DeepAgent code generator...")
        logger.info(f"Task message length: {len(task_message)} characters")
        
        try:
            # Invoke DeepAgent
            logger.info("Invoking DeepAgent (this will call LLM and use FilesystemBackend)...")
            logger.info(f"Task message preview: {task_message[:200]}...")
            
            # DeepAgents expects messages in this format
            result = deep_agent.invoke({
                "messages": [
                    {"role": "user", "content": task_message}
                ]
            })
            
            logger.info(f"DeepAgent invocation completed. Result type: {type(result)}")
            
            # Ensure we have a result
            if result is None:
                logger.error("CRITICAL: DeepAgent returned None - execution may have failed")
                raise ValueError("DeepAgent returned None - execution failed")
            
            # CRITICAL: DeepAgent uses a virtual filesystem!
            # Files are stored in result["files"] dict, not written directly to disk
            # We need to extract them and write to our workspace directory
            if isinstance(result, dict):
                logger.info(f"DeepAgent returned dict with keys: {list(result.keys())}")
                
                # Debug: Print full result structure for troubleshooting
                logger.debug(f"Full result structure: {result}")
                
                # Check for files in virtual filesystem (FilesystemBackend stores files here)
                virtual_files = result.get("files", {})
                logger.info(f"Checking result keys: {list(result.keys())}")
                logger.info(f"Virtual filesystem files: {len(virtual_files)} files")
                
                if virtual_files:
                    logger.info(f"✅ Found {len(virtual_files)} files in DeepAgent virtual filesystem")
                    logger.info(f"   File paths: {list(virtual_files.keys())[:10]}")
                    
                    # Write files from virtual filesystem to our workspace directory
                    logger.info(f"📝 Writing {len(virtual_files)} files from virtual filesystem to workspace: {workspace_dir}")
                    files_written = 0
                    for file_path, content in virtual_files.items():
                        try:
                            # Resolve file path relative to workspace
                            target_file = workspace_dir / file_path
                            
                            # Ensure parent directory exists
                            target_file.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Write file
                            with open(target_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            files_written += 1
                            logger.info(f"   ✅ Wrote: {file_path} ({len(content)} bytes)")
                        except Exception as e:
                            logger.error(f"   ❌ Failed to write {file_path}: {e}")
                    
                    logger.info(f"✅ Successfully wrote {files_written}/{len(virtual_files)} files to workspace")
                else:
                    logger.warning("⚠️  No files found in DeepAgent virtual filesystem (result['files'])")
                    logger.warning("   This means:")
                    logger.warning("   1. Agent may not have called write_file tool")
                    logger.warning("   2. FilesystemBackend may not have stored files in result['files']")
                    logger.warning("   3. Agent may have returned text/JSON instead of tool calls")
                
                # Also check messages for tool calls (for debugging)
                if "messages" in result:
                    messages = result["messages"]
                    logger.info(f"DeepAgent returned {len(messages)} messages")
                    
                    # Check for tool calls in messages
                    tool_call_count = 0
                    write_file_calls = 0
                    for msg in messages:
                        # Check if message has tool_calls attribute
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            tool_call_count += len(msg.tool_calls)
                            for tool_call in msg.tool_calls:
                                tool_name = tool_call.get('name', 'unknown') if isinstance(tool_call, dict) else getattr(tool_call, 'name', 'unknown')
                                if tool_name == 'write_file':
                                    write_file_calls += 1
                                logger.info(f"  Tool call: {tool_name}")
                        # Also check dict format
                        elif isinstance(msg, dict) and 'tool_calls' in msg:
                            tool_call_count += len(msg.get('tool_calls', []))
                            for tool_call in msg.get('tool_calls', []):
                                tool_name = tool_call.get('name', 'unknown') if isinstance(tool_call, dict) else str(tool_call)
                                if tool_name == 'write_file':
                                    write_file_calls += 1
                                logger.info(f"  Tool call: {tool_name}")
                    
                    logger.info(f"Total tool calls made: {tool_call_count}")
                    logger.info(f"write_file tool calls: {write_file_calls}")
                    
                    # CRITICAL: If we have tool calls but no files, manually execute them
                    if tool_call_count > 0 and not virtual_files:
                        logger.warning("⚠️  Tool calls detected but no files written - manually executing tool calls...")
                        from langchain_core.messages import ToolMessage
                        from langchain_core.tools import Tool
                        
                        # Create tool lookup
                        tool_dict = {tool.name: tool for tool in all_tools if hasattr(tool, 'name')}
                        
                        # Execute any write_file tool calls manually
                        for msg in messages:
                            tool_calls = []
                            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                tool_calls = msg.tool_calls
                            elif isinstance(msg, dict) and 'tool_calls' in msg:
                                tool_calls = msg.get('tool_calls', [])
                            
                            for tool_call in tool_calls:
                                tool_name = tool_call.get('name', 'unknown') if isinstance(tool_call, dict) else getattr(tool_call, 'name', 'unknown')
                                tool_args = tool_call.get('args', {}) if isinstance(tool_call, dict) else getattr(tool_call, 'args', {})
                                
                                if tool_name in tool_dict:
                                    try:
                                        logger.info(f"Manually executing tool: {tool_name} with args: {tool_args}")
                                        tool = tool_dict[tool_name]
                                        result = tool.invoke(tool_args)
                                        logger.info(f"Tool {tool_name} executed successfully: {result}")
                                    except Exception as e:
                                        logger.error(f"Failed to execute tool {tool_name}: {e}")
                    
                    if write_file_calls == 0 and not virtual_files:
                        logger.warning("⚠️  No write_file tool calls detected AND no files in virtual filesystem!")
                        logger.warning("   Agent may have returned a plan instead of executing tool calls")
                    
                    # Log last few messages with full content for debugging
                    for i, msg in enumerate(messages[-5:]):  # Log last 5 messages
                        msg_type = type(msg).__name__ if hasattr(msg, '__class__') else str(type(msg))
                        if isinstance(msg, dict):
                            content_preview = str(msg.get('content', msg))[:500]
                        else:
                            content_preview = str(getattr(msg, 'content', str(msg)))[:500]
                        logger.info(f"Message {i}: {msg_type} - {content_preview}")
                        
                        # Check for tool calls in this message
                        if isinstance(msg, dict):
                            if 'tool_calls' in msg:
                                logger.info(f"  Found tool_calls in message {i}: {msg['tool_calls']}")
                        elif hasattr(msg, 'tool_calls') and msg.tool_calls:
                            logger.info(f"  Found tool_calls in message {i}: {msg.tool_calls}")
                    
                    # If no tool calls found, log full last message for debugging
                    if tool_call_count == 0 and messages:
                        last_msg = messages[-1]
                        logger.warning("⚠️  Last message content (full):")
                        if isinstance(last_msg, dict):
                            logger.warning(f"  {last_msg.get('content', last_msg)}")
                        else:
                            logger.warning(f"  {getattr(last_msg, 'content', str(last_msg))}")
            
        except Exception as e:
            logger.error(f"DeepAgent invocation failed: {e}", exc_info=True)
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"DeepAgent code generator invocation failed: {str(e)}")
            state["status"] = "error"
            
            state["code_generator_error"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            
            return state
        
        # Extract generated files from workspace directory
        code_files = {}
        
        logger.info(f"Extracting files from workspace directory: {workspace_dir}")
        if workspace_dir.exists():
            code_files = extract_files_from_directory(
                str(workspace_dir),
                extensions=['.py', '.html', '.css', '.js', '.json', '.txt', '.md', '.yaml', '.yml', '.toml']
            )
            if code_files:
                logger.info(f"Found {len(code_files)} files in workspace directory")
                for file_path in list(code_files.keys())[:5]:  # Log first 5 files
                    logger.info(f"  - {file_path}")
        
        # Log final result
        if code_files:
            logger.info(f"Successfully extracted {len(code_files)} files from workspace")
        else:
            logger.warning("No files extracted from workspace directory - code_files will be empty")
            logger.warning(f"Checked workspace: {workspace_dir}")
            if workspace_dir.exists():
                try:
                    contents = list(workspace_dir.iterdir())
                    logger.warning(f"Workspace directory exists with {len(contents)} items:")
                    for item in contents[:10]:
                        logger.warning(f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")
                except Exception as e:
                    logger.warning(f"Could not list workspace contents: {e}")
            else:
                logger.warning(f"Workspace directory does not exist: {workspace_dir}")
        
        # Update state with code files AND workspace location
        state["code_files"] = code_files
        state["current_node"] = "code_generator_deepagent"
        
        # Store workspace location in state for reference
        if "workspace_locations" not in state:
            state["workspace_locations"] = {}
        state["workspace_locations"]["code_generator_workspace"] = str(workspace_dir)
        state["workspace_locations"]["absolute_path"] = str(workspace_dir.resolve())
        if code_files:
            state["workspace_locations"]["files_found_in"] = str(workspace_dir)
        
        # Validate that we have code files
        if not code_files:
            logger.warning("No code files extracted - checking workspace directory...")
            logger.info(f"Workspace checked: {workspace_dir}")
            
            if workspace_dir.exists():
                try:
                    all_items = list(workspace_dir.rglob('*'))
                    files_in_ws = [item for item in all_items if item.is_file()]
                    dirs_in_ws = [item for item in all_items if item.is_dir()]
                    logger.info(f"Workspace exists with {len(files_in_ws)} files and {len(dirs_in_ws)} directories")
                    
                    if files_in_ws:
                        logger.info(f"Files found on disk: {[str(f.relative_to(workspace_dir)) for f in files_in_ws[:10]]}")
                        code_files = extract_files_from_directory(
                            str(workspace_dir),
                            extensions=['.py', '.html', '.css', '.js', '.json', '.txt', '.md', '.yaml', '.yml', '.toml']
                        )
                        if code_files:
                            logger.info(f"SUCCESS: Extracted {len(code_files)} files from workspace directory")
                            state["code_files"] = code_files
                        else:
                            logger.error("Files exist on disk but could not be extracted")
                    else:
                        logger.error("No files found in workspace directory - DeepAgent may not have called write_file")
                except Exception as e:
                    logger.error(f"Could not list workspace contents: {e}", exc_info=True)
            else:
                logger.error(f"Workspace directory does not exist: {workspace_dir}")
            
            if not code_files:
                if "errors" not in state:
                    state["errors"] = []
                error_msg = f"DeepAgent code generator did not produce any files. Check workspace: {workspace_dir}"
                state["errors"].append(error_msg)
                state["status"] = "error"
                
                state["code_generator_debug"] = {
                    "workspace_dir": str(workspace_dir),
                    "workspace_exists": workspace_dir.exists()
                }
        else:
            logger.info(f"Code generation complete: {len(code_files)} files generated")
            logger.info(f"Files stored in workspace: {workspace_dir}")
            state["workspace_locations"]["files_found_in"] = str(workspace_dir)
            state["status"] = "processing"
        
    except Exception as e:
        logger.error(f"DeepAgent code generation failed: {e}", exc_info=True)
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"DeepAgent code generation error: {str(e)}")
        state["status"] = "error"
    
    return state

