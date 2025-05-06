"""
Unit Tests for ServiceHealthDashboard (AeroLearn AI)
Location: /tests/unit/core/monitoring/test_service_health_dashboard.py

Protocol coverage:
- /docs/architecture/service_health_protocol.md
- /docs/architecture/health_monitoring_protocol.md

State isolation fix:
- Ensures every test runs in a pristine environment with a clean registry
- Complies with protocol: 'All components implementing this protocol must include: Unit tests verifying state transitions...Mock implementations for testing dependent systems'
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Import canonical dashboard (per docs)
from app.core.monitoring.ServiceHealthDashboard_Class import ServiceHealthDashboard, ComponentState, StatusRecord

# Protocol-advised reset: use clear_all_status_tracking (preferred if available)
try:
    from integrations.monitoring.component_status_adapter import clear_all_status_tracking
    CLEAR_STATUS_TRACKING = True
except ImportError:
    CLEAR_STATUS_TRACKING = False

class TestServiceHealthDashboardProtocol(unittest.TestCase):

    def setUp(self):
        # Always start with a pristine dashboard/registry
        if CLEAR_STATUS_TRACKING:
            clear_all_status_tracking()
        self.dashboard = ServiceHealthDashboard()
        # Defensive sweep: Unregister any leftover test components
        # Try both protocol reset (above) and hard-clear (below)
        if hasattr(self.dashboard, 'registry'):
            # Some implementations: .components dict, others: .get_all_components
            reg = self.dashboard.registry
            if hasattr(reg, 'get_all_components'):
                all_comps = reg.get_all_components()
                for comp_id in list(all_comps.keys()):
                    reg.unregister_component(comp_id)
            elif hasattr(reg, 'components'):
                for comp_id in list(reg.components.keys()):
                    reg.unregister_component(comp_id)
        self.component_id = "test.component"
        self.component_desc = "Test Component"
        self.version = "1.0.0"

    def test_register_component(self):
        """Component can be registered with id/desc/version/state (protocol compliance)"""
        result = self.dashboard.registry.register_component(
            self.component_id,
            description=self.component_desc,
            version=self.version,
            state=ComponentState.UNKNOWN,
        )
        self.assertEqual(result.component_id, self.component_id)
        self.assertEqual(result.state, ComponentState.UNKNOWN)
        self.assertEqual(result.version, self.version)
        self.assertEqual(result.description, self.component_desc)

    def test_state_transitions(self):
        """Component state transitions propagate and are retrievable via dashboard"""
        self.dashboard.registry.register_component(self.component_id, state=ComponentState.UNKNOWN)
        for next_state in [
            ComponentState.RUNNING,
            ComponentState.DEGRADED,
            ComponentState.DOWN,
            ComponentState.FAILED,
            ComponentState.HEALTHY,
        ]:
            with self.subTest(next_state=next_state):
                ok = self.dashboard.update_component_status(self.component_id, next_state)
                self.assertTrue(ok)
                status = self.dashboard.status_for(self.component_id)
                self.assertEqual(status, next_state)
    
    def test_status_change_alert_callback(self):
        """Register alert callback; must fire exactly on DEGRADE/FAIL transitions, not repeat"""
        self.dashboard.registry.register_component(self.component_id, state=ComponentState.RUNNING)
        alert_cb = MagicMock()
        # Per health_monitoring_protocol.md - use register_alert_callback
        self.dashboard.register_alert_callback(alert_cb)
        # Only DEGRADE/FAILED should trigger alert (and only on new transitions)
        transition_pattern = [
            (ComponentState.RUNNING, False),
            (ComponentState.DEGRADED, True),  # triggers alert
            (ComponentState.DEGRADED, False), # no repeat for same state
            (ComponentState.HEALTHY, False),  # returns to healthy
            (ComponentState.DEGRADED, True),  # triggers again on new degrade
            (ComponentState.FAILED, True),    # triggers on failure
            (ComponentState.FAILED, False),   # no repeat
        ]
        for state, should_alert in transition_pattern:
            self.dashboard.update_component_status(self.component_id, state)
            if should_alert:
                alert_cb.assert_called_with(self.component_id, state)
                alert_cb.reset_mock()
            else:
                alert_cb.assert_not_called()

    def test_status_history_audit(self):
        """All state transitions are timestamped and recorded for audit/history query"""
        self.dashboard.registry.register_component(self.component_id, state=ComponentState.RUNNING)
        now = datetime.utcnow()
        states = [ComponentState.RUNNING, ComponentState.DEGRADED, ComponentState.HEALTHY]
        for s in states:
            self.dashboard.update_component_status(self.component_id, s)
        history = self.dashboard.get_component_history(self.component_id)
        # Should have at least as many records as transitions, all correct order, timestamps present
        self.assertTrue(len(history) >= len(states))
        for record, expect_state in zip(history[-len(states):], states):
            self.assertEqual(record.state, expect_state)
            self.assertIsInstance(record.timestamp, datetime)

    def test_status_query_and_all_statuses(self):
        """Test dashboard.status_for and dashboard.get_all_component_statuses APIs"""
        comp2 = "component.second"
        self.dashboard.registry.register_component(self.component_id, state=ComponentState.RUNNING)
        self.dashboard.registry.register_component(comp2, state=ComponentState.DEGRADED)
        statuses = self.dashboard.get_all_component_statuses()
        self.assertIsInstance(statuses, dict)
        self.assertEqual(statuses[self.component_id], ComponentState.RUNNING)
        self.assertEqual(statuses[comp2], ComponentState.DEGRADED)

    def test_dependency_declaration_and_graph(self):
        """Test declare_dependency, get_dependency_graph APIs (see dependency_tracking_protocol.md)"""
        db_id, api_id = "core.db", "core.api"
        self.dashboard.registry.register_component(db_id, state=ComponentState.RUNNING)
        self.dashboard.registry.register_component(api_id, state=ComponentState.RUNNING)
        # Declare dependency: API depends on DB
        ok = self.dashboard.registry.declare_dependency(api_id, db_id)
        self.assertTrue(ok)
        dep_graph = self.dashboard.registry.get_dependency_graph()
        self.assertIn(api_id, dep_graph)
        self.assertIn(db_id, dep_graph[api_id])

    def test_unregister_component_cleanup(self):
        """Unregister component removes from dashboard/status APIs"""
        self.dashboard.registry.register_component(self.component_id, state=ComponentState.RUNNING)
        self.dashboard.registry.unregister_component(self.component_id)
        self.assertNotIn(self.component_id, self.dashboard.get_all_component_statuses())

if __name__ == "__main__":
    unittest.main()
