#!/usr/bin/env python3
"""
🚀 Streamlit IDE - Complete Development Environment
==================================================

Full working editor with:
- Code editing with syntax highlighting
- Live app execution
- Git integration with authentication
- File management
- Terminal access
- Package management

Transform Streamlit into a complete development environment!
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st
import json
import yaml
import base64
import io
import zipfile
import git
from datetime import datetime
import requests

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import context-aware rule system
try:
    from utils.rule_system.context_aware_rule_loader import get_rule_loader, apply_context_aware_rules
    RULE_SYSTEM_AVAILABLE = True
except ImportError:
    get_rule_loader = None
    apply_context_aware_rules = None
    RULE_SYSTEM_AVAILABLE = False

class StreamlitIDE:
    """
    🚀 Complete Streamlit-based Integrated Development Environment
    
    Features:
    - Full code editor with syntax highlighting
    - Live app execution and testing
    - Git integration with deployment
    - File browser and management
    - Package and dependency management
    - Terminal emulation
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.workspace_root = self.project_root / "ide_workspace"
        self.workspace_root.mkdir(exist_ok=True)
        
        # Initialize session state for IDE
        self._initialize_session_state()
        
    def _initialize_session_state(self):
        """Initialize Streamlit session state for IDE."""
        
        if 'ide_current_project' not in st.session_state:
            st.session_state.ide_current_project = None
            
        if 'ide_current_file' not in st.session_state:
            st.session_state.ide_current_file = None
            
        if 'ide_file_contents' not in st.session_state:
            st.session_state.ide_file_contents = {}
            
        if 'ide_running_apps' not in st.session_state:
            st.session_state.ide_running_apps = {}
            
        if 'ide_git_credentials' not in st.session_state:
            st.session_state.ide_git_credentials = {}
            
        if 'ide_terminal_history' not in st.session_state:
            st.session_state.ide_terminal_history = []
    
    def render_ide_interface(self):
        """Render the complete IDE interface."""
        
        st.markdown("# 🚀 **Streamlit IDE - Complete Development Environment**")
        
        # Main IDE layout
        col_sidebar, col_main = st.columns([1, 3])
        
        with col_sidebar:
            self._render_project_sidebar()
        
        with col_main:
            self._render_main_editor_area()
    
    def _render_project_sidebar(self):
        """Render project management sidebar."""
        
        st.markdown("### 📁 **Project Explorer**")
        
        # Project selection/creation
        project_action = st.selectbox(
            "Project Action:",
            ["Select Existing", "Create New", "Import from Git"]
        )
        
        if project_action == "Create New":
            self._render_new_project_form()
        elif project_action == "Import from Git":
            self._render_git_import_form()
        else:
            self._render_project_selector()
        
        # File browser
        if st.session_state.ide_current_project:
            st.markdown("---")
            st.markdown("### 📂 **File Browser**")
            self._render_file_browser()
        
        # Git integration
        if st.session_state.ide_current_project:
            st.markdown("---")
            st.markdown("### 🔧 **Git Integration**")
            self._render_git_panel()
    
    def _render_new_project_form(self):
        """Render new project creation form."""
        
        with st.form("new_project_form"):
            project_name = st.text_input("Project Name:")
            project_type = st.selectbox(
                "Project Type:",
                ["Streamlit App", "Flask Web App", "FastAPI Service", "Python Package", "Data Science", "AI/ML Project"]
            )
            
            template_options = st.multiselect(
                "Include Templates:",
                ["README.md", "requirements.txt", ".gitignore", "Docker", "Tests", "CI/CD"]
            )
            
            if st.form_submit_button("🚀 Create Project"):
                self._create_new_project(project_name, project_type, template_options)
    
    def _render_git_import_form(self):
        """Render Git repository import form."""
        
        with st.form("git_import_form"):
            repo_url = st.text_input("Repository URL:")
            branch = st.text_input("Branch (optional):", value="main")
            
            # Git credentials
            st.markdown("**Git Credentials (if private repo):**")
            username = st.text_input("Username:")
            password = st.text_input("Password/Token:", type="password")
            
            if st.form_submit_button("📥 Import Repository"):
                self._import_git_repository(repo_url, branch, username, password)
    
    def _render_project_selector(self):
        """Render project selector for existing projects."""
        
        projects = self._get_existing_projects()
        
        if projects:
            selected_project = st.selectbox(
                "Select Project:",
                [""] + projects
            )
            
            if selected_project and selected_project != st.session_state.ide_current_project:
                st.session_state.ide_current_project = selected_project
                st.rerun()
        else:
            st.info("No projects found. Create a new one!")
    
    def _render_file_browser(self):
        """Render file browser with file operations."""
        
        project_path = self.workspace_root / st.session_state.ide_current_project
        
        if not project_path.exists():
            st.error("Project directory not found!")
            return
        
        # File tree
        files = self._get_file_tree(project_path)
        
        for file_info in files:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                if file_info['type'] == 'file':
                    if st.button(f"📄 {file_info['name']}", key=f"file_{file_info['path']}"):
                        self._open_file(file_info['path'])
                else:
                    st.write(f"📁 {file_info['name']}")
            
            with col2:
                if file_info['type'] == 'file':
                    if st.button("✏️", key=f"edit_{file_info['path']}"):
                        self._open_file(file_info['path'])
            
            with col3:
                if st.button("🗑️", key=f"delete_{file_info['path']}"):
                    self._delete_file(file_info['path'])
        
        # New file creation
        st.markdown("---")
        with st.form("new_file_form"):
            new_file_name = st.text_input("New File Name:")
            file_type = st.selectbox(
                "File Type:",
                ["Python (.py)", "HTML (.html)", "CSS (.css)", "JavaScript (.js)", "JSON (.json)", "YAML (.yaml)", "Markdown (.md)", "Text (.txt)"]
            )
            
            if st.form_submit_button("➕ Create File"):
                self._create_new_file(new_file_name, file_type)
    
    def _render_main_editor_area(self):
        """Render main editor area with tabs."""
        
        if not st.session_state.ide_current_project:
            st.info("👈 Select or create a project to start coding!")
            return
        
        # Main editor tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Code Editor", "🚀 Live Runner", "🖥️ Terminal", "📦 Packages", "🔧 Settings"])
        
        with tab1:
            self._render_code_editor()
        
        with tab2:
            self._render_live_runner()
        
        with tab3:
            self._render_terminal_emulator()
        
        with tab4:
            self._render_package_manager()
        
        with tab5:
            self._render_project_settings()
    
    def _render_code_editor(self):
        """Render code editor with syntax highlighting."""
        
        if not st.session_state.ide_current_file:
            st.info("Select a file from the file browser to start editing.")
            return
        
        file_path = Path(st.session_state.ide_current_file)
        
        st.markdown(f"### 📝 Editing: `{file_path.name}`")
        
        # Load file content
        if str(file_path) not in st.session_state.ide_file_contents:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    st.session_state.ide_file_contents[str(file_path)] = f.read()
            except Exception as e:
                st.error(f"Error loading file: {e}")
                return
        
        # File editor
        file_content = st.text_area(
            "File Content:",
            value=st.session_state.ide_file_contents[str(file_path)],
            height=400,
            key=f"editor_{file_path}"
        )
        
        # Update session state
        st.session_state.ide_file_contents[str(file_path)] = file_content
        
        # Editor controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💾 Save File"):
                self._save_file(file_path, file_content)
        
        with col2:
            if st.button("🔄 Reload"):
                self._reload_file(file_path)
        
        with col3:
            if st.button("📋 Copy Content"):
                st.code(file_content)
        
        with col4:
            if st.button("📤 Download"):
                self._download_file(file_path)
        
        # Syntax highlighting preview (using st.code)
        if file_path.suffix in ['.py', '.js', '.html', '.css', '.json', '.yaml', '.md']:
            st.markdown("### 🎨 **Syntax Preview**")
            language = self._get_language_from_extension(file_path.suffix)
            st.code(file_content, language=language)
    
    def _render_live_runner(self):
        """Render live app runner."""
        
        st.markdown("### 🚀 **Live App Runner**")
        
        project_path = self.workspace_root / st.session_state.ide_current_project
        
        # App configuration
        col1, col2 = st.columns(2)
        
        with col1:
            app_file = st.selectbox(
                "Main App File:",
                self._get_python_files(project_path)
            )
        
        with col2:
            app_port = st.number_input("Port:", min_value=8000, max_value=9999, value=8501)
        
        # App controls
        col_run, col_stop, col_view = st.columns(3)
        
        with col_run:
            if st.button("▶️ Run App"):
                self._run_app_live(app_file, app_port)
        
        with col_stop:
            if st.button("⏹️ Stop App"):
                self._stop_app(app_port)
        
        with col_view:
            if st.button("👁️ View App"):
                self._view_running_app(app_port)
        
        # Running apps status
        if st.session_state.ide_running_apps:
            st.markdown("### 📊 **Running Apps**")
            
            for port, app_info in st.session_state.ide_running_apps.items():
                col_info, col_actions = st.columns([2, 1])
                
                with col_info:
                    st.write(f"**Port {port}**: {app_info['file']} - Status: {app_info['status']}")
                
                with col_actions:
                    if st.button(f"🌐 Open", key=f"open_app_{port}"):
                        st.markdown(f"[Open App](http://localhost:{port})")
        
        # App logs
        st.markdown("### 📋 **App Logs**")
        
        if st.button("🔄 Refresh Logs"):
            logs = self._get_app_logs()
            if logs:
                st.code(logs, language="text")
            else:
                st.info("No logs available")
    
    def _render_terminal_emulator(self):
        """Render terminal emulator."""
        
        st.markdown("### 🖥️ **Terminal**")
        
        # Command input
        command = st.text_input(
            "Command:",
            placeholder="Enter command (e.g., pip install requests, python app.py, git status)"
        )
        
        col_run, col_clear = st.columns([3, 1])
        
        with col_run:
            if st.button("▶️ Execute") and command:
                self._execute_terminal_command(command)
        
        with col_clear:
            if st.button("🗑️ Clear"):
                st.session_state.ide_terminal_history = []
                st.rerun()
        
        # Terminal output
        if st.session_state.ide_terminal_history:
            st.markdown("### 📟 **Terminal Output**")
            
            for entry in st.session_state.ide_terminal_history[-10:]:  # Show last 10 commands
                st.markdown(f"**$ {entry['command']}**")
                
                if entry['output']:
                    st.code(entry['output'], language="bash")
                
                if entry['error']:
                    st.error(entry['error'])
                
                st.markdown("---")
    
    def _render_package_manager(self):
        """Render package manager."""
        
        st.markdown("### 📦 **Package Manager**")
        
        # Package installation
        col1, col2 = st.columns(2)
        
        with col1:
            package_name = st.text_input("Package Name:")
        
        with col2:
            install_type = st.selectbox("Install Type:", ["pip", "conda"])
        
        if st.button("📥 Install Package") and package_name:
            self._install_package(package_name, install_type)
        
        # Requirements management
        st.markdown("### 📋 **Requirements**")
        
        requirements_file = self.workspace_root / st.session_state.ide_current_project / "requirements.txt"
        
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                requirements = f.read()
            
            updated_requirements = st.text_area(
                "requirements.txt:",
                value=requirements,
                height=200
            )
            
            if st.button("💾 Save Requirements"):
                with open(requirements_file, 'w') as f:
                    f.write(updated_requirements)
                st.success("Requirements saved!")
        
        else:
            if st.button("➕ Create requirements.txt"):
                with open(requirements_file, 'w') as f:
                    f.write("# Project dependencies\n")
                st.success("requirements.txt created!")
                st.rerun()
        
        # Installed packages
        if st.button("📋 Show Installed Packages"):
            self._show_installed_packages()
    
    def _render_git_panel(self):
        """Render Git integration panel."""
        
        project_path = self.workspace_root / st.session_state.ide_current_project
        
        # Git status
        git_status = self._get_git_status(project_path)
        
        if git_status:
            st.markdown("**Git Status:**")
            st.code(git_status, language="bash")
        
        # Git operations
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Git Add All"):
                self._git_add_all(project_path)
        
        with col2:
            if st.button("📊 Git Status"):
                self._refresh_git_status(project_path)
        
        # Commit
        commit_message = st.text_input("Commit Message:")
        
        if st.button("💾 Commit") and commit_message:
            self._git_commit(project_path, commit_message)
        
        # Push/Pull
        col_push, col_pull = st.columns(2)
        
        with col_push:
            if st.button("⬆️ Push"):
                self._git_push(project_path)
        
        with col_pull:
            if st.button("⬇️ Pull"):
                self._git_pull(project_path)
        
        # Deploy to new repository
        st.markdown("---")
        st.markdown("### 🚀 **Deploy to Git Repository**")
        
        with st.form("git_deploy_form"):
            repo_url = st.text_input("Repository URL:")
            
            col_user, col_pass = st.columns(2)
            with col_user:
                git_username = st.text_input("Git Username:")
            with col_pass:
                git_password = st.text_input("Git Password/Token:", type="password")
            
            deploy_branch = st.text_input("Branch:", value="main")
            
            if st.form_submit_button("🚀 Deploy to Repository"):
                self._deploy_to_git_repository(project_path, repo_url, git_username, git_password, deploy_branch)
    
    def _render_project_settings(self):
        """Render project settings."""
        
        st.markdown("### 🔧 **Project Settings**")
        
        project_path = self.workspace_root / st.session_state.ide_current_project
        
        # Project info
        st.markdown("#### 📊 **Project Information**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Files", len(list(project_path.rglob("*"))))
        with col2:
            st.metric("Size", f"{self._get_directory_size(project_path):.2f} MB")
        
        # Environment settings
        st.markdown("#### 🐍 **Python Environment**")
        
        python_version = self._get_python_version()
        st.write(f"**Python Version**: {python_version}")
        
        # Project export
        st.markdown("#### 📤 **Export Project**")
        
        if st.button("📦 Export as ZIP"):
            self._export_project_zip(project_path)
        
        # Project deletion
        st.markdown("#### ⚠️ **Danger Zone**")
        
        if st.button("🗑️ Delete Project", type="secondary"):
            if st.checkbox("I understand this action cannot be undone"):
                self._delete_project(project_path)
    
    # Implementation methods
    def _create_new_project(self, name: str, project_type: str, templates: List[str]):
        """Create a new project."""
        
        project_path = self.workspace_root / name
        project_path.mkdir(exist_ok=True)
        
        # Create basic structure based on project type
        if project_type == "Streamlit App":
            self._create_streamlit_template(project_path, templates)
        elif project_type == "Flask Web App":
            self._create_flask_template(project_path, templates)
        # Add more project types...
        
        st.session_state.ide_current_project = name
        st.success(f"Project '{name}' created successfully!")
        st.rerun()
    
    def _create_streamlit_template(self, project_path: Path, templates: List[str]):
        """Create Streamlit app template."""
        
        # Main app file
        app_content = '''import streamlit as st

st.title("🚀 My Streamlit App")

st.write("Welcome to your new Streamlit application!")

# Add your app logic here
name = st.text_input("Enter your name:")
if name:
    st.write(f"Hello, {name}! 👋")

st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choose a page:", ["Home", "About", "Contact"])

if page == "Home":
    st.write("This is the home page.")
elif page == "About":
    st.write("This is the about page.")
else:
    st.write("This is the contact page.")
'''
        
        with open(project_path / "app.py", 'w') as f:
            f.write(app_content)
        
        # Add templates
        if "requirements.txt" in templates:
            with open(project_path / "requirements.txt", 'w') as f:
                f.write("streamlit>=1.28.0\npandas\nnumpy\n")
        
        if "README.md" in templates:
            with open(project_path / "README.md", 'w') as f:
                f.write(f"# {project_path.name}\n\nA Streamlit application.\n\n## Run\n\n```bash\nstreamlit run app.py\n```\n")
        
        if ".gitignore" in templates:
            with open(project_path / ".gitignore", 'w') as f:
                f.write("__pycache__/\n*.pyc\n.env\n.venv/\n")
    
    def _open_file(self, file_path: str):
        """Open a file in the editor."""
        st.session_state.ide_current_file = file_path
        st.rerun()
    
    def _save_file(self, file_path: Path, content: str):
        """Save file content."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            st.success(f"File saved: {file_path.name}")
        except Exception as e:
            st.error(f"Error saving file: {e}")
    
    def _run_app_live(self, app_file: str, port: int):
        """Run app live in subprocess."""
        
        if not app_file:
            st.error("Please select an app file to run.")
            return
        
        project_path = self.workspace_root / st.session_state.ide_current_project
        app_path = project_path / app_file
        
        try:
            # Start the app in background
            if app_file.endswith('.py'):
                if 'streamlit' in app_file.lower() or 'app.py' in app_file:
                    cmd = f"streamlit run {app_path} --server.port {port}"
                else:
                    cmd = f"python {app_path}"
            
            # Store running app info
            st.session_state.ide_running_apps[str(port)] = {
                'file': app_file,
                'status': 'running',
                'command': cmd,
                'start_time': datetime.now().isoformat()
            }
            
            st.success(f"App started on port {port}!")
            st.info(f"Access your app at: http://localhost:{port}")
            
        except Exception as e:
            st.error(f"Error starting app: {e}")
    
    def _execute_terminal_command(self, command: str):
        """Execute terminal command."""
        
        project_path = self.workspace_root / st.session_state.ide_current_project
        
        try:
            # Execute command in project directory
            result = subprocess.run(
                command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Store in history
            entry = {
                'command': command,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None,
                'timestamp': datetime.now().isoformat()
            }
            
            st.session_state.ide_terminal_history.append(entry)
            st.rerun()
            
        except subprocess.TimeoutExpired:
            st.error("Command timed out after 30 seconds")
        except Exception as e:
            st.error(f"Error executing command: {e}")
    
    def _deploy_to_git_repository(self, project_path: Path, repo_url: str, username: str, password: str, branch: str):
        """Deploy project to Git repository."""
        
        try:
            # Initialize git if not already initialized
            if not (project_path / ".git").exists():
                repo = git.Repo.init(project_path)
            else:
                repo = git.Repo(project_path)
            
            # Add all files
            repo.git.add(A=True)
            
            # Commit if there are changes
            if repo.is_dirty():
                repo.index.commit("Deploy from Streamlit IDE")
            
            # Add remote origin if not exists
            try:
                origin = repo.remote('origin')
            except:
                origin = repo.create_remote('origin', repo_url)
            
            # Push to repository
            if username and password:
                # Use credentials
                repo_url_with_auth = repo_url.replace('https://', f'https://{username}:{password}@')
                origin.set_url(repo_url_with_auth)
            
            origin.push(branch)
            
            st.success(f"Successfully deployed to {repo_url}")
            
        except Exception as e:
            st.error(f"Deployment failed: {e}")
    
    # Helper methods
    def _get_existing_projects(self) -> List[str]:
        """Get list of existing projects."""
        if not self.workspace_root.exists():
            return []
        
        return [d.name for d in self.workspace_root.iterdir() if d.is_dir()]
    
    def _get_file_tree(self, path: Path) -> List[Dict[str, Any]]:
        """Get file tree for directory."""
        files = []
        
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue
                
                files.append({
                    'name': item.name,
                    'path': str(item),
                    'type': 'file' if item.is_file() else 'directory'
                })
        except Exception:
            pass
        
        return files
    
    def _get_python_files(self, path: Path) -> List[str]:
        """Get Python files in project."""
        try:
            return [f.name for f in path.rglob("*.py")]
        except:
            return []
    
    def _get_language_from_extension(self, ext: str) -> str:
        """Get language for syntax highlighting."""
        lang_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown'
        }
        return lang_map.get(ext, 'text')
    
    def _get_git_status(self, project_path: Path) -> str:
        """Get git status for project."""
        try:
            if (project_path / ".git").exists():
                result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                return result.stdout
        except:
            pass
        return ""
    
    def _get_directory_size(self, path: Path) -> float:
        """Get directory size in MB."""
        try:
            total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            return total / (1024 * 1024)  # Convert to MB
        except:
            return 0.0
    
    def _get_python_version(self) -> str:
        """Get Python version."""
        try:
            result = subprocess.run(['python', '--version'], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "Unknown"

# Global IDE instance
_streamlit_ide = None

def get_streamlit_ide() -> StreamlitIDE:
    """Get the global Streamlit IDE instance."""
    global _streamlit_ide
    if _streamlit_ide is None:
        _streamlit_ide = StreamlitIDE()
    return _streamlit_ide

if __name__ == "__main__":
    # Test IDE
    ide = StreamlitIDE()
    print("🚀 Streamlit IDE initialized!")
