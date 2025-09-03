#!/usr/bin/env python3
"""
📋 Agile Template Manager - Copy and Modify Templates for Vibe-Agile Projects
=============================================================================

This module provides systematic template copying and modification capabilities
for generating project-specific agile artifacts based on vibe context and
project requirements.

Features:
- Template discovery and validation
- Context-aware template modification
- Variable substitution with vibe context
- Project-specific artifact generation
- Template versioning and updates
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass


@dataclass
class TemplateInfo:
    """Information about an available template."""
    name: str
    path: Path
    description: str
    variables: List[str]
    category: str
    vibe_adaptable: bool = True


class AgileTemplateManager:
    """Manages agile template copying and modification for vibe-driven projects."""
    
    def __init__(self, templates_root: Path, projects_root: Path):
        self.templates_root = templates_root
        self.projects_root = projects_root
        self.available_templates = self._discover_templates()
    
    def _discover_templates(self) -> Dict[str, TemplateInfo]:
        """Discover all available agile templates."""
        templates = {}
        
        if not self.templates_root.exists():
            return templates
        
        # Scan for template files
        for template_file in self.templates_root.rglob("*.md"):
            if "template" in template_file.name.lower():
                variables = self._extract_template_variables(template_file)
                category = template_file.parent.name
                
                template_info = TemplateInfo(
                    name=template_file.stem,
                    path=template_file,
                    description=self._extract_template_description(template_file),
                    variables=variables,
                    category=category
                )
                
                templates[template_info.name] = template_info
        
        return templates
    
    def _extract_template_variables(self, template_path: Path) -> List[str]:
        """Extract variable placeholders from template content."""
        variables = set()
        
        try:
            content = template_path.read_text(encoding='utf-8')
            
            # Find variables in format {variable_name} or {{variable_name}}
            variable_patterns = [
                r'\{([^}]+)\}',      # {variable}
                r'_____',            # Fill-in blanks
                r'___',              # Short fill-ins
                r'TODO:',            # TODO items
                r'PLACEHOLDER'       # Explicit placeholders
            ]
            
            for pattern in variable_patterns:
                matches = re.findall(pattern, content)
                variables.update(matches)
                
        except Exception as e:
            print(f"Warning: Could not extract variables from {template_path}: {e}")
        
        return list(variables)
    
    def _extract_template_description(self, template_path: Path) -> str:
        """Extract description from template metadata."""
        try:
            content = template_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Look for description in first few lines
            for line in lines[:10]:
                if line.startswith('#') and len(line) > 5:
                    return line.strip('# ').strip()
            
            return f"Agile template: {template_path.name}"
            
        except Exception:
            return f"Template: {template_path.name}"
    
    def create_project_agile_structure(self, project_name: str, 
                                     vibe_context: Dict[str, Any],
                                     project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create complete agile structure for a vibe-driven project."""
        
        # Create project agile directory
        project_agile_path = self.projects_root / project_name / "agile"
        project_agile_path.mkdir(parents=True, exist_ok=True)
        
        # Prepare template variables
        template_vars = self._prepare_template_variables(
            project_name, vibe_context, project_config
        )
        
        # Copy and customize core templates
        copied_templates = {}
        
        # Essential agile templates to copy
        essential_templates = [
            'sprint_planning_template',
            'sprint_retrospective_template', 
            'sprint_review_template',
            'sprint_backlog_template',
            'daily_standup_template'
        ]
        
        for template_name in essential_templates:
            if template_name in self.available_templates:
                result = self._copy_and_customize_template(
                    template_name, project_agile_path, template_vars
                )
                copied_templates[template_name] = result
        
        # Generate project-specific artifacts
        self._generate_project_epic(project_agile_path, template_vars)
        self._generate_user_stories(project_agile_path, template_vars)
        self._generate_definition_of_done(project_agile_path, template_vars)
        
        return {
            'agile_path': str(project_agile_path),
            'templates_copied': copied_templates,
            'custom_artifacts': [
                'EPIC_OVERVIEW.md',
                'USER_STORIES.md', 
                'DEFINITION_OF_DONE.md'
            ],
            'template_variables': template_vars
        }
    
    def _prepare_template_variables(self, project_name: str,
                                  vibe_context: Dict[str, Any],
                                  project_config: Dict[str, Any]) -> Dict[str, str]:
        """Prepare variable substitutions for template customization."""
        
        now = datetime.now()
        
        # Base project variables
        variables = {
            'PROJECT_NAME': project_name,
            'PROJECT_DESCRIPTION': project_config.get('description', ''),
            'CURRENT_DATE': now.strftime('%Y-%m-%d'),
            'CURRENT_DATETIME': now.strftime('%Y-%m-%d %H:%M'),
            'SPRINT_START_DATE': now.strftime('%Y-%m-%d'),
            'SPRINT_END_DATE': (now + timedelta(days=14)).strftime('%Y-%m-%d'),
            
            # Team configuration
            'TEAM_SIZE': str(project_config.get('team_size', 3)),
            'SPRINT_LENGTH': str(project_config.get('sprint_length_days', 14)),
            'METHODOLOGY': project_config.get('methodology', 'Scrum'),
            
            # Vibe context integration
            'VIBE_INTENSITY': vibe_context.get('intensity', 'focused').title(),
            'COMMUNICATION_STYLE': vibe_context.get('communication_style', 'collaborative').title(),
            'QUALITY_FOCUS': vibe_context.get('quality_focus', 'craft').title(),
            'ENERGY_LEVEL': vibe_context.get('intensity', 'focused').title(),
            
            # Agile ceremony timing adapted to vibe
            'STANDUP_DURATION': self._get_vibe_adjusted_duration('standup', vibe_context),
            'REVIEW_DURATION': self._get_vibe_adjusted_duration('review', vibe_context),
            'RETRO_DURATION': self._get_vibe_adjusted_duration('retrospective', vibe_context),
            'PLANNING_DURATION': self._get_vibe_adjusted_duration('planning', vibe_context),
            
            # Human interaction preferences
            'INTERACTION_LEVEL': project_config.get('human_interaction_level', 'standard').title(),
            'FEEDBACK_FREQUENCY': self._get_feedback_frequency(vibe_context),
            
            # Fill common blanks
            '_____': '[TO BE FILLED]',
            '___': '[TBD]'
        }
        
        return variables
    
    def _get_vibe_adjusted_duration(self, ceremony: str, vibe_context: Dict[str, Any]) -> str:
        """Get vibe-adjusted ceremony durations."""
        
        intensity = vibe_context.get('intensity', 'focused')
        
        base_durations = {
            'standup': {'calm': '10 min', 'focused': '15 min', 'energetic': '20 min', 'passionate': '25 min', 'urgent': '30 min'},
            'review': {'calm': '45 min', 'focused': '60 min', 'energetic': '75 min', 'passionate': '90 min', 'urgent': '2 hours'},
            'retrospective': {'calm': '60 min', 'focused': '75 min', 'energetic': '90 min', 'passionate': '2 hours', 'urgent': '2.5 hours'},
            'planning': {'calm': '90 min', 'focused': '2 hours', 'energetic': '2.5 hours', 'passionate': '3 hours', 'urgent': '4 hours'}
        }
        
        return base_durations.get(ceremony, {}).get(intensity, '60 min')
    
    def _get_feedback_frequency(self, vibe_context: Dict[str, Any]) -> str:
        """Get feedback frequency based on vibe context."""
        
        intensity = vibe_context.get('intensity', 'focused')
        
        frequencies = {
            'calm': 'Weekly',
            'focused': 'Bi-weekly', 
            'energetic': 'Daily',
            'passionate': 'Twice daily',
            'urgent': 'Continuous'
        }
        
        return frequencies.get(intensity, 'Weekly')
    
    def _copy_and_customize_template(self, template_name: str, 
                                   destination_path: Path,
                                   variables: Dict[str, str]) -> Dict[str, Any]:
        """Copy and customize a specific template."""
        
        if template_name not in self.available_templates:
            return {'success': False, 'error': f'Template {template_name} not found'}
        
        template_info = self.available_templates[template_name]
        
        try:
            # Read template content
            content = template_info.path.read_text(encoding='utf-8')
            
            # Apply variable substitutions
            customized_content = self._apply_variable_substitutions(content, variables)
            
            # Determine output filename
            output_name = template_name.replace('_template', '') + '.md'
            output_path = destination_path / output_name
            
            # Write customized content
            output_path.write_text(customized_content, encoding='utf-8')
            
            return {
                'success': True,
                'template_name': template_name,
                'output_path': str(output_path),
                'variables_applied': len([v for v in variables.keys() if v in content])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to copy template {template_name}: {str(e)}'
            }
    
    def _apply_variable_substitutions(self, content: str, variables: Dict[str, str]) -> str:
        """Apply variable substitutions to template content."""
        
        result = content
        
        # Apply direct variable substitutions
        for var_name, var_value in variables.items():
            # Replace {VAR_NAME} patterns
            result = result.replace(f'{{{var_name}}}', var_value)
            result = result.replace(f'{{{{{var_name}}}}}', var_value)
            
            # Replace simple patterns
            if var_name in ['_____', '___']:
                result = result.replace(var_name, var_value)
        
        # Apply contextual improvements
        result = self._apply_vibe_context_improvements(result, variables)
        
        return result
    
    def _apply_vibe_context_improvements(self, content: str, variables: Dict[str, str]) -> str:
        """Apply vibe-specific improvements to template content."""
        
        # Add vibe-specific guidance
        vibe_guidance = f"""
## 🎭 **Vibe Context for This Sprint**

**Energy Level**: {variables.get('VIBE_INTENSITY', 'Focused')}  
**Communication Style**: {variables.get('COMMUNICATION_STYLE', 'Collaborative')}  
**Quality Focus**: {variables.get('QUALITY_FOCUS', 'Craft')}  
**Interaction Level**: {variables.get('INTERACTION_LEVEL', 'Standard')}  

**Vibe Considerations**:
- Ceremony durations are adjusted for {variables.get('VIBE_INTENSITY', 'focused')} energy
- Feedback frequency: {variables.get('FEEDBACK_FREQUENCY', 'Weekly')}
- Communication approach optimized for {variables.get('COMMUNICATION_STYLE', 'collaborative')} style

---

"""
        
        # Insert vibe guidance after the main header
        lines = content.split('\n')
        header_found = False
        insert_index = 0
        
        for i, line in enumerate(lines):
            if line.startswith('#') and not header_found:
                header_found = True
                insert_index = i + 1
                break
        
        if header_found:
            lines.insert(insert_index, vibe_guidance)
            content = '\n'.join(lines)
        
        return content
    
    def _generate_project_epic(self, project_path: Path, variables: Dict[str, str]) -> None:
        """Generate project-specific Epic overview."""
        
        epic_content = f"""# 🎯 Epic: {variables['PROJECT_NAME']}

## 📋 **Epic Overview**

**Project**: {variables['PROJECT_NAME']}  
**Created**: {variables['CURRENT_DATE']}  
**Vibe Context**: {variables['VIBE_INTENSITY']} energy, {variables['COMMUNICATION_STYLE']} communication  

## 🌟 **Epic Description**

{variables['PROJECT_DESCRIPTION']}

## 🎭 **Emotional Goals**

This epic aims to create a {variables['QUALITY_FOCUS'].lower()}-focused solution that embodies {variables['VIBE_INTENSITY'].lower()} energy and supports {variables['COMMUNICATION_STYLE'].lower()} collaboration.

## 📊 **Success Metrics**

### **Functional Success**
- [ ] Core features implemented and tested
- [ ] Quality standards met per {variables['QUALITY_FOCUS']} focus
- [ ] Performance requirements satisfied

### **Emotional Success**
- [ ] Team energy maintained at {variables['VIBE_INTENSITY'].lower()} level
- [ ] Communication effectiveness validated
- [ ] User satisfaction with emotional experience

## 🎯 **User Stories**

*See USER_STORIES.md for detailed user story breakdown*

## 📅 **Sprint Planning**

**Sprint Length**: {variables['SPRINT_LENGTH']} days  
**Team Size**: {variables['TEAM_SIZE']} members  
**Methodology**: {variables['METHODOLOGY']}  

## 🔄 **Review and Iteration**

**Review Frequency**: {variables['FEEDBACK_FREQUENCY']}  
**Interaction Level**: {variables['INTERACTION_LEVEL']}  

---

**Epic Status**: In Progress  
**Last Updated**: {variables['CURRENT_DATETIME']}  
"""
        
        epic_path = project_path / 'EPIC_OVERVIEW.md'
        epic_path.write_text(epic_content, encoding='utf-8')
    
    def _generate_user_stories(self, project_path: Path, variables: Dict[str, str]) -> None:
        """Generate project-specific user stories."""
        
        user_stories_content = f"""# 📝 User Stories: {variables['PROJECT_NAME']}

## 🎯 **User Story Overview**

**Project**: {variables['PROJECT_NAME']}  
**Created**: {variables['CURRENT_DATE']}  
**Vibe Context**: {variables['VIBE_INTENSITY']} energy, {variables['QUALITY_FOCUS']} quality focus  

## 🌟 **Core User Stories**

### **US-001: Project Foundation**
**As a** user  
**I want** {variables['PROJECT_DESCRIPTION'].lower()}  
**So that** I can achieve my goals with {variables['VIBE_INTENSITY'].lower()} satisfaction  

**Acceptance Criteria**:
- [ ] Core functionality is implemented
- [ ] User experience reflects {variables['QUALITY_FOCUS']} quality focus
- [ ] System performance meets requirements
- [ ] Emotional experience is positive and engaging

**Story Points**: 8  
**Priority**: High  
**Vibe Impact**: {variables['VIBE_INTENSITY']} energy creation  

### **US-002: User Experience Excellence**
**As a** user  
**I want** an intuitive and emotionally satisfying experience  
**So that** I feel delighted and empowered while using the system  

**Acceptance Criteria**:
- [ ] Interface is intuitive and {variables['COMMUNICATION_STYLE'].lower()}
- [ ] Emotional feedback is positive throughout user journey
- [ ] Help and support are easily accessible
- [ ] Performance is smooth and responsive

**Story Points**: 5  
**Priority**: High  
**Vibe Impact**: User delight and confidence  

### **US-003: Quality and Reliability**
**As a** user  
**I want** a reliable and high-quality system  
**So that** I can trust it for important tasks  

**Acceptance Criteria**:
- [ ] System reliability meets {variables['QUALITY_FOCUS']} standards
- [ ] Error handling is graceful and informative
- [ ] Data integrity is maintained
- [ ] Security requirements are satisfied

**Story Points**: 13  
**Priority**: High  
**Vibe Impact**: Trust and confidence building  

## 📊 **Story Metrics**

**Total Stories**: 3  
**Total Story Points**: 26  
**Estimated Sprint Capacity**: Based on {variables['TEAM_SIZE']} team members  

## 🎭 **Emotional Story Map**

### **User Delight Stories**
- US-002: User Experience Excellence

### **Trust Building Stories**  
- US-003: Quality and Reliability

### **Foundation Stories**
- US-001: Project Foundation

## 🔄 **Story Refinement**

**Refinement Schedule**: {variables['FEEDBACK_FREQUENCY']}  
**Stakeholder Input**: {variables['INTERACTION_LEVEL']} involvement  

---

**Last Updated**: {variables['CURRENT_DATETIME']}  
**Next Review**: {variables['SPRINT_START_DATE']}  
"""
        
        stories_path = project_path / 'USER_STORIES.md'
        stories_path.write_text(user_stories_content, encoding='utf-8')
    
    def _generate_definition_of_done(self, project_path: Path, variables: Dict[str, str]) -> None:
        """Generate project-specific Definition of Done."""
        
        dod_content = f"""# ✅ Definition of Done: {variables['PROJECT_NAME']}

## 🎯 **Definition of Done Overview**

**Project**: {variables['PROJECT_NAME']}  
**Quality Focus**: {variables['QUALITY_FOCUS']}  
**Vibe Context**: {variables['VIBE_INTENSITY']} energy, {variables['COMMUNICATION_STYLE']} communication  
**Created**: {variables['CURRENT_DATE']}  

## 📋 **Functional Done Criteria**

### **Code Quality**
- [ ] Code follows established coding standards
- [ ] Code is reviewed and approved by team member
- [ ] No critical linting errors or warnings
- [ ] Code is properly documented with clear comments
- [ ] Complex logic includes explanatory documentation

### **Testing Requirements**
- [ ] Unit tests written and passing (90%+ coverage)
- [ ] Integration tests completed successfully
- [ ] Manual testing performed for user scenarios
- [ ] Performance testing meets requirements
- [ ] Security testing completed (if applicable)

### **Documentation**
- [ ] User documentation updated
- [ ] Technical documentation current
- [ ] API documentation complete (if applicable)
- [ ] Installation/deployment guide updated
- [ ] Known issues documented

## 🎭 **Emotional Done Criteria**

### **User Experience**
- [ ] User experience tested with real users
- [ ] Emotional response is positive
- [ ] Interface feels intuitive and {variables['COMMUNICATION_STYLE'].lower()}
- [ ] Error messages are helpful and encouraging
- [ ] Overall experience creates {variables['VIBE_INTENSITY'].lower()} satisfaction

### **Team Satisfaction**
- [ ] Team is confident in the implementation
- [ ] Code quality meets {variables['QUALITY_FOCUS']} standards
- [ ] Technical debt is minimal and documented
- [ ] Team energy level is sustainable
- [ ] Knowledge sharing completed

## 🚀 **Deployment Done Criteria**

### **Release Readiness**
- [ ] Feature is deployable to production
- [ ] Database migrations tested (if applicable)
- [ ] Configuration changes documented
- [ ] Rollback plan prepared
- [ ] Monitoring and alerting configured

### **Stakeholder Approval**
- [ ] Product Owner acceptance obtained
- [ ] Stakeholder feedback incorporated
- [ ] Business requirements validated
- [ ] User acceptance criteria met
- [ ] Go/no-go decision documented

## 📊 **Quality Metrics**

### **{variables['QUALITY_FOCUS'].title()} Focus Metrics**
- [ ] Quality standards met for {variables['QUALITY_FOCUS']} focus
- [ ] Performance benchmarks achieved
- [ ] User satisfaction targets reached
- [ ] Technical excellence demonstrated
- [ ] Emotional goals accomplished

## 🔄 **Continuous Improvement**

### **Retrospective Input**
- [ ] Lessons learned documented
- [ ] Process improvements identified
- [ ] Team feedback collected
- [ ] Emotional journey reflected upon
- [ ] Success celebration planned

---

**Definition of Done Status**: Active  
**Last Reviewed**: {variables['CURRENT_DATE']}  
**Next Review**: {variables['SPRINT_END_DATE']}  
**Vibe Alignment**: {variables['VIBE_INTENSITY']} energy maintenance  
"""
        
        dod_path = project_path / 'DEFINITION_OF_DONE.md'
        dod_path.write_text(dod_content, encoding='utf-8')
    
    def get_available_templates(self) -> Dict[str, TemplateInfo]:
        """Get all available templates."""
        return self.available_templates
    
    def validate_template_structure(self, project_path: Path) -> Dict[str, Any]:
        """Validate that project agile structure is complete."""
        
        agile_path = project_path / 'agile'
        
        if not agile_path.exists():
            return {'valid': False, 'error': 'Agile directory not found'}
        
        # Check for essential files
        essential_files = [
            'EPIC_OVERVIEW.md',
            'USER_STORIES.md',
            'DEFINITION_OF_DONE.md',
            'sprint_planning.md',
            'sprint_retrospective.md'
        ]
        
        missing_files = []
        existing_files = []
        
        for file_name in essential_files:
            file_path = agile_path / file_name
            if file_path.exists():
                existing_files.append(file_name)
            else:
                missing_files.append(file_name)
        
        return {
            'valid': len(missing_files) == 0,
            'existing_files': existing_files,
            'missing_files': missing_files,
            'completeness_percentage': (len(existing_files) / len(essential_files)) * 100
        }


# Global instance for easy use
template_manager = None


def get_template_manager(templates_root: Path, projects_root: Path) -> AgileTemplateManager:
    """Get or create the global template manager instance."""
    global template_manager
    
    if template_manager is None:
        template_manager = AgileTemplateManager(templates_root, projects_root)
    
    return template_manager


if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    
    templates_path = Path("docs/agile/templates")
    projects_path = Path("generated_projects")
    
    manager = AgileTemplateManager(templates_path, projects_path)
    
    print(f"📋 Found {len(manager.available_templates)} templates:")
    for name, info in manager.available_templates.items():
        print(f"  - {name}: {info.description}")
        print(f"    Variables: {len(info.variables)}")
        print(f"    Category: {info.category}")
