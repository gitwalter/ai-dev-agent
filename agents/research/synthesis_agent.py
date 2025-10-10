#!/usr/bin/env python3
"""
Synthesis Agent - Research Swarm
=================================

Synthesizes research findings into comprehensive report.

Responsibilities:
- Combine information from multiple sources
- Organize findings logically
- Create comprehensive report
- Cite sources properly
- Generate executive summary

Created: 2025-10-10
Part of: Web Research Swarm
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
import json

from agents.core.enhanced_base_agent import EnhancedBaseAgent
from models.config import AgentConfig

logger = logging.getLogger(__name__)


class SynthesisAgent(EnhancedBaseAgent):
    """
    Synthesizes research findings into comprehensive report.
    
    This agent combines information from multiple verified sources into
    a well-organized research report with proper citations.
    """
    
    def __init__(self):
        """Initialize Synthesis Agent with Gemini 2.0 Flash."""
        config = AgentConfig(
            agent_id="synthesis",
            agent_type="research",
            prompt_template_id="research_synthesis",
            model_name="gemini-2.0-flash-exp",
            max_retries=2,
            timeout_seconds=60
        )
        super().__init__(config)
        logger.info("✅ SynthesisAgent initialized")
    
    async def synthesize(
        self,
        query: str,
        verified_content: List[Dict],
        research_plan: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Synthesize research findings into comprehensive report.
        
        Args:
            query: Original research query
            verified_content: List of verified content items
            research_plan: Optional research plan from QueryPlannerAgent
            
        Returns:
            Research report with:
            - executive_summary: str
            - key_findings: List[str]
            - detailed_analysis: str
            - sources_cited: List[Dict]
            - recommendations: List[str]
            - metadata: Dict
        """
        if not verified_content:
            return self._empty_report(query)
        
        # Prepare content for synthesis
        content_for_synthesis = self._prepare_content(verified_content)
        
        # Generate synthesis using LLM
        synthesis = await self._generate_synthesis(
            query,
            content_for_synthesis,
            research_plan
        )
        
        # Add metadata
        synthesis["sources_used"] = len(verified_content)
        synthesis["sources_cited"] = self._extract_source_citations(verified_content)
        synthesis["timestamp"] = datetime.now().isoformat()
        synthesis["query"] = query
        
        logger.info(
            f"✅ Synthesis complete: {len(verified_content)} sources synthesized "
            f"into {len(synthesis.get('key_findings', []))} key findings"
        )
        
        return synthesis
    
    async def _generate_synthesis(
        self,
        query: str,
        content: str,
        research_plan: Optional[Dict]
    ) -> Dict[str, Any]:
        """Generate synthesis using LLM."""
        
        prompt = self._create_synthesis_prompt(query, content, research_plan)
        
        try:
            result = await self.execute_async({"prompt": prompt})
            
            if result.get("success"):
                response = result.get("content", "{}")
                synthesis = self._extract_json(response)
                
                # Validate synthesis structure
                synthesis = self._validate_synthesis(synthesis, query)
                
                return synthesis
            else:
                logger.error(f"Synthesis generation failed: {result.get('error')}")
                return self._default_report(query, content)
                
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return self._default_report(query, content)
    
    def _create_synthesis_prompt(
        self,
        query: str,
        content: str,
        research_plan: Optional[Dict]
    ) -> str:
        """Create prompt for synthesis generation."""
        
        plan_context = ""
        if research_plan:
            sub_queries = research_plan.get("sub_queries", [])
            if sub_queries:
                plan_context = f"\nSub-questions to address: {', '.join(sub_queries)}"
        
        return f"""
You are an expert research synthesizer. Create a comprehensive research report from the following sources.

Research Query: {query}{plan_context}

Research Findings:
{content}

Create a well-structured research report in JSON format with:

1. **executive_summary**: A concise 2-3 sentence summary of key findings
2. **key_findings**: 5-7 most important findings as bullet points
3. **detailed_analysis**: Comprehensive analysis organized into logical sections
4. **recommendations**: 3-5 actionable recommendations based on findings
5. **confidence_level**: Overall confidence in findings (low/medium/high)
6. **gaps_identified**: Any gaps in research or areas needing more investigation

Return ONLY valid JSON with this structure:
{{
    "executive_summary": "...",
    "key_findings": ["finding1", "finding2", ...],
    "detailed_analysis": "...",
    "recommendations": ["rec1", "rec2", ...],
    "confidence_level": "medium",
    "gaps_identified": ["gap1", ...]
}}

Focus on:
- Accuracy and factual correctness
- Logical organization
- Clear, professional language
- Actionable insights
"""
    
    def _prepare_content(self, verified_content: List[Dict]) -> str:
        """Prepare content for synthesis."""
        content_parts = []
        
        for idx, item in enumerate(verified_content, 1):
            title = item.get("source_title", "Unknown Source")
            key_points = item.get("key_points", [])
            url = item.get("source_url", "")
            
            part = f"Source {idx}: {title}\nURL: {url}"
            
            if key_points:
                part += f"\nKey Points:\n" + "\n".join(f"- {point}" for point in key_points)
            
            # Add excerpt of extracted content
            content = item.get("extracted_content", "")
            if content and len(content) > 100:
                part += f"\nExcerpt: {content[:500]}..."
            
            content_parts.append(part)
        
        # Limit total content for token efficiency
        full_content = "\n\n".join(content_parts)
        
        # Truncate if too long (max ~8000 chars for prompt)
        if len(full_content) > 8000:
            full_content = full_content[:8000] + "\n\n[Content truncated for length...]"
        
        return full_content
    
    def _extract_json(self, content: str) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        try:
            # Remove markdown code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end]
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end]
            
            return json.loads(content.strip())
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"JSON extraction error: {e}")
            return {}
    
    def _validate_synthesis(self, synthesis: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Validate and ensure synthesis has all required fields."""
        validated = {
            "executive_summary": synthesis.get("executive_summary", f"Research findings for: {query}"),
            "key_findings": synthesis.get("key_findings", []),
            "detailed_analysis": synthesis.get("detailed_analysis", "Analysis based on collected sources."),
            "recommendations": synthesis.get("recommendations", []),
            "confidence_level": synthesis.get("confidence_level", "medium"),
            "gaps_identified": synthesis.get("gaps_identified", [])
        }
        
        # Ensure confidence level is valid
        if validated["confidence_level"] not in ["low", "medium", "high"]:
            validated["confidence_level"] = "medium"
        
        return validated
    
    def _extract_source_citations(self, verified_content: List[Dict]) -> List[Dict[str, str]]:
        """Extract source citations."""
        citations = []
        
        for item in verified_content:
            citation = {
                "title": item.get("source_title", "Unknown"),
                "url": item.get("source_url", ""),
                "accessed": datetime.now().strftime("%Y-%m-%d")
            }
            citations.append(citation)
        
        return citations
    
    def _default_report(self, query: str, content: str) -> Dict[str, Any]:
        """Fallback report when LLM synthesis fails."""
        return {
            "executive_summary": f"Research completed for: {query}",
            "key_findings": [
                "Multiple sources analyzed",
                "Information gathered from verified sources",
                "Findings available in detailed analysis"
            ],
            "detailed_analysis": f"Research findings:\n\n{content[:1000]}...",
            "recommendations": [
                "Review detailed findings",
                "Verify critical information",
                "Consider additional research if needed"
            ],
            "confidence_level": "medium",
            "gaps_identified": ["Automated synthesis unavailable"]
        }
    
    def _empty_report(self, query: str) -> Dict[str, Any]:
        """Report for empty content."""
        return {
            "executive_summary": f"No verified sources found for: {query}",
            "key_findings": [],
            "detailed_analysis": "No content available for analysis.",
            "recommendations": ["Refine search terms", "Try different sources", "Expand search scope"],
            "confidence_level": "low",
            "gaps_identified": ["No sources available"],
            "sources_used": 0,
            "sources_cited": [],
            "timestamp": datetime.now().isoformat(),
            "query": query
        }


if __name__ == "__main__":
    import asyncio
    
    async def test_synthesis():
        """Test Synthesis Agent."""
        print("🧪 Testing Synthesis Agent\n")
        
        agent = SynthesisAgent()
        
        # Simulate verified content
        verified_content = [
            {
                "source_url": "https://example.com/google-api",
                "source_title": "Google Drive API Documentation",
                "key_points": [
                    "Requires OAuth2 authentication",
                    "Python client library available",
                    "Supports file upload and download"
                ],
                "extracted_content": "The Google Drive API allows developers to integrate..."
            },
            {
                "source_url": "https://example.com/mcp-integration",
                "source_title": "MCP Server Integration Guide",
                "key_points": [
                    "MCP servers use tool registration",
                    "Support for various API types",
                    "Built-in authentication management"
                ],
                "extracted_content": "Model Context Protocol servers provide..."
            },
            {
                "source_url": "https://example.com/best-practices",
                "source_title": "API Integration Best Practices",
                "key_points": [
                    "Implement rate limiting",
                    "Use exponential backoff",
                    "Secure API key storage"
                ],
                "extracted_content": "When integrating APIs, follow these best practices..."
            }
        ]
        
        report = await agent.synthesize(
            query="How to integrate Google Drive API with Python MCP server?",
            verified_content=verified_content
        )
        
        print(f"✅ Synthesis Complete:")
        print(f"   Sources used: {report['sources_used']}")
        print(f"   Key findings: {len(report['key_findings'])}")
        print(f"   Confidence: {report['confidence_level']}")
        print(f"\n📋 Executive Summary:")
        print(f"   {report['executive_summary']}")
        print(f"\n🔍 Key Findings:")
        for i, finding in enumerate(report['key_findings'][:3], 1):
            print(f"   {i}. {finding}")
    
    asyncio.run(test_synthesis())

