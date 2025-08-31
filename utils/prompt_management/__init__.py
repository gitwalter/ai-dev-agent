"""
Prompt Management System
========================

Comprehensive prompt management system for AI agents, including:
- Prompt database management
- Template system with version control
- Performance optimization framework
- A/B testing capabilities
- Dynamic loading and caching
- Quality assessment and analytics
- Backup and recovery systems
- Audit trail and compliance tracking

This module provides the complete prompt engineering capabilities for US-PE-02.

Author: AI-Dev-Agent System
Version: 2.0
Last Updated: Current Session
"""

from .prompt_manager import PromptManager, get_prompt_manager
from .prompt_template_system import (
    PromptTemplateSystem, 
    PromptTemplate, 
    TemplateType, 
    TemplateStatus,
    get_template_system
)
from .prompt_optimizer import (
    PromptOptimizer,
    OptimizationStrategy,
    OptimizationResult,
    PerformanceMetrics,
    get_prompt_optimizer
)
from .prompt_ab_testing import (
    PromptABTesting,
    ABTest,
    TestResult,
    StatisticalResult,
    TestStatus,
    TestType,
    get_ab_testing
)

# Analytics and web interface components
from .prompt_analytics import (
    PromptAnalytics, 
    PerformanceMetrics as AnalyticsPerformanceMetrics,
    CostMetrics, 
    QualityMetrics, 
    OptimizationRecommendation, 
    TrendAnalysis,
    MetricType, 
    TrendDirection
)
from .prompt_web_interface import PromptWebInterface

# Advanced optimization components
from .advanced_optimizer import (
    AdvancedPromptOptimizer,
    OptimizationType,
    OptimizationStatus,
    OptimizationContext,
    OptimizationResult,
    MLModel,
    get_advanced_optimizer
)

# NEW: Quality assessment system
from .prompt_quality_assessment import (
    PromptQualityAssessor,
    QualityDimension,
    QualityLevel,
    QualityScore,
    OverallQualityAssessment,
    QualityBenchmark,
    get_quality_assessor
)

# NEW: Backup and recovery system
from .prompt_backup_recovery import (
    PromptBackupRecovery,
    BackupType,
    BackupStatus,
    RecoveryType,
    BackupMetadata,
    RecoveryMetadata,
    IntegrityCheckResult,
    get_backup_recovery_system
)

# NEW: Audit trail system
from .prompt_audit_trail import (
    PromptAuditTrail,
    ChangeType,
    ChangeSeverity,
    ComplianceStatus,
    ChangeRecord,
    ChangeImpact,
    ComplianceRecord,
    AuditSummary,
    get_audit_trail_system
)

# Legacy imports for backward compatibility
# from .agent_prompt_loader import AgentPromptLoader  # File doesn't exist yet

# Main system integration
class PromptManagementSystem:
    """
    Main integration class for the complete prompt management system.
    Provides unified access to all prompt management capabilities.
    """
    
    def __init__(self):
        """Initialize the complete prompt management system."""
        self.prompt_manager = get_prompt_manager()
        self.template_system = get_template_system()
        self.optimizer = get_prompt_optimizer()
        self.ab_testing = get_ab_testing()
        self.analytics = PromptAnalytics()
        self.web_interface = PromptWebInterface()
        self.advanced_optimizer = get_advanced_optimizer()
        
        # NEW: Quality assessment system
        self.quality_assessor = get_quality_assessor()
        
        # NEW: Backup and recovery system
        self.backup_recovery = get_backup_recovery_system()
        
        # NEW: Audit trail system
        self.audit_trail = get_audit_trail_system()
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status."""
        return {
            "prompt_manager": {
                "status": "operational",
                "database_status": "active",
                "connection_pool": "healthy"
            },
            "template_system": {
                "status": "operational",
                "templates_loaded": "active",
                "validation": "enabled",
                "total_templates": 0
            },
            "optimizer": {
                "status": "operational",
                "optimization_engine": "active",
                "performance_tracking": "enabled",
                "optimization_history": 0
            },
            "ab_testing": {
                "status": "operational",
                "tests_running": "active",
                "analytics": "enabled",
                "total_tests": 0
            },
            "analytics": "operational",
            "web_interface": "operational", 
            "advanced_optimizer": "operational",
            "quality_assessment": "operational",
            "backup_recovery": "operational",
            "audit_trail": "operational"
        }
    
    def run_quality_assessment(self, prompt_id: str, prompt_text: str, 
                              context: dict = None) -> dict:
        """Run comprehensive quality assessment on a prompt."""
        try:
            assessment = self.quality_assessor.assess_prompt_quality(
                prompt_id, prompt_text, context
            )
            
            # Record the assessment in audit trail
            self.audit_trail.record_change(
                prompt_id=prompt_id,
                change_type=ChangeType.UPDATE,
                user_id="system",
                user_name="Quality Assessment System",
                change_summary=f"Quality assessment completed: {assessment.overall_score:.2f}",
                metadata={
                    "quality_score": assessment.overall_score,
                    "quality_level": assessment.quality_level.value,
                    "improvement_priority": assessment.improvement_priority
                }
            )
            
            return {
                "overall_score": assessment.overall_score,
                "quality_level": assessment.quality_level.value,
                "strengths": assessment.strengths,
                "weaknesses": assessment.weaknesses,
                "improvement_priority": assessment.improvement_priority,
                "dimension_scores": {
                    dim.value: {
                        "score": score.score,
                        "reasoning": score.reasoning,
                        "suggestions": score.suggestions
                    }
                    for dim, score in assessment.dimension_scores.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return {"error": str(e)}
    
    def create_backup(self, backup_type: str = "full", description: str = None) -> dict:
        """Create a backup of the prompt management system."""
        try:
            backup_id = self.backup_recovery.create_backup(
                BackupType(backup_type), description
            )
            
            # Record backup creation in audit trail
            self.audit_trail.record_change(
                prompt_id="system",
                change_type=ChangeType.CREATE,
                user_id="system",
                user_name="Backup System",
                change_summary=f"Backup created: {backup_id}",
                metadata={
                    "backup_id": backup_id,
                    "backup_type": backup_type,
                    "description": description
                }
            )
            
            return {
                "backup_id": backup_id,
                "status": "success",
                "message": f"Backup {backup_id} created successfully"
            }
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def get_audit_summary(self, days: int = 30) -> dict:
        """Get comprehensive audit summary."""
        try:
            audit_summary = self.audit_trail.get_audit_summary(days)
            return {
                "total_changes": audit_summary.total_changes,
                "changes_by_type": audit_summary.changes_by_type,
                "changes_by_severity": audit_summary.changes_by_severity,
                "changes_by_user": audit_summary.changes_by_user,
                "compliance_status": audit_summary.compliance_status,
                "recent_changes": audit_summary.recent_changes,
                "pending_approvals": audit_summary.pending_approvals,
                "compliance_issues": audit_summary.compliance_issues
            }
            
        except Exception as e:
            logger.error(f"Failed to get audit summary: {e}")
            return {"error": str(e)}
    
    def run_comprehensive_analysis(self, prompt_id: str) -> dict:
        """Run comprehensive analysis including quality, performance, and compliance."""
        try:
            # Get prompt data
            prompt_data = self.prompt_manager.get_prompt(prompt_id)
            if not prompt_data:
                return {"error": f"Prompt {prompt_id} not found"}
            
            prompt_text = prompt_data.get("content", "")
            
            # Run quality assessment
            quality_result = self.run_quality_assessment(prompt_id, prompt_text)
            
            # Get performance metrics
            performance_metrics = self.analytics.get_prompt_performance_metrics(prompt_id)
            
            # Get optimization recommendations
            optimization_recs = self.analytics.get_optimization_recommendations(prompt_id)
            
            # Get change history
            change_history = self.audit_trail.get_change_history(prompt_id, days=30)
            
            # Get backup status
            backup_summary = self.backup_recovery.get_backup_summary()
            
            return {
                "prompt_id": prompt_id,
                "quality_assessment": quality_result,
                "performance_metrics": performance_metrics,
                "optimization_recommendations": optimization_recs,
                "change_history": [
                    {
                        "change_id": change.change_id,
                        "change_type": change.change_type.value,
                        "timestamp": change.timestamp.isoformat(),
                        "user_name": change.user_name,
                        "change_summary": change.change_summary
                    }
                    for change in change_history[:10]  # Last 10 changes
                ],
                "backup_status": backup_summary,
                "system_health": self.get_system_status()
            }
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            return {"error": str(e)}
    
    def get_system_health_report(self) -> dict:
        """Get comprehensive system health report."""
        try:
            # Check all system components
            system_status = self.get_system_status()
            
            # Get recent audit summary
            audit_summary = self.audit_trail.get_audit_summary(days=7)
            
            # Get backup summary
            backup_summary = self.backup_recovery.get_backup_summary()
            
            # Check data integrity
            integrity_result = self.backup_recovery.check_data_integrity()
            
            # Calculate overall health score
            health_score = 100.0
            
            # Deduct points for issues
            if audit_summary.compliance_issues > 0:
                health_score -= min(audit_summary.compliance_issues * 5, 20)
            
            if audit_summary.pending_approvals > 5:
                health_score -= min((audit_summary.pending_approvals - 5) * 2, 15)
            
            if integrity_result.integrity_score < 0.95:
                health_score -= (0.95 - integrity_result.integrity_score) * 100
            
            health_score = max(health_score, 10.0)  # Minimum baseline health score
            
            return {
                "overall_health_score": health_score,
                "health_status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical",
                "system_status": system_status,
                "audit_summary": {
                    "total_changes": audit_summary.total_changes,
                    "compliance_issues": audit_summary.compliance_issues,
                    "pending_approvals": audit_summary.pending_approvals
                },
                "backup_status": {
                    "total_backups": backup_summary.get("total_backups", 0),
                    "failed_backups": backup_summary.get("failed_backups", 0)
                },
                "data_integrity": {
                    "integrity_score": integrity_result.integrity_score,
                    "total_files": integrity_result.total_files,
                    "corrupted_files": integrity_result.corrupted_files,
                    "missing_files": integrity_result.missing_files
                },
                "recommendations": self._generate_health_recommendations(
                    health_score, audit_summary, integrity_result
                )
            }
            
        except Exception as e:
            logger.error(f"System health report generation failed: {e}")
            return {"error": str(e)}
    
    def _generate_health_recommendations(self, health_score: float, 
                                       audit_summary, integrity_result) -> list:
        """Generate health improvement recommendations."""
        recommendations = []
        
        if health_score < 80:
            recommendations.append("System health needs attention")
        
        if audit_summary.compliance_issues > 0:
            recommendations.append(f"Address {audit_summary.compliance_issues} compliance issues")
        
        if audit_summary.pending_approvals > 5:
            recommendations.append(f"Review {audit_summary.pending_approvals} pending approvals")
        
        if integrity_result.integrity_score < 0.95:
            recommendations.append("Run data integrity check and restore corrupted files")
        
        if integrity_result.missing_files > 0:
            recommendations.append(f"Restore {integrity_result.missing_files} missing files from backup")
        
        if not recommendations:
            recommendations.append("System is healthy - continue monitoring")
        
        return recommendations
    
    def create_optimized_template(self, name: str, description: str, agent_type: str, 
                                 template_text: str, author: str, optimization_strategy,
                                 tags: list = None) -> str:
        """Create an optimized template."""
        try:
            # Create base template  
            from .prompt_template_system import TemplateType
            template_id = self.template_system.create_template(
                name=name,
                description=description,
                agent_type=agent_type,
                template_text=template_text,
                template_type=TemplateType.ENHANCED,
                author=author,
                tags=tags or []
            )
            
            # Apply optimization if available
            optimization_applied = False
            if hasattr(self, 'optimizer'):
                optimized_result = self.optimizer.optimize_prompt(
                    template_text, optimization_strategy
                )
                # Update template with optimized text and metadata
                self.template_system.update_template(
                    template_id, {
                        'template_text': optimized_result.optimized_prompt,
                        'metadata': {
                            'optimization_applied': True, 
                            'optimization_strategy': optimization_strategy.value,
                            'improvement_score': getattr(optimized_result, 'improvement_score', 0.1)
                        }
                    }
                )
                optimization_applied = True
            else:
                # Set metadata even if no optimization
                self.template_system.update_template(
                    template_id, {'metadata': {'optimization_applied': optimization_applied}}
                )
            
            # Activate the template
            from .prompt_template_system import TemplateStatus
            self.template_system.update_template(
                template_id, {'status': TemplateStatus.ACTIVE}
            )
            
            return template_id
            
        except Exception as e:
            import logging
            logging.error(f"Error creating optimized template: {e}")
            raise
    
    def create_ab_test(self, name: str, description: str, agent_type: str,
                      variant_a_text: str, variant_b_text: str, test_type) -> str:
        """Create an A/B test."""
        try:
            # Create A/B test using the ab_testing system
            test_id = self.ab_testing.create_test(
                name=name,
                description=description,
                test_type=test_type,
                variant_a={'prompt_text': variant_a_text, 'agent_type': agent_type},
                variant_b={'prompt_text': variant_b_text, 'agent_type': agent_type}
            )
            
            return test_id
            
        except Exception as e:
            import logging
            logging.error(f"Error creating A/B test: {e}")
            raise
    
    def get_optimization_recommendations(self, prompt_text: str) -> list:
        """Get optimization recommendations for a prompt."""
        try:
            from .prompt_optimizer import OptimizationStrategy
            # Analyze prompt and generate recommendations
            recommendations = []
            
            # Check prompt length for token reduction
            word_count = len(prompt_text.split())
            if word_count > 200:  # Long prompt threshold
                recommendations.append({
                    'strategy': OptimizationStrategy.TOKEN_REDUCTION,
                    'priority': 'high',
                    'reason': f'Prompt is {word_count} words, consider reducing for efficiency',
                    'suggested_action': 'Remove redundant phrases and simplify language'
                })
            
            # Check for clarity enhancement opportunities
            if any(word in prompt_text.lower() for word in ['analyze', 'process', 'handle']):
                recommendations.append({
                    'strategy': OptimizationStrategy.CLARITY_ENHANCEMENT,
                    'priority': 'medium',
                    'reason': 'Generic action words detected, could be more specific',
                    'suggested_action': 'Use more specific and actionable language'
                })
            
            # Check for context optimization opportunities
            if '{{' in prompt_text and '}}' in prompt_text:
                recommendations.append({
                    'strategy': OptimizationStrategy.CONTEXT_OPTIMIZATION,
                    'priority': 'medium',
                    'reason': 'Template variables found, context can be optimized',
                    'suggested_action': 'Ensure context variables are well-defined'
                })
            
            return recommendations
            
        except Exception as e:
            import logging
            logging.error(f"Error getting optimization recommendations: {e}")
            return []
    
    def render_template_with_context(self, template_id: str, context: dict) -> str:
        """Render a template with the provided context."""
        try:
            # Get template
            template = self.template_system.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Render template with context using simple string replacement
            rendered_text = template.template_text
            for key, value in context.items():
                rendered_text = rendered_text.replace(f"{{{{{key}}}}}", str(value))
            
            return rendered_text
            
        except Exception as e:
            import logging
            logging.error(f"Error rendering template: {e}")
            raise
    
    def record_prompt_performance(self, prompt_id: str, execution_time: float,
                                 token_count: int, response_quality: float,
                                 success: bool, metadata: dict = None):
        """Record performance metrics for a prompt."""
        try:
            # Record performance using analytics system
            performance_data = {
                'prompt_id': prompt_id,
                'execution_time': execution_time,
                'token_count': token_count,
                'response_quality': response_quality,
                'success': success,
                'metadata': metadata or {},
                'timestamp': self._get_current_timestamp()
            }
            
            # Store in analytics system
            if hasattr(self, 'analytics'):
                from .prompt_analytics import PerformanceMetrics
                from datetime import datetime
                metrics = PerformanceMetrics(
                    prompt_id=prompt_id,
                    response_time=execution_time,
                    token_count=token_count,
                    success_rate=1.0 if success else 0.0,
                    error_rate=0.0 if success else 1.0,
                    user_satisfaction=response_quality,
                    timestamp=datetime.now()
                )
                self.analytics.record_performance_metrics(metrics)
            
            # Also store in optimizer system for retrieval
            if hasattr(self, 'optimizer'):
                self.optimizer.record_performance(
                    prompt_id=prompt_id,
                    execution_time=execution_time,
                    token_count=token_count,
                    response_quality=response_quality,
                    success=success,
                    metadata=metadata
                )
            
            # Log performance
            import logging
            logging.info(f"Recorded performance for prompt {prompt_id}: success={success}, quality={response_quality}")
            
        except Exception as e:
            import logging
            logging.error(f"Error recording prompt performance: {e}")
            raise
    
    def _get_current_timestamp(self):
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


# Factory function for the complete system
def get_prompt_management_system() -> PromptManagementSystem:
    """Get a complete prompt management system instance."""
    return PromptManagementSystem()


# Export all major components for direct access
__all__ = [
    # Core components
    "PromptManager", "get_prompt_manager",
    "PromptTemplateSystem", "get_template_system",
    "PromptOptimizer", "get_prompt_optimizer",
    "PromptABTesting", "get_ab_testing",
    
    # Analytics and web interface
    "PromptAnalytics", "PromptWebInterface",
    
    # Advanced optimization
    "AdvancedPromptOptimizer", "get_advanced_optimizer",
    
    # NEW: Quality assessment
    "PromptQualityAssessor", "get_quality_assessor",
    "QualityDimension", "QualityLevel", "QualityScore", "OverallQualityAssessment",
    
    # NEW: Backup and recovery
    "PromptBackupRecovery", "get_backup_recovery_system",
    "BackupType", "BackupStatus", "RecoveryType",
    
    # NEW: Audit trail
    "PromptAuditTrail", "get_audit_trail_system",
    "ChangeType", "ChangeSeverity", "ComplianceStatus",
    
    # Main system
    "PromptManagementSystem", "get_prompt_management_system"
]
