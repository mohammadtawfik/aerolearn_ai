from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from integrations.monitoring.health_status import ComponentState, StatusRecord

class ComponentEntity:
    """Entity representing a registered component, for protocol-compliant attribute access."""
    def __init__(self, component_id: str, description: str = None, version: str = None, **kwargs):
        self.component_id = component_id
        self.description = description
        self.version = version
        self.metadata = kwargs

class MonitoringComponentRegistry:
    """
    Protocol-compliant monitoring registry for dashboards/integration tests.
    Allows registration, status update, state/history retrieval, and TDD reset.
    """

    def __init__(self):
        self._components: Dict[str, Dict[str, str]] = {}  # id → {description, version}
        self._status: Dict[str, StatusRecord] = {}        # id → latest StatusRecord
        self._history: Dict[str, List[StatusRecord]] = {} # id → all records

    def register_component(self, component_id: str, description: str = None, version: str = None, state: ComponentState = ComponentState.UNKNOWN):
        """
        Register a component for monitoring, optionally with initial state.
        """
        self._components[component_id] = {
            "description": description,
            "version": version,
        }
        now = datetime.now(timezone.utc)
        status_record = StatusRecord(
            component_id=component_id,
            state=state,
            timestamp=now,
            metrics={},
            message=f"Registered (init, state={state.name})"
        )
        self._status[component_id] = status_record
        self._history.setdefault(component_id, []).append(status_record)

    def unregister_component(self, component_id: str):
        self._components.pop(component_id, None)
        self._status.pop(component_id, None)
        self._history.pop(component_id, None)

    def update_component_status(self, component_id: str, state: ComponentState, metrics: dict = None, message: str = None, timestamp: Optional[datetime]=None):
        now = timestamp or datetime.now(timezone.utc)
        record = StatusRecord(
            component_id=component_id,
            state=state,
            timestamp=now,
            metrics=metrics or {},
            message=message
        )
        self._status[component_id] = record
        if component_id not in self._history:
            self._history[component_id] = []
        self._history[component_id].append(record)

    def get_component_status(self, component_id: str) -> Optional[StatusRecord]:
        return self._status.get(component_id)

    def get_all_components(self) -> Dict[str, StatusRecord]:
        return {cid: sr for cid, sr in self._status.items()}

    def get_component_history(self, component_id: str) -> List[StatusRecord]:
        return self._history.get(component_id, [])
        
    def get_component(self, component_id: str) -> Any:
        """
        Protocol API: Return the component entity by ID, or None.
        """
        if component_id not in self._components:
            return None
            
        component_data = self._components[component_id]
        return ComponentEntity(
            component_id=component_id,
            description=component_data.get("description"),
            version=component_data.get("version")
        )
        
    def get_registered_component_ids(self):
        """
        Protocol API: Enumerate all registered component IDs.
        """
        return list(self._components.keys())

    def clear(self):
        self._components.clear()
        self._status.clear()
        self._history.clear()

# ---- Protocol/test compliance alias ----
ComponentRegistry = MonitoringComponentRegistry
