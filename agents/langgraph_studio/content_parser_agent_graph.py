"""
Content Parser Agent Graph for LangGraph Studio.
"""

from agents.research.content_parser_agent_langgraph import ContentParserAgentCoordinator

coordinator = ContentParserAgentCoordinator()
graph = coordinator.app
