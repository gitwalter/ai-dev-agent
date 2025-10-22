"""
Database Cleanup Specialist Team Graph for LangGraph Studio.
"""

from agents.teams.database_cleanup_specialist_team_langgraph import DatabaseCleanupSpecialistTeamCoordinator

coordinator = DatabaseCleanupSpecialistTeamCoordinator()
graph = coordinator.app
