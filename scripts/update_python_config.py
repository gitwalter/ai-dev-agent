#!/usr/bin/env python3
"""
Update VS Code Python configuration from python-config.json
"""

import json
import os
from pathlib import Path

def update_vscode_python_config():
    """Update VS Code settings with Python paths from python-config.json"""
    
    # Paths
    project_root = Path(__file__).parent.parent
    config_file = project_root / "python-config.json"
    vscode_settings = project_root / ".vscode" / "settings.json"
    
    # Read python config
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            python_config = json.load(f)
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return False
    
    # Read existing VS Code settings
    vscode_config = {}
    if vscode_settings.exists():
        try:
            with open(vscode_settings, 'r') as f:
                vscode_config = json.load(f)
        except Exception as e:
            print(f"⚠️ Error reading VS Code settings: {e}")
            vscode_config = {}
    
    # Update VS Code settings
    vscode_config.update({
        "ai-dev-agent.pythonPath": python_config["pythonPath"],
        "ai-dev-agent.anacondaPath": python_config["anacondaPath"], 
        "ai-dev-agent.condaPath": python_config["condaPath"],
        "ai-dev-agent.pipPath": python_config["pipPath"]
    })
    
    # Create .vscode directory if it doesn't exist
    vscode_settings.parent.mkdir(exist_ok=True)
    
    # Write updated settings
    try:
        with open(vscode_settings, 'w') as f:
            json.dump(vscode_config, f, indent=4)
        
        print("✅ VS Code settings updated successfully!")
        print(f"📍 Python path: {python_config['pythonPath']}")
        print(f"📍 Anaconda path: {python_config['anacondaPath']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error writing VS Code settings: {e}")
        return False

def show_current_config():
    """Show current Python configuration"""
    
    project_root = Path(__file__).parent.parent
    config_file = project_root / "python-config.json"
    
    if not config_file.exists():
        print("❌ No configuration file found")
        return
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print("📋 Current Python Configuration:")
        print(f"   🐍 Python Path: {config['pythonPath']}")
        print(f"   📁 Anaconda Path: {config['anacondaPath']}")
        print(f"   🔧 Conda Path: {config['condaPath']}")
        print(f"   📦 Pip Path: {config['pipPath']}")
        
        if 'environments' in config:
            print("   🌍 Available Environments:")
            for name, path in config['environments'].items():
                print(f"      • {name}: {path}")
                
    except Exception as e:
        print(f"❌ Error reading config: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_current_config()
    else:
        print("🔄 Updating VS Code Python configuration...")
        if update_vscode_python_config():
            print("\n💡 To use the new configuration:")
            print("   1. Restart VS Code")
            print("   2. Press F5 and select a launch configuration")
            print("   3. Choose '🐍 Configured Anaconda (from settings.json)'")
        else:
            print("\n❌ Configuration update failed")
