"""
File Location: /tests/core/relationships/test_relationship_finder.py

Unit tests for RelationshipFinder.
"""

import pytest
from app.core.relationships.knowledge_graph import Node
from app.core.relationships.relationship_finder import RelationshipFinder

class Dummy:
    def __init__(self, prereq=None, references=None):
        self.prereq = prereq
        self.references = references

def test_relatedness():
    nodes = [Node("1", "Lift"), Node("2", "Aerodynamic Lift"), Node("3", "Drag")]
    rf = RelationshipFinder()
    edges = rf.find_relationships(nodes)
    assert any(e.relation == "related" for e in edges)

def test_prereq_and_references():
    nodes = [
        Node("1", "Aerodynamics", Dummy()),
        Node("2", "Lift", Dummy(prereq="Aerodynamics")),
        Node("3", "Drag", Dummy(references="Lift")),
    ]
    rf = RelationshipFinder()
    edges = rf.find_relationships(nodes)
    assert any(e.relation == "prerequisite" for e in edges)
    assert any(e.relation == "references" for e in edges)