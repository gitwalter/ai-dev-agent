"""
Query Analyst Agent for RAG Swarm

This agent specializes in understanding and expanding user queries for optimal retrieval.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.core.enhanced_base_agent import EnhancedBaseAgent
from models.config import AgentConfig

# LangChain imports for LLM
try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logger = logging.getLogger(__name__)


class QueryAnalystAgent(EnhancedBaseAgent):
    """
    Query Analyst Agent - Expert at understanding and expanding queries.
    
    Responsibilities:
    - Query intent classification
    - Query rewriting and expansion
    - Key concept extraction
    - Search strategy recommendation
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize Query Analyst Agent."""
        if config is None:
            config = AgentConfig(
                agent_id="query_analyst",
                name="Query Analyst Agent",
                role="query_analysis",
                description="Analyzes and expands user queries for optimal retrieval",
                capabilities=[
                    "intent_classification",
                    "query_rewriting",
                    "concept_extraction",
                    "strategy_recommendation"
                ]
            )
        
        super().__init__(config)
        self.analysis_stats = {
            'queries_analyzed': 0,
            'avg_variants_generated': 0,
            'avg_concepts_extracted': 0
        }
        
        logger.info(f"✅ {self.name} initialized")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a user query and provide comprehensive query intelligence.
        
        Args:
            task: Dictionary containing:
                - query: str - The user's original query
                - context: Optional[Dict] - Additional context
                
        Returns:
            Dictionary with query analysis results
        """
        query = task.get('query', '')
        
        if not query:
            return {
                'status': 'error',
                'error': 'No query provided',
                'agent_id': self.config.agent_id
            }
        
        logger.info(f"🔍 {self.name}: Analyzing query: '{query[:60]}...'")
        
        try:
            # Perform query analysis
            analysis = await self._analyze_query_with_llm(query)
            
            # Update stats
            self.analysis_stats['queries_analyzed'] += 1
            self.analysis_stats['avg_variants_generated'] = (
                (self.analysis_stats['avg_variants_generated'] * (self.analysis_stats['queries_analyzed'] - 1) + 
                 len(analysis['rewritten_queries'])) / self.analysis_stats['queries_analyzed']
            )
            self.analysis_stats['avg_concepts_extracted'] = (
                (self.analysis_stats['avg_concepts_extracted'] * (self.analysis_stats['queries_analyzed'] - 1) + 
                 len(analysis['key_concepts'])) / self.analysis_stats['queries_analyzed']
            )
            
            logger.info(f"✅ {self.name}: Analysis complete - Intent: {analysis['intent']}, "
                       f"Variants: {len(analysis['rewritten_queries'])}, "
                       f"Concepts: {len(analysis['key_concepts'])}")
            
            return {
                'status': 'success',
                'agent_id': self.config.agent_id,
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis,
                'stats': self.analysis_stats
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Analysis failed: {e}")
            return {
                'status': 'error',
                'agent_id': self.config.agent_id,
                'error': str(e),
                'fallback_analysis': self._fallback_analysis(query)
            }
    
    async def _analyze_query_with_llm(self, query: str) -> Dict[str, Any]:
        """Use LLM to perform comprehensive query analysis."""
        
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, using fallback analysis")
            return self._fallback_analysis(query)
        
        # Get API key
        api_key = self._get_gemini_api_key()
        if not api_key:
            logger.warning("No Gemini API key, using fallback analysis")
            return self._fallback_analysis(query)
        
        # Create LLM (using latest Gemini model)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Latest Gemini model
            google_api_key=api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Create analysis prompt
        system_prompt = """You are a Query Analysis Expert for a RAG (Retrieval Augmented Generation) system.

Your task is to analyze user queries and provide:
1. Intent classification (factual, conceptual, procedural, multi-hop, exploratory)
2. 3-5 rewritten query variants optimized for semantic search
3. Key concepts/terms that should be searched
4. Recommended search strategy (focused, broad, multi-stage)
5. Complexity score (0.0-1.0)

Respond in this exact JSON format:
{
    "intent": "factual|conceptual|procedural|multi-hop|exploratory",
    "rewritten_queries": ["variant1", "variant2", "variant3"],
    "key_concepts": ["concept1", "concept2", "concept3"],
    "search_strategy": "focused|broad|multi-stage",
    "complexity": 0.5,
    "reasoning": "Brief explanation"
}"""
        
        user_prompt = f"""Analyze this query:

"{query}"

Provide comprehensive query analysis in JSON format."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Call LLM
        response = await llm.ainvoke(messages)
        
        # Parse response
        import json
        import re
        
        # Extract JSON from response (handle markdown code blocks)
        response_text = response.content
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        elif response_text.startswith('```') and response_text.endswith('```'):
            response_text = response_text.strip('```').strip()
        
        try:
            analysis_data = json.loads(response_text)
        except json.JSONDecodeError:
            logger.warning("LLM response not valid JSON, using fallback")
            return self._fallback_analysis(query)
        
        # Ensure all fields are present
        analysis = {
            'original_query': query,
            'intent': analysis_data.get('intent', 'factual'),
            'rewritten_queries': analysis_data.get('rewritten_queries', [query]),
            'key_concepts': analysis_data.get('key_concepts', []),
            'search_strategy': analysis_data.get('search_strategy', 'focused'),
            'complexity': float(analysis_data.get('complexity', 0.5)),
            'reasoning': analysis_data.get('reasoning', '')
        }
        
        return analysis
    
    def _fallback_analysis(self, query: str) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available."""
        
        # Simple heuristic-based analysis
        query_lower = query.lower()
        words = query_lower.split()
        
        # Intent classification (simple heuristics)
        if any(word in query_lower for word in ['what is', 'define', 'meaning', 'explain']):
            intent = 'conceptual'
        elif any(word in query_lower for word in ['how to', 'how do', 'steps', 'process']):
            intent = 'procedural'
        elif any(word in query_lower for word in ['and', 'compare', 'difference', 'relationship']):
            intent = 'multi-hop'
        elif '?' in query:
            intent = 'factual'
        else:
            intent = 'exploratory'
        
        # Generate query variants (simple)
        rewritten_queries = [
            query,  # Original
            query.replace('?', '').strip(),  # Without question mark
            ' '.join(words[:10]) if len(words) > 10 else query  # Truncated if long
        ]
        
        # Extract key concepts (just split words, filter short ones)
        key_concepts = [word for word in words if len(word) > 3][:5]
        
        # Search strategy based on complexity
        complexity = min(len(words) / 20.0, 1.0)
        if complexity < 0.3:
            search_strategy = 'focused'
        elif complexity < 0.7:
            search_strategy = 'broad'
        else:
            search_strategy = 'multi-stage'
        
        return {
            'original_query': query,
            'intent': intent,
            'rewritten_queries': rewritten_queries[:3],
            'key_concepts': key_concepts,
            'search_strategy': search_strategy,
            'complexity': complexity,
            'reasoning': 'Fallback heuristic-based analysis'
        }
    
    def _get_gemini_api_key(self) -> Optional[str]:
        """Get Gemini API key from environment or secrets."""
        import os
        from pathlib import Path
        
        # Try environment variable first
        api_key = os.environ.get('GEMINI_API_KEY')
        if api_key:
            return api_key
        
        # Try Streamlit secrets
        try:
            secrets_path = Path.home() / '.streamlit' / 'secrets.toml'
            if secrets_path.exists():
                with open(secrets_path, 'r') as f:
                    for line in f:
                        if line.startswith('GEMINI_API_KEY'):
                            # Parse: GEMINI_API_KEY = "value" or GEMINI_API_KEY="value"
                            api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            if api_key:
                                return api_key
        except Exception as e:
            logger.warning(f"Could not read secrets.toml: {e}")
        
        return None
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate that task has required query field."""
        if not isinstance(task, dict):
            logger.error(f"❌ {self.name}: Task must be a dictionary")
            return False
        
        if 'query' not in task:
            logger.error(f"❌ {self.name}: Task must contain 'query' field")
            return False
        
        if not isinstance(task['query'], str) or not task['query'].strip():
            logger.error(f"❌ {self.name}: Query must be a non-empty string")
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get query analysis statistics."""
        return {
            'agent_id': self.config.agent_id,
            'agent_name': self.name,
            'stats': self.analysis_stats,
            'timestamp': datetime.now().isoformat()
        }

