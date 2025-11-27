"""
Architecture Designer Node for Agile Factory workflow.

Uses existing architecture_designer agent with prompt loader.
"""

import logging
import os
import re
from typing import Dict, Any
from agents.agile_factory.state.agile_state import AgileFactoryState
from agents.agile_factory.utils.safe_prompt_formatting import safe_format_prompt, safe_format_prompt_with_validation
from agents.agile_factory.utils.llm_config import get_llm_model
from prompts import get_agent_prompt_loader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


def architecture_node(state: AgileFactoryState) -> dict:
    """
    Architecture Designer Node using existing agent with prompt loader.
    
    This node:
    1. Loads prompt using existing get_agent_prompt_loader system
    2. Creates LLM with Gemini 2.5 Flash
    3. Executes architecture design
    4. Returns updates dict with architecture (LangGraph will merge with state)
    
    Args:
        state: Current workflow state
        
    Returns:
        Updates dict with architecture design (LangGraph will merge with state)
    """
    try:
        # Get API key
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable must be set")
        
        # Prepare context for architecture design
        user_story = state.get("user_story", "")
        requirements = state.get("requirements", {})
        project_type = state.get("project_type", "website")
        
        # Load prompt using existing system and inject dynamic context
        prompt_loader = get_agent_prompt_loader("architecture_designer_v1")
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
                "current_node": "architecture_designer"
            }
        
        logger.info(f"Loaded prompt template: {len(system_prompt_template)} characters (type: {type(system_prompt_template).__name__})")
        
        # Format system prompt with dynamic context using safe formatting
        try:
            # Convert requirements dict to string for formatting
            requirements_str = str(requirements) if isinstance(requirements, dict) else requirements
            system_prompt, missing_placeholders = safe_format_prompt_with_validation(
                system_prompt_template,
                user_story=user_story,
                requirements=requirements_str,
                project_type=project_type
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
                "current_node": "architecture_designer"
            }
        
        # Create LLM with configurable model
        model_name = get_llm_model(state)
        logger.info(f"Using LLM model: {model_name}")
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0,
            convert_system_message_to_human=True
        )
        
        # Task message is now embedded in the system prompt, so we use a simple instruction
        task = "Design the architecture for the project based on the requirements provided."
        
        # Execute architecture design
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task)
        ]
        
        logger.info("Calling LLM for architecture design...")
        result = llm.invoke(messages)
        logger.info(f"LLM response received: {len(result.content) if hasattr(result, 'content') else 'N/A'} characters")
        output = result.content.strip()
        
        # Parse JSON response (architecture_designer outputs JSON)
        import json
        import re
        
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
        
        architecture = json.loads(json_str)
        
        logger.info(f"Architecture design complete: {len(architecture.get('components', []))} components")
        
        # Return updates dict (correct LangGraph pattern)
        return {
            "architecture": architecture,
            "current_node": "architecture_designer"
        }
        
    except Exception as e:
        logger.error(f"Architecture design failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"Architecture design error: {str(e)}"],
            "status": "error",
            "current_node": "architecture_designer"
        }

