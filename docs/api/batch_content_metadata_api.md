# AeroLearn AI: Batch Upload, Content Type, and Metadata Systems

## Overview

This document provides:
- **API reference, usage instructions, and extension points** for Batch Upload, Content Type Registry, and Metadata Management.
- **Testing instructions** for both automated and manual integration.
- **Workflow diagrams and integration guidance**.

---

## 1. Batch Upload Controller API

- **enqueue_files(files: List[dict])**: Add multiple files to the batch.
- **start() / pause() / resume() / cancel()**: Control batch lifecycle.
- **get_progress_report()**: Aggregates and returns batch status.
- **validate_files(files: List[dict]) -> dict**: Returns validation summary for batch (supports plugin validators).
- **Events**: Emits progress and status changed signals (can be hooked in UI).

### Example
```python
controller = BatchUploadController()
controller.enqueue_files(files)
controller.start()
```

---

## 2. Content Type Registry API

- **register_detector(type: str, detector: Callable)**: Register rule/function for content type.
- **detect_type(filename: str) -> str**: Returns type for a file.
- **Plugin Support**: Call plugins’ `register` on the registry for extensibility.

### Multi-level Detection

Order: MIME > Extension > Content Inspection > AI.

---

## 3. Metadata Management System API

- **get_schema(type: str) -> dict**: Returns required/optional metadata fields for a type.
- **merge_metadata(base: dict, overrides: dict) -> dict**: Batch/folder-level inheritance.
- **index_metadata(items: List[dict])**: Create searchable metadata index.
- **search_metadata(query: dict) -> List[dict]**: Flexible searching/filtering.

### Dynamic Metadata Editor

Supports dynamic UI generation (see `/app/ui/common/`), field-level validation, batch operations.

---

## 4. Testing Instructions

- Run `pytest tests/integration/test_batch_content_metadata.py` for automated coverage.
    - **Covers:** batch controller events, aggregated progress, validation summary, registry plugins, metadata merge, search, and end-to-end integration.
- Add/extend test data in `tests/fixtures/` for more file types and metadata schemas.
- Manual verification: Use UI, batch upload, and metadata editor to test cross-component workflows.

---

## 5. Extension Points

- **Batch Controller**: Subclass and override progress aggregation, add new event hooks.
- **Content Type Registry**: Write plugins as per interface, auto-discoverable via entrypoint/convention.
- **Metadata Manager**: New schemas/fields per content type, support dynamic validation plugins.

---

## 6. Integration Workflow

```mermaid
flowchart LR
    A[User drops files / selects batch] --> B[Content Type Detection]
    B --> C[Format Validation / Batch Validator]
    C --> D[Metadata Editor & Inheritance]
    D --> E[Batch Upload Controller]
    E --> F[Progress & Status Reporting]
    F --> G[Storage/DB/Monitoring Events]
```

---

## 7. Troubleshooting & Known Issues

- **Validation Fails**: User is alerted; see logs in `/app/core/upload/`.
- **Unregistered Content Type**: Default/fallback logic applies; check plugin registration.
- **Metadata Mismatch**: Review schema in `/app/models/metadata_schema.py`.

---

## 8. References

- Source: `app/core/upload/batch_controller.py`, `app/models/content_type_registry.py`, `app/models/metadata_manager.py`
- Tests: `/tests/integration/test_batch_content_metadata.py`
- UI integration: `/app/ui/professor/upload_widget.py`, `/app/ui/common/`