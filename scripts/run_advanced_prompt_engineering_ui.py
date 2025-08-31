#!/usr/bin/env python3
"""
Advanced Prompt Engineering UI Runner

This script runs the fully functional advanced prompt engineering UI with real-time testing,
optimization, analytics, A/B testing, and advanced features.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run the advanced prompt engineering UI."""
    try:
        print("🚀 Starting Advanced Prompt Engineering UI...")
        print("=" * 60)
        print("📋 Advanced Features:")
        print("  ✅ Real-time prompt testing and validation")
        print("  ✅ Advanced prompt editor with syntax highlighting")
        print("  ✅ Live optimization preview with before/after comparison")
        print("  ✅ Interactive prompt performance analytics dashboard")
        print("  ✅ A/B testing interface for prompt variants")
        print("  ✅ Real-time cost estimation and token counting")
        print("  ✅ Batch prompt processing and testing")
        print("  ✅ Template management and version control")
        print("  ✅ Performance monitoring and trend analysis")
        print("=" * 60)
        
        # Import and run the advanced UI
        from apps.advanced_prompt_engineering_ui import main as ui_main
        
        print("\n🌐 Starting advanced web interface...")
        print("📱 The web interface will be available at: http://localhost:8503")
        print("🔄 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the advanced UI
        ui_main()
        
    except KeyboardInterrupt:
        print("\n🛑 Advanced UI stopped by user")
    except Exception as e:
        print(f"❌ Error starting advanced UI: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
