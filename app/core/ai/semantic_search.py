"""
File: /app/core/ai/semantic_search.py
Purpose: Core logic for hybrid semantic and keyword search with permission filtering and aggregation.

Save and update at /app/core/ai/semantic_search.py according to the project structure.

Implements:
- Hybrid keyword+semantic search logic
- Result aggregation and deduplication
- Component-specific target search
- Permission filtering
- Customizable scoring and rank boosting

Typical usage:
    search = HybridSemanticSearch(keyword_backend=KeywordSearch())
    results = search.search(query, targets, context, user_id)
"""

from app.core.search.base_search import SearchBackend, SearchResult
from app.core.search.keyword_search import KeywordSearch
from app.core.search.semantic_backend import SemanticSearchBackend
from app.core.search.permissions import filter_by_permission
from typing import List, Dict, Any, Optional, Callable, Union

class PermissionDenied(Exception):
    """Exception raised when a user doesn't have permission to access content"""
    pass

class HybridSemanticSearch:
    """
    Unified search interface combining keyword and semantic strategies,
    supporting permission filtering and custom scoring/aggregation.
    """

    def __init__(
        self,
        semantic_backend: Optional[SearchBackend] = None,
        keyword_backend: Optional[SearchBackend] = None,
        permission_checker: Optional[Callable] = None,
        scoring_weights: Optional[Dict[str, float]] = None
    ):
        """
        Args:
            semantic_backend: SearchBackend for embedding-based search (default: SemanticSearchBackend)
            keyword_backend: SearchBackend for keyword-based search (default: KeywordSearch)
            permission_checker: Function(user, item) -> bool
            scoring_weights: Dict of component-specific weights, e.g. {"semantic": 0.7, "keyword": 0.3}
        """
        self.semantic_backend = semantic_backend or SemanticSearchBackend()
        self.keyword_backend = keyword_backend or KeywordSearch()
        self.permission_checker = permission_checker or filter_by_permission
        self.weights = scoring_weights or {"semantic": 0.7, "keyword": 0.3}

    def search(
        self,
        query: str,
        targets: Optional[List[str]] = None,
        context: Optional[Union[List[Dict], Dict[str, List[Dict]]]] = None,
        user = None,
        limit: int = 20,
        mode: str = "hybrid",
        custom_weights: Optional[Dict[str, float]] = None,
        permission_filter: Optional[Callable] = None
    ) -> List[Dict]:
        """
        Perform hybrid search with customizable parameters.

        Args:
            query: The search query string.
            targets: List of component/content types to search (e.g., ["course", "lesson"]).
            context: Dataset(s) to search — either a single list, or a dict of {target: [docs]}.
            user: User performing the search (for permission filtering).
            limit: Max number of results.
            mode: "hybrid", "semantic", or "keyword"
            custom_weights: Optional override for scoring weights.
            permission_filter: Optional function to override instance-level permission check.

        Returns:
            List[Dict] — deduplicated, aggregated, ranked search results.
        """
        weights = custom_weights or self.weights
        permission_fn = permission_filter or self.permission_checker

        # Handle context formatting
        target_docs = {}
        if targets and isinstance(context, dict):
            for t in targets:
                target_docs[t] = context.get(t, [])
        else:
            # Single list applies to all targets or no targets specified
            target_docs = {"default": context or []}
        
        combined_results = {}
        
        # Process each target type
        for target_type, docs in target_docs.items():
            # Get results from backends based on mode
            semantic_results = []
            keyword_results = []
            
            if mode in ("hybrid", "semantic"):
                semantic_results = self.semantic_backend.search(query, context=docs, limit=limit*2)
                
            if mode in ("hybrid", "keyword"):
                keyword_results = self.keyword_backend.search(query, context=docs, limit=limit*2)
            
            # Process semantic results
            for res in semantic_results:
                doc_id = res.get("id")
                if not doc_id:
                    continue
                    
                if doc_id not in combined_results or res["score"] > combined_results[doc_id]["score"]:
                    combined_results[doc_id] = res.copy()
                
                # Add metadata
                combined_results[doc_id]["target_type"] = target_type
                combined_results[doc_id]["agg_semantic_score"] = res["score"]
                combined_results[doc_id]["source"] = "semantic"
            
            # Process keyword results
            for res in keyword_results:
                doc_id = res.get("id")
                if not doc_id:
                    continue
                
                # If already present from semantic search, combine scores
                if doc_id in combined_results:
                    base = combined_results[doc_id]
                    base["agg_score"] = (
                        weights["semantic"] * base.get("agg_semantic_score", 0) +
                        weights["keyword"] * res["score"]
                    )
                    base["agg_keyword_score"] = res["score"]
                    base["source"] = "hybrid"
                else:
                    # Only from keyword search
                    out = res.copy()
                    out["target_type"] = target_type
                    out["agg_keyword_score"] = res["score"]
                    out["agg_score"] = weights["keyword"] * res["score"]
                    out["source"] = "keyword"
                    combined_results[doc_id] = out
        
        # Ensure all aggregated keys are present and calculate final scores
        for r in combined_results.values():
            if "agg_semantic_score" not in r:
                r["agg_semantic_score"] = 0.0
            if "agg_keyword_score" not in r:
                r["agg_keyword_score"] = 0.0
            if "agg_score" not in r:
                # Calculate weighted score using available components
                r["agg_score"] = (
                    weights["semantic"] * r.get("agg_semantic_score", 0.0) +
                    weights["keyword"] * r.get("agg_keyword_score", 0.0)
                )
        
        # Convert to list and sort by aggregated score
        results_list = list(combined_results.values())
        sorted_results = sorted(results_list, key=lambda x: x.get("agg_score", 0), reverse=True)
        
        # Apply permission filtering
        if user and permission_fn:
            filtered_results = [r for r in sorted_results if permission_fn(user, r)]
        else:
            filtered_results = sorted_results
        
        return filtered_results[:limit]

    def search_legacy(self, user, query, context=None, top_k=20):
        """
        Legacy interface for backward compatibility.
        
        :param user: User object (for permission filtering)
        :param query: str, search query
        :param context: Optional dict or object to restrict search scope
        :param top_k: Number of top results to return
        :return: List of search results sorted by overall relevance
        """
        return self.search(
            query=query,
            context=context,
            user=user,
            limit=top_k
        )

# For backward compatibility
SemanticSearch = HybridSemanticSearch
