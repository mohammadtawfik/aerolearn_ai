"""
INTEGRATION TEST
File: /tests/integration/test_relationship_mapping_integration.py

Purpose:
    This file contains the integration test suite for content relationship mapping,
    as required by Day 13.2 of the project plan (/docs/development/day13_plan.md).

    It covers:
      - Extraction of domain concepts from content
      - Population and validation of the knowledge graph (nodes, edges, relationships)
      - Navigation/recommendation using the modeled relationships
      - DOT export for visualization of graph structure

Test Placement Rationale:
    This test MUST be located at /tests/integration/ per the AeroLearn AI
    project structure policy (see /code_summary.md: 'tests/integration/').
    Integration tests validate cross-module workflows, here spanning concept extraction,
    relationships, and navigation, with coverage of real code paths and system states.

    Always include an explicit rationale and file path in new test or code files.

Requirements traceability: Day 13.2 (see /docs/development/day13_plan.md)
"""

import pytest

from app.core.ai.concept_extraction import DomainConceptExtractor, extract_concept_relationships
from app.core.relationships.knowledge_graph import KnowledgeGraph, Node, Edge
from app.core.relationships.navigation import RelationshipNavigator

# Simulate a simplified content fragment
class DummyContent:
    """A stand-in class for lessons, modules, or other course content for extraction tests."""
    def __init__(self, id, title="", description="", body="", text=""):
        self.id = id
        self.title = title
        self.description = description
        self.body = body
        self.text = text

@pytest.fixture
def test_contents():
    """Provides several learning material examples across multiple physics domains."""
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
    """
    INTEGRATION: Concept Extraction, Knowledge Graph Construction, Navigation

    - Extract domain concepts from multiple contents
    - Map nodes and relationships into the knowledge graph
    - Validate relationship creation and navigation logic
    - Confirm recommendations and DOT graph exports
    """

    # --- 1. Concept Extraction and Graph Population ---
    extractor = DomainConceptExtractor(domain_terms=[
        "energy", "quantum", "wave", "entropy", "force", "motion", "heat", "schrodinger"
    ])
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

    # Validate node creation for both content and domain concepts
    for content in test_contents:
        assert content.id in graph.nodes
    for expected_concept in ["quantum", "wave", "energy", "schrodinger", "entropy", "motion", "heat", "force"]:
        assert expected_concept in graph.nodes

    # Ensure each content maps to at least one concept via "covers"
    for content in test_contents:
        covers_edges = [e for e in graph.edges if e.source == content.id and e.relation == "covers"]
        assert len(covers_edges) >= 1

    # --- 2. Navigation and Recommendation Layer ---
    navigator = RelationshipNavigator(graph)
    
    # Validate: lesson2 should recommend "energy" as a related concept
    related_concepts = navigator.get_related_concepts("lesson2")
    related_names = {c.label.lower() for c in related_concepts}
    assert "energy" in related_names

    # Validate: A path exists from lesson1 to "energy"
    path = navigator.find_path("lesson1", "energy", max_depth=2)
    assert path and path[0] == "lesson1" and path[-1] == "energy"

    # Validate: Recommendations for lesson1 include another lesson (e.g., lesson3) that covers energy
    recommendations = navigator.get_recommendations_for_content("lesson1")
    rec_ids = {n.id for n in recommendations}
    assert "lesson3" in rec_ids

    # --- 3. Visualization (DOT Export) ---
    dot_repr = graph.to_dot()
    assert "lesson1" in dot_repr and "energy" in dot_repr

    # (Optional for CI review - print output)
    print("Graph DOT output:\n", dot_repr)
    print("Recommendations for lesson1: ", rec_ids)
