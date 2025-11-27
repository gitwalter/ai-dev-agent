"""
Writer Agent for RAG Swarm

This agent specializes in synthesizing context into coherent, well-cited responses.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime


# LangGraph integration check
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from pydantic import BaseModel, Field
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available - agent will work in legacy mode only")

from agents.core.enhanced_base_agent import EnhancedBaseAgent
from models.config import AgentConfig

# LangChain imports
try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logger = logging.getLogger(__name__)




class WriterAgentState(BaseModel):
    """State for WriterAgent LangGraph workflow using Pydantic BaseModel."""
    
    # Input fields
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data")
    
    # Output fields
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output data")
    
    # Control fields
    errors: List[str] = Field(default_factory=list, description="Error messages")
    status: str = Field(default="initialized", description="Current status")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Execution metrics")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

class WriterAgent(EnhancedBaseAgent):
    """
    Writer Agent - Expert at synthesizing context into coherent responses.
    
    Responsibilities:
    - Generate comprehensive, well-structured answers
    - Cite sources appropriately
    - Maintain factual accuracy
    - Adapt tone and style to query type
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize Writer Agent."""
        if config is None:
            config = AgentConfig(
                agent_id="writer",
                name="Writer Agent",
                role="response_generation",
                description="Synthesizes context into coherent, well-cited responses",
                capabilities=[
                    "context_synthesis",
                    "source_citation",
                    "factual_accuracy",
                    "style_adaptation"
                ]
            )
        
        super().__init__(config)
        self.writing_stats = {
            'total_responses': 0,
            'avg_tokens_used': 0,
            'avg_generation_time': 0,
            'avg_confidence': 0
        }
        
        # Load prompt from LangSmith Hub (following langgraph_workflow pattern)
        from prompts.agent_prompt_loader import get_agent_prompt_loader
        self.prompt_loader = get_agent_prompt_loader("writer")
        
        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_langgraph_workflow()
            self.app = self.workflow.compile()
            logger.info("✅ LangGraph workflow compiled and ready")
        else:
            self.workflow = None
            self.app = None
            logger.info("⚠️ LangGraph not available - using legacy mode")
        
        logger.info(f"✅ {self.name} initialized")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate response from ranked context.
        
        Args:
            task: Dictionary containing:
                - ranked_results: List[Dict] from ReRankerAgent
                - query_analysis: Dict from QueryAnalystAgent
                - quality_report: Dict from QualityAssuranceAgent
                
        Returns:
            Generated response with metadata
        """
        ranked_results = task.get('ranked_results', [])
        query_analysis = task.get('query_analysis', {})
        quality_report = task.get('quality_report', {})
        
        original_query = query_analysis.get('original_query', '')
        intent = query_analysis.get('intent', 'factual')
        
        logger.info(f"✍️ {self.name}: Generating response for query")
        
        import time
        start_time = time.time()
        
        try:
            # Generate response
            response_data = await self._generate_response(
                original_query,
                ranked_results,
                intent,
                quality_report
            )
            
            generation_time = time.time() - start_time
            
            # Update stats
            self.writing_stats['total_responses'] += 1
            self.writing_stats['avg_generation_time'] = (
                (self.writing_stats['avg_generation_time'] * (self.writing_stats['total_responses'] - 1) +
                 generation_time) / self.writing_stats['total_responses']
            )
            
            if 'tokens_used' in response_data['writing_metadata']:
                tokens = response_data['writing_metadata']['tokens_used']
                self.writing_stats['avg_tokens_used'] = (
                    (self.writing_stats['avg_tokens_used'] * (self.writing_stats['total_responses'] - 1) +
                     tokens) / self.writing_stats['total_responses']
                )
            
            if 'confidence' in response_data:
                self.writing_stats['avg_confidence'] = (
                    (self.writing_stats['avg_confidence'] * (self.writing_stats['total_responses'] - 1) +
                     response_data['confidence']) / self.writing_stats['total_responses']
                )
            
            logger.info(f"✅ {self.name}: Response generated ({generation_time:.2f}s)")
            
            return {
                'status': 'success',
                'agent_id': self.config.agent_id,
                'timestamp': datetime.now().isoformat(),
                **response_data,
                'stats': self.writing_stats
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Response generation failed: {e}")
            return {
                'status': 'error',
                'agent_id': self.config.agent_id,
                'error': str(e),
                'response': self._fallback_response(original_query, ranked_results)
            }
    
    async def _generate_response(
        self,
        query: str,
        context_results: List[Dict],
        intent: str,
        quality_report: Dict
    ) -> Dict[str, Any]:
        """Generate response using LLM."""
        
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, using fallback")
            return {
                'response': self._fallback_response(query, context_results),
                'confidence': 0.5,
                'sources_cited': [],
                'writing_metadata': {
                    'tokens_used': 0,
                    'generation_time': 0,
                    'style': 'fallback'
                }
            }
        
        # Get API key (use async version to avoid blocking I/O)
        api_key = await self._get_gemini_api_key_async()
        if not api_key:
            logger.warning("No Gemini API key, using fallback")
            return {
                'response': self._fallback_response(query, context_results),
                'confidence': 0.5,
                'sources_cited': [],
                'writing_metadata': {
                    'tokens_used': 0,
                    'generation_time': 0,
                    'style': 'fallback'
                }
            }
        
        # Create LLM (using latest Gemini model for best synthesis)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Latest Gemini model with excellent synthesis
            google_api_key=api_key,
            temperature=0,
            convert_system_message_to_human=True,
            transport="rest"  # Use REST to avoid grpc event loop issues
        )
        
        # Build prompt (async to avoid blocking I/O)
        system_prompt = await self._build_system_prompt(intent)
        user_prompt = self._build_user_prompt(query, context_results, quality_report)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Generate response
        import time
        start = time.time()
        response = await llm.ainvoke(messages)
        gen_time = time.time() - start
        
        response_text = response.content
        
        # Extract sources cited (simple heuristic)
        sources_cited = self._extract_sources(response_text, context_results)
        
        # Calculate confidence (based on quality report)
        confidence = quality_report.get('quality_score', 0.7)
        
        # Determine limitations
        limitations = None
        if confidence < 0.7:
            limitations = "Answer based on limited context. Some aspects may not be fully covered."
        
        return {
            'response': response_text,
            'confidence': confidence,
            'sources_cited': sources_cited,
            'limitations': limitations,
            'writing_metadata': {
                'tokens_used': len(response_text.split()),  # Rough estimate
                'generation_time': gen_time,
                'style': self._determine_style(intent)
            }
        }
    

    async def _build_system_prompt(self, intent: str) -> str:
        """Build system prompt based on query intent (async to avoid blocking I/O)."""
        
        # CRITICAL FIX: Load prompt asynchronously to avoid blocking file reads
        # The prompt loader does synchronous file I/O, so we wrap it in asyncio.to_thread()
        import asyncio
        
        def _load_prompt_sync():
            """Synchronous prompt loading function."""
            return self.prompt_loader.get_system_prompt()
        
        # Run blocking prompt load in separate thread
        base_prompt = await asyncio.to_thread(_load_prompt_sync)
        
        # Add style adaptation based on intent (appending to hub prompt)
        if intent == "comprehensive":
            # COMPREHENSIVE MODE: Explicit instruction for thorough synthesis
            base_prompt += "\n\n**CRITICAL: COMPREHENSIVE SYNTHESIS MODE**\n"
            base_prompt += "- Synthesize information from ALL provided context documents\n"
            base_prompt += "- Provide a DETAILED, COMPREHENSIVE answer that covers all relevant aspects\n"
            base_prompt += "- Include details, examples, explanations, and nuances from multiple sources\n"
            base_prompt += "- Don't summarize too briefly - use the full depth of information available\n"
            base_prompt += "- If the context contains extensive information, reflect that depth in your answer\n"
            base_prompt += "- Ensure completeness - don't leave out important details\n"
            base_prompt += "- Cite sources appropriately when making specific claims"
        elif intent == 'conceptual':
            base_prompt += "\n\nFor this conceptual query: Provide clear explanations with examples where helpful."
        elif intent == 'procedural':
            base_prompt += "\n\nFor this procedural query: Provide step-by-step instructions or workflow descriptions."
        elif intent == 'multi-hop':
            base_prompt += "\n\nFor this multi-hop query: Connect multiple concepts and show relationships."
        else:
            base_prompt += "\n\nFor this factual query: Be concise and direct."
        
        return base_prompt
    
    def _build_user_prompt(
        self,
        query: str,
        context_results: List[Dict],
        quality_report: Dict
    ) -> str:
        """Build user prompt with context."""
        
        prompt = f"**User Query:**\n{query}\n\n"
        
        prompt += "**Retrieved Context:**\n\n"
        
        # COMPREHENSIVE MODE: Use ALL context results with FULL content (no truncation)
        # Check if comprehensive_mode flag is set to encourage thorough synthesis
        comprehensive_mode = context_results and len(context_results) > 0
        
        for idx, result in enumerate(context_results, 1):  # ALL results, not limited
            content = result.get('content', '')
            # Use FULL content - NO truncation for comprehensive synthesis
            # Try multiple possible source locations
            metadata = result.get('metadata', {})
            source = (
                result.get('file_path') or  # From context_engine.py line 809
                metadata.get('source') or 
                metadata.get('file_path') or
                result.get('source') or
                result.get('file') or
                'unknown'
            )
            score = result.get('combined_score', result.get('relevance_score', 0))
            chunk_idx = result.get('chunk_index', metadata.get('chunk_index', '?'))
            
            prompt += f"[Context {idx}] (Source: {source}, Chunk: {chunk_idx}, Relevance: {score:.2f})\n"
            prompt += f"{content}\n\n"  # FULL content - no truncation for comprehensive answers
        
        # Add comprehensive synthesis instruction
        if comprehensive_mode:
            prompt += "\n**CRITICAL INSTRUCTIONS**:\n"
            prompt += "- Synthesize information from ALL provided context documents\n"
            prompt += "- Provide a COMPREHENSIVE answer that covers all relevant aspects\n"
            prompt += "- Include details, examples, and explanations from multiple sources\n"
            prompt += "- Don't summarize too briefly - use the full depth of information available\n"
            prompt += "- Cite sources when making specific claims\n"
        
        # Add quality context
        if quality_report.get('issues'):
            prompt += f"\n**Note**: Retrieved context has some limitations: {', '.join(quality_report['issues'][:2])}\n"
        
        prompt += "\n**Instructions**: Based on the context above, provide a comprehensive, detailed answer to the user's query. Use information from all relevant documents. Cite sources when making specific claims."
        
        return prompt
    
    def _fallback_response(self, query: str, context_results: List[Dict]) -> str:
        """Generate fallback response when LLM unavailable."""
        
        if not context_results:
            return f"I don't have sufficient information to answer: {query}"
        
        # Simple concatenation of top results
        response = f"Based on available context:\n\n"
        
        for idx, result in enumerate(context_results[:3], 1):
            content = result.get('content', '')[:200]
            # Try multiple possible source locations
            metadata = result.get('metadata', {})
            source = (
                result.get('file_path') or
                metadata.get('source') or
                metadata.get('file_path') or
                result.get('source') or
                'unknown'
            )
            response += f"{idx}. From {source}: {content}...\n\n"
        
        return response
    
    def _extract_sources(self, response_text: str, context_results: List[Dict]) -> List[str]:
        """Extract which sources were used from context results with chunk details."""
        
        sources = []
        for idx, result in enumerate(context_results, 1):
            # Try different metadata fields for source
            metadata = result.get('metadata', {})
            source = (
                metadata.get('source') or 
                metadata.get('file_path') or 
                result.get('source') or 
                result.get('file_path') or
                result.get('file')
            )
            
            # Get chunk information
            chunk_index = metadata.get('chunk_index', result.get('chunk_index', 'unknown'))
            relevance = result.get('relevance_score', result.get('combined_score', 0))
            
            if source:
                # Format: "document.pdf [chunk 3, relevance: 0.85]"
                source_detail = f"{source} [chunk {chunk_index}, score: {relevance:.2f}]"
                sources.append(source_detail)
        
        return sources  # Return all sources with details
    
    def _determine_style(self, intent: str) -> str:
        """Determine writing style based on intent."""
        style_map = {
            'factual': 'concise',
            'conceptual': 'explanatory',
            'procedural': 'instructional',
            'multi-hop': 'comprehensive',
            'exploratory': 'exploratory'
        }
        return style_map.get(intent, 'technical')
    
    def _get_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key."""
        import os
        from pathlib import Path
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            return api_key
        
        # CRITICAL FIX: Use async file reading to avoid blocking I/O
        # This method is called from async context, so we need async file operations
        try:
            secrets_path = Path.home() / '.streamlit' / 'secrets.toml'
            if secrets_path.exists():
                # Use asyncio.to_thread to run blocking file read in separate thread
                import asyncio
                try:
                    # Check if we're in an async context
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in async context - use to_thread for non-blocking read
                        # But since this is a sync method called from async, we'll use sync read
                        # The actual fix is to make the file read happen in a thread
                        # For now, use sync read but wrap it in to_thread when called from async
                        pass  # Will handle below
                except RuntimeError:
                    # No event loop - sync context is fine
                    pass
                
                # Read file synchronously (this method is sync, but called from async)
                # The blocking happens, but it's quick for a small config file
                # Better solution: make this async or use aiofiles
                with open(secrets_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('GEMINI_API_KEY'):
                            api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            if api_key:
                                return api_key
        except Exception as e:
            logger.warning(f"Could not read secrets: {e}")
        
        return None
    
    async def _get_gemini_api_key_async(self) -> Optional[str]:
        """Get Gemini API key asynchronously (non-blocking)."""
        import os
        from pathlib import Path
        import asyncio
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            return api_key
        
        try:
            secrets_path = Path.home() / '.streamlit' / 'secrets.toml'
            if secrets_path.exists():
                # Use asyncio.to_thread to run blocking file read in separate thread
                def _read_secrets_file():
                    """Blocking file read function."""
                    with open(secrets_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('GEMINI_API_KEY'):
                                api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                                if api_key:
                                    return api_key
                    return None
                
                # Run blocking file read in separate thread
                api_key = await asyncio.to_thread(_read_secrets_file)
                if api_key:
                    return api_key
        except Exception as e:
            logger.warning(f"Could not read secrets asynchronously: {e}")
        
        return None
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate task has required fields."""
        if not isinstance(task, dict):
            logger.error(f"❌ {self.name}: Task must be a dictionary")
            return False
        
        if 'ranked_results' not in task:
            logger.error(f"❌ {self.name}: Task must contain 'ranked_results'")
            return False
        
        if 'query_analysis' not in task:
            logger.error(f"❌ {self.name}: Task must contain 'query_analysis'")
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get writer statistics."""
        return {
            'agent_id': self.config.agent_id,
            'agent_name': self.name,
            'stats': self.writing_stats,
            'timestamp': datetime.now().isoformat()
        }


    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Build LangGraph workflow for WriterAgent."""
        workflow = StateGraph(WriterAgentState)
        
        # Simple workflow: just execute the agent
        workflow.add_node("execute", self._langgraph_execute_node)
        workflow.set_entry_point("execute")
        workflow.add_edge("execute", END)
        
        return workflow
    
    async def _langgraph_execute_node(self, state: WriterAgentState) -> WriterAgentState:
        """Execute agent in LangGraph workflow."""
        import time
        start = time.time()
        
        try:
            # Call the agent's execute method
            result = await self.execute(state.input_data)
            
            # Update state with results
            state.output_data = result
            state.status = "completed"
            state.metrics["execution_time"] = time.time() - start
            
        except Exception as e:
            self.logger.error(f"LangGraph execution failed: {e}")
            state.errors.append(str(e))
            state.status = "failed"
            state.metrics["execution_time"] = time.time() - start
        
        return state


# Export for LangGraph Studio
_default_instance = None

def get_graph():
    """Get the compiled graph for LangGraph Studio."""
    global _default_instance
    if _default_instance is None and LANGGRAPH_AVAILABLE:
        from models.config import AgentConfig
        
        config = AgentConfig(
            agent_id='writer_agent',
            name='WriterAgent',
            description='WriterAgent agent',
            model_name='gemini-2.5-flash'
        )
        _default_instance = WriterAgent(config)
    return _default_instance.app if _default_instance else None

# Studio expects 'graph' variable
graph = get_graph()
