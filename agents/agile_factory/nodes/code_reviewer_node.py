"""
Code Reviewer Node for Agile Factory workflow.

Uses existing code_reviewer agent with prompt loader.
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


def code_reviewer_node(state: AgileFactoryState) -> dict:
    """
    Code Reviewer Node using existing agent with prompt loader.
    
    This node:
    1. Loads prompt using existing get_agent_prompt_loader system
    2. Creates LLM with Gemini 2.5 Flash
    3. Executes code review
    4. Returns updates dict with review results (LangGraph will merge with state)
    
    Args:
        state: Current workflow state
        
    Returns:
        Updates dict with code review (LangGraph will merge with state)
    """
    try:
        # Get API key
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable must be set")
        
        # Prepare context for code review
        requirements = state.get("requirements", {})
        architecture = state.get("architecture", {})
        code_files = state.get("code_files", {})
        
        # Validate that code files exist
        if not code_files:
            error_msg = "No code files found in state for review. Code generator may not have produced files."
            logger.error(error_msg)
            return {
                "errors": state.get("errors", []) + [error_msg],
                "status": "error",
                "current_node": "code_reviewer",
                "code_review": {
                    "quality_gate_passed": False,
                    "error": error_msg,
                    "issues": ["No code files available for review"]
                }
            }
        
        logger.info(f"Code reviewer received {len(code_files)} files for review")
        
        # Format code files for review (limit size to avoid token limits)
        code_summary = {}
        for path, content in list(code_files.items())[:20]:  # Limit to first 20 files
            # Truncate very long files
            if len(content) > 5000:
                content = content[:5000] + "\n... [truncated]"
            code_summary[path] = content
        
        # Load prompt using existing system and inject dynamic context
        prompt_loader = get_agent_prompt_loader("code_reviewer_v1")
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
                "current_node": "code_reviewer"
            }
        
        logger.info(f"Loaded prompt template: {len(system_prompt_template)} characters (type: {type(system_prompt_template).__name__})")
        
        # Format system prompt with dynamic context using safe formatting
        try:
            # Convert dicts to strings for safe formatting
            requirements_str = str(requirements) if isinstance(requirements, dict) else requirements
            architecture_str = str(architecture) if isinstance(architecture, dict) else architecture
            code_summary_str = str(code_summary) if isinstance(code_summary, dict) else code_summary
            
            # Get rigidity parameter for prompt formatting
            rigidity = state.get("review_rigidity", 0.3)
            
            system_prompt, missing_placeholders = safe_format_prompt_with_validation(
                system_prompt_template,
                requirements=requirements_str,
                architecture=architecture_str,
                code_files_summary=code_summary_str,
                code_files_count=len(code_files),
                review_rigidity=rigidity
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
                "current_node": "code_reviewer"
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
        
        # Get rigidity parameter and inject into task
        rigidity = state.get("review_rigidity", 0.3)
        
        # Task message with rigidity guidance
        if rigidity <= 0.3:
            task = "Review the code leniently - approve if functional and meets core requirements (80%+ coverage). Minor issues are acceptable."
        elif rigidity <= 0.7:
            task = "Review the code with moderate strictness - approve if functional and meets most requirements. Only flag significant issues."
        else:
            task = "Review the code strictly - ensure all requirements are met and code quality is high."
        
        task += f"\n\nRigidity Level: {rigidity} (0.0=very lenient, 1.0=very strict)"
        
        # Execute code review
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task)
        ]
        
        logger.info("Calling LLM for code review...")
        result = llm.invoke(messages)
        logger.info(f"LLM response received: {len(result.content) if hasattr(result, 'content') else 'N/A'} characters")
        output = result.content.strip()
        
        # Parse JSON response (code_reviewer outputs JSON)
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
        
        code_review = json.loads(json_str)
        
        # Get rigidity parameter (0.0 = very lenient/skip, 1.0 = very strict)
        rigidity = state.get("review_rigidity", 0.3)  # Default: lenient
        
        # Check if review passed
        review_passed = code_review.get("quality_gate_passed", False)
        
        # Auto-pass logic based on rigidity
        iteration_count = state.get("code_review_iteration_count", 0)
        
        # Very lenient (rigidity <= 0.3): Auto-pass if code exists
        if not review_passed and rigidity <= 0.3 and len(code_files) > 0:
            logger.info(f"Auto-passing code review (rigidity={rigidity}, files={len(code_files)}) - very lenient mode")
            review_passed = True
            code_review["quality_gate_passed"] = True
            code_review["auto_approved"] = True
            code_review["auto_approval_reason"] = f"Very lenient mode (rigidity={rigidity}) - code exists"
        
        # Lenient (rigidity <= 0.5): Auto-pass after 1 attempt if no critical bugs
        elif not review_passed and rigidity <= 0.5 and iteration_count >= 1:
            quality_gate_eval = code_review.get("quality_gate_evaluation", {})
            critical_issues = code_review.get("bugs_and_issues", [])
            
            # Count only critical/high severity issues
            critical_count = sum(1 for issue in critical_issues 
                               if issue.get("severity", "").lower() == "high")
            
            # If no critical bugs and basic requirements met, auto-pass
            if critical_count == 0:
                requirements_met = quality_gate_eval.get("requirements_implemented", False)
                if requirements_met or len(code_files) > 0:
                    logger.info(f"Auto-passing code review (rigidity={rigidity}, iter={iteration_count}) - lenient mode")
                    review_passed = True
                    code_review["quality_gate_passed"] = True
                    code_review["auto_approved"] = True
                    code_review["auto_approval_reason"] = f"Lenient mode (rigidity={rigidity}) - no critical bugs"
        
        # Medium strictness: Auto-pass after 2 attempts
        elif not review_passed and rigidity <= 0.7 and iteration_count >= 2:
            # After 2 failed attempts, check if code is at least functional
            quality_gate_eval = code_review.get("quality_gate_evaluation", {})
            critical_issues = code_review.get("bugs_and_issues", [])
            
            # Count only critical/high severity issues
            critical_count = sum(1 for issue in critical_issues 
                               if issue.get("severity", "").lower() == "high")
            
            # If no critical bugs and basic requirements met, auto-pass
            if critical_count == 0:
                requirements_met = quality_gate_eval.get("requirements_implemented", False)
                if requirements_met or len(code_files) > 0:  # At least some code exists
                    logger.info(f"Auto-passing code review (rigidity={rigidity}, iter={iteration_count}) - medium strictness")
                    review_passed = True
                    code_review["quality_gate_passed"] = True
                    code_review["auto_approved"] = True
                    code_review["auto_approval_reason"] = f"Medium strictness (rigidity={rigidity}) - no critical bugs after {iteration_count} attempts"
        
        status = "approved" if review_passed else "needs_revision"
        
        logger.info(f"Code review complete: {'PASSED' if review_passed else 'NEEDS_REVISION'} (iteration {iteration_count})")
        
        # Return updates dict (correct LangGraph pattern)
        return {
            "code_review": code_review,
            "current_node": "code_reviewer",
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Code review failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"Code review error: {str(e)}"],
            "status": "error",
            "current_node": "code_reviewer"
        }

