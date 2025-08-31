"""
Prompt Editor - Simple interface for the Streamlit UI
Provides basic prompt editing capabilities for the web interface.
"""

def get_prompt_editor():
    """Get a simple prompt editor interface."""
    return SimplePromptEditor()


class SimplePromptEditor:
    """Simple prompt editor for basic UI operations."""
    
    def __init__(self):
        """Initialize the prompt editor."""
        pass
    
    def get_agent_prompts(self, agent_name: str) -> list:
        """Get prompts for a specific agent."""
        # Return sample data for demo purposes
        return [
            {
                'id': f'{agent_name}_prompt_1',
                'template': f'You are an expert {agent_name.replace("_", " ")}. Please {agent_name.replace("_", " ")} the following: {{task}}',
                'created_at': '2024-01-01',
                'updated_at': '2024-01-01',
                'usage_count': 10,
                'success_rate': 85.5,
                'variables': {'enhanced': True}
            }
        ]
    
    def update_agent_prompt(self, prompt_id: str, template: str, description: str) -> bool:
        """Update an agent prompt."""
        # Mock successful update
        return True
    
    def get_system_prompts(self, category: str = None) -> list:
        """Get system prompts."""
        prompts = [
            {
                'id': 'sys_prompt_1',
                'name': 'Workflow Orchestration',
                'category': 'workflow',
                'template': 'Orchestrate the following workflow: {workflow_description}',
                'description': 'Main workflow orchestration prompt',
                'created_at': '2024-01-01',
                'updated_at': '2024-01-01'
            },
            {
                'id': 'sys_prompt_2', 
                'name': 'Error Handling',
                'category': 'error_handling',
                'template': 'Handle the following error gracefully: {error_details}',
                'description': 'Standard error handling prompt',
                'created_at': '2024-01-01',
                'updated_at': '2024-01-01'
            }
        ]
        
        if category:
            return [p for p in prompts if p['category'] == category]
        return prompts
    
    def update_system_prompt(self, prompt_id: str, template: str, description: str) -> bool:
        """Update a system prompt."""
        return True
    
    def delete_system_prompt(self, prompt_id: str) -> bool:
        """Delete a system prompt."""
        return True
    
    def create_system_prompt(self, name: str, template: str, category: str, description: str = None) -> int:
        """Create a new system prompt."""
        return 123  # Mock ID
    
    def get_rag_documents(self, agent_name: str = None) -> list:
        """Get RAG documents."""
        docs = [
            {
                'id': 'doc_1',
                'title': 'Sample Documentation',
                'content': 'This is sample documentation content for demonstration purposes.',
                'source_type': 'manual',
                'agent_name': agent_name,
                'source_url': None,
                'file_path': None,
                'created_at': '2024-01-01',
                'updated_at': '2024-01-01',
                'tags': ['sample', 'demo']
            }
        ]
        
        if agent_name and agent_name != "All":
            return [d for d in docs if d['agent_name'] == agent_name]
        return docs
    
    def delete_rag_document(self, doc_id: str) -> bool:
        """Delete a RAG document."""
        return True
    
    def add_rag_document(self, title: str, content: str, source_type: str, 
                        source_url: str = None, agent_name: str = None, 
                        file_path: str = None, tags: list = None) -> int:
        """Add a RAG document."""
        return 456  # Mock ID
