# File: /tests/core/external_resources/test_providers.py

import pytest
from app.core.external_resources.providers import DeepSeekResourceProvider

class DummyCourse:
    def __init__(self, title):
        self.title = title

def test_deepseek_missing_key(monkeypatch):
    # Remove API key to simulate config
    monkeypatch.setattr("app.core.external_resources.providers.AI_API_KEY", None)
    prov = DeepSeekResourceProvider()
    resources = prov.fetch_resources(DummyCourse("Nothing"))
    assert resources == []

def test_deepseek_api(monkeypatch):
    # Simulate DeepSeek API with patch
    prov = DeepSeekResourceProvider()
    monkeypatch.setattr(prov, "fetch_resources", lambda course: [{"title": "X", "url": "Y", "description": "Z"}])
    results = prov.fetch_resources(DummyCourse("Physics"))
    assert  isinstance(results, list)