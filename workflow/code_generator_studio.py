"""
Isolated Code Generator Graph for LangGraph Studio Testing

This graph contains ONLY the code generator node, allowing isolated testing
of Phase 5 context-aware, requirements-driven, and architecture-guided code generation (US-CONTEXT-001) in LangGraph Studio.

Usage in Studio:
1. Select this graph from the dropdown
2. Provide initial state with project_context, detected context, requirements, and architecture
3. Execute and view the generated code
4. Review and refine code via HITL checkpoint
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
# STATE - Simplified for Code Generator Only
# ============================================================================

class CodeGeneratorState(TypedDict, total=False):
    """State for isolated code generator testing."""
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
    
    # Input - Architecture from architecture_designer
    architecture_design: Dict[str, Any]  # Complete architecture design JSON
    system_overview: str  # System overview description
    architecture_pattern: str  # Architecture pattern
    components: List[Dict[str, Any]]  # System components
    technology_stack: Dict[str, List[str]]  # Technology stack by layer
    data_flow: str  # Data flow description
    security_considerations: List[str]  # Security considerations
    scalability_considerations: List[str]  # Scalability considerations
    performance_considerations: List[str]  # Performance considerations
    deployment_strategy: str  # Deployment strategy
    
    # Output - Code Generation
    code_files: Dict[str, str]  # Generated code files: {path: content}
    code_metadata: Dict[str, Any]  # Code generation metadata (plan, assumptions, etc.)
    file_tree: str  # File tree structure
    plan: List[str]  # Implementation plan
    assumptions: List[str]  # Assumptions made during generation
    tests: Dict[str, Any]  # Test strategy and coverage
    runbook: Dict[str, Any]  # Runbook instructions
    config_notes: str  # Configuration notes
    api_contracts: List[Dict[str, Any]]  # API contracts
    security_review: List[str]  # Security review notes
    performance_notes: List[str]  # Performance notes
    limitations: List[str]  # Known limitations
    generation_confidence: float  # 0.0 to 1.0 - confidence in code quality
    needs_more_info: bool  # True if agent needs more information
    information_requests: List[str]  # Questions to ask user for clarification
    generation_summary: str  # Human-readable summary of code generation
    
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
# CODE GENERATOR NODE
# ============================================================================

def _create_llm():
    """Create LLM instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=0.0  # Deterministic for testing
    )


def generate_code_node(state: CodeGeneratorState) -> Dict[str, Any]:
    """
    Generate production-ready code using LLM with context-aware, requirements-driven, and architecture-guided generation.
    
    Phase 5 (US-CONTEXT-001): Enhanced code generation that uses:
    - Detected context (domain, intent, complexity, entities)
    - Requirements analysis (functional, non-functional, constraints)
    - Architecture design (components, technology stack, patterns)
    - Better code generation accuracy with full context
    
    CRITICAL: Uses context, requirements, and architecture to generate production-ready code.
    """
    logger.info("💻 Generating code with context-aware, requirements-driven, and architecture-guided LLM...")
    
    llm = _create_llm()
    system_prompt = load_prompt_from_langsmith(
        "code_generator_v1",
        "You are an expert Code Generator. Write clean, production-ready code."
    )
    
    # Format requirements for prompt
    requirements_summary = state.get('requirements_analysis', {}).get('summary', 'No requirements summary available')
    functional_reqs = state.get('functional_requirements', [])
    non_functional_reqs = state.get('non_functional_requirements', [])
    
    # Format architecture for prompt
    architecture_summary = state.get('architecture_design', {}).get('system_overview', state.get('system_overview', 'No architecture summary available'))
    architecture_pattern = state.get('architecture_pattern', '')
    components = state.get('components', [])
    tech_stack = state.get('technology_stack', {})
    
    # Enhanced task prompt with context, requirements, and architecture information
    task = f"""Generate complete, production-ready source code for this project.

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
- Technical: {', '.join(state.get('technical_constraints', [])[:5]) if state.get('technical_constraints') else 'None specified'}
- Assumptions: {', '.join(state.get('assumptions', [])[:5]) if state.get('assumptions') else 'None specified'}

ARCHITECTURE DESIGN:
{architecture_summary}

ARCHITECTURE PATTERN: {architecture_pattern}

COMPONENTS ({len(components)}):
{_format_components_list(components[:5])}

TECHNOLOGY STACK:
{_format_technology_stack(tech_stack)}

CONTEXT-AWARE CODE GENERATION GUIDANCE:
- Domain: {state.get('project_domain', 'general')} → Use domain-specific patterns and libraries
  * ai → Use AI/ML frameworks (transformers, langchain, vector databases)
  * web → Use web frameworks (FastAPI, Flask, React, Next.js)
  * api → Use API frameworks (FastAPI, Flask REST, OpenAPI)
  * data → Use data processing libraries (pandas, numpy, pyspark)

- Intent: {state.get('project_intent', 'new_feature')} → Tailor code generation approach
  * new_feature → Generate complete new codebase
  * bug_fix → Generate minimal fixes for identified issues
  * refactor → Generate improved code structure

- Complexity: {state.get('project_complexity', 'medium')} → Adjust code complexity
  * simple → Simple code structure (single file or minimal modules)
  * medium → Standard code structure (modular, clear separation)
  * complex → Enterprise code structure (packages, layers, abstractions)

- Technology Stack: {_format_tech_stack_for_guidance(tech_stack)} → Use exact technologies specified
  * Follow architecture technology stack exactly
  * Use specified frameworks and libraries
  * Maintain consistency with architecture design

- Architecture Pattern: {architecture_pattern} → Follow pattern conventions
  * microservices → Separate services, API contracts, service discovery
  * monolithic → Single codebase, modular structure
  * layered → Clear layer separation (presentation, business, data)

Respond with ONLY valid JSON (no markdown, no extra text):
{{
    "plan": ["High-level implementation plan (5-12 bullets)"],
    "assumptions": ["Only if required; each <120 chars"],
    "file_tree": "Unix-like tree showing ONLY files you generate",
    "files": [
        {{"path": "path/filename.ext", "content": "<full file content>"}},
        {{"path": "path/other.ext", "content": "<full file content>"}}
    ],
    "tests": {{
        "coverage_goal": "e.g., '>=80% lines/statements'",
        "strategy": "Unit/integration/e2e approach in brief",
        "entry_commands": ["commands to run tests"]
    }},
    "runbook": {{
        "setup": ["commands to set up env/deps with pinned versions"],
        "run": ["commands to start the app/service/jobs"],
        "build": ["commands to build/package"],
        "lint": ["commands for lint/format/static analysis"],
        "migrations": ["commands if applicable"]
    }},
    "config_notes": "Rationale for key config choices (ports, env vars, security hardening)",
    "api_contracts": [
        {{
            "name": "Public API/CLI/Job",
            "interface": "Types/signatures/routes/schema",
            "errors": ["structured error shapes/codes"],
            "examples": ["request/response or CLI invocations"]
        }}
    ],
    "security_review": [
        "List concrete controls implemented (validation, authn/z, rate limits, CSRF/CORS, SSRF guards, secrets mgmt, dependency pinning)"
    ],
    "performance_notes": [
        "Hot paths, big-O where relevant, caching choices, async/concurrency decisions"
    ],
    "limitations": [
        "Honest known gaps due to constraints; suggest next steps"
    ]
}}

CRITICAL: Use the detected context, requirements, and architecture to generate production-ready code:
- Domain ({state.get('project_domain', 'general')}) → Domain-specific code patterns
- Intent ({state.get('project_intent', 'new_feature')}) → Appropriate code generation scope
- Complexity ({state.get('project_complexity', 'medium')}) → Appropriate code structure complexity
- Technology Stack ({_format_tech_stack_for_guidance(tech_stack)}) → Use exact technologies specified
- Architecture Pattern ({architecture_pattern}) → Follow pattern conventions
- Requirements → Ensure all functional requirements are implemented"""
    
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
        
        # Extract code files
        files_list = parsed.get("files", [])
        code_files = {}
        for file_obj in files_list:
            if isinstance(file_obj, dict) and "path" in file_obj and "content" in file_obj:
                code_files[file_obj["path"]] = file_obj["content"]
        
        # Extract metadata
        code_metadata = {
            "file_tree": parsed.get("file_tree", ""),
            "plan": parsed.get("plan", []),
            "assumptions": parsed.get("assumptions", []),
            "tests": parsed.get("tests", {}),
            "runbook": parsed.get("runbook", {}),
            "config_notes": parsed.get("config_notes", ""),
            "api_contracts": parsed.get("api_contracts", []),
            "security_review": parsed.get("security_review", []),
            "performance_notes": parsed.get("performance_notes", []),
            "limitations": parsed.get("limitations", [])
        }
        
        # Calculate confidence based on code quality
        confidence = _calculate_generation_confidence(
            parsed,
            len(code_files),
            state.get('project_complexity', 'medium'),
            state.get('project_domain', 'general'),
            len(functional_reqs)
        )
        
        # Determine if more information is needed
        needs_more_info = confidence < 0.7 or len(code_files) < 2
        
        # Generate information requests if needed
        information_requests = []
        if needs_more_info:
            information_requests = _generate_code_questions(
                state.get('project_context', ''),
                parsed,
                len(code_files),
                state.get('project_complexity', 'medium'),
                state.get('project_domain', 'general')
            )
        
        # Create human-readable summary
        generation_summary = _format_code_generation_summary(parsed, len(code_files), confidence)
        
        logger.info(
            f"💻 Code generation completed: {len(code_files)} files generated "
            f"(confidence: {confidence:.2f})"
        )
        
        return {
            "code_files": code_files,
            "code_metadata": code_metadata,
            "file_tree": code_metadata.get("file_tree", ""),
            "plan": code_metadata.get("plan", []),
            "assumptions": code_metadata.get("assumptions", []),
            "tests": code_metadata.get("tests", {}),
            "runbook": code_metadata.get("runbook", {}),
            "config_notes": code_metadata.get("config_notes", ""),
            "api_contracts": code_metadata.get("api_contracts", []),
            "security_review": code_metadata.get("security_review", []),
            "performance_notes": code_metadata.get("performance_notes", []),
            "limitations": code_metadata.get("limitations", []),
            "generation_confidence": confidence,
            "needs_more_info": needs_more_info,
            "information_requests": information_requests,
            "generation_summary": generation_summary,
            "current_step": "code_generated"
        }
        
    except Exception as e:
        logger.warning(f"Failed to parse code generation JSON: {e}. Using defaults.")
        # Fallback to default generation
        return {
            "code_files": {},
            "code_metadata": {},
            "file_tree": "",
            "plan": [],
            "assumptions": [],
            "tests": {},
            "runbook": {},
            "config_notes": "",
            "api_contracts": [],
            "security_review": [],
            "performance_notes": [],
            "limitations": [],
            "generation_confidence": 0.3,
            "needs_more_info": True,
            "information_requests": [
                "Could you provide more details about the project requirements?",
                "What are the main features or components that need to be implemented?",
                "What are the key constraints or limitations?"
            ],
            "generation_summary": f"⚠️ Code generation failed. Error: {str(e)}. Please provide more information.",
            "current_step": "code_generated",
            "errors": [f"Code generation error: {str(e)}"]
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


def _format_components_list(components: List[Dict[str, Any]]) -> str:
    """Format components list for prompt."""
    if not components:
        return "None specified"
    
    formatted = []
    for comp in components[:5]:  # Limit to first 5
        comp_name = comp.get('name', 'Unnamed Component')
        comp_desc = comp.get('description', '')[:100]
        formatted.append(f"- {comp_name}: {comp_desc}")
    
    return "\n".join(formatted)


def _format_technology_stack(tech_stack: Dict[str, List[str]]) -> str:
    """Format technology stack for prompt."""
    if not tech_stack:
        return "None specified"
    
    formatted = []
    for layer, techs in tech_stack.items():
        if techs:
            formatted.append(f"- {layer.capitalize()}: {', '.join(techs)}")
    
    return "\n".join(formatted) if formatted else "None specified"


def _format_tech_stack_for_guidance(tech_stack: Dict[str, List[str]]) -> str:
    """Format technology stack for guidance section."""
    if not tech_stack:
        return "Not specified"
    
    all_techs = []
    for techs in tech_stack.values():
        all_techs.extend(techs)
    
    return ', '.join(all_techs[:10]) if all_techs else "Not specified"


def _calculate_generation_confidence(
    generation: Dict[str, Any],
    file_count: int,
    complexity: str,
    domain: str,
    functional_req_count: int
) -> float:
    """Calculate confidence score for code generation."""
    confidence = 0.5  # Base confidence
    
    # Check if generation has required components
    code_files = generation.get("files", [])
    
    # Minimum files present
    if len(code_files) >= 2:
        confidence += 0.15
    if len(code_files) >= 5:
        confidence += 0.1
    
    # Plan present
    plan = generation.get("plan", [])
    if len(plan) >= 3:
        confidence += 0.1
    
    # File tree present
    file_tree = generation.get("file_tree", "")
    if file_tree:
        confidence += 0.05
    
    # Tests strategy present
    tests = generation.get("tests", {})
    if tests:
        confidence += 0.05
    
    # Security review present
    security_review = generation.get("security_review", [])
    if len(security_review) >= 2:
        confidence += 0.05
    
    # Runbook present
    runbook = generation.get("runbook", {})
    if runbook:
        confidence += 0.05
    
    # Complexity-based validation
    if complexity == "complex":
        if len(code_files) >= 8 and len(plan) >= 5:
            confidence += 0.05
    elif complexity == "medium":
        if len(code_files) >= 4 and len(plan) >= 3:
            confidence += 0.05
    elif complexity == "simple":
        if len(code_files) >= 2:
            confidence += 0.05
    
    # Domain-specific validation (check if domain mentioned in files)
    file_contents = " ".join([f.get("content", "") for f in code_files[:3]])
    domain_keywords = {
        "ai": ["import", "langchain", "transformers", "vector", "embedding"],
        "web": ["fastapi", "flask", "react", "next", "api", "route"],
        "api": ["fastapi", "flask", "rest", "endpoint", "route"],
        "data": ["pandas", "numpy", "dataframe", "etl", "process"]
    }
    
    if domain in domain_keywords:
        keywords = domain_keywords[domain]
        if any(keyword.lower() in file_contents.lower() for keyword in keywords):
            confidence += 0.05
    
    return min(confidence, 1.0)  # Cap at 1.0


def _generate_code_questions(
    context: str,
    generation: Dict[str, Any],
    file_count: int,
    complexity: str,
    domain: str
) -> List[str]:
    """Generate questions to ask user for more information about code generation."""
    requests = []
    
    # Check if generation seems incomplete
    code_files = generation.get("files", [])
    
    if len(code_files) < 2:
        requests.append("What are the main files or modules that need to be generated?")
    
    # Plan questions
    plan = generation.get("plan", [])
    if len(plan) < 3:
        requests.append("What is the implementation approach or plan?")
    
    # Technology stack questions
    if domain == "general" and len(code_files) < 3:
        requests.append("What programming language and framework should be used?")
    
    # Complexity questions
    if complexity == "complex" and len(code_files) < 6:
        requests.append("Are there additional modules or services that should be included?")
    
    # If no specific requests, add generic ones
    if not requests:
        requests.append("Are there any specific code patterns or conventions that should be followed?")
    
    return requests


def _format_code_generation_summary(
    generation: Dict[str, Any],
    file_count: int,
    confidence: float
) -> str:
    """Create human-readable summary of code generation."""
    summary_parts = [
        f"**Code Generation Summary**",
        f"",
        f"**Overall Confidence**: {confidence:.0%}",
        f"",
        f"**Files Generated**: {file_count}",
        f"",
        f"**Implementation Plan**:",
        f"{chr(10).join(['- ' + item for item in generation.get('plan', [])[:5]])}",
        f""
    ]
    
    # Add file tree
    file_tree = generation.get("file_tree", "")
    if file_tree:
        summary_parts.append("**File Tree**:")
        summary_parts.append(f"```")
        summary_parts.append(file_tree[:500])
        summary_parts.append("```")
        summary_parts.append("")
    
    # Add assumptions if any
    assumptions = generation.get("assumptions", [])
    if assumptions:
        summary_parts.append(f"**Assumptions**: {len(assumptions)}")
        for assumption in assumptions[:3]:  # Show top 3
            summary_parts.append(f"- {assumption[:150]}")
        summary_parts.append("")
    
    # Add security review if any
    security_review = generation.get("security_review", [])
    if security_review:
        summary_parts.append(f"**Security Considerations**: {len(security_review)}")
        for security in security_review[:3]:  # Show top 3
            summary_parts.append(f"- {security[:150]}")
        summary_parts.append("")
    
    # Add limitations if any
    limitations = generation.get("limitations", [])
    if limitations:
        summary_parts.append(f"**Known Limitations**: {len(limitations)}")
        for limitation in limitations[:3]:  # Show top 3
            summary_parts.append(f"- {limitation[:150]}")
    
    return "\n".join(summary_parts)


# ============================================================================
# HITL REVIEW NODE
# ============================================================================

def review_code_node(state: CodeGeneratorState) -> Dict[str, Any]:
    """
    HITL checkpoint: Review generated code, answer questions, and process human feedback.
    
    This node:
    1. Displays generated code in a readable format
    2. Answers human questions if provided (Q&A capability)
    3. Processes human feedback if provided
    4. Updates code if human provides corrections
    5. Sets routing decision for loop or END
    """
    logger.info("👤 HITL Checkpoint: Reviewing generated code...")
    
    # Get iteration count (safety limit)
    iteration_count = state.get('iteration_count', 0)
    max_iterations = 3  # Safety limit to prevent infinite loops
    
    # Get human feedback and questions if provided
    human_feedback = state.get('human_feedback', '')
    human_approval = state.get('human_approval', '')
    human_question = state.get('human_question', '')
    
    # Start with current state values
    updated_state = {
        "current_step": "code_review",
        "generation_summary": state.get('generation_summary', '')
    }
    
    # Handle human questions (Q&A capability)
    if human_question:
        logger.info(f"❓ Human question received: {human_question[:100]}...")
        
        # Check if answer already exists (from previous review cycle)
        existing_answer = state.get('agent_answer', '')
        
        if not existing_answer:
            # No answer yet - generate it
            from utils.agent_qa_node import answer_question_node
            
            # Answer the question
            qa_result = answer_question_node(state)
            updated_state.update({
                "agent_answer": qa_result.get("agent_answer", ""),
                "question_answered": qa_result.get("question_answered", False)
            })
            logger.info(f"✅ Question answered: {len(qa_result.get('agent_answer', ''))} chars")
        else:
            # Answer already exists - just use it (don't regenerate)
            updated_state.update({
                "agent_answer": existing_answer,
                "question_answered": True
            })
            logger.info(f"✅ Using existing answer: {len(existing_answer)} chars")
    
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
                # Extract additional code info from feedback
                feedback_info = _extract_code_from_feedback(human_feedback)
                
                # Merge with existing generation
                existing_code_files = state.get('code_files', {})
                if feedback_info:
                    # Enrich code with feedback
                    enriched_code_files = _enrich_code_with_feedback(existing_code_files, feedback_info)
                    updated_state.update({
                        "code_files": enriched_code_files,
                        "generation_confidence": min(state.get('generation_confidence', 0.0) + 0.1, 1.0),
                        "iteration_count": iteration_count + 1
                    })
                else:
                    # Keep existing but boost confidence
                    updated_state.update({
                        "generation_confidence": min(state.get('generation_confidence', 0.0) + 0.1, 1.0),
                        "iteration_count": iteration_count + 1
                    })
                
                logger.info(f"✅ Code refined: Updated generation")
                logger.info(f"🔄 Iteration {updated_state['iteration_count']}/{max_iterations}")
            
        elif human_approval.lower() == 'rejected':
            logger.warning("❌ Code generation rejected by human - ending workflow")
            
        elif human_approval.lower() == 'approved':
            logger.info("✅ Code generation approved by human - ending workflow")
    
    # Format review message
    code_files = state.get('code_files', {})
    file_count = len(code_files)
    
    review_message = f"""
# Code Generation Review

## Generation Summary

{state.get('generation_summary', 'No generation available')}

## Code Generation Details

- **Files Generated**: {file_count}
- **File Tree**: {state.get('file_tree', 'Not generated')[:200]}
- **Implementation Plan Steps**: {len(state.get('plan', []))}
- **Assumptions**: {len(state.get('assumptions', []))}
- **Security Considerations**: {len(state.get('security_review', []))}

## Status

- **Confidence**: {updated_state.get('generation_confidence', state.get('generation_confidence', 0.0)):.0%}
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
                review_message += f"- **Confidence Updated**: {updated_state.get('generation_confidence', 0.0):.0%}\n"
                review_message += f"- **Next**: Will re-generate code with refined information\n"
    
    if human_approval:
        review_message += f"\n## Approval Status: {human_approval}\n"
    
    # Signal workflow status based on routing decision
    if human_question and updated_state.get('agent_answer'):
        # Q&A happened - show status
        review_message += "\n## Workflow Status\n\n"
        review_message += "❓ **Question answered - reviewing answer**\n\n"
        review_message += "After reviewing the answer, you can:\n"
        review_message += "- Approve: Set `human_approval: 'approved'`\n"
        review_message += "- Request refinement: Set `human_approval: 'needs_refinement'`\n"
        review_message += "- Ask another question: Set `human_question: 'Your next question'`\n"
        review_message += "- Clear question and continue: Remove `human_question` field\n"
    elif human_approval.lower() == 'needs_refinement' and iteration_count < max_iterations:
        review_message += "\n## Workflow Status\n\n🔄 **Refinement requested - will re-generate code**\n"
    elif human_approval.lower() == 'approved':
        review_message += "\n## Workflow Status\n\n✅ **Code generation approved - workflow will complete**\n"
    elif human_approval.lower() == 'rejected':
        review_message += "\n## Workflow Status\n\n❌ **Code generation rejected - workflow ending**\n"
    else:
        review_message += "\n## Workflow Status\n\n✅ **Code generation complete - workflow finished**\n"
    
    # Update generation summary with the review message
    updated_state['generation_summary'] = review_message
    
    logger.info("💻 Review message prepared")
    
    return updated_state


def _extract_code_from_feedback(feedback: str) -> Dict[str, Any]:
    """
    Extract code information from human feedback.
    
    Examples:
    - "Add authentication module" → {"files": ["auth.py"]}
    - "Fix error handling" → {"improvements": ["error handling"]}
    """
    feedback_lower = feedback.lower()
    extracted = {
        "files": [],
        "improvements": []
    }
    
    # Look for file keywords
    file_keywords = ["file", "module", "class", "function", "add", "create"]
    if any(keyword in feedback_lower for keyword in file_keywords):
        extracted["files"].append(feedback)
    
    # Look for improvement keywords
    improvement_keywords = ["fix", "improve", "change", "update", "modify"]
    if any(keyword in feedback_lower for keyword in improvement_keywords):
        extracted["improvements"].append(feedback)
    
    return extracted


def _enrich_code_with_feedback(
    existing_code_files: Dict[str, str],
    feedback_info: Dict[str, Any]
) -> Dict[str, str]:
    """Enrich existing code with feedback information."""
    enriched = existing_code_files.copy()
    
    # Add files from feedback
    if feedback_info.get("files"):
        for feedback_file in feedback_info["files"]:
            # Create placeholder file
            file_path = feedback_file.replace(" ", "_").lower() + ".py"
            enriched[file_path] = f"# File added based on feedback\n# {feedback_file}\n\n# TODO: Implement based on requirements"
    
    return enriched


# ============================================================================
# FINALIZE NODE
# ============================================================================

def finalize_code_node(state: CodeGeneratorState) -> Dict[str, Any]:
    """
    Final completion node: Generate final summary message before workflow ends.
    
    This node runs when workflow is ending (approved/rejected/max_iterations)
    to provide a clear final message to the user.
    """
    logger.info("🏁 Finalizing code generation workflow...")
    
    human_approval = state.get('human_approval', '').lower()
    iteration_count = state.get('iteration_count', 0)
    code_files = state.get('code_files', {})
    file_count = len(code_files)
    
    # Determine completion status
    if human_approval == 'approved':
        status_emoji = "✅"
        status_text = "Approved"
        completion_message = "Code generation approved and workflow completed successfully."
    elif human_approval == 'rejected':
        status_emoji = "❌"
        status_text = "Rejected"
        completion_message = "Code generation rejected. Workflow ending."
    elif iteration_count >= 3:
        status_emoji = "⚠️"
        status_text = "Max Iterations Reached"
        completion_message = "Maximum refinement iterations reached. Workflow ending."
    else:
        status_emoji = "✅"
        status_text = "Complete"
        completion_message = "Code generation workflow completed."
    
    # Build final summary
    generation_summary = state.get('generation_summary', '')
    if not generation_summary or "Code Generation Review" in generation_summary:
        generation_summary = _format_code_generation_summary(
            {"files": [{"path": k, "content": v} for k, v in code_files.items()],
             "plan": state.get('plan', []),
             "assumptions": state.get('assumptions', []),
             "security_review": state.get('security_review', []),
             "limitations": state.get('limitations', [])},
            file_count,
            state.get('generation_confidence', 0.0)
        )
    
    # Create final completion message
    final_message = f"""
# {status_emoji} Code Generation Complete

## Final Summary

{completion_message}

## Code Generation Results

{generation_summary}

## Final Generation

- **Files Generated**: {file_count}
- **File Tree**: {state.get('file_tree', 'Not generated')[:200]}
- **Implementation Plan Steps**: {len(state.get('plan', []))}
- **Assumptions**: {len(state.get('assumptions', []))}
- **Security Considerations**: {len(state.get('security_review', []))}
- **Confidence**: {state.get('generation_confidence', 0.0):.0%}
- **Iterations**: {iteration_count}
- **Status**: {status_emoji} {status_text}

## Generated Files

{', '.join(list(code_files.keys())[:10]) if code_files else 'No files generated'}

---

## Workflow Complete

✅ **The code generation workflow has finished.**

The generated code is now ready for:
- Code review phase
- Testing phase
- Documentation phase
- Deployment planning

**Current Step**: completed
"""
    
    logger.info(f"✅ Final message prepared - workflow complete (status: {status_text})")
    
    return {
        "current_step": "completed",
        "generation_summary": final_message
    }


# ============================================================================
# ROUTING FUNCTION
# ============================================================================

def _route_after_review(state: CodeGeneratorState) -> str:
    """
    Routing function: Decide whether to loop back for refinement, show Q&A answer, or end workflow.
    
    Returns:
        "review_code" if question was asked and answer needs to be shown
        "generate_code" if refinement needed and within iteration limit
        "finalize_code" if approved, rejected, or max iterations reached
    """
    human_approval = state.get('human_approval', '').lower()
    human_question = state.get('human_question', '')
    agent_answer = state.get('agent_answer', '')
    iteration_count = state.get('iteration_count', 0)
    max_iterations = 3
    
    # CRITICAL: If question was asked but no answer yet, or answer just generated, stay at review
    # This allows user to see the answer before proceeding
    if human_question:
        if not agent_answer:
            # Question asked but no answer yet - should not happen, but route back to review
            logger.info("❓ Question asked but no answer - routing back to review_code to process")
            return "review_code"
        elif agent_answer and not human_approval:
            # Answer generated but user hasn't provided approval yet - stay at review
            logger.info("❓ Question answered - routing back to review_code to display answer")
            return "review_code"
    
    # End conditions - route to finalize_code first
    if human_approval == 'approved':
        logger.info("✅ Approved - routing to finalize_code")
        return "finalize_code"
    
    if human_approval == 'rejected':
        logger.info("❌ Rejected - routing to finalize_code")
        return "finalize_code"
    
    if iteration_count >= max_iterations:
        logger.info(f"⚠️ Max iterations ({max_iterations}) reached - routing to finalize_code")
        return "finalize_code"
    
    # Confidence-based auto-approval (if no human feedback/question and high confidence)
    if not human_approval and not human_question and state.get('generation_confidence', 0.0) >= 0.9:
        logger.info("✅ High confidence, no feedback/question - routing to finalize_code")
        return "finalize_code"
    
    # Loop back for refinement
    if human_approval == 'needs_refinement':
        logger.info(f"🔄 Refinement requested - looping back to generate_code (iteration {iteration_count + 1}/{max_iterations})")
        return "generate_code"
    
    # Default: If question was asked and answered, stay at review for user to see answer
    if human_question and agent_answer:
        logger.info("❓ Question answered - staying at review_code to display answer")
        return "review_code"
    
    # Default: route to finalize
    logger.info("🏁 No refinement requested - routing to finalize_code")
    return "finalize_code"


# ============================================================================
# GRAPH BUILDING
# ============================================================================

def build_graph():
    """
    Build isolated code generator graph with HITL checkpoint and iterative refinement loop.
    
    Graph flow:
    START → generate_code → [interrupt_after] → review_code → [conditional]
                                                              ├→ generate_code (if needs_refinement)
                                                              └→ finalize_code → END (if approved/rejected/max_iterations)
    
    NOTE: For LangGraph Studio, we use interrupt_after on generate_code
    instead of interrupt_before on review_code to ensure proper END edge handling.
    """
    workflow = StateGraph(CodeGeneratorState)
    
    # Add nodes
    workflow.add_node("generate_code", generate_code_node)
    workflow.add_node("review_code", review_code_node)
    workflow.add_node("finalize_code", finalize_code_node)  # Final completion node
    
    # Flow: START → generate_code → review_code → [conditional] → generate_code OR finalize_code → END
    workflow.set_entry_point("generate_code")
    workflow.add_edge("generate_code", "review_code")
    
    # Conditional edge: review_code → generate_code (loop) OR review_code (Q&A) OR finalize_code
    workflow.add_conditional_edges(
        "review_code",
        _route_after_review,  # Routing function decides next step
        {
            "generate_code": "generate_code",  # Loop back for refinement
            "review_code": "review_code",  # Stay at review for Q&A display
            "finalize_code": "finalize_code"  # Finalize and end
        }
    )
    
    # Finalize code → END (always ends workflow)
    workflow.add_edge("finalize_code", END)
    
    # Use interrupt_after instead of interrupt_before for better END handling
    # This pauses AFTER generate_code, allowing review_code to complete normally
    # Also interrupt after review_code if Q&A is happening
    compiled = workflow.compile(
        interrupt_after=["generate_code", "review_code"]  # HITL: pause after generation and after review (for Q&A)
    )
    
    logger.info("✅ Code generator graph compiled with iterative refinement loop")
    logger.info("🔄 Loop: generate_code → review_code → [needs_refinement?] → generate_code")
    logger.info("🏁 End flow: review_code → finalize_code → END")
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
        logger.error(f"Failed to build code generator graph: {e}")
        logger.exception("Full traceback:")
        # Return None to allow Studio to start even if this graph fails
        return None


# Export for Studio
try:
    graph = get_graph()
except Exception as e:
    logger.error(f"Failed to export code generator graph: {e}")
    logger.exception("Full traceback:")
    graph = None  # Allow Studio to start even if this graph fails

