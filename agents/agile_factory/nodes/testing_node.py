"""
Testing Agent Node for Agile Factory workflow.

Uses structured JSON output instead of tool calls to reduce LLM invocations.
Test files are written programmatically after agent produces structured output.
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


def testing_node(state: AgileFactoryState) -> dict:
    """
    Testing Agent Node using structured JSON output (NO tool calls).
    
    This node:
    1. Requests structured JSON output from LLM with test file content
    2. LLM generates all test file content in single JSON response
    3. Parses JSON and updates state.test_files
    4. Files are written programmatically after node completes (via wrapper)
    
    Args:
        state: Current workflow state
        
    Returns:
        Updates dict with test files in state.test_files and test_results
    """
    try:
        # Get API key
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable must be set")
        
        # Get workspace directory (for reference, files written later)
        workspace_dir = get_workspace_dir(state, "tests")
        
        logger.info(f"Testing agent workspace: {workspace_dir}")
        
        # Prepare context for testing
        requirements = state.get("requirements", {})
        code_files = state.get("code_files", {})
        project_type = state.get("project_type", "website")
        code_workspace = state.get("workspace_locations", {}).get("code_generator_workspace", "")
        
        # Convert dicts to strings for prompt
        requirements_str = str(requirements) if isinstance(requirements, dict) else requirements
        code_files_str = str(code_files) if isinstance(code_files, dict) else code_files
        
        # Load prompt from LangSmith Hub (source of truth)
        prompt_loader = get_agent_prompt_loader("test_generator_v1")
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
                "current_node": "testing_agent"
            }
        
        logger.info(f"Loaded prompt template from LangSmith Hub: {len(system_prompt_template)} characters")
        
        # Format system prompt with dynamic context using safe formatting
        try:
            system_prompt, missing_placeholders = safe_format_prompt_with_validation(
                system_prompt_template,
                project_type=project_type,
                requirements=requirements_str,
                code_files=code_files_str,
                code_files_count=len(code_files),
                code_workspace=code_workspace
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
                "current_node": "testing_agent"
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
        task_message = f"Generate test files as JSON for the {project_type} project. Output format: {{\"files\": {{\"test_filename.py\": \"test code\"}}, \"test_results\": {{\"all_tests_passed\": false, \"test_output\": \"summary\"}}}}"
        
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
            test_files = result_data.get("files", {})
            test_results = result_data.get("test_results", {
                "all_tests_passed": False,
                "test_output": "",
                "coverage": {}
            })
            
            if not test_files:
                logger.warning("No test files found in JSON response")
                # Try alternative structure
                if isinstance(result_data, dict) and len(result_data) > 0:
                    # Maybe files are at top level
                    test_files = {k: v for k, v in result_data.items() if isinstance(v, str) and k.endswith('.py')}
            
            logger.info(f"Parsed {len(test_files)} test files from JSON response")
            for file_path in list(test_files.keys())[:5]:
                logger.info(f"  - {file_path} ({len(test_files[file_path])} bytes)")
            
            # Ensure test_results has required structure
            if not isinstance(test_results, dict):
                test_results = {
                    "all_tests_passed": False,
                    "test_output": str(test_results) if test_results else "",
                    "coverage": {}
                }
            
            # Add test file list to test_results
            test_results["test_files"] = list(test_files.keys())
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response preview: {output[:500]}")
            return {
                "errors": state.get("errors", []) + [f"Failed to parse JSON response: {str(e)}"],
                "status": "error",
                "current_node": "testing_agent",
                "test_results": {
                    "all_tests_passed": False,
                    "error": f"JSON parse error: {str(e)}"
                }
            }
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}", exc_info=True)
            return {
                "errors": state.get("errors", []) + [f"Testing error: {str(e)}"],
                "status": "error",
                "current_node": "testing_agent",
                "test_results": {
                    "all_tests_passed": False,
                    "error": str(e)
                }
            }
        
        # Build workspace locations update
        existing_workspace_locations = state.get("workspace_locations", {}).copy()
        existing_workspace_locations["testing_workspace"] = str(workspace_dir)
        
        # Determine status
        status = "processing" if test_files else "error"
        
        logger.info(f"Testing complete: {len(test_files)} test files in state (will be written to disk)")
        
        # Return updates dict (files will be written to disk by wrapper)
        return {
            "test_files": test_files,
            "test_results": test_results,
            "current_node": "testing_agent",
            "workspace_locations": existing_workspace_locations,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Testing failed: {e}", exc_info=True)
        return {
            "errors": state.get("errors", []) + [f"Testing error: {str(e)}"],
            "status": "error",
            "current_node": "testing_agent",
            "test_results": {
                "all_tests_passed": False,
                "error": str(e)
            }
        }
