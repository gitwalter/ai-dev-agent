"""
Isolated Requirements Analyst Graph for LangGraph Studio Testing

This graph contains ONLY the requirements analyst node, allowing isolated testing
of Phase 3 context-aware requirements analysis (US-CONTEXT-001) in LangGraph Studio.

Usage in Studio:
1. Select this graph from the dropdown
2. Provide initial state with project_context and detected context
3. Execute and view the requirements analysis
4. Review and refine requirements via HITL checkpoint
"""

from __future__ import annotations

import logging
import os
from typing import Dict, Any, List
try:
    from typing_extensions import TypedDict, NotRequired  # Python < 3.12 compatibility
except ImportError:
    from typing import TypedDict  # Python >= 3.12
    try:
        from typing import NotRequired
    except ImportError:
        # Python < 3.11 - NotRequired not available, use Optional fields
        NotRequired = None
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


# ============================================================================
# STATE - Simplified for Requirements Analyst Only
# ============================================================================

class RequirementsAnalystState(TypedDict, total=False):
    """State for isolated requirements analyst testing."""
    # Input - Context from complexity_analyzer (required for initial state)
    project_context: str
    project_complexity: str  # simple, medium, complex
    project_domain: str  # ai, web, api, data, mobile, library, utility, general
    project_intent: str  # new_feature, bug_fix, refactor, migration, enhancement, general
    detected_entities: List[str]  # Technology names, frameworks, services
    
    # Output - Requirements Analysis (optional, populated by nodes)
    requirements_analysis: Dict[str, Any]  # Complete requirements analysis JSON
    functional_requirements: List[Dict[str, Any]]  # Functional requirements list
    non_functional_requirements: List[Dict[str, Any]]  # Non-functional requirements list
    user_stories: List[Dict[str, Any]]  # User stories list
    technical_constraints: List[str]  # Technical constraints
    business_constraints: List[str]  # Business constraints
    assumptions: List[str]  # Assumptions
    risks: List[str]  # Risks
    analysis_confidence: float  # 0.0 to 1.0 - confidence in analysis quality
    needs_more_info: bool  # True if agent needs more information
    information_requests: List[str]  # Questions to ask user for clarification
    analysis_summary: str  # Human-readable summary of requirements analysis
    
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
# REQUIREMENTS ANALYST NODE
# ============================================================================

def _create_llm():
    """Create LLM instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=0.0  # Deterministic for testing
    )


def analyze_requirements_node(state: RequirementsAnalystState) -> Dict[str, Any]:
    """
    Analyze project requirements using LLM with context-aware analysis.
    
    Phase 3 (US-CONTEXT-001): Enhanced requirements analysis that uses detected context:
    - Domain, intent, complexity, and entities inform requirements analysis
    - Better requirements analysis accuracy with context-aware focus
    
    CRITICAL: Uses context to focus on domain-specific requirements and concerns.
    """
    logger.info("📋 Analyzing requirements with context-aware LLM...")
    
    llm = _create_llm()
    system_prompt = load_prompt_from_langsmith(
        "requirements_analyst_v1",
        "You are an expert Requirements Analyst. Analyze project requirements thoroughly and comprehensively."
    )
    
    # Enhanced task prompt with context information
    task = f"""Analyze project requirements and generate comprehensive requirements documentation.

PROJECT CONTEXT: {state.get('project_context', 'No project context provided')}

DETECTED CONTEXT:
- Domain: {state.get('project_domain', 'general')}
- Intent: {state.get('project_intent', 'new_feature')}
- Complexity: {state.get('project_complexity', 'medium')}
- Entities: {', '.join(state.get('detected_entities', [])[:10])}

CONTEXT-AWARE ANALYSIS GUIDANCE:
- Domain: {state.get('project_domain', 'general')} → Focus on domain-specific requirements
  * ai → AI/ML requirements (models, training, inference, data pipelines)
  * web → Web development requirements (APIs, frontend, backend, deployment)
  * api → API-specific requirements (endpoints, authentication, rate limiting)
  * data → Data processing requirements (ETL, storage, analytics)

- Intent: {state.get('project_intent', 'new_feature')} → Tailor analysis approach
  * new_feature → Comprehensive requirements analysis (all requirements)
  * bug_fix → Focus on fixing existing requirements, minimal new requirements
  * refactor → Focus on technical requirements, maintainability

- Complexity: {state.get('project_complexity', 'medium')} → Adjust detail level
  * simple → Focus on core requirements, minimal complexity
  * medium → Standard requirements analysis depth
  * complex → Detailed requirements analysis with extensive coverage

- Entities: {', '.join(state.get('detected_entities', []))} → Consider technology-specific requirements
  * Mention specific technologies, frameworks, or services in requirements
  * Include constraints and considerations for these technologies

Respond with ONLY valid JSON (no markdown, no extra text):
{{
    "summary": "Concise overview of the project goals and requirements scope",
    "functional_requirements": [
        {{
            "id": "FR-001",
            "title": "Requirement Title",
            "description": "Detailed, actionable description",
            "priority": "High|Medium|Low",
            "acceptance_criteria": ["Criterion 1", "Criterion 2"],
            "dependencies": ["FR-002"],
            "rationale": "Why this requirement is necessary"
        }}
    ],
    "non_functional_requirements": [
        {{
            "id": "NFR-001",
            "category": "Performance|Security|Usability|Scalability|Maintainability|Compliance|Reliability",
            "description": "Detailed and measurable non-functional goal",
            "metric": "e.g., Response time < 200ms, Uptime >= 99.9%",
            "priority": "High|Medium|Low",
            "rationale": "Business or technical justification"
        }}
    ],
    "constraints_and_assumptions": [
        {{
            "type": "constraint|assumption",
            "description": "Explicit system boundaries or dependencies"
        }}
    ],
    "gaps_and_ambiguities": [
        {{
            "category": "Missing requirement|Ambiguous statement|Inconsistency|Undefined metric",
            "description": "Detailed issue description",
            "impact": "High|Medium|Low",
            "recommendation": "Specific action to resolve"
        }}
    ],
    "quality_assessment": {{
        "clarity": "Pass/Fail + brief justification",
        "completeness": "Pass/Fail + brief justification",
        "consistency": "Pass/Fail + brief justification",
        "testability": "Pass/Fail + brief justification",
        "traceability": "Pass/Fail + brief justification"
    }},
    "improvement_recommendations": [
        "Specific improvements or refinements"
    ]
}}

CRITICAL: Use the detected context to focus your analysis:
- Domain ({state.get('project_domain', 'general')}) → Domain-specific requirements
- Intent ({state.get('project_intent', 'new_feature')}) → Appropriate analysis depth
- Complexity ({state.get('project_complexity', 'medium')}) → Appropriate detail level
- Entities ({', '.join(state.get('detected_entities', [])[:5])}) → Technology-specific considerations"""
    
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
        
        # Extract requirements components
        functional_requirements = parsed.get("functional_requirements", [])
        non_functional_requirements = parsed.get("non_functional_requirements", [])
        user_stories = []  # Extract from summary if needed
        technical_constraints = []
        business_constraints = []
        assumptions = []
        risks = []
        
        # Extract from constraints_and_assumptions
        constraints_and_assumptions = parsed.get("constraints_and_assumptions", [])
        for item in constraints_and_assumptions:
            if item.get("type") == "constraint":
                technical_constraints.append(item.get("description", ""))
            elif item.get("type") == "assumption":
                assumptions.append(item.get("description", ""))
        
        # Extract risks from gaps_and_ambiguities if high impact
        gaps_and_ambiguities = parsed.get("gaps_and_ambiguities", [])
        for gap in gaps_and_ambiguities:
            if gap.get("impact") == "High":
                risks.append(gap.get("description", ""))
        
        # Calculate confidence based on analysis quality
        confidence = _calculate_analysis_confidence(
            parsed,
            state.get('project_complexity', 'medium'),
            state.get('project_domain', 'general'),
            state.get('project_intent', 'new_feature')
        )
        
        # Determine if more information is needed
        needs_more_info = confidence < 0.7 or len(gaps_and_ambiguities) > 3
        
        # Generate information requests if needed
        information_requests = []
        if needs_more_info:
            information_requests = _generate_requirements_questions(
                state.get('project_context', ''),
                parsed,
                state.get('project_complexity', 'medium'),
                state.get('project_domain', 'general'),
                state.get('project_intent', 'new_feature')
            )
        
        # Create human-readable summary
        analysis_summary = _format_requirements_summary(parsed, confidence)
        
        logger.info(
            f"📋 Requirements analysis completed: {len(functional_requirements)} functional, "
            f"{len(non_functional_requirements)} non-functional (confidence: {confidence:.2f})"
        )
        
        return {
            "requirements_analysis": parsed,
            "functional_requirements": functional_requirements,
            "non_functional_requirements": non_functional_requirements,
            "user_stories": user_stories,
            "technical_constraints": technical_constraints,
            "business_constraints": business_constraints,
            "assumptions": assumptions,
            "risks": risks,
            "analysis_confidence": confidence,
            "needs_more_info": needs_more_info,
            "information_requests": information_requests,
            "analysis_summary": analysis_summary,
            "current_step": "requirements_analyzed"
        }
        
    except Exception as e:
        logger.warning(f"Failed to parse requirements analysis JSON: {e}. Using defaults.")
        # Fallback to default analysis
        return {
            "requirements_analysis": {"summary": f"Analysis failed: {str(e)}"},
            "functional_requirements": [],
            "non_functional_requirements": [],
            "user_stories": [],
            "technical_constraints": [],
            "business_constraints": [],
            "assumptions": [],
            "risks": [],
            "analysis_confidence": 0.3,
            "needs_more_info": True,
            "information_requests": [
                "Could you provide more details about the project requirements?",
                "What are the main goals of this project?",
                "What are the key constraints or limitations?"
            ],
            "analysis_summary": f"⚠️ Requirements analysis failed. Error: {str(e)}. Please provide more information.",
            "current_step": "requirements_analyzed",
            "errors": [f"Requirements analysis error: {str(e)}"]
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _calculate_analysis_confidence(
    analysis: Dict[str, Any],
    complexity: str,
    domain: str,
    intent: str
) -> float:
    """Calculate confidence score for requirements analysis."""
    confidence = 0.5  # Base confidence
    
    # Check if analysis has required components
    functional = analysis.get("functional_requirements", [])
    non_functional = analysis.get("non_functional_requirements", [])
    
    # Minimum requirements present
    if len(functional) >= 3:
        confidence += 0.15
    if len(non_functional) >= 2:
        confidence += 0.15
    
    # Quality assessment present
    quality_assessment = analysis.get("quality_assessment", {})
    if quality_assessment:
        # Check if quality gates passed
        passed_count = sum(1 for v in quality_assessment.values() if "Pass" in str(v))
        if passed_count >= 4:
            confidence += 0.1
    
    # Gaps identified (shows thoroughness)
    gaps = analysis.get("gaps_and_ambiguities", [])
    if 0 < len(gaps) <= 3:
        confidence += 0.1  # Some gaps identified is good
    
    # Complexity-based validation
    if complexity == "complex":
        if len(functional) >= 5 and len(non_functional) >= 3:
            confidence += 0.05
    elif complexity == "medium":
        if len(functional) >= 3 and len(non_functional) >= 2:
            confidence += 0.05
    elif complexity == "simple":
        if len(functional) >= 2:
            confidence += 0.05
    
    # Domain-specific validation (check if domain mentioned in requirements)
    summary = analysis.get("summary", "").lower()
    domain_keywords = {
        "ai": ["ai", "ml", "machine learning", "model", "training"],
        "web": ["web", "api", "http", "frontend", "backend"],
        "api": ["api", "endpoint", "rest", "graphql"],
        "data": ["data", "database", "etl", "analytics"]
    }
    
    if domain in domain_keywords:
        keywords = domain_keywords[domain]
        if any(keyword in summary for keyword in keywords):
            confidence += 0.05
    
    return min(confidence, 1.0)  # Cap at 1.0


def _generate_requirements_questions(
    context: str,
    analysis: Dict[str, Any],
    complexity: str,
    domain: str,
    intent: str
) -> List[str]:
    """Generate questions to ask user for more information about requirements."""
    requests = []
    
    # Check if analysis seems incomplete
    functional = analysis.get("functional_requirements", [])
    non_functional = analysis.get("non_functional_requirements", [])
    
    if len(functional) < 3:
        requests.append("What are the main functional features or capabilities needed?")
    
    if len(non_functional) < 2:
        requests.append("What are the non-functional requirements (performance, security, scalability)?")
    
    # Domain-specific questions
    if domain == "general" and len(functional) < 4:
        requests.append("What domain does this project belong to? (e.g., AI, web, API, data processing)")
    
    # Complexity questions
    if complexity == "medium" and len(functional) < 4:
        requests.append("Are there additional requirements or features that should be included?")
    
    # Intent-specific questions
    if intent == "new_feature" and len(functional) < 4:
        requests.append("What specific features or capabilities should this new feature provide?")
    
    # Gaps and ambiguities
    gaps = analysis.get("gaps_and_ambiguities", [])
    if gaps:
        high_impact_gaps = [g for g in gaps if g.get("impact") == "High"]
        if high_impact_gaps:
            for gap in high_impact_gaps[:2]:  # Limit to top 2
                requests.append(f"Can you clarify: {gap.get('description', '')[:100]}?")
    
    # If no specific requests, add generic ones
    if not requests:
        requests.append("Are there any specific requirements or constraints that should be considered?")
    
    return requests


def _format_requirements_summary(
    analysis: Dict[str, Any],
    confidence: float
) -> str:
    """Create human-readable summary of requirements analysis."""
    summary_parts = [
        f"**Requirements Analysis Summary**",
        f"",
        f"**Overall Confidence**: {confidence:.0%}",
        f"",
        f"**Functional Requirements**: {len(analysis.get('functional_requirements', []))}",
        f"**Non-Functional Requirements**: {len(analysis.get('non_functional_requirements', []))}",
        f"",
        f"**Project Overview**:",
        f"{analysis.get('summary', 'No summary provided')}",
        f""
    ]
    
    # Add quality assessment
    quality_assessment = analysis.get("quality_assessment", {})
    if quality_assessment:
        summary_parts.append("**Quality Assessment**:")
        for criterion, result in quality_assessment.items():
            summary_parts.append(f"- {criterion.capitalize()}: {result}")
        summary_parts.append("")
    
    # Add gaps if any
    gaps = analysis.get("gaps_and_ambiguities", [])
    if gaps:
        summary_parts.append(f"**Gaps and Ambiguities**: {len(gaps)} identified")
        for gap in gaps[:3]:  # Show top 3
            summary_parts.append(f"- [{gap.get('impact', 'Unknown')} Impact] {gap.get('description', '')[:100]}")
        summary_parts.append("")
    
    # Add recommendations if any
    recommendations = analysis.get("improvement_recommendations", [])
    if recommendations:
        summary_parts.append(f"**Improvement Recommendations**: {len(recommendations)}")
        for rec in recommendations[:3]:  # Show top 3
            summary_parts.append(f"- {rec[:150]}")
    
    return "\n".join(summary_parts)


# ============================================================================
# HITL REVIEW NODE
# ============================================================================

def review_requirements_node(state: RequirementsAnalystState) -> Dict[str, Any]:
    """
    HITL checkpoint: Review requirements analysis and process human feedback.
    
    This node:
    1. Displays requirements analysis in a readable format
    2. Processes human feedback if provided
    3. Updates requirements if human provides corrections
    4. Sets routing decision for loop or END
    """
    logger.info("👤 HITL Checkpoint: Reviewing requirements analysis...")
    
    # Get iteration count (safety limit)
    iteration_count = state.get('iteration_count', 0)
    max_iterations = 3  # Safety limit to prevent infinite loops
    
    # Get human feedback and questions if provided
    human_feedback = state.get('human_feedback', '')
    human_approval = state.get('human_approval', '')
    human_question = state.get('human_question', '')
    
    # Start with current state values
    updated_state = {
        "current_step": "requirements_review",
        "analysis_summary": state.get('analysis_summary', '')
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
                # Extract additional requirements from feedback
                feedback_info = _extract_requirements_from_feedback(human_feedback)
                
                # Merge with existing analysis
                existing_analysis = state.get('requirements_analysis', {})
                if feedback_info:
                    # Enrich analysis with feedback
                    enriched_analysis = _enrich_analysis_with_feedback(existing_analysis, feedback_info)
                    updated_state.update({
                        "requirements_analysis": enriched_analysis,
                        "analysis_confidence": min(state.get('analysis_confidence', 0.0) + 0.1, 1.0),
                        "iteration_count": iteration_count + 1
                    })
                else:
                    # Keep existing but boost confidence
                    updated_state.update({
                        "analysis_confidence": min(state.get('analysis_confidence', 0.0) + 0.1, 1.0),
                        "iteration_count": iteration_count + 1
                    })
                
                logger.info(f"✅ Requirements refined: Updated analysis")
                logger.info(f"🔄 Iteration {updated_state['iteration_count']}/{max_iterations}")
            
        elif human_approval.lower() == 'rejected':
            logger.warning("❌ Requirements analysis rejected by human - ending workflow")
            
        elif human_approval.lower() == 'approved':
            logger.info("✅ Requirements analysis approved by human - ending workflow")
    
    # Format review message
    analysis = state.get('requirements_analysis', {})
    functional_count = len(state.get('functional_requirements', []))
    non_functional_count = len(state.get('non_functional_requirements', []))
    
    review_message = f"""
# Requirements Analysis Review

## Analysis Summary

{state.get('analysis_summary', 'No analysis available')}

## Requirements Count

- **Functional Requirements**: {functional_count}
- **Non-Functional Requirements**: {non_functional_count}
- **Technical Constraints**: {len(state.get('technical_constraints', []))}
- **Risks Identified**: {len(state.get('risks', []))}

## Status

- **Confidence**: {updated_state.get('analysis_confidence', state.get('analysis_confidence', 0.0)):.0%}
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
                review_message += f"- **Confidence Updated**: {updated_state.get('analysis_confidence', 0.0):.0%}\n"
                review_message += f"- **Next**: Will re-analyze requirements with refined information\n"
    
    if human_approval:
        review_message += f"\n## Approval Status: {human_approval}\n"
    
    # Signal workflow status based on routing decision
    if human_approval.lower() == 'needs_refinement' and iteration_count < max_iterations:
        review_message += "\n## Workflow Status\n\n🔄 **Refinement requested - will re-analyze requirements**\n"
    elif human_approval.lower() == 'approved':
        review_message += "\n## Workflow Status\n\n✅ **Requirements approved - workflow will complete**\n"
    elif human_approval.lower() == 'rejected':
        review_message += "\n## Workflow Status\n\n❌ **Requirements rejected - workflow ending**\n"
    else:
        review_message += "\n## Workflow Status\n\n✅ **Requirements analysis complete - workflow finished**\n"
    
    # Update analysis summary with the review message
    updated_state['analysis_summary'] = review_message
    
    logger.info("📋 Review message prepared")
    
    return updated_state


def _extract_requirements_from_feedback(feedback: str) -> Dict[str, Any]:
    """
    Extract requirement information from human feedback.
    
    Examples:
    - "Add requirement for authentication" → {"functional_requirements": ["authentication"]}
    - "Include performance requirements" → {"non_functional_requirements": ["performance"]}
    """
    feedback_lower = feedback.lower()
    extracted = {
        "functional_requirements": [],
        "non_functional_requirements": [],
        "constraints": [],
        "assumptions": []
    }
    
    # Look for functional requirement keywords
    functional_keywords = ["feature", "functionality", "capability", "requirement", "need"]
    if any(keyword in feedback_lower for keyword in functional_keywords):
        extracted["functional_requirements"].append(feedback)
    
    # Look for non-functional requirement keywords
    non_functional_keywords = ["performance", "security", "scalability", "usability", "reliability"]
    if any(keyword in feedback_lower for keyword in non_functional_keywords):
        extracted["non_functional_requirements"].append(feedback)
    
    # Look for constraint keywords
    constraint_keywords = ["constraint", "limitation", "restriction", "must", "cannot"]
    if any(keyword in feedback_lower for keyword in constraint_keywords):
        extracted["constraints"].append(feedback)
    
    return extracted


def _enrich_analysis_with_feedback(
    existing_analysis: Dict[str, Any],
    feedback_info: Dict[str, Any]
) -> Dict[str, Any]:
    """Enrich existing analysis with feedback information."""
    enriched = existing_analysis.copy()
    
    # Add functional requirements from feedback
    if feedback_info.get("functional_requirements"):
        func_reqs = enriched.get("functional_requirements", [])
        for feedback_req in feedback_info["functional_requirements"]:
            func_reqs.append({
                "id": f"FR-{len(func_reqs) + 1:03d}",
                "title": "Additional Requirement",
                "description": feedback_req,
                "priority": "Medium",
                "acceptance_criteria": [],
                "dependencies": [],
                "rationale": "Added based on human feedback"
            })
        enriched["functional_requirements"] = func_reqs
    
    # Add non-functional requirements from feedback
    if feedback_info.get("non_functional_requirements"):
        nfr_reqs = enriched.get("non_functional_requirements", [])
        for feedback_req in feedback_info["non_functional_requirements"]:
            nfr_reqs.append({
                "id": f"NFR-{len(nfr_reqs) + 1:03d}",
                "category": "General",
                "description": feedback_req,
                "metric": "To be defined",
                "priority": "Medium",
                "rationale": "Added based on human feedback"
            })
        enriched["non_functional_requirements"] = nfr_reqs
    
    return enriched


# ============================================================================
# FINALIZE NODE
# ============================================================================

def finalize_requirements_node(state: RequirementsAnalystState) -> Dict[str, Any]:
    """
    Final completion node: Generate final summary message before workflow ends.
    
    This node runs when workflow is ending (approved/rejected/max_iterations)
    to provide a clear final message to the user.
    """
    logger.info("🏁 Finalizing requirements analysis workflow...")
    
    human_approval = state.get('human_approval', '').lower()
    iteration_count = state.get('iteration_count', 0)
    analysis = state.get('requirements_analysis', {})
    functional_count = len(state.get('functional_requirements', []))
    non_functional_count = len(state.get('non_functional_requirements', []))
    
    # Determine completion status
    if human_approval == 'approved':
        status_emoji = "✅"
        status_text = "Approved"
        completion_message = "Requirements analysis approved and workflow completed successfully."
    elif human_approval == 'rejected':
        status_emoji = "❌"
        status_text = "Rejected"
        completion_message = "Requirements analysis rejected. Workflow ending."
    elif iteration_count >= 3:
        status_emoji = "⚠️"
        status_text = "Max Iterations Reached"
        completion_message = "Maximum refinement iterations reached. Workflow ending."
    else:
        status_emoji = "✅"
        status_text = "Complete"
        completion_message = "Requirements analysis workflow completed."
    
    # Build final summary
    analysis_summary = state.get('analysis_summary', '')
    if not analysis_summary or "Requirements Analysis Review" in analysis_summary:
        analysis_summary = _format_requirements_summary(
            analysis,
            state.get('analysis_confidence', 0.0)
        )
    
    # Create final completion message
    final_message = f"""
# {status_emoji} Requirements Analysis Complete

## Final Summary

{completion_message}

## Requirements Analysis Results

{analysis_summary}

## Final Analysis

- **Functional Requirements**: {functional_count}
- **Non-Functional Requirements**: {non_functional_count}
- **Technical Constraints**: {len(state.get('technical_constraints', []))}
- **Risks Identified**: {len(state.get('risks', []))}
- **Confidence**: {state.get('analysis_confidence', 0.0):.0%}
- **Iterations**: {iteration_count}
- **Status**: {status_emoji} {status_text}

## Project Overview

{analysis.get('summary', 'No summary available')}

---

## Workflow Complete

✅ **The requirements analysis workflow has finished.**

The requirements analysis is now ready for:
- Architecture design phase
- Code generation planning
- Test planning
- Project estimation

**Current Step**: completed
"""
    
    logger.info(f"✅ Final message prepared - workflow complete (status: {status_text})")
    
    return {
        "current_step": "completed",
        "analysis_summary": final_message
    }


# ============================================================================
# ROUTING FUNCTION
# ============================================================================

def _route_after_review(state: RequirementsAnalystState) -> str:
    """
    Routing function: Decide whether to loop back for refinement or end workflow.
    
    Returns:
        "analyze_requirements" if refinement needed and within iteration limit
        "finalize_requirements" if approved, rejected, or max iterations reached
    """
    human_approval = state.get('human_approval', '').lower()
    iteration_count = state.get('iteration_count', 0)
    max_iterations = 3
    
    # End conditions - route to finalize_requirements first
    if human_approval == 'approved':
        logger.info("✅ Approved - routing to finalize_requirements")
        return "finalize_requirements"
    
    if human_approval == 'rejected':
        logger.info("❌ Rejected - routing to finalize_requirements")
        return "finalize_requirements"
    
    if iteration_count >= max_iterations:
        logger.info(f"⚠️ Max iterations ({max_iterations}) reached - routing to finalize_requirements")
        return "finalize_requirements"
    
    # Confidence-based auto-approval (if no human feedback and high confidence)
    if not human_approval and state.get('analysis_confidence', 0.0) >= 0.9:
        logger.info("✅ High confidence, no feedback - routing to finalize_requirements")
        return "finalize_requirements"
    
    # Loop back for refinement
    if human_approval == 'needs_refinement':
        logger.info(f"🔄 Refinement requested - looping back to analyze_requirements (iteration {iteration_count + 1}/{max_iterations})")
        return "analyze_requirements"
    
    # Default: route to finalize
    logger.info("🏁 No refinement requested - routing to finalize_requirements")
    return "finalize_requirements"


# ============================================================================
# GRAPH BUILDING
# ============================================================================

def build_graph():
    """
    Build isolated requirements analyst graph with HITL checkpoint and iterative refinement loop.
    
    Graph flow:
    START → analyze_requirements → [interrupt_after] → review_requirements → [conditional]
                                                                              ├→ analyze_requirements (if needs_refinement)
                                                                              └→ finalize_requirements → END (if approved/rejected/max_iterations)
    
    NOTE: For LangGraph Studio, we use interrupt_after on analyze_requirements
    instead of interrupt_before on review_requirements to ensure proper END edge handling.
    """
    workflow = StateGraph(RequirementsAnalystState)
    
    # Add nodes
    workflow.add_node("analyze_requirements", analyze_requirements_node)
    workflow.add_node("review_requirements", review_requirements_node)
    workflow.add_node("finalize_requirements", finalize_requirements_node)  # Final completion node
    
    # Flow: START → analyze_requirements → review_requirements → [conditional] → analyze_requirements OR finalize_requirements → END
    workflow.set_entry_point("analyze_requirements")
    workflow.add_edge("analyze_requirements", "review_requirements")
    
    # Conditional edge: review_requirements → analyze_requirements (loop) OR finalize_requirements
    workflow.add_conditional_edges(
        "review_requirements",
        _route_after_review,  # Routing function decides next step
        {
            "analyze_requirements": "analyze_requirements",  # Loop back for refinement
            "finalize_requirements": "finalize_requirements"  # Finalize and end
        }
    )
    
    # Finalize requirements → END (always ends workflow)
    workflow.add_edge("finalize_requirements", END)
    
    # Use interrupt_after instead of interrupt_before for better END handling
    # This pauses AFTER analyze_requirements, allowing review_requirements to complete normally
    compiled = workflow.compile(
        interrupt_after=["analyze_requirements"]  # HITL: pause after analysis, before review
    )
    
    logger.info("✅ Requirements analyst graph compiled with iterative refinement loop")
    logger.info("🔄 Loop: analyze_requirements → review_requirements → [needs_refinement?] → analyze_requirements")
    logger.info("🏁 End flow: review_requirements → finalize_requirements → END")
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
        logger.error(f"Failed to build requirements analyst graph: {e}")
        logger.exception("Full traceback:")
        # Return None to allow Studio to start even if this graph fails
        return None


# Export for Studio
try:
    graph = get_graph()
except Exception as e:
    logger.error(f"Failed to export requirements analyst graph: {e}")
    logger.exception("Full traceback:")
    graph = None  # Allow Studio to start even if this graph fails

