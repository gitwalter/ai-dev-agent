"""
Isolated Complexity Analyzer Graph for LangGraph Studio Testing

This graph contains ONLY the complexity analyzer node, allowing isolated testing
of Phase 1 context detection (US-CONTEXT-001) in LangGraph Studio.

Usage in Studio:
1. Select this graph from the dropdown
2. Provide initial state with project_context
3. Execute and view the detected context (complexity, domain, intent, entities)
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
# STATE - Simplified for Complexity Analyzer Only
# ============================================================================

class ComplexityAnalyzerState(TypedDict):
    """State for isolated complexity analyzer testing."""
    # Input
    project_context: str
    
    # Output - Context Detection (Phase 1: US-CONTEXT-001)
    project_complexity: str  # simple, medium, complex
    project_domain: str  # ai, web, api, data, mobile, library, utility, general
    project_intent: str  # new_feature, bug_fix, refactor, migration, enhancement, general
    detected_entities: List[str]  # Technology names, frameworks, services
    
    # Context Detection Confidence & Questions
    context_confidence: float  # 0.0 to 1.0 - confidence in detection
    needs_more_info: bool  # True if agent needs more information
    information_requests: List[str]  # Questions to ask user for clarification
    context_summary: str  # Human-readable summary of detected context
    
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
# COMPLEXITY ANALYZER NODE
# ============================================================================

def _create_llm():
    """Create LLM instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=0.0  # Deterministic for testing
    )


def analyze_complexity_node(state: ComplexityAnalyzerState) -> Dict[str, Any]:
    """
    Analyze project complexity, domain, intent, and entities using LLM.
    
    Phase 1 (US-CONTEXT-001): Enhanced context detection that classifies:
    - Complexity: simple, medium, complex
    - Domain: ai, web, api, data, mobile, etc.
    - Intent: new_feature, bug_fix, refactor, migration, etc.
    - Entities: Technology names, frameworks, services extracted from context
    """
    logger.info("📊 Analyzing complexity and context with LLM...")
    
    llm = _create_llm()
    system_prompt = load_prompt_from_langsmith(
        "complexity_analyzer_v1",
        "You are a Complexity Analyzer. Analyze project complexity and context."
    )
    
    # Enhanced task prompt for context detection
    task = f"""Analyze this software project and classify:

Project: {state['project_context']}

Classify the following:
1. COMPLEXITY: simple, medium, or complex
2. DOMAIN: ai, web, api, data, mobile, library, utility, or general
3. INTENT: new_feature, bug_fix, refactor, migration, enhancement, or general
4. ENTITIES: List key technologies, frameworks, services mentioned (comma-separated)

Respond with ONLY valid JSON (no markdown, no extra text):
{{
    "project_complexity": "simple|medium|complex",
    "project_domain": "ai|web|api|data|mobile|library|utility|general",
    "project_intent": "new_feature|bug_fix|refactor|migration|enhancement|general",
    "detected_entities": ["entity1", "entity2", "entity3"]
}}

Example:
{{
    "project_complexity": "complex",
    "project_domain": "ai",
    "project_intent": "new_feature",
    "detected_entities": ["rag", "document", "search", "vector", "embeddings"]
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
        
        # Validate and extract values with defaults
        complexity = parsed.get("project_complexity", "medium").lower()
        if complexity not in ["simple", "medium", "complex"]:
            complexity = "medium"
        
        domain = parsed.get("project_domain", "general").lower()
        if domain not in ["ai", "web", "api", "data", "mobile", "library", "utility", "general"]:
            domain = "general"
        
        intent = parsed.get("project_intent", "new_feature").lower()
        if intent not in ["new_feature", "bug_fix", "refactor", "migration", "enhancement", "general"]:
            intent = "new_feature"
        
        entities = parsed.get("detected_entities", [])
        if not isinstance(entities, list):
            entities = []
        
        # Calculate confidence based on detection quality
        confidence = _calculate_confidence(parsed, complexity, domain, intent, entities)
        
        # Determine if more information is needed
        needs_more_info = confidence < 0.7 or len(entities) == 0
        
        # Generate information requests if needed
        information_requests = []
        if needs_more_info:
            information_requests = _generate_information_requests(
                state['project_context'], complexity, domain, intent, entities
            )
        
        # Create human-readable summary
        context_summary = _format_context_summary(complexity, domain, intent, entities, confidence)
        
        logger.info(
            f"📊 Context detected: complexity={complexity}, domain={domain}, "
            f"intent={intent}, entities={len(entities)}, confidence={confidence:.2f}"
        )
        
        return {
            "project_complexity": complexity,
            "project_domain": domain,
            "project_intent": intent,
            "detected_entities": entities,
            "context_confidence": confidence,
            "needs_more_info": needs_more_info,
            "information_requests": information_requests,
            "context_summary": context_summary,
            "current_step": "complexity_analyzed"
        }
        
    except Exception as e:
        logger.warning(f"Failed to parse context detection JSON: {e}. Using defaults.")
        # Fallback to defaults - low confidence since parsing failed
        return {
            "project_complexity": "medium",
            "project_domain": "general",
            "project_intent": "new_feature",
            "detected_entities": [],
            "context_confidence": 0.3,  # Low confidence due to error
            "needs_more_info": True,
            "information_requests": [
                "Could you provide more details about the project?",
                "What is the main purpose of this project?",
                "What technologies or frameworks will be used?"
            ],
            "context_summary": "⚠️ Context detection failed. Default values assigned. Please provide more information.",
            "current_step": "complexity_analyzed",
            "errors": [f"Context detection error: {str(e)}"]
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _calculate_confidence(parsed: Dict, complexity: str, domain: str, intent: str, entities: List[str]) -> float:
    """Calculate confidence score for context detection."""
    confidence = 0.5  # Base confidence
    
    # Higher confidence if we got specific values (not defaults)
    if complexity != "medium":  # Not default
        confidence += 0.1
    if domain != "general":  # Not default
        confidence += 0.15
    if intent != "new_feature":  # Not default
        confidence += 0.1
    
    # Higher confidence with more entities detected
    if len(entities) >= 3:
        confidence += 0.15
    elif len(entities) >= 1:
        confidence += 0.1
    
    # Bonus if parsed successfully
    if parsed:
        confidence += 0.05
    
    return min(confidence, 1.0)  # Cap at 1.0


def _generate_information_requests(context: str, complexity: str, domain: str, intent: str, entities: List[str]) -> List[str]:
    """Generate questions to ask user for more information."""
    requests = []
    
    # Check what's missing or unclear
    if domain == "general":
        requests.append("What domain does this project belong to? (e.g., AI, web, API, data processing)")
    
    if intent == "new_feature" and "new" not in context.lower() and "create" not in context.lower():
        requests.append("Is this a new feature, bug fix, refactoring, or migration?")
    
    if len(entities) < 2:
        requests.append("What specific technologies, frameworks, or tools will be used?")
    
    if complexity == "medium" and len(context.split()) < 10:
        requests.append("Could you provide more details about the project scope and requirements?")
    
    # If no specific requests, add generic ones
    if not requests:
        requests.append("Are there any specific requirements or constraints we should know about?")
    
    return requests


def _format_context_summary(complexity: str, domain: str, intent: str, entities: List[str], confidence: float) -> str:
    """Create human-readable summary of detected context."""
    summary_parts = [
        f"**Complexity**: {complexity.title()}",
        f"**Domain**: {domain.title()}",
        f"**Intent**: {intent.replace('_', ' ').title()}",
        f"**Confidence**: {confidence:.0%}"
    ]
    
    if entities:
        summary_parts.append(f"**Detected Technologies**: {', '.join(entities[:5])}")
        if len(entities) > 5:
            summary_parts.append(f"_(and {len(entities) - 5} more)_")
    else:
        summary_parts.append("**Detected Technologies**: None detected")
    
    return "\n".join(summary_parts)


# ============================================================================
# HITL REVIEW NODE
# ============================================================================

def review_context_node(state: ComplexityAnalyzerState) -> Dict[str, Any]:
    """
    HITL checkpoint: Review detected context, answer questions, and process human feedback.
    
    This node:
    1. Displays detected context in a readable format
    2. Answers human questions if provided (Q&A capability)
    3. Processes human feedback if provided
    4. Updates context if human provides corrections or additional info
    5. Sets routing decision for loop or END
    """
    logger.info("👤 HITL Checkpoint: Reviewing context detection...")
    
    # Get iteration count (safety limit)
    iteration_count = state.get('iteration_count', 0)
    max_iterations = 3  # Safety limit to prevent infinite loops
    
    # Get human feedback and questions if provided
    human_feedback = state.get('human_feedback', '')
    human_approval = state.get('human_approval', '')
    human_question = state.get('human_question', '')
    
    # Start with current state values
    updated_state = {
        "current_step": "context_review",
        "context_summary": state.get('context_summary', '')
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
                # Extract entities from feedback
                feedback_entities = _extract_entities_from_feedback(human_feedback)
                
                # Merge feedback into project_context
                original_context = state.get('project_context', '')
                enriched_context = f"{original_context}\n\nAdditional requirements: {human_feedback}"
                
                # Update detected entities with feedback entities
                existing_entities = state.get('detected_entities', [])
                all_entities = list(set(existing_entities + feedback_entities))
                
                # Update state with refined information
                updated_state.update({
                    "project_context": enriched_context,
                    "detected_entities": all_entities,
                    "context_confidence": min(state.get('context_confidence', 0.0) + 0.1, 1.0),  # Boost confidence after refinement
                    "iteration_count": iteration_count + 1  # Increment iteration counter
                })
                
                logger.info(f"✅ Context refined: Added {len(feedback_entities)} entities from feedback")
                logger.info(f"📦 Updated entities: {all_entities}")
                logger.info(f"🔄 Iteration {updated_state['iteration_count']}/{max_iterations}")
            
        elif human_approval.lower() == 'rejected':
            logger.warning("❌ Context rejected by human - ending workflow")
            # Keep original values, end workflow
            
        elif human_approval.lower() == 'approved':
            logger.info("✅ Context approved by human - ending workflow")
            # Context is correct, no changes needed
    
    # Format review message
    review_message = f"""
# Context Detection Review

## Detected Context

{state.get('context_summary', 'No context detected')}

## Status

- **Confidence**: {updated_state.get('context_confidence', state.get('context_confidence', 0.0)):.0%}
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
                if 'detected_entities' in updated_state:
                    review_message += f"- **Updated Entities**: {', '.join(updated_state['detected_entities'])}\n"
                if 'project_context' in updated_state:
                    review_message += f"- **Context Enriched**: Additional requirements included\n"
                review_message += f"- **Confidence Updated**: {updated_state.get('context_confidence', 0.0):.0%}\n"
                review_message += f"- **Next**: Will re-analyze context with enriched information\n"
    
    if human_approval:
        review_message += f"\n## Approval Status: {human_approval}\n"
    
    # Signal workflow status based on routing decision
    if human_approval.lower() == 'needs_refinement' and iteration_count < max_iterations:
        review_message += "\n## Workflow Status\n\n🔄 **Refinement requested - will re-analyze context**\n"
    elif human_approval.lower() == 'approved':
        review_message += "\n## Workflow Status\n\n✅ **Context approved - workflow will complete**\n"
    elif human_approval.lower() == 'rejected':
        review_message += "\n## Workflow Status\n\n❌ **Context rejected - workflow ending**\n"
    else:
        review_message += "\n## Workflow Status\n\n✅ **Context review complete - workflow finished**\n"
    
    # Update context summary with the review message
    updated_state['context_summary'] = review_message
    
    logger.info("📋 Review message prepared")
    
    return updated_state


def finalize_context_node(state: ComplexityAnalyzerState) -> Dict[str, Any]:
    """
    Final completion node: Generate final summary message before workflow ends.
    
    This node runs when workflow is ending (approved/rejected/max_iterations)
    to provide a clear final message to the user.
    """
    logger.info("🏁 Finalizing context detection workflow...")
    
    human_approval = state.get('human_approval', '').lower()
    iteration_count = state.get('iteration_count', 0)
    
    # Determine completion status
    if human_approval == 'approved':
        status_emoji = "✅"
        status_text = "Approved"
        completion_message = "Context approved and workflow completed successfully."
    elif human_approval == 'rejected':
        status_emoji = "❌"
        status_text = "Rejected"
        completion_message = "Context rejected. Workflow ending."
    elif iteration_count >= 3:
        status_emoji = "⚠️"
        status_text = "Max Iterations Reached"
        completion_message = "Maximum refinement iterations reached. Workflow ending."
    else:
        status_emoji = "✅"
        status_text = "Complete"
        completion_message = "Context detection workflow completed."
    
    # Build final summary with all detected context
    detected_summary = state.get('context_summary', '')
    
    # If context_summary is empty or just review message, create a proper summary
    if not detected_summary or "Context Detection Review" in detected_summary:
        detected_summary = _format_context_summary(
            state.get('project_complexity', 'medium'),
            state.get('project_domain', 'general'),
            state.get('project_intent', 'new_feature'),
            state.get('detected_entities', []),
            state.get('context_confidence', 0.0)
        )
    
    # Create final completion message
    final_message = f"""
# {status_emoji} Context Detection Complete

## Final Summary

{completion_message}

## Detected Context

{detected_summary}

## Final Context Values

- **Complexity**: {state.get('project_complexity', 'medium').title()}
- **Domain**: {state.get('project_domain', 'general').title()}
- **Intent**: {state.get('project_intent', 'new_feature').replace('_', ' ').title()}
- **Confidence**: {state.get('context_confidence', 0.0):.0%}
- **Iterations**: {iteration_count}
- **Status**: {status_emoji} {status_text}

## Detected Technologies

{', '.join(state.get('detected_entities', [])) if state.get('detected_entities') else 'None detected'}

---

## Workflow Complete

✅ **The context detection workflow has finished.**

The detected context is now ready for use in:
- Agent selection and routing
- Knowledge source filtering
- Tool selection and RAG
- Workflow optimization

**Current Step**: completed
"""
    
    logger.info(f"✅ Final message prepared - workflow complete (status: {status_text})")
    
    return {
        "current_step": "completed",
        "context_summary": final_message
    }


def _route_after_review(state: ComplexityAnalyzerState) -> str:
    """
    Routing function: Decide whether to loop back for refinement or end workflow.
    
    Returns:
        "complexity_analyzer" if refinement needed and within iteration limit
        "finalize_context" if approved, rejected, or max iterations reached (to show final message)
    """
    human_approval = state.get('human_approval', '').lower()
    iteration_count = state.get('iteration_count', 0)
    max_iterations = 3
    
    # End conditions - route to finalize_context first (not directly to END)
    if human_approval == 'approved':
        logger.info("✅ Approved - routing to finalize_context")
        return "finalize_context"
    
    if human_approval == 'rejected':
        logger.info("❌ Rejected - routing to finalize_context")
        return "finalize_context"
    
    if iteration_count >= max_iterations:
        logger.info(f"⚠️ Max iterations ({max_iterations}) reached - routing to finalize_context")
        return "finalize_context"
    
    # Confidence-based auto-approval (if no human feedback and high confidence)
    if not human_approval and state.get('context_confidence', 0.0) >= 0.9:
        logger.info("✅ High confidence, no feedback - routing to finalize_context")
        return "finalize_context"
    
    # Loop back for refinement
    if human_approval == 'needs_refinement':
        logger.info(f"🔄 Refinement requested - looping back to complexity_analyzer (iteration {iteration_count + 1}/{max_iterations})")
        return "complexity_analyzer"
    
    # Default: route to finalize (end workflow)
    logger.info("🏁 No refinement requested - routing to finalize_context")
    return "finalize_context"


def _extract_entities_from_feedback(feedback: str) -> List[str]:
    """
    Extract technology/framework entities from human feedback.
    
    Examples:
    - "PDF and Markdown files" -> ["PDF", "Markdown"]
    - "semantic search" -> ["semantic search"]
    - "Qdrant database" -> ["Qdrant"]
    """
    import re
    
    entities = []
    
    # Common technology patterns
    tech_patterns = [
        r'\b(PDF|Markdown|JSON|CSV|XML|HTML|YAML)\b',
        r'\b(semantic search|vector search|full-text search)\b',
        r'\b(Qdrant|Pinecone|Weaviate|Chroma|Milvus|FAISS)\b',
        r'\b(FastAPI|Flask|Django|Express|Next\.js|React|Vue)\b',
        r'\b(PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch)\b',
        r'\b(Docker|Kubernetes|AWS|GCP|Azure)\b',
    ]
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, feedback, re.IGNORECASE)
        entities.extend([m if isinstance(m, str) else m[0] for m in matches])
    
    # Extract quoted or capitalized terms
    quoted_terms = re.findall(r'["\']([^"\']+)["\']', feedback)
    entities.extend(quoted_terms)
    
    # Extract capitalized technical terms (likely technologies)
    capitalized_terms = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', feedback)
    entities.extend([term for term in capitalized_terms if len(term) > 2])
    
    # Clean and deduplicate
    entities = [e.strip() for e in entities if e.strip()]
    entities = list(set(entities))
    
    # Filter out common non-technical words
    common_words = {'The', 'And', 'This', 'That', 'Should', 'Support', 'Handle', 'System'}
    entities = [e for e in entities if e not in common_words]
    
    return entities


# ============================================================================
# GRAPH BUILDING
# ============================================================================

def build_graph():
    """
    Build isolated complexity analyzer graph with HITL checkpoint and iterative refinement loop.
    
    Graph flow:
    START → complexity_analyzer → [interrupt_after] → review_context → [conditional]
                                                                    ├→ complexity_analyzer (if needs_refinement)
                                                                    └→ finalize_context → END (if approved/rejected/max_iterations)
    
    NOTE: For LangGraph Studio, we use interrupt_after on complexity_analyzer
    instead of interrupt_before on review_context to ensure proper END edge handling.
    """
    workflow = StateGraph(ComplexityAnalyzerState)
    
    # Add nodes
    workflow.add_node("complexity_analyzer", analyze_complexity_node)
    workflow.add_node("review_context", review_context_node)
    workflow.add_node("finalize_context", finalize_context_node)  # Final completion node
    
    # Flow: START → complexity_analyzer → review_context → [conditional] → complexity_analyzer OR finalize_context → END
    workflow.set_entry_point("complexity_analyzer")
    workflow.add_edge("complexity_analyzer", "review_context")
    
    # Conditional edge: review_context → complexity_analyzer (loop) OR finalize_context
    workflow.add_conditional_edges(
        "review_context",
        _route_after_review,  # Routing function decides next step
        {
            "complexity_analyzer": "complexity_analyzer",  # Loop back for refinement
            "finalize_context": "finalize_context"  # Finalize and end
        }
    )
    
    # Finalize context → END (always ends workflow)
    workflow.add_edge("finalize_context", END)
    
    # Use interrupt_after instead of interrupt_before for better END handling
    # This pauses AFTER complexity_analyzer, allowing review_context to complete normally
    compiled = workflow.compile(
        interrupt_after=["complexity_analyzer"]  # HITL: pause after analysis, before review
    )
    
    logger.info("✅ Complexity analyzer graph compiled with iterative refinement loop")
    logger.info("🔄 Loop: complexity_analyzer → review_context → [needs_refinement?] → complexity_analyzer")
    logger.info("🏁 End flow: review_context → finalize_context → END")
    logger.info("📋 Finalize conditions: approved, rejected, max_iterations (3), or high confidence")
    return compiled


# ============================================================================
# STUDIO EXPORT
# ============================================================================

def get_graph():
    """Export for LangGraph Studio."""
    return build_graph()


# Export for Studio
graph = get_graph()

