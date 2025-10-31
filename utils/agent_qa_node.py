"""
Agent Q&A Node for Studio Graphs

Allows agents to answer human questions based on their current state and work.
This enables interactive Q&A at HITL checkpoints.
"""

from typing import Dict, Any
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


def create_llm():
    """Create LLM instance for Q&A."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=0.0  # Deterministic for consistent answers
    )


def answer_question_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Answer human questions based on agent's current state and work.
    
    This node allows agents to:
    - Explain what they've done
    - Clarify decisions
    - Answer questions about their output
    - Provide context-aware responses
    
    Usage in Studio:
        1. At HITL checkpoint, update state with:
           {"human_question": "Why did you classify this as complex?"}
        2. Route to this node (or call it directly)
        3. Answer appears in `agent_answer` field
    
    Args:
        state: Current graph state including human_question field
        
    Returns:
        Dict with agent_answer field containing the response
    """
    human_question = state.get("human_question", "")
    
    if not human_question:
        logger.warning("No question provided to answer_question_node")
        return {
            "agent_answer": "No question provided. Please ask a question in the 'human_question' field.",
            "current_step": state.get("current_step", "unknown")
        }
    
    logger.info(f"❓ Answering question: {human_question[:100]}...")
    
    # Detect agent type from state fields
    # CRITICAL: Check more specific fields FIRST to avoid misidentification
    # Code generator state has project_complexity/context_confidence from earlier steps,
    # so we must check for code_files BEFORE checking for project_complexity
    agent_name = "unknown"
    agent_context = ""
    
    # Check code generator FIRST (most specific - has code_files or generation_confidence)
    if "code_files" in state or "generation_confidence" in state:
        agent_name = "code_generator"
        code_files = state.get('code_files', {})
        file_list = list(code_files.keys())
        
        # Build detailed file information
        file_details = []
        for file_path, file_content in code_files.items():
            # Get first few lines as preview (limit to avoid huge prompts)
            lines = file_content.split('\n')[:5]
            preview = '\n'.join(lines[:3])  # First 3 lines
            file_size = len(file_content)
            file_details.append(f"- **{file_path}**: {file_size} characters\n  Preview: {preview[:150]}...")
        
        file_details_text = '\n'.join(file_details) if file_details else 'No files generated yet'
        
        agent_context = f"""You are the Code Generator agent. You generate production-ready code based on architecture and requirements.

**CRITICAL**: You have ACTUALLY GENERATED CODE FILES. You MUST use the actual files listed below, NOT conceptual examples.

Current State:
- Files Generated: {len(code_files)} files
- File List: {', '.join(file_list) if file_list else 'No files generated yet'}
- Generation Confidence: {state.get('generation_confidence', 0.0):.0%}
- Current Step: {state.get('current_step', 'unknown')}
- Iteration: {state.get('iteration_count', 0)}/3
- Project Context: {state.get('project_context', 'Not provided')}
- Project Domain: {state.get('project_domain', 'general')}
- Architecture Pattern: {state.get('architecture_pattern', 'Not specified')}

**GENERATED FILES DETAILS** (USE THESE ACTUAL FILES):
{file_details_text}

**REQUIREMENTS** (used for generation):
- Functional Requirements: {len(state.get('functional_requirements', []))} items
- Non-Functional Requirements: {len(state.get('non_functional_requirements', []))} items

**ARCHITECTURE** (used for generation):
- Components: {len(state.get('components', []))} components
- Technology Stack: {len(state.get('technology_stack', {}))} layers

**IMPORTANT INSTRUCTIONS**:
- When asked about files, ALWAYS reference the ACTUAL files you generated (listed above)
- Explain WHY each file was created and its purpose
- Reference the actual file paths and contents from the files above
- DO NOT provide "conceptual" or "expected" examples - use the REAL files!
- If asked "which files did you produce", list the actual file paths from the File List above
- If asked "why", explain based on the requirements and architecture you used
"""
    
    # Check architecture designer (has architecture_design or design_confidence)
    elif "architecture_design" in state or "design_confidence" in state:
        agent_name = "architecture_designer"
        agent_context = f"""You are the Architecture Designer agent. You design system architecture based on requirements.

Current State:
- Architecture Pattern: {state.get('architecture_pattern', 'Not specified')}
- Components: {len(state.get('components', []))} components
- Technology Stack: {len(state.get('technology_stack', {}))} layers
- Design Confidence: {state.get('design_confidence', 0.0):.0%}
- Current Step: {state.get('current_step', 'unknown')}
- Iteration: {state.get('iteration_count', 0)}/3
- Project Domain: {state.get('project_domain', 'general')}
- Project Complexity: {state.get('project_complexity', 'medium')}
"""
    
    # Check requirements analyst (has requirements_analysis or analysis_confidence)
    elif "requirements_analysis" in state or "analysis_confidence" in state:
        agent_name = "requirements_analyst"
        agent_context = f"""You are the Requirements Analyst agent. You analyze project requirements and generate:
- Functional requirements
- Non-functional requirements
- Constraints and assumptions
- Gaps and ambiguities

Current State:
- Requirements Summary: {state.get('requirements_analysis', {}).get('summary', 'Not available')[:200]}
- Functional Requirements: {len(state.get('functional_requirements', []))} items
- Non-Functional Requirements: {len(state.get('non_functional_requirements', []))} items
- Analysis Confidence: {state.get('analysis_confidence', 0.0):.0%}
- Current Step: {state.get('current_step', 'unknown')}
- Iteration: {state.get('iteration_count', 0)}/3
- Project Domain: {state.get('project_domain', 'general')}
- Project Complexity: {state.get('project_complexity', 'medium')}
"""
    
    # Check agent selector (has selected_agents or selection_confidence)
    elif "selected_agents" in state or "selection_confidence" in state:
        agent_name = "agent_selector"
        agent_context = f"""You are the Agent Selector agent. You select which specialist agents are needed for the project.

Current State:
- Selected Agents: {', '.join(state.get('selected_agents', []))}
- Selection Confidence: {state.get('selection_confidence', 0.0):.0%}
- Current Step: {state.get('current_step', 'unknown')}
- Iteration: {state.get('iteration_count', 0)}/3
- Project Domain: {state.get('project_domain', 'general')}
- Project Intent: {state.get('project_intent', 'new_feature')}
- Project Complexity: {state.get('project_complexity', 'medium')}
"""
    
    # Check complexity analyzer LAST (has project_complexity but NOT code_files)
    # This ensures we don't misidentify code generator as complexity analyzer
    elif ("project_complexity" in state or "context_confidence" in state) and "code_files" not in state:
        agent_name = "complexity_analyzer"
        agent_context = f"""You are the Complexity Analyzer agent. You analyze project context and detect:
- Project complexity (simple, medium, complex)
- Project domain (ai, web, api, data, etc.)
- Project intent (new_feature, bug_fix, refactor, etc.)
- Detected entities (technologies, frameworks, services)

Current State:
- Project Context: {state.get('project_context', 'Not provided')}
- Detected Complexity: {state.get('project_complexity', 'Not detected')}
- Detected Domain: {state.get('project_domain', 'Not detected')}
- Detected Intent: {state.get('project_intent', 'Not detected')}
- Detected Entities: {', '.join(state.get('detected_entities', []))}
- Confidence: {state.get('context_confidence', 0.0):.0%}
- Current Step: {state.get('current_step', 'unknown')}
- Iteration: {state.get('iteration_count', 0)}/3
"""
    
    # Build Q&A prompt
    system_prompt = f"""You are a helpful assistant agent that answers questions about your work.

{agent_context}

Your role is to:
- Answer questions clearly and accurately based on your current state
- Explain your reasoning and decisions
- Provide context about what you've done
- Be honest about limitations or uncertainties

Answer the human's question based on the current state information above."""
    
    user_prompt = f"""Human Question: {human_question}

Please answer this question based on your current state and work. Be specific, clear, and reference the actual values from your state when relevant."""
    
    # Generate answer
    try:
        llm = create_llm()
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        result = llm.invoke(messages)
        answer = result.content.strip()
        
        logger.info(f"✅ Question answered by {agent_name}")
        
        return {
            "agent_answer": answer,
            "question_answered": True,
            "answer_timestamp": datetime.now().isoformat(),
            "current_step": state.get("current_step", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Failed to answer question: {e}")
        return {
            "agent_answer": f"Sorry, I encountered an error while answering your question: {str(e)}",
            "question_answered": False,
            "answer_timestamp": datetime.now().isoformat(),
            "current_step": state.get("current_step", "unknown"),
            "errors": [f"Q&A error: {str(e)}"]
        }


def handle_questions_in_review_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced review node that handles questions at HITL checkpoints.
    
    This function can be called from review nodes to check for questions
    and answer them before proceeding with review.
    
    Args:
        state: Current state with optional human_question field
        
    Returns:
        Updated state with agent_answer if question was asked
    """
    human_question = state.get("human_question", "")
    
    if human_question:
        # Answer the question
        answer_result = answer_question_node(state)
        
        # Merge answer into state
        updated_state = state.copy()
        updated_state.update(answer_result)
        
        logger.info("✅ Question answered in review node")
        return updated_state
    
    # No question asked, return state as-is
    return state
