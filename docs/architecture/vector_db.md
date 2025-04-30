# AeroLearn AI Vector Database Architecture

## Overview

The vector database subsystem enables efficient storage, indexing, search, and management of high-dimensional embeddings for AI-powered content analysis (e.g., similarity search, recommendation). It is modular, supports multiple backends, and is designed for scalable and filterable vector search.

## Structure

```
/app/core/vector_db/
│
├── vector_db_client.py   # Backend-agnostic CRUD/search for vectors & metadata
├── schema.py             # Vector entry, index, and metadata schema definition
├── index_manager.py      # Index creation, management, update, and deletion
└── sync_manager.py       # Synchronization and persistence logic
```

Key integration points include `/app/core/ai/vector_index.py` (the AI utility interface) and the extraction/embedding modules.

## Core Components

### VectorDBClient

- Provides add, update, delete, search (with filter), bulk insert.
- Persists vectors/metadata via simple serialization (pickle, replaceable for DBs such as FAISS, Milvus).
- Metadata schema supports filtering and organization (e.g., by content type, source).

### Schema

- `VectorEntry`: Standardizes stored items (ID, vector, content type, etc).
- `VectorDBIndexConfig`: Encapsulates index settings (type, metric), so backends/experiments can be swapped easily.

### Index Management

- `VectorIndexManager`: Handles batch-building of indices, vector CRUD, and optimizes for search.
- Separation allows hot-swap of backend or algorithm with minimal integration rewiring.

### Synchronization

- `VectorDBSyncManager`: Handles periodic persistence of the in-memory index to disk (and can be extended for remote/federated sync).
- Ensures vector data durability between process restarts or scale-out scenarios.

## Search and Querying

- Core search operation: cosine similarity (dot product, L2 normalization).
- Support for metadata-based filtering, for domain-specific queries.

## Backends

- Default: In-memory (numpy).
- Can be upgraded for FAISS, Milvus, Pinecone, etc., via backend abstraction.

## Persistence

- Uses file-based serialization by default (configurable path).
- Sync manager automates persistence at configurable intervals and at shutdown.

## Extension Points

- Index and backend classes can be extended or swapped for production scale-out.
- Supports content type–aware partitioning and multi-tenant scenarios.

## Usage Example

```python
from app.core.vector_db.index_manager import VectorIndexManager

idx = VectorIndexManager(embedding_dim=384)
idx.build_index({'item1': [0.1]*384}, {'item1': {'meta': 'test'}})
results = idx.search([0.1]*384, top_k=5)
```

## See Also

- [API Reference: `/docs/api/vector_db_api.md`](./../api/vector_db_api.md)
- [AI Index Integration: `/app/core/ai/vector_index.py`](./../../app/core/ai/vector_index.py)