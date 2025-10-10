#!/usr/bin/env python3
"""
Enhanced MCP Testing Interface
===============================

Comprehensive testing interface for MCP tools with:
- Advanced parameter configuration
- RAG integration testing
- Database tool testing
- Batch test execution
- Test result tracking and analytics
- Configuration presets

Created: 2025-10-10
Sprint: US-RAG-001 Phase 5
Purpose: Comprehensive MCP tool testing for agent swarms
"""

import streamlit as st
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import time

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# MCP imports
try:
    from utils.mcp.server import (
        MCPServer, ToolCategory, AccessLevel, ToolExecutionContext,
        create_mcp_server
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="Enhanced MCP Testing",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .test-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4CAF50;
        margin-bottom: 1rem;
    }
    .config-section {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .result-success {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .result-error {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Session State
# ============================================================================

def initialize_session_state():
    """Initialize session state for testing."""
    if 'mcp_server' not in st.session_state:
        st.session_state.mcp_server = None
    if 'test_history' not in st.session_state:
        st.session_state.test_history = []
    if 'test_presets' not in st.session_state:
        st.session_state.test_presets = load_test_presets()
    if 'batch_tests' not in st.session_state:
        st.session_state.batch_tests = []


def load_test_presets() -> Dict[str, Dict]:
    """Load predefined test configuration presets."""
    return {
        "Database Query - Recent Activities": {
            "tool_id": "db.query_agent_activities",
            "parameters": {
                "agent_id": "",
                "activity_type": "",
                "limit": 50
            },
            "description": "Query recent agent activities from all databases"
        },
        "RAG Semantic Search": {
            "tool_id": "rag.semantic_search",
            "parameters": {
                "query": "How to create a context-aware agent?",
                "limit": 10,
                "search_type": "semantic"
            },
            "description": "Test RAG semantic search with example query"
        },
        "Agile Story Update": {
            "tool_id": "agile.update_story_status",
            "parameters": {
                "story_id": "US-RAG-001",
                "new_status": "In Progress",
                "notes": "Testing agile automation"
            },
            "description": "Update user story status with automation"
        },
        "Link Validation": {
            "tool_id": "link.validate",
            "parameters": {},
            "description": "Validate all internal links in documentation"
        },
        "Database Schema": {
            "tool_id": "db.get_schema",
            "parameters": {
                "database_name": "agent_tracking"
            },
            "description": "Get agent tracking database schema"
        },
        "RAG Statistics": {
            "tool_id": "db.get_rag_statistics",
            "parameters": {},
            "description": "Get RAG system usage statistics"
        }
    }


# ============================================================================
# Enhanced Testing Interface
# ============================================================================

def enhanced_testing_page():
    """Main enhanced testing interface."""
    st.title("🧪 Enhanced MCP Testing Interface")
    
    if not MCP_AVAILABLE:
        st.error("❌ MCP system not available. Please check installation.")
        return
    
    # Initialize server
    if st.session_state.mcp_server is None:
        st.session_state.mcp_server = create_mcp_server(host="localhost", port=8005)
    
    server = st.session_state.mcp_server
    
    # Tabs for different testing modes
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Quick Test",
        "⚙️ Advanced Configuration",
        "📦 Batch Testing",
        "📊 Test Analytics",
        "💾 Test Presets"
    ])
    
    with tab1:
        quick_test_interface(server)
    
    with tab2:
        advanced_configuration_interface(server)
    
    with tab3:
        batch_testing_interface(server)
    
    with tab4:
        test_analytics_interface()
    
    with tab5:
        test_presets_interface(server)


# ============================================================================
# Quick Test Interface
# ============================================================================

def quick_test_interface(server: MCPServer):
    """Quick test interface with smart parameter detection."""
    st.header("🎯 Quick Tool Testing")
    
    st.markdown("""
    **Quick test any MCP tool with intelligent parameter detection and validation.**
    Perfect for rapid testing during development.
    """)
    
    # Tool selection with category grouping
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Category filter
        category_filter = st.selectbox(
            "Filter by Category",
            options=['All'] + [cat.value for cat in ToolCategory]
        )
    
    with col2:
        # Tool count display
        filtered_count = len([
            t for t in server.tool_registry.tools.values()
            if category_filter == 'All' or t.category.value == category_filter
        ])
        st.metric("Available Tools", filtered_count)
    
    # Tool selection
    tools = {
        f"{tool.name} | {tool.category.value}": tool_id
        for tool_id, tool in server.tool_registry.tools.items()
        if category_filter == 'All' or tool.category.value == category_filter
    }
    
    selected_display = st.selectbox(
        "Select Tool",
        options=sorted(tools.keys()),
        help="Choose a tool to test"
    )
    
    if selected_display:
        tool_id = tools[selected_display]
        tool = server.tool_registry.tools[tool_id]
        
        # Tool information card
        st.markdown(f"""
        <div class="test-card">
            <h4>🔧 {tool.name}</h4>
            <p><strong>Description:</strong> {tool.description}</p>
            <p><strong>Category:</strong> {tool.category.value} | 
               <strong>Access:</strong> {tool.access_level.value} |
               <strong>Timeout:</strong> {tool.execution_timeout}s</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Parameter input form
        with st.form("quick_test_form"):
            st.subheader("📝 Parameters")
            
            params = render_parameter_inputs(tool, "quick")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                execute = st.form_submit_button("▶️ Execute", use_container_width=True)
            with col2:
                validate = st.form_submit_button("✓ Validate", use_container_width=True)
            
            if validate:
                validation_result = validate_parameters(params, tool)
                if validation_result['valid']:
                    st.success("✅ Parameters are valid!")
                else:
                    st.error(f"❌ Validation errors: {', '.join(validation_result['errors'])}")
            
            if execute:
                execute_tool_test(server, tool_id, tool, params, "Quick Test")


# ============================================================================
# Advanced Configuration Interface
# ============================================================================

def advanced_configuration_interface(server: MCPServer):
    """Advanced testing with detailed configuration options."""
    st.header("⚙️ Advanced Configuration")
    
    st.markdown("""
    **Comprehensive testing with advanced configuration options:**
    - Execution context configuration
    - RAG integration settings
    - Database connection parameters
    - Performance monitoring
    - Error handling options
    """)
    
    # Tool selection
    tool_id = st.selectbox(
        "Select Tool",
        options=sorted(server.tool_registry.tools.keys()),
        format_func=lambda x: f"{server.tool_registry.tools[x].name} ({x})"
    )
    
    if tool_id:
        tool = server.tool_registry.tools[tool_id]
        
        # Advanced configuration sections
        with st.expander("🔧 Tool Parameters", expanded=True):
            params = render_parameter_inputs(tool, "advanced")
        
        with st.expander("⚙️ Execution Configuration"):
            col1, col2 = st.columns(2)
            
            with col1:
                timeout = st.number_input(
                    "Execution Timeout (seconds)",
                    min_value=1,
                    max_value=300,
                    value=tool.execution_timeout,
                    help="Maximum time to wait for tool execution"
                )
                
                retry_count = st.number_input(
                    "Retry Count",
                    min_value=0,
                    max_value=5,
                    value=0,
                    help="Number of retries on failure"
                )
            
            with col2:
                agent_id = st.text_input(
                    "Agent ID",
                    value="test_agent",
                    help="Agent identifier for this test"
                )
                
                access_override = st.selectbox(
                    "Access Level Override",
                    options=[None] + [level.value for level in AccessLevel],
                    help="Override access level for testing"
                )
        
        with st.expander("🧠 RAG Configuration"):
            rag_enabled = st.checkbox("Enable RAG Context", value=False)
            
            if rag_enabled:
                col1, col2 = st.columns(2)
                
                with col1:
                    rag_query = st.text_input(
                        "RAG Query",
                        help="Query for RAG context retrieval"
                    )
                    rag_limit = st.number_input(
                        "Results Limit",
                        min_value=1,
                        max_value=50,
                        value=10
                    )
                
                with col2:
                    rag_mode = st.selectbox(
                        "Retrieval Mode",
                        options=['semantic', 'keyword', 'hybrid'],
                        index=0
                    )
                    min_score = st.slider(
                        "Minimum Relevance Score",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.5,
                        step=0.05
                    )
        
        with st.expander("🗄️ Database Configuration"):
            db_enabled = st.checkbox("Enable Database Logging", value=True)
            
            if db_enabled:
                log_to_dbs = st.multiselect(
                    "Log to Databases",
                    options=["agent_tracking", "analytics", "test_results"],
                    default=["test_results"]
                )
        
        with st.expander("📊 Performance Monitoring"):
            enable_metrics = st.checkbox("Enable Performance Metrics", value=True)
            enable_tracing = st.checkbox("Enable Execution Tracing", value=False)
            enable_profiling = st.checkbox("Enable Memory Profiling", value=False)
        
        # Execute button
        if st.button("🚀 Execute with Advanced Configuration", use_container_width=True):
            with st.spinner("Executing with advanced configuration..."):
                # Build advanced context
                advanced_context = {
                    'timeout': timeout,
                    'retry_count': retry_count,
                    'agent_id': agent_id,
                    'rag_config': {
                        'enabled': rag_enabled,
                        'query': rag_query if rag_enabled else None,
                        'limit': rag_limit if rag_enabled else None,
                        'mode': rag_mode if rag_enabled else None,
                        'min_score': min_score if rag_enabled else None
                    },
                    'db_config': {
                        'enabled': db_enabled,
                        'log_to': log_to_dbs if db_enabled else []
                    },
                    'monitoring': {
                        'metrics': enable_metrics,
                        'tracing': enable_tracing,
                        'profiling': enable_profiling
                    }
                }
                
                execute_tool_test(server, tool_id, tool, params, "Advanced Test", advanced_context)


# ============================================================================
# Batch Testing Interface
# ============================================================================

def batch_testing_interface(server: MCPServer):
    """Batch testing interface for multiple tools."""
    st.header("📦 Batch Testing")
    
    st.markdown("""
    **Execute multiple tests in sequence or parallel:**
    - Test multiple tools with different parameters
    - Compare results across configurations
    - Export test results
    """)
    
    # Batch test builder
    st.subheader("➕ Add Tests to Batch")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tool_id = st.selectbox(
            "Tool to Test",
            options=sorted(server.tool_registry.tools.keys()),
            format_func=lambda x: server.tool_registry.tools[x].name,
            key="batch_tool_select"
        )
    
    with col2:
        if st.button("➕ Add to Batch"):
            tool = server.tool_registry.tools[tool_id]
            st.session_state.batch_tests.append({
                'tool_id': tool_id,
                'tool_name': tool.name,
                'parameters': {},
                'description': f"Test {tool.name}"
            })
            st.rerun()
    
    # Display batch tests
    if st.session_state.batch_tests:
        st.subheader(f"📋 Batch Queue ({len(st.session_state.batch_tests)} tests)")
        
        for idx, test in enumerate(st.session_state.batch_tests):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{idx+1}.** {test['tool_name']} - {test['description']}")
            
            with col2:
                if st.button("🗑️ Remove", key=f"remove_batch_{idx}"):
                    st.session_state.batch_tests.pop(idx)
                    st.rerun()
        
        # Execute batch
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("▶️ Execute Batch", use_container_width=True):
                execute_batch_tests(server, st.session_state.batch_tests)
        
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.batch_tests = []
                st.rerun()
    else:
        st.info("📭 No tests in batch queue. Add tests above to start building your batch.")


# ============================================================================
# Test Analytics Interface
# ============================================================================

def test_analytics_interface():
    """Test analytics and history."""
    st.header("📊 Test Analytics")
    
    if not st.session_state.test_history:
        st.info("📭 No test history yet. Run some tests to see analytics!")
        return
    
    # Summary metrics
    st.subheader("📈 Summary")
    
    total_tests = len(st.session_state.test_history)
    successful_tests = sum(1 for t in st.session_state.test_history if t.get('success', False))
    failed_tests = total_tests - successful_tests
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tests", total_tests)
    with col2:
        st.metric("Successful", successful_tests)
    with col3:
        st.metric("Failed", failed_tests)
    with col4:
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Test history
    st.subheader("📝 Test History")
    
    for idx, test in enumerate(reversed(st.session_state.test_history[-20:])):
        with st.expander(f"Test #{total_tests - idx}: {test.get('tool_name', 'Unknown')} - {test.get('timestamp', '')}"):
            if test.get('success', False):
                st.markdown('<div class="result-success">✅ <strong>Success</strong></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-error">❌ <strong>Failed</strong></div>', unsafe_allow_html=True)
            
            st.json({
                'tool_id': test.get('tool_id'),
                'parameters': test.get('parameters'),
                'execution_time': f"{test.get('execution_time', 0):.3f}s",
                'result': test.get('result')
            })


# ============================================================================
# Test Presets Interface
# ============================================================================

def test_presets_interface(server: MCPServer):
    """Predefined test configurations."""
    st.header("💾 Test Presets")
    
    st.markdown("""
    **Quick access to common test configurations:**
    - Pre-configured parameters for frequent tests
    - One-click execution
    - Customizable presets
    """)
    
    presets = st.session_state.test_presets
    
    for preset_name, preset_config in presets.items():
        with st.expander(f"📋 {preset_name}", expanded=False):
            st.markdown(f"**Description:** {preset_config['description']}")
            st.markdown(f"**Tool:** `{preset_config['tool_id']}`")
            
            # Show parameters
            if preset_config['parameters']:
                st.json(preset_config['parameters'])
            
            if st.button(f"▶️ Execute {preset_name}", key=f"preset_{preset_name}"):
                tool_id = preset_config['tool_id']
                if tool_id in server.tool_registry.tools:
                    tool = server.tool_registry.tools[tool_id]
                    execute_tool_test(
                        server,
                        tool_id,
                        tool,
                        preset_config['parameters'],
                        f"Preset: {preset_name}"
                    )
                else:
                    st.error(f"❌ Tool not found: {tool_id}")


# ============================================================================
# Helper Functions
# ============================================================================

def render_parameter_inputs(tool, prefix: str) -> Dict[str, Any]:
    """Render parameter input fields based on tool schema."""
    params = {}
    
    if not tool.parameters_schema or 'properties' not in tool.parameters_schema:
        st.info("ℹ️ This tool has no parameters")
        return params
    
    properties = tool.parameters_schema.get('properties', {})
    required = tool.parameters_schema.get('required', [])
    
    for param_name, param_schema in properties.items():
        param_type = param_schema.get('type', 'string')
        param_desc = param_schema.get('description', '')
        is_required = param_name in required
        
        label = f"{param_name} {'🔴' if is_required else '🟢'}"
        key = f"{prefix}_{param_name}"
        
        if param_type == 'string':
            params[param_name] = st.text_input(label, help=param_desc, key=key)
        elif param_type in ['integer', 'number']:
            params[param_name] = st.number_input(label, help=param_desc, key=key)
        elif param_type == 'boolean':
            params[param_name] = st.checkbox(label, help=param_desc, key=key)
        elif param_type == 'array':
            text_input = st.text_area(label, help=f"{param_desc} (JSON array)", key=key)
            if text_input:
                try:
                    params[param_name] = json.loads(text_input)
                except json.JSONDecodeError:
                    st.error(f"Invalid JSON for {param_name}")
        else:
            text_input = st.text_area(label, help=f"{param_desc} (JSON object)", key=key)
            if text_input:
                try:
                    params[param_name] = json.loads(text_input)
                except json.JSONDecodeError:
                    st.error(f"Invalid JSON for {param_name}")
    
    return params


def validate_parameters(params: Dict[str, Any], tool) -> Dict[str, Any]:
    """Validate parameters against tool schema."""
    errors = []
    required = tool.parameters_schema.get('required', [])
    
    # Check required parameters
    for req_param in required:
        if req_param not in params or not params[req_param]:
            errors.append(f"Missing required parameter: {req_param}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def execute_tool_test(
    server: MCPServer,
    tool_id: str,
    tool,
    params: Dict[str, Any],
    test_name: str,
    advanced_context: Optional[Dict] = None
):
    """Execute a tool test and display results."""
    start_time = time.time()
    
    try:
        # Create execution context
        context = ToolExecutionContext(
            request_id=f"test_{int(time.time())}",
            agent_id=advanced_context.get('agent_id', 'test_agent') if advanced_context else 'test_agent',
            tool_id=tool_id,
            parameters=params,
            timestamp=datetime.now(),
            access_level=tool.access_level
        )
        
        # Execute
        result = asyncio.run(server.execution_engine.execute_tool(context))
        execution_time = time.time() - start_time
        
        # Display result
        if result.success:
            st.markdown(f'<div class="result-success">✅ <strong>{test_name} Successful</strong></div>', unsafe_allow_html=True)
            st.json(result.result)
        else:
            st.markdown(f'<div class="result-error">❌ <strong>{test_name} Failed</strong><br>{result.error}</div>', unsafe_allow_html=True)
            if result.error_details:
                st.json(result.error_details)
        
        st.info(f"⏱️ Execution time: {execution_time:.3f}s")
        
        # Save to history
        st.session_state.test_history.append({
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name,
            'tool_id': tool_id,
            'tool_name': tool.name,
            'parameters': params,
            'success': result.success,
            'execution_time': execution_time,
            'result': result.result if result.success else result.error
        })
        
    except Exception as e:
        st.error(f"❌ Execution error: {e}")


def execute_batch_tests(server: MCPServer, batch_tests: List[Dict]):
    """Execute batch of tests."""
    st.subheader("🚀 Batch Execution Results")
    
    with st.spinner(f"Executing {len(batch_tests)} tests..."):
        for idx, test in enumerate(batch_tests):
            with st.expander(f"Test {idx+1}: {test['tool_name']}", expanded=True):
                tool_id = test['tool_id']
                tool = server.tool_registry.tools[tool_id]
                execute_tool_test(
                    server,
                    tool_id,
                    tool,
                    test.get('parameters', {}),
                    f"Batch Test {idx+1}"
                )


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main application entry point."""
    initialize_session_state()
    enhanced_testing_page()


if __name__ == "__main__":
    main()

