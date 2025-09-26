#!/usr/bin/env python3
"""
Setup Automated Git Pull

This script sets up the git automation to make 'git pull' work seamlessly
with automatic database conflict resolution.

Excellence Standards:
- Zero user intervention after setup
- Complete error handling
- Comprehensive documentation
- Evidence-based validation
"""

import subprocess
import sys
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def setup_git_alias():
    """
    Set up git alias to automatically use our wrapper for pull commands.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        project_root = Path(__file__).parent.parent
        wrapper_script = project_root / "utils" / "git" / "git_automation_wrapper.py"
        
        # Use Python executable path for cross-platform compatibility
        python_exe = sys.executable
        alias_command = f"!{python_exe} {wrapper_script} pull"
        
        logger.info("🔧 Setting up automated git pull...")
        logger.info(f"Python executable: {python_exe}")
        logger.info(f"Wrapper script: {wrapper_script}")
        
        # Set git alias for automated pull
        result = subprocess.run([
            "git", "config", "--global", "alias.pull", alias_command
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Failed to set git alias: {result.stderr}")
            return False
        
        logger.info("✅ Git alias configured successfully!")
        logger.info("   'git pull' will now automatically handle database conflicts")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup git alias: {e}")
        return False


def test_git_alias():
    """
    Test that the git alias is working correctly.
    
    Returns:
        True if test passed, False otherwise
    """
    try:
        logger.info("🧪 Testing git alias configuration...")
        
        # Test that git recognizes our alias
        result = subprocess.run([
            "git", "config", "--global", "--get", "alias.pull"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error("❌ Git alias not found")
            return False
        
        alias_value = result.stdout.strip()
        logger.info(f"✅ Git alias configured: {alias_value}")
        
        # Verify the wrapper script exists
        if "git_automation_wrapper.py" in alias_value:
            logger.info("✅ Wrapper script reference found in alias")
            return True
        else:
            logger.error("❌ Wrapper script not properly referenced in alias")
            return False
        
    except Exception as e:
        logger.error(f"❌ Failed to test git alias: {e}")
        return False


def backup_original_git_config():
    """
    Backup the original git configuration.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("💾 Backing up original git configuration...")
        
        # Get current git config
        result = subprocess.run([
            "git", "config", "--global", "--list"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning("⚠️  Could not read git config for backup")
            return False
        
        # Save backup
        backup_file = Path.home() / ".gitconfig_backup_before_automation"
        backup_file.write_text(result.stdout)
        
        logger.info(f"✅ Git config backed up to: {backup_file}")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to backup git config: {e}")
        return False


def restore_original_git_pull():
    """
    Restore original git pull behavior (remove our alias).
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("🔄 Restoring original git pull behavior...")
        
        result = subprocess.run([
            "git", "config", "--global", "--unset", "alias.pull"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning("⚠️  Could not remove git pull alias (may not exist)")
        else:
            logger.info("✅ Original git pull behavior restored")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to restore original git pull: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("🚀 AUTOMATED GIT PULL SETUP")
    print("=" * 60)
    print()
    
    # Step 1: Backup current config
    backup_original_git_config()
    print()
    
    # Step 2: Set up the automation
    success = setup_git_alias()
    if not success:
        print("\n❌ Setup failed! Please check the errors above.")
        return False
    
    print()
    
    # Step 3: Test the configuration
    test_success = test_git_alias()
    if not test_success:
        print("\n❌ Configuration test failed!")
        return False
    
    print()
    print("=" * 60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("✅ Automated git pull is now active")
    print("✅ Simply use 'git pull' as normal")
    print("✅ Database conflicts will be handled automatically")
    print("✅ Your development data will be preserved")
    print()
    print("📋 What happens automatically:")
    print("   1. Detects staged database files")
    print("   2. Stashes them safely before pull")
    print("   3. Executes the git pull")
    print("   4. Restores your development database")
    print("   5. Restores your stashed changes")
    print()
    print("🔧 To disable automation:")
    print(f"   python {__file__} --restore")
    print()
    print("Ready to test! Try running 'git pull' now.")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup automated git pull")
    parser.add_argument(
        "--restore", 
        action="store_true", 
        help="Restore original git pull behavior"
    )
    
    args = parser.parse_args()
    
    if args.restore:
        success = restore_original_git_pull()
        if success:
            print("✅ Original git pull behavior restored")
        else:
            print("❌ Failed to restore original behavior")
        sys.exit(0 if success else 1)
    else:
        success = main()
        sys.exit(0 if success else 1)
