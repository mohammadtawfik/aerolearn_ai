# File: /tests/core/ai/test_resource_discovery.py
# Tests for ResourceDiscovery (external resource AI orchestrator)
import pytest

from app.core.ai.resource_discovery import ResourceDiscovery

class DummyCourse:
    def __init__(self, title):
        self.title = title
        self.external_resources = []

def test_discover_resources(monkeypatch):
    # Patch manager to simulate results
    class FakeManager:
        def query_all_providers(self, course):
            return [{"title": "Sample Resource", "description": "desc"}]
        def attach_resources_to_course(self, course, resources):
            course.external_resources = [r[0] for r in resources]
            return True
    
    dcourse = DummyCourse("Sample Course")
    disc = ResourceDiscovery()
    disc.manager = FakeManager()
    results = disc.discover_resources(dcourse)
    assert results
    assert isinstance(results[0], tuple)

def test_integration(monkeypatch):
    dcourse = DummyCourse("Integrable")
    disc = ResourceDiscovery()
    class FakeManager:
        def query_all_providers(self, course):
            return [{"title": "ABC", "description": "def"}]
        def attach_resources_to_course(self, course, resources):
            course.external_resources = [r[0] for r in resources]
            return True
    disc.manager = FakeManager()
    disc.integrate_resources(dcourse)
    assert dcourse.external_resources