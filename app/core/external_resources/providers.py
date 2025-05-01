# File: /app/core/external_resources/providers.py
# Define pluggable resource providers (DeepSeek, YouTube, etc.)

from typing import List, Any
import requests
import os
try:
    from app.core.config.api_secrets import AI_API_KEY  # Can rename for DeepSeek if needed
except ImportError:
    AI_API_KEY = None

class BaseResourceProvider:
    """
    Abstract external resource provider.
    Subclasses implement fetch_resources(course).
    """
    PROVIDER_NAME = "abstract"

    @staticmethod
    def load_default_providers() -> List['BaseResourceProvider']:
        # Only DeepSeek as sample here.
        return [DeepSeekResourceProvider()]

    def fetch_resources(self, course) -> List[Any]:
        """
        Discover external resources relevant to a course.
        Must be implemented by subclasses.
        """
        raise NotImplementedError
        
    def find_resources(self, course):
        """Alias for integrator compatibility."""
        return self.fetch_resources(course)


class DeepSeekResourceProvider(BaseResourceProvider):
    PROVIDER_NAME = "DeepSeek"

    def fetch_resources(self, course) -> List[dict]:
        """
        Query the DeepSeek API for resources relevant to a course (pseudo-implementation).
        Supports both single course object and lists of course objects.
        """
        # Accept single or list of course items
        items = course
        if not isinstance(items, (list, tuple)):
            items = [items]
            
        results = []
        for course_item in items:
            if not AI_API_KEY:
                print("[DeepSeek] Skipping: No API key set.")
                continue
                
            # Extract a robust string for the query (never a method, never a function)
            title = getattr(course_item, 'title', None)
            if callable(title):
                # Defensive - handle misdefined namedtuples with title as method
                query = title()
            elif title is not None:
                query = title
            else:
                # Fallback to string representation
                query = str(course_item)
            url = "https://api.deepseek.com/v1/resources/search"
            headers = {"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}
            data = {
                "query": query,
                "limit": 5
            }
            try:
                response = requests.post(url, json=data, headers=headers, timeout=5)
                response.raise_for_status()
                api_items = response.json().get("results", [])
                results.extend([
                    {"title": item.get("title"), "url": item.get("url"), "description": item.get("snippet")}
                    for item in api_items
                ])
            except Exception as exc:
                print(f"[DeepSeek] Error: {exc}")
                continue
                
        return results

# Implement the expected DeepSeekProvider alias for compatibility with tests and external imports
DeepSeekProvider = DeepSeekResourceProvider

class MockProvider(BaseResourceProvider):
    """
    A mock provider returning deterministic, static resources for use in tests.
    Used for integration and unit tests to ensure predictable results.
    """
    PROVIDER_NAME = "Mock"

    def fetch_resources(self, course_content) -> List[Any]:
        """
        Generate mock resources for testing.
        Supports both single course object and lists of course objects.
        """
        # Accept single or list of course items
        items = course_content
        if not isinstance(items, (list, tuple)):
            items = [items]
            
        resources = []
        for c in items:
            title = getattr(c, 'title', None)
            if callable(title):
                title = title()
            elif title is not None:
                title = title
            else:
                title = str(c)
            for i in range(3):
                resources.append({
                    "title": f"Mock Resource {i} for {title}",
                    "url": f"https://mock.resource/{title.replace(' ', '_')}/{i}",
                    "description": "This is a mock resource description.",
                    "score": 0.5 + 0.2 * i,  # 0.5, 0.7, 0.9
                    "quality": ["low", "medium", "high"][i],
                    "metadata": {
                        "source": "MockProvider",
                        "index": i,
                    }
                })
        return resources

# For legacy/direct compatibility with test imports
__all__ = [
    "BaseResourceProvider",
    "DeepSeekResourceProvider",
    "DeepSeekProvider",
    "MockProvider",
]
