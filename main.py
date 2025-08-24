"""
Main entry point for the AI Development Agent system.
Orchestrates the entire development workflow using LangGraph and Gemini API.
"""

import asyncio
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, Any

import google.generativeai as genai

from models.config import SystemConfig, load_config_from_env, get_default_config
from models.state import create_initial_state
from models.responses import WorkflowResult, WorkflowStatus
from workflow.workflow_graph import create_workflow_graph
from context.context_engine import ContextEngine
from utils.logging_config import setup_logging
from utils.file_manager import FileManager


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
        
        # Initialize components
        self.gemini_client = self._initialize_gemini()
        self.context_engine = ContextEngine(config.context)
        self.file_manager = FileManager(config.storage)
        self.agents = self._initialize_agents()
        self.workflow = create_workflow_graph(config, self.agents)
        
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
            from agents.requirements_analyst import RequirementsAnalyst
            from agents.architecture_designer import ArchitectureDesigner
            from agents.code_generator import CodeGenerator
            from agents.test_generator import TestGenerator
            from agents.code_reviewer import CodeReviewer
            from agents.security_analyst import SecurityAnalyst
            from agents.documentation_generator import DocumentationGenerator
            
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
                    "description": "Generates comprehensive documentation",
                    "enabled": True,
                    "max_retries": 3,
                    "timeout": 300,
                    "prompt_template": "Generate documentation for: {project_context}",
                    "system_prompt": "You are a documentation expert.",
                    "parameters": {"temperature": 0.1}
                }
            }
            
            # Import AgentConfig
            from models.config import AgentConfig
            
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
                    # Create proper AgentConfig object
                    config = AgentConfig(**config_dict)
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
        from utils.helpers import generate_project_name, create_project_path
        
        # Generate project name from description
        project_name = generate_project_name(project_context)
        
        # Create project path within generated_projects directory
        if output_dir is None:
            output_dir = "./generated_projects"
        
        project_path = create_project_path(output_dir, project_name)
        
        session_id = str(uuid.uuid4())
        start_time = asyncio.get_event_loop().time()
        
        self.logger.info(f"Starting workflow execution for project: {project_name}")
        self.logger.info(f"Project path: {project_path}")
        self.logger.info(f"Session ID: {session_id}")
        
        try:
            # Create initial state
            initial_state = create_initial_state(
                project_context=project_context,
                project_name=project_name,
                session_id=session_id
            )
            
            # Index codebase if enabled
            if self.config.context.enable_codebase_indexing:
                self.logger.info("Indexing codebase...")
                await self.context_engine.index_codebase(".")
            
            # Execute workflow
            self.logger.info("Executing workflow...")
            result_state = await self.workflow.ainvoke(
                initial_state,
                config={
                    "configurable": {
                        "thread_id": session_id,
                        "checkpoint_id": session_id
                    }
                }
            )
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
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
            
            # Save generated files
            code_files = state.get("code_files", {})
            test_files = state.get("tests", {})
            doc_files = state.get("documentation", {})
            config_files = state.get("configuration_files", {})
            
            all_files = {
                **code_files,
                **test_files,
                **doc_files,
                **config_files
            }
            
            for file_path, content in all_files.items():
                full_path = output_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Save workflow state
            state_file = output_path / "workflow_state.json"
            import json
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            
            self.logger.info(f"Results saved to: {output_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")
    
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
        
        # Extract agent results - ensure they are AgentResponse objects with enhanced documentation
        agent_results = {}
        for agent_name, result in state.get("agent_outputs", {}).items():
            if isinstance(result, dict):
                # Convert dict to AgentResponse if it has the required fields
                if "agent_name" in result and "task_name" in result:
                    from models.responses import AgentResponse, TaskStatus
                    agent_results[agent_name] = AgentResponse(
                        agent_name=result.get("agent_name", agent_name),
                        task_name=result.get("task_name", "unknown_task"),
                        status=TaskStatus(result.get("status", "completed")),
                        output=result.get("output", {}),
                        metadata=result.get("metadata", {}),
                        execution_time=result.get("execution_time", 0.0),
                        error_message=result.get("error_message"),
                        warnings=result.get("warnings", []),
                        documentation=result.get("documentation", {}),
                        logs=result.get("logs", []),
                        decisions=result.get("decisions", []),
                        artifacts=result.get("artifacts", [])
                    )
                else:
                    # Create a proper AgentResponse from the dict
                    from models.responses import AgentResponse, TaskStatus
                    agent_results[agent_name] = AgentResponse(
                        agent_name=agent_name,
                        task_name=f"{agent_name}_task",
                        status=TaskStatus.COMPLETED,
                        output=result,
                        documentation={},
                        logs=[],
                        decisions=[],
                        artifacts=[]
                    )
            elif hasattr(result, 'agent_name') and hasattr(result, 'task_name'):
                # Already an AgentResponse object
                agent_results[agent_name] = result
            else:
                # Convert to AgentResponse
                from models.responses import AgentResponse, TaskStatus
                agent_results[agent_name] = AgentResponse(
                    agent_name=agent_name,
                    task_name=f"{agent_name}_task",
                    status=TaskStatus.COMPLETED,
                    output=result.dict() if hasattr(result, 'dict') else result,
                    documentation={},
                    logs=[],
                    decisions=[],
                    artifacts=[]
                )
        
        return WorkflowResult(
            workflow_id=str(uuid.uuid4()),
            session_id=session_id,
            status=status,
            project_name=state.get("project_name", ""),
            project_context=state.get("project_context", ""),
            agent_results=agent_results,
            generated_files=state.get("code_files", {}),
            code_files=state.get("code_files", {}),
            test_files=state.get("tests", {}),
            documentation_files=state.get("documentation", {}),
            configuration_files=state.get("configuration_files", {}),
            total_execution_time=execution_time,
            start_time=state.get("created_at"),
            end_time=state.get("updated_at"),
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
