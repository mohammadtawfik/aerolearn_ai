# File location: /tests/core/vector_db/test_vector_db.py

"""
Unit and integration tests for VectorDBClient and VectorIndexManager in AeroLearn AI.
Covers vector CRUD, index building, search, update, delete, filter, and persistence.
"""

import os
import numpy as np
import tempfile
import shutil

from app.core.vector_db.vector_db_client import VectorDBClient
from app.core.vector_db.index_manager import VectorIndexManager

def test_vector_db_crud_operations():
    db = VectorDBClient(embedding_dim=4)
    db.add_vector('vec1', [1.0, 0.0, 0.0, 0.0], {'type': 'test'})
    db.add_vector('vec2', [0.0, 1.0, 0.0, 0.0], {'type': 'test2'})

    # Retrieve vector and metadata
    vector, meta = db.get_vector('vec1')
    assert np.allclose(vector, np.array([1.0, 0.0, 0.0, 0.0]))
    assert meta['type'] == 'test'

    # Update vector/metadata
    db.update_vector('vec1', [1.0, 1.0, 0.0, 0.0], {'status': 'updated'})
    v, m = db.get_vector('vec1')
    assert np.allclose(v, [1.0, 1.0, 0.0, 0.0])
    assert m['status'] == 'updated'

    # Delete
    db.delete_vector('vec2')
    assert db.get_vector('vec2') == (None, None)

def test_vector_db_bulk_and_search():
    dim = 3
    db = VectorDBClient(embedding_dim=dim)
    vectors = {
        f"vec{i}": np.random.rand(dim) for i in range(10)
    }
    db.add_bulk(vectors, {f"vec{i}": {"tag": "bulk"} for i in range(10)})

    query = np.random.rand(dim)
    results = db.search(query, top_k=5)
    assert len(results) == 5
    # Scores are float, id is correct, metadata present
    ids = {r[0] for r in results}
    assert all(i in db.vectors for i in ids)

def test_vector_db_search_with_filter():
    dim = 2
    db = VectorDBClient(embedding_dim=dim)
    db.add_vector('v1', [1.0, 0.0], {"course": "math"})
    db.add_vector('v2', [0.0, 1.0], {"course": "science"})
    db.add_vector('v3', [1.0, 1.0], {"course": "math"})

    def filter_math(meta):
        return meta.get("course") == "math"

    results = db.search([1.0, 0.0], top_k=10, filter_fn=filter_math)
    ids = [x[0] for x in results]
    assert set(ids).issubset({'v1', 'v3'})
    assert len(ids) >= 1

def test_vector_db_persistence_and_load(tmp_path):
    dim = 3
    db = VectorDBClient(embedding_dim=dim)
    db.add_vector('persist1', np.ones(dim), {'info': 'save'})
    file_path = tmp_path / "vector_db_test.pkl"
    db.save(str(file_path))

    new_db = VectorDBClient(embedding_dim=dim)
    new_db.load(str(file_path))
    v, m = new_db.get_vector('persist1')
    assert np.allclose(v, np.ones(dim))
    assert m['info'] == 'save'

def test_index_manager_build_and_search():
    dim = 4
    idx = VectorIndexManager(embedding_dim=dim)
    vectors = {f"id{i}": np.random.rand(dim) for i in range(8)}
    metadatas = {f"id{i}": {'type': 'idx'} for i in range(8)}
    idx.build_index(vectors, metadatas)
    q = np.random.rand(dim)
    results = idx.search(q, top_k=3)
    assert len(results) == 3

def test_index_manager_update_and_delete():
    idx = VectorIndexManager(embedding_dim=2)
    idx.build_index({'id1':[0.1,0.9]}, {'id1':{'tag':'x'}})
    idx.update_index('id1', [0.7,0.7], {'update':'yes'})
    v = idx.db.vectors['id1']
    assert np.allclose(v, [0.7,0.7])
    idx.delete_from_index('id1')
    assert 'id1' not in idx.db.vectors

def test_index_manager_persist_and_load(tmp_path):
    idx = VectorIndexManager(embedding_dim=2)
    idx.build_index({'vec': [1.1, 1.2]}, {'vec': {'user': 'test'}})
    file = tmp_path / "index_manager_test.pkl"
    idx.persist_index(str(file))

    new_idx = VectorIndexManager(embedding_dim=2)
    new_idx.load_index(str(file))
    assert new_idx.count() == 1
    v, m = new_idx.db.get_vector('vec')
    assert np.allclose(v, [1.1,1.2])
    assert m['user'] == 'test'