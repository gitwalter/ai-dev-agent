#!/usr/bin/env python3
"""
Cursor Auto-Startup Hook
========================

This script is automatically executed when Cursor starts up.
It ensures the Cursor integration is always running.

This file should be in .cursor/startup.py to be automatically
detected by Cursor's startup process.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils.integration.cursor_auto_startup import auto_initialize_cursor_integration
    
    # Silent startup - only log errors
    result = auto_initialize_cursor_integration()
    
    if result:
        print("Cursor integration auto-started")
    else:
        print("Cursor integration startup failed")
        
except Exception as e:
    print(f"Cursor integration startup error: {e}")
