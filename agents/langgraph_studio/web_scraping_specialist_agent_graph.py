"""
Web Scraping Specialist Agent Graph for LangGraph Studio.
"""

from agents.rag.web_scraping_specialist_agent_langgraph import WebScrapingSpecialistAgentCoordinator

coordinator = WebScrapingSpecialistAgentCoordinator()
graph = coordinator.app
