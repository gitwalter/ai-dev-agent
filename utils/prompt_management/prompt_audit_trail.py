"""
Prompt Audit Trail System

Provides comprehensive audit trail capabilities for prompt changes including:
- Complete change history tracking
- User attribution for all changes
- Change impact analysis
- Compliance and governance support
- Change notification system

This module implements the audit trail system for US-PE-02.
"""

import json
import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import difflib
from dataclasses import field
import re # Added missing import for re

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of changes that can be tracked."""
    CREATE = "create"           # New prompt created
    UPDATE = "update"           # Existing prompt modified
    DELETE = "delete"           # Prompt deleted
    ARCHIVE = "archive"         # Prompt archived
    RESTORE = "restore"         # Prompt restored from backup
    APPROVE = "approve"         # Prompt approved
    REJECT = "reject"           # Prompt rejected
    PUBLISH = "publish"         # Prompt published
    UNPUBLISH = "unpublish"     # Prompt unpublished


class ChangeSeverity(Enum):
    """Severity levels for changes."""
    LOW = "low"                 # Minor changes (formatting, typos)
    MEDIUM = "medium"           # Moderate changes (content updates)
    HIGH = "high"               # Significant changes (structure, logic)
    CRITICAL = "critical"       # Critical changes (security, compliance)


class ComplianceStatus(Enum):
    """Compliance status for changes."""
    COMPLIANT = "compliant"     # Meets all compliance requirements
    NON_COMPLIANT = "non_compliant"  # Does not meet requirements
    PENDING_REVIEW = "pending_review"  # Awaiting compliance review
    UNDER_INVESTIGATION = "under_investigation"  # Being investigated


@dataclass
class ChangeRecord:
    """Record of a single change to a prompt."""
    change_id: str
    prompt_id: str
    change_type: ChangeType
    change_severity: ChangeSeverity
    user_id: str
    user_name: str
    timestamp: datetime
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    approval_status: str = "pending"
    approver_id: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    compliance_status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW


@dataclass
class ChangeImpact:
    """Analysis of the impact of a change."""
    change_id: str
    prompt_id: str
    impact_score: float  # 0.0 to 1.0
    affected_systems: List[str]
    risk_assessment: str
    rollback_complexity: str  # "low", "medium", "high"
    estimated_downtime: int  # minutes
    business_impact: str
    recommendations: List[str]
    analysis_timestamp: datetime


@dataclass
class ComplianceRecord:
    """Compliance tracking for changes."""
    compliance_id: str
    change_id: str
    prompt_id: str
    compliance_rule: str
    rule_description: str
    compliance_status: ComplianceStatus
    violation_details: Optional[str] = None
    remediation_required: bool = False
    remediation_deadline: Optional[datetime] = None
    compliance_officer: Optional[str] = None
    review_notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditSummary:
    """Summary of audit trail data."""
    total_changes: int
    changes_by_type: Dict[str, int]
    changes_by_severity: Dict[str, int]
    changes_by_user: Dict[str, int]
    compliance_status: Dict[str, int]
    recent_changes: List[Dict[str, Any]]
    pending_approvals: int
    compliance_issues: int


class PromptAuditTrail:
    """
    Comprehensive audit trail system for prompt changes.
    """
    
    def __init__(self, db_path: str = "prompts/analytics/prompt_audit.db"):
        """Initialize the audit trail system."""
        self.db_path = db_path
        self._init_database()
        
        # Compliance rules
        self.compliance_rules = {
            "data_privacy": {
                "description": "No personal or sensitive data in prompts",
                "severity": "critical",
                "check_function": self._check_data_privacy_compliance
            },
            "security": {
                "description": "No security vulnerabilities in prompts",
                "severity": "critical",
                "check_function": self._check_security_compliance
            },
            "content_standards": {
                "description": "Content meets organizational standards",
                "severity": "medium",
                "check_function": self._check_content_standards
            },
            "formatting": {
                "description": "Proper formatting and structure",
                "severity": "low",
                "check_function": self._check_formatting_compliance
            }
        }
    
    def _init_database(self):
        """Initialize the audit trail database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Change records table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS change_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        change_id TEXT UNIQUE NOT NULL,
                        prompt_id TEXT NOT NULL,
                        change_type TEXT NOT NULL,
                        change_severity TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        user_name TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        old_value TEXT,
                        new_value TEXT,
                        change_summary TEXT NOT NULL,
                        metadata TEXT,
                        approval_status TEXT NOT NULL,
                        approver_id TEXT,
                        approval_timestamp TEXT,
                        compliance_status TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Change impact analysis table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS change_impacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        change_id TEXT UNIQUE NOT NULL,
                        prompt_id TEXT NOT NULL,
                        impact_score REAL NOT NULL,
                        affected_systems TEXT NOT NULL,
                        risk_assessment TEXT NOT NULL,
                        rollback_complexity TEXT NOT NULL,
                        estimated_downtime INTEGER NOT NULL,
                        business_impact TEXT NOT NULL,
                        recommendations TEXT NOT NULL,
                        analysis_timestamp TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Compliance records table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS compliance_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        compliance_id TEXT UNIQUE NOT NULL,
                        change_id TEXT NOT NULL,
                        prompt_id TEXT NOT NULL,
                        compliance_rule TEXT NOT NULL,
                        rule_description TEXT NOT NULL,
                        compliance_status TEXT NOT NULL,
                        violation_details TEXT,
                        remediation_required BOOLEAN NOT NULL,
                        remediation_deadline TEXT,
                        compliance_officer TEXT,
                        review_notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # User activity table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_activity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        user_name TEXT NOT NULL,
                        activity_type TEXT NOT NULL,
                        prompt_id TEXT,
                        timestamp TEXT NOT NULL,
                        details TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_change_records_prompt_id ON change_records(prompt_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_change_records_timestamp ON change_records(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_change_records_user_id ON change_records(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_records_change_id ON compliance_records(change_id)")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize audit trail database: {e}")
    
    def record_change(self, prompt_id: str, change_type: ChangeType, 
                     user_id: str, user_name: str, old_value: str = None,
                     new_value: str = None, change_summary: str = "",
                     metadata: Dict[str, Any] = None) -> str:
        """
        Record a change to a prompt.
        
        Args:
            prompt_id: ID of the prompt being changed
            change_type: Type of change being made
            user_id: ID of the user making the change
            user_name: Name of the user making the change
            old_value: Previous value of the prompt
            new_value: New value of the prompt
            change_summary: Human-readable summary of the change
            metadata: Additional metadata about the change
            
        Returns:
            Change ID of the recorded change
        """
        import uuid
        change_id = f"change_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}_{user_id}"
        
        try:
            # Determine change severity
            change_severity = self._determine_change_severity(change_type, old_value, new_value)
            
            # Create change record
            change_record = ChangeRecord(
                change_id=change_id,
                prompt_id=prompt_id,
                change_type=change_type,
                change_severity=change_severity,
                user_id=user_id,
                user_name=user_name,
                timestamp=datetime.now(),
                old_value=old_value,
                new_value=new_value,
                change_summary=change_summary,
                metadata=metadata or {},
                compliance_status=ComplianceStatus.PENDING_REVIEW
            )
            
            # Save change record
            self._save_change_record(change_record)
            
            # Record user activity
            self._record_user_activity(user_id, user_name, "prompt_change", prompt_id, change_summary)
            
            # Perform compliance check
            self._perform_compliance_check(change_record)
            
            # Analyze change impact
            self._analyze_change_impact(change_record)
            
            logger.info(f"Change recorded: {change_id} for prompt {prompt_id}")
            return change_id
            
        except Exception as e:
            logger.error(f"Failed to record change: {e}")
            raise
    
    def _determine_change_severity(self, change_type: ChangeType, 
                                  old_value: str, new_value: str) -> ChangeSeverity:
        """Determine the severity of a change."""
        
        if change_type in [ChangeType.CREATE, ChangeType.DELETE]:
            return ChangeSeverity.HIGH
        
        if change_type == ChangeType.UPDATE and old_value and new_value:
            # Calculate change magnitude
            change_magnitude = self._calculate_change_magnitude(old_value, new_value)
            
            if change_magnitude < 0.1:
                return ChangeSeverity.LOW
            elif change_magnitude < 0.3:
                return ChangeSeverity.MEDIUM
            elif change_magnitude < 0.6:
                return ChangeSeverity.HIGH
            else:
                return ChangeSeverity.CRITICAL
        
        return ChangeSeverity.MEDIUM
    
    def _calculate_change_magnitude(self, old_value: str, new_value: str) -> float:
        """Calculate the magnitude of change between two values."""
        try:
            # Use difflib to calculate similarity
            similarity = difflib.SequenceMatcher(None, old_value, new_value).ratio()
            change_magnitude = 1 - similarity
            return change_magnitude
        except Exception:
            return 0.5  # Default to medium if calculation fails
    
    def _perform_compliance_check(self, change_record: ChangeRecord):
        """Perform compliance check for a change."""
        try:
            for rule_name, rule_config in self.compliance_rules.items():
                check_function = rule_config["check_function"]
                compliance_status = check_function(change_record)
                
                # Create compliance record
                compliance_record = ComplianceRecord(
                    compliance_id=f"compliance_{change_record.change_id}_{uuid.uuid4().hex[:8]}_{rule_name}",
                    change_id=change_record.change_id,
                    prompt_id=change_record.prompt_id,
                    compliance_rule=rule_name,
                    rule_description=rule_config["description"],
                    compliance_status=compliance_status,
                    remediation_required=compliance_status == ComplianceStatus.NON_COMPLIANT
                )
                
                # Save compliance record
                self._save_compliance_record(compliance_record)
                
                # Update change record compliance status
                if compliance_status == ComplianceStatus.NON_COMPLIANT:
                    self._update_change_compliance_status(change_record.change_id, ComplianceStatus.NON_COMPLIANT)
                
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
    
    def _check_data_privacy_compliance(self, change_record: ChangeRecord) -> ComplianceStatus:
        """Check data privacy compliance."""
        try:
            # Check for personal data patterns
            personal_data_patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b\d{10,11}\b',  # Phone numbers
                r'\b[A-Za-z]+\s[A-Za-z]+\b'  # Names
            ]
            
            text_to_check = change_record.new_value or change_record.old_value or ""
            
            for pattern in personal_data_patterns:
                if re.search(pattern, text_to_check):
                    return ComplianceStatus.NON_COMPLIANT
            
            return ComplianceStatus.COMPLIANT
            
        except Exception as e:
            logger.error(f"Data privacy compliance check failed: {e}")
            return ComplianceStatus.PENDING_REVIEW
    
    def _check_security_compliance(self, change_record: ChangeRecord) -> ComplianceStatus:
        """Check security compliance."""
        try:
            # Check for security vulnerabilities
            security_patterns = [
                r'password\s*=',  # Hardcoded passwords
                r'api_key\s*=',   # Hardcoded API keys
                r'secret\s*=',    # Hardcoded secrets
                r'admin\s*:',     # Admin credentials
                r'root\s*:',      # Root credentials
            ]
            
            text_to_check = change_record.new_value or change_record.old_value or ""
            
            for pattern in security_patterns:
                if re.search(pattern, text_to_check, re.IGNORECASE):
                    return ComplianceStatus.NON_COMPLIANT
            
            return ComplianceStatus.COMPLIANT
            
        except Exception as e:
            logger.error(f"Security compliance check failed: {e}")
            return ComplianceStatus.PENDING_REVIEW
    
    def _check_content_standards(self, change_record: ChangeRecord) -> ComplianceStatus:
        """Check content standards compliance."""
        try:
            # Check for inappropriate content
            inappropriate_patterns = [
                r'\b(bad|inappropriate|unprofessional)\b',
                r'\b(hate|discrimination|bias)\b'
            ]
            
            text_to_check = change_record.new_value or change_record.old_value or ""
            
            for pattern in inappropriate_patterns:
                if re.search(pattern, text_to_check, re.IGNORECASE):
                    return ComplianceStatus.NON_COMPLIANT
            
            return ComplianceStatus.COMPLIANT
            
        except Exception as e:
            logger.error(f"Content standards check failed: {e}")
            return ComplianceStatus.PENDING_REVIEW
    
    def _check_formatting_compliance(self, change_record: ChangeRecord) -> ComplianceStatus:
        """Check formatting compliance."""
        try:
            # Basic formatting checks
            text_to_check = change_record.new_value or change_record.old_value or ""
            
            if not text_to_check.strip():
                return ComplianceStatus.NON_COMPLIANT
            
            if len(text_to_check) < 10:
                return ComplianceStatus.NON_COMPLIANT
            
            return ComplianceStatus.COMPLIANT
            
        except Exception as e:
            logger.error(f"Formatting compliance check failed: {e}")
            return ComplianceStatus.PENDING_REVIEW
    
    def _analyze_change_impact(self, change_record: ChangeRecord):
        """Analyze the impact of a change."""
        try:
            # Calculate impact score based on change severity and type
            impact_score = self._calculate_impact_score(change_record)
            
            # Determine affected systems
            affected_systems = self._identify_affected_systems(change_record)
            
            # Assess risk
            risk_assessment = self._assess_risk(change_record)
            
            # Determine rollback complexity
            rollback_complexity = self._assess_rollback_complexity(change_record)
            
            # Estimate downtime
            estimated_downtime = self._estimate_downtime(change_record)
            
            # Assess business impact
            business_impact = self._assess_business_impact(change_record)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(change_record)
            
            # Create impact analysis
            change_impact = ChangeImpact(
                change_id=change_record.change_id,
                prompt_id=change_record.prompt_id,
                impact_score=impact_score,
                affected_systems=affected_systems,
                risk_assessment=risk_assessment,
                rollback_complexity=rollback_complexity,
                estimated_downtime=estimated_downtime,
                business_impact=business_impact,
                recommendations=recommendations,
                analysis_timestamp=datetime.now()
            )
            
            # Save impact analysis
            self._save_change_impact(change_impact)
            
        except Exception as e:
            logger.error(f"Change impact analysis failed: {e}")
    
    def _calculate_impact_score(self, change_record: ChangeRecord) -> float:
        """Calculate impact score for a change."""
        base_score = 0.0
        
        # Base score from severity
        severity_scores = {
            ChangeSeverity.LOW: 0.1,
            ChangeSeverity.MEDIUM: 0.3,
            ChangeSeverity.HIGH: 0.6,
            ChangeSeverity.CRITICAL: 0.9
        }
        base_score = severity_scores.get(change_record.change_severity, 0.3)
        
        # Adjust based on change type
        if change_record.change_type == ChangeType.DELETE:
            base_score += 0.2
        elif change_record.change_type == ChangeType.CREATE:
            base_score += 0.1
        
        # Adjust based on prompt importance (from metadata)
        if change_record.metadata and "importance" in change_record.metadata:
            importance = change_record.metadata["importance"]
            if importance == "critical":
                base_score += 0.2
            elif importance == "high":
                base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _identify_affected_systems(self, change_record: ChangeRecord) -> List[str]:
        """Identify systems affected by a change."""
        affected_systems = ["prompt_management_system"]
        
        # Add systems based on metadata
        if change_record.metadata and "affected_systems" in change_record.metadata:
            affected_systems.extend(change_record.metadata["affected_systems"])
        
        # Add systems based on prompt type
        if change_record.metadata and "prompt_type" in change_record.metadata:
            prompt_type = change_record.metadata["prompt_type"]
            if prompt_type == "agent_prompt":
                affected_systems.append("agent_framework")
            elif prompt_type == "user_interface":
                affected_systems.append("web_interface")
            elif prompt_type == "api_prompt":
                affected_systems.append("api_gateway")
        
        return affected_systems
    
    def _assess_risk(self, change_record: ChangeRecord) -> str:
        """Assess risk level of a change."""
        if change_record.change_severity == ChangeSeverity.CRITICAL:
            return "high"
        elif change_record.change_severity == ChangeSeverity.HIGH:
            return "medium"
        elif change_record.change_severity == ChangeSeverity.MEDIUM:
            return "low"
        else:
            return "minimal"
    
    def _assess_rollback_complexity(self, change_record: ChangeRecord) -> str:
        """Assess rollback complexity of a change."""
        if change_record.change_type == ChangeType.DELETE:
            return "high"
        elif change_record.change_type == ChangeType.CREATE:
            return "medium"
        elif change_record.change_type == ChangeType.UPDATE:
            if change_record.old_value:
                return "low"
            else:
                return "medium"
        else:
            return "low"
    
    def _estimate_downtime(self, change_record: ChangeRecord) -> int:
        """Estimate downtime for a change."""
        base_downtime = 0
        
        if change_record.change_severity == ChangeSeverity.CRITICAL:
            base_downtime = 30  # 30 minutes
        elif change_record.change_severity == ChangeSeverity.HIGH:
            base_downtime = 15  # 15 minutes
        elif change_record.change_severity == ChangeSeverity.MEDIUM:
            base_downtime = 5   # 5 minutes
        else:
            base_downtime = 1   # 1 minute
        
        # Adjust based on change type
        if change_record.change_type == ChangeType.DELETE:
            base_downtime += 10
        elif change_record.change_type == ChangeType.CREATE:
            base_downtime += 5
        
        return base_downtime
    
    def _assess_business_impact(self, change_record: ChangeRecord) -> str:
        """Assess business impact of a change."""
        if change_record.change_severity == ChangeSeverity.CRITICAL:
            return "Significant business disruption possible"
        elif change_record.change_severity == ChangeSeverity.HIGH:
            return "Moderate business impact expected"
        elif change_record.change_severity == ChangeSeverity.MEDIUM:
            return "Limited business impact"
        else:
            return "Minimal business impact"
    
    def _generate_recommendations(self, change_record: ChangeRecord) -> List[str]:
        """Generate recommendations for a change."""
        recommendations = []
        
        if change_record.change_severity == ChangeSeverity.CRITICAL:
            recommendations.extend([
                "Schedule change during maintenance window",
                "Prepare rollback plan",
                "Notify stakeholders immediately",
                "Monitor system closely after deployment"
            ])
        elif change_record.change_severity == ChangeSeverity.HIGH:
            recommendations.extend([
                "Test change in staging environment",
                "Prepare rollback plan",
                "Notify affected users"
            ])
        elif change_record.change_severity == ChangeSeverity.MEDIUM:
            recommendations.extend([
                "Test change before deployment",
                "Monitor for any issues"
            ])
        else:
            recommendations.append("Standard deployment process")
        
        # Add compliance-specific recommendations
        if change_record.metadata and "compliance_issues" in change_record.metadata:
            recommendations.append("Address compliance issues before deployment")
        
        return recommendations
    
    def get_change_history(self, prompt_id: str, days: int = 30) -> List[ChangeRecord]:
        """Get change history for a prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM change_records 
                    WHERE prompt_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                """, (prompt_id, (datetime.now() - timedelta(days=days)).isoformat()))
                
                rows = cursor.fetchall()
                changes = []
                for row in rows:
                    change = ChangeRecord(
                        change_id=row[1],
                        prompt_id=row[2],
                        change_type=ChangeType(row[3]),
                        change_severity=ChangeSeverity(row[4]),
                        user_id=row[5],
                        user_name=row[6],
                        timestamp=datetime.fromisoformat(row[7]),
                        old_value=row[8],
                        new_value=row[9],
                        change_summary=row[10],
                        metadata=json.loads(row[11]) if row[11] else {},
                        approval_status=row[12],
                        approver_id=row[13],
                        approval_timestamp=datetime.fromisoformat(row[14]) if row[14] else None,
                        compliance_status=ComplianceStatus(row[15])
                    )
                    changes.append(change)
                
                return changes
                
        except Exception as e:
            logger.error(f"Failed to get change history: {e}")
            return []
    
    def get_user_activity(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get activity history for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM user_activity 
                    WHERE user_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                """, (user_id, (datetime.now() - timedelta(days=days)).isoformat()))
                
                rows = cursor.fetchall()
                activities = []
                for row in rows:
                    activities.append({
                        "activity_type": row[3],
                        "prompt_id": row[4],
                        "timestamp": row[5],
                        "details": row[6]
                    })
                
                return activities
                
        except Exception as e:
            logger.error(f"Failed to get user activity: {e}")
            return []
    
    def get_audit_summary(self, days: int = 30) -> AuditSummary:
        """Get summary of audit trail data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total changes
                cursor.execute("""
                    SELECT COUNT(*) FROM change_records 
                    WHERE timestamp >= ?
                """, ((datetime.now() - timedelta(days=days)).isoformat(),))
                total_changes = cursor.fetchone()[0]
                
                # Get changes by type
                cursor.execute("""
                    SELECT change_type, COUNT(*) FROM change_records 
                    WHERE timestamp >= ? GROUP BY change_type
                """, ((datetime.now() - timedelta(days=days)).isoformat(),))
                changes_by_type = dict(cursor.fetchall())
                
                # Get changes by severity
                cursor.execute("""
                    SELECT change_severity, COUNT(*) FROM change_records 
                    WHERE timestamp >= ? GROUP BY change_severity
                """, ((datetime.now() - timedelta(days=days)).isoformat(),))
                changes_by_severity = dict(cursor.fetchall())
                
                # Get changes by user
                cursor.execute("""
                    SELECT user_name, COUNT(*) FROM change_records 
                    WHERE timestamp >= ? GROUP BY user_name
                """, ((datetime.now() - timedelta(days=days)).isoformat(),))
                changes_by_user = dict(cursor.fetchall())
                
                # Get compliance status
                cursor.execute("""
                    SELECT compliance_status, COUNT(*) FROM change_records 
                    WHERE timestamp >= ? GROUP BY compliance_status
                """, ((datetime.now() - timedelta(days=days)).isoformat(),))
                compliance_status = dict(cursor.fetchall())
                
                # Get recent changes
                cursor.execute("""
                    SELECT change_id, prompt_id, change_type, user_name, timestamp, change_summary
                    FROM change_records 
                    WHERE timestamp >= ? 
                    ORDER BY timestamp DESC LIMIT 10
                """, ((datetime.now() - timedelta(days=days)).isoformat(),))
                recent_changes = []
                for row in cursor.fetchall():
                    recent_changes.append({
                        "change_id": row[0],
                        "prompt_id": row[1],
                        "change_type": row[2],
                        "user_name": row[3],
                        "timestamp": row[4],
                        "change_summary": row[5]
                    })
                
                # Get pending approvals
                cursor.execute("""
                    SELECT COUNT(*) FROM change_records 
                    WHERE approval_status = 'pending' AND timestamp >= ?
                """, ((datetime.now() - timedelta(days=days)).isoformat(),))
                pending_approvals = cursor.fetchone()[0]
                
                # Get compliance issues
                cursor.execute("""
                    SELECT COUNT(*) FROM change_records 
                    WHERE compliance_status = 'non_compliant' AND timestamp >= ?
                """, ((datetime.now() - timedelta(days=days)).isoformat(),))
                compliance_issues = cursor.fetchone()[0]
                
                return AuditSummary(
                    total_changes=total_changes,
                    changes_by_type=changes_by_type,
                    changes_by_severity=changes_by_severity,
                    changes_by_user=changes_by_user,
                    compliance_status=compliance_status,
                    recent_changes=recent_changes,
                    pending_approvals=pending_approvals,
                    compliance_issues=compliance_issues
                )
                
        except Exception as e:
            logger.error(f"Failed to get audit summary: {e}")
            return AuditSummary(
                total_changes=0,
                changes_by_type={},
                changes_by_severity={},
                changes_by_user={},
                compliance_status={},
                recent_changes=[],
                pending_approvals=0,
                compliance_issues=0
            )
    
    def _save_change_record(self, change_record: ChangeRecord):
        """Save change record to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO change_records 
                    (change_id, prompt_id, change_type, change_severity, user_id, user_name,
                     timestamp, old_value, new_value, change_summary, metadata, 
                     approval_status, compliance_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    change_record.change_id,
                    change_record.prompt_id,
                    change_record.change_type.value,
                    change_record.change_severity.value,
                    change_record.user_id,
                    change_record.user_name,
                    change_record.timestamp.isoformat(),
                    change_record.old_value,
                    change_record.new_value,
                    change_record.change_summary,
                    json.dumps(change_record.metadata),
                    change_record.approval_status,
                    change_record.compliance_status.value
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save change record: {e}")
    
    def _save_change_impact(self, change_impact: ChangeImpact):
        """Save change impact to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO change_impacts 
                    (change_id, prompt_id, impact_score, affected_systems, risk_assessment,
                     rollback_complexity, estimated_downtime, business_impact, recommendations,
                     analysis_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    change_impact.change_id,
                    change_impact.prompt_id,
                    change_impact.impact_score,
                    json.dumps(change_impact.affected_systems),
                    change_impact.risk_assessment,
                    change_impact.rollback_complexity,
                    change_impact.estimated_downtime,
                    change_impact.business_impact,
                    json.dumps(change_impact.recommendations),
                    change_impact.analysis_timestamp.isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save change impact: {e}")
    
    def _save_compliance_record(self, compliance_record: ComplianceRecord):
        """Save compliance record to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO compliance_records 
                    (compliance_id, change_id, prompt_id, compliance_rule, rule_description,
                     compliance_status, violation_details, remediation_required, 
                     remediation_deadline, compliance_officer, review_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    compliance_record.compliance_id,
                    compliance_record.change_id,
                    compliance_record.prompt_id,
                    compliance_record.compliance_rule,
                    compliance_record.rule_description,
                    compliance_record.compliance_status.value,
                    compliance_record.violation_details,
                    compliance_record.remediation_required,
                    compliance_record.remediation_deadline.isoformat() if compliance_record.remediation_deadline else None,
                    compliance_record.compliance_officer,
                    compliance_record.review_notes
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save compliance record: {e}")
    
    def _record_user_activity(self, user_id: str, user_name: str, activity_type: str,
                             prompt_id: str = None, details: str = None):
        """Record user activity."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_activity 
                    (user_id, user_name, activity_type, prompt_id, timestamp, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    user_name,
                    activity_type,
                    prompt_id,
                    datetime.now().isoformat(),
                    details
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to record user activity: {e}")
    
    def _update_change_compliance_status(self, change_id: str, compliance_status: ComplianceStatus):
        """Update compliance status of a change."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE change_records 
                    SET compliance_status = ?
                    WHERE change_id = ?
                """, (compliance_status.value, change_id))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to update change compliance status: {e}")


# Factory function
def get_audit_trail_system(db_path: str = "prompts/analytics/prompt_audit.db") -> PromptAuditTrail:
    """Get an audit trail system instance."""
    return PromptAuditTrail(db_path)
