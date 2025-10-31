"""
Isolated Architecture Designer Graph for LangGraph Studio Testing

This graph contains ONLY the architecture designer node, allowing isolated testing
of Phase 4 context-aware architecture design (US-CONTEXT-001) in LangGraph Studio.

Usage in Studio:
1. Select this graph from the dropdown
2. Provide initial state with project_context, detected context, and requirements
3. Execute and view the architecture design
4. Review and refine architecture via HITL checkpoint
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
# STATE - Simplified for Architecture Designer Only
# ============================================================================

class ArchitectureDesignerState(TypedDict, total=False):
    """State for isolated architecture designer testing."""
    # Input - Context from complexity_analyzer
    project_context: str
    project_complexity: str  # simple, medium, complex
    project_domain: str  # ai, web, api, data, mobile, library, utility, general
    project_intent: str  # new_feature, bug_fix, refactor, migration, enhancement, general
    detected_entities: List[str]  # Technology names, frameworks, services
    
    # Input - Requirements from requirements_analyst
    requirements_analysis: Dict[str, Any]  # Complete requirements analysis JSON
    functional_requirements: List[Dict[str, Any]]  # Functional requirements list
    non_functional_requirements: List[Dict[str, Any]]  # Non-functional requirements list
    technical_constraints: List[str]  # Technical constraints
    business_constraints: List[str]  # Business constraints
    assumptions: List[str]  # Assumptions
    risks: List[str]  # Risks
    
    # Output - Architecture Design
    architecture_design: Dict[str, Any]  # Complete architecture design JSON
    system_overview: str  # System overview description
    architecture_pattern: str  # Architecture pattern (Microservices, Monolithic, etc.)
    components: List[Dict[str, Any]]  # System components
    technology_stack: Dict[str, List[str]]  # Technology stack by layer
    data_flow: str  # Data flow description
    security_considerations: List[str]  # Security considerations
    scalability_considerations: List[str]  # Scalability considerations
    performance_considerations: List[str]  # Performance considerations
    deployment_strategy: str  # Deployment strategy
    design_confidence: float  # 0.0 to 1.0 - confidence in design quality
    needs_more_info: bool  # True if agent needs more information
    information_requests: List[str]  # Questions to ask user for clarification
    design_summary: str  # Human-readable summary of architecture design
    
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
# ARCHITECTURE DESIGNER NODE
# ============================================================================

def _create_llm():
    """Create LLM instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=0.0  # Deterministic for testing
    )


def design_architecture_node(state: ArchitectureDesignerState) -> Dict[str, Any]:
    """
    Design system architecture using LLM with context-aware and requirements-driven design.
    
    Phase 4 (US-CONTEXT-001): Enhanced architecture design that uses:
    - Detected context (domain, intent, complexity, entities)
    - Requirements analysis (functional, non-functional, constraints)
    - Better architecture design accuracy with context-aware and requirements-driven focus
    
    CRITICAL: Uses context to focus on domain-specific architecture patterns and requirements to ensure design completeness.
    """
    logger.info("🏗️ Designing architecture with context-aware and requirements-driven LLM...")
    
    llm = _create_llm()
    system_prompt = load_prompt_from_langsmith(
        "architecture_designer_v1",
        "You are an expert Architecture Designer. Design scalable, maintainable, production-grade systems."
    )
    
    # Format requirements for prompt
    requirements_summary = state.get('requirements_analysis', {}).get('summary', 'No requirements summary available')
    functional_reqs = state.get('functional_requirements', [])
    non_functional_reqs = state.get('non_functional_requirements', [])
    technical_constraints = state.get('technical_constraints', [])
    business_constraints = state.get('business_constraints', [])
    assumptions = state.get('assumptions', [])
    
    # Enhanced task prompt with context and requirements information
    task = f"""Design a complete, production-grade software architecture based on the project requirements and context.

PROJECT CONTEXT: {state.get('project_context', 'No project context provided')}

DETECTED CONTEXT:
- Domain: {state.get('project_domain', 'general')}
- Intent: {state.get('project_intent', 'new_feature')}
- Complexity: {state.get('project_complexity', 'medium')}
- Entities: {', '.join(state.get('detected_entities', [])[:10])}

REQUIREMENTS ANALYSIS:
{requirements_summary}

FUNCTIONAL REQUIREMENTS ({len(functional_reqs)}):
{_format_requirements_list(functional_reqs[:5])}

NON-FUNCTIONAL REQUIREMENTS ({len(non_functional_reqs)}):
{_format_requirements_list(non_functional_reqs[:5])}

CONSTRAINTS:
- Technical: {', '.join(technical_constraints[:5]) if technical_constraints else 'None specified'}
- Business: {', '.join(business_constraints[:5]) if business_constraints else 'None specified'}
- Assumptions: {', '.join(assumptions[:5]) if assumptions else 'None specified'}

CONTEXT-AWARE ARCHITECTURE GUIDANCE:
- Domain: {state.get('project_domain', 'general')} → Focus on domain-specific patterns
  * ai → AI/ML architecture (model serving, training pipelines, vector databases)
  * web → Web architecture (MVC, REST APIs, frontend/backend separation)
  * api → API-first architecture (microservices, API gateway, versioning)
  * data → Data architecture (ETL pipelines, data lakes, streaming)

- Intent: {state.get('project_intent', 'new_feature')} → Tailor architecture approach
  * new_feature → Comprehensive architecture (full system design)
  * bug_fix → Minimal architecture changes (focus on affected components)
  * refactor → Architecture improvement (focus on maintainability, scalability)

- Complexity: {state.get('project_complexity', 'medium')} → Adjust architecture depth
  * simple → Simple architecture (monolithic, minimal components)
  * medium → Standard architecture (modular layered, clear separation)
  * complex → Enterprise architecture (microservices, distributed, scalable)

- Entities: {', '.join(state.get('detected_entities', [])[:5])} → Consider technology-specific architecture
  * Use mentioned technologies in architecture design
  * Include architecture patterns appropriate for these technologies
  * Consider integration requirements for these technologies

Respond with ONLY valid JSON (no markdown, no extra text):
{{
    "system_overview": "Comprehensive description of the system architecture and design approach",
    "architecture_pattern": "Specific pattern (Microservices, Monolithic, Event-Driven, Serverless, Modular Layered)",
    "components": [
        {{
            "name": "Component Name",
            "description": "Detailed purpose and internal behavior",
            "responsibilities": ["Responsibility 1", "Responsibility 2"],
            "technology": "Concrete tech stack (e.g., 'Python 3.11 + FastAPI', 'PostgreSQL 15')",
            "interfaces": ["Interface A", "Interface B"],
            "dependencies": ["Dependency A", "Dependency B"],
            "scalability_approach": "How this component scales horizontally/vertically"
        }}
    ],
    "data_flow": "End-to-end description of how data moves through the system (under 2000 characters)",
    "technology_stack": {{
        "frontend": ["React 18", "Next.js 14"],
        "backend": ["Python 3.11", "FastAPI 0.115"],
        "database": ["PostgreSQL 15"],
        "infrastructure": ["Docker 26.0", "Kubernetes 1.30", "AWS EKS", "Terraform 1.8"]
    }},
    "security_considerations": [
        "JWT-based authentication with role-based access control",
        "TLS 1.3 enforced for all external connections",
        "Input validation and output sanitization at API layer"
    ],
    "scalability_considerations": [
        "Horizontal pod autoscaling based on CPU/memory",
        "Database read replicas for query distribution"
    ],
    "performance_considerations": [
        "Use Redis caching for frequently accessed data",
        "Asynchronous I/O for high concurrency APIs"
    ],
    "deployment_strategy": "Describe deployment pipeline and environment setup",
    "quality_assessment": {{
        "completeness": "Pass/Fail + brief justification",
        "scalability": "Pass/Fail + brief justification",
        "security": "Pass/Fail + brief justification",
        "maintainability": "Pass/Fail + brief justification",
        "traceability": "Pass/Fail + brief justification"
    }},
    "improvement_recommendations": [
        "Specific improvements or refinements"
    ]
}}

CRITICAL: Use the detected context and requirements to design an appropriate architecture:
- Domain ({state.get('project_domain', 'general')}) → Domain-specific architecture patterns
- Intent ({state.get('project_intent', 'new_feature')}) → Appropriate architecture depth
- Complexity ({state.get('project_complexity', 'medium')}) → Appropriate architecture complexity
- Entities ({', '.join(state.get('detected_entities', [])[:5])}) → Technology-specific architecture
- Requirements → Ensure all functional and non-functional requirements are addressed"""
    
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
        
        # Extract architecture components
        components = parsed.get("components", [])
        technology_stack = parsed.get("technology_stack", {})
        security_considerations = parsed.get("security_considerations", [])
        scalability_considerations = parsed.get("scalability_considerations", [])
        performance_considerations = parsed.get("performance_considerations", [])
        
        # Calculate confidence based on design quality
        confidence = _calculate_design_confidence(
            parsed,
            state.get('project_complexity', 'medium'),
            state.get('project_domain', 'general'),
            len(functional_reqs),
            len(non_functional_reqs)
        )
        
        # Determine if more information is needed
        needs_more_info = confidence < 0.7 or len(components) < 2
        
        # Generate information requests if needed
        information_requests = []
        if needs_more_info:
            information_requests = _generate_architecture_questions(
                state.get('project_context', ''),
                parsed,
                state.get('project_complexity', 'medium'),
                state.get('project_domain', 'general'),
                len(functional_reqs),
                len(non_functional_reqs)
            )
        
        # Create human-readable summary
        design_summary = _format_architecture_summary(parsed, confidence)
        
        logger.info(
            f"🏗️ Architecture design completed: {len(components)} components, "
            f"{len(technology_stack)} technology layers (confidence: {confidence:.2f})"
        )
        
        return {
            "architecture_design": parsed,
            "system_overview": parsed.get("system_overview", ""),
            "architecture_pattern": parsed.get("architecture_pattern", ""),
            "components": components,
            "technology_stack": technology_stack,
            "data_flow": parsed.get("data_flow", ""),
            "security_considerations": security_considerations,
            "scalability_considerations": scalability_considerations,
            "performance_considerations": performance_considerations,
            "deployment_strategy": parsed.get("deployment_strategy", ""),
            "design_confidence": confidence,
            "needs_more_info": needs_more_info,
            "information_requests": information_requests,
            "design_summary": design_summary,
            "current_step": "architecture_designed"
        }
        
    except Exception as e:
        logger.warning(f"Failed to parse architecture design JSON: {e}. Using defaults.")
        # Fallback to default design
        return {
            "architecture_design": {"system_overview": f"Design failed: {str(e)}"},
            "system_overview": f"Architecture design failed. Error: {str(e)}",
            "architecture_pattern": "",
            "components": [],
            "technology_stack": {},
            "data_flow": "",
            "security_considerations": [],
            "scalability_considerations": [],
            "performance_considerations": [],
            "deployment_strategy": "",
            "design_confidence": 0.3,
            "needs_more_info": True,
            "information_requests": [
                "Could you provide more details about the project requirements?",
                "What are the main system components needed?",
                "What are the key constraints or limitations?"
            ],
            "design_summary": f"⚠️ Architecture design failed. Error: {str(e)}. Please provide more information.",
            "current_step": "architecture_designed",
            "errors": [f"Architecture design error: {str(e)}"]
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _format_requirements_list(requirements: List[Dict[str, Any]]) -> str:
    """Format requirements list for prompt."""
    if not requirements:
        return "None specified"
    
    formatted = []
    for req in requirements[:5]:  # Limit to first 5
        req_id = req.get('id', 'N/A')
        title = req.get('title', req.get('description', '')[:50])
        formatted.append(f"- {req_id}: {title}")
    
    return "\n".join(formatted)


def _calculate_design_confidence(
    design: Dict[str, Any],
    complexity: str,
    domain: str,
    functional_req_count: int,
    non_functional_req_count: int
) -> float:
    """Calculate confidence score for architecture design."""
    confidence = 0.5  # Base confidence
    
    # Check if design has required components
    components = design.get("components", [])
    
    # Minimum components present
    if len(components) >= 2:
        confidence += 0.15
    if len(components) >= 4:
        confidence += 0.1
    
    # Technology stack present
    tech_stack = design.get("technology_stack", {})
    if tech_stack:
        tech_layers = sum(1 for layer in tech_stack.values() if layer)
        if tech_layers >= 2:
            confidence += 0.1
    
    # Security considerations present
    security = design.get("security_considerations", [])
    if len(security) >= 2:
        confidence += 0.1
    
    # Scalability considerations present
    scalability = design.get("scalability_considerations", [])
    if len(scalability) >= 1:
        confidence += 0.05
    
    # Quality assessment present
    quality_assessment = design.get("quality_assessment", {})
    if quality_assessment:
        # Check if quality gates passed
        passed_count = sum(1 for v in quality_assessment.values() if "Pass" in str(v))
        if passed_count >= 4:
            confidence += 0.05
    
    # Complexity-based validation
    if complexity == "complex":
        if len(components) >= 5 and len(security) >= 3:
            confidence += 0.05
    elif complexity == "medium":
        if len(components) >= 3 and len(security) >= 2:
            confidence += 0.05
    elif complexity == "simple":
        if len(components) >= 2:
            confidence += 0.05
    
    # Domain-specific validation (check if domain mentioned in components)
    system_overview = design.get("system_overview", "").lower()
    domain_keywords = {
        "ai": ["ai", "ml", "machine learning", "model", "training", "inference"],
        "web": ["web", "api", "http", "frontend", "backend", "rest"],
        "api": ["api", "endpoint", "rest", "graphql", "microservice"],
        "data": ["data", "database", "etl", "analytics", "pipeline"]
    }
    
    if domain in domain_keywords:
        keywords = domain_keywords[domain]
        if any(keyword in system_overview for keyword in keywords):
            confidence += 0.05
    
    return min(confidence, 1.0)  # Cap at 1.0


def _generate_architecture_questions(
    context: str,
    design: Dict[str, Any],
    complexity: str,
    domain: str,
    functional_req_count: int,
    non_functional_req_count: int
) -> List[str]:
    """Generate questions to ask user for more information about architecture."""
    requests = []
    
    # Check if design seems incomplete
    components = design.get("components", [])
    
    if len(components) < 2:
        requests.append("What are the main system components or modules needed?")
    
    # Technology stack questions
    tech_stack = design.get("technology_stack", {})
    if not tech_stack or not any(tech_stack.values()):
        requests.append("What technology stack should be used? (e.g., programming languages, frameworks, databases)")
    
    # Domain-specific questions
    if domain == "general" and len(components) < 3:
        requests.append("What domain does this project belong to? (e.g., AI, web, API, data processing)")
    
    # Complexity questions
    if complexity == "complex" and len(components) < 5:
        requests.append("Are there additional components or services that should be included in the architecture?")
    
    # Security questions
    security = design.get("security_considerations", [])
    if len(security) < 2:
        requests.append("What are the security requirements? (e.g., authentication, authorization, encryption)")
    
    # If no specific requests, add generic ones
    if not requests:
        requests.append("Are there any specific architectural constraints or preferences that should be considered?")
    
    return requests


def _format_architecture_summary(
    design: Dict[str, Any],
    confidence: float
) -> str:
    """Create human-readable summary of architecture design."""
    summary_parts = [
        f"**Architecture Design Summary**",
        f"",
        f"**Overall Confidence**: {confidence:.0%}",
        f"",
        f"**Architecture Pattern**: {design.get('architecture_pattern', 'Not specified')}",
        f"**Components**: {len(design.get('components', []))}",
        f"",
        f"**System Overview**:",
        f"{design.get('system_overview', 'No overview provided')[:500]}",
        f""
    ]
    
    # Add technology stack
    tech_stack = design.get("technology_stack", {})
    if tech_stack:
        summary_parts.append("**Technology Stack**:")
        for layer, techs in tech_stack.items():
            if techs:
                summary_parts.append(f"- {layer.capitalize()}: {', '.join(techs[:3])}")
        summary_parts.append("")
    
    # Add quality assessment
    quality_assessment = design.get("quality_assessment", {})
    if quality_assessment:
        summary_parts.append("**Quality Assessment**:")
        for criterion, result in quality_assessment.items():
            summary_parts.append(f"- {criterion.capitalize()}: {result}")
        summary_parts.append("")
    
    # Add recommendations if any
    recommendations = design.get("improvement_recommendations", [])
    if recommendations:
        summary_parts.append(f"**Improvement Recommendations**: {len(recommendations)}")
        for rec in recommendations[:3]:  # Show top 3
            summary_parts.append(f"- {rec[:150]}")
    
    return "\n".join(summary_parts)


# ============================================================================
# HITL REVIEW NODE
# ============================================================================

def review_architecture_node(state: ArchitectureDesignerState) -> Dict[str, Any]:
    """
    HITL checkpoint: Review architecture design, answer questions, and process human feedback.
    
    This node:
    1. Displays architecture design in a readable format
    2. Answers human questions if provided (Q&A capability)
    3. Processes human feedback if provided
    4. Updates architecture if human provides corrections
    5. Sets routing decision for loop or END
    """
    logger.info("👤 HITL Checkpoint: Reviewing architecture design...")
    
    # Get iteration count (safety limit)
    iteration_count = state.get('iteration_count', 0)
    max_iterations = 3  # Safety limit to prevent infinite loops
    
    # Get human feedback and questions if provided
    human_feedback = state.get('human_feedback', '')
    human_approval = state.get('human_approval', '')
    human_question = state.get('human_question', '')
    
    # Start with current state values
    updated_state = {
        "current_step": "architecture_review",
        "design_summary": state.get('design_summary', '')
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
                # Extract additional architecture info from feedback
                feedback_info = _extract_architecture_from_feedback(human_feedback)
                
                # Merge with existing design
                existing_design = state.get('architecture_design', {})
                if feedback_info:
                    # Enrich design with feedback
                    enriched_design = _enrich_design_with_feedback(existing_design, feedback_info)
                    updated_state.update({
                        "architecture_design": enriched_design,
                        "design_confidence": min(state.get('design_confidence', 0.0) + 0.1, 1.0),
                        "iteration_count": iteration_count + 1
                    })
                else:
                    # Keep existing but boost confidence
                    updated_state.update({
                        "design_confidence": min(state.get('design_confidence', 0.0) + 0.1, 1.0),
                        "iteration_count": iteration_count + 1
                    })
                
                logger.info(f"✅ Architecture refined: Updated design")
                logger.info(f"🔄 Iteration {updated_state['iteration_count']}/{max_iterations}")
            
        elif human_approval.lower() == 'rejected':
            logger.warning("❌ Architecture design rejected by human - ending workflow")
            
        elif human_approval.lower() == 'approved':
            logger.info("✅ Architecture design approved by human - ending workflow")
    
    # Format review message
    design = state.get('architecture_design', {})
    component_count = len(state.get('components', []))
    
    review_message = f"""
# Architecture Design Review

## Design Summary

{state.get('design_summary', 'No design available')}

## Architecture Details

- **Architecture Pattern**: {state.get('architecture_pattern', 'Not specified')}
- **Components**: {component_count}
- **Technology Stack Layers**: {len(state.get('technology_stack', {}))}
- **Security Considerations**: {len(state.get('security_considerations', []))}
- **Scalability Considerations**: {len(state.get('scalability_considerations', []))}

## Status

- **Confidence**: {updated_state.get('design_confidence', state.get('design_confidence', 0.0)):.0%}
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
                review_message += f"- **Confidence Updated**: {updated_state.get('design_confidence', 0.0):.0%}\n"
                review_message += f"- **Next**: Will re-design architecture with refined information\n"
    
    if human_approval:
        review_message += f"\n## Approval Status: {human_approval}\n"
    
    # Signal workflow status based on routing decision
    if human_approval.lower() == 'needs_refinement' and iteration_count < max_iterations:
        review_message += "\n## Workflow Status\n\n🔄 **Refinement requested - will re-design architecture**\n"
    elif human_approval.lower() == 'approved':
        review_message += "\n## Workflow Status\n\n✅ **Architecture approved - workflow will complete**\n"
    elif human_approval.lower() == 'rejected':
        review_message += "\n## Workflow Status\n\n❌ **Architecture rejected - workflow ending**\n"
    else:
        review_message += "\n## Workflow Status\n\n✅ **Architecture design complete - workflow finished**\n"
    
    # Update design summary with the review message
    updated_state['design_summary'] = review_message
    
    logger.info("🏗️ Review message prepared")
    
    return updated_state


def _extract_architecture_from_feedback(feedback: str) -> Dict[str, Any]:
    """
    Extract architecture information from human feedback.
    
    Examples:
    - "Add component for authentication" → {"components": ["authentication"]}
    - "Use microservices pattern" → {"architecture_pattern": "microservices"}
    """
    feedback_lower = feedback.lower()
    extracted = {
        "components": [],
        "architecture_pattern": None,
        "technology_stack": {}
    }
    
    # Look for component keywords
    component_keywords = ["component", "module", "service", "layer"]
    if any(keyword in feedback_lower for keyword in component_keywords):
        extracted["components"].append(feedback)
    
    # Look for architecture pattern keywords
    pattern_keywords = ["microservices", "monolithic", "serverless", "event-driven", "layered"]
    for pattern in pattern_keywords:
        if pattern in feedback_lower:
            extracted["architecture_pattern"] = pattern
            break
    
    # Look for technology keywords
    tech_keywords = ["python", "javascript", "react", "fastapi", "postgresql", "docker", "kubernetes"]
    for tech in tech_keywords:
        if tech in feedback_lower:
            if "frontend" in feedback_lower or "ui" in feedback_lower:
                extracted["technology_stack"]["frontend"] = [tech]
            elif "backend" in feedback_lower or "api" in feedback_lower:
                extracted["technology_stack"]["backend"] = [tech]
            elif "database" in feedback_lower or "db" in feedback_lower:
                extracted["technology_stack"]["database"] = [tech]
    
    return extracted


def _enrich_design_with_feedback(
    existing_design: Dict[str, Any],
    feedback_info: Dict[str, Any]
) -> Dict[str, Any]:
    """Enrich existing design with feedback information."""
    enriched = existing_design.copy()
    
    # Add components from feedback
    if feedback_info.get("components"):
        components = enriched.get("components", [])
        for feedback_component in feedback_info["components"]:
            components.append({
                "name": "Additional Component",
                "description": feedback_component,
                "responsibilities": [],
                "technology": "To be specified",
                "interfaces": [],
                "dependencies": [],
                "scalability_approach": "To be specified"
            })
        enriched["components"] = components
    
    # Update architecture pattern if specified
    if feedback_info.get("architecture_pattern"):
        enriched["architecture_pattern"] = feedback_info["architecture_pattern"]
    
    # Update technology stack if specified
    if feedback_info.get("technology_stack"):
        tech_stack = enriched.get("technology_stack", {})
        tech_stack.update(feedback_info["technology_stack"])
        enriched["technology_stack"] = tech_stack
    
    return enriched


# ============================================================================
# FINALIZE NODE
# ============================================================================

def finalize_architecture_node(state: ArchitectureDesignerState) -> Dict[str, Any]:
    """
    Final completion node: Generate final summary message before workflow ends.
    
    This node runs when workflow is ending (approved/rejected/max_iterations)
    to provide a clear final message to the user.
    """
    logger.info("🏁 Finalizing architecture design workflow...")
    
    human_approval = state.get('human_approval', '').lower()
    iteration_count = state.get('iteration_count', 0)
    design = state.get('architecture_design', {})
    component_count = len(state.get('components', []))
    
    # Determine completion status
    if human_approval == 'approved':
        status_emoji = "✅"
        status_text = "Approved"
        completion_message = "Architecture design approved and workflow completed successfully."
    elif human_approval == 'rejected':
        status_emoji = "❌"
        status_text = "Rejected"
        completion_message = "Architecture design rejected. Workflow ending."
    elif iteration_count >= 3:
        status_emoji = "⚠️"
        status_text = "Max Iterations Reached"
        completion_message = "Maximum refinement iterations reached. Workflow ending."
    else:
        status_emoji = "✅"
        status_text = "Complete"
        completion_message = "Architecture design workflow completed."
    
    # Build final summary
    design_summary = state.get('design_summary', '')
    if not design_summary or "Architecture Design Review" in design_summary:
        design_summary = _format_architecture_summary(
            design,
            state.get('design_confidence', 0.0)
        )
    
    # Create final completion message
    final_message = f"""
# {status_emoji} Architecture Design Complete

## Final Summary

{completion_message}

## Architecture Design Results

{design_summary}

## Final Design

- **Architecture Pattern**: {state.get('architecture_pattern', 'Not specified')}
- **Components**: {component_count}
- **Technology Stack Layers**: {len(state.get('technology_stack', {}))}
- **Security Considerations**: {len(state.get('security_considerations', []))}
- **Scalability Considerations**: {len(state.get('scalability_considerations', []))}
- **Confidence**: {state.get('design_confidence', 0.0):.0%}
- **Iterations**: {iteration_count}
- **Status**: {status_emoji} {status_text}

## System Overview

{state.get('system_overview', 'No overview available')}

---

## Workflow Complete

✅ **The architecture design workflow has finished.**

The architecture design is now ready for:
- Code generation phase
- Infrastructure setup
- Component implementation
- Testing planning

**Current Step**: completed
"""
    
    logger.info(f"✅ Final message prepared - workflow complete (status: {status_text})")
    
    return {
        "current_step": "completed",
        "design_summary": final_message
    }


# ============================================================================
# ROUTING FUNCTION
# ============================================================================

def _route_after_review(state: ArchitectureDesignerState) -> str:
    """
    Routing function: Decide whether to loop back for refinement or end workflow.
    
    Returns:
        "design_architecture" if refinement needed and within iteration limit
        "finalize_architecture" if approved, rejected, or max iterations reached
    """
    human_approval = state.get('human_approval', '').lower()
    iteration_count = state.get('iteration_count', 0)
    max_iterations = 3
    
    # End conditions - route to finalize_architecture first
    if human_approval == 'approved':
        logger.info("✅ Approved - routing to finalize_architecture")
        return "finalize_architecture"
    
    if human_approval == 'rejected':
        logger.info("❌ Rejected - routing to finalize_architecture")
        return "finalize_architecture"
    
    if iteration_count >= max_iterations:
        logger.info(f"⚠️ Max iterations ({max_iterations}) reached - routing to finalize_architecture")
        return "finalize_architecture"
    
    # Confidence-based auto-approval (if no human feedback and high confidence)
    if not human_approval and state.get('design_confidence', 0.0) >= 0.9:
        logger.info("✅ High confidence, no feedback - routing to finalize_architecture")
        return "finalize_architecture"
    
    # Loop back for refinement
    if human_approval == 'needs_refinement':
        logger.info(f"🔄 Refinement requested - looping back to design_architecture (iteration {iteration_count + 1}/{max_iterations})")
        return "design_architecture"
    
    # Default: route to finalize
    logger.info("🏁 No refinement requested - routing to finalize_architecture")
    return "finalize_architecture"


# ============================================================================
# GRAPH BUILDING
# ============================================================================

def build_graph():
    """
    Build isolated architecture designer graph with HITL checkpoint and iterative refinement loop.
    
    Graph flow:
    START → design_architecture → [interrupt_after] → review_architecture → [conditional]
                                                                          ├→ design_architecture (if needs_refinement)
                                                                          └→ finalize_architecture → END (if approved/rejected/max_iterations)
    
    NOTE: For LangGraph Studio, we use interrupt_after on design_architecture
    instead of interrupt_before on review_architecture to ensure proper END edge handling.
    """
    workflow = StateGraph(ArchitectureDesignerState)
    
    # Add nodes
    workflow.add_node("design_architecture", design_architecture_node)
    workflow.add_node("review_architecture", review_architecture_node)
    workflow.add_node("finalize_architecture", finalize_architecture_node)  # Final completion node
    
    # Flow: START → design_architecture → review_architecture → [conditional] → design_architecture OR finalize_architecture → END
    workflow.set_entry_point("design_architecture")
    workflow.add_edge("design_architecture", "review_architecture")
    
    # Conditional edge: review_architecture → design_architecture (loop) OR finalize_architecture
    workflow.add_conditional_edges(
        "review_architecture",
        _route_after_review,  # Routing function decides next step
        {
            "design_architecture": "design_architecture",  # Loop back for refinement
            "finalize_architecture": "finalize_architecture"  # Finalize and end
        }
    )
    
    # Finalize architecture → END (always ends workflow)
    workflow.add_edge("finalize_architecture", END)
    
    # Use interrupt_after instead of interrupt_before for better END handling
    # This pauses AFTER design_architecture, allowing review_architecture to complete normally
    compiled = workflow.compile(
        interrupt_after=["design_architecture"]  # HITL: pause after design, before review
    )
    
    logger.info("✅ Architecture designer graph compiled with iterative refinement loop")
    logger.info("🔄 Loop: design_architecture → review_architecture → [needs_refinement?] → design_architecture")
    logger.info("🏁 End flow: review_architecture → finalize_architecture → END")
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
        logger.error(f"Failed to build architecture designer graph: {e}")
        logger.exception("Full traceback:")
        # Return None to allow Studio to start even if this graph fails
        return None


# Export for Studio
try:
    graph = get_graph()
except Exception as e:
    logger.error(f"Failed to export architecture designer graph: {e}")
    logger.exception("Full traceback:")
    graph = None  # Allow Studio to start even if this graph fails

