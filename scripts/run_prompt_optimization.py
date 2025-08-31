#!/usr/bin/env python3
"""
Prompt Optimization Interface Runner

This script properly sets up the Python path and runs the prompt optimization interface.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Add utils directory to path
utils_path = project_root / "utils"
sys.path.insert(0, str(utils_path))

def main():
    """Run the prompt optimization interface."""
    try:
        # Import and run the prompt web interface
        from utils.prompt_management.prompt_web_interface import PromptWebInterface
        
        print("🚀 Starting Prompt Optimization Interface...")
        print("📊 This will open a web interface for prompt management and optimization")
        print("🌐 The interface will be available at: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 60)
        
        # Create and run the interface
        interface = PromptWebInterface()
        interface.run()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("🔧 This might be due to missing dependencies.")
        print("💡 Try running: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
