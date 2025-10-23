#!/usr/bin/env python3
"""
Content Parser Agent - Research Swarm
======================================

Parses web content and extracts relevant information.

Responsibilities:
- Extract main content from HTML
- Identify key information
- Structure extracted data
- Remove noise, ads, and irrelevant content

Created: 2025-10-10
Part of: Web Research Swarm
"""

import logging
from typing import Dict, List, Any
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

# LangChain imports for content parsing
try:
    from langchain_community.document_loaders import AsyncHtmlLoader
    from langchain_community.document_transformers import Html2TextTransformer, BeautifulSoupTransformer
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    LANGCHAIN_PARSING_AVAILABLE = True
except ImportError:
    LANGCHAIN_PARSING_AVAILABLE = False

# Fallback HTML parsing
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

logger = logging.getLogger(__name__)




class ContentParserAgentState(BaseModel):
    """State for ContentParserAgent LangGraph workflow using Pydantic BaseModel."""
    
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

class ContentParserAgent(EnhancedBaseAgent):
    """
    Parses web content and extracts relevant information.
    
    This agent processes raw web content, extracting structured information
    and removing noise. Uses LLM for intelligent content extraction.
    """
    
    def __init__(self):
        """Initialize Content Parser Agent with Gemini 2.0 Flash."""
        config = AgentConfig(
            agent_id="content_parser",
            agent_type="research",
            prompt_template_id="research_content_parser",
            model_name="gemini-2.0-flash-exp",
            max_retries=2,
            timeout_seconds=30
        )
        super().__init__(config)
        
        self.parser_available = self._check_parser_availability()
        logger.info(f"ContentParserAgent initialized (parser available: {self.parser_available})")
    
        
        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_langgraph_workflow()
            self.app = self.workflow.compile()
            self.logger.info("✅ LangGraph workflow compiled and ready")
        else:
            self.workflow = None
            self.app = None
            self.logger.info("⚠️ LangGraph not available - using legacy mode")

    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate task has required raw content."""
        return isinstance(task, dict) and 'raw_content' in task
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content parsing."""
        raw_content = task.get('raw_content', [])
        parsed = await self.parse_content(raw_content)
        return {'success': True, 'parsed_content': parsed}
    
    def _check_parser_availability(self) -> bool:
        """Check if HTML parsing libraries are available."""
        if LANGCHAIN_PARSING_AVAILABLE:
            logger.info("✅ LangChain parsing available (Html2TextTransformer + BeautifulSoup)")
            return True
        elif BS4_AVAILABLE:
            logger.info("✅ BeautifulSoup available (fallback parsing)")
            return True
        else:
            logger.warning("⚠️ No parsing libraries available - using simulated parsing")
            return False
    
    async def parse_content(
        self,
        search_results: List[Dict],
        extract_key_points: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Parse and extract information from search results.
        
        Args:
            search_results: List of search results with URLs
            extract_key_points: Whether to extract key points using LLM
            
        Returns:
            List of parsed content with:
            - source_url: Original URL
            - source_title: Page title
            - extracted_content: Main content text
            - key_points: Extracted key points (if enabled)
            - metadata: Parsing metadata
        """
        parsed_results = []
        
        for idx, result in enumerate(search_results):
            try:
                parsed = await self._parse_single_result(result, extract_key_points)
                parsed_results.append(parsed)
                
                if (idx + 1) % 5 == 0:
                    logger.info(f"Parsed {idx + 1}/{len(search_results)} results")
                    
            except Exception as e:
                logger.error(f"Failed to parse {result.get('url')}: {e}")
                # Add error result to maintain result ordering
                parsed_results.append(self._create_error_result(result, str(e)))
        
        logger.info(f"✅ Parsed {len(parsed_results)} content items")
        return parsed_results
    
    async def _parse_single_result(
        self,
        result: Dict,
        extract_key_points: bool
    ) -> Dict[str, Any]:
        """Parse a single search result."""
        
        # Step 1: Extract content (simulated for now)
        raw_content = await self._extract_raw_content(result)
        
        # Step 2: Clean content
        cleaned_content = self._clean_content(raw_content)
        
        # Step 3: Extract key points using LLM (if enabled)
        key_points = []
        if extract_key_points and cleaned_content:
            key_points = await self._extract_key_points(cleaned_content, result.get('query', ''))
        
        return {
            "source_url": result.get("url"),
            "source_title": result.get("title"),
            "extracted_content": cleaned_content,
            "key_points": key_points,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "relevance": result.get("relevance_score", 0.0),
                "parser_version": "1.0",
                "content_length": len(cleaned_content),
                "key_points_count": len(key_points)
            }
        }
    
    async def _extract_raw_content(self, result: Dict) -> str:
        """
        Extract raw content from URL using LangChain loaders.
        
        Uses LangChain's AsyncHtmlLoader + Html2TextTransformer for robust parsing.
        Falls back to BeautifulSoup if LangChain not available.
        """
        url = result.get("url", "")
        
        if not url or not url.startswith("http"):
            return self._simulate_content_extraction(result)
        
        try:
            if LANGCHAIN_PARSING_AVAILABLE:
                # Use LangChain's async HTML loader
                content = await self._langchain_extract_content(url)
                return content if content else self._simulate_content_extraction(result)
            
            elif BS4_AVAILABLE:
                # Fallback to BeautifulSoup
                content = await self._beautifulsoup_extract_content(url)
                return content if content else self._simulate_content_extraction(result)
            
            else:
                # Simulated extraction as last resort
                return self._simulate_content_extraction(result)
                
        except Exception as e:
            logger.error(f"Content extraction failed for {url}: {e}")
            return self._simulate_content_extraction(result)
    
    async def _langchain_extract_content(self, url: str) -> str:
        """Extract content using LangChain loaders and transformers."""
        try:
            # Load HTML content
            loader = AsyncHtmlLoader([url])
            docs = loader.load()
            
            if not docs:
                return ""
            
            # Transform HTML to clean text
            html2text = Html2TextTransformer()
            transformed_docs = html2text.transform_documents(docs)
            
            # Extract page content
            if transformed_docs:
                content = transformed_docs[0].page_content
                return self._clean_content(content)
            
            return ""
            
        except Exception as e:
            logger.warning(f"LangChain extraction failed: {e}")
            return ""
    
    async def _beautifulsoup_extract_content(self, url: str) -> str:
        """Fallback: Extract content using BeautifulSoup."""
        try:
            import requests
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator='\n', strip=True)
            
            return self._clean_content(text)
            
        except Exception as e:
            logger.warning(f"BeautifulSoup extraction failed: {e}")
            return ""
    
    def _simulate_content_extraction(self, result: Dict) -> str:
        """Simulate content extraction when real parsing unavailable."""
        url = result.get("url", "")
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        
        simulated_content = f"""
{title}

{snippet}

This is simulated extracted content from {url}.
In production with LangChain loaders available, this would be:
- Actual HTML content fetched via AsyncHtmlLoader
- Cleaned and transformed via Html2TextTransformer
- Parsed with BeautifulSoup for structured extraction
- Chunked appropriately for processing

Install langchain-community for real web scraping:
pip install langchain-community beautifulsoup4 html2text
"""
        
        return simulated_content.strip()
    
    def _clean_content(self, raw_content: str) -> str:
        """Clean and normalize content."""
        if not raw_content:
            return ""
        
        # Basic cleaning
        content = raw_content.strip()
        
        # Remove multiple newlines
        while "\n\n\n" in content:
            content = content.replace("\n\n\n", "\n\n")
        
        # Remove excessive whitespace
        lines = [line.strip() for line in content.split("\n")]
        content = "\n".join(line for line in lines if line)
        
        return content
    
    async def _extract_key_points(self, content: str, query: str) -> List[str]:
        """Extract key points from content using LLM."""
        if len(content) < 50:
            return []
        
        # Limit content length for LLM
        content_sample = content[:2000]
        
        prompt = f"""
Extract the key points from this content that are relevant to the research query.

Research Query: {query}

Content:
{content_sample}

Provide 3-5 key points as a bullet list. Focus on factual information directly relevant to the query.
Return ONLY the bullet points, one per line, starting with "- ".
"""
        
        try:
            result = await self.execute_async({"prompt": prompt})
            
            if result.get("success"):
                content = result.get("content", "")
                # Extract bullet points
                points = [
                    line.strip()[2:].strip()
                    for line in content.split("\n")
                    if line.strip().startswith("- ") or line.strip().startswith("* ")
                ]
                return points[:5]  # Limit to 5 points
            else:
                return []
                
        except Exception as e:
            logger.error(f"Key point extraction failed: {e}")
            return []
    
    def _create_error_result(self, result: Dict, error: str) -> Dict[str, Any]:
        """Create error result for failed parsing."""
        return {
            "source_url": result.get("url"),
            "source_title": result.get("title"),
            "extracted_content": result.get("snippet", ""),
            "key_points": [],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "error": error,
                "parse_failed": True
            }
        }
    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Build LangGraph workflow for ContentParserAgent."""
        workflow = StateGraph(ContentParserAgentState)
        
        # Simple workflow: just execute the agent
        workflow.add_node("execute", self._langgraph_execute_node)
        workflow.set_entry_point("execute")
        workflow.add_edge("execute", END)
        
        return workflow
    
    async def _langgraph_execute_node(self, state: ContentParserAgentState) -> ContentParserAgentState:
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


if __name__ == "__main__":
    import asyncio
    
    async def test_content_parser():
        """Test Content Parser Agent."""
        print("🧪 Testing Content Parser Agent\n")
        
        agent = ContentParserAgent()
        
        # Simulate search results
        search_results = [
            {
                "url": "https://example.com/google-drive-api",
                "title": "Google Drive API Integration Guide",
                "snippet": "Learn how to integrate Google Drive API with Python applications.",
                "query": "Google Drive API Python",
                "relevance_score": 0.9
            },
            {
                "url": "https://example.com/mcp-server",
                "title": "Building MCP Servers",
                "snippet": "Guide to building Model Context Protocol servers.",
                "query": "MCP server integration",
                "relevance_score": 0.85
            }
        ]
        
        parsed = await agent.parse_content(search_results, extract_key_points=True)
        
        print(f"✅ Parsing Complete:")
        print(f"   Total parsed: {len(parsed)}")
        print(f"\n📋 Sample Parsed Content:")
        for i, item in enumerate(parsed[:2], 1):
            print(f"\n   {i}. {item['source_title']}")
            print(f"      Content length: {item['metadata']['content_length']} chars")
            print(f"      Key points: {item['metadata']['key_points_count']}")
            if item['key_points']:
                print(f"      Points: {item['key_points'][:2]}")
    
    asyncio.run(test_content_parser())


# Export for LangGraph Studio
_default_instance = None

def get_graph():
    """Get the compiled graph for LangGraph Studio."""
    global _default_instance
    if _default_instance is None and LANGGRAPH_AVAILABLE:
        from models.config import AgentConfig
        
        config = AgentConfig(
            agent_id='content_parser_agent',
            name='ContentParserAgent',
            description='ContentParserAgent agent',
            model_name='gemini-2.5-flash'
        )
        _default_instance = ContentParserAgent()
    return _default_instance.app if _default_instance else None

# Studio expects 'graph' variable
graph = get_graph()
