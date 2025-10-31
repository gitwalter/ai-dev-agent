#!/usr/bin/env python3
"""
LangGraph Workflow Manager for AI Development Agent.
Test-driven implementation using established libraries.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
try:
    from typing_extensions import TypedDict  # Python < 3.12 compatibility
except ImportError:
    from typing import TypedDict  # Python >= 3.12
from datetime import datetime
import re

try:
    from langgraph.graph import StateGraph, END, START
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.output_parsers import PydanticOutputParser
    from langchain_core.prompts import PromptTemplate
    from pydantic import BaseModel, Field
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    logging.warning(f"LangGraph not available: {e}, using fallback")
    # Provide fallback imports to prevent NameError
    ChatGoogleGenerativeAI = None
    StateGraph = None
    END = None
    START = None
    MemorySaver = None
    PydanticOutputParser = None
    PromptTemplate = None

from utils.core.structured_outputs import (
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
                # Use JSON Output Parser instead of PydanticOutputParser
                json_parser = JsonOutputParser()
                
                # Create prompt template
                prompt = PromptTemplate(
                    template="""You are an expert Requirements Analyst. Analyze the project context and extract comprehensive requirements.

PROJECT CONTEXT:
{project_context}

TASK:
Analyze the project context above and generate a comprehensive requirements analysis.

IMPORTANT: Respond ONLY with a valid JSON object in the following format:
{{
    "functional_requirements": [
        {{
            "id": "REQ-001",
            "title": "Requirement Title",
            "description": "Detailed description",
            "priority": "high|medium|low",
            "type": "functional|non-functional"
        }}
    ],
    "non_functional_requirements": [
        {{
            "id": "NFR-001",
            "title": "Non-functional requirement",
            "description": "Description",
            "category": "performance|security|usability|reliability"
        }}
    ],
    "user_stories": [
        {{
            "id": "US-001",
            "title": "User Story Title",
            "description": "As a [user], I want [feature] so that [benefit]",
            "acceptance_criteria": ["Criterion 1", "Criterion 2"]
        }}
    ],
    "technical_constraints": ["Constraint 1", "Constraint 2"],
    "assumptions": ["Assumption 1", "Assumption 2"],
    "risks": ["Risk 1", "Risk 2"],
    "summary": "Overall requirements summary"
}}

Do not include any text before or after the JSON object.""",
                    input_variables=["project_context"]
                )
                
                # Create the chain
                chain = prompt | self.llm | json_parser
                
                # Execute the chain
                result = await chain.ainvoke({"project_context": state["project_context"]})
                
                # Update state
                return {
                    **state,
                    "requirements": result.get("functional_requirements", []),
                    "agent_outputs": {
                        **state["agent_outputs"],
                        "requirements_analyst": result
                    },
                    "current_step": "requirements_analysis",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "requirements_analysis",
                            "timestamp": datetime.now().isoformat(),
                            "status": "completed",
                             "output": result
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
                # Use JSON Output Parser instead of PydanticOutputParser
                json_parser = JsonOutputParser()
                
                prompt = PromptTemplate(
                    template="""You are an expert Software Architect. Design the system architecture based on the requirements.

PROJECT CONTEXT:
{project_context}

REQUIREMENTS:
{requirements}

TASK:
Design a comprehensive system architecture that meets the requirements.

IMPORTANT: Respond ONLY with a valid JSON object in the following format:
{{
    "system_overview": "High-level system description",
    "architecture_pattern": "MVC|Microservices|Event-Driven|etc",
    "technology_stack": {{
        "frontend": ["React", "Vue", "Angular"],
        "backend": ["Node.js", "Python", "Java"],
        "database": ["PostgreSQL", "MongoDB", "Redis"],
        "infrastructure": ["AWS", "Azure", "GCP"]
    }},
    "components": [
        {{
            "name": "Component Name",
            "description": "Component description",
            "responsibilities": ["Responsibility 1", "Responsibility 2"]
        }}
    ],
    "data_flow": "Description of data flow between components",
    "security_considerations": ["Security measure 1", "Security measure 2"],
    "scalability_considerations": ["Scalability approach 1", "Scalability approach 2"],
    "performance_considerations": ["Performance optimization 1", "Performance optimization 2"],
    "deployment_strategy": "Deployment approach description",
    "risk_mitigation": ["Risk 1 and mitigation", "Risk 2 and mitigation"],
    "database_schema": {{
        "tables": ["Table 1", "Table 2"],
        "relationships": "Description of relationships"
    }},
    "api_design": {{
        "endpoints": ["/api/v1/resource1", "/api/v1/resource2"],
        "authentication": "Authentication method",
        "rate_limiting": "Rate limiting strategy"
    }}
}}

Do not include any text before or after the JSON object.""",
                    input_variables=["project_context", "requirements"]
                )
                
                chain = prompt | self.llm | json_parser
                
                result = await chain.ainvoke({
                    "project_context": state["project_context"],
                    "requirements": str(state["requirements"])
                })
                
                return {
                    **state,
                    "architecture": result,
                    "agent_outputs": {
                        **state["agent_outputs"],
                        "architecture_designer": result
                    },
                    "current_step": "architecture_design",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "architecture_design",
                            "timestamp": datetime.now().isoformat(),
                            "status": "completed",
                             "output": result
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
                # Use StrOutputParser for markdown with code blocks
                output_parser = StrOutputParser()
                
                prompt = PromptTemplate(
                    template="""You are an expert Software Developer. Generate production-ready code based on the requirements and architecture.

PROJECT CONTEXT: {project_context}
REQUIREMENTS: {requirements}
ARCHITECTURE: {architecture}

Generate the complete source code in markdown format with code blocks. For each file, use this format:

## File: filename.py
```python
# code content here
```

## File: requirements.txt
```txt
# dependencies here
```

## File: README.md
```markdown
# documentation here
```

Include all necessary files for a complete, working application. Make sure the code is production-ready with proper error handling, documentation, and follows best practices.

Return ONLY the markdown with code blocks, no additional text.""",
                    input_variables=["project_context", "requirements", "architecture"]
                )
                
                chain = prompt | self.llm | output_parser
                
                result = await chain.ainvoke({
                    "project_context": state["project_context"],
                    "requirements": str(state["requirements"]),
                    "architecture": str(state["architecture"])
                })
                
                # Parse the markdown result to extract code files
                source_files = self.parse_markdown_code_blocks(result)
                
                return {
                    **state,
                    "code_files": source_files,  # FIXED: Store files directly in code_files
                    "agent_outputs": {
                        **state["agent_outputs"],
                        "code_generator": {
                            "source_files": source_files,
                            "raw_markdown": result
                        }
                    },
                    "current_step": "code_generation",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "code_generation",
                            "timestamp": datetime.now().isoformat(),
                            "status": "completed",
                            "files_generated": len(source_files),
                            "file_names": list(source_files.keys())
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
    
    def parse_markdown_code_blocks(self, markdown_text: str) -> Dict[str, str]:
            """
            Parse markdown text and extract code blocks as source files.
            
            Args:
                markdown_text: The markdown text containing code blocks
                
            Returns:
                Dictionary mapping filename to file content
            """
            source_files = {}
            
            # Pattern to match markdown code blocks with file headers
            # Matches: ## File: filename.py\n```python\ncontent\n```
            pattern = r'##\s*File:\s*([^\n]+)\s*\n```(?:[a-zA-Z]+)?\s*\n(.*?)\n```'
            
            matches = re.findall(pattern, markdown_text, re.DOTALL)
            
            for filename, content in matches:
                # Clean up the filename and content
                filename = filename.strip()
                content = content.strip()
                
                if filename and content:
                    source_files[filename] = content
            
            # If no structured format found, try to extract any code blocks
            if not source_files:
                # Fallback: extract any code blocks and assign default names
                code_block_pattern = r'```(?:[a-zA-Z]+)?\s*\n(.*?)\n```'
                code_blocks = re.findall(code_block_pattern, markdown_text, re.DOTALL)
                
                for i, content in enumerate(code_blocks):
                    content = content.strip()
                    if content:
                        # Try to determine file type from content or use default
                        if 'def ' in content or 'import ' in content:
                            filename = f"file_{i+1}.py"
                        elif 'requirements' in content.lower() or '==' in content:
                            filename = f"requirements_{i+1}.txt"
                        else:
                            filename = f"file_{i+1}.txt"
                        
                        source_files[filename] = content
            
            return source_files
    
    def create_test_generator_node(self) -> Callable[[AgentState], AgentState]:
        """Create a test generation node."""
        async def test_generator_node(state: AgentState) -> AgentState:
            try:
                # Use JSON Output Parser instead of PydanticOutputParser
                json_parser = JsonOutputParser()
                
                prompt = PromptTemplate(
                    template="""You are an expert Test Engineer. Generate comprehensive tests based on the code and requirements.

PROJECT CONTEXT: {project_context}
REQUIREMENTS: {requirements}
CODE FILES: {code_files}

IMPORTANT: Respond ONLY with a valid JSON object. Do not include any other text or explanations.

Generate tests and return them in this exact JSON format:
{{
    "test_files": {{
        "test_filename.py": {{
            "filename": "test_filename.py",
            "content": "Actual test code content",
            "test_type": "unit|integration|e2e",
            "coverage_target": "Target coverage percentage",
            "dependencies": ["pytest", "other dependencies"]
        }}
    }},
    "test_strategy": {{
        "unit_testing": "Unit testing approach and framework",
        "integration_testing": "Integration testing approach",
        "test_data": "Test data management strategy",
        "coverage_goals": "Test coverage goals and metrics"
    }},
    "test_scenarios": [
        {{
            "id": "SCENARIO-001",
            "description": "Test scenario description",
            "test_cases": ["Test case 1", "Test case 2"],
            "expected_outcomes": ["Expected outcome 1", "Expected outcome 2"]
        }}
    ],
    "test_environment": {{
        "setup_instructions": ["Step 1", "Step 2"],
        "dependencies": ["List of test dependencies"],
        "configuration": "Test environment configuration"
    }}
}}

Return ONLY the JSON object.""",
                    input_variables=["project_context", "requirements", "code_files"]
                )
                
                chain = prompt | self.llm | json_parser
                
                result = await chain.ainvoke({
                    "project_context": state["project_context"],
                    "requirements": str(state["requirements"]),
                    "code_files": str(state["code_files"])
                })
                
                return {
                    **state,
                    "tests": result.get("test_files", {}),
                    "agent_outputs": {
                        **state["agent_outputs"],
                        "test_generator": result
                    },
                    "current_step": "test_generation",
                    "execution_history": [
                        *state["execution_history"],
                        {
                            "step": "test_generation",
                            "timestamp": datetime.now().isoformat(),
                            "status": "completed",
                            "output": result
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
            # Use environment variable directly (like working project)
            import os
            return ChatGoogleGenerativeAI(
                model=self.llm_config.get("model_name", "gemini-2.5-flash"),
                google_api_key=os.environ.get("GEMINI_API_KEY"),  # Direct env access
                temperature=self.llm_config.get("temperature", 0),
                convert_system_message_to_human=True,  # Required for Gemini
                max_retries=5,  # Retry on API errors
                timeout=120  # 2 minute timeout
            )
        except Exception as e:
            self.logger.error(f"Failed to setup LLM: {e}")
            raise
    
    def _initialize_state_node(self, state: dict) -> AgentState:
        """Initialize state with default values for all required fields."""
        import uuid
        
        self.logger.info(f"📝 Initializing state with project_context: {state.get('project_context', 'NOT_PROVIDED')}")
        
        return {
            "project_context": state.get("project_context", ""),
            "project_name": state.get("project_name", "unnamed_project"),
            "session_id": state.get("session_id", str(uuid.uuid4())),
            "requirements": state.get("requirements", []),
            "architecture": state.get("architecture", {}),
            "code_files": state.get("code_files", {}),
            "tests": state.get("tests", {}),
            "documentation": state.get("documentation", {}),
            "diagrams": state.get("diagrams", {}),
            "agent_outputs": state.get("agent_outputs", {}),
            "errors": state.get("errors", []),
            "warnings": state.get("warnings", []),
            "approval_requests": state.get("approval_requests", []),
            "current_step": state.get("current_step", "initialization"),
            "execution_history": state.get("execution_history", [])
        }
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add initialization node to ensure all state fields have default values
        workflow.add_node("initialize", self._initialize_state_node)
        
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
        
        # Define the main workflow edges - START with initialization
        workflow.add_edge(START, "initialize")
        workflow.add_edge("initialize", "requirements_analysis")
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
        
        # Compile the workflow (Studio handles persistence)
        return workflow.compile()
    
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


# Export for LangGraph Studio
_default_instance = None

def get_graph():
    """Get the compiled graph for LangGraph Studio."""
    global _default_instance
    if _default_instance is None:
        # LLM will read GEMINI_API_KEY directly from OS environment
        llm_config = {
            "model_name": "gemini-2.5-flash",
            "temperature": 0,
            "max_tokens": 8192
        }
        
        try:
            _default_instance = LangGraphWorkflowManager(llm_config)
            logging.getLogger(__name__).info("✅ Alternative workflow graph compiled for Studio")
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to create workflow graph: {e}")
            return None
    
    return _default_instance.workflow if _default_instance else None

# Studio expects 'graph' variable
graph = get_graph()


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
