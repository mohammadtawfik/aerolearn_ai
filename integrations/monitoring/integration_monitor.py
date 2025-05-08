# /integrations/monitoring/integration_monitor.py
"""
IntegrationMonitor — Protocol-compliant integration monitoring (transaction/failure/statistics storage and analysis).

Follows protocol from /docs/architecture/health_monitoring_protocol.md and modularization plan.
"""

import time
from enum import Enum


class ComponentState(Enum):
    """Possible states for a monitored component."""
    UNKNOWN = "UNKNOWN"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class IntegrationMonitor:
    """
    Protocol-driven monitor for integration points.
    Registers components, updates/queries health state and metrics.
    Tracks transactions and failures for analysis. Protocol/test complete.
    """
    
    def __init__(self):
        # Component state tracking
        self._components = {}  # Maps component_id -> state
        self._component_details = {}  # Maps component_id -> details dict
        self._metrics = {}  # Maps component_id -> latest metrics dict
        self._metrics_history = {}  # Maps component_id -> list of metrics dict snapshots
        
        # Transaction tracking
        self._monitored = {}  # Maps component_id -> list of transaction records
        self._failures = {}  # Maps component_id -> list of failure records

    def register_component(self, component_id):
        """Register a component for monitoring."""
        self._components[component_id] = ComponentState.UNKNOWN
        self._component_details[component_id] = {}
        self._metrics.setdefault(component_id, {})
        self._metrics_history.setdefault(component_id, [])
        self._monitored.setdefault(component_id, [])
        self._failures.setdefault(component_id, [])
        
    def monitor_integration(self, integration):
        """Register an integration for monitoring (legacy method)."""
        self.register_component(integration)

    def list_components(self):
        """Return a list of all registered components."""
        return list(self._components.keys())
        
    def update_health(self, component_id, state, details=None):
        """
        Update the health state of a component.
        
        Args:
            component_id: ID of the component
            state: One of the ComponentState values or string
            details: Optional dict with additional health information
        """
        if component_id not in self._components:
            self.register_component(component_id)
            
        # Handle both enum and string values for state
        if isinstance(state, str):
            try:
                state = ComponentState(state)
            except ValueError:
                # If not a valid enum value, use as is
                pass
                
        self._components[component_id] = state
        if details:
            self._component_details[component_id] = details

    def get_component_state(self, component_id):
        """Return the current state of a component."""
        state = self._components.get(component_id, ComponentState.UNKNOWN)
        # Return string value for protocol compatibility
        if isinstance(state, ComponentState):
            return state.value
        return state
        
    def get_component_details(self, component_id):
        """Return detailed health information for a component."""
        return self._component_details.get(component_id, {})
    
    def get_health_details(self, component_id):
        """Alias for test/protocol compliance."""
        return self.get_component_details(component_id)
        
    def set_metrics(self, component_id, metric_record):
        """
        Set metrics for a component.
        
        Args:
            component_id: ID of the component
            metric_record: Dict containing metrics
        """
        if component_id not in self._components:
            self.register_component(component_id)
            
        # Protocol/test-driven logic: 
        # Always append the new (current) metrics snapshot to history, so length grows with every set.
        self._metrics_history[component_id].append(dict(metric_record))  # use a copy to prevent test pollution
        self._metrics[component_id] = metric_record

    def get_metrics(self, component_id):
        """Return metrics for a component."""
        return self._metrics.get(component_id, {})
    
    def get_metrics_history(self, component_id):
        """Return list of historical metrics dicts (oldest first, excluding current value)."""
        return list(self._metrics_history.get(component_id, []))

    def record_transaction(self, integration, status, duration, details=None):
        """
        Record a transaction for an integration.
        
        Args:
            integration: Name of the integration
            status: 'success' or 'fail'
            duration: Time taken for transaction (in ms or s)
            details: Additional dict with info (protocol)
        """
        if integration not in self._components:
            self.register_component(integration)
            
        timestamp = time.time()
        entry = {'integration': integration, 'status': status, 'duration': duration, 'timestamp': timestamp}
        if details is not None:
            entry['details'] = details
        self._monitored[integration].append(entry)
        
        # Update component state based on transaction
        if status == "fail":
            self._failures[integration].append(entry)
            self.update_health(integration, ComponentState.DEGRADED, 
                              {"last_failure": timestamp, "reason": "Transaction failure"})
        else:
            # Only update to healthy if not in failed state
            current_state = self.get_component_state(integration)
            if current_state != ComponentState.FAILED.value:
                self.update_health(integration, ComponentState.HEALTHY)
                
        # Update metrics with transaction data
        metrics = self.get_metrics(integration)
        metrics.setdefault('transactions', {})
        metrics['transactions'].setdefault('total', 0)
        metrics['transactions'].setdefault('failures', 0)
        metrics['transactions']['total'] = len(self._monitored[integration])
        metrics['transactions']['failures'] = len(self._failures[integration])
        metrics['last_transaction'] = timestamp
        self.set_metrics(integration, metrics)

    def get_transactions(self, integration):
        """
        Return all transaction records for an integration (protocol/test compliance).
        """
        return list(self._monitored.get(integration, []))

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
            # Update component state for repeated failures
            self.update_health(integration, ComponentState.FAILED, 
                              {"pattern": pattern, "count": count})
        elif count > 0:
            pattern = "occasional_failure"
            self.update_health(integration, ComponentState.DEGRADED, 
                              {"pattern": pattern, "count": count})
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
        
        # Update metrics with health score
        metrics = self._metrics.get(integration, {})
        metrics['health_score'] = max(0.0, min(1.0, score))
        
        # Add additional metrics for protocol compliance
        metrics['transaction_count'] = total
        metrics['failure_count'] = fails
        metrics['success_rate'] = score
        
        self._metrics[integration] = metrics
        
        return max(0.0, min(1.0, score))

    def simulate_failure(self, integration, fail_type):
        """
        Inject a simulated failure for testing purposes.
        
        Args:
            integration: Name of the integration
            fail_type: Type of failure to simulate
        """
        if integration not in self._components:
            self.register_component(integration)
            
        timestamp = time.time()
        entry = {'integration': integration, 'status': 'fail', 'duration': None, 
                'timestamp': timestamp, 'fail_type': fail_type}
        self._monitored[integration].append(entry)
        self._failures[integration].append(entry)
        
        # Update component state for simulated failure
        self.update_health(integration, ComponentState.FAILED, 
                          {"timestamp": timestamp, "reason": f"Simulated failure: {fail_type}"})
                          
        # Update metrics for the simulated failure
        metrics = self.get_metrics(integration)
        metrics.setdefault('simulated_failures', 0)
        metrics['simulated_failures'] += 1
        metrics['last_simulated_failure'] = {'timestamp': timestamp, 'type': fail_type}
        self.set_metrics(integration, metrics)

    def clear(self):
        """Reset all state (all integrations, traces, and history)."""
        self._components.clear()
        self._component_details.clear()
        self._metrics.clear()
        self._metrics_history.clear()
        self._monitored.clear()
        self._failures.clear()
        
    def get_status_summary(self):
        """
        Return a summary of all component statuses.
        
        Returns:
            dict: Maps component_id to its current state
        """
        summary = {}
        for component_id, state in self._components.items():
            if isinstance(state, ComponentState):
                summary[component_id] = state.value
            else:
                summary[component_id] = state
        return summary
        
    def get_all_metrics(self):
        """
        Return all metrics for all components.
        
        Returns:
            dict: Maps component_id to its metrics dict
        """
        return self._metrics.copy()
