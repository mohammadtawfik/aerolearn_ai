"""
File: /tests/core/search/test_keyword_search.py
Purpose: Unit tests for /app/core/search/keyword_search.py

This file should be saved as /tests/core/search/test_keyword_search.py according to the project structure.
"""

from app.core.search.keyword_search import KeywordSearch

def test_keyword_search_simple():
    backend = KeywordSearch()
    context = [
        {'id': '1', 'title': 'Introduction to AI', 'content': 'Artificial intelligence overview'},
        {'id': '2', 'title': 'Math review', 'content': 'Algebra and calculus'},
    ]
    results = backend.search('AI', context=context)
    assert results and results[0]['id'] == '1'

def test_keyword_case_insensitive():
    backend = KeywordSearch()
    context = [{'id': '3', 'title': 'Physics', 'content': 'Energy'}]
    results = backend.search('physics', context=context)
    assert results and results[0]['id'] == '3'

def test_keyword_score():
    backend = KeywordSearch()
    context = [{'id': '4', 'title': 'Deep Learning', 'content': 'deep learning in practice'}]
    results = backend.search('deep', context=context)
    assert results[0]['score'] >= 2  # 2 points for title, min 1 for content