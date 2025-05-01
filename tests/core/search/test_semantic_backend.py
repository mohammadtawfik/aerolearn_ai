"""
File: /tests/core/search/test_semantic_backend.py
Purpose: Unit tests for /app/core/search/semantic_backend.py

This file should be saved as /tests/core/search/test_semantic_backend.py according to the project structure.
"""

from app.core.search.semantic_backend import SemanticSearchBackend

def test_semantic_search_basic():
    backend = SemanticSearchBackend()
    context = [
        {'id': '10', 'title': 'Neural Net', 'content': 'Deep AI'}, 
        {'id': '20', 'title': 'Robotics', 'content': 'Sensors and actuators'},
    ]
    results = backend.search('neural', context=context)
    assert results and results[0]['id'] == '10'

def test_semantic_score_nonzero():
    backend = SemanticSearchBackend()
    item = {'id': '100', 'title': 'Machine', 'content': 'Learning stuff'}
    res = backend.search('machine learning', context=[item])
    assert res[0]['score'] > 0

def test_semantic_search_empty_context():
    backend = SemanticSearchBackend()
    assert backend.search('test', context=[]) == []