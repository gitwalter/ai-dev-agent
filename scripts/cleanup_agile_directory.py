#!/usr/bin/env python3
"""
Agile Directory Cleanup Script
===============================

Removes obsolete files, consolidates documentation, and organizes useful files.

Features:
- Identifies obsolete/redundant files
- Removes historical noise
- Consolidates multiple summaries
- Organizes files into proper subdirectories
- Updates index files

Usage:
    python scripts/cleanup_agile_directory.py [--dry-run]

Author: AI Development Agent
Created: 2025-10-10
"""

import sys
from pathlib import Path
import shutil
from datetime import datetime
from typing import Dict, List, Set

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class AgileDirectoryCleanup:
    """Clean up and organize agile directory."""
    
    # Files to DELETE (obsolete/redundant)
    OBSOLETE_FILES = [
        'AGILE_IMPLEMENTATION_SUMMARY.md',  # Obsolete summary
        'ORGANIZATION_SUMMARY.md',  # Old organization info
        'SPEED_OPTIMIZATION_SUMMARY.md',  # Historical
        'CURRENT_SPRINT_ACHIEVEMENTS_SUMMARY.md',  # Move to achievements/
        'US-DOC-001_COMPLETION_SUMMARY.md',  # Old completion
        'velocity_tracking_current.md',  # Duplicate of metrics/velocity_tracking.md
    ]
    
    # Files to MOVE to subdirectories
    FILE_MOVES = {
        # To overview/
        'AGILE_OVERVIEW.md': 'overview/AGILE_OVERVIEW.md',
        'COMPREHENSIVE_AGILE_MANUAL.md': 'overview/COMPREHENSIVE_AGILE_MANUAL.md',
        'HOW_TO_WORK_WITH_AGILE.md': 'overview/HOW_TO_WORK_WITH_AGILE.md',
        
        # To frameworks/
        'SPEED_OPTIMIZED_AGILE_FRAMEWORK.md': 'frameworks/SPEED_OPTIMIZED_AGILE_FRAMEWORK.md',
        
        # To teams/
        'EXPERT_TEAM_STAFFING_FRAMEWORK.md': 'teams/EXPERT_TEAM_STAFFING_FRAMEWORK.md',
        
        # To automation/
        'AUTOMATION_SYSTEM_OVERVIEW.md': 'automation/AUTOMATION_SYSTEM_OVERVIEW.md',
        
        # To validation/
        'AUTOMATIC_ARTIFACT_MAINTENANCE_VALIDATION.md': 'validation/AUTOMATIC_ARTIFACT_MAINTENANCE_VALIDATION.md',
    }
    
    def __init__(self, dry_run=False):
        self.agile_dir = project_root / "docs" / "agile"
        self.dry_run = dry_run
        self.deleted_files = []
        self.moved_files = []
        
    def cleanup(self):
        """Execute full cleanup."""
        
        print("[INFO] Agile Directory Cleanup")
        print("=" * 60)
        
        if self.dry_run:
            print("[DRY RUN] No actual changes will be made\n")
        
        # Step 1: Delete obsolete files
        self._delete_obsolete_files()
        
        # Step 2: Move files to subdirectories
        self._move_files_to_subdirs()
        
        # Step 3: Update README
        self._update_readme()
        
        # Step 4: Update META_DOCUMENTATION_INDEX
        self._update_meta_index()
        
        # Generate summary
        self._generate_summary()
    
    def _delete_obsolete_files(self):
        """Delete obsolete/redundant files."""
        
        print("\n[PHASE 1] Deleting obsolete files...")
        print("-" * 60)
        
        for filename in self.OBSOLETE_FILES:
            file_path = self.agile_dir / filename
            
            if file_path.exists():
                if not self.dry_run:
                    file_path.unlink()
                self.deleted_files.append(filename)
                print(f"  [DELETE] {filename}")
            else:
                print(f"  [SKIP] {filename} (not found)")
    
    def _move_files_to_subdirs(self):
        """Move files to appropriate subdirectories."""
        
        print("\n[PHASE 2] Moving files to subdirectories...")
        print("-" * 60)
        
        for source_name, target_rel in self.FILE_MOVES.items():
            source_path = self.agile_dir / source_name
            target_path = self.agile_dir / target_rel
            
            if source_path.exists():
                if not self.dry_run:
                    # Create target directory if needed
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source_path), str(target_path))
                
                self.moved_files.append((source_name, target_rel))
                print(f"  [MOVE] {source_name} -> {target_rel}")
            else:
                print(f"  [SKIP] {source_name} (not found)")
    
    def _update_readme(self):
        """Update main README with new structure."""
        
        print("\n[PHASE 3] Updating README...")
        print("-" * 60)
        
        readme_path = self.agile_dir / "README.md"
        
        readme_content = f"""# Agile Documentation

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: ✅ Organized and Clean

## Quick Navigation

### Active Work
- **Daily Standup**: [`daily_standup.md`](./daily_standup.md)
- **Current Sprint**: [`sprints/current_sprint.md`](./sprints/current_sprint.md)

### Core Documentation
- **Overview**: [`overview/`](./overview/) - System overview and manuals
- **Core Rules**: [`core/`](./core/) - Agile rules and workflows
- **Catalogs**: [`catalogs/`](./catalogs/) - Tracking catalogs (stories, epics, tasks)

### Sprint Work
- **Sprints**: [`sprints/`](./sprints/) - All sprint documentation
- **User Stories**: [`user_stories/`](./user_stories/) - Cross-sprint user stories
- **Epics**: [`epics/`](./epics/) - Epic definitions
- **Backlog**: [`backlog/`](./backlog/) - Product backlog items

### Planning & Execution
- **Planning**: [`planning/`](./planning/) - Planning artifacts
- **Execution**: [`execution/`](./execution/) - Execution tracking
- **Metrics**: [`metrics/`](./metrics/) - Metrics and velocity tracking

### Team & Process
- **Teams**: [`teams/`](./teams/) - Team structures and staffing
- **Frameworks**: [`frameworks/`](./frameworks/) - Agile frameworks
- **Retrospectives**: [`retrospectives/`](./retrospectives/) - Cross-sprint retrospectives
- **Lessons Learned**: [`lessons_learned/`](./lessons_learned/) - Lessons and improvements

### System Support
- **Templates**: [`templates/`](./templates/) - Templates for artifacts
- **Automation**: [`automation/`](./automation/) - Automation systems
- **Validation**: [`validation/`](./validation/) - Validation reports
- **Analysis**: [`analysis/`](./analysis/) - Analysis and strategy

### Tracking
- **Achievements**: [`achievements/`](./achievements/) - Achievement tracking
- **Health**: [`health/`](./health/) - Project health assessments
- **Compliance**: [`compliance/`](./compliance/) - Compliance audits

## Organization Standards
- **Sprint Organization**: [`sprints/SPRINT_ORGANIZATION_STANDARD.md`](./sprints/SPRINT_ORGANIZATION_STANDARD.md)
- **Agile Directory Organization**: [`AGILE_DIRECTORY_ORGANIZATION_STANDARD.md`](./AGILE_DIRECTORY_ORGANIZATION_STANDARD.md)

## Key Principles
1. **Clean Root**: Only README.md and daily_standup.md in root
2. **Organized Subdirectories**: Everything in its proper place
3. **No Backup Files**: Use git history, not .backup_* files
4. **Link Integrity**: Automated link healing for file moves
5. **Current Only**: Remove obsolete/historical noise

## Getting Started
1. Check [`daily_standup.md`](./daily_standup.md) for today's focus
2. Review [`sprints/current_sprint.md`](./sprints/current_sprint.md) for active sprint
3. Check [`catalogs/USER_STORY_CATALOG.md`](./catalogs/USER_STORY_CATALOG.md) for stories
4. Review [`core/agile_cursor_rules.md`](./core/agile_cursor_rules.md) for commands

## Maintenance
- Run `python scripts/cleanup_agile_directory.py` for cleanup
- Run `python scripts/link_healing_system.py` for link validation
- Run `python scripts/organize_sprints_directory.py` for sprint organization

Last cleanup: {datetime.now().strftime('%Y-%m-%d')}
"""
        
        if not self.dry_run:
            readme_path.write_text(readme_content, encoding='utf-8')
        
        print(f"  [UPDATE] README.md")
    
    def _update_meta_index(self):
        """Update META_DOCUMENTATION_INDEX with current structure."""
        
        print("\n[PHASE 4] Updating META_DOCUMENTATION_INDEX...")
        print("-" * 60)
        
        index_content = f"""# Meta-Documentation Index

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Purpose**: Master index of agile documentation
**Status**: ✅ Current and Organized

## Directory Structure

### Core Documentation (`core/`)
- `agile_cursor_rules.md` - Cursor agile commands and rules
- `agile_meeting_rules.md` - Meeting rules and guidelines
- `agile_workflow.md` - Agile workflow documentation
- `AGILE_COORDINATION_SYSTEM.md` - Coordination system
- `AGILE_KEYWORD_SYSTEM.md` - Keyword detection system
- `definition_of_done.md` - Definition of done

### Catalogs (`catalogs/`)
- `USER_STORY_CATALOG.md` - Complete user story index
- `EPIC_CATALOG.md` - Epic tracking catalog  
- `EPIC_OVERVIEW.md` - Epic overview and status
- `TASK_CATALOG.md` - Task tracking catalog
- `CURRENT_BACKLOG.md` - Current backlog status
- `SPRINT_SUMMARY.md` - Cross-sprint summary
- `CROSS_SPRINT_TRACKING.md` - Cross-sprint tracking

### Sprint Documentation (`sprints/`)
- `current_sprint.md` - Active sprint dashboard
- `README.md` - Sprint system overview
- `SPRINT_ORGANIZATION_STANDARD.md` - Organization standards
- `sprint_0/` through `sprint_6/` - Individual sprint directories
- `templates/` - Sprint templates

### Overview (`overview/`)
- `AGILE_OVERVIEW.md` - High-level agile overview
- `COMPREHENSIVE_AGILE_MANUAL.md` - Complete agile manual
- `HOW_TO_WORK_WITH_AGILE.md` - User guide for agile system

### Frameworks (`frameworks/`)
- `SPEED_OPTIMIZED_AGILE_FRAMEWORK.md` - Speed-optimized framework
- `TEAM_SYNERGY_EXCELLENCE_FRAMEWORK.md` - Team synergy framework

### Teams (`teams/`)
- `EXPERT_TEAM_STAFFING_FRAMEWORK.md` - Team staffing framework

### Automation (`automation/`)
- `AUTOMATION_SYSTEM_OVERVIEW.md` - Automation system overview
- `automation_framework.md` - Automation framework

### Validation (`validation/`)
- `AUTOMATIC_ARTIFACT_MAINTENANCE_VALIDATION.md` - Artifact validation
- `hilbert_consistency_report.md` - Consistency validation

### Metrics (`metrics/`)
- `metrics_dashboard.md` - Metrics dashboard
- `velocity_tracking.md` - Velocity tracking
- `cross_sprint_velocity_analysis.md` - Velocity analysis
- `performance_indicators.md` - Performance indicators
- `quality_gates.md` - Quality gates

### Analysis (`analysis/`)
- `LINK_ANALYSIS_REPORT.md` - Link integrity analysis
- `LINK_HEALING_STRATEGY.md` - Link healing strategy
- `NAMING_CONVENTION_CLEANUP_PLAN.md` - Naming conventions

### Achievements (`achievements/`)
- `SYSTEMATIC_EXCELLENCE_ACHIEVEMENTS.md` - Achievement tracking
- `UNIVERSAL_COMPOSITION_LAYER_LAUNCH.md` - Launch achievements

## Index Maintenance
- **Last Cleanup**: {datetime.now().strftime('%Y-%m-%d')}
- **Next Review**: Continuous (as files change)
- **Maintenance Script**: `scripts/cleanup_agile_directory.py`

## Quality Standards
- ✅ Clean root directory
- ✅ Organized subdirectories
- ✅ No backup files
- ✅ Link integrity maintained
- ✅ Current documentation only
"""
        
        index_path = self.agile_dir / "META_DOCUMENTATION_INDEX.md"
        
        if not self.dry_run:
            index_path.write_text(index_content, encoding='utf-8')
        
        print(f"  [UPDATE] META_DOCUMENTATION_INDEX.md")
    
    def _generate_summary(self):
        """Generate cleanup summary."""
        
        print("\n" + "=" * 60)
        print("CLEANUP SUMMARY")
        print("=" * 60)
        
        print(f"\n[SUMMARY]")
        print(f"  Files deleted: {len(self.deleted_files)}")
        print(f"  Files moved: {len(self.moved_files)}")
        print(f"  Dry run mode: {self.dry_run}")
        
        if self.deleted_files:
            print(f"\n[DELETED FILES]")
            for filename in self.deleted_files:
                print(f"  - {filename}")
        
        if self.moved_files:
            print(f"\n[MOVED FILES]")
            for source, target in self.moved_files:
                print(f"  - {source} -> {target}")
        
        print("\n" + "=" * 60)
        
        if not self.dry_run:
            print("[OK] Agile directory cleanup complete!")
            print("\n[NEXT STEPS]")
            print("  1. Run: python scripts/link_healing_system.py")
            print("  2. Review: docs/agile/README.md")
            print("  3. Review: docs/agile/META_DOCUMENTATION_INDEX.md")
        else:
            print("[DRY RUN] Review changes above, then run without --dry-run")
        
        print("=" * 60)


def main():
    """Main entry point."""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean up and organize agile directory"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    cleanup = AgileDirectoryCleanup(dry_run=args.dry_run)
    cleanup.cleanup()


if __name__ == "__main__":
    main()

