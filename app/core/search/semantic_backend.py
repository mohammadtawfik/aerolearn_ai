"""
File: /app/core/search/semantic_backend.py
Purpose: Semantic vector search backend

This file should be saved as /app/core/search/semantic_backend.py according to the project structure.
"""

from app.core.search.base_search import SearchBackend, SearchResult
from typing import List, Any
import string

# --- Improved dummy embedding model ---
def embed_text(text: str) -> list:
    """
    Improved dummy embedding: Bag-of-characters (lowercase a-z and space).
    Returns a fixed 27-dimensional vector (frequency of each a-z and ' ').
    This approach gives positive similarity for overlapping terms, unlike character hash.
    """
    text = text.lower()
    alphabet = string.ascii_lowercase + ' '
    vector = [0.0 for _ in range(len(alphabet))]
    for c in text:
        if c in alphabet:
            idx = alphabet.index(c)
            vector[idx] += 1.0
    return vector

def cosine_similarity(vec1, vec2):
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a*b for a, b in zip(vec1, vec2))
    norm1 = sum(a*a for a in vec1) ** 0.5
    norm2 = sum(b*b for b in vec2) ** 0.5
    return dot / (norm1 * norm2 + 1e-10)

class SemanticSearchBackend(SearchBackend):
    """
    Embedding-based semantic search backend.
    Uses naive bag-of-characters dummy embedding for demonstration/testing.
    Replace embed_text with real embedding model for production use.
    """
    def search(self, query: str, context: Any = None, limit: int = 50) -> List[SearchResult]:
        if context is None:
            return []
        query_vec = embed_text(query)
        results = []
        for item in context:
            content = item.get('title', '') + ' ' + item.get('content', '')
            item_vec = embed_text(content)
            score = cosine_similarity(query_vec, item_vec)
            if score > 0.0:  # Accept anything with some overlap
                results.append(SearchResult(
                    id=item['id'],
                    score=score,
                    source='semantic',
                    data=item
                ))
        return sorted(results, key=lambda r: r['score'], reverse=True)[:limit]
