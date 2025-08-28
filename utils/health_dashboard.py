#!/usr/bin/env python3
"""
Real-time System Health Dashboard for AI-Dev-Agent System.

This module provides a Streamlit-based dashboard for monitoring system health,
displaying agent status, alerts, and system metrics in real-time.

Following Sprint 1 requirements for US-001: System Health Monitoring.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any

from utils.system_health_monitor import (
    get_health_monitor, 
    HealthStatus, 
    AlertLevel,
    get_current_system_health
)


class HealthDashboard:
    """
    Real-time health dashboard for system monitoring.
    
    Provides comprehensive visualization of agent health, alerts,
    and system performance metrics.
    """
    
    def __init__(self):
        """Initialize the health dashboard."""
        self.monitor = get_health_monitor()
        
    def render_dashboard(self):
        """Render the complete health monitoring dashboard."""
        st.set_page_config(
            page_title="AI-Dev-Agent System Health",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🔍 AI-Dev-Agent System Health Monitor")
        st.markdown("*Real-time monitoring and health status of all system agents*")
        
        # Add refresh controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🔄 Force Health Check", type="primary"):
                with st.spinner("Performing health check..."):
                    try:
                        asyncio.run(self.monitor.force_health_check())
                        st.success("Health check completed!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Health check failed: {e}")
        
        with col2:
            auto_refresh = st.checkbox("Auto Refresh (30s)", value=True)
        
        with col3:
            if st.button("📊 Export Report"):
                self._export_health_report()
        
        # Auto-refresh logic
        if auto_refresh:
            # Use a placeholder for auto-refresh
            placeholder = st.empty()
            with placeholder:
                st.info("Auto-refreshing every 30 seconds...")
            
            # Wait and refresh
            import time
            time.sleep(30)
            st.rerun()
        
        # Get current health data
        try:
            health_data = get_current_system_health()
        except Exception as e:
            st.error(f"Failed to load health data: {e}")
            return
        
        # Render dashboard sections
        self._render_system_overview(health_data)
        self._render_agent_status_grid(health_data)
        self._render_alerts_section(health_data)
        self._render_performance_metrics(health_data)
        self._render_system_logs()
        
    def _render_system_overview(self, health_data: Dict[str, Any]):
        """Render system overview section."""
        st.header("📊 System Overview")
        
        summary = health_data.get('summary', {})
        
        # Create overview metrics columns
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            status = summary.get('overall_status', 'unknown')
            status_color = self._get_status_color(status)
            st.metric(
                label="System Status",
                value=status.upper(),
                delta=None
            )
            st.markdown(f"<div style='color: {status_color}; font-size: 20px; text-align: center;'>●</div>", 
                       unsafe_allow_html=True)
        
        with col2:
            healthy = summary.get('healthy_agents', 0)
            total = summary.get('total_agents', 7)
            st.metric(
                label="Healthy Agents",
                value=f"{healthy}/{total}",
                delta=f"{(healthy/total*100):.0f}%" if total > 0 else "0%"
            )
        
        with col3:
            alerts = summary.get('active_alerts', 0)
            st.metric(
                label="Active Alerts",
                value=alerts,
                delta="0" if alerts == 0 else f"+{alerts}",
                delta_color="normal" if alerts == 0 else "inverse"
            )
        
        with col4:
            uptime = summary.get('system_uptime_hours', 0)
            st.metric(
                label="System Uptime",
                value=f"{uptime:.1f}h",
                delta=None
            )
        
        with col5:
            monitoring_active = health_data.get('monitoring_active', False)
            st.metric(
                label="Monitoring",
                value="ACTIVE" if monitoring_active else "INACTIVE",
                delta=None
            )
            monitor_color = "green" if monitoring_active else "red"
            st.markdown(f"<div style='color: {monitor_color}; font-size: 20px; text-align: center;'>●</div>", 
                       unsafe_allow_html=True)
        
        # System health gauge
        st.subheader("System Health Score")
        health_score = (healthy / total * 100) if total > 0 else 0
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = health_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Health Score (%)"},
            delta = {'reference': 100},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_agent_status_grid(self, health_data: Dict[str, Any]):
        """Render agent status grid."""
        st.header("🤖 Agent Status")
        
        agents = health_data.get('agents', {})
        
        if not agents:
            st.warning("No agent data available")
            return
        
        # Create agent status grid
        cols = st.columns(3)  # 3 columns for 7 agents
        
        for idx, (agent_name, metrics) in enumerate(agents.items()):
            col = cols[idx % 3]
            
            with col:
                with st.container():
                    status = metrics.get('status', 'unknown')
                    status_color = self._get_status_color(status)
                    
                    # Agent card
                    st.markdown(f"""
                    <div style="
                        border: 2px solid {status_color};
                        border-radius: 10px;
                        padding: 15px;
                        margin: 5px;
                        background-color: rgba(255,255,255,0.05);
                    ">
                        <h4 style="color: {status_color}; margin: 0;">
                            {agent_name.replace('_', ' ').title()}
                        </h4>
                        <p style="margin: 5px 0;"><strong>Status:</strong> {status.upper()}</p>
                        <p style="margin: 5px 0;"><strong>Response Time:</strong> {metrics.get('response_time_ms', 0):.1f}ms</p>
                        <p style="margin: 5px 0;"><strong>Success Rate:</strong> {metrics.get('success_rate', 0):.1f}%</p>
                        <p style="margin: 5px 0;"><strong>Last Check:</strong> {self._format_timestamp(metrics.get('last_heartbeat'))}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show last error if any
                    if metrics.get('last_error'):
                        st.error(f"⚠️ {metrics['last_error']}")
    
    def _render_alerts_section(self, health_data: Dict[str, Any]):
        """Render alerts and notifications section."""
        st.header("🚨 Active Alerts")
        
        alerts = health_data.get('active_alerts', [])
        
        if not alerts:
            st.success("✅ No active alerts - All systems operating normally")
            return
        
        # Display alerts
        for alert in alerts:
            level = alert.get('level', 'info')
            agent_name = alert.get('agent_name', 'unknown')
            message = alert.get('message', 'No message')
            timestamp = alert.get('timestamp', '')
            
            # Choose alert styling based on level
            if level == 'emergency':
                st.error(f"🚨 **EMERGENCY** [{agent_name}]: {message}")
            elif level == 'critical':
                st.error(f"❌ **CRITICAL** [{agent_name}]: {message}")
            elif level == 'warning':
                st.warning(f"⚠️ **WARNING** [{agent_name}]: {message}")
            else:
                st.info(f"ℹ️ **INFO** [{agent_name}]: {message}")
            
            st.caption(f"Alert time: {self._format_timestamp(timestamp)}")
        
        # Alert summary chart
        if len(alerts) > 1:
            st.subheader("Alert Level Distribution")
            
            alert_counts = {}
            for alert in alerts:
                level = alert.get('level', 'info')
                alert_counts[level] = alert_counts.get(level, 0) + 1
            
            fig = px.pie(
                values=list(alert_counts.values()),
                names=list(alert_counts.keys()),
                title="Active Alerts by Severity Level"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_performance_metrics(self, health_data: Dict[str, Any]):
        """Render performance metrics and trends."""
        st.header("📈 Performance Metrics")
        
        agents = health_data.get('agents', {})
        
        if not agents:
            st.warning("No performance data available")
            return
        
        # Response time chart
        agent_names = list(agents.keys())
        response_times = [agents[name].get('response_time_ms', 0) for name in agent_names]
        success_rates = [agents[name].get('success_rate', 0) for name in agent_names]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Response Times")
            fig = px.bar(
                x=[name.replace('_', ' ').title() for name in agent_names],
                y=response_times,
                title="Agent Response Times (ms)",
                color=response_times,
                color_continuous_scale="RdYlGn_r"
            )
            fig.update_layout(
                xaxis_title="Agent",
                yaxis_title="Response Time (ms)",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Success Rates")
            fig = px.bar(
                x=[name.replace('_', ' ').title() for name in agent_names],
                y=success_rates,
                title="Agent Success Rates (%)",
                color=success_rates,
                color_continuous_scale="RdYlGn"
            )
            fig.update_layout(
                xaxis_title="Agent",
                yaxis_title="Success Rate (%)",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance summary table
        st.subheader("Detailed Performance Metrics")
        
        performance_data = []
        for agent_name, metrics in agents.items():
            performance_data.append({
                "Agent": agent_name.replace('_', ' ').title(),
                "Status": metrics.get('status', 'unknown').upper(),
                "Response Time (ms)": f"{metrics.get('response_time_ms', 0):.1f}",
                "Success Rate (%)": f"{metrics.get('success_rate', 0):.1f}",
                "Uptime (hrs)": f"{metrics.get('uptime_hours', 0):.1f}",
                "Error Count": metrics.get('error_count', 0),
                "Last Check": self._format_timestamp(metrics.get('last_heartbeat'))
            })
        
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True)
    
    def _render_system_logs(self):
        """Render system logs and history."""
        st.header("📋 System Logs")
        
        # Load health history if available
        history_path = Path("monitoring/health_history.json")
        
        if history_path.exists():
            try:
                with open(history_path, 'r') as f:
                    history = json.load(f)
                
                st.subheader("Health Check History")
                
                # Show recent history
                recent_history = history[-10:] if len(history) > 10 else history
                
                for entry in reversed(recent_history):
                    timestamp = entry.get('timestamp', 'Unknown')
                    summary = entry.get('summary', {})
                    
                    st.write(f"**{self._format_timestamp(timestamp)}**")
                    st.write(f"System Status: {summary.get('overall_status', 'unknown').upper()}")
                    st.write(f"Healthy Agents: {summary.get('healthy_agents', 0)}/{summary.get('total_agents', 0)}")
                    st.write(f"Active Alerts: {summary.get('active_alerts', 0)}")
                    st.write("---")
                
            except Exception as e:
                st.error(f"Failed to load history: {e}")
        else:
            st.info("No historical data available yet")
    
    def _get_status_color(self, status: str) -> str:
        """Get color for status display."""
        color_map = {
            'healthy': 'green',
            'warning': 'orange', 
            'critical': 'red',
            'offline': 'red',
            'unknown': 'gray'
        }
        return color_map.get(status.lower(), 'gray')
    
    def _format_timestamp(self, timestamp_str: str) -> str:
        """Format timestamp for display."""
        if not timestamp_str:
            return "Never"
        
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp_str
    
    def _export_health_report(self):
        """Export health report to JSON."""
        try:
            health_data = get_current_system_health()
            
            report = {
                "export_time": datetime.now().isoformat(),
                "health_data": health_data
            }
            
            report_json = json.dumps(report, indent=2)
            
            st.download_button(
                label="📥 Download Health Report",
                data=report_json,
                file_name=f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Failed to export report: {e}")


def main():
    """Main dashboard application."""
    dashboard = HealthDashboard()
    dashboard.render_dashboard()


if __name__ == "__main__":
    main()
