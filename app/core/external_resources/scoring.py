# File: /app/core/external_resources/scoring.py
# Functions and classes to score and filter resources for relevance and quality versus course content

from difflib import SequenceMatcher
from typing import List, Any

def score_resource(resource, course) -> float:
    """
    Compute a relevance/quality score between this resource and the course.
    This can be as sophisticated as needed; for now, use title similarity and fallback.
    """
    course_title = getattr(course, 'title', str(course))
    res_title = resource.get("title", "")
    # Very basic similarity ratio, can extend to embedding/AI scoring
    title_score = SequenceMatcher(None, res_title.lower(), course_title.lower()).ratio()
    # Additional: prioritize resources with description present
    desc_bonus = 0.1 if resource.get("description") else 0
    # Placeholder for more signal (citations, domain, recency, etc.)
    return round(title_score + desc_bonus, 3)

class ResourceScorer:
    """
    Class encapsulating resource scoring and filtering logic.
    Used by resource discovery orchestrators and integration tests.
    """
    def score(self, resource, course_content) -> float:
        # Proxy to score_resource for backward compatibility
        return score_resource(resource, course_content)
    
    def filter_by_score(self, resources: List[Any], min_score: float = 0.7) -> List[Any]:
        """
        Filter a list of resources, keeping only those with score >= min_score.
        Will auto-score resources that do not have a 'score' attribute.
        Returns filtered list, preserving input order.
        """
        filtered = []
        for r in resources:
            sc = getattr(r, "score", None)
            # r may be a dict or an object, so fallback to .get
            if sc is None and hasattr(r, "get"):
                sc = r.get("score", None)
            if sc is None and hasattr(r, "__dict__"):
                sc = getattr(r, "score", None)
            if sc is None:
                # Try to score if not present and course content is available
                # Here, we assume original resource list had course_content passed separately if needed
                sc = self.score(r, course_content=None)  # None will fallback to string
            if sc is not None and sc >= min_score:
                filtered.append(r)
        return filtered

# For compatibility with previous interface and test imports
__all__ = ["score_resource", "ResourceScorer"]
