"""
Isolated Agent Selector Graph for LangGraph Studio Testing

This graph contains ONLY the agent selector node, allowing isolated testing
of Phase 2 context-aware agent selection (US-CONTEXT-001) in LangGraph Studio.

Usage in Studio:
1. Select this graph from the dropdown
2. Provide initial state with project_context and detected context
3. Execute and view the selected agents
4. Review and refine agent selection via HITL checkpoint
"""

from __future__ import annotations

import logging
import os
from typing import Dict, Any, List
try:
    from typing_extensions import TypedDict  # Python < 3.12 compatibility
except ImportError:
    from typing import TypedDict  # Python >= 3.12
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


# ============================================================================
# STATE - Simplified for Agent Selector Only
# ============================================================================

class AgentSelectorState(TypedDict):
    """State for isolated agent selector testing."""
    # Input - Context from complexity_analyzer
    project_context: str
    project_complexity: str  # simple, medium, complex
    project_domain: str  # ai, web, api, data, mobile, library, utility, general
    project_intent: str  # new_feature, bug_fix, refactor, migration, enhancement, general
    detected_entities: List[str]  # Technology names, frameworks, services
    
    # Output - Agent Selection
    required_agents: List[str]  # Selected agents list
    selection_reasoning: str  # Why these agents were selected
    selection_confidence: float  # 0.0 to 1.0 - confidence in selection
    needs_more_info: bool  # True if agent needs more information
    information_requests: List[str]  # Questions to ask user for clarification
    selection_summary: str  # Human-readable summary of selected agents
    
    # Human Feedback (for HITL checkpoint)
    human_feedback: str  # Feedback provided by human at HITL checkpoint
    human_approval: str  # "approved", "rejected", or "needs_refinement"
    human_question: str  # Question asked by human (for Q&A)
    agent_answer: str  # Answer provided by agent to human question
    
    # Iteration tracking
    iteration_count: int  # Number of refinement iterations (safety limit)
    
    # Status
    current_step: str
    errors: List[str]


# ============================================================================
# STANDARD AGENT ORDER (enforced in code)
# ============================================================================

STANDARD_AGENT_ORDER = [
    "requirements_analyst",
    "architecture_designer",
    "code_generator",
    "test_generator",
    "code_reviewer",
    "documentation_generator"
]

AVAILABLE_AGENTS = {
    "requirements_analyst": "Analyzes project requirements and creates user stories",
    "architecture_designer": "Designs system architecture and selects technology stack",
    "code_generator": "Generates production-ready code",
    "test_generator": "Creates comprehensive test suites",
    "code_reviewer": "Reviews code quality and identifies improvements",
    "documentation_generator": "Creates technical documentation and user guides"
}


# ============================================================================
# PROMPT LOADING
# ============================================================================

def load_prompt_from_langsmith(prompt_name: str, fallback: str = None) -> str:
    """Load prompt from LangSmith with local caching."""
    from pathlib import Path
    
    cache_dir = Path("prompts/langsmith_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{prompt_name}.txt"
    
    try:
        try:
            import streamlit as st
            api_key = st.secrets.get('LANGSMITH_API_KEY') or st.secrets.get('LANGCHAIN_API_KEY')
        except:
            api_key = os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGCHAIN_API_KEY")
        
        if api_key:
            from langsmith import Client
            client = Client(api_key=api_key)
            prompt = client.pull_prompt(prompt_name, include_model=True)
            
            prompt_text = None
            if hasattr(prompt, 'template'):
                prompt_text = prompt.template
            elif hasattr(prompt, 'messages') and prompt.messages:
                prompt_text = str(prompt.messages[0].prompt.template)
            else:
                prompt_text = str(prompt)
            
            try:
                cache_file.write_text(prompt_text, encoding='utf-8')
                logger.info(f"Cached prompt: {prompt_name}")
            except Exception as cache_err:
                logger.warning(f"Failed to cache {prompt_name}: {cache_err}")
            
            return prompt_text
        else:
            if cache_file.exists():
                logger.info(f"Using cached prompt (no API key): {prompt_name}")
                return cache_file.read_text(encoding='utf-8')
            else:
                logger.info(f"No API key, no cache - using fallback for {prompt_name}")
                return fallback or f"You are {prompt_name}. Complete the task."
                
    except Exception as e:
        if cache_file.exists():
            logger.warning(f"LangSmith failed for {prompt_name}, using cache: {e}")
            return cache_file.read_text(encoding='utf-8')
        else:
            logger.warning(f"LangSmith failed, no cache - using fallback for {prompt_name}: {e}")
            return fallback or f"You are {prompt_name}. Complete the task."


# ============================================================================
# AGENT SELECTOR NODE
# ============================================================================

def _create_llm():
    """Create LLM instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=0.0  # Deterministic for testing
    )


def select_agents_node(state: AgentSelectorState) -> Dict[str, Any]:
    """
    Select which agents to run using LLM with context-aware routing.
    
    Phase 2 (US-CONTEXT-001): Enhanced agent selection that uses detected context:
    - Domain, intent, complexity, and entities inform agent selection
    - Better agent selection accuracy with context-aware routing
    
    CRITICAL: LLM selects WHICH agents, but code enforces STANDARD ORDER.
    """
    logger.info("🎯 Selecting agents with context-aware LLM...")
    
    llm = _create_llm()
    system_prompt = load_prompt_from_langsmith(
        "agent_selector_v1",
        "You are an Agent Selector. Select which specialist agents are needed based on project requirements."
    )
    
    # Enhanced task prompt with context information
    task = f"""Select which specialist agents are needed for this project.

Project: {state['project_context']}

Detected Context:
- Domain: {state.get('project_domain', 'general')}
- Intent: {state.get('project_intent', 'new_feature')}
- Complexity: {state.get('project_complexity', 'medium')}
- Entities: {', '.join(state.get('detected_entities', [])[:10])}

Available agents:
- requirements_analyst: Analyzes requirements and creates user stories (ALWAYS REQUIRED)
- architecture_designer: Designs system architecture (Required for medium+, web_app, api, data_processing)
- code_generator: Generates production-ready code (ALWAYS REQUIRED)
- test_generator: Creates test suites (Required for medium+, critical functionality)
- code_reviewer: Reviews code quality (Required for medium+, production code)
- documentation_generator: Creates documentation (ALWAYS REQUIRED)

Use the detected context to make informed agent selection decisions.
For example:
- Domain: ai + Complexity: complex → Usually needs all agents
- Intent: bug_fix → May need code_generator, test_generator, code_reviewer
- Intent: new_feature → Usually needs all agents
- Complexity: simple → Minimum: requirements_analyst, code_generator, documentation_generator

Respond with ONLY valid JSON (no markdown, no extra text):
{{
    "required_agents": ["agent1", "agent2", "agent3"],
    "reasoning": "Brief explanation of why these agents were selected based on context"
}}

Example:
{{
    "required_agents": ["requirements_analyst", "architecture_designer", "code_generator", "test_generator", "code_reviewer", "documentation_generator"],
    "reasoning": "Complex AI project requires full development lifecycle: requirements analysis, architecture design, code implementation, testing, code review, and documentation."
}}"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=task)
    ]
    
    try:
        result = llm.invoke(messages)
        output = result.content.strip()
        
        # Parse JSON response
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
        
        parsed = json.loads(json_str)
        
        # Extract and validate agents
        selected_agents = parsed.get("required_agents", [])
        reasoning = parsed.get("reasoning", "Agent selection based on detected context")
        
        # Validate agent names
        valid_agents = set(AVAILABLE_AGENTS.keys())
        selected_set = set(agent for agent in selected_agents if agent in valid_agents)
        
        # Ensure we have at least minimum required agents
        if not selected_set:
            selected_set = {"requirements_analyst", "code_generator", "documentation_generator"}
        
        # CRITICAL: Enforce standard execution order
        # Sort selected agents according to STANDARD_AGENT_ORDER
        required = [agent for agent in STANDARD_AGENT_ORDER if agent in selected_set]
        
        # Calculate confidence based on selection quality
        confidence = _calculate_selection_confidence(
            required, state.get('project_complexity', 'medium'),
            state.get('project_domain', 'general'),
            state.get('project_intent', 'new_feature')
        )
        
        # Determine if more information is needed
        needs_more_info = confidence < 0.7 or len(required) < 3
        
        # Generate information requests if needed
        information_requests = []
        if needs_more_info:
            information_requests = _generate_selection_questions(
                state.get('project_context', ''),
                required,
                state.get('project_complexity', 'medium'),
                state.get('project_domain', 'general'),
                state.get('project_intent', 'new_feature')
            )
        
        # Create human-readable summary
        selection_summary = _format_selection_summary(required, reasoning, confidence)
        
        logger.info(
            f"🎯 Agents selected: {required} (confidence: {confidence:.2f}, "
            f"reasoning: {reasoning[:50]}...)"
        )
        
        return {
            "required_agents": required,
            "selection_reasoning": reasoning,
            "selection_confidence": confidence,
            "needs_more_info": needs_more_info,
            "information_requests": information_requests,
            "selection_summary": selection_summary,
            "current_step": "agents_selected"
        }
        
    except Exception as e:
        logger.warning(f"Failed to parse agent selection JSON: {e}. Using defaults.")
        # Fallback to default selection
        default_agents = ["requirements_analyst", "code_generator", "documentation_generator"]
        return {
            "required_agents": default_agents,
            "selection_reasoning": f"Default selection due to parsing error: {str(e)}",
            "selection_confidence": 0.3,  # Low confidence due to error
            "needs_more_info": True,
            "information_requests": [
                "Could you clarify which agents are needed for this project?",
                "What is the main purpose of this project?",
                "What is the complexity level?"
            ],
            "selection_summary": f"⚠️ Agent selection failed. Default agents assigned: {', '.join(default_agents)}. Please provide more information.",
            "current_step": "agents_selected",
            "errors": [f"Agent selection error: {str(e)}"]
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _calculate_selection_confidence(
    selected_agents: List[str],
    complexity: str,
    domain: str,
    intent: str
) -> float:
    """Calculate confidence score for agent selection."""
    confidence = 0.5  # Base confidence
    
    # Check if selection matches expected patterns
    min_agents = {"requirements_analyst", "code_generator", "documentation_generator"}
    selected_set = set(selected_agents)
    
    # Minimum agents present
    if min_agents.issubset(selected_set):
        confidence += 0.2
    
    # Complexity-based validation
    if complexity == "complex":
        if len(selected_agents) >= 5:
            confidence += 0.15
    elif complexity == "medium":
        if len(selected_agents) >= 4:
            confidence += 0.15
    elif complexity == "simple":
        if 3 <= len(selected_agents) <= 4:
            confidence += 0.15
    
    # Domain-specific validation
    if domain != "general":
        if "architecture_designer" in selected_set:
            confidence += 0.1
    
    # Intent-specific validation
    if intent == "new_feature":
        if len(selected_agents) >= 5:
            confidence += 0.05
    elif intent == "bug_fix":
        if "code_generator" in selected_set and "test_generator" in selected_set:
            confidence += 0.1
    
    return min(confidence, 1.0)  # Cap at 1.0


def _generate_selection_questions(
    context: str,
    selected_agents: List[str],
    complexity: str,
    domain: str,
    intent: str
) -> List[str]:
    """Generate questions to ask user for more information about agent selection."""
    requests = []
    
    # Check if selection seems incomplete
    if len(selected_agents) < 3:
        requests.append("Are there any additional agents needed for this project?")
    
    # Domain-specific questions
    if domain == "general" and len(selected_agents) < 4:
        requests.append("What domain does this project belong to? (e.g., AI, web, API, data processing)")
    
    # Complexity questions
    if complexity == "medium" and len(selected_agents) < 4:
        requests.append("Is this project more complex than initially assessed? Should we include architecture_designer?")
    
    # Intent-specific questions
    if intent == "new_feature" and "test_generator" not in selected_agents:
        requests.append("Should we include test generation for this new feature?")
    
    # Architecture questions
    if "architecture_designer" not in selected_agents and complexity != "simple":
        requests.append("Does this project require architecture design?")
    
    # If no specific requests, add generic ones
    if not requests:
        requests.append("Are there any specific requirements or constraints that affect agent selection?")
    
    return requests


def _format_selection_summary(
    agents: List[str],
    reasoning: str,
    confidence: float
) -> str:
    """Create human-readable summary of selected agents."""
    summary_parts = [
        f"**Selected Agents**: {', '.join(agents)}",
        f"**Count**: {len(agents)} agents",
        f"**Confidence**: {confidence:.0%}",
        f"**Reasoning**: {reasoning}"
    ]
    
    # Add agent descriptions
    summary_parts.append("\n**Agent Descriptions**:")
    for agent in agents:
        if agent in AVAILABLE_AGENTS:
            summary_parts.append(f"- {agent}: {AVAILABLE_AGENTS[agent]}")
    
    return "\n".join(summary_parts)


# ============================================================================
# HITL REVIEW NODE
# ============================================================================

def review_selection_node(state: AgentSelectorState) -> Dict[str, Any]:
    """
    HITL checkpoint: Review selected agents, answer questions, and process human feedback.
    
    This node:
    1. Displays selected agents in a readable format
    2. Answers human questions if provided (Q&A capability)
    3. Processes human feedback if provided
    4. Updates agent selection if human provides corrections
    5. Sets routing decision for loop or END
    """
    logger.info("👤 HITL Checkpoint: Reviewing agent selection...")
    
    # Get iteration count (safety limit)
    iteration_count = state.get('iteration_count', 0)
    max_iterations = 3  # Safety limit to prevent infinite loops
    
    # Get human feedback and questions if provided
    human_feedback = state.get('human_feedback', '')
    human_approval = state.get('human_approval', '')
    human_question = state.get('human_question', '')
    
    # Start with current state values
    updated_state = {
        "current_step": "selection_review",
        "selection_summary": state.get('selection_summary', '')
    }
    
    # Handle human questions (Q&A capability)
    if human_question:
        logger.info(f"❓ Human question received: {human_question[:100]}...")
        from utils.agent_qa_node import answer_question_node
        
        # Answer the question
        qa_result = answer_question_node(state)
        updated_state.update({
            "agent_answer": qa_result.get("agent_answer", ""),
            "question_answered": qa_result.get("question_answered", False)
        })
        logger.info(f"✅ Question answered: {len(qa_result.get('agent_answer', ''))} chars")
    
    # If human provided feedback, process it
    if human_feedback:
        logger.info(f"👤 Human feedback received: {human_feedback}")
        
        # Process feedback based on approval status
        if human_approval.lower() == 'needs_refinement':
            logger.info("🔄 Processing refinement request...")
            
            # Check iteration limit
            if iteration_count >= max_iterations:
                logger.warning(f"⚠️ Max iterations ({max_iterations}) reached - ending workflow")
                updated_state['human_approval'] = 'approved'  # Force approval to end
                human_approval = 'approved'  # Update for routing
            else:
                # Parse agent list from feedback
                feedback_agents = _extract_agents_from_feedback(human_feedback)
                
                # Merge with existing selection
                existing_agents = state.get('required_agents', [])
                if feedback_agents:
                    # Replace with feedback agents if provided
                    all_agents = list(set(existing_agents + feedback_agents))
                    # Enforce standard order
                    refined_agents = [agent for agent in STANDARD_AGENT_ORDER if agent in all_agents]
                else:
                    # Keep existing but boost confidence
                    refined_agents = existing_agents
                
                # Update state with refined selection
                updated_state.update({
                    "required_agents": refined_agents,
                    "selection_confidence": min(state.get('selection_confidence', 0.0) + 0.1, 1.0),
                    "iteration_count": iteration_count + 1
                })
                
                logger.info(f"✅ Selection refined: Updated to {refined_agents}")
                logger.info(f"🔄 Iteration {updated_state['iteration_count']}/{max_iterations}")
            
        elif human_approval.lower() == 'rejected':
            logger.warning("❌ Selection rejected by human - ending workflow")
            # Keep original values, end workflow
            
        elif human_approval.lower() == 'approved':
            logger.info("✅ Selection approved by human - ending workflow")
            # Selection is correct, no changes needed
    
    # Format review message
    review_message = f"""
# Agent Selection Review

## Selected Agents

{state.get('selection_summary', 'No agents selected')}

## Status

- **Confidence**: {updated_state.get('selection_confidence', state.get('selection_confidence', 0.0)):.0%}
- **Iteration**: {updated_state.get('iteration_count', iteration_count)}/{max_iterations}
- **Status**: {'✅ Ready to proceed' if not state.get('needs_more_info', False) else '⚠️ More information needed'}

"""
    
    if state.get('needs_more_info', False) and state.get('information_requests'):
        review_message += "\n## Questions for Clarification\n\n"
        for i, question in enumerate(state.get('information_requests', []), 1):
            review_message += f"{i}. {question}\n"
        review_message += "\n**Please provide answers by updating the state (see instructions below).**\n"
    
    # Add Q&A section if question was asked
    if human_question:
        review_message += f"\n## Question & Answer\n\n"
        review_message += f"**Question**: {human_question}\n\n"
        agent_answer = updated_state.get('agent_answer', '')
        if agent_answer:
            review_message += f"**Answer**: {agent_answer}\n\n"
        else:
            review_message += f"**Answer**: Processing question...\n\n"
    
    # If human provided feedback, show it and the processing result
    if human_feedback:
        review_message += f"\n## Human Feedback Received\n\n{human_feedback}\n"
        
        if human_approval.lower() == 'needs_refinement':
            if iteration_count >= max_iterations:
                review_message += f"\n### ⚠️ Max Iterations Reached\n\n"
                review_message += f"Maximum refinement iterations ({max_iterations}) reached. Workflow will end.\n"
            else:
                review_message += f"\n### Refinement Applied ✅\n\n"
                if 'required_agents' in updated_state:
                    review_message += f"- **Updated Agents**: {', '.join(updated_state['required_agents'])}\n"
                review_message += f"- **Confidence Updated**: {updated_state.get('selection_confidence', 0.0):.0%}\n"
                review_message += f"- **Next**: Will re-select agents with refined information\n"
    
    if human_approval:
        review_message += f"\n## Approval Status: {human_approval}\n"
    
    # Signal workflow status based on routing decision
    if human_approval.lower() == 'needs_refinement' and iteration_count < max_iterations:
        review_message += "\n## Workflow Status\n\n🔄 **Refinement requested - will re-select agents**\n"
    elif human_approval.lower() == 'approved':
        review_message += "\n## Workflow Status\n\n✅ **Selection approved - workflow will complete**\n"
    elif human_approval.lower() == 'rejected':
        review_message += "\n## Workflow Status\n\n❌ **Selection rejected - workflow ending**\n"
    else:
        review_message += "\n## Workflow Status\n\n✅ **Agent selection complete - workflow finished**\n"
    
    # Update selection summary with the review message
    updated_state['selection_summary'] = review_message
    
    logger.info("📋 Review message prepared")
    
    return updated_state


def _extract_agents_from_feedback(feedback: str) -> List[str]:
    """
    Extract agent names from human feedback.
    
    Examples:
    - "Add test_generator" -> ["test_generator"]
    - "Remove architecture_designer" -> []
    - "requirements_analyst, code_generator, test_generator" -> ["requirements_analyst", "code_generator", "test_generator"]
    """
    import re
    
    agents_found = []
    feedback_lower = feedback.lower()
    
    # Look for agent names mentioned
    for agent_name in AVAILABLE_AGENTS.keys():
        # Check for explicit mentions
        if agent_name.lower() in feedback_lower:
            # Check if it's "remove" or "skip"
            if "remove" in feedback_lower or "skip" in feedback_lower or "don't need" in feedback_lower:
                continue  # Skip this agent
            agents_found.append(agent_name)
    
    # Look for comma-separated list
    comma_match = re.search(r'\[([^\]]+)\]|agents?:\s*([^\.]+)', feedback_lower)
    if comma_match:
        agent_list_str = comma_match.group(1) or comma_match.group(2)
        for agent in agent_list_str.split(','):
            agent = agent.strip()
            if agent in AVAILABLE_AGENTS:
                agents_found.append(agent)
    
    return list(set(agents_found))  # Deduplicate


# ============================================================================
# FINALIZE NODE
# ============================================================================

def finalize_selection_node(state: AgentSelectorState) -> Dict[str, Any]:
    """
    Final completion node: Generate final summary message before workflow ends.
    
    This node runs when workflow is ending (approved/rejected/max_iterations)
    to provide a clear final message to the user.
    """
    logger.info("🏁 Finalizing agent selection workflow...")
    
    human_approval = state.get('human_approval', '').lower()
    iteration_count = state.get('iteration_count', 0)
    selected_agents = state.get('required_agents', [])
    
    # Determine completion status
    if human_approval == 'approved':
        status_emoji = "✅"
        status_text = "Approved"
        completion_message = "Agent selection approved and workflow completed successfully."
    elif human_approval == 'rejected':
        status_emoji = "❌"
        status_text = "Rejected"
        completion_message = "Agent selection rejected. Workflow ending."
    elif iteration_count >= 3:
        status_emoji = "⚠️"
        status_text = "Max Iterations Reached"
        completion_message = "Maximum refinement iterations reached. Workflow ending."
    else:
        status_emoji = "✅"
        status_text = "Complete"
        completion_message = "Agent selection workflow completed."
    
    # Build final summary
    selection_summary = state.get('selection_summary', '')
    if not selection_summary or "Agent Selection Review" in selection_summary:
        selection_summary = _format_selection_summary(
            selected_agents,
            state.get('selection_reasoning', 'Selected based on detected context'),
            state.get('selection_confidence', 0.0)
        )
    
    # Create final completion message
    final_message = f"""
# {status_emoji} Agent Selection Complete

## Final Summary

{completion_message}

## Selected Agents

{selection_summary}

## Final Selection

- **Agents**: {', '.join(selected_agents)}
- **Count**: {len(selected_agents)} agents
- **Confidence**: {state.get('selection_confidence', 0.0):.0%}
- **Iterations**: {iteration_count}
- **Status**: {status_emoji} {status_text}

## Execution Order

Agents will execute in this order:
1. {selected_agents[0] if selected_agents else 'N/A'}
2. {selected_agents[1] if len(selected_agents) > 1 else 'N/A'}
3. {selected_agents[2] if len(selected_agents) > 2 else 'N/A'}
4. {selected_agents[3] if len(selected_agents) > 3 else 'N/A'}
5. {selected_agents[4] if len(selected_agents) > 4 else 'N/A'}
6. {selected_agents[5] if len(selected_agents) > 5 else 'N/A'}

---

## Workflow Complete

✅ **The agent selection workflow has finished.**

The selected agents are now ready for execution:
- Context-aware selection completed
- Standard execution order enforced
- Ready for workflow routing

**Current Step**: completed
"""
    
    logger.info(f"✅ Final message prepared - workflow complete (status: {status_text})")
    
    return {
        "current_step": "completed",
        "selection_summary": final_message
    }


# ============================================================================
# ROUTING FUNCTION
# ============================================================================

def _route_after_review(state: AgentSelectorState) -> str:
    """
    Routing function: Decide whether to loop back for refinement or end workflow.
    
    Returns:
        "select_agents" if refinement needed and within iteration limit
        "finalize_selection" if approved, rejected, or max iterations reached
    """
    human_approval = state.get('human_approval', '').lower()
    iteration_count = state.get('iteration_count', 0)
    max_iterations = 3
    
    # End conditions - route to finalize_selection first
    if human_approval == 'approved':
        logger.info("✅ Approved - routing to finalize_selection")
        return "finalize_selection"
    
    if human_approval == 'rejected':
        logger.info("❌ Rejected - routing to finalize_selection")
        return "finalize_selection"
    
    if iteration_count >= max_iterations:
        logger.info(f"⚠️ Max iterations ({max_iterations}) reached - routing to finalize_selection")
        return "finalize_selection"
    
    # Confidence-based auto-approval (if no human feedback and high confidence)
    if not human_approval and state.get('selection_confidence', 0.0) >= 0.9:
        logger.info("✅ High confidence, no feedback - routing to finalize_selection")
        return "finalize_selection"
    
    # Loop back for refinement
    if human_approval == 'needs_refinement':
        logger.info(f"🔄 Refinement requested - looping back to select_agents (iteration {iteration_count + 1}/{max_iterations})")
        return "select_agents"
    
    # Default: route to finalize
    logger.info("🏁 No refinement requested - routing to finalize_selection")
    return "finalize_selection"


# ============================================================================
# GRAPH BUILDING
# ============================================================================

def build_graph():
    """
    Build isolated agent selector graph with HITL checkpoint and iterative refinement loop.
    
    Graph flow:
    START → select_agents → [interrupt_after] → review_selection → [conditional]
                                                                  ├→ select_agents (if needs_refinement)
                                                                  └→ finalize_selection → END (if approved/rejected/max_iterations)
    
    NOTE: For LangGraph Studio, we use interrupt_after on select_agents
    instead of interrupt_before on review_selection to ensure proper END edge handling.
    """
    workflow = StateGraph(AgentSelectorState)
    
    # Add nodes
    workflow.add_node("select_agents", select_agents_node)
    workflow.add_node("review_selection", review_selection_node)
    workflow.add_node("finalize_selection", finalize_selection_node)  # Final completion node
    
    # Flow: START → select_agents → review_selection → [conditional] → select_agents OR finalize_selection → END
    workflow.set_entry_point("select_agents")
    workflow.add_edge("select_agents", "review_selection")
    
    # Conditional edge: review_selection → select_agents (loop) OR finalize_selection
    workflow.add_conditional_edges(
        "review_selection",
        _route_after_review,  # Routing function decides next step
        {
            "select_agents": "select_agents",  # Loop back for refinement
            "finalize_selection": "finalize_selection"  # Finalize and end
        }
    )
    
    # Finalize selection → END (always ends workflow)
    workflow.add_edge("finalize_selection", END)
    
    # Use interrupt_after instead of interrupt_before for better END handling
    # This pauses AFTER select_agents, allowing review_selection to complete normally
    compiled = workflow.compile(
        interrupt_after=["select_agents"]  # HITL: pause after selection, before review
    )
    
    logger.info("✅ Agent selector graph compiled with iterative refinement loop")
    logger.info("🔄 Loop: select_agents → review_selection → [needs_refinement?] → select_agents")
    logger.info("🏁 End flow: review_selection → finalize_selection → END")
    logger.info("📋 Finalize conditions: approved, rejected, max_iterations (3), or high confidence")
    return compiled


# ============================================================================
# STUDIO EXPORT
# ============================================================================

def get_graph():
    """Export for LangGraph Studio."""
    try:
        return build_graph()
    except Exception as e:
        logger.error(f"Failed to build agent selector graph: {e}")
        logger.exception("Full traceback:")
        # Return None to allow Studio to start even if this graph fails
        return None


# Export for Studio
try:
    graph = get_graph()
except Exception as e:
    logger.error(f"Failed to export agent selector graph: {e}")
    logger.exception("Full traceback:")
    graph = None  # Allow Studio to start even if this graph fails

