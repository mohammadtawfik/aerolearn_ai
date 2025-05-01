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


class DeepSeekResourceProvider(BaseResourceProvider):
    PROVIDER_NAME = "DeepSeek"

    def fetch_resources(self, course) -> List[dict]:
        """
        Query the DeepSeek API for resources relevant to a course (pseudo-implementation).
        """
        if not AI_API_KEY:
            print("[DeepSeek] Skipping: No API key set.")
            return []
        query = getattr(course, 'title', str(course))
        url = "https://api.deepseek.com/v1/resources/search"
        headers = {"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}
        data = {
            "query": query,
            "limit": 5
        }
        try:
            response = requests.post(url, json=data, headers=headers, timeout=5)
            response.raise_for_status()
            items = response.json().get("results", [])
            return [
                {"title": item.get("title"), "url": item.get("url"), "description": item.get("snippet")}
                for item in items
            ]
        except Exception as exc:
            print(f"[DeepSeek] Error: {exc}")
            return []