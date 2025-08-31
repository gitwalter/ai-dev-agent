"""
Pydantic Migration Expert Team for fixing validation errors.
"""

from typing import Dict, List, Any


class PydanticMigrationExpert:
    """Expert for fixing Pydantic V2 validation issues."""
    
    def analyze_workflow_result_error(self, error_message: str) -> Dict[str, Any]:
        """Analyze WorkflowResult validation error and provide fix."""
        
        # Extract failing fields from error message
        failing_fields = []
        lines = error_message.split('\n')
        for line in lines:
            if "Extra inputs are not permitted" in line:
                parts = line.strip().split()
                if parts:
                    field_name = parts[0]
                    if field_name not in failing_fields:
                        failing_fields.append(field_name)
        
        return {
            "issue": "WorkflowResult model missing required fields",
            "failing_fields": failing_fields,
            "field_count": len(failing_fields),
            "fix_strategy": "Add missing fields to WorkflowResult model",
            "model_location": "models/responses.py",
            "recommended_action": "extend_model_fields"
        }
    
    def generate_field_definitions(self, field_names: List[str]) -> Dict[str, str]:
        """Generate Pydantic field definitions for missing fields."""
        field_definitions = {}
        
        for field_name in field_names:
            if "time" in field_name or "date" in field_name:
                field_type = "datetime"
                default = "Field(default_factory=datetime.now, description=\"Timestamp\")"
            elif "id" in field_name:
                field_type = "str" 
                default = "Field(..., description=\"Identifier\")"
            elif "files" in field_name or "results" in field_name:
                field_type = "Dict[str, Any]"
                default = "Field(default_factory=dict, description=\"File data\")"
            elif "errors" in field_name or "warnings" in field_name:
                field_type = "List[str]"
                default = "Field(default_factory=list, description=\"Messages\")"
            elif "total" in field_name or "execution_time" in field_name:
                field_type = "float"
                default = "Field(0.0, description=\"Numeric value\")"
            else:
                field_type = "Optional[Any]"
                default = "Field(None, description=\"Optional field\")"
            
            field_definitions[field_name] = f"{field_name}: {field_type} = {default}"
        
        return field_definitions


# Expert instance
pydantic_expert = PydanticMigrationExpert()
