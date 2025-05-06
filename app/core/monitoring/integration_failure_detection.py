import time
from threading import Lock
from typing import List, Dict, Any, Optional
from collections import defaultdict, deque

class IntegrationMonitor:
    def __init__(self):
        # Per integration: each keeps a list of transaction records, a list of failure types, and a circular failure window
        self._records: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._failures: Dict[str, List[str]] = defaultdict(list)
        self._lock = Lock()

    def monitor_integration(self, integration):
        """Register or reset tracking for the named integration."""
        name = integration.name if hasattr(integration, "name") else str(integration)
        with self._lock:
            if name not in self._records:
                self._records[name] = []
                self._failures[name] = []

    def record_transaction(self, integration, status: str, duration: int):
        """Record a transaction, success or fail, with timestamp."""
        name = integration if isinstance(integration, str) else getattr(integration, "name", str(integration))
        status_normalized = status.lower()
        record = {
            "integration": name,
            "status": "success" if status_normalized == "success" else "fail",
            "duration": duration,
            "timestamp": time.time()
        }
        with self._lock:
            self._records[name].append(record)

    def get_failure_trace(self, integration) -> List[Dict[str, Any]]:
        """Return list of all trace records; if fail_type is present, included."""
        name = integration if isinstance(integration, str) else getattr(integration, "name", str(integration))
        with self._lock:
            # Protocol: Only allowed fields ("integration", "status", "duration", "timestamp", "fail_type" if present)
            records = []
            for rec in self._records.get(name, []):
                proto_rec = {k: v for k, v in rec.items() if k in {"integration", "status", "duration", "timestamp", "fail_type"}}
                records.append(proto_rec)
            # Add simulated failures (with fail_type) if any have occurred
            for fail_type in self._failures.get(name, []):
                records.append({
                    "integration": name,
                    "status": "fail",
                    "duration": None,
                    "timestamp": time.time(),
                    "fail_type": fail_type
                })
            return records

    def detect_failure_patterns(self, integration) -> Dict[str, Any]:
        """Detect simple repeated/burst failure patterns per protocol."""
        name = integration if isinstance(integration, str) else getattr(integration, "name", str(integration))
        with self._lock:
            recs = self._records.get(name, [])
            consecutive_fails = 0
            for r in recs[-10:]:  # recent window
                if r["status"] == "fail":
                    consecutive_fails += 1
            pattern = None
            count = sum(1 for r in recs if r["status"] == "fail")
            if consecutive_fails >= 3:
                pattern = "repeated_failure"
            elif count > 0:
                pattern = "occasional_failure"
            return {"pattern": pattern, "count": count}

    def get_health_score(self, integration) -> float:
        """Return m/n: successful transaction ratio (protocol: score between 0-1)."""
        name = integration if isinstance(integration, str) else getattr(integration, "name", str(integration))
        with self._lock:
            recs = self._records.get(name, [])
            if not recs:
                return 1.0  # If nothing monitored yet, default to healthy
            total = len(recs)
            successes = sum(1 for r in recs if r["status"] == "success")
            return successes / total if total > 0 else 0.0

    def simulate_failure(self, integration, fail_type: str):
        """Simulate a type of failure—inject as special trace with fail_type."""
        name = integration if isinstance(integration, str) else getattr(integration, "name", str(integration))
        with self._lock:
            # Keep protocol hygiene: fail_type only included on simulated records
            self._failures[name].append(fail_type)

    def clear(self):
        with self._lock:
            self._records.clear()
            self._failures.clear()