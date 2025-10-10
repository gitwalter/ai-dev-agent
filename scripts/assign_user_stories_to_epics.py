#!/usr/bin/env python3
"""
User Story Epic Assignment Script
Systematically assigns all user stories to appropriate epics based on content analysis.

Created: 2025-09-05
Last Updated: 2025-09-05
Temporal Authority: Local Machine (Always Trusted)
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class UserStoryEpicAssigner:
    """Systematically assign user stories to epics based on content analysis."""
    
    def __init__(self):
        self.epic_mappings = {
            # EPIC-0: Development Excellence (Foundation)
            "EPIC-0": {
                "keywords": ["test", "testing", "quality", "code quality", "refactor", "architecture", 
                           "clean code", "technical debt", "foundation", "infrastructure", "build", 
                           "deployment", "CI/CD", "automation pipeline", "development excellence"],
                "patterns": [r"US-000", r"test.*fail", r"refactor", r"architecture", r"clean.*code", 
                           r"technical.*debt", r"build.*system", r"deployment", r"infrastructure"]
            },
            
            # EPIC-2: Intelligent Prompt Engineering  
            "EPIC-2": {
                "keywords": ["prompt", "engineering", "optimization", "template", "LLM", "model",
                           "AI interaction", "prompt database", "prompt management", "prompt optimization"],
                "patterns": [r"prompt", r"template", r"LLM", r"model.*optimization", r"AI.*interaction"]
            },
            
            # EPIC-3: Agent Development & Optimization
            "EPIC-3": {
                "keywords": ["agent", "swarm", "agent framework", "agent development", "AI agent",
                           "multi-agent", "agent coordination", "agent architecture", "agent system"],
                "patterns": [r"agent(?!.*logging)", r"swarm", r"multi.*agent", r"agent.*framework", 
                           r"agent.*development", r"agent.*coordination"]
            },
            
            # EPIC-4: Integrated System Intelligence & Organic Metabolic Architecture
            "EPIC-4": {
                "keywords": ["intelligence", "cognitive", "learning", "ontological", "reasoning", 
                           "knowledge", "context", "decision making", "pattern recognition",
                           "self-optimization", "metabolic", "health monitoring", "system vitality",
                           "agent logging", "agent ontological", "cognitive architecture"],
                "patterns": [r"intelligence", r"cognitive", r"learning", r"ontological", r"reasoning",
                           r"knowledge", r"context.*detection", r"decision.*making", r"pattern.*recognition",
                           r"self.*optimization", r"health.*monitoring", r"agent.*logging", r"metabolic"]
            },
            
            # EPIC-6: Full Cursor Automation
            "EPIC-6": {
                "keywords": ["cursor", "automation", "workflow", "IDE", "editor", "development tools",
                           "full automation", "workflow composition", "context switching"],
                "patterns": [r"cursor", r"automation", r"workflow", r"IDE", r"editor", 
                           r"development.*tools", r"workflow.*composition"]
            },
            
            # EPIC-7: Formal Principles Excellence
            "EPIC-7": {
                "keywords": ["formal", "principles", "mathematical", "logical", "systematic", 
                           "verification", "validation", "consistency", "formal methods"],
                "patterns": [r"formal", r"principles", r"mathematical", r"logical", r"systematic",
                           r"verification", r"validation", r"consistency", r"formal.*methods"]
            },
            
            # EPIC-8: Developer Delight & Maximum Usefulness
            "EPIC-8": {
                "keywords": ["user experience", "UX", "UI", "interface", "usability", "developer experience",
                           "user interface", "dashboard", "visualization", "delight", "usefulness"],
                "patterns": [r"user.*experience", r"UX", r"UI", r"interface", r"usability", 
                           r"developer.*experience", r"dashboard", r"visualization", r"delight"]
            }
        }
        
        self.assignment_results = []
        self.project_root = Path("C:/Users/pogawal/WorkFolder/Documents/Python/ai-dev-agent")
    
    def analyze_user_story_content(self, file_path: Path) -> Tuple[str, str]:
        """Analyze user story content to determine best epic assignment."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            # Score each epic based on keyword and pattern matches
            epic_scores = {}
            
            for epic_id, criteria in self.epic_mappings.items():
                score = 0
                matches = []
                
                # Check keywords
                for keyword in criteria["keywords"]:
                    if keyword.lower() in content:
                        score += 1
                        matches.append(f"keyword: {keyword}")
                
                # Check patterns
                for pattern in criteria["patterns"]:
                    if re.search(pattern, content, re.IGNORECASE):
                        score += 2  # Patterns worth more than keywords
                        matches.append(f"pattern: {pattern}")
                
                epic_scores[epic_id] = {
                    "score": score,
                    "matches": matches
                }
            
            # Find best match
            best_epic = max(epic_scores.keys(), key=lambda x: epic_scores[x]["score"])
            best_score = epic_scores[best_epic]["score"]
            
            # If no clear match, assign to EPIC-0 (Development Excellence) as default
            if best_score == 0:
                best_epic = "EPIC-0"
                reasoning = "Default assignment (no specific epic indicators found)"
            else:
                reasoning = f"Score: {best_score}, Matches: {epic_scores[best_epic]['matches'][:3]}"
            
            return best_epic, reasoning
            
        except Exception as e:
            return "EPIC-0", f"Error reading file: {e}"
    
    def find_all_user_stories(self) -> List[Path]:
        """Find all user story files in the project."""
        user_story_files = []
        
        # Search in docs/agile directory
        agile_dir = self.project_root / "docs" / "agile"
        if agile_dir.exists():
            for file_path in agile_dir.rglob("US-*.md"):
                if file_path.is_file() and not file_path.name.endswith('.backup_20250901_090524') and not file_path.name.endswith('.backup_20250901_090525'):
                    user_story_files.append(file_path)
        
        return sorted(user_story_files)
    
    def update_user_story_epic_assignment(self, file_path: Path, epic_id: str) -> bool:
        """Update a user story file with the assigned epic."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            epic_name_map = {
                "EPIC-0": "Development Excellence",
                "EPIC-2": "Intelligent Prompt Engineering", 
                "EPIC-3": "Agent Development & Optimization",
                "EPIC-4": "Integrated System Intelligence & Organic Metabolic Architecture",
                "EPIC-6": "Full Cursor Automation",
                "EPIC-7": "Formal Principles Excellence",
                "EPIC-8": "Developer Delight & Maximum Usefulness"
            }
            
            epic_line = f"**Epic**: {epic_id} - {epic_name_map.get(epic_id, 'Unknown Epic')}"
            
            # Look for existing epic assignment and update it
            lines = content.split('\n')
            updated_lines = []
            epic_found = False
            
            for line in lines:
                if re.match(r'\*\*Epic\*\*:', line) or re.match(r'Epic:', line):
                    updated_lines.append(epic_line)
                    epic_found = True
                elif '## 🎯 **Epic Link**' in line:
                    updated_lines.append(line)
                    # Add epic line after Epic Link header if not found elsewhere
                    if not epic_found:
                        updated_lines.append(epic_line)
                        epic_found = True
                else:
                    updated_lines.append(line)
            
            # If no epic assignment found, add it after the title
            if not epic_found:
                new_lines = []
                title_found = False
                for i, line in enumerate(updated_lines):
                    new_lines.append(line)
                    if line.startswith('# ') and not title_found:
                        title_found = True
                        # Add epic line after title and separator
                        new_lines.append('')
                        new_lines.append(epic_line)
                        new_lines.append('')
                updated_lines = new_lines
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(updated_lines))
            
            return True
            
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            return False
    
    def assign_all_user_stories(self) -> Dict:
        """Assign all user stories to appropriate epics."""
        user_story_files = self.find_all_user_stories()
        
        print(f"Found {len(user_story_files)} user story files to process...")
        
        results = {
            "total_files": len(user_story_files),
            "successful_assignments": 0,
            "failed_assignments": 0,
            "assignments_by_epic": {},
            "assignment_details": []
        }
        
        for file_path in user_story_files:
            try:
                # Analyze content and determine epic
                assigned_epic, reasoning = self.analyze_user_story_content(file_path)
                
                # Update the file
                success = self.update_user_story_epic_assignment(file_path, assigned_epic)
                
                if success:
                    results["successful_assignments"] += 1
                    if assigned_epic not in results["assignments_by_epic"]:
                        results["assignments_by_epic"][assigned_epic] = []
                    results["assignments_by_epic"][assigned_epic].append(file_path.name)
                else:
                    results["failed_assignments"] += 1
                
                # Track details
                results["assignment_details"].append({
                    "file": str(file_path.relative_to(self.project_root)),
                    "assigned_epic": assigned_epic,
                    "reasoning": reasoning,
                    "success": success
                })
                
                print(f"[OK] {file_path.name} -> {assigned_epic}")
                
            except Exception as e:
                results["failed_assignments"] += 1
                print(f"[ERROR] Error processing {file_path.name}: {e}")
        
        return results

def main():
    """Main function to run the epic assignment process."""
    print("[START] Starting User Story Epic Assignment Process...")
    print("=" * 60)
    
    assigner = UserStoryEpicAssigner()
    results = assigner.assign_all_user_stories()
    
    print("\n" + "=" * 60)
    print("[RESULTS] ASSIGNMENT RESULTS:")
    print(f"Total Files Processed: {results['total_files']}")
    print(f"Successful Assignments: {results['successful_assignments']}")
    print(f"Failed Assignments: {results['failed_assignments']}")
    
    print("\n[ASSIGNMENTS] ASSIGNMENTS BY EPIC:")
    for epic_id, files in results["assignments_by_epic"].items():
        print(f"{epic_id}: {len(files)} stories")
        for file in files[:5]:  # Show first 5
            print(f"  - {file}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")
    
    # Save detailed results
    results_file = Path("epic_assignment_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n[SAVED] Detailed results saved to: {results_file}")
    print("[SUCCESS] Epic assignment process completed!")

if __name__ == "__main__":
    main()
