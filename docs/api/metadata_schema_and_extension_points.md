# Metadata Schema and Extension Points

## Overview

The AeroLearn Metadata System provides a structured, extensible way to attach, validate, and search metadata for files, folders, and content items.

## Base Schema

| Field        | Type    | Required | Description                   |
|--------------|---------|----------|-------------------------------|
| title        | str     | Yes      | User-facing title             |
| author       | str     | Yes      | Creator/uploader              |
| description  | str     | No       | Free-form description         |
| tags         | list    | No       | List of tags                  |
| created_at   | str     | Yes      | ISO8601 Date String           |
| updated_at   | str     | No       | ISO8601 Date String           |

## Extension Mechanism

Metadata schemas can be extended by:
- Adding new `MetadataField` objects to a schema.
- Subclassing schema classes (e.g. for domain-specific needs, like videos, CAD files).

## Example Extension

Add a "format" and "duration_seconds" to create a video content metadata schema, as shown in `app/core/drive/metadata_schema.py`.

## Inheritance

*Metadata inheritance* allows batch and folder-level defaults to propagate, with per-item overrides. See `metadata_inheritance.py`.

## Editor and Search

- A Python-based CLI metadata editor helps create valid, structured metadata.
- Metadata is persisted via a simple file-based store; enable search/filtering by any field.

## Tests

Core tests validate correct persistence and retrieval. See `tests/test_metadata_store.py`.

---

## Extension Points

- Add new fields/types by extending `MetadataField`.
- Implement custom validation via the `validator` parameter.
- Adapt to a DB/ORM layer by swapping `MetadataStore`.