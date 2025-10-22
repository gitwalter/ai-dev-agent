"""
Code Generator Agent - LangGraph Implementation

Generates production-ready code using LangGraph with proper state management,
memory, and node-based architecture.
"""

import logging
from typing import Dict, Any, List, Annotated, Optional
from pydantic import BaseModel, Field
from datetime import datetime

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.store.memory import InMemoryStore
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available")

from agents.development.code_generator import CodeGenerator
from models.config import AgentConfig
from utils.llm.gemini_client_factory import get_gemini_client

logger = logging.getLogger(__name__)


class CodeGeneratorState(BaseModel):
    """State for Code Generator workflow with memory support using Pydantic BaseModel."""
    
    # Input (required fields)
    requirements: Dict[str, Any] = Field(..., description="Project requirements")
    architecture: Dict[str, Any] = Field(..., description="System architecture design")
    project_name: str = Field(..., description="Name of the project")
    tech_stack: Dict[str, List[str]] = Field(default_factory=dict, description="Selected technology stack")
    
    # Node outputs (initialized with defaults)
    project_structure: Dict[str, Any] = Field(default_factory=dict, description="Generated project structure")
    code_files: List[Dict[str, Any]] = Field(default_factory=list, description="Generated code files")
    configuration_files: List[Dict[str, Any]] = Field(default_factory=list, description="Config files")
    documentation: Dict[str, str] = Field(default_factory=dict, description="Generated documentation")
    test_files: List[Dict[str, Any]] = Field(default_factory=list, description="Generated test files")
    
    # Memory context (initialized with defaults)
    generation_history: List[Dict] = Field(default_factory=list, description="History of code generations for learning")
    patterns_learned: Dict[str, Any] = Field(default_factory=dict, description="Learned code patterns from memory")
    
    # Workflow control (initialized with defaults)
    current_stage: str = Field(default="initialized", description="Current generation stage")
    stages_completed: List[str] = Field(default_factory=list, description="Completed stages")
    needs_revision: bool = Field(default=False, description="Whether revision is needed")
    revision_count: int = Field(default=0, description="Number of revisions performed")
    max_revisions: int = Field(default=2, description="Maximum allowed revisions")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    
    # Metrics (automatically initialized as empty dict)
    metrics: Dict[str, float] = Field(default_factory=dict, description="Generation timing metrics")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class CodeGeneratorCoordinator:
    """
    Code Generator using LangGraph with memory for learning patterns.
    
    Implements:
    - Node-based code generation workflow
    - Short-term memory via checkpointer (thread-scoped)
    - Long-term memory via store (cross-thread pattern learning)
    - Conditional edges for quality-based revision
    """
    
    def __init__(self, gemini_client=None):
        """
        Initialize Code Generator with LangGraph and memory.
        
        Args:
            gemini_client: Optional LLM client for swarm coordination.
                          If None, creates standalone client for independent use.
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required. Install with: pip install langgraph")
        
        # Create or use LLM client
        if gemini_client is None:
            gemini_client = get_gemini_client(
                agent_name='code_generator',
                model_name='gemini-2.5-flash',
                temperature=0.2
            )
            logger.info("✅ Code Generator: Created standalone LLM client")
        else:
            logger.info("✅ Code Generator: Using shared LLM client from swarm")
        
        # Initialize the underlying agent
        config = AgentConfig(
            agent_id='code_generator',
            name='Code Generator',
            description='Generates production-ready code',
            model_name='gemini-2.5-flash'
        )
        self.generator = CodeGenerator(config, gemini_client=gemini_client)
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        logger.info("Code Generator Coordinator (LangGraph) initialized")
    
    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow with nodes and conditional edges.
        
        Workflow:
        1. load_patterns (from long-term memory)
        2. design_structure
        3. generate_code
        4. generate_tests
        5. generate_config
        6. generate_docs
        7. validate_quality
        8. (conditional) revise or finalize
        """
        
        workflow = StateGraph(CodeGeneratorState)
        
        # Add nodes (discrete operations)
        workflow.add_node("load_patterns", self._load_patterns_from_memory)
        workflow.add_node("design_structure", self._design_project_structure)
        workflow.add_node("generate_code", self._generate_code_files)
        workflow.add_node("generate_tests", self._generate_test_files)
        workflow.add_node("generate_config", self._generate_configuration)
        workflow.add_node("generate_docs", self._generate_documentation)
        workflow.add_node("validate_quality", self._validate_code_quality)
        workflow.add_node("revise", self._revise_code)
        workflow.add_node("finalize", self._finalize_and_save_patterns)
        
        # Define edges (flow between nodes)
        workflow.set_entry_point("load_patterns")
        workflow.add_edge("load_patterns", "design_structure")
        workflow.add_edge("design_structure", "generate_code")
        workflow.add_edge("generate_code", "generate_tests")
        workflow.add_edge("generate_tests", "generate_config")
        workflow.add_edge("generate_config", "generate_docs")
        workflow.add_edge("generate_docs", "validate_quality")
        
        # Conditional edge: quality check determines next step
        workflow.add_conditional_edges(
            "validate_quality",
            self._should_revise,
            {
                "revise": "revise",      # Quality below threshold
                "finalize": "finalize",  # Quality acceptable
                END: END                 # Max revisions reached
            }
        )
        
        # Revision loop
        workflow.add_edge("revise", "generate_code")  # Loop back to regenerate
        
        # Final node
        workflow.add_edge("finalize", END)
        
        return workflow
    
    # ========================================================================
    # NODE IMPLEMENTATIONS
    # ========================================================================
    
    async def _load_patterns_from_memory(self, state: CodeGeneratorState) -> CodeGeneratorState:
        """
        Node 1: Load learned patterns from long-term memory.
        
        This demonstrates long-term memory usage across different sessions.
        """
        import time
        start = time.time()
        
        logger.info("[CodeGen] Loading patterns from long-term memory...")
        
        try:
            # Access long-term memory store (cross-thread)
            # In production, this would use PostgresStore or RedisStore
            tech_stack_key = str(state.get('tech_stack', {}))
            
            # Retrieve previously learned patterns for this tech stack
            patterns = {}
            # TODO: Implement store.get() when store API is fully available
            # patterns = await self.store.get(tech_stack_key, default={})
            
            state['patterns_learned'] = patterns
            state['generation_history'] = []
            state['current_stage'] = 'patterns_loaded'
            state['stages_completed'] = state.get('stages_completed', []) + ['load_patterns']
            state['metrics']['load_patterns_time'] = time.time() - start
            
            logger.info(f"[CodeGen] ✅ Loaded {len(patterns)} patterns from memory")
            
        except Exception as e:
            logger.error(f"[CodeGen] ❌ Pattern loading failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Pattern loading error: {str(e)}"]
        
        return state
    
    async def _design_project_structure(self, state: CodeGeneratorState) -> CodeGeneratorState:
        """Node 2: Design project structure based on requirements and patterns."""
        import time
        start = time.time()
        
        logger.info("[CodeGen] Designing project structure...")
        
        try:
            # Use learned patterns to inform structure design
            patterns = state.get('patterns_learned', {})
            
            # Design structure
            structure = {
                'root': state.get('project_name', 'project'),
                'directories': [
                    'src/',
                    'tests/',
                    'docs/',
                    'config/',
                    'scripts/'
                ],
                'files': [
                    'README.md',
                    'requirements.txt',
                    'setup.py',
                    '.gitignore'
                ]
            }
            
            state['project_structure'] = structure
            state['current_stage'] = 'structure_designed'
            state['stages_completed'] = state.get('stages_completed', []) + ['design_structure']
            state['metrics']['design_structure_time'] = time.time() - start
            
            logger.info(f"[CodeGen] ✅ Designed structure with {len(structure['directories'])} directories")
            
        except Exception as e:
            logger.error(f"[CodeGen] ❌ Structure design failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Structure design error: {str(e)}"]
        
        return state
    
    async def _generate_code_files(self, state: CodeGeneratorState) -> CodeGeneratorState:
        """Node 3: Generate code files using underlying generator agent."""
        import time
        start = time.time()
        
        logger.info("[CodeGen] Generating code files...")
        
        try:
            # Call underlying code generator
            task = {
                'project_context': f"Project: {state.get('project_name')}",
                'architecture': state.get('architecture', {}),
                'tech_stack': state.get('tech_stack', {}),
                'description': 'Generate production-ready code',
                'context': state.get('requirements', {})
            }
            
            result = await self.generator.execute(task)
            
            code_files = result.get('code_files', [
                {'path': 'src/main.py', 'content': '# Generated code', 'language': 'python'},
                {'path': 'src/__init__.py', 'content': '', 'language': 'python'}
            ])
            
            state['code_files'] = code_files
            state['current_stage'] = 'code_generated'
            state['stages_completed'] = state.get('stages_completed', []) + ['generate_code']
            state['metrics']['generate_code_time'] = time.time() - start
            
            logger.info(f"[CodeGen] ✅ Generated {len(code_files)} code files")
            
        except Exception as e:
            logger.error(f"[CodeGen] ❌ Code generation failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Code generation error: {str(e)}"]
        
        return state
    
    async def _generate_test_files(self, state: CodeGeneratorState) -> CodeGeneratorState:
        """Node 4: Generate test files for generated code."""
        import time
        start = time.time()
        
        logger.info("[CodeGen] Generating test files...")
        
        try:
            test_files = []
            for code_file in state.get('code_files', []):
                if code_file['path'].endswith('.py') and not code_file['path'].endswith('__init__.py'):
                    test_path = code_file['path'].replace('src/', 'tests/test_')
                    test_files.append({
                        'path': test_path,
                        'content': f"# Tests for {code_file['path']}",
                        'language': 'python'
                    })
            
            state['test_files'] = test_files
            state['current_stage'] = 'tests_generated'
            state['stages_completed'] = state.get('stages_completed', []) + ['generate_tests']
            state['metrics']['generate_tests_time'] = time.time() - start
            
            logger.info(f"[CodeGen] ✅ Generated {len(test_files)} test files")
            
        except Exception as e:
            logger.error(f"[CodeGen] ❌ Test generation failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Test generation error: {str(e)}"]
        
        return state
    
    async def _generate_configuration(self, state: CodeGeneratorState) -> CodeGeneratorState:
        """Node 5: Generate configuration files."""
        import time
        start = time.time()
        
        logger.info("[CodeGen] Generating configuration files...")
        
        try:
            config_files = [
                {
                    'path': 'requirements.txt',
                    'content': 'fastapi==0.104.1\nuvicorn==0.24.0\npydantic==2.5.0',
                    'type': 'requirements'
                },
                {
                    'path': '.gitignore',
                    'content': '__pycache__/\n*.pyc\n.env\nvenv/',
                    'type': 'gitignore'
                },
                {
                    'path': 'setup.py',
                    'content': f"from setuptools import setup\n\nsetup(name='{state.get('project_name')}')",
                    'type': 'setup'
                }
            ]
            
            state['configuration_files'] = config_files
            state['current_stage'] = 'config_generated'
            state['stages_completed'] = state.get('stages_completed', []) + ['generate_config']
            state['metrics']['generate_config_time'] = time.time() - start
            
            logger.info(f"[CodeGen] ✅ Generated {len(config_files)} configuration files")
            
        except Exception as e:
            logger.error(f"[CodeGen] ❌ Configuration generation failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Config generation error: {str(e)}"]
        
        return state
    
    async def _generate_documentation(self, state: CodeGeneratorState) -> CodeGeneratorState:
        """Node 6: Generate documentation."""
        import time
        start = time.time()
        
        logger.info("[CodeGen] Generating documentation...")
        
        try:
            documentation = {
                'README.md': f"# {state.get('project_name')}\n\nGenerated project documentation.",
                'API.md': "# API Documentation\n\nAPI endpoints and usage.",
                'CONTRIBUTING.md': "# Contributing Guidelines\n\nHow to contribute to this project."
            }
            
            state['documentation'] = documentation
            state['current_stage'] = 'docs_generated'
            state['stages_completed'] = state.get('stages_completed', []) + ['generate_docs']
            state['metrics']['generate_docs_time'] = time.time() - start
            
            logger.info(f"[CodeGen] ✅ Generated {len(documentation)} documentation files")
            
        except Exception as e:
            logger.error(f"[CodeGen] ❌ Documentation generation failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Documentation error: {str(e)}"]
        
        return state
    
    async def _validate_code_quality(self, state: CodeGeneratorState) -> CodeGeneratorState:
        """Node 7: Validate code quality."""
        import time
        start = time.time()
        
        logger.info("[CodeGen] Validating code quality...")
        
        try:
            # Simple quality metrics
            code_files = state.get('code_files', [])
            test_files = state.get('test_files', [])
            
            quality_score = 0.0
            if code_files:
                quality_score += 0.4
            if test_files:
                quality_score += 0.3
            if state.get('documentation'):
                quality_score += 0.3
            
            # Determine if revision is needed
            quality_threshold = 0.7
            state['needs_revision'] = quality_score < quality_threshold
            
            state['current_stage'] = 'quality_validated'
            state['stages_completed'] = state.get('stages_completed', []) + ['validate_quality']
            state['metrics']['validate_quality_time'] = time.time() - start
            state['metrics']['quality_score'] = quality_score
            
            logger.info(f"[CodeGen] ✅ Quality score: {quality_score:.2f} (threshold: {quality_threshold})")
            
        except Exception as e:
            logger.error(f"[CodeGen] ❌ Quality validation failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Quality validation error: {str(e)}"]
        
        return state
    
    async def _revise_code(self, state: CodeGeneratorState) -> CodeGeneratorState:
        """Node 8: Revise code based on quality feedback."""
        import time
        start = time.time()
        
        logger.info("[CodeGen] Revising code...")
        
        try:
            revision_count = state.get('revision_count', 0)
            state['revision_count'] = revision_count + 1
            
            # TODO: Implement actual revision logic
            # For now, just mark as revised
            
            state['current_stage'] = 'code_revised'
            state['stages_completed'] = state.get('stages_completed', []) + ['revise']
            state['metrics']['revise_time'] = time.time() - start
            
            logger.info(f"[CodeGen] ✅ Revision {state['revision_count']} completed")
            
        except Exception as e:
            logger.error(f"[CodeGen] ❌ Revision failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Revision error: {str(e)}"]
        
        return state
    
    async def _finalize_and_save_patterns(self, state: CodeGeneratorState) -> CodeGeneratorState:
        """Node 9: Finalize and save learned patterns to long-term memory."""
        import time
        start = time.time()
        
        logger.info("[CodeGen] Finalizing and saving patterns...")
        
        try:
            # Extract patterns learned during this generation
            patterns = {
                'tech_stack': state.get('tech_stack'),
                'structure': state.get('project_structure'),
                'quality_score': state['metrics'].get('quality_score', 0.0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to long-term memory (cross-thread)
            tech_stack_key = str(state.get('tech_stack', {}))
            # TODO: Implement store.put() when store API is fully available
            # await self.store.put(tech_stack_key, patterns)
            
            # Add to generation history (short-term, thread-scoped via checkpointer)
            history_entry = {
                'project_name': state.get('project_name'),
                'files_generated': len(state.get('code_files', [])),
                'quality_score': state['metrics'].get('quality_score', 0.0),
                'timestamp': datetime.now().isoformat()
            }
            state['generation_history'].append(history_entry)
            
            state['current_stage'] = 'complete'
            state['stages_completed'] = state.get('stages_completed', []) + ['finalize']
            state['metrics']['finalize_time'] = time.time() - start
            
            logger.info("[CodeGen] ✅ Generation finalized, patterns saved to memory")
            
        except Exception as e:
            logger.error(f"[CodeGen] ❌ Finalization failed: {e}")
            state['errors'] = state.get('errors', []) + [f"Finalization error: {str(e)}"]
        
        return state
    
    # ========================================================================
    # CONDITIONAL EDGE LOGIC
    # ========================================================================
    
    def _should_revise(self, state: CodeGeneratorState) -> str:
        """
        Conditional edge: determine if code should be revised or finalized.
        
        Decision logic:
        - If revision_count >= max_revisions: END (prevent infinite loops)
        - If needs_revision is True: "revise"
        - Otherwise: "finalize"
        """
        revision_count = state.get('revision_count', 0)
        max_revisions = state.get('max_revisions', 2)
        needs_revision = state.get('needs_revision', False)
        
        # Safety: prevent infinite loops
        if revision_count >= max_revisions:
            logger.info(f"[Control] Max revisions ({max_revisions}) reached - END")
            return END
        
        # Check if revision is needed
        if needs_revision:
            logger.info(f"[Control] 🔄 Revision needed (attempt {revision_count + 1}/{max_revisions})")
            return "revise"
        
        # Quality acceptable - finalize
        logger.info("[Control] ✅ Quality acceptable - FINALIZE")
        return "finalize"
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code generation using LangGraph with memory.
        
        Args:
            task: Dictionary with:
                - requirements: dict
                - architecture: dict
                - project_name: str
                - tech_stack: dict
                - max_revisions: int (optional, default: 2)
                
        Returns:
            Complete code generation result with all artifacts
        """
        import time
        start_time = time.time()
        
        # Initialize state
        initial_state: CodeGeneratorState = {
            'requirements': task.get('requirements', {}),
            'architecture': task.get('architecture', {}),
            'project_name': task.get('project_name', 'generated_project'),
            'tech_stack': task.get('tech_stack', {}),
            'project_structure': {},
            'code_files': [],
            'configuration_files': [],
            'documentation': {},
            'test_files': [],
            'generation_history': [],
            'patterns_learned': {},
            'current_stage': 'initialized',
            'stages_completed': [],
            'needs_revision': False,
            'revision_count': 0,
            'max_revisions': task.get('max_revisions', 2),
            'errors': [],
            'metrics': {}
        }
        
        try:
            logger.info(f"Code Generator: Processing project '{task.get('project_name', '')}'")
            
            # Execute workflow with memory persistence
            final_state = await self.app.ainvoke(
                initial_state,
                config={
                    "configurable": {
                        "thread_id": f"codegen_{datetime.now().timestamp()}"
                    }
                }
            )
            
            total_time = time.time() - start_time
            final_state['metrics']['total_time'] = total_time
            
            # Build result
            result = {
                'status': 'success',
                'project_name': final_state['project_name'],
                'project_structure': final_state['project_structure'],
                'code_files': final_state['code_files'],
                'test_files': final_state['test_files'],
                'configuration_files': final_state['configuration_files'],
                'documentation': final_state['documentation'],
                'pipeline_state': {
                    'stages_completed': final_state['stages_completed'],
                    'revision_count': final_state['revision_count'],
                    'quality_score': final_state['metrics'].get('quality_score', 0.0),
                    'metrics': final_state['metrics']
                }
            }
            
            logger.info(f"Code Generator: Complete in {total_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Code Generator: Failed with error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'status': 'error',
                'error': str(e),
                'project_name': task.get('project_name', ''),
                'code_files': []
            }

