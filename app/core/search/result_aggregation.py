"""
File: /app/core/search/result_aggregation.py
Purpose: Utilities for aggregating, deduplicating, and ranking hybrid search results.

This file should be saved as /app/core/search/result_aggregation.py according to the project structure.
"""

from typing import List, Dict, Any

def aggregate_and_deduplicate_results(results_backends: List[List[Dict]], query: str) -> List[Dict]:
    """
    Combines results from multiple backends, dedupes using ID, and fuses scores.
    Returns unified list sorted by hybrid score.
    """
    result_map = {}
    for backend_results in results_backends:
        for result in backend_results:
            rid = result['id']
            if rid not in result_map:
                result_map[rid] = result.copy()
                result_map[rid]['score_components'] = {result['source']: result['score']}
            else:
                # Fuse scores: weighted average, more weight to semantic if exists
                src = result['source']
                prev = result_map[rid]
                prev['score_components'][src] = result['score']
                prev['score'] = (
                    0.6 * prev['score_components'].get('semantic', 0) +
                    0.4 * prev['score_components'].get('keyword', 0)
                )
    results = list(result_map.values())
    results.sort(key=lambda r: r['score'], reverse=True)
    return results