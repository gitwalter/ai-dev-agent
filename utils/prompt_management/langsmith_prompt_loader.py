"""
LangSmith Prompt Loader
=======================

Hybrid prompt management system that integrates LangSmith Prompt Hub
with local fallback for offline development and resilience.

Features:
- Automatic sync with LangSmith Hub (hub = source of truth)
- Smart caching with conflict detection
- Local fallback for offline development

Author: AI-Dev-Agent System
Version: 2.0 - Enhanced with Smart Sync
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# LangSmith availability check
try:
    from langchain import hub
    LANGSMITH_HUB_AVAILABLE = True
except ImportError:
    LANGSMITH_HUB_AVAILABLE = False
    logger.debug("LangSmith hub not available, will use local fallback")

# Import sync manager
try:
    from utils.prompt_management.prompt_sync_manager import PromptSyncManager
    SYNC_MANAGER_AVAILABLE = True
except ImportError:
    SYNC_MANAGER_AVAILABLE = False
    logger.debug("Sync manager not available")


class LangSmithPromptLoader:
    """
    Hybrid prompt loader with LangSmith integration and local fallback.
    
    Loading Strategy (in order):
    1. LangSmith Prompt Hub (cached)
    2. LangSmith Prompt Hub (fresh)
    3. Local database
    4. Hardcoded fallback
    """
    
    def __init__(self, organization: str = "ai-dev-agent", auto_sync: bool = True):
        """
        Initialize the LangSmith prompt loader.
        
        Args:
            organization: LangSmith organization/namespace
            auto_sync: Enable automatic sync with hub (recommended)
        """
        self.organization = organization
        self.cache = {}  # In-memory cache for loaded prompts
        self.auto_sync = auto_sync
        self._load_api_key()
        
        # Initialize sync manager if available
        if SYNC_MANAGER_AVAILABLE and auto_sync:
            self.sync_manager = PromptSyncManager()
        else:
            self.sync_manager = None
    
    def _load_api_key(self) -> Optional[str]:
        """Load LangSmith API key from environment or secrets.toml"""
        # Try environment variables first
        api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")
        
        # Try secrets.toml
        if not api_key:
            try:
                secrets_path = Path(".streamlit/secrets.toml")
                if secrets_path.exists():
                    with open(secrets_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                if key in ["LANGSMITH_API_KEY", "LANGCHAIN_API_KEY"]:
                                    api_key = value.strip().strip('"').strip("'")
                                    break
            except Exception as e:
                logger.debug(f"Could not load API key from secrets.toml: {e}")
        
        if api_key:
            # Set environment variable for langchain hub
            os.environ["LANGCHAIN_API_KEY"] = api_key
            logger.debug("[OK] LangSmith API key loaded")
        else:
            logger.warning("[WARNING] LangSmith API key not found, will use local fallback only")
        
        return api_key
    
    def load_from_langsmith(self, agent_name: str, version: str = "latest", 
                           use_cache: bool = True) -> Optional[str]:
        """
        Load prompt from LangSmith Prompt Hub with automatic sync.
        
        Enhanced with smart sync:
        - Auto-syncs with hub (hub = source of truth)
        - Detects local modifications and handles conflicts
        - Falls back to local cache if hub unavailable
        
        Based on: https://docs.langchain.com/langsmith/manage-prompts-programmatically
        
        Args:
            agent_name: Name of the agent
            version: Version tag (e.g., "latest", "prod") or commit hash
            use_cache: Whether to use cached version
            
        Returns:
            Prompt text or None if not available
        """
        # Step 1: Try smart sync if available
        if self.sync_manager and self.auto_sync:
            try:
                logger.debug(f"[SYNC] Auto-syncing {agent_name}...")
                sync_result = self.sync_manager.sync_prompt(agent_name, auto_push=False, dry_run=False)
                
                if sync_result['success']:
                    # Load from local cache after sync
                    local_path = self.sync_manager.get_local_path(agent_name)
                    if local_path.exists():
                        prompt_text = local_path.read_text(encoding='utf-8')
                        
                        # Cache in memory
                        cache_key = f"{agent_name}:{version}"
                        self.cache[cache_key] = prompt_text
                        
                        logger.debug(f"[SYNC] Loaded {agent_name} after sync ({len(prompt_text)} chars)")
                        return prompt_text
                
            except Exception as e:
                logger.debug(f"[SYNC] Sync failed for {agent_name}, falling back: {e}")
        
        # Step 2: Fall back to direct hub pull (original behavior)
        if not LANGSMITH_HUB_AVAILABLE:
            logger.debug(f"[INFO] LangSmith hub not available for {agent_name}")
            return None
        
        # Check in-memory cache first
        cache_key = f"{agent_name}:{version}"
        if use_cache and cache_key in self.cache:
            logger.debug(f"[CACHE] Using in-memory cached prompt for {agent_name}")
            return self.cache[cache_key]
        
        try:
            # Construct prompt identifier
            prompt_name = f"{agent_name}_v1"
            if version and version != "latest":
                prompt_id = f"{prompt_name}:{version}"
            else:
                prompt_id = prompt_name
            
            logger.debug(f"[INFO] Loading prompt from LangSmith: {prompt_id}")
            
            # Load from LangSmith Hub using hub.pull()
            prompt = hub.pull(prompt_id)
            
            # Extract template text from the PromptTemplate object
            if hasattr(prompt, 'template'):
                prompt_text = prompt.template
            elif hasattr(prompt, 'messages') and len(prompt.messages) > 0:
                # For ChatPromptTemplate, get the first message content
                prompt_text = prompt.messages[0].content if hasattr(prompt.messages[0], 'content') else str(prompt.messages[0])
            else:
                prompt_text = str(prompt)
            
            # Cache the result in memory
            self.cache[cache_key] = prompt_text
            logger.info(f"[OK] Loaded prompt for {agent_name} from LangSmith ({len(prompt_text)} chars)")
            
            return prompt_text
            
        except Exception as e:
            logger.debug(f"[INFO] Could not load {agent_name} from LangSmith: {e}")
            return None
    
    def clear_cache(self, agent_name: Optional[str] = None):
        """
        Clear the prompt cache.
        
        Args:
            agent_name: Specific agent to clear, or None to clear all
        """
        if agent_name:
            # Clear specific agent
            keys_to_remove = [k for k in self.cache.keys() if k.startswith(f"{agent_name}:")]
            for key in keys_to_remove:
                del self.cache[key]
            logger.info(f"[OK] Cleared cache for {agent_name}")
        else:
            # Clear all
            self.cache.clear()
            logger.info("[OK] Cleared all prompt cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_prompts": len(self.cache),
            "agents": list(set(k.split(':')[0] for k in self.cache.keys()))
        }


# Global loader instance
_langsmith_loader: Optional[LangSmithPromptLoader] = None


def get_langsmith_loader(organization: str = "ai-dev-agent") -> LangSmithPromptLoader:
    """Get or create the global LangSmith loader instance."""
    global _langsmith_loader
    if _langsmith_loader is None:
        _langsmith_loader = LangSmithPromptLoader(organization)
    return _langsmith_loader


def load_prompt_from_langsmith(agent_name: str, version: str = "latest") -> Optional[str]:
    """
    Convenience function to load a prompt from LangSmith.
    
    Args:
        agent_name: Name of the agent
        version: Version tag
        
    Returns:
        Prompt text or None
    """
    loader = get_langsmith_loader()
    return loader.load_from_langsmith(agent_name, version)

