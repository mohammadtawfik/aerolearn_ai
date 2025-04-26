"""
Integration health monitoring for the AeroLearn AI system.

This module provides health metric collection, status tracking, and visualization
data structures for monitoring the health of system integrations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable
import time
import uuid
import threading

from integrations.events.event_types import Event, EventCategory, EventPriority
from integrations.registry.component_registry import Component


class HealthStatus(Enum):
    """Health status levels for components and integrations."""
    HEALTHY = auto()
    DEGRADED = auto()
    FAILING = auto()
    CRITICAL = auto()
    UNKNOWN = auto()


class HealthMetricType(Enum):
    """Types of health metrics that can be collected."""
    RESPONSE_TIME = auto()
    ERROR_RATE = auto()
    THROUGHPUT = auto()
    RESOURCE_USAGE = auto()
    AVAILABILITY = auto()
    CUSTOM = auto()


class HealthMetric:
    """A single health metric measurement."""
    
    def __init__(
        self, 
        name: str, 
        value: float, 
        metric_type: HealthMetricType,
        component_id: str,
        timestamp: Optional[datetime] = None,
        threshold_warning: Optional[float] = None,
        threshold_critical: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new health metric.
        
        Args:
            name: Name of the metric
            value: Measured value
            metric_type: Type of the metric
            component_id: ID of the component this metric belongs to
            timestamp: When the metric was recorded (defaults to now)
            threshold_warning: Warning threshold value
            threshold_critical: Critical threshold value
            metadata: Additional metric metadata
        """
        self.name = name
        self.value = value
        self.metric_type = metric_type
        self.component_id = component_id
        self.timestamp = timestamp or datetime.now()
        self.threshold_warning = threshold_warning
        self.threshold_critical = threshold_critical
        self.metadata = metadata or {}
        
    def get_status(self) -> HealthStatus:
        """Determine health status based on thresholds."""
        if self.threshold_critical is not None and self.value >= self.threshold_critical:
            return HealthStatus.CRITICAL
        elif self.threshold_warning is not None and self.value >= self.threshold_warning:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'value': self.value,
            'metric_type': self.metric_type.name,
            'component_id': self.component_id,
            'timestamp': self.timestamp.isoformat(),
            'threshold_warning': self.threshold_warning,
            'threshold_critical': self.threshold_critical,
            'status': self.get_status().name,
            'metadata': self.metadata
        }


class HealthEvent(Event):
    """Event fired when a significant health status change occurs."""
    
    def __init__(
        self, 
        component_id: str,
        metric: HealthMetric,
        old_status: Optional[HealthStatus] = None,
        new_status: Optional[HealthStatus] = None
    ):
        """
        Initialize a new health event.
        
        Args:
            component_id: ID of the affected component
            metric: The health metric that triggered the event
            old_status: Previous health status
            new_status: New health status
        """
        super().__init__()
        self.component_id = component_id
        self.metric = metric
        self.old_status = old_status
        self.new_status = new_status
        self.category = EventCategory.SYSTEM
        self.priority = (
            EventPriority.HIGH if new_status in (HealthStatus.FAILING, HealthStatus.CRITICAL)
            else EventPriority.MEDIUM
        )


class HealthProvider(ABC):
    """Interface for components that provide health information."""
    
    @abstractmethod
    def get_health_metrics(self) -> List[HealthMetric]:
        """
        Get current health metrics from the component.
        
        Returns:
            List of health metrics
        """
        pass
    
    @abstractmethod
    def get_health_status(self) -> HealthStatus:
        """
        Get the overall health status of the component.
        
        Returns:
            Current health status
        """
        pass


class IntegrationHealthError(Exception):
    """Exception raised for errors in the integration health system."""
    pass


class IntegrationHealth(Component):
    """
    Central system for tracking integration health across components.
    
    This class collects health metrics from components, detects health status
    changes, and provides visualization data for monitoring interfaces.
    """
    
    def __init__(self, polling_interval: float = 60.0):
        """
        Initialize the integration health tracker.
        
        Args:
            polling_interval: How often to poll components for health metrics (in seconds)
        """
        # Initialize with required Component parameters
        super().__init__(
            component_id="system.integration_health",
            component_type="monitoring",
            version="1.0.0"
        )
        self.name = "Integration Health Monitor"
        self.polling_interval = polling_interval
        self.metrics_history: Dict[str, List[HealthMetric]] = {}
        self.latest_metrics: Dict[str, Dict[str, HealthMetric]] = {}
        self.health_providers: Dict[str, HealthProvider] = {}
        self.status_cache: Dict[str, HealthStatus] = {}
        self._stop_polling = threading.Event()
        self._polling_thread: Optional[threading.Thread] = None
    
    def register_health_provider(self, component_id: str, provider: HealthProvider) -> None:
        """
        Register a component that provides health metrics.
        
        Args:
            component_id: ID of the component
            provider: The health provider implementation
        """
        self.health_providers[component_id] = provider
        self.metrics_history[component_id] = []
        self.latest_metrics[component_id] = {}
        self.status_cache[component_id] = HealthStatus.UNKNOWN
    
    def unregister_health_provider(self, component_id: str) -> None:
        """
        Unregister a health provider.
        
        Args:
            component_id: ID of the component to unregister
        """
        if component_id in self.health_providers:
            del self.health_providers[component_id]
            # Keep history and latest metrics for reference
    
    def collect_metrics(self, component_id: Optional[str] = None) -> Dict[str, List[HealthMetric]]:
        """
        Collect health metrics from registered providers.
        
        Args:
            component_id: Specific component to collect from (None for all)
            
        Returns:
            Dictionary mapping component IDs to their metrics
        """
        results: Dict[str, List[HealthMetric]] = {}
        
        if component_id is not None:
            if component_id not in self.health_providers:
                raise IntegrationHealthError(f"Unknown component ID: {component_id}")
            provider = self.health_providers[component_id]
            metrics = provider.get_health_metrics()
            results[component_id] = metrics
            self._update_metrics(component_id, metrics)
        else:
            for c_id, provider in self.health_providers.items():
                try:
                    metrics = provider.get_health_metrics()
                    results[c_id] = metrics
                    self._update_metrics(c_id, metrics)
                except Exception as e:
                    # If a provider fails, create an error metric
                    error_metric = HealthMetric(
                        name="health_collection_error",
                        value=1.0,
                        metric_type=HealthMetricType.ERROR_RATE,
                        component_id=c_id,
                        metadata={"error": str(e)}
                    )
                    results[c_id] = [error_metric]
                    self._update_metrics(c_id, [error_metric])
        
        return results
    
    def _update_metrics(self, component_id: str, metrics: List[HealthMetric]) -> None:
        """
        Update stored metrics and check for status changes.
        
        Args:
            component_id: Component ID
            metrics: List of new metrics
        """
        # Store metrics in history
        if component_id not in self.metrics_history:
            self.metrics_history[component_id] = []
        
        # Add to history and keep latest for each metric name
        for metric in metrics:
            self.metrics_history[component_id].append(metric)
            
            # Update latest metrics
            if component_id not in self.latest_metrics:
                self.latest_metrics[component_id] = {}
            self.latest_metrics[component_id][metric.name] = metric
        
        # Trim history if needed (keep last 1000 metrics per component)
        if len(self.metrics_history[component_id]) > 1000:
            self.metrics_history[component_id] = self.metrics_history[component_id][-1000:]
        
        # Check for status changes
        self._check_status_changes(component_id)
    
    def _check_status_changes(self, component_id: str) -> None:
        """
        Check if component health status has changed.
        
        Args:
            component_id: Component to check
        """
        if component_id in self.health_providers:
            try:
                new_status = self.health_providers[component_id].get_health_status()
                old_status = self.status_cache.get(component_id, HealthStatus.UNKNOWN)
                
                if new_status != old_status:
                    # Status has changed, fire an event
                    # Include the first failing metric if status is worse
                    triggering_metric = None
                    if (new_status in (HealthStatus.FAILING, HealthStatus.CRITICAL) and 
                            component_id in self.latest_metrics):
                        # Find first critical/failing metric
                        for metric in self.latest_metrics[component_id].values():
                            if metric.get_status() in (HealthStatus.FAILING, HealthStatus.CRITICAL):
                                triggering_metric = metric
                                break
                    
                    # If no failing metric found, use first available
                    if not triggering_metric and component_id in self.latest_metrics:
                        metrics = list(self.latest_metrics[component_id].values())
                        if metrics:
                            triggering_metric = metrics[0]
                    
                    # Create a default metric if none available
                    if not triggering_metric:
                        triggering_metric = HealthMetric(
                            name="status_change",
                            value=1.0,
                            metric_type=HealthMetricType.CUSTOM,
                            component_id=component_id,
                        )
                    
                    # Fire event
                    event = HealthEvent(
                        component_id=component_id,
                        metric=triggering_metric,
                        old_status=old_status,
                        new_status=new_status
                    )
                    
                    # Update status
                    self.status_cache[component_id] = new_status
                    
                    # Publish event - we'll integrate with EventBus later
                    # For now we'll just print it for testing
                    # In a real implementation, we would do:
                    # from integrations.events.event_bus import EventBus
                    # EventBus().publish(event)
                    print(f"Health status changed for {component_id}: {old_status} -> {new_status}")
            except Exception as e:
                # If status collection fails, set to UNKNOWN
                self.status_cache[component_id] = HealthStatus.UNKNOWN
                print(f"Error checking health status for {component_id}: {str(e)}")
    
    def start_polling(self) -> None:
        """Start background polling of health metrics."""
        if self._polling_thread is not None and self._polling_thread.is_alive():
            return  # Already polling
        
        self._stop_polling.clear()
        self._polling_thread = threading.Thread(
            target=self._polling_loop,
            daemon=True,
            name="HealthMetricsPoller"
        )
        self._polling_thread.start()
    
    def stop_polling(self) -> None:
        """Stop background polling of health metrics."""
        if self._polling_thread is not None:
            self._stop_polling.set()
            self._polling_thread.join(timeout=5.0)
            self._polling_thread = None
    
    def _polling_loop(self) -> None:
        """Background thread that periodically polls health providers."""
        while not self._stop_polling.is_set():
            try:
                self.collect_metrics()
            except Exception as e:
                print(f"Error in health metrics polling: {str(e)}")
            
            # Sleep until next poll or until stopped
            self._stop_polling.wait(self.polling_interval)
    
    def get_component_health_status(self, component_id: str) -> HealthStatus:
        """
        Get the current health status of a component.
        
        Args:
            component_id: Component to check
            
        Returns:
            Current health status
        """
        if component_id not in self.health_providers:
            return HealthStatus.UNKNOWN
        
        return self.status_cache.get(component_id, HealthStatus.UNKNOWN)
    
    def get_overall_system_health(self) -> HealthStatus:
        """
        Get the overall health of the system.
        
        Returns:
            Overall system health status
        """
        if not self.status_cache:
            return HealthStatus.UNKNOWN
        
        # System is as healthy as its least healthy component
        status_priorities = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 1,
            HealthStatus.FAILING: 2,
            HealthStatus.CRITICAL: 3,
            HealthStatus.UNKNOWN: 4
        }
        
        worst_status = HealthStatus.HEALTHY
        for status in self.status_cache.values():
            if status_priorities[status] > status_priorities[worst_status]:
                worst_status = status
        
        return worst_status
    
    def get_health_visualization_data(self) -> Dict[str, Any]:
        """
        Get data for health visualization dashboards.
        
        Returns:
            Dictionary with visualization-ready data
        """
        result = {
            'overall_status': self.get_overall_system_health().name,
            'component_status': {
                component_id: status.name
                for component_id, status in self.status_cache.items()
            },
            'metrics_summary': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Add metric summaries
        for component_id, metrics in self.latest_metrics.items():
            result['metrics_summary'][component_id] = {
                metric_name: {
                    'value': metric.value,
                    'status': metric.get_status().name,
                    'timestamp': metric.timestamp.isoformat()
                }
                for metric_name, metric in metrics.items()
            }
        
        return result
    
    def collect_metric(self, key: str, value: Any) -> None:
        """
        Set a metric for testing purposes.
        
        Args:
            key: The metric key
            value: The metric value
        """
        if not hasattr(self, '_test_metrics'):
            self._test_metrics = {}
        self._test_metrics[key] = value
    
    def get_metric(self, key: str) -> Any:
        """
        Get a metric value for testing purposes.
        
        Args:
            key: The metric key
            
        Returns:
            The metric value or None if not found
        """
        if not hasattr(self, '_test_metrics'):
            self._test_metrics = {}
        return self._test_metrics.get(key, None)
    
    def create_timer_metric(self, name: str, component_id: str) -> Callable[[], HealthMetric]:
        """
        Create a timer for measuring operation duration.
        
        Args:
            name: Metric name
            component_id: Component ID
            
        Returns:
            Function that stops timing and returns a HealthMetric
        """
        start_time = time.time()
        
        def stop_timer(threshold_warning: Optional[float] = None,
                       threshold_critical: Optional[float] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> HealthMetric:
            duration = time.time() - start_time
            return HealthMetric(
                name=name,
                value=duration,
                metric_type=HealthMetricType.RESPONSE_TIME,
                component_id=component_id,
                threshold_warning=threshold_warning,
                threshold_critical=threshold_critical,
                metadata=metadata
            )
        
        return stop_timer
