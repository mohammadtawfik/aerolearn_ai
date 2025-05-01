"""
INTEGRATION TEST
File: /tests/integration/test_relationship_mapping_integration.py

Covers: Extraction from content, population of knowledge graph, and navigation recommendations.

Required for Day 13.2 review.
"""

import pytest

from app.core.ai.concept_extraction import DomainConceptExtractor, extract_concept_relationships
from app.core.relationships.knowledge_graph import KnowledgeGraph, Node, Edge
from app.core.relationships.navigation import RelationshipNavigator

# DummyContent model for test, simulating lesson etc.
class DummyContent:
    def __init__(self, id, title="", description="", body="", text=""):
        self.id = id
        self.title = title
        self.description = description
        self.body = body
        self.text = text

@pytest.fixture
def test_contents():
    # Simulated learning materials
    return [
        DummyContent(
            id="lesson1",
            title="Introduction to Quantum Physics",
            description="Describes wave-particle duality, key principles, and energy.",
            body="The Schrödinger equation governs quantum state evolution."
        ),
        DummyContent(
            id="lesson2",
            title="Classical Mechanics Overview",
            description="Forces and motion, Newton’s laws, Energy.",
            body="Explores kinetic and potential energy."
        ),
        DummyContent(
            id="lesson3",
            title="Thermodynamics Basics",
            description="Main topics: Energy, Heat, Entropy.",
            body="Covers the law of conservation of energy and entropy."
        ),
    ]

def test_relationship_integration(test_contents):
    # 1. Extract concepts for all content
    extractor = DomainConceptExtractor(domain_terms=["energy", "quantum", "wave", "entropy", "force", "motion", "heat", "schrodinger"])
    graph = KnowledgeGraph()

    # Map content and concepts, and add nodes/relationships to the graph
    for content in test_contents:
        graph.add_node(Node(content.id, content.title))
        text_blob = " ".join([content.title, content.description, content.body, content.text])
        concepts = extractor.extract(text_blob)
        for concept in concepts:
            cid = concept.name.lower()
            # Add concept node (id=concept name)
            if cid not in graph.nodes:
                graph.add_node(Node(cid, concept.name))
            # Link: content_id "covers" concept_id
            graph.add_edge(Edge(content.id, cid, "covers"))

    # Confirm nodes and edges exist as expected (content and concept nodes)
    for content in test_contents:
        assert content.id in graph.nodes
    for expected_concept in ["quantum", "wave", "energy", "schrodinger", "entropy", "motion", "heat", "force"]:
        assert expected_concept in graph.nodes

    # Confirm at least one edge from each content to at least one concept
    for content in test_contents:
        covers_edges = [e for e in graph.edges if e.source == content.id and e.relation == "covers"]
        assert len(covers_edges) >= 1

    # 2. Test navigation/recommendation layer
    navigator = RelationshipNavigator(graph)
    # E.g., lesson2 should recommend "energy" as related concept
    related_concepts = navigator.get_related_concepts("lesson2")
    related_names = {c.label.lower() for c in related_concepts}
    assert "energy" in related_names

    # path (lesson1 -> "energy") exists via some edge
    path = navigator.find_path("lesson1", "energy", max_depth=2)
    assert path and path[0] == "lesson1" and path[-1] == "energy"

    # 3. Recommendations for lesson1 (other lessons covering related concepts)
    recommendations = navigator.get_recommendations_for_content("lesson1")
    # lesson3 should also cover "energy", and be recommended if not the current lesson
    rec_ids = {n.id for n in recommendations}
    assert "lesson3" in rec_ids

    # 4. DOT export available / includes expected nodes
    dot_repr = graph.to_dot()
    assert "lesson1" in dot_repr and "energy" in dot_repr

    # Optional: Print output for review/debugging
    print("Graph DOT output:\n", dot_repr)
    print("Recommendations for lesson1: ", rec_ids)
