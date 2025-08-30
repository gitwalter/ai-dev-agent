#!/usr/bin/env python3
"""
Web Interface Runner for US-PE-01: Prompt Engineering Core System

This script runs the web interface to test the complete prompt management system.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run the prompt management web interface."""
    try:
        from utils.prompt_management.prompt_web_interface import PromptWebInterface
        
        print("🚀 Starting Prompt Management Web Interface...")
        print("=" * 50)
        print("📋 System Components:")
        print("  ✅ Template System")
        print("  ✅ Optimization Engine")
        print("  ✅ Analytics System")
        print("  ✅ Web Interface")
        print("  ✅ Pre-built Templates")
        print("=" * 50)
        
        # Initialize the web interface
        web_interface = PromptWebInterface()
        
        # Load pre-built templates if not already loaded
        try:
            from utils.prompt_management.prebuilt_templates import load_prebuilt_templates
            template_system = web_interface.template_system
            
            # Check if templates are already loaded
            existing_templates = template_system.get_all_templates()
            if len(existing_templates) < 10:  # If less than 10 templates, load pre-built ones
                print("📦 Loading pre-built templates...")
                created_ids = load_prebuilt_templates(template_system)
                print(f"✅ Loaded {len(created_ids)} pre-built templates")
            else:
                print(f"✅ {len(existing_templates)} templates already loaded")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not load pre-built templates: {e}")
        
        print("\n🌐 Starting web interface...")
        print("📱 The web interface will be available at: http://localhost:8501")
        print("🔄 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run the web interface
        web_interface.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped by user")
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
