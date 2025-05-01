# Search API Documentation

## Overview

The Search API provides a unified interface for performing hybrid keyword and semantic (embedding-based) search over AeroLearn AI content, supporting permission filtering, component-specific targeting, and customizable result ranking.

## Methods

### `/search`

#### **Parameters**
- `query` (string): The user's search query.
- `targets` (list of strings): List of content/component types to search (e.g., `["course", "lesson"]`).
- `user_id` (string): ID of user whose permissions/filtering should be applied.
- `limit` (int): Max results to return.
- `mode` (string): `"hybrid"` (default), `"semantic"`, or `"keyword"` (search strategy).
- `options` (dict): Advanced options (override scoring weights, result aggregation, etc.).

#### **Returns**
- A ranked, deduplicated list of matching content entries, each including:
  - `id`, `score`, `agg_score`, (optionally) `agg_keyword_score`, `agg_semantic_score`, and all referenced content fields.
  - `source`: `"semantic"`, `"keyword"`, or `"hybrid"`.

## Filtering Logic

- Permission filters may be specified as callbacks or inferred per user role/content.
- Permission pruning is applied before ranking/aggregation.
- Deduplication is by `id` across all backends.

## Customization

- Scoring weights may be passed per request (`options["scoring_weights"]`), e.g., `{"semantic": 0.8, "keyword": 0.2}`.
- Custom permission filter functions can be supplied at call time or bound to a searcher instance.

## Example Usage

```python
from app.core.ai.semantic_search import HybridSemanticSearch

# Set up semantic and keyword backends, and permission logic
searcher = HybridSemanticSearch(semantic_backend, keyword_backend, permission_checker, scoring_weights)

results = searcher.search(
    "deep learning",
    ["lesson", "course"], 
    context, 
    user_id="admin",
    limit=10,
    mode="hybrid"
)
```

## Implementation Location

- Core hybrid logic: `/app/core/ai/semantic_search.py`
- Semantic backend: `/app/core/search/semantic_backend.py`
- API handler/endpoint registration: (see `/app/api/search_api.py` if applicable)