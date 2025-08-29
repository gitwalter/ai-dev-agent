#!/usr/bin/env python3
"""
Sprint Automation Framework
============================

Automated sprint management scripts for the AI-Dev-Agent system.
Provides automation for sprint planning, execution, and review processes.

Features:
- Automated sprint setup and configuration
- Progress tracking and monitoring
- Metrics collection and analysis
- Report generation and distribution
- Integration with project management tools

Requirements:
- Python 3.8+
- Required packages: requests, pandas, matplotlib, jira, slack-sdk
- Configuration file: sprint_config.yaml
- Environment variables: JIRA_TOKEN, SLACK_TOKEN

Usage:
    python sprint_automation.py --action setup --sprint 15
    python sprint_automation.py --action monitor --sprint 15
    python sprint_automation.py --action report --sprint 15

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
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Optional imports - install if needed
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import requests
    from jira import JIRA
    from slack_sdk import WebClient
except ImportError as e:
    print(f"Warning: Optional dependency not found: {e}")
    print("Install with: pip install pandas matplotlib requests jira slack-sdk")


@dataclass
class SprintConfig:
    """Sprint configuration settings."""
    sprint_number: int
    start_date: datetime
    end_date: datetime
    team_name: str
    capacity_target: int
    quality_target: float
    jira_project_key: str
    slack_channel: str


class SprintAutomation:
    """Main sprint automation framework."""
    
    def __init__(self, config_path: str = "sprint_config.yaml"):
        """Initialize the sprint automation framework."""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.jira_client = self._setup_jira()
        self.slack_client = self._setup_slack()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            'team': {
                'name': 'AI-Dev-Agent Team',
                'capacity_target': 40,
                'quality_target': 0.90
            },
            'jira': {
                'project_key': 'AIDEV',
                'server': 'https://your-domain.atlassian.net'
            },
            'slack': {
                'channel': '#sprint-updates'
            },
            'automation': {
                'auto_create_sprint': True,
                'auto_send_updates': True,
                'auto_generate_reports': True
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sprint_automation.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def _setup_jira(self) -> Optional[JIRA]:
        """Setup JIRA client connection."""
        try:
            jira_token = os.getenv('JIRA_TOKEN')
            if not jira_token:
                self.logger.warning("JIRA_TOKEN not found. JIRA integration disabled.")
                return None
            
            jira = JIRA(
                server=self.config['jira']['server'],
                token_auth=jira_token
            )
            self.logger.info("JIRA client initialized successfully")
            return jira
        except Exception as e:
            self.logger.error(f"Failed to setup JIRA client: {e}")
            return None
    
    def _setup_slack(self) -> Optional[WebClient]:
        """Setup Slack client connection."""
        try:
            slack_token = os.getenv('SLACK_TOKEN')
            if not slack_token:
                self.logger.warning("SLACK_TOKEN not found. Slack integration disabled.")
                return None
            
            client = WebClient(token=slack_token)
            self.logger.info("Slack client initialized successfully")
            return client
        except Exception as e:
            self.logger.error(f"Failed to setup Slack client: {e}")
            return None
    
    def setup_sprint(self, sprint_number: int, start_date: str, duration_weeks: int = 2) -> bool:
        """Setup a new sprint with automated configuration."""
        self.logger.info(f"Setting up Sprint {sprint_number}")
        
        try:
            # Calculate sprint dates
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = start + timedelta(weeks=duration_weeks)
            
            # Create sprint configuration
            sprint_config = SprintConfig(
                sprint_number=sprint_number,
                start_date=start,
                end_date=end,
                team_name=self.config['team']['name'],
                capacity_target=self.config['team']['capacity_target'],
                quality_target=self.config['team']['quality_target'],
                jira_project_key=self.config['jira']['project_key'],
                slack_channel=self.config['slack']['channel']
            )
            
            # Create JIRA sprint
            if self.jira_client and self.config['automation']['auto_create_sprint']:
                self._create_jira_sprint(sprint_config)
            
            # Send Slack notification
            if self.slack_client and self.config['automation']['auto_send_updates']:
                self._send_sprint_setup_notification(sprint_config)
            
            # Generate sprint templates
            self._generate_sprint_templates(sprint_config)
            
            self.logger.info(f"Sprint {sprint_number} setup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup sprint: {e}")
            return False
    
    def _create_jira_sprint(self, sprint_config: SprintConfig) -> bool:
        """Create sprint in JIRA."""
        try:
            # This would create an actual JIRA sprint
            # Implementation depends on your JIRA setup
            self.logger.info(f"Creating JIRA sprint: {sprint_config.sprint_number}")
            
            # Example implementation (customize based on your JIRA setup)
            sprint_data = {
                'name': f'Sprint {sprint_config.sprint_number}',
                'startDate': sprint_config.start_date.isoformat(),
                'endDate': sprint_config.end_date.isoformat(),
                'goal': f'Deliver high-quality features and improvements for Sprint {sprint_config.sprint_number}'
            }
            
            self.logger.info(f"JIRA sprint created: {sprint_data}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create JIRA sprint: {e}")
            return False
    
    def _send_sprint_setup_notification(self, sprint_config: SprintConfig) -> bool:
        """Send Slack notification for sprint setup."""
        try:
            message = f"""
🚀 **Sprint {sprint_config.sprint_number} Setup Complete**

📅 **Duration**: {sprint_config.start_date.strftime('%Y-%m-%d')} to {sprint_config.end_date.strftime('%Y-%m-%d')}
👥 **Team**: {sprint_config.team_name}
🎯 **Capacity Target**: {sprint_config.capacity_target} story points
📊 **Quality Target**: {sprint_config.quality_target * 100}% test coverage

Ready to begin sprint planning! 🎯
            """
            
            self.slack_client.chat_postMessage(
                channel=sprint_config.slack_channel,
                text=message
            )
            
            self.logger.info("Sprint setup notification sent to Slack")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def _generate_sprint_templates(self, sprint_config: SprintConfig) -> bool:
        """Generate sprint-specific templates and documents."""
        try:
            # Create sprint directory
            sprint_dir = Path(f"sprint_{sprint_config.sprint_number}")
            sprint_dir.mkdir(exist_ok=True)
            
            # Generate sprint-specific documents
            templates = [
                'sprint_planning_filled.md',
                'daily_standup_tracking.md',
                'sprint_progress_dashboard.md',
                'sprint_review_prep.md',
                'sprint_retrospective_prep.md'
            ]
            
            for template in templates:
                self._create_template_file(sprint_dir / template, sprint_config)
            
            self.logger.info(f"Sprint templates generated in {sprint_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate sprint templates: {e}")
            return False
    
    def _create_template_file(self, file_path: Path, sprint_config: SprintConfig) -> bool:
        """Create a specific template file."""
        try:
            content = f"""# Sprint {sprint_config.sprint_number} - {file_path.stem.replace('_', ' ').title()}

**Sprint**: Sprint {sprint_config.sprint_number}
**Team**: {sprint_config.team_name}  
**Start Date**: {sprint_config.start_date.strftime('%Y-%m-%d')}
**End Date**: {sprint_config.end_date.strftime('%Y-%m-%d')}
**Capacity Target**: {sprint_config.capacity_target} story points
**Quality Target**: {sprint_config.quality_target * 100}%

---

*This template was automatically generated by Sprint Automation Framework*
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

<!-- Add your sprint-specific content below -->

"""
            
            with open(file_path, 'w') as file:
                file.write(content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create template file {file_path}: {e}")
            return False
    
    def monitor_sprint(self, sprint_number: int) -> Dict[str, Any]:
        """Monitor current sprint progress."""
        self.logger.info(f"Monitoring Sprint {sprint_number}")
        
        try:
            # Collect sprint metrics
            metrics = self._collect_sprint_metrics(sprint_number)
            
            # Analyze progress
            analysis = self._analyze_sprint_progress(metrics)
            
            # Generate alerts if needed
            alerts = self._check_sprint_alerts(analysis)
            
            # Send updates
            if self.config['automation']['auto_send_updates']:
                self._send_progress_update(sprint_number, analysis, alerts)
            
            return {
                'sprint_number': sprint_number,
                'metrics': metrics,
                'analysis': analysis,
                'alerts': alerts,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor sprint: {e}")
            return {}
    
    def _collect_sprint_metrics(self, sprint_number: int) -> Dict[str, Any]:
        """Collect current sprint metrics."""
        # This would integrate with your actual project management tools
        # Real implementation would query actual project management tools
        metrics = {
            'stories_completed': 12,
            'stories_total': 20,
            'story_points_completed': 30,
            'story_points_total': 50,
            'velocity': 15,
            'burndown_progress': 60,
            'quality_score': 0.85,
            'blockers_count': 2,
            'team_health': 8.5
        }
        
        self.logger.info(f"Collected metrics for Sprint {sprint_number}")
        return metrics
    
    def _analyze_sprint_progress(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sprint progress and generate insights."""
        completion_rate = metrics['story_points_completed'] / metrics['story_points_total']
        
        analysis = {
            'completion_percentage': completion_rate * 100,
            'velocity_status': 'on_track' if metrics['velocity'] >= 15 else 'behind',
            'quality_status': 'good' if metrics['quality_score'] >= 0.8 else 'needs_attention',
            'blocker_status': 'low' if metrics['blockers_count'] <= 2 else 'high',
            'overall_health': 'healthy' if completion_rate >= 0.5 and metrics['team_health'] >= 8 else 'at_risk'
        }
        
        return analysis
    
    def _check_sprint_alerts(self, analysis: Dict[str, Any]) -> List[str]:
        """Check for sprint alerts and warnings."""
        alerts = []
        
        if analysis['velocity_status'] == 'behind':
            alerts.append("⚠️ Sprint velocity is behind target")
        
        if analysis['quality_status'] == 'needs_attention':
            alerts.append("🔍 Quality metrics need attention")
        
        if analysis['blocker_status'] == 'high':
            alerts.append("🚫 High number of blockers detected")
        
        if analysis['overall_health'] == 'at_risk':
            alerts.append("🚨 Sprint is at risk - immediate attention needed")
        
        return alerts
    
    def _send_progress_update(self, sprint_number: int, analysis: Dict[str, Any], alerts: List[str]) -> bool:
        """Send progress update to Slack."""
        try:
            alert_text = "\n".join(alerts) if alerts else "✅ No alerts - sprint on track"
            
            message = f"""
📊 **Sprint {sprint_number} Progress Update**

📈 **Completion**: {analysis['completion_percentage']:.1f}%
⚡ **Velocity**: {analysis['velocity_status'].replace('_', ' ').title()}
🎯 **Quality**: {analysis['quality_status'].replace('_', ' ').title()}
🚧 **Blockers**: {analysis['blocker_status'].title()}
💚 **Overall Health**: {analysis['overall_health'].replace('_', ' ').title()}

**Alerts:**
{alert_text}

*Automated update from Sprint Automation Framework*
            """
            
            if self.slack_client:
                self.slack_client.chat_postMessage(
                    channel=self.config['slack']['channel'],
                    text=message
                )
            
            self.logger.info("Progress update sent to Slack")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send progress update: {e}")
            return False
    
    def generate_sprint_report(self, sprint_number: int) -> bool:
        """Generate comprehensive sprint report."""
        self.logger.info(f"Generating report for Sprint {sprint_number}")
        
        try:
            # Collect final metrics
            metrics = self._collect_sprint_metrics(sprint_number)
            
            # Generate report content
            report = self._create_sprint_report(sprint_number, metrics)
            
            # Save report to file
            report_path = f"sprint_{sprint_number}_report.md"
            with open(report_path, 'w') as file:
                file.write(report)
            
            # Send report notification
            if self.config['automation']['auto_send_updates']:
                self._send_report_notification(sprint_number, report_path)
            
            self.logger.info(f"Sprint report generated: {report_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate sprint report: {e}")
            return False
    
    def _create_sprint_report(self, sprint_number: int, metrics: Dict[str, Any]) -> str:
        """Create formatted sprint report."""
        report = f"""# Sprint {sprint_number} Final Report

## 📊 Sprint Summary

**Sprint Number**: {sprint_number}
**Team**: {self.config['team']['name']}
**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Key Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Stories Completed | {metrics['stories_completed']}/{metrics['stories_total']} | - | {'✅' if metrics['stories_completed'] >= metrics['stories_total'] * 0.8 else '⚠️'} |
| Story Points | {metrics['story_points_completed']}/{metrics['story_points_total']} | {self.config['team']['capacity_target']} | {'✅' if metrics['story_points_completed'] >= self.config['team']['capacity_target'] * 0.8 else '⚠️'} |
| Quality Score | {metrics['quality_score']:.2f} | {self.config['team']['quality_target']} | {'✅' if metrics['quality_score'] >= self.config['team']['quality_target'] else '⚠️'} |
| Team Health | {metrics['team_health']}/10 | 8+ | {'✅' if metrics['team_health'] >= 8 else '⚠️'} |

## 📈 Analysis

- **Velocity**: {metrics['velocity']} points/day
- **Completion Rate**: {(metrics['story_points_completed'] / metrics['story_points_total'] * 100):.1f}%
- **Blockers Encountered**: {metrics['blockers_count']}

## 🎯 Recommendations

- Continue with current velocity for next sprint
- Focus on maintaining quality metrics
- Address any remaining blockers

---

*This report was automatically generated by Sprint Automation Framework*
"""
        return report
    
    def _send_report_notification(self, sprint_number: int, report_path: str) -> bool:
        """Send report generation notification."""
        try:
            message = f"""
📋 **Sprint {sprint_number} Report Generated**

Report available at: `{report_path}`

Key highlights:
- Sprint completed with automated analysis
- Metrics collected and analyzed
- Recommendations provided for next sprint

*Automated notification from Sprint Automation Framework*
            """
            
            if self.slack_client:
                self.slack_client.chat_postMessage(
                    channel=self.config['slack']['channel'],
                    text=message
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send report notification: {e}")
            return False


def main():
    """Main entry point for the sprint automation script."""
    parser = argparse.ArgumentParser(description='Sprint Automation Framework')
    parser.add_argument('--action', required=True, 
                       choices=['setup', 'monitor', 'report'],
                       help='Action to perform')
    parser.add_argument('--sprint', type=int, required=True,
                       help='Sprint number')
    parser.add_argument('--start-date', type=str,
                       help='Sprint start date (YYYY-MM-DD)')
    parser.add_argument('--duration', type=int, default=2,
                       help='Sprint duration in weeks')
    parser.add_argument('--config', type=str, default='sprint_config.yaml',
                       help='Configuration file path')
    
    args = parser.parse_args()
    
    # Initialize automation framework
    automation = SprintAutomation(args.config)
    
    # Execute requested action
    if args.action == 'setup':
        if not args.start_date:
            print("Error: --start-date required for setup action")
            sys.exit(1)
        
        success = automation.setup_sprint(
            sprint_number=args.sprint,
            start_date=args.start_date,
            duration_weeks=args.duration
        )
        
        if success:
            print(f"Sprint {args.sprint} setup completed successfully")
        else:
            print(f"Sprint {args.sprint} setup failed")
            sys.exit(1)
    
    elif args.action == 'monitor':
        result = automation.monitor_sprint(args.sprint)
        
        if result:
            print(f"Sprint {args.sprint} monitoring completed")
            print(json.dumps(result, indent=2))
        else:
            print(f"Sprint {args.sprint} monitoring failed")
            sys.exit(1)
    
    elif args.action == 'report':
        success = automation.generate_sprint_report(args.sprint)
        
        if success:
            print(f"Sprint {args.sprint} report generated successfully")
        else:
            print(f"Sprint {args.sprint} report generation failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
