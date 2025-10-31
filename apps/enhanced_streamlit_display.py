"""
Enhanced Streamlit Display Components for Agent Swarm Results
==============================================================

Beautiful, comprehensive display of ALL agent outputs with attention to every detail.
"God is in the details" - Ludwig Mies van der Rohe
"""

import streamlit as st
from typing import Dict, Any
import json
import re
from pathlib import Path
from datetime import datetime

# Import shared extraction utilities
from utils.workflow_file_extractor import (
    extract_code_files as _extract_code_files_util,
    extract_test_files as _extract_test_files_util
)


def display_agent_swarm_results(result_state: Dict[str, Any]):
    """
    Display agent swarm results with God-level attention to detail.
    
    Shows COMPLETE state including:
    - Requirements Analysis
    - Architecture Design
    - Generated Code Files
    - Code Metadata (plan, assumptions, etc.)
    - Test Files & Strategy
    - Code Review Results
    - Documentation
    
    Args:
        result_state: The final state from the agent swarm workflow
    """
    
    st.header("🎯 Agent Swarm Results - Complete View")
    
    # Display execution summary at the top
    display_execution_summary(result_state)
    
    # Main tabs for complete coverage of ALL outputs
    tabs = st.tabs([
        "📋 Requirements & Architecture",
        "💻 Generated Code",
        "🧪 Tests & Quality",
        "📚 Documentation & Review", 
        "🤖 Agent Execution",
        "💾 Download Project"
    ])
    
    with tabs[0]:
        display_requirements_and_architecture(result_state)
    
    with tabs[1]:
        display_code_generation(result_state)
    
    with tabs[2]:
        display_tests_and_quality(result_state)
    
    with tabs[3]:
        display_documentation_and_review(result_state)
    
    with tabs[4]:
        display_agent_execution_details(result_state)
    
    with tabs[5]:
        display_download_options(result_state)


def display_execution_summary(state: Dict[str, Any]):
    """Display high-level execution summary with beautiful metrics."""
    
    st.subheader("📊 Execution Summary")
    
    # Top-level metrics in columns
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        complexity = state.get("project_complexity", "Unknown")
        st.metric(
            "Complexity", 
            complexity.title(),
            help="Project complexity determined by analyzer agent"
        )
    
    with col2:
        required = state.get("required_agents", [])
        completed = state.get("completed_agents", [])
        st.metric(
            "Agents", 
            f"{len(completed)}/{len(required)}",
            help=f"Completed agents: {', '.join(completed) if completed else 'None'}"
        )
    
    with col3:
        code_files = state.get("code_files", {})
        file_count = len(code_files) if isinstance(code_files, dict) else 0
        st.metric(
            "Source Files", 
            file_count,
            help="Total source code files generated"
        )
    
    with col4:
        test_files = state.get("test_files", {})
        test_count = 0
        if isinstance(test_files, dict):
            if "files" in test_files:
                test_count = len(test_files.get("files", {}))
            else:
                test_count = len([k for k in test_files.keys() if not k in ["test_strategy", "coverage_analysis", "test_suites", "performance_tests", "quality_gate_passed"]])
        st.metric(
            "Test Files", 
            test_count,
            help="Total test files generated"
        )
    
    with col5:
        errors = state.get("errors", [])
        error_count = len(errors) if errors else 0
        st.metric(
            "Errors", 
            error_count, 
            delta=None,
            delta_color="inverse" if error_count > 0 else "off",
            help="Errors encountered during execution"
        )
    
    with col6:
        # Check if all required agents completed
        progress = len(completed) / len(required) if required else 0
        status = "Complete" if progress >= 1.0 else "In Progress"
        st.metric(
            "Status",
            status,
            help=f"Workflow progress: {progress*100:.0f}%"
        )
    
    # Progress bar
    if required:
        st.progress(progress, text=f"Workflow Progress: {len(completed)}/{len(required)} agents")
    
    # Show errors prominently if any
    errors = state.get("errors", [])
    if errors:
        st.error("⚠️ **Errors Encountered During Execution:**")
        for i, error in enumerate(errors, 1):
            st.markdown(f"{i}. {error}")
    
    # Current step indicator
    current_step = state.get("current_step", "Unknown")
    if current_step != "Unknown":
        st.info(f"📍 **Current Step:** `{current_step}`")


def display_requirements_and_architecture(state: Dict[str, Any]):
    """Display requirements and architecture outputs beautifully."""
    
    st.subheader("📋 Requirements Analysis & Architecture Design")
    
    # Requirements Section
    requirements = state.get("requirements", {})
    if requirements:
        st.markdown("### 🎯 Requirements Analysis")
        st.markdown("*Output from Requirements Analyst Agent*")
        st.markdown("---")
        
        if isinstance(requirements, dict):
            output = requirements.get("output", "")
            if output:
                # Display in expandable, formatted text area
                with st.expander("📄 View Full Requirements Document", expanded=True):
                    st.text_area(
                        "Requirements",
                        value=output,
                        height=400,
                        help="Complete requirements analysis from the Requirements Analyst agent",
                        label_visibility="collapsed"
                    )
            else:
                # Show structured data if no output text
                st.json(requirements)
        else:
            st.text_area("Requirements", value=str(requirements), height=300)
    else:
        st.info("💡 Requirements analysis not yet available - agent may not have run")
    
    st.markdown("---")
    
    # Architecture Section
    architecture = state.get("architecture", {})
    if architecture:
        st.markdown("### 🏗️ System Architecture Design")
        st.markdown("*Output from Architecture Designer Agent*")
        st.markdown("---")
        
        if isinstance(architecture, dict):
            output = architecture.get("output", "")
            if output:
                with st.expander("📐 View Full Architecture Document", expanded=True):
                    st.text_area(
                        "Architecture",
                        value=output,
                        height=400,
                        help="Complete architecture design from the Architecture Designer agent",
                        label_visibility="collapsed"
                    )
            else:
                st.json(architecture)
        else:
            st.text_area("Architecture", value=str(architecture), height=300)
    else:
        st.info("💡 Architecture design not yet available - agent may not have run")


def display_code_generation(state: Dict[str, Any]):
    """Display generated code files and metadata with exquisite detail."""
    
    st.subheader("💻 Code Generation Results")
    
    # Code Files - extract from nested structure
    code_files_raw = state.get("code_files", {})
    code_metadata = state.get("code_metadata", {})
    
    # Extract actual files using shared utility
    code_files = _extract_code_files_util(code_files_raw)
    
    if not code_files:
        st.warning("⚠️ No code files generated yet - code generator agent may not have run")
        return
    
    # Display file tree first
    file_tree = code_metadata.get("file_tree", "")
    if file_tree:
        st.markdown("### 🌳 Project Structure")
        if isinstance(file_tree, list):
            st.code("\n".join(file_tree), language="text")
        else:
            st.code(file_tree, language="text")
    
    st.markdown("---")
    
    # Display generated files
    st.markdown(f"### 📁 Generated Source Files ({len(code_files)} files)")
    
    if isinstance(code_files, dict) and code_files:
        # File selector
        file_names = sorted(list(code_files.keys()))
        selected_file = st.selectbox(
            "Select file to view:",
            file_names,
            key="code_file_selector"
        )
        
        if selected_file:
            content = code_files[selected_file]
            
            # File header with metadata
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"#### 📄 `{selected_file}`")
                # Show file size and line count
                lines = content.split('\n')
                st.caption(f"📏 {len(lines)} lines | 💾 {len(content)} characters")
            
            with col2:
                # Download button
                st.download_button(
                    label="💾 Download",
                    data=content,
                    file_name=selected_file,
                    mime="text/plain",
                    key=f"download_code_{selected_file}"
                )
            
            # Content display with syntax highlighting
            language = _detect_language(selected_file)
            st.code(content, language=language, line_numbers=True)
    else:
        st.warning("Code files data structure is unexpected")
    
    st.markdown("---")
    
    # Display Implementation Plan and Metadata
    if code_metadata:
        st.markdown("### 📋 Implementation Details")
        
        # Create sub-tabs for different metadata sections
        metadata_tabs = st.tabs([
            "📝 Plan & Assumptions",
            "🔧 Configuration & Setup",
            "🔌 API Contracts",
            "🔒 Security & Performance"
        ])
        
        with metadata_tabs[0]:
            display_plan_and_assumptions(code_metadata)
        
        with metadata_tabs[1]:
            display_configuration_setup(code_metadata)
        
        with metadata_tabs[2]:
            display_api_contracts(code_metadata)
        
        with metadata_tabs[3]:
            display_security_performance(code_metadata)


def display_plan_and_assumptions(metadata: Dict[str, Any]):
    """Display implementation plan and assumptions."""
    
    plan = metadata.get("plan", [])
    if plan:
        st.markdown("#### 🎯 Implementation Plan")
        for i, step in enumerate(plan, 1):
            st.markdown(f"**Step {i}:** {step}")
    else:
        st.info("No implementation plan available")
    
    st.markdown("---")
    
    assumptions = metadata.get("assumptions", [])
    if assumptions:
        st.markdown("#### 💭 Assumptions Made")
        for assumption in assumptions:
            st.markdown(f"- {assumption}")
    else:
        st.info("No assumptions documented")
    
    st.markdown("---")
    
    limitations = metadata.get("limitations", [])
    if limitations:
        st.markdown("#### ⚠️ Known Limitations")
        for limitation in limitations:
            st.markdown(f"- {limitation}")


def display_configuration_setup(metadata: Dict[str, Any]):
    """Display configuration and setup instructions."""
    
    # Runbook
    runbook = metadata.get("runbook", {})
    if runbook:
        st.markdown("#### 📖 Setup & Run Instructions")
        
        for section, commands in runbook.items():
            st.markdown(f"**{section.replace('_', ' ').title()}:**")
            if isinstance(commands, list):
                for cmd in commands:
                    st.code(cmd, language="bash")
            else:
                st.code(str(commands), language="bash")
    else:
        st.info("No runbook available")
    
    st.markdown("---")
    
    # Configuration notes
    config_notes = metadata.get("config_notes", "")
    if config_notes:
        st.markdown("#### ⚙️ Configuration Notes")
        st.info(config_notes)
    else:
        st.info("No configuration notes available")


def display_api_contracts(metadata: Dict[str, Any]):
    """Display API contracts."""
    
    api_contracts = metadata.get("api_contracts", [])
    if api_contracts:
        st.markdown("#### 🔌 API Contracts")
        
        for i, contract in enumerate(api_contracts, 1):
            with st.expander(f"API Contract {i}: {contract.get('name', 'Unnamed')}", expanded=False):
                st.markdown("**Interface:**")
                st.code(contract.get("interface", ""), language="text")
                
                errors = contract.get("errors", [])
                if errors:
                    st.markdown("**Possible Errors:**")
                    for error in errors:
                        st.markdown(f"- {error}")
                
                examples = contract.get("examples", [])
                if examples:
                    st.markdown("**Usage Examples:**")
                    for example in examples:
                        st.code(example, language="bash")
    else:
        st.info("No API contracts defined")


def display_security_performance(metadata: Dict[str, Any]):
    """Display security and performance considerations."""
    
    # Security
    security_review = metadata.get("security_review", [])
    if security_review:
        st.markdown("#### 🔒 Security Review")
        for item in security_review:
            st.markdown(f"- {item}")
    else:
        st.info("No security review available")
    
    st.markdown("---")
    
    # Performance
    performance_notes = metadata.get("performance_notes", [])
    if performance_notes:
        st.markdown("#### ⚡ Performance Considerations")
        for note in performance_notes:
            st.markdown(f"- {note}")
    else:
        st.info("No performance notes available")


def display_tests_and_quality(state: Dict[str, Any]):
    """Display test files and testing strategy with comprehensive detail."""
    
    st.subheader("🧪 Tests & Quality Assurance")
    
    test_files_raw = state.get("test_files", {})
    
    if not test_files_raw:
        st.warning("⚠️ No test data available - test generator agent may not have run")
        return
    
    # Extract actual test files using shared utility
    test_files_extracted = _extract_test_files_util(test_files_raw)
    test_files = test_files_raw  # Keep the raw for metadata access
    
    # Test Strategy (if available)
    if isinstance(test_files, dict):
        test_strategy = test_files.get("test_strategy", {})
        if test_strategy:
            st.markdown("### 📋 Testing Strategy")
            st.markdown("*Comprehensive testing approach designed by Test Generator agent*")
            
            with st.expander("View Testing Strategy Details", expanded=True):
                if isinstance(test_strategy, dict):
                    for key, value in test_strategy.items():
                        st.markdown(f"**{key.replace('_', ' ').title()}:**")
                        if isinstance(value, list):
                            for item in value:
                                st.markdown(f"- {item}")
                        else:
                            st.markdown(f"{value}")
                        st.markdown("")
                else:
                    st.text_area("Test Strategy", value=str(test_strategy), height=200)
            
            st.markdown("---")
        
        # Coverage Analysis
        coverage_analysis = test_files.get("coverage_analysis", {})
        if coverage_analysis:
            st.markdown("### 📊 Coverage Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                target = coverage_analysis.get("target_coverage", "Not specified")
                st.metric("Target Coverage", target)
            
            with col2:
                actual = coverage_analysis.get("actual_coverage", "Not measured")
                st.metric("Actual Coverage", actual)
            
            with col3:
                status = coverage_analysis.get("status", "Unknown")
                st.metric("Status", status)
            
            gaps = coverage_analysis.get("coverage_gaps", [])
            if gaps:
                st.markdown("**Coverage Gaps:**")
                for gap in gaps:
                    st.markdown(f"- {gap}")
            
            st.markdown("---")
        
        # Test Suites
        test_suites = test_files.get("test_suites", [])
        if test_suites:
            st.markdown("### 📦 Test Suites")
            
            for suite in test_suites:
                with st.expander(f"Test Suite: {suite.get('name', 'Unnamed')}", expanded=False):
                    st.markdown(f"**Description:** {suite.get('description', 'No description')}")
                    
                    tests = suite.get("tests", [])
                    if tests:
                        st.markdown(f"**Tests ({len(tests)}):**")
                        for test in tests:
                            st.markdown(f"- `{test}`")
            
            st.markdown("---")
        
        # Generated Test Files
        if test_files_extracted:
            st.markdown(f"### 🧪 Generated Test Files ({len(test_files_extracted)} files)")
            
            # File selector
            file_names = sorted(list(test_files_extracted.keys()))
            selected_file = st.selectbox(
                "Select test file to view:",
                file_names,
                key="test_file_selector"
            )
            
            if selected_file:
                content = test_files_extracted[selected_file]
                
                # File header
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"#### 📄 `{selected_file}`")
                    lines = content.split('\n')
                    st.caption(f"📏 {lines} lines | 💾 {len(content)} characters")
                
                with col2:
                    st.download_button(
                        label="💾 Download",
                        data=content,
                        file_name=selected_file,
                        mime="text/plain",
                        key=f"download_test_{selected_file}"
                    )
                
                # Display test file with syntax highlighting
                language = _detect_language(selected_file)
                st.code(content, language=language, line_numbers=True)
        
        # Quality Gate
        quality_gate = test_files.get("quality_gate_passed", None)
        if quality_gate is not None:
            st.markdown("---")
            st.markdown("### 🚦 Quality Gate")
            if quality_gate:
                st.success("✅ Quality gate PASSED - All quality standards met!")
            else:
                st.error("❌ Quality gate FAILED - Review required")


def display_documentation_and_review(state: Dict[str, Any]):
    """Display documentation and code review outputs."""
    
    st.subheader("📚 Documentation & Code Review")
    
    # Code Review Section
    code_review = state.get("code_review", {})
    if code_review:
        st.markdown("### 🔍 Code Review Results")
        st.markdown("*Professional code review by Code Reviewer agent*")
        st.markdown("---")
        
        if isinstance(code_review, dict):
            output = code_review.get("output", "")
            if output:
                with st.expander("📋 View Full Code Review", expanded=True):
                    st.text_area(
                        "Code Review",
                        value=output,
                        height=400,
                        help="Complete code review analysis",
                        label_visibility="collapsed"
                    )
            else:
                st.json(code_review)
        else:
            st.text_area("Code Review", value=str(code_review), height=300)
    else:
        st.info("💡 Code review not yet available - agent may not have run")
    
    st.markdown("---")
    
    # Documentation Section  
    documentation = state.get("documentation", {})
    if documentation:
        st.markdown("### 📚 Project Documentation")
        st.markdown("*Comprehensive documentation by Documentation Generator agent*")
        st.markdown("---")
        
        if isinstance(documentation, dict):
            output = documentation.get("output", "")
            if output:
                with st.expander("📖 View Full Documentation", expanded=True):
                    st.text_area(
                        "Documentation",
                        value=output,
                        height=400,
                        help="Complete project documentation",
                        label_visibility="collapsed"
                    )
            else:
                st.json(documentation)
        else:
            st.text_area("Documentation", value=str(documentation), height=300)
    else:
        st.info("💡 Documentation not yet available - agent may not have run")


def display_agent_execution_details(state: Dict[str, Any]):
    """Display detailed agent execution information."""
    
    st.subheader("🤖 Agent Execution Details")
    
    # Agent execution timeline
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Required Agents")
        required_agents = state.get("required_agents", [])
        if required_agents:
            for i, agent in enumerate(required_agents, 1):
                agent_name = agent.replace('_', ' ').title()
                st.markdown(f"{i}. {agent_name}")
        else:
            st.info("No required agents specified")
    
    with col2:
        st.markdown("### ✅ Completed Agents")
        completed_agents = state.get("completed_agents", [])
        if completed_agents:
            for agent in completed_agents:
                agent_name = agent.replace('_', ' ').title()
                st.markdown(f"✓ {agent_name}")
        else:
            st.info("No agents completed yet")
    
    # Progress visualization
    if required_agents and completed_agents:
        progress = len(completed_agents) / len(required_agents)
        st.progress(progress)
        st.caption(f"Progress: {len(completed_agents)}/{len(required_agents)} agents ({progress*100:.0f}%)")
    
    st.markdown("---")
    
    # Agent Messages/Logs
    messages = state.get("messages", [])
    if messages:
        st.markdown("### 💬 Agent Communication Log")
        st.caption(f"Total messages: {len(messages)}")
        
        with st.expander("View All Messages", expanded=False):
            for i, msg in enumerate(messages, 1):
                if hasattr(msg, 'content'):
                    content = msg.content
                    msg_type = msg.__class__.__name__
                    
                    if 'AI' in msg_type:
                        st.success(f"**Message {i} (AI):** {content}")
                    elif 'Human' in msg_type:
                        st.info(f"**Message {i} (Human):** {content}")
                    else:
                        st.text(f"**Message {i}:** {content}")
                else:
                    st.text(f"**Message {i}:** {str(msg)}")
    
    st.markdown("---")
    
    # Full state for debugging
    with st.expander("🔧 Complete State (Debug View)", expanded=False):
        st.json(state)


def display_download_options(state: Dict[str, Any]):
    """Display comprehensive download options."""
    
    st.subheader("💾 Download Generated Project")
    
    code_files_raw = state.get("code_files", {})
    test_files_raw = state.get("test_files", {})
    
    # Extract actual code files - they might be nested in raw_output JSON
    extracted_code_files = _extract_code_files_util(code_files_raw)
    
    # Extract test files - they might be nested in files dict
    extracted_test_files = _extract_test_files_util(test_files_raw)
    
    # Combine all files
    all_files = {}
    all_files.update(extracted_code_files)
    all_files.update(extracted_test_files)
    
    if not all_files:
        st.warning("⚠️ No files available for download yet")
        return
    
    # Download statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Files", len(all_files))
    
    with col2:
        st.metric("Source Files", len(extracted_code_files))
    
    with col3:
        st.metric("Test Files", len(extracted_test_files))
    
    with col4:
        total_size = sum(len(str(content)) for content in all_files.values())
        st.metric("Total Size", f"{total_size:,} chars")
    
    st.markdown("---")
    
    # Download options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 Download Complete Project")
        
        if st.button("Generate ZIP Archive", type="primary", key="generate_zip"):
            zip_data = _create_zip_archive(all_files, state)
            
            # Generate safe filename
            project_context = state.get("project_context", "project")
            safe_name = _sanitize_filename(project_context[:30])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            st.download_button(
                label="⬇️ Download ZIP Archive",
                data=zip_data,
                file_name=f"{safe_name}_{timestamp}.zip",
                mime="application/zip",
                key="download_zip"
            )
    
    with col2:
        st.markdown("### 📄 Individual Files")
        st.info("💡 Use the 'Generated Code' and 'Tests & Quality' tabs to download individual files")
    
    st.markdown("---")
    
    # Project summary export
    st.markdown("### 📋 Project Summary")
    
    summary = {
        "project_context": state.get("project_context", ""),
        "complexity": state.get("project_complexity", "Unknown"),
        "agents_used": state.get("completed_agents", []),
        "total_files": len(all_files),
        "source_files": len(extracted_code_files),
        "test_files": len(extracted_test_files),
        "generated_at": datetime.now().isoformat()
    }
    
    summary_json = json.dumps(summary, indent=2)
    
    st.download_button(
        label="📥 Download Project Summary (JSON)",
        data=summary_json,
        file_name=f"project_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        key="download_summary"
    )


# File extraction functions are now in utils.workflow_file_extractor
# Imported above as _extract_code_files_util and _extract_test_files_util

def _detect_language(filename: str) -> str:
    """Detect programming language from filename extension."""
    ext = Path(filename).suffix.lower()
    
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sql': 'sql',
        '.sh': 'bash',
        '.bash': 'bash',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.md': 'markdown',
        '.txt': 'text',
        '.toml': 'toml',
        '.ini': 'ini',
    }
    
    return language_map.get(ext, 'text')


def _create_zip_archive(files: Dict[str, str], state: Dict[str, Any]) -> bytes:
    """Create a comprehensive ZIP archive with all files and metadata."""
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add all source and test files
        for file_path, content in files.items():
            zip_file.writestr(file_path, content)
        
        # Add comprehensive metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "project_context": state.get("project_context", ""),
            "project_complexity": state.get("project_complexity", "Unknown"),
            "agents_used": state.get("completed_agents", []),
            "total_files": len(files),
            "execution_summary": {
                "required_agents": state.get("required_agents", []),
                "completed_agents": state.get("completed_agents", []),
                "errors": state.get("errors", [])
            }
        }
        
        # Add code metadata if available
        code_metadata = state.get("code_metadata", {})
        if code_metadata:
            metadata["implementation"] = {
                "plan": code_metadata.get("plan", []),
                "assumptions": code_metadata.get("assumptions", []),
                "limitations": code_metadata.get("limitations", []),
                "config_notes": code_metadata.get("config_notes", "")
            }
        
        # Add test metadata if available
        test_files = state.get("test_files", {})
        if isinstance(test_files, dict):
            test_strategy = test_files.get("test_strategy", {})
            coverage = test_files.get("coverage_analysis", {})
            if test_strategy or coverage:
                metadata["testing"] = {
                    "strategy": test_strategy,
                    "coverage_analysis": coverage,
                    "quality_gate_passed": test_files.get("quality_gate_passed", None)
                }
        
        # Write metadata as JSON
        zip_file.writestr("PROJECT_METADATA.json", json.dumps(metadata, indent=2))
        
        # Add README with instructions
        readme_content = f"""# AI-Generated Project

**Generated:** {metadata['generated_at']}
**Complexity:** {metadata['project_complexity']}
**Agents Used:** {', '.join(metadata['agents_used'])}

## Project Context
{state.get('project_context', 'No context provided')}

## Files Included
- Source Files: {len([f for f in files.keys() if not 'test' in f.lower()])}
- Test Files: {len([f for f in files.keys() if 'test' in f.lower()])}

## Next Steps
1. Review the generated code files
2. Check PROJECT_METADATA.json for implementation details
3. Run tests to verify functionality
4. Customize as needed for your specific requirements

---
Generated by AI Development Agent using LangGraph and Gemini API
"""
        zip_file.writestr("README.md", readme_content)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe download."""
    # Remove or replace problematic characters
    safe_name = re.sub(r'[<>:"/\\|?*\s]', '_', filename.strip())
    safe_name = re.sub(r'_+', '_', safe_name).strip('_')
    
    return safe_name if safe_name else "project"
