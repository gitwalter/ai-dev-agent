"""
Prompt Manager Web Application

A Streamlit-based web interface for managing AI Development Agent prompts
and RAG documents.
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

from utils.prompt_editor import get_prompt_editor
from utils.rag_processor import get_rag_processor


def main():
    """Main application function."""
    st.set_page_config(
        page_title="AI Development Agent - Prompt Manager",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 AI Development Agent - Prompt Manager")
    st.markdown("Manage system prompts and RAG documents for the AI Development Agent system.")
    
    # Initialize components
    prompt_editor = get_prompt_editor()
    rag_processor = get_rag_processor()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📊 Dashboard", "🔧 Agent Prompts", "⚙️ System Prompts", "📚 RAG Documents", "➕ Add Content"]
    )
    
    if page == "📊 Dashboard":
        show_dashboard(prompt_editor)
    elif page == "🔧 Agent Prompts":
        show_agent_prompts(prompt_editor)
    elif page == "⚙️ System Prompts":
        show_system_prompts(prompt_editor)
    elif page == "📚 RAG Documents":
        show_rag_documents(prompt_editor, rag_processor)
    elif page == "➕ Add Content":
        show_add_content(prompt_editor, rag_processor)


def show_dashboard(prompt_editor):
    """Show the dashboard with statistics."""
    st.header("📊 Dashboard")
    
    # Get statistics
    stats = prompt_editor.get_prompt_statistics()
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Agent Prompts",
            value=stats['agent_prompts']['total'],
            delta=f"{stats['agent_prompts']['unique_agents']} agents"
        )
    
    with col2:
        st.metric(
            label="System Prompts",
            value=stats['system_prompts']['total'],
            delta=f"{stats['system_prompts']['unique_categories']} categories"
        )
    
    with col3:
        st.metric(
            label="RAG Documents",
            value=stats['rag_documents']['total'],
            delta=f"{stats['rag_documents']['agents_with_docs']} agents"
        )
    
    # Success rate chart
    if stats['agent_prompts']['avg_success_rate'] > 0:
        st.subheader("Agent Prompt Performance")
        st.metric(
            label="Average Success Rate",
            value=f"{stats['agent_prompts']['avg_success_rate']:.1f}%"
        )
    
    # Recent activity
    st.subheader("Recent Activity")
    st.info("Activity tracking will be implemented in future versions.")


def show_agent_prompts(prompt_editor):
    """Show agent prompts management."""
    st.header("🔧 Agent Prompts")
    
    # Agent selection
    agents = [
        "requirements_analyst", "architecture_designer", "code_generator",
        "test_generator", "code_reviewer", "security_analyst", "documentation_generator"
    ]
    
    selected_agent = st.selectbox("Select Agent:", agents)
    
    if selected_agent:
        # Get prompts for selected agent
        prompts = prompt_editor.get_agent_prompts(selected_agent)
        
        if prompts:
            st.subheader(f"Prompts for {selected_agent.replace('_', ' ').title()}")
            
            # Display prompts in tabs
            tab_names = [f"Prompt {i+1}" for i in range(len(prompts))]
            tabs = st.tabs(tab_names)
            
            for i, (tab, prompt) in enumerate(zip(tabs, prompts)):
                with tab:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Show prompt template
                        st.text_area(
                            "Prompt Template:",
                            value=prompt['template'],
                            height=300,
                            key=f"prompt_{prompt['id']}"
                        )
                    
                    with col2:
                        # Show metadata
                        st.write("**Metadata:**")
                        st.write(f"**ID:** {prompt['id']}")
                        st.write(f"**Created:** {prompt['created_at']}")
                        st.write(f"**Updated:** {prompt['updated_at']}")
                        st.write(f"**Usage Count:** {prompt['usage_count']}")
                        st.write(f"**Success Rate:** {prompt['success_rate']:.1f}%")
                        
                        # Show if it's enhanced
                        if prompt['variables'].get('enhanced'):
                            st.success("✨ Enhanced Prompt")
                    
                    # Edit button
                    if st.button(f"Update Prompt {i+1}", key=f"update_{prompt['id']}"):
                        # Get the updated template
                        updated_template = st.session_state.get(f"prompt_{prompt['id']}")
                        if updated_template and updated_template != prompt['template']:
                            success = prompt_editor.update_agent_prompt(
                                prompt['id'], 
                                updated_template,
                                f"Updated via web interface on {datetime.now()}"
                            )
                            if success:
                                st.success("Prompt updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update prompt.")
        else:
            st.info(f"No prompts found for {selected_agent}.")


def show_system_prompts(prompt_editor):
    """Show system prompts management."""
    st.header("⚙️ System Prompts")
    
    # Category filter
    categories = ["workflow", "general", "error_handling", "validation", "custom"]
    selected_category = st.selectbox("Filter by Category:", ["All"] + categories)
    
    # Get system prompts
    if selected_category == "All":
        prompts = prompt_editor.get_system_prompts()
    else:
        prompts = prompt_editor.get_system_prompts(selected_category)
    
    if prompts:
        st.subheader(f"System Prompts ({len(prompts)} total)")
        
        # Display prompts
        for prompt in prompts:
            with st.expander(f"{prompt['name']} ({prompt['category']})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Show prompt template
                    updated_template = st.text_area(
                        "Prompt Template:",
                        value=prompt['template'],
                        height=200,
                        key=f"sys_prompt_{prompt['id']}"
                    )
                    
                    # Description
                    if prompt['description']:
                        st.write(f"**Description:** {prompt['description']}")
                
                with col2:
                    st.write("**Metadata:**")
                    st.write(f"**ID:** {prompt['id']}")
                    st.write(f"**Category:** {prompt['category']}")
                    st.write(f"**Created:** {prompt['created_at']}")
                    st.write(f"**Updated:** {prompt['updated_at']}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Update", key=f"update_sys_{prompt['id']}"):
                        if updated_template != prompt['template']:
                            success = prompt_editor.update_system_prompt(
                                prompt['id'], 
                                updated_template,
                                f"Updated via web interface on {datetime.now()}"
                            )
                            if success:
                                st.success("System prompt updated!")
                                st.rerun()
                            else:
                                st.error("Failed to update system prompt.")
                
                with col2:
                    if st.button("Delete", key=f"delete_sys_{prompt['id']}"):
                        if st.confirm(f"Are you sure you want to delete '{prompt['name']}'?"):
                            success = prompt_editor.delete_system_prompt(prompt['id'])
                            if success:
                                st.success("System prompt deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete system prompt.")
    else:
        st.info("No system prompts found.")


def show_rag_documents(prompt_editor, rag_processor):
    """Show RAG documents management."""
    st.header("📚 RAG Documents")
    
    # Agent filter
    agents = ["All", "requirements_analyst", "architecture_designer", "code_generator",
              "test_generator", "code_reviewer", "security_analyst", "documentation_generator"]
    selected_agent = st.selectbox("Filter by Agent:", agents)
    
    # Get RAG documents
    if selected_agent == "All":
        documents = prompt_editor.get_rag_documents()
    else:
        documents = prompt_editor.get_rag_documents(selected_agent)
    
    if documents:
        st.subheader(f"RAG Documents ({len(documents)} total)")
        
        # Display documents
        for doc in documents:
            with st.expander(f"{doc['title']} ({doc['source_type']})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Show document content (truncated)
                    content_preview = doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content']
                    st.text_area(
                        "Content Preview:",
                        value=content_preview,
                        height=150,
                        disabled=True
                    )
                    
                    # Show full content in expandable section
                    with st.expander("View Full Content"):
                        st.text(doc['content'])
                
                with col2:
                    st.write("**Metadata:**")
                    st.write(f"**ID:** {doc['id']}")
                    st.write(f"**Source Type:** {doc['source_type']}")
                    if doc['agent_name']:
                        st.write(f"**Agent:** {doc['agent_name']}")
                    if doc['source_url']:
                        st.write(f"**URL:** {doc['source_url']}")
                    if doc['file_path']:
                        st.write(f"**File:** {doc['file_path']}")
                    st.write(f"**Created:** {doc['created_at']}")
                    st.write(f"**Updated:** {doc['updated_at']}")
                    
                    # Show tags
                    if doc['tags']:
                        st.write("**Tags:**")
                        for tag in doc['tags']:
                            st.write(f"• {tag}")
                
                # Action buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Delete", key=f"delete_doc_{doc['id']}"):
                        if st.confirm(f"Are you sure you want to delete '{doc['title']}'?"):
                            success = prompt_editor.delete_rag_document(doc['id'])
                            if success:
                                st.success("Document deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete document.")
                
                with col2:
                    if st.button("Process Chunks", key=f"chunk_{doc['id']}"):
                        chunks = rag_processor.chunk_text(doc['content'])
                        st.write(f"**Generated {len(chunks)} chunks:**")
                        for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                            st.text_area(f"Chunk {i+1}", value=chunk, height=100, disabled=True)
    else:
        st.info("No RAG documents found.")


def show_add_content(prompt_editor, rag_processor):
    """Show add content interface."""
    st.header("➕ Add Content")
    
    # Tabs for different content types
    tab1, tab2, tab3 = st.tabs(["📝 System Prompt", "🌐 URL Document", "📁 File Document"])
    
    with tab1:
        st.subheader("Create New System Prompt")
        
        with st.form("new_system_prompt"):
            prompt_name = st.text_input("Prompt Name:")
            prompt_category = st.selectbox("Category:", ["workflow", "general", "error_handling", "validation", "custom"])
            prompt_description = st.text_area("Description (optional):")
            prompt_template = st.text_area("Prompt Template:", height=300)
            
            submitted = st.form_submit_button("Create System Prompt")
            
            if submitted:
                if prompt_name and prompt_template:
                    prompt_id = prompt_editor.create_system_prompt(
                        prompt_name, prompt_template, prompt_category, prompt_description
                    )
                    if prompt_id > 0:
                        st.success(f"System prompt created with ID: {prompt_id}")
                    else:
                        st.error("Failed to create system prompt.")
                else:
                    st.error("Please provide both name and template.")
    
    with tab2:
        st.subheader("Add URL Document")
        
        with st.form("new_url_document"):
            url = st.text_input("URL:")
            agent_name = st.selectbox("Associated Agent (optional):", 
                                    ["None"] + ["requirements_analyst", "architecture_designer", "code_generator",
                                               "test_generator", "code_reviewer", "security_analyst", "documentation_generator"])
            tags = st.text_input("Tags (comma-separated):")
            
            submitted = st.form_submit_button("Process URL")
            
            if submitted and url:
                # Validate URL
                if rag_processor.validate_url(url):
                    with st.spinner("Processing URL..."):
                        result = rag_processor.process_url(url)
                        
                        if result['success']:
                            # Show preview
                            st.write("**Preview:**")
                            st.write(f"**Title:** {result['title']}")
                            st.write(f"**Content Length:** {len(result['content'])} characters")
                            
                            # Show content preview
                            content_preview = result['content'][:500] + "..." if len(result['content']) > 500 else result['content']
                            st.text_area("Content Preview:", value=content_preview, height=150, disabled=True)
                            
                            # Add to database
                            if st.button("Add to Database"):
                                agent = None if agent_name == "None" else agent_name
                                tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
                                
                                doc_id = prompt_editor.add_rag_document(
                                    result['title'], result['content'], 'url',
                                    source_url=url, agent_name=agent, tags=tag_list
                                )
                                
                                if doc_id > 0:
                                    st.success(f"Document added with ID: {doc_id}")
                                else:
                                    st.error("Failed to add document to database.")
                        else:
                            st.error(f"Failed to process URL: {result['content']}")
                else:
                    st.error("Invalid or inaccessible URL.")
    
    with tab3:
        st.subheader("Add File Document")
        
        with st.form("new_file_document"):
            uploaded_file = st.file_uploader("Choose a file:", 
                                           type=['txt', 'md', 'py', 'js', 'html', 'css', 'json'])
            agent_name = st.selectbox("Associated Agent (optional):", 
                                    ["None"] + ["requirements_analyst", "architecture_designer", "code_generator",
                                               "test_generator", "code_reviewer", "security_analyst", "documentation_generator"])
            tags = st.text_input("Tags (comma-separated):")
            
            submitted = st.form_submit_button("Process File")
            
            if submitted and uploaded_file:
                # Process uploaded file
                content = uploaded_file.read().decode('utf-8')
                
                # Show preview
                st.write("**Preview:**")
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**Content Length:** {len(content)} characters")
                
                # Show content preview
                content_preview = content[:500] + "..." if len(content) > 500 else content
                st.text_area("Content Preview:", value=content_preview, height=150, disabled=True)
                
                # Add to database
                if st.button("Add to Database"):
                    agent = None if agent_name == "None" else agent_name
                    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
                    
                    doc_id = prompt_editor.add_rag_document(
                        uploaded_file.name, content, 'file',
                        file_path=uploaded_file.name, agent_name=agent, tags=tag_list
                    )
                    
                    if doc_id > 0:
                        st.success(f"Document added with ID: {doc_id}")
                    else:
                        st.error("Failed to add document to database.")


if __name__ == "__main__":
    main()
