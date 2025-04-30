# File location: /app/core/vector_db/schema.py

"""
Vector DB schema definitions for AeroLearn AI.
Defines standard metadata fields, vector index configuration, and filter rules.
"""

class VectorEntry:
    def __init__(self, vector_id, vector, content_type, source, tags=None, extra=None):
        self.vector_id = vector_id
        self.vector = vector
        self.content_type = content_type
        self.source = source
        self.tags = tags or []
        self.extra = extra or {}

    def to_dict(self):
        return {
            "vector_id": self.vector_id,
            "vector": self.vector,
            "content_type": self.content_type,
            "source": self.source,
            "tags": self.tags,
            **self.extra
        }

class VectorDBIndexConfig:
    def __init__(self, index_type="cosine", nlist=100, metric="cosine"):
        self.index_type = index_type  # e.g., "flat" for CPU, "IVF" for FAISS, "HNSW" for scalable
        self.nlist = nlist
        self.metric = metric

    def as_dict(self):
        return {
            "index_type": self.index_type,
            "nlist": self.nlist,
            "metric": self.metric
        }