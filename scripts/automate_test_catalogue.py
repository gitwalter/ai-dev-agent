#!/usr/bin/env python3
"""
Automated Test Catalogue Maintenance
===================================

Automatically maintains the test catalogue by:
1. Detecting changes in test files
2. Regenerating catalogue when changes are detected  
3. Integration with git hooks for automatic updates
4. Scheduled updates during development
5. Integration with agile artifacts automation

Features:
- File change detection using checksums
- Incremental updates for efficiency
- Git hook integration for commit/push triggers
- Scheduled background updates
- Integration with existing automation systems

Usage:
    python scripts/automate_test_catalogue.py [--force] [--schedule] [--git-hook]

Author: AI Development Agent
Last Updated: 2025-08-29
"""

import os
import sys
import hashlib
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import time

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.core.logging_config import setup_logging

class TestCatalogueAutomation:
    """Automated test catalogue maintenance system."""
    
    def __init__(self):
        self.logger = setup_logging(__name__)
        self.project_root = Path(__file__).parent.parent
        self.test_root = self.project_root / "tests"
        self.catalogue_file = self.project_root / "docs" / "testing" / "TEST_CATALOGUE.md"
        self.generator_script = self.project_root / "scripts" / "generate_test_catalogue.py"
        self.state_file = self.project_root / "monitoring" / ".test_catalogue_state.json"
        
    def get_test_files_state(self) -> Dict[str, str]:
        """Get current state (checksums) of all test files."""
        
        state = {}
        
        for test_file in self.test_root.rglob("test_*.py"):
            try:
                relative_path = str(test_file.relative_to(self.project_root))
                
                # Calculate file checksum
                with open(test_file, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                state[relative_path] = file_hash
                
            except Exception as e:
                self.logger.warning(f"Failed to process {test_file}: {e}")
        
        return state
    
    def load_previous_state(self) -> Dict[str, str]:
        """Load previous test files state."""
        
        if not self.state_file.exists():
            return {}
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                return data.get('test_files', {})
        except Exception as e:
            self.logger.warning(f"Failed to load previous state: {e}")
            return {}
    
    def save_current_state(self, state: Dict[str, str]) -> None:
        """Save current test files state."""
        
        data = {
            'test_files': state,
            'last_update': datetime.now().isoformat(),
            'catalogue_generated': self.catalogue_file.exists()
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def has_changes(self, force: bool = False) -> bool:
        """Check if test files have changed since last catalogue generation."""
        
        if force:
            self.logger.info("Force update requested")
            return True
        
        if not self.catalogue_file.exists():
            self.logger.info("Test catalogue doesn't exist - needs generation")
            return True
        
        current_state = self.get_test_files_state()
        previous_state = self.load_previous_state()
        
        # Check for new files
        new_files = set(current_state.keys()) - set(previous_state.keys())
        if new_files:
            self.logger.info(f"Found {len(new_files)} new test files")
            return True
        
        # Check for deleted files
        deleted_files = set(previous_state.keys()) - set(current_state.keys())
        if deleted_files:
            self.logger.info(f"Found {len(deleted_files)} deleted test files")
            return True
        
        # Check for modified files
        modified_files = []
        for file_path, current_hash in current_state.items():
            previous_hash = previous_state.get(file_path)
            if previous_hash and current_hash != previous_hash:
                modified_files.append(file_path)
        
        if modified_files:
            self.logger.info(f"Found {len(modified_files)} modified test files")
            return True
        
        self.logger.debug("No changes detected in test files")
        return False
    
    def regenerate_catalogue(self) -> bool:
        """Regenerate the test catalogue."""
        
        self.logger.info("Regenerating test catalogue...")
        
        try:
            # Run the generator script
            result = subprocess.run([
                sys.executable, str(self.generator_script)
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.logger.info("Test catalogue regenerated successfully")
                
                # Update state
                current_state = self.get_test_files_state()
                self.save_current_state(current_state)
                
                return True
            else:
                self.logger.error(f"Catalogue generation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Catalogue generation timed out")
            return False
        except Exception as e:
            self.logger.error(f"Failed to regenerate catalogue: {e}")
            return False
    
    def update_if_needed(self, force: bool = False) -> bool:
        """Update catalogue if changes are detected."""
        
        self.logger.info("Checking for test file changes...")
        
        if self.has_changes(force=force):
            return self.regenerate_catalogue()
        else:
            self.logger.info("Test catalogue is up to date")
            return True
    
    def setup_git_hook(self) -> bool:
        """Set up git hook to automatically update test catalogue."""
        
        self.logger.info("Setting up git hook for test catalogue automation...")
        
        hooks_dir = self.project_root / ".git" / "hooks"
        if not hooks_dir.exists():
            self.logger.error("Git hooks directory not found")
            return False
        
        # Create or update post-commit hook
        hook_file = hooks_dir / "post-commit"
        hook_content = ""
        
        # Read existing hook if it exists
        if hook_file.exists():
            try:
                with open(hook_file, 'r') as f:
                    hook_content = f.read()
            except Exception:
                hook_content = ""
        
        # Check if our automation is already in the hook
        automation_marker = "# Test catalogue automation"
        if automation_marker in hook_content:
            self.logger.info("✅ Test catalogue automation already in git hook")
            return True
        
        # Add our automation to the hook
        automation_addition = f"""
{automation_marker}
echo "🔄 Updating test catalogue..."
cd "{self.project_root}"
python scripts/automate_test_catalogue.py --git-hook
"""
        
        # Add shebang if file is empty
        if not hook_content.strip():
            hook_content = "#!/bin/bash\n"
        
        hook_content += automation_addition
        
        try:
            with open(hook_file, 'w') as f:
                f.write(hook_content)
            
            # Make executable (if not on Windows)
            if os.name != 'nt':
                os.chmod(hook_file, 0o755)
            
            self.logger.info("✅ Git hook configured for test catalogue automation")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup git hook: {e}")
            return False
    
    def run_scheduled_updates(self, interval_minutes: int = 10) -> None:
        """Run scheduled updates in a loop."""
        
        self.logger.info(f"⏰ Starting scheduled test catalogue updates (every {interval_minutes} minutes)")
        
        try:
            while True:
                try:
                    self.update_if_needed()
                    time.sleep(interval_minutes * 60)
                    
                except KeyboardInterrupt:
                    self.logger.info("🛑 Scheduled updates stopped by user")
                    break
                except Exception as e:
                    self.logger.error(f"❌ Error in scheduled update: {e}")
                    time.sleep(30)  # Wait 30 seconds before retrying
                    
        except Exception as e:
            self.logger.error(f"❌ Scheduled updates failed: {e}")
    
    def validate_catalogue_integrity(self) -> bool:
        """Validate that the catalogue is consistent with actual test files."""
        
        self.logger.info("🔍 Validating test catalogue integrity...")
        
        if not self.catalogue_file.exists():
            self.logger.error("❌ Test catalogue file doesn't exist")
            return False
        
        # Run validator
        try:
            result = subprocess.run([
                sys.executable, str(self.generator_script), "--validate"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.logger.info("✅ Test catalogue integrity validated")
                return True
            else:
                self.logger.error(f"❌ Catalogue validation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to validate catalogue: {e}")
            return False
    
    def get_catalogue_stats(self) -> Dict[str, Any]:
        """Get statistics about the test catalogue."""
        
        stats = {
            'catalogue_exists': self.catalogue_file.exists(),
            'catalogue_size': 0,
            'catalogue_age': None,
            'test_files_count': 0,
            'last_update': None
        }
        
        if self.catalogue_file.exists():
            stats['catalogue_size'] = self.catalogue_file.stat().st_size
            stats['catalogue_age'] = datetime.now().timestamp() - self.catalogue_file.stat().st_mtime
        
        # Count test files
        stats['test_files_count'] = len(list(self.test_root.rglob("test_*.py")))
        
        # Get last update from state
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    stats['last_update'] = data.get('last_update')
            except Exception:
                pass
        
        return stats
    
    def print_status(self) -> None:
        """Print current status of test catalogue automation."""
        
        stats = self.get_catalogue_stats()
        
        print("Test Catalogue Automation Status")
        print("=" * 40)
        print(f"Catalogue exists: {'YES' if stats['catalogue_exists'] else 'NO'}")
        print(f"Catalogue size: {stats['catalogue_size']:,} bytes")
        
        if stats['catalogue_age']:
            age_hours = stats['catalogue_age'] / 3600
            print(f"Catalogue age: {age_hours:.1f} hours")
        
        print(f"Test files: {stats['test_files_count']}")
        
        if stats['last_update']:
            print(f"Last update: {stats['last_update']}")
        
        print()
        
        # Check if changes are needed
        if self.has_changes():
            print("WARNING: Test catalogue needs updating")
        else:
            print("SUCCESS: Test catalogue is up to date")

def main():
    """Main execution function."""
    
    parser = argparse.ArgumentParser(description="Automated Test Catalogue Maintenance")
    parser.add_argument("--force", action="store_true",
                       help="Force catalogue regeneration")
    parser.add_argument("--schedule", action="store_true",
                       help="Run scheduled updates")
    parser.add_argument("--interval", type=int, default=10,
                       help="Update interval in minutes for scheduled mode (default: 10)")
    parser.add_argument("--git-hook", action="store_true",
                       help="Run as git hook (silent mode)")
    parser.add_argument("--setup-hook", action="store_true",
                       help="Set up git hook integration")
    parser.add_argument("--status", action="store_true",
                       help="Show current status")
    parser.add_argument("--validate", action="store_true",
                       help="Validate catalogue integrity")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose logging")
    
    args = parser.parse_args()
    
    # Initialize automation
    automation = TestCatalogueAutomation()
    
    if args.verbose:
        automation.logger.setLevel("DEBUG")
    
    # Handle different modes
    if args.status:
        automation.print_status()
        return
    
    if args.validate:
        success = automation.validate_catalogue_integrity()
        sys.exit(0 if success else 1)
    
    if args.setup_hook:
        success = automation.setup_git_hook()
        sys.exit(0 if success else 1)
    
    if args.schedule:
        automation.run_scheduled_updates(args.interval)
        return
    
    # Default: update if needed
    if args.git_hook:
        # Silent mode for git hooks
        automation.logger.setLevel("ERROR")
    
    success = automation.update_if_needed(force=args.force)
    
    if success and not args.git_hook:
        automation.print_status()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
