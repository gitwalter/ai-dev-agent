"""
Prompt Editor - Enhanced interface for the Streamlit UI
Provides comprehensive prompt editing capabilities integrated with US-PE-01 PromptTemplateSystem.
"""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import US-PE-01 PromptTemplateSystem for integration
from utils.prompt_management.prompt_template_system import (
    PromptTemplateSystem, PromptTemplate, TemplateType, TemplateStatus
)
from utils.prompts.rag_processor import RAGProcessor

class PromptEditor:
    """Simple prompt editor for Streamlit interface."""
    
    # Agent name mapping: Streamlit app names → Template agent_type values
    AGENT_NAME_MAPPING = {
        'requirements_analyst': 'analyzer',
        'architecture_designer': 'architect',
        'code_generator': 'code_generator',
        'test_generator': 'test_generator',
        'code_reviewer': 'code_reviewer',
        'security_analyst': 'code_reviewer',  # Security reviews use code_reviewer
        'documentation_generator': 'documentation_writer'
    }
    
    def __init__(self, prompts_dir: str = "prompts/templates"):
        """Initialize the prompt editor with prompts directory and US-PE-01 integration."""
        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize US-PE-01 PromptTemplateSystem
        self.template_system = PromptTemplateSystem(prompts_dir)
        
        # Initialize RAG processor for document management
        self.rag_processor = RAGProcessor()
        self.rag_metadata_file = Path("data/rag_documents/metadata.json")
        
    def load_prompt(self, prompt_name: str) -> Optional[Dict]:
        """Load a prompt by name."""
        prompt_file = self.prompts_dir / f"{prompt_name}.json"
        
        if prompt_file.exists():
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading prompt '{prompt_name}': {e}")
                return None
        return None
    
    def save_prompt(self, prompt_name: str, prompt_data: Dict) -> bool:
        """Save a prompt with given name and data."""
        prompt_file = self.prompts_dir / f"{prompt_name}.json"
        
        try:
            with open(prompt_file, 'w', encoding='utf-8') as f:
                json.dump(prompt_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving prompt '{prompt_name}': {e}")
            return False
    
    def list_prompts(self) -> List[str]:
        """List all available prompts."""
        try:
            prompt_files = list(self.prompts_dir.glob("*.json"))
            return [f.stem for f in prompt_files]
        except Exception as e:
            st.error(f"Error listing prompts: {e}")
            return []
    
    def delete_prompt(self, prompt_name: str) -> bool:
        """Delete a prompt by name."""
        prompt_file = self.prompts_dir / f"{prompt_name}.json"
        
        try:
            if prompt_file.exists():
                prompt_file.unlink()
                return True
            else:
                st.warning(f"Prompt '{prompt_name}' not found")
                return False
        except Exception as e:
            st.error(f"Error deleting prompt '{prompt_name}': {e}")
            return False
    
    def render_editor_ui(self):
        """Render the prompt editor UI in Streamlit."""
        st.header("🎨 Prompt Editor")
        
        # Sidebar for prompt management
        with st.sidebar:
            st.subheader("📁 Prompt Management")
            
            # List existing prompts
            existing_prompts = self.list_prompts()
            
            if existing_prompts:
                st.write("**Existing Prompts:**")
                selected_prompt = st.selectbox(
                    "Select a prompt to edit:",
                    [""] + existing_prompts,
                    key="selected_prompt_edit"
                )
            else:
                st.info("No existing prompts found")
                selected_prompt = ""
            
            # New prompt name
            new_prompt_name = st.text_input(
                "New prompt name:",
                placeholder="my_new_prompt",
                key="new_prompt_name"
            )
        
        # Main editor area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Load existing prompt if selected
            if selected_prompt:
                prompt_data = self.load_prompt(selected_prompt)
                if prompt_data:
                    st.success(f"Loaded prompt: {selected_prompt}")
                    current_name = selected_prompt
                    current_content = prompt_data.get('content', '')
                    current_description = prompt_data.get('description', '')
                    current_tags = ', '.join(prompt_data.get('tags', []))
                    current_variables = prompt_data.get('variables', {})
                else:
                    current_name = selected_prompt
                    current_content = ''
                    current_description = ''
                    current_tags = ''
                    current_variables = {}
            else:
                current_name = new_prompt_name
                current_content = ''
                current_description = ''
                current_tags = ''
                current_variables = {}
            
            # Prompt editing form
            st.subheader("✏️ Edit Prompt")
            
            prompt_name = st.text_input(
                "Prompt Name:",
                value=current_name,
                key="prompt_name_edit"
            )
            
            prompt_description = st.text_area(
                "Description:",
                value=current_description,
                height=60,
                key="prompt_description_edit"
            )
            
            prompt_content = st.text_area(
                "Prompt Content:",
                value=current_content,
                height=300,
                placeholder="Enter your prompt here...",
                key="prompt_content_edit"
            )
            
            prompt_tags = st.text_input(
                "Tags (comma-separated):",
                value=current_tags,
                placeholder="ai, coding, helper",
                key="prompt_tags_edit"
            )
        
        with col2:
            st.subheader("💾 Actions")
            
            # Save button
            if st.button("💾 Save Prompt", type="primary"):
                if prompt_name and prompt_content:
                    prompt_data = {
                        'name': prompt_name,
                        'description': prompt_description,
                        'content': prompt_content,
                        'tags': [tag.strip() for tag in prompt_tags.split(',') if tag.strip()],
                        'variables': current_variables
                    }
                    
                    if self.save_prompt(prompt_name, prompt_data):
                        st.success(f"✅ Saved prompt: {prompt_name}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save prompt")
                else:
                    st.error("Please provide both name and content")
            
            # Delete button
            if selected_prompt and st.button("🗑️ Delete Prompt", type="secondary"):
                if st.checkbox(f"Confirm delete '{selected_prompt}'"):
                    if self.delete_prompt(selected_prompt):
                        st.success(f"✅ Deleted prompt: {selected_prompt}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete prompt")
            
            # Preview
            if prompt_content:
                st.subheader("👁️ Preview")
                with st.expander("Preview Prompt", expanded=False):
                    st.text(prompt_content[:200] + "..." if len(prompt_content) > 200 else prompt_content)
    
    # ========================================================================
    # NEW METHODS: Integration with US-PE-01 PromptTemplateSystem
    # ========================================================================
    
    def get_agent_prompts(self, agent_name: str) -> List[Dict]:
        """
        Get prompts for specific agent.
        
        Args:
            agent_name: Name of the agent to get prompts for (Streamlit app name)
            
        Returns:
            List of prompt dictionaries with template information
        """
        try:
            # Map Streamlit agent name to template agent_type
            template_agent_type = self.AGENT_NAME_MAPPING.get(agent_name, agent_name)
            
            # Get templates by the mapped agent type
            templates = self.template_system.get_templates_by_agent(
                template_agent_type, 
                status=TemplateStatus.ACTIVE
            )
            
            # Also try DRAFT status if no ACTIVE templates found
            if not templates:
                templates = self.template_system.get_templates_by_agent(
                    template_agent_type,
                    status=TemplateStatus.DRAFT
                )
            
            return self._convert_templates_to_dict(templates)
        except Exception as e:
            st.error(f"Error getting agent prompts for '{agent_name}' (mapped to '{self.AGENT_NAME_MAPPING.get(agent_name, agent_name)}'): {e}")
            return []
    
    def get_system_prompts(self, category: str = None) -> List[Dict]:
        """
        Get system prompts, optionally filtered by category.
        
        Args:
            category: Optional category filter (agent_type)
            
        Returns:
            List of system prompt dictionaries
        """
        try:
            all_templates = self.template_system.get_all_templates()
            # Filter for specialized/system templates
            system_templates = [t for t in all_templates 
                              if t.template_type == TemplateType.SPECIALIZED]
            
            # Apply category filter if provided
            if category and category != "All":
                system_templates = [t for t in system_templates 
                                  if t.agent_type == category]
            
            return self._convert_templates_to_dict(system_templates)
        except Exception as e:
            st.error(f"Error getting system prompts: {e}")
            return []
    
    def update_agent_prompt(self, prompt_id: str, template: str, reason: str) -> bool:
        """
        Update an agent prompt.
        
        Args:
            prompt_id: ID of the prompt to update
            template: New template text
            reason: Reason for the update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            existing = self.template_system.get_template(prompt_id)
            if not existing:
                st.error(f"Prompt {prompt_id} not found")
                return False
            
            # Update template with new version
            new_version = self._increment_version(existing.version)
            existing.template_text = template
            existing.version = new_version
            existing.updated_at = datetime.utcnow()
            if 'update_reason' not in existing.metadata:
                existing.metadata['update_reason'] = []
            existing.metadata['update_reason'].append({
                'date': datetime.utcnow().isoformat(),
                'reason': reason
            })
            
            # Save updated template
            self.template_system._save_template(existing)
            return True
        except Exception as e:
            st.error(f"Error updating agent prompt: {e}")
            return False
    
    def update_system_prompt(self, prompt_id: str, template: str, reason: str) -> bool:
        """
        Update a system prompt.
        
        Args:
            prompt_id: ID of the prompt to update
            template: New template text
            reason: Reason for the update
            
        Returns:
            True if successful, False otherwise
        """
        # System prompts use same update mechanism as agent prompts
        return self.update_agent_prompt(prompt_id, template, reason)
    
    def delete_system_prompt(self, prompt_id: str) -> bool:
        """
        Delete a system prompt.
        
        Args:
            prompt_id: ID of the prompt to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            existing = self.template_system.get_template(prompt_id)
            if not existing:
                st.error(f"Prompt {prompt_id} not found")
                return False
            
            # Mark as archived rather than deleting
            existing.status = TemplateStatus.ARCHIVED
            existing.updated_at = datetime.utcnow()
            self.template_system._save_template(existing)
            
            # Remove from active templates
            if prompt_id in self.template_system.templates:
                del self.template_system.templates[prompt_id]
            
            return True
        except Exception as e:
            st.error(f"Error deleting system prompt: {e}")
            return False
    
    def create_system_prompt(self, name: str, template: str, 
                           category: str, description: str = "") -> int:
        """
        Create a new system prompt.
        
        Args:
            name: Name of the prompt
            template: Template text
            category: Category/agent type
            description: Optional description
            
        Returns:
            Prompt ID (as integer hash) if successful, -1 otherwise
        """
        try:
            template_id = self.template_system.create_template(
                name=name,
                description=description,
                template_type=TemplateType.SPECIALIZED,
                agent_type=category,
                template_text=template,
                author="streamlit_user",
                tags=["system", "web_interface"]
            )
            
            # Activate the template immediately
            template_obj = self.template_system.get_template(template_id)
            if template_obj:
                template_obj.status = TemplateStatus.ACTIVE
                self.template_system._save_template(template_obj)
            
            return hash(template_id) if template_id else -1
        except Exception as e:
            st.error(f"Error creating system prompt: {e}")
            return -1
    
    # ========================================================================
    # RAG DOCUMENT MANAGEMENT METHODS
    # ========================================================================
    
    def get_rag_documents(self, agent_name: str = None) -> List[Dict]:
        """
        Get RAG documents, optionally filtered by agent.
        
        Args:
            agent_name: Optional agent name to filter by
            
        Returns:
            List of RAG document dictionaries
        """
        try:
            metadata = self._load_rag_metadata()
            documents = []
            
            for doc_name in self.rag_processor.list_documents():
                doc_meta = metadata.get(doc_name, {})
                
                # Filter by agent if specified
                if agent_name is None or doc_meta.get('agent_name') == agent_name:
                    # Get document content
                    content = self._get_document_content(doc_name)
                    
                    documents.append({
                        'id': doc_name,
                        'title': doc_meta.get('title', doc_name),
                        'content': content,
                        'source_type': doc_meta.get('source_type', 'file'),
                        'agent_name': doc_meta.get('agent_name'),
                        'source_url': doc_meta.get('source_url'),
                        'file_path': doc_meta.get('file_path'),
                        'created_at': doc_meta.get('created_at', 'Unknown'),
                        'updated_at': doc_meta.get('updated_at', 'Unknown'),
                        'tags': doc_meta.get('tags', [])
                    })
            
            return documents
        except Exception as e:
            st.error(f"Error getting RAG documents: {e}")
            return []
    
    def add_rag_document(self, title: str, content: str, source_type: str,
                        source_url: str = None, file_path: str = None,
                        agent_name: str = None, tags: List[str] = None) -> int:
        """
        Add a RAG document.
        
        Args:
            title: Document title
            content: Document content
            source_type: Type of source (url, file, etc.)
            source_url: Optional source URL
            file_path: Optional file path
            agent_name: Optional associated agent
            tags: Optional tags
            
        Returns:
            Document ID (as integer hash) if successful, -1 otherwise
        """
        try:
            doc_id = self._generate_doc_id(title)
            
            metadata = {
                'title': title,
                'source_type': source_type,
                'source_url': source_url,
                'file_path': file_path,
                'agent_name': agent_name,
                'tags': tags or [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Store document content using RAG processor
            if self.rag_processor.ingest_document(content, doc_id, metadata):
                # Update metadata registry
                self._update_rag_metadata(doc_id, metadata)
                return hash(doc_id)  # Return numeric ID for compatibility
            
            return -1
        except Exception as e:
            st.error(f"Error adding RAG document: {e}")
            return -1
    
    def delete_rag_document(self, doc_id: str) -> bool:
        """
        Delete a RAG document.
        
        Args:
            doc_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete document using RAG processor
            if self.rag_processor.delete_document(doc_id):
                # Remove from metadata registry
                metadata = self._load_rag_metadata()
                if doc_id in metadata:
                    del metadata[doc_id]
                    self._save_rag_metadata(metadata)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting RAG document: {e}")
            return False
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _convert_templates_to_dict(self, templates: List[PromptTemplate]) -> List[Dict]:
        """
        Convert PromptTemplate objects to dict format expected by UI.
        
        Args:
            templates: List of PromptTemplate objects
            
        Returns:
            List of dictionaries with template information
        """
        return [{
            'id': t.template_id,
            'template': t.template_text,
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': t.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'usage_count': t.metadata.get('usage_count', 0),
            'success_rate': t.metadata.get('success_rate', 100.0),
            'variables': t.parameters
        } for t in templates]
    
    def _increment_version(self, version: str) -> str:
        """
        Increment semantic version.
        
        Args:
            version: Current version string (e.g., "1.0.0")
            
        Returns:
            Incremented version string (e.g., "1.0.1")
        """
        try:
            parts = version.split('.')
            parts[-1] = str(int(parts[-1]) + 1)
            return '.'.join(parts)
        except Exception:
            return "1.0.1"  # Default if parsing fails
    
    def _load_rag_metadata(self) -> Dict:
        """
        Load RAG document metadata registry.
        
        Returns:
            Dictionary of document metadata
        """
        if self.rag_metadata_file.exists():
            try:
                with open(self.rag_metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.warning(f"Error loading RAG metadata: {e}")
                return {}
        return {}
    
    def _save_rag_metadata(self, metadata: Dict):
        """
        Save RAG document metadata registry.
        
        Args:
            metadata: Dictionary of document metadata
        """
        try:
            self.rag_metadata_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.rag_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Error saving RAG metadata: {e}")
    
    def _update_rag_metadata(self, doc_id: str, metadata: Dict):
        """
        Update RAG metadata registry for a specific document.
        
        Args:
            doc_id: Document ID
            metadata: Metadata dictionary for the document
        """
        all_metadata = self._load_rag_metadata()
        all_metadata[doc_id] = metadata
        self._save_rag_metadata(all_metadata)
    
    def _get_document_content(self, doc_name: str) -> str:
        """
        Get content of a RAG document.
        
        Args:
            doc_name: Document name/ID
            
        Returns:
            Document content string
        """
        try:
            doc_file = self.rag_processor.docs_dir / f"{doc_name}.txt"
            if doc_file.exists():
                with open(doc_file, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            st.warning(f"Error reading document {doc_name}: {e}")
            return ""
    
    def _generate_doc_id(self, title: str) -> str:
        """
        Generate a document ID from title.
        
        Args:
            title: Document title
            
        Returns:
            Document ID string
        """
        # Create safe filename from title
        import re
        safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', title.lower())
        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{safe_title}_{timestamp}"


def get_prompt_editor():
    """Get prompt editor instance."""
    return PromptEditor()


def main():
    """Main function for standalone prompt editor."""
    editor = PromptEditor()
    editor.render_editor_ui()


if __name__ == "__main__":
    main()
