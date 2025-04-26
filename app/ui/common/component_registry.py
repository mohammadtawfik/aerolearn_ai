from typing import Any, Dict, List, Optional, Type
import threading

from app.ui.common.component_base import BaseComponent

class ComponentRegistry:
    """
    Registry for UI components (Singleton).
    Supports registration, discovery, replacement, and lifecycle management.
    """

    _instance = None
    _lock = threading.RLock()

    def __init__(self):
        self._components: Dict[str, BaseComponent] = {}
        self._component_classes: Dict[str, Type[BaseComponent]] = {}

    @classmethod
    def instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def register_component(self, name: str, component: BaseComponent):
        with self._lock:
            self._components[name] = component

    def register_component_class(self, name: str, component_cls: Type[BaseComponent]):
        with self._lock:
            self._component_classes[name] = component_cls

    def get_component(self, name: str) -> Optional[BaseComponent]:
        return self._components.get(name)

    def discover_components(self) -> List[str]:
        return list(self._components.keys())

    def replace_component(self, name: str, new_component: BaseComponent):
        with self._lock:
            if name in self._components:
                self._components[name].on_stop()
            self._components[name] = new_component
            new_component.on_start()

    def start_all(self):
        for component in self._components.values():
            component.on_start()

    def stop_all(self):
        for component in self._components.values():
            component.on_stop()

    def inject_dependency(self, component_name: str, dependency_name: str, dependency: Any):
        comp = self.get_component(component_name)
        if comp:
            comp.replace_dependency(dependency_name, dependency)