# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---
import os
import sys

def _add_project_root_to_syspath():
    here = os.path.abspath(os.path.dirname(__file__))
    root = here
    while root and not (os.path.isdir(os.path.join(root, "app")) and os.path.isdir(os.path.join(root, "tests"))):
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    if root not in sys.path:
        sys.path.insert(0, root)
_add_project_root_to_syspath()
# --- END PATCH ---

"""
Unit tests for the integration health monitoring system.

This module tests the health metric collection functionality including:
- Health metric registration
- Health metric updates
- Health metric querying
- Threshold monitoring
"""
import unittest
import asyncio
from unittest.mock import patch, MagicMock
import time
from datetime import datetime, timedelta

from integrations.monitoring.integration_health import (
    HealthMetric, MetricType, HealthStatus,
    HealthMonitor, HealthThreshold, ThresholdDirection
)
from integrations.events.event_bus import EventBus
from integrations.events.event_types import Event, EventCategory


class TestHealthMonitoring(unittest.TestCase):
    """Test suite for the health metric collection system."""

    def setUp(self):
        """Set up test fixtures for each test."""
        # Create a clean health monitor for each test
        self.health_monitor = HealthMonitor()
        
        # Mock the event bus to prevent actual events from being published
        self.event_bus_patcher = patch('integrations.monitoring.integration_health.EventBus')
        self.mock_event_bus = self.event_bus_patcher.start()
        self.mock_event_bus_instance = MagicMock()
        self.mock_event_bus.return_value = self.mock_event_bus_instance
        
        # Create some test metrics
        self.cpu_metric = HealthMetric(
            name="system.cpu",
            metric_type=MetricType.GAUGE,
            component_id="system_monitor",
            description="CPU usage percentage"
        )
        
        self.memory_metric = HealthMetric(
            name="system.memory",
            metric_type=MetricType.GAUGE,
            component_id="system_monitor",
            description="Memory usage percentage"
        )
        
        self.api_calls_metric = HealthMetric(
            name="api.calls",
            metric_type=MetricType.COUNTER,
            component_id="api_client",
            description="Number of API calls made"
        )

    def tearDown(self):
        """Clean up after each test."""
        self.event_bus_patcher.stop()

    def test_metric_registration(self):
        """Test that metrics can be registered correctly."""
        # Register metrics
        self.health_monitor.register_metric(self.cpu_metric)
        self.health_monitor.register_metric(self.memory_metric)
        
        # Verify metrics are registered
        metrics = self.health_monitor.get_all_metrics()
        self.assertEqual(len(metrics), 2)
        self.assertIn("system.cpu", [metric.name for metric in metrics])
        self.assertIn("system.memory", [metric.name for metric in metrics])
        
        # Test registering duplicate metric
        with self.assertRaises(ValueError):
            self.health_monitor.register_metric(self.cpu_metric)
    
    def test_metric_update(self):
        """Test that metric values can be updated correctly."""
        # Register metric
        self.health_monitor.register_metric(self.cpu_metric)
        
        # Update metric value
        self.health_monitor.update_metric("system.cpu", 50.0)
        
        # Verify metric value
        metric = self.health_monitor.get_metric("system.cpu")
        self.assertEqual(metric.current_value, 50.0)
        self.assertEqual(metric.status, HealthStatus.OK)
        
        # Update metric again
        self.health_monitor.update_metric("system.cpu", 90.0)
        
        # Verify metric value updated
        metric = self.health_monitor.get_metric("system.cpu")
        self.assertEqual(metric.current_value, 90.0)
    
    def test_counter_metric(self):
        """Test that counter metrics increment correctly."""
        # Register metric
        self.health_monitor.register_metric(self.api_calls_metric)
        
        # Update metric value
        self.health_monitor.update_metric("api.calls", 1)
        
        # Verify metric value
        metric = self.health_monitor.get_metric("api.calls")
        self.assertEqual(metric.current_value, 1)
        
        # Increment counter
        self.health_monitor.update_metric("api.calls", 1)
        
        # Verify metric value
        metric = self.health_monitor.get_metric("api.calls")
        self.assertEqual(metric.current_value, 2)
    
    def test_metric_history(self):
        """Test that metric history is correctly maintained."""
        # Register metric with history
        cpu_metric_with_history = HealthMetric(
            name="system.cpu.history",
            metric_type=MetricType.GAUGE,
            component_id="system_monitor",
            description="CPU usage percentage",
            max_history=3
        )
        self.health_monitor.register_metric(cpu_metric_with_history)
        
        # Update metric multiple times
        self.health_monitor.update_metric("system.cpu.history", 10.0)
        self.health_monitor.update_metric("system.cpu.history", 20.0)
        self.health_monitor.update_metric("system.cpu.history", 30.0)
        
        # Verify history
        metric = self.health_monitor.get_metric("system.cpu.history")
        self.assertEqual(len(metric.history), 3)
        values = [item[1] for item in metric.history]
        self.assertIn(10.0, values)
        self.assertIn(20.0, values)
        self.assertIn(30.0, values)
        
        # Add one more value (should drop oldest)
        self.health_monitor.update_metric("system.cpu.history", 40.0)
        
        # Verify history
        metric = self.health_monitor.get_metric("system.cpu.history")
        self.assertEqual(len(metric.history), 3)
        values = [item[1] for item in metric.history]
        self.assertIn(20.0, values)
        self.assertIn(30.0, values)
        self.assertIn(40.0, values)
        self.assertNotIn(10.0, values)
    
    def test_threshold_detection(self):
        """Test that threshold crossings are detected correctly."""
        # Create metric with threshold
        cpu_metric_with_threshold = HealthMetric(
            name="system.cpu.threshold",
            metric_type=MetricType.GAUGE,
            component_id="system_monitor",
            description="CPU usage percentage",
            thresholds=[
                HealthThreshold(
                    value=80.0,
                    status=HealthStatus.WARNING,
                    direction=ThresholdDirection.ABOVE
                ),
                HealthThreshold(
                    value=90.0,
                    status=HealthStatus.CRITICAL,
                    direction=ThresholdDirection.ABOVE
                )
            ]
        )
        
        self.health_monitor.register_metric(cpu_metric_with_threshold)
        
        # Test normal value
        self.health_monitor.update_metric("system.cpu.threshold", 50.0)
        metric = self.health_monitor.get_metric("system.cpu.threshold")
        self.assertEqual(metric.status, HealthStatus.OK)
        
        # Test warning value
        self.health_monitor.update_metric("system.cpu.threshold", 85.0)
        metric = self.health_monitor.get_metric("system.cpu.threshold")
        self.assertEqual(metric.status, HealthStatus.WARNING)
        
        # Verify event was emitted for warning threshold
        self.mock_event_bus_instance.publish.assert_called()
        
        # Test critical value
        self.health_monitor.update_metric("system.cpu.threshold", 95.0)
        metric = self.health_monitor.get_metric("system.cpu.threshold")
        self.assertEqual(metric.status, HealthStatus.CRITICAL)
        
        # Test back to normal
        self.health_monitor.update_metric("system.cpu.threshold", 70.0)
        metric = self.health_monitor.get_metric("system.cpu.threshold")
        self.assertEqual(metric.status, HealthStatus.OK)
    
    def test_component_health(self):
        """Test aggregating health for a component."""
        # Register multiple metrics for one component
        self.health_monitor.register_metric(self.cpu_metric)
        self.health_monitor.register_metric(self.memory_metric)
        
        # Setup CPU metric with warning threshold
        cpu_threshold = HealthThreshold(
            value=80.0,
            status=HealthStatus.WARNING,
            direction=ThresholdDirection.ABOVE
        )
        self.cpu_metric.add_threshold(cpu_threshold)
        
        # Setup memory metric with critical threshold
        memory_threshold = HealthThreshold(
            value=90.0,
            status=HealthStatus.CRITICAL,
            direction=ThresholdDirection.ABOVE
        )
        self.memory_metric.add_threshold(memory_threshold)
        
        # Update metrics
        self.health_monitor.update_metric("system.cpu", 50.0)
        self.health_monitor.update_metric("system.memory", 50.0)
        
        # Check component health (should be OK)
        component_health = self.health_monitor.get_component_health("system_monitor")
        self.assertEqual(component_health["status"], HealthStatus.OK)
        
        # Update one metric to warning
        self.health_monitor.update_metric("system.cpu", 85.0)
        
        # Check component health (should be WARNING)
        component_health = self.health_monitor.get_component_health("system_monitor")
        self.assertEqual(component_health["status"], HealthStatus.WARNING)
        
        # Update another metric to critical
        self.health_monitor.update_metric("system.memory", 95.0)
        
        # Check component health (should be CRITICAL)
        component_health = self.health_monitor.get_component_health("system_monitor")
        self.assertEqual(component_health["status"], HealthStatus.CRITICAL)

    def test_system_health_visualization(self):
        """Test the health visualization data structures."""
        # Register metrics for multiple components
        self.health_monitor.register_metric(self.cpu_metric)
        self.health_monitor.register_metric(self.memory_metric)
        self.health_monitor.register_metric(self.api_calls_metric)
        
        # Update metrics with different statuses
        self.health_monitor.update_metric("system.cpu", 85.0)
        cpu_threshold = HealthThreshold(
            value=80.0,
            status=HealthStatus.WARNING,
            direction=ThresholdDirection.ABOVE
        )
        self.cpu_metric.add_threshold(cpu_threshold)
        
        self.health_monitor.update_metric("system.memory", 95.0)
        memory_threshold = HealthThreshold(
            value=90.0,
            status=HealthStatus.CRITICAL,
            direction=ThresholdDirection.ABOVE
        )
        self.memory_metric.add_threshold(memory_threshold)
        
        self.health_monitor.update_metric("api.calls", 100)
        
        # Get visualization data
        health_data = self.health_monitor.get_health_visualization_data()
        
        # Verify data structure
        self.assertIn("components", health_data)
        self.assertIn("system_monitor", health_data["components"])
        self.assertIn("api_client", health_data["components"])
        
        # Verify component health status
        self.assertEqual(health_data["components"]["system_monitor"]["status"], HealthStatus.CRITICAL)
        self.assertEqual(health_data["components"]["api_client"]["status"], HealthStatus.OK)
        
        # Verify overall system health (should be worst status)
        self.assertEqual(health_data["overall_status"], HealthStatus.CRITICAL)
        
        # Verify metric counts
        self.assertEqual(health_data["metric_counts"]["total"], 3)
        self.assertEqual(health_data["metric_counts"][HealthStatus.OK.name], 1)
        self.assertEqual(health_data["metric_counts"][HealthStatus.WARNING.name], 1)
        self.assertEqual(health_data["metric_counts"][HealthStatus.CRITICAL.name], 1)
        self.assertEqual(health_data["metric_counts"][HealthStatus.UNKNOWN.name], 0)


if __name__ == '__main__':
    unittest.main()
