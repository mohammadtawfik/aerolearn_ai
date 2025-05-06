import time
from typing import Callable, List, Dict, Any, Optional
from enum import Enum, auto
from threading import Lock

# --- Protocol-compliant AlertLevel Enum ---
class AlertLevel(Enum):
    INFO = auto()
    WARNING = auto()
    CRITICAL = auto()

# --- AlertRule: Holds a matching condition (predicate) for alerts ---
class AlertRule:
    def __init__(self, condition: Callable[[Dict[str, Any]], bool]):
        self.condition = condition

# --- AlertNotification: Rule Engine, Routing, Escalation, History ---
class AlertNotification:
    def __init__(self):
        self._rules: List[tuple[AlertRule, Callable[[Dict], None]]] = []
        self._history: List[Dict[str, Any]] = []
        self._lock = Lock()
        # Escalation state for repeated triggering (component/category -> [timestamps])
        self._escalation_counter: Dict[str, List[float]] = {}

    def register_rule(self, rule: AlertRule, callback: Callable[[Dict], None]):
        """Register a routing rule and callback for protocol-compliant alerts."""
        with self._lock:
            self._rules.append((rule, callback))

    def trigger_alert(self, component, message: str, severity: str, category: str):
        """Primary protocol API to trigger and route a new alert event."""
        # Ensure field names and only protocol-allowed types
        alert = {
            "component": component.name if hasattr(component, "name") else str(component),
            "message": message,
            "severity": severity,
            "category": category,
            "timestamp": time.time()
        }
        with self._lock:
            self._history.append(alert)
            for rule, callback in self._rules:
                if rule.condition(alert):
                    callback(alert)
            # Track for escalation
            key = f"{alert['component']}::{category}"
            self._escalation_counter.setdefault(key, []).append(alert["timestamp"])

    def escalate_alert(self, component_name: str):
        """Escalate alerts for a given component/category by protocol workflow."""
        # Protocol: On repeated warnings, escalate to CRITICAL (if such escalation is required by protocol/spec)
        with self._lock:
            now = time.time()
            keys = [k for k in self._escalation_counter.keys() if k.startswith(f"{component_name}::")]
            for key in keys:
                recent_times = [t for t in self._escalation_counter[key] if now - t < 300]  # 5-min window (example)
                if len(recent_times) >= 3:
                    # Escalate: add CRITICAL alert for component/category
                    _component, category = key.split("::", 1)
                    self.trigger_alert(component_name, f"Escalated alert: {category}", severity="CRITICAL", category=category)
                    # Clear escalation state for this key to avoid continuous re-trigger
                    self._escalation_counter[key] = []
                else:
                    self._escalation_counter[key] = recent_times

    def query_alert_history(self) -> List[Dict[str, Any]]:
        """Protocol API: Retrieve alert history; only protocol fields are returned."""
        with self._lock:
            return [dict(alert) for alert in self._history]

    def clear(self):
        """Clear all alert rules/history (test, admin, or redeploy only)."""
        with self._lock:
            self._rules.clear()
            self._history.clear()
            self._escalation_counter.clear()