"""
Main entry point for the AI Development Agent system.
Orchestrates the entire development workflow using LangGraph and Gemini API.
"""

import asyncio
import logging
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import google.generativeai as genai

from models.config import SystemConfig, load_config_from_env, get_default_config
from models.state import create_initial_state
from models.responses import WorkflowResult, WorkflowStatus, AgentResponse, TaskStatus
from workflow.langgraph_workflow import LangGraphWorkflowManager
from context.context_engine import ContextEngine
from utils.core.logging_config import setup_logging
from utils.core.langchain_logging import setup_langchain_logging, get_logging_manager
from utils.core.file_manager import FileManager


class AIDevelopmentAgent:
    """
    Main orchestrator for the AI Development Agent system.
    
    Manages the entire development workflow from requirements analysis
    to final deployment, using specialized agents and LangGraph for
    workflow orchestration.
    """
    
    def __init__(self, config: SystemConfig):
        """
        Initialize the AI Development Agent system.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.logger = logging.getLogger("ai_dev_agent")
        
        # Initialize LangChain logging
        self.logging_manager = get_logging_manager("ai-dev-agent", enable_langsmith=True)
        
        # Initialize components
        self.gemini_client = self._initialize_gemini()
        self.context_engine = ContextEngine(config.context)
        self.file_manager = FileManager(config.storage)
        self.agents = self._initialize_agents()
        
        # Initialize LangGraph workflow manager
        llm_config = {
            "model_name": self.config.gemini.model_name,
            "temperature": self.config.gemini.temperature,
            "max_tokens": self.config.gemini.max_tokens
        }
        # Set GEMINI_API_KEY in environment for ChatGoogleGenerativeAI
        os.environ["GEMINI_API_KEY"] = self.config.gemini.api_key
        self.workflow_manager = LangGraphWorkflowManager(llm_config)
        
        self.logger.info("AI Development Agent system initialized successfully")
    
    def _initialize_gemini(self) -> genai.GenerativeModel:
        """
        Initialize the Gemini API client.
        
        Returns:
            Configured Gemini client
        """
        try:
            # Configure Gemini API
            genai.configure(api_key=self.config.gemini.api_key)
            
            # Create the model
            model = genai.GenerativeModel(
                model_name=self.config.gemini.model_name,
                generation_config={
                    "temperature": self.config.gemini.temperature,
                    "top_p": self.config.gemini.top_p,
                    "top_k": self.config.gemini.top_k,
                    "max_output_tokens": self.config.gemini.max_tokens,
                },
                safety_settings=self.config.gemini.safety_settings
            )
            
            self.logger.info(f"Gemini client initialized with model: {self.config.gemini.model_name}")
            return model
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """
        Initialize all specialized agents.
        
        Returns:
            Dictionary of initialized agents
        """
        agents = {}
        
        try:
            # Import agent classes
            from agents.development.requirements_analyst import RequirementsAnalyst
            from agents.development.architecture_designer import ArchitectureDesigner
            from agents.development.code_generator import CodeGenerator
            from agents.development.test_generator import TestGenerator
            from agents.development.code_reviewer import CodeReviewer
            from agents.security.security_analyst import SecurityAnalyst
            from agents.development.documentation_generator import DocumentationGenerator
            
            # Create agent configurations
            agent_configs = {
                "requirements_analyst": {
                    "name": "requirements_analyst",
                    "description": "Analyzes project requirements and creates detailed specifications",
                    "enabled": True,
                    "max_retries": 3,
                    "timeout": 300,
                    "prompt_template": "Analyze the project requirements: {project_context}",
                    "system_prompt": "You are a requirements analyst expert.",
                    "parameters": {"temperature": 0.1}
                },
                "architecture_designer": {
                    "name": "architecture_designer", 
                    "description": "Designs system architecture and technology stack",
                    "enabled": True,
                    "max_retries": 3,
                    "timeout": 300,
                    "prompt_template": "Design architecture for: {project_context}",
                    "system_prompt": "You are an architecture design expert.",
                    "parameters": {"temperature": 0.1}
                },
                "code_generator": {
                    "name": "code_generator",
                    "description": "Generates code based on requirements and architecture",
                    "enabled": True,
                    "max_retries": 3,
                    "timeout": 600,
                    "prompt_template": "Generate comprehensive, production-ready code for: {project_context} with architecture: {architecture} and tech stack: {tech_stack}. Include all necessary files, proper error handling, security measures, and documentation.",
                    "system_prompt": """You are an expert Software Developer with extensive experience in writing clean, maintainable, and production-ready code. 

CRITICAL REQUIREMENTS:
1. Generate COMPREHENSIVE, PRODUCTION-READY code - not simple examples
2. Include ALL necessary files (models, schemas, services, utilities, config, etc.)
3. Implement proper error handling, validation, and security measures
4. Use best practices for the chosen technology stack
5. Include proper documentation and comments
6. Generate working, runnable code that can be deployed immediately
7. Follow the exact JSON structure specified in the response format
8. Ensure all strings are properly escaped in JSON
9. Include comprehensive requirements.txt with specific versions
10. Generate proper project structure and deployment instructions

Your goal is to create a complete, professional-grade application that can be deployed to production immediately.""",
                    "parameters": {"temperature": 0.1}
                },
                "test_generator": {
                    "name": "test_generator",
                    "description": "Generates comprehensive tests for the codebase",
                    "enabled": True,
                    "max_retries": 3,
                    "timeout": 300,
                    "prompt_template": "Generate tests for: {code_files}",
                    "system_prompt": "You are a test generation expert.",
                    "parameters": {"temperature": 0.1}
                },
                "code_reviewer": {
                    "name": "code_reviewer",
                    "description": "Reviews code for quality and best practices",
                    "enabled": True,
                    "max_retries": 3,
                    "timeout": 300,
                    "prompt_template": "Review code: {code_files}",
                    "system_prompt": "You are a code review expert.",
                    "parameters": {"temperature": 0.1}
                },
                "security_analyst": {
                    "name": "security_analyst",
                    "description": "Analyzes code for security vulnerabilities",
                    "enabled": True,
                    "max_retries": 3,
                    "timeout": 300,
                    "prompt_template": "Analyze security for: {code_files}",
                    "system_prompt": "You are a security analysis expert.",
                    "parameters": {"temperature": 0.1}
                },
                "documentation_generator": {
                    "name": "documentation_generator",
                    "description": "Generates comprehensive documentation with UML and BPMN diagrams",
                    "enabled": True,
                    "max_retries": 3,
                    "timeout": 300,
                    "prompt_template": "Generate comprehensive documentation with diagrams for: {project_context}",
                    "system_prompt": """You are an expert Technical Writer and Software Architect specializing in creating comprehensive documentation with visual diagrams.

CRITICAL REQUIREMENTS:
1. Generate COMPREHENSIVE documentation covering all aspects of the project
2. Create UML diagrams (Class, Sequence, Activity, Use Case) using PlantUML syntax
3. Create BPMN diagrams for business processes using BPMN XML format
4. Use Mermaid syntax for flowcharts and simple diagrams
5. Ensure all diagrams are GitHub-compatible and can be rendered properly
6. Include detailed explanations for each diagram
7. Follow the exact JSON structure specified in the response format
8. Ensure all strings are properly escaped in JSON

DIAGRAM REQUIREMENTS:
- Class Diagrams: Show system entities, relationships, and methods
- Sequence Diagrams: Show interaction flows between components
- Activity Diagrams: Show process flows and decision points
- Use Case Diagrams: Show system functionality from user perspective
- BPMN Diagrams: Show business processes with proper BPMN elements
- Component Diagrams: Show system architecture and component relationships

DIAGRAM FORMATS:
- PlantUML: Use for UML diagrams (class, sequence, activity, use case)
- Mermaid: Use for flowcharts, state diagrams, and simple diagrams
- BPMN XML: Use for business process modeling

Your goal is to create professional, comprehensive documentation that includes clear visual representations of the system architecture and processes.""",
                    "parameters": {"temperature": 0.1}
                }
            }
            
            # Import AgentConfig from the correct location
            from agents.core.base_agent import AgentConfig
            
            # Initialize agents
            agent_classes = {
                "requirements_analyst": RequirementsAnalyst,
                "architecture_designer": ArchitectureDesigner,
                "code_generator": CodeGenerator,
                "test_generator": TestGenerator,
                "code_reviewer": CodeReviewer,
                "security_analyst": SecurityAnalyst,
                "documentation_generator": DocumentationGenerator
            }
            
            for agent_name, agent_class in agent_classes.items():
                if agent_configs[agent_name]["enabled"]:
                    config_dict = agent_configs[agent_name]
                    # Create proper AgentConfig object with correct fields
                    config = AgentConfig(
                        agent_id=agent_name,
                        agent_type=agent_name,
                        prompt_template_id=f"{agent_name}_template",
                        model_name=config_dict.get("parameters", {}).get("model_name", "gemini-2.5-flash-lite"),
                        temperature=config_dict.get("parameters", {}).get("temperature", 0.1),
                        max_retries=config_dict.get("max_retries", 3),
                        timeout_seconds=config_dict.get("timeout", 300)
                    )
                    agents[agent_name] = agent_class(config, self.gemini_client)
                    self.logger.info(f"Initialized agent: {agent_name}")
            
            self.logger.info(f"Initialized {len(agents)} agents")
            return agents
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {str(e)}")
            raise
    
    async def execute_workflow(
        self,
        project_context: str,
        output_dir: str = None
    ) -> WorkflowResult:
        """
        Execute the complete development workflow.
        
        Args:
            project_context: Description of the project to develop
            output_dir: Directory to save generated files (optional)
            
        Returns:
            WorkflowResult with complete execution results
        """
        from utils.core.helpers import generate_project_name, create_project_path
        
        # Generate project name from description
        project_name = generate_project_name(project_context)
        
        # Create project path within generated_projects directory
        if output_dir is None:
            output_dir = "./generated_projects"
        
        project_path = create_project_path(output_dir, project_name)
        
        session_id = str(uuid.uuid4())
        start_time = asyncio.get_event_loop().time()
        
        # Create session-specific logger
        session_logger = self.logging_manager.create_session_logger(session_id)
        
        self.logger.info(f"Starting workflow execution for project: {project_name}")
        self.logger.info(f"Project path: {project_path}")
        self.logger.info(f"Session ID: {session_id}")
        
        # Log workflow start
        session_logger.info(f"Workflow started - Project: {project_name}, Context: {project_context[:200]}..., Output: {output_dir}")
        
        try:
            # Create initial state
            initial_state = create_initial_state(
                project_context=project_context,
                project_name=project_name,
                session_id=session_id
            )
            
            # Skip codebase indexing for new project generation
            # The context engine should not index the current project when generating a new one
            self.logger.info("Skipping codebase indexing for new project generation")
            
            # Execute workflow using LangGraph workflow manager with logging
            self.logger.info("Executing workflow...")
            
            # Get LangChain callback configuration with thread_id for LangGraph
            runnable_config = {
                "configurable": {
                    "thread_id": session_id,
                    "session_id": session_id,
                    "checkpoint_id": session_id
                },
                "tags": ["workflow_execution", project_name]
            }
            
            result_state = await self.workflow_manager.workflow.ainvoke(
                initial_state,
                config=runnable_config
            )
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Log workflow completion
            session_logger.info(f"Workflow completed successfully - "
                               f"Execution time: {execution_time:.2f}s, "
                               f"Agent outputs: {len(result_state.get('agent_outputs', {}))}, "
                               f"Errors: {len(result_state.get('errors', []))}")
            
            # Log performance metrics
            files_generated = (len(result_state.get("code_files", {})) + 
                             len(result_state.get("tests", {})) + 
                             len(result_state.get("documentation", {})))
            session_logger.info(f"Performance metrics - "
                               f"Total time: {execution_time:.2f}s, "
                               f"Agents: {len(result_state.get('agent_outputs', {}))}, "
                               f"Files: {files_generated}, "
                               f"Errors: {len(result_state.get('errors', []))}")
            
            # Save results
            await self._save_results(result_state, project_path)
            
            # Create workflow result
            workflow_result = self._create_workflow_result(
                result_state, session_id, execution_time
            )
            
            self.logger.info(f"Workflow completed successfully in {execution_time:.2f}s")
            return workflow_result
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Log error
            session_logger.error(f"Workflow execution failed: {str(e)} (Project: {project_name}, Context: {project_context[:200]}..., Time: {execution_time:.2f}s)")
            
            # Log workflow failure
            session_logger.error(f"Workflow failed after {execution_time:.2f}s - Status: failed, Error: {str(e)}")
            
            # Create error result
            error_state = create_initial_state(
                project_context=project_context,
                project_name=project_name,
                session_id=session_id
            )
            
            return self._create_workflow_result(
                error_state, session_id, execution_time, error=str(e)
            )
    
    async def _save_results(self, state: Dict[str, Any], output_dir: str):
        """
        Save workflow results to the specified directory.
        
        Args:
            state: Workflow state with results
            output_dir: Directory to save results
        """
        try:
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Import extraction utilities
            from utils.workflow_file_extractor import (
                extract_code_files,
                extract_test_files,
                extract_documentation_files
            )
            
            # Get raw data from state
            code_files_raw = state.get("code_files", {})
            test_files_raw = state.get("test_files", {})
            doc_files_raw = state.get("documentation", {})
            config_files_raw = state.get("configuration_files", {})
            
            # Extract actual files using proper extraction logic
            code_files = extract_code_files(code_files_raw)
            test_files = extract_test_files(test_files_raw)
            doc_files = extract_documentation_files(doc_files_raw)
            
            # Process configuration files (usually simple dict)
            config_files = {}
            if isinstance(config_files_raw, dict):
                for key, value in config_files_raw.items():
                    if key not in ["output", "raw_output", "metadata"]:
                        if isinstance(value, str):
                            # Skip JSON in markdown blocks
                            if not re.match(r'^\s*```json\s*\{', value, re.DOTALL):
                                config_files[key] = value
            
            # Combine all extracted files
            all_files = {}
            all_files.update(code_files)
            all_files.update(test_files)
            all_files.update(doc_files)
            all_files.update(config_files)
            
            self.logger.info(
                f"Extracted files: {len(code_files)} code, {len(test_files)} test, "
                f"{len(doc_files)} docs, {len(config_files)} config"
            )
            
            for file_path, content in all_files.items():
                # Sanitize the file path to ensure it's a valid filename
                sanitized_path = self._sanitize_file_path(file_path)
                if not sanitized_path:
                    self.logger.warning(f"Skipping invalid file path: {file_path[:100]}...")
                    continue
                
                full_path = output_path / sanitized_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Save workflow state
            state_file = output_path / "workflow_state.json"
            import json
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            
            # 🎯 ADD AGILE ARTIFACTS TO ALL GENERATED PROJECTS
            self._add_agile_artifacts_to_project(output_path, state)
            
            self.logger.info(f"Results saved to: {output_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")
    
    def _sanitize_file_path(self, file_path: str) -> str:
        """
        Sanitize a file path to ensure it's a valid filename.
        
        Args:
            file_path: Original file path
            
        Returns:
            Sanitized file path or empty string if invalid
        """
        import re
        import os
        
        # If the file_path looks like code content rather than a filename, generate a proper filename
        if len(file_path) > 200 or '\n' in file_path or file_path.count('/') > 5:
            # This looks like code content, not a filename
            # Extract a meaningful name from the first line or use a default
            lines = file_path.split('\n')
            first_line = lines[0].strip()
            
            # Try to extract a meaningful name
            if 'def ' in first_line:
                # Extract function name
                match = re.search(r'def\s+(\w+)', first_line)
                if match:
                    return f"{match.group(1)}.py"
            elif 'class ' in first_line:
                # Extract class name
                match = re.search(r'class\s+(\w+)', first_line)
                if match:
                    return f"{match.group(1)}.py"
            elif 'import ' in first_line or 'from ' in first_line:
                # This might be a module file
                return "module.py"
            else:
                # Use a generic name based on content
                return "generated_file.py"
        
        # Remove or replace invalid characters
        # Windows invalid characters: < > : " | ? * \ /
        invalid_chars = r'[<>:"|?*\\/\n\r\t]'
        sanitized = re.sub(invalid_chars, '_', file_path)
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        
        # Ensure it's not empty
        if not sanitized:
            return "unnamed_file.txt"
        
        # Limit length
        if len(sanitized) > 255:
            # Keep extension if present
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
        
        return sanitized
    
    def _add_agile_artifacts_to_project(self, project_path: Path, state: Dict[str, Any]):
        """Add comprehensive agile artifacts to any generated project."""
        
        # Create agile directory
        agile_path = project_path / "agile"
        agile_path.mkdir(exist_ok=True)
        
        # Get current timestamp for consistency
        from datetime import datetime
        created_date = datetime.now().strftime('%Y-%m-%d')
        created_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract project info from state
        project_name = state.get('project_name', project_path.name)
        project_context = state.get('project_context', 'AI-powered project generated with systematic agile methodology.')
        
        # Detect capabilities from generated files
        code_files = state.get('code_files', {})
        capabilities = []
        
        # Analyze generated files to extract capabilities
        for file_path in code_files.keys():
            if 'api' in file_path.lower() or 'routes' in file_path.lower():
                capabilities.append('api_development')
            elif 'test' in file_path.lower():
                capabilities.append('testing_framework')
            elif 'model' in file_path.lower() or 'schema' in file_path.lower():
                capabilities.append('data_modeling')
            elif 'auth' in file_path.lower():
                capabilities.append('authentication')
            elif 'database' in file_path.lower() or 'db' in file_path.lower():
                capabilities.append('database_integration')
        
        if not capabilities:
            capabilities = ['core_functionality', 'user_interface', 'data_processing']
        
        # Create project config for agile artifacts
        project_config = {
            'name': project_name,
            'description': project_context,
            'capabilities': capabilities
        }
        
        # Create the agile artifacts using the same approach as other generators
        from datetime import datetime
        created_date = datetime.now().strftime('%Y-%m-%d')
        created_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Epic Overview
        epic_content = f"""# Epic Overview: {project_config.get('name', 'Generated Project')}

**Created**: {created_date}  
**Status**: In Progress  
**Priority**: High  

## Epic Description

{project_config.get('description', 'AI-powered project generated with systematic agile methodology.')}

## Business Value

- **Automated Excellence**: Leverage AI capabilities for enhanced productivity
- **Scalable Architecture**: Built with modern frameworks and best practices
- **Quality Assurance**: Comprehensive testing and validation included
- **Developer Experience**: Optimized for maintainability and extensibility

## User Stories

See USER_STORIES.md for detailed breakdown of this epic into actionable user stories.

---
**Generated by**: Universal Composition Layer - Agile Artifacts System  
**Timestamp**: {created_timestamp}
"""
        
        (agile_path / "EPIC_OVERVIEW.md").write_text(epic_content, encoding='utf-8')
        
        # User Stories
        capabilities = project_config.get('capabilities', [])
        user_stories_content = f"""# User Stories: {project_config.get('name', 'Generated Project')}

**Created**: {created_date}  
**Epic**: {project_config.get('name', 'Generated Project')}  

## User Story Index

"""
        
        for i, capability in enumerate(capabilities, 1):
            story_id = f"US-{i:03d}"
            capability_name = capability.replace('_', ' ').title()
            
            user_stories_content += f"""
### {story_id}: {capability_name}

**As a** user  
**I want** {capability_name.lower()} functionality  
**So that** I can leverage the system's capabilities effectively  

**Acceptance Criteria:**
- [ ] {capability_name} is implemented and functional
- [ ] Error handling is comprehensive
- [ ] Performance meets requirements
- [ ] Documentation is complete
- [ ] Testing covers all scenarios

**Story Points**: 5  
**Priority**: High  
**Status**: Ready for Development  

"""
        
        user_stories_content += f"""
---
**Generated by**: Universal Composition Layer - Agile Artifacts System  
**Timestamp**: {created_timestamp}
"""
        
        (agile_path / "USER_STORIES.md").write_text(user_stories_content, encoding='utf-8')
        
        # Definition of Done
        dod_content = f"""# Definition of Done: {project_config.get('name', 'Generated Project')}

**Created**: {created_date}  
**Applies to**: All user stories and tasks in this project  

## Code Quality Standards

- [ ] **Code Review**: All code reviewed by at least one team member
- [ ] **Testing**: Unit tests written and passing (minimum 80% coverage)
- [ ] **Documentation**: Code is well-documented with clear comments
- [ ] **Standards**: Follows project coding standards and conventions
- [ ] **Performance**: No performance regressions introduced

## Functional Requirements

- [ ] **Feature Complete**: All acceptance criteria met
- [ ] **Error Handling**: Comprehensive error handling implemented
- [ ] **Validation**: Input validation and sanitization in place
- [ ] **Integration**: Successfully integrates with existing components
- [ ] **User Experience**: Intuitive and responsive user interface

## Review and Approval

- [ ] **Product Owner**: Approved by product owner
- [ ] **Technical Review**: Technical architecture approved
- [ ] **Business Value**: Business value delivered and measurable
- [ ] **Ready for Production**: All production readiness criteria met

---
**Generated by**: Universal Composition Layer - Agile Artifacts System  
**Timestamp**: {created_timestamp}
"""
        
        (agile_path / "DEFINITION_OF_DONE.md").write_text(dod_content, encoding='utf-8')
        
        self.logger.info(f"Agile artifacts added to project at: {agile_path}")
    
    def _create_workflow_result(
        self,
        state: Dict[str, Any],
        session_id: str,
        execution_time: float,
        error: str = None
    ) -> WorkflowResult:
        """
        Create a WorkflowResult from the final state.
        
        Args:
            state: Final workflow state
            session_id: Session identifier
            execution_time: Total execution time
            error: Error message if workflow failed
            
        Returns:
            WorkflowResult object
        """
        # Determine status
        if error:
            status = WorkflowStatus.FAILED
        elif state.get("errors"):
            status = WorkflowStatus.FAILED
        else:
            status = WorkflowStatus.COMPLETED
        
        # Extract agent results - convert to AgentResponse objects for WorkflowResult
        agent_results = {}
        for agent_name, result in state.get("agent_outputs", {}).items():
            try:
                if isinstance(result, dict):
                    # Convert dictionary to AgentResponse object
                    agent_results[agent_name] = AgentResponse(
                        agent_name=agent_name,
                        task_name=f"{agent_name}_task",
                        status=TaskStatus.COMPLETED,
                        output=result.get("output", result),
                        metadata=result.get("metadata", {}),
                        timestamp=datetime.now(),
                        execution_time=result.get("execution_time", 0.0),
                        error_message=result.get("error_message"),
                        warnings=result.get("warnings", []),
                        documentation=result.get("documentation", {}),
                        logs=result.get("logs", []),
                        decisions=result.get("decisions", []),
                        artifacts=result.get("artifacts", [])
                    )
                elif hasattr(result, 'agent_name') and hasattr(result, 'task_name'):
                    # Already an AgentResponse object
                    agent_results[agent_name] = result
                else:
                    # Convert unknown format to AgentResponse
                    agent_results[agent_name] = AgentResponse(
                        agent_name=agent_name,
                        task_name=f"{agent_name}_task",
                        status=TaskStatus.COMPLETED,
                        output=result.dict() if hasattr(result, 'dict') else result,
                        metadata={},
                        timestamp=datetime.now(),
                        execution_time=0.0,
                        error_message=None,
                        warnings=[],
                        documentation={},
                        logs=[],
                        decisions=[],
                        artifacts=[]
                    )
            except Exception as e:
                # If conversion fails, create a minimal AgentResponse
                agent_results[agent_name] = AgentResponse(
                    agent_name=agent_name,
                    task_name=f"{agent_name}_task",
                    status=TaskStatus.FAILED,
                    output={},
                    metadata={},
                    timestamp=datetime.now(),
                    execution_time=0.0,
                    error_message=f"Failed to convert agent result: {str(e)}",
                    warnings=[],
                    documentation={},
                    logs=[],
                    decisions=[],
                    artifacts=[]
                )
        
        # Combine all file types for generated_files
        code_files = state.get("code_files", {})
        test_files = state.get("tests", {})
        documentation_files = state.get("documentation", {})
        configuration_files = state.get("configuration_files", {})
        diagrams = state.get("diagrams", {})
        
        # Debug: Print state keys and file counts
        print(f"DEBUG: State keys: {list(state.keys())}")
        print(f"DEBUG: Code files in state: {len(code_files)}")
        print(f"DEBUG: Test files in state: {len(test_files)}")
        print(f"DEBUG: Documentation files in state: {len(documentation_files)}")
        print(f"DEBUG: Configuration files in state: {len(configuration_files)}")
        
        # Process documentation files to extract content from DocumentationFile objects
        processed_documentation_files = {}
        for file_path, file_data in documentation_files.items():
            if isinstance(file_data, dict) and "content" in file_data:
                # Extract content from DocumentationFile object
                processed_documentation_files[file_path] = file_data["content"]
            elif isinstance(file_data, str):
                # Already a string
                processed_documentation_files[file_path] = file_data
            else:
                # Convert to string if possible
                processed_documentation_files[file_path] = str(file_data)
        
        # Process code files to extract content from SourceFile objects
        processed_code_files = {}
        for file_path, file_data in code_files.items():
            if isinstance(file_data, dict) and "content" in file_data:
                # Extract content from SourceFile object
                processed_code_files[file_path] = file_data["content"]
            elif isinstance(file_data, str):
                # Already a string
                processed_code_files[file_path] = file_data
            else:
                # Convert to string if possible
                processed_code_files[file_path] = str(file_data)
        
        # Process test files to extract content from TestFile objects
        processed_test_files = {}
        for file_path, file_data in test_files.items():
            if isinstance(file_data, dict) and "content" in file_data:
                # Extract content from TestFile object
                processed_test_files[file_path] = file_data["content"]
            elif isinstance(file_data, str):
                # Already a string
                processed_test_files[file_path] = file_data
            else:
                # Convert to string if possible
                processed_test_files[file_path] = str(file_data)
        
        # Process configuration files to extract content from ConfigurationFile objects
        processed_configuration_files = {}
        for file_path, file_data in configuration_files.items():
            if isinstance(file_data, dict) and "content" in file_data:
                # Extract content from ConfigurationFile object
                processed_configuration_files[file_path] = file_data["content"]
            elif isinstance(file_data, str):
                # Already a string
                processed_configuration_files[file_path] = file_data
            else:
                # Convert to string if possible
                processed_configuration_files[file_path] = str(file_data)
        
        # Process diagram files
        processed_diagram_files = {}
        for diagram_type, diagram_data in diagrams.items():
            if isinstance(diagram_data, dict) and "filename" in diagram_data and "content" in diagram_data:
                # Extract content from diagram object
                processed_diagram_files[diagram_data["filename"]] = diagram_data["content"]
            elif isinstance(diagram_data, str):
                # Already a string content
                processed_diagram_files[f"{diagram_type}.puml"] = diagram_data
            else:
                # Convert to string if possible
                processed_diagram_files[f"{diagram_type}.puml"] = str(diagram_data)
        
        # Merge all file types into generated_files
        generated_files = {}
        generated_files.update(processed_code_files)
        generated_files.update(processed_test_files)
        generated_files.update(processed_documentation_files)
        generated_files.update(processed_configuration_files)
        generated_files.update(processed_diagram_files)
        
        return WorkflowResult(
            workflow_id=str(uuid.uuid4()),
            session_id=session_id,
            status=status,
            project_name=state.get("project_name", ""),
            project_context=state.get("project_context", ""),
            agent_results=agent_results,
            generated_files=generated_files,
            code_files=processed_code_files,
            test_files=processed_test_files,
            documentation_files=processed_documentation_files,
            raw_state=state,  # Include raw state for enhanced display
            configuration_files=processed_configuration_files,
            diagram_files=processed_diagram_files,
            total_execution_time=execution_time,
            start_time=state.get("created_at") or datetime.now(),
            end_time=state.get("updated_at") or datetime.now(),
            human_approvals=state.get("approval_requests", []),
            errors=state.get("errors", []),
            warnings=state.get("warnings", [])
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current system status.
        
        Returns:
            Dictionary with system status information
        """
        return {
            "system_name": self.config.project_name,
            "version": self.config.version,
            "environment": self.config.environment,
            "agents": {
                name: agent.get_performance_metrics()
                for name, agent in self.agents.items()
            },
            "gemini_model": self.config.gemini.model_name,
            "workflow_enabled": True,
            "context_engine_enabled": self.config.context.enable_codebase_indexing
        }


async def main():
    """
    Main entry point for the application.
    """
    # Setup logging
    setup_logging()
    setup_langchain_logging("ai-dev-agent", enable_langsmith=True)
    logger = logging.getLogger("main")
    
    try:
        # Load configuration
        config = load_config_from_env()
        logger.info("Configuration loaded successfully")
        
        # Initialize the development agent
        agent = AIDevelopmentAgent(config)
        
        # Example usage
        project_context = """
        Create a REST API for user management with the following features:
        - User registration and authentication
        - User profile management
        - Role-based access control
        - Password reset functionality
        - Email verification
        
        The API should be built with Python FastAPI, use PostgreSQL for the database,
        and include comprehensive testing and documentation.
        """
        
        output_dir = "./generated_projects"
        
        # Execute workflow
        result = await agent.execute_workflow(
            project_context=project_context,
            output_dir=output_dir
        )
        
        # Print results
        print(f"\nWorkflow completed with status: {result.status}")
        print(f"Total execution time: {result.total_execution_time:.2f}s")
        print(f"Generated files: {len(result.generated_files)}")
        print(f"Agent results: {len(result.agent_results)}")
        
        if result.errors:
            print(f"Errors encountered: {len(result.errors)}")
            for error in result.errors:
                print(f"  - {error.get('error_message', 'Unknown error')}")
        
        # Print system status
        status = agent.get_system_status()
        print(f"\nSystem Status:")
        print(f"  Agents: {len(status['agents'])}")
        print(f"  Gemini Model: {status['gemini_model']}")
        
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
