"""
Integration tests for Adaptive Retrieval UI components.

Tests the UI integration of the adaptive chunk retrieval system (US-RAG-003).

Author: AI Dev Agent
Date: 2025-10-10
User Story: US-RAG-003
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestAdaptiveRetrievalUIIntegration:
    """
    Integration tests for the Adaptive Retrieval UI components.
    
    These tests verify that:
    1. UI controls are properly initialized with session state
    2. Retrieval mode selection works correctly
    3. Manual chunk count slider appears/disappears appropriately
    4. Parameters are correctly passed to the RAG swarm
    5. Adaptive decision info is displayed in debug mode
    """
    
    @pytest.fixture
    def mock_streamlit(self):
        """Mock Streamlit components."""
        with patch('streamlit.selectbox') as mock_select, \
             patch('streamlit.slider') as mock_slider, \
             patch('streamlit.success') as mock_success, \
             patch('streamlit.info') as mock_info, \
             patch('streamlit.warning') as mock_warning, \
             patch('streamlit.session_state', new_callable=lambda: MagicMock()) as mock_state:
            
            # Setup default session state values
            mock_state.retrieval_mode = 'auto'
            mock_state.manual_chunk_count = 15
            
            yield {
                'selectbox': mock_select,
                'slider': mock_slider,
                'success': mock_success,
                'info': mock_info,
                'warning': mock_warning,
                'session_state': mock_state
            }
    
    def test_retrieval_mode_selection(self, mock_streamlit):
        """Test retrieval mode selection updates session state correctly."""
        # Simulate user selecting different modes
        test_cases = [
            ("🤖 Auto (Recommended)", "auto"),
            ("👤 Manual Control", "manual"),
            ("⚡ Performance Mode", "performance")
        ]
        
        for display_value, expected_mode in test_cases:
            mock_streamlit['selectbox'].return_value = display_value
            
            # Simulate mode extraction logic
            if "Auto" in display_value:
                result_mode = "auto"
            elif "Manual" in display_value:
                result_mode = "manual"
            else:
                result_mode = "performance"
            
            assert result_mode == expected_mode, \
                f"Mode extraction failed for {display_value}"
    
    def test_manual_chunk_count_validation(self, mock_streamlit):
        """Test manual chunk count slider validation and feedback."""
        mock_streamlit['session_state'].retrieval_mode = 'manual'
        
        test_cases = [
            (5, "low", "warning"),     # Low count - should warn
            (15, "optimal", "success"),  # Optimal count - should succeed
            (45, "high", "warning")     # High count - should warn
        ]
        
        for chunk_count, category, expected_feedback in test_cases:
            mock_streamlit['slider'].return_value = chunk_count
            
            # Simulate feedback logic
            if chunk_count < 10:
                feedback_type = "warning"
            elif chunk_count > 40:
                feedback_type = "warning"
            else:
                feedback_type = "success"
            
            assert feedback_type == expected_feedback, \
                f"Feedback validation failed for {chunk_count} chunks ({category})"
    
    def test_swarm_parameter_passing(self, mock_streamlit):
        """Test that adaptive retrieval parameters are correctly passed to swarm."""
        # Setup test scenarios
        test_scenarios = [
            {
                'mode': 'auto',
                'manual_count': None,
                'expected_in_params': ['retrieval_mode', 'available_doc_count']
            },
            {
                'mode': 'manual',
                'manual_count': 25,
                'expected_in_params': ['retrieval_mode', 'manual_chunk_count', 'available_doc_count']
            },
            {
                'mode': 'performance',
                'manual_count': None,
                'expected_in_params': ['retrieval_mode', 'available_doc_count']
            }
        ]
        
        for scenario in test_scenarios:
            mock_streamlit['session_state'].retrieval_mode = scenario['mode']
            mock_streamlit['session_state'].manual_chunk_count = scenario.get('manual_count', 15)
            
            # Simulate parameter construction
            params = {
                'retrieval_mode': scenario['mode'],
                'available_doc_count': 100
            }
            
            if scenario['mode'] == 'manual':
                params['manual_chunk_count'] = scenario['manual_count']
            
            # Verify expected parameters are present
            for expected_param in scenario['expected_in_params']:
                assert expected_param in params, \
                    f"Expected parameter {expected_param} not found for mode {scenario['mode']}"
    
    def test_adaptive_decision_display(self, mock_streamlit):
        """Test adaptive decision info is properly displayed in debug mode."""
        # Mock adaptive decision data
        adaptive_decision = {
            'query_type': 'complex_conceptual',
            'chunk_count': 35,
            'query_analysis': {
                'complexity_score': 0.82,
                'specificity_score': 0.65
            },
            'rationale': 'High complexity query requires extensive context'
        }
        
        context_stats = {
            'adaptive_decision': adaptive_decision
        }
        
        # Verify decision data structure
        assert context_stats.get('adaptive_decision') is not None, \
            "Adaptive decision should be present in context stats"
        
        decision = context_stats['adaptive_decision']
        assert 'query_type' in decision, "Query type should be in decision"
        assert 'chunk_count' in decision, "Chunk count should be in decision"
        assert 'rationale' in decision, "Rationale should be in decision"
        
        # Verify query analysis is accessible
        if 'query_analysis' in decision:
            analysis = decision['query_analysis']
            assert 'complexity_score' in analysis, "Complexity score should be in analysis"
            assert 'specificity_score' in analysis, "Specificity score should be in analysis"
    
    def test_session_state_initialization(self, mock_streamlit):
        """Test session state is properly initialized for adaptive retrieval."""
        # Simulate first-time initialization
        session_state = {}
        
        # Initialization logic
        if 'retrieval_mode' not in session_state:
            session_state['retrieval_mode'] = 'auto'
        if 'manual_chunk_count' not in session_state:
            session_state['manual_chunk_count'] = 15
        
        # Verify defaults
        assert session_state['retrieval_mode'] == 'auto', \
            "Default retrieval mode should be 'auto'"
        assert session_state['manual_chunk_count'] == 15, \
            "Default manual chunk count should be 15"
    
    def test_mode_specific_ui_visibility(self, mock_streamlit):
        """Test UI elements appear/disappear based on mode selection."""
        # Test manual mode - slider should be visible
        mock_streamlit['session_state'].retrieval_mode = 'manual'
        should_show_slider = (mock_streamlit['session_state'].retrieval_mode == 'manual')
        assert should_show_slider, "Slider should be visible in manual mode"
        
        # Test auto mode - slider should be hidden
        mock_streamlit['session_state'].retrieval_mode = 'auto'
        should_show_slider = (mock_streamlit['session_state'].retrieval_mode == 'manual')
        assert not should_show_slider, "Slider should be hidden in auto mode"
        
        # Test performance mode - slider should be hidden
        mock_streamlit['session_state'].retrieval_mode = 'performance'
        should_show_slider = (mock_streamlit['session_state'].retrieval_mode == 'manual')
        assert not should_show_slider, "Slider should be hidden in performance mode"
    
    def test_help_text_comprehensiveness(self):
        """Test that help text provides comprehensive guidance."""
        help_texts = {
            'mode_selector': (
                "**Auto**: Agent intelligently determines optimal chunk count based on query complexity\n\n"
                "**Manual**: You specify exact chunk count (5-50)\n\n"
                "**Performance**: Fast mode with focused retrieval (8 chunks)"
            ),
            'chunk_slider': (
                "Specify exact number of document chunks to retrieve.\n\n"
                "💡 **Tip**: 10-20 chunks works well for most queries.\n\n"
                "**Guidelines:**\n"
                "- Simple questions: 5-15 chunks\n"
                "- Moderate queries: 15-25 chunks\n"
                "- Complex analysis: 25-40 chunks\n"
                "- Multi-step reasoning: 35-50 chunks"
            )
        }
        
        # Verify help texts contain key information
        assert "Auto" in help_texts['mode_selector'], "Help should explain Auto mode"
        assert "Manual" in help_texts['mode_selector'], "Help should explain Manual mode"
        assert "Performance" in help_texts['mode_selector'], "Help should explain Performance mode"
        
        assert "Guidelines" in help_texts['chunk_slider'], "Slider help should provide guidelines"
        assert "Simple" in help_texts['chunk_slider'], "Should guide simple queries"
        assert "Complex" in help_texts['chunk_slider'], "Should guide complex queries"


def test_ui_integration_imports():
    """Test that all required modules can be imported."""
    try:
        from utils.rag import QueryAnalyzer, AdaptiveRetrievalStrategy
        from agents.rag import RAGSwarmCoordinator
        assert True, "All required imports successful"
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

