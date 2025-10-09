#!/usr/bin/env python3
"""
Simple Cursor Integration Starter
=================================

This script starts the Cursor integration without complex command-line escaping.
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Start Cursor integration."""
    try:
        print("Starting Cursor integration...")
        
        # Import and run the auto-initialization
        from utils.integration.cursor_auto_startup import auto_initialize_cursor_integration
        
        # Initialize the integration
        result = auto_initialize_cursor_integration()
        
        if result:
            print("SUCCESS: Cursor integration started!")
            return 0
        else:
            print("ERROR: Cursor integration failed!")
            return 1
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
