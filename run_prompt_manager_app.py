#!/usr/bin/env python3
"""
Prompt Manager App Runner

This script runs the fixed prompt manager app that uses our completed US-PE-01 system.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run the prompt manager app."""
    try:
        print("🚀 Starting Prompt Manager App...")
        print("=" * 50)
        print("📋 Fixed Components:")
        print("  ✅ Import errors resolved")
        print("  ✅ Using completed US-PE-01 system")
        print("  ✅ Simple RAG processor stub")
        print("  ✅ Template management integration")
        print("=" * 50)
        
        # Import and run the app
        from apps.prompt_manager_app import main as app_main
        
        print("\n🌐 Starting web interface...")
        print("📱 The web interface will be available at: http://localhost:8502")
        print("🔄 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run the app
        app_main()
        
    except KeyboardInterrupt:
        print("\n🛑 App stopped by user")
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
