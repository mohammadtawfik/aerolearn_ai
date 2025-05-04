# File: /integrations/registry/component_state.py

from enum import Enum

class ComponentState(Enum):
    
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
            
    """Enum for component lifecycle states, protocol/test-compliant."""
    RUNNING = "running"
    HEALTHY = "healthy"   # Protocol: synonym for RUNNING
    DOWN = "down"
    PAUSED = "paused"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    ERROR = "error"       # Legacy; protocol now expects FAILED for alerting
    FAILED = "failed"     # Protocol/test required; use for irrecoverable error
