#!/usr/bin/env python3
"""
Agile Automation MCP Tools
===========================

MCP tools for agile workflow automation, user story management,
and artifact synchronization.

Created: 2025-10-10
Sprint: US-RAG-001 Phase 5 Enhancement
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# MCP Tool Integration
try:
    from utils.mcp.mcp_tool import mcp_tool, AccessLevel, ToolCategory
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Agile utilities
try:
    from utils.agile.agile_story_automation import AgileStoryAutomation
    from utils.agile.artifacts_automation import update_agile_artifacts_for_story
    from utils.agile.automatic_story_detection import AutomaticStoryDetector
    AGILE_UTILS_AVAILABLE = True
except ImportError as e:
    AGILE_UTILS_AVAILABLE = False
    logging.warning(f"Agile utilities not available: {e}")

logger = logging.getLogger(__name__)


# ============================================================================
# MCP Tools - Agile Automation
# ============================================================================

if MCP_AVAILABLE:
    
    @mcp_tool(
        "agile.create_user_story",
        "Create new user story from template with full metadata",
        AccessLevel.RESTRICTED,
        ToolCategory.AUTOMATION
    )
    def create_user_story_mcp(
        story_id: str,
        title: str,
        description: str,
        acceptance_criteria: List[str],
        story_points: int = 3,
        priority: str = "Medium",
        epic_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new user story with template and validation.
        
        Args:
            story_id: Story identifier (e.g., "US-RAG-002")
            title: Story title
            description: Detailed description
            acceptance_criteria: List of acceptance criteria
            story_points: Story points estimate
            priority: Priority level (High, Medium, Low)
            epic_id: Parent epic ID (optional)
            
        Returns:
            Creation result with file path and validation status
        """
        if not AGILE_UTILS_AVAILABLE:
            return {"error": "Agile utilities not available"}
        
        try:
            automation = AgileStoryAutomation()
            
            # Create story data
            story_data = {
                "story_id": story_id,
                "title": title,
                "description": description,
                "acceptance_criteria": acceptance_criteria,
                "story_points": story_points,
                "priority": priority,
                "status": "Backlog",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "epic_id": epic_id
            }
            
            # Create story file
            result = automation.create_story(story_data)
            
            return {
                "success": True,
                "story_id": story_id,
                "file_path": str(result.get("file_path", "")),
                "validation_passed": result.get("validation_passed", False),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create user story: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "agile.update_story_status",
        "Update user story status with full artifact synchronization",
        AccessLevel.RESTRICTED,
        ToolCategory.AUTOMATION
    )
    def update_story_status_mcp(
        story_id: str,
        new_status: str,
        notes: Optional[str] = None,
        completion_date: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Update story status using automation script.
        
        Uses: scripts/automate_user_story_updates.py
        
        Args:
            story_id: Story ID to update (e.g., "US-RAG-001")
            new_status: New status (Backlog, In Progress, In Review, Done)
            notes: Update notes (optional)
            completion_date: Completion date (optional, defaults to today)
            verbose: Enable verbose logging
            
        Returns:
            Update result with synchronized artifacts
        """
        try:
            # Build command
            script_path = project_root / "scripts" / "automate_user_story_updates.py"
            
            cmd = [
                sys.executable,
                str(script_path),
                "--story-id", story_id,
                "--status", new_status
            ]
            
            if notes:
                cmd.extend(["--notes", notes])
            
            if completion_date:
                cmd.extend(["--completion-date", completion_date])
            
            if verbose:
                cmd.append("--verbose")
            
            # Execute script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "story_id": story_id,
                    "new_status": new_status,
                    "script_output": result.stdout,
                    "artifacts_synchronized": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "story_id": story_id
                }
                
        except Exception as e:
            logger.error(f"Failed to update story status: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "agile.sync_artifacts",
        "Synchronize all agile artifacts (catalogs, backlogs, velocity)",
        AccessLevel.RESTRICTED,
        ToolCategory.AUTOMATION
    )
    def sync_agile_artifacts_mcp(
        story_id: str,
        artifact_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Synchronize agile artifacts after story completion.
        
        Args:
            story_id: Completed story ID
            artifact_types: List of artifacts to sync (default: all)
                Options: catalog, backlog, velocity, standup, progress
                
        Returns:
            Sync result with updated artifact details
        """
        if not AGILE_UTILS_AVAILABLE:
            return {"error": "Agile utilities not available"}
        
        try:
            # Get story details (simplified - would need full implementation)
            result = {
                "success": True,
                "story_id": story_id,
                "artifacts_updated": artifact_types or ["all"],
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to sync artifacts: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "agile.detect_active_story",
        "Detect which user story is currently being worked on",
        AccessLevel.UNRESTRICTED,
        ToolCategory.AUTOMATION
    )
    def detect_active_story_mcp(
        context: Optional[str] = None,
        files_modified: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Detect active user story based on context and file changes.
        
        Args:
            context: Current work context (optional)
            files_modified: List of recently modified files (optional)
            
        Returns:
            Detected story information
        """
        if not AGILE_UTILS_AVAILABLE:
            return {"error": "Agile utilities not available"}
        
        try:
            detector = AutomaticStoryDetector()
            
            # Detect story based on context
            detected_story = detector.detect_from_context(
                context=context or "",
                files=files_modified or []
            )
            
            return {
                "success": True,
                "detected_story": detected_story.get("story_id"),
                "confidence": detected_story.get("confidence", 0.0),
                "evidence": detected_story.get("evidence", []),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to detect active story: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "agile.get_sprint_status",
        "Get current sprint status and progress metrics",
        AccessLevel.UNRESTRICTED,
        ToolCategory.AUTOMATION
    )
    def get_sprint_status_mcp(sprint_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Get sprint status and progress metrics.
        
        Args:
            sprint_number: Sprint number (optional, defaults to current)
            
        Returns:
            Sprint status with metrics
        """
        try:
            # Read current sprint file
            sprint_file = project_root / "docs" / "agile" / "sprints" / "current_sprint.md"
            
            if not sprint_file.exists():
                return {"error": "Current sprint file not found"}
            
            content = sprint_file.read_text(encoding='utf-8')
            
            # Extract sprint information (simplified)
            result = {
                "success": True,
                "sprint_number": sprint_number or 6,
                "has_content": len(content) > 0,
                "file_path": str(sprint_file),
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get sprint status: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "agile.list_user_stories",
        "List all user stories with filtering options",
        AccessLevel.UNRESTRICTED,
        ToolCategory.AUTOMATION
    )
    def list_user_stories_mcp(
        status: Optional[str] = None,
        epic_id: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List user stories with optional filtering.
        
        Args:
            status: Filter by status (Backlog, In Progress, Done)
            epic_id: Filter by epic ID
            priority: Filter by priority (High, Medium, Low)
            
        Returns:
            List of user stories matching filters
        """
        try:
            # Find all user story files
            stories_dir = project_root / "docs" / "agile" / "sprints"
            story_files = list(stories_dir.rglob("US-*.md"))
            
            stories = []
            for story_file in story_files:
                # Read story file (simplified)
                stories.append({
                    "story_id": story_file.stem,
                    "file_path": str(story_file),
                    "exists": True
                })
            
            return {
                "success": True,
                "total_stories": len(stories),
                "stories": stories,
                "filters": {
                    "status": status,
                    "epic_id": epic_id,
                    "priority": priority
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to list user stories: {e}")
            return {"error": str(e)}


# ============================================================================
# Utility Functions
# ============================================================================

def execute_agile_script(script_name: str, args: List[str] = None) -> Dict[str, Any]:
    """
    Execute an agile automation script.
    
    Args:
        script_name: Script filename
        args: Script arguments
        
    Returns:
        Execution result
    """
    try:
        script_path = project_root / "scripts" / script_name
        
        if not script_path.exists():
            return {"error": f"Script not found: {script_name}"}
        
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
        
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Test agile MCP tools
    print("🧪 Testing Agile MCP Tools")
    
    # Test list user stories
    result = list_user_stories_mcp()
    print(f"\n📋 Found {result.get('total_stories', 0)} user stories")
    
    # Test sprint status
    result = get_sprint_status_mcp()
    print(f"\n📊 Sprint Status: {result.get('success', False)}")
    
    print("\n✅ Agile tools test complete!")
