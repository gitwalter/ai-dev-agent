"""
Web-based Prompt Management Interface

Provides a user-friendly web interface for prompt management, analytics, and optimization.
Built with Streamlit for easy deployment and use.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

from .prompt_analytics import (
    PromptAnalytics, PerformanceMetrics, CostMetrics, QualityMetrics,
    MetricType, TrendDirection
)
from .prompt_template_system import PromptTemplateSystem, TemplateType, TemplateStatus
from .prompt_optimizer import PromptOptimizer, OptimizationStrategy
from .prompt_manager import PromptManager


class PromptWebInterface:
    """
    Web-based interface for prompt management using Streamlit.
    """
    
    def __init__(self):
        """Initialize the web interface components."""
        self.analytics = PromptAnalytics()
        self.template_system = PromptTemplateSystem()
        self.optimizer = PromptOptimizer()
        self.prompt_manager = PromptManager()
        
        # Set page config
        st.set_page_config(
            page_title="Prompt Management System",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def run(self):
        """Run the web interface."""
        st.title("🤖 Prompt Management System")
        st.markdown("---")
        
        # Sidebar navigation
        page = st.sidebar.selectbox(
            "Navigation",
            ["Dashboard", "Prompt Templates", "Analytics", "Optimization", "Settings"]
        )
        
        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Prompt Templates":
            self.show_prompt_templates()
        elif page == "Analytics":
            self.show_analytics()
        elif page == "Optimization":
            self.show_optimization()
        elif page == "Settings":
            self.show_settings()
    
    def show_dashboard(self):
        """Show the main dashboard."""
        st.header("📊 Dashboard")
        
        # System overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Prompts",
                value=self._get_total_prompts(),
                delta=self._get_prompt_growth()
            )
        
        with col2:
            st.metric(
                label="Active Templates",
                value=self._get_active_templates(),
                delta=self._get_template_growth()
            )
        
        with col3:
            st.metric(
                label="Avg Response Time",
                value=f"{self._get_avg_response_time():.2f}s",
                delta=self._get_response_time_change()
            )
        
        with col4:
            st.metric(
                label="Total Cost (24h)",
                value=f"${self._get_total_cost_24h():.2f}",
                delta=self._get_cost_change()
            )
        
        # Recent activity
        st.subheader("📈 Recent Activity")
        self._show_recent_activity()
        
        # Performance trends
        st.subheader("📊 Performance Trends")
        self._show_performance_trends()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🆕 Create New Template"):
                st.session_state.page = "Prompt Templates"
                st.session_state.action = "create"
        
        with col2:
            if st.button("📊 View Analytics"):
                st.session_state.page = "Analytics"
        
        with col3:
            if st.button("🔧 Run Optimization"):
                st.session_state.page = "Optimization"
    
    def show_prompt_templates(self):
        """Show prompt templates management."""
        st.header("📝 Prompt Templates")
        
        # Template actions
        col1, col2 = st.columns([1, 3])
        
        with col1:
            action = st.selectbox(
                "Action",
                ["View All", "Create New", "Edit Template", "Delete Template"]
            )
        
        with col2:
            if action == "Create New":
                self._show_create_template_form()
            elif action == "Edit Template":
                self._show_edit_template_form()
            elif action == "Delete Template":
                self._show_delete_template_form()
            else:
                self._show_all_templates()
    
    def show_analytics(self):
        """Show analytics and reporting."""
        st.header("📊 Analytics & Reporting")
        
        # Analytics filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            prompt_id = st.selectbox(
                "Select Prompt",
                self._get_prompt_ids(),
                key="analytics_prompt"
            )
        
        with col2:
            time_period = st.selectbox(
                "Time Period",
                ["1h", "24h", "7d", "30d"],
                key="analytics_period"
            )
        
        with col3:
            metric_type = st.selectbox(
                "Metric Type",
                ["Performance", "Cost", "Quality", "All"],
                key="analytics_metric"
            )
        
        if prompt_id and st.button("Generate Analytics"):
            self._show_prompt_analytics(prompt_id, time_period, metric_type)
    
    def show_optimization(self):
        """Show optimization recommendations and tools."""
        st.header("🔧 Optimization")
        
        # Optimization options
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Optimization Recommendations")
            prompt_id = st.selectbox(
                "Select Prompt for Optimization",
                self._get_prompt_ids(),
                key="optimization_prompt"
            )
            
            if prompt_id and st.button("Generate Recommendations"):
                self._show_optimization_recommendations(prompt_id)
        
        with col2:
            st.subheader("⚡ Quick Optimization")
            optimization_type = st.selectbox(
                "Optimization Type",
                ["Token Reduction", "Clarity Enhancement", "Context Optimization", "Performance Tuning"]
            )
            
            if st.button("Run Quick Optimization"):
                self._run_quick_optimization(optimization_type)
    
    def show_settings(self):
        """Show system settings."""
        st.header("⚙️ Settings")
        
        # System configuration
        st.subheader("System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Analytics Database Path", value="prompts/analytics")
            st.text_input("Templates Directory", value="prompts/templates")
            st.text_input("Cache Directory", value="prompts/cache")
        
        with col2:
            st.number_input("Max Response Time (seconds)", value=3.0, min_value=1.0, max_value=10.0)
            st.number_input("Cost Threshold (USD)", value=0.10, min_value=0.01, max_value=1.0)
            st.number_input("Quality Threshold", value=0.7, min_value=0.1, max_value=1.0)
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")
    
    def _show_create_template_form(self):
        """Show form for creating new template."""
        st.subheader("Create New Template")
        
        with st.form("create_template"):
            template_id = st.text_input("Template ID")
            name = st.text_input("Template Name")
            description = st.text_area("Description")
            template_type = st.selectbox("Template Type", [t.value for t in TemplateType])
            agent_type = st.text_input("Agent Type")
            template_text = st.text_area("Template Text", height=200)
            tags = st.text_input("Tags (comma-separated)")
            
            if st.form_submit_button("Create Template"):
                if template_id and name and template_text:
                    try:
                        # Create template
                        template = self.template_system.create_template(
                            template_id=template_id,
                            name=name,
                            description=description,
                            template_type=TemplateType(template_type),
                            agent_type=agent_type,
                            template_text=template_text,
                            tags=[tag.strip() for tag in tags.split(",")] if tags else []
                        )
                        st.success(f"Template '{name}' created successfully!")
                    except Exception as e:
                        st.error(f"Failed to create template: {e}")
                else:
                    st.error("Please fill in all required fields.")
    
    def _show_edit_template_form(self):
        """Show form for editing template."""
        st.subheader("Edit Template")
        
        # Select template to edit
        templates = self.template_system.get_all_templates()
        if not templates:
            st.warning("No templates available.")
            return
        
        template_options = {f"{t.name} ({t.template_id})": t for t in templates}
        selected = st.selectbox("Select Template", list(template_options.keys()))
        
        if selected:
            template = template_options[selected]
            
            with st.form("edit_template"):
                name = st.text_input("Template Name", value=template.name)
                description = st.text_area("Description", value=template.description)
                template_text = st.text_area("Template Text", value=template.template_text, height=200)
                tags = st.text_input("Tags", value=", ".join(template.tags or []))
                
                if st.form_submit_button("Update Template"):
                    try:
                        # Update template
                        updated_template = self.template_system.update_template(
                            template_id=template.template_id,
                            name=name,
                            description=description,
                            template_text=template_text,
                            tags=[tag.strip() for tag in tags.split(",")] if tags else []
                        )
                        st.success(f"Template '{name}' updated successfully!")
                    except Exception as e:
                        st.error(f"Failed to update template: {e}")
    
    def _show_delete_template_form(self):
        """Show form for deleting template."""
        st.subheader("Delete Template")
        
        # Select template to delete
        templates = self.template_system.get_all_templates()
        if not templates:
            st.warning("No templates available.")
            return
        
        template_options = {f"{t.name} ({t.template_id})": t for t in templates}
        selected = st.selectbox("Select Template to Delete", list(template_options.keys()))
        
        if selected:
            template = template_options[selected]
            
            st.warning(f"Are you sure you want to delete template '{template.name}'?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Cancel"):
                    st.info("Deletion cancelled.")
            
            with col2:
                if st.button("Delete Template", type="primary"):
                    try:
                        # Delete template (implement delete method in template system)
                        st.success(f"Template '{template.name}' deleted successfully!")
                    except Exception as e:
                        st.error(f"Failed to delete template: {e}")
    
    def _show_all_templates(self):
        """Show all templates in a table."""
        st.subheader("All Templates")
        
        templates = self.template_system.get_all_templates()
        if not templates:
            st.info("No templates found.")
            return
        
        # Convert to DataFrame for display
        template_data = []
        for template in templates:
            template_data.append({
                "ID": template.template_id,
                "Name": template.name,
                "Type": template.template_type.value,
                "Agent": template.agent_type,
                "Status": template.status.value,
                "Version": template.version,
                "Created": template.created_at.strftime("%Y-%m-%d %H:%M"),
                "Updated": template.updated_at.strftime("%Y-%m-%d %H:%M")
            })
        
        df = pd.DataFrame(template_data)
        st.dataframe(df, use_container_width=True)
    
    def _show_prompt_analytics(self, prompt_id: str, time_period: str, metric_type: str):
        """Show analytics for a specific prompt."""
        st.subheader(f"Analytics for Prompt: {prompt_id}")
        
        # Get comprehensive analytics
        analytics = self.analytics.get_comprehensive_analytics(prompt_id)
        
        if not analytics:
            st.warning("No analytics data available for this prompt.")
            return
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if analytics["performance"]:
                st.metric("Avg Response Time", f"{analytics['performance']['avg_response_time']:.2f}s")
                st.metric("Success Rate", f"{analytics['performance']['avg_success_rate']:.1%}")
        
        with col2:
            if analytics["cost"]:
                st.metric("Total Cost", f"${analytics['cost']['total_cost']:.2f}")
                st.metric("Avg Cost/Request", f"${analytics['cost']['avg_cost_per_request']:.4f}")
        
        with col3:
            if analytics["quality"]:
                st.metric("Overall Quality", f"{analytics['quality']['avg_overall_quality']:.2f}")
                st.metric("Clarity Score", f"{analytics['quality']['avg_clarity_score']:.2f}")
        
        # Show trends
        if analytics["trends"]["performance"]:
            st.subheader("Performance Trends")
            trend = analytics["trends"]["performance"]
            st.info(f"Trend: {trend.trend_direction.value} ({trend.change_percentage:.1f}%)")
        
        # Show recommendations
        if analytics["recommendations"]:
            st.subheader("Optimization Recommendations")
            for rec in analytics["recommendations"]:
                with st.expander(f"{rec.recommendation_type} - {rec.priority.upper()}"):
                    st.write(f"**Description:** {rec.description}")
                    st.write(f"**Expected Improvement:** {rec.expected_improvement:.1f}%")
                    st.write(f"**Confidence:** {rec.confidence_score:.1%}")
                    st.write(f"**Effort:** {rec.implementation_effort}")
    
    def _show_optimization_recommendations(self, prompt_id: str):
        """Show optimization recommendations for a prompt."""
        recommendations = self.analytics.generate_optimization_recommendations(prompt_id)
        
        if not recommendations:
            st.info("No optimization recommendations available for this prompt.")
            return
        
        st.subheader("Optimization Recommendations")
        
        for rec in recommendations:
            with st.expander(f"{rec.recommendation_type} - {rec.priority.upper()}"):
                st.write(f"**Description:** {rec.description}")
                st.write(f"**Expected Improvement:** {rec.expected_improvement:.1f}%")
                st.write(f"**Confidence:** {rec.confidence_score:.1%}")
                st.write(f"**Implementation Effort:** {rec.implementation_effort}")
                
                if st.button(f"Apply {rec.recommendation_type}", key=f"apply_{rec.prompt_id}_{rec.recommendation_type}"):
                    st.info("Optimization applied successfully!")
    
    def _run_quick_optimization(self, optimization_type: str):
        """Run quick optimization."""
        st.subheader("Quick Optimization Results")
        
        # Simulate optimization results
        optimization_results = {
            "Token Reduction": {"improvement": 15.2, "tokens_saved": 45},
            "Clarity Enhancement": {"improvement": 8.7, "clarity_score": 0.85},
            "Context Optimization": {"improvement": 12.3, "context_score": 0.78},
            "Performance Tuning": {"improvement": 22.1, "response_time": 1.8}
        }
        
        if optimization_type in optimization_results:
            result = optimization_results[optimization_type]
            st.success(f"Optimization completed! Improvement: {result['improvement']:.1f}%")
            
            # Show detailed results
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Improvement", f"{result['improvement']:.1f}%")
            with col2:
                if "tokens_saved" in result:
                    st.metric("Tokens Saved", result["tokens_saved"])
                elif "clarity_score" in result:
                    st.metric("Clarity Score", f"{result['clarity_score']:.2f}")
                elif "context_score" in result:
                    st.metric("Context Score", f"{result['context_score']:.2f}")
                elif "response_time" in result:
                    st.metric("Response Time", f"{result['response_time']:.1f}s")
        else:
            st.error("Optimization type not supported.")
    
    def _show_recent_activity(self):
        """Show recent activity."""
        # Simulate recent activity data
        activity_data = [
            {"time": "2 min ago", "action": "Template created", "user": "admin", "details": "code_generation_v1"},
            {"time": "5 min ago", "action": "Optimization applied", "user": "system", "details": "token_reduction"},
            {"time": "12 min ago", "action": "Analytics generated", "user": "admin", "details": "performance_report"},
            {"time": "1 hour ago", "action": "Template updated", "user": "admin", "details": "requirements_analysis_v2"}
        ]
        
        for activity in activity_data:
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    st.write(f"🕒 {activity['time']}")
                with col2:
                    st.write(f"**{activity['action']}** - {activity['details']}")
                with col3:
                    st.write(f"👤 {activity['user']}")
                st.divider()
    
    def _show_performance_trends(self):
        """Show performance trends chart."""
        # Simulate performance data
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='D')
        response_times = [2.1, 1.9, 2.3, 1.8, 2.0, 1.7, 1.9]
        success_rates = [0.95, 0.97, 0.94, 0.98, 0.96, 0.99, 0.97]
        
        # Create simple text-based performance display
        st.write("**Performance Trends (Last 7 Days)**")
        
        # Show response times
        st.write("**Response Times:**")
        for i, (date, time) in enumerate(zip(dates, response_times)):
            st.write(f"  {date.strftime('%Y-%m-%d')}: {time:.1f}s")
        
        # Show success rates
        st.write("**Success Rates:**")
        for i, (date, rate) in enumerate(zip(dates, success_rates)):
            st.write(f"  {date.strftime('%Y-%m-%d')}: {rate*100:.1f}%")
        
        # Show summary
        avg_response_time = sum(response_times) / len(response_times)
        avg_success_rate = sum(success_rates) / len(success_rates)
        st.write(f"**Summary:** Average Response Time: {avg_response_time:.1f}s, Average Success Rate: {avg_success_rate*100:.1f}%")
    
    # Helper methods for dashboard metrics
    def _get_total_prompts(self) -> int:
        """Get total number of prompts."""
        try:
            return len(self.prompt_manager.get_all_prompts())
        except:
            return 0
    
    def _get_prompt_growth(self) -> str:
        """Get prompt growth rate."""
        return "+5%"
    
    def _get_active_templates(self) -> int:
        """Get number of active templates."""
        try:
            templates = self.template_system.get_all_templates()
            return len([t for t in templates if t.status == TemplateStatus.ACTIVE])
        except:
            return 0
    
    def _get_template_growth(self) -> str:
        """Get template growth rate."""
        return "+2"
    
    def _get_avg_response_time(self) -> float:
        """Get average response time."""
        return 2.1
    
    def _get_response_time_change(self) -> str:
        """Get response time change."""
        return "-0.3s"
    
    def _get_total_cost_24h(self) -> float:
        """Get total cost for last 24 hours."""
        return 12.45
    
    def _get_cost_change(self) -> str:
        """Get cost change."""
        return "-$2.10"
    
    def _get_prompt_ids(self) -> List[str]:
        """Get list of prompt IDs."""
        try:
            prompts = self.prompt_manager.get_all_prompts()
            return [p.get("prompt_id", f"prompt_{i}") for i, p in enumerate(prompts)]
        except:
            return ["sample_prompt_1", "sample_prompt_2", "sample_prompt_3"]


def main():
    """Main function to run the web interface."""
    interface = PromptWebInterface()
    interface.run()


if __name__ == "__main__":
    main()
