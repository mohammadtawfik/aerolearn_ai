"""
File Location: /app/core/ai/concept_extraction.py

Implements concept extraction from educational content (required for Task 13.2: Content Relationship Mapping).

This component identifies key concepts, entities, and skills from Content models.
"""

from typing import List, Dict, Any, Set, Tuple
import re
import unicodedata
from collections import Counter

def _normalize_term(term: str) -> str:
    """
    Basic lemmatization to normalize terms (e.g., plurals to singular form).
    
    Args:
        term: The term to normalize
        
    Returns:
        Normalized form of the term
    """
    term = term.lower()
    # Remove simple plurals
    if term.endswith('es') and len(term) > 3 and term[:-2] + 'e' != term:  # avoid 'cheese'->'chee'
        if term[:-2] in ['forc', 'wav', 'quiz', 'box', 'lux', 'bus']:
            term = term[:-2]
        else:
            term = term[:-1]  # default fallback
    elif term.endswith('s') and len(term) > 2 and not term.endswith('ss'):
        term = term[:-1]
    return term


def normalize_to_ascii(s: str) -> str:
    """
    Remove accents/diacritics and lower-case.
    
    Args:
        s: The string to normalize
        
    Returns:
        ASCII-normalized lowercase string
    """
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()

class Concept:
    """
    Represents an extracted concept (e.g., term, skill, entity).
    """
    def __init__(self, name: str, confidence: float = 1.0, metadata: Dict[str, Any]=None):
        self.name = name
        self.confidence = confidence
        self.metadata = metadata or {}

    def __repr__(self):
        return f"Concept(name={self.name!r}, confidence={self.confidence:.2f})"

    def to_dict(self):
        return {"name": self.name, "confidence": self.confidence, "metadata": self.metadata}


class ConceptExtractor:
    """
    Base class for concept extractors.
    """
    def extract(self, text: str) -> List[Concept]:
        """Extract concepts from text."""
        raise NotImplementedError("Subclasses must implement extract()")
    
    def extract_from_content(self, content: Any) -> List[Concept]:
        """
        Pulls appropriate text fields from a Content or Lesson object, then extracts.
        """
        fields = []
        for key in ('title', 'description', 'body', 'text'):
            v = getattr(content, key, None)
            if v and isinstance(v, str):
                fields.append(v)
        merged = " ".join(fields)
        return self.extract(merged)


class PatternConceptExtractor(ConceptExtractor):
    """
    Extracts concepts from text using regex patterns.
    For MVP: improved keyword/phrase extraction with extensibility hooks.
    Extracts both compound phrases and their components.
    """

    # Match capitalized phrases (e.g., "Aerodynamics Principles")
    PHRASE_PATTERN = r"\b(?:[A-Z][a-z]{2,}(?: [A-Z][a-z]{2,})+)\b"
    # Match single capitalized words (e.g., "Aerodynamics", "Drag")
    SINGLE_WORD_PATTERN = r"\b[A-Z][a-z]{2,}\b"

    def __init__(self, custom_patterns: List[str]=None):
        self.patterns = [
            self.PHRASE_PATTERN,
            self.SINGLE_WORD_PATTERN,
            *(custom_patterns or [])
        ]
    
    def extract(self, text: str) -> List[Concept]:
        """
        Returns list of Concepts extracted from the text.
        Extracts both composite phrases and their individual components.
        """
        found: Set[str] = set()
        results: List[Concept] = []

        # 1. Extract phrases first
        for match in re.findall(self.PHRASE_PATTERN, text):
            cleaned = match.strip()
            key = cleaned.lower()
            if len(cleaned) > 1 and key not in found:
                found.add(key)
                confidence = min(1.0, max(0.7, len(cleaned)/30))
                results.append(Concept(cleaned, confidence=confidence))

            # Extract individual words inside phrase
            for word in cleaned.split():
                word_key = word.lower()
                if len(word) > 1 and word_key not in found:
                    found.add(word_key)
                    # Slightly lower confidence for sub-components
                    sub_confidence = min(0.95, max(0.7, len(word)/15))
                    results.append(Concept(word, confidence=sub_confidence))

        # 2. Extract single capitalized words NOT part of previously matched phrases
        for match in re.findall(self.SINGLE_WORD_PATTERN, text):
            cleaned = match.strip()
            key = cleaned.lower()
            if len(cleaned) > 1 and key not in found:
                found.add(key)
                confidence = min(1.0, max(0.7, len(cleaned)/15))
                results.append(Concept(cleaned, confidence=confidence))

        return results


class DomainConceptExtractor(ConceptExtractor):
    """
    Extracts concepts from a set of provided domain terms.
    - Matches are accent/diacritic-insensitive (so schrodinger matches Schrödinger)
    - Handles plurals, compounds, and hyphen-joined words robustly
    - Only the canonical domain term spelling appears in result Concept names
    """
    def __init__(self, domain_terms: List[str] = None, top_n: int = 20):
        """
        Initialize with domain-specific terms.
        
        Args:
            domain_terms: List of domain-specific key terms (e.g., science vocabulary)
            top_n: Default maximum number of concepts to return
        """
        domain_terms = domain_terms or []
        self.top_n = top_n
        
        # Store original domain terms with their original case
        self.domain_terms_raw = [dt for dt in domain_terms]
        self.domain_terms = [dt.lower() for dt in domain_terms]
        
        # ASCII-normalized form for all domain terms (for accent-robust matching)
        self.domain_terms_ascii = [normalize_to_ascii(dt) for dt in self.domain_terms]
        
        # Map all ASCII-normalized spellings to the canonical domain spelling
        self.ascii_to_canonical: Dict[str, str] = {
            ascii_dt: orig_dt
            for ascii_dt, orig_dt in zip(self.domain_terms_ascii, self.domain_terms_raw)
        }
        
        # Handle plurals and other variants
        for dt, ascii_dt in zip(self.domain_terms_raw, self.domain_terms_ascii):
            # Simple plurals (s)
            self.ascii_to_canonical[ascii_dt + 's'] = dt
            
            # Special case plurals (es)
            if ascii_dt.endswith(('ch', 'sh', 'x', 'z', 'ss')):
                self.ascii_to_canonical[ascii_dt + 'es'] = dt
                
            # Handle -y to -ies conversion
            if ascii_dt.endswith('y') and len(ascii_dt) > 1 and ascii_dt[-2] not in 'aeiou':
                self.ascii_to_canonical[ascii_dt[:-1] + 'ies'] = dt
                
            # Add normalized forms
            norm_dt = _normalize_term(ascii_dt)
            if norm_dt != ascii_dt:
                self.ascii_to_canonical[norm_dt] = dt

    def extract(self, text: str, top_n: int = None) -> List[Concept]:
        """
        Extracts concepts from the given text, but only returns canonical domain terms.

        Args:
            text: The educational content as a string.
            top_n: Max number of extracted concepts to return (overrides default).

        Returns:
            List[Concept]: List of Concept objects with canonical domain term names
        """
        if top_n is None:
            top_n = self.top_n
            
        # Normalize text for matching
        norm_text = unicodedata.normalize("NFKC", text.lower())
        ascii_text = normalize_to_ascii(norm_text)
        
        # Extract all words and calculate frequencies
        tokens = re.findall(r"\b[\w-]+\b", norm_text)
        ascii_tokens = [normalize_to_ascii(tok) for tok in tokens]
        word_counts = Counter(tokens)
        
        # Track found canonical domain terms
        found_terms = set()
        term_frequencies = {}
        
        # 1. Exact token/ascii-token matches, including plurals
        for token, ascii_token in zip(tokens, ascii_tokens):
            canonical = self.ascii_to_canonical.get(ascii_token)
            if canonical:
                found_terms.add(canonical)
                term_frequencies[canonical] = term_frequencies.get(canonical, 0) + word_counts[token]
        
        # 2. Substring (domain in any ascii token, hyphenated/compound match)
        for token, ascii_token in zip(tokens, ascii_tokens):
            for ascii_dt, canonical in self.ascii_to_canonical.items():
                if canonical in found_terms:
                    continue
                    
                # Check if domain term is part of a compound/hyphenated word
                if ascii_dt in ascii_token:
                    # Check if it's a standalone part (at start, end, or between hyphens)
                    if (ascii_token.startswith(ascii_dt + '-') or 
                        ascii_token.endswith('-' + ascii_dt) or 
                        ('-' + ascii_dt + '-') in ascii_token):
                        found_terms.add(canonical)
                        term_frequencies[canonical] = term_frequencies.get(canonical, 0) + 1
        
        # 3. Multi-word domain terms in ascii text directly
        for ascii_dt, canonical in self.ascii_to_canonical.items():
            if ' ' in ascii_dt and ascii_dt in ascii_text and canonical not in found_terms:
                found_terms.add(canonical)
                # Count occurrences of the exact phrase
                count = len(re.findall(r'\b' + re.escape(ascii_dt) + r'\b', ascii_text))
                term_frequencies[canonical] = max(1, count)
        
        # Create concepts from found terms
        concepts = []
        max_freq = max(term_frequencies.values()) if term_frequencies else 1
        
        for term in found_terms:
            freq = term_frequencies.get(term, 1)
            confidence = min(1.0, freq / max_freq)
            
            # Boost multi-word terms slightly
            if ' ' in term:
                confidence = min(1.0, confidence * 1.1)
                
            concepts.append(Concept(
                name=term,  # Always use the canonical domain term
                confidence=confidence,
                metadata={"frequency": freq}
            ))
            
        # Sort by confidence and return top results
        return sorted(concepts, key=lambda c: c.confidence, reverse=True)[:top_n]


def extract_concept_relationships(content_id: str, text: str, extractor: ConceptExtractor) -> List[Tuple[str, str]]:
    """
    Identify relationships (content_id <-> concept) using the extractor.

    Args:
        content_id: The identifier for the material (lesson, quiz, etc)
        text: The source text
        extractor: The concept extractor

    Returns:
        List of (content_id, concept_name) tuples representing relationships
    """
    concepts = extractor.extract(text)
    return [(content_id, concept.name) for concept in concepts]
