# health_status.py
# Location: /integrations/monitoring/health_status.py
# Purpose: Protocol-conformant implementation of HealthStatus, HealthMetric, HealthMetricType, etc.

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime, timezone



class HealthStatus(Enum):
    """
    Protocol-compliant health status enum representing component states.
    """
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    RUNNING = "RUNNING"
    DOWN = "DOWN"

    def __str__(self):
        return self.value

class HealthMetricType(Enum):
    """
    Protocol-compliant metric types for health monitoring.
    """
    UPTIME = "UPTIME"
    RESPONSE_TIME = "RESPONSE_TIME"
    LATENCY = "LATENCY"
    THROUGHPUT = "THROUGHPUT"
    ERROR_RATE = "ERROR_RATE"
    CPU_USAGE = "CPU_USAGE"
    MEMORY_USAGE = "MEMORY_USAGE"
    CUSTOM = "CUSTOM"

    def __str__(self):
        return self.value

@dataclass
class HealthMetric:
    """
    Protocol-compliant health metric representation.
    Represents a single health metric (e.g., CPU_USAGE, MEMORY_USAGE, ERROR_RATE, etc.)
    """
    type: HealthMetricType
    value: float
    name: str = None
    unit: str = None
    timestamp: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Auto TZ-aware UTC timestamp if none supplied
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def __str__(self):
        attrs = [f"type={self.type}", f"value={self.value}"]
        if self.name:
            attrs.append(f"name={self.name}")
        if self.unit:
            attrs.append(f"unit={self.unit}")
        if self.timestamp:
            attrs.append(f"timestamp={self.timestamp}")
        return f"HealthMetric(" + ", ".join(attrs) + ")"

@dataclass
class StatusRecord:
    """
    Protocol model for a status record, per service_health_protocol.md
    """
    component_id: str
    state: HealthStatus
    timestamp: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)
    message: Optional[str] = None
