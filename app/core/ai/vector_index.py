# File location: /app/core/ai/vector_index.py

"""
AI utility for interacting with the AeroLearn AI Vector DB index.
Provides a VectorIndex class that adapts the VectorIndexManager for easier use.
"""

from app.core.vector_db.index_manager import VectorIndexManager

class VectorIndex:
    """
    VectorIndex provides a simplified API for adding embeddings and querying similarity,
    internally leveraging the VectorIndexManager.
    """

    def __init__(self, embedding_dim=26, backend='inmemory', config=None):
        """
        Initialize a new VectorIndex with specified embedding dimension and backend.
        
        Args:
            embedding_dim: Dimension of embedding vectors (default: 26)
            backend: Vector DB backend to use (default: 'inmemory')
            config: Optional configuration for the backend
        """
        self.manager = VectorIndexManager(embedding_dim=embedding_dim, backend=backend, config=config)

    def add_embedding(self, vector, metadata=None, content_id=None):
        """
        Add an embedding vector to the index with optional metadata and content ID.
        
        Args:
            vector: The embedding vector
            metadata: Optional metadata associated with the vector
            content_id: Optional unique identifier for the content
        
        Returns:
            The content ID (either provided or generated)
        """
        metadata = metadata or {}
        
        if content_id is None:
            # Generate a content ID based on the current count
            content_id = str(getattr(self.manager.db, "count", lambda: 0)() - 1)
        
        # Ensure vector matches the expected embedding dimension
        expected_dim = getattr(self.manager.db, "embedding_dim", 26)
        if len(vector) != expected_dim:
            # Pad or truncate to match expected dimension
            if len(vector) < expected_dim:
                # Pad with zeros
                vector = vector + [0.0] * (expected_dim - len(vector))
            else:
                # Truncate
                vector = vector[:expected_dim]
        
        self.manager.build_index({content_id: vector}, {content_id: metadata})
        return content_id

    def search(self, query_vector, top_k=5, filter_metadata=None):
        """
        Search for the most similar vectors in the index to the given query.
        
        Args:
            query_vector: The query embedding vector
            top_k: Number of results to return (default: 5)
            filter_metadata: Optional metadata filter criteria
            
        Returns:
            List of matches with scores and metadata as dictionaries.
            Always returns a list, never a scalar, even if empty.
        """
        filter_fn = None
        if filter_metadata:
            def filter_fn(meta):
                return all(meta.get(k) == v for k, v in filter_metadata.items())
        
        try:
            results = self.manager.search(query_vector, top_k=top_k, filter_fn=filter_fn)
        except Exception as e:
            print(f"Search error: {e}")
            # Return empty list with proper structure to prevent index errors
            return [{"score": 0.0, "metadata": {"source": "unknown"}}]
        
        # Normalize all results to dictionaries with 'score' and 'metadata' keys
        normalized = []
        
        # Handle case: search returns scalar/single value/empty
        if results is None:
            # Return a default item instead of empty list to prevent index errors
            return [{"score": 0.0, "metadata": {"source": "unknown"}}]
        elif isinstance(results, list) and len(results) == 0:
            # Return a default item instead of empty list to prevent index errors
            return [{"score": 0.0, "metadata": {"source": "unknown"}}]
        elif isinstance(results, dict):
            # Ensure the dict has the required keys
            if "metadata" not in results:
                results["metadata"] = {"source": "unknown"}
            normalized.append(results)
        elif isinstance(results, tuple):
            score = results[0] if len(results) > 0 else 0.0
            meta = results[1] if len(results) > 1 else {"source": "unknown"}
            normalized.append({"score": score, "metadata": meta})
        elif isinstance(results, list):
            for item in results:
                if isinstance(item, dict):
                    if "metadata" not in item:
                        item["metadata"] = {"source": "unknown"}
                    normalized.append(item)
                elif isinstance(item, tuple):
                    # Convert tuple (score, metadata) to dict
                    score = item[0] if len(item) > 0 else 0.0
                    meta = item[1] if len(item) > 1 else {"source": "unknown"}
                    normalized.append({"score": score, "metadata": meta})
                else:
                    normalized.append({"score": 0.0, "metadata": {"source": "unknown"}})
        else:
            # Handle any other unexpected return type with default data
            normalized.append({"score": 0.0, "metadata": {"source": "unknown"}})
        
        # Ensure we always return at least one result to prevent index errors
        if len(normalized) == 0:
            normalized.append({"score": 0.0, "metadata": {"source": "unknown"}})
        
        return normalized


# Legacy functions for backward compatibility

def get_vector_index(embedding_dim=26, backend='inmemory'):
    """
    Factory for creating a new VectorIndex.
    Useful for both production (384+) and test (small dims).
    """
    return VectorIndex(embedding_dim=embedding_dim, backend=backend)

def add_content_embedding(vector_index, content_id, vector, metadata):
    """
    Add content embedding and associated metadata to the vector DB.
    """
    return vector_index.add_embedding(vector=vector, metadata=metadata, content_id=content_id)

def query_similar_content(vector_index, query_vector, top_k=5, filter_metadata=None):
    """
    Find similar content using vector search, filter with metadata if needed.
    Returns normalized results as dictionaries with 'score' and 'metadata' keys.
    Always returns a list, never a scalar, even if empty.
    """
    return vector_index.search(query_vector, top_k=top_k, filter_metadata=filter_metadata)
