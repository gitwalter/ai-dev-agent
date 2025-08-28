#!/usr/bin/env python3
"""
Setup script for Git hooks to enable automatic database cleaning.

This script configures Git hooks to automatically clean the database before pushing
and restore it after pulling from GitHub.
"""

import os
import sys
import platform
import shutil
from pathlib import Path

def setup_git_hooks():
    """Set up Git hooks for automatic database management."""
    
    print("🔧 Setting up Git hooks for automatic database management...")
    
    # Get project root
    project_root = Path(__file__).parent
    hooks_dir = project_root / ".git" / "hooks"
    
    if not hooks_dir.exists():
        print("❌ Error: .git/hooks directory not found")
        print("   Make sure you're in a Git repository")
        return False
    
    # Determine the operating system
    system = platform.system().lower()
    
    if system == "windows":
        # Use PowerShell on Windows
        pre_push_source = project_root / ".git" / "hooks" / "pre-push.ps1"
        post_merge_source = project_root / ".git" / "hooks" / "post-merge.ps1"
        pre_push_dest = hooks_dir / "pre-push"
        post_merge_dest = hooks_dir / "post-merge"
        
        # Create PowerShell wrapper scripts
        create_powershell_wrapper(pre_push_source, pre_push_dest, "pre-push")
        create_powershell_wrapper(post_merge_source, post_merge_dest, "post-merge")
        
    else:
        # Use bash on Unix-like systems
        pre_push_source = project_root / ".git" / "hooks" / "pre-push"
        post_merge_source = project_root / ".git" / "hooks" / "post-merge"
        pre_push_dest = hooks_dir / "pre-push"
        post_merge_dest = hooks_dir / "post-merge"
        
        # Copy the bash scripts
        shutil.copy2(pre_push_source, pre_push_dest)
        shutil.copy2(post_merge_source, post_merge_dest)
        
        # Make them executable
        os.chmod(pre_push_dest, 0o755)
        os.chmod(post_merge_dest, 0o755)
    
    print("✅ Git hooks configured successfully!")
    print("\n📋 What happens now:")
    print("  🚀 Before git push: Database is automatically cleaned for GitHub")
    print("  🔄 After git pull: Development database is automatically restored")
    print("  📦 Your user data is safely backed up and restored")
    
    return True

def create_powershell_wrapper(source_path, dest_path, hook_type):
    """Create a PowerShell wrapper script for Git hooks on Windows."""
    
    if not source_path.exists():
        print(f"❌ Error: Source hook file not found: {source_path}")
        return False
    
    # Create PowerShell wrapper
    wrapper_content = f"""#!/usr/bin/env powershell
# Git {hook_type} hook wrapper for Windows
# This wrapper ensures PowerShell execution policy allows the script to run

# Set execution policy for this process
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Run the actual hook script
& "{source_path.absolute()}"

# Exit with the same code as the hook script
exit $LASTEXITCODE
"""
    
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(wrapper_content)
    
    return True

def test_hooks():
    """Test that the hooks are properly configured."""
    
    print("\n🧪 Testing Git hooks configuration...")
    
    project_root = Path(__file__).parent
    hooks_dir = project_root / ".git" / "hooks"
    
    # Check if hooks exist
    pre_push_hook = hooks_dir / "pre-push"
    post_merge_hook = hooks_dir / "post-merge"
    
    if not pre_push_hook.exists():
        print("❌ pre-push hook not found")
        return False
    
    if not post_merge_hook.exists():
        print("❌ post-merge hook not found")
        return False
    
    # Check if automation script exists
    automation_script = project_root / "utils" / "github_database_automation.py"
    if not automation_script.exists():
        print("❌ Database automation script not found")
        return False
    
    print("✅ All hooks and scripts are properly configured")
    return True

def show_usage():
    """Show usage information."""
    
    print("\n📖 Usage:")
    print("  python setup_git_hooks.py setup    - Set up Git hooks")
    print("  python setup_git_hooks.py test     - Test hook configuration")
    print("  python setup_git_hooks.py status   - Show current status")
    
    print("\n🔄 Manual commands:")
    print("  python utils/github_database_automation.py prepare  - Prepare for GitHub")
    print("  python utils/github_database_automation.py restore  - Restore development DB")
    print("  python utils/github_database_automation.py status   - Show DB status")

def show_status():
    """Show the current status of the Git hooks setup."""
    
    print("📊 Git Hooks Status:")
    
    project_root = Path(__file__).parent
    hooks_dir = project_root / ".git" / "hooks"
    
    # Check hooks
    pre_push_hook = hooks_dir / "pre-push"
    post_merge_hook = hooks_dir / "post-merge"
    
    print(f"  Pre-push hook: {'✅' if pre_push_hook.exists() else '❌'}")
    print(f"  Post-merge hook: {'✅' if post_merge_hook.exists() else '❌'}")
    
    # Check automation script
    automation_script = project_root / "utils" / "github_database_automation.py"
    print(f"  Automation script: {'✅' if automation_script.exists() else '❌'}")
    
    # Check database
    database_path = project_root / "prompts" / "prompt_templates.db"
    print(f"  Database exists: {'✅' if database_path.exists() else '❌'}")
    
    if database_path.exists():
        size = database_path.stat().st_size
        print(f"  Database size: {size:,} bytes")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        success = setup_git_hooks()
        if success:
            test_hooks()
        sys.exit(0 if success else 1)
    
    elif command == "test":
        success = test_hooks()
        sys.exit(0 if success else 1)
    
    elif command == "status":
        show_status()
        sys.exit(0)
    
    else:
        print(f"❌ Unknown command: {command}")
        show_usage()
        sys.exit(1)
