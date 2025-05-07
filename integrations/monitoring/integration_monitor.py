# /integrations/monitoring/integration_monitor.py
"""
IntegrationMonitor — Protocol-compliant integration monitoring (transaction/failure/statistics storage and analysis).

Follows protocol from /docs/architecture/health_monitoring_protocol.md and modularization plan.
"""

import time


class IntegrationMonitor:
    """Monitor integration health, transactions, and failures."""
    
    def __init__(self):
        # Key: integration name, Value: list of transaction dicts
        self._monitored = {}
        self._failures = {}

    def monitor_integration(self, integration):
        """Register an integration for monitoring."""
        self._monitored.setdefault(integration, [])
        self._failures.setdefault(integration, [])

    def record_transaction(self, integration, status, duration):
        """
        Record a transaction for an integration.
        
        Args:
            integration: Name of the integration
            status: 'success' or 'fail'
            duration: Time taken for transaction (in ms or s)
        """
        timestamp = time.time()
        entry = {'integration': integration, 'status': status, 'duration': duration, 'timestamp': timestamp}
        self._monitored.setdefault(integration, []).append(entry)
        if status == "fail":
            self._failures.setdefault(integration, []).append(entry)

    def get_failure_trace(self, integration):
        """Return all failed transaction records for an integration."""
        return list(self._failures.get(integration, []))

    def detect_failure_patterns(self, integration):
        """
        Analyze failure patterns for an integration.
        
        Returns:
            dict: Contains 'pattern' (None, 'occasional_failure', or 'repeated_failure')
                 and 'count' of failures
        """
        fails = self._failures.get(integration, [])
        count = len(fails)
        if count >= 3:
            pattern = "repeated_failure"
        elif count > 0:
            pattern = "occasional_failure"
        else:
            pattern = None
        return {"pattern": pattern, "count": count}

    def get_health_score(self, integration):
        """
        Return ratio of successful transactions to total (0..1, or 1 if none recorded).
        
        A score of 1.0 means perfect health, 0.0 means complete failure.
        """
        records = self._monitored.get(integration, [])
        if not records:
            return 1.0
        total = len(records)
        fails = sum(1 for r in records if r['status'] == 'fail')
        score = (total - fails) / total
        return max(0.0, min(1.0, score))

    def simulate_failure(self, integration, fail_type):
        """
        Inject a simulated failure for testing purposes.
        
        Args:
            integration: Name of the integration
            fail_type: Type of failure to simulate
        """
        timestamp = time.time()
        entry = {'integration': integration, 'status': 'fail', 'duration': None, 
                'timestamp': timestamp, 'fail_type': fail_type}
        self._monitored.setdefault(integration, []).append(entry)
        self._failures.setdefault(integration, []).append(entry)

    def clear(self):
        """Reset all state (all integrations, traces, and history)."""
        self._monitored.clear()
        self._failures.clear()
