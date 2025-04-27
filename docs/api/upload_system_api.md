# AeroLearn AI Upload System API & Integration Documentation

## Table of Contents

- Overview
- ProfessorUploadWidget API
- Upload Processing Service API
- Format Validation API
- Batch Upload Controller API
- Content Type System API
- Metadata Management API
- Integration & Event Flow
- Extending the System
- Example Use Cases
- Error Handling & Troubleshooting

---

## Overview

The upload system enables educators to upload diverse material efficiently and integrates AI-compatible validation, rich metadata, and extensible content type detection. Components are designed to be tested, reused, and extended by third-party developers.

---

## ProfessorUploadWidget API

- Signals:
  - `fileUploadRequested(list[dict])`
  - `fileUploadProgress(str, int)`
  - `fileUploadCompleted(str, bool)`
- Usage: Connect in PyQt6 UI to initiate upload and track status.

## Upload Processing Service

- Methods: `enqueue(upload: UploadRequest)`, `stop()`
- Chunked uploads, retry features, async management (see `upload_service.py`)

## Format Validation API

- Registry of format validators for each content type.
- Extend via plugins and custom formats (see `format_validator.py`)
- Example:
```python
validators.validate('pdf', filepath, mimetype)
```

## Batch Upload Controller API

- Batch start/pause/resume/cancel
- Aggregated progress/event tracking
- Designed for integration with UIs and backend job queues

## Content Type System

- Register, detect, categorize content types (see `content_type_registry.py`)
- Used in validation/routing logic

## Metadata Management

- Schema definition per content type
- Editor API for dynamic UI and validation
- Inherits/merges for batch operations

## Integration and Event Flow

- Typical pipeline: UI → Validation → Metadata → Upload/Batch → Monitoring
- Signal-based and/or service-callback integration

## Extending the System

- Write new validator plugins and content types
- Custom uploader backends and batch controllers
- Example: CAD file plugins, Researcher-import workflows

## Example Use Cases

- Professor dragging a PDF, filling metadata, uploading to cloud, batch progress reported to dashboard
- Bulk upload of lecture videos with type/format detection and validation hooks

## Error Handling & Troubleshooting

- Validation fails: user notified via UI, logs captured for support
- Upload fails: retry policies, batch reports, escalation to admin

---

_Reference implementations and ready-to-integrate source code are available in the `/app/core/` and `/app/models/` directories. Unit and integration tests in `/tests/`._