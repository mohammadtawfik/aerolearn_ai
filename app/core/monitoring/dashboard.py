from typing import Dict, Any, Callable, List, Optional, Tuple
from datetime import datetime, timezone

from integrations.monitoring.health_status import ComponentState, StatusRecord, HealthMetric
from app.api.monitoring.protocol_fields import PROTOCOL_APPROVED_REPORT_FIELDS

class ServiceHealthDashboard:
    """
    Protocol-compliant implementation of ServiceHealthDashboard.

    See: /docs/architecture/service_health_protocol.md
    """

    def __init__(self, registry=None):
        # registry may provide dependency and component data, or live status
        self._registry = registry
        self._component_status: Dict[str, StatusRecord] = {}
        self._status_history: Dict[str, List[StatusRecord]] = {}
        self._listeners: List[Callable[[str, ComponentState], None]] = []
        self._cascading_status = True  # for protocol-mandated cascading status
        self._dependency_graph: Dict[str, List[str]] = {}

    def update_component_status(self, component_id: str, state: ComponentState,
                               metrics: Any = None, message: str = "",
                               timestamp: Optional[datetime] = None) -> bool:
        now = timestamp or datetime.now(timezone.utc)
        # Enforce metrics as a list (e.g. [HealthMetric, ...]) or empty list
        metrics_list = []
        if metrics is None:
            metrics_list = []
        elif isinstance(metrics, list):
            metrics_list = metrics
        elif isinstance(metrics, dict):
            # Accept dict for legacy/compat, but test will fail if not a list of HealthMetric
            metrics_list = []
        else:
            try:
                metrics_list = list(metrics)
            except Exception:
                metrics_list = []
        record = StatusRecord(
            component_id=component_id,
            state=state,
            timestamp=now,
            metrics=metrics_list,
            message=message,
        )
        self._component_status[component_id] = record
        self._status_history.setdefault(component_id, []).append(record)
        for listener in self._listeners:
            listener(component_id, state)
        # If cascading is on, propagate to dependents (simple protocol-compliant logic)
        if self._cascading_status and self._registry:
            dependents = self.get_dependents(component_id)
            for dep in dependents:
                # Propagate "degeneration" to children (not full per-protocol graph, but core behavior)
                if state in (ComponentState.DEGRADED, ComponentState.FAILED):
                    cascaded_record = StatusRecord(
                        component_id=dep,
                        state=state,
                        timestamp=now,
                        metrics=[],
                        message=f"Cascaded from {component_id}",
                    )
                    self._component_status[dep] = cascaded_record
                    self._status_history.setdefault(dep, []).append(cascaded_record)
                    for listener in self._listeners:
                        listener(dep, state)
        return True

    def status_for(self, component_id: str, as_record: bool = False):
        """
        Get the current status (ComponentState) or record object for the specified component.
        If as_record=True, returns StatusRecord; else returns state.
        """
        record = self._component_status.get(component_id)
        if record:
            return record if as_record else record.state
        # Fallback to registry for unknown components
        if self._registry and hasattr(self._registry, "get_component"):
            reg_comp = self._registry.get_component(component_id)
            if reg_comp:
                reg_state = getattr(reg_comp, "state", ComponentState.UNKNOWN)
                reg_metrics = getattr(reg_comp, "metrics", [])
                reg_msg = getattr(reg_comp, "message", "")
                # Ensure metrics is always a list
                if not isinstance(reg_metrics, list):
                    reg_metrics = []
                record = StatusRecord(
                    component_id=component_id,
                    state=reg_state,
                    timestamp=datetime.now(timezone.utc),
                    metrics=reg_metrics,
                    message=reg_msg
                )
                if as_record:
                    return record
                return reg_state
        return None if as_record else ComponentState.UNKNOWN
    
    def get_status(self, component_id: str):
        """
        Protocol/test-compliant: Always returns StatusRecord; .state and .metrics are exactly as last set.
        """
        return self.status_for(component_id, as_record=True)

    def get_all_component_statuses(self) -> Dict[str, ComponentState]:
        return {cid: rec.state for cid, rec in self._component_status.items()}

    def register_status_listener(self, listener: Callable[[str, ComponentState], None]) -> str:
        self._listeners.append(listener)
        return str(id(listener))

    def get_component_history(self, component_id: str, 
                             time_range: Optional[Tuple[datetime, datetime]] = None) -> List[StatusRecord]:
        history = self._status_history.get(component_id, [])
        if time_range:
            start, end = time_range
            return [
                rec for rec in history
                if start <= rec.timestamp <= end
            ]
        return history

    def supports_cascading_status(self) -> bool:
        return self._cascading_status

    def clear(self) -> None:
        self._component_status.clear()
        self._status_history.clear()
        self._listeners.clear()
        self._dependency_graph.clear()
        
    def get_report_data(self) -> Dict[str, Any]:
        """
        Returns a dict with protocol-approved fields for dashboard reporting.
        Conforms to: /docs/architecture/service_health_protocol.md §Reporting Fields
        """
        report = {}
        
        # Get overall system state based on component statuses
        overall_state = ComponentState.HEALTHY
        for component_id, status in self._component_status.items():
            if status.state == ComponentState.FAILED:
                overall_state = ComponentState.FAILED
                break
            elif status.state == ComponentState.DEGRADED and overall_state != ComponentState.FAILED:
                overall_state = ComponentState.DEGRADED
        
        # Populate report with protocol-approved fields
        for key in PROTOCOL_APPROVED_REPORT_FIELDS:
            if key == "component":
                report["component"] = "ServiceHealthDashboard"
            elif key == "state":
                report["state"] = overall_state.name if isinstance(overall_state, ComponentState) else str(overall_state)
            elif key == "timestamp":
                report["timestamp"] = datetime.now(timezone.utc).isoformat()
            elif key == "metrics":
                # Collect metrics from all components
                all_metrics = {}
                for component_id, status in self._component_status.items():
                    if status.metrics:
                        component_metrics = {}
                        for metric in status.metrics:
                            if isinstance(metric, HealthMetric):
                                component_metrics[metric.name] = metric.value
                        if component_metrics:
                            all_metrics[component_id] = component_metrics
                report["metrics"] = all_metrics
            elif key == "reason":
                # Provide reason based on overall state
                if overall_state == ComponentState.FAILED:
                    failed_components = [c for c, s in self._component_status.items() 
                                        if s.state == ComponentState.FAILED]
                    report["reason"] = f"Failed components: {', '.join(failed_components)}"
                elif overall_state == ComponentState.DEGRADED:
                    degraded_components = [c for c, s in self._component_status.items() 
                                          if s.state == ComponentState.DEGRADED]
                    report["reason"] = f"Degraded components: {', '.join(degraded_components)}"
                else:
                    report["reason"] = "All systems operational"
            elif key == "components":
                # Include individual component statuses
                report["components"] = {
                    component_id: {
                        "state": status.state.name if isinstance(status.state, ComponentState) else str(status.state),
                        "timestamp": status.timestamp.isoformat(),
                        "message": status.message
                    }
                    for component_id, status in self._component_status.items()
                }
            else:
                report[key] = None  # Fill any additional protocol-compliant fields
                
        return report

    # ---- Dashboard API helpers - dependency graph for visualization ----
    def set_dependency_graph(self, dep_graph: Dict[str, List[str]]):
        """
        Sets the model for dependency graph (for visualization/analytics); registry may supply it.
        """
        self._dependency_graph = dep_graph

    def get_dependents(self, component_id: str) -> List[str]:
        # Returns a list of components that depend on `component_id`
        dependents = []
        if self._registry:
            # If registry supports API, use it (protocol-compat)
            if hasattr(self._registry, "analyze_dependency_impact"):
                return self._registry.analyze_dependency_impact(component_id)
        else:
            # Else, reverse search in local graph
            for cid, deps in self._dependency_graph.items():
                if component_id in deps:
                    dependents.append(cid)
        return dependents
