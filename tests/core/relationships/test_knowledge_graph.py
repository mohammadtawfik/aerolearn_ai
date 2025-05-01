"""
File Location: /tests/core/relationships/test_knowledge_graph.py

Unit tests for KnowledgeGraph, Node, Edge, and relationship navigation.
"""

import pytest
from app.core.relationships.knowledge_graph import KnowledgeGraph, Node, Edge
from app.core.relationships.relationship_extractor import ConceptRelationship

def test_add_nodes_and_edges():
    graph = KnowledgeGraph()
    n1 = Node("c1", "Aerodynamics")
    n2 = Node("c2", "Lift")
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_edge(Edge("c1", "c2", "prerequisite"))
    assert "c1" in graph.nodes
    assert any(e.source == "c1" and e.target == "c2" for e in graph.edges)

def test_neighbors():
    graph = KnowledgeGraph()
    n1 = Node("c1", "Aerodynamics")
    n2 = Node("c2", "Lift")
    n3 = Node("c3", "Drag")
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)
    graph.add_edge(Edge("c1", "c2", "related"))
    graph.add_edge(Edge("c1", "c3", "related"))
    neighbors = graph.get_neighbors("c1", return_objects=True)
    neighbor_ids = [n.id for n in neighbors]
    assert set(neighbor_ids) == {"c2", "c3"}

def test_knowledge_graph_basic():
    kg = KnowledgeGraph()
    n1, n2, n3 = "LessonA", "Force", "Energy"
    r1 = ConceptRelationship(n1, n2, "covers")
    r2 = ConceptRelationship(n1, n3, "covers")
    r3 = ConceptRelationship(n2, n3, "related")
    kg.add_relationship(r1)
    kg.add_relationship(r2)
    kg.add_relationship(r3)
    assert n1 in kg.nodes
    assert any(e.source == n2 and e.target == n3 for e in kg.edges)
    assert len(kg.get_related(n1)) == 2
    assert set(kg.get_related(n1)) == {n2, n3}

def test_dot_export():
    kg = KnowledgeGraph()
    kg.add_relationship(ConceptRelationship("LessonA", "Force", "covers"))
    kg.add_relationship(ConceptRelationship("LessonA", "Energy", "covers"))
    kg.add_relationship(ConceptRelationship("Force", "Energy", "related"))
    
    dot_out = kg.to_dot()
    assert "digraph" in dot_out
    assert '"LessonA" -> "Force"' in dot_out
    assert '"LessonA" -> "Energy"' in dot_out
    assert '"Force" -> "Energy"' in dot_out
    assert 'label="related"' in dot_out

def test_navigation_and_traversal():
    kg = KnowledgeGraph()
    # Create a more complex graph
    concepts = ["Physics", "Mechanics", "Thermodynamics", "Energy", "Force", "Heat"]
    
    # Add relationships
    kg.add_relationship(ConceptRelationship("Physics", "Mechanics", "includes"))
    kg.add_relationship(ConceptRelationship("Physics", "Thermodynamics", "includes"))
    kg.add_relationship(ConceptRelationship("Mechanics", "Force", "covers"))
    kg.add_relationship(ConceptRelationship("Mechanics", "Energy", "covers"))
    kg.add_relationship(ConceptRelationship("Thermodynamics", "Heat", "covers"))
    kg.add_relationship(ConceptRelationship("Thermodynamics", "Energy", "covers"))
    kg.add_relationship(ConceptRelationship("Energy", "Heat", "related"))
    
    # Test navigation
    assert set(kg.get_related("Physics")) == {"Mechanics", "Thermodynamics"}
    assert set(kg.get_related("Mechanics")) == {"Force", "Energy"}
    assert "Energy" in kg.get_related("Thermodynamics")
    
    # Test path finding if implemented
    if hasattr(kg, 'find_path'):
        path = kg.find_path("Physics", "Heat")
        assert path is not None
        assert path[0] == "Physics"
        assert path[-1] == "Heat"
