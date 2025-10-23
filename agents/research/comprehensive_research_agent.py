#!/usr/bin/env python3
"""
Comprehensive Research Agent - Enhanced Multi-Domain Research System
================================================================

Building on the successful PhilosophyResearchAgent to create a comprehensive
research system that supports all agent types and development domains.

This system implements the Research-First Principle with web search integration,
intelligent caching, and multi-domain research capabilities.

Created: 2025-09-22 (Research Enhancement Sprint)
Status: US-RESEARCH-001 Implementation
"""

import os
import json
import asyncio
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3


# LangGraph integration check
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from pydantic import BaseModel, Field
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available - agent will work in legacy mode only")

# Core imports
from agents.core.enhanced_base_agent import EnhancedBaseAgent
from agents.core.base_agent import AgentConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchDomain(Enum):
    """Research domains supported by the system."""
    PHILOSOPHY = "philosophy"
    TECHNOLOGY = "technology" 
    SOFTWARE_ENGINEERING = "software_engineering"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    TESTING = "testing"
    AGILE = "agile"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    AI_ML = "ai_ml"
    FRAMEWORKS = "frameworks"
    TOOLS = "tools"
    BEST_PRACTICES = "best_practices"
    INDUSTRY_STANDARDS = "industry_standards"

class ResearchPriority(Enum):
    """Research priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"

class ResearchStatus(Enum):
    """Research status states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CACHED = "cached"
    FAILED = "failed"
    INVALIDATED = "invalidated"

@dataclass
class ResearchQuery:
    """Represents a research query."""
    query_id: str
    domain: ResearchDomain
    query_text: str
    priority: ResearchPriority
    context: Dict[str, Any]
    requested_by: str
    created_at: str
    deadline: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass  
class ResearchResult:
    """Represents research findings."""
    query_id: str
    domain: ResearchDomain
    status: ResearchStatus
    findings: Dict[str, Any]
    sources: List[Dict[str, str]]
    confidence_score: float
    relevance_score: float
    created_at: str
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ResearchRecommendation:
    """Represents a research-based recommendation."""
    recommendation_id: str
    title: str
    description: str
    impact_level: str  # 'high', 'medium', 'low'
    implementation_effort: str  # 'low', 'medium', 'high'
    research_evidence: List[str]
    confidence_score: float
    created_at: str



class ComprehensiveResearchAgentState(BaseModel):
    """State for ComprehensiveResearchAgent LangGraph workflow using Pydantic BaseModel."""
    
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

class ComprehensiveResearchAgent(EnhancedBaseAgent):
    """
    Enhanced research agent with multi-domain capabilities, web search integration,
    and intelligent caching. Builds on PhilosophyResearchAgent foundation.
    """
    
    def __init__(self, project_root: str = ".", config: Optional[AgentConfig] = None):
        """Initialize the comprehensive research agent."""
        
        if config is None:
            config = AgentConfig(
                agent_id="comprehensive_research_agent",
                agent_type="research",
                prompt_template_id="research_comprehensive",
                max_retries=2,
                timeout_seconds=300
            )
        
        super().__init__(config)
        
        self.project_root = Path(project_root)
        self.research_db_path = self.project_root / "data" / "research_cache.db"
        self.research_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize research databases
        self._init_research_database()
        
        # Research capabilities
        self.domain_specialists = self._initialize_domain_specialists()
        self.web_search_enabled = self._check_web_search_availability()
        
        # Cache and performance settings
        self.cache_expiry_days = 30
        self.max_concurrent_searches = 3
        self.confidence_threshold = 0.7
        
        # Research findings storage
        self.research_cache: Dict[str, ResearchResult] = {}
        self.active_queries: Dict[str, ResearchQuery] = {}
        
        logger.info("✅ Comprehensive Research Agent initialized")
        logger.info(f"📂 Research database: {self.research_db_path}")
        logger.info(f"🌐 Web search available: {self.web_search_enabled}")
    
        
        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_langgraph_workflow()
            self.app = self.workflow.compile()
            self.logger.info("✅ LangGraph workflow compiled and ready")
        else:
            self.workflow = None
            self.app = None
            self.logger.info("⚠️ LangGraph not available - using legacy mode")

    def execute_sync(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for execute method."""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, we need to handle this differently
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.execute(task))
                    return future.result()
            else:
                return loop.run_until_complete(self.execute(task))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self.execute(task))
    
    def _init_research_database(self):
        """Initialize SQLite database for research caching."""
        with sqlite3.connect(self.research_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS research_queries (
                    query_id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    query_text TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    context TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    deadline TEXT,
                    tags TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS research_results (
                    query_id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    status TEXT NOT NULL,
                    findings TEXT NOT NULL,
                    sources TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    relevance_score REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS research_recommendations (
                    recommendation_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    impact_level TEXT NOT NULL,
                    implementation_effort TEXT NOT NULL,
                    research_evidence TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
        
        logger.info("✅ Research database initialized")
    
    def _initialize_domain_specialists(self) -> Dict[ResearchDomain, Dict[str, Any]]:
        """Initialize domain-specific research capabilities."""
        
        specialists = {
            ResearchDomain.PHILOSOPHY: {
                "keywords": ["philosophy", "ethics", "values", "principles", "wisdom"],
                "sources": ["academic", "philosophical", "ethical"],
                "validation_criteria": ["logical_consistency", "ethical_alignment", "practical_applicability"]
            },
            ResearchDomain.SOFTWARE_ENGINEERING: {
                "keywords": ["software engineering", "development practices", "clean code", "SOLID"],
                "sources": ["technical", "academic", "industry"],
                "validation_criteria": ["proven_effectiveness", "industry_adoption", "maintainability"]
            },
            ResearchDomain.ARCHITECTURE: {
                "keywords": ["software architecture", "design patterns", "system design", "scalability"],
                "sources": ["technical", "architectural", "best_practices"],
                "validation_criteria": ["scalability", "maintainability", "performance"]
            },
            ResearchDomain.SECURITY: {
                "keywords": ["cybersecurity", "security practices", "vulnerabilities", "encryption"],
                "sources": ["security", "technical", "standards"],
                "validation_criteria": ["security_effectiveness", "compliance", "risk_reduction"]
            },
            ResearchDomain.TESTING: {
                "keywords": ["software testing", "test automation", "quality assurance", "TDD"],
                "sources": ["technical", "testing", "quality"],
                "validation_criteria": ["test_effectiveness", "coverage", "reliability"]
            },
            ResearchDomain.AGILE: {
                "keywords": ["agile methodology", "scrum", "kanban", "project management"],
                "sources": ["methodology", "project_management", "agile"],
                "validation_criteria": ["team_effectiveness", "delivery_improvement", "adaptability"]
            }
        }
        
        return specialists
    
    def _check_web_search_availability(self) -> bool:
        """Check if web search capabilities are available."""
        try:
            # Check for web search dependencies
            import requests
            return True
        except ImportError:
            logger.warning("⚠️ Web search not available - install requests package")
            return False
    
    async def research(self, 
                      query: str, 
                      domain: Union[ResearchDomain, str],
                      priority: Union[ResearchPriority, str] = ResearchPriority.MEDIUM,
                      context: Optional[Dict[str, Any]] = None,
                      use_cache: bool = True,
                      use_web_search: bool = True) -> ResearchResult:
        """
        Main research method - comprehensive research with caching and web search.
        
        Args:
            query: Research question or topic
            domain: Research domain (ResearchDomain enum or string)
            priority: Research priority level
            context: Additional context for the research
            use_cache: Whether to use cached results
            use_web_search: Whether to use web search
            
        Returns:
            ResearchResult with findings and metadata
        """
        
        # Normalize inputs
        if isinstance(domain, str):
            domain = ResearchDomain(domain)
        if isinstance(priority, str):
            priority = ResearchPriority(priority)
        if context is None:
            context = {}
        
        # Generate query ID
        query_id = self._generate_query_id(query, domain, context)
        
        # Check cache first
        if use_cache:
            cached_result = self._get_cached_result(query_id)
            if cached_result and not self._is_result_expired(cached_result):
                logger.info(f"📋 Using cached research result for: {query}")
                cached_result.status = ResearchStatus.CACHED
                return cached_result
        
        # Create research query
        research_query = ResearchQuery(
            query_id=query_id,
            domain=domain,
            query_text=query,
            priority=priority,
            context=context,
            requested_by=self.config.agent_id,
            created_at=datetime.now().isoformat()
        )
        
        # Store active query
        self.active_queries[query_id] = research_query
        self._save_query_to_db(research_query)
        
        logger.info(f"🔍 Starting research: {query} (Domain: {domain.value})")
        
        try:
            # Perform research
            result = await self._perform_comprehensive_research(research_query, use_web_search)
            
            # Cache result
            if result.confidence_score >= self.confidence_threshold:
                self._cache_result(result)
            
            # Clean up active query
            del self.active_queries[query_id]
            
            logger.info(f"✅ Research completed: {query} (Confidence: {result.confidence_score:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Research failed: {query} - {e}")
            
            # Create failed result
            failed_result = ResearchResult(
                query_id=query_id,
                domain=domain,
                status=ResearchStatus.FAILED,
                findings={"error": str(e)},
                sources=[],
                confidence_score=0.0,
                relevance_score=0.0,
                created_at=datetime.now().isoformat()
            )
            
            # Clean up active query
            if query_id in self.active_queries:
                del self.active_queries[query_id]
            
            return failed_result
    
    async def _perform_comprehensive_research(self, 
                                            query: ResearchQuery, 
                                            use_web_search: bool) -> ResearchResult:
        """Perform comprehensive research using multiple sources."""
        
        findings = {}
        sources = []
        confidence_scores = []
        
        # 1. Domain-specific research
        domain_findings = await self._research_domain_specific(query)
        findings.update(domain_findings["findings"])
        sources.extend(domain_findings["sources"])
        confidence_scores.append(domain_findings["confidence"])
        
        # 2. Local knowledge base research
        local_findings = await self._research_local_knowledge(query)
        findings.update(local_findings["findings"])
        sources.extend(local_findings["sources"])
        confidence_scores.append(local_findings["confidence"])
        
        # 3. Web search research (if enabled)
        if use_web_search and self.web_search_enabled:
            web_findings = await self._research_web_search(query)
            findings.update(web_findings["findings"])
            sources.extend(web_findings["sources"])
            confidence_scores.append(web_findings["confidence"])
        
        # 4. Cross-reference validation
        validation_score = await self._validate_research_findings(findings, sources)
        confidence_scores.append(validation_score)
        
        # Calculate overall confidence and relevance
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        relevance_score = self._calculate_relevance_score(query, findings)
        
        # Create result
        result = ResearchResult(
            query_id=query.query_id,
            domain=query.domain,
            status=ResearchStatus.COMPLETED,
            findings=findings,
            sources=sources,
            confidence_score=overall_confidence,
            relevance_score=relevance_score,
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(days=self.cache_expiry_days)).isoformat(),
            metadata={
                "research_method": "comprehensive",
                "domain_specialist": True,
                "local_knowledge": True,
                "web_search": use_web_search and self.web_search_enabled,
                "validation_performed": True
            }
        )
        
        return result
    
    async def _research_domain_specific(self, query: ResearchQuery) -> Dict[str, Any]:
        """Perform domain-specific research using specialized knowledge."""
        
        domain_spec = self.domain_specialists.get(query.domain, {})
        keywords = domain_spec.get("keywords", [])
        
        findings = {
            "domain_analysis": {
                "domain": query.domain.value,
                "specialized_keywords": keywords,
                "research_focus": self._extract_research_focus(query.query_text, keywords),
                "domain_context": self._get_domain_context(query.domain)
            }
        }
        
        sources = [{
            "type": "domain_specialist",
            "domain": query.domain.value,
            "confidence": 0.9
        }]
        
        return {
            "findings": findings,
            "sources": sources,
            "confidence": 0.85
        }
    
    async def _research_local_knowledge(self, query: ResearchQuery) -> Dict[str, Any]:
        """Research using local knowledge base and documentation."""
        
        findings = {
            "local_knowledge": {
                "project_documentation": self._scan_project_documentation(query.query_text),
                "existing_implementations": self._find_existing_implementations(query),
                "related_files": self._find_related_files(query.query_text)
            }
        }
        
        sources = [{
            "type": "local_knowledge",
            "location": str(self.project_root),
            "confidence": 0.95
        }]
        
        return {
            "findings": findings,
            "sources": sources,
            "confidence": 0.80
        }
    
    async def _research_web_search(self, query: ResearchQuery) -> Dict[str, Any]:
        """Perform web search research with validation."""
        
        if not self.web_search_enabled:
            return {"findings": {}, "sources": [], "confidence": 0.0}
        
        try:
            # Prepare search query
            search_query = self._optimize_search_query(query)
            
            # Perform web search (placeholder - would integrate with actual web search API)
            search_results = await self._perform_web_search(search_query)
            
            # Validate and process results
            validated_results = self._validate_web_results(search_results, query)
            
            findings = {
                "web_research": {
                    "search_query": search_query,
                    "results_count": len(validated_results),
                    "key_findings": self._extract_key_findings(validated_results),
                    "authoritative_sources": self._identify_authoritative_sources(validated_results)
                }
            }
            
            sources = [{
                "type": "web_search",
                "search_query": search_query,
                "results_processed": len(validated_results),
                "confidence": 0.75
            }]
            
            return {
                "findings": findings,
                "sources": sources,
                "confidence": 0.70
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Web search failed: {e}")
            return {"findings": {}, "sources": [], "confidence": 0.0}
    
    def _generate_query_id(self, query: str, domain: ResearchDomain, context: Dict[str, Any]) -> str:
        """Generate unique ID for research query."""
        content = f"{query}:{domain.value}:{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_result(self, query_id: str) -> Optional[ResearchResult]:
        """Get cached research result."""
        try:
            with sqlite3.connect(self.research_db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM research_results WHERE query_id = ?",
                    (query_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return ResearchResult(
                        query_id=row[0],
                        domain=ResearchDomain(row[1]),
                        status=ResearchStatus(row[2]),
                        findings=json.loads(row[3]),
                        sources=json.loads(row[4]),
                        confidence_score=row[5],
                        relevance_score=row[6],
                        created_at=row[7],
                        expires_at=row[8],
                        metadata=json.loads(row[9]) if row[9] else {}
                    )
        except Exception as e:
            logger.warning(f"⚠️ Cache lookup failed: {e}")
        
        return None
    
    def _is_result_expired(self, result: ResearchResult) -> bool:
        """Check if research result has expired."""
        if not result.expires_at:
            return False
        
        try:
            expires = datetime.fromisoformat(result.expires_at)
            return datetime.now() > expires
        except:
            return True
    
    def _cache_result(self, result: ResearchResult):
        """Cache research result to database."""
        try:
            with sqlite3.connect(self.research_db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO research_results 
                    (query_id, domain, status, findings, sources, confidence_score, 
                     relevance_score, created_at, expires_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.query_id,
                    result.domain.value,
                    result.status.value,
                    json.dumps(result.findings),
                    json.dumps(result.sources),
                    result.confidence_score,
                    result.relevance_score,
                    result.created_at,
                    result.expires_at,
                    json.dumps(result.metadata)
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"⚠️ Cache save failed: {e}")
    
    def _save_query_to_db(self, query: ResearchQuery):
        """Save research query to database."""
        try:
            with sqlite3.connect(self.research_db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO research_queries 
                    (query_id, domain, query_text, priority, context, requested_by, 
                     created_at, deadline, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    query.query_id,
                    query.domain.value,
                    query.query_text,
                    query.priority.value,
                    json.dumps(query.context),
                    query.requested_by,
                    query.created_at,
                    query.deadline,
                    json.dumps(query.tags)
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"⚠️ Query save failed: {e}")
    
    def get_research_recommendations(self, domain: Optional[ResearchDomain] = None) -> List[ResearchRecommendation]:
        """Get research-based recommendations."""
        try:
            with sqlite3.connect(self.research_db_path) as conn:
                if domain:
                    cursor = conn.execute(
                        "SELECT * FROM research_recommendations WHERE research_evidence LIKE ?",
                        (f"%{domain.value}%",)
                    )
                else:
                    cursor = conn.execute("SELECT * FROM research_recommendations")
                
                recommendations = []
                for row in cursor.fetchall():
                    recommendations.append(ResearchRecommendation(
                        recommendation_id=row[0],
                        title=row[1],
                        description=row[2],
                        impact_level=row[3],
                        implementation_effort=row[4],
                        research_evidence=json.loads(row[5]),
                        confidence_score=row[6],
                        created_at=row[7]
                    ))
                
                return recommendations
        except Exception as e:
            logger.warning(f"⚠️ Recommendations retrieval failed: {e}")
            return []
    
    # Validation and helper methods
    async def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate research task."""
        required_fields = ["query", "domain"]
        return all(field in task for field in required_fields)
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task."""
        query = task.get("query", "")
        domain = task.get("domain", ResearchDomain.TECHNOLOGY)
        priority = task.get("priority", ResearchPriority.MEDIUM)
        context = task.get("context", {})
        
        result = await self.research(query, domain, priority, context)
        
        return {
            "status": "completed",
            "result": asdict(result),
            "timestamp": datetime.now().isoformat()
        }
    
    # Helper methods for research implementation
    def _extract_research_focus(self, query: str, keywords: List[str]) -> List[str]:
        """Extract research focus areas from query."""
        focus_areas = []
        query_lower = query.lower()
        
        for keyword in keywords:
            if keyword.lower() in query_lower:
                focus_areas.append(keyword)
        
        return focus_areas
    
    def _get_domain_context(self, domain: ResearchDomain) -> Dict[str, Any]:
        """Get context for specific research domain."""
        context_map = {
            ResearchDomain.PHILOSOPHY: {
                "core_concepts": ["ethics", "values", "principles", "wisdom"],
                "application_areas": ["development_ethics", "user_care", "team_values"]
            },
            ResearchDomain.SOFTWARE_ENGINEERING: {
                "core_concepts": ["clean_code", "SOLID", "patterns", "practices"],
                "application_areas": ["code_quality", "maintainability", "scalability"]
            },
            ResearchDomain.SECURITY: {
                "core_concepts": ["authentication", "authorization", "encryption", "validation"],
                "application_areas": ["application_security", "data_protection", "access_control"]
            }
        }
        
        return context_map.get(domain, {"core_concepts": [], "application_areas": []})
    
    def _scan_project_documentation(self, query: str) -> List[Dict[str, str]]:
        """Scan project documentation for relevant information."""
        docs_dir = self.project_root / "docs"
        relevant_docs = []
        
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*.md"):
                if self._is_document_relevant(doc_file, query):
                    relevant_docs.append({
                        "file": str(doc_file),
                        "type": "documentation",
                        "relevance": "high"
                    })
        
        return relevant_docs
    
    def _find_existing_implementations(self, query: ResearchQuery) -> List[Dict[str, str]]:
        """Find existing implementations related to the query."""
        implementations = []
        
        # Search for relevant Python files
        for py_file in self.project_root.rglob("*.py"):
            if self._is_file_relevant(py_file, query.query_text):
                implementations.append({
                    "file": str(py_file),
                    "type": "implementation",
                    "domain": query.domain.value
                })
        
        return implementations
    
    def _find_related_files(self, query: str) -> List[str]:
        """Find files related to the research query."""
        related_files = []
        query_words = query.lower().split()
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                file_name_lower = file_path.name.lower()
                if any(word in file_name_lower for word in query_words):
                    related_files.append(str(file_path))
        
        return related_files[:10]  # Limit to 10 most relevant
    
    def _is_document_relevant(self, doc_path: Path, query: str) -> bool:
        """Check if document is relevant to query."""
        try:
            content = doc_path.read_text(encoding='utf-8').lower()
            query_words = query.lower().split()
            return any(word in content for word in query_words if len(word) > 3)
        except:
            return False
    
    def _is_file_relevant(self, file_path: Path, query: str) -> bool:
        """Check if file is relevant to query."""
        file_name = file_path.name.lower()
        query_words = query.lower().split()
        return any(word in file_name for word in query_words if len(word) > 3)
    
    async def _validate_research_findings(self, findings: Dict[str, Any], sources: List[Dict[str, str]]) -> float:
        """Validate research findings across sources."""
        if not findings or not sources:
            return 0.0
        
        # Cross-reference validation
        source_types = set(source.get("type", "") for source in sources)
        
        # Higher confidence if multiple source types agree
        if len(source_types) >= 2:
            return 0.9
        elif len(source_types) == 1:
            return 0.7
        else:
            return 0.5
    
    def _calculate_relevance_score(self, query: ResearchQuery, findings: Dict[str, Any]) -> float:
        """Calculate relevance score for research findings."""
        if not findings:
            return 0.0
        
        # Count relevant sections
        relevant_sections = 0
        total_sections = len(findings)
        
        query_words = set(query.query_text.lower().split())
        
        for section_data in findings.values():
            if isinstance(section_data, dict):
                section_text = json.dumps(section_data).lower()
                if any(word in section_text for word in query_words):
                    relevant_sections += 1
        
        return relevant_sections / total_sections if total_sections > 0 else 0.0
    
    # Placeholder methods for web search (to be implemented with actual web search API)
    def _optimize_search_query(self, query: ResearchQuery) -> str:
        """Optimize query for web search."""
        # Add domain-specific keywords
        domain_spec = self.domain_specialists.get(query.domain, {})
        keywords = domain_spec.get("keywords", [])
        
        optimized_query = query.query_text
        if keywords:
            optimized_query += f" {' '.join(keywords[:2])}"
        
        return optimized_query
    
    async def _perform_web_search(self, search_query: str) -> List[Dict[str, Any]]:
        """Perform actual web search (placeholder for real implementation)."""
        # Placeholder - would integrate with actual web search API
        return [
            {
                "title": f"Research result for: {search_query}",
                "url": "https://example.com/research",
                "snippet": f"Relevant information about {search_query}",
                "source": "academic"
            }
        ]
    
    def _validate_web_results(self, results: List[Dict[str, Any]], query: ResearchQuery) -> List[Dict[str, Any]]:
        """Validate web search results."""
        validated = []
        
        for result in results:
            # Basic validation
            if result.get("title") and result.get("snippet"):
                # Add validation score
                result["validation_score"] = 0.8
                validated.append(result)
        
        return validated
    
    def _extract_key_findings(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract key findings from web search results."""
        findings = []
        
        for result in results[:5]:  # Top 5 results
            snippet = result.get("snippet", "")
            if snippet:
                findings.append(snippet)
        
        return findings
    
    def _identify_authoritative_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identify authoritative sources from results."""
        authoritative_domains = [
            "github.com", "stackoverflow.com", "docs.python.org",
            "academic.edu", "ieee.org", "acm.org"
        ]
        
        authoritative = []
        for result in results:
            url = result.get("url", "")
            if any(domain in url for domain in authoritative_domains):
                authoritative.append({
                    "title": result.get("title", ""),
                    "url": url,
                    "authority_score": "high"
                })
        
        return authoritative
    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Build LangGraph workflow for ComprehensiveResearchAgent."""
        workflow = StateGraph(ComprehensiveResearchAgentState)
        
        # Simple workflow: just execute the agent
        workflow.add_node("execute", self._langgraph_execute_node)
        workflow.set_entry_point("execute")
        workflow.add_edge("execute", END)
        
        return workflow
    
    async def _langgraph_execute_node(self, state: ComprehensiveResearchAgentState) -> ComprehensiveResearchAgentState:
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


# Factory function for easy instantiation
def create_research_agent(project_root: str = ".") -> ComprehensiveResearchAgent:
    """Create and return a configured research agent."""
    return ComprehensiveResearchAgent(project_root)


# Example usage and testing
if __name__ == "__main__":
    async def test_research_agent():
        """Test the research agent functionality."""
        print("🧪 Testing Comprehensive Research Agent...")
        
        agent = create_research_agent()
        
        # Test basic research
        result = await agent.research(
            query="best practices for clean code",
            domain=ResearchDomain.SOFTWARE_ENGINEERING,
            priority=ResearchPriority.HIGH
        )
        
        print(f"✅ Research completed: {result.status}")
        print(f"📊 Confidence: {result.confidence_score:.2f}")
        print(f"🎯 Relevance: {result.relevance_score:.2f}")
        print(f"📚 Sources: {len(result.sources)}")
        
        return result
    
    # Run test
    import asyncio
    result = asyncio.run(test_research_agent())
    print("🎉 Research agent test completed!")


# Export for LangGraph Studio
_default_instance = None

def get_graph():
    """Get the compiled graph for LangGraph Studio."""
    global _default_instance
    if _default_instance is None and LANGGRAPH_AVAILABLE:
        from models.config import AgentConfig
        
        config = AgentConfig(
            agent_id='comprehensive_research_agent',
            name='ComprehensiveResearchAgent',
            description='ComprehensiveResearchAgent agent',
            model_name='gemini-2.5-flash'
        )
        _default_instance = ComprehensiveResearchAgent(".", config)
    return _default_instance.app if _default_instance else None

# Studio expects 'graph' variable
graph = get_graph()
