#!/usr/bin/env python3
"""
Update All Catalogs - Comprehensive Automation
==============================================

Unified automation script that updates all project catalogs and documentation:
1. Test Catalogue - Complete test inventory
2. User Story Catalog - Agile artifacts
3. Task Catalog - Detailed task tracking
4. Documentation index updates
5. Live documentation synchronization

Features:
- Unified interface for all catalog updates
- Change detection for efficiency
- Validation and consistency checks
- Integration with existing automation systems
- Git integration for automatic updates

Usage:
    python scripts/update_all_catalogs.py [--force] [--test-only] [--agile-only]

Author: AI Development Agent
Last Updated: 2025-08-29
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.core.logging_config import setup_logging

class CatalogManager:
    """Unified catalog management system."""
    
    def __init__(self):
        self.logger = setup_logging(__name__)
        self.project_root = Path(__file__).parent.parent
        self.catalogs = {
            'test_catalogue': {
                'script': 'scripts/generate_test_catalogue.py',
                'output': 'docs/testing/TEST_CATALOGUE.md',
                'description': 'Test Catalogue - Complete test inventory'
            },
            'test_automation': {
                'script': 'scripts/automate_test_catalogue.py',
                'description': 'Test Catalogue Automation'
            },
            'agile_artifacts': {
                'script': 'scripts/update_agile_artifacts.py',
                'description': 'Agile Artifacts Automation'
            },
            'user_story_updates': {
                'script': 'scripts/automate_user_story_updates.py',
                'description': 'User Story Status Updates'
            }
        }
    
    def run_script(self, script_path: str, args: List[str] = None) -> bool:
        """Run a script and return success status."""
        
        args = args or []
        full_path = self.project_root / script_path
        
        if not full_path.exists():
            self.logger.error(f"Script not found: {script_path}")
            return False

    def run_module(self, module_name: str, args: List[str] = None) -> bool:
        """Run a Python module via `python -m <module>` and return success status."""
        args = args or []

        try:
            self.logger.info(f"Running module {module_name}...")

            cmd = [sys.executable, "-m", module_name] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=self.project_root,
            )

            if result.returncode == 0:
                self.logger.info(f"[OK] Module {module_name} completed successfully")
                return True

            self.logger.error(f"[ERROR] Module {module_name} failed: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"[TIMEOUT] Module {module_name} timed out")
            return False
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to run module {module_name}: {e}")
            return False
        
        try:
            self.logger.info(f"Running {script_path}...")
            
            cmd = [sys.executable, str(full_path)] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                self.logger.info(f"[OK] {script_path} completed successfully")
                return True
            else:
                self.logger.error(f"[ERROR] {script_path} failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"[TIMEOUT] {script_path} timed out")
            return False
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to run {script_path}: {e}")
            return False
    
    def update_test_catalogue(self, force: bool = False) -> bool:
        """Update the test catalogue."""
        
        self.logger.info("Updating test catalogue...")
        
        # Check if update is needed
        if not force:
            check_result = self.run_script('scripts/automate_test_catalogue.py', ['--status'])
            if not check_result:
                self.logger.warning("Could not check test catalogue status")
        
        # Update catalogue
        args = ['--force'] if force else []
        return self.run_script('scripts/automate_test_catalogue.py', args)
    
    def update_agile_artifacts(self, force: bool = False) -> bool:
        """Update agile artifacts and user stories."""
        
        self.logger.info("Updating agile artifacts...")

        # The story status update script requires a specific --story-id, so it's not
        # a valid "regenerate agile catalogs" entrypoint. For catalog regeneration,
        # rely on the User Story Catalog Manager which scans story files and rebuilds
        # docs/agile/catalogs/USER_STORY_CATALOG.md deterministically.
        #
        # Note: Task/Sprint summary catalogs are maintained separately; this method
        # focuses on the canonical story catalog used by stakeholders.
        return self.run_module("utils.agile.user_story_catalog_manager")
    
    def validate_all_catalogs(self) -> bool:
        """Validate all catalogs for consistency."""
        
        self.logger.info("Validating all catalogs...")
        
        validation_results = {}
        
        # Validate test catalogue
        validation_results['test_catalogue'] = self.run_script(
            'scripts/generate_test_catalogue.py', ['--validate']
        )
        
        # Check if files exist
        required_files = [
            'docs/testing/TEST_CATALOGUE.md',
            'docs/agile/catalogs/USER_STORY_CATALOG.md',
            'docs/agile/catalogs/TASK_CATALOG.md'
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.logger.error(f"Required catalog missing: {file_path}")
                validation_results[file_path] = False
            else:
                validation_results[file_path] = True
        
        # Summary
        all_valid = all(validation_results.values())
        
        if all_valid:
            self.logger.info("[OK] All catalogs validated successfully")
        else:
            failed = [k for k, v in validation_results.items() if not v]
            self.logger.error(f"[ERROR] Validation failed for: {failed}")
        
        return all_valid
    
    def get_catalog_status(self) -> Dict[str, Any]:
        """Get status of all catalogs."""
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'catalogs': {}
        }
        
        # Check each catalog
        for catalog_name, catalog_info in self.catalogs.items():
            catalog_status = {
                'exists': False,
                'size': 0,
                'modified': None,
                'description': catalog_info['description']
            }
            
            # Check output file if specified
            if 'output' in catalog_info:
                output_path = self.project_root / catalog_info['output']
                if output_path.exists():
                    catalog_status['exists'] = True
                    catalog_status['size'] = output_path.stat().st_size
                    catalog_status['modified'] = datetime.fromtimestamp(
                        output_path.stat().st_mtime
                    ).isoformat()
            
            # Check script exists
            script_path = self.project_root / catalog_info['script']
            catalog_status['script_exists'] = script_path.exists()
            
            status['catalogs'][catalog_name] = catalog_status
        
        return status
    
    def print_status(self) -> None:
        """Print comprehensive status of all catalogs."""
        
        status = self.get_catalog_status()
        
        print("Catalog Management Status")
        print("=" * 50)
        print(f"Last checked: {status['timestamp']}")
        print()
        
        for catalog_name, catalog_info in status['catalogs'].items():
            print(f"- {catalog_info['description']}")
            print(f"  Script: {'OK' if catalog_info['script_exists'] else 'MISSING'}")
            
            if 'exists' in catalog_info:
                print(f"  Output: {'OK' if catalog_info['exists'] else 'MISSING'}")
                
                if catalog_info['exists']:
                    print(f"  Size: {catalog_info['size']:,} bytes")
                    if catalog_info['modified']:
                        modified_dt = datetime.fromisoformat(catalog_info['modified'])
                        age = datetime.now() - modified_dt
                        print(f"  Age: {age.total_seconds() / 3600:.1f} hours")
            
            print()
    
    def update_all(self, force: bool = False, test_only: bool = False, agile_only: bool = False) -> bool:
        """Update all catalogs."""
        
        self.logger.info("[START] Starting comprehensive catalog update...")
        
        results = {}
        
        # Update test catalogue
        if not agile_only:
            results['test_catalogue'] = self.update_test_catalogue(force=force)
        
        # Update agile artifacts
        if not test_only:
            results['agile_artifacts'] = self.update_agile_artifacts(force=force)
        
        # Validate all catalogs
        if not any([test_only, agile_only]):
            results['validation'] = self.validate_all_catalogs()
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        self.logger.info(f"[SUMMARY] Catalog update summary: {successful}/{total} successful")
        
        if successful == total:
            self.logger.info("[SUCCESS] All catalog updates completed successfully")
            return True
        else:
            failed_tasks = [task for task, success in results.items() if not success]
            self.logger.error(f"[ERROR] Failed tasks: {failed_tasks}")
            return False
    
    def setup_automation(self) -> bool:
        """Set up automation for all catalogs."""
        
        self.logger.info("Setting up catalog automation...")
        
        # Create automation script for integration
        automation_script = self.project_root / "scripts" / "catalog_automation.py"
        
        automation_content = f'''#!/usr/bin/env python3
"""
Catalog Automation Integration
=============================

This script is called by git hooks and scheduled tasks to maintain
all project catalogs automatically.

Generated: {datetime.now().isoformat()}
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.update_all_catalogs import CatalogManager

def main():
    manager = CatalogManager()
    
    # Silent mode for automation
    manager.logger.setLevel("ERROR")
    
    # Update all catalogs
    success = manager.update_all()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
'''
        
        try:
            with open(automation_script, 'w', encoding='utf-8') as f:
                f.write(automation_content)
            
            self.logger.info("[OK] Automation script created")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to create automation script: {e}")
            return False

def main():
    """Main execution function."""
    
    parser = argparse.ArgumentParser(description="Update All Catalogs")
    parser.add_argument("--force", action="store_true",
                       help="Force update all catalogs")
    parser.add_argument("--test-only", action="store_true",
                       help="Update only test catalogue")
    parser.add_argument("--agile-only", action="store_true",
                       help="Update only agile artifacts")
    parser.add_argument("--status", action="store_true",
                       help="Show status of all catalogs")
    parser.add_argument("--validate", action="store_true",
                       help="Validate all catalogs")
    parser.add_argument("--setup", action="store_true",
                       help="Set up automation")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose logging")
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = CatalogManager()
    
    if args.verbose:
        manager.logger.setLevel("DEBUG")
    
    # Handle different modes
    if args.status:
        manager.print_status()
        return
    
    if args.validate:
        success = manager.validate_all_catalogs()
        sys.exit(0 if success else 1)
    
    if args.setup:
        success = manager.setup_automation()
        sys.exit(0 if success else 1)
    
    # Default: update all catalogs
    success = manager.update_all(
        force=args.force,
        test_only=args.test_only,
        agile_only=args.agile_only
    )
    
    # Show status after update
    if success:
        print()
        manager.print_status()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
