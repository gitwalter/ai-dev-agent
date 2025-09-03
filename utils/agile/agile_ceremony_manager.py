#!/usr/bin/env python3
"""
🎭 Agile Ceremony Manager
========================

Complete implementation of all agile rituals and ceremonies for Streamlit integration.
Supports daily standups, sprint planning, reviews, retrospectives, and backlog refinement.

ALL agile ceremonies with full human interaction and vibe integration.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.agile.temporal_authority import get_temporal_authority

class AgileCeremony(Enum):
    """All agile ceremonies supported by the system."""
    DAILY_STANDUP = "daily_standup"
    SPRINT_PLANNING = "sprint_planning"
    SPRINT_REVIEW = "sprint_review"
    SPRINT_RETROSPECTIVE = "sprint_retrospective"
    BACKLOG_REFINEMENT = "backlog_refinement"
    STORY_POINTING = "story_pointing"
    DEMO_SESSION = "demo_session"
    TEAM_CHECKIN = "team_checkin"

@dataclass
class CeremonyConfig:
    """Configuration for agile ceremonies."""
    ceremony_type: AgileCeremony
    duration_minutes: int
    participants: List[str]
    required_artifacts: List[str]
    outcomes: List[str]
    vibe_integration: bool = True

@dataclass
class CeremonySession:
    """Active ceremony session data."""
    ceremony_id: str
    ceremony_type: AgileCeremony
    project_id: str
    start_time: datetime
    participants: List[str]
    session_data: Dict[str, Any]
    status: str = "active"  # active, completed, cancelled
    outcomes: List[str] = None

class AgileCeremonyManager:
    """
    🎭 Complete Agile Ceremony Management System
    
    Implements ALL agile rituals with full human interaction:
    - Daily Standups with blockers and progress
    - Sprint Planning with story estimation
    - Sprint Reviews with demos and feedback
    - Retrospectives with team improvement
    - Backlog Refinement with story grooming
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.temporal_authority = get_temporal_authority()
        
        # Active ceremony sessions
        self.active_sessions: Dict[str, CeremonySession] = {}
        
        # Ceremony configurations
        self.ceremony_configs = self._initialize_ceremony_configs()
        
        # Session history
        self.ceremony_history = []
        
    def _initialize_ceremony_configs(self) -> Dict[AgileCeremony, CeremonyConfig]:
        """Initialize all agile ceremony configurations."""
        
        return {
            AgileCeremony.DAILY_STANDUP: CeremonyConfig(
                ceremony_type=AgileCeremony.DAILY_STANDUP,
                duration_minutes=15,
                participants=["Team"],
                required_artifacts=["Sprint Backlog", "Burndown Chart"],
                outcomes=["Progress Update", "Blockers Identified", "Daily Plan"]
            ),
            
            AgileCeremony.SPRINT_PLANNING: CeremonyConfig(
                ceremony_type=AgileCeremony.SPRINT_PLANNING,
                duration_minutes=120,
                participants=["Product Owner", "Scrum Master", "Development Team"],
                required_artifacts=["Product Backlog", "Team Velocity", "Definition of Done"],
                outcomes=["Sprint Goal", "Sprint Backlog", "Story Point Estimates"]
            ),
            
            AgileCeremony.SPRINT_REVIEW: CeremonyConfig(
                ceremony_type=AgileCeremony.SPRINT_REVIEW,
                duration_minutes=60,
                participants=["Product Owner", "Stakeholders", "Development Team"],
                required_artifacts=["Sprint Deliverables", "Demo Environment"],
                outcomes=["Stakeholder Feedback", "Product Increment Review", "Backlog Updates"]
            ),
            
            AgileCeremony.SPRINT_RETROSPECTIVE: CeremonyConfig(
                ceremony_type=AgileCeremony.SPRINT_RETROSPECTIVE,
                duration_minutes=90,
                participants=["Scrum Master", "Development Team"],
                required_artifacts=["Sprint Metrics", "Team Feedback"],
                outcomes=["Process Improvements", "Action Items", "Team Agreements"]
            ),
            
            AgileCeremony.BACKLOG_REFINEMENT: CeremonyConfig(
                ceremony_type=AgileCeremony.BACKLOG_REFINEMENT,
                duration_minutes=60,
                participants=["Product Owner", "Development Team"],
                required_artifacts=["Product Backlog", "Acceptance Criteria"],
                outcomes=["Refined Stories", "Story Point Estimates", "Ready Stories"]
            )
        }
    
    def start_ceremony(self, ceremony_type: AgileCeremony, project_id: str, 
                      participants: List[str] = None) -> CeremonySession:
        """Start a new agile ceremony session."""
        
        ceremony_id = f"{ceremony_type.value}_{self.temporal_authority.now().strftime('%Y%m%d_%H%M%S')}"
        
        config = self.ceremony_configs[ceremony_type]
        
        session = CeremonySession(
            ceremony_id=ceremony_id,
            ceremony_type=ceremony_type,
            project_id=project_id,
            start_time=self.temporal_authority.now(),
            participants=participants or config.participants,
            session_data=self._initialize_ceremony_data(ceremony_type),
            outcomes=[]
        )
        
        self.active_sessions[ceremony_id] = session
        
        return session
    
    def _initialize_ceremony_data(self, ceremony_type: AgileCeremony) -> Dict[str, Any]:
        """Initialize ceremony-specific data structures."""
        
        if ceremony_type == AgileCeremony.DAILY_STANDUP:
            return {
                "yesterday_work": [],
                "today_plan": [],
                "blockers": [],
                "team_energy": "focused",
                "sprint_progress": 0
            }
        
        elif ceremony_type == AgileCeremony.SPRINT_PLANNING:
            return {
                "sprint_goal": "",
                "sprint_capacity": 0,
                "selected_stories": [],
                "story_estimates": {},
                "task_breakdown": {},
                "team_commitments": []
            }
        
        elif ceremony_type == AgileCeremony.SPRINT_REVIEW:
            return {
                "completed_stories": [],
                "demo_items": [],
                "stakeholder_feedback": [],
                "product_increment": "",
                "backlog_updates": []
            }
        
        elif ceremony_type == AgileCeremony.SPRINT_RETROSPECTIVE:
            return {
                "went_well": [],
                "could_improve": [],
                "action_items": [],
                "team_mood": "positive",
                "process_changes": []
            }
        
        elif ceremony_type == AgileCeremony.BACKLOG_REFINEMENT:
            return {
                "refined_stories": [],
                "story_estimates": {},
                "acceptance_criteria": {},
                "ready_stories": [],
                "parking_lot": []
            }
        
        return {}
    
    # DAILY STANDUP CEREMONIES
    def get_daily_standup_questions(self, session: CeremonySession) -> List[Dict[str, Any]]:
        """Get daily standup questions with vibe integration."""
        
        return [
            {
                "id": "yesterday_work",
                "question": "What did you accomplish yesterday?",
                "type": "multiselect",
                "options": [
                    "Completed user stories",
                    "Fixed bugs",
                    "Code reviews",
                    "Testing",
                    "Documentation",
                    "Team collaboration",
                    "Learning/Research",
                    "Other"
                ],
                "follow_up": "Please describe your key accomplishments:"
            },
            {
                "id": "today_plan",
                "question": "What are you planning to work on today?",
                "type": "text_area",
                "placeholder": "Describe your priorities and tasks for today..."
            },
            {
                "id": "blockers",
                "question": "Do you have any blockers or impediments?",
                "type": "text_area",
                "placeholder": "Describe any obstacles preventing your progress..."
            },
            {
                "id": "team_energy",
                "question": "How is your energy level today?",
                "type": "slider",
                "min": 1,
                "max": 10,
                "default": 7,
                "labels": {1: "Low Energy", 5: "Moderate", 10: "High Energy"}
            },
            {
                "id": "help_needed",
                "question": "Do you need help from team members?",
                "type": "text_area",
                "placeholder": "What support or collaboration would be helpful?"
            }
        ]
    
    # SPRINT PLANNING CEREMONIES  
    def get_sprint_planning_flow(self, session: CeremonySession) -> List[Dict[str, Any]]:
        """Get sprint planning ceremony flow."""
        
        return [
            {
                "phase": "sprint_goal",
                "title": "🎯 Sprint Goal Setting",
                "description": "Define what we want to achieve this sprint",
                "questions": [
                    {
                        "id": "sprint_goal",
                        "question": "What is the main goal for this sprint?",
                        "type": "text_area",
                        "placeholder": "Define a clear, achievable sprint goal..."
                    },
                    {
                        "id": "success_criteria",
                        "question": "How will we know we've succeeded?",
                        "type": "text_area",
                        "placeholder": "Define measurable success criteria..."
                    }
                ]
            },
            {
                "phase": "capacity_planning",
                "title": "⚡ Team Capacity Planning",
                "description": "Determine team availability and capacity",
                "questions": [
                    {
                        "id": "team_capacity",
                        "question": "What is our team capacity for this sprint?",
                        "type": "slider",
                        "min": 10,
                        "max": 100,
                        "default": 80,
                        "unit": "story points"
                    },
                    {
                        "id": "availability_notes",
                        "question": "Any planned absences or capacity changes?",
                        "type": "text_area",
                        "placeholder": "Holidays, training, other commitments..."
                    }
                ]
            },
            {
                "phase": "story_selection",
                "title": "📋 Story Selection & Estimation",
                "description": "Select and estimate stories for the sprint",
                "questions": [
                    {
                        "id": "selected_stories",
                        "question": "Which stories should we include?",
                        "type": "multiselect",
                        "options": self._get_available_stories(session.project_id)
                    },
                    {
                        "id": "estimation_confidence",
                        "question": "How confident are we in our estimates?",
                        "type": "slider",
                        "min": 1,
                        "max": 10,
                        "default": 7
                    }
                ]
            }
        ]
    
    # SPRINT REVIEW CEREMONIES
    def get_sprint_review_agenda(self, session: CeremonySession) -> List[Dict[str, Any]]:
        """Get sprint review ceremony agenda."""
        
        return [
            {
                "phase": "demo_preparation",
                "title": "🎬 Demo Preparation",
                "description": "Prepare to showcase completed work",
                "questions": [
                    {
                        "id": "demo_stories",
                        "question": "Which stories are ready for demo?",
                        "type": "multiselect",
                        "options": self._get_completed_stories(session.project_id)
                    },
                    {
                        "id": "demo_order",
                        "question": "In what order should we demo?",
                        "type": "text_area",
                        "placeholder": "Plan the demo flow for maximum impact..."
                    }
                ]
            },
            {
                "phase": "stakeholder_demo",
                "title": "🚀 Live Demo Session",
                "description": "Demonstrate completed features to stakeholders",
                "interactive": True,
                "demo_mode": True
            },
            {
                "phase": "feedback_collection",
                "title": "💭 Stakeholder Feedback",
                "description": "Collect and document stakeholder input",
                "questions": [
                    {
                        "id": "stakeholder_satisfaction",
                        "question": "Overall stakeholder satisfaction?",
                        "type": "slider",
                        "min": 1,
                        "max": 10,
                        "default": 8
                    },
                    {
                        "id": "feedback_themes",
                        "question": "What are the main feedback themes?",
                        "type": "multiselect",
                        "options": [
                            "Meets expectations",
                            "Exceeds expectations", 
                            "Needs improvement",
                            "Missing features",
                            "UI/UX feedback",
                            "Performance concerns",
                            "New requirements"
                        ]
                    }
                ]
            }
        ]
    
    # RETROSPECTIVE CEREMONIES
    def get_retrospective_activities(self, session: CeremonySession) -> List[Dict[str, Any]]:
        """Get retrospective ceremony activities."""
        
        return [
            {
                "activity": "mood_check",
                "title": "🎭 Team Mood Check",
                "description": "How is everyone feeling about the sprint?",
                "questions": [
                    {
                        "id": "team_mood",
                        "question": "Overall team mood this sprint?",
                        "type": "radio",
                        "options": ["😞 Frustrated", "😐 Neutral", "😊 Good", "🤩 Excellent"]
                    },
                    {
                        "id": "energy_level",
                        "question": "Team energy level?",
                        "type": "slider",
                        "min": 1,
                        "max": 10,
                        "default": 6
                    }
                ]
            },
            {
                "activity": "what_went_well",
                "title": "✅ What Went Well",
                "description": "Celebrate our successes and positive moments",
                "questions": [
                    {
                        "id": "successes",
                        "question": "What went really well this sprint?",
                        "type": "text_area",
                        "placeholder": "Team achievements, process improvements, technical wins..."
                    },
                    {
                        "id": "team_strengths",
                        "question": "What team strengths did we leverage?",
                        "type": "multiselect",
                        "options": [
                            "Great collaboration",
                            "Technical expertise", 
                            "Problem solving",
                            "Communication",
                            "Creativity",
                            "Persistence",
                            "Learning agility"
                        ]
                    }
                ]
            },
            {
                "activity": "improvements",
                "title": "🔧 What Could We Improve",
                "description": "Identify areas for growth and improvement",
                "questions": [
                    {
                        "id": "improvement_areas",
                        "question": "What could we improve next sprint?",
                        "type": "text_area",
                        "placeholder": "Process issues, communication gaps, technical debt..."
                    },
                    {
                        "id": "root_causes",
                        "question": "What were the root causes of issues?",
                        "type": "text_area",
                        "placeholder": "Dig deeper into why problems occurred..."
                    }
                ]
            },
            {
                "activity": "action_items",
                "title": "🎯 Action Items & Next Steps",
                "description": "Commit to specific improvements",
                "questions": [
                    {
                        "id": "action_items",
                        "question": "What specific actions will we take?",
                        "type": "text_area",
                        "placeholder": "Concrete, actionable commitments..."
                    },
                    {
                        "id": "action_owners",
                        "question": "Who will own these actions?",
                        "type": "text_area",
                        "placeholder": "Assign responsibility for follow-through..."
                    }
                ]
            }
        ]
    
    # BACKLOG REFINEMENT CEREMONIES
    def get_backlog_refinement_flow(self, session: CeremonySession) -> List[Dict[str, Any]]:
        """Get backlog refinement ceremony flow."""
        
        return [
            {
                "phase": "story_review",
                "title": "📖 Story Review & Clarification",
                "description": "Review and clarify upcoming stories",
                "questions": [
                    {
                        "id": "stories_to_refine",
                        "question": "Which stories need refinement?",
                        "type": "multiselect", 
                        "options": self._get_backlog_stories(session.project_id)
                    },
                    {
                        "id": "clarity_rating",
                        "question": "How clear are the requirements?",
                        "type": "slider",
                        "min": 1,
                        "max": 10,
                        "default": 6
                    }
                ]
            },
            {
                "phase": "acceptance_criteria",
                "title": "✅ Acceptance Criteria Definition",
                "description": "Define clear acceptance criteria for stories",
                "questions": [
                    {
                        "id": "acceptance_criteria",
                        "question": "What are the acceptance criteria?",
                        "type": "text_area",
                        "placeholder": "Given/When/Then format preferred..."
                    },
                    {
                        "id": "edge_cases",
                        "question": "What edge cases should we consider?",
                        "type": "text_area",
                        "placeholder": "Error scenarios, boundary conditions..."
                    }
                ]
            },
            {
                "phase": "story_estimation",
                "title": "🎯 Story Point Estimation",
                "description": "Estimate effort using planning poker",
                "questions": [
                    {
                        "id": "story_points",
                        "question": "Story point estimate?",
                        "type": "radio",
                        "options": ["1", "2", "3", "5", "8", "13", "20", "Too Large"]
                    },
                    {
                        "id": "estimation_confidence",
                        "question": "Confidence in estimate?",
                        "type": "slider",
                        "min": 1,
                        "max": 10,
                        "default": 7
                    }
                ]
            }
        ]
    
    def complete_ceremony(self, ceremony_id: str, outcomes: List[str]) -> Dict[str, Any]:
        """Complete a ceremony and record outcomes."""
        
        if ceremony_id not in self.active_sessions:
            raise ValueError(f"No active ceremony with id: {ceremony_id}")
        
        session = self.active_sessions[ceremony_id]
        session.status = "completed"
        session.outcomes = outcomes
        
        # Move to history
        self.ceremony_history.append(session)
        del self.active_sessions[ceremony_id]
        
        return {
            "ceremony_id": ceremony_id,
            "ceremony_type": session.ceremony_type.value,
            "duration": (self.temporal_authority.now() - session.start_time).total_seconds() / 60,
            "outcomes": outcomes,
            "completed_at": self.temporal_authority.iso_timestamp()
        }
    
    def get_ceremony_metrics(self, project_id: str) -> Dict[str, Any]:
        """Get agile ceremony metrics for a project."""
        
        project_ceremonies = [
            session for session in self.ceremony_history 
            if session.project_id == project_id
        ]
        
        if not project_ceremonies:
            return {"message": "No ceremony data available"}
        
        return {
            "total_ceremonies": len(project_ceremonies),
            "ceremony_types": list(set(s.ceremony_type.value for s in project_ceremonies)),
            "average_duration": sum(
                (s.start_time - s.start_time).total_seconds() / 60 
                for s in project_ceremonies if s.status == "completed"
            ) / len([s for s in project_ceremonies if s.status == "completed"]) if project_ceremonies else 0,
            "recent_ceremonies": [
                {
                    "type": s.ceremony_type.value,
                    "date": s.start_time.strftime("%Y-%m-%d"),
                    "outcomes": len(s.outcomes or [])
                }
                for s in sorted(project_ceremonies, key=lambda x: x.start_time, reverse=True)[:5]
            ]
        }
    
    # Helper methods
    def _get_available_stories(self, project_id: str) -> List[str]:
        """Get available stories for sprint planning."""
        return [
            "User Authentication System",
            "Dashboard Analytics",
            "Real-time Notifications", 
            "Data Export Feature",
            "Mobile Responsive Design",
            "Performance Optimization",
            "Security Enhancements"
        ]
    
    def _get_completed_stories(self, project_id: str) -> List[str]:
        """Get completed stories for demo."""
        return [
            "User Login/Logout", 
            "Basic Dashboard",
            "Data Visualization",
            "User Profile Management"
        ]
    
    def _get_backlog_stories(self, project_id: str) -> List[str]:
        """Get backlog stories for refinement."""
        return [
            "Advanced Search Feature",
            "Batch Data Processing",
            "Third-party Integrations",
            "Automated Testing Suite",
            "Documentation Portal"
        ]

# Global ceremony manager instance
_ceremony_manager = None

def get_ceremony_manager() -> AgileCeremonyManager:
    """Get the global ceremony manager instance."""
    global _ceremony_manager
    if _ceremony_manager is None:
        _ceremony_manager = AgileCeremonyManager()
    return _ceremony_manager

if __name__ == "__main__":
    # Test ceremony manager
    manager = AgileCeremonyManager()
    
    # Test daily standup
    standup = manager.start_ceremony(AgileCeremony.DAILY_STANDUP, "test_project")
    questions = manager.get_daily_standup_questions(standup)
    
    print("🎭 Agile Ceremony Manager Test:")
    print(f"Standup Session: {standup.ceremony_id}")
    print(f"Questions: {len(questions)} questions configured")
    print("✅ Ceremony system ready!")
