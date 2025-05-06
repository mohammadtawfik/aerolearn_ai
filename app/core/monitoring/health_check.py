from threading import Lock
from typing import Dict, List, Optional
from enum import Enum, auto
from collections import defaultdict, deque
import time

# -- Protocol-Compliant Status Enum (can be imported if defined elsewhere) --
class HealthStatus(Enum):
    OK = auto()
    DEGRADED = auto()
    FAILED = auto()

# -- Registry and Dependency Graph for Health Aggregation --
class Component:
    def __init__(self, name):
        self.name = name
        self.status = HealthStatus.OK
        self.last_updated = time.time()
        self.status_history = deque(maxlen=100)
        self.status_history.append({"timestamp": self.last_updated, "status": self.status})

class HealthCheckAPI:
    def __init__(self):
        self._components: Dict[str, Component] = dict()
        self._dependencies: Dict[str, List[str]] = defaultdict(list)  # component -> dependency names
        self._lock = Lock()

    def register_component(self, name: str):
        with self._lock:
            if name not in self._components:
                self._components[name] = Component(name)
            # else: ignore, already present

    def declare_dependency(self, component: str, depends_on: str):
        with self._lock:
            # Ensure both components exist
            if component not in self._components:
                self._components[component] = Component(component)
            if depends_on not in self._components:
                self._components[depends_on] = Component(depends_on)
            # Add dependency (no duplicate)
            if depends_on not in self._dependencies[component]:
                self._dependencies[component].append(depends_on)

    def set_component_health(self, name: str, status: str):
        """Status must be 'OK', 'DEGRADED', or 'FAILED' per protocol."""
        status_enum = HealthStatus[status]
        with self._lock:
            c = self._components.get(name)
            now = time.time()
            if c:
                c.status = status_enum
                c.last_updated = now
                c.status_history.append({"timestamp": now, "status": c.status})
            else:
                self._components[name] = Component(name)
                self._components[name].status = status_enum
                self._components[name].last_updated = now
                self._components[name].status_history.append({"timestamp": now, "status": status_enum})

    def _propagate_status(self) -> Dict[str, HealthStatus]:
        # Build actual, dependency-aware status tree.
        with self._lock:
            propagation = {}
            visit_order = list(self._components.keys())
            # First, assign direct component states.
            for name, comp in self._components.items():
                propagation[name] = comp.status
            # Then propagate: any dependency with lower status must move parent down
            # (FAILED > DEGRADED > OK)
            for name in visit_order:
                deps = self._dependencies.get(name, [])
                for dep in deps:
                    if propagation[dep].value > propagation[name].value:
                        propagation[name] = propagation[dep]
            return propagation

    def get_system_health(self) -> Dict:
        """Protocol endpoint: return overall system health, components, and status."""
        with self._lock:
            propagation = self._propagate_status()
            system_status = HealthStatus.OK
            for status in propagation.values():
                if status == HealthStatus.FAILED:
                    system_status = HealthStatus.FAILED
                    break
                elif status == HealthStatus.DEGRADED and system_status == HealthStatus.OK:
                    system_status = HealthStatus.DEGRADED
            return {
                "status": system_status.name,
                "components": {name: s.name for name, s in propagation.items()}
            }

    def get_health_dashboard(self) -> Dict:
        """Return structured dashboard data: status overview, component tree, history."""
        with self._lock:
            propagation = self._propagate_status()
            status_overview = {name: s.name for name, s in propagation.items()}
            component_tree = {}
            # For tree: child -> [dependencies]
            for name in self._components.keys():
                component_tree[name] = list(self._dependencies.get(name, []))
            status_history = {
                name: list(self._components[name].status_history)
                for name in self._components.keys()
            }
            return {
                "status_overview": status_overview,
                "component_tree": component_tree,
                "status_history": status_history,
            }

    def clear(self):
        """Reset for test or redeployment."""
        with self._lock:
            self._components.clear()
            self._dependencies.clear()