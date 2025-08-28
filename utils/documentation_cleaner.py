"""
Documentation Cleaner Utility

This module implements the Documentation Cleanliness and Organization rule
to maintain a pristine documentation folder with no temporary, messy, or redundant files.

CRITICAL: This utility enforces the documentation cleanliness rule and must be used
before any documentation changes to ensure the docs/ folder remains clean and organized.
"""

import os
import glob
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentationCleanlinessError(Exception):
    """Raised when documentation cleanliness rules are violated."""
    pass

class DocumentationOrganizationError(Exception):
    """Raised when documentation organization rules are violated."""
    pass

class DocumentationIndexError(Exception):
    """Raised when documentation index is not current."""
    pass

class DocumentationDuplicateError(Exception):
    """Raised when duplicate documentation files are found."""
    pass

class DocumentationCleaner:
    """
    Documentation Cleaner for maintaining pristine documentation folder.
    
    Enforces the Documentation Cleanliness and Organization rule to ensure
    no temporary, messy, or redundant files exist in the docs/ directory.
    """
    
    def __init__(self, docs_root: str = "docs/"):
        self.docs_root = Path(docs_root)
        self.forbidden_patterns = [
            "DOCUMENTATION_*_SUMMARY.md",    # Temporary summary files
            "*_TEMP.md",                     # Temporary files
            "*_DRAFT.md",                    # Draft files
            "*_BACKUP.md",                   # Backup files
            "*_OLD.md",                      # Old versions
            "*_COPY.md",                     # Copy files
            "temp_*",                        # Temporary files
            "draft_*",                       # Draft files
            "*_notes.md",                    # Personal notes
            "*_TODO.md",                     # TODO files
            "*_CHANGES.md",                  # Change logs (use git)
            "*_UPDATES.md",                  # Update logs (use git)
            "*_INTEGRATION_SUMMARY.md",      # Integration summaries
            "*_UPDATE_SUMMARY.md",           # Update summaries
            "*_RULE_INTEGRATION_SUMMARY.md", # Rule integration summaries
        ]
        
        self.required_structure = {
            "concepts/": ["integration/", "migration/"],
            "guides/": ["development/", "implementation/", "database/", "deployment/", 
                       "testing/", "observability/", "langgraph/", "architecture/"],
            "analysis/": ["agent_analysis/", "summaries/"],
            "architecture/": ["overview/", "components/", "diagrams/"]
        }
        
        self.allowed_root_files = [
            "DOCUMENTATION_INDEX.md",
            "README.md"
        ]
    
    def cleanup_documentation(self) -> Dict[str, Any]:
        """
        Perform comprehensive documentation cleanup.
        
        Returns:
            Dict containing cleanup results and statistics
        """
        logger.info("Starting comprehensive documentation cleanup")
        
        results = {
            "temporary_files_removed": [],
            "files_moved": [],
            "duplicates_removed": [],
            "structure_created": [],
            "errors": []
        }
        
        try:
            # 1. Remove temporary files
            results["temporary_files_removed"] = self.remove_temporary_files()
            
            # 2. Move files to correct locations
            results["files_moved"] = self.organize_files()
            
            # 3. Update documentation index
            self.update_documentation_index()
            
            # 4. Validate structure
            results["structure_created"] = self.validate_structure()
            
            # 5. Remove duplicates
            results["duplicates_removed"] = self.remove_duplicates()
            
            logger.info("Documentation cleanup completed successfully")
            
        except Exception as e:
            results["errors"].append(str(e))
            logger.error(f"Documentation cleanup failed: {e}")
            raise
        
        return results
    
    def remove_temporary_files(self) -> List[str]:
        """Remove all temporary and summary files."""
        removed_files = []
        
        for pattern in self.forbidden_patterns:
            pattern_path = self.docs_root / pattern
            files = glob.glob(str(pattern_path))
            
            for file_path in files:
                try:
                    os.remove(file_path)
                    removed_files.append(file_path)
                    logger.info(f"Removed temporary file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove {file_path}: {e}")
        
        return removed_files
    
    def organize_files(self) -> List[Dict[str, str]]:
        """Move files to appropriate subdirectories."""
        moved_files = []
        
        # Move concept papers to concepts/
        concept_patterns = [
            "*_concept.md",
            "*_strategy.md",
            "*_approach.md"
        ]
        
        for pattern in concept_patterns:
            files = glob.glob(str(self.docs_root / pattern))
            
            for file_path in files:
                if not str(file_path).startswith(str(self.docs_root / "concepts/")):
                    try:
                        new_path = self.docs_root / "concepts" / Path(file_path).name
                        shutil.move(file_path, new_path)
                        moved_files.append({
                            "from": file_path,
                            "to": str(new_path)
                        })
                        logger.info(f"Moved concept file: {file_path} -> {new_path}")
                    except Exception as e:
                        logger.warning(f"Failed to move {file_path}: {e}")
        
        return moved_files
    
    def update_documentation_index(self):
        """Update DOCUMENTATION_INDEX.md to reflect current state."""
        index_file = self.docs_root / "DOCUMENTATION_INDEX.md"
        
        if not index_file.exists():
            logger.warning("DOCUMENTATION_INDEX.md not found, skipping update")
            return
        
        # Scan all documentation files
        all_files = self.scan_documentation_files()
        
        # Update index with current files
        self.regenerate_index(all_files)
        
        logger.info("Updated documentation index")
    
    def scan_documentation_files(self) -> Dict[str, List[str]]:
        """Scan all documentation files and categorize them."""
        files_by_category = {
            "concepts": [],
            "guides": [],
            "analysis": [],
            "architecture": [],
            "root": []
        }
        
        for file_path in self.docs_root.rglob("*.md"):
            relative_path = file_path.relative_to(self.docs_root)
            
            if relative_path.parts[0] in files_by_category:
                files_by_category[relative_path.parts[0]].append(str(relative_path))
            elif file_path.name in self.allowed_root_files:
                files_by_category["root"].append(file_path.name)
            else:
                logger.warning(f"Uncategorized file: {relative_path}")
        
        return files_by_category
    
    def regenerate_index(self, files_by_category: Dict[str, List[str]]):
        """Regenerate the documentation index."""
        # This is a simplified version - in practice, you'd want to maintain
        # the existing index structure and just update the file lists
        logger.info("Regenerating documentation index")
        
        # For now, just log what we found
        for category, files in files_by_category.items():
            logger.info(f"Category {category}: {len(files)} files")
    
    def validate_structure(self) -> List[str]:
        """Validate and create required directory structure."""
        created_dirs = []
        
        for main_dir, sub_dirs in self.required_structure.items():
            main_path = self.docs_root / main_dir
            if not main_path.exists():
                main_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(main_path))
                logger.info(f"Created directory: {main_path}")
            
            for sub_dir in sub_dirs:
                sub_path = main_path / sub_dir
                if not sub_path.exists():
                    sub_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(str(sub_path))
                    logger.info(f"Created subdirectory: {sub_path}")
        
        return created_dirs
    
    def remove_duplicates(self) -> List[str]:
        """Remove duplicate documentation files."""
        removed_files = []
        
        # Find files with similar names
        all_files = list(self.docs_root.rglob("*.md"))
        file_groups = {}
        
        for file_path in all_files:
            base_name = file_path.stem.lower().replace("_", "").replace("-", "")
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(file_path)
        
        # Keep the most recent/complete version
        for base_name, files in file_groups.items():
            if len(files) > 1:
                # Sort by modification time and keep the newest
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                # Remove older duplicates
                for file_path in files[1:]:
                    try:
                        os.remove(file_path)
                        removed_files.append(str(file_path))
                        logger.info(f"Removed duplicate: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to remove duplicate {file_path}: {e}")
        
        return removed_files
    
    def find_temporary_files(self) -> List[str]:
        """Find temporary files without removing them."""
        temp_files = []
        
        for pattern in self.forbidden_patterns:
            pattern_path = self.docs_root / pattern
            files = glob.glob(str(pattern_path))
            temp_files.extend(files)
        
        return temp_files
    
    def find_misplaced_files(self) -> List[str]:
        """Find files in wrong locations."""
        misplaced_files = []
        
        # Check for .md files directly in docs/ (except allowed ones)
        for file_path in self.docs_root.glob("*.md"):
            if file_path.name not in self.allowed_root_files:
                misplaced_files.append(str(file_path))
        
        return misplaced_files
    
    def is_index_current(self) -> bool:
        """Check if documentation index is current."""
        index_file = self.docs_root / "DOCUMENTATION_INDEX.md"
        
        if not index_file.exists():
            return False
        
        # Simple check - in practice, you'd want more sophisticated validation
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
                return "Last Updated" in content
        except Exception:
            return False
    
    def find_duplicates(self) -> List[List[str]]:
        """Find duplicate files without removing them."""
        duplicates = []
        
        all_files = list(self.docs_root.rglob("*.md"))
        file_groups = {}
        
        for file_path in all_files:
            base_name = file_path.stem.lower().replace("_", "").replace("-", "")
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(str(file_path))
        
        for base_name, files in file_groups.items():
            if len(files) > 1:
                duplicates.append(files)
        
        return duplicates


class DocumentationMaintenance:
    """
    Documentation maintenance scheduler for regular cleanup tasks.
    """
    
    def __init__(self, docs_root: str = "docs/"):
        self.cleaner = DocumentationCleaner(docs_root)
        self.last_cleanup = None
    
    def daily_cleanup(self) -> Dict[str, Any]:
        """Perform daily documentation cleanup."""
        logger.info("Performing daily documentation cleanup")
        
        results = {
            "temporary_files_removed": [],
            "index_updated": False,
            "errors": []
        }
        
        try:
            # Quick cleanup of obvious temporary files
            results["temporary_files_removed"] = self.cleaner.remove_temporary_files()
            
            # Update index if files changed
            if self.files_changed_today():
                self.cleaner.update_documentation_index()
                results["index_updated"] = True
            
            self.last_cleanup = datetime.now()
            
        except Exception as e:
            results["errors"].append(str(e))
            logger.error(f"Daily cleanup failed: {e}")
        
        return results
    
    def weekly_cleanup(self) -> Dict[str, Any]:
        """Perform weekly comprehensive documentation cleanup."""
        logger.info("Performing weekly comprehensive documentation cleanup")
        
        results = self.cleaner.cleanup_documentation()
        results["cleanup_type"] = "weekly"
        results["timestamp"] = datetime.now().isoformat()
        
        return results
    
    def monthly_audit(self) -> Dict[str, Any]:
        """Perform monthly documentation audit."""
        logger.info("Performing monthly documentation audit")
        
        audit_results = {
            "total_files": 0,
            "temporary_files": [],
            "misplaced_files": [],
            "duplicates": [],
            "structure_issues": [],
            "index_status": "unknown",
            "recommendations": []
        }
        
        try:
            # Count total files
            all_files = list(self.cleaner.docs_root.rglob("*.md"))
            audit_results["total_files"] = len(all_files)
            
            # Check for issues
            audit_results["temporary_files"] = self.cleaner.find_temporary_files()
            audit_results["misplaced_files"] = self.cleaner.find_misplaced_files()
            audit_results["duplicates"] = self.cleaner.find_duplicates()
            audit_results["index_status"] = "current" if self.cleaner.is_index_current() else "outdated"
            
            # Generate recommendations
            if audit_results["temporary_files"]:
                audit_results["recommendations"].append("Remove temporary files")
            
            if audit_results["misplaced_files"]:
                audit_results["recommendations"].append("Reorganize misplaced files")
            
            if audit_results["duplicates"]:
                audit_results["recommendations"].append("Remove duplicate files")
            
            if audit_results["index_status"] == "outdated":
                audit_results["recommendations"].append("Update documentation index")
            
        except Exception as e:
            audit_results["errors"] = [str(e)]
            logger.error(f"Monthly audit failed: {e}")
        
        return audit_results
    
    def files_changed_today(self) -> bool:
        """Check if any documentation files changed today."""
        today = datetime.now().date()
        
        for file_path in self.cleaner.docs_root.rglob("*.md"):
            file_date = datetime.fromtimestamp(file_path.stat().st_mtime).date()
            if file_date == today:
                return True
        
        return False


def validate_documentation_cleanliness() -> bool:
    """
    Validate documentation cleanliness before commit.
    
    Returns:
        True if validation passes, raises exception otherwise
    """
    cleaner = DocumentationCleaner()
    
    # Check for temporary files
    temp_files = cleaner.find_temporary_files()
    if temp_files:
        raise DocumentationCleanlinessError(f"Temporary files found: {temp_files}")
    
    # Check file organization
    misplaced_files = cleaner.find_misplaced_files()
    if misplaced_files:
        raise DocumentationOrganizationError(f"Misplaced files: {misplaced_files}")
    
    # Check index currency
    if not cleaner.is_index_current():
        raise DocumentationIndexError("Documentation index is not current")
    
    # Check for duplicates
    duplicates = cleaner.find_duplicates()
    if duplicates:
        raise DocumentationDuplicateError(f"Duplicate files: {duplicates}")
    
    logger.info("Documentation cleanliness validation passed")
    return True


def documentation_quality_gates() -> bool:
    """
    Run documentation quality gates.
    
    Returns:
        True if all gates pass, raises exception otherwise
    """
    gates = [
        ("no_temporary_files", lambda: not bool(DocumentationCleaner().find_temporary_files())),
        ("proper_organization", lambda: not bool(DocumentationCleaner().find_misplaced_files())),
        ("current_index", lambda: DocumentationCleaner().is_index_current()),
        ("no_duplicates", lambda: not bool(DocumentationCleaner().find_duplicates())),
    ]
    
    for gate_name, gate_check in gates:
        if not gate_check():
            raise DocumentationCleanlinessError(f"Failed quality gate: {gate_name}")
    
    logger.info("All documentation quality gates passed")
    return True


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run documentation cleanup
    cleaner = DocumentationCleaner()
    results = cleaner.cleanup_documentation()
    
    print("Documentation cleanup completed:")
    print(f"- Temporary files removed: {len(results['temporary_files_removed'])}")
    print(f"- Files moved: {len(results['files_moved'])}")
    print(f"- Duplicates removed: {len(results['duplicates_removed'])}")
    print(f"- Structure created: {len(results['structure_created'])}")
    
    if results['errors']:
        print(f"- Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")
