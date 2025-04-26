# component_base.py

from typing import Any, Callable, Dict
import threading

# For event integration, import the event bus (assume already implemented in integrations.events.event_bus)
try:
    from integrations.events.event_bus import EventBus
    _HAS_EVENTBUS = True
except ImportError:
    EventBus = None  # Allows testing in isolation
    _HAS_EVENTBUS = False

class BaseComponent:
    """
    Base class for all UI components.

    Lifecycle: init -> start -> stop
    Supports event bus integration and dependency injection.
    """

    _version: str = '1.0.0'

    def __init__(self, name: str = None, **dependencies):
        self.name = name or self.__class__.__name__
        self._dependencies = dependencies
        self._status = "initialized"
        # Only try to use EventBus.instance() if EventBus exists and has method 'instance'
        if "event_bus" in dependencies:
            self._event_bus = dependencies["event_bus"]
        elif _HAS_EVENTBUS and hasattr(EventBus, "instance"):
            self._event_bus = EventBus.instance()
        else:
            self._event_bus = None
        self._lock = threading.RLock()
        self._event_handlers: Dict[str, Callable] = {}

        self.on_init()

    @property
    def version(self):
        return self._version

    @property
    def status(self):
        return self._status

    def on_init(self):
        """Initialize component resources."""
        pass

    def on_start(self):
        """Hook for when the component starts."""
        self._status = "started"

    def on_stop(self):
        """Hook for when the component stops."""
        self._status = "stopped"

    def register_event_handler(self, event_type: str, handler: Callable):
        """Registers an event handler for a specific event type."""
        self._event_handlers[event_type] = handler
        if self._event_bus:
            self._event_bus.subscribe(event_type, self.event_callback)

    def event_callback(self, event):
        """Generic handler, routes to specific handlers."""
        handler = self._event_handlers.get(event.type)
        if handler:
            handler(event)

    def publish_event(self, event_type: str, data: Any):
        """Publishes an event to the bus."""
        if self._event_bus:
            self._event_bus.publish(event_type, data)

    def get_dependency(self, name: str):
        """Returns a dependency (for dependency injection)."""
        return self._dependencies.get(name)

    def replace_dependency(self, name: str, new_value: Any):
        """Allows for dynamic dependency injection / replacement."""
        self._dependencies[name] = new_value

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} status={self._status} version={self.version}>"
