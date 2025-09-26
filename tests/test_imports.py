#!/usr/bin/env python3
"""Test that reorganized imports work correctly."""

import pytest


class TestReorganizedImports:
    """Test reorganized imports after file restructuring."""
    
    def test_core_utilities_import(self):
        """Test core utilities import properly."""
        try:
            from utils.core.logging_config import setup_logging
            assert setup_logging is not None
        except ImportError as e:
            pytest.fail(f"Core logging import failed: {e}")
            
        try:
            from utils.core.platform_safe_commands import validate_command_before_execution
            assert validate_command_before_execution is not None
        except ImportError as e:
            pytest.fail(f"Platform commands import failed: {e}")
            
        try:
            from utils.core.file_manager import FileManager
            assert FileManager is not None
        except ImportError as e:
            pytest.fail(f"File manager import failed: {e}")
    
    def test_system_utilities_import(self):
        """Test system utilities import properly."""
        try:
            import utils.system.live_cursor_keyword_detector
            assert utils.system.live_cursor_keyword_detector is not None
        except ImportError as e:
            pytest.fail(f"Keyword detector import failed: {e}")
            
        try:
            import utils.system.universal_agent_tracker
            assert utils.system.universal_agent_tracker is not None
        except ImportError as e:
            pytest.fail(f"Agent tracker import failed: {e}")
    
    def test_prompt_utilities_import(self):
        """Test prompt utilities import properly."""
        try:
            from utils.prompts.prompt_editor import get_prompt_editor
            assert get_prompt_editor is not None
        except ImportError as e:
            pytest.fail(f"Prompt editor import failed: {e}")
            
        try:
            from utils.prompts.rag_processor import get_rag_processor
            assert get_rag_processor is not None
        except ImportError as e:
            pytest.fail(f"RAG processor import failed: {e}")
    
    def test_main_utils_import(self):
        """Test main utils import properly."""
        try:
            from utils import setup_logging
            assert setup_logging is not None
        except ImportError as e:
            pytest.fail(f"Utils main import failed: {e}")

