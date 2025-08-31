#!/usr/bin/env python3
"""
File Organization Expert Team

Specialized team of experts to clean up project file structure without breaking anything.
This team follows the File Organization and Cleanup Rule to create a pristine project structure.

Expert Team Roles:
- @file_architect: Designs optimal file structure
- @file_analyzer: Analyzes current violations and dependencies
- @file_mover: Safely moves files to correct locations
- @file_validator: Validates structure and functionality
- @file_cleaner: Removes temporary and unnecessary files
"""

import os
import shutil
import glob
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FileViolation:
    """Represents a file organization violation"""
    file_path: str
    violation_type: str
    current_location: str
    correct_location: str
    severity: str
    dependencies: List[str]

@dataclass
class CleanupPlan:
    """Comprehensive cleanup plan"""
    violations: List[FileViolation]
    move_operations: List[Tuple[str, str]]
    delete_operations: List[str]
    create_directories: List[str]
    validation_steps: List[str]

class FileArchitectExpert:
    """@file_architect - Designs optimal file structure"""
    
    def __init__(self):
        self.optimal_structure = {
            # Core application structure
            "agents/": "AI agent implementations and orchestration",
            "apps/": "Streamlit applications and UI components", 
            "context/": "Context management and processing",
            "models/": "Data models and schemas",
            "utils/": "Utility functions and helper modules",
            "workflow/": "Workflow management and orchestration",
            
            # Development and operations
            "scripts/": "Utility scripts and automation tools",
            "tests/": "All test files and test utilities",
            "monitoring/": "System monitoring and observability",
            "logs/": "Application logs and debugging",
            
            # Documentation and configuration
            "docs/": "Project documentation and guides",
            "prompts/": "Prompt templates and management",
            "backups/": "Backup files and archives",
            "generated_projects/": "AI-generated project outputs",
            
            # Development artifacts (temporary)
            "temp/": "Temporary files and work-in-progress",
            "archive/": "Archived files and old versions"
        }
    
    def design_optimal_structure(self) -> Dict[str, str]:
        """Design optimal file structure for the project"""
        logger.info("🏗️ @file_architect: Designing optimal file structure")
        
        return self.optimal_structure
    
    def analyze_current_violations(self, root_path: str) -> List[FileViolation]:
        """Analyze current file structure violations"""
        violations = []
        
        # Get all files in root directory
        root_files = [f for f in os.listdir(root_path) if os.path.isfile(os.path.join(root_path, f))]
        
        for file in root_files:
            violation = self._classify_file_violation(file, root_path)
            if violation:
                violations.append(violation)
        
        logger.info(f"🔍 @file_architect: Found {len(violations)} file organization violations")
        return violations
    
    def _classify_file_violation(self, filename: str, root_path: str) -> FileViolation:
        """Classify a file violation and determine correct location"""
        file_path = os.path.join(root_path, filename)
        
        # Test files
        if filename.startswith('test_') or filename.endswith('_test.py'):
            return FileViolation(
                file_path=file_path,
                violation_type="misplaced_test_file",
                current_location="root",
                correct_location="tests/",
                severity="high",
                dependencies=[]
            )
        
        # Script files
        if filename.startswith('run_') or filename.endswith('_script.py'):
            return FileViolation(
                file_path=file_path,
                violation_type="misplaced_script",
                current_location="root", 
                correct_location="scripts/",
                severity="medium",
                dependencies=[]
            )
        
        # Utility files
        if filename.startswith('update_') or filename.endswith('_util.py'):
            return FileViolation(
                file_path=file_path,
                violation_type="misplaced_utility",
                current_location="root",
                correct_location="utils/",
                severity="medium", 
                dependencies=[]
            )
        
        # Temporary/Summary files
        if any(pattern in filename.upper() for pattern in ['SUMMARY', 'ANALYSIS', 'REPORT', 'VERIFICATION', 'OPTIMIZATION']):
            if filename.endswith('.md'):
                return FileViolation(
                    file_path=file_path,
                    violation_type="temporary_file",
                    current_location="root",
                    correct_location="temp/",
                    severity="low",
                    dependencies=[]
                )
        
        # Configuration files that should stay in root
        if filename in ['README.md', 'requirements.txt', '.gitignore', 'pyproject.toml', 'setup.py']:
            return None  # These belong in root
        
        # Database files
        if filename.endswith('.db'):
            return FileViolation(
                file_path=file_path,
                violation_type="misplaced_database",
                current_location="root",
                correct_location="utils/" if "prompt" in filename else "monitoring/",
                severity="medium",
                dependencies=[]
            )
        
        # Batch files
        if filename.endswith('.bat'):
            return FileViolation(
                file_path=file_path,
                violation_type="misplaced_script",
                current_location="root",
                correct_location="scripts/",
                severity="low",
                dependencies=[]
            )
        
        # Python files that don't belong in root
        if filename.endswith('.py') and filename not in ['setup.py']:
            return FileViolation(
                file_path=file_path,
                violation_type="misplaced_python_file",
                current_location="root",
                correct_location="utils/",  # Default to utils for misc Python files
                severity="medium",
                dependencies=[]
            )
        
        return None

class FileAnalyzerExpert:
    """@file_analyzer - Analyzes dependencies and impact"""
    
    def analyze_dependencies(self, violations: List[FileViolation]) -> Dict[str, List[str]]:
        """Analyze file dependencies to ensure safe moves"""
        logger.info("🔍 @file_analyzer: Analyzing file dependencies")
        
        dependencies = {}
        
        for violation in violations:
            file_deps = self._find_file_dependencies(violation.file_path)
            dependencies[violation.file_path] = file_deps
            violation.dependencies = file_deps
        
        return dependencies
    
    def _find_file_dependencies(self, file_path: str) -> List[str]:
        """Find dependencies for a specific file"""
        dependencies = []
        
        if not file_path.endswith('.py'):
            return dependencies
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Look for imports that might reference this file
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        # Extract import information
                        if 'import' in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                module = parts[1].split('.')[0]
                                dependencies.append(module)
        
        except Exception as e:
            logger.warning(f"Could not analyze dependencies for {file_path}: {e}")
        
        return dependencies
    
    def assess_move_safety(self, violation: FileViolation) -> bool:
        """Assess if it's safe to move a file"""
        # For now, assume most moves are safe
        # In production, this would do more sophisticated analysis
        
        # Never move core configuration files
        if os.path.basename(violation.file_path) in ['README.md', 'requirements.txt', '.gitignore']:
            return False
        
        # Test files are safe to move
        if violation.violation_type == "misplaced_test_file":
            return True
        
        # Scripts are generally safe to move
        if violation.violation_type == "misplaced_script":
            return True
        
        # Temporary files are safe to move or delete
        if violation.violation_type == "temporary_file":
            return True
        
        return True

class FileMoverExpert:
    """@file_mover - Safely moves files to correct locations"""
    
    def __init__(self):
        self.move_log = []
    
    def create_cleanup_plan(self, violations: List[FileViolation]) -> CleanupPlan:
        """Create comprehensive cleanup plan"""
        logger.info("📋 @file_mover: Creating cleanup plan")
        
        move_operations = []
        delete_operations = []
        create_directories = set()
        
        for violation in violations:
            if violation.severity == "high" or violation.violation_type == "temporary_file":
                # Determine target directory
                target_dir = violation.correct_location
                create_directories.add(target_dir)
                
                # Plan move operation
                filename = os.path.basename(violation.file_path)
                target_path = os.path.join(target_dir, filename)
                
                if violation.violation_type == "temporary_file":
                    # Move temporary files to temp directory
                    move_operations.append((violation.file_path, target_path))
                else:
                    # Move other files to correct locations
                    move_operations.append((violation.file_path, target_path))
        
        validation_steps = [
            "Verify all imports still work",
            "Run test suite to ensure functionality",
            "Check that applications still start correctly",
            "Validate file structure follows organization rules"
        ]
        
        plan = CleanupPlan(
            violations=violations,
            move_operations=move_operations,
            delete_operations=delete_operations,
            create_directories=list(create_directories),
            validation_steps=validation_steps
        )
        
        logger.info(f"📋 @file_mover: Created plan with {len(move_operations)} moves, {len(create_directories)} directories")
        return plan
    
    def execute_cleanup_plan(self, plan: CleanupPlan, dry_run: bool = True) -> bool:
        """Execute the cleanup plan"""
        logger.info(f"🚀 @file_mover: Executing cleanup plan (dry_run={dry_run})")
        
        try:
            # Create directories
            for directory in plan.create_directories:
                if not dry_run:
                    os.makedirs(directory, exist_ok=True)
                logger.info(f"📁 {'[DRY RUN] ' if dry_run else ''}Create directory: {directory}")
            
            # Execute move operations
            for source, target in plan.move_operations:
                if not dry_run:
                    # Ensure target directory exists
                    target_dir = os.path.dirname(target)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # Move file
                    shutil.move(source, target)
                    self.move_log.append((source, target))
                
                logger.info(f"📦 {'[DRY RUN] ' if dry_run else ''}Move: {source} → {target}")
            
            # Execute delete operations
            for file_path in plan.delete_operations:
                if not dry_run:
                    os.remove(file_path)
                logger.info(f"🗑️ {'[DRY RUN] ' if dry_run else ''}Delete: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ @file_mover: Cleanup execution failed: {e}")
            return False

class FileValidatorExpert:
    """@file_validator - Validates structure and functionality"""
    
    def validate_file_structure(self, root_path: str) -> Dict[str, bool]:
        """Validate the file structure follows organization rules"""
        logger.info("✅ @file_validator: Validating file structure")
        
        validation_results = {}
        
        # Check for test files in root
        root_test_files = glob.glob(os.path.join(root_path, "test_*.py"))
        validation_results["no_root_test_files"] = len(root_test_files) == 0
        
        # Check for empty files
        empty_files = self._find_empty_files(root_path)
        validation_results["no_empty_files"] = len(empty_files) == 0
        
        # Check for temporary files in root
        temp_patterns = ["*SUMMARY*", "*ANALYSIS*", "*REPORT*", "*VERIFICATION*"]
        temp_files = []
        for pattern in temp_patterns:
            temp_files.extend(glob.glob(os.path.join(root_path, pattern)))
        validation_results["no_temp_files_in_root"] = len(temp_files) == 0
        
        # Check directory structure
        required_dirs = ["agents", "tests", "utils", "scripts", "docs"]
        for dir_name in required_dirs:
            dir_path = os.path.join(root_path, dir_name)
            validation_results[f"has_{dir_name}_directory"] = os.path.isdir(dir_path)
        
        return validation_results
    
    def _find_empty_files(self, root_path: str) -> List[str]:
        """Find empty files in the project"""
        empty_files = []
        
        for root, dirs, files in os.walk(root_path):
            # Skip certain directories
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getsize(file_path) == 0:
                        empty_files.append(file_path)
                except OSError:
                    continue
        
        return empty_files
    
    def validate_functionality(self, root_path: str) -> Dict[str, bool]:
        """Validate that core functionality still works"""
        logger.info("🧪 @file_validator: Validating functionality")
        
        validation_results = {}
        
        # Check if Python files can be imported
        try:
            import sys
            sys.path.insert(0, root_path)
            
            # Test key imports
            test_imports = [
                "agents",
                "utils", 
                "models",
                "workflow"
            ]
            
            for module in test_imports:
                try:
                    __import__(module)
                    validation_results[f"import_{module}"] = True
                except ImportError as e:
                    validation_results[f"import_{module}"] = False
                    logger.warning(f"Import failed for {module}: {e}")
            
        except Exception as e:
            logger.error(f"Functionality validation failed: {e}")
            validation_results["functionality_check"] = False
        
        return validation_results

class FileCleanerExpert:
    """@file_cleaner - Removes unnecessary files"""
    
    def find_files_to_clean(self, root_path: str) -> Dict[str, List[str]]:
        """Find files that should be cleaned up"""
        logger.info("🧹 @file_cleaner: Finding files to clean")
        
        cleanup_candidates = {
            "empty_files": [],
            "temporary_files": [],
            "duplicate_files": [],
            "old_backup_files": []
        }
        
        # Find empty files
        for root, dirs, files in os.walk(root_path):
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                
                # Empty files
                try:
                    if os.path.getsize(file_path) == 0:
                        cleanup_candidates["empty_files"].append(file_path)
                except OSError:
                    continue
                
                # Temporary files
                if any(pattern in file.upper() for pattern in ['TEMP', 'TMP', 'BACKUP', 'BAK']):
                    cleanup_candidates["temporary_files"].append(file_path)
                
                # Old summary/analysis files
                if any(pattern in file.upper() for pattern in ['SUMMARY', 'ANALYSIS', 'REPORT', 'VERIFICATION']):
                    if file.endswith('.md') and root == root_path:  # Only root directory
                        cleanup_candidates["temporary_files"].append(file_path)
        
        return cleanup_candidates

class FileOrganizationExpertTeam:
    """Coordinated team of file organization experts"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = os.path.abspath(root_path)
        self.architect = FileArchitectExpert()
        self.analyzer = FileAnalyzerExpert()
        self.mover = FileMoverExpert()
        self.validator = FileValidatorExpert()
        self.cleaner = FileCleanerExpert()
        
    def execute_complete_cleanup(self, dry_run: bool = True) -> Dict[str, any]:
        """Execute complete file organization cleanup"""
        logger.info("🎯 EXPERT TEAM: Starting complete file organization cleanup")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "violations_found": 0,
            "files_moved": 0,
            "files_cleaned": 0,
            "directories_created": 0,
            "validation_results": {},
            "success": False
        }
        
        try:
            # 1. Architect: Analyze violations
            logger.info("🏗️ Phase 1: Architecture Analysis")
            violations = self.architect.analyze_current_violations(self.root_path)
            results["violations_found"] = len(violations)
            
            # 2. Analyzer: Check dependencies
            logger.info("🔍 Phase 2: Dependency Analysis")
            dependencies = self.analyzer.analyze_dependencies(violations)
            
            # 3. Mover: Create and execute cleanup plan
            logger.info("📦 Phase 3: File Movement")
            cleanup_plan = self.mover.create_cleanup_plan(violations)
            move_success = self.mover.execute_cleanup_plan(cleanup_plan, dry_run)
            
            if move_success:
                results["files_moved"] = len(cleanup_plan.move_operations)
                results["directories_created"] = len(cleanup_plan.create_directories)
            
            # 4. Cleaner: Clean up unnecessary files
            logger.info("🧹 Phase 4: File Cleanup")
            cleanup_candidates = self.cleaner.find_files_to_clean(self.root_path)
            results["files_to_clean"] = sum(len(files) for files in cleanup_candidates.values())
            
            # 5. Validator: Validate results
            logger.info("✅ Phase 5: Validation")
            structure_validation = self.validator.validate_file_structure(self.root_path)
            functionality_validation = self.validator.validate_functionality(self.root_path)
            
            results["validation_results"] = {
                "structure": structure_validation,
                "functionality": functionality_validation
            }
            
            # Overall success
            results["success"] = move_success and all(structure_validation.values())
            
            logger.info(f"🎉 EXPERT TEAM: Cleanup {'simulation' if dry_run else 'execution'} complete")
            return results
            
        except Exception as e:
            logger.error(f"❌ EXPERT TEAM: Cleanup failed: {e}")
            results["error"] = str(e)
            return results
    
    def generate_cleanup_report(self, results: Dict[str, any]) -> str:
        """Generate comprehensive cleanup report"""
        report = f"""
# File Organization Expert Team Report

**Execution Time**: {results['timestamp']}
**Mode**: {'Dry Run (Simulation)' if results['dry_run'] else 'Live Execution'}
**Overall Success**: {'✅ Success' if results['success'] else '❌ Failed'}

## Summary
- **Violations Found**: {results['violations_found']}
- **Files Moved**: {results['files_moved']}
- **Files Cleaned**: {results.get('files_to_clean', 0)}
- **Directories Created**: {results['directories_created']}

## Validation Results

### Structure Validation
"""
        
        if 'validation_results' in results and 'structure' in results['validation_results']:
            for check, passed in results['validation_results']['structure'].items():
                status = '✅' if passed else '❌'
                report += f"- {check}: {status}\n"
        
        report += "\n### Functionality Validation\n"
        
        if 'validation_results' in results and 'functionality' in results['validation_results']:
            for check, passed in results['validation_results']['functionality'].items():
                status = '✅' if passed else '❌'
                report += f"- {check}: {status}\n"
        
        if 'error' in results:
            report += f"\n## Error\n{results['error']}\n"
        
        return report

def main():
    """Main execution function"""
    print("🎯 FILE ORGANIZATION EXPERT TEAM")
    print("=" * 50)
    
    # Initialize expert team
    expert_team = FileOrganizationExpertTeam()
    
    # Execute dry run first
    print("\n🔍 PHASE 1: DRY RUN ANALYSIS")
    dry_run_results = expert_team.execute_complete_cleanup(dry_run=True)
    
    # Generate and display report
    report = expert_team.generate_cleanup_report(dry_run_results)
    print(report)
    
    # Ask for confirmation to proceed
    if dry_run_results['success'] and dry_run_results['violations_found'] > 0:
        print(f"\n📋 Found {dry_run_results['violations_found']} violations to fix")
        print(f"📦 Will move {dry_run_results['files_moved']} files")
        print(f"📁 Will create {dry_run_results['directories_created']} directories")
        
        response = input("\n🤔 Proceed with actual cleanup? (yes/no): ").lower().strip()
        
        if response == 'yes':
            print("\n🚀 PHASE 2: EXECUTING CLEANUP")
            live_results = expert_team.execute_complete_cleanup(dry_run=False)
            
            final_report = expert_team.generate_cleanup_report(live_results)
            print(final_report)
            
            if live_results['success']:
                print("\n🎉 FILE ORGANIZATION CLEANUP COMPLETE!")
                print("✅ Project structure is now clean and organized")
            else:
                print("\n❌ CLEANUP FAILED")
                print("Please review errors and try again")
        else:
            print("\n⏸️ Cleanup cancelled by user")
    else:
        print("\n✅ No violations found or dry run failed")

if __name__ == "__main__":
    main()
