# File: /integrations/registry/component_state.py
"""
Defines ComponentState enum in a location all modules can import without circularity.
Protocol-compliant implementation of component lifecycle states.
"""

from enum import Enum

class ComponentState(Enum):
    """Enum for component lifecycle states, protocol/test-compliant."""
    UNKNOWN = "UNKNOWN"
    RUNNING = "RUNNING"
    HEALTHY = "RUNNING"   # Protocol: synonym for RUNNING
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"
    PAUSED = "PAUSED"
    FAILED = "FAILED"     # Protocol/test required; use for irrecoverable error
    ERROR = "FAILED"       # Legacy; protocol now expects FAILED for alerting

    @classmethod
    def from_any(cls, value):
        """Best-effort conversion or fallback to UNKNOWN"""
        try:
            return cls(value)
        except ValueError:
            if isinstance(value, str):
                v = value.lower()
                if v in ("run", "running", "healthy"):
                    return cls.RUNNING
                if v in ("fail", "failed", "error"):
                    return cls.FAILED
                if v in ("degraded",):
                    return cls.DEGRADED
                if v in ("pause", "paused"):
                    return cls.PAUSED
                if v in ("down",):
                    return cls.DOWN
                if v in ("unknown",):
                    return cls.UNKNOWN
            return cls.UNKNOWN
