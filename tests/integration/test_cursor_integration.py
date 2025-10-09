#!/usr/bin/env python3
"""
Test Cursor Integration
======================

Debug script to test cursor integration functionality.
"""

import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_cursor_integration():
    """Test cursor integration step by step."""
    
    print("🔧 Testing Cursor Integration...")
    
    # Test 1: Import cursor auto-startup
    try:
        from utils.integration.cursor_auto_startup import auto_initialize_cursor_integration
        print("✅ cursor_auto_startup imported successfully")
    except ImportError as e:
        print(f"❌ cursor_auto_startup import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 2: Import cursor integration hook
    try:
        from utils.integration.cursor_integration_hook import get_cursor_hook, start_cursor_tracking
        print("✅ cursor_integration_hook imported successfully")
    except ImportError as e:
        print(f"❌ cursor_integration_hook import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 3: Try to initialize
    try:
        print("\n🚀 Attempting to initialize cursor integration...")
        result = auto_initialize_cursor_integration()
        
        if result:
            print("✅ Cursor integration initialized successfully")
        else:
            print("⚠️ Cursor integration initialization returned False")
        
        return result
        
    except Exception as e:
        print(f"❌ Cursor integration initialization failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cursor_integration()
    
    if success:
        print("\n🎉 Cursor integration is working!")
    else:
        print("\n⚠️ Cursor integration has issues that need fixing.")
