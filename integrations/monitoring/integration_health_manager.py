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
    def __init__(self, registry=None, dashboard=None):
        """
        Accept a ComponentRegistry for orchestration, testing, and system state coordination.
        Optionally accept a ServiceHealthDashboard for protocol/test compliance and event propagation.
        
        Args:
            registry: Optional ComponentRegistry for orchestration and system state coordination
            dashboard: Optional ServiceHealthDashboard for monitoring/integration
        """
        self.registry = registry
        self.dashboard = dashboard
        # Store component information: {component_id: {description, version, current_status, history, metrics}}
        self._components: Dict[str, Dict[str, Any]] = {}
        # Store alert callbacks
        self._alert_callbacks: List[Callable[[str, HealthStatus], None]] = []
        # Track previous status for alert/callback edge detection
        self._last_status: Dict[str, Optional[HealthStatus]] = {}

    def register_component(self, component_id: str, description: str = None, version: str = None, **kwargs):
        """Register a new component for health monitoring.
        
        Args:
            component_id: Unique identifier for the component
            description: Optional human-readable description of the component
            version: Optional version string of the component
            **kwargs: Additional component parameters
        """
        # Try to lookup description/version from registry if not provided
        if self.registry and (description is None or version is None):
            component_obj = self._fetch_registry_component(component_id)
            
            if component_obj:
                if description is None:
                    description = getattr(component_obj, 'description', None)
                if version is None:
                    version = getattr(component_obj, 'version', None)
        
        if component_id not in self._components:
            self._components[component_id] = {
                "description": description,
                "version": version,
                "current_status": None,
                "history": [],
                "metrics": [],
                "state": None  # Track exact last enum value for protocol/test pass
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
        self._ensure_registered(component_id)
        
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
        self._components[component_id]["state"] = status  # Preserve for dashboard update
        
        # Check if we need to trigger alert callbacks
        prev_status = self._last_status.get(component_id)
        if prev_status != status:
            # Notify callbacks on status change
            for callback in self._alert_callbacks:
                callback(component_id, status)
            
            # Update last notified status
            self._last_status[component_id] = status
            
        # Propagate status and metrics to dashboard, if present
        if self.dashboard is not None:
            self.dashboard.update_component_status(component_id, status, metrics=metrics or {}, message=message, timestamp=now)

    def _fetch_registry_component(self, component_id):
        """
        Attempt to fetch a component from the registry using multiple protocol-compliant methods.
        
        Args:
            component_id: Unique identifier for the component
            
        Returns:
            Component object if found, None otherwise
        """
        reg = self.registry
        if not reg:
            return None
            
        # 1. Preferred: get_component()
        if hasattr(reg, "get_component"):
            try:
                obj = reg.get_component(component_id)
                if obj: return obj
            except Exception: pass
            
        # 2. .get()
        if hasattr(reg, "get"):
            try:
                obj = reg.get(component_id)
                if obj: return obj
            except Exception: pass
            
        # 3. __getitem__
        if hasattr(reg, "__getitem__"):
            try:
                obj = reg[component_id]
                if obj: return obj
            except Exception: pass
            
        # 4. .components dict attribute
        if hasattr(reg, "components"):
            components = getattr(reg, "components")
            if components and component_id in components:
                return components[component_id]
                
        # 5. Try enumerating registry (protocol method for listing component IDs)
        for attr in ["get_registered_component_ids", "list_components"]:
            if hasattr(reg, attr):
                try:
                    ids = getattr(reg, attr)()
                    if component_id in ids:
                        # Attempt to retrieve via get_component or fallback
                        try:
                            if hasattr(reg, "get_component"):
                                obj = reg.get_component(component_id)
                                if obj: return obj
                            elif hasattr(reg, "get"):
                                obj = reg.get(component_id)
                                if obj: return obj
                            elif hasattr(reg, "__getitem__"):
                                obj = reg[component_id]
                                if obj: return obj
                        except Exception: pass
                except Exception: pass
                
        # 6. As a last ditch, try to iterate keys of registry's components dict attribute
        if hasattr(reg, "components"):
            try:
                components = getattr(reg, "components")
                if isinstance(components, dict):
                    if component_id in components:
                        return components[component_id]
            except Exception: pass
            
        # Not found
        return None

    def _ensure_registered(self, component_id):
        """
        Internal: Ensure a component is registered in manager._components.
        If not, and present in self.registry, auto-register (copying description, version).
        Looks up using the protocol-compliant get_component() from registry, or appropriate fallback.
        """
        if component_id not in self._components:
            if not self.registry:
                raise ValueError(f"Component {component_id} not registered")
                
            component_obj = self._fetch_registry_component(component_id)
                    
            if component_obj is not None:
                desc = getattr(component_obj, "description", None)
                ver = getattr(component_obj, "version", None)
                self.register_component(component_id, description=desc, version=ver)
            else:
                # Protocol diagnostics: enumerate all known IDs for debugging
                reg = self.registry
                known_ids = []
                # Try common enumeration protocols for diagnostics
                if hasattr(reg, "get_registered_component_ids"):
                    try: known_ids = getattr(reg, "get_registered_component_ids")()
                    except Exception: known_ids = []
                elif hasattr(reg, "list_components"):
                    try: known_ids = getattr(reg, "list_components")()
                    except Exception: known_ids = []
                elif hasattr(reg, "components"):
                    try: known_ids = list(getattr(reg, "components").keys())
                    except Exception: known_ids = []
                
                raise ValueError(
                    f"Component {component_id} not registered (registry has: {known_ids})"
                )

    def get_component_status(self, component_id: str) -> Optional[StatusRecord]:
        """Get the current health status of a component.
        
        Args:
            component_id: Unique identifier for the component
            
        Returns:
            Current health status record of the component
        """
        self._ensure_registered(component_id)
        return self._components[component_id]["current_status"]
        
    def get_status(self, component_id: str) -> HealthStatus:
        """Return latest HealthStatus for the given component_id.
        If no status exists, return HealthStatus.UNKNOWN
        
        Args:
            component_id: Unique identifier for the component
            
        Returns:
            Current HealthStatus of the component or UNKNOWN if not set
        """
        self._ensure_registered(component_id)
        comp = self._components.get(component_id)
        if comp and comp.get("current_status") is not None:
            return comp["current_status"].state
        return HealthStatus.UNKNOWN

    def record_metric(self, component_id: str, metric: HealthMetric):
        """Record a health metric for a component.
        
        Args:
            component_id: Unique identifier for the component
            metric: Health metric to record
        """
        self._ensure_registered(component_id)
            
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
        self._ensure_registered(component_id)
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
        self._ensure_registered(component_id)
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
        
    def update_health(self, component_id: str, status: HealthStatus, metrics: Dict[str, Any]=None, message: Optional[str]=None, timestamp: Optional[datetime]=None):
        """
        Protocol-compliant method to update health status for a component. Alias for update_component_status.
        """
        return self.update_component_status(component_id, status, metrics=metrics, message=message, timestamp=timestamp)

    def process_health_event(self, event):
        """
        Protocol-compliant method to process a HealthEvent.
        Updates internal state, and notifies dashboard (if present).
        """
        cid = getattr(event, "component", None)
        state = getattr(event, "state", None)
        metrics = getattr(event, "metrics", None)
        message = getattr(event, "reason", None)
        timestamp = getattr(event, "timestamp", None)
        if cid is None or state is None:
            raise ValueError("Event must have component and state attributes")
        self._ensure_registered(cid)
        self.update_component_status(cid, state, metrics=metrics, message=message, timestamp=timestamp)
        # Optionally propagate to dashboard if available
        if hasattr(self, "dashboard") and self.dashboard:
            self.dashboard.update_component_status(cid, state)

    def update_health_with_metrics(self, component_id: str, metrics):
        """
        Protocol-compliant method to update a component with a batch of metrics.
        Args:
            component_id: Unique id for the component
            metrics: List of HealthMetric objects
        """
        self._ensure_registered(component_id)
        metrics_list = list(metrics) if metrics is not None else []
        for metric in metrics_list:
            self.record_metric(component_id, metric)
            
        # After recording, propagate combined last state and metrics to dashboard
        # Prefer exactly the last state set for this component (even if None)
        last_state = self._components[component_id].get("state", HealthStatus.UNKNOWN)
        # Compose metrics list for dashboard propagation
        all_metrics = self.get_component_metrics(component_id)
        if self.dashboard is not None:
            self.dashboard.update_component_status(component_id, last_state, metrics=all_metrics)
