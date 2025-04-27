# /app/models/category_suggestion.py

class CategorySuggestionService:
    """
    Suggests categories for content using either rule-based or AI/statistical analysis.

    TODO: Integrate with content analysis pipeline or external AI.
    """
    def suggest(self, content_text, top_k=3):
        # Stub logic: returns mock category names based on keywords
        keywords = {"biology": "Science", "calculus": "Mathematics", "ai": "Technology"}
        suggestions = []
        for kw, cat in keywords.items():
            if kw in content_text.lower():
                suggestions.append(cat)
        return suggestions[:top_k]