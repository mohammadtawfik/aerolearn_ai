# Integration Test Patterns – AeroLearn AI

## Overview
This document outlines patterns, strategies, and protocol-compliant expectations for writing and maintaining integration tests across ServiceHealthDashboard, ComponentRegistry, ComponentStatusAdapter, and related modules.

---

## Key Patterns

### 1. Always Use Protocol-Compliant Providers
- **All test/mocked components must be wrapped in `SimpleComponentStatusProvider`**—never register a bare object.
- Adapters/trackers expect providers to implement `provide_status()`.

### 2. Explicit State Transition Testing
- Always trigger status updates with explicit state arguments when asserting on historical changes.
- Sequence: Change `.state` on the underlying component > call `update_component_status(name, state)`.

### 3. Callback/Event Testing
- Register status listeners with the expected signature: `(component_id, state, details)`.
- Assert callbacks are invoked in all supported state transitions (RUNNING, DEGRADED, DOWN, FAILED).

### 4. Transaction Integrity and Clean Slate
- Use the `.clear()` method on dashboards, adapters, and registries between test runs to ensure test isolation.
- Validate that clearing resets both live and historical state.

---

## Sample Pattern

```python
from integrations.monitoring.component_status_adapter import SimpleComponentStatusProvider

# Register a test component
component = TestComponent("Example")
provider = SimpleComponentStatusProvider(component)
adapter.register_status_provider(component.name, provider)
```

---

## Troubleshooting

- **Legacy fixture errors?** Remove or modernize; do not mix old-style provider registration.
- **Missing data in history?** Ensure `update_component_status` is called explicitly with each transition.

---

## Reference

- See `/docs/architecture/service_health_protocol.md` for method and event signatures.
- For examples, see `/tests/integration/monitoring/test_service_health_dashboard_integration.py`.

---