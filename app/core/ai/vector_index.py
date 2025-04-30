# File location: /app/core/ai/vector_index.py

"""
AI utility for interacting with the AeroLearn AI Vector DB index.
Provides functions to instantiate and use vector managers at any embedding dimension (testable and modular).
"""

from app.core.vector_db.index_manager import VectorIndexManager

def get_vector_index(embedding_dim=384, backend='inmemory'):
    """
    Factory for creating a new VectorIndexManager.
    Useful for both production (384+) and test (small dims).
    """
    return VectorIndexManager(embedding_dim=embedding_dim, backend=backend)

def add_content_embedding(vector_index, content_id, vector, metadata):
    """
    Add content embedding and associated metadata to the vector DB.
    """
    vector_index.build_index({content_id: vector}, {content_id: metadata})

def query_similar_content(vector_index, query_vector, top_k=5, filter_metadata=None):
    """
    Find similar content using vector search, filter with metadata if needed.
    """
    filter_fn = None
    if filter_metadata:
        def filter_fn(meta):
            return all(meta.get(k) == v for k, v in filter_metadata.items())
    return vector_index.search(query_vector, top_k=top_k, filter_fn=filter_fn)
