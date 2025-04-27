# /app/models/tag_suggestion.py

class TagSuggestionService:
    """
    Suggests tags for content using simple keyword matching or ML backend.

    TODO: Connect to content/AI analysis and expand as needed.
    """
    def suggest(self, content_text, top_k=5):
        # Basic stub: extract words longer than 3 chars as 'tags'
        words = set(word.strip(",.?!").lower() for word in content_text.split())
        return [w for w in words if len(w) > 3][:top_k]