#!/usr/bin/env python3
"""
Quick test to verify core functionality without hanging.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Quick test function."""
    print("🔍 Quick Core Test")
    print("=" * 30)
    
    # Test 1: Basic imports
    try:
        print("Testing imports...")
        from main import AIDevelopmentAgent
        print("✅ AIDevelopmentAgent imported")
        
        from models.config import load_config_from_env
        print("✅ Config module imported")
        
        from models.state import create_initial_state
        print("✅ State module imported")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Config loading
    try:
        print("\nTesting config loading...")
        config = load_config_from_env()
        print(f"✅ Config loaded - Model: {config.gemini.model_name}")
        print(f"   API Key: {'Yes' if config.gemini.api_key else 'No'}")
        
    except Exception as e:
        print(f"❌ Config failed: {e}")
        return False
    
    # Test 3: Agent creation
    try:
        print("\nTesting agent creation...")
        agent = AIDevelopmentAgent(config)
        print(f"✅ Agent created - {len(agent.agents)} agents loaded")
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False
    
    print("\n🎉 Core functionality test passed!")
    return True

if __name__ == "__main__":
    success = main()
    print(f"\nExit code: {0 if success else 1}")
    sys.exit(0 if success else 1)
