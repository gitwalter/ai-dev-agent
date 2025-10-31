"""
Knowledge Source Manager
========================

Manages different categories of knowledge sources for RAG-enhanced development:
- Architecture documents
- Agile management documents (sprints, user stories)
- Coding guidelines
- Framework documentation
- Custom documents and websites

Provides specialized retrieval tools for each category.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeSource:
    """Represents a knowledge source."""
    source: str
    category: str
    source_type: str  # 'file', 'url', 'directory'
    document_count: int = 0
    added_at: datetime = field(default_factory=datetime.now)
    used_count: int = 0
    last_used: Optional[datetime] = None


class KnowledgeSourceManager:
    """
    Manage active knowledge sources for development workflow.
    
    Features:
    - Categorize documents by type (architecture, agile, coding, etc.)
    - Create specialized retrieval tools per category
    - Track usage statistics
    - Dynamic document loading
    """
    
    def __init__(self, context_engine):
        """
        Initialize knowledge source manager.
        
        Args:
            context_engine: ContextEngine for RAG operations
        """
        self.context_engine = context_engine
        self.active_sources: Dict[str, List[KnowledgeSource]] = {
            "architecture": [],
            "agile": [],
            "coding_guidelines": [],
            "frameworks": [],
            "custom": []
        }
        
        logger.info("✅ KnowledgeSourceManager initialized")
    
    async def add_source(
        self, 
        category: str, 
        source: str, 
        source_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Add a knowledge source to active set.
        
        Args:
            category: Category (architecture, agile, coding_guidelines, frameworks, custom)
            source: Path or URL to document
            source_type: Type of source ('file', 'url', 'directory', 'auto')
            
        Returns:
            Dict with status and document count
        """
        logger.info(f"📚 Adding {category} source: {source}")
        
        # Auto-detect source type
        if source_type == "auto":
            source_type = self._detect_source_type(source)
        
        # Load documents
        try:
            documents = await self._load_source(source, source_type)
            
            # Add to vector store
            await self.context_engine.add_documents(documents)
            
            # Track as active source
            knowledge_source = KnowledgeSource(
                source=source,
                category=category,
                source_type=source_type,
                document_count=len(documents)
            )
            
            self.active_sources[category].append(knowledge_source)
            
            logger.info(f"✅ Added {len(documents)} documents from {source}")
            
            return {
                "status": "success",
                "source": source,
                "category": category,
                "document_count": len(documents)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to add source {source}: {e}")
            return {
                "status": "error",
                "source": source,
                "error": str(e)
            }
    
    def _detect_source_type(self, source: str) -> str:
        """Auto-detect source type."""
        if source.startswith("http://") or source.startswith("https://"):
            return "url"
        elif Path(source).is_dir():
            return "directory"
        elif Path(source).is_file():
            return "file"
        else:
            return "unknown"
    
    async def _load_source(self, source: str, source_type: str) -> List[Any]:
        """Load documents from source."""
        from utils.rag.document_loader import DocumentLoader
        
        loader = DocumentLoader()
        
        if source_type == "url":
            return await loader.load_from_url(source)
        elif source_type == "file":
            return await loader.load_file(source)
        elif source_type == "directory":
            return await loader.load_directory(source)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    def create_specialized_retrieval_tools(self) -> List:
        """
        Create specialized retrieval tools for each document category.
        
        Returns:
            List of LangChain tools for category-specific retrieval
        """
        tools = []
        
        # Tool 1: Architecture Documents
        if self.active_sources["architecture"]:
            architecture_tool = create_retriever_tool(
                self.context_engine.vector_store.as_retriever(
                    search_kwargs={"k": 5, "filter": {"category": "architecture"}}
                ),
                "retrieve_architecture_docs",
                "Search and return architectural guidelines, design patterns, and system architecture documents. "
                "Use for questions about system design, architectural decisions, and design patterns."
            )
            tools.append(architecture_tool)
            logger.info("✅ Created architecture retrieval tool")
        
        # Tool 2: Agile Documents (User Stories, Sprints)
        if self.active_sources["agile"]:
            agile_tool = create_retriever_tool(
                self.context_engine.vector_store.as_retriever(
                    search_kwargs={"k": 5, "filter": {"category": "agile"}}
                ),
                "retrieve_agile_docs",
                "Search and return agile artifacts like user stories, acceptance criteria, sprint plans, and backlog items. "
                "Use to understand requirements, sprint goals, and acceptance criteria."
            )
            tools.append(agile_tool)
            logger.info("✅ Created agile retrieval tool")
        
        # Tool 3: Coding Guidelines
        if self.active_sources["coding_guidelines"]:
            coding_tool = create_retriever_tool(
                self.context_engine.vector_store.as_retriever(
                    search_kwargs={"k": 5, "filter": {"category": "coding_guidelines"}}
                ),
                "retrieve_coding_guidelines",
                "Search and return coding standards, style guides, best practices, and code review guidelines. "
                "Use to ensure code follows project conventions and quality standards."
            )
            tools.append(coding_tool)
            logger.info("✅ Created coding guidelines retrieval tool")
        
        # Tool 4: Framework Documentation
        if self.active_sources["frameworks"]:
            framework_tool = create_retriever_tool(
                self.context_engine.vector_store.as_retriever(
                    search_kwargs={"k": 5, "filter": {"category": "frameworks"}}
                ),
                "retrieve_framework_docs",
                "Search and return framework documentation (LangChain, LangGraph, FastAPI, etc.). "
                "Use to understand correct API usage, patterns, and best practices for frameworks."
            )
            tools.append(framework_tool)
            logger.info("✅ Created framework retrieval tool")
        
        # Tool 5: Custom Documents
        if self.active_sources["custom"]:
            custom_tool = create_retriever_tool(
                self.context_engine.vector_store.as_retriever(
                    search_kwargs={"k": 5, "filter": {"category": "custom"}}
                ),
                "retrieve_custom_docs",
                "Search and return custom documents and resources added for specific tasks. "
                "Use for task-specific knowledge and context."
            )
            tools.append(custom_tool)
            logger.info("✅ Created custom documents retrieval tool")
        
        logger.info(f"✅ Created {len(tools)} specialized retrieval tools")
        return tools
    
    def get_active_sources(self, category: str = None) -> List[KnowledgeSource]:
        """
        Get currently active knowledge sources.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of active knowledge sources
        """
        if category:
            return self.active_sources.get(category, [])
        
        # Return all sources
        all_sources = []
        for category_sources in self.active_sources.values():
            all_sources.extend(category_sources)
        return all_sources
    
    def mark_source_used(self, source: str):
        """Mark a source as used by an agent."""
        for category in self.active_sources:
            for src in self.active_sources[category]:
                if src.source == source:
                    src.used_count += 1
                    src.last_used = datetime.now()
                    logger.info(f"📊 Source used: {source} (total: {src.used_count})")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for all sources."""
        stats = {
            "total_sources": 0,
            "total_documents": 0,
            "by_category": {},
            "most_used": []
        }
        
        all_sources = self.get_active_sources()
        stats["total_sources"] = len(all_sources)
        stats["total_documents"] = sum(src.document_count for src in all_sources)
        
        # Stats by category
        for category, sources in self.active_sources.items():
            stats["by_category"][category] = {
                "count": len(sources),
                "documents": sum(src.document_count for src in sources)
            }
        
        # Most used sources
        sorted_sources = sorted(all_sources, key=lambda x: x.used_count, reverse=True)
        stats["most_used"] = [
            {"source": src.source, "category": src.category, "used": src.used_count}
            for src in sorted_sources[:5]
        ]
        
        return stats
    
    def load_default_project_sources(self):
        """
        Load default project documentation sources.
        
        Automatically loads:
        - Architecture documents from docs/architecture/
        - Agile documents from docs/agile/
        - Coding guidelines from docs/guides/
        """
        logger.info("📚 Loading default project sources...")
        
        default_sources = [
            ("architecture", "docs/architecture", "directory"),
            ("agile", "docs/agile", "directory"),
            ("coding_guidelines", "docs/guides", "directory"),
        ]
        
        for category, source, source_type in default_sources:
            if Path(source).exists():
                try:
                    self.add_source(category, source, source_type)
                    logger.info(f"✅ Loaded {category} from {source}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {source}: {e}")
            else:
                logger.warning(f"⚠️ Source not found: {source}")


class DocumentSelectionPrompt:
    """
    Proactive document selection - agent asks user which docs to use.
    
    This class helps agents ask users about guidelines and frameworks
    before starting work.
    """
    
    @staticmethod
    def generate_selection_prompt(task_description: str, agent_role: str) -> str:
        """
        Generate a prompt where agent asks user for document guidance.
        
        Args:
            task_description: Description of the development task
            agent_role: Role of the agent (architecture_designer, code_generator, etc.)
            
        Returns:
            Prompt text for agent to ask user
        """
        if agent_role == "architecture_designer":
            return f"""
I'm the Architecture Designer, and I'm about to design the architecture for:
"{task_description}"

Before I start, I'd like to ensure my design aligns with your project standards. 
Please help me by specifying which documents or guidelines I should follow:

📐 **Architecture Guidelines**: 
   - Do you have specific architecture documents I should reference?
   - Any architectural patterns you prefer (layered, hexagonal, microservices)?
   - Specific files: (e.g., docs/architecture/system_design.md)

🎯 **User Story/Requirements**:
   - Which user story is this for? (e.g., US-DEV-001)
   - Any specific acceptance criteria I should address?

📝 **Coding Standards**:
   - Any specific coding guidelines to follow?
   - Framework preferences? (LangChain patterns, etc.)

🌐 **External References**:
   - Any external documentation or websites to reference?
   - Framework docs? (LangChain, LangGraph, etc.)

Please specify which documents/guidelines I should use, or say "use defaults" to use standard project documentation.
"""
        
        elif agent_role == "code_generator":
            return f"""
I'm the Code Generator, and I'm about to implement:
"{task_description}"

To generate code that matches your project standards, please guide me on:

📝 **Coding Standards**:
   - Specific coding guidelines to follow? (style guides, patterns)
   - File: (e.g., docs/guides/python_standards.md)

🏗️ **Architecture Constraints**:
   - Approved architecture design to follow?
   - Any architectural boundaries or layers to respect?

🧪 **Testing Requirements**:
   - Testing guidelines? (TDD, coverage requirements)
   - Specific test patterns?

📚 **Framework Documentation**:
   - LangChain/LangGraph best practices?
   - Framework-specific patterns to follow?

🎯 **User Story Context**:
   - Which user story's acceptance criteria should I address?

Please specify guidelines, or say "use defaults" for standard project documentation.
"""
        
        elif agent_role == "code_reviewer":
            return f"""
I'm the Code Reviewer, and I'm about to review code for:
"{task_description}"

To provide a thorough review aligned with your standards, please specify:

✅ **Review Checklist**:
   - Specific code review guidelines?
   - File: (e.g., docs/guides/code_review_checklist.md)

📐 **Architecture Compliance**:
   - Architecture document to validate against?
   - Design patterns to verify?

📝 **Coding Standards**:
   - Coding style guide to enforce?
   - Quality metrics to check?

🔒 **Security Guidelines**:
   - Security checklist?
   - Vulnerability patterns to look for?

🎯 **Acceptance Criteria**:
   - User story to validate against?

Please specify review guidelines, or say "use defaults".
"""
        
        else:
            return f"""
Before I start working on: "{task_description}"

Please help me understand which documents and guidelines I should reference:

📚 **Project Documentation**:
   - Specific documents to follow?
   - Guidelines or standards?

🎯 **Requirements**:
   - User story or issue?
   - Acceptance criteria?

🌐 **External References**:
   - Websites or external docs?
   - Framework documentation?

Please specify, or say "use defaults" for standard project documentation.
"""
    
    @staticmethod
    def parse_user_response(response: str) -> Dict[str, List[str]]:
        """
        Parse user's response to extract document selections.
        
        Args:
            response: User's response text
            
        Returns:
            Dict mapping categories to document paths/URLs
        """
        selections = {
            "architecture": [],
            "agile": [],
            "coding_guidelines": [],
            "frameworks": [],
            "custom": []
        }
        
        # Simple parsing logic - can be enhanced
        lines = response.lower().split('\n')
        
        for line in lines:
            # Look for file paths
            if 'docs/architecture' in line or '.md' in line:
                # Extract path
                import re
                paths = re.findall(r'docs/[\w/]+\.md', line)
                for path in paths:
                    if 'architecture' in path:
                        selections["architecture"].append(path)
                    elif 'agile' in path:
                        selections["agile"].append(path)
                    elif 'guides' in path or 'standards' in path:
                        selections["coding_guidelines"].append(path)
            
            # Look for URLs
            if 'http' in line:
                import re
                urls = re.findall(r'https?://[^\s]+', line)
                selections["custom"].extend(urls)
            
            # Look for user story IDs
            if 'us-' in line:
                import re
                stories = re.findall(r'US-[\w-]+', line, re.IGNORECASE)
                for story in stories:
                    selections["agile"].append(f"docs/agile/sprints/sprint_*/user_stories/{story}.md")
        
        # Filter out empty categories
        return {k: v for k, v in selections.items() if v}


# Convenience function for creating the manager
def create_knowledge_source_manager(context_engine) -> KnowledgeSourceManager:
    """Create and initialize knowledge source manager."""
    manager = KnowledgeSourceManager(context_engine)
    
    # Load default project sources
    try:
        manager.load_default_project_sources()
    except Exception as e:
        logger.warning(f"⚠️ Could not load default sources: {e}")
    
    return manager

