#!/usr/bin/env python3
"""
Broken Windows Theory Implementation - Disorder Detection and Response
====================================================================

Immediate disorder detection and response system based on criminological research.
Implements zero tolerance for any form of system disorder.

Based on Wilson & Kelling (1982) Broken Windows Theory:
"If a window in a building is broken and is left unrepaired, all the rest 
of the windows will soon be broken."

Software Engineering Translation:
"If a broken link in a codebase is left unrepaired, all the rest of the 
system will soon decay."

Features:
- Real-time disorder detection
- 24-hour response SLA enforcement  
- Zero tolerance policy implementation
- Entropy prevention and order maintenance
- Psychological environment management
"""

import os
import re
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum


class DisorderType(Enum):
    """Types of disorder that signal broken windows."""
    BROKEN_LINK = "broken_link"
    INCOMPLETE_DOCUMENT = "incomplete_document"
    PLACEHOLDER_CONTENT = "placeholder_content"
    NAMING_VIOLATION = "naming_violation"
    DEAD_REFERENCE = "dead_reference"
    ORPHANED_FILE = "orphaned_file"
    INCONSISTENT_PATTERN = "inconsistent_pattern"
    OUTDATED_CONTENT = "outdated_content"


class SeverityLevel(Enum):
    """Severity levels for disorder signals."""
    CRITICAL = "CRITICAL"      # Visible to stakeholders, immediate response required
    HIGH = "HIGH"              # Affects functionality, 4-hour response
    MEDIUM = "MEDIUM"          # Quality degradation, 24-hour response  
    LOW = "LOW"                # Minor inconsistency, next maintenance cycle


@dataclass
class DisorderSignal:
    """Represents a detected disorder (broken window)."""
    file_path: str
    disorder_type: DisorderType
    severity: SeverityLevel
    description: str
    evidence: str
    impact_assessment: str
    fix_estimate_hours: float
    auto_fixable: bool
    detected_timestamp: str
    sla_deadline: str
    

@dataclass
class EntropyAssessment:
    """Assessment of system entropy and degradation risk."""
    total_disorders: int
    entropy_level: float  # 0.0 (perfect order) to 1.0 (complete chaos)
    degradation_trend: str  # "improving", "stable", "degrading"
    risk_factors: List[str]
    time_to_critical: Optional[str]  # Time until system becomes unusable
    

@dataclass
class OrderRestorationPlan:
    """Plan for restoring order and eliminating broken windows."""
    emergency_actions: List[str]
    repair_sequence: List[DisorderSignal]
    resource_requirements: Dict[str, int]
    completion_timeline: str
    success_criteria: List[str]


class BrokenWindowsDetector:
    """
    Main detector implementing Broken Windows Theory for software systems.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.disorders: List[DisorderSignal] = []
        
        # SLA timeframes based on severity
        self.sla_hours = {
            SeverityLevel.CRITICAL: 1,    # 1 hour for critical disorders
            SeverityLevel.HIGH: 4,        # 4 hours for high severity
            SeverityLevel.MEDIUM: 24,     # 24 hours for medium severity
            SeverityLevel.LOW: 168        # 1 week for low severity
        }
        
        # Placeholder content patterns that signal disorder
        self.placeholder_patterns = [
            r'\bTODO\b',
            r'\bFIXME\b',
            r'\bHACK\b',
            r'\bCOMING\s+SOON\b',
            r'\bPLACEHOLDER\b',
            r'\bTEMP\b',
            r'\bNOT\s+IMPLEMENTED\b',
            r'\bUNDER\s+CONSTRUCTION\b',
            r'\.\.\.+',  # Multiple dots indicating incomplete content
            r'\b(?:lorem|ipsum)\b',  # Lorem ipsum placeholder text
        ]
        
        # Broken link patterns
        self.broken_link_patterns = [
            r'\[([^\]]+)\]\(([^)]+)\)',  # Markdown links
            r'\[([^\]]+)\]:\s*(.+)',    # Reference links
            r'href=["\']([^"\']+)["\']', # HTML links
        ]
    
    def detect_all_disorders(self) -> List[DisorderSignal]:
        """
        Comprehensive disorder detection across the entire system.
        """
        print("🔍 Scanning for broken windows and disorder signals...")
        self.disorders = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if self._should_scan_file(file):
                    file_path = Path(root) / file
                    self._scan_file_for_disorders(file_path)
        
        # Sort by severity and then by SLA deadline
        self.disorders.sort(key=lambda d: (d.severity.value, d.sla_deadline))
        
        return self.disorders
    
    def _should_scan_file(self, filename: str) -> bool:
        """Determine if file should be scanned for disorders."""
        scan_extensions = {'.md', '.py', '.txt', '.rst', '.html', '.json', '.yaml', '.yml'}
        return any(filename.endswith(ext) for ext in scan_extensions)
    
    def _scan_file_for_disorders(self, file_path: Path) -> None:
        """Scan individual file for all types of disorders."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            rel_path = file_path.relative_to(self.project_root)
            
            # Detect different types of disorders
            self._detect_broken_links(rel_path, content)
            self._detect_placeholder_content(rel_path, content)
            self._detect_incomplete_documents(rel_path, content)
            self._detect_naming_violations(rel_path)
            self._detect_orphaned_files(rel_path, content)
            
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
    
    def _detect_broken_links(self, file_path: Path, content: str) -> None:
        """Detect broken hyperlinks and references."""
        for pattern in self.broken_link_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                link_text = match.group(1)
                link_target = match.group(2)
                
                # Check if link target exists
                if self._is_broken_link(file_path, link_target):
                    disorder = DisorderSignal(
                        file_path=str(file_path),
                        disorder_type=DisorderType.BROKEN_LINK,
                        severity=SeverityLevel.HIGH,
                        description=f"Broken link: '{link_text}' → '{link_target}'",
                        evidence=match.group(0),
                        impact_assessment="Broken navigation affects user experience and credibility",
                        fix_estimate_hours=0.5,
                        auto_fixable=True,
                        detected_timestamp=datetime.now().isoformat(),
                        sla_deadline=self._calculate_sla_deadline(SeverityLevel.HIGH)
                    )
                    self.disorders.append(disorder)
    
    def _is_broken_link(self, file_path: Path, link_target: str) -> bool:
        """Check if a link target is broken."""
        # Skip external URLs and anchors
        if link_target.startswith(('http://', 'https://', 'mailto:', '#')):
            return False
        
        # Resolve relative path
        if link_target.startswith('/'):
            target_path = self.project_root / link_target.lstrip('/')
        else:
            target_path = file_path.parent / link_target
        
        # Remove URL fragments and query parameters
        target_path = Path(str(target_path).split('#')[0].split('?')[0])
        
        return not target_path.exists()
    
    def _detect_placeholder_content(self, file_path: Path, content: str) -> None:
        """Detect placeholder content that signals incomplete work."""
        for pattern in self.placeholder_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                # Get context around the match
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].replace('\n', ' ')
                
                disorder = DisorderSignal(
                    file_path=str(file_path),
                    disorder_type=DisorderType.PLACEHOLDER_CONTENT,
                    severity=SeverityLevel.MEDIUM,
                    description=f"Placeholder content found: {match.group(0)}",
                    evidence=f"Context: ...{context}...",
                    impact_assessment="Placeholder content signals incomplete work and unprofessional appearance",
                    fix_estimate_hours=2.0,
                    auto_fixable=False,
                    detected_timestamp=datetime.now().isoformat(),
                    sla_deadline=self._calculate_sla_deadline(SeverityLevel.MEDIUM)
                )
                self.disorders.append(disorder)
    
    def _detect_incomplete_documents(self, file_path: Path, content: str) -> None:
        """Detect documents that appear incomplete or minimal."""
        lines = content.strip().split('\n')
        word_count = len(content.split())
        
        # Check for minimal content
        if file_path.suffix == '.md' and word_count < 50:
            disorder = DisorderSignal(
                file_path=str(file_path),
                disorder_type=DisorderType.INCOMPLETE_DOCUMENT,
                severity=SeverityLevel.MEDIUM,
                description=f"Document appears incomplete ({word_count} words, {len(lines)} lines)",
                evidence=f"Content preview: {content[:200]}...",
                impact_assessment="Incomplete documents provide poor user experience and signal low quality",
                fix_estimate_hours=4.0,
                auto_fixable=False,
                detected_timestamp=datetime.now().isoformat(),
                sla_deadline=self._calculate_sla_deadline(SeverityLevel.MEDIUM)
            )
            self.disorders.append(disorder)
    
    def _detect_naming_violations(self, file_path: Path) -> None:
        """Detect naming convention violations."""
        filename = file_path.name
        
        # Check for common naming violations
        violations = []
        
        # Check for spaces in filenames
        if ' ' in filename:
            violations.append("Contains spaces")
        
        # Check for uppercase in non-standard files
        if filename != filename.lower() and not self._is_standard_uppercase_file(filename):
            violations.append("Non-standard capitalization")
        
        # Check for special characters
        if re.search(r'[^a-zA-Z0-9._-]', filename):
            violations.append("Contains special characters")
        
        for violation in violations:
            disorder = DisorderSignal(
                file_path=str(file_path),
                disorder_type=DisorderType.NAMING_VIOLATION,
                severity=SeverityLevel.LOW,
                description=f"Naming violation: {violation}",
                evidence=f"Filename: {filename}",
                impact_assessment="Naming violations create inconsistency and break automation",
                fix_estimate_hours=0.25,
                auto_fixable=True,
                detected_timestamp=datetime.now().isoformat(),
                sla_deadline=self._calculate_sla_deadline(SeverityLevel.LOW)
            )
            self.disorders.append(disorder)
    
    def _is_standard_uppercase_file(self, filename: str) -> bool:
        """Check if file follows standard uppercase conventions."""
        uppercase_standards = ['README.md', 'LICENSE', 'Dockerfile', 'Makefile']
        return filename in uppercase_standards
    
    def _detect_orphaned_files(self, file_path: Path, content: str) -> None:
        """Detect files that may be orphaned or unreferenced."""
        # This is a simplified check - in practice, would need comprehensive reference analysis
        pass
    
    def _calculate_sla_deadline(self, severity: SeverityLevel) -> str:
        """Calculate SLA deadline based on severity."""
        hours = self.sla_hours[severity]
        deadline = datetime.now() + timedelta(hours=hours)
        return deadline.isoformat()
    
    def assess_entropy_level(self) -> EntropyAssessment:
        """Assess current system entropy level and degradation risk."""
        total_disorders = len(self.disorders)
        
        # Calculate entropy level (0.0 = perfect order, 1.0 = complete chaos)
        if total_disorders == 0:
            entropy_level = 0.0
        else:
            # Weight by severity
            severity_weights = {
                SeverityLevel.CRITICAL: 1.0,
                SeverityLevel.HIGH: 0.7,
                SeverityLevel.MEDIUM: 0.4,
                SeverityLevel.LOW: 0.1
            }
            
            weighted_disorders = sum(severity_weights[d.severity] for d in self.disorders)
            # Normalize to reasonable scale (assuming 50+ weighted disorders = chaos)
            entropy_level = min(1.0, weighted_disorders / 50.0)
        
        # Assess degradation trend (simplified - would need historical data)
        degradation_trend = "stable"
        if entropy_level > 0.7:
            degradation_trend = "degrading"
        elif entropy_level < 0.2:
            degradation_trend = "improving"
        
        # Identify risk factors
        risk_factors = []
        if any(d.severity == SeverityLevel.CRITICAL for d in self.disorders):
            risk_factors.append("Critical disorders present")
        if total_disorders > 20:
            risk_factors.append("High disorder count")
        if any(d.disorder_type == DisorderType.BROKEN_LINK for d in self.disorders):
            risk_factors.append("Broken navigation infrastructure")
        
        # Estimate time to critical degradation
        time_to_critical = None
        if entropy_level > 0.5:
            time_to_critical = "System approaching critical degradation"
        
        return EntropyAssessment(
            total_disorders=total_disorders,
            entropy_level=entropy_level,
            degradation_trend=degradation_trend,
            risk_factors=risk_factors,
            time_to_critical=time_to_critical
        )
    
    def create_restoration_plan(self) -> OrderRestorationPlan:
        """Create plan for restoring order and eliminating broken windows."""
        # Emergency actions for critical disorders
        emergency_actions = []
        for disorder in self.disorders:
            if disorder.severity == SeverityLevel.CRITICAL:
                emergency_actions.append(f"IMMEDIATE: Fix {disorder.description} in {disorder.file_path}")
        
        # Sequence repairs by severity and dependencies
        repair_sequence = sorted(self.disorders, key=lambda d: (d.severity.value, d.fix_estimate_hours))
        
        # Estimate resource requirements
        total_hours = sum(d.fix_estimate_hours for d in self.disorders)
        resource_requirements = {
            "developer_hours": total_hours,
            "technical_writer_hours": sum(d.fix_estimate_hours for d in self.disorders 
                                        if d.disorder_type == DisorderType.INCOMPLETE_DOCUMENT),
            "qa_hours": total_hours * 0.3  # 30% QA overhead
        }
        
        # Calculate completion timeline
        working_hours_per_day = 8
        days_required = max(1, total_hours / working_hours_per_day)
        completion_timeline = f"{days_required:.1f} days with dedicated team"
        
        # Define success criteria
        success_criteria = [
            "Zero broken links across all documentation",
            "Zero placeholder content in any document", 
            "All documents complete and professional",
            "100% naming convention compliance",
            "Entropy level < 0.1 (near-perfect order)",
            "All SLA deadlines met"
        ]
        
        return OrderRestorationPlan(
            emergency_actions=emergency_actions,
            repair_sequence=repair_sequence,
            resource_requirements=resource_requirements,
            completion_timeline=completion_timeline,
            success_criteria=success_criteria
        )
    
    def generate_broken_windows_report(self) -> Dict:
        """Generate comprehensive Broken Windows Theory analysis report."""
        entropy_assessment = self.assess_entropy_level()
        restoration_plan = self.create_restoration_plan()
        
        # Categorize disorders by type
        disorders_by_type = {}
        for disorder in self.disorders:
            disorder_type = disorder.disorder_type.value
            if disorder_type not in disorders_by_type:
                disorders_by_type[disorder_type] = []
            disorders_by_type[disorder_type].append(disorder)
        
        # Calculate SLA compliance
        overdue_disorders = [d for d in self.disorders 
                           if datetime.fromisoformat(d.sla_deadline) < datetime.now()]
        
        report = {
            "broken_windows_analysis": {
                "scan_timestamp": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "total_disorders": len(self.disorders),
                "entropy_assessment": asdict(entropy_assessment),
                "sla_compliance": {
                    "total_disorders": len(self.disorders),
                    "overdue_disorders": len(overdue_disorders),
                    "compliance_rate": 1.0 - (len(overdue_disorders) / max(1, len(self.disorders)))
                },
                "disorders_by_type": {k: len(v) for k, v in disorders_by_type.items()},
                "disorders_by_severity": {
                    severity.value: len([d for d in self.disorders if d.severity == severity])
                    for severity in SeverityLevel
                },
                "restoration_plan": asdict(restoration_plan),
                "immediate_actions": restoration_plan.emergency_actions[:5],  # Top 5 emergency actions
                "psychological_impact": self._assess_psychological_impact(entropy_assessment)
            },
            "detailed_disorders": [asdict(d) for d in self.disorders[:20]]  # Top 20 for report
        }
        
        return report
    
    def _assess_psychological_impact(self, entropy: EntropyAssessment) -> Dict[str, str]:
        """Assess psychological impact of current disorder level."""
        if entropy.entropy_level < 0.1:
            return {
                "team_morale": "HIGH - Clean environment promotes excellence",
                "quality_culture": "STRONG - High standards are clearly maintained",
                "stakeholder_confidence": "HIGH - Professional appearance builds trust",
                "development_efficiency": "OPTIMAL - No disorder overhead"
            }
        elif entropy.entropy_level < 0.3:
            return {
                "team_morale": "GOOD - Minor issues don't affect overall confidence",
                "quality_culture": "SOLID - Standards mostly maintained",
                "stakeholder_confidence": "GOOD - Generally professional appearance",
                "development_efficiency": "GOOD - Minimal disorder overhead"
            }
        elif entropy.entropy_level < 0.7:
            return {
                "team_morale": "CONCERNING - Visible disorder affects confidence",
                "quality_culture": "WEAKENING - Standards inconsistently applied",
                "stakeholder_confidence": "DECLINING - Quality issues are visible",
                "development_efficiency": "IMPACTED - Disorder creates overhead"
            }
        else:
            return {
                "team_morale": "CRITICAL - Disorder signals system neglect",
                "quality_culture": "BROKEN - Standards not maintained", 
                "stakeholder_confidence": "LOW - Unprofessional appearance",
                "development_efficiency": "SEVERELY IMPACTED - High disorder overhead"
            }


def main():
    """CLI interface for Broken Windows Theory disorder detection."""
    parser = argparse.ArgumentParser(
        description="Broken Windows Theory Implementation - Disorder Detection and Response",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan for all disorders
  python broken_windows_detector.py --scan
  
  # Generate comprehensive report
  python broken_windows_detector.py --scan --report
  
  # Focus on critical disorders only
  python broken_windows_detector.py --scan --severity CRITICAL
  
  # Continuous monitoring mode
  python broken_windows_detector.py --monitor --interval 300
        """
    )
    
    parser.add_argument('--scan', action='store_true',
                       help='Scan for disorder signals (broken windows)')
    parser.add_argument('--monitor', action='store_true',
                       help='Continuous monitoring mode')
    parser.add_argument('--interval', type=int, default=300,
                       help='Monitoring interval in seconds (default: 300)')
    parser.add_argument('--severity', choices=[s.value for s in SeverityLevel],
                       help='Filter by severity level')
    parser.add_argument('--root', default='.',
                       help='Project root directory (default: current directory)')
    parser.add_argument('--report', action='store_true',
                       help='Generate comprehensive disorder report')
    parser.add_argument('--json-output',
                       help='Save JSON report to file')
    
    args = parser.parse_args()
    
    if not (args.scan or args.monitor):
        parser.error("Must specify either --scan or --monitor")
    
    detector = BrokenWindowsDetector(args.root)
    
    def run_detection():
        """Run disorder detection and reporting."""
        print("🏚️  BROKEN WINDOWS THEORY DISORDER DETECTION")
        print("=" * 50)
        
        disorders = detector.detect_all_disorders()
        
        # Filter by severity if specified
        if args.severity:
            severity_level = SeverityLevel(args.severity)
            disorders = [d for d in disorders if d.severity == severity_level]
        
        entropy = detector.assess_entropy_level()
        
        # Print summary
        print(f"\n📊 DISORDER ANALYSIS SUMMARY:")
        print(f"   Total disorders detected: {len(disorders)}")
        print(f"   System entropy level: {entropy.entropy_level:.2f}/1.0")
        print(f"   Degradation trend: {entropy.degradation_trend}")
        
        if entropy.entropy_level > 0.5:
            print(f"   ⚠️  WARNING: High entropy detected - immediate action required")
        
        # Print severity breakdown
        severity_counts = {}
        for disorder in disorders:
            severity_counts[disorder.severity.value] = severity_counts.get(disorder.severity.value, 0) + 1
        
        print(f"\n⚠️  DISORDERS BY SEVERITY:")
        for severity in SeverityLevel:
            count = severity_counts.get(severity.value, 0)
            sla_hours = detector.sla_hours[severity]
            print(f"   {severity.value}: {count} disorders (SLA: {sla_hours}h)")
        
        # Show critical disorders first
        critical_disorders = [d for d in disorders if d.severity == SeverityLevel.CRITICAL]
        if critical_disorders:
            print(f"\n🚨 CRITICAL DISORDERS (IMMEDIATE ACTION REQUIRED):")
            for disorder in critical_disorders[:5]:
                print(f"   • {disorder.file_path}: {disorder.description}")
                print(f"     SLA Deadline: {disorder.sla_deadline}")
                print()
        
        # Show sample of other disorders
        other_disorders = [d for d in disorders if d.severity != SeverityLevel.CRITICAL]
        if other_disorders:
            print(f"\n🔍 OTHER DISORDERS (Sample):")
            for disorder in other_disorders[:10]:
                print(f"   • {disorder.severity.value}: {disorder.file_path}")
                print(f"     {disorder.description}")
                print()
        
        # Generate full report if requested
        if args.report:
            report = detector.generate_broken_windows_report()
            
            print(f"\n📋 BROKEN WINDOWS THEORY ANALYSIS:")
            print(f"   Psychological Impact Assessment:")
            for aspect, assessment in report["broken_windows_analysis"]["psychological_impact"].items():
                print(f"     {aspect}: {assessment}")
            
            print(f"\n📈 RESTORATION PLAN:")
            plan = report["broken_windows_analysis"]["restoration_plan"]
            print(f"   Timeline: {plan['completion_timeline']}")
            print(f"   Required resources: {plan['resource_requirements']}")
            
            if plan["emergency_actions"]:
                print(f"\n🚨 IMMEDIATE ACTIONS REQUIRED:")
                for action in plan["emergency_actions"]:
                    print(f"     • {action}")
            
            # Save JSON report if requested
            if args.json_output:
                with open(args.json_output, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                print(f"\n📄 Full report saved: {args.json_output}")
        
        return len(disorders) > 0
    
    if args.scan:
        # Single scan
        has_disorders = run_detection()
        sys.exit(1 if has_disorders else 0)
    
    elif args.monitor:
        # Continuous monitoring
        print(f"🔄 Starting continuous monitoring (interval: {args.interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                has_disorders = run_detection()
                if has_disorders:
                    print(f"⚠️  Disorders detected - review and fix within SLA deadlines")
                else:
                    print("✅ System order maintained - no disorders detected")
                
                print(f"\n⏰ Next scan in {args.interval} seconds...")
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
            sys.exit(0)


if __name__ == "__main__":
    main()
