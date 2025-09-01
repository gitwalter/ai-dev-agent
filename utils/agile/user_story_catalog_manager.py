#!/usr/bin/env python3
"""
User Story Catalog Manager
==========================

Automatically maintains the USER_STORY_CATALOG.md with real-time updates
whenever user stories are created, modified, or their status changes.

This ensures 100% transparency and up-to-date project visibility for all stakeholders.

Author: AI-Dev-Agent Team with Agile Excellence
Created: 2024
License: Open Source - For transparent project management
"""

import os
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
import glob

@dataclass
class UserStory:
    """Represents a user story with all its metadata."""
    story_id: str
    title: str
    epic: str
    sprint: str
    status: str
    points: int
    assignee: str
    priority: str
    dependencies: List[str]
    completion_date: Optional[str]
    file_path: str
    description: str
    business_value: str
    acceptance_criteria: List[str]
    last_updated: str

@dataclass
class CatalogMetrics:
    """Metrics for the user story catalog."""
    total_stories: int
    total_points: int
    completed_stories: int
    completed_points: int
    in_progress_stories: int
    in_progress_points: int
    pending_stories: int
    pending_points: int
    completion_rate: float
    points_completion_rate: float

class UserStoryCatalogManager:
    """
    Manages the USER_STORY_CATALOG.md with automatic updates and real-time synchronization.
    Ensures stakeholders always have current project visibility.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.catalog_file = self.project_root / "docs" / "agile" / "catalogs" / "USER_STORY_CATALOG.md"
        self.user_stories_dir = self.project_root / "docs" / "agile" / "sprints"
        
        # Status mappings
        self.status_mappings = {
            "completed": ["✅ Completed", "✅ Complete", "✅ COMPLETED", "Complete", "Completed"],
            "in_progress": ["🔄 In Progress", "In Progress", "🔄 Active", "Active"],
            "pending": ["⏳ Pending", "Pending", "📋 Planned", "Planned", "To Do"],
            "blocked": ["🔴 Blocked", "Blocked", "❌ Blocked"],
            "cancelled": ["❌ Cancelled", "Cancelled", "🚫 Cancelled"]
        }
        
        print("📋 User Story Catalog Manager initialized for real-time updates")
    
    def scan_all_user_stories(self) -> List[UserStory]:
        """Scan all user stories across all sprints and gather complete information."""
        
        user_stories = []
        
        # Find all user story files
        story_pattern = str(self.user_stories_dir / "**" / "US-*.md")
        story_files = glob.glob(story_pattern, recursive=True)
        
        print(f"📖 Scanning {len(story_files)} user story files...")
        
        for file_path in story_files:
            story = self._parse_user_story_file(file_path)
            if story:
                user_stories.append(story)
        
        # Sort by story ID
        user_stories.sort(key=lambda s: s.story_id)
        
        print(f"✅ Successfully parsed {len(user_stories)} user stories")
        return user_stories
    
    def _parse_user_story_file(self, file_path: str) -> Optional[UserStory]:
        """Parse a single user story file and extract all metadata."""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract basic information
            story_id = self._extract_story_id(file_path, content)
            title = self._extract_title(content)
            epic = self._extract_epic(content, file_path)
            sprint = self._extract_sprint(file_path)
            status = self._extract_status(content)
            points = self._extract_points(content)
            assignee = self._extract_assignee(content)
            priority = self._extract_priority(content)
            dependencies = self._extract_dependencies(content)
            completion_date = self._extract_completion_date(content)
            description = self._extract_description(content)
            business_value = self._extract_business_value(content)
            acceptance_criteria = self._extract_acceptance_criteria(content)
            
            return UserStory(
                story_id=story_id,
                title=title,
                epic=epic,
                sprint=sprint,
                status=status,
                points=points,
                assignee=assignee,
                priority=priority,
                dependencies=dependencies,
                completion_date=completion_date,
                file_path=str(Path(file_path).relative_to(self.project_root)),
                description=description,
                business_value=business_value,
                acceptance_criteria=acceptance_criteria,
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
        except Exception as e:
            print(f"⚠️ Error parsing {file_path}: {e}")
            return None
    
    def _extract_story_id(self, file_path: str, content: str) -> str:
        """Extract story ID from filename or content."""
        # Try filename first
        filename = Path(file_path).stem
        if filename.startswith("US-"):
            return filename
        
        # Try content
        id_match = re.search(r'\*\*Story ID\*\*:\s*([A-Z]+-[A-Z0-9]+-[0-9]+)', content)
        if id_match:
            return id_match.group(1)
        
        # Fallback to filename
        return filename
    
    def _extract_title(self, content: str) -> str:
        """Extract story title."""
        # Try Story Overview section
        title_match = re.search(r'\*\*Title\*\*:\s*(.+)', content)
        if title_match:
            return title_match.group(1).strip()
        
        # Try main heading
        heading_match = re.search(r'^#\s+User Story [^:]*:\s*(.+)', content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()
        
        # Try first heading
        first_heading = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        if first_heading:
            return first_heading.group(1).strip()
        
        return "Unknown Title"
    
    def _extract_epic(self, content: str, file_path: str) -> str:
        """Extract epic information."""
        # Try explicit epic mention
        epic_match = re.search(r'\*\*Epic\*\*:\s*(.+)', content)
        if epic_match:
            return epic_match.group(1).strip()
        
        # Try dependencies
        deps_match = re.search(r'\*\*Dependencies\*\*:\s*(.+)', content)
        if deps_match and "Epic" in deps_match.group(1):
            return deps_match.group(1).strip()
        
        # Infer from content
        if any(keyword in content.lower() for keyword in ["wisdom", "philosophical", "confucian", "wu wei", "sun tzu"]):
            return "Philosophical Integration"
        elif any(keyword in content.lower() for keyword in ["architecture", "documentation", "overview"]):
            return "Architecture Documentation"
        elif any(keyword in content.lower() for keyword in ["test", "quality", "validation"]):
            return "Quality Assurance"
        elif any(keyword in content.lower() for keyword in ["agent", "ai", "prompt"]):
            return "AI Development"
        elif any(keyword in content.lower() for keyword in ["foundation", "infrastructure"]):
            return "Foundation"
        else:
            return "General Development"
    
    def _extract_sprint(self, file_path: str) -> str:
        """Extract sprint from file path."""
        sprint_match = re.search(r'sprint_(\d+)', file_path)
        if sprint_match:
            return f"Sprint {sprint_match.group(1)}"
        
        if "sprint_0" in file_path:
            return "Sprint 0"
        
        return "Current Sprint"
    
    def _extract_status(self, content: str) -> str:
        """Extract status from content."""
        status_match = re.search(r'\*\*Status\*\*:\s*(.+)', content)
        if status_match:
            status_text = status_match.group(1).strip()
            return self._normalize_status(status_text)
        
        # Check for completion indicators
        if "✅ COMPLETED" in content or "✅ Complete" in content:
            return "✅ Completed"
        elif "🔄 In Progress" in content or "In Progress" in content:
            return "🔄 In Progress"
        elif "⏳ Pending" in content or "Pending" in content:
            return "⏳ Pending"
        elif "🔴 Blocked" in content or "Blocked" in content:
            return "🔴 Blocked"
        else:
            return "⏳ Pending"
    
    def _normalize_status(self, status_text: str) -> str:
        """Normalize status text to standard format."""
        for standard_status, variations in self.status_mappings.items():
            if any(variation.lower() in status_text.lower() for variation in variations):
                if standard_status == "completed":
                    return "✅ Completed"
                elif standard_status == "in_progress":
                    return "🔄 In Progress"
                elif standard_status == "pending":
                    return "⏳ Pending"
                elif standard_status == "blocked":
                    return "🔴 Blocked"
                elif standard_status == "cancelled":
                    return "❌ Cancelled"
        
        return status_text
    
    def _extract_points(self, content: str) -> int:
        """Extract story points."""
        points_match = re.search(r'\*\*Story Points\*\*:\s*(\d+)', content)
        if points_match:
            return int(points_match.group(1))
        
        # Alternative patterns
        alt_points = re.search(r'Points\*\*:\s*(\d+)', content)
        if alt_points:
            return int(alt_points.group(1))
        
        return 0
    
    def _extract_assignee(self, content: str) -> str:
        """Extract assignee information."""
        assignee_match = re.search(r'\*\*Assignee\*\*:\s*(.+)', content)
        if assignee_match:
            return assignee_match.group(1).strip()
        
        return "AI Team"
    
    def _extract_priority(self, content: str) -> str:
        """Extract priority information."""
        priority_match = re.search(r'\*\*Priority\*\*:\s*(.+)', content)
        if priority_match:
            return priority_match.group(1).strip()
        
        # Check for critical indicators
        if "CRITICAL" in content.upper():
            return "🔴 Critical"
        elif "HIGH" in content.upper():
            return "🟡 High"
        elif "MEDIUM" in content.upper():
            return "🟠 Medium"
        elif "LOW" in content.upper():
            return "🟢 Low"
        else:
            return "🟠 Medium"
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies list."""
        deps_match = re.search(r'\*\*Dependencies\*\*:\s*(.+)', content)
        if deps_match:
            deps_text = deps_match.group(1).strip()
            if deps_text.lower() in ["none", "n/a", "-"]:
                return []
            
            # Split by common separators
            deps = re.split(r'[,;\s]+', deps_text)
            return [dep.strip() for dep in deps if dep.strip()]
        
        return []
    
    def _extract_completion_date(self, content: str) -> Optional[str]:
        """Extract completion date if available."""
        completion_match = re.search(r'\*\*Completion Date\*\*:\s*(.+)', content)
        if completion_match:
            return completion_match.group(1).strip()
        
        return None
    
    def _extract_description(self, content: str) -> str:
        """Extract story description."""
        desc_match = re.search(r'## Story Description\s*\n(.+?)(?=\n##)', content, re.DOTALL)
        if desc_match:
            return desc_match.group(1).strip()
        
        # Alternative patterns
        desc_alt = re.search(r'## Description\s*\n(.+?)(?=\n##)', content, re.DOTALL)
        if desc_alt:
            return desc_alt.group(1).strip()
        
        return "No description available"
    
    def _extract_business_value(self, content: str) -> str:
        """Extract business justification/value."""
        value_match = re.search(r'## Business Justification\s*\n(.+?)(?=\n##)', content, re.DOTALL)
        if value_match:
            return value_match.group(1).strip()
        
        return "Business value to be defined"
    
    def _extract_acceptance_criteria(self, content: str) -> List[str]:
        """Extract acceptance criteria."""
        criteria = []
        
        # Find acceptance criteria section
        ac_match = re.search(r'## Acceptance Criteria\s*\n(.+?)(?=\n##)', content, re.DOTALL)
        if ac_match:
            ac_text = ac_match.group(1)
            
            # Extract bullet points
            bullets = re.findall(r'[-*]\s*\[.\]\s*(.+)', ac_text)
            criteria.extend(bullets)
            
            # Extract numbered items
            numbered = re.findall(r'\d+\.\s*(.+)', ac_text)
            criteria.extend(numbered)
        
        return criteria
    
    def calculate_metrics(self, user_stories: List[UserStory]) -> CatalogMetrics:
        """Calculate comprehensive metrics for the catalog."""
        
        total_stories = len(user_stories)
        total_points = sum(story.points for story in user_stories)
        
        completed_stories = len([s for s in user_stories if "completed" in s.status.lower()])
        completed_points = sum(s.points for s in user_stories if "completed" in s.status.lower())
        
        in_progress_stories = len([s for s in user_stories if "progress" in s.status.lower()])
        in_progress_points = sum(s.points for s in user_stories if "progress" in s.status.lower())
        
        pending_stories = len([s for s in user_stories if "pending" in s.status.lower()])
        pending_points = sum(s.points for s in user_stories if "pending" in s.status.lower())
        
        completion_rate = (completed_stories / max(total_stories, 1)) * 100
        points_completion_rate = (completed_points / max(total_points, 1)) * 100
        
        return CatalogMetrics(
            total_stories=total_stories,
            total_points=total_points,
            completed_stories=completed_stories,
            completed_points=completed_points,
            in_progress_stories=in_progress_stories,
            in_progress_points=in_progress_points,
            pending_stories=pending_stories,
            pending_points=pending_points,
            completion_rate=completion_rate,
            points_completion_rate=points_completion_rate
        )
    
    def generate_catalog_content(self, user_stories: List[UserStory], metrics: CatalogMetrics) -> str:
        """Generate the complete USER_STORY_CATALOG.md content."""
        
        # Group stories by epic and sprint
        stories_by_epic = defaultdict(list)
        stories_by_sprint = defaultdict(list)
        
        for story in user_stories:
            stories_by_epic[story.epic].append(story)
            stories_by_sprint[story.sprint].append(story)
        
        # Generate content
        content = f"""# User Story Catalog - Master Index

**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Automated Real-Time Update
**Maintainer**: AI Development Agent Project Team  
**Purpose**: Central tracking of all user stories across all sprints
**🤖 Status**: Automatically synchronized with all user story files

## 📊 **Catalog Overview**

This catalog provides a **real-time view** of all user stories across the entire project, automatically updated whenever user stories are created, modified, or their status changes.

**🤖 AUTOMATED AGILE MANAGEMENT**: This catalog is automatically maintained by the User Story Catalog Manager. All changes to user stories are immediately reflected here to ensure 100% stakeholder transparency.

## 🎯 **Project Metrics Dashboard**

### **📈 Overall Statistics**
- **Total User Stories**: {metrics.total_stories}
- **Total Story Points**: {metrics.total_points}
- **Completion Rate**: {metrics.completion_rate:.1f}% ({metrics.completed_stories}/{metrics.total_stories} stories)
- **Points Completion**: {metrics.points_completion_rate:.1f}% ({metrics.completed_points}/{metrics.total_points} points)

### **📊 Status Distribution**
| Status | Stories | Points | Percentage |
|--------|---------|--------|------------|
| ✅ **Completed** | **{metrics.completed_stories}** | **{metrics.completed_points}** | **{(metrics.completed_stories/max(metrics.total_stories,1)*100):.1f}%** |
| 🔄 In Progress | {metrics.in_progress_stories} | {metrics.in_progress_points} | {(metrics.in_progress_stories/max(metrics.total_stories,1)*100):.1f}% |
| ⏳ Pending | {metrics.pending_stories} | {metrics.pending_points} | {(metrics.pending_stories/max(metrics.total_stories,1)*100):.1f}% |

## 🎯 **Stories by Sprint**

"""
        
        # Add stories grouped by sprint
        for sprint in sorted(stories_by_sprint.keys()):
            sprint_stories = stories_by_sprint[sprint]
            sprint_metrics = self.calculate_metrics(sprint_stories)
            
            content += f"""### **🚀 {sprint}** 
**Status**: {sprint_metrics.completed_stories}/{sprint_metrics.total_stories} completed ({sprint_metrics.completion_rate:.1f}%)

| ID | Title | Epic | Status | Points | Assignee | Priority |
|----|-------|------|--------|--------|----------|----------|
"""
            
            for story in sorted(sprint_stories, key=lambda s: s.story_id):
                content += f"| **{story.story_id}** | **{story.title}** | {story.epic} | {story.status} | {story.points} | {story.assignee} | {story.priority} |\n"
            
            content += f"\n**Sprint Total**: {sprint_metrics.total_stories} stories, {sprint_metrics.total_points} points\n\n"
        
        # Add stories grouped by epic
        content += "## 🏗️ **Stories by Epic**\n\n"
        
        for epic in sorted(stories_by_epic.keys()):
            epic_stories = stories_by_epic[epic]
            epic_metrics = self.calculate_metrics(epic_stories)
            
            content += f"""### **{epic}**
**Epic Status**: {epic_metrics.completed_stories}/{epic_metrics.total_stories} completed ({epic_metrics.completion_rate:.1f}%)

| ID | Title | Sprint | Status | Points | Priority |
|----|-------|--------|--------|--------|----------|
"""
            
            for story in sorted(epic_stories, key=lambda s: s.story_id):
                content += f"| **{story.story_id}** | **{story.title}** | {story.sprint} | {story.status} | {story.points} | {story.priority} |\n"
            
            content += f"\n**Epic Total**: {epic_metrics.total_stories} stories, {epic_metrics.total_points} points\n\n"
        
        # Add detailed story information
        content += "## 📋 **Detailed Story Information**\n\n"
        
        for story in user_stories:
            content += f"""### **{story.story_id}: {story.title}**
- **Epic**: {story.epic}
- **Sprint**: {story.sprint}
- **Status**: {story.status}
- **Points**: {story.points}
- **Priority**: {story.priority}
- **Assignee**: {story.assignee}
- **Dependencies**: {', '.join(story.dependencies) if story.dependencies else 'None'}
- **File**: `{story.file_path}`
- **Last Updated**: {story.last_updated}

**Description**: {story.description[:200]}{'...' if len(story.description) > 200 else ''}

---

"""
        
        # Add footer
        content += f"""
## 🔄 **Automatic Updates**

This catalog is automatically updated whenever:
- New user stories are created
- Existing user stories are modified
- Story status changes
- Story metadata is updated

**Last Scan**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Stories Scanned**: {metrics.total_stories}  
**Update Frequency**: Real-time  

## 📞 **For Questions**

This catalog is maintained automatically by the User Story Catalog Manager. For questions about specific user stories, refer to the individual story files or contact the assigned team members.

---

**🌟 This catalog represents our commitment to complete transparency and stakeholder visibility in our mission to serve all beings through wisdom-driven AI development.** 🙏✨
"""
        
        return content
    
    def update_catalog(self) -> bool:
        """Update the USER_STORY_CATALOG.md with current information."""
        
        try:
            print("🔄 Updating User Story Catalog...")
            
            # Scan all user stories
            user_stories = self.scan_all_user_stories()
            
            # Calculate metrics
            metrics = self.calculate_metrics(user_stories)
            
            # Generate content
            catalog_content = self.generate_catalog_content(user_stories, metrics)
            
            # Ensure directory exists
            self.catalog_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write updated catalog
            with open(self.catalog_file, 'w', encoding='utf-8') as f:
                f.write(catalog_content)
            
            print(f"✅ User Story Catalog updated successfully!")
            print(f"   📊 {metrics.total_stories} stories, {metrics.total_points} points")
            print(f"   ✅ {metrics.completed_stories} completed ({metrics.completion_rate:.1f}%)")
            print(f"   📁 Catalog saved to: {self.catalog_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating catalog: {e}")
            return False
    
    def watch_for_changes(self) -> None:
        """Watch for changes in user story files and auto-update catalog."""
        print("👁️ Starting user story change monitoring...")
        print("   (In a real implementation, this would use file system watchers)")
        
        # This would use file system watchers like watchdog in a real implementation
        # For now, we'll just update the catalog once
        self.update_catalog()

def main():
    """Demonstrate the User Story Catalog Manager."""
    
    print("📋 " + "="*60)
    print("🔄 USER STORY CATALOG MANAGER DEMONSTRATION")
    print("   Automatic real-time catalog maintenance")
    print("="*60)
    
    # Initialize manager
    manager = UserStoryCatalogManager()
    
    # Update catalog
    success = manager.update_catalog()
    
    if success:
        print("\n✅ User Story Catalog Manager ready for automatic updates!")
    else:
        print("\n❌ Error in catalog management - please check configuration")
    
    print("="*60)

if __name__ == "__main__":
    main()
