# File: /integrations/registry/component_state.py

from enum import Enum

class ComponentState(Enum):
    """Enum for component lifecycle states."""
    RUNNING = "running"
    DOWN = "down"
    PAUSED = "paused"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    ERROR = "error"
