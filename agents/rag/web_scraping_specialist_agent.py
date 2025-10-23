#!/usr/bin/env python3
"""
Web Scraping Specialist Agent
==============================

Intelligent web scraping agent for RAG system with:
- Recursive site crawling with depth control
- CSS selector-based content filtering
- Rate limiting and respectful crawling
- Metadata extraction
- Duplicate detection

Author: AI Development Agent
Created: 2025-01-09
Purpose: US-RAG-001 Phase 2 - Enhanced Website Scraping
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urljoin, urlparse
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

# LangChain and web scraping
try:
    from langchain_community.document_loaders import WebBaseLoader
    from bs4 import BeautifulSoup
    import requests
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

from models.config import AgentConfig

logger = logging.getLogger(__name__)




class WebScrapingSpecialistAgentState(BaseModel):
    """State for WebScrapingSpecialistAgent LangGraph workflow using Pydantic BaseModel."""
    
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

class WebScrapingSpecialistAgent:
    """
    Specialist agent for intelligent web scraping with advanced features.
    
    Features:
    - Recursive crawling with depth control
    - CSS selector filtering
    - Rate limiting
    - Duplicate detection
    - Metadata extraction
    """
    
    def __init__(self, config: AgentConfig, document_loader=None):
        """
        Initialize web scraping specialist agent.
        
        Args:
            config: Agent configuration
            document_loader: DocumentLoader instance for processing
        """
        if not SCRAPING_AVAILABLE:
            raise ImportError("Web scraping dependencies not available")
        
        self.config = config
        self.document_loader = document_loader
        
        # Scraping state
        self.visited_urls: Set[str] = set()
        self.scraped_documents: List[Dict] = []
        
        # Statistics
        self.scraping_stats = {
            'total_urls_discovered': 0,
            'urls_scraped': 0,
            'urls_skipped': 0,
            'duplicates_detected': 0,
            'errors': 0,
            'total_bytes': 0,
            'average_scrape_time': 0.0
        }
        
        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_langgraph_workflow()
            self.app = self.workflow.compile()
            logger.info("✅ LangGraph workflow compiled and ready")
        else:
            self.workflow = None
            self.app = None
            logger.info("⚠️ LangGraph not available - using legacy mode")
        
        logger.info(f"✅ {self.config.name} initialized")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute web scraping task with advanced features.
        
        Args:
            task: Dictionary containing:
                - start_url: str - Starting URL
                - recursive: bool - Enable recursive crawling (default: False)
                - max_depth: int - Maximum crawling depth (default: 1)
                - css_selector: str - Optional CSS selector for content filtering
                - rate_limit: float - Delay between requests in seconds (default: 1.0)
                - max_pages: int - Maximum pages to scrape (default: 10)
                - same_domain_only: bool - Stay within same domain (default: True)
                - skip_duplicates: bool - Skip duplicate URLs (default: True)
                
        Returns:
            Dictionary with scraping results
        """
        start_url = task.get('start_url')
        recursive = task.get('recursive', False)
        max_depth = task.get('max_depth', 1)
        css_selector = task.get('css_selector')
        rate_limit = task.get('rate_limit', 1.0)
        max_pages = task.get('max_pages', 10)
        same_domain_only = task.get('same_domain_only', True)
        skip_duplicates = task.get('skip_duplicates', True)
        
        if not start_url:
            return {
                'status': 'error',
                'error': 'No start_url provided',
                'agent_id': self.config.agent_id
            }
        
        logger.info(f"🌐 {self.config.name}: Starting scrape of {start_url}")
        logger.info(f"   Recursive: {recursive}, Max depth: {max_depth}, Max pages: {max_pages}")
        
        # Reset state
        self.visited_urls.clear()
        self.scraped_documents.clear()
        
        start_time = time.time()
        
        try:
            if recursive:
                # Recursive crawling
                await self._recursive_crawl(
                    url=start_url,
                    current_depth=0,
                    max_depth=max_depth,
                    css_selector=css_selector,
                    rate_limit=rate_limit,
                    max_pages=max_pages,
                    same_domain_only=same_domain_only,
                    skip_duplicates=skip_duplicates
                )
            else:
                # Single page scraping
                await self._scrape_single_page(
                    url=start_url,
                    css_selector=css_selector,
                    skip_duplicates=skip_duplicates
                )
            
            total_time = time.time() - start_time
            
            logger.info(f"✅ {self.config.name}: Scraping complete")
            logger.info(f"   Pages scraped: {self.scraping_stats['urls_scraped']}")
            logger.info(f"   Duplicates skipped: {self.scraping_stats['duplicates_detected']}")
            logger.info(f"   Total time: {total_time:.2f}s")
            
            return {
                'status': 'success',
                'agent_id': self.config.agent_id,
                'timestamp': datetime.now().isoformat(),
                'documents': self.scraped_documents,
                'stats': self.scraping_stats,
                'total_time': total_time
            }
            
        except Exception as e:
            logger.error(f"❌ {self.config.name}: Scraping failed: {e}")
            return {
                'status': 'error',
                'agent_id': self.config.agent_id,
                'error': str(e),
                'documents': self.scraped_documents,  # Return what we got
                'stats': self.scraping_stats
            }
    
    async def _recursive_crawl(
        self,
        url: str,
        current_depth: int,
        max_depth: int,
        css_selector: Optional[str],
        rate_limit: float,
        max_pages: int,
        same_domain_only: bool,
        skip_duplicates: bool
    ):
        """Recursively crawl website."""
        
        # Check if we should stop
        if current_depth > max_depth:
            logger.debug(f"Max depth {max_depth} reached for {url}")
            return
        
        if len(self.visited_urls) >= max_pages:
            logger.info(f"Max pages {max_pages} reached, stopping crawl")
            return
        
        if url in self.visited_urls:
            logger.debug(f"Already visited: {url}")
            return
        
        # Mark as visited
        self.visited_urls.add(url)
        self.scraping_stats['total_urls_discovered'] += 1
        
        # Scrape this page
        logger.info(f"🌐 Scraping (depth {current_depth}): {url}")
        
        doc_result = await self._scrape_single_page(url, css_selector, skip_duplicates)
        
        # Don't stop on duplicates - continue to extract links
        # Only stop on actual errors
        if not doc_result.get('success') and not doc_result.get('skipped'):
            logger.warning(f"   Failed to scrape {url}, stopping branch")
            return
        
        # Rate limiting
        if rate_limit > 0:
            await asyncio.sleep(rate_limit)
        
        # Extract links for recursive crawling (even if page was duplicate)
        if current_depth < max_depth:
            links = await self._extract_links(url, same_domain_only)
            
            # Filter out already visited links
            new_links = [link for link in links if link not in self.visited_urls]
            
            logger.info(f"   Found {len(links)} total links, {len(new_links)} new links to crawl")
            
            # Crawl discovered links
            for i, link in enumerate(new_links, 1):
                if len(self.visited_urls) >= max_pages:
                    logger.info(f"   Stopping: Max pages ({max_pages}) reached")
                    break
                
                logger.info(f"   Crawling link {i}/{len(new_links)}: {link}")
                
                await self._recursive_crawl(
                    url=link,
                    current_depth=current_depth + 1,
                    max_depth=max_depth,
                    css_selector=css_selector,
                    rate_limit=rate_limit,
                    max_pages=max_pages,
                    same_domain_only=same_domain_only,
                    skip_duplicates=skip_duplicates
                )
        else:
            logger.info(f"   Max depth ({max_depth}) reached, not extracting links")
    
    async def _scrape_single_page(
        self,
        url: str,
        css_selector: Optional[str],
        skip_duplicates: bool
    ) -> Dict[str, Any]:
        """Scrape a single page with optional CSS filtering."""
        
        try:
            start_time = time.time()
            
            # Use document loader if available
            if self.document_loader:
                result = await self.document_loader.load_website(url, skip_duplicates=skip_duplicates)
                
                if result.get('success'):
                    self.scraped_documents.append(result)
                    self.scraping_stats['urls_scraped'] += 1
                    
                    scrape_time = time.time() - start_time
                    
                    # Update average scrape time
                    n = self.scraping_stats['urls_scraped']
                    avg = self.scraping_stats['average_scrape_time']
                    self.scraping_stats['average_scrape_time'] = ((avg * (n - 1)) + scrape_time) / n
                    
                    logger.info(f"   ✅ Successfully scraped: {url}")
                    return result
                elif result.get('skipped'):
                    # Still add to scraped_documents so UI knows we visited it
                    self.scraped_documents.append(result)
                    self.scraping_stats['duplicates_detected'] += 1
                    logger.info(f"   ⏭️ Skipping duplicate (already in DB): {url}")
                    return result
                else:
                    self.scraping_stats['errors'] += 1
                    return result
            
            # Fallback: Direct scraping without document loader
            loader = WebBaseLoader(url)
            documents = await asyncio.to_thread(loader.load)
            
            # Apply CSS selector filtering if provided
            if css_selector and documents:
                filtered_content = self._apply_css_filter(documents[0].page_content, css_selector)
                documents[0].page_content = filtered_content
            
            result = {
                'success': True,
                'url': url,
                'documents': documents,
                'document_count': len(documents)
            }
            
            self.scraped_documents.append(result)
            self.scraping_stats['urls_scraped'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            self.scraping_stats['errors'] += 1
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
    
    async def _extract_links(self, url: str, same_domain_only: bool) -> List[str]:
        """Extract links from a page for recursive crawling."""
        
        try:
            # Fetch page
            logger.debug(f"   Fetching page for link extraction: {url}")
            response = await asyncio.to_thread(requests.get, url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"   HTTP {response.status_code} when fetching {url}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all links
            links = []
            base_domain = urlparse(url).netloc
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # Skip empty hrefs, anchors, and javascript
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, href)
                
                # Parse URL
                parsed = urlparse(absolute_url)
                
                # Filter out non-http(s) links
                if parsed.scheme not in ['http', 'https']:
                    continue
                
                # Filter by domain if required
                if same_domain_only and parsed.netloc != base_domain:
                    continue
                
                # Remove fragments
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    clean_url += f"?{parsed.query}"
                
                links.append(clean_url)
            
            # Remove duplicates
            unique_links = list(set(links))
            
            logger.debug(f"   Extracted {len(unique_links)} unique links from {url}")
            return unique_links
            
        except requests.RequestException as e:
            logger.warning(f"   Network error extracting links from {url}: {e}")
            return []
        except Exception as e:
            logger.error(f"   Unexpected error extracting links from {url}: {e}", exc_info=True)
            return []
    

    def _apply_css_filter(self, html_content: str, css_selector: str) -> str:
        """Apply CSS selector to extract specific content."""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            selected_elements = soup.select(css_selector)
            
            if selected_elements:
                # Combine selected content
                filtered_content = '\n\n'.join(
                    element.get_text(separator=' ', strip=True)
                    for element in selected_elements
                )
                logger.info(f"✂️ CSS filter applied: {len(selected_elements)} elements selected")
                return filtered_content
            else:
                logger.warning(f"CSS selector '{css_selector}' matched no elements")
                return html_content
                
        except Exception as e:
            logger.error(f"CSS filtering failed: {e}")
            return html_content
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        return self.scraping_stats.copy()


    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Build LangGraph workflow for WebScrapingSpecialistAgent."""
        workflow = StateGraph(WebScrapingSpecialistAgentState)
        
        # Simple workflow: just execute the agent
        workflow.add_node("execute", self._langgraph_execute_node)
        workflow.set_entry_point("execute")
        workflow.add_edge("execute", END)
        
        return workflow
    
    async def _langgraph_execute_node(self, state: WebScrapingSpecialistAgentState) -> WebScrapingSpecialistAgentState:
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
            agent_id='web_scraping_specialist_agent',
            name='WebScrapingSpecialistAgent',
            description='WebScrapingSpecialistAgent agent',
            model_name='gemini-2.5-flash'
        )
        _default_instance = WebScrapingSpecialistAgent(config)
    return _default_instance.app if _default_instance else None

# Studio expects 'graph' variable
graph = get_graph()
