"""
Pydantic Migration Specialist Team Graph for LangGraph Studio.
"""

from agents.teams.pydantic_migration_specialist_team_langgraph import PydanticMigrationSpecialistTeamCoordinator

coordinator = PydanticMigrationSpecialistTeamCoordinator()
graph = coordinator.app
