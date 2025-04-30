# Vector Database API

## Modules

---

### `vector_db_client.py`

#### `VectorDBClient`

| Method         | Signature                                              | Description                                   |
|----------------|-------------------------------------------------------|-----------------------------------------------|
| `__init__`     | (embedding_dim, backend='inmemory')                   | Create a new client for specified dimension   |
| `add_vector`   | (vector_id, vector, metadata=None)                    | Add a single vector and metadata              |
| `add_bulk`     | (embeddings, metadatas=None)                          | Add a batch of vectors/metadata               |
| `update_vector`| (vector_id, new_vector=None, new_metadata=None)       | Update vector or metadata by ID               |
| `delete_vector`| (vector_id)                                           | Delete entry by ID                            |
| `count`        | ()                                                    | Returns total stored vectors                  |
| `clear`        | ()                                                    | Clear all entries                             |
| `get_vector`   | (vector_id)                                           | Get vector and metadata by ID                 |
| `search`       | (query_vector, top_k=5, filter_fn=None)               | Find most similar vectors (with optional filter) |
| `save`         | (filepath)                                            | Persist DB to file                            |
| `load`         | (filepath)                                            | Load DB from file                             |

#### Example

```python
db = VectorDBClient(embedding_dim=4)
db.add_vector('id1', [1,0,0,1], {'course': 'math'})
results = db.search([1,0,0,1])
```

---

### `schema.py`

#### `VectorEntry`
- Model for a single DB entry (ID, vector, metadata).

#### `VectorDBIndexConfig`
- Configure index type & metric.

---

### `index_manager.py`

#### `VectorIndexManager`

| Method         | Signature                                              | Description                                   |
|----------------|-------------------------------------------------------|-----------------------------------------------|
| `__init__`     | (embedding_dim, backend='inmemory', config=None)      | New index manager for vectors                 |
| `build_index`  | (vectors, metadatas=None)                             | Add group of vectors to the index             |
| `search`       | (query_vector, top_k=10, filter_fn=None)              | Search index for most similar                 |
| `update_index` | (vector_id, new_vector=None, new_metadata=None)       | Update vector or metadata                     |
| `delete_from_index` | (vector_id)                                      | Remove item from index                        |
| `persist_index`| (filepath)                                            | Save index                                    |
| `load_index`   | (filepath)                                            | Load index                                    |
| `count`        | ()                                                    | Entry count                                   |

---

### `sync_manager.py`

#### `VectorDBSyncManager`

| Method         | Signature                                              | Description                                   |
|----------------|-------------------------------------------------------|-----------------------------------------------|
| `__init__`     | (index_manager, persist_path="...", interval_sec=60)  | Create sync manager with path & interval      |
| `start_auto_sync` | ()                                                 | Begin background persistence                  |
| `stop_auto_sync`  | ()                                                 | Stop background persistence                   |
| `persist`      | ()                                                    | Force save to disk                            |
| `restore`      | ()                                                    | Restore from disk if available                |

---

## Index Integration (AI Layer)

- See `/app/core/ai/vector_index.py` for usage in embedding/extraction workflows.