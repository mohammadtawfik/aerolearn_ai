# File location: /tests/core/ai/test_vector_index.py

"""
Tests for high-level AeroLearn AI vector index interface.
Uses local index with fixed test dimension, NO dependency on production singleton.
"""

import numpy as np
from app.core.ai import vector_index as vi

def make_test_index():
    # Use tiny dim for test speed, isolation, and compatibility
    return vi.get_vector_index(embedding_dim=4)

def test_add_content_embedding_and_query():
    idx = make_test_index()
    idx.db.clear()

    v1 = np.array([0.2, 0.8, 0, 0])
    v2 = np.array([0.1, 0.1, 0.9, 0.1])
    vi.add_content_embedding(idx, "content1", v1, {"course": "physics"})
    vi.add_content_embedding(idx, "content2", v2, {"course": "math"})

    q = np.array([0.2, 0.9, 0, 0])
    results = vi.query_similar_content(idx, q, top_k=2)
    ids = [x[0] for x in results]
    assert "content1" in ids

def test_query_similar_content_with_metadata_filter():
    idx = make_test_index()
    idx.db.clear()
    vi.add_content_embedding(idx, "a", [1,0,0,0], {"subject": "math"})
    vi.add_content_embedding(idx, "b", [0,1,0,0], {"subject": "english"})
    q = [1,0,0,0]
    results = vi.query_similar_content(idx, q, top_k=2, filter_metadata={"subject": "math"})
    assert all(meta["subject"]=="math" for _,_,meta in results)
    assert len(results) >= 1
