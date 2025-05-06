from enum import Enum, auto
from typing import Callable, List, Dict, Any, Optional
from dataclasses import dataclass, field
from threading import Lock

# --- Protocol-compliant Severity Enum ---
class ErrorSeverity(Enum):
    CRITICAL = auto()
    WARNING = auto()
    INFO = auto()
    DEBUG = auto()

# --- Structured Error Log Entry ---
@dataclass
class ErrorEntry:
    component: str
    message: str
    severity: ErrorSeverity
    category: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

# --- Error Logger: protocol-compliant, central, extendable ---
class ErrorLogger:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_internal()
            return cls._instance

    def _init_internal(self):
        # Internal log storage
        self._logs: List[ErrorEntry] = []
        # Registered notification rules
        self._notification_rules: List[tuple[Callable[[ErrorEntry], bool], Callable[[ErrorEntry], None]]] = []
        self._notification_lock = Lock()

    def log_error(self, component, message: str, severity: ErrorSeverity, category: str, metadata: dict = None):
        """Log a structured error entry.

        Parameters:
            component (str|object): identifier or object representing component (must support .name or .__str__())
            message (str): error message text
            severity (ErrorSeverity): error severity
            category (str): functional or technical category (e.g. 'db', 'io', 'auth')
            metadata (dict, optional): extra fields for debugging, traces, etc.
        """
        component_name = component if isinstance(component, str) else getattr(component, 'name', str(component))
        entry = ErrorEntry(
            component=component_name,
            message=message,
            severity=severity,
            category=category,
            metadata=metadata or {},
        )
        # Add to central collection
        with self._lock:
            self._logs.append(entry)

        # Check and fire notifications
        with self._notification_lock:
            for rule, callback in self._notification_rules:
                if rule(entry):
                    callback(entry)

    def query_errors(
        self, 
        component: Optional[str] = None, 
        severity: Optional[ErrorSeverity] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """Query log history; filterable by component, severity, category."""
        with self._lock:
            filtered = [
                entry for entry in self._logs
                if (component is None or entry.component == component)
                and (severity is None or entry.severity == severity)
                and (category is None or entry.category == category)
            ]
            if limit is not None:
                filtered = filtered[-limit:]
            # Return as dicts for easier test/assert (and possible API serialization)
            return [
                {
                    "component": e.component,
                    "message": e.message,
                    "severity": e.severity,
                    "category": e.category,
                    "metadata": e.metadata,
                }
                for e in filtered
            ]

    def aggregate_errors(self) -> Dict[str, Any]:
        """Aggregate error information for diagnostics and protocol reporting."""
        with self._lock:
            count_by_severity = {}
            for e in self._logs:
                key = str(e.severity)
                count_by_severity[key] = count_by_severity.get(key, 0) + 1
            return {
                "count": len(self._logs),
                "by_severity": count_by_severity,
            }

    def register_notification_rule(self, rule: Callable[[Dict], bool], callback: Callable[[Dict], None]):
        """Register a notification rule.
        - rule: function accepting an error dict, returning True if callback should fire.
        - callback: function accepting error dict.
        Protocol: callbacks fire synchronously every time a matching error is logged.
        """
        def wrapped_rule(entry: ErrorEntry):
            # Convert entry to dict for rule/callback for consistency with the protocol/test shape
            return rule({
                "component": entry.component,
                "message": entry.message,
                "severity": entry.severity,
                "category": entry.category,
                "metadata": entry.metadata,
            })
        def wrapped_callback(entry: ErrorEntry):
            return callback({
                "component": entry.component,
                "message": entry.message,
                "severity": entry.severity,
                "category": entry.category,
                "metadata": entry.metadata,
            })
        with self._notification_lock:
            self._notification_rules.append((wrapped_rule, wrapped_callback))

    def clear(self):
        """For test cleanup: clear all logs and notification rules."""
        with self._lock:
            self._logs.clear()
        with self._notification_lock:
            self._notification_rules.clear()

# Export singleton per central logger requirement, protocol-compliant:
error_logger = ErrorLogger()