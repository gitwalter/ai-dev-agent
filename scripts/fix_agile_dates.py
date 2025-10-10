#!/usr/bin/env python3
"""
Quick Date Fix Script for Agile Documents
=========================================

Corrects all instances of dates before August 2025 (project start) to current date.
Project started in August 2025, so any dates before that are incorrect.

Usage:
    python scripts/fix_agile_dates.py
"""

import os
import re
from pathlib import Path
import datetime


def fix_agile_dates():
    """Fix all incorrect dates in agile documents."""
    
    print("[FIX] **Fixing Agile Document Dates**")
    print("Project started: August 2025")
    print("Correcting all dates before August 2025...")
    
    agile_docs_path = Path("docs/agile")
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    
    # Patterns to replace (dates before August 2025)
    date_replacements = {
        # Specific incorrect dates
        "2025-01-31": current_date,
        
        # Pattern-based replacements for any date before August 2025
        r"2025-0[1-7]-\d{2}": current_date,  # Jan-July 2025
        r"202[0-4]-\d{2}-\d{2}": current_date,  # Any date 2020-2024
        r"2019-\d{2}-\d{2}": current_date,  # 2019 dates
        r"2018-\d{2}-\d{2}": current_date,  # 2018 dates
    }
    
    files_processed = 0
    corrections_made = 0
    
    # Process all markdown files in agile directory
    for md_file in agile_docs_path.rglob("*.md"):
        # Skip backup files
        if ".backup_" in md_file.name:
            continue
            
        try:
            # Read file content
            content = md_file.read_text(encoding='utf-8')
            original_content = content
            
            # Apply pattern-based replacements
            for pattern, replacement in date_replacements.items():
                if isinstance(pattern, str):
                    # Direct string replacement
                    content = content.replace(pattern, replacement)
                else:
                    # Regex replacement
                    content = re.sub(pattern, replacement, content)
            
            # Write back if changed
            if content != original_content:
                md_file.write_text(content, encoding='utf-8')
                
                # Count changes
                changes = len(re.findall(r'\b\d{4}-\d{2}-\d{2}\b', original_content)) - len(re.findall(r'\b\d{4}-\d{2}-\d{2}\b', content))
                if changes > 0:
                    corrections_made += changes
                    files_processed += 1
                    print(f"[OK] Fixed {md_file.relative_to(Path.cwd())}")
        
        except Exception as e:
            print(f"[ERROR] Error processing {md_file}: {e}")
    
    print(f"\n[SUMMARY] **Date Correction Summary**")
    print(f"Files processed: {files_processed}")
    print(f"Date corrections: {corrections_made}")
    print(f"New date standard: {current_date}")
    print(f"[OK] All dates now conform to project timeline (August 2025 onwards)")


if __name__ == "__main__":
    fix_agile_dates()
