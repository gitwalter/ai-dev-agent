#!/usr/bin/env python3
"""
Proactive Alerting System for AI-Dev-Agent Health Monitoring.

Provides advanced alerting capabilities including:
- Predictive health degradation detection
- Multi-channel notifications (email, webhook, slack)
- Alert escalation and suppression
- Smart alert correlation and deduplication
- Recovery notifications and status updates

Part of US-001: Automated System Health Monitoring implementation.
"""

import asyncio
import json
import logging
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import aiohttp
import streamlit as st

from utils.system_health_monitor import (
    HealthAlert,
    AlertLevel,
    HealthStatus,
    AgentHealthMetrics
)


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    CONSOLE = "console"
    FILE = "file"


class EscalationLevel(str, Enum):
    """Alert escalation levels."""
    LEVEL_1 = "level_1"  # Initial alert
    LEVEL_2 = "level_2"  # Manager escalation
    LEVEL_3 = "level_3"  # Executive escalation
    LEVEL_4 = "level_4"  # Emergency escalation


@dataclass
class NotificationConfig:
    """Configuration for notification channels."""
    channel: NotificationChannel
    enabled: bool = True
    endpoint: Optional[str] = None
    credentials: Dict[str, str] = field(default_factory=dict)
    template: Optional[str] = None
    retry_count: int = 3
    retry_delay: int = 30  # seconds


@dataclass
class EscalationRule:
    """Alert escalation rule configuration."""
    alert_level: AlertLevel
    escalation_delay: int  # minutes
    escalation_level: EscalationLevel
    notification_channels: List[NotificationChannel]
    suppress_after: int = 60  # minutes


@dataclass
class AlertPattern:
    """Pattern for smart alert correlation."""
    pattern_id: str
    pattern_type: str  # "sequence", "frequency", "threshold"
    conditions: Dict[str, Any]
    correlation_window: int  # minutes
    action: str  # "suppress", "escalate", "correlate"


class SmartAlertProcessor:
    """
    Smart alert processing with correlation and deduplication.
    
    Implements intelligent alert handling to reduce noise and
    improve signal-to-noise ratio in alerts.
    """
    
    def __init__(self):
        """Initialize smart alert processor."""
        self.logger = logging.getLogger(__name__)
        self.alert_history: List[HealthAlert] = []
        self.correlation_patterns: List[AlertPattern] = []
        self.suppressed_alerts: Dict[str, datetime] = {}
        
        # Load correlation patterns
        self._load_correlation_patterns()
    
    def _load_correlation_patterns(self):
        """Load alert correlation patterns."""
        # Define common correlation patterns
        self.correlation_patterns = [
            AlertPattern(
                pattern_id="agent_cascade_failure",
                pattern_type="sequence",
                conditions={
                    "alert_count": 3,
                    "time_window": 5,  # minutes
                    "same_agent": True
                },
                correlation_window=10,
                action="correlate"
            ),
            AlertPattern(
                pattern_id="system_wide_degradation",
                pattern_type="frequency",
                conditions={
                    "alert_count": 5,
                    "time_window": 10,  # minutes
                    "min_agents": 3
                },
                correlation_window=15,
                action="escalate"
            ),
            AlertPattern(
                pattern_id="flapping_agent",
                pattern_type="frequency",
                conditions={
                    "alert_count": 10,
                    "time_window": 30,  # minutes
                    "same_agent": True,
                    "alternating_states": True
                },
                correlation_window=60,
                action="suppress"
            )
        ]
    
    def process_alert(self, alert: HealthAlert) -> Dict[str, Any]:
        """
        Process alert through smart correlation and deduplication.
        
        Args:
            alert: Health alert to process
            
        Returns:
            Processing result with actions to take
        """
        # Check if alert should be suppressed
        if self._should_suppress_alert(alert):
            return {
                "action": "suppress",
                "reason": "duplicate_or_suppressed",
                "original_alert": alert
            }
        
        # Check for correlation patterns
        correlation_result = self._check_correlation_patterns(alert)
        if correlation_result:
            return correlation_result
        
        # Add to history
        self.alert_history.append(alert)
        
        # Clean old history (keep last 1000 alerts)
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        return {
            "action": "process",
            "alert": alert,
            "enhanced": False
        }
    
    def _should_suppress_alert(self, alert: HealthAlert) -> bool:
        """Check if alert should be suppressed."""
        # Check suppression list
        alert_key = f"{alert.agent_name}_{alert.level}_{alert.message}"
        
        if alert_key in self.suppressed_alerts:
            suppress_until = self.suppressed_alerts[alert_key]
            if datetime.now() < suppress_until:
                return True
            else:
                # Remove expired suppression
                del self.suppressed_alerts[alert_key]
        
        # Check for duplicate in recent history (last 10 minutes)
        recent_cutoff = datetime.now() - timedelta(minutes=10)
        recent_alerts = [a for a in self.alert_history if a.timestamp > recent_cutoff]
        
        for recent_alert in recent_alerts:
            if (recent_alert.agent_name == alert.agent_name and
                recent_alert.level == alert.level and
                recent_alert.message == alert.message):
                return True
        
        return False
    
    def _check_correlation_patterns(self, alert: HealthAlert) -> Optional[Dict[str, Any]]:
        """Check alert against correlation patterns."""
        for pattern in self.correlation_patterns:
            if self._matches_pattern(alert, pattern):
                return self._apply_pattern_action(alert, pattern)
        return None
    
    def _matches_pattern(self, alert: HealthAlert, pattern: AlertPattern) -> bool:
        """Check if alert matches correlation pattern."""
        if pattern.pattern_type == "sequence":
            return self._check_sequence_pattern(alert, pattern)
        elif pattern.pattern_type == "frequency":
            return self._check_frequency_pattern(alert, pattern)
        elif pattern.pattern_type == "threshold":
            return self._check_threshold_pattern(alert, pattern)
        return False
    
    def _check_sequence_pattern(self, alert: HealthAlert, pattern: AlertPattern) -> bool:
        """Check sequence-based correlation pattern."""
        conditions = pattern.conditions
        time_window = timedelta(minutes=conditions.get("time_window", 5))
        cutoff_time = datetime.now() - time_window
        
        recent_alerts = [a for a in self.alert_history if a.timestamp > cutoff_time]
        
        if conditions.get("same_agent"):
            recent_alerts = [a for a in recent_alerts if a.agent_name == alert.agent_name]
        
        return len(recent_alerts) >= conditions.get("alert_count", 3)
    
    def _check_frequency_pattern(self, alert: HealthAlert, pattern: AlertPattern) -> bool:
        """Check frequency-based correlation pattern."""
        conditions = pattern.conditions
        time_window = timedelta(minutes=conditions.get("time_window", 10))
        cutoff_time = datetime.now() - time_window
        
        recent_alerts = [a for a in self.alert_history if a.timestamp > cutoff_time]
        
        if conditions.get("same_agent"):
            recent_alerts = [a for a in recent_alerts if a.agent_name == alert.agent_name]
        
        # Check minimum number of affected agents
        if conditions.get("min_agents"):
            affected_agents = set(a.agent_name for a in recent_alerts)
            if len(affected_agents) < conditions.get("min_agents"):
                return False
        
        return len(recent_alerts) >= conditions.get("alert_count", 5)
    
    def _check_threshold_pattern(self, alert: HealthAlert, pattern: AlertPattern) -> bool:
        """Check threshold-based correlation pattern."""
        # Implementation for threshold patterns
        return False
    
    def _apply_pattern_action(self, alert: HealthAlert, pattern: AlertPattern) -> Dict[str, Any]:
        """Apply action based on matched pattern."""
        if pattern.action == "suppress":
            # Suppress similar alerts for correlation window
            alert_key = f"{alert.agent_name}_{alert.level}_{alert.message}"
            suppress_until = datetime.now() + timedelta(minutes=pattern.correlation_window)
            self.suppressed_alerts[alert_key] = suppress_until
            
            return {
                "action": "suppress",
                "reason": f"pattern_match_{pattern.pattern_id}",
                "pattern": pattern,
                "original_alert": alert
            }
        
        elif pattern.action == "escalate":
            return {
                "action": "escalate",
                "reason": f"pattern_match_{pattern.pattern_id}",
                "pattern": pattern,
                "alert": alert,
                "enhanced": True
            }
        
        elif pattern.action == "correlate":
            return {
                "action": "correlate",
                "reason": f"pattern_match_{pattern.pattern_id}",
                "pattern": pattern,
                "alert": alert,
                "enhanced": True
            }
        
        return {"action": "process", "alert": alert}


class ProactiveAlertingSystem:
    """
    Advanced proactive alerting system with multi-channel notifications.
    
    Provides intelligent alerting with predictive capabilities,
    smart correlation, and multi-channel delivery.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize proactive alerting system.
        
        Args:
            config_file: Path to alerting configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file or "monitoring/alerting_config.json"
        
        # Components
        self.smart_processor = SmartAlertProcessor()
        self.notification_channels: Dict[NotificationChannel, NotificationConfig] = {}
        self.escalation_rules: List[EscalationRule] = []
        
        # State tracking
        self.alert_history: List[HealthAlert] = []
        self.escalated_alerts: Dict[str, Dict[str, Any]] = {}
        self.notification_queue: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.health_trends: Dict[str, List[float]] = {}
        self.prediction_models: Dict[str, Any] = {}
        
        # Load configuration
        self._load_configuration()
        
        self.logger.info("Proactive Alerting System initialized")
    
    def _load_configuration(self):
        """Load alerting configuration."""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                self._parse_notification_config(config.get('notifications', {}))
                self._parse_escalation_config(config.get('escalation', {}))
                
                self.logger.info("Alerting configuration loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load alerting config: {e}")
                self._load_default_configuration()
        else:
            self._load_default_configuration()
    
    def _load_default_configuration(self):
        """Load default alerting configuration."""
        # Default notification channels
        self.notification_channels = {
            NotificationChannel.CONSOLE: NotificationConfig(
                channel=NotificationChannel.CONSOLE,
                enabled=True
            ),
            NotificationChannel.FILE: NotificationConfig(
                channel=NotificationChannel.FILE,
                enabled=True,
                endpoint="monitoring/alerts.log"
            )
        }
        
        # Default escalation rules
        self.escalation_rules = [
            EscalationRule(
                alert_level=AlertLevel.EMERGENCY,
                escalation_delay=0,  # Immediate
                escalation_level=EscalationLevel.LEVEL_3,
                notification_channels=[NotificationChannel.CONSOLE, NotificationChannel.FILE]
            ),
            EscalationRule(
                alert_level=AlertLevel.CRITICAL,
                escalation_delay=5,  # 5 minutes
                escalation_level=EscalationLevel.LEVEL_2,
                notification_channels=[NotificationChannel.CONSOLE, NotificationChannel.FILE]
            ),
            EscalationRule(
                alert_level=AlertLevel.WARNING,
                escalation_delay=15,  # 15 minutes
                escalation_level=EscalationLevel.LEVEL_1,
                notification_channels=[NotificationChannel.CONSOLE, NotificationChannel.FILE]
            )
        ]
        
        self.logger.info("Default alerting configuration loaded")
    
    def _parse_notification_config(self, config: Dict[str, Any]):
        """Parse notification configuration."""
        for channel_name, channel_config in config.items():
            try:
                channel = NotificationChannel(channel_name)
                self.notification_channels[channel] = NotificationConfig(
                    channel=channel,
                    enabled=channel_config.get('enabled', True),
                    endpoint=channel_config.get('endpoint'),
                    credentials=channel_config.get('credentials', {}),
                    template=channel_config.get('template'),
                    retry_count=channel_config.get('retry_count', 3),
                    retry_delay=channel_config.get('retry_delay', 30)
                )
            except ValueError:
                self.logger.warning(f"Unknown notification channel: {channel_name}")
    
    def _parse_escalation_config(self, config: Dict[str, Any]):
        """Parse escalation configuration."""
        for rule_config in config.get('rules', []):
            try:
                self.escalation_rules.append(EscalationRule(
                    alert_level=AlertLevel(rule_config['alert_level']),
                    escalation_delay=rule_config.get('escalation_delay', 5),
                    escalation_level=EscalationLevel(rule_config['escalation_level']),
                    notification_channels=[
                        NotificationChannel(ch) for ch in rule_config.get('notification_channels', [])
                    ],
                    suppress_after=rule_config.get('suppress_after', 60)
                ))
            except (ValueError, KeyError) as e:
                self.logger.warning(f"Invalid escalation rule configuration: {e}")
    
    async def process_alert(self, alert: HealthAlert):
        """
        Process incoming health alert through smart correlation and notification.
        
        Args:
            alert: Health alert to process
        """
        self.logger.info(f"Processing alert: {alert.level} for {alert.agent_name}")
        
        # Smart processing
        processing_result = self.smart_processor.process_alert(alert)
        
        if processing_result["action"] == "suppress":
            self.logger.info(f"Alert suppressed: {processing_result['reason']}")
            return
        
        # Add to history
        self.alert_history.append(alert)
        
        # Find applicable escalation rule
        escalation_rule = self._find_escalation_rule(alert)
        
        if escalation_rule:
            await self._handle_escalation(alert, escalation_rule, processing_result)
        else:
            # Default notification
            await self._send_notifications(alert, [NotificationChannel.CONSOLE])
    
    def _find_escalation_rule(self, alert: HealthAlert) -> Optional[EscalationRule]:
        """Find applicable escalation rule for alert."""
        for rule in self.escalation_rules:
            if rule.alert_level == alert.level:
                return rule
        return None
    
    async def _handle_escalation(self, alert: HealthAlert, rule: EscalationRule, processing_result: Dict[str, Any]):
        """Handle alert escalation according to rules."""
        if rule.escalation_delay == 0:
            # Immediate escalation
            await self._send_notifications(alert, rule.notification_channels)
        else:
            # Delayed escalation
            escalation_key = f"{alert.alert_id}_{rule.escalation_level}"
            escalation_time = datetime.now() + timedelta(minutes=rule.escalation_delay)
            
            self.escalated_alerts[escalation_key] = {
                "alert": alert,
                "rule": rule,
                "escalation_time": escalation_time,
                "sent": False
            }
            
            self.logger.info(f"Alert scheduled for escalation at {escalation_time}")
    
    async def _send_notifications(self, alert: HealthAlert, channels: List[NotificationChannel]):
        """Send notifications through specified channels."""
        for channel in channels:
            if channel in self.notification_channels:
                config = self.notification_channels[channel]
                if config.enabled:
                    await self._send_notification(alert, config)
    
    async def _send_notification(self, alert: HealthAlert, config: NotificationConfig):
        """Send notification through specific channel."""
        try:
            if config.channel == NotificationChannel.CONSOLE:
                await self._send_console_notification(alert)
            elif config.channel == NotificationChannel.FILE:
                await self._send_file_notification(alert, config)
            elif config.channel == NotificationChannel.EMAIL:
                await self._send_email_notification(alert, config)
            elif config.channel == NotificationChannel.WEBHOOK:
                await self._send_webhook_notification(alert, config)
            elif config.channel == NotificationChannel.SLACK:
                await self._send_slack_notification(alert, config)
            
            self.logger.info(f"Notification sent via {config.channel} for alert {alert.alert_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send notification via {config.channel}: {e}")
            
            # Retry logic
            if config.retry_count > 0:
                await asyncio.sleep(config.retry_delay)
                config.retry_count -= 1
                await self._send_notification(alert, config)
    
    async def _send_console_notification(self, alert: HealthAlert):
        """Send console notification."""
        timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        message = f"🚨 [{timestamp}] {alert.level.upper()} - {alert.agent_name}: {alert.message}"
        print(message)
        self.logger.warning(message)
    
    async def _send_file_notification(self, alert: HealthAlert, config: NotificationConfig):
        """Send file notification."""
        log_path = Path(config.endpoint or "monitoring/alerts.log")
        log_path.parent.mkdir(exist_ok=True)
        
        timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {alert.level.upper()} - {alert.agent_name}: {alert.message}\n"
        
        with open(log_path, 'a') as f:
            f.write(log_entry)
    
    async def _send_email_notification(self, alert: HealthAlert, config: NotificationConfig):
        """Send email notification."""
        # Email implementation would require SMTP configuration
        self.logger.info(f"Email notification would be sent for alert: {alert.alert_id}")
    
    async def _send_webhook_notification(self, alert: HealthAlert, config: NotificationConfig):
        """Send webhook notification."""
        if not config.endpoint:
            return
        
        payload = {
            "alert_id": alert.alert_id,
            "level": alert.level,
            "agent_name": alert.agent_name,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat()
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(config.endpoint, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Webhook returned {response.status}")
    
    async def _send_slack_notification(self, alert: HealthAlert, config: NotificationConfig):
        """Send Slack notification."""
        # Slack implementation would require webhook URL
        self.logger.info(f"Slack notification would be sent for alert: {alert.alert_id}")
    
    def update_health_trends(self, agent_name: str, metrics: AgentHealthMetrics):
        """
        Update health trends for predictive analysis.
        
        Args:
            agent_name: Name of the agent
            metrics: Current health metrics
        """
        if agent_name not in self.health_trends:
            self.health_trends[agent_name] = []
        
        # Add current metric (response time as primary indicator)
        self.health_trends[agent_name].append(metrics.response_time_ms)
        
        # Keep only last 100 data points
        if len(self.health_trends[agent_name]) > 100:
            self.health_trends[agent_name] = self.health_trends[agent_name][-100:]
        
        # Check for predictive alerts
        self._check_predictive_alerts(agent_name)
    
    def _check_predictive_alerts(self, agent_name: str):
        """Check for predictive health degradation."""
        if agent_name not in self.health_trends:
            return
        
        trends = self.health_trends[agent_name]
        if len(trends) < 10:  # Need minimum data points
            return
        
        # Simple trend analysis (slope of last 10 points)
        recent_trends = trends[-10:]
        slope = self._calculate_slope(recent_trends)
        
        # If response time is trending upward significantly
        if slope > 50:  # 50ms increase per measurement
            # Create predictive alert
            predictive_alert = HealthAlert(
                alert_id=f"predictive_{agent_name}_{int(time.time())}",
                level=AlertLevel.WARNING,
                agent_name=agent_name,
                message=f"Predictive alert: Response time degrading (trend: +{slope:.1f}ms)",
                timestamp=datetime.now()
            )
            
            # Process predictive alert
            asyncio.create_task(self.process_alert(predictive_alert))
    
    def _calculate_slope(self, data: List[float]) -> float:
        """Calculate slope of data trend."""
        if len(data) < 2:
            return 0
        
        n = len(data)
        x_mean = (n - 1) / 2  # 0, 1, 2, ... n-1
        y_mean = sum(data) / n
        
        numerator = sum((i - x_mean) * (data[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0
    
    async def run_escalation_processor(self):
        """Background task to process escalated alerts."""
        while True:
            try:
                current_time = datetime.now()
                
                # Check for alerts ready for escalation
                ready_alerts = []
                for key, escalation_data in self.escalated_alerts.items():
                    if (not escalation_data["sent"] and 
                        current_time >= escalation_data["escalation_time"]):
                        ready_alerts.append(key)
                
                # Send escalated alerts
                for key in ready_alerts:
                    escalation_data = self.escalated_alerts[key]
                    alert = escalation_data["alert"]
                    rule = escalation_data["rule"]
                    
                    await self._send_notifications(alert, rule.notification_channels)
                    escalation_data["sent"] = True
                    
                    self.logger.info(f"Escalated alert sent: {alert.alert_id}")
                
                # Clean up old escalations (older than 24 hours)
                cutoff_time = current_time - timedelta(hours=24)
                keys_to_remove = []
                for key, escalation_data in self.escalated_alerts.items():
                    if escalation_data["escalation_time"] < cutoff_time:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self.escalated_alerts[key]
                
                # Sleep for 30 seconds before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in escalation processor: {e}")
                await asyncio.sleep(60)  # Wait longer on error


# Global alerting system instance
_alerting_system: Optional[ProactiveAlertingSystem] = None


def get_proactive_alerting_system() -> ProactiveAlertingSystem:
    """Get or create the global proactive alerting system."""
    global _alerting_system
    if _alerting_system is None:
        _alerting_system = ProactiveAlertingSystem()
    return _alerting_system


async def start_proactive_alerting():
    """Start the proactive alerting system."""
    alerting_system = get_proactive_alerting_system()
    
    # Start escalation processor
    asyncio.create_task(alerting_system.run_escalation_processor())
    
    return alerting_system


if __name__ == "__main__":
    # Example usage and testing
    async def main():
        alerting = ProactiveAlertingSystem()
        
        # Create test alert
        test_alert = HealthAlert(
            alert_id="test_001",
            level=AlertLevel.WARNING,
            agent_name="test_agent",
            message="Test alert for proactive alerting system",
            timestamp=datetime.now()
        )
        
        # Process test alert
        await alerting.process_alert(test_alert)
        
        print("Proactive alerting test complete")
    
    # Run test
    asyncio.run(main())
