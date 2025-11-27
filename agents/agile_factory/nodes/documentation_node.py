"""
Documentation Generator Node for Agile Factory workflow.

Uses structured JSON output instead of tool calls to reduce LLM invocations.
Files are written programmatically after agent produces structured output.
"""

import logging
import os
import json
import re
from pathlib import Path
from typing import Dict, Any
from agents.agile_factory.state.agile_state import AgileFactoryState
from agents.agile_factory.utils.safe_prompt_formatting import safe_format_prompt, safe_format_prompt_with_validation
from agents.agile_factory.utils.llm_config import get_llm_model
from prompts import get_agent_prompt_loader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from agents.agile_factory.utils.file_writer import get_workspace_dir

logger = logging.getLogger(__name__)


def documentation_node(state: AgileFactoryState) -> dict:
    """
    Documentation Generator Node using structured JSON output (NO tool calls).
    
    This node:
    1. Requests structured JSON output from LLM
    2. LLM generates all documentation file content in single JSON response
    3. Parses JSON and updates state.documentation_files
    4. Files are written programmatically after node completes (via wrapper)
    
    Args:
        state: Current workflow state
        
    Returns:
        Updates dict with documentation files in state.documentation_files
    """
    try:
        # Get API key
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable must be set")
        
        # Get workspace directory (for reference, files written later)
        workspace_dir = get_workspace_dir(state, "docs")
        
        logger.info(f"Documentation generator workspace: {workspace_dir}")
        
        # Prepare context for documentation
        user_story = state.get("user_story", "")
        requirements = state.get("requirements", {})
        architecture = state.get("architecture", {})
        code_files = state.get("code_files", {})
        project_type = state.get("project_type", "website")
        
        # Convert dicts to strings for prompt
        requirements_str = str(requirements) if isinstance(requirements, dict) else requirements
        architecture_str = str(architecture) if isinstance(architecture, dict) else architecture
        
        # Load prompt from LangSmith Hub (source of truth)
        prompt_loader = get_agent_prompt_loader("documentation_generator_v1")
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
                "current_node": "documentation_generator"
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
                code_files_count=len(code_files)
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
                "current_node": "documentation_generator"
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
        task_message = f"Generate documentation files as JSON for the {project_type} project. Output format: {{\"files\": {{\"filename.md\": \"content\"}}}}"
        
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
            documentation_files = result_data.get("files", {})
            
            if not documentation_files:
                logger.warning("No files found in JSON response")
                # Try alternative structure
                if isinstance(result_data, dict) and len(result_data) > 0:
                    # Maybe files are at top level
                    documentation_files = {k: v for k, v in result_data.items() if isinstance(v, str)}
            
            logger.info(f"Parsed {len(documentation_files)} documentation files from JSON response")
            for file_path in list(documentation_files.keys())[:5]:
                logger.info(f"  - {file_path} ({len(documentation_files[file_path])} bytes)")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response preview: {output[:500]}")
            return {
                "errors": state.get("errors", []) + [f"Failed to parse JSON response: {str(e)}"],
                "status": "error",
                "current_node": "documentation_generator"
            }
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}", exc_info=True)
            return {
                "errors": state.get("errors", []) + [f"Documentation generation error: {str(e)}"],
                "status": "error",
                "current_node": "documentation_generator"
            }
        
        # Build workspace locations update
        existing_workspace_locations = state.get("workspace_locations", {}).copy()
        existing_workspace_locations["documentation_workspace"] = str(workspace_dir)
        
        # Determine status
        if documentation_files:
            status = "complete"
        else:
            logger.warning("No documentation files generated")
            status = "processing"  # Continue workflow even if no docs
        
        logger.info(f"Documentation generation complete: {len(documentation_files)} files in state (will be written to disk)")
        
        # Return updates dict (files will be written to disk by wrapper)
        return {
            "documentation_files": documentation_files,
            "current_node": "documentation_generator",
            "workspace_locations": existing_workspace_locations,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Documentation generation failed: {e}", exc_info=True)
        return {
            "errors": state.get("errors", []) + [f"Documentation generation error: {str(e)}"],
            "status": "error",
            "current_node": "documentation_generator"
        }
