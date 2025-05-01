"""
File: /tests/integration/test_resource_discovery_integration.py

Purpose:
    Integration tests for the external resource discovery API, tying together course content,
    resource provider(s), scoring, filtering, end-to-end deduplication and relevance logic.
    As required by /docs/development/day13_plan.md.

Requires:
    - /app/core/ai/resource_discovery.py (ResourceDiscoveryOrchestrator)
    - /app/core/external_resources/providers.py (provider classes)
    - /app/core/external_resources/scoring.py (scoring/filtering)
    - /tests/fixtures/sample_content.py, plus external resource mocks
"""

import pytest
from app.core.ai.resource_discovery import ResourceDiscoveryOrchestrator
from app.core.external_resources.providers import DeepSeekProvider, MockProvider
from app.core.external_resources.scoring import ResourceScorer
from tests.fixtures.sample_content import create_sample_course_content, external_resource_fixtures

@pytest.fixture
def resource_env():
    course_content = create_sample_course_content()
    providers = [DeepSeekProvider(), MockProvider()]
    orchestrator = ResourceDiscoveryOrchestrator(providers=providers)
    scorer = ResourceScorer()
    return orchestrator, scorer, course_content

def test_basic_resource_discovery(resource_env):
    orchestrator, scorer, course_content = resource_env
    resources = orchestrator.find_relevant_resources(course_content)
    assert isinstance(resources, list)
    assert all(hasattr(r, 'url') and hasattr(r, 'score') for r in resources)

def test_resource_scoring_and_filtering(resource_env):
    orchestrator, scorer, course_content = resource_env
    resources = orchestrator.find_relevant_resources(course_content)
    filtered = scorer.filter_by_score(resources, min_score=0.7)
    assert all(r.score >= 0.7 for r in filtered)
    # At least 1 result should be filtered away if min_score reasonable and data varied
    assert len(filtered) < len(resources)

def test_provider_deduplication(resource_env):
    orchestrator, scorer, course_content = resource_env
    resources = orchestrator.find_relevant_resources(course_content)
    urls = [r.url for r in resources]
    assert len(urls) == len(set(urls))  # No duplicates

def test_quality_and_metadata_fields(resource_env):
    orchestrator, scorer, course_content = resource_env
    resources = orchestrator.find_relevant_resources(course_content)
    for r in resources:
        assert r.quality in {"high", "medium", "low"}
        assert isinstance(r.metadata, dict)
        assert "source" in r.metadata

def test_full_integration_flow_with_edge_cases(resource_env):
    orchestrator, scorer, course_content = resource_env
    # Simulate edge case: course content with rare keyword or no direct match
    rare_content = [c for c in course_content if "muon tomography" in c.title]
    if rare_content:
        resources = orchestrator.find_relevant_resources(rare_content)
        assert isinstance(resources, list)
        # Might be empty, but must not fail
        assert all(hasattr(r, 'url') for r in resources)
    else:
        pytest.skip("No rare keyword test case in fixture")