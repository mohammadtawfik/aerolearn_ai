"""
Stub implementation for Integration Status Monitoring.
Location: /app/core/monitoring/integration_monitor.py

Implements protocol-driven interfaces per plan and test requirements.
Fulfills requirements of:
    - /docs/development/day19_plan.md (Task 3.6.3)
    - /docs/architecture/service_health_protocol.md
    - /docs/architecture/health_monitoring_protocol.md
    - /docs/architecture/architecture_overview.md
    - /code_summary.md (module structure)
**Only class signatures & method stubs; add logic according to TDD process.**
"""

from typing import Any, Dict, List, Callable, Optional
from datetime import datetime

class IntegrationHealthEvent:
    def __init__(self, integration_point: str, status: str, timestamp: Optional[datetime] = None, error_msg: Optional[str] = None):
        self.integration_point = integration_point
        self.status = status
        self.timestamp = timestamp or datetime.utcnow()
        self.error_msg = error_msg

class IntegrationPointRegistry:
    def __init__(self):
        self._points: Dict[str, Dict[str, Any]] = {}
        
    def register_integration_point(self, name: str, description: Optional[str] = None, version: Optional[str] = None) -> None:
        """Register a new integration point."""
        self._points[name] = {
            'description': description,
            'version': version
        }

    def get_all_points(self) -> List[str]:
        """Return a list of all registered integration point names."""
        return list(self._points.keys())

class IntegrationMonitor:
    """
    Implements service/integration health monitoring, transaction audit/history,
    and alerting, as defined in the protocol docs.
    """
    def __init__(self):
        # Store transactions per integration point
        self._transactions: Dict[str, List[Dict[str, Any]]] = {}
        self._failures: Dict[str, List[Dict[str, Any]]] = {}
        self._events: Dict[str, List[IntegrationHealthEvent]] = {}
        
        # State for alert deduplication and alert callbacks registry
        self._last_state: Dict[str, str] = {}  # "RUNNING", "FAILED", "DEGRADED"
        self._alert_callbacks: List[Callable[[str, str, Optional[str]], None]] = []

    def log_transaction(self, point_name: str, success: bool, duration_ms: int, meta: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a transaction (protocol: history, state, alert, callback).
        Fires alert(s) on relevant state transitions only.
        """
        tx = {
            "success": success,
            "duration_ms": duration_ms,
            "meta": meta or {},
            "timestamp": datetime.utcnow(),
        }
        
        # Add error_msg (if any, on failure) at root for diagnostic protocols
        error_msg = None
        if not success and meta is not None and "error_msg" in meta:
            tx["error_msg"] = meta["error_msg"]
            error_msg = meta["error_msg"]
            
        # Record transaction
        if point_name not in self._transactions:
            self._transactions[point_name] = []
        self._transactions[point_name].append(tx)
        
        # Failure tracking
        if not success:
            if point_name not in self._failures:
                self._failures[point_name] = []
            self._failures[point_name].append(tx)
        
        # Health events tracking (for completeness/test access)
        evt = IntegrationHealthEvent(
            integration_point=point_name,
            status="FAILED" if not success else "RUNNING",
            error_msg=error_msg
        )
        if point_name not in self._events:
            self._events[point_name] = []
        self._events[point_name].append(evt)
        
        # State/alert protocol
        previous_state = self._last_state.get(point_name, "RUNNING")
        new_state = "FAILED" if not success else "RUNNING"
        if not success:
            # Only fire alert if previous state was not FAILED or DEGRADED (protocol: no duplicate alerts)
            if previous_state not in ("FAILED", "DEGRADED"):
                for callback in self._alert_callbacks:
                    # Protocol signature: (component_id, state, error_msg)
                    callback(point_name, "FAILED", error_msg)
        else:
            # If returning from a failed state, can use for "recovery" logic if needed
            pass
        self._last_state[point_name] = new_state

    def get_transaction(self, point_name: str) -> List[Dict[str, Any]]:
        """
        Return transaction list for a given integration point.
        """
        return self._transactions.get(point_name, [])

    def get_recent_failures(self, point_name: str) -> List[Dict[str, Any]]:
        """
        Return recent failed transaction records for a point.
        """
        return self._failures.get(point_name, [])

    def get_health_events(self, point_name: str) -> List[IntegrationHealthEvent]:
        """
        Access list of health events for a point.
        """
        return self._events.get(point_name, [])

    def get_performance_summary(self, point_name: str) -> Dict[str, Any]:
        """Return summary statistics (min, max, mean durations, etc.) for an integration point."""
        txs = self._transactions.get(point_name, [])
        durations = [tx["duration_ms"] for tx in txs if isinstance(tx.get("duration_ms"), (int, float))]
        
        if not durations:
            return {}
            
        min_dur = min(durations)
        max_dur = max(durations)
        mean_dur = sum(durations) / len(durations)
        
        return {
            "min_duration_ms": min_dur,
            "max_duration_ms": max_dur,
            "mean_duration_ms": mean_dur,
            "transaction_count": len(durations)
        }

    def get_transaction_history(self, point_name: str, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Returns all (optionally filtered) transaction records by protocol/test.
        All fields preserved so meta["ts"] etc are accessible.
        """
        records = self._transactions.get(point_name, [])
        if since is not None:
            # Return only transactions after the 'since' datetime
            return [tx for tx in records if tx.get("meta", {}).get("ts") and tx["meta"]["ts"] >= since or tx["timestamp"] >= since]
        return records

    def register_alert_callback(self, callback: Callable[[str, str, Optional[str]], None]) -> None:
        """
        Register an alert callback (protocol: component_id, state, error_msg)
        """
        if callback not in self._alert_callbacks:
            self._alert_callbacks.append(callback)
