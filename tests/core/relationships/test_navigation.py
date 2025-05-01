"""
File Location: /tests/core/relationships/test_navigation.py

Unit tests for RelationshipNavigator, which provides recommendations based on the knowledge graph.
"""

import pytest
from app.core.relationships.knowledge_graph import KnowledgeGraph, Node, Edge
from app.core.relationships.navigation import RelationshipNavigator

def make_graph():
    graph = KnowledgeGraph()
    a = Node("a", "Aerodynamics")
    b = Node("b", "Lift")
    c = Node("c", "Drag")
    d = Node("d", "Bernoulli Principle")
    for n in [a, b, c, d]:
        graph.add_node(n)
    graph.add_edge(Edge("a", "b", "prerequisite"))
    graph.add_edge(Edge("b", "c", "related"))
    graph.add_edge(Edge("a", "d", "related"))
    return graph

def test_recommend_next():
    graph = make_graph()
    navigator = RelationshipNavigator(graph)
    next_nodes = navigator.recommend_next("a")
    labels = [n.label for n in next_nodes]
    assert "Lift" in labels
    assert "Bernoulli Principle" in labels

def test_find_path():
    graph = make_graph()
    navigator = RelationshipNavigator(graph)
    path = navigator.find_path("a", "c")
    assert path == ["a", "b", "c"] or path == ["a", "d", "c"]  # Accept alternative routes if available

def test_get_related_content():
    """Test that navigator can find content related to a specific concept."""
    graph = KnowledgeGraph()
    
    # Create nodes for lessons and concepts
    lesson1 = Node("lesson1", "Introduction to Physics")
    lesson2 = Node("lesson2", "Forces in Motion")
    concept = Node("concept", "Force")
    
    # Add nodes to graph
    for node in [lesson1, lesson2, concept]:
        graph.add_node(node)
    
    # Connect lessons to the concept
    graph.add_edge(Edge("lesson1", "concept", "covers"))
    graph.add_edge(Edge("lesson2", "concept", "covers"))
    
    navigator = RelationshipNavigator(graph)
    related_content = navigator.get_related_content("concept")
    
    # Both lessons should be related to the concept
    assert len(related_content) == 2
    assert "lesson1" in [node.id for node in related_content]
    assert "lesson2" in [node.id for node in related_content]

def test_get_recommendations_for_content():
    """Test that navigator can recommend related content based on shared concepts."""
    graph = KnowledgeGraph()
    
    # Create nodes for lessons and concepts
    lesson1 = Node("lesson1", "Basic Mechanics")
    lesson2 = Node("lesson2", "Advanced Mechanics")
    lesson3 = Node("lesson3", "Thermodynamics")
    concept1 = Node("concept1", "Force")
    concept2 = Node("concept2", "Energy")
    
    # Add nodes to graph
    for node in [lesson1, lesson2, lesson3, concept1, concept2]:
        graph.add_node(node)
    
    # Connect lessons to concepts
    graph.add_edge(Edge("lesson1", "concept1", "covers"))
    graph.add_edge(Edge("lesson2", "concept1", "covers"))
    graph.add_edge(Edge("lesson2", "concept2", "covers"))
    graph.add_edge(Edge("lesson3", "concept2", "covers"))
    
    navigator = RelationshipNavigator(graph)
    
    # Recommendations for lesson1 should include lesson2 (shared concept: Force)
    recommendations = navigator.get_recommendations_for_content("lesson1")
    assert len(recommendations) >= 1
    assert "lesson2" in [node.id for node in recommendations]
    assert "lesson1" not in [node.id for node in recommendations]  # Should not recommend itself
    
    # Recommendations for lesson2 should include both lesson1 and lesson3
    recommendations = navigator.get_recommendations_for_content("lesson2")
    assert len(recommendations) >= 2
    assert "lesson1" in [node.id for node in recommendations]
    assert "lesson3" in [node.id for node in recommendations]
    assert "lesson2" not in [node.id for node in recommendations]  # Should not recommend itself
