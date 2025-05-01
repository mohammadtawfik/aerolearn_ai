"""
File Location: /tests/core/ai/test_concept_extraction.py

Unit tests for the concept extraction module (/app/core/ai/concept_extraction.py)
Covers extraction logic, domain term bias, extraction-to-relationship mapping, and field merging.
"""

import pytest
from app.core.ai.concept_extraction import DomainConceptExtractor, Concept, extract_concept_relationships

class DummyContent:
    def __init__(self, title="", description="", body="", text=""):
        self.title = title
        self.description = description
        self.body = body
        self.text = text

def test_basic_extraction():
    ce = DomainConceptExtractor()
    content = DummyContent(
        title="Introduction to Aerodynamics",
        description="Principles of Lift and Drag.",
        body="Aerodynamic force and Bernoulli Principle are major topics."
    )
    results = ce.extract_from_content(content)
    names = {c.name.lower() for c in results}
    # Should catch domain-relevant words and capitalized phrases
    assert any("aerodynamics" in n or "aerodynamic" in n for n in names)
    assert "lift" in names
    assert "drag" in names
    assert "bernoulli" in names or "bernoulli principle" in names

def test_no_false_positives():
    ce = DomainConceptExtractor()
    content = DummyContent(title="a b c")
    results = ce.extract_from_content(content)
    # No valid concepts in nonsense input
    assert len(results) == 0

def test_confidence_range():
    ce = DomainConceptExtractor()
    c = list(ce.extract("Advanced Fluid Mechanics"))
    assert all(0.0 <= v.confidence <= 1.0 for v in c)

def test_domain_term_boost():
    """Test that domain terms are given higher confidence even if not capitalized."""
    ce = DomainConceptExtractor(domain_terms=['force', 'energy'])
    text = "The force and energy in a closed system remain constant."
    results = ce.extract(text)
    names = {c.name.lower() for c in results}
    # Both domain terms should be present
    assert "force" in names
    assert "energy" in names
    # Domain terms should have at least moderate confidence
    for c in results:
        if c.name.lower() in {"force", "energy"}:
            assert c.confidence > 0.5

def test_extract_relationships():
    """Test extraction of relationships between content and concepts."""
    ce = DomainConceptExtractor(domain_terms=['energy'])
    text = "The Law of Conservation of Energy states that energy cannot be created or destroyed."
    content_id = "lesson42"
    rels = extract_concept_relationships(content_id, text, ce)
    # Should produce tuples of (content_id, concept_name)
    assert all(isinstance(r, tuple) and r[0] == content_id for r in rels)
    # 'energy' should definitely be a relationship
    assert any(r[1].lower() == "energy" for r in rels)

def test_empty_text():
    ce = DomainConceptExtractor()
    concepts = ce.extract("")
    assert concepts == []

def test_no_duplicates():
    ce = DomainConceptExtractor(domain_terms=['force', 'energy'])
    text = "Force force Force. Energy energy."
    concepts = ce.extract(text)
    names = [c.name.lower() for c in concepts]
    # Should not return duplicates, just increased confidence/frequency
    assert len(set(names)) == len(names)

def test_content_extraction_combined_fields():
    ce = DomainConceptExtractor()
    content = DummyContent(
        title="Quantum Physics",
        description="Introduction to quantum mechanics and wave-particle duality.",
        body="The Schrödinger equation describes how quantum states evolve."
    )
    results = ce.extract_from_content(content)
    names = [c.name.lower() for c in results]
    assert "quantum physics" in names or "quantum" in names
    assert "wave-particle" in " ".join(names) or "wave" in names
    assert "schrödinger" in " ".join(names) or "schrodinger" in " ".join(names)

def test_concept_attributes():
    ce = DomainConceptExtractor()
    concepts = ce.extract("Einstein's Theory of Relativity")
    for c in concepts:
        assert hasattr(c, "name")
        assert hasattr(c, "confidence")
        assert hasattr(c, "metadata")
