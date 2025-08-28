"""
Streamlit Web Application for AI Development Agent.
Provides a user-friendly interface for the AI Development Agent system.
"""

import streamlit as st
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime
# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.config import get_default_config
from models.state import create_initial_state
from models.responses import WorkflowResult, WorkflowStatus
from utils.logging_config import setup_logging
from main import AIDevelopmentAgent
from models.config import load_config_from_env
from utils.toml_config import TOMLConfigLoader, ensure_secrets_file
from utils.prompt_editor import get_prompt_editor
from utils.rag_processor import get_rag_processor


# Page configuration
st.set_page_config(
    page_title="AI Development Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .file-preview {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'workflow_result' not in st.session_state:
        st.session_state.workflow_result = None
    if 'project_files' not in st.session_state:
        st.session_state.project_files = {}
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'api_key_configured' not in st.session_state:
        st.session_state.api_key_configured = False
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = False
    if 'show_log_viewer' not in st.session_state:
        st.session_state.show_log_viewer = False


def configure_api_key():
    """Configure API key using multiple sources with proper priority."""
    st.sidebar.subheader("🔑 API Key Configuration")
    
    # Priority 1: Check Streamlit secrets (highest priority)
    try:
        if hasattr(st.secrets, "GEMINI_API_KEY"):
            api_key = st.secrets.GEMINI_API_KEY
            if api_key and api_key != "your-gemini-api-key-here":
                st.sidebar.success("✅ API key found in Streamlit secrets")
                st.session_state.api_key_configured = True
                return True
    except Exception:
        pass
    
    # Priority 2: Check secrets.toml file
    try:
        toml_loader = TOMLConfigLoader()
        api_key = toml_loader.get_gemini_api_key()
        if api_key and api_key != "your-gemini-api-key-here":
            st.sidebar.success("✅ API key found in secrets.toml")
            st.session_state.api_key_configured = True
            return True
    except Exception:
        pass
    
    # Priority 3: Check environment variable
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    if env_api_key:
        st.sidebar.success("✅ API key found in environment variable")
        st.session_state.api_key_configured = True
        return True
    
    # If no API key found, provide input option
    st.sidebar.warning("⚠️ No API key found")
    
    with st.sidebar.expander("Configure API Key", expanded=True):
        st.info("Please provide your Gemini API key to use the application.")
        
        api_key_input = st.text_input(
            "Gemini API Key",
            type="password",
            help="Enter your Gemini API key from Google AI Studio"
        )
        
        if st.button("Save API Key"):
            if api_key_input:
                # Save to secrets.toml
                try:
                    ensure_secrets_file()
                    secrets_content = f"""# AI Development Agent Secrets Configuration
# This file contains sensitive configuration data
# DO NOT commit this file to version control

GEMINI_API_KEY = "{api_key_input}"
"""
                    with open("secrets.toml", "w") as f:
                        f.write(secrets_content)
                    
                    st.success("✅ API key saved to secrets.toml")
                    st.session_state.api_key_configured = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving API key: {str(e)}")
            else:
                st.error("❌ Please enter a valid API key")
    
    return False


def configure_model_selection():
    """Configure Gemini model selection."""
    st.sidebar.subheader("🤖 Model Configuration")
    
    # Initialize model selection in session state
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "gemini-2.5-flash-lite"
    
    # Available Gemini models
    available_models = {
        "gemini-2.5-flash": "Gemini 2.5 Flash (Fast, balanced)",
        "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite (Fastest, efficient)"
    }
    
    # Model selection dropdown
    selected_model = st.sidebar.selectbox(
        "Select Gemini Model",
        options=list(available_models.keys()),
        index=list(available_models.keys()).index(st.session_state.selected_model),
        format_func=lambda x: f"{x} - {available_models[x]}",
        help="Choose the Gemini model for AI generation"
    )
    
    # Update session state if model changed
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        # Reset agent to force reinitialization with new model
        st.session_state.agent = None
        st.sidebar.success(f"✅ Model changed to {selected_model}")
    
    # Display model information
    with st.sidebar.expander("Model Information", expanded=False):
        st.info(f"""
        **Current Model:** {selected_model}
        
        **Model Details:**
        - **Gemini 2.5 Flash**: Best balance of speed and capability
        - **Gemini 2.5 Flash Lite**: Fastest model, optimized for efficiency
        
        **Note:** Changing the model will reinitialize the agent.
        """)
    
    return selected_model


def show_performance_dashboard():
    """Display performance monitoring dashboard."""
    st.subheader("📊 Performance Dashboard")
    
    try:
        from utils.performance_optimizer import performance_optimizer, analyze_and_optimize_performance
        
        # Add performance analysis button
        if st.button("🔍 Analyze Performance", type="primary"):
            with st.spinner("Analyzing performance metrics..."):
                analysis_results = analyze_and_optimize_performance()
                
                if "error" in analysis_results:
                    st.error(f"Performance analysis failed: {analysis_results['error']}")
                    return
                
                # Display workflow analysis
                workflow_analysis = analysis_results["workflow_analysis"]
                
                # Overall metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Executions", workflow_analysis["total_executions"])
                with col2:
                    st.metric("Success Rate", f"{workflow_analysis['average_success_rate']:.1%}")
                with col3:
                    st.metric("Total Cost", f"${workflow_analysis['total_cost']:.4f}")
                with col4:
                    st.metric("Performance Score", f"{workflow_analysis['performance_score']:.1f}/100")
                
                # Agent performance table
                st.subheader("Agent Performance Analysis")
                agent_data = []
                for agent_name, analysis in workflow_analysis["agent_analyses"].items():
                    agent_data.append({
                        "Agent": agent_name,
                        "Performance Score": f"{analysis.performance_score:.1f}/100",
                        "Success Rate": f"{analysis.success_rate:.1%}",
                        "Avg Time": f"{analysis.average_execution_time:.2f}s",
                        "Cost/Exec": f"${analysis.cost_per_execution:.4f}",
                        "Total Execs": analysis.total_executions
                    })
                
                if agent_data:
                    st.dataframe(agent_data, use_container_width=True)
                
                # Optimization results
                if analysis_results["optimization_results"]:
                    st.subheader("🚀 Optimization Results")
                    for agent_name, results in analysis_results["optimization_results"].items():
                        with st.expander(f"Optimizations for {agent_name}"):
                            st.write(f"**Implemented Optimizations:** {', '.join(results['implemented_optimizations'])}")
                            st.write(f"**Expected Improvements:**")
                            for opt_type, improvement in results["expected_improvements"].items():
                                st.write(f"- {opt_type}: {improvement['expected_impact']}")
                
                # Performance report
                st.subheader("📋 Detailed Performance Report")
                st.text_area("Performance Report", analysis_results["performance_report"], height=400)
        
        # Quick metrics display
        if performance_optimizer.metrics:
            st.subheader("📈 Recent Performance Metrics")
            
            # Get recent metrics (last 10)
            recent_metrics = performance_optimizer.metrics[-10:]
            
            # Create metrics display
            metric_data = []
            for metric in recent_metrics:
                metric_data.append({
                    "Agent": metric.agent_name,
                    "Time": f"{metric.execution_time:.2f}s",
                    "Success": "✅" if metric.success else "❌",
                    "Model": metric.model_used,
                    "Cost": f"${metric.cost_estimate:.4f}",
                    "Timestamp": metric.timestamp.strftime("%H:%M:%S")
                })
            
            if metric_data:
                st.dataframe(metric_data, use_container_width=True)
        else:
            st.info("No performance metrics available yet. Run some agent operations to see metrics.")
    
    except ImportError:
        st.error("Performance optimization module not available")
    except Exception as e:
        st.error(f"Error loading performance dashboard: {e}")


def create_agent():
    """Create and initialize the AI Development Agent."""
    if st.session_state.agent is None:
        setup_logging()
        try:
            # Load configuration from environment
            config = load_config_from_env()
            
            # Update model name if selected model is different from config
            if 'selected_model' in st.session_state:
                config.gemini.model_name = st.session_state.selected_model
            
            st.session_state.agent = AIDevelopmentAgent(config)
        except Exception as e:
            st.error(f"Failed to initialize AI Development Agent: {str(e)}")
            st.error("Please check your GEMINI_API_KEY environment variable.")
            return None
    return st.session_state.agent


def display_header():
    """Display the main header."""
    st.markdown('<h1 class="main-header">🚀 AI Development Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate complete software projects with AI-powered agents</p>', unsafe_allow_html=True)


def clear_logs():
    """Clear (truncate) all log files to empty."""
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return False, "No logs directory found."
        
        # Count files before clearing
        total_files = 0
        total_size = 0
        cleared_files = 0
        cleared_size = 0
        
        # Clear files in main logs directory
        for log_file in logs_dir.glob("*.log"):
            total_files += 1
            total_size += log_file.stat().st_size
            try:
                log_file.write_text("")  # Truncate to empty
                cleared_files += 1
                cleared_size += total_size
            except (PermissionError, OSError):
                pass
        
        # Clear files in agents subdirectory
        agents_dir = logs_dir / "agents"
        if agents_dir.exists():
            for log_file in agents_dir.glob("*.log"):
                total_files += 1
                total_size += log_file.stat().st_size
                try:
                    log_file.write_text("")  # Truncate to empty
                    cleared_files += 1
                    cleared_size += total_size
                except (PermissionError, OSError):
                    pass
        
        # Create success message
        size_mb = total_size / (1024 * 1024)
        
        if cleared_files == total_files:
            return True, f"Successfully cleared all {cleared_files} log files ({size_mb:.1f} MB)."
        elif cleared_files > 0:
            failed_count = total_files - cleared_files
            return True, f"Cleared {cleared_files}/{total_files} log files ({size_mb:.1f} MB). {failed_count} files could not be cleared (may be in use)."
        else:
            return False, f"Could not clear any log files. All {total_files} files may be in use by another process."
            
    except Exception as e:
        return False, f"Error clearing logs: {str(e)}"


def delete_logs():
    """Delete all log files."""
    import os
    
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return False, "No logs directory found."
        
        # Count files before deletion
        total_files = 0
        total_size = 0
        deleted_files = 0
        deleted_size = 0
        failed_files = []
        
        # Delete files in main logs directory
        for log_file in logs_dir.glob("*.log"):
            total_files += 1
            total_size += log_file.stat().st_size
            try:
                log_file.unlink()
                deleted_files += 1
                deleted_size += log_file.stat().st_size
            except (PermissionError, OSError) as e:
                failed_files.append(f"{log_file.name}: {str(e)}")
        
        # Delete files in agents subdirectory
        agents_dir = logs_dir / "agents"
        if agents_dir.exists():
            for log_file in agents_dir.glob("*.log"):
                total_files += 1
                total_size += log_file.stat().st_size
                try:
                    log_file.unlink()
                    deleted_files += 1
                    deleted_size += log_file.stat().st_size
                except (PermissionError, OSError) as e:
                    failed_files.append(f"agents/{log_file.name}: {str(e)}")
        
        # Create success message
        size_mb = deleted_size / (1024 * 1024)
        
        if deleted_files == total_files:
            return True, f"Successfully deleted all {deleted_files} log files ({size_mb:.1f} MB)."
        elif deleted_files > 0:
            failed_count = total_files - deleted_files
            return True, f"Deleted {deleted_files}/{total_files} log files ({size_mb:.1f} MB). {failed_count} files could not be deleted (may be in use)."
        else:
            # Try alternative approach: truncate files instead of deleting
            truncated_files = 0
            for log_file in logs_dir.glob("*.log"):
                try:
                    log_file.write_text("")  # Truncate to empty
                    truncated_files += 1
                except (PermissionError, OSError):
                    pass
            
            if agents_dir.exists():
                for log_file in agents_dir.glob("*.log"):
                    try:
                        log_file.write_text("")  # Truncate to empty
                        truncated_files += 1
                    except (PermissionError, OSError):
                        pass
            
            if truncated_files > 0:
                return True, f"Could not delete files (in use), but truncated {truncated_files}/{total_files} log files to empty."
            else:
                return False, f"Could not delete or truncate any log files. All {total_files} files may be in use by another process. Try stopping the application first."
            
    except Exception as e:
        return False, f"Error deleting logs: {str(e)}"


def display_log_viewer():
    """Display log viewer interface."""
    st.header("📋 Log Viewer")
    
    # Get available log files
    logs_dir = Path("logs")
    if not logs_dir.exists():
        st.info("No logs directory found.")
        return
    
    # Main log file
    main_log = logs_dir / "agent.log"
    agent_logs = []
    
    if main_log.exists():
        agent_logs.append(("Main Log", main_log))
    
    # Agent log files
    agents_dir = logs_dir / "agents"
    if agents_dir.exists():
        for log_file in agents_dir.glob("*.log"):
            agent_name = log_file.stem.replace("_", " ").title()
            agent_logs.append((agent_name, log_file))
    
    if not agent_logs:
        st.info("No log files found.")
        return
    
    # Log file selection
    selected_log_name, selected_log_path = st.selectbox(
        "Select Log File:",
        options=agent_logs,
        format_func=lambda x: f"{x[0]} ({x[1].stat().st_size / 1024 / 1024:.1f} MB)"
    )
    
    # Display log content
    if selected_log_path.exists():
        try:
            with open(selected_log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # Show last N lines
            lines = log_content.split('\n')
            num_lines = st.slider("Show last N lines:", min_value=10, max_value=1000, value=100)
            
            if len(lines) > num_lines:
                display_lines = lines[-num_lines:]
                st.info(f"Showing last {num_lines} lines of {len(lines)} total lines")
            else:
                display_lines = lines
            
            # Display log content
            st.text_area(
                f"Log Content - {selected_log_name}",
                value='\n'.join(display_lines),
                height=400,
                disabled=True
            )
            
            # Download button
            st.download_button(
                label=f"📥 Download {selected_log_name}",
                data=log_content,
                file_name=selected_log_path.name,
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Error reading log file: {str(e)}")
    else:
        st.error(f"Log file {selected_log_path} not found.")
    
    # Close button
    if st.button("❌ Close Log Viewer"):
        st.session_state.show_log_viewer = False
        st.rerun()


def display_sidebar():
    """Display the sidebar with configuration options."""
    st.sidebar.title("⚙️ Configuration")
    
    # Navigation
    st.sidebar.subheader("📱 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🚀 Main App", "🔧 Prompt Manager", "📚 RAG Documents", "⚙️ System Prompts"]
    )
    
    # Configure API key
    api_key_configured = configure_api_key()
    
    # Configure model selection (only if API key is configured)
    if api_key_configured:
        selected_model = configure_model_selection()
    else:
        selected_model = "gemini-2.5-flash-lite"  # Default model
    
    st.sidebar.subheader("Project Settings")
    output_dir = st.sidebar.text_input(
        "Output Directory",
        value="./generated_projects",
        help="Directory where generated files will be saved"
    )
    
    st.sidebar.subheader("Agent Settings")
    enable_logging = st.sidebar.checkbox("Enable Logging", value=True)
    
    # Log Management
    st.sidebar.subheader("📋 Log Management")
    
    # Show log file sizes
    logs_dir = Path("logs")
    if logs_dir.exists():
        total_size = 0
        log_files = []
        
        # Main log file
        main_log = logs_dir / "agent.log"
        if main_log.exists():
            size = main_log.stat().st_size
            total_size += size
            log_files.append(f"agent.log ({size / 1024 / 1024:.1f} MB)")
        
        # Agent log files
        agents_dir = logs_dir / "agents"
        if agents_dir.exists():
            for log_file in agents_dir.glob("*.log"):
                size = log_file.stat().st_size
                total_size += size
                log_files.append(f"{log_file.name} ({size / 1024 / 1024:.1f} MB)")
        
        if log_files:
            st.sidebar.write(f"**Total Log Size:** {total_size / 1024 / 1024:.1f} MB")
            with st.sidebar.expander("Log Files", expanded=False):
                for log_file in log_files:
                    st.write(f"• {log_file}")
    
    # Log viewer
    if st.sidebar.button("📋 View Latest Logs", type="secondary"):
        st.session_state.show_log_viewer = True
        st.rerun()
    
    # Delete logs button
    if not st.session_state.show_delete_confirm:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.sidebar.button("🗑️ Delete All Logs", type="secondary"):
                st.session_state.show_delete_confirm = True
                st.rerun()
        with col2:
            if st.sidebar.button("🧹 Clear Logs", type="secondary"):
                success, message = clear_logs()
                if success:
                    st.sidebar.success(message)
                else:
                    st.sidebar.error(message)
    else:
        st.sidebar.write("⚠️ **Confirm deletion:**")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.sidebar.button("✅ Confirm", type="primary"):
                success, message = delete_logs()
                if success:
                    st.sidebar.success(message)
                else:
                    st.sidebar.error(message)
                st.session_state.show_delete_confirm = False
                st.rerun()
        with col2:
            if st.sidebar.button("❌ Cancel", type="secondary"):
                st.session_state.show_delete_confirm = False
                st.rerun()
    
    st.sidebar.subheader("About")
    st.sidebar.info("""
    **AI Development Agent** is a multi-agent system that generates complete software projects from natural language descriptions.
    
    **Features:**
    - Requirements Analysis
    - Architecture Design
    - Code Generation
    - Test Generation
    - Documentation
    - Security Analysis
    - Prompt Management
    - RAG Document Management
    
    **Note:** Project names are automatically generated from your project description.
    """)
    
    return {
        'output_dir': output_dir,
        'enable_logging': enable_logging,
        'page': page,
        'selected_model': selected_model
    }


def display_project_input():
    """Display the project input section."""
    st.header("📋 Project Description")
    
    # Initialize session state for project context
    if 'project_context' not in st.session_state:
        st.session_state.project_context = ""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Use session state to maintain the text area value
        project_context = st.text_area(
            "Describe your project",
            value=st.session_state.project_context,
            height=400,
            placeholder="""📋 Example Project Descriptions - Copy and Modify These Templates

🎯 Simple Web Applications:

Personal Blog System:
"Create a personal blog application with user authentication, post creation and editing, comment system, and responsive design. Use Python Flask for the backend, SQLite for the database, and Bootstrap for the frontend. Include user registration, login/logout functionality, admin panel for managing posts and comments, search functionality, and social media sharing buttons."

Portfolio Website:
"Build a modern portfolio website with dynamic content management, project showcase, contact form, and blog section. Use React for the frontend, Node.js with Express for the backend, MongoDB for content storage, and AWS S3 for image hosting. Include responsive design, SEO optimization, and analytics tracking."

Recipe Management App:
"Develop a recipe management application where users can create, save, and share recipes. Use Django with PostgreSQL, implement user authentication, recipe categories, ingredient management, cooking instructions with step-by-step photos, rating system, and meal planning calendar."

📊 Business Applications:

Inventory Management System:
"Create a comprehensive inventory management system for a retail business. Use FastAPI with PostgreSQL, implement product catalog, stock tracking, supplier management, purchase orders, sales tracking, barcode scanning, reporting dashboard, and low stock alerts."

Customer Relationship Management (CRM):
"Build a CRM system for managing customer interactions, sales pipeline, and business opportunities. Use Node.js with Express, MongoDB for data storage, implement contact management, lead tracking, deal pipeline, email integration, task management, and reporting analytics."

Project Management Tool:
"Develop a project management application with task tracking, team collaboration, and progress monitoring. Use React for the frontend, Django REST Framework for the backend, PostgreSQL database, implement user roles, project boards, time tracking, file sharing, and real-time notifications."

🛒 E-commerce Solutions:

Online Store Platform:
"Create a full-featured e-commerce platform with product catalog, shopping cart, payment processing, and order management. Use FastAPI with PostgreSQL, implement user authentication, product categories, inventory management, Stripe payment integration, order tracking, and admin dashboard."

Marketplace Application:
"Build a marketplace platform connecting buyers and sellers. Use Django with PostgreSQL, implement user registration, product listings, messaging system, review system, payment escrow, dispute resolution, and analytics dashboard."

Subscription Service:
"Develop a subscription management platform with recurring billing, user management, and content delivery. Use Node.js with Express, MongoDB, implement subscription plans, payment processing with Stripe, content access control, usage analytics, and automated billing."

📱 Mobile App Backends:

Fitness Tracking API:
"Create a backend API for a fitness tracking mobile app. Use Django REST Framework with PostgreSQL, implement user profiles, workout tracking, progress analytics, social features, push notifications, data visualization endpoints, and comprehensive API documentation."

Food Delivery Service:
"Build a backend for a food delivery app connecting restaurants, drivers, and customers. Use FastAPI with PostgreSQL, implement restaurant management, order processing, real-time tracking, driver assignment, payment processing, and notification system."

Social Media Platform:
"Develop a social media platform backend with user profiles, posts, comments, likes, follows, and messaging. Use Node.js with Express, MongoDB for data storage, implement real-time notifications, content moderation, hashtag system, and analytics."

🏥 Healthcare Applications:

Patient Management System:
"Create a patient management system for a medical clinic. Use Django with PostgreSQL, implement patient records, appointment scheduling, medical history tracking, prescription management, billing integration, and HIPAA compliance features."

Telemedicine Platform:
"Build a telemedicine platform connecting patients and healthcare providers. Use FastAPI with PostgreSQL, implement video consultations, appointment scheduling, medical records, prescription management, payment processing, and secure messaging."

Health Monitoring Dashboard:
"Develop a health monitoring dashboard for tracking vital signs and health metrics. Use React frontend, Node.js backend, MongoDB database, implement data visualization, alert systems, trend analysis, and integration with wearable devices."

🎓 Educational Platforms:

Learning Management System (LMS):
"Create a comprehensive LMS for online education. Use Django with PostgreSQL, implement course management, student enrollment, assignment submission, grading system, discussion forums, video streaming, and progress tracking."

Tutoring Platform:
"Build a platform connecting students with tutors for online learning. Use FastAPI with PostgreSQL, implement user matching, scheduling system, video conferencing, payment processing, progress tracking, and review system."

Skill Assessment Platform:
"Develop a platform for creating and taking skill assessments. Use Node.js with Express, MongoDB, implement quiz creation, automated grading, performance analytics, certificate generation, and adaptive learning algorithms."

🏢 Enterprise Solutions:

Employee Management System:
"Create an HR management system for employee records, payroll, and performance tracking. Use Django with PostgreSQL, implement employee profiles, time tracking, leave management, performance reviews, payroll integration, and reporting."

Document Management System:
"Build a document management system with version control, collaboration, and search capabilities. Use FastAPI with PostgreSQL, implement file upload, version tracking, collaborative editing, search functionality, access control, and audit logging."

Business Intelligence Dashboard:
"Develop a BI dashboard for data visualization and business analytics. Use React frontend, Node.js backend, PostgreSQL database, implement data connectors, interactive charts, custom reports, user permissions, and automated data refresh."

🔧 Developer Tools:

API Gateway:
"Create an API gateway for managing multiple microservices. Use FastAPI with Redis, implement request routing, rate limiting, authentication, logging, monitoring, load balancing, and API documentation."

Code Review Platform:
"Build a platform for code review and collaboration. Use Django with PostgreSQL, implement repository integration, pull request management, code commenting, automated testing, and review analytics."

Deployment Automation Tool:
"Develop a tool for automating application deployment and infrastructure management. Use Node.js with Express, implement deployment pipelines, environment management, monitoring integration, rollback capabilities, and deployment analytics."

🎮 Gaming Applications:

Multiplayer Game Backend:
"Create a backend for a multiplayer online game. Use Node.js with Socket.io, Redis for real-time data, implement user authentication, game state management, matchmaking, leaderboards, and real-time communication."

Gaming Tournament Platform:
"Build a platform for organizing and managing gaming tournaments. Use FastAPI with PostgreSQL, implement tournament creation, player registration, bracket management, match scheduling, results tracking, and prize distribution."

Game Analytics Dashboard:
"Develop a dashboard for analyzing gaming data and player behavior. Use React frontend, Node.js backend, MongoDB database, implement data collection, player analytics, performance metrics, and predictive modeling."

🚀 Advanced Projects:

Machine Learning Platform:
"Build a machine learning platform with data preprocessing, model training, evaluation, and deployment capabilities. Use Python with FastAPI, scikit-learn, TensorFlow, implement data pipelines, model versioning, automated training, and API deployment."

Blockchain Application:
"Create a decentralized application (DApp) using blockchain technology. Use Solidity for smart contracts, Web3.js for frontend integration, implement token management, transaction tracking, and decentralized storage."

IoT Dashboard:
"Develop an IoT dashboard for monitoring and controlling smart devices. Use React frontend, Node.js backend, MongoDB database, implement device management, real-time data visualization, alert systems, and mobile app integration."

Microservices Architecture:
"Create a microservices-based e-commerce system with separate services for user management, product catalog, order processing, and payment handling. Use Docker containers, Kubernetes orchestration, message queues, and service discovery."

Real-time Collaboration Platform:
"Build a real-time collaboration platform similar to Google Docs. Use React frontend, Node.js with Socket.io backend, MongoDB database, implement real-time editing, user presence, conflict resolution, and document versioning."

AI-Powered Chatbot Platform:
"Create a platform for building and deploying AI chatbots. Use FastAPI with PostgreSQL, implement natural language processing, conversation management, integration APIs, analytics dashboard, and multi-channel support."

📋 How to Use These Templates:

1. Copy one of the example descriptions above
2. Modify it to match your specific requirements
3. Add or remove features as needed
4. Specify your preferred technology stack
5. Include any specific business rules or constraints
6. Add performance and scalability requirements
7. Specify security and compliance needs
8. Include deployment preferences

💡 Tips for Customization:

• Replace generic terms with your specific domain
• Add your unique business requirements
• Specify exact features you need
• Include integration requirements
• Mention performance expectations
• Add security requirements
• Specify user roles and permissions
• Include reporting and analytics needs

Start by copying and modifying one of these templates to describe your project!""",
            help="Describe your project requirements in detail. Be specific about features, technology preferences, and requirements.",
            key="project_text_area"
        )
        
        # Update session state with current value
        st.session_state.project_context = project_context
    
    with col2:
        st.subheader("💡 Tips")
        st.markdown("""
        **Be specific about:**
        - Technology stack preferences
        - Database requirements
        - Authentication needs
        - API endpoints needed
        - Testing requirements
        - Deployment preferences
        """)
        
        st.subheader("🎯 Example Projects")
        col2_1, col2_2 = st.columns(2)
        
        with col2_1:
            if st.button("🚀 Simple Project", key="simple_btn"):
                st.session_state.project_context = """Create a simple Python application with the following features:
- Basic CRUD operations
- Simple file-based storage
- Command-line interface
- Basic error handling
- Simple logging
- Basic documentation
- No external dependencies beyond standard library
- Easy to understand and modify code"""
                st.rerun()
            
            if st.button("📝 Todo API", key="todo_btn"):
                st.session_state.project_context = """Create a comprehensive Todo API with the following features:
- User registration and authentication using JWT tokens
- CRUD operations for todo items (Create, Read, Update, Delete)
- Todo categories and priority levels
- Due date management and reminders
- User-specific todo lists
- RESTful API with proper HTTP status codes
- PostgreSQL database with SQLAlchemy ORM
- Input validation and error handling
- Comprehensive API documentation
- Unit tests and integration tests
- Docker containerization
- Environment configuration management"""
                st.rerun()
            
            if st.button("👥 User Management", key="user_btn"):
                st.session_state.project_context = """Create a User Management System with the following features:
- User registration with email verification
- Role-based access control (Admin, User, Moderator)
- Password reset functionality
- User profile management
- Account activation/deactivation
- Session management
- Audit logging for user actions
- RESTful API with FastAPI
- PostgreSQL database with migrations
- JWT authentication
- Rate limiting and security headers
- Comprehensive testing suite
- API documentation with examples"""
                st.rerun()
        
        with col2_2:
            if st.button("🛒 E-commerce API", key="ecommerce_btn"):
                st.session_state.project_context = """Create an E-commerce API with the following features:
- Product catalog with categories and search
- Shopping cart functionality
- User authentication and profiles
- Order management and tracking
- Payment integration (stripe/paypal)
- Inventory management
- Product reviews and ratings
- Discount codes and promotions
- Shipping calculation
- Admin dashboard endpoints
- RESTful API with FastAPI
- PostgreSQL database with complex relationships
- Redis for caching
- Comprehensive testing
- API documentation with Swagger UI"""
                st.rerun()
            
            if st.button("🗑️ Clear", key="clear_btn"):
                st.session_state.project_context = ""
                st.rerun()
    
    return st.session_state.project_context


def display_workflow_execution(agent, project_context, config):
    """Display the workflow execution section."""
    st.header("🔄 Workflow Execution")
    
    if st.button("🚀 Start Development Workflow", type="primary", disabled=st.session_state.is_running):
        if not project_context.strip():
            st.error("Please provide a project description before starting the workflow.")
            return
        
        st.session_state.is_running = True
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Execute workflow
            status_text.text("Initializing AI Development Agent...")
            progress_bar.progress(10)
            
            status_text.text("Analyzing requirements...")
            progress_bar.progress(20)
            
            status_text.text("Designing architecture...")
            progress_bar.progress(40)
            
            status_text.text("Generating code...")
            progress_bar.progress(60)
            
            status_text.text("Creating tests...")
            progress_bar.progress(80)
            
            status_text.text("Generating documentation...")
            progress_bar.progress(90)
            
            # Run the actual workflow
            result = asyncio.run(agent.execute_workflow(
                project_context=project_context,
                output_dir=config['output_dir']
            ))
            
            st.session_state.workflow_result = result
            progress_bar.progress(100)
            status_text.text("✅ Workflow completed successfully!")
            
            # Display success message
            st.success("🎉 Project generated successfully!")
            
        except Exception as e:
            st.error(f"❌ Workflow failed: {str(e)}")
            progress_bar.progress(0)
        finally:
            st.session_state.is_running = False


def display_results():
    """Display the workflow results."""
    if st.session_state.workflow_result is None:
        return
    
    result = st.session_state.workflow_result
    
    st.header("📊 Results")
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Status", result.status.value)
    
    with col2:
        st.metric("Execution Time", f"{result.total_execution_time:.2f}s")
    
    with col3:
        st.metric("Generated Files", len(result.generated_files))
    
    with col4:
        diagram_count = len(result.diagram_files) if hasattr(result, 'diagram_files') else 0
        st.metric("Diagrams", diagram_count)
    
    with col5:
        st.metric("Project Name", result.project_name)
    
    # Agent documentation summary
    if result.agent_results:
        st.subheader("📊 Agent Documentation Summary")
        agent_summary_data = []
        
        for agent_name, agent_result in result.agent_results.items():
            doc = agent_result.documentation
            if isinstance(doc, dict):
                summary = doc.get('summary', 'No summary available')
                agent_summary_data.append({
                    "Agent": agent_name,
                    "Summary": summary[:100] + "..." if len(summary) > 100 else summary,
                    "Log Entries": len(agent_result.logs),
                    "Decisions": len(agent_result.decisions),
                    "Artifacts": len(agent_result.artifacts),
                    "Execution Time": f"{agent_result.execution_time:.2f}s"
                })
        
        if agent_summary_data:
            import pandas as pd
            df = pd.DataFrame(agent_summary_data)
            st.dataframe(df, use_container_width=True)
    
    # Detailed results
    st.subheader("📁 Generated Files")
    
    # Code files
    if result.code_files:
        with st.expander("💻 Source Code", expanded=True):
            for file_path, content in result.code_files.items():
                st.markdown(f"**{file_path}**")
                st.code(content, language='python')
    
    # Test files
    if result.test_files:
        with st.expander("🧪 Test Files", expanded=False):
            for file_path, content in result.test_files.items():
                st.markdown(f"**{file_path}**")
                st.code(content, language='python')
    
    # Documentation files
    if result.documentation_files:
        with st.expander("📚 Documentation", expanded=False):
            for file_path, content in result.documentation_files.items():
                st.markdown(f"**{file_path}**")
                st.markdown(content)
    
    # Configuration files
    if result.configuration_files:
        with st.expander("⚙️ Configuration Files", expanded=False):
            for file_path, content in result.configuration_files.items():
                st.markdown(f"**{file_path}**")
                st.code(content, language='text')
    
    # Diagram files
    if hasattr(result, 'diagram_files') and result.diagram_files:
        with st.expander("📊 Diagrams", expanded=False):
            for file_path, content in result.diagram_files.items():
                st.markdown(f"**{file_path}**")
                
                # Determine the language based on file extension
                if file_path.endswith('.puml'):
                    st.code(content, language='plantuml')
                elif file_path.endswith('.bpmn'):
                    st.code(content, language='xml')
                elif file_path.endswith('.md'):
                    st.markdown(content)
                else:
                    st.code(content, language='text')
                
                # Add download button for diagram files
                st.download_button(
                    label=f"📥 Download {file_path}",
                    data=content,
                    file_name=file_path,
                    mime="text/plain"
                )
    
    # Agent results with enhanced documentation
    if result.agent_results:
        st.subheader("🤖 Agent Results & Documentation")
        for agent_name, agent_result in result.agent_results.items():
            with st.expander(f"Agent: {agent_name}", expanded=False):
                # Agent summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", agent_result.status.value)
                with col2:
                    st.metric("Execution Time", f"{agent_result.execution_time:.2f}s")
                with col3:
                    st.metric("Log Entries", len(agent_result.logs))
                
                # Documentation summary
                if agent_result.documentation:
                    st.subheader("📋 Documentation")
                    doc = agent_result.documentation
                    if isinstance(doc, dict):
                        st.write(f"**Summary:** {doc.get('summary', 'No summary available')}")
                        
                        # Key details
                        details = doc.get('details', {})
                        if details:
                            st.write("**Key Details:**")
                            for key, value in details.items():
                                if isinstance(value, dict):
                                    st.write(f"- **{key.replace('_', ' ').title()}:**")
                                    for sub_key, sub_value in value.items():
                                        st.write(f"  - {sub_key.replace('_', ' ').title()}: {sub_value}")
                                else:
                                    st.write(f"- **{key.replace('_', ' ').title()}:** {value}")
                
                # Execution logs
                if agent_result.logs:
                    st.subheader("📝 Execution Logs")
                    for log_entry in agent_result.logs:
                        if isinstance(log_entry, dict):
                            timestamp = log_entry.get('timestamp', 'Unknown')
                            level = log_entry.get('level', 'info')
                            message = log_entry.get('message', 'No message')
                            
                            # Color code by log level
                            if level == 'error':
                                st.error(f"**{timestamp}** [{level.upper()}] {message}")
                            elif level == 'warning':
                                st.warning(f"**{timestamp}** [{level.upper()}] {message}")
                            elif level == 'debug':
                                st.text(f"**{timestamp}** [{level.upper()}] {message}")
                            else:
                                st.info(f"**{timestamp}** [{level.upper()}] {message}")
                
                # Key decisions
                if agent_result.decisions:
                    st.subheader("🎯 Key Decisions")
                    for decision in agent_result.decisions:
                        if isinstance(decision, dict):
                            st.write(f"**{decision.get('decision', 'Unknown decision')}**")
                            st.write(f"*Rationale:* {decision.get('rationale', 'No rationale provided')}")
                            if decision.get('alternatives'):
                                st.write(f"*Alternatives considered:* {', '.join(decision['alternatives'])}")
                            if decision.get('impact'):
                                st.write(f"*Impact:* {decision['impact']}")
                            st.write("---")
                
                # Artifacts created
                if agent_result.artifacts:
                    st.subheader("📦 Artifacts Created")
                    for i, artifact in enumerate(agent_result.artifacts):
                        if isinstance(artifact, dict):
                            st.write(f"**{artifact.get('name', 'Unknown')}** ({artifact.get('type', 'unknown type')})")
                            st.write(f"*Description:* {artifact.get('description', 'No description')}")
                            if artifact.get('content'):
                                # Use a checkbox to toggle content visibility
                                # Make key unique by including agent name and artifact index
                                unique_key = f"show_artifact_{agent_name}_{i}"
                                show_content = st.checkbox(f"Show content for {artifact.get('name', 'Unknown')}", key=unique_key)
                                if show_content:
                                    st.json(artifact['content'])
                            st.write("---")
    
    # Raw output section (outside agent expanders to avoid nesting)
    if result.agent_results:
        st.subheader("🔧 Raw Agent Outputs")
        for agent_name, agent_result in result.agent_results.items():
            with st.expander(f"Raw Output: {agent_name}", expanded=False):
                st.json(agent_result.output)
    
    # Download section
    st.subheader("💾 Download Project")
    
    if st.button("📦 Download Project Files"):
        # Create a zip file of the generated project
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all generated files to the zip
            all_files = {
                **result.code_files,
                **result.test_files,
                **result.documentation_files,
                **result.configuration_files
            }
            
            # Add diagram files if they exist
            if hasattr(result, 'diagram_files') and result.diagram_files:
                all_files.update(result.diagram_files)
            
            for file_path, content in all_files.items():
                zip_file.writestr(file_path, content)
        
        zip_buffer.seek(0)
        
        st.download_button(
            label="📥 Download ZIP",
            data=zip_buffer.getvalue(),
            file_name=f"{result.project_name}.zip",
            mime="application/zip"
        )


def delete_generated_project(project_name: str):
    """Delete a generated project from the filesystem."""
    try:
        project_path = Path("generated_projects") / project_name
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)
            return True, f"Project '{project_name}' deleted successfully."
        else:
            return False, f"Project '{project_name}' not found."
    except Exception as e:
        return False, f"Error deleting project: {str(e)}"


def list_generated_projects():
    """List all generated projects."""
    projects_path = Path("generated_projects")
    if not projects_path.exists():
        return []
    
    projects = []
    for project_dir in projects_path.iterdir():
        if project_dir.is_dir():
            projects.append({
                "name": project_dir.name,
                "created": datetime.fromtimestamp(project_dir.stat().st_ctime),
                "size": sum(f.stat().st_size for f in project_dir.rglob('*') if f.is_file())
            })
    return sorted(projects, key=lambda x: x["created"], reverse=True)


def display_project_management():
    """Display project management interface."""
    st.header("🗂️ Project Management")
    
    # List existing projects
    projects = list_generated_projects()
    
    if not projects:
        st.info("No generated projects found.")
        return
    
    st.subheader("📁 Generated Projects")
    
    for project in projects:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.write(f"**{project['name']}**")
        
        with col2:
            st.write(f"Created: {project['created'].strftime('%Y-%m-%d %H:%M')}")
        
        with col3:
            size_mb = project['size'] / (1024 * 1024)
            st.write(f"Size: {size_mb:.1f} MB")
        
        with col4:
            if st.button(f"🗑️ Delete", key=f"delete_{project['name']}"):
                success, message = delete_generated_project(project['name'])
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def display_project_info():
    """Display project information and statistics."""
    st.header("📈 Project Statistics")
    
    if st.session_state.workflow_result is None:
        st.info("No project has been generated yet. Start a workflow to see statistics.")
        return
    
    result = st.session_state.workflow_result
    
    # Project overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Project Overview")
        st.write(f"**Project Name:** {result.project_name}")
        st.write(f"**Status:** {result.status.value}")
        st.write(f"**Execution Time:** {result.total_execution_time:.2f} seconds")
        st.write(f"**Generated Files:** {len(result.generated_files)}")
        
        if result.start_time:
            st.write(f"**Started:** {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if result.end_time:
            st.write(f"**Completed:** {result.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        st.subheader("📊 File Breakdown")
        
        file_types = {
            "Source Code": len(result.code_files),
            "Test Files": len(result.test_files),
            "Documentation": len(result.documentation_files),
            "Configuration": len(result.configuration_files)
        }
        
        for file_type, count in file_types.items():
            st.write(f"**{file_type}:** {count} files")
    
    # Errors and warnings
    if result.errors:
        st.subheader("⚠️ Errors")
        for error in result.errors:
            st.error(f"Error: {error}")
    
    if result.warnings:
        st.subheader("⚠️ Warnings")
        for warning in result.warnings:
            st.warning(f"Warning: {warning}")


def display_prompt_manager():
    """Display the prompt manager interface."""
    st.header("🔧 Prompt Manager")
    
    # Initialize components
    prompt_editor = get_prompt_editor()
    
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


def display_system_prompts():
    """Display system prompts management."""
    st.header("⚙️ System Prompts")
    
    # Initialize components
    prompt_editor = get_prompt_editor()
    
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
    
    # Add new system prompt
    st.subheader("➕ Create New System Prompt")
    
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
                    st.rerun()
                else:
                    st.error("Failed to create system prompt.")
            else:
                st.error("Please provide both name and template.")


def display_rag_documents():
    """Display RAG documents management."""
    st.header("📚 RAG Documents")
    
    # Initialize components
    prompt_editor = get_prompt_editor()
    rag_processor = get_rag_processor()
    
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
    
    # Add new RAG documents
    st.subheader("➕ Add RAG Documents")
    
    # Tabs for different content types
    tab1, tab2 = st.tabs(["🌐 URL Document", "📁 File Document"])
    
    with tab1:
        st.subheader("Add URL Document")
        
        # URL processing form
        with st.form("new_url_document"):
            url = st.text_input("URL:")
            agent_name = st.selectbox("Associated Agent (optional):", 
                                    ["None"] + ["requirements_analyst", "architecture_designer", "code_generator",
                                               "test_generator", "code_reviewer", "security_analyst", "documentation_generator"])
            tags = st.text_input("Tags (comma-separated):")
            
            submitted = st.form_submit_button("Process URL")
        
        # Handle form submission outside the form
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
                        
                        # Store data in session state for the button
                        st.session_state.url_doc_data = {
                            'title': result['title'],
                            'content': result['content'],
                            'url': url,
                            'agent_name': agent_name,
                            'tags': tags
                        }
                        
                        # Add to database button (outside form)
                        if st.button("Add to Database", key="add_url_doc"):
                            data = st.session_state.url_doc_data
                            agent = None if data['agent_name'] == "None" else data['agent_name']
                            tag_list = [tag.strip() for tag in data['tags'].split(",")] if data['tags'] else []
                            
                            doc_id = prompt_editor.add_rag_document(
                                data['title'], data['content'], 'url',
                                source_url=data['url'], agent_name=agent, tags=tag_list
                            )
                            
                            if doc_id > 0:
                                st.success(f"Document added with ID: {doc_id}")
                                # Clear session state
                                if 'url_doc_data' in st.session_state:
                                    del st.session_state.url_doc_data
                                st.rerun()
                            else:
                                st.error("Failed to add document to database.")
                    else:
                        st.error(f"Failed to process URL: {result['content']}")
            else:
                st.error("Invalid or inaccessible URL.")
    
    with tab2:
        st.subheader("Add File Document")
        
        # File processing form
        with st.form("new_file_document"):
            uploaded_file = st.file_uploader("Choose a file:", 
                                           type=['txt', 'md', 'py', 'js', 'html', 'css', 'json'])
            agent_name = st.selectbox("Associated Agent (optional):", 
                                    ["None"] + ["requirements_analyst", "architecture_designer", "code_generator",
                                               "test_generator", "code_reviewer", "security_analyst", "documentation_generator"])
            tags = st.text_input("Tags (comma-separated):")
            
            submitted = st.form_submit_button("Process File")
        
        # Handle form submission outside the form
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
            
            # Store data in session state for the button
            st.session_state.file_doc_data = {
                'filename': uploaded_file.name,
                'content': content,
                'agent_name': agent_name,
                'tags': tags
            }
            
            # Add to database button (outside form)
            if st.button("Add to Database", key="add_file_doc"):
                data = st.session_state.file_doc_data
                agent = None if data['agent_name'] == "None" else data['agent_name']
                tag_list = [tag.strip() for tag in data['tags'].split(",")] if data['tags'] else []
                
                doc_id = prompt_editor.add_rag_document(
                    data['filename'], data['content'], 'file',
                    file_path=data['filename'], agent_name=agent, tags=tag_list
                )
                
                if doc_id > 0:
                    st.success(f"Document added with ID: {doc_id}")
                    # Clear session state
                    if 'file_doc_data' in st.session_state:
                        del st.session_state.file_doc_data
                    st.rerun()
                else:
                    st.error("Failed to add document to database.")


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    display_header()
    
    # Get configuration from sidebar (includes API key configuration)
    config = display_sidebar()
    
    # Check if API key is configured
    if not st.session_state.api_key_configured:
        st.warning("⚠️ Please configure your Gemini API key to use the application.")
        st.stop()
    
    # Handle different pages
    if config['page'] == "🚀 Main App":
        # Create agent
        agent = create_agent()
        
        # Main content
        project_context = display_project_input()
        
        # Workflow execution
        display_workflow_execution(agent, project_context, config)
        
        # Display results if available
        if st.session_state.workflow_result is not None:
            display_results()
            display_project_info()
        
        # Project management section
        display_project_management()
        
    elif config['page'] == "🔧 Prompt Manager":
        display_prompt_manager()
        
    elif config['page'] == "📚 RAG Documents":
        display_rag_documents()
        
    elif config['page'] == "⚙️ System Prompts":
        display_system_prompts()
    
    # Log viewer (if activated from sidebar)
    if st.session_state.show_log_viewer:
        display_log_viewer()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🚀 AI Development Agent - Powered by LangGraph and Gemini API</p>
            <p>Generate complete software projects with AI-powered agents</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
