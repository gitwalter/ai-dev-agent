#!/usr/bin/env python3
"""
Test script to verify prompt optimization interface imports work correctly.
"""

import sys
import os
from pathlib import Path

def setup_paths():
    """Set up Python paths for the project."""
    project_root = Path(__file__).parent.absolute()
    utils_path = project_root / "utils"
    
    # Add to Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    if str(utils_path) not in sys.path:
        sys.path.insert(0, str(utils_path))
    
    return project_root, utils_path

def test_imports():
    """Test all required imports for the prompt optimization interface."""
    print("🧪 Testing imports for Prompt Optimization Interface...")
    print("-" * 50)
    
    # Setup paths
    project_root, utils_path = setup_paths()
    print(f"📁 Project root: {project_root}")
    print(f"🔧 Utils path: {utils_path}")
    
    # Test basic imports
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    # Test prompt management imports
    try:
        from utils.prompt_management.prompt_web_interface import PromptWebInterface
        print("✅ PromptWebInterface imported successfully")
    except ImportError as e:
        print(f"❌ PromptWebInterface import failed: {e}")
        return False
    
    try:
        from utils.prompt_management.prompt_analytics import PromptAnalytics
        print("✅ PromptAnalytics imported successfully")
    except ImportError as e:
        print(f"❌ PromptAnalytics import failed: {e}")
        return False
    
    try:
        from utils.prompt_management.prompt_template_system import PromptTemplateSystem
        print("✅ PromptTemplateSystem imported successfully")
    except ImportError as e:
        print(f"❌ PromptTemplateSystem import failed: {e}")
        return False
    
    try:
        from utils.prompt_management.prompt_optimizer import PromptOptimizer
        print("✅ PromptOptimizer imported successfully")
    except ImportError as e:
        print(f"❌ PromptOptimizer import failed: {e}")
        return False
    
    try:
        from utils.prompt_management.prompt_manager import PromptManager
        print("✅ PromptManager imported successfully")
    except ImportError as e:
        print(f"❌ PromptManager import failed: {e}")
        return False
    
    # Test new US-PE-02 components
    try:
        from utils.prompt_management.prompt_quality_assessment import PromptQualityAssessor
        print("✅ PromptQualityAssessor imported successfully")
    except ImportError as e:
        print(f"❌ PromptQualityAssessor import failed: {e}")
        return False
    
    try:
        from utils.prompt_management.prompt_backup_recovery import PromptBackupRecovery
        print("✅ PromptBackupRecovery imported successfully")
    except ImportError as e:
        print(f"❌ PromptBackupRecovery import failed: {e}")
        return False
    
    try:
        from utils.prompt_management.prompt_audit_trail import PromptAuditTrail
        print("✅ PromptAuditTrail imported successfully")
    except ImportError as e:
        print(f"❌ PromptAuditTrail import failed: {e}")
        return False
    
    print("-" * 50)
    print("🎉 All imports successful! The prompt optimization interface should work.")
    return True

def test_interface_creation():
    """Test creating the interface instance."""
    print("\n🧪 Testing interface creation...")
    print("-" * 30)
    
    try:
        from utils.prompt_management.prompt_web_interface import PromptWebInterface
        interface = PromptWebInterface()
        print("✅ PromptWebInterface instance created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create interface instance: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Prompt Optimization Interface Import Test")
    print("=" * 60)
    
    success = test_imports()
    
    if success:
        test_interface_creation()
        print("\n🎯 Ready to run the prompt optimization interface!")
        print("💡 Use: python start_prompt_optimization.py")
    else:
        print("\n❌ Import test failed. Please check your dependencies.")
        print("💡 Try: pip install -r requirements.txt")
