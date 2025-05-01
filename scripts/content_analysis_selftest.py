"""
Content Analysis Self-Test Script for AeroLearn AI

This script runs integration checks for:
- Extraction and preprocessing of test data
- Embedding generation
- Similarity scoring
- Vector DB search/retrieval

Usage:
    python scripts/content_analysis_selftest.py

Save location: /scripts/content_analysis_selftest.py (per project structure)
"""

from app.core.extraction.text_extractor import TextExtractor
from app.core.ai.embedding import EmbeddingGenerator
from app.core.ai.content_similarity import ContentSimilarityCalculator
from app.core.vector_db.vector_db_client import VectorDBClient

def main():
    # Example minimal content for demonstration; can be replaced by CLI args or config auto-discovery
    docs = [
        ("Sample PDF", "tests/fixtures/sample_content/sample_lecture_notes.pdf"),
        ("Sample DOCX", "tests/fixtures/sample_content/sample_report.docx"),
    ]
    extractor = TextExtractor()
    emb_gen = EmbeddingGenerator()
    similarity_calc = ContentSimilarityCalculator()
    vector_db = VectorDBClient()

    embeddings = {}
    print("===== Extraction and Embedding =====")
    for label, path in docs:
        try:
            text = extractor.extract(path)
            embedding = emb_gen.embed(text)
            embeddings[label] = embedding
            vector_db.add_vector(embedding, metadata={"label": label, "path": path})
            print(f"[OK] {label}: Extracted, embedded, and indexed.")
        except Exception as e:
            print(f"[FAIL] {label}: {e}")

    print("\n===== Similarity Analysis =====")
    labels = list(embeddings.keys())
    if len(labels) >= 2:
        sim = similarity_calc.similarity_score(embeddings[labels[0]], embeddings[labels[1]])
        print(f"Similarity between '{labels[0]}' and '{labels[1]}': {sim:.3f}")
    else:
        print("Not enough embeddings for similarity scoring.")

    print("\n===== Vector DB Search Demo =====")
    try:
        results = vector_db.search(embeddings[labels[0]], top_k=2)
        for result in results:
            print(f"Found: {result['metadata'].get('label')} (score: {result.get('score', 'N/A')})")
    except Exception as e:
        print(f"Search error: {e}")

    print("\n===== Selftest Complete =====")

if __name__ == "__main__":
    main()