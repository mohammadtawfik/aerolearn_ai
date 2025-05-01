"""
File: /tests/core/ai/test_semantic_search.py
Purpose: Unit tests for /app/core/ai/semantic_search.py

This file should be saved as /tests/core/ai/test_semantic_search.py according to the project structure.
"""

import pytest
from app.core.ai.semantic_search import HybridSemanticSearch

class DummyKeywordBackend:
    def search(self, query, context=None, limit=50):
        res = []
        q = query.lower()
        for item in context:
            if q in (item.get('title','').lower() + ' ' + item.get('content','').lower()):
                res.append({
                    'id': item['id'],
                    'score': 0.8,
                    'source': 'keyword',
                    'data': item
                })
        return res[:limit]

class DummySemanticBackend:
    def search(self, query, context=None, limit=50):
        res = []
        q = query.lower()
        for item in context:
            # Simple simulation of semantic matching
            if 'neural' in q and 'neural' in item.get('content','').lower():
                res.append({
                    'id': item['id'],
                    'score': 0.9,
                    'source': 'semantic',
                    'data': item
                })
            elif 'python' in q and 'python' in item.get('content','').lower():
                res.append({
                    'id': item['id'],
                    'score': 0.85,
                    'source': 'semantic',
                    'data': item
                })
        return res[:limit]

class DummyUser:
    def __init__(self, permissions):
        self.permissions = permissions

@pytest.fixture
def simple_context():
    return [
        {'id': 'doc1', 'title': 'Neural Networks', 'content': 'Deep learning with neural nets', 'permissions': ['ai.read', 'course.view']},
        {'id': 'doc2', 'title': 'Physics Basics', 'content': 'Newton laws and motion', 'permissions': ['course.view']},
        {'id': 'doc3', 'title': 'Python Guide', 'content': 'How to code with python', 'permissions': ['coding.read']},
    ]

def test_keyword_only(simple_context):
    searcher = HybridSemanticSearch(
        keyword_backend=DummyKeywordBackend(),
        semantic_backend=DummySemanticBackend()
    )
    user = DummyUser(['ai.read', 'course.view'])
    
    def permission_filter(user_id, item):
        return any(perm in user.permissions for perm in item.get('permissions', []))
    
    results = searcher.search('Neural', ['document'], simple_context, 
                             mode="keyword", 
                             permission_filter=permission_filter)
    
    assert any(r['id'] == 'doc1' for r in results)
    assert all(r['source'] == 'keyword' for r in results)

def test_semantic_only(simple_context):
    searcher = HybridSemanticSearch(
        keyword_backend=DummyKeywordBackend(),
        semantic_backend=DummySemanticBackend()
    )
    user = DummyUser(['ai.read'])
    
    def permission_filter(user_id, item):
        return any(perm in user.permissions for perm in item.get('permissions', []))
    
    results = searcher.search('neural deep learning', ['document'], simple_context, 
                             mode="semantic", 
                             permission_filter=permission_filter)
    
    assert any(r['id'] == 'doc1' for r in results)
    assert all(r['source'] == 'semantic' for r in results)

def test_hybrid_and_dedupe(simple_context):
    searcher = HybridSemanticSearch(
        keyword_backend=DummyKeywordBackend(),
        semantic_backend=DummySemanticBackend()
    )
    user = DummyUser(['ai.read', 'course.view'])
    
    def permission_filter(user_id, item):
        return any(perm in user.permissions for perm in item.get('permissions', []))
    
    results = searcher.search('Neural deep', ['document'], simple_context, 
                             mode="hybrid", 
                             permission_filter=permission_filter)
    
    doc_ids = [r['id'] for r in results]
    # Should dedupe doc1, aggregate scores
    assert doc_ids.count('doc1') <= 1
    
    # Check for aggregated scores in hybrid mode
    if any(r['id'] == 'doc1' for r in results):
        doc1 = next(r for r in results if r['id'] == 'doc1')
        assert 'agg_keyword_score' in doc1
        assert 'agg_semantic_score' in doc1

def test_permission_filtering(simple_context):
    searcher = HybridSemanticSearch(
        keyword_backend=DummyKeywordBackend(),
        semantic_backend=DummySemanticBackend()
    )
    user = DummyUser(['coding.read'])
    
    def permission_filter(user_id, item):
        return any(perm in user.permissions for perm in item.get('permissions', []))
    
    results = searcher.search('python', ['document'], simple_context, 
                             mode="hybrid", 
                             permission_filter=permission_filter)
    
    doc_ids = [r['id'] for r in results]
    assert 'doc3' in doc_ids
    assert 'doc1' not in doc_ids

def test_score_aggregation(simple_context):
    searcher = HybridSemanticSearch(
        keyword_backend=DummyKeywordBackend(),
        semantic_backend=DummySemanticBackend()
    )
    user = DummyUser(['ai.read', 'course.view'])
    
    def permission_filter(user_id, item):
        return any(perm in user.permissions for perm in item.get('permissions', []))
    
    results = searcher.search('Neural', ['document'], simple_context, 
                             mode="hybrid", 
                             permission_filter=permission_filter)
    
    # Check that scores are properly aggregated
    for result in results:
        if result['id'] == 'doc1':
            assert 'score' in result
            assert 'agg_keyword_score' in result
            assert 'agg_semantic_score' in result
            # Final score should be a combination of both
            assert result['score'] >= max(result.get('agg_keyword_score', 0), 
                                         result.get('agg_semantic_score', 0))

def test_empty_results(simple_context):
    searcher = HybridSemanticSearch(
        keyword_backend=DummyKeywordBackend(),
        semantic_backend=DummySemanticBackend()
    )
    user = DummyUser(['unknown.permission'])
    
    def permission_filter(user_id, item):
        return any(perm in user.permissions for perm in item.get('permissions', []))
    
    results = searcher.search('something', ['document'], simple_context, 
                             mode="hybrid", 
                             permission_filter=permission_filter)
    
    # Should return empty list when no results match
    assert len(results) == 0
