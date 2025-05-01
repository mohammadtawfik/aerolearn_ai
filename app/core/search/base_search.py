"""
File: /app/core/search/base_search.py
Purpose: Abstract/protocol definitions for search backends and results.

This file should be saved as /app/core/search/base_search.py according to the project structure.
"""

from abc import ABC, abstractmethod
from typing import List, Any, Dict

class SearchResult(dict):
    """
    Dict with required fields for all search results:
    id: str     - Unique result identifier
    score: float- Raw relevance score
    source: str - Which backend provided this result
    data: dict  - Arbitrary additional result data
    """
    pass

class SearchBackend(ABC):
    """
    Base interface for all search backends.
    """
    @abstractmethod
    def search(self, query: str, context: Any = None, limit: int = 50) -> List[SearchResult]:
        """
        Execute search for query in context.
        Returns a list of SearchResult objects.
        """
        pass