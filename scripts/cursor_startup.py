#!/usr/bin/env python3
"""
Cursor Startup Script
====================

Automatically starts Cursor integration when the workspace is opened.
This script can be run manually or triggered automatically by VS Code tasks.

Usage:
    python scripts/cursor_startup.py
    
Features:
- Auto-detects if integration is already running
- Provides status feedback
- Handles errors gracefully
- Can be run multiple times safely
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Main startup function."""
    print("🚀 Cursor Integration Startup Script")
    print("=" * 40)
    
    try:
        # Import the auto-startup module
        from utils.integration.cursor_auto_startup import (
            auto_initialize_cursor_integration,
            get_initialization_status,
            is_cursor_integration_healthy
        )
        
        # Check current status first
        current_status = get_initialization_status()
        if current_status['initialized']:
            print("✅ Cursor integration is already running")
            print(f"   Started: {current_status['initialization_time']}")
            
            # Check health
            healthy = is_cursor_integration_healthy()
            print(f"   Health: {'✅ Healthy' if healthy else '⚠️ Unhealthy'}")
            
            if healthy:
                print("🎉 Integration is running and healthy!")
                return True
            else:
                print("🔄 Integration exists but unhealthy, reinitializing...")
        
        # Start or restart integration
        print("🔧 Starting Cursor integration...")
        success = auto_initialize_cursor_integration()
        
        if success:
            print("✅ Cursor integration started successfully!")
            
            # Verify health
            healthy = is_cursor_integration_healthy()
            if healthy:
                print("🎉 Integration is running and healthy!")
            else:
                print("⚠️ Integration started but health check failed")
                
            return True
        else:
            print("❌ Failed to start Cursor integration")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
