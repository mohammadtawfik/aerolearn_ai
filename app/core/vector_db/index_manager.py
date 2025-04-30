# File location: /app/core/vector_db/index_manager.py

"""
Vector index management for AeroLearn AI.
Handles creation, rebuilding, update and optimization of vector indices for efficient search.
"""

from .vector_db_client import VectorDBClient

class VectorIndexManager:
    def __init__(self, embedding_dim, backend='inmemory', config=None):
        self.db = VectorDBClient(embedding_dim, backend=backend)
        self.config = config or {}

    def build_index(self, vectors, metadatas=None):
        # Bulk add for optimized indexing
        self.db.add_bulk(vectors, metadatas)

    def search(self, query_vector, top_k=10, filter_fn=None):
        # Delegate to DB client, allow for custom filter
        return self.db.search(query_vector, top_k=top_k, filter_fn=filter_fn)

    def update_index(self, vector_id, new_vector=None, new_metadata=None):
        self.db.update_vector(vector_id, new_vector, new_metadata)

    def delete_from_index(self, vector_id):
        self.db.delete_vector(vector_id)

    def persist_index(self, filepath):
        self.db.save(filepath)

    def load_index(self, filepath):
        self.db.load(filepath)

    def count(self):
        return self.db.count()