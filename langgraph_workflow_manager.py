#!/usr/bin/env python3
"""
LangGraph Workflow Manager for AI Development Agent.
Test-driven implementation using established libraries.
"""

import asyncio
import logging
from typing import Dict, Any, List, TypedDict, Optional, Callable
from datetime import datetime

try:
    from langgraph.graph import StateGraph, END, START
    from langgraph.checkpoint.memory import MemorySaver
    from langchain.output_parsers import PydanticOutputParser
    from langchain.prompts import PromptTemplate
    from langchain.schema.runnable import RunnablePassthrough
    from langchain_google_genai import ChatGoogleGenerativeAI
    from pydantic import BaseModel, Field
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available, using fallback")

from utils.structured_outputs import (
    RequirementsAnalysisOutput, ArchitectureDesignOutput, CodeGenerationOutput,
    TestGenerationOutput, CodeReviewOutput, SecurityAnalysisOutput, DocumentationGenerationOutput
)

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """LangGraph state definition for agent workflow."""
    project_context: str
    project_name: str
    session_id: str
    requirements: List[Dict[str, Any]]
    architecture: Dict[str, Any]
    code_files: Dict[str, Any]
    tests: Dict[str, Any]
    documentation: Dict[str, Any]
    diagrams: Dict[str, Any]
    agent_outputs: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    approval_requests: List[Dict[str, Any]]
    current_step: str
    execution_history: List[Dict[str, Any]]


class AgentNodeFactory:
    """Factory for creating agent nodes with proper error handling and validation."""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """Initialize the agent node factory."""
        self.llm = llm
        self.logger = logging.getLogger(__name__)
    
    def create_requirements_node(self) -> Callable[[AgentState], AgentState]:
        """Create a requirements analysis node."""
        async def requirements_node(state: AgentState) -> AgentState:
            try:
                # Create parser for structured output
                parser = PydanticOutputParser(pydantic_object=RequirementsAnalysisOutput)
                
                # Create prompt template
                prompt = PromptTemplate(
                    template="""You are an expert Requirements Analyst. Analyze the project context and extract comprehensive requirements.

PROJECT CONTEXT:
{project_context}

TASK:
Analyze the project context above and generate a comprehensive requirements analysis.

{format_instructions}""",
                    input_variables=["project_context"],
                    partial_variables={"format_instructions": parser.get_format_instructions()}
                )
                
                # Create the chain
                chain = prompt | self.llm | parser
                
                # Execute the chain
                result = await chain.ainvoke({"project_context": state["project_context"]})
                
                # Update state
                return {
                    **state,
                    "requirements": result.functional_requirements,
                    "agent_outputs": {
                        **state["agent_outputs"],
                        "requirements_analyst": result.dict()
                    },
                    "current_step": "requirements_analysis",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "requirements_analysis",
                            "timestamp": datetime.now().isoformat(),
                            "status": "completed",
                            "output": result.dict()
                        }
                    ]
                }
                
            except Exception as e:
                self.logger.error(f"Requirements analysis failed: {e}")
                return {
                    **state,
                    "errors": [*state["errors"], f"Requirements analysis failed: {str(e)}"],
                    "current_step": "requirements_analysis",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "requirements_analysis",
                            "timestamp": datetime.now().isoformat(),
                            "status": "failed",
                            "error": str(e)
                        }
                    ]
                }
        
        return requirements_node
    
    def create_architecture_node(self) -> Callable[[AgentState], AgentState]:
        """Create an architecture design node."""
        async def architecture_node(state: AgentState) -> AgentState:
            try:
                parser = PydanticOutputParser(pydantic_object=ArchitectureDesignOutput)
                
                prompt = PromptTemplate(
                    template="""You are an expert Software Architect. Design the system architecture based on the requirements.

PROJECT CONTEXT:
{project_context}

REQUIREMENTS:
{requirements}

TASK:
Design a comprehensive system architecture that meets the requirements.

{format_instructions}""",
                    input_variables=["project_context", "requirements"],
                    partial_variables={"format_instructions": parser.get_format_instructions()}
                )
                
                chain = prompt | self.llm | parser
                
                result = await chain.ainvoke({
                    "project_context": state["project_context"],
                    "requirements": str(state["requirements"])
                })
                
                return {
                    **state,
                    "architecture": result.dict(),
                    "agent_outputs": {
                        **state["agent_outputs"],
                        "architecture_designer": result.dict()
                    },
                    "current_step": "architecture_design",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "architecture_design",
                            "timestamp": datetime.now().isoformat(),
                            "status": "completed",
                            "output": result.dict()
                        }
                    ]
                }
                
            except Exception as e:
                self.logger.error(f"Architecture design failed: {e}")
                return {
                    **state,
                    "errors": [*state["errors"], f"Architecture design failed: {str(e)}"],
                    "current_step": "architecture_design",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "architecture_design",
                            "timestamp": datetime.now().isoformat(),
                            "status": "failed",
                            "error": str(e)
                        }
                    ]
                }
        
        return architecture_node
    
    def create_code_generator_node(self) -> Callable[[AgentState], AgentState]:
        """Create a code generation node."""
        async def code_generator_node(state: AgentState) -> AgentState:
            try:
                parser = PydanticOutputParser(pydantic_object=CodeGenerationOutput)
                
                prompt = PromptTemplate(
                    template="""You are an expert Software Developer. Generate production-ready code based on the requirements and architecture.

PROJECT CONTEXT:
{project_context}

REQUIREMENTS:
{requirements}

ARCHITECTURE:
{architecture}

TASK:
Generate comprehensive, production-ready code that implements the requirements according to the architecture.

{format_instructions}""",
                    input_variables=["project_context", "requirements", "architecture"],
                    partial_variables={"format_instructions": parser.get_format_instructions()}
                )
                
                chain = prompt | self.llm | parser
                
                result = await chain.ainvoke({
                    "project_context": state["project_context"],
                    "requirements": str(state["requirements"]),
                    "architecture": str(state["architecture"])
                })
                
                return {
                    **state,
                    "code_files": result.source_files,
                    "agent_outputs": {
                        **state["agent_outputs"],
                        "code_generator": result.dict()
                    },
                    "current_step": "code_generation",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "code_generation",
                            "timestamp": datetime.now().isoformat(),
                            "status": "completed",
                            "output": result.dict()
                        }
                    ]
                }
                
            except Exception as e:
                self.logger.error(f"Code generation failed: {e}")
                return {
                    **state,
                    "errors": [*state["errors"], f"Code generation failed: {str(e)}"],
                    "current_step": "code_generation",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "code_generation",
                            "timestamp": datetime.now().isoformat(),
                            "status": "failed",
                            "error": str(e)
                        }
                    ]
                }
        
        return code_generator_node
    
    def create_test_generator_node(self) -> Callable[[AgentState], AgentState]:
        """Create a test generation node."""
        async def test_generator_node(state: AgentState) -> AgentState:
            try:
                parser = PydanticOutputParser(pydantic_object=TestGenerationOutput)
                
                prompt = PromptTemplate(
                    template="""You are an expert Test Engineer. Generate comprehensive tests based on the code and requirements.

PROJECT CONTEXT:
{project_context}

REQUIREMENTS:
{requirements}

CODE FILES:
{code_files}

TASK:
Generate comprehensive test files that cover the functionality of the code according to the requirements.

{format_instructions}""",
                    input_variables=["project_context", "requirements", "code_files"],
                    partial_variables={"format_instructions": parser.get_format_instructions()}
                )
                
                chain = prompt | self.llm | parser
                
                result = await chain.ainvoke({
                    "project_context": state["project_context"],
                    "requirements": str(state["requirements"]),
                    "code_files": str(state["code_files"])
                })
                
                return {
                    **state,
                    "tests": result.test_files,
                    "agent_outputs": {
                        **state["agent_outputs"],
                        "test_generator": result.dict()
                    },
                    "current_step": "test_generation",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "test_generation",
                            "timestamp": datetime.now().isoformat(),
                            "status": "completed",
                            "output": result.dict()
                        }
                    ]
                }
                
            except Exception as e:
                self.logger.error(f"Test generation failed: {e}")
                return {
                    **state,
                    "errors": [*state["errors"], f"Test generation failed: {str(e)}"],
                    "current_step": "test_generation",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "test_generation",
                            "timestamp": datetime.now().isoformat(),
                            "status": "failed",
                            "error": str(e)
                        }
                    ]
                }
        
        return test_generator_node
    
    def create_code_reviewer_node(self) -> Callable[[AgentState], AgentState]:
        """Create a code review node."""
        async def code_reviewer_node(state: AgentState) -> AgentState:
            try:
                parser = PydanticOutputParser(pydantic_object=CodeReviewOutput)
                
                prompt = PromptTemplate(
                    template="""You are an expert Code Reviewer. Review the generated code for quality, security, and best practices.

PROJECT CONTEXT:
{project_context}

CODE FILES:
{code_files}

TASK:
Perform a comprehensive code review, identifying issues, suggesting improvements, and ensuring code quality.

{format_instructions}""",
                    input_variables=["project_context", "code_files"],
                    partial_variables={"format_instructions": parser.get_format_instructions()}
                )
                
                chain = prompt | self.llm | parser
                
                result = await chain.ainvoke({
                    "project_context": state["project_context"],
                    "code_files": str(state["code_files"])
                })
                
                return {
                    **state,
                    "agent_outputs": {
                        **state["agent_outputs"],
                        "code_reviewer": result.dict()
                    },
                    "current_step": "code_review",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "code_review",
                            "timestamp": datetime.now().isoformat(),
                            "status": "completed",
                            "output": result.dict()
                        }
                    ]
                }
                
            except Exception as e:
                self.logger.error(f"Code review failed: {e}")
                return {
                    **state,
                    "errors": [*state["errors"], f"Code review failed: {str(e)}"],
                    "current_step": "code_review",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "code_review",
                            "timestamp": datetime.now().isoformat(),
                            "status": "failed",
                            "error": str(e)
                        }
                    ]
                }
        
        return code_reviewer_node
    
    def create_security_analyst_node(self) -> Callable[[AgentState], AgentState]:
        """Create a security analysis node."""
        async def security_analyst_node(state: AgentState) -> AgentState:
            try:
                parser = PydanticOutputParser(pydantic_object=SecurityAnalysisOutput)
                
                prompt = PromptTemplate(
                    template="""You are an expert Security Analyst. Analyze the code and architecture for security vulnerabilities.

PROJECT CONTEXT:
{project_context}

CODE FILES:
{code_files}

ARCHITECTURE:
{architecture}

TASK:
Perform a comprehensive security analysis, identifying vulnerabilities and providing security recommendations.

{format_instructions}""",
                    input_variables=["project_context", "code_files", "architecture"],
                    partial_variables={"format_instructions": parser.get_format_instructions()}
                )
                
                chain = prompt | self.llm | parser
                
                result = await chain.ainvoke({
                    "project_context": state["project_context"],
                    "code_files": str(state["code_files"]),
                    "architecture": str(state["architecture"])
                })
                
                return {
                    **state,
                    "agent_outputs": {
                        **state["agent_outputs"],
                        "security_analyst": result.dict()
                    },
                    "current_step": "security_analysis",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "security_analysis",
                            "timestamp": datetime.now().isoformat(),
                            "status": "completed",
                            "output": result.dict()
                        }
                    ]
                }
                
            except Exception as e:
                self.logger.error(f"Security analysis failed: {e}")
                return {
                    **state,
                    "errors": [*state["errors"], f"Security analysis failed: {str(e)}"],
                    "current_step": "security_analysis",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "security_analysis",
                            "timestamp": datetime.now().isoformat(),
                            "status": "failed",
                            "error": str(e)
                        }
                    ]
                }
        
        return security_analyst_node
    
    def create_documentation_generator_node(self) -> Callable[[AgentState], AgentState]:
        """Create a documentation generation node."""
        async def documentation_generator_node(state: AgentState) -> AgentState:
            try:
                parser = PydanticOutputParser(pydantic_object=DocumentationGenerationOutput)
                
                prompt = PromptTemplate(
                    template="""You are an expert Technical Writer. Generate comprehensive documentation based on the project.

PROJECT CONTEXT:
{project_context}

REQUIREMENTS:
{requirements}

CODE FILES:
{code_files}

TESTS:
{tests}

TASK:
Generate comprehensive documentation including README, API docs, and user guides.

{format_instructions}""",
                    input_variables=["project_context", "requirements", "code_files", "tests"],
                    partial_variables={"format_instructions": parser.get_format_instructions()}
                )
                
                chain = prompt | self.llm | parser
                
                result = await chain.ainvoke({
                    "project_context": state["project_context"],
                    "requirements": str(state["requirements"]),
                    "code_files": str(state["code_files"]),
                    "tests": str(state["tests"])
                })
                
                return {
                    **state,
                    "documentation": result.documentation_files,
                    "agent_outputs": {
                        **state["agent_outputs"],
                        "documentation_generator": result.dict()
                    },
                    "current_step": "documentation_generation",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "documentation_generation",
                            "timestamp": datetime.now().isoformat(),
                            "status": "completed",
                            "output": result.dict()
                        }
                    ]
                }
                
            except Exception as e:
                self.logger.error(f"Documentation generation failed: {e}")
                return {
                    **state,
                    "errors": [*state["errors"], f"Documentation generation failed: {str(e)}"],
                    "current_step": "documentation_generation",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "documentation_generation",
                            "timestamp": datetime.now().isoformat(),
                            "status": "failed",
                            "error": str(e)
                        }
                    ]
                }
        
        return documentation_generator_node


class LangGraphWorkflowManager:
    """
    LangGraph-based workflow manager for AI Development Agent.
    Test-driven implementation with comprehensive error handling.
    """
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the LangGraph workflow manager.
        
        Args:
            llm_config: Configuration for the LLM
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required for this workflow")
        
        self.llm_config = llm_config
        self.logger = logging.getLogger(__name__)
        self.llm = self._setup_llm()
        self.node_factory = AgentNodeFactory(self.llm)
        self.workflow = self._create_workflow()
        
    def _setup_llm(self) -> ChatGoogleGenerativeAI:
        """Setup the LLM for the workflow."""
        try:
            return ChatGoogleGenerativeAI(
                model=self.llm_config.get("model_name", "gemini-2.5-flash-lite"),
                temperature=self.llm_config.get("temperature", 0.1),
                max_output_tokens=self.llm_config.get("max_tokens", 8192),
                google_api_key=self.llm_config.get("api_key")
            )
        except Exception as e:
            self.logger.error(f"Failed to setup LLM: {e}")
            raise
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("requirements_analysis", self.node_factory.create_requirements_node())
        workflow.add_node("architecture_design", self.node_factory.create_architecture_node())
        workflow.add_node("code_generation", self.node_factory.create_code_generator_node())
        workflow.add_node("test_generation", self.node_factory.create_test_generator_node())
        workflow.add_node("code_review", self.node_factory.create_code_reviewer_node())
        workflow.add_node("security_analysis", self.node_factory.create_security_analyst_node())
        workflow.add_node("documentation_generation", self.node_factory.create_documentation_generator_node())
        
        # Add error handling nodes
        workflow.add_node("error_handler", self._error_handler_node)
        workflow.add_node("workflow_complete", self._workflow_complete_node)
        
        # Define the main workflow edges
        workflow.add_edge(START, "requirements_analysis")
        workflow.add_edge("requirements_analysis", "architecture_design")
        workflow.add_edge("architecture_design", "code_generation")
        workflow.add_edge("code_generation", "test_generation")
        workflow.add_edge("test_generation", "code_review")
        workflow.add_edge("code_review", "security_analysis")
        workflow.add_edge("security_analysis", "documentation_generation")
        workflow.add_edge("documentation_generation", "workflow_complete")
        
        # Add error handling edges
        workflow.add_edge("error_handler", END)
        workflow.add_edge("workflow_complete", END)
        
        # Compile the workflow
        return workflow.compile(checkpointer=MemorySaver())
    
    def _error_handler_node(self, state: AgentState) -> AgentState:
        """Error handling node."""
        self.logger.error(f"Workflow error at step {state.get('current_step', 'unknown')}")
        return {
            **state,
            "current_step": "error",
            "execution_history": [
                *state["execution_history"],
                {
                    "step": "error_handler",
                    "timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "errors": state.get("errors", [])
                }
            ]
        }
    
    def _workflow_complete_node(self, state: AgentState) -> AgentState:
        """Workflow completion node."""
        self.logger.info("Workflow completed successfully")
        return {
            **state,
            "current_step": "completed",
            "execution_history": [
                *state["execution_history"],
                {
                    "step": "workflow_complete",
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed"
                }
            ]
        }
    
    async def execute_workflow(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the LangGraph workflow.
        
        Args:
            initial_state: Initial workflow state
            
        Returns:
            Final workflow state
        """
        try:
            # Convert to AgentState format
            agent_state = AgentState(
                project_context=initial_state.get("project_context", ""),
                project_name=initial_state.get("project_name", ""),
                session_id=initial_state.get("session_id", ""),
                requirements=[],
                architecture={},
                code_files={},
                tests={},
                documentation={},
                diagrams={},
                agent_outputs={},
                errors=[],
                warnings=[],
                approval_requests=[],
                current_step="started",
                execution_history=[]
            )
            
            # Execute the workflow
            result = await self.workflow.ainvoke(agent_state)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return {
                **initial_state,
                "errors": [f"Workflow execution failed: {str(e)}"],
                "current_step": "failed"
            }


# Example usage and testing
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
    
    # Example initial state
    initial_state = {
        "project_context": "Create a simple task management system with user authentication",
        "project_name": "task-management-system",
        "session_id": "test-session-123"
    }
    
    # Execute workflow
    result = asyncio.run(workflow_manager.execute_workflow(initial_state))
    print("Workflow completed:", result)
