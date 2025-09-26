"""
Research Agents Module
===================

This module provides comprehensive research capabilities for the AI Development Agent system.
Built on the foundation of the successful PhilosophyResearchAgent, it extends research
capabilities to all domains with web search integration and intelligent caching.

Key Components:
- ComprehensiveResearchAgent: Multi-domain research with web search and caching
- ResearchDomain: Supported research domains and specializations
- ResearchQuery/ResearchResult: Data structures for research operations

Usage:
    from agents.research import ComprehensiveResearchAgent, ResearchDomain
    
    agent = ComprehensiveResearchAgent()
    result = await agent.research(
        query="best practices for testing",
        domain=ResearchDomain.TESTING
    )
"""

from .comprehensive_research_agent import (
    ComprehensiveResearchAgent,
    ResearchDomain,
    ResearchPriority,
    ResearchStatus,
    ResearchQuery,
    ResearchResult,
    ResearchRecommendation,
    create_research_agent
)

__all__ = [
    "ComprehensiveResearchAgent",
    "ResearchDomain", 
    "ResearchPriority",
    "ResearchStatus",
    "ResearchQuery",
    "ResearchResult", 
    "ResearchRecommendation",
    "create_research_agent"
]

__version__ = "1.0.0"
__description__ = "Comprehensive Research Agent System"

