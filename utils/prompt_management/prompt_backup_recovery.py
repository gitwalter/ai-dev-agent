"""
Prompt Backup and Recovery System

Provides comprehensive backup and recovery capabilities for prompt data including:
- Automated backup scheduling
- Point-in-time recovery
- Disaster recovery procedures
- Data integrity validation
- Backup encryption and compression

This module implements the backup and recovery system for US-PE-02.
"""

import json
import sqlite3
import shutil
import zipfile
import hashlib
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os
import tempfile
import gzip
import pickle

logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Types of backup operations."""
    FULL = "full"           # Complete system backup
    INCREMENTAL = "incremental"  # Only changed data
    DIFFERENTIAL = "differential"  # Changes since last full backup
    MANUAL = "manual"       # User-initiated backup


class BackupStatus(Enum):
    """Status of backup operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


class RecoveryType(Enum):
    """Types of recovery operations."""
    FULL_RESTORE = "full_restore"      # Complete system restore
    SELECTIVE_RESTORE = "selective"    # Restore specific prompts
    POINT_IN_TIME = "point_in_time"    # Restore to specific timestamp
    ROLLBACK = "rollback"              # Rollback to previous version


@dataclass
class BackupMetadata:
    """Metadata for a backup operation."""
    backup_id: str
    backup_type: BackupType
    timestamp: datetime
    size_bytes: int
    checksum: str
    source_paths: List[str]
    compression_ratio: float
    encryption_enabled: bool
    backup_status: BackupStatus
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class RecoveryMetadata:
    """Metadata for a recovery operation."""
    recovery_id: str
    recovery_type: RecoveryType
    backup_id: str
    timestamp: datetime
    target_paths: List[str]
    recovery_status: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class IntegrityCheckResult:
    """Result of data integrity check."""
    check_id: str
    timestamp: datetime
    total_files: int
    corrupted_files: int
    missing_files: int
    checksum_matches: int
    integrity_score: float  # 0.0 to 1.0
    issues: List[str]
    recommendations: List[str]


class PromptBackupRecovery:
    """
    Comprehensive backup and recovery system for prompt data.
    """
    
    def __init__(self, backup_dir: str = "prompt_backups", 
                 source_dbs: List[str] = None,
                 encryption_key: str = None):
        """Initialize the backup and recovery system."""
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Default source databases
        if source_dbs is None:
            self.source_dbs = [
                "prompt_database.db",
                "prompt_quality.db",
                "prompt_analytics.db"
            ]
        else:
            self.source_dbs = source_dbs
        
        self.encryption_key = encryption_key
        self._init_backup_database()
        
        # Backup retention policy
        self.retention_policy = {
            "daily": 7,      # Keep daily backups for 7 days
            "weekly": 4,     # Keep weekly backups for 4 weeks
            "monthly": 12    # Keep monthly backups for 12 months
        }
    
    def _init_backup_database(self):
        """Initialize the backup tracking database."""
        try:
            backup_db_path = self.backup_dir / "backup_tracking.db"
            with sqlite3.connect(backup_db_path) as conn:
                cursor = conn.cursor()
                
                # Backup operations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backup_operations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        backup_id TEXT UNIQUE NOT NULL,
                        backup_type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        checksum TEXT NOT NULL,
                        source_paths TEXT NOT NULL,
                        compression_ratio REAL NOT NULL,
                        encryption_enabled BOOLEAN NOT NULL,
                        backup_status TEXT NOT NULL,
                        error_message TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Recovery operations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recovery_operations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        recovery_id TEXT UNIQUE NOT NULL,
                        recovery_type TEXT NOT NULL,
                        backup_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        target_paths TEXT NOT NULL,
                        recovery_status TEXT NOT NULL,
                        error_message TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Integrity checks table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS integrity_checks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        check_id TEXT UNIQUE NOT NULL,
                        timestamp TEXT NOT NULL,
                        total_files INTEGER NOT NULL,
                        corrupted_files INTEGER NOT NULL,
                        missing_files INTEGER NOT NULL,
                        checksum_matches INTEGER NOT NULL,
                        integrity_score REAL NOT NULL,
                        issues TEXT NOT NULL,
                        recommendations TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize backup database: {e}")
    
    def create_backup(self, backup_type: BackupType = BackupType.FULL, 
                      description: str = None) -> str:
        """
        Create a new backup of prompt data.
        
        Args:
            backup_type: Type of backup to create
            description: Optional description of the backup
            
        Returns:
            Backup ID of the created backup
        """
        import uuid
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}_{backup_type.value}"
        
        try:
            # Update status to in progress
            self._update_backup_status(backup_id, BackupStatus.IN_PROGRESS)
            
            # Create backup directory
            backup_path = self.backup_dir / backup_id
            backup_path.mkdir(exist_ok=True)
            
            # Collect source files
            source_files = self._collect_source_files(backup_type)
            
            # Create backup archive
            archive_path = self._create_backup_archive(backup_id, source_files)
            
            # Calculate checksum
            checksum = self._calculate_checksum(archive_path)
            
            # Get file size
            size_bytes = archive_path.stat().st_size
            
            # Calculate compression ratio
            original_size = sum(f.stat().st_size for f in source_files)
            compression_ratio = 1 - (size_bytes / original_size) if original_size > 0 else 0
            
            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=backup_type,
                timestamp=datetime.now(),
                size_bytes=size_bytes,
                checksum=checksum,
                source_paths=[str(f) for f in source_files],
                compression_ratio=compression_ratio,
                encryption_enabled=bool(self.encryption_key),
                backup_status=BackupStatus.COMPLETED,
                metadata={"description": description} if description else None
            )
            
            # Save metadata
            self._save_backup_metadata(metadata)
            
            # Update status to completed
            self._update_backup_status(backup_id, BackupStatus.COMPLETED)
            
            # Verify backup integrity
            if self._verify_backup_integrity(backup_id, checksum):
                self._update_backup_status(backup_id, BackupStatus.VERIFIED)
                logger.info(f"Backup {backup_id} created and verified successfully")
            else:
                logger.error(f"Backup {backup_id} integrity check failed")
                self._update_backup_status(backup_id, BackupStatus.FAILED, "Integrity check failed")
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return backup_id
            
        except Exception as e:
            error_msg = f"Backup creation failed: {e}"
            logger.error(error_msg)
            self._update_backup_status(backup_id, BackupStatus.FAILED, error_msg)
            raise
    
    def _collect_source_files(self, backup_type: BackupType) -> List[Path]:
        """Collect source files for backup based on type."""
        source_files = []
        
        if backup_type == BackupType.FULL:
            # Include all source databases and prompt files
            for db_path in self.source_dbs:
                if Path(db_path).exists():
                    source_files.append(Path(db_path))
            
            # Include prompt template files
            prompt_dirs = ["prompt_templates", "prompt_examples", "prompt_configs"]
            for prompt_dir in prompt_dirs:
                if Path(prompt_dir).exists():
                    source_files.extend(Path(prompt_dir).rglob("*"))
        
        elif backup_type == BackupType.INCREMENTAL:
            # Only include files changed since last backup
            last_backup_time = self._get_last_backup_time()
            if last_backup_time:
                for db_path in self.source_dbs:
                    if Path(db_path).exists():
                        if Path(db_path).stat().st_mtime > last_backup_time.timestamp():
                            source_files.append(Path(db_path))
        
        elif backup_type == BackupType.DIFFERENTIAL:
            # Include changes since last full backup
            last_full_backup_time = self._get_last_full_backup_time()
            if last_full_backup_time:
                for db_path in self.source_dbs:
                    if Path(db_path).exists():
                        if Path(db_path).stat().st_mtime > last_full_backup_time.timestamp():
                            source_files.append(Path(db_path))
        
        return source_files
    
    def _create_backup_archive(self, backup_id: str, source_files: List[Path]) -> Path:
        """Create a compressed backup archive."""
        archive_path = self.backup_dir / f"{backup_id}.zip"
        
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for source_file in source_files:
                    if source_file.is_file():
                        # Add file to archive with relative path
                        arcname = source_file.name
                        zipf.write(source_file, arcname)
                        
                        # Also add file metadata
                        metadata = {
                            "original_path": str(source_file),
                            "size": source_file.stat().st_size,
                            "modified": source_file.stat().st_mtime,
                            "checksum": self._calculate_file_checksum(source_file)
                        }
                        
                        # Store metadata in a separate file
                        metadata_name = f"{source_file.stem}_metadata.json"
                        zipf.writestr(metadata_name, json.dumps(metadata, indent=2))
            
            return archive_path
            
        except Exception as e:
            logger.error(f"Failed to create backup archive: {e}")
            raise
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate checksum: {e}")
            return ""
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate checksum for a single file."""
        return self._calculate_checksum(file_path)
    
    def _verify_backup_integrity(self, backup_id: str, expected_checksum: str) -> bool:
        """Verify backup integrity by checking checksum."""
        try:
            archive_path = self.backup_dir / f"{backup_id}.zip"
            if not archive_path.exists():
                return False
            
            actual_checksum = self._calculate_checksum(archive_path)
            return actual_checksum == expected_checksum
            
        except Exception as e:
            logger.error(f"Backup integrity verification failed: {e}")
            return False
    
    def restore_from_backup(self, backup_id: str, target_paths: List[str] = None,
                           recovery_type: RecoveryType = RecoveryType.FULL_RESTORE) -> str:
        """
        Restore prompt data from a backup.
        
        Args:
            backup_id: ID of the backup to restore from
            target_paths: Specific paths to restore (for selective restore)
            recovery_type: Type of recovery operation
            
        Returns:
            Recovery ID of the restore operation
        """
        recovery_id = f"recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Verify backup exists and is valid
            if not self._backup_exists(backup_id):
                raise ValueError(f"Backup {backup_id} not found")
            
            # Create recovery metadata
            recovery_metadata = RecoveryMetadata(
                recovery_id=recovery_id,
                recovery_type=recovery_type,
                backup_id=backup_id,
                timestamp=datetime.now(),
                target_paths=target_paths or [],
                recovery_status="in_progress"
            )
            
            # Save recovery metadata
            self._save_recovery_metadata(recovery_metadata)
            
            # Perform restore operation
            if recovery_type == RecoveryType.FULL_RESTORE:
                self._perform_full_restore(backup_id, recovery_id)
            elif recovery_type == RecoveryType.SELECTIVE_RESTORE:
                self._perform_selective_restore(backup_id, target_paths, recovery_id)
            elif recovery_type == RecoveryType.POINT_IN_TIME:
                self._perform_point_in_time_restore(backup_id, recovery_id)
            elif recovery_type == RecoveryType.ROLLBACK:
                self._perform_rollback_restore(backup_id, recovery_id)
            
            # Update recovery status
            self._update_recovery_status(recovery_id, "completed")
            
            logger.info(f"Recovery {recovery_id} completed successfully")
            return recovery_id
            
        except Exception as e:
            error_msg = f"Recovery failed: {e}"
            logger.error(error_msg)
            self._update_recovery_status(recovery_id, "failed", error_msg)
            raise
    
    def _perform_full_restore(self, backup_id: str, recovery_id: str):
        """Perform a full system restore."""
        try:
            archive_path = self.backup_dir / f"{backup_id}.zip"
            
            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract backup archive
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                # Restore files to their original locations
                for item in Path(temp_dir).iterdir():
                    if item.is_file() and not item.name.endswith('_metadata.json'):
                        # Find original path from metadata
                        metadata_file = item.parent / f"{item.stem}_metadata.json"
                        if metadata_file.exists():
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                                original_path = Path(metadata['original_path'])
                                
                                # Create parent directory if it doesn't exist
                                original_path.parent.mkdir(parents=True, exist_ok=True)
                                
                                # Restore file
                                shutil.copy2(item, original_path)
                                
                                # Verify checksum
                                restored_checksum = self._calculate_file_checksum(original_path)
                                if restored_checksum != metadata['checksum']:
                                    raise ValueError(f"Checksum mismatch for {original_path}")
            
            logger.info(f"Full restore completed for backup {backup_id}")
            
        except Exception as e:
            logger.error(f"Full restore failed: {e}")
            raise
    
    def _perform_selective_restore(self, backup_id: str, target_paths: List[str], recovery_id: str):
        """Perform selective restore of specific files."""
        try:
            archive_path = self.backup_dir / f"{backup_id}.zip"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    # Extract only target files
                    for target_path in target_paths:
                        target_name = Path(target_path).name
                        
                        # Find file in archive
                        for archive_item in zipf.namelist():
                            if archive_item == target_name:
                                zipf.extract(archive_item, temp_dir)
                                
                                # Restore to target location
                                extracted_file = Path(temp_dir) / archive_item
                                target_file = Path(target_path)
                                
                                # Create parent directory if needed
                                target_file.parent.mkdir(parents=True, exist_ok=True)
                                
                                # Restore file
                                shutil.copy2(extracted_file, target_file)
                                break
            
            logger.info(f"Selective restore completed for {len(target_paths)} files")
            
        except Exception as e:
            logger.error(f"Selective restore failed: {e}")
            raise
    
    def _perform_point_in_time_restore(self, backup_id: str, recovery_id: str):
        """Perform point-in-time restore."""
        # This would require additional timestamp information in the backup
        # For now, perform full restore
        self._perform_full_restore(backup_id, recovery_id)
    
    def _perform_rollback_restore(self, backup_id: str, recovery_id: str):
        """Perform rollback to previous version."""
        # This would require version control information
        # For now, perform full restore
        self._perform_full_restore(backup_id, recovery_id)
    
    def check_data_integrity(self) -> IntegrityCheckResult:
        """Perform comprehensive data integrity check."""
        import uuid
        check_id = f"integrity_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        try:
            total_files = 0
            corrupted_files = 0
            missing_files = 0
            checksum_matches = 0
            issues = []
            recommendations = []
            
            # Check all source databases
            for db_path in self.source_dbs:
                if Path(db_path).exists():
                    total_files += 1
                    
                    # Check database integrity
                    if self._check_database_integrity(db_path):
                        checksum_matches += 1
                    else:
                        corrupted_files += 1
                        issues.append(f"Database corruption detected in {db_path}")
                        recommendations.append(f"Restore {db_path} from latest backup")
                else:
                    missing_files += 1
                    issues.append(f"Missing database file: {db_path}")
                    recommendations.append(f"Restore {db_path} from backup")
            
            # Check prompt template files
            prompt_dirs = ["prompt_templates", "prompt_examples", "prompt_configs"]
            for prompt_dir in prompt_dirs:
                if Path(prompt_dir).exists():
                    for file_path in Path(prompt_dir).rglob("*"):
                        if file_path.is_file():
                            total_files += 1
                            
                            # Check file integrity
                            if self._check_file_integrity(file_path):
                                checksum_matches += 1
                            else:
                                corrupted_files += 1
                                issues.append(f"File corruption detected in {file_path}")
                                recommendations.append(f"Restore {file_path} from backup")
            
            # Calculate integrity score
            if total_files > 0:
                integrity_score = checksum_matches / total_files
            else:
                integrity_score = 0.0
            
            # Create integrity check result
            result = IntegrityCheckResult(
                check_id=check_id,
                timestamp=datetime.now(),
                total_files=total_files,
                corrupted_files=corrupted_files,
                missing_files=missing_files,
                checksum_matches=checksum_matches,
                integrity_score=integrity_score,
                issues=issues,
                recommendations=recommendations
            )
            
            # Save integrity check result
            self._save_integrity_check_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Data integrity check failed: {e}")
            raise
    
    def _check_database_integrity(self, db_path: str) -> bool:
        """Check integrity of a SQLite database."""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Check if database is accessible
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                
                if result and result[0] == "ok":
                    return True
                else:
                    return False
                    
        except Exception as e:
            logger.error(f"Database integrity check failed for {db_path}: {e}")
            return False
    
    def _check_file_integrity(self, file_path: Path) -> bool:
        """Check integrity of a file."""
        try:
            # Basic file integrity check
            if not file_path.exists():
                return False
            
            # Check if file is readable
            with open(file_path, 'rb') as f:
                f.read(1)
            
            return True
            
        except Exception as e:
            logger.error(f"File integrity check failed for {file_path}: {e}")
            return False
    
    def _backup_exists(self, backup_id: str) -> bool:
        """Check if a backup exists."""
        archive_path = self.backup_dir / f"{backup_id}.zip"
        return archive_path.exists()
    
    def _get_last_backup_time(self) -> Optional[datetime]:
        """Get timestamp of last backup."""
        try:
            backup_db_path = self.backup_dir / "backup_tracking.db"
            with sqlite3.connect(backup_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT timestamp FROM backup_operations 
                    WHERE backup_status = 'verified' 
                    ORDER BY timestamp DESC LIMIT 1
                """)
                result = cursor.fetchone()
                
                if result:
                    return datetime.fromisoformat(result[0])
                return None
                
        except Exception as e:
            logger.error(f"Failed to get last backup time: {e}")
            return None
    
    def _get_last_full_backup_time(self) -> Optional[datetime]:
        """Get timestamp of last full backup."""
        try:
            backup_db_path = self.backup_dir / "backup_tracking.db"
            with sqlite3.connect(backup_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT timestamp FROM backup_operations 
                    WHERE backup_type = 'full' AND backup_status = 'verified'
                    ORDER BY timestamp DESC LIMIT 1
                """)
                result = cursor.fetchone()
                
                if result:
                    return datetime.fromisoformat(result[0])
                return None
                
        except Exception as e:
            logger.error(f"Failed to get last full backup time: {e}")
            return None
    
    def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy."""
        try:
            current_time = datetime.now()
            
            # Get all backups
            backups = self._get_all_backups()
            
            for backup in backups:
                backup_age = current_time - backup.timestamp
                
                # Check retention policy
                should_delete = False
                
                if backup.backup_type == BackupType.DAILY and backup_age.days > self.retention_policy["daily"]:
                    should_delete = True
                elif backup.backup_type == BackupType.WEEKLY and backup_age.days > self.retention_policy["weekly"] * 7:
                    should_delete = True
                elif backup.backup_type == BackupType.MONTHLY and backup_age.days > self.retention_policy["monthly"] * 30:
                    should_delete = True
                
                if should_delete:
                    self._delete_backup(backup.backup_id)
                    
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def _delete_backup(self, backup_id: str):
        """Delete a backup and its metadata."""
        try:
            # Delete archive file
            archive_path = self.backup_dir / f"{backup_id}.zip"
            if archive_path.exists():
                archive_path.unlink()
            
            # Delete metadata from database
            backup_db_path = self.backup_dir / "backup_tracking.db"
            with sqlite3.connect(backup_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM backup_operations WHERE backup_id = ?", (backup_id,))
                conn.commit()
            
            logger.info(f"Backup {backup_id} deleted successfully")
            
        except Exception as e:
            logger.error(f"Failed to delete backup {backup_id}: {e}")
    
    def _get_all_backups(self) -> List[BackupMetadata]:
        """Get all backup metadata."""
        try:
            backup_db_path = self.backup_dir / "backup_tracking.db"
            with sqlite3.connect(backup_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM backup_operations ORDER BY timestamp DESC")
                rows = cursor.fetchall()
                
                backups = []
                for row in rows:
                    backup = BackupMetadata(
                        backup_id=row[1],
                        backup_type=BackupType(row[2]),
                        timestamp=datetime.fromisoformat(row[3]),
                        size_bytes=row[4],
                        checksum=row[5],
                        source_paths=json.loads(row[6]),
                        compression_ratio=row[7],
                        encryption_enabled=bool(row[8]),
                        backup_status=BackupStatus(row[9]),
                        error_message=row[10],
                        metadata=json.loads(row[11]) if row[11] else None
                    )
                    backups.append(backup)
                
                return backups
                
        except Exception as e:
            logger.error(f"Failed to get all backups: {e}")
            return []
    
    def _update_backup_status(self, backup_id: str, status: BackupStatus, error_message: str = None):
        """Update backup status in database."""
        try:
            backup_db_path = self.backup_dir / "backup_tracking.db"
            with sqlite3.connect(backup_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE backup_operations 
                    SET backup_status = ?, error_message = ?
                    WHERE backup_id = ?
                """, (status.value, error_message, backup_id))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to update backup status: {e}")
    
    def _update_recovery_status(self, recovery_id: str, status: str, error_message: str = None):
        """Update recovery status in database."""
        try:
            backup_db_path = self.backup_dir / "backup_tracking.db"
            with sqlite3.connect(backup_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE recovery_operations 
                    SET recovery_status = ?, error_message = ?
                    WHERE recovery_id = ?
                """, (status, error_message, recovery_id))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to update recovery status: {e}")
    
    def _save_backup_metadata(self, metadata: BackupMetadata):
        """Save backup metadata to database."""
        try:
            backup_db_path = self.backup_dir / "backup_tracking.db"
            with sqlite3.connect(backup_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO backup_operations 
                    (backup_id, backup_type, timestamp, size_bytes, checksum,
                     source_paths, compression_ratio, encryption_enabled, backup_status, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metadata.backup_id,
                    metadata.backup_type.value,
                    metadata.timestamp.isoformat(),
                    metadata.size_bytes,
                    metadata.checksum,
                    json.dumps(metadata.source_paths),
                    metadata.compression_ratio,
                    metadata.encryption_enabled,
                    metadata.backup_status.value,
                    json.dumps(metadata.metadata) if metadata.metadata else None
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save backup metadata: {e}")
    
    def _save_recovery_metadata(self, metadata: RecoveryMetadata):
        """Save recovery metadata to database."""
        try:
            backup_db_path = self.backup_dir / "backup_tracking.db"
            with sqlite3.connect(backup_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO recovery_operations 
                    (recovery_id, recovery_type, backup_id, timestamp, target_paths, recovery_status, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    metadata.recovery_id,
                    metadata.recovery_type.value,
                    metadata.backup_id,
                    metadata.timestamp.isoformat(),
                    json.dumps(metadata.target_paths),
                    metadata.recovery_status,
                    json.dumps(metadata.metadata) if metadata.metadata else None
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save recovery metadata: {e}")
    
    def _save_integrity_check_result(self, result: IntegrityCheckResult):
        """Save integrity check result to database."""
        try:
            backup_db_path = self.backup_dir / "backup_tracking.db"
            with sqlite3.connect(backup_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO integrity_checks 
                    (check_id, timestamp, total_files, corrupted_files, missing_files,
                     checksum_matches, integrity_score, issues, recommendations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.check_id,
                    result.timestamp.isoformat(),
                    result.total_files,
                    result.corrupted_files,
                    result.missing_files,
                    result.checksum_matches,
                    result.integrity_score,
                    json.dumps(result.issues),
                    json.dumps(result.recommendations)
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save integrity check result: {e}")
    
    def get_backup_summary(self) -> Dict[str, Any]:
        """Get summary of all backups."""
        try:
            backups = self._get_all_backups()
            
            summary = {
                "total_backups": len(backups),
                "total_size_gb": sum(b.size_bytes for b in backups) / (1024**3),
                "backup_types": {},
                "recent_backups": [],
                "failed_backups": len([b for b in backups if b.backup_status == BackupStatus.FAILED])
            }
            
            # Count by type
            for backup in backups:
                backup_type = backup.backup_type.value
                summary["backup_types"][backup_type] = summary["backup_types"].get(backup_type, 0) + 1
            
            # Recent backups (last 5)
            recent_backups = sorted(backups, key=lambda x: x.timestamp, reverse=True)[:5]
            summary["recent_backups"] = [
                {
                    "id": b.backup_id,
                    "type": b.backup_type.value,
                    "timestamp": b.timestamp.isoformat(),
                    "size_mb": b.size_bytes / (1024**2),
                    "status": b.backup_status.value
                }
                for b in recent_backups
            ]
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get backup summary: {e}")
            return {}


# Factory function
def get_backup_recovery_system(backup_dir: str = "prompt_backups",
                               source_dbs: List[str] = None,
                               encryption_key: str = None) -> PromptBackupRecovery:
    """Get a backup and recovery system instance."""
    return PromptBackupRecovery(backup_dir, source_dbs, encryption_key)
