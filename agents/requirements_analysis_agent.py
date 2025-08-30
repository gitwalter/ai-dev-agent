"""
Requirements Analysis Agent

This agent specializes in analyzing user requirements and breaking down complex
development tasks into manageable components with clear acceptance criteria.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig
import json
import re

class RequirementsAnalysisAgent(BaseAgent):
    """
    Agent specialized in requirements analysis and task breakdown.
    """
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate that the task is appropriate for requirements analysis."""
        required_fields = ['description', 'context']
        return all(field in task for field in required_fields)
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute requirements analysis task.
        
        Args:
            task: Task containing description and context
            
        Returns:
            Analysis results with breakdown and recommendations
        """
        try:
            # Get optimized prompt for requirements analysis
            prompt = self.get_optimized_prompt(
                "requirements_analysis_template",
                {
                    'description': task['description'],
                    'context': task['context'],
                    'user_id': task.get('user_id', 'default')
                }
            )
            
            # Prepare the analysis request
            analysis_request = {
                'description': task['description'],
                'context': task['context'],
                'requirements': task.get('requirements', []),
                'constraints': task.get('constraints', []),
                'stakeholders': task.get('stakeholders', [])
            }
            
            # Generate analysis using LLM
            if self.llm_model:
                response = await self._generate_analysis(prompt, analysis_request)
            else:
                response = self._fallback_analysis(analysis_request)
            
            # Process and structure the response
            structured_result = self._structure_analysis_result(response, analysis_request)
            
            return {
                'success': True,
                'analysis': structured_result,
                'confidence': 0.85,
                'quality_score': 0.9,
                'recommendations': structured_result.get('recommendations', []),
                'user_stories': structured_result.get('user_stories', []),
                'technical_requirements': structured_result.get('technical_requirements', []),
                'risks': structured_result.get('risks', []),
                'dependencies': structured_result.get('dependencies', [])
            }
            
        except Exception as e:
            self.logger.error(f"Requirements analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'confidence': 0.0,
                'quality_score': 0.0
            }
    
    async def _generate_analysis(self, prompt: str, analysis_request: Dict[str, Any]) -> str:
        """Generate analysis using LLM."""
        try:
            # Prepare the full prompt with context
            full_prompt = f"""
{prompt}

**Task Description:**
{analysis_request['description']}

**Context:**
{analysis_request['context']}

**Requirements:**
{json.dumps(analysis_request.get('requirements', []), indent=2)}

**Constraints:**
{json.dumps(analysis_request.get('constraints', []), indent=2)}

**Stakeholders:**
{json.dumps(analysis_request.get('stakeholders', []), indent=2)}

Please provide a comprehensive requirements analysis including:
1. User stories with acceptance criteria
2. Technical requirements
3. Dependencies and risks
4. Implementation recommendations
5. Success metrics

Format the response as structured JSON.
"""
            
            # Generate response using LLM
            response = await self.llm_model.ainvoke(full_prompt)
            return response.content
            
        except Exception as e:
            self.logger.error(f"LLM analysis generation failed: {e}")
            raise
    
    def _fallback_analysis(self, analysis_request: Dict[str, Any]) -> str:
        """Fallback analysis when LLM is not available."""
        description = analysis_request['description']
        context = analysis_request['context']
        
        # Basic keyword extraction
        keywords = self._extract_keywords(description)
        
        # Generate basic user stories
        user_stories = self._generate_basic_user_stories(description, keywords)
        
        # Generate technical requirements
        technical_requirements = self._generate_technical_requirements(description, keywords)
        
        return json.dumps({
            'user_stories': user_stories,
            'technical_requirements': technical_requirements,
            'risks': ['Limited analysis due to fallback mode'],
            'dependencies': ['Core system components'],
            'recommendations': ['Implement comprehensive requirements gathering process']
        }, indent=2)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key technical and domain keywords from text."""
        # Simple keyword extraction - can be enhanced with NLP
        keywords = []
        
        # Technical keywords
        tech_keywords = ['api', 'database', 'web', 'mobile', 'cloud', 'security', 'performance', 'scalability']
        for keyword in tech_keywords:
            if keyword.lower() in text.lower():
                keywords.append(keyword)
        
        # Domain keywords
        domain_keywords = ['user', 'data', 'system', 'feature', 'function', 'process', 'workflow']
        for keyword in domain_keywords:
            if keyword.lower() in text.lower():
                keywords.append(keyword)
        
        return list(set(keywords))
    
    def _generate_basic_user_stories(self, description: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Generate basic user stories from description."""
        stories = []
        
        # Extract potential user actions
        action_patterns = [
            r'user\s+can\s+(\w+)',
            r'(\w+)\s+feature',
            r'(\w+)\s+functionality'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, description.lower())
            for match in matches:
                stories.append({
                    'id': f'US-{len(stories) + 1:03d}',
                    'title': f'User can {match}',
                    'description': f'As a user, I want to {match} so that I can achieve my goals',
                    'acceptance_criteria': [
                        f'User can successfully {match}',
                        f'System responds appropriately to {match} action',
                        f'Error handling works for {match} scenarios'
                    ],
                    'priority': 'medium',
                    'story_points': 3
                })
        
        # Add a default story if none found
        if not stories:
            stories.append({
                'id': 'US-001',
                'title': 'Implement core functionality',
                'description': f'As a user, I want the system to provide {description[:50]}...',
                'acceptance_criteria': [
                    'Core functionality works as described',
                    'System is responsive and reliable',
                    'User interface is intuitive'
                ],
                'priority': 'high',
                'story_points': 5
            })
        
        return stories
    
    def _generate_technical_requirements(self, description: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Generate technical requirements from description."""
        requirements = []
        
        # Add requirements based on keywords
        if 'api' in keywords:
            requirements.append({
                'id': 'TR-001',
                'category': 'API',
                'description': 'Implement RESTful API endpoints',
                'priority': 'high',
                'complexity': 'medium'
            })
        
        if 'database' in keywords:
            requirements.append({
                'id': 'TR-002',
                'category': 'Database',
                'description': 'Design and implement database schema',
                'priority': 'high',
                'complexity': 'medium'
            })
        
        if 'security' in keywords:
            requirements.append({
                'id': 'TR-003',
                'category': 'Security',
                'description': 'Implement authentication and authorization',
                'priority': 'high',
                'complexity': 'high'
            })
        
        # Add default requirements
        if not requirements:
            requirements.extend([
                {
                    'id': 'TR-001',
                    'category': 'Core',
                    'description': 'Implement core system functionality',
                    'priority': 'high',
                    'complexity': 'medium'
                },
                {
                    'id': 'TR-002',
                    'category': 'Testing',
                    'description': 'Implement comprehensive testing',
                    'priority': 'medium',
                    'complexity': 'medium'
                }
            ])
        
        return requirements
    
    def _structure_analysis_result(self, response: str, original_request: Dict[str, Any]) -> Dict[str, Any]:
        """Structure the analysis result into a consistent format."""
        try:
            # Try to parse as JSON
            if response.strip().startswith('{'):
                parsed = json.loads(response)
                return parsed
            else:
                # Parse structured text response
                return self._parse_text_response(response)
        except json.JSONDecodeError:
            # Fallback to text parsing
            return self._parse_text_response(response)
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse text response into structured format."""
        sections = {
            'user_stories': [],
            'technical_requirements': [],
            'risks': [],
            'dependencies': [],
            'recommendations': []
        }
        
        # Simple text parsing - can be enhanced
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if 'user story' in line.lower() or 'story' in line.lower():
                current_section = 'user_stories'
            elif 'technical' in line.lower() or 'requirement' in line.lower():
                current_section = 'technical_requirements'
            elif 'risk' in line.lower():
                current_section = 'risks'
            elif 'dependency' in line.lower():
                current_section = 'dependencies'
            elif 'recommendation' in line.lower():
                current_section = 'recommendations'
            elif current_section and line.startswith('-'):
                # Add item to current section
                sections[current_section].append(line[1:].strip())
        
        return sections
