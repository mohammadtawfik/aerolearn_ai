from typing import Dict, Any, Callable, List, Optional, Tuple
from datetime import datetime, timezone

from integrations.monitoring.health_status import ComponentState, StatusRecord

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
                               metrics: Dict = None, message: str = "",
                               timestamp: Optional[datetime] = None) -> bool:
        now = timestamp or datetime.now(timezone.utc)
        record = StatusRecord(
            component_id=component_id,
            state=state,
            timestamp=now,
            metrics=metrics or {},
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
                    self._component_status[dep] = StatusRecord(
                        component_id=dep,
                        state=state,
                        timestamp=now,
                        metrics={},
                        message=f"Cascaded from {component_id}",
                    )
                    self._status_history.setdefault(dep, []).append(self._component_status[dep])
                    for listener in self._listeners:
                        listener(dep, state)
        return True

    def status_for(self, component_id: str) -> ComponentState:
        record = self._component_status.get(component_id)
        return record.state if record else ComponentState.UNKNOWN

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