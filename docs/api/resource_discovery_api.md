# External Resource Discovery API

## Overview

The External Resource Discovery module enables AI-powered retrieval, scoring, and integration of third-party resources (videos, articles, datasets, etc.) with course content.

## Main API Entry Point

**Class:** `ResourceDiscovery`  
**Location:** `/app/core/ai/resource_discovery.py`

### Methods

- `discover_resources(course, max_results=10)`  
  Returns a sorted list of `(resource, score)` tuples relevant to the provided course.
- `integrate_resources(course)`  
  Attaches top resources to the course's metadata or recommendation field.

## Provider Plugin Architecture

- **Base Class:** `BaseResourceProvider` in `/app/core/external_resources/providers.py`
- **Default Provider:** DeepSeek (`DeepSeekResourceProvider`)
- Providers handle API/network/config errors gracefully

## Quality & Scoring

- Scoring logic in `/app/core/external_resources/scoring.py`
- Default scoring combines:
  - Text similarity between course content and resource
  - Completeness bonus for comprehensive resources
  - Custom criteria specific to resource types

## Example Usage

```python
from app.core.ai.resource_discovery import ResourceDiscovery

# Initialize the discovery engine
discovery = ResourceDiscovery()

# Get scored resources
resources = discovery.discover_resources(course, max_results=10)
# resources is a list of (resource, score) tuples

# Automatically integrate resources with course
discovery.integrate_resources(course)
```

## Extending/Customizing

- **Add a new provider:**
  1. Subclass `BaseResourceProvider` in `providers.py`
  2. Implement required methods
  3. Register in `BaseResourceProvider.load_default_providers()`

- **Custom scoring:**
  - Enhance or replace scoring logic in `scoring.py`
  - Add new scoring criteria for specific resource types

## Error Handling

- If no API key or network is available, the orchestrator will proceed without crashing
- Unavailable providers are skipped gracefully
- Errors are logged for debugging purposes

## See Also

- Check implementation details in the source code
- Refer to provider-specific documentation for API key setup
