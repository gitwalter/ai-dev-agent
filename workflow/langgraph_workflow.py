"""
LangGraph Agent Swarm - Following Framework Standards
======================================================

Simple implementation following LangGraph/LangChain patterns:
- Use StateGraph for workflow
- Use create_react_agent for agents  
- Let framework handle event loops and state
- Add complexity only when use case requires it
"""

from __future__ import annotations

import logging
import os
from typing import Dict, Any, List, Annotated
try:
    from typing_extensions import TypedDict  # Python < 3.12 compatibility
except ImportError:
    from typing import TypedDict  # Python >= 3.12
import operator
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

# ============================================================================
# PROMPT LOADING - Simple helper
# ============================================================================

def load_prompt_from_langsmith(prompt_name: str, fallback: str = None) -> str:
    """Load prompt from LangSmith with local caching.
    
    Caching strategy:
    1. Check local cache (prompts/langsmith_cache/{prompt_name}.txt)
    2. If not cached, pull from LangSmith Hub
    3. Save to cache for future use
    4. If LangSmith fails, use cached version if available
    5. If no cache and LangSmith fails, use fallback
    
    IMPORTANT: Uses exact same naming as LangSmith Hub (e.g., test_generator_v1)
    """
    from pathlib import Path
    
    # Cache directory and file (use exact LangSmith name)
    cache_dir = Path("prompts/langsmith_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{prompt_name}.txt"
    
    try:
        # Try Streamlit secrets first
        try:
            import streamlit as st
            api_key = st.secrets.get('LANGSMITH_API_KEY') or st.secrets.get('LANGCHAIN_API_KEY')
        except:
            api_key = os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGCHAIN_API_KEY")
        
        if api_key:
            from langsmith import Client
            client = Client(api_key=api_key)
            prompt = client.pull_prompt(prompt_name, include_model=True)
            
            # Extract template
            prompt_text = None
            if hasattr(prompt, 'template'):
                prompt_text = prompt.template
            elif hasattr(prompt, 'messages') and prompt.messages:
                prompt_text = str(prompt.messages[0].prompt.template)
            else:
                prompt_text = str(prompt)
            
            # Cache the prompt (using exact LangSmith name)
            try:
                cache_file.write_text(prompt_text, encoding='utf-8')
                logger.info(f"Cached prompt: {prompt_name}")
            except Exception as cache_err:
                logger.warning(f"Failed to cache {prompt_name}: {cache_err}")
            
            return prompt_text
        else:
            # No API key - try cache
            if cache_file.exists():
                logger.info(f"Using cached prompt (no API key): {prompt_name}")
                return cache_file.read_text(encoding='utf-8')
            else:
                logger.info(f"No API key, no cache - using fallback for {prompt_name}")
                return fallback or f"You are {prompt_name}. Complete the task."
            
    except Exception as e:
        # LangSmith failed - try cache
        if cache_file.exists():
            logger.warning(f"LangSmith failed for {prompt_name}, using cache: {e}")
            return cache_file.read_text(encoding='utf-8')
        else:
            logger.warning(f"LangSmith failed, no cache - using fallback for {prompt_name}: {e}")
            return fallback or f"You are {prompt_name}. Complete the task."


# ============================================================================
# STATE - Simple TypedDict with Annotated reducers
# ============================================================================

class SwarmState(TypedDict):
    """Agent swarm state - following LangGraph patterns."""
    # Input
    project_context: str
    
    # Routing decisions - Context Detection (Phase 1: US-CONTEXT-001)
    project_complexity: str  # simple, medium, complex
    project_domain: str  # ai, web, api, data, mobile, etc.
    project_intent: str  # new_feature, bug_fix, refactor, migration, etc.
    detected_entities: List[str]  # Technology names, frameworks, services, etc.
    required_agents: List[str]  # Which agents to run
    next_agent: str  # Which agent runs next
    
    # Messages - accumulated (operator.add)
    messages: Annotated[List, operator.add]
    
    # Agent outputs - each agent has its own field(s)
    requirements: Dict[str, Any]        # requirements_analyst output
    architecture: Dict[str, Any]        # architecture_designer output
    code_files: Dict[str, str]          # code_generator output: {filename: content}
    code_metadata: Dict[str, Any]       # code_generator metadata: plan, assumptions, etc.
    test_files: Dict[str, Any]          # test_generator output
    code_review: Dict[str, Any]         # code_reviewer output
    documentation: Dict[str, Any]       # documentation_generator output
    
    # Tracking
    completed_agents: Annotated[List[str], operator.add]
    current_step: str
    errors: Annotated[List[str], operator.add]


# ============================================================================
# AGENT SWARM - Simple and Clean
# ============================================================================

class AgentSwarm:
    """Simple agent swarm following LangGraph patterns."""
    
    # Define standard agent execution order (CRITICAL: enforced in code, not LLM)
    STANDARD_AGENT_ORDER = [
        "requirements_analyst",
        "architecture_designer",
        "code_generator",
        "test_generator",
        "code_reviewer",
        "documentation_generator"
    ]
    
    def __init__(self, llm_config: Dict[str, Any]):
        """Initialize swarm."""
        self.llm_config = llm_config
        self.logger = logging.getLogger(__name__)
        
        # Build workflow immediately - simple and straightforward
        self.workflow = self._build_workflow()
        
        self.logger.info("✅ Agent Swarm initialized")
    
    def _create_llm(self):
        """Create LLM - simple helper."""
        return ChatGoogleGenerativeAI(
            model=self.llm_config.get('model_name', 'gemini-2.5-flash'),
            google_api_key=os.environ.get("GEMINI_API_KEY"),
            temperature=self.llm_config.get('temperature', 0.0)  # Deterministic for software development
        )
    
    def _build_workflow(self):
        """Build workflow with supervisor pattern - following LangGraph standards."""
        
        # Create single LLM for all agents (simple and efficient)
        llm = self._create_llm()
        
        # Load prompts from LangSmith (simple with fallbacks)
        self.logger.info("📥 Loading prompts from LangSmith...")
        prompts = {
            # Supervisor/Coordination Agent Prompts
            "complexity_analyzer": load_prompt_from_langsmith(
                "complexity_analyzer_v1",
                "You are a Complexity Analyzer. Analyze project complexity and classify as simple, medium, or complex."
            ),
            "agent_selector": load_prompt_from_langsmith(
                "agent_selector_v1",
                "You are an Agent Selector. Select which specialist agents are needed based on project requirements."
            ),
            "router": load_prompt_from_langsmith(
                "router_v1",
                "You are a Router. Route to the next agent in the workflow based on completion status."
            ),
            # Specialist Agent Prompts
            "requirements_analyst": load_prompt_from_langsmith(
                "requirements_analyst_v1",
                "You are an expert Requirements Analyst. Analyze project requirements thoroughly."
            ),
            "architecture_designer": load_prompt_from_langsmith(
                "architecture_designer_v1",
                "You are an expert Architecture Designer. Design scalable, maintainable systems."
            ),
            "code_generator": load_prompt_from_langsmith(
            "code_generator_v1",
                "You are an expert Code Generator. Write clean, production-ready code."
            ),
            "test_generator": load_prompt_from_langsmith(
                "test_generator_v1",
                "You are an expert Test Generator. Create comprehensive test suites."
            ),
            "code_reviewer": load_prompt_from_langsmith(
                "code_reviewer_v1",
                "You are an expert Code Reviewer. Review code quality and suggest improvements."
            ),
            "documentation_generator": load_prompt_from_langsmith(
                "documentation_generator_v1",
                "You are an expert Documentation Generator. Create clear, comprehensive docs."
            ),
        }
        
        # Store prompts for use in agent nodes
        self.prompts = prompts
        self.logger.info(f"✅ Loaded {len(prompts)} prompts")
        
        # Create specialist agents using create_react_agent (standard LangGraph way)
        # Note: Prompts are applied in the node wrappers, not here
        self.agents = {
            "requirements_analyst": create_react_agent(llm, name="requirements_analyst", tools=[]),
            "architecture_designer": create_react_agent(llm, name="architecture_designer", tools=[]),
            "code_generator": create_react_agent(llm, name="code_generator", tools=[]),
            "test_generator": create_react_agent(llm, name="test_generator", tools=[]),
            "code_reviewer": create_react_agent(llm, name="code_reviewer", tools=[]),
            "documentation_generator": create_react_agent(llm, name="documentation_generator", tools=[]),
        }
        
        # Build workflow graph
        workflow = StateGraph(SwarmState)
        
        # Add supervisor nodes (simple decision makers)
        workflow.add_node("complexity_analyzer", self._analyze_complexity)
        workflow.add_node("agent_selector", self._select_agents)
        workflow.add_node("router", self._route_to_next)
        
        # Add specialist agent nodes
        workflow.add_node("requirements_analyst", self._requirements_node)
        workflow.add_node("architecture_designer", self._architecture_node)
        workflow.add_node("code_generator", self._code_node)
        workflow.add_node("test_generator", self._test_node)
        workflow.add_node("code_reviewer", self._review_node)
        workflow.add_node("documentation_generator", self._doc_node)
        
        # Flow: complexity → selector → router → agents → router → ... → END
        workflow.set_entry_point("complexity_analyzer")
        workflow.add_edge("complexity_analyzer", "agent_selector")
        workflow.add_edge("agent_selector", "router")
        
        # Router uses conditional edge to decide next agent or END
        # Use named method instead of lambda to avoid "Unnamed" nodes in LangSmith traces
        workflow.add_conditional_edges(
            "router",
            self._router_decision,
            {
                "requirements_analyst": "requirements_analyst",
                "architecture_designer": "architecture_designer",
                "code_generator": "code_generator",
                "test_generator": "test_generator",
                "code_reviewer": "code_reviewer",
                "documentation_generator": "documentation_generator",
                "END": END
            }
        )
        
        # All agents return to router
        for agent_name in self.agents.keys():
            workflow.add_edge(agent_name, "router")
        
        # Compile (no checkpointer for Studio compatibility)
        return workflow.compile()
    
    # ========================================================================
    # SUPERVISOR NODES - LLM-based intelligent decision makers
    # ========================================================================
    
    def _analyze_complexity(self, state: SwarmState) -> Dict[str, Any]:
        """
        Analyze project complexity, domain, intent, and entities using LLM.
        
        Phase 1 (US-CONTEXT-001): Enhanced context detection that classifies:
        - Complexity: simple, medium, complex
        - Domain: ai, web, api, data, mobile, etc.
        - Intent: new_feature, bug_fix, refactor, migration, etc.
        - Entities: Technology names, frameworks, services extracted from context
        """
        self.logger.info("📊 Analyzing complexity and context with LLM...")
        
        llm = self._create_llm()
        system_prompt = self.prompts.get("complexity_analyzer", "You are a complexity analyzer")
        
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
        
        result = llm.invoke(messages)
        output = result.content.strip()
        
        # Parse JSON response
        try:
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
            
            self.logger.info(
                f"📊 Context detected: complexity={complexity}, domain={domain}, "
                f"intent={intent}, entities={len(entities)}"
            )
            
            return {
                "project_complexity": complexity,
                "project_domain": domain,
                "project_intent": intent,
                "detected_entities": entities,
                "current_step": "complexity_analyzed"
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to parse context detection JSON: {e}. Using defaults.")
            # Fallback to defaults
            return {
                "project_complexity": "medium",
                "project_domain": "general",
                "project_intent": "new_feature",
                "detected_entities": [],
                "current_step": "complexity_analyzed"
            }
    
    def _select_agents(self, state: SwarmState) -> Dict[str, Any]:
        """Select which agents to run using LLM with LangSmith prompt.
        
        Phase 2 (US-CONTEXT-001): Enhanced agent selection that uses detected context:
        - Domain, intent, and entities inform agent selection
        - Better agent selection accuracy with context-aware routing
        
        CRITICAL: LLM selects WHICH agents, but code enforces STANDARD ORDER.
        """
        self.logger.info("🎯 Selecting agents with LLM...")
        
        llm = self._create_llm()
        system_prompt = self.prompts.get("agent_selector", "You are an agent selector")
        
        # Enhanced task prompt with context information
        task = f"""Select which specialist agents are needed for this project.

Project: {state['project_context']}

Detected Context:
- Domain: {state.get('project_domain', 'general')}
- Intent: {state.get('project_intent', 'new_feature')}
- Complexity: {state.get('project_complexity', 'medium')}
- Entities: {', '.join(state.get('detected_entities', [])[:10])}  # Limit to first 10

Available agents:
- requirements_analyst: Analyzes requirements
- architecture_designer: Designs system architecture  
- code_generator: Writes code
- test_generator: Creates tests
- code_reviewer: Reviews code quality
- documentation_generator: Creates documentation

Use the detected context to make informed agent selection decisions.
For example:
- Domain: ai → May need all agents for complex AI systems
- Intent: bug_fix → May need code_generator, test_generator, code_reviewer
- Intent: new_feature → Usually needs all agents

Respond with a comma-separated list of agent names that are needed (order doesn't matter)."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task)
        ]
        
        result = llm.invoke(messages)
        agent_list = result.content.strip()
        
        # Parse agent names
        selected = [name.strip() for name in agent_list.split(",")]
        
        # Validate agent names
        valid_agents = set(self.agents.keys())
        selected_set = set(agent for agent in selected if agent in valid_agents)
        
        # Ensure we have at least some agents
        if not selected_set:
            selected_set = valid_agents
        
        # CRITICAL FIX: Enforce standard execution order
        # Sort selected agents according to STANDARD_AGENT_ORDER
        required = [agent for agent in self.STANDARD_AGENT_ORDER if agent in selected_set]
        
        self.logger.info(f"🎯 Selected {len(required)} agents in standard order: {required}")
        return {"required_agents": required, "current_step": "agents_selected"}
    
    def _route_to_next(self, state: SwarmState) -> Dict[str, Any]:
        """Route to next agent - simple sequential logic."""
        required = state.get("required_agents", [])
        completed = state.get("completed_agents", [])
        
        # Find next agent not yet completed
        next_agent = "END"
        for agent in required:
            if agent not in completed:
                next_agent = agent
                break
            
        self.logger.info(f"🔀 Next: {next_agent}")
        return {"next_agent": next_agent, "current_step": "routing"}
    
    def _router_decision(self, state: SwarmState) -> str:
        """Router decision for conditional edge - returns next agent name or END.
        
        This is a named method (not lambda) to ensure proper tracing in LangSmith.
        """
        return state.get("next_agent", "END")
    
    # ========================================================================
    # SPECIALIST AGENT NODES - Simple wrappers
    # ========================================================================
    
    def _requirements_node(self, state: SwarmState) -> Dict[str, Any]:
        """Requirements analyst node."""
        return self._run_agent(self.agents["requirements_analyst"], state, "requirements_analyst", "requirements")
    
    def _architecture_node(self, state: SwarmState) -> Dict[str, Any]:
        """Architecture designer node."""
        return self._run_agent(self.agents["architecture_designer"], state, "architecture_designer", "architecture")
    
    def _code_node(self, state: SwarmState) -> Dict[str, Any]:
        """Code generator node."""
        agent = self.agents["code_generator"]
        system_prompt = self.prompts.get("code_generator", "You are a code generator")
        
        task = f"""Project: {state['project_context']}

Requirements: {state.get('requirements', {})}
Architecture: {state.get('architecture', {})}

Generate complete, production-ready source code for this project."""
        
        try:
            self.logger.info(f"🤖 Running code_generator...")
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=task)
            ]
            
            result = agent.invoke({"messages": messages})
            last_msg = result["messages"][-1]
            output = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            
            # Parse the structured JSON output from LangSmith prompt
            try:
                import json
                import re
                
                # Extract JSON from markdown code block if present
                json_match = re.search(r'```json\s*(\{.*\})\s*```', output, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = output
                
                parsed = json.loads(json_str)
                
                # Extract code files from structured format
                if "files" in parsed and isinstance(parsed["files"], list):
                    code_files = {}
                    for file_obj in parsed["files"]:
                        if "path" in file_obj and "content" in file_obj:
                            code_files[file_obj["path"]] = file_obj["content"]
                    
                    self.logger.info(f"✅ code_generator completed - generated {len(code_files)} files")
                    
                    # Return structured output - store files directly in code_files
                    # and metadata separately
                    return {
                        "code_files": code_files,  # FIXED: Store files directly, not nested
                        "code_metadata": {
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
                        },
                        "completed_agents": ["code_generator"],
                        "current_step": "code_generator",
                        "messages": [AIMessage(content=f"code_generator: Generated {len(code_files)} files")]
                    }
                else:
                    raise ValueError("No files found in output")
                    
            except Exception as parse_error:
                self.logger.warning(f"Failed to parse structured output: {parse_error}")
                # Fallback: use raw output
            return {
                    "code_files": {"raw_output": output},
                    "completed_agents": ["code_generator"],
                    "current_step": "code_generator",
                    "messages": [AIMessage(content=f"code_generator: Generated code (unparsed)")]
            }
            
        except Exception as e:
            self.logger.error(f"❌ code_generator failed: {e}")
            return {
                "errors": [f"code_generator: {str(e)}"],
                "completed_agents": ["code_generator"],
                "current_step": "code_generator_failed"
            }
    
    def _test_node(self, state: SwarmState) -> Dict[str, Any]:
        """Test generator node - generates actual test code files."""
        agent = self.agents["test_generator"]
        system_prompt = self.prompts.get("test_generator", "You are a test generator")
        
        # Simple task - the LangSmith prompt handles all instructions
        task = f"""Project: {state['project_context']}

Requirements: {state.get('requirements', {})}
Code Files: {state.get('code_files', {})}

Generate comprehensive test files with actual, executable test code."""
        
        try:
            self.logger.info(f"🤖 Running test_generator...")
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=task)
            ]
            
            result = agent.invoke({"messages": messages})
            last_msg = result["messages"][-1]
            output = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            
            # Parse the structured JSON output with robust error handling
            try:
                import json
                import re
                
                # Step 1: Extract JSON from markdown code block if present
                # Method 1: Look for markdown code block with json
                json_match = re.search(r'```json\s*(\{.*\})\s*```', output, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Method 2: Find JSON object boundaries using balanced brace counting
                    # This handles nested braces correctly
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
                            # Unclosed braces - use what we have
                            json_str = output[first_brace:]
                    else:
                        json_str = output
                
                # Step 2: Clean and validate JSON string
                # Remove any trailing commas before closing braces/brackets
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                
                # Step 3: Try to parse JSON with detailed error reporting
                try:
                    parsed = json.loads(json_str)
                except json.JSONDecodeError as json_err:
                    # Log detailed error information
                    self.logger.warning(
                        f"JSON parse error at line {json_err.lineno}, column {json_err.colno}: {json_err.msg}\n"
                        f"Context (first 500 chars): {json_str[:500]}\n"
                        f"Context around error (last 500 chars): {json_str[max(0, json_err.pos-250):json_err.pos+250]}"
                    )
                    raise
                
                # Extract test files from structured format
                # Handle multiple possible formats
                test_files = {}
                
                if "test_files" in parsed:
                    test_files_data = parsed["test_files"]
                    
                    # Format 1: List of file objects with path/content
                    if isinstance(test_files_data, list):
                        for file_obj in test_files_data:
                            if isinstance(file_obj, dict):
                                # Try path/content format
                                if "path" in file_obj and "content" in file_obj:
                                    test_files[file_obj["path"]] = file_obj["content"]
                                # Try filename/content format
                                elif "filename" in file_obj and "content" in file_obj:
                                    test_files[file_obj["filename"]] = file_obj["content"]
                    
                    # Format 2: Dict mapping filename to content (direct)
                    elif isinstance(test_files_data, dict):
                        for filename, content in test_files_data.items():
                            # Handle nested structure (filename -> {content: "...", ...})
                            if isinstance(content, dict) and "content" in content:
                                test_files[filename] = content["content"]
                            # Handle direct string content
                            elif isinstance(content, str):
                                test_files[filename] = content
                
                if test_files:
                    self.logger.info(f"✅ test_generator completed - generated {len(test_files)} test files")
                    
                    # Return structured output with all metadata
                    return {
                        "test_files": {
                            "files": test_files,
                            "test_strategy": parsed.get("test_strategy", {}),
                            "coverage_analysis": parsed.get("coverage_analysis", {}),
                            "test_suites": parsed.get("test_suites", []),
                            "performance_tests": parsed.get("performance_tests", {}),
                            "quality_gate_passed": parsed.get("quality_gate_passed", True)
                        },
                        "completed_agents": ["test_generator"],
                        "current_step": "test_generator",
                        "messages": [AIMessage(content=f"test_generator: Generated {len(test_files)} test files")]
                    }
                else:
                    # Fallback: use raw output with parsed JSON structure
                    self.logger.warning("No test_files found in parsed output, using parsed structure as-is")
                    return {
                        "test_files": {
                            "raw_output": output,
                            "parsed_structure": parsed,
                            "test_strategy": parsed.get("test_strategy", {}),
                            "coverage_analysis": parsed.get("coverage_analysis", {}),
                            "test_suites": parsed.get("test_suites", []),
                            "performance_tests": parsed.get("performance_tests", {}),
                            "quality_gate_passed": parsed.get("quality_gate_passed", True)
                        },
                        "completed_agents": ["test_generator"],
                        "current_step": "test_generator",
                        "messages": [AIMessage(content="test_generator: Generated test strategy (parsed)")]
                    }
                    
            except Exception as parse_error:
                # Log detailed error information for debugging
                self.logger.warning(
                    f"Failed to parse test generator output: {parse_error}\n"
                    f"Output length: {len(output)} characters\n"
                    f"Output preview (first 1000 chars): {output[:1000]}\n"
                    f"Output preview (last 500 chars): {output[-500:] if len(output) > 500 else output}"
                )
                # Fallback: use raw output so workflow can continue
                return {
                    "test_files": {"raw_output": output},
                    "completed_agents": ["test_generator"],
                    "current_step": "test_generator",
                    "messages": [AIMessage(content="test_generator: Generated tests (unparsed - check logs)")]
                }
            
        except Exception as e:
            self.logger.error(f"❌ test_generator failed: {e}")
            return {
                "errors": [f"test_generator: {str(e)}"],
                "completed_agents": ["test_generator"],
                "current_step": "test_generator_failed"
            }
    
    def _review_node(self, state: SwarmState) -> Dict[str, Any]:
        """Code reviewer node."""
        return self._run_agent(self.agents["code_reviewer"], state, "code_reviewer", "code_review")
    
    def _doc_node(self, state: SwarmState) -> Dict[str, Any]:
        """Documentation generator node."""
        return self._run_agent(self.agents["documentation_generator"], state, "documentation_generator", "documentation")
    
    def _run_agent(self, agent, state: SwarmState, agent_name: str, output_key: str) -> Dict[str, Any]:
        """Run agent - simple wrapper following LangGraph patterns."""
        try:
            self.logger.info(f"🤖 Running {agent_name}...")
            
            # Get agent's system prompt from LangSmith
            system_prompt = self.prompts.get(agent_name, f"You are {agent_name}")
            
            # Create task-specific message
            task = f"Project: {state['project_context']}\n\n"
            if agent_name == "requirements_analyst":
                task += "Analyze the project requirements and provide detailed specifications."
            elif agent_name == "architecture_designer":
                task += f"Design the system architecture.\nRequirements: {state.get('requirements', {})}"
            elif agent_name == "code_generator":
                task += f"Generate code.\nArchitecture: {state.get('architecture', {})}\nRequirements: {state.get('requirements', {})}"
            elif agent_name == "test_generator":
                task += f"Create comprehensive tests.\nCode: {state.get('code_files', {})}"
            elif agent_name == "code_reviewer":
                task += f"Review the code quality.\nCode: {state.get('code_files', {})}"
            elif agent_name == "documentation_generator":
                task += "Create comprehensive documentation for the project."
            
            # Invoke agent with system prompt + task (LangGraph patterns)
            # System message sets behavior, Human message provides task
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=task)
            ]
            result = agent.invoke({"messages": messages})
            
            # Extract output
            output = "No output"
            if result and "messages" in result and len(result["messages"]) > 0:
                last_msg = result["messages"][-1]
                output = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            
            self.logger.info(f"✅ {agent_name} completed")
            
            # Return state update (framework merges automatically)
            return {
                output_key: {"output": output},
                "completed_agents": [agent_name],
                "current_step": agent_name,
                "messages": [AIMessage(content=f"{agent_name}: {output[:100]}...")]
            }
            
        except Exception as e:
            self.logger.error(f"❌ {agent_name} failed: {e}")
            return {
                "errors": [f"{agent_name}: {str(e)}"],
                "completed_agents": [agent_name],
                "current_step": f"{agent_name}_failed"
            }
    
    async def execute_swarm(self, project_context: str, session_id: str = None) -> Dict[str, Any]:
        """Execute swarm - simple and clean."""
        
        # Initial state
        initial_state: SwarmState = {
            "project_context": project_context,
            "project_complexity": "medium",
            "project_domain": "general",  # Default, will be detected by complexity analyzer
            "project_intent": "new_feature",  # Default, will be detected by complexity analyzer
            "detected_entities": [],  # Will be detected by complexity analyzer
            "required_agents": [],
            "next_agent": "",
            "messages": [],
            "requirements": {},
            "architecture": {},
            "code_files": {},
            "code_metadata": {},
            "test_files": {},
            "code_review": {},
            "documentation": {},
            "completed_agents": [],
            "current_step": "start",
            "errors": []
        }
        
        # Execute workflow - LangGraph handles the rest!
        result = await self.workflow.ainvoke(initial_state)
        
        return result


# ============================================================================
# STUDIO EXPORT - Simple and Clean
# ============================================================================

def get_graph():
    """Export for LangGraph Studio."""
    llm_config = {"model_name": "gemini-2.5-flash", "temperature": 0.0}  # Deterministic
    swarm = AgentSwarm(llm_config)
    return swarm.workflow


# Export for Studio
graph = get_graph()

# Backward compatibility
LangGraphWorkflowManager = AgentSwarm
