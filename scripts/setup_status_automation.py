#!/usr/bin/env python3
"""
Setup User Story Status Automation
=================================

This script helps you set up automated user story status updates
using various methods (scheduled, git hooks, IDE integration).

Usage:
    python scripts/setup_status_automation.py [options]

Options:
    --scheduler     Set up scheduled automation (every 5 minutes)
    --git-hooks     Set up git post-commit hooks
    --ide           Set up IDE integration (VS Code/Cursor)
    --all           Set up all automation methods
    --test          Test the automation system

Author: AI Development Agent
Version: 1.0.0
Last Updated: 2025-08-29
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from textwrap import dedent

class AutomationSetup:
    """Setup utility for user story status automation."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.git_hooks_dir = self.project_root / ".git" / "hooks"
        self.vscode_dir = self.project_root / ".vscode"
        
    def test_automation(self) -> bool:
        """Test that the automation system works correctly."""
        
        print("🧪 Testing automation system...")
        
        # Test 1: Verify script exists and is executable
        script_path = self.project_root / "scripts" / "automate_user_story_updates.py"
        if not script_path.exists():
            print("❌ Automation script not found")
            return False
        print("✅ Automation script found")
        
        # Test 2: Test dry-run execution
        try:
            result = subprocess.run([
                sys.executable, str(script_path), "--dry-run"
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Dry-run test successful")
            else:
                print(f"❌ Dry-run test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to execute dry-run test: {e}")
            return False
        
        # Test 3: Verify required directories exist
        required_dirs = [
            "docs/agile/sprints/sprint_1/user_stories",
            "docs/agile/catalogs",
            "monitoring"
        ]
        
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                print(f"❌ Required directory missing: {dir_path}")
                return False
        print("✅ Required directories exist")
        
        # Test 4: Verify user stories exist
        required_stories = ["US-000.md", "US-001.md"]
        stories_dir = self.project_root / "docs/agile/sprints/sprint_1/user_stories"
        
        for story in required_stories:
            if not (stories_dir / story).exists():
                print(f"❌ Required user story missing: {story}")
                return False
        print("✅ Required user stories exist")
        
        print("🎉 All automation tests passed!")
        return True
    
    def setup_scheduler(self):
        """Set up scheduled automation."""
        
        print("⏰ Setting up scheduled automation...")
        
        scheduler_script = self.project_root / "scripts" / "schedule_status_updates.py"
        
        if not scheduler_script.exists():
            print("❌ Scheduler script not found")
            return False
        
        print("✅ Scheduler script available")
        print("\nTo start scheduled automation:")
        print(f"  python {scheduler_script}")
        print("\nTo run in background:")
        print(f"  nohup python {scheduler_script} > logs/scheduler.log 2>&1 &")
        print("\nScheduled automation will run every 5 minutes during development hours (8 AM - 6 PM)")
        
        return True
    
    def setup_git_hooks(self):
        """Set up git post-commit hooks."""
        
        print("🔗 Setting up git post-commit hooks...")
        
        if not self.git_hooks_dir.exists():
            print("❌ Git hooks directory not found - is this a git repository?")
            return False
        
        # Create post-commit hook
        hook_script = self.git_hooks_dir / "post-commit"
        
        hook_content = dedent(f'''
        #!/bin/bash
        # Post-commit hook to update user story status
        
        echo "🔄 Updating user story status after commit..."
        
        # Change to project directory
        cd "{self.project_root}"
        
        # Run the automation script
        python scripts/automate_user_story_updates.py
        
        if [ $? -eq 0 ]; then
            echo "✅ User story status updated successfully"
        else
            echo "❌ Failed to update user story status"
        fi
        ''').strip()
        
        try:
            with open(hook_script, 'w') as f:
                f.write(hook_content)
            
            # Make executable (Windows may not need this)
            if os.name != 'nt':
                os.chmod(hook_script, 0o755)
            
            print("✅ Git post-commit hook installed")
            print("   Status updates will run automatically after each commit")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create git hook: {e}")
            return False
    
    def setup_ide_integration(self):
        """Set up IDE integration (VS Code/Cursor)."""
        
        print("💻 Setting up IDE integration...")
        
        # Create .vscode directory if it doesn't exist
        self.vscode_dir.mkdir(exist_ok=True)
        
        # Create tasks.json
        tasks_config = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Update User Story Status",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "scripts/automate_user_story_updates.py"
                    ],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": []
                },
                {
                    "label": "Preview User Story Updates",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "scripts/automate_user_story_updates.py",
                        "--dry-run",
                        "--verbose"
                    ],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": []
                }
            ]
        }
        
        # Create keybindings.json
        keybindings_config = [
            {
                "key": "ctrl+shift+u",
                "command": "workbench.action.tasks.runTask",
                "args": "Update User Story Status"
            },
            {
                "key": "ctrl+shift+alt+u", 
                "command": "workbench.action.tasks.runTask",
                "args": "Preview User Story Updates"
            }
        ]
        
        try:
            # Write tasks.json
            tasks_file = self.vscode_dir / "tasks.json"
            with open(tasks_file, 'w') as f:
                json.dump(tasks_config, f, indent=4)
            
            # Write keybindings.json
            keybindings_file = self.vscode_dir / "keybindings.json"
            with open(keybindings_file, 'w') as f:
                json.dump(keybindings_config, f, indent=4)
            
            print("✅ IDE integration configured")
            print("   Available keyboard shortcuts:")
            print("   • Ctrl+Shift+U: Update user story status")
            print("   • Ctrl+Shift+Alt+U: Preview updates (dry-run)")
            print("   • Command Palette: 'Tasks: Run Task' -> 'Update User Story Status'")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to set up IDE integration: {e}")
            return False
    
    def print_summary(self):
        """Print setup summary and usage instructions."""
        
        print("\n" + "="*60)
        print("🎉 User Story Status Automation Setup Complete!")
        print("="*60)
        
        print("\n📋 Available Automation Methods:")
        print("\n1. 🔧 Manual Execution:")
        print("   python scripts/automate_user_story_updates.py")
        print("   python scripts/automate_user_story_updates.py --dry-run")
        
        print("\n2. ⏰ Scheduled Automation:")
        print("   python scripts/schedule_status_updates.py")
        print("   # Runs every 5 minutes during development hours")
        
        if (self.git_hooks_dir / "post-commit").exists():
            print("\n3. 🔗 Git Integration:")
            print("   ✅ Enabled - Updates run automatically after commits")
        
        if (self.vscode_dir / "tasks.json").exists():
            print("\n4. 💻 IDE Integration:")
            print("   ✅ Enabled - Use Ctrl+Shift+U to update status")
        
        print("\n📊 Current System Status:")
        
        # Get current status by running a quick dry-run
        try:
            result = subprocess.run([
                sys.executable, 
                str(self.project_root / "scripts" / "automate_user_story_updates.py"), 
                "--dry-run"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Parse output for status
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if "Test Success Rate:" in line:
                        print(f"   🧪 {line.strip()}")
                    elif "Health Monitoring:" in line:
                        print(f"   🏥 {line.strip()}")
                    elif "Stories Updated:" in line:
                        print(f"   📝 {line.strip()}")
            else:
                print("   ⚠️  Could not retrieve current status")
                
        except Exception:
            print("   ⚠️  Could not retrieve current status")
        
        print(f"\n📚 Documentation:")
        print(f"   📖 Full Guide: docs/automation/USER_STORY_STATUS_AUTOMATION.md")
        print(f"   🔧 Cursor Rule: .cursor/automated_user_story_status_updates.mdc")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Choose your preferred automation method")
        print(f"   2. Test with: python scripts/automate_user_story_updates.py --dry-run")
        print(f"   3. Monitor logs in: logs/agent.log")
        print(f"   4. Verify updates in: docs/agile/sprints/sprint_1/user_stories/")


def main():
    """Main execution function."""
    
    parser = argparse.ArgumentParser(description="Setup User Story Status Automation")
    parser.add_argument("--scheduler", action="store_true", 
                       help="Set up scheduled automation")
    parser.add_argument("--git-hooks", action="store_true",
                       help="Set up git post-commit hooks")
    parser.add_argument("--ide", action="store_true",
                       help="Set up IDE integration")
    parser.add_argument("--all", action="store_true",
                       help="Set up all automation methods")
    parser.add_argument("--test", action="store_true",
                       help="Test the automation system")
    
    args = parser.parse_args()
    
    setup = AutomationSetup()
    
    # If no specific options, show help and run test
    if not any([args.scheduler, args.git_hooks, args.ide, args.all, args.test]):
        print("🔧 User Story Status Automation Setup")
        print("="*40)
        parser.print_help()
        print("\nRunning basic system test...\n")
        args.test = True
    
    success = True
    
    # Run tests first if requested
    if args.test:
        success = setup.test_automation() and success
    
    # Set up components based on arguments
    if args.all or args.scheduler:
        success = setup.setup_scheduler() and success
    
    if args.all or args.git_hooks:
        success = setup.setup_git_hooks() and success
    
    if args.all or args.ide:
        success = setup.setup_ide_integration() and success
    
    # Print summary if any setup was performed
    if args.scheduler or args.git_hooks or args.ide or args.all:
        setup.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
