"""
Writer Agent for RAG Swarm

This agent specializes in synthesizing context into coherent, well-cited responses.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

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
        
        # Get API key
        api_key = self._get_gemini_api_key()
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
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Build prompt
        system_prompt = self._build_system_prompt(intent)
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
    
    def _build_system_prompt(self, intent: str) -> str:
        """Build system prompt based on query intent."""
        
        base_prompt = """You are an expert technical writer and knowledge synthesizer.

Your task is to generate comprehensive, accurate answers based on provided context.

Guidelines:
1. **Accuracy**: Only use information from the provided context. Never hallucinate or make up facts.
2. **Citations**: Reference sources when making specific claims (e.g., "According to file.py...")
3. **Clarity**: Write clearly and structure your response logically
4. **Completeness**: Address all aspects of the question if context allows
5. **Honesty**: If context doesn't fully answer the question, acknowledge limitations"""
        
        if intent == 'conceptual':
            base_prompt += "\n6. **Style**: Provide clear explanations with examples where helpful"
        elif intent == 'procedural':
            base_prompt += "\n6. **Style**: Provide step-by-step instructions or workflow descriptions"
        elif intent == 'multi-hop':
            base_prompt += "\n6. **Style**: Connect multiple concepts and show relationships"
        else:
            base_prompt += "\n6. **Style**: Be concise and direct for factual queries"
        
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
        
        for idx, result in enumerate(context_results[:10], 1):  # Top 10
            content = result.get('content', '')
            source = result.get('source', result.get('file', 'unknown'))
            score = result.get('combined_score', 0)
            
            prompt += f"[Context {idx}] (Relevance: {score:.2f}, Source: {source})\n"
            prompt += f"{content[:500]}...\n\n"  # First 500 chars
        
        # Add quality context
        if quality_report.get('issues'):
            prompt += f"\n**Note**: Retrieved context has some limitations: {', '.join(quality_report['issues'][:2])}\n"
        
        prompt += "\n**Instructions**: Based on the context above, provide a comprehensive answer to the user's query. Cite sources when making specific claims."
        
        return prompt
    
    def _fallback_response(self, query: str, context_results: List[Dict]) -> str:
        """Generate fallback response when LLM unavailable."""
        
        if not context_results:
            return f"I don't have sufficient information to answer: {query}"
        
        # Simple concatenation of top results
        response = f"Based on available context:\n\n"
        
        for idx, result in enumerate(context_results[:3], 1):
            content = result.get('content', '')[:200]
            source = result.get('source', 'unknown')
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
        
        try:
            secrets_path = Path.home() / '.streamlit' / 'secrets.toml'
            if secrets_path.exists():
                with open(secrets_path, 'r') as f:
                    for line in f:
                        if line.startswith('GEMINI_API_KEY'):
                            api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            if api_key:
                                return api_key
        except Exception as e:
            logger.warning(f"Could not read secrets: {e}")
        
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

