"""
Integration health monitoring for the AeroLearn AI system.

This module provides health metric collection, status tracking, and visualization
data structures for monitoring the health of system integrations.
"""

from abc import ABC, abstractmethod
from collections import defaultdict
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
    It also supports real-time notifications of health status changes through
    a listener pattern.
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
        self._health_listeners: List[Callable[[str, HealthStatus, HealthStatus], None]] = []
    
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
                    
                    # Notify health status listeners
                    self._notify_health_listeners(component_id, old_status, new_status)
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
        
    def add_status_listener(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Register a callback to be triggered on integration status updates.
        
        The callback will be called with (point_name, status_data) whenever
        a transaction is logged or a failure is reported.
        
        Args:
            callback: Function that takes (point_name, status_data) parameters
        """
        self._listeners.append(callback)
        
    def remove_status_listener(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Remove a previously registered status listener.
        
        Args:
            callback: The callback function to remove
        """
        if callback in self._listeners:
            self._listeners.remove(callback)
            
    def _notify_status_listeners(self, point: str, status: Dict[str, Any]) -> None:
        """
        Internal method to notify all registered listeners about a status change.
        
        Args:
            point: Integration point name
            status: Status data dictionary
        """
        for listener in self._listeners:
            try:
                listener(point, status)
            except Exception as e:
                print(f"Error in status listener: {str(e)}")
    
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
        
    def add_health_listener(self, callback: Callable[[str, HealthStatus, HealthStatus], None]) -> None:
        """
        Register a callback to be notified when component health status changes.
        
        Args:
            callback: Function that takes (component_id, old_status, new_status) parameters
        """
        self._health_listeners.append(callback)
        
    def remove_health_listener(self, callback: Callable[[str, HealthStatus, HealthStatus], None]) -> None:
        """
        Remove a previously registered health listener.
        
        Args:
            callback: The callback function to remove
        """
        if callback in self._health_listeners:
            self._health_listeners.remove(callback)
            
    def _notify_health_listeners(self, component_id: str, old_status: HealthStatus, new_status: HealthStatus) -> None:
        """
        Internal method to notify all registered listeners about health status changes.
        
        Args:
            component_id: Component identifier
            old_status: Previous health status
            new_status: New health status
        """
        for listener in self._health_listeners:
            try:
                listener(component_id, old_status, new_status)
            except Exception as e:
                print(f"Error in health listener: {str(e)}")


class IntegrationMonitor:
    """
    Monitors integration points for transaction success, performance, and failures.
    
    This class provides methods to log transactions, report failures, and retrieve
    performance statistics for integration points. It also supports real-time
    status notifications through a listener pattern.
    """
    
    def __init__(self):
        """Initialize the integration monitor."""
        self._transactions = {}
        self._failures = defaultdict(list)
        self._performance_stats = defaultdict(lambda: {"count": 0, "total_ms": 0, "failures": 0})
        self._listeners = []
    
    def log_transaction(self, point: str, success: bool, duration_ms: Optional[float] = None) -> str:
        """
        Log a transaction with an integration point.
        
        Args:
            point: Name of the integration point
            success: Whether the transaction was successful
            duration_ms: Duration of the transaction in milliseconds
            
        Returns:
            Transaction ID (str) that can be used to retrieve transaction details later
        """
        txn_id = str(uuid.uuid4())
        self._transactions[txn_id] = {
            "point": point,
            "success": success,
            "timestamp": datetime.now(),
            "duration_ms": duration_ms
        }
        
        # Update performance stats
        stats = self._performance_stats[point]
        stats["count"] += 1
        if not success:
            stats["failures"] += 1
        if duration_ms is not None:
            stats["total_ms"] += duration_ms
        
        # Notify listeners about this transaction
        self._notify_status_listeners(point, {
            "type": "transaction",
            "success": success,
            "txn_id": txn_id,
            "duration_ms": duration_ms
        })
        
        return txn_id
    
    def get_transaction(self, txn_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific transaction.
        
        Args:
            txn_id: Transaction ID
            
        Returns:
            Transaction details or None if not found
        """
        return self._transactions.get(txn_id)
    
    def report_failure(self, point: str, error: Any) -> None:
        """
        Report a failure with an integration point.
        
        Args:
            point: Name of the integration point
            error: Error information (exception or error message)
        """
        failure_entry = {
            "timestamp": datetime.now(),
            "error": str(error)
        }
        self._failures[point].append(failure_entry)
        
        # Update failure count in performance stats
        if point in self._performance_stats:
            self._performance_stats[point]["failures"] += 1
            
        # Notify listeners about this failure
        self._notify_status_listeners(point, {
            "type": "failure",
            "error": str(error),
            "details": failure_entry
        })
    
    def get_recent_failures(self, point: str) -> List[Dict[str, Any]]:
        """
        Get recent failures for an integration point.
        
        Args:
            point: Name of the integration point
            
        Returns:
            List of recent failures
        """
        return self._failures.get(point, [])
    
    def get_performance_stats(self, point: str) -> Dict[str, Any]:
        """
        Get performance statistics for an integration point.
        
        Args:
            point: Name of the integration point
            
        Returns:
            Performance statistics dictionary containing:
            - count: Total number of transactions
            - total_ms: Total duration in milliseconds
            - failures: Number of failed transactions
            - success_rate: Ratio of successful transactions (if count > 0)
            - avg_duration_ms: Average transaction duration (if count > 0)
        """
        stats = self._performance_stats.get(point, {"count": 0, "total_ms": 0, "failures": 0})
        
        # Calculate derived metrics
        result = dict(stats)
        if stats["count"] > 0:
            result["success_rate"] = (stats["count"] - stats["failures"]) / stats["count"]
            if stats["total_ms"] > 0:
                result["avg_duration_ms"] = stats["total_ms"] / stats["count"]
        
        return result


class IntegrationPointRegistry:
    """
    Registry for integration points in the system.
    
    This class maintains a registry of all integration points and provides
    methods to register and retrieve them. It also supports notifications
    when integration points are registered or updated.
    """
    
    def __init__(self):
        """Initialize the integration point registry."""
        self._points = {}
        self._listeners = []
    
    def register_integration_point(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register an integration point.
        
        Args:
            name: Name of the integration point
            metadata: Additional metadata about the integration point, such as:
                     - type: The type of integration (API, database, etc.)
                     - owner: Team or person responsible for this integration
                     - description: Human-readable description
                     - url: Endpoint URL if applicable
        """
        point_data = {
            "name": name,
            "registered_at": datetime.now(),
            "metadata": metadata or {}
        }
        
        is_update = name in self._points
        self._points[name] = point_data
        
        # Notify listeners
        self._notify_listeners(name, point_data, is_update)
    
    def get_all_points(self) -> List[str]:
        """
        Get all registered integration points.
        
        Returns:
            List of integration point names
        """
        return list(self._points.keys())
    
    def get_point_details(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific integration point.
        
        Args:
            name: Name of the integration point
            
        Returns:
            Integration point details or None if not found
        """
        return self._points.get(name)
        
    def add_registry_listener(self, callback: Callable[[str, Dict[str, Any], bool], None]) -> None:
        """
        Register a callback to be notified when integration points are registered or updated.
        
        Args:
            callback: Function that takes (name, point_data, is_update) parameters
        """
        self._listeners.append(callback)
        
    def remove_registry_listener(self, callback: Callable[[str, Dict[str, Any], bool], None]) -> None:
        """
        Remove a previously registered listener.
        
        Args:
            callback: The callback function to remove
        """
        if callback in self._listeners:
            self._listeners.remove(callback)
            
    def _notify_listeners(self, name: str, point_data: Dict[str, Any], is_update: bool) -> None:
        """
        Internal method to notify all registered listeners about registry changes.
        
        Args:
            name: Integration point name
            point_data: Integration point data
            is_update: Whether this is an update to an existing point
        """
        for listener in self._listeners:
            try:
                listener(name, point_data, is_update)
            except Exception as e:
                print(f"Error in registry listener: {str(e)}")
