#!/usr/bin/env python3
"""
🎭 Enhanced Phase-Specific Dialogues for Vibe-Agile Development
===============================================================

This module provides rich, contextual, engaging dialogues for each agile phase,
adapted to the project's vibe context and emotional intelligence settings.

Each phase includes:
- Deep, thoughtful questions that matter
- Vibe-appropriate interaction styles  
- Emotional intelligence integration
- Success criteria validation
- Context-aware follow-ups
"""

from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass


class QuestionType(Enum):
    """Types of questions for adaptive UI elements."""
    SCALE = "scale"
    CHOICE = "choice"
    TEXT = "text"
    YES_NO = "yes_no"
    MULTI_SELECT = "multi_select"


@dataclass
class DialogueQuestion:
    """A structured dialogue question with metadata."""
    text: str
    question_type: QuestionType
    options: List[str] = None
    scale_range: tuple = (1, 10)
    required: bool = True
    help_text: str = None
    emotional_weight: float = 1.0  # How much this affects emotional tracking


class EnhancedPhaseDialogues:
    """Enhanced dialogues for each agile phase with deep contextual intelligence."""
    
    def get_phase_dialogues(self, phase: str, vibe_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive dialogue configuration for a specific phase."""
        
        intensity = vibe_context.get('intensity', 'focused')
        communication_style = vibe_context.get('communication_style', 'collaborative')
        quality_focus = vibe_context.get('quality_focus', 'craft')
        
        phase_methods = {
            'inception': self._get_inception_dialogues,
            'planning': self._get_planning_dialogues,
            'development': self._get_development_dialogues,
            'testing': self._get_testing_dialogues,
            'review': self._get_review_dialogues,
            'retrospective': self._get_retrospective_dialogues,
            'deployment': self._get_deployment_dialogues
        }
        
        if phase in phase_methods:
            return phase_methods[phase](intensity, communication_style, quality_focus)
        else:
            return self._get_default_dialogues(phase, intensity, communication_style, quality_focus)
    
    def _get_inception_dialogues(self, intensity: str, comm_style: str, quality_focus: str) -> Dict[str, Any]:
        """Deep, vision-setting dialogues for project inception."""
        
        questions = [
            DialogueQuestion(
                text=f"How does this project vision resonate with your {intensity} energy level?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate how well the project energy matches your personal energy",
                emotional_weight=1.5
            ),
            DialogueQuestion(
                text=f"What does {quality_focus}-focused excellence mean to you in this project?",
                question_type=QuestionType.TEXT,
                help_text="Describe what quality excellence looks like from your perspective",
                emotional_weight=1.3
            ),
            DialogueQuestion(
                text="Which emotional outcomes are most important for this project?",
                question_type=QuestionType.MULTI_SELECT,
                options=["User delight", "Team satisfaction", "Personal growth", "Innovation excitement", "Calm confidence", "Creative fulfillment"],
                help_text="Select all emotional outcomes that matter to you",
                emotional_weight=1.4
            ),
            DialogueQuestion(
                text=f"How should we adapt our {comm_style} communication approach for optimal collaboration?",
                question_type=QuestionType.TEXT,
                help_text="Share how you prefer to communicate and receive feedback",
                emotional_weight=1.2
            ),
            DialogueQuestion(
                text="What human touchpoints will be most valuable throughout development?",
                question_type=QuestionType.MULTI_SELECT,
                options=["Daily check-ins", "Weekly deep dives", "Milestone celebrations", "Problem-solving sessions", "Creative brainstorming", "Strategic reviews"],
                help_text="Choose the types of interactions that will support you best"
            ),
            DialogueQuestion(
                text="On a scale of 1-10, how confident do you feel about this project direction?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Your honest confidence level helps us calibrate our approach",
                emotional_weight=1.5
            )
        ]
        
        return {
            'phase': 'Inception',
            'description': 'Setting the vision and emotional foundation for success',
            'duration': '15-20 minutes',
            'questions': questions,
            'success_criteria': [
                'Clear emotional alignment on project vision',
                'Communication preferences understood',
                'Quality standards agreed upon',
                'Human interaction plan established'
            ],
            'follow_up_actions': [
                'Document emotional requirements',
                'Set up preferred communication channels',
                'Schedule first planning session',
                'Create project vision statement'
            ]
        }
    
    def _get_planning_dialogues(self, intensity: str, comm_style: str, quality_focus: str) -> Dict[str, Any]:
        """Strategic planning dialogues with emotional intelligence."""
        
        questions = [
            DialogueQuestion(
                text=f"Does this sprint plan honor your {intensity} energy patterns?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Consider your natural energy rhythms and work preferences",
                emotional_weight=1.4
            ),
            DialogueQuestion(
                text="What concerns or excitement do you have about the planned timeline?",
                question_type=QuestionType.TEXT,
                help_text="Share both concerns and positive anticipations",
                emotional_weight=1.3
            ),
            DialogueQuestion(
                text="Which user stories resonate most emotionally with you?",
                question_type=QuestionType.MULTI_SELECT,
                options=["Core functionality", "User experience", "Performance", "Security", "Innovation features", "Accessibility"],
                help_text="Select the stories that create the strongest emotional connection"
            ),
            DialogueQuestion(
                text="How should we balance speed vs. quality given your preferences?",
                question_type=QuestionType.CHOICE,
                options=["Prioritize thorough quality", "Balanced approach", "Emphasize delivery speed", "Adaptive based on context"],
                help_text="Choose the balance that feels right for this project"
            ),
            DialogueQuestion(
                text=f"What {quality_focus}-specific quality measures should we track?",
                question_type=QuestionType.TEXT,
                help_text="Define what quality tracking would be most meaningful",
                emotional_weight=1.2
            ),
            DialogueQuestion(
                text="How confident are you that this plan will lead to the emotional outcomes you want?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate your confidence in achieving the emotional goals",
                emotional_weight=1.5
            )
        ]
        
        return {
            'phase': 'Planning',
            'description': 'Strategic planning with emotional intelligence and sustainable pacing',
            'duration': '20-25 minutes',
            'questions': questions,
            'success_criteria': [
                'Sprint plan aligns with energy patterns',
                'Quality measures are clearly defined',
                'Timeline feels achievable and exciting',
                'User story priorities reflect emotional values'
            ],
            'follow_up_actions': [
                'Adjust sprint timeline based on feedback',
                'Define quality metrics and tracking',
                'Set up progress monitoring',
                'Schedule development check-ins'
            ]
        }
    
    def _get_development_dialogues(self, intensity: str, comm_style: str, quality_focus: str) -> Dict[str, Any]:
        """In-development feedback and course correction dialogues."""
        
        questions = [
            DialogueQuestion(
                text="How does the emerging implementation feel to you emotionally?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate your gut feeling about how the development is going",
                emotional_weight=1.5
            ),
            DialogueQuestion(
                text=f"Is our {comm_style} communication style working well for you during development?",
                question_type=QuestionType.YES_NO,
                help_text="Honest feedback helps us adjust our collaboration approach"
            ),
            DialogueQuestion(
                text="What aspects of the user experience are you most excited about?",
                question_type=QuestionType.TEXT,
                help_text="Share what's generating positive energy for you",
                emotional_weight=1.3
            ),
            DialogueQuestion(
                text="Are there any areas where you feel we should slow down for quality?",
                question_type=QuestionType.TEXT,
                help_text="Identify where more attention to quality would feel important"
            ),
            DialogueQuestion(
                text="How well is the development pace matching your energy and availability?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate how sustainable the current pace feels",
                emotional_weight=1.4
            ),
            DialogueQuestion(
                text="What human support or interaction would be most helpful right now?",
                question_type=QuestionType.MULTI_SELECT,
                options=["Technical guidance", "Emotional encouragement", "Strategic thinking", "Problem solving", "Creative brainstorming", "Quality review"],
                help_text="Select the types of support that would help most"
            )
        ]
        
        return {
            'phase': 'Development',
            'description': 'Real-time development feedback and emotional support',
            'duration': '10-15 minutes',
            'questions': questions,
            'success_criteria': [
                'Development feels emotionally sustainable',
                'Communication rhythm is working',
                'Quality concerns are addressed',
                'Energy level is being maintained'
            ],
            'follow_up_actions': [
                'Adjust development pace if needed',
                'Provide requested support',
                'Address quality concerns',
                'Schedule next check-in'
            ]
        }
    
    def _get_testing_dialogues(self, intensity: str, comm_style: str, quality_focus: str) -> Dict[str, Any]:
        """Quality validation and testing phase dialogues."""
        
        questions = [
            DialogueQuestion(
                text=f"Does the current quality level meet your {quality_focus} standards?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate how well the quality matches your expectations",
                emotional_weight=1.5
            ),
            DialogueQuestion(
                text="How does the user experience feel when you interact with it?",
                question_type=QuestionType.TEXT,
                help_text="Describe your emotional response to using the system",
                emotional_weight=1.4
            ),
            DialogueQuestion(
                text="What areas give you the most confidence vs. concern?",
                question_type=QuestionType.TEXT,
                help_text="Identify what feels solid vs. what needs attention"
            ),
            DialogueQuestion(
                text="Are there any emotional experience gaps that need addressing?",
                question_type=QuestionType.TEXT,
                help_text="Consider the emotional journey of end users",
                emotional_weight=1.3
            ),
            DialogueQuestion(
                text="How ready do you feel to share this with others?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate your comfort level with broader exposure",
                emotional_weight=1.4
            ),
            DialogueQuestion(
                text="What final touches would make you most proud of this work?",
                question_type=QuestionType.TEXT,
                help_text="Identify what would create maximum satisfaction"
            )
        ]
        
        return {
            'phase': 'Testing',
            'description': 'Quality validation with emotional experience assessment',
            'duration': '15-20 minutes',
            'questions': questions,
            'success_criteria': [
                'Quality standards are met',
                'User experience feels right',
                'Confidence level is high',
                'Emotional experience is satisfying'
            ],
            'follow_up_actions': [
                'Address quality concerns',
                'Polish emotional experience',
                'Prepare for review',
                'Document lessons learned'
            ]
        }
    
    def _get_review_dialogues(self, intensity: str, comm_style: str, quality_focus: str) -> Dict[str, Any]:
        """Review and demonstration phase dialogues."""
        
        questions = [
            DialogueQuestion(
                text="How do you feel about presenting this work to stakeholders?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate your excitement vs. nervousness about the review",
                emotional_weight=1.5
            ),
            DialogueQuestion(
                text="What aspects of this work make you most proud?",
                question_type=QuestionType.TEXT,
                help_text="Celebrate what went really well",
                emotional_weight=1.4
            ),
            DialogueQuestion(
                text="How well did we achieve the emotional outcomes you wanted?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate how well we met your emotional goals",
                emotional_weight=1.5
            ),
            DialogueQuestion(
                text="What story do you want to tell about this development phase?",
                question_type=QuestionType.TEXT,
                help_text="Frame the narrative you'd like to share"
            ),
            DialogueQuestion(
                text="Are there any concerns about stakeholder reactions?",
                question_type=QuestionType.TEXT,
                help_text="Surface any worries so we can address them"
            ),
            DialogueQuestion(
                text="How satisfied are you with the collaborative process we used?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate the quality of our working relationship",
                emotional_weight=1.3
            )
        ]
        
        return {
            'phase': 'Review',
            'description': 'Stakeholder review preparation and success celebration',
            'duration': '10-15 minutes',
            'questions': questions,
            'success_criteria': [
                'Confidence in presenting work',
                'Pride in accomplishments',
                'Emotional goals achieved',
                'Strong collaborative relationship'
            ],
            'follow_up_actions': [
                'Prepare presentation materials',
                'Practice demonstration',
                'Gather stakeholder feedback',
                'Celebrate achievements'
            ]
        }
    
    def _get_retrospective_dialogues(self, intensity: str, comm_style: str, quality_focus: str) -> Dict[str, Any]:
        """Retrospective and learning extraction dialogues."""
        
        questions = [
            DialogueQuestion(
                text="What was the most emotionally satisfying part of this development cycle?",
                question_type=QuestionType.TEXT,
                help_text="Identify what created the most positive energy",
                emotional_weight=1.5
            ),
            DialogueQuestion(
                text="What challenged you most, and how did you grow from it?",
                question_type=QuestionType.TEXT,
                help_text="Reflect on difficulties and learning",
                emotional_weight=1.4
            ),
            DialogueQuestion(
                text="How well did our human interaction approach serve your needs?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate the effectiveness of our collaboration style",
                emotional_weight=1.3
            ),
            DialogueQuestion(
                text="What would you change about the process for next time?",
                question_type=QuestionType.TEXT,
                help_text="Suggest improvements for future cycles"
            ),
            DialogueQuestion(
                text="How sustainable was this pace and approach for you?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate the long-term viability of this working style",
                emotional_weight=1.4
            ),
            DialogueQuestion(
                text="What wisdom would you share with future teams doing similar work?",
                question_type=QuestionType.TEXT,
                help_text="Capture insights for others to benefit from"
            )
        ]
        
        return {
            'phase': 'Retrospective',
            'description': 'Deep reflection and wisdom extraction for continuous improvement',
            'duration': '20-25 minutes',
            'questions': questions,
            'success_criteria': [
                'Key learnings captured',
                'Emotional journey processed',
                'Process improvements identified',
                'Wisdom extracted for future use'
            ],
            'follow_up_actions': [
                'Document lessons learned',
                'Update process guidelines',
                'Share insights with team',
                'Plan next cycle improvements'
            ]
        }
    
    def _get_deployment_dialogues(self, intensity: str, comm_style: str, quality_focus: str) -> Dict[str, Any]:
        """Deployment and release phase dialogues."""
        
        questions = [
            DialogueQuestion(
                text="How confident do you feel about releasing this to the world?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate your confidence in the release readiness",
                emotional_weight=1.5
            ),
            DialogueQuestion(
                text="What emotions come up when you think about users experiencing this?",
                question_type=QuestionType.TEXT,
                help_text="Reflect on your emotional anticipation of user impact",
                emotional_weight=1.4
            ),
            DialogueQuestion(
                text="Are there any last-minute concerns we should address?",
                question_type=QuestionType.TEXT,
                help_text="Surface any final worries or considerations"
            ),
            DialogueQuestion(
                text="How do you want to monitor and support the emotional impact on users?",
                question_type=QuestionType.TEXT,
                help_text="Plan for measuring emotional success"
            ),
            DialogueQuestion(
                text="What success would make this deployment feel emotionally fulfilling?",
                question_type=QuestionType.TEXT,
                help_text="Define what emotional success looks like",
                emotional_weight=1.3
            ),
            DialogueQuestion(
                text="How ready are you to receive feedback and iterate?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                help_text="Rate your openness to post-release evolution"
            )
        ]
        
        return {
            'phase': 'Deployment',
            'description': 'Release preparation with emotional readiness and user impact focus',
            'duration': '15-20 minutes',
            'questions': questions,
            'success_criteria': [
                'High confidence in release',
                'Emotional preparedness for user feedback',
                'Clear success metrics defined',
                'Support systems in place'
            ],
            'follow_up_actions': [
                'Execute deployment plan',
                'Monitor user feedback',
                'Track emotional impact metrics',
                'Plan first iteration'
            ]
        }
    
    def _get_default_dialogues(self, phase: str, intensity: str, comm_style: str, quality_focus: str) -> Dict[str, Any]:
        """Default dialogues for unknown phases."""
        
        questions = [
            DialogueQuestion(
                text=f"How do you feel about the current {phase} activities?",
                question_type=QuestionType.SCALE,
                scale_range=(1, 10),
                emotional_weight=1.3
            ),
            DialogueQuestion(
                text="What's working well that we should continue?",
                question_type=QuestionType.TEXT
            ),
            DialogueQuestion(
                text="What would you like to see changed or improved?",
                question_type=QuestionType.TEXT
            )
        ]
        
        return {
            'phase': phase.title(),
            'description': f'General feedback and interaction for {phase} phase',
            'duration': '10 minutes',
            'questions': questions,
            'success_criteria': ['Clear feedback provided', 'Next steps identified'],
            'follow_up_actions': ['Address feedback', 'Plan next interaction']
        }


# Global instance for easy use
enhanced_dialogues = EnhancedPhaseDialogues()


def get_enhanced_phase_dialogue(phase: str, vibe_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get enhanced dialogue configuration for a specific agile phase.
    
    Args:
        phase: The agile phase (inception, planning, development, testing, review, retrospective, deployment)
        vibe_context: Dictionary containing vibe configuration (intensity, communication_style, quality_focus)
    
    Returns:
        Dictionary containing questions, success criteria, and interaction metadata
    """
    return enhanced_dialogues.get_phase_dialogues(phase, vibe_context)


if __name__ == "__main__":
    # Example usage
    sample_vibe = {
        'intensity': 'energetic',
        'communication_style': 'collaborative', 
        'quality_focus': 'user_delight'
    }
    
    # Test each phase
    phases = ['inception', 'planning', 'development', 'testing', 'review', 'retrospective', 'deployment']
    
    for phase in phases:
        dialogue = get_enhanced_phase_dialogue(phase, sample_vibe)
        print(f"\n🎭 {dialogue['phase']} Phase")
        print(f"📝 Questions: {len(dialogue['questions'])}")
        print(f"⏰ Duration: {dialogue['duration']}")
        print(f"✅ Success Criteria: {len(dialogue['success_criteria'])}")
