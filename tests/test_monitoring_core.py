"""
Unit tests for monitoring core components.

This module provides comprehensive unit tests for the core monitoring
infrastructure including data models, base classes, and utilities.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import time

from monitoring.core.data_models import (
    HealthStatus, AlertSeverity, MetricType, MetricValue, ComponentHealth,
    SystemHealthReport, PerformanceMetrics, Alert, MonitoringConfiguration
)
from monitoring.core.monitoring_base import MonitoringBase, MonitoringRegistry
from monitoring.core.utilities import (
    MetricCalculator, TimestampUtils, ConfigurationManager, DataConverter
)


class TestDataModels(unittest.TestCase):
    """Test core data models."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.timestamp = datetime.now()
        
    def test_health_status_enum(self):
        """Test HealthStatus enum functionality."""
        # Test enum values
        self.assertEqual(HealthStatus.HEALTHY.value, "healthy")
        self.assertEqual(HealthStatus.WARNING.value, "warning")
        self.assertEqual(HealthStatus.CRITICAL.value, "critical")
        self.assertEqual(HealthStatus.UNKNOWN.value, "unknown")
        
        # Test numeric values
        self.assertEqual(HealthStatus.HEALTHY.numeric_value, 100)
        self.assertEqual(HealthStatus.WARNING.numeric_value, 60)
        self.assertEqual(HealthStatus.CRITICAL.numeric_value, 20)
        self.assertEqual(HealthStatus.UNKNOWN.numeric_value, 0)
        
        # Test string representation
        self.assertEqual(str(HealthStatus.HEALTHY), "healthy")
    
    def test_metric_value_creation(self):
        """Test MetricValue creation and validation."""
        # Valid metric value
        metric = MetricValue(
            metric_type=MetricType.RESPONSE_TIME,
            value=250.5,
            unit="ms",
            timestamp=self.timestamp,
            component="test_component"
        )
        
        self.assertEqual(metric.metric_type, MetricType.RESPONSE_TIME)
        self.assertEqual(metric.value, 250.5)
        self.assertEqual(metric.unit, "ms")
        self.assertEqual(metric.component, "test_component")
        self.assertEqual(metric.metadata, {})
        
        # Test validation - negative value
        with self.assertRaises(ValueError):
            MetricValue(
                metric_type=MetricType.RESPONSE_TIME,
                value=-10,
                unit="ms",
                timestamp=self.timestamp,
                component="test"
            )
        
        # Test validation - empty component
        with self.assertRaises(ValueError):
            MetricValue(
                metric_type=MetricType.RESPONSE_TIME,
                value=100,
                unit="ms",
                timestamp=self.timestamp,
                component=""
            )
    
    def test_metric_value_serialization(self):
        """Test MetricValue to_dict and from_dict methods."""
        original_metric = MetricValue(
            metric_type=MetricType.CPU_USAGE,
            value=75.2,
            unit="percent",
            timestamp=self.timestamp,
            component="system",
            metadata={"source": "psutil"}
        )
        
        # Convert to dictionary
        metric_dict = original_metric.to_dict()
        self.assertIsInstance(metric_dict, dict)
        self.assertEqual(metric_dict["metric_type"], "cpu_usage")
        self.assertEqual(metric_dict["value"], 75.2)
        self.assertEqual(metric_dict["metadata"]["source"], "psutil")
        
        # Convert back from dictionary
        restored_metric = MetricValue.from_dict(metric_dict)
        self.assertEqual(restored_metric.metric_type, original_metric.metric_type)
        self.assertEqual(restored_metric.value, original_metric.value)
        self.assertEqual(restored_metric.component, original_metric.component)
        self.assertEqual(restored_metric.metadata, original_metric.metadata)
    
    def test_component_health_creation(self):
        """Test ComponentHealth creation and methods."""
        component_health = ComponentHealth(
            component_name="test_agent",
            status=HealthStatus.HEALTHY,
            health_score=95.0,
            last_check=self.timestamp
        )
        
        self.assertEqual(component_health.component_name, "test_agent")
        self.assertEqual(component_health.status, HealthStatus.HEALTHY)
        self.assertEqual(component_health.health_score, 95.0)
        self.assertEqual(len(component_health.metrics), 0)
        self.assertEqual(len(component_health.issues), 0)
        
        # Test validation - invalid health score
        with self.assertRaises(ValueError):
            ComponentHealth(
                component_name="test",
                status=HealthStatus.HEALTHY,
                health_score=150.0,  # Invalid score > 100
                last_check=self.timestamp
            )
        
        # Test adding metrics and issues
        metric = MetricValue(
            MetricType.RESPONSE_TIME, 100, "ms", self.timestamp, "test_agent"
        )
        component_health.add_metric(metric)
        component_health.add_issue("Test issue")
        component_health.add_recommendation("Test recommendation")
        
        self.assertEqual(len(component_health.metrics), 1)
        self.assertEqual(len(component_health.issues), 1)
        self.assertEqual(len(component_health.recommendations), 1)
    
    def test_system_health_report_creation(self):
        """Test SystemHealthReport creation and aggregation."""
        health_report = SystemHealthReport(
            overall_status=HealthStatus.HEALTHY,
            overall_score=92.5,
            timestamp=self.timestamp
        )
        
        self.assertEqual(health_report.overall_status, HealthStatus.HEALTHY)
        self.assertEqual(health_report.overall_score, 92.5)
        self.assertEqual(len(health_report.components), 0)
        
        # Add component health
        component_health = ComponentHealth(
            component_name="agent1",
            status=HealthStatus.WARNING,
            health_score=70.0,
            last_check=self.timestamp
        )
        health_report.add_component(component_health)
        
        self.assertEqual(len(health_report.components), 1)
        self.assertEqual(health_report.components["agent1"].status, HealthStatus.WARNING)
        
        # Test status counts
        status_counts = health_report.get_component_count_by_status()
        self.assertEqual(status_counts[HealthStatus.WARNING], 1)
        self.assertEqual(status_counts[HealthStatus.HEALTHY], 0)
        
        # Test unhealthy components
        unhealthy = health_report.get_unhealthy_components()
        self.assertEqual(len(unhealthy), 1)
        self.assertEqual(unhealthy[0].component_name, "agent1")
    
    def test_performance_metrics_creation(self):
        """Test PerformanceMetrics creation and methods."""
        performance_metrics = PerformanceMetrics(timestamp=self.timestamp)
        
        self.assertEqual(len(performance_metrics.current_metrics), 0)
        self.assertEqual(len(performance_metrics.historical_data), 0)
        
        # Add metrics
        metric1 = MetricValue(
            MetricType.RESPONSE_TIME, 150, "ms", self.timestamp, "api"
        )
        metric2 = MetricValue(
            MetricType.CPU_USAGE, 65, "percent", self.timestamp, "system"
        )
        
        performance_metrics.add_metric(metric1)
        performance_metrics.add_metric(metric2)
        
        self.assertEqual(len(performance_metrics.current_metrics), 2)
        
        # Test filtering by type
        response_time_metrics = performance_metrics.get_metrics_by_type(MetricType.RESPONSE_TIME)
        self.assertEqual(len(response_time_metrics), 1)
        self.assertEqual(response_time_metrics[0].value, 150)
        
        # Test filtering by component
        api_metrics = performance_metrics.get_metrics_by_component("api")
        self.assertEqual(len(api_metrics), 1)
        self.assertEqual(api_metrics[0].metric_type, MetricType.RESPONSE_TIME)
    
    def test_alert_creation_and_resolution(self):
        """Test Alert creation and resolution."""
        alert = Alert(
            alert_id="test_alert_001",
            title="High Response Time",
            description="API response time exceeded threshold",
            severity=AlertSeverity.WARNING,
            component="api",
            metric_type=MetricType.RESPONSE_TIME,
            threshold_value=1000,
            actual_value=1500,
            timestamp=self.timestamp
        )
        
        self.assertEqual(alert.alert_id, "test_alert_001")
        self.assertEqual(alert.severity, AlertSeverity.WARNING)
        self.assertFalse(alert.resolved)
        self.assertIsNone(alert.resolution_timestamp)
        
        # Test resolution
        alert.resolve("Fixed by optimizing database queries")
        self.assertTrue(alert.resolved)
        self.assertIsNotNone(alert.resolution_timestamp)
        self.assertEqual(alert.resolution_notes, "Fixed by optimizing database queries")
        
        # Test duration calculation
        duration = alert.get_duration()
        self.assertIsNotNone(duration)
        self.assertIsInstance(duration, float)
    
    def test_monitoring_configuration(self):
        """Test MonitoringConfiguration creation and serialization."""
        config = MonitoringConfiguration()
        
        # Test default values
        self.assertEqual(config.health_check_interval, 30)
        self.assertEqual(config.metrics_collection_interval, 30)
        self.assertEqual(config.response_time_warning_ms, 1000)
        
        # Test serialization
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict["health_check_interval"], 30)
        
        # Test deserialization
        restored_config = MonitoringConfiguration.from_dict(config_dict)
        self.assertEqual(restored_config.health_check_interval, config.health_check_interval)
        self.assertEqual(restored_config.metrics_collection_interval, config.metrics_collection_interval)


class TestMonitoringBase(unittest.TestCase):
    """Test MonitoringBase abstract class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create concrete implementation for testing
        class TestMonitoringComponent(MonitoringBase):
            def get_health_status(self):
                return {"status": "healthy", "component": "test"}
            
            def collect_metrics(self):
                return [MetricValue(
                    MetricType.THROUGHPUT, 100, "ops/sec", 
                    datetime.now(), "test_component"
                )]
        
        self.component = TestMonitoringComponent()
    
    def test_initialization(self):
        """Test MonitoringBase initialization."""
        self.assertIsNotNone(self.component.config)
        self.assertIsNotNone(self.component.logger)
        self.assertFalse(self.component.is_running)
        self.assertEqual(self.component.status, "initialized")
        self.assertEqual(self.component.error_count, 0)
    
    def test_lifecycle_management(self):
        """Test start/stop lifecycle."""
        # Test start
        self.assertFalse(self.component.is_running)
        self.component.start()
        self.assertTrue(self.component.is_running)
        self.assertEqual(self.component.status, "running")
        
        # Test stop
        self.component.stop()
        self.assertFalse(self.component.is_running)
        self.assertEqual(self.component.status, "stopped")
    
    def test_error_handling(self):
        """Test error handling and tracking."""
        initial_error_count = self.component.error_count
        
        # Simulate error
        test_error = ValueError("Test error")
        self.component._handle_error(test_error, "Test context")
        
        self.assertEqual(self.component.error_count, initial_error_count + 1)
        self.assertEqual(self.component.last_error, test_error)
        self.assertIsNotNone(self.component._last_error_time)
    
    def test_status_info(self):
        """Test status information retrieval."""
        status_info = self.component.get_status_info()
        
        self.assertIsInstance(status_info, dict)
        self.assertIn("component_name", status_info)
        self.assertIn("status", status_info)
        self.assertIn("is_running", status_info)
        self.assertIn("health_score", status_info)
        self.assertIn("error_count", status_info)
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with self.component as component:
            self.assertTrue(component.is_running)
        
        self.assertFalse(self.component.is_running)


class TestMonitoringRegistry(unittest.TestCase):
    """Test MonitoringRegistry functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = MonitoringRegistry()
        
        # Create mock components
        self.mock_component1 = Mock(spec=MonitoringBase)
        self.mock_component1.is_running = False
        self.mock_component1.get_status_info.return_value = {
            "health_score": 95.0,
            "is_running": False
        }
        
        self.mock_component2 = Mock(spec=MonitoringBase)
        self.mock_component2.is_running = True
        self.mock_component2.get_status_info.return_value = {
            "health_score": 85.0,
            "is_running": True
        }
    
    def test_component_registration(self):
        """Test component registration and retrieval."""
        # Test registration
        self.registry.register("component1", self.mock_component1)
        self.assertEqual(len(self.registry.get_all_components()), 1)
        
        # Test duplicate registration
        with self.assertRaises(ValueError):
            self.registry.register("component1", self.mock_component2)
        
        # Test retrieval
        retrieved = self.registry.get_component("component1")
        self.assertEqual(retrieved, self.mock_component1)
        
        # Test non-existent component
        self.assertIsNone(self.registry.get_component("nonexistent"))
    
    def test_component_unregistration(self):
        """Test component unregistration."""
        self.registry.register("component1", self.mock_component1)
        self.assertEqual(len(self.registry.get_all_components()), 1)
        
        # Test unregistration
        self.registry.unregister("component1")
        self.assertEqual(len(self.registry.get_all_components()), 0)
        
        # Test unregistering non-existent component
        with self.assertRaises(ValueError):
            self.registry.unregister("nonexistent")
    
    def test_lifecycle_management(self):
        """Test start_all and stop_all functionality."""
        self.registry.register("component1", self.mock_component1)
        self.registry.register("component2", self.mock_component2)
        
        # Test start_all
        self.registry.start_all()
        self.mock_component1.start.assert_called_once()
        # Component2 is already running in the mock setup, so it shouldn't be started again
        
        # Test stop_all
        self.registry.stop_all()
        # Component1 was started, so it should be stopped
        # Component2 was already running, so it should be stopped
        self.mock_component2.stop.assert_called_once()
    
    def test_overall_health_calculation(self):
        """Test overall health calculation."""
        # No components
        health = self.registry.get_overall_health()
        self.assertEqual(health["status"], "no_components")
        self.assertEqual(health["health_score"], 0.0)
        
        # Add components
        self.registry.register("component1", self.mock_component1)
        self.registry.register("component2", self.mock_component2)
        
        health = self.registry.get_overall_health()
        self.assertEqual(health["component_count"], 2)
        self.assertEqual(health["running_count"], 1)
        self.assertEqual(health["health_score"], 90.0)  # Average of 95 and 85


class TestUtilities(unittest.TestCase):
    """Test utility classes and functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.timestamp = datetime.now()
        self.metrics = [
            MetricValue(MetricType.RESPONSE_TIME, 100, "ms", self.timestamp, "test"),
            MetricValue(MetricType.RESPONSE_TIME, 150, "ms", self.timestamp, "test"),
            MetricValue(MetricType.RESPONSE_TIME, 200, "ms", self.timestamp, "test"),
            MetricValue(MetricType.RESPONSE_TIME, 125, "ms", self.timestamp, "test"),
            MetricValue(MetricType.RESPONSE_TIME, 175, "ms", self.timestamp, "test")
        ]
    
    def test_metric_calculator_basic_stats(self):
        """Test basic statistical calculations."""
        calc = MetricCalculator()
        
        # Test average
        avg = calc.calculate_average(self.metrics)
        self.assertEqual(avg, 150.0)  # (100+150+200+125+175)/5
        
        # Test median
        median = calc.calculate_median(self.metrics)
        self.assertEqual(median, 150.0)
        
        # Test standard deviation
        std_dev = calc.calculate_standard_deviation(self.metrics)
        self.assertIsNotNone(std_dev)
        self.assertGreater(std_dev, 0)
        
        # Test with empty list
        self.assertIsNone(calc.calculate_average([]))
        self.assertIsNone(calc.calculate_median([]))
    
    def test_metric_calculator_percentiles(self):
        """Test percentile calculations."""
        calc = MetricCalculator()
        
        # Test 50th percentile (median)
        p50 = calc.calculate_percentile(self.metrics, 50)
        self.assertEqual(p50, 150.0)
        
        # Test 90th percentile
        p90 = calc.calculate_percentile(self.metrics, 90)
        self.assertGreater(p90, 150.0)
        
        # Test invalid percentile
        with self.assertRaises(ValueError):
            calc.calculate_percentile(self.metrics, 150)
    
    def test_metric_calculator_outliers(self):
        """Test outlier detection."""
        calc = MetricCalculator()
        
        # Add obvious outlier
        outlier_metrics = self.metrics + [
            MetricValue(MetricType.RESPONSE_TIME, 1000, "ms", self.timestamp, "test")
        ]
        
        outliers = calc.detect_outliers(outlier_metrics, threshold=2.0)
        self.assertGreater(len(outliers), 0)
        
        # Test with normal data
        normal_outliers = calc.detect_outliers(self.metrics, threshold=2.0)
        self.assertEqual(len(normal_outliers), 0)
    
    def test_metric_calculator_trends(self):
        """Test trend calculation."""
        calc = MetricCalculator()
        
        # Create increasing trend
        increasing_metrics = []
        for i, base_time in enumerate([
            self.timestamp + timedelta(minutes=i) for i in range(5)
        ]):
            increasing_metrics.append(
                MetricValue(MetricType.RESPONSE_TIME, 100 + i*20, "ms", base_time, "test")
            )
        
        trend = calc.calculate_trend(increasing_metrics)
        self.assertEqual(trend, "increasing")
        
        # Create decreasing trend
        decreasing_metrics = []
        for i, base_time in enumerate([
            self.timestamp + timedelta(minutes=i) for i in range(5)
        ]):
            decreasing_metrics.append(
                MetricValue(MetricType.RESPONSE_TIME, 200 - i*20, "ms", base_time, "test")
            )
        
        trend = calc.calculate_trend(decreasing_metrics)
        self.assertEqual(trend, "decreasing")
    
    def test_timestamp_utils(self):
        """Test timestamp utility functions."""
        utils = TimestampUtils()
        
        # Test interval rounding
        timestamp = datetime(2024, 1, 1, 12, 34, 56)
        rounded = utils.round_to_interval(timestamp, 300)  # 5 minutes
        self.assertEqual(rounded.second, 0)
        self.assertIn(rounded.minute, [30, 35])  # Should round to nearest 5-minute mark
        
        # Test time bucket generation
        start_time = datetime(2024, 1, 1, 12, 0, 0)
        end_time = datetime(2024, 1, 1, 12, 10, 0)
        buckets = utils.get_time_buckets(start_time, end_time, 300)  # 5-minute buckets
        self.assertEqual(len(buckets), 3)  # 12:00, 12:05, 12:10
        
        # Test duration formatting
        self.assertEqual(utils.format_duration(0.5), "500.0ms")
        self.assertEqual(utils.format_duration(5), "5.0s")
        self.assertEqual(utils.format_duration(90), "1.5m")
        self.assertEqual(utils.format_duration(7200), "2.0h")
        
        # Test duration parsing
        self.assertEqual(utils.parse_duration_string("500ms"), 0.5)
        self.assertEqual(utils.parse_duration_string("5s"), 5.0)
        self.assertEqual(utils.parse_duration_string("2m"), 120.0)
        self.assertEqual(utils.parse_duration_string("1h"), 3600.0)
    
    @patch('builtins.open', create=True)
    @patch('pathlib.Path.exists')
    def test_configuration_manager(self, mock_exists, mock_open):
        """Test configuration management."""
        mock_exists.return_value = False
        
        config_manager = ConfigurationManager("test_config.json")
        
        # Test default config creation
        config = config_manager.load_config()
        self.assertIsInstance(config, dict)
        self.assertIn("monitoring", config)
        self.assertIn("thresholds", config)
        
        # Test getting specific values
        health_interval = config_manager.get_config_value("monitoring.health_check_interval", 60)
        self.assertEqual(health_interval, 30)  # Default value
        
        # Test setting values
        config_manager.set_config_value("monitoring.health_check_interval", 45)
        # Note: In real test, we'd verify the save was called
    
    def test_data_converter(self):
        """Test data conversion utilities."""
        converter = DataConverter()
        
        # Test metrics to dict list
        dict_list = converter.metrics_to_dict_list(self.metrics)
        self.assertEqual(len(dict_list), len(self.metrics))
        self.assertIsInstance(dict_list[0], dict)
        
        # Test dict list to metrics
        restored_metrics = converter.dict_list_to_metrics(dict_list)
        self.assertEqual(len(restored_metrics), len(self.metrics))
        self.assertIsInstance(restored_metrics[0], MetricValue)
        
        # Test metric compression
        compressed = converter.compress_metrics(self.metrics, 0.4)  # Keep 40%
        self.assertLessEqual(len(compressed), len(self.metrics))
        
        # Test aggregation
        aggregated = converter.aggregate_metrics_by_time(
            self.metrics, 3600, "average"  # 1-hour buckets
        )
        self.assertLessEqual(len(aggregated), len(self.metrics))


if __name__ == '__main__':
    unittest.main()
