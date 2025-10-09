#!/usr/bin/env python3
"""
Agile Tools for MCP Server
==========================

Tool wrapper implementations for agile management functionality.
These wrappers connect MCP tool definitions to existing agile utilities.

Tools Implemented:
- agile.create_user_story: Create and manage user stories
- agile.update_artifacts: Automated agile artifact maintenance
- agile.update_story_status: User story status updates
- agile.update_catalogs: Unified catalog updates
- agile.detect_stories: Automatic story context detection

Author: AI Development Agent
Created: 2025-01-02 (US-MCP-001 Phase 1)
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


async def create_user_story(title: str, description: str, story_points: int = 5, 
                          priority: str = "Medium") -> Dict[str, Any]:
    """
    Create a new user story with full lifecycle management.
    
    Args:
        title: User story title
        description: Detailed story description
        story_points: Story complexity points (1-21)
        priority: Story priority (Critical, High, Medium, Low)
        
    Returns:
        Dictionary with story creation results
    """
    try:
        # Import agile story automation
        from utils.agile.agile_story_automation import AgileStoryAutomation, UserStory, Priority, Status
        
        # Create story automation instance
        automation = AgileStoryAutomation()
        
        # Map priority string to enum
        priority_map = {
            "Critical": Priority.CRITICAL,
            "High": Priority.HIGH, 
            "Medium": Priority.MEDIUM,
            "Low": Priority.LOW
        }
        
        # Create user story
        story = UserStory(
            story_id=f"US-{datetime.now().strftime('%Y%m%d')}-{len(automation.stories) + 1:03d}",
            title=title,
            description=description,
            priority=priority_map.get(priority, Priority.MEDIUM),
            status=Status.DRAFT,
            story_points=story_points,
            created_date=datetime.now(),
            assignee="AI Team"
        )
        
        # Add story to automation system
        automation.add_story(story)
        
        # Generate story file
        story_file = automation.generate_story_file(story)
        
        logger.info(f"✅ Created user story: {story.story_id}")
        
        return {
            "success": True,
            "story_id": story.story_id,
            "status": story.status.value,
            "file_path": str(story_file),
            "story_points": story_points,
            "priority": priority,
            "created_at": story.created_date.isoformat()
        }
        
    except ImportError as e:
        logger.error(f"❌ Agile automation not available: {e}")
        return {
            "success": False,
            "error": f"Agile automation module not available: {e}",
            "fallback_action": "Manual story creation required"
        }
    except Exception as e:
        logger.error(f"❌ Failed to create user story: {e}")
        return {
            "success": False,
            "error": str(e),
            "title": title,
            "description": description
        }


async def update_artifacts(artifact_type: str = "catalog", force_update: bool = False) -> Dict[str, Any]:
    """
    Update agile artifacts automatically.
    
    Args:
        artifact_type: Type of artifact to update (catalog, sprint, backlog)
        force_update: Force update even if no changes detected
        
    Returns:
        Dictionary with update results
    """
    try:
        # Import artifacts automation
        from utils.agile.artifacts_automation import ArtifactsAutomation
        
        # Create automation instance
        automation = ArtifactsAutomation()
        
        # Perform update based on artifact type
        if artifact_type == "catalog":
            result = automation.update_user_story_catalog(force=force_update)
        elif artifact_type == "sprint":
            result = automation.update_sprint_artifacts(force=force_update)
        elif artifact_type == "backlog":
            result = automation.update_backlog_artifacts(force=force_update)
        else:
            return {
                "success": False,
                "error": f"Unknown artifact type: {artifact_type}",
                "valid_types": ["catalog", "sprint", "backlog"]
            }
        
        logger.info(f"✅ Updated {artifact_type} artifacts")
        
        return {
            "success": True,
            "artifact_type": artifact_type,
            "updated": result.get("updated", True),
            "changes": result.get("changes", []),
            "files_modified": result.get("files_modified", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except ImportError as e:
        logger.error(f"❌ Artifacts automation not available: {e}")
        return {
            "success": False,
            "error": f"Artifacts automation module not available: {e}",
            "fallback_action": "Manual artifact update required"
        }
    except Exception as e:
        logger.error(f"❌ Failed to update artifacts: {e}")
        return {
            "success": False,
            "error": str(e),
            "artifact_type": artifact_type
        }


async def update_story_status(story_id: str, new_status: str, 
                            completion_notes: Optional[str] = None) -> Dict[str, Any]:
    """
    Update user story status with automated tracking.
    
    Args:
        story_id: User story identifier
        new_status: New status (Draft, Ready, In Progress, Completed, Cancelled)
        completion_notes: Optional completion notes
        
    Returns:
        Dictionary with status update results
    """
    try:
        # Import user story updates automation
        from scripts.automate_user_story_updates import UserStoryStatusAutomation
        
        # Create automation instance
        automation = UserStoryStatusAutomation()
        
        # Update story status
        result = automation.update_story_status(
            story_id=story_id,
            new_status=new_status,
            notes=completion_notes
        )
        
        logger.info(f"✅ Updated story {story_id} status to {new_status}")
        
        return {
            "success": True,
            "story_id": story_id,
            "old_status": result.get("old_status"),
            "new_status": new_status,
            "updated_at": datetime.now().isoformat(),
            "completion_notes": completion_notes,
            "artifacts_updated": result.get("artifacts_updated", False)
        }
        
    except ImportError as e:
        logger.error(f"❌ Story status automation not available: {e}")
        return {
            "success": False,
            "error": f"Story status automation module not available: {e}",
            "fallback_action": "Manual status update required"
        }
    except Exception as e:
        logger.error(f"❌ Failed to update story status: {e}")
        return {
            "success": False,
            "error": str(e),
            "story_id": story_id,
            "requested_status": new_status
        }


async def update_catalogs(catalog_types: Optional[List[str]] = None, 
                        force_update: bool = False) -> Dict[str, Any]:
    """
    Update all project catalogs with unified automation.
    
    Args:
        catalog_types: List of catalog types to update (None = all)
        force_update: Force update even if no changes detected
        
    Returns:
        Dictionary with catalog update results
    """
    try:
        # Import catalog update automation
        from scripts.update_all_catalogs import CatalogManager
        
        # Create catalog manager
        manager = CatalogManager()
        
        # Determine which catalogs to update
        if catalog_types is None:
            catalog_types = ["test_catalogue", "agile_artifacts", "user_story_updates"]
        
        results = {}
        total_updated = 0
        
        # Update each catalog type
        for catalog_type in catalog_types:
            if catalog_type in manager.catalogs:
                catalog_result = manager.update_catalog(catalog_type, force=force_update)
                results[catalog_type] = catalog_result
                if catalog_result.get("updated", False):
                    total_updated += 1
            else:
                results[catalog_type] = {
                    "success": False,
                    "error": f"Unknown catalog type: {catalog_type}"
                }
        
        logger.info(f"✅ Updated {total_updated}/{len(catalog_types)} catalogs")
        
        return {
            "success": True,
            "catalogs_updated": total_updated,
            "total_catalogs": len(catalog_types),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except ImportError as e:
        logger.error(f"❌ Catalog automation not available: {e}")
        return {
            "success": False,
            "error": f"Catalog automation module not available: {e}",
            "fallback_action": "Manual catalog update required"
        }
    except Exception as e:
        logger.error(f"❌ Failed to update catalogs: {e}")
        return {
            "success": False,
            "error": str(e),
            "requested_catalogs": catalog_types
        }


async def detect_stories(context_message: str, auto_create: bool = False) -> Dict[str, Any]:
    """
    Automatically detect story context and suggest story creation.
    
    Args:
        context_message: Message or context to analyze for story detection
        auto_create: Automatically create detected stories
        
    Returns:
        Dictionary with story detection results
    """
    try:
        # Import story detection automation
        from utils.agile.automatic_story_detection import AutomaticStoryDetection
        
        # Create detection instance
        detector = AutomaticStoryDetection()
        
        # Analyze context for story opportunities
        detection_result = detector.analyze_context(context_message)
        
        detected_stories = []
        created_stories = []
        
        # Process detected story opportunities
        for opportunity in detection_result.get("story_opportunities", []):
            story_suggestion = {
                "suggested_title": opportunity.get("title"),
                "suggested_description": opportunity.get("description"),
                "confidence": opportunity.get("confidence", 0.0),
                "category": opportunity.get("category", "general"),
                "estimated_points": opportunity.get("story_points", 5)
            }
            detected_stories.append(story_suggestion)
            
            # Auto-create if requested and confidence is high
            if auto_create and opportunity.get("confidence", 0.0) > 0.8:
                creation_result = await create_user_story(
                    title=opportunity.get("title"),
                    description=opportunity.get("description"),
                    story_points=opportunity.get("story_points", 5)
                )
                if creation_result.get("success"):
                    created_stories.append(creation_result["story_id"])
        
        logger.info(f"✅ Detected {len(detected_stories)} story opportunities")
        
        return {
            "success": True,
            "context_analyzed": context_message[:100] + "..." if len(context_message) > 100 else context_message,
            "stories_detected": len(detected_stories),
            "detected_stories": detected_stories,
            "auto_created": len(created_stories),
            "created_story_ids": created_stories,
            "timestamp": datetime.now().isoformat()
        }
        
    except ImportError as e:
        logger.error(f"❌ Story detection not available: {e}")
        return {
            "success": False,
            "error": f"Story detection module not available: {e}",
            "fallback_action": "Manual story analysis required"
        }
    except Exception as e:
        logger.error(f"❌ Failed to detect stories: {e}")
        return {
            "success": False,
            "error": str(e),
            "context_message": context_message[:100] + "..."
        }
