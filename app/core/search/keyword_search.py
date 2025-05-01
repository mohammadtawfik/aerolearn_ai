"""
File: /app/core/search/keyword_search.py
Purpose: Keyword-based search backend for AeroLearn AI

This file should be saved as /app/core/search/keyword_search.py according to the project structure.
"""

from app.core.search.base_search import SearchBackend, SearchResult
from typing import List, Any

class KeywordSearch(SearchBackend):
    """
    Concrete implementation of a keyword-based search backend.
    """
    def search(self, query: str, context: Any = None, limit: int = 50) -> List[SearchResult]:
        # Placeholder: In reality, would query an inverted index or database
        # Here, we assume context is a sequence of dicts with 'title' and 'content'
        results = []
        if context is None:
            return results
        for item in context:
            score = self._compute_score(query, item)
            if score > 0:
                results.append(
                    SearchResult(
                        id=item['id'],
                        score=score,
                        source='keyword',
                        data=item
                    )
                )
        # Sort by score, limit to N
        return sorted(results, key=lambda r: r['score'], reverse=True)[:limit]

    def _compute_score(self, query: str, item: dict) -> float:
        # Very basic keyword matching (stub)
        score = 0
        for word in query.split():
            if word.lower() in item.get('title', '').lower():
                score += 2
            if word.lower() in item.get('content', '').lower():
                score += 1
        return score