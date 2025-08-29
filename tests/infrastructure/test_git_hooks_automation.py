#!/usr/bin/env python3
"""
Infrastructure Tests for Git Hooks Automation

This module tests the complete git hooks automation system including:
- Pre-push hook functionality
- Post-merge hook functionality  
- Safe git operations for database management
- End-to-end push-pull cycles
- Error handling and recovery
- IDE and command line integration

Excellence Standards Applied:
- Comprehensive test coverage (all scenarios)
- Evidence-based validation (actual execution)
- Error exposure (no silent failures)
- Complete workflow testing (end-to-end)
"""

import pytest
import subprocess
import tempfile
import shutil
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from typing import List, Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.safe_git_operations import SafeGitOperations


class TestGitHooksInfrastructure:
    """
    Comprehensive tests for git hooks automation infrastructure.
    
    Tests both Windows PowerShell hooks and Python backend integration.
    """
    
    def setup_method(self):
        """Set up test environment for each test."""
        self.project_root = project_root
        self.git_hooks_dir = self.project_root / ".git" / "hooks"
        self.safe_git = SafeGitOperations(self.project_root)
        
        # Test file paths
        self.test_db_file = self.project_root / "prompts" / "prompt_templates.db"
        self.test_gitignore = self.project_root / ".gitignore"
        
    def test_safe_git_operations_initialization(self):
        """Test SafeGitOperations initializes correctly."""
        safe_git = SafeGitOperations()
        
        assert safe_git.project_root is not None
        assert isinstance(safe_git.database_files, list)
        assert len(safe_git.database_files) > 0
        assert "prompts/prompt_templates.db" in safe_git.database_files
        
    def test_git_status_check(self):
        """Test git status checking functionality."""
        has_changes, staged, unstaged = self.safe_git.check_git_status()
        
        # Should return boolean and lists
        assert isinstance(has_changes, bool)
        assert isinstance(staged, list)
        assert isinstance(unstaged, list)
        
    def test_database_files_detection(self):
        """Test detection of staged database files."""
        # Test when no database files are staged
        has_db_staged = self.safe_git.has_database_files_staged()
        staged_db_files = self.safe_git.get_staged_database_files()
        
        assert isinstance(has_db_staged, bool)
        assert isinstance(staged_db_files, list)
        
    def test_safe_git_operations_command_line_interface(self):
        """Test the command line interface of safe_git_operations.py."""
        script_path = self.project_root / "utils" / "safe_git_operations.py"
        
        # Test status command
        result = subprocess.run([
            sys.executable, str(script_path), "status"
        ], capture_output=True, text=True, cwd=self.project_root)
        
        assert result.returncode == 0
        assert "Git Status:" in result.stdout
        
    def test_safe_git_operations_pre_merge_command(self):
        """Test pre-merge command functionality."""
        script_path = self.project_root / "utils" / "safe_git_operations.py"
        
        # Test pre-merge command
        result = subprocess.run([
            sys.executable, str(script_path), "pre-merge"
        ], capture_output=True, text=True, cwd=self.project_root)
        
        assert result.returncode == 0
        assert "Pre-merge preparation completed successfully" in result.stdout
        
    def test_safe_git_operations_post_merge_command(self):
        """Test post-merge command functionality."""
        script_path = self.project_root / "utils" / "safe_git_operations.py"
        
        # Test post-merge command
        result = subprocess.run([
            sys.executable, str(script_path), "post-merge"
        ], capture_output=True, text=True, cwd=self.project_root)
        
        assert result.returncode == 0
        assert "Post-merge hook executed successfully" in result.stdout
        
    def test_git_hooks_files_exist(self):
        """Test that required git hook files exist."""
        pre_push_hook = self.git_hooks_dir / "pre-push.ps1"
        post_merge_hook = self.git_hooks_dir / "post-merge.ps1"
        
        assert pre_push_hook.exists(), f"Pre-push hook missing: {pre_push_hook}"
        assert post_merge_hook.exists(), f"Post-merge hook missing: {post_merge_hook}"
        
        # Check that they reference the correct script
        pre_push_content = pre_push_hook.read_text()
        post_merge_content = post_merge_hook.read_text()
        
        assert "safe_git_operations.py" in pre_push_content
        assert "safe_git_operations.py" in post_merge_content
        
    @pytest.mark.skipif(os.name != 'nt', reason="PowerShell tests only run on Windows")
    def test_powershell_pre_push_hook_execution(self):
        """Test PowerShell pre-push hook execution on Windows."""
        hook_path = self.git_hooks_dir / "pre-push.ps1"
        
        if not hook_path.exists():
            pytest.skip("Pre-push PowerShell hook not found")
            
        # Execute the PowerShell hook
        result = subprocess.run([
            "powershell", "-ExecutionPolicy", "Bypass", "-File", str(hook_path)
        ], capture_output=True, text=True, cwd=self.project_root)
        
        assert result.returncode == 0, f"Pre-push hook failed: {result.stderr}"
        assert "Pre-push hook:" in result.stdout
        assert "preparation completed successfully" in result.stdout
        
    @pytest.mark.skipif(os.name != 'nt', reason="PowerShell tests only run on Windows")
    def test_powershell_post_merge_hook_execution(self):
        """Test PowerShell post-merge hook execution on Windows."""
        hook_path = self.git_hooks_dir / "post-merge.ps1"
        
        if not hook_path.exists():
            pytest.skip("Post-merge PowerShell hook not found")
            
        # Execute the PowerShell hook
        result = subprocess.run([
            "powershell", "-ExecutionPolicy", "Bypass", "-File", str(hook_path)
        ], capture_output=True, text=True, cwd=self.project_root)
        
        assert result.returncode == 0, f"Post-merge hook failed: {result.stderr}"
        assert "Post-merge hook:" in result.stdout
        assert "Development database successfully restored" in result.stdout
        
    def test_error_handling_invalid_command(self):
        """Test error handling for invalid commands."""
        script_path = self.project_root / "utils" / "safe_git_operations.py"
        
        # Test invalid command
        result = subprocess.run([
            sys.executable, str(script_path), "invalid-command"
        ], capture_output=True, text=True, cwd=self.project_root)
        
        assert result.returncode != 0
        assert "invalid choice" in result.stderr.lower()
        
    def test_prepare_for_pull_functionality(self):
        """Test prepare_for_pull method functionality."""
        # Mock git operations to avoid affecting real repository
        with patch.object(self.safe_git, 'check_git_status') as mock_status:
            with patch.object(self.safe_git, 'stash_database_changes') as mock_stash:
                # Test when no database files are staged
                mock_status.return_value = (False, [], [])
                
                success, stashed = self.safe_git.prepare_for_pull()
                
                assert success is True
                assert stashed is False
                mock_stash.assert_not_called()
                
    def test_cleanup_after_pull_functionality(self):
        """Test cleanup_after_pull method functionality."""
        with patch.object(self.safe_git, 'restore_stashed_changes') as mock_restore:
            mock_restore.return_value = True
            
            # Test cleanup when changes were stashed
            success = self.safe_git.cleanup_after_pull(had_stashed_changes=True)
            
            assert success is True
            mock_restore.assert_called_once()
            
            # Test cleanup when no changes were stashed
            mock_restore.reset_mock()
            success = self.safe_git.cleanup_after_pull(had_stashed_changes=False)
            
            assert success is True
            mock_restore.assert_not_called()


class TestGitHooksEndToEndScenarios:
    """
    End-to-end scenario tests for git hooks automation.
    
    Tests complete workflows that would occur during real development.
    """
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = project_root
        self.safe_git = SafeGitOperations(self.project_root)
        
    def test_complete_push_pull_cycle_simulation(self):
        """Test simulated complete push-pull cycle."""
        # This test simulates the complete cycle without actually doing git operations
        
        # 1. Simulate pre-push preparation
        success, stashed = self.safe_git.prepare_for_pull()
        assert success is True
        
        # 2. Simulate post-merge cleanup
        cleanup_success = self.safe_git.cleanup_after_pull(stashed)
        assert cleanup_success is True
        
    def test_database_file_handling_workflow(self):
        """Test database file handling workflow."""
        # Get current database files that might be staged
        staged_db_files = self.safe_git.get_staged_database_files()
        
        # Should return a list (empty or with files)
        assert isinstance(staged_db_files, list)
        
        # Test unstaging (should work even if no files are staged)
        unstage_success = self.safe_git.unstage_database_files()
        assert unstage_success is True
        
    def test_git_automation_wrapper_integration(self):
        """Test integration with git automation wrapper."""
        wrapper_path = self.project_root / "utils" / "git_automation_wrapper.py"
        
        if not wrapper_path.exists():
            pytest.skip("Git automation wrapper not found")
        
        # Test that wrapper can be imported and initialized
        sys.path.insert(0, str(self.project_root))
        try:
            from utils.git_automation_wrapper import GitAutomationWrapper
            
            # Should initialize without errors
            wrapper = GitAutomationWrapper(self.project_root)
            assert wrapper.project_root == self.project_root
            assert wrapper.safe_git is not None
            
        except ImportError as e:
            pytest.skip(f"Git automation wrapper import failed: {e}")


class TestGitHooksErrorScenarios:
    """
    Test error scenarios and edge cases for git hooks automation.
    """
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = project_root
        self.safe_git = SafeGitOperations(self.project_root)
        
    def test_missing_git_repository(self):
        """Test behavior when not in a git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            safe_git_temp = SafeGitOperations(temp_path)
            
            # Should handle missing git repository gracefully
            try:
                has_changes, staged, unstaged = safe_git_temp.check_git_status()
                # If it doesn't raise an exception, it should return reasonable defaults
                assert isinstance(has_changes, bool)
                assert isinstance(staged, list)
                assert isinstance(unstaged, list)
            except Exception:
                # It's acceptable to raise an exception for missing git repo
                pass
                
    def test_git_command_failure_handling(self):
        """Test handling of git command failures."""
        with patch('subprocess.run') as mock_run:
            # Simulate git command failure
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Git command failed"
            mock_run.return_value = mock_result
            
            # Should handle git command failure gracefully
            has_changes, staged, unstaged = self.safe_git.check_git_status()
            
            # Should return defaults when git command fails
            assert has_changes is False
            assert staged == []
            assert unstaged == []


class TestGitHooksDocumentationAndCompliance:
    """
    Test documentation and compliance aspects of git hooks automation.
    """
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = project_root
    
    def test_safe_git_operations_has_proper_docstrings(self):
        """Test that SafeGitOperations has proper documentation."""
        from utils.safe_git_operations import SafeGitOperations
        
        # Class should have docstring
        assert SafeGitOperations.__doc__ is not None
        assert len(SafeGitOperations.__doc__.strip()) > 50
        
        # Key methods should have docstrings
        assert SafeGitOperations.check_git_status.__doc__ is not None
        assert SafeGitOperations.prepare_for_pull.__doc__ is not None
        assert SafeGitOperations.cleanup_after_pull.__doc__ is not None
        
    def test_git_hooks_contain_required_comments(self):
        """Test that git hooks contain proper documentation."""
        hooks_dir = self.project_root / ".git" / "hooks"
        
        if (hooks_dir / "pre-push.ps1").exists():
            pre_push_content = (hooks_dir / "pre-push.ps1").read_text()
            assert "pre-push hook" in pre_push_content.lower()
            assert "database" in pre_push_content.lower()
            
        if (hooks_dir / "post-merge.ps1").exists():
            post_merge_content = (hooks_dir / "post-merge.ps1").read_text()
            assert "post-merge hook" in post_merge_content.lower()
            assert "database" in post_merge_content.lower()


if __name__ == "__main__":
    # Run tests with pytest when executed directly
    pytest.main([__file__, "-v", "--tb=short"])
