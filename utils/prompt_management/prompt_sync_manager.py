"""
Smart Prompt Sync Manager
==========================

Intelligent prompt synchronization system that respects LangSmith Hub as source of truth.

Principles:
1. Hub = Source of Truth (always prefer hub version)
2. Only upload local edits if explicitly modified locally AND different from hub
3. Track all changes with metadata
4. Safe comparison using content hashes
5. Automatic sync with conflict detection

Author: AI-Dev-Agent System
Version: 1.0
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# Try to import LangSmith
try:
    from langsmith import Client
    from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    logger.debug("LangSmith not available")


@dataclass
class PromptMetadata:
    """Metadata for tracking prompt sync status."""
    prompt_name: str
    last_fetched_from_hub: Optional[str] = None  # ISO timestamp
    locally_modified: bool = False
    local_edit_timestamp: Optional[str] = None  # ISO timestamp
    hub_content_hash: Optional[str] = None  # SHA256 of hub version
    local_content_hash: Optional[str] = None  # SHA256 of local version
    last_sync_timestamp: Optional[str] = None
    sync_direction: Optional[str] = None  # "pull" or "push"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptMetadata':
        """Create from dictionary."""
        return cls(**data)


class PromptSyncManager:
    """
    Smart prompt synchronization manager.
    
    Respects LangSmith Hub as source of truth while allowing local edits.
    """
    
    def __init__(self, cache_dir: str = "prompts/langsmith_cache"):
        """
        Initialize the sync manager.
        
        Args:
            cache_dir: Directory for local prompt cache
        """
        self.cache_dir = Path(cache_dir)
        self.metadata_dir = self.cache_dir / "metadata"
        
        # Create directories if needed
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        self._load_api_key()
    
    def _load_api_key(self) -> Optional[str]:
        """Load LangSmith API key."""
        api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")
        
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
                logger.debug(f"Could not load API key from secrets: {e}")
        
        if api_key:
            os.environ["LANGCHAIN_API_KEY"] = api_key
        
        return api_key
    
    @staticmethod
    def compute_hash(content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get_local_path(self, prompt_name: str) -> Path:
        """Get path to local cache file."""
        return self.cache_dir / f"{prompt_name}.txt"
    
    def get_metadata_path(self, prompt_name: str) -> Path:
        """Get path to metadata file."""
        # Normalize filename for metadata
        safe_name = prompt_name.replace('_v1', '-v1')
        return self.metadata_dir / f"{safe_name}.json"
    
    def load_metadata(self, prompt_name: str) -> PromptMetadata:
        """Load metadata for a prompt."""
        metadata_path = self.get_metadata_path(prompt_name)
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return PromptMetadata.from_dict(data)
            except Exception as e:
                logger.warning(f"Could not load metadata for {prompt_name}: {e}")
        
        # Return new metadata
        return PromptMetadata(prompt_name=prompt_name)
    
    def save_metadata(self, metadata: PromptMetadata):
        """Save metadata for a prompt."""
        metadata_path = self.get_metadata_path(metadata.prompt_name)
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Could not save metadata for {metadata.prompt_name}: {e}")
    
    def fetch_from_hub(self, prompt_name: str) -> Optional[str]:
        """
        Fetch prompt from LangSmith Hub.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            Prompt content or None if not available
        """
        if not LANGSMITH_AVAILABLE:
            logger.debug("LangSmith not available")
            return None
        
        try:
            api_key = self._load_api_key()
            if not api_key:
                logger.debug("No API key available")
                return None
            
            # Create client
            client = Client(api_key=api_key)
            
            prompt_id = f"{prompt_name}_v1" if not prompt_name.endswith('_v1') else prompt_name
            logger.debug(f"Fetching {prompt_id} from LangSmith Hub...")
            
            # Pull from hub using client
            prompt = client.pull_prompt(prompt_id)
            
            # Extract text
            if hasattr(prompt, 'template'):
                prompt_text = prompt.template
            elif hasattr(prompt, 'messages') and len(prompt.messages) > 0:
                prompt_text = prompt.messages[0].content if hasattr(prompt.messages[0], 'content') else str(prompt.messages[0])
            else:
                prompt_text = str(prompt)
            
            logger.debug(f"✅ Fetched {prompt_id} from hub ({len(prompt_text)} chars)")
            return prompt_text
            
        except Exception as e:
            logger.debug(f"Could not fetch {prompt_name} from hub: {e}")
            return None
    
    def push_to_hub(self, prompt_name: str, content: str, dry_run: bool = False, tags: Optional[List[str]] = None) -> bool:
        """
        Push prompt to LangSmith Hub.
        
        Args:
            prompt_name: Name of the prompt
            content: Prompt content
            dry_run: If True, don't actually push
            tags: Optional list of tags for the prompt
            
        Returns:
            True if successful
        """
        if not LANGSMITH_AVAILABLE:
            logger.error("LangSmith not available - cannot push")
            return False
        
        if dry_run:
            logger.info(f"[DRY RUN] Would push {prompt_name} to hub")
            return True
        
        try:
            api_key = self._load_api_key()
            if not api_key:
                logger.error("No API key available")
                return False
            
            # Create client
            client = Client(api_key=api_key)
            
            # Create prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", content)
            ])
            
            # Infer tags from prompt name if not provided
            if tags is None:
                tags = self._infer_tags_from_name(prompt_name)
            
            # Push to hub with tags
            prompt_id = f"{prompt_name}_v1" if not prompt_name.endswith('_v1') else prompt_name
            url = client.push_prompt(prompt_id, object=prompt_template, tags=tags)
            
            logger.info(f"✅ Pushed {prompt_id} to LangSmith Hub: {url} (tags: {tags})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push {prompt_name}: {e}")
            return False
    
    def _infer_tags_from_name(self, prompt_name: str) -> List[str]:
        """Infer appropriate tags from prompt name."""
        tags = []
        
        # Add version tag
        if '_v1' in prompt_name or prompt_name.endswith('_v1'):
            tags.append('v1')
        
        # Add category tags based on name
        name_lower = prompt_name.lower()
        
        if 'rag' in name_lower:
            tags.append('rag')
        if 'simple_rag' in name_lower:
            tags.append('simple-rag')
        if 'agentic_rag' in name_lower:
            tags.append('agentic-rag')
        if 'system' in name_lower:
            tags.append('system-prompt')
        if 'query' in name_lower:
            tags.append('query-processing')
        if 'document' in name_lower:
            tags.append('document-processing')
        if 'writer' in name_lower:
            tags.append('content-generation')
        if 'architect' in name_lower:
            tags.append('architecture')
        if 'code_generator' in name_lower or 'generator' in name_lower:
            tags.append('code-generation')
        if 'test' in name_lower:
            tags.append('testing')
        if 'security' in name_lower:
            tags.append('security')
        if 'analyst' in name_lower:
            tags.append('analysis')
        if 'selector' in name_lower:
            tags.append('selection')
            tags.append('coordination')
        if 'agent' in name_lower and 'agentic' not in name_lower:
            tags.append('agent')
        if 'router' in name_lower:
            tags.append('routing')
            tags.append('coordination')
        if 'complexity' in name_lower:
            tags.append('analysis')
            tags.append('complexity')
        
        return tags if tags else ['prompt', 'v1']
    
    def sync_prompt(self, prompt_name: str, auto_push: bool = False, 
                    dry_run: bool = False) -> Dict[str, Any]:
        """
        Smart sync a single prompt.
        
        Sync Logic:
        1. Fetch from hub (hub = source of truth)
        2. Load local version and metadata
        3. Compare:
           - If local modified AND differs from hub → offer to push (if auto_push)
           - If hub version differs from cached → update local cache
           - If no changes → no action
        
        Args:
            prompt_name: Name of the prompt
            auto_push: If True, automatically push local changes
            dry_run: If True, don't make actual changes
            
        Returns:
            Dict with sync results
        """
        result = {
            "prompt_name": prompt_name,
            "action": "none",
            "success": True,
            "message": "",
            "hub_available": False,
            "local_modified": False,
            "conflict": False
        }
        
        # Load metadata
        metadata = self.load_metadata(prompt_name)
        
        # Try to fetch from hub
        hub_content = self.fetch_from_hub(prompt_name)
        result["hub_available"] = hub_content is not None
        
        # Load local version
        local_path = self.get_local_path(prompt_name)
        local_content = None
        if local_path.exists():
            local_content = local_path.read_text(encoding='utf-8')
        
        # Compute hashes
        hub_hash = self.compute_hash(hub_content) if hub_content else None
        local_hash = self.compute_hash(local_content) if local_content else None
        
        # CASE 1: No hub version available
        if not hub_content:
            # If we have local content and auto_push enabled, push to hub
            if local_content and auto_push:
                if self.push_to_hub(prompt_name, local_content, dry_run):
                    if not dry_run:
                        metadata.hub_content_hash = local_hash
                        metadata.local_content_hash = local_hash
                        metadata.locally_modified = False
                        metadata.last_sync_timestamp = datetime.now().isoformat()
                        metadata.sync_direction = "push"
                        self.save_metadata(metadata)
                    
                    result["action"] = "created_on_hub"
                    result["message"] = f"Created new prompt on hub ({len(local_content)} chars)"
                    return result
                else:
                    result["success"] = False
                    result["message"] = "Failed to create prompt on hub"
                    return result
            
            # No auto_push or no local content
            if local_content and metadata.locally_modified:
                result["message"] = "Hub unavailable, local modified version preserved (use --auto-push to create on hub)"
            else:
                result["message"] = "Hub unavailable, no local version"
            return result
        
        # CASE 2: Hub available, no local version
        if not local_content:
            if not dry_run:
                local_path.write_text(hub_content, encoding='utf-8')
                metadata.hub_content_hash = hub_hash
                metadata.local_content_hash = hub_hash
                metadata.last_fetched_from_hub = datetime.now().isoformat()
                metadata.last_sync_timestamp = datetime.now().isoformat()
                metadata.sync_direction = "pull"
                self.save_metadata(metadata)
            
            result["action"] = "pulled_from_hub"
            result["message"] = f"Pulled fresh version from hub ({len(hub_content)} chars)"
            return result
        
        # CASE 3: Both versions exist - compare
        result["local_modified"] = metadata.locally_modified
        
        # Check if content differs
        content_differs = hub_hash != local_hash
        
        if not content_differs:
            # No changes - just update metadata
            if not dry_run:
                metadata.hub_content_hash = hub_hash
                metadata.local_content_hash = local_hash
                metadata.last_sync_timestamp = datetime.now().isoformat()
                self.save_metadata(metadata)
            
            result["message"] = "Hub and local are identical - no sync needed"
            return result
        
        # Content differs - determine action
        if metadata.locally_modified:
            # Local was modified - check if we should push
            if auto_push:
                if self.push_to_hub(prompt_name, local_content, dry_run):
                    if not dry_run:
                        metadata.hub_content_hash = local_hash
                        metadata.last_sync_timestamp = datetime.now().isoformat()
                        metadata.sync_direction = "push"
                        metadata.locally_modified = False  # Reset after successful push
                        self.save_metadata(metadata)
                    
                    result["action"] = "pushed_to_hub"
                    result["message"] = f"Pushed local changes to hub ({len(local_content)} chars)"
                else:
                    result["success"] = False
                    result["message"] = "Failed to push local changes to hub"
            else:
                result["conflict"] = True
                result["message"] = "Local modified and differs from hub - manual resolution needed"
        else:
            # Local not modified - hub is newer, update local
            if not dry_run:
                # Backup old version
                backup_path = self.cache_dir / f"{prompt_name}.backup.txt"
                if local_path.exists():
                    backup_path.write_text(local_content, encoding='utf-8')
                
                # Update local with hub version
                local_path.write_text(hub_content, encoding='utf-8')
                metadata.hub_content_hash = hub_hash
                metadata.local_content_hash = hub_hash
                metadata.last_fetched_from_hub = datetime.now().isoformat()
                metadata.last_sync_timestamp = datetime.now().isoformat()
                metadata.sync_direction = "pull"
                self.save_metadata(metadata)
            
            result["action"] = "updated_from_hub"
            result["message"] = f"Updated local with newer hub version ({len(hub_content)} chars)"
        
        return result
    
    def sync_all_prompts(self, auto_push: bool = False, 
                        dry_run: bool = False) -> Dict[str, Any]:
        """
        Sync all cached prompts.
        
        Args:
            auto_push: If True, automatically push local changes
            dry_run: If True, don't make actual changes
            
        Returns:
            Summary of sync results
        """
        results = {
            "total": 0,
            "pulled": 0,
            "pushed": 0,
            "updated": 0,
            "conflicts": 0,
            "errors": 0,
            "details": []
        }
        
        # Find all cached prompts
        prompt_files = list(self.cache_dir.glob("*.txt"))
        results["total"] = len(prompt_files)
        
        logger.info(f"Syncing {len(prompt_files)} prompts...")
        
        for prompt_file in prompt_files:
            if prompt_file.stem == "backup":
                continue
            
            prompt_name = prompt_file.stem
            logger.info(f"Syncing {prompt_name}...")
            
            try:
                result = self.sync_prompt(prompt_name, auto_push=auto_push, dry_run=dry_run)
                results["details"].append(result)
                
                # Update counters
                if result["action"] == "pulled_from_hub":
                    results["pulled"] += 1
                elif result["action"] == "pushed_to_hub":
                    results["pushed"] += 1
                elif result["action"] == "updated_from_hub":
                    results["updated"] += 1
                
                if result["conflict"]:
                    results["conflicts"] += 1
                
                if not result["success"]:
                    results["errors"] += 1
                    
            except Exception as e:
                logger.error(f"Error syncing {prompt_name}: {e}")
                results["errors"] += 1
        
        return results
    
    def mark_as_locally_edited(self, prompt_name: str):
        """
        Mark a prompt as locally edited.
        
        Call this after manually editing a prompt file to track that it was modified locally.
        
        Args:
            prompt_name: Name of the prompt
        """
        metadata = self.load_metadata(prompt_name)
        metadata.locally_modified = True
        metadata.local_edit_timestamp = datetime.now().isoformat()
        
        # Update local content hash
        local_path = self.get_local_path(prompt_name)
        if local_path.exists():
            content = local_path.read_text(encoding='utf-8')
            metadata.local_content_hash = self.compute_hash(content)
        
        self.save_metadata(metadata)
        logger.info(f"✅ Marked {prompt_name} as locally edited")
    
    def get_sync_status(self) -> List[Dict[str, Any]]:
        """
        Get sync status of all prompts.
        
        Returns:
            List of prompt status information
        """
        status_list = []
        
        for prompt_file in self.cache_dir.glob("*.txt"):
            if prompt_file.stem.endswith('.backup'):
                continue
            
            prompt_name = prompt_file.stem
            metadata = self.load_metadata(prompt_name)
            
            status = {
                "prompt_name": prompt_name,
                "locally_modified": metadata.locally_modified,
                "last_fetched": metadata.last_fetched_from_hub,
                "last_edited": metadata.local_edit_timestamp,
                "last_sync": metadata.last_sync_timestamp,
                "sync_direction": metadata.sync_direction
            }
            
            status_list.append(status)
        
        return status_list


# Convenience functions
def sync_prompt(prompt_name: str, auto_push: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """Sync a single prompt."""
    manager = PromptSyncManager()
    return manager.sync_prompt(prompt_name, auto_push=auto_push, dry_run=dry_run)


def sync_all_prompts(auto_push: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """Sync all prompts."""
    manager = PromptSyncManager()
    return manager.sync_all_prompts(auto_push=auto_push, dry_run=dry_run)


def mark_prompt_as_edited(prompt_name: str):
    """Mark a prompt as locally edited."""
    manager = PromptSyncManager()
    manager.mark_as_locally_edited(prompt_name)

