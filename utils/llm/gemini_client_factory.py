"""
Gemini Client Factory for Agent LLM Initialization.

Provides centralized LLM client creation for agents that need to work both:
1. Standalone (with their own LLM instance)
2. In coordinated swarms (with shared/injected LLM)
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# LangChain integration
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain Google GenAI not available")

# Direct Gemini SDK
try:
    import google.generativeai as genai
    GENAI_SDK_AVAILABLE = True
except ImportError:
    GENAI_SDK_AVAILABLE = False
    logger.warning("Google GenerativeAI SDK not available")


class GeminiClientFactory:
    """Factory for creating Gemini LLM clients with proper configuration."""
    
    # Default model configuration
    DEFAULT_MODEL = "gemini-2.5-flash"
    DEFAULT_TEMPERATURE = 0.1
    DEFAULT_MAX_TOKENS = 8192
    
    _api_key = None
    _genai_configured = False
    
    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Get Gemini API key from environment or config files."""
        if cls._api_key:
            return cls._api_key
        
        # Try environment variables
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if api_key:
            cls._api_key = api_key
            return api_key
        
        # Try .env file
        try:
            env_path = Path(".env")
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GOOGLE_API_KEY") or line.startswith("GEMINI_API_KEY"):
                            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if api_key:
                                cls._api_key = api_key
                                return api_key
        except Exception as e:
            logger.debug(f"Failed to read .env file: {e}")
        
        # Try secrets.toml
        try:
            secrets_path = Path(".streamlit/secrets.toml")
            if secrets_path.exists():
                with open(secrets_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY") or line.startswith("GOOGLE_API_KEY"):
                            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if api_key and api_key != "your-gemini-api-key-here":
                                cls._api_key = api_key
                                return api_key
        except Exception as e:
            logger.debug(f"Failed to read secrets.toml: {e}")
        
        logger.warning("No Gemini API key found in environment or config files")
        return None
    
    @classmethod
    def create_langchain_client(
        cls,
        model_name: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        **kwargs
    ) -> Optional[Any]:
        """
        Create LangChain ChatGoogleGenerativeAI client.
        
        Preferred method for agents that use LangChain, as it provides:
        - Automatic LangSmith tracing
        - Better error handling
        - Structured output support
        """
        if not LANGCHAIN_AVAILABLE:
            logger.error("LangChain Google GenAI not available")
            return None
        
        api_key = cls.get_api_key()
        if not api_key:
            logger.error("Cannot create LangChain client: No API key")
            return None
        
        try:
            client = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                google_api_key=api_key,
                **kwargs
            )
            logger.info(f"✅ Created LangChain Gemini client: {model_name}")
            return client
        except Exception as e:
            logger.error(f"Failed to create LangChain client: {e}")
            return None
    
    @classmethod
    def create_genai_client(
        cls,
        model_name: str = DEFAULT_MODEL,
        **kwargs
    ) -> Optional[Any]:
        """
        Create direct Google GenerativeAI SDK client.
        
        Use for agents that need direct SDK access or don't use LangChain.
        """
        if not GENAI_SDK_AVAILABLE:
            logger.error("Google GenerativeAI SDK not available")
            return None
        
        api_key = cls.get_api_key()
        if not api_key:
            logger.error("Cannot create GenAI client: No API key")
            return None
        
        try:
            # Configure SDK if not already done
            if not cls._genai_configured:
                genai.configure(api_key=api_key)
                cls._genai_configured = True
            
            # Create model
            client = genai.GenerativeModel(model_name, **kwargs)
            logger.info(f"✅ Created GenAI SDK client: {model_name}")
            return client
        except Exception as e:
            logger.error(f"Failed to create GenAI SDK client: {e}")
            return None
    
    @classmethod
    def create_client_for_agent(
        cls,
        agent_name: str,
        prefer_langchain: bool = True,
        model_name: str = DEFAULT_MODEL,
        **kwargs
    ) -> Optional[Any]:
        """
        Create appropriate LLM client for an agent.
        
        Args:
            agent_name: Name of the agent (for logging)
            prefer_langchain: Whether to prefer LangChain client over direct SDK
            model_name: Gemini model to use
            **kwargs: Additional model configuration
            
        Returns:
            LLM client or None if creation failed
        """
        logger.info(f"🤖 Creating LLM client for agent: {agent_name}")
        
        if prefer_langchain and LANGCHAIN_AVAILABLE:
            client = cls.create_langchain_client(model_name=model_name, **kwargs)
            if client:
                return client
            logger.warning(f"LangChain client creation failed, falling back to GenAI SDK")
        
        if GENAI_SDK_AVAILABLE:
            return cls.create_genai_client(model_name=model_name, **kwargs)
        
        logger.error(f"❌ Cannot create LLM client for {agent_name}: No available LLM libraries")
        return None


def get_gemini_client(
    agent_name: str = "agent",
    model_name: str = "gemini-2.5-flash",
    **kwargs
) -> Optional[Any]:
    """
    Convenience function to get a Gemini client for an agent.
    
    Args:
        agent_name: Name of the agent
        model_name: Gemini model to use (default: gemini-2.5-flash)
        **kwargs: Additional model configuration
        
    Returns:
        LLM client or None
    """
    return GeminiClientFactory.create_client_for_agent(
        agent_name=agent_name,
        model_name=model_name,
        **kwargs
    )

