#!/usr/bin/env python3
"""
Verification Agent - Research Swarm
====================================

Verifies information quality and reliability.

Responsibilities:
- Check source credibility
- Verify fact accuracy
- Detect contradictions
- Assess information quality
- Trigger re-search if quality insufficient

Created: 2025-10-10
Part of: Web Research Swarm
"""

import logging
from typing import Dict, List, Any

from agents.core.enhanced_base_agent import EnhancedBaseAgent
from models.config import AgentConfig

logger = logging.getLogger(__name__)


class VerificationAgent(EnhancedBaseAgent):
    """
    Verifies information quality and reliability.
    
    This agent assesses the credibility, accuracy, and completeness of
    research findings, and determines if additional research is needed.
    """
    
    def __init__(self):
        """Initialize Verification Agent with Gemini 2.0 Flash."""
        config = AgentConfig(
            agent_id="verification",
            agent_type="research",
            prompt_template_id="research_verification",
            model_name="gemini-2.0-flash-exp",
            max_retries=2,
            timeout_seconds=30
        )
        super().__init__(config)
        logger.info("✅ VerificationAgent initialized")
    
    async def verify(
        self,
        parsed_content: List[Dict],
        query: str,
        quality_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Verify information quality and reliability.
        
        Args:
            parsed_content: List of parsed content items
            query: Original research query
            quality_threshold: Minimum quality score (0-1)
            
        Returns:
            Verification report with:
            - total_sources: int
            - verified_sources: int
            - quality_score: float (0-1)
            - credibility_score: float (0-1)
            - coverage_score: float (0-1)
            - needs_additional_search: bool
            - warnings: List[str]
            - verified_content: List[Dict] (filtered content)
        """
        total_sources = len(parsed_content)
        
        if total_sources == 0:
            return self._empty_verification_report()
        
        # Analyze content quality
        quality_analysis = await self._analyze_quality(parsed_content, query)
        
        # Filter low-quality sources
        verified_content = self._filter_quality_content(
            parsed_content,
            quality_analysis,
            quality_threshold
        )
        
        verified_count = len(verified_content)
        
        # Calculate scores
        quality_score = quality_analysis.get("overall_quality", 0.0)
        credibility_score = quality_analysis.get("credibility", 0.0)
        coverage_score = self._calculate_coverage(verified_content, query)
        
        # Determine if more research needed
        needs_more = self._needs_additional_research(
            quality_score,
            coverage_score,
            verified_count,
            quality_threshold
        )
        
        # Generate warnings
        warnings = self._generate_warnings(
            quality_score,
            credibility_score,
            coverage_score,
            verified_count,
            total_sources
        )
        
        report = {
            "total_sources": total_sources,
            "verified_sources": verified_count,
            "quality_score": round(quality_score, 2),
            "credibility_score": round(credibility_score, 2),
            "coverage_score": round(coverage_score, 2),
            "needs_additional_search": needs_more,
            "warnings": warnings,
            "verified_content": verified_content,
            "quality_analysis": quality_analysis
        }
        
        logger.info(
            f"✅ Verification complete: {verified_count}/{total_sources} sources verified "
            f"(Q:{quality_score:.2f}, C:{credibility_score:.2f}, Coverage:{coverage_score:.2f})"
        )
        
        return report
    
    async def _analyze_quality(self, content: List[Dict], query: str) -> Dict[str, Any]:
        """Analyze content quality using LLM."""
        
        # Prepare content summary for LLM
        content_summary = self._prepare_content_summary(content)
        
        prompt = f"""
Analyze the quality of these research sources for the query: "{query}"

Sources Summary:
{content_summary}

Evaluate:
1. **Overall Quality** (0-1): Relevance, depth, accuracy
2. **Credibility** (0-1): Source reliability, author expertise
3. **Consistency** (0-1): Agreement between sources
4. **Completeness** (0-1): Coverage of query aspects

Return JSON:
{{
    "overall_quality": 0.0-1.0,
    "credibility": 0.0-1.0,
    "consistency": 0.0-1.0,
    "completeness": 0.0-1.0,
    "strengths": ["strength1", ...],
    "weaknesses": ["weakness1", ...],
    "contradictions": ["contradiction1", ...]
}}
"""
        
        try:
            result = await self.execute_async({"prompt": prompt})
            
            if result.get("success"):
                import json
                content = result.get("content", "{}")
                
                # Extract JSON
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end]
                
                analysis = json.loads(content.strip())
                return analysis
            else:
                return self._default_quality_analysis()
                
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            return self._default_quality_analysis()
    
    def _prepare_content_summary(self, content: List[Dict]) -> str:
        """Prepare content summary for LLM analysis."""
        summaries = []
        
        for idx, item in enumerate(content[:10], 1):  # Limit to 10 for token efficiency
            title = item.get("source_title", "Unknown")
            key_points = item.get("key_points", [])
            
            summary = f"{idx}. {title}"
            if key_points:
                summary += f"\n   Key points: {', '.join(key_points[:3])}"
            
            summaries.append(summary)
        
        return "\n".join(summaries)
    
    def _filter_quality_content(
        self,
        content: List[Dict],
        analysis: Dict[str, Any],
        threshold: float
    ) -> List[Dict]:
        """Filter content based on quality scores."""
        # For now, use simple filtering
        # In production, could use per-source quality scores
        
        overall_quality = analysis.get("overall_quality", 0.0)
        
        if overall_quality >= threshold:
            # All content passes
            return content
        else:
            # Filter based on relevance scores in metadata
            filtered = [
                item for item in content
                if item.get("metadata", {}).get("relevance", 0) >= threshold
            ]
            return filtered if filtered else content[:max(1, len(content) // 2)]
    
    def _calculate_coverage(self, content: List[Dict], query: str) -> float:
        """Calculate how well content covers the query."""
        if not content:
            return 0.0
        
        # Simple heuristic: more sources with key points = better coverage
        sources_with_keypoints = sum(1 for item in content if item.get("key_points"))
        total_keypoints = sum(len(item.get("key_points", [])) for item in content)
        
        # Normalize to 0-1
        coverage = min(1.0, (sources_with_keypoints / len(content) + total_keypoints / (len(content) * 5)) / 2)
        
        return coverage
    
    def _needs_additional_research(
        self,
        quality: float,
        coverage: float,
        verified_count: int,
        threshold: float
    ) -> bool:
        """Determine if additional research is needed."""
        # Need more research if:
        # - Quality too low
        # - Coverage insufficient
        # - Too few verified sources
        
        if quality < threshold:
            return True
        if coverage < 0.6:
            return True
        if verified_count < 3:
            return True
        
        return False
    
    def _generate_warnings(
        self,
        quality: float,
        credibility: float,
        coverage: float,
        verified: int,
        total: int
    ) -> List[str]:
        """Generate warnings based on verification results."""
        warnings = []
        
        if quality < 0.5:
            warnings.append(f"Low quality score: {quality:.2f}")
        
        if credibility < 0.6:
            warnings.append(f"Low credibility score: {credibility:.2f}")
        
        if coverage < 0.5:
            warnings.append(f"Insufficient coverage: {coverage:.2f}")
        
        if verified < total * 0.5:
            warnings.append(f"Many sources filtered: {verified}/{total} verified")
        
        if verified < 3:
            warnings.append(f"Very few sources: only {verified} verified")
        
        return warnings
    
    def _default_quality_analysis(self) -> Dict[str, Any]:
        """Fallback quality analysis."""
        return {
            "overall_quality": 0.7,
            "credibility": 0.7,
            "consistency": 0.7,
            "completeness": 0.7,
            "strengths": ["Multiple sources available"],
            "weaknesses": ["Automated analysis unavailable"],
            "contradictions": []
        }
    
    def _empty_verification_report(self) -> Dict[str, Any]:
        """Report for empty content."""
        return {
            "total_sources": 0,
            "verified_sources": 0,
            "quality_score": 0.0,
            "credibility_score": 0.0,
            "coverage_score": 0.0,
            "needs_additional_search": True,
            "warnings": ["No sources to verify"],
            "verified_content": [],
            "quality_analysis": {}
        }


if __name__ == "__main__":
    import asyncio
    
    async def test_verification():
        """Test Verification Agent."""
        print("🧪 Testing Verification Agent\n")
        
        agent = VerificationAgent()
        
        # Simulate parsed content
        parsed_content = [
            {
                "source_url": "https://example.com/source1",
                "source_title": "Google Drive API Guide",
                "key_points": ["OAuth2 authentication", "File access methods", "Python client library"],
                "metadata": {"relevance": 0.9}
            },
            {
                "source_url": "https://example.com/source2",
                "source_title": "MCP Server Tutorial",
                "key_points": ["Server setup", "Tool registration", "Client integration"],
                "metadata": {"relevance": 0.85}
            },
            {
                "source_url": "https://example.com/source3",
                "source_title": "API Integration Best Practices",
                "key_points": ["Error handling", "Rate limiting", "Security"],
                "metadata": {"relevance": 0.8}
            }
        ]
        
        report = await agent.verify(
            parsed_content,
            query="How to integrate Google Drive API with Python MCP server?",
            quality_threshold=0.7
        )
        
        print(f"✅ Verification Complete:")
        print(f"   Total sources: {report['total_sources']}")
        print(f"   Verified: {report['verified_sources']}")
        print(f"   Quality: {report['quality_score']}")
        print(f"   Credibility: {report['credibility_score']}")
        print(f"   Coverage: {report['coverage_score']}")
        print(f"   Needs more research: {report['needs_additional_search']}")
        if report['warnings']:
            print(f"   Warnings: {report['warnings']}")
    
    asyncio.run(test_verification())

