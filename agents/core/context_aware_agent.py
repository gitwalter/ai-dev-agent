#!/usr/bin/env python3
"""
Context-Aware Agent
==================

Agent base class with integrated ContextEngine for RAG-enhanced decision-making.

**CRITICAL INTEGRATION**: All agents that need semantic search, pattern learning,
and project intelligence should inherit from this class.

Features:
- Semantic search using ContextEngine
- Pattern learning and error solution access
- Import suggestions based on learned patterns
- Project intelligence for informed decisions
- LangChain retriever compatibility

Created: 2025-01-08
Sprint: US-RAG-001 Phase 5
Priority: HIGH
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import base agent
from agents.core.enhanced_base_agent import EnhancedBaseAgent
from agents.core.base_agent import AgentConfig

# Import context engine and config
try:
    from context.context_engine import ContextEngine
    from models.config import ContextConfig
    CONTEXT_ENGINE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ContextEngine not available: {e}")
    CONTEXT_ENGINE_AVAILABLE = False
    ContextEngine = None
    ContextConfig = None

# Import LangChain for LangSmith tracing
try:
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.callbacks import BaseCallbackHandler
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LangChain not available - LangSmith tracing disabled: {e}")
    LANGCHAIN_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


class ContextAwareAgent(EnhancedBaseAgent):
    """
    Agent with integrated ContextEngine for RAG-enhanced decision-making.
    
    This agent has access to:
    - Semantic search across the entire codebase
    - Pattern learning from existing code
    - Error solution knowledge base
    - Import suggestions based on learned patterns
    - Project intelligence and statistics
    
    All specialized agents that need context should inherit from this class.
    """
    
    def __init__(self, config: AgentConfig, gemini_client=None, context_engine=None):
        """
        Initialize context-aware agent.
        
        Args:
            config: Agent configuration
            gemini_client: Gemini client instance
            context_engine: Shared ContextEngine instance (optional)
        """
        super().__init__(config, gemini_client)
        
        # ContextEngine integration
        self.context_engine = None
        self.retriever = None
        self.context_available = False
        
        if CONTEXT_ENGINE_AVAILABLE:
            try:
                # Use provided ContextEngine or create new one
                if context_engine:
                    self.context_engine = context_engine
                    logger.info(f"✅ {self.name}: Using shared ContextEngine")
                else:
                    # Create default ContextEngine
                    context_config = ContextConfig()
                    self.context_engine = ContextEngine(context_config)
                    logger.info(f"✅ {self.name}: Created new ContextEngine")
                
                # Create LangChain retriever if vector store available
                if self.context_engine.vector_store:
                    self.retriever = self.context_engine.vector_store.as_retriever(
                        search_kwargs={"k": 5}
                    )
                    logger.info(f"✅ {self.name}: LangChain retriever created")
                
                self.context_available = True
                
            except Exception as e:
                logger.error(f"❌ {self.name}: Failed to initialize ContextEngine: {e}")
                self.context_engine = None
                self.context_available = False
        else:
            logger.warning(f"⚠️ {self.name}: ContextEngine not available, operating without context")
        
        # Context usage statistics
        self.context_stats = {
            'searches_performed': 0,
            'patterns_retrieved': 0,
            'errors_solved': 0,
            'imports_suggested': 0,
            'total_context_time': 0.0
        }
        
        logger.info(f"🤖 Context-Aware Agent '{config.agent_id}' initialized")
    
    async def execute_with_context(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task with advanced RAG retrieval using best practices.
        
        Implements multi-stage retrieval with:
        - Query rewriting for better semantic matching
        - Hybrid search (dense + sparse retrieval)
        - Multi-stage concept extraction
        - Smart deduplication and re-ranking
        
        Sources:
        - https://masteringllm.medium.com/best-practices-for-rag-pipeline-8c12a8096453
        - https://cloud.google.com/blog/products/ai-machine-learning/optimizing-rag-retrieval
        
        Args:
            task: Task to execute with context enhancement
            
        Returns:
            Execution results with context information
        """
        if not self.context_available or not self.context_engine:
            logger.warning(f"⚠️ {self.name}: Context not available, executing without context")
            return await self.execute(task)
        
        try:
            start_time = datetime.now()
            
            # 1. Extract and rewrite query for better retrieval
            original_query = self._extract_query_from_task(task)
            
            # 2. Advanced multi-stage semantic search for better context
            all_search_results = []
            if original_query:
                # Stage 1: Query rewriting (improves semantic matching)
                rewritten_queries = self._rewrite_query(original_query)
                logger.info(f"🔄 Query rewriting: {len(rewritten_queries)} variants generated")
                
                # Stage 2: Retrieve with multiple query variants - INCREASED limits!
                for query_variant in rewritten_queries[:5]:  # Top 5 variants (was 3)
                    variant_results = await self.context_engine.semantic_search(query_variant, limit=15)  # 15 per query (was 5)
                    all_search_results.extend(variant_results.get('results', []))
                    self.context_stats['searches_performed'] += 1
                
                logger.info(f"🔍 Stage 1 (Query variants): Retrieved {len(all_search_results)} results")
                
                # Stage 3: Extract key concepts and search again - INCREASED!
                key_concepts = self._extract_key_concepts(original_query)
                for concept in key_concepts[:5]:  # Top 5 concepts (was 3)
                    concept_results = await self.context_engine.semantic_search(concept, limit=15)  # 15 per concept (was 5)
                    all_search_results.extend(concept_results.get('results', []))
                    self.context_stats['searches_performed'] += 1
                
                logger.info(f"🔍 Stage 2 (Key concepts): Total {len(all_search_results)} results")
                
                # Stage 4: Smart deduplication and re-ranking
                search_results = self._deduplicate_and_rerank(all_search_results, original_query)
                logger.info(f"🔍 Final: {len(search_results)} unique, re-ranked results")
            else:
                search_results = []
            
            # 3. Get file-specific context if file path provided
            file_context = None
            file_path = task.get('file_path', '')
            if file_path:
                file_context = self.context_engine.get_context_for_file(file_path)
                if file_context:
                    logger.info(f"📄 {self.name}: Retrieved context for {file_path}")
            
            # 4. Get import suggestions based on patterns
            import_suggestions = []
            if file_path:
                import_suggestions = self.context_engine.get_import_suggestions(file_path)
                if import_suggestions:
                    self.context_stats['imports_suggested'] += len(import_suggestions)
                    logger.info(f"📦 {self.name}: Generated {len(import_suggestions)} import suggestions")
            
            # 5. Get project intelligence summary
            project_intelligence = self.context_engine.get_project_intelligence_summary()
            
            # 6. Build comprehensive context data
            context_data = {
                'semantic_search_results': search_results if isinstance(search_results, list) else search_results.get('results', []) if search_results else [],
                'search_results': search_results if isinstance(search_results, list) else search_results.get('results', []) if search_results else [],
                'search_type': 'multi_stage_semantic',
                'total_found': len(search_results) if isinstance(search_results, list) else search_results.get('total_found', 0) if search_results else 0,
                'file_context': file_context,
                'import_suggestions': import_suggestions,
                'project_intelligence': project_intelligence,
                'context_retrieval_time': (datetime.now() - start_time).total_seconds()
            }
            
            # 7. Enhance task with rich context
            enhanced_task = {
                **task,
                'context': context_data,
                'has_context': True,
                'context_type': 'rag_enhanced',
                'context_engine_version': 'v2.0'
            }
            
            # 8. Execute with enhanced context
            result = await self.execute(enhanced_task)
            
            # 9. Update statistics
            context_time = (datetime.now() - start_time).total_seconds()
            self.context_stats['total_context_time'] += context_time
            
            # 10. Add context information to result
            result['context_used'] = True
            result['context_stats'] = {
                'retrieval_time': context_time,
                'results_count': len(context_data['search_results']),
                'has_file_context': file_context is not None,
                'import_suggestions_count': len(import_suggestions),
                'search_type': context_data['search_type']
            }
            
            logger.info(f"✅ {self.name}: Executed with context in {context_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Context execution failed: {e}")
            # Fallback to execution without context
            logger.info(f"🔄 {self.name}: Falling back to execution without context")
            return await self.execute(task)
    
    def _extract_query_from_task(self, task: Dict[str, Any]) -> str:
        """
        Extract semantic search query from task.
        
        Args:
            task: Task dictionary
            
        Returns:
            Search query string
        """
        # Try multiple common query fields
        query_fields = ['query', 'description', 'task_description', 'requirement', 'question']
        
        for field in query_fields:
            if field in task and task[field]:
                return str(task[field])
        
        # Fallback: use task type and name
        task_type = task.get('type', '')
        task_name = task.get('name', '')
        if task_type or task_name:
            return f"{task_type} {task_name}".strip()
        
        return ""
    
    async def get_relevant_context(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get relevant context for a query using semantic search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Search results with metadata
        """
        if not self.context_available or not self.context_engine:
            logger.warning(f"⚠️ {self.name}: Context not available for search")
            return {'results': [], 'error': 'Context engine not available'}
        
        try:
            results = await self.context_engine.semantic_search(query, limit)
            self.context_stats['searches_performed'] += 1
            logger.info(f"🔍 {self.name}: Found {results.get('total_found', 0)} results for '{query}'")
            return results
        except Exception as e:
            logger.error(f"❌ {self.name}: Search failed: {e}")
            return {'results': [], 'error': str(e)}
    
    def get_file_context(self, file_path: str) -> Optional[str]:
        """
        Get context for specific file.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content if indexed, None otherwise
        """
        if not self.context_available or not self.context_engine:
            logger.warning(f"⚠️ {self.name}: Context not available for file lookup")
            return None
        
        try:
            context = self.context_engine.get_context_for_file(file_path)
            if context:
                logger.info(f"📄 {self.name}: Retrieved context for {file_path}")
            return context
        except Exception as e:
            logger.error(f"❌ {self.name}: Failed to get file context: {e}")
            return None
    
    def get_import_suggestions(self, file_path: str) -> List[str]:
        """
        Get import suggestions based on learned patterns.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of import suggestions
        """
        if not self.context_available or not self.context_engine:
            logger.warning(f"⚠️ {self.name}: Context not available for import suggestions")
            return []
        
        try:
            suggestions = self.context_engine.get_import_suggestions(file_path)
            if suggestions:
                self.context_stats['imports_suggested'] += len(suggestions)
                logger.info(f"📦 {self.name}: Generated {len(suggestions)} import suggestions")
            return suggestions
        except Exception as e:
            logger.error(f"❌ {self.name}: Failed to get import suggestions: {e}")
            return []
    
    def get_error_solution(self, error_message: str) -> List[str]:
        """
        Get solution suggestions for error message.
        
        Args:
            error_message: Error message to find solutions for
            
        Returns:
            List of solution suggestions
        """
        if not self.context_available or not self.context_engine:
            logger.warning(f"⚠️ {self.name}: Context not available for error solutions")
            return []
        
        try:
            solutions = self.context_engine.get_error_solutions(error_message)
            if solutions:
                self.context_stats['errors_solved'] += 1
                logger.info(f"💡 {self.name}: Found {len(solutions)} solutions for error")
            return solutions
        except Exception as e:
            logger.error(f"❌ {self.name}: Failed to get error solutions: {e}")
            return []
    
    def get_project_intelligence(self) -> Dict[str, Any]:
        """
        Get project intelligence summary.
        
        Returns:
            Project intelligence data
        """
        if not self.context_available or not self.context_engine:
            logger.warning(f"⚠️ {self.name}: Context not available for project intelligence")
            return {}
        
        try:
            intelligence = self.context_engine.get_project_intelligence_summary()
            logger.info(f"🧠 {self.name}: Retrieved project intelligence")
            return intelligence
        except Exception as e:
            logger.error(f"❌ {self.name}: Failed to get project intelligence: {e}")
            return {}
    
    def get_context_stats(self) -> Dict[str, Any]:
        """
        Get context usage statistics for this agent.
        
        Returns:
            Context usage statistics
        """
        return {
            'agent_id': self.config.agent_id,
            'context_available': self.context_available,
            'statistics': self.context_stats,
            'average_context_time': (
                self.context_stats['total_context_time'] / 
                max(self.context_stats['searches_performed'], 1)
            )
        }
    
    async def index_project(self, root_path: str = '.') -> bool:
        """
        Index the project codebase for context retrieval.
        
        Args:
            root_path: Root path of the project to index
            
        Returns:
            True if indexing successful
        """
        if not self.context_available or not self.context_engine:
            logger.warning(f"⚠️ {self.name}: Context not available for indexing")
            return False
        
        try:
            logger.info(f"📚 {self.name}: Starting project indexing...")
            await self.context_engine.index_codebase(root_path)
            
            # Create retriever after indexing
            if self.context_engine.vector_store:
                self.retriever = self.context_engine.vector_store.as_retriever(
                    search_kwargs={"k": 5}
                )
            
            logger.info(f"✅ {self.name}: Project indexing complete")
            return True
        except Exception as e:
            logger.error(f"❌ {self.name}: Project indexing failed: {e}")
            return False
    
    # Implement abstract methods from BaseAgent
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute with LLM using RAG context.
        
        Args:
            task: Task with query and retrieved context
            
        Returns:
            LLM response with context
        """
        logger.info(f"🤖 {self.name}: Executing task with LLM...")
        
        query = task.get('query', '')
        context_data = task.get('context', {})
        
        # Build prompt with RAG context
        prompt = self._build_rag_prompt(query, context_data)
        
        # Call LLM
        try:
            # Try to call Gemini (it will check for API key internally)
            response_text = await self._call_gemini(prompt)
        except Exception as e:
            logger.warning(f"LLM call failed, using fallback: {e}")
            # Fallback: Use context-based response
            response_text = self._generate_context_response(query, context_data)
        
        return {
            'status': 'success',
            'agent_id': self.config.agent_id,
            'response': response_text,
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'context_stats': {
                'retrieval_time': 0.0,
                'results_count': len(context_data.get('semantic_search_results', [])),
                'has_file_context': context_data.get('file_context') is not None,
                'import_suggestions_count': len(context_data.get('import_suggestions', [])),
                'search_type': context_data.get('search_type', 'none')
            }
        }
    
    def _build_rag_prompt(self, query: str, context_data: Dict[str, Any]) -> str:
        """Build prompt with RAG context for LLM - GIVE LLM ALL CONTEXT!"""
        
        prompt = f"User Query: {query}\n\n"
        
        # Add retrieved context - INCREASED to show ALL results with FULL content
        semantic_results = context_data.get('semantic_search_results', [])
        if semantic_results:
            prompt += f"=== Retrieved Context ({len(semantic_results)} documents) ===\n\n"
            
            # INCREASED: Show up to 20 results (was 5) with FULL content (was 500 chars)
            for i, result in enumerate(semantic_results[:20], 1):
                content = result.get('content', '')
                file_path = result.get('metadata', {}).get('file_path', 'unknown')
                source = result.get('file_path', file_path)  # Try both metadata and direct
                relevance = result.get('relevance_score', 0)
                search_type = result.get('search_type', 'unknown')
                
                prompt += f"[Document {i}] Source: {source} | Relevance: {relevance:.2f} | Type: {search_type}\n"
                prompt += f"{content}\n"  # FULL CONTENT - no truncation!
                prompt += f"\n{'='*80}\n\n"
        
        # Add file context if available
        file_context = context_data.get('file_context')
        if file_context:
            prompt += f"Additional File Context:\n{file_context[:2000]}...\n\n"
        
        # Add import suggestions
        import_suggestions = context_data.get('import_suggestions', [])
        if import_suggestions:
            prompt += f"Common Imports: {', '.join(import_suggestions[:5])}\n\n"
        
        prompt += "\nInstructions: Based on ALL the context documents provided above, answer the user's query comprehensively. Use information from MULTIPLE documents if relevant. If specific strategies, lists, or details are mentioned across documents, compile them into a complete answer."
        
        return prompt
    
    async def _call_gemini(self, prompt: str) -> str:
        """
        Call Gemini API with LangChain for automatic LangSmith tracing.
        
        This uses ChatGoogleGenerativeAI which automatically logs to LangSmith
        when LANGCHAIN_TRACING_V2=true is set in environment.
        """
        try:
            # Use LangChain if available (provides LangSmith tracing)
            if LANGCHAIN_AVAILABLE:
                api_key = self._get_gemini_api_key()
                if not api_key:
                    raise ValueError("No Gemini API key found")
                
                # Initialize LangChain ChatGoogleGenerativeAI
                # This automatically traces to LangSmith when enabled
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",  # Latest Gemini model
                    google_api_key=api_key,
                    temperature=0.7,
                    convert_system_message_to_human=True  # Gemini compatibility
                )
                
                # Create messages for LangChain (automatically traced)
                messages = [
                    SystemMessage(content="You are a helpful AI assistant with access to relevant context from a codebase."),
                    HumanMessage(content=prompt)
                ]
                
                # Invoke with automatic LangSmith tracing
                response = await llm.ainvoke(messages)
                return response.content
            
            else:
                # Fallback to direct Gemini API (no tracing)
                import google.generativeai as genai
                
                if not hasattr(self, '_genai_configured'):
                    api_key = self._get_gemini_api_key()
                    if api_key:
                        genai.configure(api_key=api_key)
                        self._genai_configured = True
                    else:
                        raise ValueError("No Gemini API key found")
                
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = await model.generate_content_async(prompt)
                return response.text
                
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _get_gemini_api_key(self) -> str:
        """Get Gemini API key from environment or config."""
        import os
        from pathlib import Path
        
        # Try environment variable
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            return api_key
        
        # Try secrets.toml
        try:
            secrets_path = Path(".streamlit/secrets.toml")
            if secrets_path.exists():
                with open(secrets_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY"):
                            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if api_key and api_key != "your-gemini-api-key-here":
                                return api_key
        except Exception as e:
            logger.warning(f"Failed to read secrets.toml: {e}")
        
        return None
    
    def _generate_context_response(self, query: str, context_data: Dict[str, Any]) -> str:
        """Fallback: Generate response from context without LLM."""
        
        semantic_results = context_data.get('semantic_search_results', [])
        
        if semantic_results:
            response = f"Based on the codebase context for '{query}':\n\n"
            
            for i, result in enumerate(semantic_results[:3], 1):
                file_path = result.get('metadata', {}).get('file_path', 'unknown')
                content = result.get('content', '')
                relevance = result.get('relevance_score', 0)
                
                response += f"{i}. {file_path} (relevance: {relevance:.2f})\n"
                response += f"   {content[:200]}...\n\n"
            
            response += f"Found {len(semantic_results)} relevant sections in the codebase."
        else:
            response = f"No specific context found for '{query}'. Please ensure the project is indexed."
        
        return response
    
    def _rewrite_query(self, query: str) -> List[str]:
        """
        Rewrite query into multiple variants for better retrieval.
        
        Implements Query Rewriting from RAG best practices.
        Source: https://www.promptingguide.ai/research/rag
        
        Strategies:
        1. Original query
        2. Question decomposition (break into sub-questions)
        3. Hypothetical document generation (HyDE-inspired)
        4. Keyword extraction
        """
        variants = [query]  # Always include original
        
        # Strategy 1: Decompose complex questions
        if '?' in query and ('and' in query.lower() or 'or' in query.lower()):
            # Split compound questions
            parts = query.replace(' and ', ' ? ').replace(' or ', ' ? ').split('?')
            for part in parts:
                part = part.strip()
                if len(part) > 10:
                    variants.append(part + '?')
        
        # Strategy 2: Convert question to statement (HyDE-inspired)
        # "What is X?" -> "X is" or "X refers to"
        question_words = ['what', 'how', 'why', 'when', 'where', 'who']
        query_lower = query.lower()
        for qword in question_words:
            if query_lower.startswith(qword):
                # Convert to statement form
                rest = query[len(qword):].strip()
                if rest.startswith('is '):
                    variants.append(rest[3:].rstrip('?'))
                elif rest.startswith('are '):
                    variants.append(rest[4:].rstrip('?'))
                else:
                    variants.append(rest.rstrip('?'))
                break
        
        # Strategy 3: Extract core concepts (remove question words)
        core_query = query
        for qword in question_words + ['the', 'a', 'an']:
            core_query = core_query.lower().replace(f'{qword} ', '').replace(f' {qword}', '')
        if core_query != query.lower():
            variants.append(core_query.strip().rstrip('?'))
        
        # Return unique variants
        return list(dict.fromkeys([v for v in variants if len(v) > 5]))[:4]
    
    def _extract_key_concepts(self, query: str) -> List[str]:
        """
        Extract key concepts from query for multi-stage search.
        
        Implements concept extraction for better semantic coverage.
        Source: https://masteringllm.medium.com/best-practices-for-rag-pipeline-8c12a8096453
        """
        # Enhanced stop words list
        stop_words = {'what', 'is', 'are', 'the', 'a', 'an', 'how', 'why', 'when', 'where', 
                     'which', 'who', 'to', 'do', 'does', 'in', 'on', 'at', 'for', 'with', 
                     'about', 'this', 'that', 'these', 'those', 'can', 'should', 'would'}
        
        words = query.lower().split()
        concepts = []
        
        # Extract multi-word phrases (2-3 words) - technical terms often multi-word
        for i in range(len(words)):
            if words[i] not in stop_words:
                # Single word concept (technical terms)
                if len(words[i]) > 3:
                    concepts.append(words[i])
                
                # Two word phrase
                if i < len(words) - 1 and words[i+1] not in stop_words:
                    concepts.append(f"{words[i]} {words[i+1]}")
                
                # Three word phrase (e.g., "context engineering guide")
                if i < len(words) - 2 and words[i+1] not in stop_words and words[i+2] not in stop_words:
                    concepts.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        # Return unique concepts, prioritize longer phrases (more specific)
        unique_concepts = list(dict.fromkeys(concepts))
        return sorted(unique_concepts, key=lambda x: len(x.split()), reverse=True)[:5]
    
    def _deduplicate_and_rerank(self, results: List[Dict], original_query: str) -> List[Dict]:
        """
        Advanced deduplication and re-ranking using multiple signals.
        
        Implements re-ranking best practices from:
        - https://masteringllm.medium.com/best-practices-for-rag-pipeline-8c12a8096453
        - https://cloud.google.com/blog/products/ai-machine-learning/optimizing-rag-retrieval
        - https://www.promptingguide.ai/research/rag
        
        Strategies:
        1. Content-based deduplication (semantic fingerprinting)
        2. Multi-signal scoring (relevance + diversity + recency)
        3. Position-aware re-ranking (avoid "lost in the middle")
        """
        if not results:
            return []
        
        # Step 1: Deduplicate based on content similarity
        unique_results = []
        seen_fingerprints = set()
        
        for result in results:
            content = result.get('content', '')
            # Use first 200 chars + last 100 chars as fingerprint (captures beginning and end)
            fingerprint = (content[:200] + content[-100:]).strip().lower()
            fingerprint = ''.join(fingerprint.split())  # Remove whitespace variations
            
            if fingerprint and fingerprint not in seen_fingerprints:
                seen_fingerprints.add(fingerprint)
                unique_results.append(result)
        
        # Step 2: Enhanced scoring with multiple signals
        query_lower = original_query.lower()
        query_words = set(query_lower.split())
        
        for idx, result in enumerate(unique_results):
            content = result.get('content', '').lower()
            
            # Signal 1: Base relevance score (from semantic search)
            base_score = result.get('relevance_score', 0.5)
            
            # Signal 2: Keyword overlap (BM25-inspired)
            content_words = set(content.split())
            overlap = len(query_words & content_words)
            keyword_score = min(overlap / len(query_words), 1.0) if query_words else 0
            
            # Signal 3: Content quality (longer, well-structured content often better)
            content_length = len(content)
            quality_score = min(content_length / 1000, 1.0)  # Normalize to 0-1
            
            # Signal 4: Diversity bonus (penalize very similar consecutive results)
            diversity_bonus = 1.0
            if idx > 0:
                prev_content = unique_results[idx-1].get('content', '').lower()
                # Simple Jaccard similarity
                prev_words = set(prev_content.split())
                similarity = len(content_words & prev_words) / len(content_words | prev_words) if content_words | prev_words else 0
                diversity_bonus = 1.0 - (similarity * 0.3)  # Penalize high similarity
            
            # Combined score with weights based on research
            # Research shows semantic relevance most important, followed by keyword match
            combined_score = (
                base_score * 0.50 +           # Semantic relevance (highest weight)
                keyword_score * 0.25 +         # Keyword match (important for precision)
                quality_score * 0.15 +         # Content quality
                diversity_bonus * 0.10         # Diversity
            )
            
            result['combined_score'] = combined_score
            result['scoring_details'] = {
                'base': base_score,
                'keyword': keyword_score,
                'quality': quality_score,
                'diversity': diversity_bonus
            }
        
        # Step 3: Sort by combined score
        ranked_results = sorted(unique_results, key=lambda x: x.get('combined_score', 0), reverse=True)
        
        # Step 4: Apply position optimization ("lost in the middle" mitigation)
        # Research shows: most relevant at start and end, less relevant in middle
        top_results = ranked_results[:15]  # Top 15 results
        
        if len(top_results) > 5:
            # Reorder: [most relevant] + [least relevant in middle] + [2nd most relevant at end]
            # This follows "reverse" re-packing strategy from research
            reordered = []
            for i in range(0, len(top_results), 2):
                if i < len(top_results):
                    reordered.append(top_results[i])
            for i in range(1, len(top_results), 2):
                if i < len(top_results):
                    reordered.insert(len(reordered)//2, top_results[i])
            
            return reordered
        
        return top_results
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate that the task is appropriate for this agent.
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid, False otherwise
        """
        # Basic validation - ensure task is a dictionary
        if not isinstance(task, dict):
            logger.warning(f"⚠️ {self.name}: Task must be a dictionary")
            return False
        
        # Task should have at least a query or description
        if not any(key in task for key in ['query', 'description', 'task_description']):
            logger.warning(f"⚠️ {self.name}: Task must have query or description")
            return False
        
        return True


# Utility functions for creating context-aware agents

def create_context_aware_agent(
    agent_id: str,
    agent_type: str,
    prompt_template_id: str,
    shared_context_engine: Optional[ContextEngine] = None,
    **kwargs
) -> ContextAwareAgent:
    """
    Factory function to create a context-aware agent.
    
    Args:
        agent_id: Unique agent identifier
        agent_type: Type of agent
        prompt_template_id: Prompt template identifier
        shared_context_engine: Shared ContextEngine instance (recommended)
        **kwargs: Additional agent configuration
        
    Returns:
        Configured ContextAwareAgent instance
    """
    config = AgentConfig(
        agent_id=agent_id,
        agent_type=agent_type,
        prompt_template_id=prompt_template_id,
        **kwargs
    )
    
    return ContextAwareAgent(config, context_engine=shared_context_engine)


def get_shared_context_engine() -> Optional[ContextEngine]:
    """
    Get a shared ContextEngine instance for multiple agents.
    
    This is the recommended pattern to avoid multiple ContextEngines
    indexing the same codebase.
    
    Returns:
        Shared ContextEngine instance or None if not available
    """
    if not CONTEXT_ENGINE_AVAILABLE:
        logger.warning("⚠️ ContextEngine not available")
        return None
    
    try:
        context_config = ContextConfig()
        context_engine = ContextEngine(context_config)
        logger.info("✅ Created shared ContextEngine instance")
        return context_engine
    except Exception as e:
        logger.error(f"❌ Failed to create shared ContextEngine: {e}")
        return None


if __name__ == "__main__":
    # Test the context-aware agent
    async def test_context_aware_agent():
        """Test context-aware agent functionality."""
        print("🧪 Testing ContextAwareAgent...")
        
        # Create test agent
        config = AgentConfig(
            agent_id="test_context_agent",
            agent_type="test",
            prompt_template_id="test_template"
        )
        
        agent = ContextAwareAgent(config)
        
        # Index project
        print("\n📚 Indexing project...")
        success = await agent.index_project('.')
        print(f"Indexing: {'✅ Success' if success else '❌ Failed'}")
        
        # Test semantic search
        print("\n🔍 Testing semantic search...")
        results = await agent.get_relevant_context("agent base class")
        print(f"Found {results.get('total_found', 0)} results")
        
        # Test project intelligence
        print("\n🧠 Testing project intelligence...")
        intelligence = agent.get_project_intelligence()
        print(f"Files indexed: {intelligence.get('total_files_indexed', 0)}")
        print(f"Semantic search: {intelligence.get('semantic_search_available', False)}")
        
        # Test context stats
        print("\n📊 Context statistics:")
        stats = agent.get_context_stats()
        print(f"Searches: {stats['statistics']['searches_performed']}")
        print(f"Average time: {stats['average_context_time']:.3f}s")
        
        print("\n✅ ContextAwareAgent test complete!")
    
    # Run test
    asyncio.run(test_context_aware_agent())

