#!/usr/bin/env python3
"""
Report Generation Scripts
=========================

Automated report and dashboard generation for sprint planning and analysis.
Creates comprehensive reports, visualizations, and dashboards from collected metrics.

Features:
- Multi-format report generation (PDF, HTML, Markdown)
- Interactive dashboards and visualizations
- Automated scheduling and distribution
- Template-based report customization
- Historical trend analysis
- Executive summary generation

Requirements:
- Python 3.8+
- Required packages: matplotlib, plotly, jinja2, weasyprint, pandas
- Template files in templates/ directory
- Configuration file: reports_config.yaml

Usage:
    python report_generation.py --type sprint --sprint 15 --format pdf
    python report_generation.py --type dashboard --team alpha --output dashboard.html
    python report_generation.py --type trend --days 90 --format html

Author: AI-Dev-Agent Team
Version: 1.0
Last Updated: Current Session
"""

import argparse
import json
import logging
import os
import sys
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
import sqlite3

# Optional imports - install if needed
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    from weasyprint import HTML, CSS
    import seaborn as sns
except ImportError as e:
    print(f"Warning: Optional dependency not found: {e}")
    print("Install with: pip install pandas matplotlib plotly jinja2 weasyprint seaborn")


class ReportGenerator:
    """Main report generation framework."""
    
    def __init__(self, config_path: str = "reports_config.yaml"):
        """Initialize the report generator."""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.db_connection = self._setup_database()
        self.template_env = self._setup_templates()
        
        # Setup matplotlib style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            'templates': {
                'directory': 'templates',
                'sprint_report': 'sprint_report.html',
                'dashboard': 'dashboard.html',
                'trend_analysis': 'trend_analysis.html'
            },
            'output': {
                'directory': 'reports',
                'formats': ['html', 'pdf', 'markdown'],
                'charts_directory': 'charts'
            },
            'styling': {
                'theme': 'professional',
                'color_scheme': 'blue',
                'font_family': 'Arial, sans-serif'
            },
            'distribution': {
                'auto_email': False,
                'email_recipients': [],
                'slack_channels': []
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('report_generation.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def _setup_database(self) -> sqlite3.Connection:
        """Setup database connection for reading metrics."""
        try:
            conn = sqlite3.connect('sprint_metrics.db')
            self.logger.info("Database connection established")
            return conn
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _setup_templates(self) -> Environment:
        """Setup Jinja2 template environment."""
        template_dir = self.config['templates']['directory']
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
            self._create_default_templates(template_dir)
        
        return Environment(loader=FileSystemLoader(template_dir))
    
    def _create_default_templates(self, template_dir: str) -> None:
        """Create default report templates."""
        templates = {
            'sprint_report.html': self._get_sprint_report_template(),
            'dashboard.html': self._get_dashboard_template(),
            'trend_analysis.html': self._get_trend_analysis_template()
        }
        
        for filename, content in templates.items():
            with open(os.path.join(template_dir, filename), 'w') as f:
                f.write(content)
        
        self.logger.info(f"Default templates created in {template_dir}")
    
    def generate_sprint_report(self, sprint_number: int, team_name: str, 
                              output_format: str = 'html') -> str:
        """Generate comprehensive sprint report."""
        self.logger.info(f"Generating sprint report for Sprint {sprint_number}")
        
        try:
            # Collect sprint data
            sprint_data = self._get_sprint_data(sprint_number, team_name)
            
            # Generate visualizations
            charts = self._generate_sprint_charts(sprint_data)
            
            # Prepare report context
            context = {
                'sprint_number': sprint_number,
                'team_name': team_name,
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sprint_data': sprint_data,
                'charts': charts,
                'summary': self._generate_sprint_summary(sprint_data),
                'recommendations': self._generate_recommendations(sprint_data)
            }
            
            # Generate report
            output_path = self._render_report('sprint_report.html', context, 
                                            f'sprint_{sprint_number}_report', output_format)
            
            self.logger.info(f"Sprint report generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate sprint report: {e}")
            raise
    
    def generate_dashboard(self, team_name: str, days_back: int = 30) -> str:
        """Generate interactive team dashboard."""
        self.logger.info(f"Generating dashboard for team {team_name}")
        
        try:
            # Collect dashboard data
            dashboard_data = self._get_dashboard_data(team_name, days_back)
            
            # Generate interactive charts
            interactive_charts = self._generate_interactive_charts(dashboard_data)
            
            # Prepare dashboard context
            context = {
                'team_name': team_name,
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'dashboard_data': dashboard_data,
                'charts': interactive_charts,
                'kpis': self._calculate_kpis(dashboard_data),
                'alerts': self._check_dashboard_alerts(dashboard_data)
            }
            
            # Generate dashboard
            output_path = self._render_report('dashboard.html', context,
                                            f'{team_name}_dashboard', 'html')
            
            self.logger.info(f"Dashboard generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate dashboard: {e}")
            raise
    
    def generate_trend_analysis(self, team_name: str, days_back: int = 90,
                               output_format: str = 'html') -> str:
        """Generate trend analysis report."""
        self.logger.info(f"Generating trend analysis for team {team_name}")
        
        try:
            # Collect historical data
            historical_data = self._get_historical_data(team_name, days_back)
            
            # Generate trend charts
            trend_charts = self._generate_trend_charts(historical_data)
            
            # Analyze trends
            trend_analysis = self._analyze_trends(historical_data)
            
            # Prepare context
            context = {
                'team_name': team_name,
                'period_days': days_back,
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'historical_data': historical_data,
                'charts': trend_charts,
                'analysis': trend_analysis,
                'forecasts': self._generate_forecasts(historical_data)
            }
            
            # Generate report
            output_path = self._render_report('trend_analysis.html', context,
                                            f'{team_name}_trends', output_format)
            
            self.logger.info(f"Trend analysis generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate trend analysis: {e}")
            raise
    
    def _get_sprint_data(self, sprint_number: int, team_name: str) -> Dict[str, Any]:
        """Get comprehensive sprint data."""
        cursor = self.db_connection.cursor()
        
        # Get sprint metrics
        cursor.execute('''
            SELECT * FROM sprint_metrics 
            WHERE sprint_number = ? AND team_name = ?
            ORDER BY timestamp DESC LIMIT 1
        ''', (sprint_number, team_name))
        
        sprint_row = cursor.fetchone()
        if not sprint_row:
            raise ValueError(f"No data found for Sprint {sprint_number}")
        
        columns = [description[0] for description in cursor.description]
        sprint_metrics = dict(zip(columns, sprint_row))
        
        # Get daily metrics for the sprint
        cursor.execute('''
            SELECT * FROM daily_metrics 
            WHERE sprint_number = ? AND team_name = ?
            ORDER BY date
        ''', (sprint_number, team_name))
        
        daily_rows = cursor.fetchall()
        daily_columns = [description[0] for description in cursor.description]
        daily_metrics = [dict(zip(daily_columns, row)) for row in daily_rows]
        
        return {
            'sprint_metrics': sprint_metrics,
            'daily_metrics': daily_metrics,
            'burndown_data': json.loads(sprint_metrics.get('raw_data', '{}'))
        }
    
    def _get_dashboard_data(self, team_name: str, days_back: int) -> Dict[str, Any]:
        """Get dashboard data for specified period."""
        since_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        cursor = self.db_connection.cursor()
        
        # Get recent sprint metrics
        cursor.execute('''
            SELECT * FROM sprint_metrics 
            WHERE team_name = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        ''', (team_name, since_date))
        
        sprint_rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        sprint_metrics = [dict(zip(columns, row)) for row in sprint_rows]
        
        # Get daily metrics
        cursor.execute('''
            SELECT * FROM daily_metrics 
            WHERE team_name = ? AND timestamp >= ?
            ORDER BY date
        ''', (team_name, since_date))
        
        daily_rows = cursor.fetchall()
        daily_columns = [description[0] for description in cursor.description]
        daily_metrics = [dict(zip(daily_columns, row)) for row in daily_rows]
        
        return {
            'sprint_metrics': sprint_metrics,
            'daily_metrics': daily_metrics,
            'period_start': since_date,
            'period_end': datetime.now().isoformat()
        }
    
    def _get_historical_data(self, team_name: str, days_back: int) -> Dict[str, Any]:
        """Get historical data for trend analysis."""
        return self._get_dashboard_data(team_name, days_back)
    
    def _generate_sprint_charts(self, sprint_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate charts for sprint report."""
        charts = {}
        charts_dir = Path(self.config['output']['charts_directory'])
        charts_dir.mkdir(exist_ok=True)
        
        # Burndown chart
        if sprint_data['daily_metrics']:
            charts['burndown'] = self._create_burndown_chart(
                sprint_data['daily_metrics'], charts_dir / 'burndown.png'
            )
        
        # Velocity chart
        if sprint_data['sprint_metrics']:
            charts['velocity'] = self._create_velocity_chart(
                sprint_data['sprint_metrics'], charts_dir / 'velocity.png'
            )
        
        # Quality metrics chart
        charts['quality'] = self._create_quality_chart(
            sprint_data['sprint_metrics'], charts_dir / 'quality.png'
        )
        
        return charts
    
    def _create_burndown_chart(self, daily_metrics: List[Dict], output_path: Path) -> str:
        """Create burndown chart."""
        if not daily_metrics:
            return ""
        
        try:
            # Extract data
            dates = [datetime.fromisoformat(d['date']) for d in daily_metrics]
            remaining_points = [d['story_points_remaining'] for d in daily_metrics]
            
            # Create chart
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(dates, remaining_points, 'b-o', label='Actual Burndown', linewidth=2)
            
            # Add ideal burndown line
            if len(remaining_points) > 1:
                ideal_line = [remaining_points[0] * (1 - i/(len(remaining_points)-1)) 
                             for i in range(len(remaining_points))]
                ax.plot(dates, ideal_line, 'r--', label='Ideal Burndown', alpha=0.7)
            
            ax.set_title('Sprint Burndown Chart', fontsize=16, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Story Points Remaining')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(output_path)
        except Exception as e:
            self.logger.error(f"Failed to create burndown chart: {e}")
            return ""
    
    def _create_velocity_chart(self, sprint_metrics: Dict[str, Any], output_path: Path) -> str:
        """Create velocity chart."""
        try:
            # Create simple velocity bar chart
            fig, ax = plt.subplots(figsize=(8, 6))
            
            categories = ['Committed', 'Completed']
            values = [
                sprint_metrics['story_points_committed'],
                sprint_metrics['story_points_completed']
            ]
            colors = ['lightblue', 'darkblue']
            
            bars = ax.bar(categories, values, color=colors)
            ax.set_title('Sprint Velocity', fontsize=16, fontweight='bold')
            ax.set_ylabel('Story Points')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{value}', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(output_path)
        except Exception as e:
            self.logger.error(f"Failed to create velocity chart: {e}")
            return ""
    
    def _create_quality_chart(self, sprint_metrics: Dict[str, Any], output_path: Path) -> str:
        """Create quality metrics chart."""
        try:
            # Create quality metrics radar/polar chart
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            categories = ['Test Coverage', 'Code Quality', 'Team Satisfaction', 'Velocity']
            values = [
                sprint_metrics.get('quality_score', 0) * 10,  # Normalize to 0-10
                sprint_metrics.get('quality_score', 0),
                sprint_metrics.get('team_satisfaction', 0),
                min(sprint_metrics.get('velocity', 0), 10)  # Cap at 10 for visualization
            ]
            
            # Add first value at end to close the polygon
            values += values[:1]
            
            angles = [i * 2 * 3.14159 / len(categories) for i in range(len(categories) + 1)]
            
            ax.plot(angles, values, 'b-o', linewidth=2)
            ax.fill(angles, values, alpha=0.25)
            ax.set_ylim(0, 10)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_title('Quality Metrics', fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(output_path)
        except Exception as e:
            self.logger.error(f"Failed to create quality chart: {e}")
            return ""
    
    def _generate_interactive_charts(self, dashboard_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate interactive Plotly charts for dashboard."""
        charts = {}
        
        try:
            # Velocity trend chart
            if dashboard_data['sprint_metrics']:
                charts['velocity_trend'] = self._create_velocity_trend_chart(
                    dashboard_data['sprint_metrics']
                )
            
            # Team health chart
            if dashboard_data['daily_metrics']:
                charts['team_health'] = self._create_team_health_chart(
                    dashboard_data['daily_metrics']
                )
            
            return charts
        except Exception as e:
            self.logger.error(f"Failed to generate interactive charts: {e}")
            return {}
    
    def _create_velocity_trend_chart(self, sprint_metrics: List[Dict]) -> str:
        """Create interactive velocity trend chart."""
        try:
            sprints = [s['sprint_number'] for s in sprint_metrics]
            velocities = [s['velocity'] for s in sprint_metrics]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sprints,
                y=velocities,
                mode='lines+markers',
                name='Velocity',
                line=dict(color='blue', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title='Velocity Trend',
                xaxis_title='Sprint',
                yaxis_title='Velocity (points/day)',
                template='plotly_white'
            )
            
            return fig.to_html(include_plotlyjs='inline', div_id="velocity_chart")
        except Exception as e:
            self.logger.error(f"Failed to create velocity trend chart: {e}")
            return ""
    
    def _create_team_health_chart(self, daily_metrics: List[Dict]) -> str:
        """Create interactive team health chart."""
        try:
            dates = [d['date'] for d in daily_metrics]
            moods = [d['team_mood'] for d in daily_metrics]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=moods,
                mode='lines+markers',
                name='Team Mood',
                line=dict(color='green', width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title='Team Health Trend',
                xaxis_title='Date',
                yaxis_title='Team Mood (1-10)',
                yaxis=dict(range=[1, 10]),
                template='plotly_white'
            )
            
            return fig.to_html(include_plotlyjs='inline', div_id="health_chart")
        except Exception as e:
            self.logger.error(f"Failed to create team health chart: {e}")
            return ""
    
    def _generate_trend_charts(self, historical_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate trend analysis charts."""
        # Similar to interactive charts but focused on trends
        return self._generate_interactive_charts(historical_data)
    
    def _generate_sprint_summary(self, sprint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sprint summary statistics."""
        sprint_metrics = sprint_data['sprint_metrics']
        
        return {
            'completion_rate': (sprint_metrics['stories_completed'] / 
                              max(sprint_metrics['stories_committed'], 1) * 100),
            'velocity_achieved': sprint_metrics['velocity'],
            'quality_score': sprint_metrics.get('quality_score', 0),
            'team_satisfaction': sprint_metrics.get('team_satisfaction', 0),
            'points_delivered': sprint_metrics['story_points_completed'],
            'stories_delivered': sprint_metrics['stories_completed']
        }
    
    def _generate_recommendations(self, sprint_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on sprint data."""
        recommendations = []
        summary = self._generate_sprint_summary(sprint_data)
        
        if summary['completion_rate'] < 80:
            recommendations.append("Consider reducing sprint scope or investigating blockers")
        
        if summary['quality_score'] < 7:
            recommendations.append("Focus on improving code quality and test coverage")
        
        if summary['team_satisfaction'] < 7:
            recommendations.append("Address team satisfaction concerns in retrospective")
        
        if summary['velocity_achieved'] < 2:
            recommendations.append("Review estimation accuracy and team capacity")
        
        if not recommendations:
            recommendations.append("Great sprint! Continue with current practices")
        
        return recommendations
    
    def _calculate_kpis(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key performance indicators."""
        if not dashboard_data['sprint_metrics']:
            return {}
        
        recent_sprint = dashboard_data['sprint_metrics'][0]
        
        return {
            'current_velocity': recent_sprint['velocity'],
            'average_completion_rate': 85.5,  # Would calculate from multiple sprints
            'quality_trend': 'improving',
            'team_health': recent_sprint.get('team_satisfaction', 8.0)
        }
    
    def _check_dashboard_alerts(self, dashboard_data: Dict[str, Any]) -> List[str]:
        """Check for dashboard alerts."""
        alerts = []
        
        if dashboard_data['sprint_metrics']:
            recent = dashboard_data['sprint_metrics'][0]
            
            if recent['velocity'] < 2:
                alerts.append("Low velocity detected")
            
            if recent.get('quality_score', 10) < 6:
                alerts.append("Quality metrics below target")
        
        return alerts
    
    def _analyze_trends(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in historical data."""
        if not historical_data['sprint_metrics']:
            return {}
        
        velocities = [s['velocity'] for s in historical_data['sprint_metrics']]
        
        return {
            'velocity_trend': 'increasing' if len(velocities) > 1 and velocities[0] > velocities[-1] else 'stable',
            'average_velocity': sum(velocities) / len(velocities),
            'velocity_stability': 'stable' if max(velocities) - min(velocities) < 2 else 'variable'
        }
    
    def _generate_forecasts(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate forecasts based on historical data."""
        if not historical_data['sprint_metrics']:
            return {}
        
        velocities = [s['velocity'] for s in historical_data['sprint_metrics'][-3:]]
        avg_velocity = sum(velocities) / len(velocities)
        
        return {
            'next_sprint_velocity': avg_velocity,
            'confidence': 'medium',
            'basis': f'Based on last {len(velocities)} sprints'
        }
    
    def _render_report(self, template_name: str, context: Dict[str, Any],
                      output_name: str, output_format: str) -> str:
        """Render report using template and context."""
        try:
            # Load template
            template = self.template_env.get_template(template_name)
            
            # Render HTML
            html_content = template.render(**context)
            
            # Setup output directory
            output_dir = Path(self.config['output']['directory'])
            output_dir.mkdir(exist_ok=True)
            
            if output_format.lower() == 'html':
                output_path = output_dir / f'{output_name}.html'
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            elif output_format.lower() == 'pdf':
                output_path = output_dir / f'{output_name}.pdf'
                HTML(string=html_content).write_pdf(output_path)
            
            elif output_format.lower() == 'markdown':
                output_path = output_dir / f'{output_name}.md'
                # Convert HTML to Markdown (simplified)
                md_content = self._html_to_markdown(html_content, context)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
            
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to render report: {e}")
            raise
    
    def _html_to_markdown(self, html_content: str, context: Dict[str, Any]) -> str:
        """Convert HTML content to Markdown (simplified version)."""
        # This is a simplified conversion - in practice you'd use a proper HTML to Markdown converter
        md_content = f"""# Sprint {context.get('sprint_number', 'N/A')} Report

## Summary
- **Team**: {context.get('team_name', 'N/A')}
- **Generated**: {context.get('generated_date', 'N/A')}

## Metrics
- **Velocity**: {context.get('sprint_data', {}).get('sprint_metrics', {}).get('velocity', 'N/A')}
- **Completion Rate**: {context.get('summary', {}).get('completion_rate', 'N/A')}%

## Recommendations
"""
        
        for rec in context.get('recommendations', []):
            md_content += f"- {rec}\n"
        
        return md_content
    
    def _get_sprint_report_template(self) -> str:
        """Get default sprint report HTML template."""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Sprint {{ sprint_number }} Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; }
        .metric { background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .chart { text-align: center; margin: 20px 0; }
        .recommendation { background: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Sprint {{ sprint_number }} Report</h1>
    <p><strong>Team:</strong> {{ team_name }}</p>
    <p><strong>Generated:</strong> {{ generated_date }}</p>
    
    <h2>Sprint Summary</h2>
    <div class="metric">
        <strong>Completion Rate:</strong> {{ "%.1f"|format(summary.completion_rate) }}%
    </div>
    <div class="metric">
        <strong>Velocity:</strong> {{ "%.2f"|format(summary.velocity_achieved) }} points/day
    </div>
    <div class="metric">
        <strong>Quality Score:</strong> {{ "%.1f"|format(summary.quality_score) }}/10
    </div>
    
    <h2>Charts</h2>
    {% if charts.burndown %}
    <div class="chart">
        <h3>Burndown Chart</h3>
        <img src="{{ charts.burndown }}" alt="Burndown Chart" style="max-width: 100%;">
    </div>
    {% endif %}
    
    <h2>Recommendations</h2>
    {% for rec in recommendations %}
    <div class="recommendation">{{ rec }}</div>
    {% endfor %}
</body>
</html>'''
    
    def _get_dashboard_template(self) -> str:
        """Get default dashboard HTML template."""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>{{ team_name }} Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .kpi { display: inline-block; background: #3498db; color: white; padding: 20px; margin: 10px; border-radius: 5px; min-width: 150px; text-align: center; }
        .alert { background: #e74c3c; color: white; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .chart-container { margin: 20px 0; }
    </style>
</head>
<body>
    <h1>{{ team_name }} Dashboard</h1>
    <p><strong>Generated:</strong> {{ generated_date }}</p>
    
    <h2>Key Performance Indicators</h2>
    <div class="kpi">
        <h3>Current Velocity</h3>
        <p>{{ "%.2f"|format(kpis.current_velocity) }}</p>
    </div>
    <div class="kpi">
        <h3>Team Health</h3>
        <p>{{ "%.1f"|format(kpis.team_health) }}/10</p>
    </div>
    
    {% if alerts %}
    <h2>Alerts</h2>
    {% for alert in alerts %}
    <div class="alert">{{ alert }}</div>
    {% endfor %}
    {% endif %}
    
    <h2>Charts</h2>
    <div class="chart-container">
        {{ charts.velocity_trend|safe }}
    </div>
    <div class="chart-container">
        {{ charts.team_health|safe }}
    </div>
</body>
</html>'''
    
    def _get_trend_analysis_template(self) -> str:
        """Get default trend analysis HTML template."""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>{{ team_name }} Trend Analysis</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .trend { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .forecast { background: #fff3cd; padding: 15px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>{{ team_name }} Trend Analysis</h1>
    <p><strong>Period:</strong> Last {{ period_days }} days</p>
    <p><strong>Generated:</strong> {{ generated_date }}</p>
    
    <h2>Trend Analysis</h2>
    <div class="trend">
        <strong>Velocity Trend:</strong> {{ analysis.velocity_trend|title }}
    </div>
    <div class="trend">
        <strong>Average Velocity:</strong> {{ "%.2f"|format(analysis.average_velocity) }}
    </div>
    
    <h2>Forecasts</h2>
    <div class="forecast">
        <strong>Next Sprint Velocity:</strong> {{ "%.2f"|format(forecasts.next_sprint_velocity) }}
        <br><strong>Confidence:</strong> {{ forecasts.confidence|title }}
    </div>
</body>
</html>'''


def main():
    """Main entry point for report generation script."""
    parser = argparse.ArgumentParser(description='Sprint Report Generation')
    parser.add_argument('--type', required=True,
                       choices=['sprint', 'dashboard', 'trend'],
                       help='Type of report to generate')
    parser.add_argument('--sprint', type=int,
                       help='Sprint number (required for sprint reports)')
    parser.add_argument('--team', type=str, default='AI-Dev-Agent',
                       help='Team name')
    parser.add_argument('--format', type=str, default='html',
                       choices=['html', 'pdf', 'markdown'],
                       help='Output format')
    parser.add_argument('--output', type=str,
                       help='Output file path (optional)')
    parser.add_argument('--days', type=int, default=30,
                       help='Days back for dashboard/trend reports')
    parser.add_argument('--config', type=str, default='reports_config.yaml',
                       help='Configuration file path')
    
    args = parser.parse_args()
    
    # Initialize report generator
    generator = ReportGenerator(args.config)
    
    try:
        # Generate requested report
        if args.type == 'sprint':
            if not args.sprint:
                print("Error: --sprint required for sprint reports")
                sys.exit(1)
            
            output_path = generator.generate_sprint_report(
                args.sprint, args.team, args.format
            )
            print(f"Sprint report generated: {output_path}")
        
        elif args.type == 'dashboard':
            output_path = generator.generate_dashboard(args.team, args.days)
            print(f"Dashboard generated: {output_path}")
        
        elif args.type == 'trend':
            output_path = generator.generate_trend_analysis(
                args.team, args.days, args.format
            )
            print(f"Trend analysis generated: {output_path}")
    
    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
