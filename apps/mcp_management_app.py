#!/usr/bin/env python3
"""
MCP Server Management UI
========================

Comprehensive Streamlit interface for managing Model Context Protocol (MCP) infrastructure.

Features:
- Tool Registry: Browse, search, filter, and test 47 MCP tools
- Prompt Database: Manage and test prompt templates
- Server Monitoring: Real-time server status and performance metrics
- Interactive Testing: Execute tools and test prompts with live results
- Security Management: View access levels and permissions

Author: AI Development Agent
Created: 2025-01-09
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import MCP components
from utils.mcp.server import (
    MCPServer, ToolCategory, AccessLevel, ToolExecutionContext,
    create_mcp_server
)

# Import prompt manager
try:
    from prompts.agent_prompt_loader import AgentPromptLoader
    PROMPT_MANAGER_AVAILABLE = True
except ImportError:
    PROMPT_MANAGER_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="MCP Management",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
    }
    .tool-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #e1f5fe;
        padding: 0.75rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ==================== Session State Initialization ====================

def initialize_session_state():
    """Initialize session state variables."""
    if 'mcp_server' not in st.session_state:
        st.session_state.mcp_server = None
    if 'mcp_client' not in st.session_state:
        st.session_state.mcp_client = None
    if 'prompt_loader' not in st.session_state and PROMPT_MANAGER_AVAILABLE:
        # Initialize with generic agent name for UI management
        st.session_state.prompt_loader = AgentPromptLoader(agent_name="mcp_ui")
    if 'tool_execution_history' not in st.session_state:
        st.session_state.tool_execution_history = []
    if 'prompt_test_history' not in st.session_state:
        st.session_state.prompt_test_history = []


# ==================== MCP Server Management ====================

def start_mcp_server():
    """Start or retrieve MCP server instance."""
    if st.session_state.mcp_server is None:
        st.session_state.mcp_server = create_mcp_server(host="localhost", port=8005)
    return st.session_state.mcp_server


def get_server_stats(server: MCPServer) -> Dict[str, Any]:
    """Get server statistics."""
    # Get execution metrics from execution engine
    execution_stats = getattr(server.execution_engine, 'execution_metrics', {})
    
    return {
        'total_tools': len(server.tool_registry.tools),
        'categories': len(set(tool.category for tool in server.tool_registry.tools.values())),
        'access_levels': {
            'public': len([t for t in server.tool_registry.tools.values() if t.access_level == AccessLevel.PUBLIC]),
            'restricted': len([t for t in server.tool_registry.tools.values() if t.access_level == AccessLevel.RESTRICTED]),
            'privileged': len([t for t in server.tool_registry.tools.values() if t.access_level == AccessLevel.PRIVILEGED])
        },
        'total_executions': execution_stats.get('total_executions', 0),
        'avg_execution_time': execution_stats.get('avg_execution_time', 0.0)
    }


# ==================== Tool Registry UI ====================

def tool_registry_page():
    """Tool Registry management interface."""
    st.header("🔧 Tool Registry")
    
    server = start_mcp_server()
    tools = server.tool_registry.tools
    
    # Tool Statistics
    st.subheader("📊 Tool Statistics")
    stats = get_server_stats(server)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tools", stats['total_tools'])
    with col2:
        st.metric("Categories", stats['categories'])
    with col3:
        st.metric("Public Tools", stats['access_levels']['public'])
    with col4:
        st.metric("Total Executions", stats['total_executions'])
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            options=['All'] + [cat.value for cat in ToolCategory],
            index=0
        )
    
    with col2:
        access_filter = st.selectbox(
            "Filter by Access Level",
            options=['All'] + [level.value for level in AccessLevel],
            index=0
        )
    
    with col3:
        search_query = st.text_input("🔍 Search tools", placeholder="Search by name or description...")
    
    # Filter tools
    filtered_tools = []
    for tool_id, tool_def in tools.items():
        # Category filter
        if category_filter != 'All' and tool_def.category.value != category_filter:
            continue
        
        # Access level filter
        if access_filter != 'All' and tool_def.access_level.value != access_filter:
            continue
        
        # Search filter
        if search_query:
            search_lower = search_query.lower()
            if not (search_lower in tool_def.name.lower() or search_lower in tool_def.description.lower()):
                continue
        
        filtered_tools.append((tool_id, tool_def))
    
    st.markdown(f"**Showing {len(filtered_tools)} of {len(tools)} tools**")
    
    # Display tools in expandable cards
    for tool_id, tool_def in sorted(filtered_tools, key=lambda x: x[1].name):
        with st.expander(f"🔨 {tool_def.name} ({tool_def.category.value})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {tool_def.description}")
                st.markdown(f"**Tool ID:** `{tool_id}`")
                st.markdown(f"**Source:** `{tool_def.source_module}.{tool_def.function_name}`")
                
                # Parameters
                if tool_def.parameters_schema:
                    st.markdown("**Parameters:**")
                    for param_name, param_schema in tool_def.parameters_schema.get('properties', {}).items():
                        param_type = param_schema.get('type', 'any')
                        param_desc = param_schema.get('description', 'No description')
                        required = param_name in tool_def.parameters_schema.get('required', [])
                        req_badge = "🔴 Required" if required else "🟢 Optional"
                        st.markdown(f"- `{param_name}` ({param_type}) - {req_badge}: {param_desc}")
            
            with col2:
                # Metadata badges
                st.markdown(f"**Category:**")
                st.info(tool_def.category.value)
                
                st.markdown(f"**Access Level:**")
                if tool_def.access_level == AccessLevel.PUBLIC:
                    st.success(tool_def.access_level.value)
                elif tool_def.access_level == AccessLevel.RESTRICTED:
                    st.warning(tool_def.access_level.value)
                else:
                    st.error(tool_def.access_level.value)
                
                st.markdown(f"**Timeout:**")
                st.info(f"{tool_def.execution_timeout}s")
                
                if tool_def.requires_confirmation:
                    st.warning("⚠️ Requires confirmation")
            
            # Test button
            if st.button(f"🧪 Test Tool", key=f"test_{tool_id}"):
                st.session_state[f"testing_tool_{tool_id}"] = True
                st.rerun()
            
            # Tool testing interface
            if st.session_state.get(f"testing_tool_{tool_id}", False):
                st.markdown("---")
                st.markdown("### 🧪 Tool Testing")
                
                with st.form(key=f"test_form_{tool_id}"):
                    st.markdown("**Enter parameters:**")
                    
                    params = {}
                    for param_name, param_schema in tool_def.parameters_schema.get('properties', {}).items():
                        param_type = param_schema.get('type', 'string')
                        param_desc = param_schema.get('description', '')
                        
                        if param_type == 'string':
                            params[param_name] = st.text_input(
                                param_name,
                                help=param_desc,
                                key=f"param_{tool_id}_{param_name}"
                            )
                        elif param_type in ['integer', 'number']:
                            params[param_name] = st.number_input(
                                param_name,
                                help=param_desc,
                                key=f"param_{tool_id}_{param_name}"
                            )
                        elif param_type == 'boolean':
                            params[param_name] = st.checkbox(
                                param_name,
                                help=param_desc,
                                key=f"param_{tool_id}_{param_name}"
                            )
                        else:
                            params[param_name] = st.text_area(
                                param_name,
                                help=f"{param_desc} (JSON format)",
                                key=f"param_{tool_id}_{param_name}"
                            )
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        execute_button = st.form_submit_button("▶️ Execute")
                    with col2:
                        cancel_button = st.form_submit_button("❌ Cancel")
                    
                    if cancel_button:
                        st.session_state[f"testing_tool_{tool_id}"] = False
                        st.rerun()
                    
                    if execute_button:
                        with st.spinner("Executing tool..."):
                            try:
                                # Create execution context
                                context = ToolExecutionContext(
                                    request_id=f"test_{int(time.time())}",
                                    agent_id="mcp_ui_test",
                                    tool_id=tool_id,
                                    parameters=params,
                                    timestamp=datetime.now(),
                                    access_level=tool_def.access_level
                                )
                                
                                # Execute tool
                                result = asyncio.run(server.execution_engine.execute_tool(context))
                                
                                # Store in history
                                st.session_state.tool_execution_history.append({
                                    'timestamp': datetime.now().isoformat(),
                                    'tool_id': tool_id,
                                    'tool_name': tool_def.name,
                                    'parameters': params,
                                    'result': result
                                })
                                
                                # Display result
                                if result.success:
                                    st.success("✅ Tool executed successfully!")
                                    st.json(result.result)
                                else:
                                    st.error(f"❌ Tool execution failed: {result.error}")
                                    if result.error_details:
                                        st.json(result.error_details)
                                
                                # Execution metrics
                                st.info(f"⏱️ Execution time: {result.execution_time:.3f}s")
                                
                            except Exception as e:
                                st.error(f"❌ Execution error: {e}")


# ==================== Prompt Database UI ====================

def prompt_database_page():
    """Prompt Database management interface."""
    st.header("💬 Prompt Database")
    
    if not PROMPT_MANAGER_AVAILABLE:
        st.error("❌ Prompt Manager not available")
        return
    
    # Access the underlying prompt manager directly
    prompt_manager = st.session_state.prompt_loader.prompt_manager
    
    # Prompt Statistics
    st.subheader("📊 Prompt Statistics")
    
    try:
        # Get all prompts from the database
        all_prompts = prompt_manager.get_all_prompts()
        
        # Define available agent types (from AgentPromptLoader defaults)
        agent_types = [
            'requirements_analyst',
            'architecture_designer',
            'code_generator',
            'test_generator',
            'code_reviewer',
            'security_analyst',
            'documentation_generator',
            'project_manager'
        ]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Prompts", len(all_prompts) if all_prompts else len(agent_types))
        with col2:
            st.metric("Agent Types", len(agent_types))
        with col3:
            st.metric("DB Prompts", len(all_prompts) if all_prompts else 0)
        
        st.markdown("---")
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            agent_type_filter = st.selectbox(
                "Filter by Agent Type",
                options=['All'] + sorted(agent_types),
                index=0
            )
        
        with col2:
            search_query = st.text_input("🔍 Search prompts", placeholder="Search by agent name...")
        
        # Filter agent types
        filtered_agents = []
        for agent_type in agent_types:
            # Agent type filter
            if agent_type_filter != 'All' and agent_type != agent_type_filter:
                continue
            
            # Search filter
            if search_query:
                search_lower = search_query.lower()
                if not (search_lower in agent_type.lower()):
                    continue
            
            filtered_agents.append(agent_type)
        
        st.markdown(f"**Showing {len(filtered_agents)} of {len(agent_types)} agent prompts**")
        
        # Display prompts
        for agent_type in sorted(filtered_agents):
            # Load the default prompt for this agent
            loader = AgentPromptLoader(agent_type)
            prompt_content = loader.get_default_prompt()
            
            with st.expander(f"💬 {agent_type.replace('_', ' ').title()} Agent"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Agent Type:** `{agent_type}`")
                    st.markdown(f"**Source:** Default system prompt")
                    
                    # Show prompt content
                    if st.button("📄 Show Prompt Content", key=f"show_{agent_type}"):
                        st.session_state[f"show_prompt_{agent_type}"] = not st.session_state.get(f"show_prompt_{agent_type}", False)
                        st.rerun()
                    
                    if st.session_state.get(f"show_prompt_{agent_type}", False):
                        # Get line count for display
                        line_count = len(prompt_content.split('\n'))
                        st.markdown(f"**Lines:** {line_count}")
                        st.code(prompt_content, language='markdown', line_numbers=True)
                
                with col2:
                    # Metadata
                    st.markdown(f"**Type:**")
                    st.info("System")
                    
                    st.markdown(f"**Status:**")
                    st.success("✅ Active")
                    
                    st.markdown(f"**Lines:**")
                    st.info(f"{len(prompt_content.split(chr(10)))}")
    
    except Exception as e:
        st.error(f"❌ Error loading prompts: {e}")


# ==================== Server Monitoring UI ====================

def server_monitoring_page():
    """Server monitoring and performance interface."""
    st.header("📊 Server Monitoring")
    
    server = start_mcp_server()
    stats = get_server_stats(server)
    
    # Real-time metrics
    st.subheader("⏱️ Real-time Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tools", stats['total_tools'])
    with col2:
        st.metric("Total Executions", stats['total_executions'])
    with col3:
        st.metric("Avg Execution Time", f"{stats['avg_execution_time']:.3f}s")
    with col4:
        st.metric("Server Status", "🟢 Running")
    
    st.markdown("---")
    
    # Access level distribution
    st.subheader("🔒 Access Level Distribution")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Public", stats['access_levels']['public'])
    with col2:
        st.metric("Restricted", stats['access_levels']['restricted'])
    with col3:
        st.metric("Privileged", stats['access_levels']['privileged'])
    
    st.markdown("---")
    
    # Tool category breakdown
    st.subheader("📁 Tool Categories")
    
    category_stats = {}
    for tool_def in server.tool_registry.tools.values():
        cat = tool_def.category.value
        if cat not in category_stats:
            category_stats[cat] = 0
        category_stats[cat] += 1
    
    cols = st.columns(len(category_stats))
    for idx, (category, count) in enumerate(sorted(category_stats.items())):
        with cols[idx]:
            st.metric(category.capitalize(), count)
    
    st.markdown("---")
    
    # Execution history
    st.subheader("📜 Recent Tool Executions")
    
    if st.session_state.tool_execution_history:
        for idx, execution in enumerate(reversed(st.session_state.tool_execution_history[-10:])):
            with st.expander(f"🔨 {execution['tool_name']} - {execution['timestamp']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Parameters:**")
                    st.json(execution['parameters'])
                
                with col2:
                    st.markdown("**Result:**")
                    result = execution['result']
                    if result.success:
                        st.success("✅ Success")
                        st.json(result.result)
                    else:
                        st.error(f"❌ Failed: {result.error}")
    else:
        st.info("No tool executions yet. Test a tool in the Tool Registry tab.")


# ==================== Testing Interface ====================

def testing_interface_page():
    """Enhanced interactive testing interface for tools and prompts."""
    st.header("🧪 Enhanced Testing Interface")
    
    # Add test presets at the top
    if 'test_presets' not in st.session_state:
        st.session_state.test_presets = load_test_presets()
    if 'batch_tests' not in st.session_state:
        st.session_state.batch_tests = []
    
    # Main tabs with enhanced features
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Quick Test",
        "💬 Prompt Testing",
        "⚙️ Advanced Config",
        "📦 Batch Testing",
        "📊 Test Analytics"
    ])
    
    with tab1:
        quick_tool_testing_tab()
    
    with tab2:
        prompt_testing_tab()
    
    with tab3:
        advanced_configuration_tab()
    
    with tab4:
        batch_testing_tab()
    
    with tab5:
        test_analytics_tab()


def load_test_presets():
    """Load predefined test configuration presets."""
    return {
        "Database Query - Recent Activities": {
            "tool_id": "db.query_agent_activities",
            "parameters": {"agent_id": "", "activity_type": "", "limit": 50},
            "description": "Query recent agent activities"
        },
        "RAG Semantic Search": {
            "tool_id": "rag.semantic_search",
            "parameters": {"query": "How to create a context-aware agent?", "limit": 10},
            "description": "Test RAG semantic search"
        },
        "Database Schema": {
            "tool_id": "db.get_schema",
            "parameters": {"database_name": "agent_tracking"},
            "description": "Get database schema"
        },
        "RAG Statistics": {
            "tool_id": "db.get_rag_statistics",
            "parameters": {},
            "description": "Get RAG usage statistics"
        },
        "Link Validation": {
            "tool_id": "link.validate",
            "parameters": {},
            "description": "Validate all documentation links"
        }
    }


def quick_tool_testing_tab():
    """Quick test interface with smart parameter detection."""
    st.subheader("🎯 Quick Tool Testing")
    
    server = start_mcp_server()
    tools = server.tool_registry.tools
    
    # Test presets quick access
    with st.expander("💾 Quick Presets", expanded=False):
        st.markdown("**One-click test configurations:**")
        
        cols = st.columns(3)
        for idx, (preset_name, preset_config) in enumerate(st.session_state.test_presets.items()):
            with cols[idx % 3]:
                if st.button(f"▶️ {preset_name}", key=f"preset_quick_{idx}", use_container_width=True):
                    tool_id = preset_config['tool_id']
                    if tool_id in tools:
                        execute_preset_test(server, preset_config, preset_name)
                    else:
                        st.warning(f"Tool not found: {tool_id}")
    
    st.markdown("---")
    
    # Category filter
    col1, col2 = st.columns([3, 1])
    
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            options=['All'] + [cat.value for cat in ToolCategory]
        )
    
    with col2:
        filtered_count = len([
            t for t in tools.values()
            if category_filter == 'All' or t.category.value == category_filter
        ])
        st.metric("Tools", filtered_count)
    
    # Tool selection with better formatting
    tool_options = {
        f"{tool_def.name} | {tool_def.category.value}": tool_id 
        for tool_id, tool_def in tools.items()
        if category_filter == 'All' or tool_def.category.value == category_filter
    }
    
    selected_tool_display = st.selectbox(
        "Select Tool to Test",
        options=sorted(tool_options.keys()),
        help="Choose a tool to test with custom parameters"
    )
    
    if selected_tool_display:
        tool_id = tool_options[selected_tool_display]
        tool_def = tools[tool_id]
        
        # Tool info card with better formatting
        st.markdown("#### 🔧 Tool Information")
        st.info(f"**{tool_def.name}**")
        st.markdown(f"**Description:** {tool_def.description}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Category", tool_def.category.value)
        with col2:
            st.metric("Access", tool_def.access_level.value)
        with col3:
            st.metric("Timeout", f"{tool_def.execution_timeout}s")
        
        st.markdown("---")
        
        # Parameter input form
        with st.form(key="quick_test_form"):
            st.markdown("### 📝 Parameters")
            
            params = render_parameter_inputs(tool_def, "quick")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                execute_button = st.form_submit_button("▶️ Execute", use_container_width=True)
            with col2:
                validate_button = st.form_submit_button("✓ Validate", use_container_width=True)
            
            if validate_button:
                validation_result = validate_parameters(params, tool_def)
                if validation_result['valid']:
                    st.success("✅ Parameters are valid!")
                else:
                    st.error(f"❌ Validation errors: {', '.join(validation_result['errors'])}")
            
            if execute_button:
                    with st.spinner("Executing tool..."):
                        try:
                            # Create execution context
                            context = ToolExecutionContext(
                                request_id=f"quick_test_{int(time.time())}",
                                agent_id="mcp_ui_quick_test",
                                tool_id=tool_id,
                                parameters=params,
                                timestamp=datetime.now(),
                                access_level=tool_def.access_level
                            )
                            
                            # Execute tool
                            result = asyncio.run(server.execution_engine.execute_tool(context))
                            
                            if result.success:
                                st.success("✅ Tool executed successfully!")
                                st.json(result.result)
                                st.info(f"⏱️ Execution time: {result.execution_time:.3f}s")
                            else:
                                st.error(f"❌ Tool execution failed: {result.error}")
                                if result.error_details:
                                    st.json(result.error_details)
                        
                        except Exception as e:
                            st.error(f"❌ Execution error: {e}")
        
        if not PROMPT_MANAGER_AVAILABLE:
            st.error("❌ Prompt Manager not available")
            return
        
        try:
            # Define available agent types
            agent_types = [
                'requirements_analyst',
                'architecture_designer',
                'code_generator',
                'test_generator',
                'code_reviewer',
                'security_analyst',
                'documentation_generator',
                'project_manager'
            ]
            
            # Agent selection
            agent_options = {agent_type.replace('_', ' ').title(): agent_type for agent_type in agent_types}
            
            selected_agent_display = st.selectbox(
                "Select an agent to view prompt",
                options=sorted(agent_options.keys())
            )
            
            if selected_agent_display:
                agent_type = agent_options[selected_agent_display]
                
                # Load the prompt for this agent
                loader = AgentPromptLoader(agent_type)
                prompt_content = loader.get_default_prompt()
                
                st.info(f"**Agent Type:** {agent_type}")
                st.info(f"**Lines:** {len(prompt_content.split(chr(10)))}")
                
                # Display prompt
                with st.form(key="quick_prompt_test_form"):
                    st.markdown("**System Prompt:**")
                    st.code(prompt_content, language='markdown', line_numbers=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        copy_button = st.form_submit_button("📋 Copy to Clipboard")
                    with col2:
                        close_button = st.form_submit_button("❌ Close")
                    
                    if copy_button:
                        st.success("✅ Prompt ready to copy (use browser copy function)")
                    if close_button:
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error loading prompts: {e}")


# ==================== Helper Functions for Enhanced Testing ====================

def render_parameter_inputs(tool_def, prefix: str) -> Dict[str, Any]:
    """Render parameter input fields directly from MCP server's parameter schema."""
    params = {}
    
    if not tool_def.parameters_schema:
        st.info("ℹ️ This tool has no parameters")
        return params
    
    # Direct representation of MCP server's schema: {"param": {"type": "...", "required": bool, "default": ...}}
    for param_name, param_schema in tool_def.parameters_schema.items():
        param_type = param_schema.get('type', 'string')
        param_desc = param_schema.get('description', '')
        is_required = param_schema.get('required', False)
        default_value = param_schema.get('default')
        enum_values = param_schema.get('enum')
        
        label = f"{param_name} {'🔴' if is_required else '🟢'}"
        key = f"{prefix}_{param_name}"
        
        # Render based on MCP server's type definition
        if enum_values:
            # Enum type from MCP server
            params[param_name] = st.selectbox(label, options=enum_values, help=param_desc, key=key)
        elif param_type == 'string':
            params[param_name] = st.text_input(label, value=default_value if default_value else "", help=param_desc, key=key)
        elif param_type in ['integer', 'number']:
            params[param_name] = st.number_input(label, value=default_value if default_value is not None else 0, help=param_desc, key=key)
        elif param_type == 'boolean':
            params[param_name] = st.checkbox(label, value=default_value if default_value is not None else False, help=param_desc, key=key)
        elif param_type == 'array':
            text_input = st.text_area(label, help=f"{param_desc} (JSON array)", key=key)
            if text_input:
                try:
                    params[param_name] = json.loads(text_input)
                except json.JSONDecodeError:
                    st.error(f"Invalid JSON for {param_name}")
        else:
            text_input = st.text_area(label, help=f"{param_desc} (JSON)", key=key)
            if text_input:
                try:
                    params[param_name] = json.loads(text_input)
                except json.JSONDecodeError:
                    st.error(f"Invalid JSON for {param_name}")
    
    return params


def validate_parameters(params: Dict[str, Any], tool_def) -> Dict[str, Any]:
    """Validate parameters against MCP server's parameter schema."""
    errors = []
    
    # Check required parameters directly from MCP server's schema
    for param_name, param_schema in tool_def.parameters_schema.items():
        is_required = param_schema.get('required', False)
        if is_required and (param_name not in params or not params[param_name]):
            errors.append(f"Missing required parameter: {param_name}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def execute_preset_test(server: MCPServer, preset_config: Dict, preset_name: str):
    """Execute a preset test configuration."""
    tool_id = preset_config['tool_id']
    tool = server.tool_registry.tools[tool_id]
    params = preset_config['parameters']
    
    with st.spinner(f"Executing {preset_name}..."):
        execute_tool_test(server, tool_id, tool, params, preset_name)


def execute_tool_test(server: MCPServer, tool_id: str, tool, params: Dict[str, Any], test_name: str):
    """Execute a tool test and display results."""
    start_time = time.time()
    
    try:
        # Create execution context
        context = ToolExecutionContext(
            request_id=f"test_{int(time.time())}",
            agent_id="mcp_ui_test",
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
            st.success(f"✅ {test_name} - Success!")
            st.json(result.result)
        else:
            st.error(f"❌ {test_name} - Failed: {result.error}")
            if result.error_details:
                st.json(result.error_details)
        
        st.info(f"⏱️ Execution time: {execution_time:.3f}s")
        
        # Save to history
        st.session_state.tool_execution_history.append({
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


def prompt_testing_tab():
    """Prompt testing tab for viewing agent prompts."""
    st.subheader("💬 Prompt Testing")
    
    if not PROMPT_MANAGER_AVAILABLE:
        st.error("❌ Prompt Manager not available")
        return
    
    try:
        # Define available agent types
        agent_types = [
            'requirements_analyst',
            'architecture_designer',
            'code_generator',
            'test_generator',
            'code_reviewer',
            'security_analyst',
            'documentation_generator',
            'project_manager'
        ]
        
        # Agent selection
        agent_options = {agent_type.replace('_', ' ').title(): agent_type for agent_type in agent_types}
        
        selected_agent_display = st.selectbox(
            "Select an agent to view prompt",
            options=sorted(agent_options.keys())
        )
        
        if selected_agent_display:
            agent_type = agent_options[selected_agent_display]
            
            # Load the prompt for this agent
            loader = AgentPromptLoader(agent_type)
            prompt_content = loader.get_default_prompt()
            
            st.info(f"**Agent Type:** {agent_type}")
            st.info(f"**Lines:** {len(prompt_content.split(chr(10)))}")
            
            # Display prompt
            with st.form(key="quick_prompt_test_form"):
                st.markdown("**System Prompt:**")
                st.code(prompt_content, language='markdown', line_numbers=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    copy_button = st.form_submit_button("📋 Copy to Clipboard")
                with col2:
                    close_button = st.form_submit_button("❌ Close")
                
                if copy_button:
                    st.success("✅ Prompt ready to copy (use browser copy function)")
                if close_button:
                    st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error loading prompts: {e}")


def advanced_configuration_tab():
    """Advanced configuration tab (placeholder for now)."""
    st.subheader("⚙️ Advanced Configuration")
    st.info("🚧 Advanced configuration coming soon! Will include RAG settings, database logging, and performance monitoring.")


def batch_testing_tab():
    """Batch testing tab (placeholder for now)."""
    st.subheader("📦 Batch Testing")
    st.info("🚧 Batch testing coming soon! Will allow testing multiple tools in sequence.")


def test_analytics_tab():
    """Test analytics tab."""
    st.subheader("📊 Test Analytics")
    
    if not st.session_state.tool_execution_history:
        st.info("📭 No test history yet. Run some tests to see analytics!")
        return
    
    # Summary metrics
    total_tests = len(st.session_state.tool_execution_history)
    successful_tests = sum(1 for t in st.session_state.tool_execution_history if t.get('success', False))
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
    st.markdown("### 📝 Recent Tests")
    
    for idx, test in enumerate(reversed(st.session_state.tool_execution_history[-10:])):
        status = "✅" if test.get('success', False) else "❌"
        with st.expander(f"{status} {test.get('tool_name', 'Unknown')} - {test.get('timestamp', '')}"):
            st.json({
                'test_name': test.get('test_name'),
                'tool_id': test.get('tool_id'),
                'parameters': test.get('parameters'),
                'execution_time': f"{test.get('execution_time', 0):.3f}s",
                'result': test.get('result')
            })


# ==================== Main Application ====================

def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80?text=MCP+Management", use_container_width=True)
        st.title("MCP Management")
        st.markdown("---")
        
        # Navigation
        st.subheader("📋 Navigation")
        page = st.radio(
            "Select a page:",
            options=[
                "Tool Registry",
                "Prompt Database",
                "Server Monitoring",
                "Testing Interface"
            ],
            index=0
        )
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("⚡ Quick Stats")
        if st.session_state.mcp_server:
            stats = get_server_stats(st.session_state.mcp_server)
            st.metric("Tools", stats['total_tools'])
            st.metric("Executions", len(st.session_state.tool_execution_history))
        else:
            st.info("Server not started")
        
        st.markdown("---")
        st.caption("© 2025 AI Dev Agent")
    
    # Main content
    if page == "Tool Registry":
        tool_registry_page()
    elif page == "Prompt Database":
        prompt_database_page()
    elif page == "Server Monitoring":
        server_monitoring_page()
    elif page == "Testing Interface":
        testing_interface_page()


if __name__ == "__main__":
    main()

