#!/usr/bin/env python3
"""
Sprint Directory Organization Script
====================================

Organizes sprint directories according to the SPRINT_ORGANIZATION_STANDARD.md.
Uses link healing system to prevent broken links during reorganization.

Features:
- Creates standard subdirectory structure
- Moves files to correct locations
- Tracks all file moves for link healing
- Validates organization after completion

Usage:
    python scripts/organize_sprints_directory.py [--dry-run]

Author: AI Development Agent
Created: 2025-10-10
"""

import sys
from pathlib import Path
import shutil
from typing import Dict, List, Tuple
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SprintDirectoryOrganizer:
    """Organize sprint directories with link healing."""
    
    STANDARD_SUBDIRS = [
        'planning',
        'execution',
        'user_stories',
        'tasks',
        'daily_standups',
        'review',
        'retrospective',
        'metrics',
        'analysis',
        'completion',
        'archive'
    ]
    
    def __init__(self, dry_run=False):
        self.sprints_dir = project_root / "docs" / "agile" / "sprints"
        self.dry_run = dry_run
        self.rename_mapping = {}  # Track file moves for link healing
        self.moves_made = []
        
    def organize_all_sprints(self):
        """Organize all sprint directories."""
        
        print("[INFO] Sprint Directory Organization")
        print("=" * 60)
        
        if self.dry_run:
            print("[DRY RUN] No actual changes will be made\n")
        
        # Find all sprint directories
        sprint_dirs = sorted([d for d in self.sprints_dir.iterdir() 
                            if d.is_dir() and d.name.startswith('sprint_')])
        
        print(f"[INFO] Found {len(sprint_dirs)} sprint directories\n")
        
        for sprint_dir in sprint_dirs:
            self._organize_sprint(sprint_dir)
        
        # Generate summary
        self._generate_summary()
        
        return self.rename_mapping
    
    def _organize_sprint(self, sprint_dir: Path):
        """Organize a single sprint directory."""
        
        sprint_name = sprint_dir.name
        print(f"\n[INFO] Organizing {sprint_name}...")
        print("-" * 60)
        
        # Step 1: Create standard subdirectories
        self._create_standard_subdirs(sprint_dir)
        
        # Step 2: Organize files in root
        self._organize_root_files(sprint_dir)
        
        # Step 3: Validate structure
        self._validate_sprint_structure(sprint_dir)
    
    def _create_standard_subdirs(self, sprint_dir: Path):
        """Create standard subdirectories if they don't exist."""
        
        created = []
        
        for subdir in self.STANDARD_SUBDIRS:
            subdir_path = sprint_dir / subdir
            if not subdir_path.exists():
                if not self.dry_run:
                    subdir_path.mkdir(parents=True, exist_ok=True)
                created.append(subdir)
        
        if created:
            print(f"[OK] Created subdirectories: {', '.join(created)}")
        else:
            print(f"[OK] All standard subdirectories exist")
    
    def _organize_root_files(self, sprint_dir: Path):
        """Organize files in sprint root according to naming patterns."""
        
        sprint_name = sprint_dir.name
        
        # Get all files in root (excluding directories and README)
        root_files = [f for f in sprint_dir.iterdir() 
                     if f.is_file() and f.name != 'README.md']
        
        if not root_files:
            print(f"[INFO] No files to organize in root")
            return
        
        print(f"[INFO] Found {len(root_files)} files in root")
        
        moves = []
        
        for file in root_files:
            target_subdir = self._determine_target_subdir(file)
            
            if target_subdir:
                target_path = sprint_dir / target_subdir / file.name
                moves.append((file, target_path, target_subdir))
        
        # Execute moves
        for source, target, subdir in moves:
            if not self.dry_run:
                if not target.parent.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.move(str(source), str(target))
                
                # Track for link healing
                self.rename_mapping[str(source.relative_to(project_root))] = \
                    str(target.relative_to(project_root))
            
            self.moves_made.append({
                'sprint': sprint_name,
                'file': source.name,
                'from': 'root',
                'to': subdir
            })
            
            print(f"  [MOVE] {source.name} -> {subdir}/")
    
    def _determine_target_subdir(self, file: Path) -> str:
        """Determine target subdirectory based on file name patterns."""
        
        filename = file.name.lower()
        
        # Planning files
        if any(x in filename for x in ['planning', 'goal', 'capacity']):
            return 'planning'
        
        # Execution files
        if any(x in filename for x in ['backlog', 'progress', 'blocker']):
            return 'execution'
        
        # Review files
        if 'review' in filename:
            return 'review'
        
        # Retrospective files
        if 'retrospective' in filename or 'retro' in filename or 'lessons' in filename:
            return 'retrospective'
        
        # Metrics files
        if 'metric' in filename or 'velocity' in filename:
            return 'metrics'
        
        # Analysis files
        if 'analysis' in filename or 'research' in filename:
            return 'analysis'
        
        # Completion/closure files
        if any(x in filename for x in ['completion', 'closure', 'final', 'status']):
            return 'completion'
        
        # Daily standup files
        if 'standup' in filename or 'daily' in filename:
            return 'daily_standups'
        
        # Archive
        if 'archive' in filename:
            return 'archive'
        
        # Default: execution for generic sprint files
        return 'execution'
    
    def _validate_sprint_structure(self, sprint_dir: Path):
        """Validate sprint has standard structure."""
        
        missing = []
        
        for subdir in self.STANDARD_SUBDIRS:
            if not (sprint_dir / subdir).exists():
                missing.append(subdir)
        
        if missing:
            print(f"[WARNING] Missing subdirectories: {', '.join(missing)}")
        else:
            print(f"[OK] Sprint structure validated")
    
    def _generate_summary(self):
        """Generate organization summary."""
        
        print("\n" + "=" * 60)
        print("ORGANIZATION SUMMARY")
        print("=" * 60)
        
        print(f"\n[SUMMARY]")
        print(f"  Total files moved: {len(self.moves_made)}")
        print(f"  Dry run mode: {self.dry_run}")
        
        if self.moves_made:
            print(f"\n[FILE MOVES]")
            by_sprint = {}
            for move in self.moves_made:
                sprint = move['sprint']
                if sprint not in by_sprint:
                    by_sprint[sprint] = []
                by_sprint[sprint].append(move)
            
            for sprint, moves in sorted(by_sprint.items()):
                print(f"\n  {sprint}: {len(moves)} files moved")
                for move in moves:
                    print(f"    {move['file']}: {move['from']} -> {move['to']}")
        
        if self.rename_mapping:
            print(f"\n[LINK HEALING]")
            print(f"  Files to heal: {len(self.rename_mapping)}")
            print(f"  Run link healing system to update references")
        
        print("\n" + "=" * 60)
        
        if not self.dry_run:
            print("[OK] Sprint directory organization complete!")
        else:
            print("[DRY RUN] Review changes above, then run without --dry-run")
        
        print("=" * 60)


def main():
    """Main entry point."""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Organize sprint directories according to standard structure"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    organizer = SprintDirectoryOrganizer(dry_run=args.dry_run)
    rename_mapping = organizer.organize_all_sprints()
    
    if not args.dry_run and rename_mapping:
        print("\n[INFO] Link healing required!")
        print("[INFO] Please run link healing system to update references:")
        print(f"[INFO]   python scripts/link_healing_system.py")


if __name__ == "__main__":
    main()

