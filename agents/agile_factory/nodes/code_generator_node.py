"""
Code Generator Node for Agile Factory workflow.

Uses structured JSON output instead of tool calls to reduce LLM invocations.
Files are written programmatically after agent produces structured output.
"""

import logging
import os
import json
import re
from pathlib import Path
from agents.agile_factory.state.agile_state import AgileFactoryState
from prompts import get_agent_prompt_loader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from agents.agile_factory.utils.safe_prompt_formatting import safe_format_prompt, safe_format_prompt_with_validation
from agents.agile_factory.utils.llm_config import get_llm_model
from agents.agile_factory.utils.file_writer import get_workspace_dir
from prompts import get_agent_prompt_loader

logger = logging.getLogger(__name__)


def code_generator_node(state: AgileFactoryState) -> AgileFactoryState:
    """
    Code Generator Node using structured JSON output (NO tool calls).
    
    This node:
    1. Loads prompt and requests structured JSON output
    2. LLM generates all file content in single JSON response
    3. Parses JSON and updates state.code_files
    4. Files are written programmatically after node completes (via wrapper)
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with generated code files in state.code_files
    """
    try:
        # Get API key
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable must be set")
        
        # Get workspace directory (for reference, files written later)
        workspace_dir = get_workspace_dir(state, "code")
        
        logger.info(f"Code generator workspace: {workspace_dir}")
        
        # Prepare context for code generation
        user_story = state.get("user_story", "")
        requirements = state.get("requirements", {})
        architecture = state.get("architecture", {})
        project_type = state.get("project_type", "website")
        
        # Extract file structure from architecture (critical for lite model)
        file_structure = architecture.get("file_structure", {})
        files_to_generate = []
        
        # Try to extract files from different possible structures
        if isinstance(file_structure, dict):
            # Check for "structure" key (list of files, may include directory structure)
            if "structure" in file_structure:
                structure_list = file_structure["structure"]
                # Extract just filenames (remove directory prefixes and indentation)
                for item in structure_list:
                    if isinstance(item, str):
                        # Remove directory prefixes like "project-root/" or "  "
                        cleaned = item.strip().lstrip("./")
                        # Skip directory entries (end with /)
                        if cleaned and not cleaned.endswith("/"):
                            # Extract filename (last part after /)
                            filename = cleaned.split("/")[-1]
                            if filename and filename not in files_to_generate:
                                files_to_generate.append(filename)
            # Check for "files" key
            elif "files" in file_structure:
                files_list = file_structure["files"]
                if isinstance(files_list, list):
                    files_to_generate.extend([f for f in files_list if isinstance(f, str)])
        # Check if it's a list directly
        elif isinstance(file_structure, list):
            for item in file_structure:
                if isinstance(item, str):
                    cleaned = item.strip().lstrip("./")
                    if cleaned and not cleaned.endswith("/"):
                        filename = cleaned.split("/")[-1]
                        if filename and filename not in files_to_generate:
                            files_to_generate.append(filename)
        
        # Also check components for file references
        components = architecture.get("components", [])
        for component in components:
            if isinstance(component, dict):
                # Look for file references in component
                if "files" in component:
                    if isinstance(component["files"], list):
                        for f in component["files"]:
                            if isinstance(f, str) and f not in files_to_generate:
                                files_to_generate.append(f)
                    elif isinstance(component["files"], str) and component["files"] not in files_to_generate:
                        files_to_generate.append(component["files"])
                # Check for file_path or file_name
                for key in ["file_path", "file_name", "file"]:
                    if key in component:
                        file_ref = component[key]
                        if isinstance(file_ref, str) and file_ref not in files_to_generate:
                            # Extract filename if it's a path
                            filename = file_ref.split("/")[-1]
                            if filename not in files_to_generate:
                                files_to_generate.append(filename)
        
        # Ensure we have at least basic files if architecture doesn't specify
        if not files_to_generate:
            if project_type == "website":
                files_to_generate = ["index.html", "styles.css"]
            elif project_type == "streamlit_app":
                files_to_generate = ["app.py", "requirements.txt"]
        
        # Create explicit file list for prompt (numbered for clarity)
        files_list_str = "\n".join([f"{i+1}. {f}" for i, f in enumerate(files_to_generate)])
        logger.info(f"Files to generate (from architecture): {files_to_generate}")
        
        # Convert dicts to strings for safe formatting
        requirements_str = str(requirements) if isinstance(requirements, dict) else requirements
        architecture_str = str(architecture) if isinstance(architecture, dict) else architecture
        
        # Load prompt from LangSmith Hub (source of truth)
        prompt_loader = get_agent_prompt_loader("code_generator_v1")
        system_prompt_template = prompt_loader.get_system_prompt()
        
        # Ensure prompt is a string (not PromptTemplate object)
        if not isinstance(system_prompt_template, str):
            logger.warning(f"Prompt is not a string (type: {type(system_prompt_template)}), converting...")
            if hasattr(system_prompt_template, 'template'):
                system_prompt_template = system_prompt_template.template
            else:
                system_prompt_template = str(system_prompt_template)
        
        # Validate prompt was loaded
        if not system_prompt_template or len(system_prompt_template.strip()) == 0:
            error_msg = "Failed to load system prompt template - prompt is empty"
            logger.error(error_msg)
            return {
                "errors": state.get("errors", []) + [error_msg],
                "status": "error",
                "current_node": "code_generator"
            }
        
        logger.info(f"Loaded prompt template from LangSmith Hub: {len(system_prompt_template)} characters")
        
        # Format system prompt with dynamic context using safe formatting
        try:
            system_prompt, missing_placeholders = safe_format_prompt_with_validation(
                system_prompt_template,
                user_story=user_story,
                project_type=project_type,
                requirements=requirements_str,
                architecture=architecture_str,
                workspace_dir=str(workspace_dir),
                files_to_generate=files_list_str
            )
            
            if missing_placeholders:
                logger.warning(f"Some placeholders not replaced: {missing_placeholders}")
            
            logger.info(f"Formatted prompt: {len(system_prompt)} characters")
        except Exception as e:
            error_msg = f"Prompt formatting failed: {e}"
            logger.error(error_msg, exc_info=True)
            return {
                "errors": state.get("errors", []) + [error_msg],
                "status": "error",
                "current_node": "code_generator"
            }
        
        # Create LLM with configurable model (NO tools bound)
        model_name = get_llm_model(state)
        logger.info(f"Using LLM model: {model_name} (structured JSON output, NO tools)")
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0,
            convert_system_message_to_human=True
        )
        
        # Invoke LLM directly (NO tool calls)
        task_message = f"Generate code files as JSON for the {project_type} project. Output format: {{\"files\": {{\"filename\": \"content\"}}}}"
        
        logger.info("Calling LLM for structured JSON output (NO tool calls)...")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task_message)
        ]
        
        try:
            response = llm.invoke(messages)
            output = response.content.strip()
            
            logger.info(f"LLM response received: {len(output)} characters")
            
            # Parse JSON response
            # Extract JSON from markdown code block if present
            json_match = re.search(r'```json\s*(\{.*\})\s*```', output, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object boundaries
                first_brace = output.find('{')
                if first_brace != -1:
                    brace_count = 0
                    json_start = first_brace
                    for i, char in enumerate(output[first_brace:], start=first_brace):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_str = output[json_start:i+1]
                                break
                    else:
                        json_str = output[first_brace:]
                else:
                    json_str = output
            
            # Clean trailing commas
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            # Parse JSON
            result_data = json.loads(json_str)
            code_files = result_data.get("files", {})
            
            if not code_files:
                logger.warning("No files found in JSON response")
                # Try alternative structure
                if isinstance(result_data, dict) and len(result_data) > 0:
                    # Maybe files are at top level
                    code_files = {k: v for k, v in result_data.items() if isinstance(v, str)}
            
            logger.info(f"Parsed {len(code_files)} files from JSON response")
            for file_path in list(code_files.keys())[:5]:
                logger.info(f"  - {file_path} ({len(code_files[file_path])} bytes)")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response preview: {output[:500]}")
            return {
                "errors": state.get("errors", []) + [f"Failed to parse JSON response: {str(e)}"],
                "status": "error",
                "current_node": "code_generator"
            }
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}", exc_info=True)
            return {
                "errors": state.get("errors", []) + [f"Code generator error: {str(e)}"],
                "status": "error",
                "current_node": "code_generator"
            }
        
        # Update state with code files (files will be written to disk by wrapper)
        updates = {
            "code_files": code_files,
            "current_node": "code_generator",
            "workspace_locations": {
                "code_generator_workspace": str(workspace_dir)
            },
            "status": "processing" if code_files else "error"
        }
        
        if not code_files:
            error_msg = "Code generator did not produce any files in JSON response"
            updates["errors"] = state.get("errors", []) + [error_msg]
            updates["status"] = "error"
        else:
            logger.info(f"Code generation complete: {len(code_files)} files in state (will be written to disk)")
        
        return updates
        
    except Exception as e:
        logger.error(f"Code generation failed: {e}", exc_info=True)
        return {
            "errors": state.get("errors", []) + [f"Code generation error: {str(e)}"],
            "status": "error",
            "current_node": "code_generator"
        }
