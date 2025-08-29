#!/usr/bin/env python3
"""
Test-driven tests for Agile Artifacts Automation System

This system automates the tedious manual process of updating multiple agile artifacts
when stories are completed, following the Live Documentation Updates Rule.

TDD Approach: Write comprehensive tests first, then implement the automation.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

# Import the classes we'll implement (TDD red phase)
try:
    from utils.agile.artifacts_automation import (
        AgileArtifactsAutomator,
        StoryCompletion,
        ArtifactUpdateResult,
        ArtifactValidationResult
    )
except ImportError:
    # Expected in TDD red phase
    AgileArtifactsAutomator = None
    StoryCompletion = None
    ArtifactUpdateResult = None
    ArtifactValidationResult = None


class TestAgileArtifactsAutomator:
    """
    Test-driven tests for the main AgileArtifactsAutomator class.
    
    This class should automatically update all agile artifacts when stories complete.
    """

    @pytest.fixture
    def temp_docs_dir(self):
        """Create temporary docs directory structure for testing."""
        temp_dir = tempfile.mkdtemp()
        docs_dir = Path(temp_dir) / "docs" / "agile"
        
        # Create directory structure
        (docs_dir / "sprints" / "sprint_1").mkdir(parents=True)
        (docs_dir / "planning").mkdir(parents=True)
        
        # Create sample files
        self._create_sample_artifacts(docs_dir)
        
        yield docs_dir
        shutil.rmtree(temp_dir)

    def _create_sample_artifacts(self, docs_dir: Path):
        """Create sample agile artifact files for testing."""
        
        # Daily standup
        (docs_dir / "daily_standup.md").write_text("""# Daily Standup

#### **What I accomplished yesterday:**
- [x] Completed some work

#### **What I'm working on today:**
- Ready to start: US-002 (Testing Pipeline) - 13 points

#### **Any blockers or impediments:**
- None
""", encoding='utf-8')
        
        # Sprint progress
        (docs_dir / "sprints" / "sprint_1" / "progress.md").write_text("""# Sprint 1 Progress

## Story Progress Tracking

### **Completed Stories**
| Story ID | Title | Story Points | Completed Date | Notes |
|----------|-------|--------------|----------------|-------|
| | | | | |

### **Ready to Start Stories**
| Story ID | Title | Story Points | Priority | Dependencies | Ready Date |
|----------|-------|--------------|----------|--------------|------------|
| US-002 | Testing Pipeline | 13 | High | US-000 Complete | READY NOW |
""", encoding='utf-8')
        
        # Velocity tracking
        (docs_dir / "velocity_tracking_current.md").write_text("""# Velocity Tracking

## Current Sprint Velocity

### **Sprint 1 Metrics**
- **Story Points Completed**: 15
- **Current Velocity**: 15 points/day

### **Completed Stories**
| Story ID | Title | Story Points | Completion Date | Velocity Impact |
|----------|-------|--------------|-----------------|----------------|
| US-000 | Foundation | 15 | 2024-08-29 | +15 points |

### **Remaining Stories**
| Story ID | Title | Story Points | Priority | Dependencies | Velocity Impact |
|----------|-------|--------------|----------|--------------|----------------|
| US-002 | Testing Pipeline | 13 | High | None | +13 points |
""", encoding='utf-8')

        # Sprint backlog
        (docs_dir / "sprints" / "sprint_1" / "backlog.md").write_text("""# Sprint 1 Backlog

### **Story US-002: Testing Pipeline**
**Story Points**: 13 | **Priority**: High | **Assignee**: AI Team

#### **Acceptance Criteria**
- [ ] Automated testing implemented
- [ ] Coverage requirements met

#### **Tasks**
| Task | Status | Assignee |
|------|--------|----------|
| Design pipeline | To Do | AI Team |
| Implement tests | To Do | AI Team |
""", encoding='utf-8')

        # User stories
        (docs_dir / "planning" / "user_stories.md").write_text("""# User Stories

### **US-002: Testing Pipeline**
**As a** developer
**I want** automated testing
**So that** quality is assured

**Acceptance Criteria:**
- [ ] Automated testing implemented
- [ ] Coverage requirements met

**Story Points**: 13
**Priority**: High
""", encoding='utf-8')

    def test_automator_initialization(self, temp_docs_dir):
        """Test that the automator initializes correctly with docs directory."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: A docs directory
        docs_dir = temp_docs_dir
        
        # When: We initialize the automator
        automator = AgileArtifactsAutomator(docs_dir)
        
        # Then: It should be properly configured
        assert automator.docs_dir == docs_dir
        assert automator.is_initialized is True
        assert hasattr(automator, 'artifacts_config')
        assert hasattr(automator, 'timestamp_format')

    def test_story_completion_data_structure(self):
        """Test that story completion data structure is properly defined."""
        if StoryCompletion is None:
            pytest.skip("StoryCompletion not implemented yet (TDD red phase)")
        
        # When: We create a story completion object
        completion = StoryCompletion(
            story_id="US-002",
            title="Fully Automated Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed",
            acceptance_criteria=[
                "100% automated testing with zero manual intervention",
                "Test failures block deployment automatically"
            ],
            tasks_completed=8,
            tasks_total=8,
            notes="Perfect TDD success with 22/22 tests passing"
        )
        
        # Then: It should contain all necessary information
        assert completion.story_id == "US-002"
        assert completion.title == "Fully Automated Testing Pipeline"
        assert completion.story_points == 13
        assert completion.completion_date == "2024-08-29"
        assert completion.status == "completed"
        assert len(completion.acceptance_criteria) == 2
        assert completion.tasks_completed == 8
        assert completion.tasks_total == 8

    def test_update_daily_standup(self, temp_docs_dir):
        """Test that daily standup is updated correctly when story completes."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: An automator and completed story
        automator = AgileArtifactsAutomator(temp_docs_dir)
        completion = StoryCompletion(
            story_id="US-002",
            title="Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed"
        )
        
        # When: We update the daily standup
        result = automator.update_daily_standup(completion)
        
        # Then: The standup should be updated
        assert result.success is True
        assert result.file_updated is True
        
        # And: The file should contain completion information
        standup_content = (temp_docs_dir / "daily_standup.md").read_text()
        assert "US-002 (13 story points) - COMPLETED!" in standup_content
        assert "Testing Pipeline" in standup_content

    def test_update_sprint_progress(self, temp_docs_dir):
        """Test that sprint progress tracking is updated correctly."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: An automator and completed story
        automator = AgileArtifactsAutomator(temp_docs_dir)
        completion = StoryCompletion(
            story_id="US-002",
            title="Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed"
        )
        
        # When: We update sprint progress
        result = automator.update_sprint_progress(completion)
        
        # Then: The progress should be updated
        assert result.success is True
        assert result.file_updated is True
        
        # And: Story should be moved from ready to completed
        progress_content = (temp_docs_dir / "sprints" / "sprint_1" / "progress.md").read_text()
        assert "US-002" in progress_content
        assert "Testing Pipeline" in progress_content
        assert "2024-08-29" in progress_content

    def test_update_velocity_tracking(self, temp_docs_dir):
        """Test that velocity tracking is updated with new completion."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: An automator and completed story
        automator = AgileArtifactsAutomator(temp_docs_dir)
        completion = StoryCompletion(
            story_id="US-002",
            title="Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed"
        )
        
        # When: We update velocity tracking
        result = automator.update_velocity_tracking(completion)
        
        # Then: Velocity should be updated
        assert result.success is True
        assert result.velocity_updated is True
        
        # And: Story points should be added to completed total
        velocity_content = (temp_docs_dir / "velocity_tracking_current.md").read_text()
        assert "Story Points Completed**: 28" in velocity_content  # 15 + 13
        assert "US-002" in velocity_content

    def test_update_sprint_backlog(self, temp_docs_dir):
        """Test that sprint backlog is updated to mark story as complete."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: An automator and completed story with tasks
        automator = AgileArtifactsAutomator(temp_docs_dir)
        completion = StoryCompletion(
            story_id="US-002",
            title="Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed",
            acceptance_criteria=["Automated testing", "Coverage requirements"],
            tasks_completed=2,
            tasks_total=2
        )
        
        # When: We update the sprint backlog
        result = automator.update_sprint_backlog(completion)
        
        # Then: Backlog should be updated
        assert result.success is True
        assert result.tasks_updated is True
        
        # And: Story should be marked as completed
        backlog_content = (temp_docs_dir / "sprints" / "sprint_1" / "backlog.md").read_text()
        assert "**COMPLETED**" in backlog_content
        assert "[x]" in backlog_content  # Acceptance criteria checked

    def test_update_user_stories(self, temp_docs_dir):
        """Test that user stories master document is updated."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: An automator and completed story
        automator = AgileArtifactsAutomator(temp_docs_dir)
        completion = StoryCompletion(
            story_id="US-002",
            title="Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed"
        )
        
        # When: We update user stories
        result = automator.update_user_stories(completion)
        
        # Then: User stories should be updated
        assert result.success is True
        assert result.file_updated is True
        
        # And: Story should be marked as completed
        user_stories_content = (temp_docs_dir / "planning" / "user_stories.md").read_text()
        assert "**COMPLETED**" in user_stories_content
        assert "2024-08-29" in user_stories_content

    def test_update_all_artifacts(self, temp_docs_dir):
        """Test that all artifacts are updated in a single operation."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: An automator and completed story
        automator = AgileArtifactsAutomator(temp_docs_dir)
        completion = StoryCompletion(
            story_id="US-002",
            title="Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed",
            acceptance_criteria=["Automated testing", "Coverage requirements"],
            tasks_completed=2,
            tasks_total=2,
            notes="Perfect TDD implementation"
        )
        
        # When: We update all artifacts
        result = automator.update_all_artifacts(completion)
        
        # Then: All updates should succeed
        assert result.success is True
        assert result.artifacts_updated == 5  # 5 different files
        assert result.errors == []
        assert result.timestamp is not None
        
        # And: All files should be updated consistently
        assert result.daily_standup_updated is True
        assert result.sprint_progress_updated is True
        assert result.velocity_tracking_updated is True
        assert result.sprint_backlog_updated is True
        assert result.user_stories_updated is True

    def test_validation_after_updates(self, temp_docs_dir):
        """Test that validation ensures all artifacts are consistent after updates."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: An automator with updated artifacts
        automator = AgileArtifactsAutomator(temp_docs_dir)
        completion = StoryCompletion(
            story_id="US-002",
            title="Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed"
        )
        
        # When: We update and validate
        update_result = automator.update_all_artifacts(completion)
        validation_result = automator.validate_artifact_consistency(completion)
        
        # Then: Validation should pass
        assert validation_result.is_consistent is True
        assert validation_result.story_id_matches is True
        assert validation_result.story_points_match is True
        assert validation_result.completion_dates_match is True
        assert len(validation_result.inconsistencies) == 0

    def test_timestamp_management(self, temp_docs_dir):
        """Test that timestamps are properly managed across all artifacts."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: An automator
        automator = AgileArtifactsAutomator(temp_docs_dir)
        completion = StoryCompletion(
            story_id="US-002",
            title="Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed"
        )
        
        # When: We update with timestamp tracking
        result = automator.update_all_artifacts(completion, include_timestamps=True)
        
        # Then: Timestamps should be added
        assert result.success is True
        assert result.timestamp_format is not None
        
        # And: Files should contain proper timestamps
        for artifact_file in [
            "daily_standup.md",
            "sprints/sprint_1/progress.md",
            "velocity_tracking_current.md"
        ]:
            content = (temp_docs_dir / artifact_file).read_text()
            assert "Automated Update" in content

    def test_backup_and_rollback(self, temp_docs_dir):
        """Test that backup and rollback functionality works."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: An automator with backup enabled
        automator = AgileArtifactsAutomator(temp_docs_dir, enable_backup=True)
        completion = StoryCompletion(
            story_id="US-002",
            title="Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed"
        )
        
        # When: We update with backup
        original_content = (temp_docs_dir / "daily_standup.md").read_text()
        result = automator.update_all_artifacts(completion)
        
        # Then: Backup should be created
        assert result.backup_created is True
        assert result.backup_location is not None
        
        # When: We rollback
        rollback_result = automator.rollback_to_backup(result.backup_location)
        
        # Then: Files should be restored
        assert rollback_result.success is True
        restored_content = (temp_docs_dir / "daily_standup.md").read_text()
        assert restored_content == original_content

    def test_error_handling(self, temp_docs_dir):
        """Test that errors are handled gracefully during updates."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: An automator with a problematic file
        automator = AgileArtifactsAutomator(temp_docs_dir)
        completion = StoryCompletion(
            story_id="US-002",
            title="Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed"
        )
        
        # When: A file is read-only (simulating permission error)
        with patch('pathlib.Path.write_text', side_effect=PermissionError("Access denied")):
            result = automator.update_all_artifacts(completion)
        
        # Then: Error should be handled gracefully
        assert result.success is False
        assert len(result.errors) > 0
        assert "permission" in result.errors[0].lower() or "access" in result.errors[0].lower()

    def test_concurrent_updates_protection(self, temp_docs_dir):
        """Test that concurrent updates are protected against conflicts."""
        if AgileArtifactsAutomator is None:
            pytest.skip("AgileArtifactsAutomator not implemented yet (TDD red phase)")
        
        # Given: An automator with file locking
        automator = AgileArtifactsAutomator(temp_docs_dir, enable_locking=True)
        completion = StoryCompletion(
            story_id="US-002",
            title="Testing Pipeline",
            story_points=13,
            completion_date="2024-08-29",
            status="completed"
        )
        
        # When: We attempt concurrent updates (simulated)
        result1 = automator.update_all_artifacts(completion)
        result2 = automator.update_all_artifacts(completion)
        
        # Then: One should succeed, other should be handled appropriately
        assert result1.success is True or result2.success is True
        # At least one operation should complete successfully


@pytest.fixture
def sample_story_completion():
    """Sample story completion data for testing."""
    if StoryCompletion is None:
        return None
    
    return StoryCompletion(
        story_id="US-002",
        title="Fully Automated Testing Pipeline",
        story_points=13,
        completion_date="2024-08-29",
        status="completed",
        acceptance_criteria=[
            "100% automated testing with zero manual intervention",
            "Test failures block deployment automatically",
            "90%+ test coverage with performance validation",
            "Automated test execution on every commit",
            "Test result reporting and notification system"
        ],
        tasks_completed=8,
        tasks_total=8,
        notes="Perfect TDD success: 22/22 tests passing, zero manual intervention achieved",
        implementation_method="TDD",
        test_results="22/22 passing"
    )


if __name__ == "__main__":
    # Run the tests to see current TDD status
    pytest.main([__file__, "-v", "--tb=short"])
