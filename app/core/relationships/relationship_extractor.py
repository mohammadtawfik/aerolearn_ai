"""
Implements concept-to-content and inter-concept relationship extraction.

Location: /app/core/relationships/relationship_extractor.py
"""

from typing import List, Any

class ConceptRelationship:
    """
    Represents a relationship between two concepts or between a concept and a content object.
    """
    def __init__(self, source, target, rel_type: str = "associated", metadata=None):
        self.source = source
        self.target = target
        self.rel_type = rel_type  # e.g., 'prerequisite', 'related', 'mentions', 'explains'
        self.metadata = metadata or {}

    def __repr__(self):
        return f"ConceptRelationship({self.source!r} -[{self.rel_type}]-> {self.target!r})"

class RelationshipExtractor:
    """
    Extracts explicit and implicit relationships between concepts or content.
    """
    def extract_content_relationships(self, content_obj, concepts: List[Any]) -> List[ConceptRelationship]:
        """
        Link a content object to all extracted concepts.
        rel_type: "covers" or "mentions"
        """
        relationships = []
        for concept in concepts:
            relationships.append(
                ConceptRelationship(source=content_obj, target=concept, rel_type="covers")
            )
        return relationships

    def extract_interconcept_relationships(self, concepts: List[Any]) -> List[ConceptRelationship]:
        """
        Detect relationships like 'related', 'prerequisite', etc. between concepts.
        For MVP, relate all pairs as 'related' (later enhance with AI/NLP).
        """
        relationships = []
        for i, c1 in enumerate(concepts):
            for j, c2 in enumerate(concepts):
                if i != j:
                    relationships.append(
                        ConceptRelationship(source=c1, target=c2, rel_type="related")
                    )
        return relationships