#!/usr/bin/env python3
"""
File Access MCP Tools
=====================

MCP tools for file system operations including reading, writing, searching,
and analyzing files. Provides safe file access for agents with proper validation.

Created: 2025-10-10
Sprint: US-RAG-001 Enhancement
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import mimetypes
import hashlib

# MCP Tool Integration
try:
    from utils.mcp.mcp_tool import mcp_tool, AccessLevel, ToolCategory
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

logger = logging.getLogger(__name__)

# Project root for safety checks
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


# ============================================================================
# File Safety and Validation
# ============================================================================

def is_safe_path(file_path: str) -> bool:
    """Check if file path is safe to access."""
    try:
        path = Path(file_path).resolve()
        # Must be within project root or explicitly allowed directories
        return path.is_relative_to(PROJECT_ROOT)
    except Exception:
        return False


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get comprehensive file information."""
    path = Path(file_path)
    
    if not path.exists():
        return {"error": "File not found"}
    
    stat = path.stat()
    mime_type, _ = mimetypes.guess_type(str(path))
    
    return {
        "path": str(path),
        "name": path.name,
        "size": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "is_file": path.is_file(),
        "is_dir": path.is_directory(),
        "extension": path.suffix,
        "mime_type": mime_type,
        "readable": os.access(path, os.R_OK),
        "writable": os.access(path, os.W_OK)
    }


# ============================================================================
# MCP Tools - File Access
# ============================================================================

if MCP_AVAILABLE:
    
    @mcp_tool(
        "file.read",
        "Read contents of a file with optional line range",
        AccessLevel.UNRESTRICTED,
        ToolCategory.FILE_SYSTEM
    )
    def read_file_mcp(
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        max_size_mb: int = 10
    ) -> Dict[str, Any]:
        """
        Read file contents with optional line range.
        
        Args:
            file_path: Path to file to read
            start_line: Optional start line (1-indexed)
            end_line: Optional end line (1-indexed)
            max_size_mb: Maximum file size in MB
            
        Returns:
            File contents and metadata
        """
        try:
            # Safety check
            if not is_safe_path(file_path):
                return {"error": "Access denied - path outside project scope"}
            
            path = Path(file_path)
            
            if not path.exists():
                return {"error": f"File not found: {file_path}"}
            
            if not path.is_file():
                return {"error": f"Not a file: {file_path}"}
            
            # Size check
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > max_size_mb:
                return {"error": f"File too large: {file_size_mb:.2f}MB (max: {max_size_mb}MB)"}
            
            # Read file
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                if start_line or end_line:
                    lines = f.readlines()
                    start = (start_line - 1) if start_line else 0
                    end = end_line if end_line else len(lines)
                    content = ''.join(lines[start:end])
                    line_count = end - start
                else:
                    content = f.read()
                    line_count = len(content.split('\n'))
            
            return {
                "success": True,
                "file_path": str(path),
                "content": content,
                "line_count": line_count,
                "size_bytes": len(content),
                "encoding": "utf-8",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "file.write",
        "Write content to a file (creates or overwrites)",
        AccessLevel.RESTRICTED,
        ToolCategory.FILE_SYSTEM
    )
    def write_file_mcp(
        file_path: str,
        content: str,
        create_dirs: bool = True,
        backup: bool = True
    ) -> Dict[str, Any]:
        """
        Write content to file with optional backup.
        
        Args:
            file_path: Path to file
            content: Content to write
            create_dirs: Create parent directories if needed
            backup: Create backup if file exists
            
        Returns:
            Write operation result
        """
        try:
            # Safety check
            if not is_safe_path(file_path):
                return {"error": "Access denied - path outside project scope"}
            
            path = Path(file_path)
            
            # Create parent directories if needed
            if create_dirs and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup existing file
            backup_path = None
            if backup and path.exists():
                backup_path = path.with_suffix(path.suffix + '.backup')
                import shutil
                shutil.copy2(path, backup_path)
            
            # Write file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": str(path),
                "bytes_written": len(content),
                "lines_written": len(content.split('\n')),
                "backup_created": backup_path is not None,
                "backup_path": str(backup_path) if backup_path else None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "file.list_directory",
        "List files and directories with filtering options",
        AccessLevel.UNRESTRICTED,
        ToolCategory.FILE_SYSTEM
    )
    def list_directory_mcp(
        directory: str = ".",
        pattern: Optional[str] = None,
        recursive: bool = False,
        include_hidden: bool = False,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List directory contents with filtering.
        
        Args:
            directory: Directory to list
            pattern: Glob pattern for filtering (e.g., "*.py")
            recursive: Search subdirectories
            include_hidden: Include hidden files (starting with .)
            file_type: Filter by type ("file", "dir", or None for both)
            
        Returns:
            List of files/directories with metadata
        """
        try:
            # Safety check
            if not is_safe_path(directory):
                return {"error": "Access denied - path outside project scope"}
            
            path = Path(directory)
            
            if not path.exists():
                return {"error": f"Directory not found: {directory}"}
            
            if not path.is_dir():
                return {"error": f"Not a directory: {directory}"}
            
            # Gather files
            files = []
            
            if recursive:
                pattern_str = f"**/{pattern}" if pattern else "**/*"
            else:
                pattern_str = pattern or "*"
            
            for item in path.glob(pattern_str):
                # Skip hidden files if not included
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                # Filter by type
                if file_type == "file" and not item.is_file():
                    continue
                if file_type == "dir" and not item.is_dir():
                    continue
                
                files.append({
                    "path": str(item.relative_to(path)),
                    "name": item.name,
                    "is_file": item.is_file(),
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else None,
                    "extension": item.suffix if item.is_file() else None,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            
            return {
                "success": True,
                "directory": str(path),
                "total_items": len(files),
                "files": files,
                "filters": {
                    "pattern": pattern,
                    "recursive": recursive,
                    "file_type": file_type
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to list directory {directory}: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "file.search_content",
        "Search for text content within files",
        AccessLevel.UNRESTRICTED,
        ToolCategory.FILE_SYSTEM
    )
    def search_content_mcp(
        search_text: str,
        directory: str = ".",
        file_pattern: str = "*.py",
        case_sensitive: bool = False,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        Search for text content in files.
        
        Args:
            search_text: Text to search for
            directory: Directory to search in
            file_pattern: File pattern (e.g., "*.py")
            case_sensitive: Case-sensitive search
            max_results: Maximum number of results
            
        Returns:
            Search results with file locations
        """
        try:
            # Safety check
            if not is_safe_path(directory):
                return {"error": "Access denied - path outside project scope"}
            
            path = Path(directory)
            
            if not path.exists():
                return {"error": f"Directory not found: {directory}"}
            
            results = []
            search_lower = search_text if case_sensitive else search_text.lower()
            
            # Search files
            for file_path in path.rglob(file_pattern):
                if not file_path.is_file():
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            line_to_search = line if case_sensitive else line.lower()
                            
                            if search_lower in line_to_search:
                                results.append({
                                    "file": str(file_path.relative_to(path)),
                                    "line_number": line_num,
                                    "line_content": line.strip(),
                                    "match_position": line_to_search.find(search_lower)
                                })
                                
                                if len(results) >= max_results:
                                    break
                    
                    if len(results) >= max_results:
                        break
                        
                except Exception:
                    continue
            
            return {
                "success": True,
                "search_text": search_text,
                "directory": str(path),
                "total_matches": len(results),
                "results": results,
                "truncated": len(results) >= max_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to search content: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "file.get_info",
        "Get detailed file information and metadata",
        AccessLevel.UNRESTRICTED,
        ToolCategory.FILE_SYSTEM
    )
    def get_file_info_mcp(file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            File information and metadata
        """
        try:
            # Safety check
            if not is_safe_path(file_path):
                return {"error": "Access denied - path outside project scope"}
            
            info = get_file_info(file_path)
            
            if "error" not in info:
                info["success"] = True
                info["timestamp"] = datetime.now().isoformat()
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "file.exists",
        "Check if a file or directory exists",
        AccessLevel.UNRESTRICTED,
        ToolCategory.FILE_SYSTEM
    )
    def file_exists_mcp(file_path: str) -> Dict[str, Any]:
        """
        Check if file or directory exists.
        
        Args:
            file_path: Path to check
            
        Returns:
            Existence status with type information
        """
        try:
            # Safety check
            if not is_safe_path(file_path):
                return {"error": "Access denied - path outside project scope"}
            
            path = Path(file_path)
            
            return {
                "success": True,
                "file_path": str(path),
                "exists": path.exists(),
                "is_file": path.is_file() if path.exists() else False,
                "is_dir": path.is_dir() if path.exists() else False,
                "is_symlink": path.is_symlink() if path.exists() else False,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to check file existence: {e}")
            return {"error": str(e)}


# ============================================================================
# Utility Functions
# ============================================================================

def calculate_file_hash(file_path: str) -> Optional[str]:
    """Calculate SHA256 hash of file."""
    try:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)
        return sha256.hexdigest()
    except Exception:
        return None


if __name__ == "__main__":
    # Test file access tools
    print("🧪 Testing File Access MCP Tools")
    
    # Test list directory
    result = list_directory_mcp(".", pattern="*.py", recursive=False)
    print(f"\n📂 Found {result.get('total_items', 0)} Python files")
    
    # Test file exists
    result = file_exists_mcp("README.md")
    print(f"\n📄 README.md exists: {result.get('exists', False)}")
    
    print("\n✅ File access tools test complete!")

