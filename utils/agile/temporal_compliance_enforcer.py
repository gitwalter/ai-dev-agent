#!/usr/bin/env python3
"""
Temporal Compliance Enforcer for Agile Artifacts
Ensures all agile artifacts always use real, current timestamps from local machine.
Implements the Temporal Trust Rule across all automation systems.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from .temporal_authority import get_temporal_authority, validate_temporal_compliance, TemporalTrustViolation
import logging

logger = logging.getLogger(__name__)

class TemporalComplianceEnforcer:
    """Enforces temporal trust rule across all agile artifacts and automation."""
    
    def __init__(self, project_root: Path = None):
        self.temporal_auth = get_temporal_authority()
        self.project_root = project_root or Path.cwd()
        self.violations_found = []
        
    def scan_all_agile_artifacts(self) -> Dict[str, List[str]]:
        """Scan all agile artifacts for temporal compliance violations."""
        violations = {
            'outdated_dates': [],
            'placeholder_dates': [],
            'missing_timestamps': [],
            'incorrect_format': []
        }
        
        # Scan agile directory
        agile_dir = self.project_root / "docs" / "agile"
        if agile_dir.exists():
            for file_path in agile_dir.rglob("*.md"):
                if self._should_check_file(file_path):
                    file_violations = self._check_file_temporal_compliance(file_path)
                    for violation_type, violation_list in file_violations.items():
                        violations[violation_type].extend(violation_list)
        
        return violations
    
    def _should_check_file(self, file_path: Path) -> bool:
        """Determine if file should be checked for temporal compliance."""
        # Skip backup files
        if '.backup_' in file_path.name:
            return False
        
        # Skip completion reports (they should preserve original dates)
        if 'completion' in file_path.name.lower() and 'report' in file_path.name.lower():
            return False
            
        # Check agile artifacts
        return file_path.suffix == '.md'
    
    def _check_file_temporal_compliance(self, file_path: Path) -> Dict[str, List[str]]:
        """Check a single file for temporal compliance."""
        violations = {
            'outdated_dates': [],
            'placeholder_dates': [],
            'missing_timestamps': [],
            'incorrect_format': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for outdated dates
            current_date = self.temporal_auth.today()
            outdated_patterns = [
                r'2025-09-04', r'2025-09-03', r'2025-09-02', r'2025-09-01',
                r'2025-08-\d{2}', r'2024-\d{2}-\d{2}'
            ]
            
            for pattern in outdated_patterns:
                if re.search(pattern, content):
                    violations['outdated_dates'].append(f"{file_path}: Found outdated date {pattern}")
            
            # Check for placeholder dates
            placeholder_patterns = [
                r'\[DATE\]', r'\[TIMESTAMP\]', r'TODO.*date', r'TBD.*date',
                r'YYYY-MM-DD', r'HH:MM:SS'
            ]
            
            for pattern in placeholder_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violations['placeholder_dates'].append(f"{file_path}: Found placeholder {pattern}")
            
            # Check Last Updated fields
            if "Last Updated" in content:
                if current_date not in content:
                    violations['missing_timestamps'].append(f"{file_path}: Last Updated should use {current_date}")
            
            return violations
            
        except Exception as e:
            logger.error(f"Error checking {file_path}: {e}")
            return violations
    
    def fix_temporal_violations(self, file_path: Path) -> bool:
        """Fix temporal violations in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            current_date = self.temporal_auth.today()
            current_timestamp = self.temporal_auth.timestamp()
            
            # Fix outdated Last Updated fields
            content = re.sub(
                r'(\*\*Last Updated\*\*:\s*)(2025-09-[0-4]\d|\d{4}-\d{2}-\d{2})',
                f'\\g<1>{current_date}',
                content
            )
            
            # Fix outdated timestamps in Last Updated
            content = re.sub(
                r'(\*\*Last Updated\*\*:\s*)(2025-09-[0-4]\d\s+\d{2}:\d{2}:\d{2})',
                f'\\g<1>{current_timestamp}',
                content
            )
            
            # Fix placeholder dates
            content = re.sub(r'\[DATE\]', current_date, content)
            content = re.sub(r'\[TIMESTAMP\]', current_timestamp, content)
            
            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Fixed temporal violations in {file_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
            return False
    
    def enforce_temporal_compliance_all_files(self) -> Dict[str, int]:
        """Enforce temporal compliance across all agile artifacts."""
        results = {
            'files_scanned': 0,
            'files_fixed': 0,
            'violations_found': 0,
            'errors': 0
        }
        
        violations = self.scan_all_agile_artifacts()
        results['violations_found'] = sum(len(v) for v in violations.values())
        
        if results['violations_found'] > 0:
            logger.warning(f"Found {results['violations_found']} temporal compliance violations")
            
            # Fix violations
            agile_dir = self.project_root / "docs" / "agile"
            if agile_dir.exists():
                for file_path in agile_dir.rglob("*.md"):
                    if self._should_check_file(file_path):
                        results['files_scanned'] += 1
                        try:
                            if self.fix_temporal_violations(file_path):
                                results['files_fixed'] += 1
                        except Exception as e:
                            results['errors'] += 1
                            logger.error(f"Error processing {file_path}: {e}")
        
        return results
    
    def create_temporal_compliance_report(self) -> str:
        """Create a comprehensive temporal compliance report."""
        violations = self.scan_all_agile_artifacts()
        current_time = self.temporal_auth.timestamp()
        
        report = f"""# Temporal Compliance Report
        
**Generated**: {current_time}  
**Scanner**: TemporalComplianceEnforcer  
**Authority**: Local Machine Time (Trusted)

## 🎯 **Compliance Status**

### **Violations Found**
- **Outdated Dates**: {len(violations['outdated_dates'])}
- **Placeholder Dates**: {len(violations['placeholder_dates'])}
- **Missing Timestamps**: {len(violations['missing_timestamps'])}
- **Format Issues**: {len(violations['incorrect_format'])}

**Total Violations**: {sum(len(v) for v in violations.values())}

## 📊 **Violation Details**

### **Outdated Dates**
{chr(10).join(violations['outdated_dates']) if violations['outdated_dates'] else "✅ No outdated dates found"}

### **Placeholder Dates**
{chr(10).join(violations['placeholder_dates']) if violations['placeholder_dates'] else "✅ No placeholder dates found"}

### **Missing Timestamps**
{chr(10).join(violations['missing_timestamps']) if violations['missing_timestamps'] else "✅ All timestamps present"}

## 🔧 **Recommended Actions**

1. **Fix Outdated Dates**: Update all dates to current system date: {self.temporal_auth.today()}
2. **Remove Placeholders**: Replace all placeholder dates with real timestamps
3. **Add Missing Timestamps**: Add "Last Updated" fields where missing
4. **Validate Format**: Ensure all dates follow YYYY-MM-DD format

## 🛡️ **Temporal Trust Enforcement**

This report enforces the Temporal Trust Rule:
- **Always trust local machine time**
- **Never use placeholder or fake dates**
- **Update timestamps when modifying artifacts**
- **Maintain temporal consistency across all artifacts**

---

**Report Status**: {'✅ COMPLIANT' if sum(len(v) for v in violations.values()) == 0 else '⚠️ VIOLATIONS FOUND'}  
**Next Scan**: Run after any artifact modifications
"""
        
        return report

def enforce_temporal_compliance(project_root: Path = None) -> Dict[str, int]:
    """Main function to enforce temporal compliance across all agile artifacts."""
    enforcer = TemporalComplianceEnforcer(project_root)
    return enforcer.enforce_temporal_compliance_all_files()

def validate_agile_artifact_dates(content: str) -> bool:
    """Validate that agile artifact content uses current system dates."""
    try:
        validate_temporal_compliance(content)
        return True
    except TemporalTrustViolation as e:
        logger.error(f"Temporal compliance violation: {e}")
        return False

# Export main functions for use in other automation scripts
__all__ = [
    'TemporalComplianceEnforcer',
    'enforce_temporal_compliance', 
    'validate_agile_artifact_dates'
]
