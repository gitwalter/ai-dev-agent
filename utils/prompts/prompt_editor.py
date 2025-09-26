"""
Prompt Editor - Simple interface for the Streamlit UI
Provides basic prompt editing capabilities for the web interface.
"""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import os

class PromptEditor:
    """Simple prompt editor for Streamlit interface."""
    
    def __init__(self, prompts_dir: str = "prompts/templates"):
        """Initialize the prompt editor with prompts directory."""
        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
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


def get_prompt_editor():
    """Get prompt editor instance."""
    return PromptEditor()


def main():
    """Main function for standalone prompt editor."""
    editor = PromptEditor()
    editor.render_editor_ui()


if __name__ == "__main__":
    main()
