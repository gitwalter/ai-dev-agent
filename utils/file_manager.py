"""
File management utilities for the AI Development Agent system.
Provides safe file operations and project structure management.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import logging


class FileManager:
    """
    Manages file operations for the AI Development Agent system.
    Provides safe file operations and project structure management.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize FileManager with project root.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or Path.cwd()
        self.logger = logging.getLogger(f"utils.{self.__class__.__name__}")
        
    def ensure_directory(self, directory_path: Path) -> bool:
        """
        Ensure directory exists, creating it if necessary.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            directory_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create directory {directory_path}: {e}")
            return False
    
    def safe_write_file(self, file_path: Path, content: str, backup: bool = True) -> bool:
        """
        Safely write content to file with optional backup.
        
        Args:
            file_path: Path to file
            content: Content to write
            backup: Whether to create backup of existing file
            
        Returns:
            True if write was successful
        """
        try:
            # Ensure parent directory exists
            self.ensure_directory(file_path.parent)
            
            # Create backup if requested and file exists
            if backup and file_path.exists():
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                shutil.copy2(file_path, backup_path)
                self.logger.debug(f"Created backup: {backup_path}")
            
            # Write content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.debug(f"Successfully wrote file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write file {file_path}: {e}")
            return False
    
    def safe_read_file(self, file_path: Path) -> Optional[str]:
        """
        Safely read content from file.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content or None if read failed
        """
        try:
            if not file_path.exists():
                self.logger.warning(f"File does not exist: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.debug(f"Successfully read file: {file_path}")
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    def safe_delete_file(self, file_path: Path, backup: bool = True) -> bool:
        """
        Safely delete file with optional backup.
        
        Args:
            file_path: Path to file
            backup: Whether to create backup before deletion
            
        Returns:
            True if deletion was successful
        """
        try:
            if not file_path.exists():
                self.logger.warning(f"File does not exist: {file_path}")
                return True
            
            # Create backup if requested
            if backup:
                backup_path = file_path.with_suffix(f"{file_path.suffix}.deleted")
                shutil.copy2(file_path, backup_path)
                self.logger.debug(f"Created backup before deletion: {backup_path}")
            
            # Delete file
            file_path.unlink()
            self.logger.debug(f"Successfully deleted file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def copy_file(self, source_path: Path, destination_path: Path) -> bool:
        """
        Copy file from source to destination.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            True if copy was successful
        """
        try:
            # Ensure destination directory exists
            self.ensure_directory(destination_path.parent)
            
            # Copy file
            shutil.copy2(source_path, destination_path)
            self.logger.debug(f"Successfully copied file from {source_path} to {destination_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to copy file from {source_path} to {destination_path}: {e}")
            return False
    
    def move_file(self, source_path: Path, destination_path: Path) -> bool:
        """
        Move file from source to destination.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            True if move was successful
        """
        try:
            # Ensure destination directory exists
            self.ensure_directory(destination_path.parent)
            
            # Move file
            shutil.move(str(source_path), str(destination_path))
            self.logger.debug(f"Successfully moved file from {source_path} to {destination_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to move file from {source_path} to {destination_path}: {e}")
            return False
    
    def list_files(self, directory_path: Path, pattern: str = "*", recursive: bool = True) -> List[Path]:
        """
        List files matching pattern in directory.
        
        Args:
            directory_path: Directory to search
            pattern: File pattern to match
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        try:
            if not directory_path.exists():
                self.logger.warning(f"Directory does not exist: {directory_path}")
                return []
            
            if recursive:
                files = list(directory_path.rglob(pattern))
            else:
                files = list(directory_path.glob(pattern))
            
            # Filter to only include files (not directories)
            files = [f for f in files if f.is_file()]
            
            self.logger.debug(f"Found {len(files)} files matching pattern '{pattern}' in {directory_path}")
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to list files in {directory_path}: {e}")
            return []
    
    def save_json(self, file_path: Path, data: Dict[str, Any], backup: bool = True) -> bool:
        """
        Save data as JSON file.
        
        Args:
            file_path: Path to JSON file
            data: Data to save
            backup: Whether to create backup of existing file
            
        Returns:
            True if save was successful
        """
        try:
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            return self.safe_write_file(file_path, json_content, backup)
            
        except Exception as e:
            self.logger.error(f"Failed to save JSON file {file_path}: {e}")
            return False
    
    def load_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load data from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Loaded data or None if load failed
        """
        try:
            content = self.safe_read_file(file_path)
            if content is None:
                return None
            
            return json.loads(content)
            
        except Exception as e:
            self.logger.error(f"Failed to load JSON file {file_path}: {e}")
            return None
    
    def get_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            File information dictionary or None if file doesn't exist
        """
        try:
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            return {
                "path": str(file_path),
                "name": file_path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir(),
                "suffix": file_path.suffix,
                "stem": file_path.stem
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {e}")
            return None

