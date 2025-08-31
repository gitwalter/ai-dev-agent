#!/usr/bin/env python3
"""
Streamlit Prompt Optimization Interface Runner

This script sets up the Python path and runs the prompt optimization interface using Streamlit.
"""

import sys
import os
import subprocess
from pathlib import Path

def setup_environment():
    """Set up the Python environment for the project."""
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Add project root to Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Add utils directory to Python path
    utils_path = project_root / "utils"
    if str(utils_path) not in sys.path:
        sys.path.insert(0, str(utils_path))
    
    # Set environment variables
    os.environ['PYTHONPATH'] = f"{project_root}:{utils_path}:{os.environ.get('PYTHONPATH', '')}"
    
    return project_root

def main():
    """Main function to run the prompt optimization interface."""
    print("🚀 Setting up Prompt Optimization Interface...")
    
    # Setup environment
    project_root = setup_environment()
    
    # Path to the web interface
    web_interface_path = project_root / "utils" / "prompt_management" / "prompt_web_interface.py"
    
    if not web_interface_path.exists():
        print(f"❌ Error: Web interface file not found at {web_interface_path}")
        return 1
    
    print(f"📁 Project root: {project_root}")
    print(f"🌐 Web interface: {web_interface_path}")
    print("🚀 Starting Streamlit server...")
    print("📊 The interface will be available at: http://localhost:8503")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Run streamlit with the web interface
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(web_interface_path),
            "--server.port", "8503",
            "--server.address", "localhost"
        ]
        
        # Run the command
        subprocess.run(cmd, cwd=project_root)
        
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
