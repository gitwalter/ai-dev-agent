"""
File management utilities for the AI Development Agent system.
Handles file operations, project structure, and artifact management.
"""

import os
import shutil
import zipfile
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

from models.config import StorageConfig


class FileManager:
    """
    Manages file operations for the AI Development Agent system.
    
    Handles:
    - Project file generation and organization
    - Backup and restore operations
    - File compression and archiving
    - Project structure validation
    """
    
    def __init__(self, config: StorageConfig):
        """
        Initialize the file manager.
        
        Args:
            config: Storage configuration
        """
        self.config = config
        self.logger = logging.getLogger("file_manager")
        
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self) -> None:
        """Create necessary directories for file operations."""
        directories = [
            self.config.output_dir,
            self.config.temp_dir,
            self.config.backup_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created directory: {directory}")
    
    def save_generated_files(
        self,
        files: Dict[str, str],
        project_name: str,
        base_path: Optional[str] = None
    ) -> str:
        """
        Save generated files to the output directory.
        
        Args:
            files: Dictionary of file paths and contents
            project_name: Name of the project
            base_path: Base path for the project (optional)
            
        Returns:
            Path to the saved project directory
        """
        if base_path is None:
            base_path = self.config.output_dir
        
        project_path = Path(base_path) / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        for file_path, content in files.items():
            # Validate and sanitize filename
            safe_file_path = self._validate_and_sanitize_filename(file_path)
            
            # Create full file path
            full_path = project_path / safe_file_path
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                saved_files.append(str(full_path))
                self.logger.debug(f"Saved file: {full_path}")
            except Exception as e:
                self.logger.error(f"Failed to save file {full_path}: {str(e)}")
                raise
        
        self.logger.info(f"Saved {len(saved_files)} files to {project_path}")
        return str(project_path)
    
    def _validate_and_sanitize_filename(self, filename: str) -> str:
        """
        Validate and sanitize a filename to make it safe for file system operations.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not filename or not isinstance(filename, str):
            return "unknown_file.txt"
        
        # Check length
        if len(filename) > 100:
            # Truncate and add extension
            safe_filename = filename[:95] + ".txt"
        else:
            safe_filename = filename
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/', '\n', '\r', '\t']
        for char in invalid_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # Check for common file extensions
        valid_extensions = ['.py', '.js', '.ts', '.java', '.txt', '.json', '.yml', '.yaml', '.md', '.html', '.css', '.xml', '.go', '.rs', '.cpp', '.c']
        if not any(safe_filename.endswith(ext) for ext in valid_extensions):
            safe_filename += '.txt'
        
        # Check that filename doesn't look like content
        if len(safe_filename) > 50 and (' ' in safe_filename or '\n' in safe_filename):
            # Generate a safe filename
            import hashlib
            safe_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
            safe_filename = f"file_{safe_hash}.txt"
        
        # Ensure filename is not empty
        if not safe_filename.strip():
            safe_filename = "unknown_file.txt"
        
        self.logger.debug(f"Sanitized filename: '{filename}' -> '{safe_filename}'")
        return safe_filename
    
    def create_project_structure(
        self,
        project_name: str,
        structure: Dict[str, Any],
        base_path: Optional[str] = None
    ) -> str:
        """
        Create a project directory structure.
        
        Args:
            project_name: Name of the project
            structure: Dictionary defining the project structure
            base_path: Base path for the project (optional)
            
        Returns:
            Path to the created project directory
        """
        if base_path is None:
            base_path = self.config.output_dir
        
        project_path = Path(base_path) / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        self._create_structure_recursive(project_path, structure)
        
        self.logger.info(f"Created project structure: {project_path}")
        return str(project_path)
    
    def _create_structure_recursive(self, current_path: Path, structure: Dict[str, Any]) -> None:
        """
        Recursively create directory structure.
        
        Args:
            current_path: Current directory path
            structure: Structure definition for current level
        """
        for name, content in structure.items():
            item_path = current_path / name
            
            if isinstance(content, dict):
                # Directory
                item_path.mkdir(exist_ok=True)
                self._create_structure_recursive(item_path, content)
            elif isinstance(content, str):
                # File with content
                item_path.parent.mkdir(parents=True, exist_ok=True)
                with open(item_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                # Empty file
                item_path.parent.mkdir(parents=True, exist_ok=True)
                item_path.touch()
    
    def create_backup(
        self,
        source_path: str,
        backup_name: Optional[str] = None,
        compress: Optional[bool] = None
    ) -> str:
        """
        Create a backup of a project directory.
        
        Args:
            source_path: Path to the source directory
            backup_name: Name for the backup (optional)
            compress: Whether to compress the backup (optional)
            
        Returns:
            Path to the backup file
        """
        if compress is None:
            compress = self.config.enable_compression
        
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")
        
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.name}_{timestamp}"
        
        backup_path = Path(self.config.backup_dir) / backup_name
        
        if compress:
            backup_path = backup_path.with_suffix('.zip')
            self._create_compressed_backup(source_path, backup_path)
        else:
            backup_path = backup_path.with_suffix('')
            shutil.copytree(source_path, backup_path)
        
        self.logger.info(f"Created backup: {backup_path}")
        return str(backup_path)
    
    def _create_compressed_backup(self, source_path: Path, backup_path: Path) -> None:
        """
        Create a compressed backup.
        
        Args:
            source_path: Path to the source directory
            backup_path: Path for the backup file
        """
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_path)
                    zipf.write(file_path, arcname)
    
    def restore_backup(
        self,
        backup_path: str,
        target_path: Optional[str] = None,
        overwrite: bool = False
    ) -> str:
        """
        Restore a project from backup.
        
        Args:
            backup_path: Path to the backup file
            target_path: Target path for restoration (optional)
            overwrite: Whether to overwrite existing files
            
        Returns:
            Path to the restored project
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file does not exist: {backup_path}")
        
        if target_path is None:
            target_path = self.config.output_dir
        
        target_path = Path(target_path)
        
        if target_path.exists() and not overwrite:
            raise FileExistsError(f"Target path exists and overwrite=False: {target_path}")
        
        if backup_path.suffix == '.zip':
            self._restore_compressed_backup(backup_path, target_path)
        else:
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(backup_path, target_path)
        
        self.logger.info(f"Restored backup to: {target_path}")
        return str(target_path)
    
    def _restore_compressed_backup(self, backup_path: Path, target_path: Path) -> None:
        """
        Restore a compressed backup.
        
        Args:
            backup_path: Path to the backup file
            target_path: Target path for restoration
        """
        if target_path.exists():
            shutil.rmtree(target_path)
        
        target_path.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(target_path)
    
    def cleanup_old_backups(self, keep_count: Optional[int] = None) -> List[str]:
        """
        Clean up old backup files.
        
        Args:
            keep_count: Number of backups to keep (optional)
            
        Returns:
            List of removed backup files
        """
        if keep_count is None:
            keep_count = self.config.max_backup_count
        
        backup_dir = Path(self.config.backup_dir)
        backup_files = list(backup_dir.glob('*'))
        
        # Sort by modification time (oldest first)
        backup_files.sort(key=lambda x: x.stat().st_mtime)
        
        # Remove old backups
        removed_files = []
        for backup_file in backup_files[:-keep_count]:
            try:
                backup_file.unlink()
                removed_files.append(str(backup_file))
                self.logger.debug(f"Removed old backup: {backup_file}")
            except Exception as e:
                self.logger.error(f"Failed to remove backup {backup_file}: {str(e)}")
        
        self.logger.info(f"Cleaned up {len(removed_files)} old backups")
        return removed_files
    
    def validate_project_structure(
        self,
        project_path: str,
        required_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate a project structure.
        
        Args:
            project_path: Path to the project
            required_files: List of required files (optional)
            
        Returns:
            Validation results
        """
        project_path = Path(project_path)
        if not project_path.exists():
            return {
                "valid": False,
                "errors": [f"Project path does not exist: {project_path}"]
            }
        
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "files": [],
            "directories": []
        }
        
        # Scan project structure
        for item in project_path.rglob('*'):
            if item.is_file():
                results["files"].append(str(item.relative_to(project_path)))
            elif item.is_dir():
                results["directories"].append(str(item.relative_to(project_path)))
        
        # Check required files
        if required_files:
            for required_file in required_files:
                if not (project_path / required_file).exists():
                    results["valid"] = False
                    results["errors"].append(f"Required file missing: {required_file}")
        
        # Check for common issues
        if not results["files"]:
            results["warnings"].append("No files found in project")
        
        # Check for common project files
        common_files = ["README.md", "requirements.txt", "setup.py", "package.json"]
        missing_common = [f for f in common_files if not (project_path / f).exists()]
        if missing_common:
            results["warnings"].append(f"Missing common project files: {missing_common}")
        
        self.logger.info(f"Project validation completed: {results['valid']}")
        return results
    
    def get_project_info(self, project_path: str) -> Dict[str, Any]:
        """
        Get information about a project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Project information
        """
        project_path = Path(project_path)
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        info = {
            "name": project_path.name,
            "path": str(project_path),
            "created": datetime.fromtimestamp(project_path.stat().st_ctime),
            "modified": datetime.fromtimestamp(project_path.stat().st_mtime),
            "size": 0,
            "file_count": 0,
            "directory_count": 0,
            "file_types": {},
            "largest_files": []
        }
        
        file_sizes = []
        
        for item in project_path.rglob('*'):
            if item.is_file():
                info["file_count"] += 1
                size = item.stat().st_size
                info["size"] += size
                file_sizes.append((str(item.relative_to(project_path)), size))
                
                # Count file types
                ext = item.suffix.lower()
                info["file_types"][ext] = info["file_types"].get(ext, 0) + 1
            elif item.is_dir():
                info["directory_count"] += 1
        
        # Get largest files
        file_sizes.sort(key=lambda x: x[1], reverse=True)
        info["largest_files"] = file_sizes[:10]
        
        return info
    
    def create_project_archive(
        self,
        project_path: str,
        archive_name: Optional[str] = None,
        include_git: bool = False
    ) -> str:
        """
        Create an archive of a project.
        
        Args:
            project_path: Path to the project
            archive_name: Name for the archive (optional)
            include_git: Whether to include .git directory
            
        Returns:
            Path to the archive file
        """
        project_path = Path(project_path)
        if not project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        if archive_name is None:
            archive_name = f"{project_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        archive_path = Path(self.config.output_dir) / f"{archive_name}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    # Skip .git directory unless explicitly included
                    if '.git' in file_path.parts and not include_git:
                        continue
                    
                    arcname = file_path.relative_to(project_path)
                    zipf.write(file_path, arcname)
        
        self.logger.info(f"Created project archive: {archive_path}")
        return str(archive_path)
    
    def cleanup_temp_files(self) -> List[str]:
        """
        Clean up temporary files.
        
        Returns:
            List of removed temporary files
        """
        temp_dir = Path(self.config.temp_dir)
        if not temp_dir.exists():
            return []
        
        removed_files = []
        
        for item in temp_dir.rglob('*'):
            if item.is_file():
                try:
                    item.unlink()
                    removed_files.append(str(item))
                except Exception as e:
                    self.logger.error(f"Failed to remove temp file {item}: {str(e)}")
            elif item.is_dir():
                try:
                    shutil.rmtree(item)
                    removed_files.append(str(item))
                except Exception as e:
                    self.logger.error(f"Failed to remove temp directory {item}: {str(e)}")
        
        self.logger.info(f"Cleaned up {len(removed_files)} temporary files")
        return removed_files
