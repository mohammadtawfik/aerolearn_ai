# Modularization Plan: `/integrations/monitoring/integration_health.py`

## Background

- `/integrations/monitoring/integration_health.py` has grown to over 30KB and now has multiple responsibilities: health states/entities, provider ABC, orchestration/management, monitoring, integration registry, and notification/event logic.
- **Protocols, architecture overview, and planning docs require modular, protocol-aligned, testable surface for each feature.**
- TDD is mandatory for all future refactorings—split each protocol/API surface, write modular tests first.

---

## Required Modularization

### **Split Into:**

- **`health_status.py`**:  
  - `HealthStatus`, `HealthMetricType`, `HealthMetric`
- **`health_provider.py`**:  
  - `HealthProvider` (ABC)
- **`events.py`**:  
  - `HealthEvent` and event-related logic/listener utilities
- **`integration_health_manager.py`**:  
  - Main `IntegrationHealth` service/orchestration (depends on above modules)
- **`integration_monitor.py`**:  
  - `IntegrationMonitor` (transaction/failure/stats)
- **`integration_point_registry.py`**:  
  - `IntegrationPointRegistry` (registers/maintains system integration points)
- **`__init__.py`**:
  - Expose all protocol APIs as per public/project standards

### **All files located in** `/integrations/monitoring/`

---

## TDD Requirements for Refactor

- **Before any code is moved**:  
  - Write/ensure modular test coverage for each new module/class.
  - Unit tests for: health status/entities logic, provider contracts, event firing, monitor/registry state, listeners, orchestration.
  - Integration tests for manager/service orchestration and system-wide behavior.
  - Place unit tests in `/tests/unit/core/monitoring/` and integration in `/tests/integration/monitoring/`, one-per-protocol surface.

---

## Documentation

- **Must update on merge**:
  - `/code_summary.md`
  - `/docs/architecture/architecture_overview.md`
  - `/docs/development/day23_plan.md`
  - Any affected protocol docs listing module structure or API.

---

## Protocol/Documentation Alignment

- **Protocols strictly enforced:** All classes/functions must keep their current API and behaviors unless protocol docs also change.
- _Adapters/tests must update imports to point to the new module structure; legacy monolithic interfaces should be removed once all is green._

---

## Implementation Steps

1. **Write modular test coverage for each split surface** (entities, provider, event, registry, manager, etc).
2. **Modularize code**, moving definitions into the respective files and updating all internal/external imports.
3. **Run tests and sync docs.** No merge unless all tests pass and docs are up to date.

---

**This modularization is required to proceed with maintainable monitoring system extension, matches all current documentation, and is in line with the project's TDD/process discipline.**