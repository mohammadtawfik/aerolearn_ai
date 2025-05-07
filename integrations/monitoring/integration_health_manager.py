# /integrations/monitoring/integration_health_manager.py
"""Protocol-compliant implementation for IntegrationHealthManager
Location: /integrations/monitoring/integration_health_manager.py
Aligns with: /docs/architecture/health_monitoring_protocol.md, /docs/development/integration_health_modularization_plan.md
"""

from typing import List, Callable, Dict, Any, Optional
from datetime import datetime, timezone
from integrations.monitoring.health_status import HealthStatus, HealthMetric, StatusRecord

class IntegrationHealth:
    """
    Protocol/root class for orchestration required in TDD/protocol. To be fully realized in later steps.
    """
    pass

class IntegrationHealthManager:
    """Protocol-compliant implementation for the main IntegrationHealth orchestration module.
    See /docs/architecture/health_monitoring_protocol.md for all method contracts.
    """
    def __init__(self):
        # Store component information: {component_id: {description, version, current_status, history, metrics}}
        self._components: Dict[str, Dict[str, Any]] = {}
        # Store alert callbacks
        self._alert_callbacks: List[Callable[[str, HealthStatus], None]] = []
        # Track previous status for alert/callback edge detection
        self._last_status: Dict[str, Optional[HealthStatus]] = {}

    def register_component(self, component_id: str, description: str, version: str):
        """Register a new component for health monitoring.
        
        Args:
            component_id: Unique identifier for the component
            description: Human-readable description of the component
            version: Version string of the component
        """
        if component_id not in self._components:
            self._components[component_id] = {
                "description": description,
                "version": version,
                "current_status": None,
                "history": [],
                "metrics": []
            }

    def update_component_status(self, component_id: str, status: HealthStatus, metrics: Dict[str, Any]=None, message: Optional[str]=None, timestamp: Optional[datetime]=None):
        """Update the health status of a registered component.
        
        Args:
            component_id: Unique identifier for the component
            status: Current health status of the component
            metrics: Optional metrics to include with the status
            message: Optional message describing the status
            timestamp: Optional timestamp for the status update
        """
        if component_id not in self._components:
            raise ValueError(f"Component {component_id} not registered")
        
        now = timestamp or datetime.now(timezone.utc)
        record = StatusRecord(
            component_id=component_id,
            state=status,
            timestamp=now,
            metrics=metrics or {},
            message=message
        )
        
        self._components[component_id]["current_status"] = record
        self._components[component_id]["history"].append(record)
        
        # Check if we need to trigger alert callbacks
        prev_status = self._last_status.get(component_id)
        if prev_status != status:
            # Notify callbacks on status change
            for callback in self._alert_callbacks:
                callback(component_id, status)
            
            # Update last notified status
            self._last_status[component_id] = status

    def get_component_status(self, component_id: str) -> Optional[StatusRecord]:
        """Get the current health status of a component.
        
        Args:
            component_id: Unique identifier for the component
            
        Returns:
            Current health status record of the component
        """
        comp = self._components.get(component_id)
        if not comp:
            raise ValueError(f"Component {component_id} not registered")
            
        return comp["current_status"]

    def record_metric(self, component_id: str, metric: HealthMetric):
        """Record a health metric for a component.
        
        Args:
            component_id: Unique identifier for the component
            metric: Health metric to record
        """
        if component_id not in self._components:
            raise ValueError(f"Component {component_id} not registered")
            
        # Add timestamp if not present
        if not hasattr(metric, 'timestamp') or metric.timestamp is None:
            metric.timestamp = datetime.now(timezone.utc)
            
        self._components[component_id]["metrics"].append(metric)
        
        # Update the current status record's metrics if it exists
        current_status = self._components[component_id].get("current_status")
        if current_status:
            # Use metric.type directly for string matching in tests
            current_status.metrics[metric.type] = metric.value

    def get_component_metrics(self, component_id: str) -> List[HealthMetric]:
        """Get all recorded metrics for a component.
        
        Args:
            component_id: Unique identifier for the component
            
        Returns:
            List of health metrics for the component
            
        Note:
            Supports direct string type matching as required by tests.
        """
        comp = self._components.get(component_id)
        if comp is None:
            return []
        return comp["metrics"]
        
    def get_component_history(self, component_id: str) -> List[StatusRecord]:
        """Get the status history for a component.
        
        Args:
            component_id: Unique identifier for the component
            
        Returns:
            List of status records for the component
        """
        comp = self._components.get(component_id)
        if not comp:
            return []
        return comp['history']

    def register_alert_callback(self, cb: Callable[[str, HealthStatus], None]):
        """Register a callback to be called when component health changes.
        
        Args:
            cb: Callback function that takes component_id and status
        """
        self._alert_callbacks.append(cb)
    def clear(self):
        """Reset all health manager state for test isolation.
        """
        self._components.clear()
        self._alert_callbacks.clear()
        self._last_status.clear()
