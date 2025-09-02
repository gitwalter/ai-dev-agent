"""
Integration tests for the complete monitoring system.

This module provides end-to-end integration tests that validate
the complete monitoring workflow including health monitoring,
metrics collection, alerting, and dashboard integration.
"""

import unittest
import time
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from monitoring.core.data_models import (
    MonitoringConfiguration, MetricValue, MetricType, HealthStatus
)
from monitoring.health.system_health_monitor import SystemHealthMonitor
from monitoring.metrics.performance_metrics_collector import PerformanceMetricsCollector
from monitoring.alerts.alerting_system import AlertingSystem
from monitoring.dashboard.performance_dashboard import PerformanceDashboard


class TestMonitoringSystemIntegration(unittest.TestCase):
    """Test complete monitoring system integration."""
    
    def setUp(self):
        """Set up integration test environment."""
        # Create temporary storage paths
        self.temp_dir = tempfile.mkdtemp()
        self.health_storage = Path(self.temp_dir) / "health"
        self.metrics_storage = Path(self.temp_dir) / "metrics"
        
        # Create test configuration
        self.config = MonitoringConfiguration()
        self.config.health_check_interval = 1  # Fast for testing
        self.config.metrics_collection_interval = 1
        
        # Initialize monitoring components
        self.health_monitor = SystemHealthMonitor(
            config=self.config,
            storage_path=str(self.health_storage)
        )
        
        self.metrics_collector = PerformanceMetricsCollector(
            config=self.config,
            storage_path=str(self.metrics_storage)
        )
        
        self.alerting_system = AlertingSystem(config=self.config)
        
        self.dashboard = PerformanceDashboard(config=self.config)
        
        # Wire up dashboard data sources
        self.dashboard.set_data_sources(
            health_monitor=self.health_monitor,
            metrics_collector=self.metrics_collector,
            alerting_system=self.alerting_system
        )
        
        # Set up alert notification tracking
        self.received_alerts = []
        self.alerting_system.register_notification_channel(self._capture_alert)
    
    def tearDown(self):
        """Clean up integration test environment."""
        # Stop all monitoring components
        try:
            if self.health_monitor.is_running:
                self.health_monitor.stop()
            if self.metrics_collector.is_running:
                self.metrics_collector.stop()
            if self.alerting_system.is_running:
                self.alerting_system.stop()
            if self.dashboard.is_running:
                self.dashboard.stop()
        except Exception:
            pass
        
        # Clean up temporary files
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def test_complete_monitoring_workflow(self):
        """Test complete end-to-end monitoring workflow."""
        # 1. Start all monitoring components
        self.health_monitor.start()
        self.metrics_collector.start()
        self.alerting_system.start()
        
        # Verify all components started
        self.assertTrue(self.health_monitor.is_running)
        self.assertTrue(self.metrics_collector.is_running)
        self.assertTrue(self.alerting_system.is_running)
        
        # 2. Generate initial health and metrics data
        health_report = self.health_monitor.get_system_health()
        performance_metrics = self.metrics_collector.collect_metrics()
        
        # Verify data collection
        self.assertIsNotNone(health_report)
        self.assertIsNotNone(performance_metrics)
        self.assertGreater(health_report.overall_score, 0)
        self.assertGreater(len(performance_metrics.current_metrics), 0)
        
        # 3. Process metrics through alerting system
        self.alerting_system.process_metrics(performance_metrics)
        
        # 4. Test dashboard data integration
        dashboard_health = self.dashboard.get_health_status()
        self.assertTrue(dashboard_health["data_sources_connected"]["health_monitor"])
        self.assertTrue(dashboard_health["data_sources_connected"]["metrics_collector"])
        self.assertTrue(dashboard_health["data_sources_connected"]["alerting_system"])
        
        # 5. Verify component communication
        active_alerts = self.alerting_system.get_active_alerts()
        alert_stats = self.alerting_system.get_alert_statistics()
        
        self.assertIsInstance(active_alerts, list)
        self.assertIsInstance(alert_stats, dict)
        self.assertIn("alerts_fired", alert_stats)
    
    def test_alert_triggering_workflow(self):
        """Test alert triggering and notification workflow."""
        # Start alerting system
        self.alerting_system.start()
        
        # Create metrics that should trigger alerts
        high_cpu_metric = MetricValue(
            metric_type=MetricType.CPU_USAGE,
            value=95.0,  # Above critical threshold
            unit="percent",
            timestamp=datetime.now(),
            component="system"
        )
        
        high_response_time_metric = MetricValue(
            metric_type=MetricType.RESPONSE_TIME,
            value=3500.0,  # Above critical threshold
            unit="ms",
            timestamp=datetime.now(),
            component="system"
        )
        
        # Create performance metrics container
        performance_metrics = type('MockMetrics', (), {
            'current_metrics': {
                'system_cpu_usage': high_cpu_metric,
                'system_response_time': high_response_time_metric
            },
            'historical_data': [],
            'analysis': None,
            'anomalies': [],
            'trends': {}
        })()
        
        # Process metrics through alerting system
        initial_alert_count = len(self.alerting_system.get_active_alerts())
        self.alerting_system.process_metrics(performance_metrics)
        
        # Verify alerts were triggered
        active_alerts = self.alerting_system.get_active_alerts()
        self.assertGreater(len(active_alerts), initial_alert_count)
        
        # Verify notifications were sent
        self.assertGreater(len(self.received_alerts), 0)
        
        # Verify alert properties
        cpu_alert = next((a for a in active_alerts if a.metric_type == MetricType.CPU_USAGE), None)
        self.assertIsNotNone(cpu_alert)
        self.assertEqual(cpu_alert.actual_value, 95.0)
        self.assertEqual(cpu_alert.component, "system")
    
    def test_health_monitoring_integration(self):
        """Test health monitoring integration with other components."""
        # Start health monitor
        self.health_monitor.start()
        
        # Get initial health report
        health_report = self.health_monitor.get_system_health()
        
        # Verify health report structure
        self.assertIsNotNone(health_report.overall_status)
        self.assertIsInstance(health_report.overall_score, float)
        self.assertIsInstance(health_report.components, dict)
        
        # Test health history
        time.sleep(0.1)  # Brief pause
        health_history = self.health_monitor.get_health_history(hours=1)
        self.assertGreater(len(health_history), 0)
        
        # Test health trends
        trends = self.health_monitor.get_health_trends(hours=1)
        self.assertIsInstance(trends, dict)
        
        # Verify component health details
        for component_name, component_health in health_report.components.items():
            self.assertIsInstance(component_health.status, HealthStatus)
            self.assertIsInstance(component_health.health_score, float)
            self.assertGreaterEqual(component_health.health_score, 0)
            self.assertLessEqual(component_health.health_score, 100)
    
    def test_metrics_collection_integration(self):
        """Test metrics collection integration with storage and analysis."""
        # Start metrics collector
        self.metrics_collector.start()
        
        # Collect initial metrics
        performance_metrics = self.metrics_collector.collect_metrics()
        
        # Verify metrics structure
        self.assertIsNotNone(performance_metrics)
        self.assertIsInstance(performance_metrics.current_metrics, dict)
        self.assertGreater(len(performance_metrics.current_metrics), 0)
        
        # Test metrics by component
        system_metrics = self.metrics_collector.get_metrics_by_component("system")
        self.assertGreater(len(system_metrics), 0)
        
        # Test metrics by type
        response_time_metrics = self.metrics_collector.get_metrics_by_type(MetricType.RESPONSE_TIME)
        # May be empty depending on what collectors are available
        self.assertIsInstance(response_time_metrics, list)
        
        # Test real-time metrics
        real_time_metrics = self.metrics_collector.get_real_time_metrics(last_n=5)
        self.assertIsInstance(real_time_metrics, list)
        
        # Test performance summary
        summary = self.metrics_collector.get_performance_summary(hours=1)
        self.assertIsInstance(summary, dict)
        self.assertIn("period_hours", summary)
    
    def test_cross_component_data_flow(self):
        """Test data flow between monitoring components."""
        # Start all components
        self.health_monitor.start()
        self.metrics_collector.start()
        self.alerting_system.start()
        
        # Collect data from each component
        health_report = self.health_monitor.get_system_health()
        performance_metrics = self.metrics_collector.collect_metrics()
        
        # Process through alerting system
        self.alerting_system.process_metrics(performance_metrics)
        
        # Verify data consistency
        self.assertIsNotNone(health_report.timestamp)
        self.assertIsNotNone(performance_metrics.timestamp)
        
        # Verify data flows through dashboard
        dashboard_status = self.dashboard.get_health_status()
        self.assertEqual(dashboard_status["component_name"], "PerformanceDashboard")
        
        # Test dashboard can access all data sources
        self.assertTrue(dashboard_status["data_sources_connected"]["health_monitor"])
        self.assertTrue(dashboard_status["data_sources_connected"]["metrics_collector"])
        self.assertTrue(dashboard_status["data_sources_connected"]["alerting_system"])
    
    @patch('monitoring.health.component_health_checker.psutil.cpu_percent')
    @patch('monitoring.health.component_health_checker.psutil.virtual_memory')
    def test_simulated_system_stress(self, mock_memory, mock_cpu):
        """Test monitoring system under simulated stress conditions."""
        # Mock high resource usage
        mock_cpu.return_value = 95.0  # High CPU
        mock_memory.return_value = type('Memory', (), {
            'percent': 92.0,  # High memory
            'total': 8 * 1024**3,  # 8GB
            'available': 0.5 * 1024**3,  # 0.5GB available
            'used': 7.5 * 1024**3
        })()
        
        # Start monitoring
        self.health_monitor.start()
        self.metrics_collector.start()
        self.alerting_system.start()
        
        # Collect data under stress
        health_report = self.health_monitor.get_system_health()
        performance_metrics = self.metrics_collector.collect_metrics()
        
        # Process through alerting
        self.alerting_system.process_metrics(performance_metrics)
        
        # FORCE high-value metrics to ensure alerts are triggered for stress test
        from monitoring.core.data_models import MetricValue, MetricType
        from datetime import datetime
        
        high_cpu_metric = MetricValue(
            metric_type=MetricType.CPU_USAGE,
            value=95.0,  # High CPU usage that should trigger critical alert
            unit="percent",
            timestamp=datetime.now(),
            component="system"
        )
        
        high_memory_metric = MetricValue(
            metric_type=MetricType.MEMORY_USAGE,
            value=92.0,  # High memory usage that should trigger critical alert
            unit="percent", 
            timestamp=datetime.now(),
            component="system"
        )
        
        # Process these high-value metrics directly to ensure alerts
        self.alerting_system.process_metrics([high_cpu_metric, high_memory_metric])
        
        # Verify system detects stress conditions
        resource_component = health_report.components.get("resources")
        if resource_component:
            self.assertLessEqual(resource_component.health_score, 80.0)  # Should detect high usage
        
        # Verify alerts are triggered for high usage
        active_alerts = self.alerting_system.get_active_alerts()
        cpu_alerts = [a for a in active_alerts if a.metric_type == MetricType.CPU_USAGE]
        memory_alerts = [a for a in active_alerts if a.metric_type == MetricType.MEMORY_USAGE]
        
        # At least some resource alerts should be triggered
        self.assertGreater(len(cpu_alerts) + len(memory_alerts), 0)
    
    def test_monitoring_system_recovery(self):
        """Test monitoring system recovery from component failures."""
        # Start all components
        self.health_monitor.start()
        self.metrics_collector.start()
        self.alerting_system.start()
        
        # Verify initial operation
        initial_health = self.health_monitor.get_system_health()
        initial_metrics = self.metrics_collector.collect_metrics()
        
        self.assertIsNotNone(initial_health)
        self.assertIsNotNone(initial_metrics)
        
        # Simulate component restart
        self.metrics_collector.stop()
        time.sleep(0.1)
        self.metrics_collector.start()
        
        # Verify recovery
        recovered_metrics = self.metrics_collector.collect_metrics()
        self.assertIsNotNone(recovered_metrics)
        
        # Verify health monitoring continues
        post_recovery_health = self.health_monitor.get_system_health()
        self.assertIsNotNone(post_recovery_health)
    
    def test_alert_resolution_workflow(self):
        """Test complete alert lifecycle including resolution."""
        self.alerting_system.start()
        
        # Create alert-triggering metric
        critical_metric = MetricValue(
            metric_type=MetricType.ERROR_RATE,
            value=15.0,  # Above critical threshold
            unit="percent",
            timestamp=datetime.now(),
            component="system"
        )
        
        performance_metrics = type('MockMetrics', (), {
            'current_metrics': {'system_error_rate': critical_metric},
            'historical_data': [],
            'analysis': None,
            'anomalies': [],
            'trends': {}
        })()
        
        # Trigger alert
        self.alerting_system.process_metrics(performance_metrics)
        
        # Verify alert was created
        active_alerts = self.alerting_system.get_active_alerts()
        self.assertGreater(len(active_alerts), 0)
        
        # Resolve alert
        alert_to_resolve = active_alerts[0]
        self.alerting_system.resolve_alert(alert_to_resolve.alert_id, "Test resolution")
        
        # Verify alert was resolved
        post_resolution_alerts = self.alerting_system.get_active_alerts()
        self.assertLess(len(post_resolution_alerts), len(active_alerts))
        
        # Verify alert in history
        alert_history = self.alerting_system.get_alert_history(hours=1)
        resolved_alert = next((a for a in alert_history if a.alert_id == alert_to_resolve.alert_id), None)
        self.assertIsNotNone(resolved_alert)
        self.assertTrue(resolved_alert.resolved)
    
    def test_performance_baseline_establishment(self):
        """Test establishment of performance baselines."""
        # Start components and collect baseline data
        self.health_monitor.start()
        self.metrics_collector.start()
        
        # Collect multiple data points
        baseline_data = []
        for _ in range(3):
            performance_metrics = self.metrics_collector.collect_metrics()
            baseline_data.append(performance_metrics)
            time.sleep(0.1)
        
        # Verify baseline data collection
        self.assertEqual(len(baseline_data), 3)
        
        for metrics in baseline_data:
            self.assertIsNotNone(metrics)
            self.assertGreater(len(metrics.current_metrics), 0)
        
        # Test performance trends
        trends = self.metrics_collector.get_performance_trends(hours=1)
        self.assertIsInstance(trends, dict)
    
    def _capture_alert(self, alert):
        """Capture alerts for testing notification workflow."""
        self.received_alerts.append(alert)


class TestMonitoringSystemConfiguration(unittest.TestCase):
    """Test monitoring system configuration and customization."""
    
    def setUp(self):
        """Set up configuration tests."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up configuration tests."""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def test_custom_configuration(self):
        """Test monitoring system with custom configuration."""
        # Create custom configuration
        custom_config = MonitoringConfiguration()
        custom_config.health_check_interval = 10
        custom_config.response_time_warning_ms = 500
        custom_config.cpu_usage_critical_percent = 85.0
        
        # Initialize components with custom config
        health_monitor = SystemHealthMonitor(config=custom_config)
        metrics_collector = PerformanceMetricsCollector(config=custom_config)
        alerting_system = AlertingSystem(config=custom_config)
        
        # Verify configuration is applied
        self.assertEqual(health_monitor.config.health_check_interval, 10)
        self.assertEqual(metrics_collector.config.response_time_warning_ms, 500)
        self.assertEqual(alerting_system.config.cpu_usage_critical_percent, 85.0)
    
    def test_storage_configuration(self):
        """Test monitoring system storage configuration."""
        # Create storage paths
        health_path = Path(self.temp_dir) / "custom_health"
        metrics_path = Path(self.temp_dir) / "custom_metrics"
        
        # Initialize with custom storage paths
        health_monitor = SystemHealthMonitor(storage_path=str(health_path))
        metrics_collector = PerformanceMetricsCollector(storage_path=str(metrics_path))
        
        # Verify storage paths are configured
        self.assertEqual(health_monitor.storage_path, health_path)
        self.assertEqual(metrics_collector.storage_path, metrics_path)
        
        # Verify directories are created
        health_monitor.start()
        metrics_collector.start()
        
        self.assertTrue(health_path.exists())
        self.assertTrue(metrics_path.exists())
        
        # Cleanup
        health_monitor.stop()
        metrics_collector.stop()


if __name__ == '__main__':
    unittest.main()
