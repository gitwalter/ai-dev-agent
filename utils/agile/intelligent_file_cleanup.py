"""
Intelligent File Cleanup System for Speed-Optimized Agile Framework

Uses the rapid execution engine to safely identify and clean up empty or unnecessary files
while maintaining project integrity and following the expert team staffing framework.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FileAnalysisResult:
    """Result of file analysis for cleanup decisions."""
    file_path: str
    file_size: int
    is_empty: bool
    is_safe_to_remove: bool
    reason: str
    category: str  # empty, temporary, duplicate, unnecessary
    importance_score: float  # 0.0 (safe to remove) to 1.0 (critical)


@dataclass
class CleanupReport:
    """Comprehensive cleanup report with safety metrics."""
    total_files_analyzed: int
    files_marked_for_removal: List[str]
    files_kept_for_safety: List[str]
    safety_score: float  # 0.0 to 1.0
    cleanup_categories: Dict[str, int]
    warnings: List[str]
    recommendations: List[str]


class IntelligentFileCleanup:
    """
    Intelligent file cleanup system with embedded safety checks.
    
    Uses expert team patterns from the speed-optimized agile framework
    to safely identify and remove unnecessary files.
    """
    
    def __init__(self, project_root: str = "."):
        """Initialize the intelligent cleanup system."""
        self.project_root = Path(project_root).resolve()
        self.safety_patterns = self._load_safety_patterns()
        self.critical_files = self._identify_critical_files()
        
        logger.info("🧹 Intelligent File Cleanup System initialized")
    
    def _load_safety_patterns(self) -> Dict[str, List[str]]:
        """Load safety patterns for file analysis."""
        return {
            "never_remove": [
                "__init__.py",  # Python package markers
                "requirements.txt", "setup.py", "pyproject.toml",  # Package management
                ".gitignore", ".gitattributes",  # Git configuration
                "README.md", "LICENSE", "CHANGELOG.md",  # Documentation
                "*.mdc",  # Cursor rules
                "*.yaml", "*.yml",  # Configuration files
            ],
            "safe_empty_removal": [
                "*.tmp", "*.temp", "*.bak", "*.backup",  # Temporary files
                "*.log",  # Log files (if empty)
                "*.cache",  # Cache files
            ],
            "careful_analysis": [
                "*.py",  # Python files need careful analysis
                "*.js", "*.ts",  # JavaScript/TypeScript
                "*.md",  # Markdown (some may be placeholders)
            ],
            "directories_preserve": [
                ".git", ".cursor", "__pycache__",  # System directories
                "node_modules", ".pytest_cache",  # Cache directories
                "generated_projects",  # AI-generated content
            ]
        }
    
    def _identify_critical_files(self) -> Set[str]:
        """Identify files that are absolutely critical to the project."""
        critical_files = set()
        
        # Always critical
        always_critical = [
            "README.md", "requirements.txt", "setup.py", "pyproject.toml",
            ".gitignore", "pytest.ini", "__init__.py"
        ]
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file in always_critical:
                    rel_path = os.path.relpath(os.path.join(root, file), self.project_root)
                    critical_files.add(rel_path)
        
        return critical_files
    
    async def analyze_project_files(self) -> Dict[str, FileAnalysisResult]:
        """Analyze all project files for cleanup potential."""
        logger.info("🔍 Starting intelligent file analysis")
        
        analysis_results = {}
        total_files = 0
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip system directories
            dirs[:] = [d for d in dirs if not any(skip in d for skip in 
                      self.safety_patterns["directories_preserve"])]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_root)
                
                total_files += 1
                analysis = await self._analyze_single_file(file_path, rel_path)
                analysis_results[rel_path] = analysis
        
        logger.info(f"📊 Analyzed {total_files} files")
        return analysis_results
    
    async def _analyze_single_file(self, file_path: str, rel_path: str) -> FileAnalysisResult:
        """Analyze a single file for cleanup potential."""
        try:
            file_size = os.path.getsize(file_path)
            is_empty = file_size == 0
            
            # Determine safety and importance
            is_safe, reason, category, importance = self._evaluate_file_safety(
                rel_path, file_size, is_empty
            )
            
            return FileAnalysisResult(
                file_path=rel_path,
                file_size=file_size,
                is_empty=is_empty,
                is_safe_to_remove=is_safe,
                reason=reason,
                category=category,
                importance_score=importance
            )
            
        except OSError as e:
            logger.warning(f"⚠️ Could not analyze file {rel_path}: {e}")
            return FileAnalysisResult(
                file_path=rel_path,
                file_size=0,
                is_empty=True,
                is_safe_to_remove=False,
                reason=f"Analysis failed: {e}",
                category="error",
                importance_score=1.0  # Assume important if can't analyze
            )
    
    def _evaluate_file_safety(self, rel_path: str, file_size: int, is_empty: bool) -> Tuple[bool, str, str, float]:
        """Evaluate whether a file is safe to remove."""
        file_name = os.path.basename(rel_path)
        file_ext = os.path.splitext(file_name)[1]
        
        # Never remove critical files
        if rel_path in self.critical_files:
            return False, "Critical project file", "critical", 1.0
        
        # Never remove files matching never_remove patterns
        for pattern in self.safety_patterns["never_remove"]:
            if self._matches_pattern(file_name, pattern):
                return False, f"Protected pattern: {pattern}", "protected", 1.0
        
        # Empty files analysis
        if is_empty:
            # Check if it's safe to remove empty files of this type
            for pattern in self.safety_patterns["safe_empty_removal"]:
                if self._matches_pattern(file_name, pattern):
                    return True, f"Empty temporary file: {pattern}", "empty_temp", 0.1
            
            # Special handling for __init__.py files (usually should be kept even if empty)
            if file_name == "__init__.py":
                return False, "Empty __init__.py (Python package marker)", "package_marker", 0.9
            
            # Empty Python files need careful consideration
            if file_ext == ".py":
                # Check if it's in a test directory or temporary location
                if any(part in rel_path.lower() for part in ["test", "temp", "tmp", "backup"]):
                    return True, "Empty Python file in test/temp location", "empty_test", 0.3
                else:
                    return False, "Empty Python file in main codebase", "empty_code", 0.7
            
            # Empty markdown files might be placeholders
            if file_ext == ".md":
                if any(word in file_name.lower() for word in ["placeholder", "todo", "draft"]):
                    return True, "Empty placeholder markdown", "empty_placeholder", 0.2
                else:
                    return False, "Empty markdown file (might be intentional)", "empty_doc", 0.5
            
            # Other empty files
            return True, "Empty file of unknown importance", "empty_unknown", 0.4
        
        # Non-empty files - generally keep unless specifically identified as temporary
        for pattern in self.safety_patterns["safe_empty_removal"]:
            if self._matches_pattern(file_name, pattern):
                return True, f"Temporary file: {pattern}", "temporary", 0.2
        
        # Check for very small files that might be artifacts
        if file_size < 10:  # Less than 10 bytes
            if file_ext in [".log", ".cache", ".tmp"]:
                return True, "Very small temporary file", "small_temp", 0.3
        
        # Default: keep the file
        return False, "Regular project file", "regular", 0.8
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a pattern (simple glob-like matching)."""
        if pattern.startswith("*."):
            return filename.endswith(pattern[1:])
        return filename == pattern
    
    async def generate_cleanup_report(self, analysis_results: Dict[str, FileAnalysisResult]) -> CleanupReport:
        """Generate a comprehensive cleanup report with safety metrics."""
        logger.info("📋 Generating cleanup report")
        
        files_for_removal = []
        files_kept = []
        categories = {}
        warnings = []
        recommendations = []
        
        total_files = len(analysis_results)
        safe_removal_count = 0
        
        for rel_path, analysis in analysis_results.items():
            # Count categories
            categories[analysis.category] = categories.get(analysis.category, 0) + 1
            
            if analysis.is_safe_to_remove:
                files_for_removal.append(rel_path)
                safe_removal_count += 1
            else:
                files_kept.append(rel_path)
            
            # Generate warnings for edge cases
            if analysis.is_empty and analysis.category == "empty_code":
                warnings.append(f"Empty Python file kept for safety: {rel_path}")
            
            if analysis.file_size < 10 and not analysis.is_empty:
                warnings.append(f"Very small file detected: {rel_path} ({analysis.file_size} bytes)")
        
        # Calculate safety score
        safety_score = 1.0 - (safe_removal_count / total_files) if total_files > 0 else 1.0
        
        # Generate recommendations
        empty_python_files = [path for path, analysis in analysis_results.items() 
                             if analysis.is_empty and path.endswith(".py") and not analysis.is_safe_to_remove]
        if empty_python_files:
            recommendations.append(f"Review {len(empty_python_files)} empty Python files manually")
        
        temp_files = [path for path, analysis in analysis_results.items() 
                     if analysis.category in ["empty_temp", "temporary"]]
        if temp_files:
            recommendations.append(f"Consider cleaning {len(temp_files)} temporary files")
        
        return CleanupReport(
            total_files_analyzed=total_files,
            files_marked_for_removal=files_for_removal,
            files_kept_for_safety=files_kept,
            safety_score=safety_score,
            cleanup_categories=categories,
            warnings=warnings,
            recommendations=recommendations
        )
    
    async def execute_safe_cleanup(self, analysis_results: Dict[str, FileAnalysisResult], 
                                  dry_run: bool = True) -> Dict[str, any]:
        """Execute safe file cleanup with comprehensive logging."""
        logger.info(f"🚀 Executing cleanup (dry_run={dry_run})")
        
        removed_files = []
        errors = []
        
        for rel_path, analysis in analysis_results.items():
            if analysis.is_safe_to_remove:
                full_path = os.path.join(self.project_root, rel_path)
                
                try:
                    if not dry_run:
                        os.remove(full_path)
                        logger.info(f"🗑️ Removed: {rel_path} ({analysis.reason})")
                    else:
                        logger.info(f"🗑️ Would remove: {rel_path} ({analysis.reason})")
                    
                    removed_files.append(rel_path)
                    
                except OSError as e:
                    error_msg = f"Failed to remove {rel_path}: {e}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
        
        return {
            "removed_files": removed_files,
            "errors": errors,
            "dry_run": dry_run,
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_intelligent_cleanup(self, dry_run: bool = True) -> Dict[str, any]:
        """Run the complete intelligent cleanup process."""
        start_time = datetime.now()
        logger.info("🧹 Starting intelligent file cleanup process")
        
        try:
            # Phase 1: Analyze all files
            analysis_results = await self.analyze_project_files()
            
            # Phase 2: Generate cleanup report
            cleanup_report = await self.generate_cleanup_report(analysis_results)
            
            # Phase 3: Execute cleanup
            execution_result = await self.execute_safe_cleanup(analysis_results, dry_run)
            
            # Generate final report
            execution_time = (datetime.now() - start_time).total_seconds()
            
            final_report = {
                "execution_time_seconds": execution_time,
                "dry_run": dry_run,
                "safety_score": cleanup_report.safety_score,
                "total_files_analyzed": cleanup_report.total_files_analyzed,
                "files_marked_for_removal": len(cleanup_report.files_marked_for_removal),
                "files_removed": len(execution_result["removed_files"]),
                "errors": execution_result["errors"],
                "warnings": cleanup_report.warnings,
                "recommendations": cleanup_report.recommendations,
                "categories": cleanup_report.cleanup_categories,
                "timestamp": start_time.isoformat(),
                "status": "success" if not execution_result["errors"] else "partial_success"
            }
            
            logger.info(f"✅ Cleanup completed in {execution_time:.2f} seconds")
            logger.info(f"📊 Safety Score: {cleanup_report.safety_score:.2%}")
            logger.info(f"🗑️ Files processed: {len(execution_result['removed_files'])}")
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": start_time.isoformat()
            }


# Integration with rapid execution engine
async def execute_intelligent_file_cleanup(project_root: str = ".", dry_run: bool = True) -> Dict[str, any]:
    """
    Main interface for intelligent file cleanup using rapid execution patterns.
    
    Args:
        project_root: Root directory of the project
        dry_run: If True, simulate cleanup without actually removing files
        
    Returns:
        Comprehensive cleanup report with safety metrics
    """
    cleanup_system = IntelligentFileCleanup(project_root)
    return await cleanup_system.run_intelligent_cleanup(dry_run)


# CLI interface for direct usage
async def main():
    """CLI interface for intelligent file cleanup."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Intelligent File Cleanup System")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (default is dry-run)")
    parser.add_argument("--output", help="Save report to JSON file")
    
    args = parser.parse_args()
    
    # Run cleanup
    dry_run = not args.execute
    result = await execute_intelligent_file_cleanup(args.project_root, dry_run)
    
    # Display results
    print("\n" + "="*60)
    print("INTELLIGENT FILE CLEANUP REPORT")
    print("="*60)
    print(f"Status: {result['status'].upper()}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTION'}")
    print(f"Safety Score: {result.get('safety_score', 0):.2%}")
    print(f"Files Analyzed: {result.get('total_files_analyzed', 0)}")
    print(f"Files Processed: {result.get('files_removed', 0)}")
    print(f"Execution Time: {result.get('execution_time_seconds', 0):.2f} seconds")
    
    if result.get('warnings'):
        print(f"\nWarnings ({len(result['warnings'])}):")
        for warning in result['warnings']:
            print(f"  ⚠️ {warning}")
    
    if result.get('recommendations'):
        print(f"\nRecommendations ({len(result['recommendations'])}):")
        for rec in result['recommendations']:
            print(f"  💡 {rec}")
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
