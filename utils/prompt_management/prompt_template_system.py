"""
Prompt Template System
======================

Provides comprehensive template management, version control, and dynamic loading
capabilities for AI agent prompts. This is a core component of the prompt engineering
system for US-PE-01.

Author: AI-Dev-Agent System
Version: 1.0
Last Updated: Current Session
"""

import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Types of prompt templates."""
    SIMPLE = "simple"
    ENHANCED = "enhanced"
    CONTEXTUAL = "contextual"
    SPECIALIZED = "specialized"


class TemplateStatus(Enum):
    """Status of prompt templates."""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class PromptTemplate:
    """Represents a prompt template with metadata."""
    template_id: str
    name: str
    description: str
    template_type: TemplateType
    agent_type: str
    template_text: str
    version: str
    status: TemplateStatus
    created_at: datetime
    updated_at: datetime
    author: str
    tags: List[str] = None
    parameters: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.parameters is None:
            self.parameters = {}
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        data = asdict(self)
        data['template_type'] = self.template_type.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """Create template from dictionary."""
        data['template_type'] = TemplateType(data['template_type'])
        data['status'] = TemplateStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class PromptTemplateSystem:
    """Core prompt template management system."""
    
    def __init__(self, templates_dir: str = "prompts/templates"):
        """
        Initialize the prompt template system.
        
        Args:
            templates_dir: Directory to store template files
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, PromptTemplate] = {}
        self.template_cache: Dict[str, PromptTemplate] = {}
        self._load_templates()
    
    def create_template(self, name: str, description: str, template_type: TemplateType,
                       agent_type: str, template_text: str, author: str,
                       tags: List[str] = None, parameters: Dict[str, Any] = None) -> str:
        """
        Create a new prompt template.
        
        Args:
            name: Template name
            description: Template description
            template_type: Type of template
            agent_type: Target agent type
            template_text: Template content
            author: Template author
            tags: Template tags
            parameters: Template parameters
            
        Returns:
            str: Template ID
        """
        template_id = self._generate_template_id(name, agent_type)
        version = "1.0.0"
        
        template = PromptTemplate(
            template_id=template_id,
            name=name,
            description=description,
            template_type=template_type,
            agent_type=agent_type,
            template_text=template_text,
            version=version,
            status=TemplateStatus.DRAFT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            author=author,
            tags=tags or [],
            parameters=parameters or {}
        )
        
        # Store template
        self.templates[template_id] = template
        self._save_template(template)
        
        logger.info(f"Created template {template_id} for {agent_type}")
        return template_id
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            PromptTemplate or None if not found
        """
        # Check cache first
        if template_id in self.template_cache:
            return self.template_cache[template_id]
        
        # Check memory
        if template_id in self.templates:
            template = self.templates[template_id]
            self.template_cache[template_id] = template
            return template
        
        # Load from file
        template = self._load_template_file(template_id)
        if template:
            self.templates[template_id] = template
            self.template_cache[template_id] = template
        
        return template
    
    def get_templates_by_agent(self, agent_type: str, 
                              status: TemplateStatus = TemplateStatus.ACTIVE) -> List[PromptTemplate]:
        """
        Get all templates for an agent type.
        
        Args:
            agent_type: Agent type
            status: Template status filter
            
        Returns:
            List of templates
        """
        templates = []
        for template in self.templates.values():
            if (template.agent_type == agent_type and 
                template.status == status):
                templates.append(template)
        
        return sorted(templates, key=lambda t: t.updated_at, reverse=True)
    
    def get_all_templates(self) -> List[PromptTemplate]:
        """
        Get all templates.
        
        Returns:
            List of all templates
        """
        return list(self.templates.values())
    
    def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a template.
        
        Args:
            template_id: Template ID
            updates: Fields to update
            
        Returns:
            bool: True if updated successfully
        """
        template = self.get_template(template_id)
        if not template:
            return False
        
        # Update fields
        for field, value in updates.items():
            if hasattr(template, field):
                if field == 'template_type' and isinstance(value, str):
                    value = TemplateType(value)
                elif field == 'status' and isinstance(value, str):
                    value = TemplateStatus(value)
                elif field in ['created_at', 'updated_at'] and isinstance(value, str):
                    value = datetime.fromisoformat(value)
                
                setattr(template, field, value)
        
        # Update timestamp
        template.updated_at = datetime.utcnow()
        
        # Save updated template
        self._save_template(template)
        
        # Update cache
        self.template_cache[template_id] = template
        
        logger.info(f"Updated template {template_id}")
        return True
    
    def create_version(self, template_id: str, new_version: str, 
                      template_text: str, author: str) -> str:
        """
        Create a new version of a template.
        
        Args:
            template_id: Original template ID
            new_version: New version string
            template_text: New template text
            author: Version author
            
        Returns:
            str: New template ID
        """
        original = self.get_template(template_id)
        if not original:
            raise ValueError(f"Template {template_id} not found")
        
        # Create new template ID for version
        new_template_id = f"{template_id}_v{new_version.replace('.', '_')}"
        
        # Create new template
        new_template = PromptTemplate(
            template_id=new_template_id,
            name=f"{original.name} (v{new_version})",
            description=original.description,
            template_type=original.template_type,
            agent_type=original.agent_type,
            template_text=template_text,
            version=new_version,
            status=TemplateStatus.DRAFT,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            author=author,
            tags=original.tags.copy(),
            parameters=original.parameters.copy(),
            metadata=original.metadata.copy()
        )
        
        # Store new template
        self.templates[new_template_id] = new_template
        self._save_template(new_template)
        
        logger.info(f"Created version {new_version} of template {template_id}")
        return new_template_id
    
    def render_template(self, template_id: str, context: Dict[str, Any] = None) -> str:
        """
        Render a template with context.
        
        Args:
            template_id: Template ID
            context: Context variables for template rendering
            
        Returns:
            str: Rendered template
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        context = context or {}
        
        # Simple template rendering with variable substitution
        rendered = template.template_text
        
        # Replace variables in format {{variable_name}}
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def _generate_template_id(self, name: str, agent_type: str) -> str:
        """Generate a unique template ID."""
        base = f"{agent_type}_{name.lower().replace(' ', '_')}"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{base}_{timestamp}"
    
    def _save_template(self, template: PromptTemplate):
        """Save template to file."""
        # Ensure directory exists
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        template_file = self.templates_dir / f"{template.template_id}.json"
        with open(template_file, 'w') as f:
            json.dump(template.to_dict(), f, indent=2)
    
    def _load_template_file(self, template_id: str) -> Optional[PromptTemplate]:
        """Load template from file."""
        template_file = self.templates_dir / f"{template_id}.json"
        if not template_file.exists():
            return None
        
        try:
            with open(template_file, 'r') as f:
                data = json.load(f)
            return PromptTemplate.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load template {template_id}: {e}")
            return None
    
    def _load_templates(self):
        """Load all templates from files."""
        for template_file in self.templates_dir.glob("*.json"):
            try:
                template_id = template_file.stem
                template = self._load_template_file(template_id)
                if template:
                    self.templates[template_id] = template
            except Exception as e:
                logger.error(f"Failed to load template from {template_file}: {e}")


# Global template system instance
_template_system = None

def get_template_system() -> PromptTemplateSystem:
    """Get the global template system instance."""
    global _template_system
    if _template_system is None:
        _template_system = PromptTemplateSystem()
    return _template_system
