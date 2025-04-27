# Project Summary: aerolearn_ai

*Generated on code_summary.md*

Total Python files: 110

## Table of Contents

1. [Project Structure](#project-structure)
2. [Key Files](#key-files)
3. [Dependencies](#dependencies)
4. [Detailed Code Analysis](#detailed-code-analysis)

## Project Structure

```
├── app
│   ├── core
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   ├── credential_manager.py
│   │   │   ├── user_profile.py
│   │   │   ├── authentication.py
│   │   │   ├── session.py
│   │   │   ├── authorization.py
│   │   │   └── permission_registry.py
│   │   ├── db
│   │   │   ├── __init__.py
│   │   │   ├── db_client.py
│   │   │   ├── schema.py
│   │   │   ├── migrations.py
│   │   │   ├── event_hooks.py
│   │   │   ├── db_events.py
│   │   │   ├── local_cache.py
│   │   │   └── sync_manager.py
│   │   ├── drive
│   │   │   ├── __init__.py
│   │   │   ├── file_operations.py
│   │   │   ├── folder_structure.py
│   │   │   ├── metadata.py
│   │   │   └── sync_manager.py
│   │   ├── ai
│   │   │   └── __init__.py
│   │   └── api
│   │       ├── api_client.py
│   │       ├── deepseek_client.py
│   │       └── google_drive_client.py
│   ├── ui
│   │   ├── common
│   │   │   ├── __init__.py
│   │   │   ├── component_base.py
│   │   │   ├── test_component_architecture.py
│   │   │   ├── component_registry.py
│   │   │   ├── main_window.py
│   │   │   ├── navigation.py
│   │   │   ├── form_controls.py
│   │   │   ├── content_browser.py
│   │   │   └── content_preview.py
│   │   ├── professor
│   │   │   └── __init__.py
│   │   ├── student
│   │   │   └── __init__.py
│   │   └── admin
│   │       └── __init__.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── content.py
│   │   └── assessment.py
│   ├── utils
│   │   ├── __init__.py
│   │   └── crypto.py
│   ├── config
│   │   └── __init__.py
│   ├── __init__.py
│   └── main.py
├── integrations
│   ├── interfaces
│   │   ├── __init__.py
│   │   ├── base_interface.py
│   │   ├── content_interface.py
│   │   ├── storage_interface.py
│   │   └── ai_interface.py
│   ├── registry
│   │   ├── __init__.py
│   │   ├── dependency_tracker.py
│   │   ├── component_registry.py
│   │   └── interface_registry.py
│   ├── events
│   │   ├── __init__.py
│   │   ├── event_types.py
│   │   ├── event_subscribers.py
│   │   └── event_bus.py
│   ├── monitoring
│   │   ├── __init__.py
│   │   ├── integration_health.py
│   │   ├── component_status.py
│   │   └── transaction_logger.py
│   └── __init__.py
├── tests
│   ├── unit
│   │   ├── core
│   │   │   ├── auth
│   │   │   │   ├── test_authentication.py
│   │   │   │   └── test_authorization.py
│   │   │   ├── api
│   │   │   │   └── test_api_clients.py
│   │   │   ├── __init__.py
│   │   │   └── test_integration_health.py
│   │   ├── ui
│   │   │   └── __init__.py
│   │   ├── models
│   │   │   └── __init__.py
│   │   ├── test_crypto.py
│   │   ├── test_credential_manager.py
│   │   └── test_local_cache_and_sync.py
│   ├── integration
│   │   ├── interfaces
│   │   │   ├── test_base_interface.py
│   │   │   ├── test_content_interface.py
│   │   │   ├── test_storage_interface.py
│   │   │   └── test_ai_interface.py
│   │   ├── __init__.py
│   │   ├── test_event_bus.py
│   │   ├── test_component_registry.py
│   │   ├── test_component_registry_async.py
│   │   ├── test_component_registry_Simple.py
│   │   ├── test_monitoring.py
│   │   ├── test_health_metrics.py
│   │   ├── test_component_status.py
│   │   ├── test_auth_event_bus.py
│   │   ├── test_db_integration.py
│   │   ├── test_phase1_foundation.py
│   │   ├── phase1_foundation_patch.py
│   │   ├── component_harness.py
│   │   ├── test_framework.py
│   │   ├── test_auth_integration.py
│   │   ├── test_storage_integration.py
│   │   └── test_ui_integration.py
│   ├── ui
│   │   ├── __init__.py
│   │   ├── test_component_architecture.py
│   │   ├── test_main_window.py
│   │   └── test_common_ui_controls.py
│   ├── fixtures
│   │   └── __init__.py
│   ├── examples
│   │   └── event_bus_example.py
│   ├── models
│   │   └── test_models.py
│   └── __init__.py
├── docs
│   ├── architecture

│   ├── api

│   ├── user_guides

│   └── development

├── tools
│   ├── integration_monitor
│   │   └── __init__.py
│   └── project_management
│       └── __init__.py
├── resources
│   ├── styles

│   ├── templates
│   │   ├── ai_prompts

│   │   └── report_templates

│   └── sample_data
│       ├── courses

│       ├── users

│       └── content

├── scripts
│   ├── __init__.py
│   └── setup.py
├── .spyproject
│   └── config
│       ├── backups

│       └── defaults

├── .qodo

├── untitled3.py
├── code_summarizer.py
└── setup.py
```

## Key Files

### integrations\events\event_types.py

Event type definitions for the AeroLearn AI event system.

This module defines the event classes and types used throughout the system for
inter-compon...

- Classes: 13
- Functions: 0
- Dependency Score: 91.00

### integrations\registry\component_registry.py

Component registry for the AeroLearn AI system.

This module provides a centralized registry for all system components,
tracking their lifecycle, depe...

- Classes: 6
- Functions: 0
- Dependency Score: 71.00

### integrations\interfaces\base_interface.py

Base interface definitions for the AeroLearn AI system.

This module provides the core interface contract infrastructure, including interface
registra...

- Classes: 10
- Functions: 1
- Dependency Score: 63.00

### integrations\monitoring\transaction_logger.py

Transaction logging for the AeroLearn AI system.

This module provides tools for tracking and logging cross-component transactions,
making it easier t...

- Classes: 6
- Functions: 0
- Dependency Score: 62.00

### integrations\events\event_bus.py

Event bus implementation for the AeroLearn AI event system.

This module provides the central event bus for inter-component communication,
implementin...

- Classes: 1
- Functions: 0
- Dependency Score: 61.00

### integrations\monitoring\integration_health.py

Integration health monitoring for the AeroLearn AI system.

This module provides health metric collection, status tracking, and visualization
data str...

- Classes: 7
- Functions: 0
- Dependency Score: 57.00

### integrations\interfaces\ai_interface.py

AI interface contracts for the AeroLearn AI system.

This module defines the interfaces for AI-powered components, including language models,
content ...

- Classes: 15
- Functions: 1
- Dependency Score: 56.00

### app\core\db\schema.py

Schema configuration for AeroLearn AI
Defines SQLAlchemy declarative base and example table definitions for testing relationships.

- Classes: 11
- Functions: 0
- Dependency Score: 54.00

### integrations\monitoring\component_status.py

Component status tracking for the AeroLearn AI system.

This module provides components for tracking and visualizing the status
of system components, ...

- Classes: 6
- Functions: 0
- Dependency Score: 53.00

### tests\integration\interfaces\test_ai_interface.py

Unit tests for the AI interface contracts.

This module tests the functionality of the AI-related interfaces like
AIModelProviderInterface, ContentAna...

- Classes: 10
- Functions: 0
- Dependency Score: 48.00

## Dependencies

Key file relationships (files with most dependencies):

- **integrations\monitoring\transaction_logger.py** depends on: integrations\registry\component_registry.py, integrations\events\event_types.py
- **integrations\monitoring\integration_health.py** depends on: integrations\registry\component_registry.py, integrations\events\event_types.py
- **integrations\monitoring\component_status.py** depends on: integrations\registry\component_registry.py, integrations\events\event_types.py
- **tests\integration\interfaces\test_ai_interface.py** depends on: integrations\interfaces\ai_interface.py, integrations\interfaces\base_interface.py


## Detailed Code Analysis

### integrations\events\event_types.py

**Description:**

Event type definitions for the AeroLearn AI event system.

This module defines the event classes and types used throughout the system for
inter-component communication. It provides a type-safe way to define and handle events.

Event types can be accessed either through the EventType enum (for type checking and IDE support)
or through the category-specific classes (SystemEventType, ContentEventType, etc.) for
organizational clarity.

**Classes:**

- `EventType`
 (inherits from: enum.Enum)


  General event type enumeration for core system/event bus usage.

- `EventPriority`
 (inherits from: enum.IntEnum)


  Event priority levels for determining handling order.

- `EventCategory`
 (inherits from: enum.Enum)


  Categories for grouping related events.

- `Event`


  Base class for all events in the system.

  Methods: `serialize()`, `deserialize()`

- `SystemEvent`
 (inherits from: Event)


  System-level events related to application lifecycle and operations.

  Methods: `__init__()`

- `ContentEvent`
 (inherits from: Event)


  Events related to educational content operations.

  Methods: `__init__()`

- `UserEvent`
 (inherits from: Event)


  Events related to user actions and profile changes.

  Methods: `__init__()`

- `AIEvent`
 (inherits from: Event)


  Events related to AI operations and intelligence.

  Methods: `__init__()`

- `UIEvent`
 (inherits from: Event)


  Events related to user interface interactions.

  Methods: `__init__()`

- `SystemEventType`


  Common system event type constants.

- `ContentEventType`


  Common content event type constants.

- `UserEventType`


  Common user event type constants.

- `AIEventType`


  Common AI event type constants.



### integrations\registry\component_registry.py

**Description:**

Component registry for the AeroLearn AI system.

This module provides a centralized registry for all system components,
tracking their lifecycle, dependencies, and version information.

**Classes:**

- `ComponentRegisteredEvent`
 (inherits from: Event)


  Event fired when a component is registered.

  Methods: `__init__()`

- `ComponentUnregisteredEvent`
 (inherits from: Event)


  Event fired when a component is unregistered.

  Methods: `__init__()`

- `ComponentStateChangedEvent`
 (inherits from: Event)


  Event fired when a component's state changes.

  Methods: `__init__()`

- `ComponentState`


  Enum-like class for component lifecycle states.

- `Component`


  Base class for all registrable components in the system.

  Methods: `__init__()`, `__getitem__()`, `__iter__()`, `items()`, `declare_dependency()`, ... (2 more)

- `ComponentRegistry`


  Central registry for AeroLearn AI system components.

  Methods: `__new__()`, `__init__()`, `register_component()`, `register_component_instance()`, `unregister_component()`, ... (8 more)



### integrations\interfaces\base_interface.py

**Description:**

Base interface definitions for the AeroLearn AI system.

This module provides the core interface contract infrastructure, including interface
registration, discovery, and method signature validation mechanisms. All specific
interfaces in the system should inherit from the base classes defined here.

**Classes:**

- `InterfaceVersion`


  Helper class for managing interface versioning.

  Methods: `__init__()`, `__str__()`, `from_string()`, `is_compatible_with()`

- `MethodSignature`


  Class for representing and validating method signatures.

  Methods: `__init__()`, `validate_implementation()`

- `InterfaceMethod`


  Decorator for interface methods that captures signature information.

  Methods: `__init__()`, `__get__()`

- `InterfaceError`
 (inherits from: Exception)


  Base exception for interface-related errors.

- `InterfaceImplementationError`
 (inherits from: InterfaceError)


  Exception raised when an interface is implemented incorrectly.

- `InterfaceRegistryError`
 (inherits from: InterfaceError)


  Exception raised for interface registration errors.

- `InterfaceVersionError`
 (inherits from: InterfaceError)


  Exception raised for interface version errors.

- `BaseInterface`
 (inherits from: abc.ABC)


  Base class for all interface contracts in the system.

  Methods: `register_interface()`, `get_interface()`, `get_all_interfaces()`, `get_interface_methods()`, `validate_implementation()`, ... (1 more)

- `InterfaceImplementation`


  Decorator for classes that implement interfaces.

  Methods: `__init__()`, `__call__()`

- `InterfaceRegisteredEvent`
 (inherits from: Event)


  Event fired when an interface is registered.

  Methods: `__init__()`

**Functions:**

- `register_all_interfaces()`

  Register all interfaces defined in the system.



### integrations\monitoring\transaction_logger.py

**Description:**

Transaction logging for the AeroLearn AI system.

This module provides tools for tracking and logging cross-component transactions,
making it easier to trace operations as they flow through different parts of the system.

**Classes:**

- `TransactionStage`
 (inherits from: Enum)


  Stages of a transaction lifecycle.

- `TransactionEvent`
 (inherits from: Event)


  Event fired when a transaction changes stage.

  Methods: `__init__()`, `to_dict()`

- `TransactionError`
 (inherits from: Exception)


  Exception raised for errors in transaction processing.

- `Transaction`


  Represents a cross-component transaction.

  Methods: `__init__()`, `start()`, `process()`, `complete()`, `fail()`, ... (6 more)

- `TransactionContext`


  Context manager for transaction handling.

  Methods: `__init__()`, `__enter__()`, `__exit__()`

- `TransactionLogger`
 (inherits from: Component)


  System for logging and tracking cross-component transactions.

  Methods: `__init__()`, `create_transaction()`, `update_transaction()`, `get_transaction()`, `get_transactions_by_parent()`, ... (14 more)



### integrations\events\event_bus.py

**Description:**

Event bus implementation for the AeroLearn AI event system.

This module provides the central event bus for inter-component communication,
implementing the publisher-subscriber pattern with event filtering
and persistence for critical events.

**Classes:**

- `EventBus`


  Central event bus for the AeroLearn AI system.

  Methods: `get()`, `__new__()`, `__init__()`, `register_subscriber()`, `unregister_subscriber()`, ... (8 more)



### integrations\monitoring\integration_health.py

**Description:**

Integration health monitoring for the AeroLearn AI system.

This module provides health metric collection, status tracking, and visualization
data structures for monitoring the health of system integrations.

**Classes:**

- `HealthStatus`
 (inherits from: Enum)


  Health status levels for components and integrations.

- `HealthMetricType`
 (inherits from: Enum)


  Types of health metrics that can be collected.

- `HealthMetric`


  A single health metric measurement.

  Methods: `__init__()`, `get_status()`, `to_dict()`

- `HealthEvent`
 (inherits from: Event)


  Event fired when a significant health status change occurs.

  Methods: `__init__()`

- `HealthProvider`
 (inherits from: ABC)


  Interface for components that provide health information.

  Methods: `get_health_metrics()`, `get_health_status()`

- `IntegrationHealthError`
 (inherits from: Exception)


  Exception raised for errors in the integration health system.

- `IntegrationHealth`
 (inherits from: Component)


  Central system for tracking integration health across components.

  Methods: `__init__()`, `register_health_provider()`, `unregister_health_provider()`, `collect_metrics()`, `_update_metrics()`, ... (10 more)



### integrations\interfaces\ai_interface.py

**Description:**

AI interface contracts for the AeroLearn AI system.

This module defines the interfaces for AI-powered components, including language models,
content analysis, question answering, and recommendation systems.

**Classes:**

- `AIModelType`
 (inherits from: Enum)


  Types of AI models used in the system.

- `AIModelCapability`
 (inherits from: Enum)


  Specific capabilities that AI models might provide.

- `AIProviderType`
 (inherits from: Enum)


  Types of AI providers.

- `AIModelMetadata`


  Metadata about an AI model.

  Methods: `__init__()`

- `AIRequest`


  Base class for AI requests.

  Methods: `__init__()`

- `TextGenerationRequest`
 (inherits from: AIRequest)


  Request for text generation.

  Methods: `__init__()`

- `EmbeddingRequest`
 (inherits from: AIRequest)


  Request for text embedding.

  Methods: `__init__()`

- `AIResponse`


  Base class for AI responses.

  Methods: `__init__()`

- `TextGenerationResponse`
 (inherits from: AIResponse)


  Response from text generation.

  Methods: `__init__()`

- `EmbeddingResponse`
 (inherits from: AIResponse)


  Response from text embedding.

  Methods: `__init__()`

- `AIModelProviderInterface`
 (inherits from: BaseInterface)


  Interface for components that provide access to AI models.

- `ContentAnalysisInterface`
 (inherits from: BaseInterface)


  Interface for AI components that analyze educational content.

- `LearningAssistantInterface`
 (inherits from: BaseInterface)


  Interface for AI components that provide learning assistance.

- `PersonalizationInterface`
 (inherits from: BaseInterface)


  Interface for AI components that provide personalized recommendations.

- `AIUsageTrackingInterface`
 (inherits from: BaseInterface)


  Interface for components that track AI usage and costs.

**Functions:**

- `register_ai_interfaces()`

  Register all AI interfaces.



### app\core\db\schema.py

**Description:**

Schema configuration for AeroLearn AI
Defines SQLAlchemy declarative base and example table definitions for testing relationships.

**Classes:**

- `User`
 (inherits from: Base)


- `UserProfile`
 (inherits from: Base)


- `Topic`
 (inherits from: Base)


- `Module`
 (inherits from: Base)


- `Lesson`
 (inherits from: Base)


- `Quiz`
 (inherits from: Base)


- `Question`
 (inherits from: Base)


- `Answer`
 (inherits from: Base)


- `LearningPath`
 (inherits from: Base)


- `PathModule`
 (inherits from: Base)


- `ProgressRecord`
 (inherits from: Base)




### integrations\monitoring\component_status.py

**Description:**

Component status tracking for the AeroLearn AI system.

This module provides components for tracking and visualizing the status
of system components, including lifecycle state changes, health status,
and operational capability.

**Classes:**

- `StatusSeverity`
 (inherits from: Enum)


  Severity levels for component status changes.

- `StatusChangeEvent`
 (inherits from: Event)


  Event fired when a component's status changes.

  Methods: `__init__()`, `to_dict()`

- `ComponentStatusProvider`
 (inherits from: ABC)


  Interface for components that provide status information.

  Methods: `get_component_state()`, `get_status_details()`

- `ComponentStatus`


  Represents the status of a component at a specific point in time.

  Methods: `__init__()`, `to_dict()`, `set_status()`, `get_status()`

- `StatusHistoryEntry`


  A historical status entry for a component.

  Methods: `__init__()`, `to_dict()`

- `ComponentStatusTracker`
 (inherits from: Component)


  System for tracking component status changes over time.

  Methods: `__init__()`, `register_status_provider()`, `unregister_status_provider()`, `update_component_status()`, `update_all_statuses()`, ... (8 more)



### tests\integration\interfaces\test_ai_interface.py

**Description:**

Unit tests for the AI interface contracts.

This module tests the functionality of the AI-related interfaces like
AIModelProviderInterface, ContentAnalysisInterface, and others.

**Classes:**

- `TestAIEnums`


  Tests for AI-related enumerations.

  Methods: `test_ai_model_type_values()`, `test_ai_model_capability_values()`, `test_ai_provider_type_values()`

- `TestAIModelMetadata`


  Tests for the AIModelMetadata class.

  Methods: `test_init_with_required_fields()`, `test_init_with_all_fields()`

- `TestAIRequests`


  Tests for AI request classes.

  Methods: `test_ai_request_init()`, `test_text_generation_request_init()`, `test_embedding_request_init()`

- `TestAIResponses`


  Tests for AI response classes.

  Methods: `test_ai_response_init()`, `test_text_generation_response_init()`, `test_embedding_response_init()`

- `TestAIModelProviderInterface`


  Tests for the AIModelProviderInterface.

  Methods: `test_interface_registration()`

- `TestContentAnalysisInterface`


  Tests for the ContentAnalysisInterface.

  Methods: `test_interface_registration()`

- `TestLearningAssistantInterface`


  Tests for the LearningAssistantInterface.

  Methods: `test_interface_registration()`

- `TestPersonalizationInterface`


  Tests for the PersonalizationInterface.

  Methods: `test_interface_registration()`

- `TestAIUsageTrackingInterface`


  Tests for the AIUsageTrackingInterface.

  Methods: `test_interface_registration()`

- `TestRegisterAIInterfaces`


  Tests for the register_ai_interfaces function.

  Methods: `test_register_ai_interfaces()`, `test_individual_interface_registrations()`



### integrations\events\event_subscribers.py

**Description:**

Event subscriber definitions and management for the AeroLearn AI event system.

This module provides the base classes and utilities for components to subscribe to
and handle events from the event bus. It also defines the EventFilter interface for selective event handling.

**Classes:**

- `EventFilter`


  EventFilter selects which events a subscriber is interested in 

  Methods: `__init__()`, `matches()`, `filter()`

- `AcceptAllEventFilter`
 (inherits from: EventFilter)


  Default event filter that accepts all events.

  Methods: `__init__()`, `matches()`, `filter()`

- `CompositeEventFilter`
 (inherits from: EventFilter)


  Accepts events if any of the provided filters accept them.

  Methods: `__init__()`, `matches()`, `filter()`

- `EventSubscriber`


  Abstract base class for components that subscribe to events from the EventBus.

  Methods: `__init__()`, `add_filter()`, `on_event()`, `event_filter()`

- `LoggingEventSubscriber`
 (inherits from: EventSubscriber)


  Example event subscriber that logs all received events.

  Methods: `__init__()`, `on_event()`

- `CallbackEventSubscriber`
 (inherits from: EventSubscriber)


  Event subscriber that uses a provided callback function for event processing.

  Methods: `__init__()`, `on_event()`



### app\ui\common\form_controls.py

**Description:**

AeroLearn AI — Standardized UI Form Controls module

This module provides reusable, themed UI form controls for the desktop UI. 
Designed to be used with a UI toolkit such as PyQt5/PySide2 (Qt), though logic is separated
for backend/UI framework independence and testability.

Includes:
- TextInputControl (single-line)
- PasswordInputControl
- MultiLineTextControl
- DropdownControl
- CheckboxControl

Implements:
- Input validation
- Error/validation message display
- Event emission (value changed, validation status)
- Theme/style compatibility
- Basic accessibility support

Integration: Hooks into EventBus system for notification and validation events.

**Classes:**

- `BaseFormControl`
 (inherits from: QWidget)


  Abstract base for AeroLearn form controls.

  Methods: `__init__()`, `_setup_ui()`, `_connect_events()`, `get_value()`, `set_value()`, ... (1 more)

- `TextInputControl`
 (inherits from: BaseFormControl)


  Methods: `_setup_ui()`, `_connect_events()`, `get_value()`, `set_value()`

- `PasswordInputControl`
 (inherits from: TextInputControl)


  Methods: `_setup_ui()`

- `MultiLineTextControl`
 (inherits from: BaseFormControl)


  Methods: `_setup_ui()`, `_connect_events()`, `get_value()`, `set_value()`

- `DropdownControl`
 (inherits from: BaseFormControl)


  Methods: `__init__()`, `_setup_ui()`, `_connect_events()`, `get_value()`, `set_value()`

- `CheckboxControl`
 (inherits from: BaseFormControl)


  Methods: `_setup_ui()`, `_connect_events()`, `get_value()`, `set_value()`

**Functions:**

- `create_test_form()`



### tests\integration\interfaces\test_storage_interface.py

**Description:**

Unit tests for the storage interface contracts.

This module tests the functionality of the storage-related interfaces like
StorageProviderInterface, SynchronizationInterface, and others.

**Classes:**

- `TestStorageEnums`


  Tests for storage-related enumerations.

  Methods: `test_storage_scope_values()`, `test_storage_permission_values()`, `test_sync_status_values()`

- `TestStorageItem`


  Tests for the StorageItem class.

  Methods: `test_init_with_required_fields()`, `test_init_with_all_fields()`, `test_to_dict()`, `test_from_dict()`

- `TestSyncConflict`


  Tests for the SyncConflict class.

  Methods: `test_init()`

- `TestSyncProgress`


  Tests for the SyncProgress class.

  Methods: `test_init_with_required_fields()`, `test_init_with_all_fields()`, `test_completion_percentage()`

- `TestStorageProviderInterface`


  Tests for the StorageProviderInterface.

  Methods: `test_interface_registration()`

- `TestSynchronizationInterface`


  Tests for the SynchronizationInterface.

  Methods: `test_interface_registration()`

- `TestStorageQuotaInterface`


  Tests for the StorageQuotaInterface.

  Methods: `test_interface_registration()`

- `TestStoragePermissionInterface`


  Tests for the StoragePermissionInterface.

  Methods: `test_interface_registration()`

- `TestFileStreamingInterface`


  Tests for the FileStreamingInterface.

  Methods: `test_interface_registration()`



### integrations\interfaces\storage_interface.py

**Description:**

Storage interface contracts for the AeroLearn AI system.

This module defines the interfaces for storage systems, including local and cloud
storage providers, synchronization mechanisms, and file operations.

**Classes:**

- `StorageScope`
 (inherits from: Enum)


  Defines the scope/visibility of stored data.

- `StoragePermission`
 (inherits from: Enum)


  Permission levels for stored items.

- `SyncStatus`
 (inherits from: Enum)


  Synchronization status for stored items.

- `StorageItem`


  Represents a storage item (file or folder) with metadata.

  Methods: `__init__()`, `to_dict()`, `from_dict()`

- `SyncConflict`


  Represents a synchronization conflict between local and remote versions.

  Methods: `__init__()`

- `SyncProgress`


  Represents the progress of a synchronization operation.

  Methods: `__init__()`, `completion_percentage()`

- `StorageProviderInterface`
 (inherits from: BaseInterface)


  Interface for components that provide storage capabilities.

- `SynchronizationInterface`
 (inherits from: BaseInterface)


  Interface for components that synchronize content between storage providers.

- `StorageQuotaInterface`
 (inherits from: BaseInterface)


  Interface for components that manage storage quotas.

- `StoragePermissionInterface`
 (inherits from: BaseInterface)


  Interface for components that manage storage permissions.

- `FileStreamingInterface`
 (inherits from: BaseInterface)


  Interface for components that provide file streaming capabilities.



### tests\integration\interfaces\test_base_interface.py

**Description:**

Unit tests for the base interface contracts.

This module tests the functionality of the BaseInterface class and related
interface registration and validation mechanisms.

**Classes:**

- `TestInterfaceVersion`


  Tests for the InterfaceVersion class.

  Methods: `test_init()`, `test_str_representation()`, `test_from_string_valid()`, `test_from_string_invalid()`, `test_is_compatible_with()`

- `TestMethodSignature`


  Tests for the MethodSignature class.

  Methods: `test_capture_signature()`, `test_validate_implementation_valid()`, `test_validate_implementation_invalid_return()`, `test_validate_implementation_missing_param()`, `test_validate_implementation_invalid_param_type()`, ... (2 more)

- `TestBaseInterface`


  Tests for the BaseInterface class.

  Methods: `setup_method()`, `test_register_interface()`, `test_register_interface_no_name()`, `test_register_interface_duplicate_compatible()`, `test_register_interface_duplicate_incompatible()`, ... (3 more)

- `TestInterfaceImplementation`


  Tests for the InterfaceImplementation decorator.

  Methods: `setup_method()`, `test_valid_implementation()`, `test_invalid_implementation_missing_method()`, `test_invalid_implementation_wrong_signature()`, `test_implementation_with_component()`

- `TestRegisterAllInterfaces`


  Tests for the register_all_interfaces function.

  Methods: `setup_method()`, `test_register_all_interfaces()`



### tests\integration\interfaces\test_content_interface.py

**Description:**

Unit tests for the content interface contracts.

This module tests the functionality of the content-related interfaces like
ContentProviderInterface, ContentSearchInterface, and others.

**Classes:**

- `TestContentEnums`


  Tests for content-related enumerations.

  Methods: `test_content_type_values()`, `test_content_format_values()`

- `TestContentMetadata`


  Tests for the ContentMetadata class.

  Methods: `test_init_with_required_fields()`, `test_init_with_all_fields()`, `test_dict_functionality()`

- `TestContentReference`


  Tests for the ContentReference class.

  Methods: `test_init_with_required_fields()`, `test_init_with_all_fields()`

- `TestContentSearchResult`


  Tests for the ContentSearchResult class.

  Methods: `test_init_with_required_fields()`, `test_init_with_all_fields()`

- `TestContentProviderInterface`


  Tests for the ContentProviderInterface.

  Methods: `test_interface_registration()`

- `TestContentSearchInterface`


  Tests for the ContentSearchInterface.

  Methods: `test_interface_registration()`

- `TestContentIndexerInterface`


  Tests for the ContentIndexerInterface.

  Methods: `test_interface_registration()`

- `TestContentProcessorInterface`


  Tests for the ContentProcessorInterface.

  Methods: `test_interface_registration()`

- `TestContentAnalyzerInterface`


  Tests for the ContentAnalyzerInterface.

  Methods: `test_interface_registration()`



### integrations\interfaces\content_interface.py

**Description:**

Content interface contracts for the AeroLearn AI system.

This module defines the interfaces for content management, including content
providers, content retrieval, and content processing components.

**Classes:**

- `ContentType`
 (inherits from: Enum)


  Enumeration of supported content types.

- `ContentFormat`
 (inherits from: Enum)


  Enumeration of specific content formats.

- `ContentMetadata`
 (inherits from: dict)


  Class for content metadata with standard fields and custom properties.

  Methods: `__init__()`

- `ContentReference`


  Reference to content that can be resolved by content providers.

  Methods: `__init__()`

- `ContentSearchResult`


  Result from a content search operation.

  Methods: `__init__()`

- `ContentProviderInterface`
 (inherits from: BaseInterface)


  Interface for components that provide access to content.

- `ContentSearchInterface`
 (inherits from: BaseInterface)


  Interface for components that provide content search capabilities.

- `ContentIndexerInterface`
 (inherits from: BaseInterface)


  Interface for components that index content for search.

- `ContentProcessorInterface`
 (inherits from: BaseInterface)


  Interface for components that process and transform content.

- `ContentAnalyzerInterface`
 (inherits from: BaseInterface)


  Interface for components that analyze content for insights.



### app\core\api\api_client.py

**Classes:**

- `APIClientError`
 (inherits from: Exception)


  Base exception for API client errors.

- `RateLimitExceeded`
 (inherits from: APIClientError)


  Raised when API rate limits are exceeded.

- `APIClient`


  Abstract base API client.

  Methods: `__init__()`, `authenticate()`, `rate_limited()`, `get_cache()`, `set_cache()`, ... (3 more)

- `DeepSeekAPIError`
 (inherits from: APIClientError)


- `DeepSeekClient`
 (inherits from: APIClient)


  Concrete API client for DeepSeek services.

  Methods: `__init__()`, `authenticate()`, `_do_request()`

- `GoogleDriveAPIError`
 (inherits from: APIClientError)


- `GoogleDriveClient`
 (inherits from: APIClient)


  Concrete API client for Google Drive services.

  Methods: `__init__()`, `authenticate()`, `_do_request()`



### app\models\content.py

**Description:**

Content model for AeroLearn AI (Topic, Module, Lesson, Quiz).

Location: app/models/content.py
Depends on: app/core/db/schema.py, integrations/events/event_bus.py

Handles Topic, Module, Lesson, Quiz logic; validation, serialization, and event integration.

**Classes:**

- `TopicModel`


  Methods: `__init__()`, `id()`, `serialize()`, `validate()`

- `ModuleModel`


  Methods: `__init__()`, `id()`, `serialize()`, `validate()`

- `LessonModel`


  Methods: `__init__()`, `id()`, `serialize()`, `validate()`

- `QuizModel`


  Methods: `__init__()`, `id()`, `serialize()`, `validate()`

- `QuestionModel`


  Methods: `__init__()`, `id()`, `serialize()`, `validate()`



### app\core\auth\authorization.py

**Classes:**

- `Permission`


  Represents a single permission string, such as 'content.edit' or 'user.manage'.

  Methods: `__init__()`, `__str__()`, `__eq__()`, `__hash__()`

- `Role`


  Represents a user role (e.g., student, professor, admin), with a set of permissions.

  Methods: `__init__()`, `all_permissions()`, `add_permission()`, `add_parent()`

- `UserPermissions`


  Assigns roles and direct permissions to users (by user_id).

  Methods: `__init__()`, `assign_role()`, `remove_role()`, `assign_permission()`, `remove_permission()`, ... (3 more)

- `PermissionError`
 (inherits from: Exception)


**Functions:**

- `require_permission(permission)`

  Decorator for functions/methods to enforce the required permission.



### integrations\registry\interface_registry.py

**Description:**

Interface registry for the AeroLearn AI system.

This module provides a registry for component interfaces, ensuring components
properly implement required interfaces and allowing for interface discovery.

**Classes:**

- `InterfaceDefinitionError`
 (inherits from: Exception)


  Exception raised when an interface is improperly defined.

- `InterfaceImplementationError`
 (inherits from: Exception)


  Exception raised when an interface is improperly implemented.

- `Interface`


  Base class for all interfaces in the system.

  Methods: `get_interface_name()`, `get_interface_version()`, `get_required_methods()`, `validate_implementation()`

- `InterfaceRegisteredEvent`
 (inherits from: Event)


  Event fired when an interface is registered.

  Methods: `__init__()`

- `InterfaceRegistry`


  Registry for interfaces in the system.

  Methods: `__new__()`, `__init__()`, `register_interface()`, `get_interface()`, `get_interface_version()`, ... (4 more)

**Functions:**

- `implements(interface_cls)`

  Decorator to mark a class as implementing an interface.



### tests\integration\component_harness.py

**Description:**

Integration Test Harness, Mock Component System, and Event Capture Utility
Location: tests/integration/component_harness.py

This module provides the foundational tools required to do component-based integration testing in AeroLearn AI.

**Classes:**

- `ComponentTestHarness`


  Generic test harness for initializing, managing, and verifying system component behavior in integration tests.

  Methods: `__init__()`, `register_component()`, `init_all()`, `start_all()`, `stop_all()`, ... (1 more)

- `MockComponent`


  Example mock component for use in harness-based tests.

  Methods: `__init__()`, `init()`, `start()`, `stop()`, `handle_event()`

- `EventCaptureUtility`


  Utility for subscribing to global events (such as via event bus)

  Methods: `__init__()`, `subscribe()`, `unsubscribe()`, `clear()`, `get_events()`, ... (1 more)



### app\ui\common\component_base.py

**Classes:**

- `BaseComponent`


  Base class for all UI components.

  Methods: `__init__()`, `version()`, `status()`, `on_init()`, `on_start()`, ... (7 more)



### tests\integration\test_monitoring.py

**Description:**

Integration tests for the monitoring system.

This module tests the integration health, component status, and transaction logging
components to ensure they work together correctly.

**Classes:**

- `MockComponent`
 (inherits from: Component, HealthProvider, ComponentStatusProvider)


  Mock component for testing monitoring systems.

  Methods: `__init__()`, `get_health_metrics()`, `get_health_status()`, `set_health_status()`, `get_component_state()`, ... (2 more)

- `TestMonitoringSystem`
 (inherits from: unittest.TestCase)


  Test cases for the monitoring system components.

  Methods: `setUp()`, `test_health_metrics_collection()`, `test_health_status_changes()`, `test_overall_system_health()`, `test_component_status_tracking()`, ... (6 more)



### tests\integration\test_ui_integration.py

**Description:**

UI Component Integration Tests

These tests target integration between UI components and their data providers,
event bus interactions, and support for end-to-end and performance scenarios.

Assumptions:
- UI components expose load_content, update_data, and subscribe_to_events
- EventBus used for event-driven updates

**Classes:**

- `FakeContentProvider`


  Methods: `__init__()`, `get_content()`, `list_content()`

- `DummyUIComponent`


  Methods: `__init__()`, `load_content()`, `update_data()`, `subscribe_to_events()`

- `SimpleEventBus`


  Methods: `__init__()`, `publish()`, `on()`

**Functions:**

- `ui_integration_env()`

- `test_ui_loads_content_and_triggers_event(ui_integration_env)`

- `test_ui_update_triggers_event(ui_integration_env)`

- `test_end_to_end_ui_to_data_workflow(ui_integration_env)`

- `test_ui_event_handler_performance(ui_integration_env)`



### code_summarizer.py

**Description:**

CodeSummarizer: A tool to create concise summaries of Python codebases
for maintaining context in AI assistant conversations.

This script:
1. Scans a project directory for Python files
2. Extracts key information (imports, classes, functions, docstrings)
3. Creates a structured summary
4. Optionally enhances the summary using DeepSeek API

**Classes:**

- `Colors`


- `CodeSummarizer`


  Methods: `__init__()`, `scan_project()`, `_find_python_files()`, `_get_directory_structure()`, `_process_file()`, ... (11 more)

**Functions:**

- `main()`

  Main function that can be run both from command line and directly from an IDE.



### app\core\auth\authentication.py

**Classes:**

- `AuthEvent`
 (inherits from: Event)


  Event representing authentication-related changes (login, logout, failure).

  Methods: `__init__()`

- `AuthenticationProvider`
 (inherits from: ABC)


  Interface for authentication providers.

  Methods: `authenticate()`

- `LocalAuthenticationProvider`
 (inherits from: AuthenticationProvider)


  Simple authentication provider with in-memory user verification and event emission.

  Methods: `__init__()`, `authenticate()`, `logout()`



### integrations\registry\dependency_tracker.py

**Description:**

Dependency tracking for the AeroLearn AI component system.

This module provides utilities for tracking, validating, and visualizing
component dependencies and ensuring proper component initialization order.

**Classes:**

- `CircularDependencyError`
 (inherits from: Exception)


  Exception raised when a circular dependency is detected.

- `DependencyTracker`


  Utility for tracking and analyzing dependencies between components.

  Methods: `__init__()`, `declare_dependency()`, `has_dependency()`, `validate_dependencies()`, `detect_circular_dependencies()`, ... (6 more)



### app\core\db\local_cache.py

**Description:**

Local Cache System for AeroLearn AI
- Local cache storage using SQLite (for persistence and offline ops)
- Invalidation logic for expiration or manual/integrity-based removes
- Cache prioritization support for critical data
- Thread-safe design

**Classes:**

- `LocalCacheInvalidationPolicy`


  Handles cache invalidation policies (time-based, manual, integrity).

  Methods: `__init__()`, `is_expired()`

- `LocalCache`


  Local cache storage supporting offline operation and prioritization.

  Methods: `__new__()`, `__init__()`, `set()`, `get()`, `delete()`, ... (5 more)



### tests\integration\test_auth_integration.py

**Description:**

Authentication Integration Tests

These tests verify the integration between authentication, session management, event bus, 
and the permission/role system. They include E2E flows and event verification for multi-role scenarios.

Assumptions:
- Auth system exposes: authenticate_user, create_session, get_user_profile, logout_user
- EventBus is set up and events are fired for auth state changes
- User/role data is pre-populated or mocked as necessary

**Classes:**

- `DummyAuth`


  Methods: `authenticate_user()`, `create_session()`, `get_user_profile()`

- `FakeEventBus`


  Methods: `__init__()`, `publish()`, `clear()`

**Functions:**

- `event_bus()`

- `auth_system(event_bus)`

- `test_authenticate_multiple_roles(auth_system, event_bus)`

- `test_invalid_authentication_fires_event(auth_system, event_bus)`

- `test_session_created_on_auth(auth_system)`

- `test_logout_event_firing(auth_system, event_bus)`

- `test_user_profile_retrieval()`

- `test_auth_end_to_end_workflow(auth_system, event_bus)`

- `test_performance_multiple_auth(auth_system)`



### tests\integration\test_storage_integration.py

**Description:**

Storage System Integration Tests

These tests validate the storage layer's integration with local and cloud backends,
including end-to-end workflows and performance measurement.

Assumptions:
- Storage interface exposes: upload_file, download_file, delete_file, list_files
- There is a unified abstraction for local/cloud, selectable by config or function arg

**Classes:**

- `DummyLocalStorage`


  Methods: `upload_file()`, `download_file()`, `delete_file()`, `list_files()`

- `DummyCloudStorage`


  Methods: `upload_file()`, `download_file()`, `delete_file()`, `list_files()`

**Functions:**

- `reset_storage()`

- `storage_system(request)`

- `test_file_upload_and_download(storage_system)`

- `test_file_delete_and_list(storage_system)`

- `test_cross_backend_integrity()`

- `test_end_to_end_storage_workflow(storage_system)`

- `test_storage_performance_upload(storage_system)`



### app\core\db\sync_manager.py

**Description:**

SyncManager for AeroLearn AI
- Handles synchronization between local cache and remote persistence (or server)
- Implements conflict resolution (last-writer-wins for now, pluggable in future)
- Batch synchronization and detection of offline/online state

**Classes:**

- `RemoteSyncProvider`


  Simulated remote store (would be replaced with actual DB/API client).

  Methods: `__init__()`, `pull()`, `push()`, `get()`

- `SyncManager`


  Manage synchronization between the local cache and remote (cloud/server).

  Methods: `__init__()`, `go_offline()`, `go_online()`, `sync()`, `resolve_conflict()`, ... (2 more)



### app\ui\common\main_window.py

**Description:**

Main application window for AeroLearn AI.

Implements:
- Central widget layout with view-switching (navigation)
- Role-based navigation (hooked)
- Status bar showing integration health
- Window state persistence/restoration
- Theme and style management

Requires PyQt6 (or compatible PySide6).

**Classes:**

- `MainWindow`
 (inherits from: QMainWindow)


  Methods: `__init__()`, `add_example_views()`, `update_role_navigation()`, `update_integration_health()`, `closeEvent()`, ... (5 more)



### app\core\auth\user_profile.py

**Classes:**

- `UserProfile`


  Represents the user's profile and identity attributes.

  Methods: `__init__()`, `to_dict()`, `from_dict()`



### app\core\auth\session.py

**Classes:**

- `Session`


  Represents an authenticated session.

  Methods: `__init__()`, `is_active()`, `touch()`

- `SessionManager`


  Handles session creation, validation, and expiration.

  Methods: `__init__()`, `create_session()`, `get_session()`, `invalidate_session()`, `cleanup_expired()`



### app\core\db\db_client.py

**Description:**

Database Client for AeroLearn AI
Handles SQLAlchemy engine and session management.
Edit DB_URL in schema.py as required for different environments.

**Classes:**

- `DBClient`


  Methods: `__new__()`, `_initialize()`, `get_session()`, `dispose()`, `session_scope()`, ... (6 more)



### tests\ui\test_component_architecture.py

**Classes:**

- `MockEvent`


  Methods: `__init__()`

- `MockEventBus`


  Methods: `__init__()`, `subscribe()`, `publish()`

**Functions:**

- `mock_event_bus()`

- `test_base_component_lifecycle_and_status(mock_event_bus)`

- `test_event_handler_registration_and_callback(mock_event_bus)`

- `test_registry_register_and_discover()`

- `test_registry_replace_component()`

- `test_dependency_injection_and_replacement()`

- `test_bulk_lifecycle_operations()`



### app\ui\common\test_component_architecture.py

**Classes:**

- `MockEvent`


  Methods: `__init__()`

- `MockEventBus`


  Methods: `__init__()`, `subscribe()`, `publish()`

**Functions:**

- `mock_event_bus()`

- `test_component_creation_and_lifecycle(mock_event_bus)`

- `test_component_event_handler_and_publish(mock_event_bus)`

- `test_component_registry_add_discover_replace()`

- `test_dependency_injection()`

- `test_lifecycle_bulk_operations()`



### app\ui\common\component_registry.py

**Classes:**

- `ComponentRegistry`


  Registry for UI components (Singleton).

  Methods: `__init__()`, `instance()`, `register_component()`, `register_component_class()`, `get_component()`, ... (5 more)



### tests\unit\test_credential_manager.py

**Classes:**

- `TestCredentialManager`
 (inherits from: unittest.TestCase)


  Methods: `setUp()`, `tearDown()`, `_cleanup_files()`, `test_store_and_retrieve_credential()`, `test_encryption_at_rest()`, ... (7 more)



### tests\integration\test_framework.py

**Description:**

Integration Test Framework for the AeroLearn Project
Location: tests/integration/test_framework.py

Includes:
- Interface compliance validation for components.
- Test scenario builder.
- Pytest-discoverable integration test functions.

**Classes:**

- `InterfaceComplianceTest`


  Validates that a component implements the required interface contract

  Methods: `__init__()`, `validate()`

- `TestScenarioBuilder`


  Builds and runs structured integration test scenarios.

  Methods: `__init__()`, `add_step()`, `run()`

**Functions:**

- `test_component_lifecycle()`

  Test: Component harness initializes, starts and tears down components.

- `test_event_capture_utility()`

  Test: EventCaptureUtility captures events via dummy event bus.

- `test_interface_compliance()`

  Test: InterfaceComplianceTest properly checks interface contract.

- `test_scenario_builder_runall()`

  Test: TestScenarioBuilder properly runs a sample scenario.



### app\utils\crypto.py

**Classes:**

- `CryptoUtils`


  Methods: `__init__()`, `generate_key()`, `generate_salt()`, `encrypt()`, `decrypt()`



### tests\unit\core\auth\test_authentication.py

**Classes:**

- `DummyEventBus`


  Methods: `__init__()`

- `TestAuthenticationProviderAndSession`
 (inherits from: unittest.TestCase)


  Methods: `setUp()`, `test_login_success_event_emission()`, `test_login_failure_event_emission()`, `test_session_creation_and_expiry()`, `test_logout_event_emission()`, ... (2 more)



### tests\integration\test_component_status.py

**Classes:**

- `DummyComponentState`
 (inherits from: Enum)


- `DummyProvider`
 (inherits from: ComponentStatusProvider)


  Methods: `__init__()`, `get_component_state()`, `get_status_details()`

**Functions:**

- `test_register_status_provider_and_update()`

- `test_state_change_records_history_and_severity()`

- `test_history_limit_and_filter()`

- `test_dependency_tracking_and_warnings()`

- `test_status_summary()`



### tests\integration\phase1_foundation_patch.py

**Functions:**

- `matches(self, event)`

  Determine whether the event matches this filter.

- `register_component(self, component_id, version)`

  Register a component by id and version only (test-friendly API).

- `register_component_instance(self, component)`

  Register a full Component instance (production API).

- `declare_dependency(self, dependent, requirements)`

  For testing: add a trivial mapping of dependencies from module to list.

- `has_dependency(self, dependent, requirement)`

  For testing: Check if dependent has declared requirement in stub.

- `interface_method(method)`

  Decorator for marking interface methods (test supports normal signature).

- `collect_metric(self, key, value)`

  Set a metric for test stubs.

- `get_metric(self, key)`

  Get metric for test stub.

- `__init__(self)`

- `set_status(self, component, status)`

- `get_status(self, component)`

- `__init__(self)`

- `log_transaction(self, source, target, type_, data)`

- `get_logs(self)`



### app\core\drive\sync_manager.py

**Description:**

File: sync_manager.py

Implements file synchronization between local cache and remote backend (e.g., Google Drive).
Handles conflict resolution, batch sync, and uses MetadataManager for change detection.

**Classes:**

- `ConflictType`


- `SyncConflict`
 (inherits from: Exception)


  Methods: `__init__()`

- `SyncManager`


  Methods: `__init__()`, `sync_file()`, `sync_all()`



### app\models\user.py

**Description:**

User model for AeroLearn AI.

Location: app/models/user.py
Depends on: app/core/db/schema.py, integrations/events/event_bus.py

Implements validation, event integration, and serialization.

**Classes:**

- `UserModel`


  Methods: `__init__()`, `id()`, `username()`, `email()`, `is_active()`, ... (2 more)



### app\models\course.py

**Description:**

Course model for AeroLearn AI.

Location: app/models/course.py
Depends on: app/core/db/schema.py, integrations/events/event_bus.py

Covers ORM integration, validation, serialization, and event emission.

**Classes:**

- `CourseModel`


  Methods: `__init__()`, `id()`, `title()`, `description()`, `modules()`, ... (2 more)



### app\core\auth\credential_manager.py

**Classes:**

- `CredentialManager`


  Methods: `__init__()`, `_load_or_generate_salt()`, `store_credential()`, `retrieve_credential()`, `_load_credentials()`, ... (1 more)



### app\core\api\deepseek_client.py

**Classes:**

- `DeepSeekAPIError`
 (inherits from: APIClientError)


- `DeepSeekClient`
 (inherits from: APIClient)


  Concrete API client for DeepSeek services.

  Methods: `__init__()`, `authenticate()`, `_do_request()`



### app\core\api\google_drive_client.py

**Classes:**

- `GoogleDriveAPIError`
 (inherits from: APIClientError)


- `GoogleDriveClient`
 (inherits from: APIClient)


  Concrete API client for Google Drive services.

  Methods: `__init__()`, `authenticate()`, `_do_request()`



### app\ui\common\content_preview.py

**Description:**

AeroLearn AI — Content Preview Component

This module provides the ContentPreview UI widget for displaying quick previews of content
selected in the browser. Handles text, images, PDF, video, and provides graceful fallback.

Features:
- Preview for multiple file/content types (text, image, PDF, etc)
- Dynamic selection of preview provider based on detected content type
- "Open with" actions allowing content launch in associated editors/viewers
- Drag-and-drop integration for UI/file sharing
- Preview loading errors are handled and surfaced to user via notification
- Notification system for preview/interaction feedback

**Classes:**

- `ContentPreview`
 (inherits from: QWidget)


  ContentPreview widget for dynamically showing the preview of content item/file.

  Methods: `__init__()`, `_setup_ui()`, `preview_content()`, `_show_text_preview()`, `_show_image_preview()`, ... (3 more)

**Functions:**

- `create_test_content_preview()`



### tests\unit\core\test_integration_health.py

**Description:**

Unit tests for the integration health monitoring system.

This module tests the health metric collection functionality including:
- Health metric registration
- Health metric updates
- Health metric querying
- Threshold monitoring

**Classes:**

- `TestHealthMonitoring`
 (inherits from: unittest.TestCase)


  Test suite for the health metric collection system.

  Methods: `setUp()`, `tearDown()`, `test_metric_registration()`, `test_metric_update()`, `test_counter_metric()`, ... (4 more)



### tests\ui\test_common_ui_controls.py

**Description:**

Test Suite for AeroLearn Common UI Controls (Task 4.3)

Covers:
- Form controls: validation, value change, error display
- Content browser: item listing, search, selection, drag event
- Content preview: file/type-based preview, error, notification
- Notification signal aggregation
- Simulated drag-and-drop (programmatic, for basic verification)
- Hooks for manual interaction

Requirements: PyQt5 or PySide2, minimal test assets (text/image files for preview step)

To run:
$ python tests/ui/test_common_ui_controls.py

Note: Because most UI verification requires human observation (and/or QtTest for full automation), this provides BOTH interactive UI and signal logging for confirmation.

**Classes:**

- `NotificationManager`
 (inherits from: QWidget)


  Simple notification logger for UI tests.

  Methods: `__init__()`, `notify()`

- `TestMainWindow`
 (inherits from: QWidget)


  Methods: `__init__()`, `submit_form()`

**Functions:**

- `main()`

- `test_pyqt5_installed()`

  Minimal test to show that the UI test suite is present and PyQt5 is importable.



### tests\examples\event_bus_example.py

**Description:**

Example usage of the event bus system.

This script demonstrates how to set up and use the event bus for
inter-component communication in the AeroLearn AI system.

**Classes:**

- `SystemComponent`
 (inherits from: EventSubscriber)


  Example system component that publishes and subscribes to events.

  Methods: `__init__()`

- `ContentManager`
 (inherits from: EventSubscriber)


  Example content manager component.

  Methods: `__init__()`

- `UserManager`
 (inherits from: EventSubscriber)


  Example user manager component.

  Methods: `__init__()`



### app\core\db\event_hooks.py

**Description:**

Event Bus hooks for publishing DB changes.
This uses real project models (User, Module, Lesson, etc).

**Classes:**

- `EventBus`


  Methods: `publish()`

**Functions:**

- `after_insert(mapper, connection, target)`

- `after_update(mapper, connection, target)`

- `after_delete(mapper, connection, target)`

- `install_event_hooks()`



### app\ui\common\navigation.py

**Description:**

Navigation management for AeroLearn AI main window.

Handles:
- Sidebar navigation UI
- View registration and switching
- Role-based navigation

Requires PyQt6 (or compatible PySide6).

**Classes:**

- `NavigationManager`


  Methods: `__init__()`, `set_stacked_widget()`, `register_view()`, `switch_to_role()`, `on_navigate()`



### tests\integration\test_component_registry.py

**Description:**

Revised Component Registry tests for Spyder - adapted to your implementation.

**Classes:**

- `TestComponentRegistry`


  Test wrapper for ComponentRegistry that disables event publishing.

  Methods: `__init__()`, `__getattr__()`, `restore()`

- `TestComponent`
 (inherits from: Component)


  Basic test component for registry tests.

  Methods: `__init__()`

**Functions:**

- `improved_register_component(component)`

  Register component directly with all necessary bookkeeping.



### tests\integration\test_health_metrics.py

**Classes:**

- `DummyHealthProvider`
 (inherits from: HealthProvider)


  Methods: `__init__()`, `get_health_metrics()`, `get_health_status()`

**Functions:**

- `test_register_and_collect_metrics()`

- `test_status_transition_on_metric_thresholds()`

- `test_collect_metrics_error_handling()`

- `test_aggregation_and_history()`

- `test_health_status_cache()`



### tests\ui\test_main_window.py

**Description:**

Test cases for MainWindow and Navigation system.

Uses pytest-qt or manual app launch for functional/smoke tests.

**Classes:**

- `DummyAuthService`


  Methods: `__init__()`, `get_current_role()`

**Functions:**

- `qt_app()`

  Provide QApplication only once per pytest session.

- `test_window_initialization(qt_app)`

- `test_navigation_role_switch(qt_app)`

- `test_status_bar_health(qt_app)`

- `test_theme_toggle(qt_app)`

- `test_window_state_persistence(qt_app)`



### app\core\drive\file_operations.py

**Description:**

File: file_operations.py

Implements file upload and download operations with support for local and remote (Google Drive) backends.
Uses events to notify about operations and errors. Metadata updates handled via metadata.py.

**Classes:**

- `FileOperationError`
 (inherits from: Exception)


  Custom exception type for file operations.

- `FileOperations`


  Methods: `__init__()`, `upload()`, `download()`, `delete()`



### app\ui\common\content_browser.py

**Description:**

AeroLearn AI - Content Browser Component

This module provides the ContentBrowser UI widget for displaying lists and trees of
content items (documents, lessons, media, etc.), supporting filtering, search, selection,
and drag-and-drop integration.

Intended for use with a Qt UI stack (PyQt/PySide), but logic is separable.

Features:
- List and tree mode for content
- Icons/thumbnails per type
- Text search/filter
- Selection events (single, multiple)
- Drag-and-drop support (signals/hooks)
- EventBus integration for content selection

Extensible to work with actual content models/data sources.

**Classes:**

- `ContentBrowser`
 (inherits from: QWidget)


  Widget to browse, search, and select content items.

  Methods: `__init__()`, `_setup_ui()`, `_populate()`, `_filter_content()`, `_item_selected()`, ... (1 more)

**Functions:**

- `create_test_content_browser()`



### app\models\assessment.py

**Description:**

Assessment model for AeroLearn AI.

Location: app/models/assessment.py
Depends on: app/core/db/schema.py, integrations/events/event_bus.py

Wraps ProgressRecord and assessment-related logic; provides validation, serialization, and event integration.

**Classes:**

- `AssessmentModel`


  Methods: `__init__()`, `id()`, `serialize()`, `validate()`



### tests\unit\core\auth\test_authorization.py

**Classes:**

- `TestAuthorizationAndPermissions`
 (inherits from: unittest.TestCase)


  Methods: `setUp()`, `test_permission_and_role_equality()`, `test_role_permission_inheritance()`, `test_user_role_assignment_and_permission_check()`, `test_dynamic_permission_assignment_and_removal()`, ... (2 more)



### tests\unit\core\api\test_api_clients.py

**Functions:**

- `test_deepseek_authentication()`

- `test_google_drive_authentication()`

- `test_deepseek_success_request_is_cached()`

- `test_google_drive_success_request_is_cached()`

- `test_deepseek_error_handling()`

- `test_google_drive_error_handling()`

- `test_deepseek_rate_limit()`

- `test_google_drive_rate_limit()`

- `test_rate_limit_resets_after_period()`

- `test_clearing_cache()`



### tests\integration\test_component_registry_async.py

**Description:**

Modified Component Registry tests for Spyder that patch event creation.

**Classes:**

- `TestComponent`
 (inherits from: Component)


  Test component for registry tests.

  Methods: `__init__()`

- `TestComponentRegistry`


  Test wrapper for ComponentRegistry that disables event publishing.

  Methods: `__init__()`, `__getattr__()`, `restore()`



### tests\integration\test_auth_event_bus.py

**Classes:**

- `AuthEventRecorder`
 (inherits from: EventSubscriber)


  Methods: `__init__()`

- `AsyncTestCase`
 (inherits from: unittest.IsolatedAsyncioTestCase)


- `TestAuthEventBusIntegration`
 (inherits from: AsyncTestCase)




### app\core\auth\permission_registry.py

**Functions:**

- `assign_user_role(user_id, role_name)`

- `assign_user_permission(user_id, permission)`

- `get_user_permissions(user_id)`



### app\core\db\migrations.py

**Description:**

Database migration and verification tools for AeroLearn AI.
Provides utilities for creating, dropping, and inspecting database tables.

**Functions:**

- `create_all_tables()`

  Create all tables defined in the Base metadata.

- `drop_all_tables()`

  Drop all tables defined in the Base metadata.

- `list_tables()`

  List all tables in the database.

- `verify_schema()`

  Verify that the database schema matches the expected schema.

- `get_table_details(table_name)`

  Get detailed information about a specific table.

- `run_migration(version)`

  Run migration to specified version or latest.



### app\core\drive\folder_structure.py

**Description:**

File: folder_structure.py

Defines folder structure management utilities for file storage system.
Able to create, verify, list, and traverse folders both locally and in external backends.

**Classes:**

- `FolderStructure`


  Methods: `__init__()`, `create_folder()`, `folder_exists()`, `list_folders()`, `get_folder_tree()`



### app\core\drive\metadata.py

**Description:**

File: metadata.py

Manages metadata for files and directories, including custom tags, versioning, and change detection.

**Classes:**

- `MetadataManager`


  Methods: `__init__()`, `generate_file_hash()`, `set_metadata()`, `get_metadata()`, `detect_change()`



### tests\unit\test_local_cache_and_sync.py

**Functions:**

- `reset_cache_singletons()`

- `test_cache_storage_and_retrieval(tmp_path)`

- `test_cache_expiry(tmp_path)`

- `test_cache_priority(tmp_path)`

- `test_cache_offline_mode_sync(tmp_path)`

- `test_sync_conflict_resolution(tmp_path)`

- `test_cache_invalidation(tmp_path)`

- `test_cache_persistence(tmp_path)`



### tests\integration\test_phase1_foundation.py

**Functions:**

- `test_event_filter_matching()`

- `test_component_registry_and_discovery()`

- `test_dependency_tracking_validation()`

- `test_base_interface_signature_validation()`

- `test_integration_health_collect()`

- `test_component_status_tracking()`

- `test_transaction_logger()`



### tests\unit\test_crypto.py

**Classes:**

- `TestCryptoUtils`
 (inherits from: unittest.TestCase)


  Methods: `setUp()`, `test_encryption_decryption()`



### tests\integration\test_event_bus.py

**Description:**

Integration test for the event bus system.

This module tests the event bus functionality to ensure events are correctly
published, subscribers receive the correct events, filters work, and concurrent/event thread safety is maintained.

**Classes:**

- `TestEventSubscriber`
 (inherits from: EventSubscriber)


  Test subscriber that records received events for verification.

  Methods: `__init__()`, `reset()`



### tests\integration\test_component_registry_Simple.py

**Description:**

Simplified Spyder-compatible tests for the Component Registry system without events.

**Classes:**

- `TestComponent`
 (inherits from: Component)


  Test component for registry tests.

  Methods: `__init__()`

**Functions:**

- `safe_call(obj, primary_method, fallback_method)`

  Call primary_method if it exists, otherwise try fallback_method



### tests\integration\test_db_integration.py

**Description:**

Tests for AeroLearn DB client, schema, migrations, and event hooks.
Run as:
    python -m pytest tests/integration/test_db_integration.py

**Functions:**

- `reset_db()`

- `test_schema_and_migration()`

- `test_user_module_lesson_crud()`

- `test_relationships_and_queries()`

- `test_event_hooks()`



### untitled3.py

**Functions:**

- `create_directory(path)`

  Create directory if it doesn't exist.

- `create_file(path, content)`

  Create file with given content.

- `create_init_file(path)`

  Create a Python __init__.py file.

- `generate_project_structure()`



### tests\models\test_models.py

**Description:**

Basic tests for models created in Task 3.2.

Location: tests/models/test_models.py

Covers:
- Creation, validation, and serialization for User, Course, Content, Assessment models.
- Relationship checks.
- Event bus integration stubs (mocked, as real event bus may need async setup).

NOTE: This is a minimal, demonstration-level test suite. Extend as needed for CI or deeper coverage.

**Functions:**

- `test_user_model_creation_and_validation()`

- `test_course_model_and_relationships()`

- `test_content_models()`

- `test_assessment_model()`



### app\core\db\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### app\core\db\db_events.py

**Description:**

Database Event Hooks for Event Bus Integration (Task 3.1)
---------------------------------------------------------

This module connects SQLAlchemy ORM events (insert/update/delete) for tracked models 
to the AeroLearn AI event system. 

- Hooks are registered for all mapped models in app.core.db.schema.
- On DB entity changes, a content.event (CREATED, UPDATED, DELETED) is published to the EventBus.
- Each event includes model, PK, and change data in the payload.

Place this file at: `app/core/db/db_events.py`

To activate event publishing, import this module after SQLAlchemy models are loaded (e.g., at app startup):

    from app.core.db import db_events

Requires: event bus to be started (`await EventBus().start()`).

**Functions:**

- `_get_primary_key(obj)`

  Helper to retrieve primary key(s) as a dict.

- `register_db_event_hooks()`

  Register all hooks for after_insert, after_update, after_delete



### app\main.py

**Description:**

Main entry point for the AeroLearn AI application.

**Functions:**

- `main()`

  Initialize and run the AeroLearn AI application.



### setup.py



### app\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Version: 0.1.0
Created: 2025-04-24

An AI-first education system for Aerospace Engineering that enhances teaching
and learning experiences through intelligent content management, personalized
learning assistance, and comprehensive analytics.



### app\core\auth\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### app\core\drive\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### app\core\ai\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### app\ui\common\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### app\ui\professor\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### app\ui\student\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### app\ui\admin\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### app\models\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### app\utils\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### app\config\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### integrations\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### integrations\interfaces\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### integrations\registry\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### integrations\events\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### integrations\monitoring\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-25

This module provides monitoring capabilities for integration health, component status,
and cross-component transaction logging.

The monitoring package helps track system health, detect integration failures,
and provide visualization data for system administrators.



### tests\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### tests\unit\core\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### tests\unit\ui\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### tests\unit\models\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### tests\integration\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### tests\ui\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### tests\fixtures\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### tools\integration_monitor\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### tools\project_management\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.



### scripts\__init__.py

**Description:**

AeroLearn AI - Aerospace Engineering Education Platform
Created: 2025-04-24

This module is part of the AeroLearn AI project.


