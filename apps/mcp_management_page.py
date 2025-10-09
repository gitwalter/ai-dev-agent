#!/usr/bin/env python3
"""
MCP Server Management UI
========================

Streamlit interface for managing MCP tools, prompts, and testing.

Features:
- Tool Registry Browser (47 tools across 6 categories)
- Prompt Database Manager
- Interactive Tool Testing
- Performance Monitoring
- Security Access Control

Author: AI Development Agent
Created: 2025-01-09
Purpose: US-RAG-001 Phase 4 - MCP Management UI
"""

import streamlit as st
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# MCP imports
try:
    from utils.mcp.server import MCPServer, ToolCategory, AccessLevel
    from utils.prompt_management.prompt_manager import PromptManager
    from utils.prompt_management.prompt_template_system import PromptTemplateSystem, TemplateType
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


def mcp_tool_registry_page():
    """Tool Registry Browser - View and manage 47 MCP tools."""
    st.markdown("### 🛠️ Tool Registry")
    
    if not MCP_AVAILABLE:
        st.error("MCP system not available. Please check installation.")
        return
    
    # Initialize MCP server
    if 'mcp_server' not in st.session_state:
        st.session_state.mcp_server = MCPServer()
    
    server = st.session_state.mcp_server
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_tools = len(server.tool_registry.tools)
    categories = len(set(tool.category for tool in server.tool_registry.tools.values()))
    
    with col1:
        st.metric("Total Tools", total_tools)
    with col2:
        st.metric("Categories", categories)
    with col3:
        st.metric("Public Tools", sum(1 for t in server.tool_registry.tools.values() if t.access_level == AccessLevel.PUBLIC))
    with col4:
        st.metric("Privileged Tools", sum(1 for t in server.tool_registry.tools.values() if t.access_level == AccessLevel.PRIVILEGED))
    
    st.markdown("---")
    
    # Filter controls
    col1, col2 = st.columns(2)
    
    with col1:
        # Category filter
        category_options = ["All"] + [cat.value for cat in ToolCategory]
        selected_category = st.selectbox("Filter by Category", category_options)
    
    with col2:
        # Access level filter
        access_options = ["All"] + [level.value for level in AccessLevel]
        selected_access = st.selectbox("Filter by Access Level", access_options)
    
    # Search
    search_query = st.text_input("🔍 Search Tools", placeholder="Search by name or description...")
    
    # Get filtered tools
    filtered_tools = []
    for tool in server.tool_registry.tools.values():
        # Category filter
        if selected_category != "All" and tool.category.value != selected_category:
            continue
        
        # Access level filter
        if selected_access != "All" and tool.access_level.value != selected_access:
            continue
        
        # Search filter
        if search_query:
            search_lower = search_query.lower()
            if search_lower not in tool.name.lower() and search_lower not in tool.description.lower():
                continue
        
        filtered_tools.append(tool)
    
    st.markdown(f"**Showing {len(filtered_tools)} tools**")
    
    # Display tools grouped by category
    if filtered_tools:
        for category in ToolCategory:
            category_tools = [t for t in filtered_tools if t.category == category]
            
            if category_tools:
                with st.expander(f"📦 {category.value.upper()} ({len(category_tools)} tools)", expanded=False):
                    for tool in category_tools:
                        st.markdown(f"#### `{tool.name}`")
                        st.markdown(f"**Description**: {tool.description}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            access_emoji = {"public": "🟢", "restricted": "🟡", "privileged": "🔴"}
                            st.markdown(f"**Access**: {access_emoji.get(tool.access_level.value, '⚪')} {tool.access_level.value}")
                        with col2:
                            st.markdown(f"**Module**: `{tool.source_module}`")
                        with col3:
                            st.markdown(f"**Timeout**: {tool.execution_timeout}s")
                        
                        # Parameters
                        with st.expander("📋 Parameters Schema"):
                            st.json(tool.parameters_schema)
                        
                        # Returns
                        with st.expander("📤 Returns Schema"):
                            st.json(tool.returns_schema)
                        
                        st.markdown("---")


def mcp_prompt_database_page():
    """Prompt Database Manager - View and manage prompts."""
    st.markdown("### 📝 Prompt Database")
    
    # Initialize prompt manager
    if 'prompt_manager' not in st.session_state:
        st.session_state.prompt_manager = PromptManager()
    
    if 'prompt_template_system' not in st.session_state:
        st.session_state.prompt_template_system = PromptTemplateSystem()
    
    pm = st.session_state.prompt_manager
    pts = st.session_state.prompt_template_system
    
    # Tabs for different prompt management functions
    tab1, tab2, tab3 = st.tabs(["📚 Browse Templates", "➕ Create Template", "📊 Performance"])
    
    with tab1:
        st.markdown("#### Prompt Templates")
        
        # List all templates
        templates = pts.templates
        
        if templates:
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.metric("Total Templates", len(templates))
                
                # Agent type filter
                agent_types = sorted(set(t.agent_type for t in templates.values()))
                selected_agent = st.selectbox("Filter by Agent", ["All"] + agent_types)
            
            with col2:
                # Display templates
                filtered_templates = [
                    t for t in templates.values()
                    if selected_agent == "All" or t.agent_type == selected_agent
                ]
                
                for template in filtered_templates:
                    with st.expander(f"📄 {template.name} ({template.agent_type})"):
                        st.markdown(f"**Description**: {template.description}")
                        st.markdown(f"**Type**: {template.template_type.value}")
                        st.markdown(f"**Status**: {template.status.value}")
                        st.markdown(f"**Version**: {template.version}")
                        st.markdown(f"**Author**: {template.author}")
                        st.markdown(f"**Tags**: {', '.join(template.tags)}")
                        
                        st.markdown("**Template Text:**")
                        st.code(template.template_text, language="text")
                        
                        # Edit button
                        if st.button(f"✏️ Edit", key=f"edit_{template.template_id}"):
                            st.session_state.editing_template = template.template_id
                            st.rerun()
        else:
            st.info("No prompt templates found. Create your first template!")
    
    with tab2:
        st.markdown("#### Create New Prompt Template")
        
        with st.form("create_template_form"):
            name = st.text_input("Template Name", placeholder="e.g., Query Analysis Prompt")
            description = st.text_area("Description", placeholder="What does this template do?")
            
            col1, col2 = st.columns(2)
            with col1:
                template_type = st.selectbox("Template Type", [t.value for t in TemplateType])
                agent_type = st.text_input("Agent Type", placeholder="e.g., rag_specialist")
            
            with col2:
                author = st.text_input("Author", value="AI Development Agent")
                tags = st.text_input("Tags (comma-separated)", placeholder="e.g., rag, query, analysis")
            
            template_text = st.text_area(
                "Template Text",
                height=300,
                placeholder="Enter your prompt template here..."
            )
            
            submitted = st.form_submit_button("💾 Create Template")
            
            if submitted:
                if name and description and template_text:
                    try:
                        template_id = pts.create_template(
                            name=name,
                            description=description,
                            template_type=TemplateType(template_type),
                            agent_type=agent_type,
                            template_text=template_text,
                            author=author,
                            tags=[t.strip() for t in tags.split(",")] if tags else []
                        )
                        st.success(f"✅ Template created: {template_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to create template: {e}")
                else:
                    st.warning("⚠️ Please fill in all required fields")
    
    with tab3:
        st.markdown("#### Prompt Performance Metrics")
        st.info("📊 Performance tracking coming soon - will show execution stats, success rates, and optimization suggestions")


def mcp_tool_testing_page():
    """Interactive Tool Testing - Test MCP tools with custom inputs."""
    st.markdown("### 🧪 Tool Testing")
    
    if not MCP_AVAILABLE:
        st.error("MCP system not available.")
        return
    
    # Initialize MCP server
    if 'mcp_server' not in st.session_state:
        st.session_state.mcp_server = MCPServer()
    
    server = st.session_state.mcp_server
    
    # Tool selection
    tool_names = sorted(server.tool_registry.tools.keys())
    selected_tool_id = st.selectbox("Select Tool to Test", tool_names)
    
    if selected_tool_id:
        tool = server.tool_registry.tools[selected_tool_id]
        
        # Tool info
        st.markdown(f"#### `{tool.name}`")
        st.markdown(f"**Description**: {tool.description}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            access_emoji = {"public": "🟢", "restricted": "🟡", "privileged": "🔴"}
            st.markdown(f"**Access**: {access_emoji.get(tool.access_level.value, '⚪')} {tool.access_level.value}")
        with col2:
            st.markdown(f"**Category**: {tool.category.value}")
        with col3:
            st.markdown(f"**Timeout**: {tool.execution_timeout}s")
        
        st.markdown("---")
        
        # Parameters input
        st.markdown("#### Input Parameters")
        
        # Generate input form based on parameters schema
        params_input = {}
        
        if tool.parameters_schema:
            required_params = tool.parameters_schema.get('required', [])
            properties = tool.parameters_schema.get('properties', {})
            
            for param_name, param_schema in properties.items():
                param_type = param_schema.get('type', 'string')
                param_desc = param_schema.get('description', '')
                is_required = param_name in required_params
                
                label = f"{param_name} {'*' if is_required else ''}"
                
                if param_type == 'string':
                    params_input[param_name] = st.text_input(
                        label,
                        help=param_desc
                    )
                elif param_type == 'integer':
                    params_input[param_name] = st.number_input(
                        label,
                        value=0,
                        step=1,
                        help=param_desc
                    )
                elif param_type == 'boolean':
                    params_input[param_name] = st.checkbox(
                        label,
                        help=param_desc
                    )
                elif param_type == 'array':
                    params_input[param_name] = st.text_area(
                        label,
                        help=f"{param_desc} (JSON array)"
                    )
                else:
                    params_input[param_name] = st.text_area(
                        label,
                        help=f"{param_desc} (JSON)"
                    )
        else:
            st.info("This tool has no parameters")
        
        # Execute button
        if st.button("▶️ Execute Tool", type="primary"):
            with st.spinner("Executing..."):
                try:
                    # Prepare parameters
                    prepared_params = {}
                    for key, value in params_input.items():
                        if value:  # Only include non-empty params
                            # Try to parse JSON for arrays and objects
                            if isinstance(value, str) and value.strip().startswith(('[', '{')):
                                try:
                                    prepared_params[key] = json.loads(value)
                                except json.JSONDecodeError:
                                    prepared_params[key] = value
                            else:
                                prepared_params[key] = value
                    
                    # Execute tool
                    result = asyncio.run(server.execute_tool(
                        tool_id=selected_tool_id,
                        parameters=prepared_params,
                        context={'test_mode': True}
                    ))
                    
                    # Display result
                    st.markdown("#### ✅ Execution Result")
                    
                    if result.get('success'):
                        st.success("Tool executed successfully")
                        st.json(result.get('result', {}))
                    else:
                        st.error("Tool execution failed")
                        st.json(result)
                    
                    # Show execution metadata
                    with st.expander("📊 Execution Metadata"):
                        st.json({
                            'execution_id': result.get('execution_id'),
                            'timestamp': result.get('timestamp'),
                            'execution_time': result.get('execution_time'),
                            'tool_id': selected_tool_id
                        })
                
                except Exception as e:
                    st.error(f"❌ Execution error: {e}")
                    st.exception(e)


def mcp_management_app():
    """Main MCP Management Application."""
    st.set_page_config(
        page_title="MCP Server Management",
        page_icon="🛠️",
        layout="wide"
    )
    
    st.title("🛠️ MCP Server Management")
    st.markdown("Model Context Protocol - Tool Registry, Prompts, and Testing")
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        page = st.radio(
            "Select Page",
            ["🛠️ Tool Registry", "📝 Prompt Database", "🧪 Tool Testing"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📊 System Status")
        
        if MCP_AVAILABLE:
            st.success("✅ MCP System Online")
        else:
            st.error("❌ MCP System Offline")
    
    # Route to appropriate page
    if page == "🛠️ Tool Registry":
        mcp_tool_registry_page()
    elif page == "📝 Prompt Database":
        mcp_prompt_database_page()
    elif page == "🧪 Tool Testing":
        mcp_tool_testing_page()


if __name__ == "__main__":
    mcp_management_app()

