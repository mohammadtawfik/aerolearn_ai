# File: /app/core/external_resources/scoring.py
# Functions to score resources for relevance and quality versus course content

from difflib import SequenceMatcher

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