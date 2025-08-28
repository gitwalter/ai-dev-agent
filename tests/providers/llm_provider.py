#!/usr/bin/env python3
"""
LLM Provider Abstraction for Configurable Testing

Provides unified interface for both mock and real LLM providers:
- MockLLMProvider: Fast, deterministic responses for development
- RealLLMProvider: Actual LLM API calls for integration testing

Features:
- Unified async interface
- Response validation
- Performance tracking
- Error handling and retries
"""

import asyncio
import json
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from enum import Enum

try:
    import streamlit as st
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.config.test_config import get_test_config, TestMode
from utils.structured_outputs import (
    RequirementsAnalysisOutput,
    ArchitectureDesignOutput,
    CodeGenerationOutput,
    TestGenerationOutput,
    CodeReviewOutput,
    SecurityAnalysisOutput,
    DocumentationGenerationOutput
)


@dataclass
class LLMResponse:
    """Standardized LLM response container."""
    content: str
    model: str
    provider: str
    execution_time: float
    token_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._performance_metrics = []
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from prompt."""
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information."""
        pass
    
    def get_performance_metrics(self) -> List[Dict[str, Any]]:
        """Get performance metrics."""
        return self._performance_metrics.copy()
    
    def clear_performance_metrics(self) -> None:
        """Clear performance metrics."""
        self._performance_metrics.clear()


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for fast testing."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._mock_responses = self._load_mock_responses()
        self.response_delay = config.get("response_delay", 0.1) if config else 0.1
    
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate mock response based on prompt content."""
        start_time = time.time()
        
        # Simulate processing delay
        await asyncio.sleep(self.response_delay)
        
        # Determine response type based on prompt
        response_content = self._get_mock_response(prompt)
        
        execution_time = time.time() - start_time
        
        # Track performance
        self._performance_metrics.append({
            "timestamp": time.time(),
            "execution_time": execution_time,
            "prompt_length": len(prompt),
            "response_length": len(response_content),
            "provider": "mock"
        })
        
        return LLMResponse(
            content=response_content,
            model="mock-model",
            provider="mock",
            execution_time=execution_time,
            token_count=len(response_content.split()),
            metadata={"mock": True, "response_type": self._classify_prompt(prompt)}
        )
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get mock provider information."""
        return {
            "provider": "mock",
            "model": "mock-model",
            "response_delay": self.response_delay,
            "total_responses": len(self._performance_metrics),
            "avg_response_time": self._get_avg_response_time()
        }
    
    def _get_avg_response_time(self) -> float:
        """Calculate average response time."""
        if not self._performance_metrics:
            return 0.0
        return sum(m["execution_time"] for m in self._performance_metrics) / len(self._performance_metrics)
    
    def _classify_prompt(self, prompt: str) -> str:
        """Classify prompt type to return appropriate mock response."""
        prompt_lower = prompt.lower()
        
        if "requirements" in prompt_lower and "analysis" in prompt_lower:
            return "requirements_analysis"
        elif "architecture" in prompt_lower and ("design" in prompt_lower or "overview" in prompt_lower):
            return "architecture_design"
        elif "code" in prompt_lower and ("generate" in prompt_lower or "implementation" in prompt_lower):
            return "code_generation"
        elif "test" in prompt_lower and ("generate" in prompt_lower or "write" in prompt_lower):
            return "test_generation"
        elif "review" in prompt_lower and "code" in prompt_lower:
            return "code_review"
        elif "security" in prompt_lower and ("analysis" in prompt_lower or "assess" in prompt_lower):
            return "security_analysis"
        elif "documentation" in prompt_lower or "readme" in prompt_lower:
            return "documentation_generation"
        else:
            return "generic"
    
    def _get_mock_response(self, prompt: str) -> str:
        """Get appropriate mock response for prompt."""
        response_type = self._classify_prompt(prompt)
        return self._mock_responses.get(response_type, self._mock_responses["generic"])
    
    def _load_mock_responses(self) -> Dict[str, str]:
        """Load predefined mock responses."""
        return {
            "requirements_analysis": json.dumps({
                "functional_requirements": [
                    {
                        "id": "REQ-001",
                        "title": "Basic Calculator Interface",
                        "description": "Create a user interface for basic arithmetic operations",
                        "priority": "high",
                        "type": "functional"
                    },
                    {
                        "id": "REQ-002", 
                        "title": "Arithmetic Operations",
                        "description": "Support addition, subtraction, multiplication, and division",
                        "priority": "high",
                        "type": "functional"
                    },
                    {
                        "id": "REQ-003",
                        "title": "Result Display",
                        "description": "Display calculation results clearly to the user",
                        "priority": "medium",
                        "type": "functional"
                    }
                ],
                "summary": {
                    "description": "Simple calculator web application with basic arithmetic operations"
                },
                "assumptions": [
                    "Users have basic computer literacy",
                    "Modern web browser support is available"
                ],
                "technical_constraints": [
                    "Must work in web browsers",
                    "Should be responsive for mobile devices"
                ]
            }),
            
            "architecture_design": json.dumps({
                "architecture_overview": "MVC architecture with React frontend and Node.js backend, using REST API for communication",
                "data_flow": "User input -> UI components -> API calls -> Server processing -> Database storage -> Response to UI",
                "deployment_strategy": "Docker containerization with separate frontend and backend containers",
                "tech_stack": {
                    "frontend": ["React.js", "CSS3", "HTML5"],
                    "backend": ["Node.js", "Express.js", "SQLite"]
                },
                "components": [
                    {
                        "name": "Calculator UI",
                        "type": "frontend",
                        "description": "React-based user interface for calculator operations"
                    },
                    {
                        "name": "Calculation API",
                        "type": "backend", 
                        "description": "REST API for processing arithmetic operations"
                    }
                ]
            }),
            
            "code_generation": json.dumps({
                "files": [
                    {
                        "filename": "calculator.py",
                        "content": "# Mock calculator implementation\nclass Calculator:\n    def add(self, a, b):\n        return a + b\n    \n    def subtract(self, a, b):\n        return a - b"
                    }
                ],
                "implementation_notes": "Mock implementation for testing purposes",
                "dependencies": ["python>=3.8"]
            }),
            
            "test_generation": json.dumps({
                "test_files": [
                    {
                        "filename": "test_calculator.py",
                        "content": "# Mock test implementation\nimport unittest\n\nclass TestCalculator(unittest.TestCase):\n    def test_addition(self):\n        self.assertEqual(2 + 2, 4)"
                    }
                ],
                "test_framework": "unittest",
                "coverage_target": "90%"
            }),
            
            "code_review": json.dumps({
                "summary": "Code review completed with minor suggestions",
                "critical_issues": 0,
                "minor_issues": 2,
                "suggestions": 3,
                "overall_quality": "good"
            }),
            
            "security_analysis": json.dumps({
                "security_score": 85,
                "vulnerabilities": [],
                "recommendations": ["Add input validation", "Implement rate limiting"],
                "compliance_status": "compliant"
            }),
            
            "documentation_generation": json.dumps({
                "sections": [
                    {"title": "Installation", "content": "Mock installation instructions"},
                    {"title": "Usage", "content": "Mock usage instructions"}
                ],
                "format": "markdown"
            }),
            
            "generic": json.dumps({
                "status": "completed",
                "message": "Mock response generated successfully",
                "data": {}
            })
        }


class RealLLMProvider(LLMProvider):
    """Real LLM provider using actual API calls."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain not available for real LLM provider")
        
        self.api_key = config.get("api_key") if config else None
        if not self.api_key:
            test_config = get_test_config()
            self.api_key = test_config.api_key
        
        if not self.api_key:
            raise ValueError("API key required for real LLM provider")
        
        self.model_name = config.get("model_name", "gemini-2.5-flash-lite") if config else "gemini-2.5-flash-lite"
        self.temperature = config.get("temperature", 0.1) if config else 0.1
        self.max_tokens = config.get("max_tokens", 2048) if config else 2048
        
        self._llm = self._create_llm()
    
    def _create_llm(self) -> ChatGoogleGenerativeAI:
        """Create LangChain LLM instance."""
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
    
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate real response from LLM API."""
        start_time = time.time()
        
        try:
            # Make API call
            response = await self._llm.ainvoke(prompt)
            
            execution_time = time.time() - start_time
            
            # Extract content
            if isinstance(response, AIMessage):
                content = response.content
            else:
                content = str(response)
            
            # Track performance
            self._performance_metrics.append({
                "timestamp": time.time(),
                "execution_time": execution_time,
                "prompt_length": len(prompt),
                "response_length": len(content),
                "provider": "real",
                "model": self.model_name
            })
            
            return LLMResponse(
                content=content,
                model=self.model_name,
                provider="real",
                execution_time=execution_time,
                token_count=self._estimate_tokens(content),
                metadata={"real": True, "model": self.model_name}
            )
            
        except Exception as e:
            self.logger.error(f"Real LLM API call failed: {e}")
            raise
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get real provider information."""
        return {
            "provider": "real",
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "total_responses": len(self._performance_metrics),
            "avg_response_time": self._get_avg_response_time()
        }
    
    def _get_avg_response_time(self) -> float:
        """Calculate average response time."""
        if not self._performance_metrics:
            return 0.0
        return sum(m["execution_time"] for m in self._performance_metrics) / len(self._performance_metrics)
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        return len(text.split())


class LLMProviderFactory:
    """Factory for creating LLM providers based on configuration."""
    
    @staticmethod
    def create_provider(config: Optional[Dict[str, Any]] = None) -> LLMProvider:
        """Create appropriate LLM provider based on test configuration."""
        test_config = get_test_config()
        
        if test_config.mode == TestMode.MOCK:
            return MockLLMProvider(config)
        elif test_config.mode == TestMode.REAL:
            provider_config = config or {}
            provider_config["api_key"] = test_config.api_key
            return RealLLMProvider(provider_config)
        else:
            raise ValueError(f"Unknown test mode: {test_config.mode}")
    
    @staticmethod
    def create_mock_provider(config: Optional[Dict[str, Any]] = None) -> MockLLMProvider:
        """Create mock provider explicitly."""
        return MockLLMProvider(config)
    
    @staticmethod
    def create_real_provider(api_key: str, config: Optional[Dict[str, Any]] = None) -> RealLLMProvider:
        """Create real provider explicitly."""
        provider_config = config or {}
        provider_config["api_key"] = api_key
        return RealLLMProvider(provider_config)


# Convenience functions
def get_llm_provider(config: Optional[Dict[str, Any]] = None) -> LLMProvider:
    """Get LLM provider based on current test configuration."""
    return LLMProviderFactory.create_provider(config)


async def generate_llm_response(prompt: str, config: Optional[Dict[str, Any]] = None) -> LLMResponse:
    """Generate LLM response using current configuration."""
    provider = get_llm_provider(config)
    return await provider.generate_response(prompt)


if __name__ == "__main__":
    # Demo/test the provider system
    async def demo():
        print("🤖 LLM Provider System Demo")
        print("=" * 40)
        
        # Test mock provider
        print("\n📋 Testing Mock Provider...")
        mock_provider = LLMProviderFactory.create_mock_provider()
        
        mock_response = await mock_provider.generate_response(
            "Generate requirements analysis for a calculator application"
        )
        
        print(f"Mock response length: {len(mock_response.content)}")
        print(f"Mock execution time: {mock_response.execution_time:.3f}s")
        print(f"Mock provider info: {mock_provider.get_provider_info()}")
        
        # Test based on configuration
        print(f"\n🔧 Current test mode: {get_test_config().mode.value}")
        current_provider = get_llm_provider()
        print(f"Provider type: {type(current_provider).__name__}")
        
        print("\n✅ Provider system demo complete")
    
    asyncio.run(demo())
