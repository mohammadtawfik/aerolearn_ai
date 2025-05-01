"""
INTEGRATION TEST
File: /tests/integration/test_semantic_search_integration.py

Purpose:
    Integration test for hybrid semantic search with correct predicate-based permission filtering
    for each result. Uses a per-result predicate function matching HybridSemanticSearch's expected filter.
    All test assertions use r["data"][...] fields.

    Place in /tests/integration/ as per code_summary.md and roadmap.
"""

import pytest

from app.core.ai.semantic_search import HybridSemanticSearch
from app.core.search.keyword_search import KeywordSearch
from app.models.content import Content

from tests.fixtures.sample_content.repositories import create_sample_repositories

def permission_filter_predicate(user, result):
    """Permission filter for a SINGLE result dict, to match HybridSemanticSearch usage."""
    # result is a dict with 'data' field (the original doc), and optionally permissions list
    perms = set(result.get("data", {}).get("permissions", []))
    user_perms = set(getattr(user, "permissions", []))
    return bool(perms & user_perms) or not perms  # allow if user has any required perm, or unrestricted

@pytest.fixture
def sample_env():
    return create_sample_repositories()

@pytest.fixture
def dummy_user(sample_env):
    _, users, _ = sample_env
    return users["student"]

@pytest.fixture
def test_context(sample_env):
    repositories, _, _ = sample_env
    return repositories.get("docs", [])

def test_hybrid_search_permission_filtering_and_aggregation(sample_env):
    repositories, users, auth_manager = sample_env
    search = HybridSemanticSearch(
        keyword_backend=KeywordSearch(),
        permission_checker=permission_filter_predicate
    )

    user = users["student"]
    query = "Quantum entanglement experiments"
    context = repositories.get("docs", [])
    results = search.search(query=query, context=context, user=user)
    
    # Verify permission filtering works
    assert all(permission_filter_predicate(user, r) for r in results)
    
    # Should return the quantum document
    assert any("Quantum" in r["data"].get("title", "") for r in results)

def test_semantic_vs_keyword_results(sample_env):
    repositories, users, _ = sample_env
    search = HybridSemanticSearch(
        keyword_backend=KeywordSearch(),
        permission_checker=permission_filter_predicate
    )

    user = users["professor"]
    context = repositories.get("docs", [])

    exact = search.search(query="Heisenberg uncertainty", context=context, user=user, mode="keyword")
    semantic = search.search(query="Limitations of precise measurement", context=context, user=user, mode="semantic")

    assert len(semantic) >= len(exact)
    # At least one doc with Heisenberg in the title
    assert any("Heisenberg" in r["data"].get("title", "") for r in semantic)

def test_aggregation_and_deduplication(sample_env):
    repositories, users, _ = sample_env
    search = HybridSemanticSearch(
        keyword_backend=KeywordSearch(),
        permission_checker=permission_filter_predicate
    )

    user = users["admin"]
    context = repositories.get("docs", [])

    # Insert duplicate IDs manually to simulate aggregation
    context_with_dupe = context + [{"id": "doc1", "title": "Quantum Entanglement Experiments", "body": "Dupe", "content": "Dupe", "summary": "", "permissions": ["content.view"]}]
    results = search.search(query="quantum", context=context_with_dupe, user=user)
    # Should deduplicate by id
    ids = [r["data"]["id"] for r in results]
    assert len(ids) == len(set(ids))

def test_empty_query_returns_nothing(sample_env):
    repositories, users, _ = sample_env
    search = HybridSemanticSearch(
        keyword_backend=KeywordSearch(),
        permission_checker=permission_filter_predicate
    )

    user = users["student"]
    context = repositories.get("docs", [])
    results = search.search(query="", context=context, user=user)
    assert results == []

def test_search_accuracy_edge_case(sample_env):
    repositories, users, _ = sample_env
    search = HybridSemanticSearch(
        keyword_backend=KeywordSearch(),
        permission_checker=permission_filter_predicate
    )

    user = users["professor"]
    context = repositories.get("docs", [])

    # Query with ambiguous meaning - should retrieve both physics and admin docs for admin user
    admin_user = users["admin"]
    results = search.search(query="charge", context=context, user=admin_user)
    physics_count = sum("electron" in r["data"].get("content", "") for r in results)
    admin_count = sum("user charge" in r["data"].get("summary", "") for r in results)
    # Should find at least one for each interpretation
    assert physics_count > 0 and admin_count > 0

def test_semantic_search_with_test_context(dummy_user, test_context):
    search = HybridSemanticSearch(
        keyword_backend=KeywordSearch(),
        permission_checker=permission_filter_predicate
    )
    query = "What is energy in physics?"
    results = search.search(query, context=test_context, user=dummy_user, limit=5)
    assert isinstance(results, list)
    assert any("energy" in (r["data"].get("title", "") + " " + r["data"].get("body", "") + " " + r["data"].get("content", "")).lower() for r in results)
