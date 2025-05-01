# File: /app/core/ai/resource_discovery.py
# This orchestrates external resource discovery, scoring, deduplication, and normalization.

from typing import List, Dict, Any, Tuple
from app.core.external_resources import ExternalResourceManager
from app.core.external_resources.scoring import score_resource
from app.models.course import Course

# Import provider infrastructure
try:
    from app.core.external_resources.providers import DeepSeekProvider, MockProvider, BaseResourceProvider
except ImportError:
    # Fallbacks or stubs if providers not available
    DeepSeekProvider = MockProvider = BaseResourceProvider = object

class ResourceResult:
    """Standardized resource result format as expected by tests."""
    def __init__(self, url, score, quality, metadata: dict):
        self.url = url
        self.score = score
        self.quality = quality
        self.metadata = metadata

    def __eq__(self, other):
        if not isinstance(other, ResourceResult):
            return False
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)

class ResourceDiscoveryOrchestrator:
    """
    Coordinates resource discovery from multiple providers,
    ensures deduplication, normalization, and compatibility with scoring/filtering logic.
    Handles both single content and list of contents.
    Always attempts fetch_resources first, then find_resources if available.
    """
    def __init__(self, providers: List[Any] = None):
        """
        providers: list of provider instances (e.g., DeepSeekProvider, MockProvider)
        """
        # Accept any provider that implements .find_resources(content)
        self.providers = providers if providers is not None else [DeepSeekProvider(), MockProvider()]
    
    def find_relevant_resources(self, course_content) -> List[ResourceResult]:
        """
        Accepts either a single course_content or a list.
        Calls each provider, aggregates, deduplicates, scores, and normalizes results.
        Returns a list of ResourceResult.
        """
        discovered = []
        content_items = course_content
        # Accept both a single item and a list/tuple of items
        if not isinstance(content_items, (list, tuple)):
            content_items = [content_items]
            
        for content in content_items:
            for provider in self.providers:
                results = []
                # Robustly try fetch_resources, fallback to find_resources (for integration test compatibility)
                fetch = getattr(provider, "fetch_resources", None)
                find = getattr(provider, "find_resources", None)
                if callable(fetch):
                    try:
                        results = fetch(content)
                    except Exception:
                        results = []
                elif callable(find):
                    try:
                        results = find(content)
                    except Exception:
                        results = []
                if results:
                    discovered.extend(results)

        # Deduplicate by url:
        resource_map = {}
        for res in discovered:
            url = getattr(res, "url", None) or (res.get("url") if isinstance(res, dict) else None)
            if not url or url in resource_map:
                continue
            
            # Score if not present
            score = getattr(res, "score", None) if hasattr(res, "score") else res.get("score") if isinstance(res, dict) else None
            if score is None:
                score = score_resource(res, content_items[0])  # Use first course for scoring context
            
            # Assign quality according to score:
            if score >= 0.85:
                quality = "high"
            elif score >= 0.7:
                quality = "medium"
            else:
                quality = "low"
                
            # Compose metadata:
            meta = getattr(res, "metadata", {}) if hasattr(res, "metadata") else res.get("metadata", {}) or {}
            meta = dict(meta)  # ensure dict
            # Warn if source is not being set
            meta.setdefault("source", provider.__class__.__name__ if hasattr(provider, "__class__") else str(provider))
            resource_map[url] = ResourceResult(url, score, quality, meta)

        # Return sorted list (by score desc)
        results = list(resource_map.values())
        results.sort(key=lambda x: x.score, reverse=True)
        return results

class ResourceDiscovery:
    """Legacy class maintained for backward compatibility."""
    def __init__(self, providers=None):
        self.manager = ExternalResourceManager(providers)
    
    def discover_resources(self, course: Course, max_results=10):
        """
        Find relevant external resources for the given course.
        Returns a list of (resource, score) tuples.
        """
        discovered = self.manager.query_all_providers(course)
        # Score all resources
        scored = [(res, score_resource(res, course)) for res in discovered]
        # Sort and filter by descending score
        scored = sorted(scored, key=lambda x: x[1], reverse=True)
        return scored[:max_results]
    
    def integrate_resources(self, course: Course):
        """
        Integrate discovered resources into the course's metadata or recommendations.
        """
        resources = self.discover_resources(course)
        self.manager.attach_resources_to_course(course, resources)
        return resources

# For module __all__ export and public import consistency
__all__ = ["ResourceDiscoveryOrchestrator", "ResourceDiscovery", "ResourceResult"]
