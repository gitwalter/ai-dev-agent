#!/usr/bin/env python3
"""
LangGraph-based Workflow System for AI Development Agent.
Uses standard LangChain/LangGraph patterns for agent implementation.
Implements adaptive agent selection based on project requirements.
"""

import asyncio
import logging
from typing import Dict, Any, List, TypedDict, Optional, Annotated
from datetime import datetime

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.prompts import PromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.tools import BaseTool, tool
    from pydantic import BaseModel, Field
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    ChatGoogleGenerativeAI = None
    logging.warning("LangGraph not available, using fallback")

from utils.structured_outputs import (
    RequirementsAnalysisOutput, ArchitectureDesignOutput, CodeGenerationOutput,
    TestGenerationOutput, CodeReviewOutput, SecurityAnalysisOutput, DocumentationGenerationOutput
)

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """
    State management for LangGraph workflow using TypedDict.
    Follows standard LangGraph patterns from Cursor documentation.
    """
    messages: Annotated[List[Any], "Chat messages"]
    current_step: Annotated[str, "Current workflow step"]
    project_context: Annotated[str, "Project context and requirements"]
    project_type: Annotated[str, "Type of project (web_app, api, library, etc.)"]
    project_complexity: Annotated[str, "Project complexity (simple, medium, complex)"]
    
    # Agent outputs (optional based on project needs)
    requirements: Annotated[Dict[str, Any], "Requirements analysis results"]
    architecture: Annotated[Dict[str, Any], "Architecture design results"]
    code_files: Annotated[Dict[str, Any], "Generated code files"]
    test_files: Annotated[Dict[str, Any], "Generated test files"]
    review_results: Annotated[Dict[str, Any], "Code review results"]
    security_analysis: Annotated[Dict[str, Any], "Security analysis results"]
    documentation: Annotated[Dict[str, Any], "Documentation results"]
    
    # Workflow control
    agent_outputs: Annotated[Dict[str, Any], "All agent outputs"]
    errors: Annotated[List[str], "Error messages"]
    execution_history: Annotated[List[Dict[str, Any]], "Execution history"]
    memory: Annotated[Dict[str, Any], "Persistent memory storage"]
    recall_memories: Annotated[List[str], "Retrieved long-term memories"]
    
    # Adaptive workflow control
    required_agents: Annotated[List[str], "List of agents required for this project"]
    completed_agents: Annotated[List[str], "List of completed agents"]
    next_agent: Annotated[Optional[str], "Next agent to execute"]
    workflow_complete: Annotated[bool, "Whether workflow is complete"]


class LangGraphWorkflowManager:
    """
    LangGraph-based workflow manager for AI Development Agent.
    Uses standard LangChain/LangGraph patterns from Cursor documentation.
    Implements adaptive agent selection based on project requirements.
    """
    
    def __init__(self, llm_config: Dict[str, Any], agents: Dict[str, Any] = None, logging_manager = None):
        """
        Initialize the LangGraph workflow manager.
        
        Args:
            llm_config: Configuration for the LLM
            agents: Dictionary of agent instances to use (optional)
            logging_manager: LangChain logging manager for observability
        """
        self.llm_config = llm_config
        self.agents = agents or {}
        self.logging_manager = logging_manager
        self.logger = logging.getLogger(__name__)
        self.llm = self._setup_llm()
        self.workflow = self._create_workflow()
        
    def _setup_llm(self) -> Any:
        """Setup LLM using LangChain patterns."""
        if not LANGGRAPH_AVAILABLE or ChatGoogleGenerativeAI is None:
            raise ImportError("LangGraph or ChatGoogleGenerativeAI not available")
        
        try:
            llm = ChatGoogleGenerativeAI(
                model=self.llm_config.get("model_name", "gemini-2.5-flash-lite"),
                google_api_key=self.llm_config.get("api_key"),
                temperature=self.llm_config.get("temperature", 0.1),
                max_tokens=self.llm_config.get("max_tokens", 8192)
            )
            self.logger.info(f"LLM setup successful: {llm is not None}")
            return llm
        except Exception as e:
            self.logger.error(f"LLM setup failed: {e}")
            raise
    
    def _create_workflow(self) -> StateGraph:
        """Create LangGraph workflow using standard patterns with adaptive routing."""
        # Create workflow graph
        workflow = StateGraph(AgentState)
        
        # Add supervisor nodes
        workflow.add_node("project_analyzer", self._project_analyzer_node)
        workflow.add_node("agent_selector", self._agent_selector_node)
        workflow.add_node("workflow_controller", self._workflow_controller_node)
        
        # Add agent nodes (all optional)
        workflow.add_node("requirements_analyst", self._requirements_analyst_node)
        workflow.add_node("architecture_designer", self._architecture_designer_node)
        workflow.add_node("code_generator", self._code_generator_node)
        workflow.add_node("test_generator", self._test_generator_node)
        workflow.add_node("code_reviewer", self._code_reviewer_node)
        workflow.add_node("security_analyst", self._security_analyst_node)
        workflow.add_node("documentation_generator", self._documentation_generator_node)
        
        # Define adaptive workflow edges
        workflow.add_edge("project_analyzer", "agent_selector")
        workflow.add_edge("agent_selector", "workflow_controller")
        
        # Add START edge to project_analyzer
        workflow.set_entry_point("project_analyzer")
        
        # Add conditional edges for dynamic agent routing
        workflow.add_conditional_edges(
            "workflow_controller",
            self._route_to_next_agent,
            {
                "requirements_analyst": "requirements_analyst",
                "architecture_designer": "architecture_designer", 
                "code_generator": "code_generator",
                "test_generator": "test_generator",
                "code_reviewer": "code_reviewer",
                "security_analyst": "security_analyst",
                "documentation_generator": "documentation_generator",
                "complete": END
            }
        )
        
        # Add edges back to workflow controller after each agent
        workflow.add_edge("requirements_analyst", "workflow_controller")
        workflow.add_edge("architecture_designer", "workflow_controller")
        workflow.add_edge("code_generator", "workflow_controller")
        workflow.add_edge("test_generator", "workflow_controller")
        workflow.add_edge("code_reviewer", "workflow_controller")
        workflow.add_edge("security_analyst", "workflow_controller")
        workflow.add_edge("documentation_generator", "workflow_controller")
        
        # Compile workflow with memory saver
        return workflow.compile(checkpointer=MemorySaver())
    
    def _project_analyzer_node(self, state: AgentState) -> AgentState:
        """Analyze project requirements and determine complexity."""
        try:
            # Simple project analysis based on context
            project_context = state.get("project_context", "").lower()
            
            # Determine project type
            if any(word in project_context for word in ["web", "app", "website", "frontend"]):
                project_type = "web_app"
            elif any(word in project_context for word in ["api", "service", "backend"]):
                project_type = "api"
            elif any(word in project_context for word in ["library", "package", "module"]):
                project_type = "library"
            elif any(word in project_context for word in ["script", "utility", "tool"]):
                project_type = "utility"
            else:
                project_type = "general"
            
            # Determine complexity
            if len(project_context.split()) < 50:
                complexity = "simple"
            elif len(project_context.split()) < 200:
                complexity = "medium"
            else:
                complexity = "complex"
            
            return {
                **state,
                "project_type": project_type,
                "project_complexity": complexity,
                "current_step": "project_analysis",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "project_analysis",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed",
                        "project_type": project_type,
                        "complexity": complexity
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Project analysis failed: {e}")
            return {
                **state,
                "project_type": "general",
                "project_complexity": "medium",
                "errors": [*state.get("errors", []), f"Project analysis failed: {str(e)}"],
                "current_step": "project_analysis",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "project_analysis",
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "error": str(e)
                    }
                ]
            }
    
    def _agent_selector_node(self, state: AgentState) -> AgentState:
        """Select which agents are required for this project."""
        try:
            project_type = state.get("project_type", "general")
            complexity = state.get("project_complexity", "medium")
            
            # Define agent requirements based on project type and complexity
            agent_requirements = {
                "web_app": {
                    "simple": ["requirements_analyst", "code_generator", "documentation_generator"],
                    "medium": ["requirements_analyst", "architecture_designer", "code_generator", "test_generator", "documentation_generator"],
                    "complex": ["requirements_analyst", "architecture_designer", "code_generator", "test_generator", "code_reviewer", "security_analyst", "documentation_generator"]
                },
                "api": {
                    "simple": ["requirements_analyst", "code_generator", "test_generator"],
                    "medium": ["requirements_analyst", "architecture_designer", "code_generator", "test_generator", "security_analyst"],
                    "complex": ["requirements_analyst", "architecture_designer", "code_generator", "test_generator", "code_reviewer", "security_analyst", "documentation_generator"]
                },
                "library": {
                    "simple": ["requirements_analyst", "code_generator", "test_generator"],
                    "medium": ["requirements_analyst", "code_generator", "test_generator", "code_reviewer"],
                    "complex": ["requirements_analyst", "architecture_designer", "code_generator", "test_generator", "code_reviewer", "security_analyst", "documentation_generator"]
                },
                "utility": {
                    "simple": ["requirements_analyst", "code_generator"],
                    "medium": ["requirements_analyst", "code_generator", "test_generator"],
                    "complex": ["requirements_analyst", "code_generator", "test_generator", "code_reviewer"]
                },
                "general": {
                    "simple": ["requirements_analyst", "code_generator"],
                    "medium": ["requirements_analyst", "architecture_designer", "code_generator", "test_generator"],
                    "complex": ["requirements_analyst", "architecture_designer", "code_generator", "test_generator", "code_reviewer", "security_analyst", "documentation_generator"]
                }
            }
            
            required_agents = agent_requirements.get(project_type, {}).get(complexity, ["requirements_analyst", "code_generator"])
            
            return {
                **state,
                "required_agents": required_agents,
                "completed_agents": [],
                "next_agent": required_agents[0] if required_agents else None,
                "workflow_complete": False,
                "current_step": "agent_selection",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "agent_selection",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed",
                        "required_agents": required_agents
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Agent selection failed: {e}")
            return {
                **state,
                "required_agents": ["requirements_analyst", "code_generator"],
                "completed_agents": [],
                "next_agent": "requirements_analyst",
                "workflow_complete": False,
                "errors": [*state.get("errors", []), f"Agent selection failed: {str(e)}"],
                "current_step": "agent_selection",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "agent_selection",
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "error": str(e)
                    }
                ]
            }
    
    def _workflow_controller_node(self, state: AgentState) -> AgentState:
        """Control workflow execution and determine next steps."""
        try:
            required_agents = state.get("required_agents", [])
            completed_agents = state.get("completed_agents", [])
            
            # Find next agent to execute
            next_agent = None
            for agent in required_agents:
                if agent not in completed_agents:
                    next_agent = agent
                    break
            
            # Check if workflow is complete
            workflow_complete = next_agent is None
            
            return {
                **state,
                "next_agent": next_agent,
                "workflow_complete": workflow_complete,
                "current_step": "workflow_control",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "workflow_control",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed",
                        "next_agent": next_agent,
                        "workflow_complete": workflow_complete
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Workflow control failed: {e}")
            return {
                **state,
                "next_agent": None,
                "workflow_complete": True,
                "errors": [*state.get("errors", []), f"Workflow control failed: {str(e)}"],
                "current_step": "workflow_control",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "workflow_control",
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "error": str(e)
                    }
                ]
            }
    
    def _route_to_next_agent(self, state: AgentState) -> str:
        """Route to the next agent or complete workflow."""
        next_agent = state.get("next_agent")
        workflow_complete = state.get("workflow_complete", False)
        
        if workflow_complete or next_agent is None:
            return "complete"
        
        return next_agent
    
    def _requirements_analyst_node(self, state: AgentState) -> AgentState:
        """Requirements analysis node using standard LangChain patterns."""
        try:
            # Debug: Check if LLM is available
            if self.llm is None:
                self.logger.error("LLM is None in requirements analyst node")
                raise ValueError("LLM is not initialized")
            
            # Use JsonOutputParser for structured output
            parser = JsonOutputParser()
            
            # Create prompt template using LangChain patterns
            prompt = PromptTemplate(
                template="""You are an expert Requirements Analyst. Analyze the project context and extract comprehensive requirements.

PROJECT CONTEXT:
{project_context}

PROJECT TYPE: {project_type}
PROJECT COMPLEXITY: {project_complexity}

TASK:
Analyze the project context above and generate a comprehensive requirements analysis.

Return your response as a valid JSON object with the following structure:
{{
    "functional_requirements": [
        {{
            "id": "REQ-001",
            "title": "Requirement Title",
            "description": "Detailed description of the requirement",
            "priority": "high|medium|low",
            "category": "functional|non-functional|technical"
        }}
    ],
    "non_functional_requirements": [
        {{
            "id": "NFR-001", 
            "title": "Non-functional requirement title",
            "description": "Description of non-functional requirement",
            "category": "performance|security|usability|reliability"
        }}
    ],
    "technical_constraints": [
        "List of technical constraints and limitations"
    ],
    "assumptions": [
        "List of assumptions made during analysis"
    ]
}}""",
                input_variables=["project_context", "project_type", "project_complexity"]
            )
            
            # Create the chain using LangChain patterns
            chain = prompt | self.llm | parser
            
            # Execute the chain
            result = chain.invoke({
                "project_context": state.get("project_context", ""),
                "project_type": state.get("project_type", "general"),
                "project_complexity": state.get("project_complexity", "medium")
            })
            
            # Update completed agents
            completed_agents = state.get("completed_agents", [])
            completed_agents.append("requirements_analyst")
            
            # Update state following LangGraph patterns
            return {
                **state,
                "requirements": result,
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    "requirements_analyst": result
                },
                "completed_agents": completed_agents,
                "current_step": "requirements_analysis",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "requirements_analysis",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Requirements analysis failed: {e}")
            return {
                **state,
                "errors": [*state.get("errors", []), f"Requirements analysis failed: {str(e)}"],
                "current_step": "requirements_analysis",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "requirements_analysis",
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "error": str(e)
                    }
                ]
            }
    
    def _architecture_designer_node(self, state: AgentState) -> AgentState:
        """Architecture design node using standard LangChain patterns."""
        try:
            parser = JsonOutputParser()
            
            prompt = PromptTemplate(
                template="""You are an expert Software Architect. Design the system architecture based on the requirements.

PROJECT CONTEXT:
{project_context}

PROJECT TYPE: {project_type}
PROJECT COMPLEXITY: {project_complexity}

REQUIREMENTS:
{requirements}

TASK:
Design a comprehensive system architecture that meets the requirements.

Return your response as a valid JSON object with the following structure:
{{
    "architecture_design": {{
        "system_overview": "High-level system description",
        "components": [
            {{
                "name": "Component Name",
                "description": "Component description",
                "responsibilities": ["List of responsibilities"],
                "dependencies": ["List of dependencies"]
            }}
        ],
        "technology_stack": {{
            "frontend": ["List of frontend technologies"],
            "backend": ["List of backend technologies"],
            "database": ["List of database technologies"],
            "infrastructure": ["List of infrastructure technologies"]
        }},
        "data_flow": "Description of data flow between components",
        "security_considerations": ["List of security considerations"]
    }}
}}""",
                input_variables=["project_context", "project_type", "project_complexity", "requirements"]
            )
            
            chain = prompt | self.llm | parser
            
            result = chain.invoke({
                "project_context": state.get("project_context", ""),
                "project_type": state.get("project_type", "general"),
                "project_complexity": state.get("project_complexity", "medium"),
                "requirements": str(state.get("requirements", {}))
            })
            
            # Update completed agents
            completed_agents = state.get("completed_agents", [])
            completed_agents.append("architecture_designer")
            
            return {
                **state,
                "architecture": result.get("architecture_design", {}),
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    "architecture_designer": result
                },
                "completed_agents": completed_agents,
                "current_step": "architecture_design",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "architecture_design",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Architecture design failed: {e}")
            return {
                **state,
                "errors": [*state.get("errors", []), f"Architecture design failed: {str(e)}"],
                "current_step": "architecture_design",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "architecture_design",
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "error": str(e)
                    }
                ]
            }
    
    def _code_generator_node(self, state: AgentState) -> AgentState:
        """Code generation node using standard LangChain patterns."""
        try:
            parser = JsonOutputParser()
            
            prompt = PromptTemplate(
                template="""You are an expert Software Developer. Generate production-ready code based on the architecture.

PROJECT CONTEXT:
{project_context}

PROJECT TYPE: {project_type}
PROJECT COMPLEXITY: {project_complexity}

REQUIREMENTS:
{requirements}

ARCHITECTURE:
{architecture}

TASK:
Generate production-ready code that implements the architecture and meets the requirements.

Return your response as a valid JSON object with the following structure:
{{
    "generated_code": {{
        "main_files": [
            {{
                "filename": "main.py",
                "content": "Complete file content with imports and main logic",
                "description": "Description of what this file does"
            }}
        ],
        "module_files": [
            {{
                "filename": "module_name.py",
                "content": "Complete module content",
                "description": "Description of the module"
            }}
        ],
        "configuration_files": [
            {{
                "filename": "config.py",
                "content": "Configuration file content",
                "description": "Description of configuration"
            }}
        ],
        "test_files": [
            {{
                "filename": "test_module.py",
                "content": "Test file content",
                "description": "Description of tests"
            }}
        ],
        "documentation": [
            {{
                "filename": "README.md",
                "content": "Documentation content",
                "description": "Description of documentation"
            }}
        ],
        "dependencies": [
            "List of required dependencies and versions"
        ],
        "setup_instructions": "Step-by-step setup and installation instructions"
    }}
}}""",
                input_variables=["project_context", "project_type", "project_complexity", "requirements", "architecture"]
            )
            
            chain = prompt | self.llm | parser
            
            try:
                result = chain.invoke({
                    "project_context": state.get("project_context", ""),
                    "project_type": state.get("project_type", "general"),
                    "project_complexity": state.get("project_complexity", "medium"),
                    "requirements": str(state.get("requirements", {})),
                    "architecture": str(state.get("architecture", {}))
                })
                
                # Validate result
                if result is None:
                    raise ValueError("LLM returned None result")
                    
                self.logger.info(f"Code generator LLM result type: {type(result)}")
                self.logger.info(f"Code generator LLM result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
            except Exception as e:
                self.logger.error(f"Code generator LLM call failed: {e}")
                raise
            
            # Update completed agents
            completed_agents = state.get("completed_agents", [])
            completed_agents.append("code_generator")
            
            # Extract generated code and organize into proper file structure
            generated_code = result.get("generated_code", {})
            
            # Extract different file types
            code_files = {}
            test_files = {}
            documentation_files = {}
            configuration_files = {}
            
            # Process main files
            for file_data in generated_code.get("main_files", []):
                filename = file_data.get("filename", "main.py")
                content = file_data.get("content", "")
                code_files[filename] = content
            
            # Process module files
            for file_data in generated_code.get("module_files", []):
                filename = file_data.get("filename", "module.py")
                content = file_data.get("content", "")
                code_files[filename] = content
            
            # Process test files
            test_files_raw = generated_code.get("test_files", [])
            print(f"DEBUG: Found {len(test_files_raw)} test files in generated code")
            for file_data in test_files_raw:
                filename = file_data.get("filename", "test.py")
                content = file_data.get("content", "")
                test_files[filename] = content
                print(f"DEBUG: Extracted test file: {filename} with {len(content)} characters")
            
            # Process documentation files
            for file_data in generated_code.get("documentation", []):
                filename = file_data.get("filename", "README.md")
                content = file_data.get("content", "")
                documentation_files[filename] = content
            
            # Process configuration files
            for file_data in generated_code.get("configuration_files", []):
                filename = file_data.get("filename", "config.py")
                content = file_data.get("content", "")
                configuration_files[filename] = content
            
            # Debug logging
            print(f"DEBUG: Code generator extraction results:")
            print(f"DEBUG:   Code files: {len(code_files)}")
            print(f"DEBUG:   Test files: {len(test_files)}")
            print(f"DEBUG:   Documentation files: {len(documentation_files)}")
            print(f"DEBUG:   Configuration files: {len(configuration_files)}")
            
            return {
                **state,
                "code_files": code_files,
                "tests": test_files,
                "documentation": documentation_files,
                "configuration_files": configuration_files,
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    "code_generator": result
                },
                "completed_agents": completed_agents,
                "current_step": "code_generation",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "code_generation",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return {
                **state,
                "errors": [*state.get("errors", []), f"Code generation failed: {str(e)}"],
                "current_step": "code_generation",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "code_generation",
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "error": str(e)
                    }
                ]
            }
    
    def _test_generator_node(self, state: AgentState) -> AgentState:
        """Test generation node using standard LangChain patterns."""
        try:
            parser = JsonOutputParser()
            
            prompt = PromptTemplate(
                template="""You are an expert Test Engineer. Generate comprehensive tests for the generated code.

CRITICAL OUTPUT FORMAT REQUIREMENTS:
Return ONLY a JSON object with this EXACT structure:
{{
    "test_files": {{
        "test_filename.py": "complete test file content as string",
        "test_another.py": "complete test file content as string"
    }}
}}

CONSTRAINTS:
- NO nested objects, arrays, or complex structures
- NO metadata, descriptions, or test_cases arrays
- NO test_type or other fields
- Each value must be a complete, runnable Python test file as a string
- Use descriptive filenames based on the code being tested
- Include proper imports, test functions, and assertions

PROJECT CONTEXT:
{project_context}

PROJECT TYPE: {project_type}
PROJECT COMPLEXITY: {project_complexity}

REQUIREMENTS:
{requirements}

CODE FILES:
{code_files}

TASK:
Generate comprehensive tests that cover all functionality and edge cases.

Return the exact JSON structure above with no additional fields or nested structures. Each test file should be a complete, runnable Python test file with proper imports, test functions, and assertions.""",
                input_variables=["project_context", "project_type", "project_complexity", "requirements", "code_files"]
            )
            
            chain = prompt | self.llm | parser
            
            result = chain.invoke({
                "project_context": state.get("project_context", ""),
                "project_type": state.get("project_type", "general"),
                "project_complexity": state.get("project_complexity", "medium"),
                "requirements": str(state.get("requirements", {})),
                "code_files": str(state.get("code_files", {}))
            })
            
            # Update completed agents
            completed_agents = state.get("completed_agents", [])
            completed_agents.append("test_generator")
            
            # Get test files directly from the result (now flattened)
            test_files = result.get("test_files", {})
            
            # Debug: Print the test files result
            print(f"DEBUG: Test generator result keys: {list(result.keys())}")
            print(f"DEBUG: Test files type: {type(test_files)}")
            print(f"DEBUG: Test files count: {len(test_files)}")
            print(f"DEBUG: Test files keys: {list(test_files.keys())}")
            
            # Debug: Check state before and after update
            print(f"DEBUG: State test_files before update: {len(state.get('test_files', {}))}")
            updated_state = {
                **state,
                "test_files": test_files,
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    "test_generator": result
                },
                "completed_agents": completed_agents,
                "current_step": "test_generation",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "test_generation",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    }
                ]
            }
            print(f"DEBUG: State test_files after update: {len(updated_state.get('test_files', {}))}")
            
            return updated_state
            
        except Exception as e:
            self.logger.error(f"Test generation failed: {e}")
            return {
                **state,
                "errors": [*state.get("errors", []), f"Test generation failed: {str(e)}"],
                "current_step": "test_generation",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "test_generation",
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "error": str(e)
                    }
                ]
            }
    
    def _code_reviewer_node(self, state: AgentState) -> AgentState:
        """Code review node using standard LangChain patterns."""
        try:
            parser = JsonOutputParser()
            
            prompt = PromptTemplate(
                template="""You are an expert Code Reviewer. Review the generated code for quality, best practices, and potential issues.

PROJECT CONTEXT:
{project_context}

PROJECT TYPE: {project_type}
PROJECT COMPLEXITY: {project_complexity}

CODE FILES:
{code_files}

TEST FILES:
{test_files}

TASK:
Review the code and tests for quality, best practices, and potential issues.

Return your response as a valid JSON object with the following structure:
{{
    "code_review": {{
        "overall_assessment": {{
            "quality_score": "Score from 1-10",
            "readiness": "production_ready|needs_improvement|not_ready",
            "summary": "Overall assessment summary"
        }},
        "code_quality": [
            {{
                "file": "filename.py",
                "issues": [
                    {{
                        "type": "bug|warning|suggestion|best_practice",
                        "severity": "high|medium|low",
                        "description": "Description of the issue",
                        "line": "Line number or section",
                        "suggestion": "How to fix or improve"
                    }}
                ],
                "strengths": [
                    "List of positive aspects of the code"
                ]
            }}
        ],
        "test_quality": [
            {{
                "file": "test_filename.py",
                "coverage": "Coverage assessment",
                "issues": [
                    {{
                        "type": "coverage|quality|best_practice",
                        "description": "Description of test issue",
                        "suggestion": "How to improve tests"
                    }}
                ],
                "strengths": [
                    "List of positive aspects of the tests"
                ]
            }}
        ],
        "security_analysis": [
            {{
                "issue": "Security concern description",
                "severity": "critical|high|medium|low",
                "impact": "Potential impact description",
                "recommendation": "How to address the security issue"
            }}
        ],
        "performance_analysis": [
            {{
                "concern": "Performance concern description",
                "impact": "Performance impact assessment",
                "recommendation": "How to optimize performance"
            }}
        ],
        "recommendations": [
            "List of specific recommendations for improvement"
        ],
        "approval_status": "approved|approved_with_changes|needs_revision|rejected"
    }}
}}""",
                input_variables=["project_context", "project_type", "project_complexity", "code_files", "test_files"]
            )
            
            chain = prompt | self.llm | parser
            
            result = chain.invoke({
                "project_context": state.get("project_context", ""),
                "project_type": state.get("project_type", "general"),
                "project_complexity": state.get("project_complexity", "medium"),
                "code_files": str(state.get("code_files", {})),
                "test_files": str(state.get("test_files", {}))
            })
            
            # Update completed agents
            completed_agents = state.get("completed_agents", [])
            completed_agents.append("code_reviewer")
            
            return {
                **state,
                "review_results": result.get("review_results", {}),
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    "code_reviewer": result
                },
                "completed_agents": completed_agents,
                "current_step": "code_review",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "code_review",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Code review failed: {e}")
            return {
                **state,
                "errors": [*state.get("errors", []), f"Code review failed: {str(e)}"],
                "current_step": "code_review",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "code_review",
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "error": str(e)
                    }
                ]
            }
    
    def _security_analyst_node(self, state: AgentState) -> AgentState:
        """Security analysis node using standard LangChain patterns."""
        try:
            parser = JsonOutputParser()
            
            prompt = PromptTemplate(
                template="""You are an expert Security Analyst. Analyze the code for security vulnerabilities and best practices.

PROJECT CONTEXT:
{project_context}

PROJECT TYPE: {project_type}
PROJECT COMPLEXITY: {project_complexity}

CODE FILES:
{code_files}

REVIEW RESULTS:
{review_results}

TASK:
Analyze the code for security vulnerabilities and provide security recommendations.

Return your response as a valid JSON object with the following structure:
{{
    "security_analysis": {{
        "overall_security_score": "Score from 1-10",
        "security_status": "secure|needs_improvement|vulnerable|critical",
        "summary": "Overall security assessment summary",
        "vulnerabilities": [
            {{
                "type": "authentication|authorization|input_validation|data_exposure|injection|other",
                "severity": "critical|high|medium|low",
                "description": "Detailed description of the vulnerability",
                "file": "filename.py",
                "line": "Line number or section",
                "impact": "Potential impact of the vulnerability",
                "recommendation": "How to fix the vulnerability",
                "cwe_id": "Common Weakness Enumeration ID if applicable"
            }}
        ],
        "security_strengths": [
            "List of security best practices already implemented"
        ],
        "authentication_analysis": [
            {{
                "aspect": "Authentication method or mechanism",
                "assessment": "secure|weak|missing",
                "description": "Description of authentication analysis",
                "recommendation": "How to improve authentication"
            }}
        ],
        "authorization_analysis": [
            {{
                "aspect": "Authorization mechanism or check",
                "assessment": "secure|weak|missing",
                "description": "Description of authorization analysis",
                "recommendation": "How to improve authorization"
            }}
        ],
        "data_protection_analysis": [
            {{
                "aspect": "Data protection mechanism",
                "assessment": "secure|weak|missing",
                "description": "Description of data protection analysis",
                "recommendation": "How to improve data protection"
            }}
        ],
        "input_validation_analysis": [
            {{
                "aspect": "Input validation mechanism",
                "assessment": "secure|weak|missing",
                "description": "Description of input validation analysis",
                "recommendation": "How to improve input validation"
            }}
        ],
        "security_recommendations": [
            "List of specific security recommendations for improvement"
        ],
        "compliance_assessment": [
            {{
                "standard": "Security standard or framework",
                "compliance": "compliant|partially_compliant|non_compliant",
                "gaps": ["List of compliance gaps"],
                "recommendations": ["How to achieve compliance"]
            }}
        ],
        "security_testing_recommendations": [
            "List of security testing approaches and tools to use"
        ]
    }}
}}""",
                input_variables=["project_context", "project_type", "project_complexity", "code_files", "review_results"]
            )
            
            chain = prompt | self.llm | parser
            
            result = chain.invoke({
                "project_context": state.get("project_context", ""),
                "project_type": state.get("project_type", "general"),
                "project_complexity": state.get("project_complexity", "medium"),
                "code_files": str(state.get("code_files", {})),
                "review_results": str(state.get("review_results", {}))
            })
            
            # Update completed agents
            completed_agents = state.get("completed_agents", [])
            completed_agents.append("security_analyst")
            
            return {
                **state,
                "security_analysis": result.get("security_analysis", {}),
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    "security_analyst": result
                },
                "completed_agents": completed_agents,
                "current_step": "security_analysis",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "security_analysis",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Security analysis failed: {e}")
            return {
                **state,
                "errors": [*state.get("errors", []), f"Security analysis failed: {str(e)}"],
                "current_step": "security_analysis",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "security_analysis",
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "error": str(e)
                    }
                ]
            }
    
    def _documentation_generator_node(self, state: AgentState) -> AgentState:
        """Documentation generation node using standard LangChain patterns."""
        try:
            parser = JsonOutputParser()
            
            prompt = PromptTemplate(
                template="""You are an expert Technical Writer. Generate comprehensive documentation for the project.

PROJECT CONTEXT:
{project_context}

PROJECT TYPE: {project_type}
PROJECT COMPLEXITY: {project_complexity}

REQUIREMENTS:
{requirements}

ARCHITECTURE:
{architecture}

CODE FILES:
{code_files}

TEST FILES:
{test_files}

REVIEW RESULTS:
{review_results}

SECURITY ANALYSIS:
{security_analysis}

TASK:
Generate comprehensive documentation including user guides, API documentation, and technical specifications.

Return your response as a valid JSON object with the following structure:
{{
    "documentation": {{
        "project_overview": {{
            "filename": "README.md",
            "content": "Complete project overview and introduction",
            "sections": ["Installation", "Usage", "Features", "Contributing"]
        }},
        "user_guides": [
            {{
                "filename": "USER_GUIDE.md",
                "content": "Complete user guide content",
                "description": "Description of the user guide",
                "sections": ["Getting Started", "Basic Usage", "Advanced Features", "Troubleshooting"]
            }}
        ],
        "api_documentation": [
            {{
                "filename": "API_DOCS.md",
                "content": "Complete API documentation content",
                "description": "Description of the API documentation",
                "endpoints": [
                    {{
                        "name": "Endpoint name",
                        "method": "GET|POST|PUT|DELETE",
                        "description": "Endpoint description",
                        "parameters": ["List of parameters"],
                        "response": "Response format description"
                    }}
                ]
            }}
        ],
        "technical_specifications": [
            {{
                "filename": "TECHNICAL_SPEC.md",
                "content": "Complete technical specification content",
                "description": "Description of technical specifications",
                "sections": ["Architecture", "Data Models", "Security", "Performance"]
            }}
        ],
        "installation_guide": {{
            "filename": "INSTALLATION.md",
            "content": "Complete installation guide content",
            "description": "Step-by-step installation instructions",
            "prerequisites": ["List of prerequisites"],
            "steps": ["List of installation steps"]
        }},
        "deployment_guide": {{
            "filename": "DEPLOYMENT.md",
            "content": "Complete deployment guide content",
            "description": "Deployment instructions and configuration",
            "environments": ["Development", "Staging", "Production"],
            "configuration": "Configuration details"
        }},
        "troubleshooting_guide": {{
            "filename": "TROUBLESHOOTING.md",
            "content": "Complete troubleshooting guide content",
            "description": "Common issues and solutions",
            "common_issues": [
                {{
                    "issue": "Common issue description",
                    "symptoms": "How to identify the issue",
                    "solution": "How to resolve the issue",
                    "prevention": "How to prevent the issue"
                }}
            ]
        }},
        "developer_documentation": {{
            "filename": "DEVELOPER_GUIDE.md",
            "content": "Complete developer guide content",
            "description": "Documentation for developers",
            "sections": ["Setup", "Architecture", "Contributing", "Testing"]
        }}
    }}
}}""",
                input_variables=["project_context", "project_type", "project_complexity", "requirements", "architecture", "code_files", "test_files", "review_results", "security_analysis"]
            )
            
            chain = prompt | self.llm | parser
            
            result = chain.invoke({
                "project_context": state.get("project_context", ""),
                "project_type": state.get("project_type", "general"),
                "project_complexity": state.get("project_complexity", "medium"),
                "requirements": str(state.get("requirements", {})),
                "architecture": str(state.get("architecture", {})),
                "code_files": str(state.get("code_files", {})),
                "test_files": str(state.get("test_files", {})),
                "review_results": str(state.get("review_results", {})),
                "security_analysis": str(state.get("security_analysis", {}))
            })
            
            # Update completed agents
            completed_agents = state.get("completed_agents", [])
            completed_agents.append("documentation_generator")
            
            return {
                **state,
                "documentation": result.get("documentation", {}),
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    "documentation_generator": result
                },
                "completed_agents": completed_agents,
                "current_step": "documentation_generation",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "documentation_generation",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Documentation generation failed: {e}")
            return {
                **state,
                "errors": [*state.get("errors", []), f"Documentation generation failed: {str(e)}"],
                "current_step": "documentation_generation",
                "execution_history": [
                    *state.get("execution_history", []),
                    {
                        "step": "documentation_generation",
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "error": str(e)
                    }
                ]
            }
    
    async def execute_workflow(self, project_context: str, session_id: str = None) -> Dict[str, Any]:
        """
        Execute the complete workflow using standard LangGraph patterns.
        
        Args:
            project_context: The project context and requirements
            session_id: Optional session ID for persistence
            
        Returns:
            Final workflow state
        """
        try:
            # Initialize state following LangGraph patterns
            initial_state = AgentState(
                messages=[],
                current_step="start",
                project_context=project_context,
                project_type="general",
                project_complexity="medium",
                requirements={},
                architecture={},
                code_files={},
                test_files={},
                review_results={},
                security_analysis={},
                documentation={},
                agent_outputs={},
                errors=[],
                execution_history=[],
                memory={},
                recall_memories=[],
                required_agents=[],
                completed_agents=[],
                next_agent=None,
                workflow_complete=False
            )
            
            # Execute workflow using LangGraph patterns
            config = {}
            if session_id:
                config = {
                    "configurable": {
                        "thread_id": session_id,
                        "checkpoint_id": session_id
                    }
                }
            
            result_state = await self.workflow.ainvoke(initial_state, config=config)
            
            return result_state
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise


# Example usage
if __name__ == "__main__":
    # Example configuration
    llm_config = {
        "api_key": "your-gemini-api-key",
        "model_name": "gemini-2.5-flash-lite",
        "temperature": 0.1,
        "max_tokens": 8192
    }
    
    # Create workflow manager
    workflow_manager = LangGraphWorkflowManager(llm_config)
    
    # Example project contexts
    simple_project = "Create a simple calculator script"
    complex_project = "Build a full-stack web application with user authentication, database, and API endpoints"
    
    # Execute workflow
    result = asyncio.run(workflow_manager.execute_workflow(simple_project))
    print("Workflow completed:", result)
