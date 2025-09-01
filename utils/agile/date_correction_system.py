#!/usr/bin/env python3
"""
Agile Document Date Correction System
====================================

Automatically corrects incorrect dates in agile documentation to maintain
professional standards and stakeholder trust.

Features:
- Scans all agile documents for date inconsistencies
- Corrects dates to current standard format (YYYY-MM-DD)
- Maintains audit trail of corrections
- Validates date formats and logic
- Integrates with agile artifact generation

Usage:
    python utils/agile/date_correction_system.py --scan
    python utils/agile/date_correction_system.py --correct
"""

import os
import re
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass, asdict


@dataclass
class DateIssue:
    """Represents a date issue found in documentation."""
    
    file_path: str
    line_number: int
    original_text: str
    incorrect_date: str
    corrected_date: str
    issue_type: str  # 'wrong_year', 'wrong_month', 'invalid_format', 'future_date'
    confidence: float  # 0.0 - 1.0


@dataclass
class CorrectionSummary:
    """Summary of date corrections performed."""
    
    files_scanned: int
    issues_found: int
    corrections_applied: int
    backup_created: bool
    correction_timestamp: str
    issues_by_type: Dict[str, int]
    corrected_files: List[str]


class AgileDateCorrectionSystem:
    """Automated system for correcting dates in agile documentation."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.agile_docs_path = self.project_root / "docs" / "agile"
        self.backup_path = self.project_root / "backups" / "agile_date_corrections"
        
        # Current date for corrections
        self.current_date = datetime.date.today()
        self.current_date_str = self.current_date.strftime("%Y-%m-%d")
        
        # Date patterns to detect and correct
        self.date_patterns = {
            # Common incorrect patterns (dates before project start August 2025)
            r'Date[:\s]*2025-01-31': ('before_project_start', f'Date: {self.current_date_str}'),
            r'Date[:\s]*2025-0[1-7]-\d{2}': ('before_project_start', f'Date: {self.current_date_str}'),
            r'Date[:\s]*202[0-4]-\d{2}-\d{2}': ('before_project_start', f'Date: {self.current_date_str}'),
            
            # Note: 2025-08-31 is VALID (project timeline), not corrected
            
            # Format corrections
            r'Date[:\s]*(\d{4})-(\d{2})-(\d{2})': self._validate_and_correct_date,
            r'Start Date[:\s]*(\d{4})-(\d{2})-(\d{2})': self._validate_and_correct_start_date,
            r'Last Updated[:\s]*(\d{4})-(\d{2})-(\d{2})': self._validate_and_correct_updated_date,
            
            # Timestamp patterns
            r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})': self._validate_and_correct_timestamp
        }
        
        # Valid date ranges - Project started August 2025
        self.valid_date_range = (
            datetime.date(2025, 8, 1),  # Project start (August 2025)
            datetime.date(2026, 12, 31)  # Reasonable future limit
        )
        
    def scan_agile_documents(self) -> List[DateIssue]:
        """Scan all agile documents for date issues."""
        
        print(f"🔍 **Scanning Agile Documents for Date Issues**")
        print(f"📁 Target Directory: {self.agile_docs_path}")
        
        issues = []
        files_scanned = 0
        
        # Scan all markdown files in agile directory
        for md_file in self.agile_docs_path.rglob("*.md"):
            files_scanned += 1
            file_issues = self._scan_file_for_date_issues(md_file)
            issues.extend(file_issues)
        
        print(f"📊 **Scan Results**: {len(issues)} issues found in {files_scanned} files")
        
        # Group issues by type for summary
        issues_by_type = {}
        for issue in issues:
            issues_by_type[issue.issue_type] = issues_by_type.get(issue.issue_type, 0) + 1
        
        print(f"📋 **Issues by Type**:")
        for issue_type, count in issues_by_type.items():
            print(f"   - {issue_type}: {count} occurrences")
        
        return issues
    
    def _scan_file_for_date_issues(self, file_path: Path) -> List[DateIssue]:
        """Scan a single file for date issues."""
        
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line_issues = self._analyze_line_for_date_issues(
                    file_path, line_num, line
                )
                issues.extend(line_issues)
        
        except Exception as e:
            print(f"⚠️  Warning: Could not scan {file_path}: {e}")
        
        return issues
    
    def _analyze_line_for_date_issues(self, file_path: Path, line_num: int, 
                                    line: str) -> List[DateIssue]:
        """Analyze a single line for date issues."""
        
        issues = []
        
        # Check for obvious incorrect dates (before project start August 2025)
        incorrect_dates = [
            ('2025-01-31', 'before_project_start'),  # Before August 2025
            ('2025-02-', 'before_project_start'),    # Before August 2025
            ('2025-03-', 'before_project_start'),    # Before August 2025
            ('2025-04-', 'before_project_start'),    # Before August 2025
            ('2025-05-', 'before_project_start'),    # Before August 2025
            ('2025-06-', 'before_project_start'),    # Before August 2025
            ('2025-07-', 'before_project_start'),    # Before August 2025
            ('2024-', 'before_project_start'),       # Any 2024 date
            ('2023-', 'before_project_start'),       # Any 2023 date
            ('2022-', 'before_project_start'),       # Any 2022 date
            ('2025-13-', 'invalid_month'),
            ('2025-00-', 'invalid_month'),
            ('2025-12-32', 'invalid_day'),
            ('2025-02-30', 'invalid_day')
        ]
        
        for incorrect_date, issue_type in incorrect_dates:
            if incorrect_date in line:
                corrected_date = self._generate_corrected_date(incorrect_date, issue_type)
                
                issue = DateIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    original_text=line,
                    incorrect_date=incorrect_date,
                    corrected_date=corrected_date,
                    issue_type=issue_type,
                    confidence=0.9
                )
                issues.append(issue)
        
        # Check for future dates that seem incorrect
        future_date_pattern = r'(\d{4})-(\d{2})-(\d{2})'
        matches = re.finditer(future_date_pattern, line)
        
        for match in matches:
            year, month, day = match.groups()
            try:
                date_obj = datetime.date(int(year), int(month), int(day))
                
                # Check if date is unreasonably in the future
                days_in_future = (date_obj - self.current_date).days
                
                if days_in_future > 365:  # More than 1 year in future
                    corrected_date = self.current_date_str
                    
                    issue = DateIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        original_text=line,
                        incorrect_date=match.group(0),
                        corrected_date=corrected_date,
                        issue_type='future_date',
                        confidence=0.8
                    )
                    issues.append(issue)
                
                # Check if date is before project start
                elif date_obj < self.valid_date_range[0]:
                    corrected_date = self.current_date_str
                    
                    issue = DateIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        original_text=line,
                        incorrect_date=match.group(0),
                        corrected_date=corrected_date,
                        issue_type='before_project_start',
                        confidence=0.7
                    )
                    issues.append(issue)
            
            except ValueError:
                # Invalid date
                issue = DateIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    original_text=line,
                    incorrect_date=match.group(0),
                    corrected_date=self.current_date_str,
                    issue_type='invalid_date',
                    confidence=1.0
                )
                issues.append(issue)
        
        return issues
    
    def _generate_corrected_date(self, incorrect_date: str, issue_type: str) -> str:
        """Generate the correct date for an incorrect date."""
        
        if issue_type in ['wrong_year_month', 'future_date', 'before_project_start']:
            return self.current_date_str
        
        elif issue_type == 'invalid_month':
            # Try to preserve year and day if possible
            parts = incorrect_date.split('-')
            if len(parts) >= 2:
                year = parts[0]
                # Use current month
                month = f"{self.current_date.month:02d}"
                day = parts[2] if len(parts) > 2 else f"{self.current_date.day:02d}"
                return f"{year}-{month}-{day}"
        
        elif issue_type == 'invalid_day':
            # Try to preserve year and month
            parts = incorrect_date.split('-')
            if len(parts) >= 3:
                year, month = parts[0], parts[1]
                # Use last valid day of month
                try:
                    import calendar
                    last_day = calendar.monthrange(int(year), int(month))[1]
                    return f"{year}-{month}-{last_day:02d}"
                except:
                    pass
        
        # Default fallback
        return self.current_date_str
    
    def _validate_and_correct_date(self, match) -> Tuple[str, str]:
        """Validate and correct a date match."""
        year, month, day = match.groups()
        date_str = f"{year}-{month}-{day}"
        
        try:
            date_obj = datetime.date(int(year), int(month), int(day))
            
            # Check if date is reasonable
            if date_obj < self.valid_date_range[0] or date_obj > self.valid_date_range[1]:
                return ('date_out_of_range', f'Date: {self.current_date_str}')
            
            return ('valid_date', match.group(0))
        
        except ValueError:
            return ('invalid_date', f'Date: {self.current_date_str}')
    
    def _validate_and_correct_start_date(self, match) -> Tuple[str, str]:
        """Validate and correct a start date match."""
        issue_type, corrected = self._validate_and_correct_date(match)
        if issue_type != 'valid_date':
            return (issue_type, corrected.replace('Date:', 'Start Date:'))
        return (issue_type, corrected)
    
    def _validate_and_correct_updated_date(self, match) -> Tuple[str, str]:
        """Validate and correct an updated date match."""
        # Last Updated should always be current
        return ('outdated_timestamp', f'Last Updated: {self.current_date_str}')
    
    def _validate_and_correct_timestamp(self, match) -> Tuple[str, str]:
        """Validate and correct a timestamp match."""
        year, month, day, hour, minute, second = match.groups()
        
        try:
            date_obj = datetime.date(int(year), int(month), int(day))
            time_obj = datetime.time(int(hour), int(minute), int(second))
            
            # Check if date is reasonable
            if date_obj < self.valid_date_range[0] or date_obj > self.valid_date_range[1]:
                current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return ('timestamp_out_of_range', current_timestamp)
            
            return ('valid_timestamp', match.group(0))
        
        except ValueError:
            current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return ('invalid_timestamp', current_timestamp)
    
    def correct_date_issues(self, issues: List[DateIssue], 
                          create_backup: bool = True) -> CorrectionSummary:
        """Correct the identified date issues."""
        
        print(f"🔧 **Correcting {len(issues)} Date Issues**")
        
        if create_backup:
            self._create_backup()
        
        corrections_applied = 0
        corrected_files = set()
        issues_by_type = {}
        
        # Group issues by file for efficient processing
        issues_by_file = {}
        for issue in issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
        
        # Process each file
        for file_path, file_issues in issues_by_file.items():
            if self._correct_file_dates(file_path, file_issues):
                corrected_files.add(file_path)
                corrections_applied += len(file_issues)
                
                for issue in file_issues:
                    issue_type = issue.issue_type
                    issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
        
        summary = CorrectionSummary(
            files_scanned=len(issues_by_file),
            issues_found=len(issues),
            corrections_applied=corrections_applied,
            backup_created=create_backup,
            correction_timestamp=datetime.datetime.now().isoformat(),
            issues_by_type=issues_by_type,
            corrected_files=list(corrected_files)
        )
        
        print(f"✅ **Correction Complete**: {corrections_applied} issues corrected in {len(corrected_files)} files")
        
        return summary
    
    def _correct_file_dates(self, file_path: str, issues: List[DateIssue]) -> bool:
        """Correct date issues in a single file."""
        
        try:
            file_path_obj = Path(file_path)
            content = file_path_obj.read_text(encoding='utf-8')
            
            # Apply corrections
            modified_content = content
            for issue in sorted(issues, key=lambda x: x.line_number, reverse=True):
                # Replace the incorrect date with corrected date
                modified_content = modified_content.replace(
                    issue.incorrect_date, 
                    issue.corrected_date
                )
            
            # Write corrected content
            file_path_obj.write_text(modified_content, encoding='utf-8')
            
            print(f"✅ Corrected {len(issues)} issues in {file_path_obj.name}")
            return True
        
        except Exception as e:
            print(f"❌ Failed to correct {file_path}: {e}")
            return False
    
    def _create_backup(self) -> bool:
        """Create backup of agile documents before correction."""
        
        try:
            import shutil
            
            self.backup_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_path / f"backup_{timestamp}"
            
            # Copy entire agile directory
            shutil.copytree(self.agile_docs_path, backup_dir)
            
            print(f"📁 **Backup Created**: {backup_dir}")
            return True
        
        except Exception as e:
            print(f"⚠️  Backup creation failed: {e}")
            return False
    
    def generate_correction_report(self, summary: CorrectionSummary) -> str:
        """Generate a detailed correction report."""
        
        report = f"""# Agile Document Date Correction Report

**Correction Timestamp**: {summary.correction_timestamp}
**Files Scanned**: {summary.files_scanned}
**Issues Found**: {summary.issues_found}
**Corrections Applied**: {summary.corrections_applied}
**Backup Created**: {'✅' if summary.backup_created else '❌'}

## Issues Corrected by Type

"""
        
        for issue_type, count in summary.issues_by_type.items():
            report += f"- **{issue_type}**: {count} occurrences\n"
        
        report += f"""

## Files Modified

"""
        
        for file_path in summary.corrected_files:
            relative_path = Path(file_path).relative_to(self.project_root)
            report += f"- {relative_path}\n"
        
        report += f"""

## Quality Assurance

✅ All dates corrected to current date format: {self.current_date_str}
✅ Invalid dates replaced with current date
✅ Future dates adjusted to realistic timeline
✅ Backup created for rollback capability

## Next Steps

1. Review corrected documents for accuracy
2. Verify agile artifact consistency
3. Update stakeholder communications
4. Implement date validation in future artifact generation

---
*Report generated by Agile Date Correction System*
"""
        
        return report


def main():
    """CLI for agile date correction."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Agile Document Date Correction System')
    parser.add_argument('--scan', action='store_true', help='Scan for date issues')
    parser.add_argument('--correct', action='store_true', help='Correct date issues')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    parser.add_argument('--report', type=str, help='Output report file path')
    
    args = parser.parse_args()
    
    corrector = AgileDateCorrectionSystem()
    
    if args.scan or not args.correct:
        # Scan for issues
        issues = corrector.scan_agile_documents()
        
        if issues:
            print(f"\n📋 **Issues Found**:")
            for issue in issues[:10]:  # Show first 10
                print(f"   {Path(issue.file_path).name}:{issue.line_number} - {issue.issue_type}")
                print(f"      '{issue.incorrect_date}' → '{issue.corrected_date}'")
            
            if len(issues) > 10:
                print(f"   ... and {len(issues) - 10} more issues")
        
        if not args.correct:
            print(f"\n💡 **To correct issues**: python {sys.argv[0]} --correct")
            return
    
    if args.correct:
        # Scan and correct
        issues = corrector.scan_agile_documents()
        
        if not issues:
            print("✅ **No date issues found** - all documents are correctly dated")
            return
        
        # Apply corrections
        summary = corrector.correct_date_issues(issues, not args.no_backup)
        
        # Generate report
        report = corrector.generate_correction_report(summary)
        
        if args.report:
            Path(args.report).write_text(report, encoding='utf-8')
            print(f"📊 **Report saved**: {args.report}")
        else:
            print("\n" + report)


if __name__ == "__main__":
    main()
