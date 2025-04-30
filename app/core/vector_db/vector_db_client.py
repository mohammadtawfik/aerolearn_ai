# File location: /app/core/vector_db/vector_db_client.py

"""
Vector database client for AeroLearn AI.

Handles connection, insertion, retrieval, search, deletion, and schema operations for vector storage.
Abstraction allows plugging in different engines (e.g., FAISS, Milvus, Pinecone).
"""

import numpy as np

class VectorDBClient:
    def __init__(self, embedding_dim, backend='inmemory'):
        """
        Initialize vector DB client.
        :param embedding_dim: Dimension of vector embeddings
        :param backend: 'inmemory', 'faiss', 'milvus', etc. (demo uses in-memory)
        """
        self.embedding_dim = embedding_dim
        self.backend = backend
        self.vectors = {}   # {id: vector}
        self.metadata = {}  # {id: meta dict}

    def add_vector(self, vector_id, vector, metadata=None):
        if len(vector) != self.embedding_dim:
            raise ValueError("Vector dimension does not match embedding_dim")
        self.vectors[vector_id] = np.asarray(vector, dtype=np.float32)
        self.metadata[vector_id] = metadata or {}

    def add_bulk(self, embeddings, metadatas=None):
        """
        Add many vectors at once.
        embeddings: dict {id: vector}
        metadatas: dict {id: metadata}
        """
        for vector_id, vector in embeddings.items():
            self.add_vector(vector_id, vector, (metadatas or {}).get(vector_id, {}))

    def search(self, query_vector, top_k=5, filter_fn=None):
        """
        Returns: List[tuple(id, score, metadata)]
        filter_fn: Optional function to filter by metadata before scoring
        """
        query = np.asarray(query_vector, dtype=np.float32)
        results = []
        for vid, v in self.vectors.items():
            meta = self.metadata[vid]
            if filter_fn and not filter_fn(meta):
                continue
            score = np.dot(query, v) / (np.linalg.norm(query) * np.linalg.norm(v) + 1e-12)
            results.append((vid, score, meta))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def update_vector(self, vector_id, new_vector=None, new_metadata=None):
        if new_vector is not None:
            self.add_vector(vector_id, new_vector, self.metadata[vector_id])
        if new_metadata is not None:
            self.metadata[vector_id].update(new_metadata)

    def delete_vector(self, vector_id):
        self.vectors.pop(vector_id, None)
        self.metadata.pop(vector_id, None)

    def get_vector(self, vector_id):
        return self.vectors.get(vector_id), self.metadata.get(vector_id)

    def count(self):
        return len(self.vectors)

    def clear(self):
        self.vectors.clear()
        self.metadata.clear()

    def save(self, filepath):
        import pickle
        with open(filepath, "wb") as f:
            pickle.dump((self.embedding_dim, self.vectors, self.metadata), f)

    def load(self, filepath):
        import pickle
        with open(filepath, "rb") as f:
            embedding_dim, vectors, metadata = pickle.load(f)
        assert embedding_dim == self.embedding_dim
        self.vectors = vectors
        self.metadata = metadata