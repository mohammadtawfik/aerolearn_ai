# AeroLearn AI System Architecture

## Overview [Updated: Post-Day 24]

AeroLearn AI is architected as a **modular, event-driven, and interface-based platform** for robust, extensible, and testable aerospace education applications. The system follows a layered approach with clear separation of concerns, enabling independent development and testing of components.

This overview has been updated to reflect all completed Day 24 tasks, with emphasis on protocol compliance, health monitoring, dependency tracking improvements, and the addition of the Advanced Analytics subsystem.

## Design Goals

- **Loose Coupling:** Components interact through events and interfaces, not direct dependencies
- **Extensibility:** Plug-and-play architecture allows for easy addition of new features
- **Observability:** Built-in monitoring of component health, status, and transaction tracing
- **Security:** Foundation for secure authentication, credential management, and authorization
- **Testability:** Components can be tested in isolation with mock dependencies

## Architecture Layers

### 1. Integration Framework Layer

The foundation that enables all other components to work together:

- **Event Bus:** Type-safe publish/subscribe system for cross-component communication
- **Component Registry:** Dynamic registration, discovery, and lifecycle management
- **Interface Contracts:** Formal definitions of component interactions and capabilities
- **Monitoring & Health:** System-wide observability and diagnostics

### 2. Core Application Layer

Provides fundamental services and utilities:

- **Authentication & Authorization:** User authentication, role-based access control, secure credential storage
- **Database & ORM Models:** Cloud database connectivity, local cache synchronization, data models
- **Storage Providers:** Google Drive integration, file/content management, metadata handling
- **API Clients:** Standardized clients for external services (DeepSeek, etc.)

### 3. User Interface Layer

Multiple interfaces sharing common components:

- **Professor Interface:** Content management, student monitoring, analytics dashboards
- **Student Interface:** Content access, AI learning assistance, progress tracking
- **Administrator Interface:** System management, user administration, reporting tools
- **Shared Components:** Reusable UI elements, navigation, form controls

### 4. Data Model

Structured representation of system entities:

- **User Models:** Authentication, profile, permissions
- **Course Models:** Structure, metadata, relationships
- **Content Models:** Various content types, metadata, embeddings
- **Assessment Models:** Questions, answers, evaluations, analytics

## System Diagram

```mermaid
flowchart TD
    subgraph Integration Layer
        EBus["Event Bus"]
        CReg["Component Registry"]
        Ifc["Interface Contracts"]
        Mon["Monitoring & Health"]
    end
    subgraph Application Layer
        Auth["Authentication & Authorization"]
        API["API Clients"]
        DB["Database/ORM Models"]
        Storage["File/Content Storage"]
        UI["User Interfaces"]
    end
    EBus <--> CReg
    EBus <--> Ifc
    CReg <--> Ifc
    EBus <--> Mon
    Mon <--> CReg
    API --> EBus
    Auth --> EBus
    Storage --> EBus
    DB --> EBus
    UI --> EBus
    API --> Ifc
    Storage --> Ifc
    DB --> Ifc
    Auth --> Ifc
    UI --> Ifc
    UI --> CReg
    API --> CReg
    Auth --> CReg
    Storage --> CReg
    DB --> CReg
    UI --> Mon
```

## Subsystem & Module Structure

| Subsystem                  | Core Modules / Directories                           | Responsibilities                                                                      |
|----------------------------|-----------------------------------------------------|---------------------------------------------------------------------------------------|
| **Integration Framework**  | `integrations/` (events, interfaces, monitoring, registry) | Event bus, type-safe events, interfaces, modular monitoring system, registry/dependency management    |
| **Registry & Dependencies**| `integrations/registry/` (component, component_state, dependency_graph, component_registry) | Component identity, dependency tracking, lifecycle management, graph operations |
| **Authentication & Authz** | `app/core/auth/`                                    | Credential management, authentication, session, permissions, RBAC                     |
| **Database & Models**      | `app/core/db/`, `app/models/`                       | ORM schema, client, migrations, content/user/assessment/course models                 |
| **API Clients**            | `app/core/api/`                                     | Standardized API clients for external integrations                                    |
| **Storage Providers**      | `app/core/drive/`                                   | File/folder/metadata storage, Google Drive/Cloud/Local                               |
| **Advanced Analytics**     | `app/core/analytics/`, `app/api/analytics/`         | Usage activity/engagement, aggregation, analytics/reporting API endpoints             |
| **User Interface**         | `app/ui/`                                           | Pure-Python base components, navigation, form controls, content browser, preview      |
| **Testing**                | `tests/`                                            | Unit and integration tests (including modular registry tests, analytics), UI/component harness, health monitoring |
| **Tools/Resources**        | `tools/`, `resources/`                              | Supporting scripts, templates, static files                                           |

## Key Integration Patterns

- **Event-Driven Communication:**  
  The EventBus and strongly-typed event model allow safe, extensible communication between subsystems without import-time coupling.

- **Discovery & Lifecycle Management:**  
  The Component Registry provides dynamic registration, versioning, dependency validation, and lifecycle hooks for all major platform parts.

- **Strict Interface Contracts:**  
  All major extensibility points (AI, storage, content, etc.) are defined as formal interfaces, with registration, method validation, and inheritance.

- **Continuous Monitoring:**  
  Integration status, health, and transaction logging layers ensure observability of cross-component operations.

- **Canonical cross-module enums**:  
  All registry, adapter, and dashboard logic uses enums defined in `/integrations/registry/component_state.py`.

- **Test modularity**:  
  Monolithic registry/integration tests are deprecated; all surfaces use `/tests/integration/registry/` split.

## Security Architecture

- **Secure Credential Storage:** Encrypted storage of user credentials and API keys
- **Role-Based Access Control:** Fine-grained permissions based on user roles
- **Data Encryption:** Encryption of sensitive data at rest and in transit
- **API Authentication:** Secure token-based authentication for all API calls
- **Privacy Protection:** Data minimization and user consent management

## Monitoring and Status Dashboards

- The `ServiceHealthDashboard` now supports explicit registry injection for full protocol compliance.
- It exposes the method `supports_cascading_status()` as a protocol check surface in accordance with current service health and dependency tracking documentation.
- For details of required interface and protocols, see [service_health_protocol.md](./service_health_protocol.md) and [dependency_tracking_protocol.md](./dependency_tracking_protocol.md).
- The ServiceHealthDashboard (`/app/core/monitoring/dashboard.py`) provides a protocol-compliant `get_report_data()` method returning only fields sanctioned by `/app/api/monitoring/protocol_fields.py`, directly reflecting `/docs/architecture/service_health_protocol.md`.
- The operational dashboard reporting API endpoint (`/app/api/monitoring/endpoints.py`) is verified by TDD coverage in `/tests/unit/core/monitoring/test_dashboard_reporting.py`, ensuring conformance to protocol and privacy/security requirements.
- All dashboard/reporting data surfaced in any UI or API is strictly protocol-driven, privacy-policy compliant, and is test-validated for every required field and prohibition.

### Self-Healing Architecture

- **ReliabilityManager** (`/app/core/monitoring/reliability.py`): Implements protocol-driven self-diagnosis capabilities used by the integration orchestrator for automated health checks and recovery prompting.
- **RecoveryManager** (`/app/core/monitoring/recovery.py`): Provides protocol-compliant self-repair functionality that automatically updates component state, health metrics, registry entries, and integration point tracking.
- **IntegrationPointRegistry Support**: The RecoveryManager automatically integrates with any present IntegrationPointRegistry adapter via the `notify_recovery_action` method, ensuring system-wide traceability for orchestration and dashboard views.

### Service Health & Monitoring Implementation

- All health and monitoring mechanisms now comply with `/docs/architecture/service_health_protocol.md` and `/docs/architecture/health_monitoring_protocol.md`.
- Centralized status and health reporting for all major system components use standardized protocols.
- **All protocol-mandated monitoring splits are COMPLETE, TDD-tested, and protocol-compliant in `/integrations/monitoring/`:**
  - `health_status.py` – HealthStatus, HealthMetricType, HealthMetric
  - `health_provider.py` – HealthProvider (ABC)
  - `events.py` – HealthEvent, HealthEventDispatcher, and `register_health_event_listener`
  - `integration_monitor.py` – IntegrationMonitor
  - `integration_point_registry.py` – IntegrationPointRegistry
  - `integration_health.py` – Cross-component health tracking
  - `integration_health_manager.py` – IntegrationHealth orchestration
- Additional implementations:
  - `/app/core/monitoring/metrics.py`: Core metrics collection and reporting

### Monitoring Orchestration & Event Workflow

AeroLearn AI implements protocol-driven monitoring and event orchestration:

- **Orchestrator:** `/app/core/monitoring/orchestration.py`
  - Accepts a component registry and health manager
  - Exposes protocol-compliant methods:
    - `propagate_status(component)` - Propagates status changes through dependency graph
    - `fire_status_event(component, dispatcher)` - Emits events for status changes

- **Event Dispatcher:** `/integrations/monitoring/events.py`
  - Protocol API:
    - `register_listener(listener)` - Registers event listeners
    - `fire(event)` - Emits events to all registered listeners
  - Used to emit HealthEvent objects with fields: `component`, `state`, `reason`, `timestamp`
  - Listener pattern enables full TDD of event emissions and event-driven side effects

- **Status/Event Test Coverage**:
  - All cross-module and event-driven tests implemented in `/tests/unit/core/monitoring/test_orchestration.py`
  - Tests enforce protocol compliance including correct method/argument names and workflow sequencing
  - All components must use protocol-documented argument names (e.g., `component` not `component_id`, `state` not `status`)

**Example API Usage (Protocol-Compliant):**
```python
# Register and initialize components
comp_id = registry.register_component(name="ComponentA")
health_manager.register_component(comp_id)
health_manager.update_component_status(comp_id, HealthStatus.HEALTHY)

# Set up orchestration and fire events
orchestrator = MonitoringOrchestrator(registry, health_manager)
orchestrator.fire_status_event(comp_id, dispatcher=dispatcher)
```

### Self-Healing Orchestration

The AeroLearn AI platform implements a comprehensive self-healing workflow that enables automatic detection, diagnosis, and recovery from component failures:

- **End-to-End Self-Healing Flow:**
  1. The ReliabilityManager continuously monitors component health via the health manager
  2. When issues are detected, it performs protocol-driven diagnosis to identify root causes
  3. The RecoveryManager is invoked with appropriate recovery strategies
  4. Recovery actions are executed and tracked through the IntegrationPointRegistry
  5. Component states and health metrics are automatically updated
  6. Recovery events are dispatched to all registered listeners

- **Test-Driven Validation:**
  - Complete self-healing workflow is validated in `/tests/integration/monitoring/test_reliability_and_selfhealing.py`
  - Tests verify all events, state transitions, metrics updates, and registry interactions
  - Protocol compliance is enforced for all APIs, enums, and event structures

**Self-Healing API Example:**
```python
# Detect and diagnose issues
reliability_manager = ReliabilityManager(health_manager, registry)
diagnosis_result = reliability_manager.diagnose_component(component_id)

# Perform recovery
recovery_manager = RecoveryManager(health_manager, registry)
recovery_result = recovery_manager.attempt_recovery(
    component_id, 
    diagnosis_result.recommended_strategy
)

# Verify recovery success
assert recovery_result.success
assert health_manager.get_component_status(component_id) == HealthStatus.HEALTHY
```

## Registry & Dependency Management

**Motivation:**  
Complex component/service systems require robust, testable, and modular state and dependency tracking. The registry layer is split into four modules for clarity, maintainability, and to enforce separation of health/monitoring and registry state:

- `component.py`: Pure "Component" entity, protocol-driven, holds identity, description, version, and state.
- `component_state.py`: Canonical source for `ComponentState` enum. Used by all registry, monitoring, and dashboard logic; prevents cross-import/circularity.
- `dependency_graph.py`: Standalone dependency edge management, insertion order doctrine, and analytics.
- `component_registry.py`: Orchestrates protocol API (register, unregister, declare_dependency), delegates state and dependency logic.

**Protocol Enforcement:**
- **ComponentRegistration, lifecycle, and dependency tracking fully modularized and enforced by protocol.**
- **All protocol features are enforced and proven by:**
    - `/tests/integration/registry/test_component_registry_registration.py`
    - `/tests/integration/registry/test_component_registry_lifecycle.py`
    - `/tests/integration/registry/test_component_registry_dependency.py`
    - `/tests/integration/monitoring/test_dependency_tracking.py` (Day 22 addition)

**Integration:**  
- All cross-component state enums are imported from `component_state.py`.
- All health monitoring, dashboard, and adapter modules interact with the registry solely through this focused protocol API.
- Downstream modules and tests should create or query components and dependencies via these APIs for full protocol compliance.

**Test-Driven Approach:**  
- Modular, TDD-first integration and protocol tests are now placed under `/tests/integration/registry/`.
- Each registry/protocol surface is verified by a dedicated test module before implementation.
- Protocol compliance is now enforced at structure and API surface levels.

**Ordered Dependency Lists:**  
- All dependency lists, outbound or inbound, are guaranteed to preserve insertion order.
- Whether querying direct dependencies (`get_dependency_graph()`) or dependents (`analyze_dependency_impact`, `get_dependents()`), lists are presented in runtime registration order—never as unordered sets.
- This ordering guarantee is essential for deterministic analytics, visualizations, and exact test repeatability.

**Dependency Tracking Implementation:**
- Dependency tracking implemented in `/integrations/registry/dependency_graph.py` with insertion-order guarantee.
- All registry components call this protocol module; coverage is enforced by modular tests per plan and TDD.
- Day 22 update: All component and service dependency relationships have been synchronized and verified against `/docs/architecture/dependency_tracking_protocol.md`.

Refer to `/integrations/registry` for implementation details.


## Protocol Reference Table

| Protocol                           | Documented in                                            | Implemented in                                |
|-------------------------------------|----------------------------------------------------------|-----------------------------------------------|
| Service Health Protocol             | `/docs/architecture/service_health_protocol.md`          | `/app/core/monitoring/metrics.py`, `/integrations/monitoring/integration_health.py` |
| Health Monitoring Protocol          | `/docs/architecture/health_monitoring_protocol.md`       | `/integrations/monitoring/` (fully modularized: health_status.py, health_provider.py, events.py, integration_monitor.py, etc.) |
| Dependency Tracking Protocol        | `/docs/architecture/dependency_tracking_protocol.md`     | `/integrations/registry/component_registry.py` |
| Monitoring Orchestration Protocol   | `/docs/architecture/health_monitoring_protocol.md`       | `/app/core/monitoring/orchestration.py`, `/integrations/monitoring/events.py` |
| Health Metrics Protocol             | `/docs/architecture/health_monitoring_protocol.md`       | `/integrations/monitoring/health_status.py`, `/app/core/monitoring/metrics.py` |
| Analytics Protocol                  | `/docs/architecture/health_monitoring_protocol.md`       | `/app/core/analytics/advanced.py`, `/app/api/analytics/endpoints.py` |
| Self-Healing Protocol               | `/docs/architecture/health_monitoring_protocol.md`       | `/app/core/monitoring/reliability.py`, `/app/core/monitoring/recovery.py` |
| AI Recommendation Protocol          | `/docs/architecture/ai_recommendation_protocol.md`       | `/app/core/ai/learning_path.py`, `/app/core/ai/material_selection.py`, `/app/core/ai/cross_course_recommendation.py` |
| Content Optimization Protocol       | `/docs/architecture/content_optimization_protocol.md`    | `/app/core/ai/content_optimization.py` |

## Testing and Verification

All Day 24 delivered components, services, and protocols are supported with comprehensive automated tests:

- **Health Monitoring Tests**: Verify protocol compliance for all monitoring interfaces through TDD-driven modular test suites
- **Dependency Tracking Tests**: Ensure proper dependency relationship management
- **Integration Tests**: Validate cross-component interactions and state management
- **Protocol Compliance Tests**: Confirm adherence to documented protocol specifications
- **Health Metrics Tests**: Validate preservation of health metrics and state propagation
- **Analytics Tests**: Verify analytics data collection, aggregation, and reporting functionality
- **Self-Healing Tests**: Validate the complete self-healing workflow including diagnosis, recovery, and state restoration

For detailed test coverage, see `/tests/integration/monitoring/`, `/tests/integration/registry/`, `/tests/integration/analytics/`, and the dedicated self-healing test suite at `/tests/integration/monitoring/test_reliability_and_selfhealing.py`.

### Health Metrics and State Propagation Protocol

- **ServiceHealthDashboard** and **IntegrationHealthManager** guarantee that updates to status or health metrics propagate exactly as set—metrics are always preserved as a list (of HealthMetric objects) and state is preserved (HEALTHY, RUNNING, etc.) with no normalization.
- Downstream tests (including cross-module and TDD-driven integration) pass by directly querying the dashboard for the last-set state and full metrics.
- All protocol API surfaces enforce this contract.
- Test-driven development ensures that:
  - Health metrics are preserved in their original form
  - State transitions are accurately tracked and propagated
  - Component dependencies correctly reflect health status changes
  - Dashboard displays accurate and up-to-date health information

## Analytics Architecture

- **UsageAnalytics** (in `/app/core/analytics/advanced.py`) is the protocol-compliant analytics backbone, implementing `track_activity`, `query_activities`, `aggregate_usage`, `feature_usage_report`, `query_sessions`, `clear`.
- **API Endpoints:** `/app/api/analytics/endpoints.py` exposes analytics with strictly protocol-documented fields, verified by `/tests/integration/analytics/test_endpoints.py`.
- **Test-Driven Compliance:** TDD tests for every analytics protocol surface are in `/tests/unit/core/analytics/test_advanced.py`, always preceding any implementation.
- **Protocol Cross-link:** All analytics APIs/fields are specified and mapped to `/docs/architecture/health_monitoring_protocol.md`.
- **Complete Test/Doc Sync:** As of Day 24 plan closure, all analytics systems, interfaces, and test coverage are synchronized in documentation and implementation.
- **Teaching Insights Analytics** (in `/app/core/analytics/teaching_insights.py`):
  - Protocol-driven computation of teaching effectiveness, content impact, engagement-outcome correlation, and actionable recommendations for instructors.
  - Exposes all protocol APIs and structured data as per `/docs/architecture/health_monitoring_protocol.md` §11.
  - All analytics methods, fields, and multi-surface report aggregation are TDD tested; status exported to dashboards and API endpoints.
  - Unit and integration test coverage fully synchronized and green as of Day 25; full documentation/test/code sync policy enforced.

## AI Recommendation Engine

The AeroLearn AI platform includes a protocol-driven recommendation engine that generates personalized learning paths for students:

- **Learning Path Generator** (in `/app/core/ai/learning_path.py`):
  - Implements the canonical API `generate_learning_path(student, candidate_content, max_length=10, adaptivity=True)`
  - Returns structured learning paths with sequenced content items, difficulty levels, prerequisites, and justifications
  - Supports adaptive mode that dynamically adjusts recommendations based on student performance and preferences
  - Ensures all recommendations include RFC3339 timestamps and proper student identification

- **Personalized Material Selection** (in `/app/core/ai/material_selection.py`):
  - Detects student learning styles using protocol-compliant detection strategies
  - Matches content items/styles, adapts filtering and sequencing based on individualized profiles
  - Protocol and API contract: see `/docs/architecture/ai_recommendation_protocol.md`
  - Fully test-driven: All required tests implemented and passing (`/tests/unit/core/ai/test_material_selection.py`)
  - Documentation, code, and test surfaces are strictly synchronized as of Day 25

- **Cross-Course Recommendation Engine** (in `/app/core/ai/cross_course_recommendation.py`):
  - Aggregates learning data, content, and analytic events across courses for each student or program
  - Provides unified recommendations, curriculum-wide sequencing, cross-referencing, and optimization suggestions
  - Implements all contract fields and APIs from `/docs/architecture/ai_recommendation_protocol.md`
  - Supports holistic learning path generation that spans multiple courses and disciplines
  - Comprehensive test coverage through unit and integration tests (`/tests/unit/core/ai/test_crosscourse_reco.py`, `/tests/integration/ai/test_crosscourse_reco.py`)
  - Fully integrated with the AI recommendation system and analytics framework

- **Protocol Compliance:**
  - All recommendation engine interfaces adhere to `/docs/architecture/ai_recommendation_protocol.md`
  - Returned data structures follow strict protocol specifications including required fields:
    - `student_id`: Unique identifier for the target student
    - `generated_at`: RFC3339 timestamp of recommendation generation
    - `steps`: Ordered array of learning path steps with content references, difficulty, prerequisites, and justifications

- **Test-Driven Development:**
  - Comprehensive test suite in `/tests/unit/core/ai/test_learning_path.py` and `/tests/unit/core/ai/test_material_selection.py`
  - Tests verify all protocol requirements including sequencing logic, adaptivity toggling, max length enforcement, and field validation
  - No implementation is merged without passing all protocol-specified test cases

- **Integration Points:**
  - Integrates with the analytics subsystem to incorporate usage patterns into recommendations
  - Connects with content models to access metadata for intelligent sequencing
  - Interfaces with student progress tracking to tailor recommendations to individual learning journeys

## Future Evolution

- Pluggable data providers (beyond Google Drive)
- Multi-modal UI (Web, CLI, Desktop)
- Enhanced analytics and adaptive learning flows
- Automated deployment & update system

## Further Reference

For detailed protocol requirements and implementation specifics, always crosscheck:
- [Day 24 Plan and Completion](/docs/development/day24_plan.md)
- [Protocol Specification Documents](/docs/architecture/)
- [Service Health Protocol (API)](/docs/api/service_health_protocol.md)
- [Analytics Protocol (API)](/docs/api/analytics_protocol.md)

## End-of-Day 25 Architecture Summary [UPDATED]
- Advanced Usage Analytics framework is fully implemented, TDD tested (unit+integration), and doc-synced with protocols and `/code_summary.md`
- All analytics API endpoints expose only protocol/documented fields, privacy and test-verified
- Teaching Insights Analytics subsystem is fully implemented with protocol-driven instructor recommendations and effectiveness metrics
- No analytics task or documentation mismatches remain open as of this cycle
- Learning Path Recommendation Engine is fully implemented with protocol compliance and comprehensive test coverage
- AI recommendation capabilities now support personalized, adaptive learning paths with proper sequencing and justifications
- Content Optimization Engine is fully implemented with protocol compliance and comprehensive test coverage
- Personalized Material Selection subsystem is fully implemented with learning style detection and content matching capabilities
- Cross-Course Recommendation Engine is fully implemented with curriculum-wide recommendation capabilities
- All AI recommendation components are now synchronized across documentation, implementation, and test coverage

## AI Content Optimization Engine

The AeroLearn AI platform includes a protocol-driven engine for automated content improvement:

- **Content Optimization Engine** (in `/app/core/ai/content_optimization.py`):
  - Implements the canonical API `suggest_content_optimizations(content_item, templates=None, context=None)`
  - Suggests, explains, and previews improvements for educational content (clarity, engagement, etc.)
  - Returns protocol-specified dictionary with:
    - `content_id`: Unique identifier for the content being optimized
    - `suggestions`: Array of improvement suggestions (each with template, before/after text, explanation)
    - `overall_analysis`: Content quality scores, tags, and preview
    - `generated_at`: RFC3339 timestamp of optimization generation

- **Protocol Compliance:**
  - All optimization engine interfaces adhere to `/docs/architecture/content_optimization_protocol.md`
  - Returned data structures follow strict protocol specifications including required fields
  - Supports template-driven optimization strategies that can be extended or customized

- **Test-Driven Development:**
  - Comprehensive test suite in `/tests/unit/core/ai/test_content_optimization.py`
  - Tests verify all protocol requirements including no-op behavior, template application, preview generation, analytics integration, and timestamp compliance
  - No implementation is merged without passing all protocol-specified test cases

- **Extensibility:**
  - Protocol, code, and test suite evolve together with every feature or template extension
  - All changes are documented in `/docs/architecture/content_optimization_protocol.md`
  - Integration with analytics system to track optimization effectiveness
