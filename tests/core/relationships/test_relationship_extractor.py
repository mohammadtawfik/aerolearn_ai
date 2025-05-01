import pytest
from app.core.relationships.relationship_extractor import RelationshipExtractor, ConceptRelationship

class DummyContent:
    def __init__(self, id, title): self.id, self.title = id, title
    def __repr__(self): return f"DummyContent(id={self.id}, title={self.title!r})"

class DummyConcept:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name

def test_content_relationships():
    rc = RelationshipExtractor()
    dc = DummyContent("11", "Intro to Engineering")
    concepts = [DummyConcept("Force"), DummyConcept("Energy")]
    rels = rc.extract_content_relationships(dc, concepts)
    assert all(isinstance(r, ConceptRelationship) for r in rels)
    assert rels[0].source == dc and rels[0].target == concepts[0]
    assert rels[0].rel_type == "covers"

def test_interconcept_relationships():
    rc = RelationshipExtractor()
    concepts = [DummyConcept("Newton's Laws"), DummyConcept("Friction")]
    rels = rc.extract_interconcept_relationships(concepts)
    assert all(r.rel_type == "related" for r in rels)
    # Each concept related to the other
    assert len(rels) == 2