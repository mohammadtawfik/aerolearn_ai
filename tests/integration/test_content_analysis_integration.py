
"""
Integration tests for AeroLearn AI content analysis pipeline.

Save this file as: /tests/integration/test_content_analysis_integration.py

Changes:
- Only create a PDF if fpdf is actually present; otherwise skip PDF-related tests.
- Use the project-standard embedder (`TextEmbedder().embed()`) for text embeddings.
- All extractor calls use real filepaths to real files created in the test environment
- All vector index build/batch calls now use dicts of IDs to vectors/metadata, matching add_bulk signature

--- PATCHED/FIXED for vector dimension error ---
- Dynamically determine embedding dimension from TextEmbedder
- Ensure vector_index is always constructed with the actual embedding size
- This makes the integration test robust to changes in embedder model.
"""

import time
import pytest
from pathlib import Path

from app.core.extraction.text_extractor import TextExtractor
from app.core.ai.embedding import TextEmbedder
from app.core.vector_db.index_manager import VectorIndexManager
from app.core.ai.content_similarity import ContentSimilarityCalculator

@pytest.fixture
def example_docs(tmp_path):
    docs = []
    # TXT file
    txt_fp = tmp_path / "lecture1.txt"
    txt_content = "Introduction to Aerospace Engineering...\n[Full lecture text here for testing.]"
    txt_fp.write_text(txt_content, encoding="utf-8")
    docs.append(("lecture1.txt", str(txt_fp)))
    # DOCX file
    try:
        import docx
        docx_fp = tmp_path / "quiz.docx"
        doc = docx.Document()
        doc.add_paragraph("Q1: What is lift? A: Lift is the force that opposes gravity...")
        doc.save(str(docx_fp))
        docs.append(("quiz.docx", str(docx_fp)))
    except ImportError:
        pass  # Don't add DOCX if not present
    # PDF file
    try:
        from fpdf import FPDF
        pdf_fp = tmp_path / "summary.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, "Summary: Aerospace is the science of flight...\nMulti-line PDF content for testing.")
        pdf.output(str(pdf_fp))
        docs.append(("summary.pdf", str(pdf_fp)))
    except ImportError:
        pass  # Don't add PDF if PDF library isn't present
    return docs

@pytest.fixture
def embedding_dim():
    # Dynamically detect embedding dimension
    # Use a representative text to get output shape
    embedder = TextEmbedder()
    dummy_text = "dummy text for embedding dimension detection"
    emb = embedder.embed(dummy_text)
    if hasattr(emb, "shape"):
        return emb.shape[0]
    return len(emb)

@pytest.fixture
def vector_index(embedding_dim):
    # Always construct with detected embedding dimension
    return VectorIndexManager(embedding_dim)

def make_id(fname, idx):
    """Guarantee unique, reproducible ID for each example vector."""
    return f"{fname}_{idx}"

def test_content_extraction_pipeline(example_docs):
    extractor = TextExtractor()
    extracted = []
    for fname, fpath in example_docs:
        text = extractor.extract_text(fpath)
        assert isinstance(text, str)
        assert len(text) > 20
        extracted.append(text)

def test_embedding_and_vector_index(example_docs, vector_index):
    extractor = TextExtractor()
    embedder = TextEmbedder()

    embeddings_dict = {}
    metadatas_dict = {}
    
    for i, (fname, fpath) in enumerate(example_docs):
        text = extractor.extract_text(fpath)
        embedding = embedder.embed(text)
        vid = make_id(fname, i)
        embeddings_dict[vid] = embedding
        metadatas_dict[vid] = {"filename": fname}

    vector_index.build_index(embeddings_dict, metadatas=metadatas_dict)

    query_text = "What is aerospace?"
    query_vec = embedder.embed(query_text)
    results = vector_index.search(query_vec, top_k=2)
    assert isinstance(results, list)
    assert len(results) >= 1

def test_similarity_across_content_types(example_docs, embedding_dim):
    extractor = TextExtractor()
    embedder = TextEmbedder()
    similarity_calculator = ContentSimilarityCalculator()

    # Test does not actually build a vector index, but we need correct dimensionality for embeddings

    texts = [extractor.extract_text(fpath) for _, fpath in example_docs]
    embeddings = [embedder.embed(t) for t in texts]
    sim_scores = []
    for i in range(len(embeddings)):
        for j in range(i+1, len(embeddings)):
            score = similarity_calculator.similarity_score(embeddings[i], embeddings[j], metric="cosine")
            assert 0.0 <= score <= 1.0
            sim_scores.append(score)
    if sim_scores:  # Only assert if there are pairs
        assert any(s > 0.5 for s in sim_scores)

def test_vector_search_performance(example_docs, embedding_dim):
    extractor = TextExtractor()
    embedder = TextEmbedder()
    # Use dynamic dimension
    vector_index = VectorIndexManager(embedding_dim)
    embeddings_dict = {}
    
    for _ in range(10):  # Lower scale for integration environment
        for i, (fname, fpath) in enumerate(example_docs):
            text = extractor.extract_text(fpath)
            embedding = embedder.embed(text)
            vid = make_id(fname, i) + f"_r{_}"
            embeddings_dict[vid] = embedding
            
    vector_index.build_index(embeddings_dict)
    query_text = "What is lift?"
    query_vec = embedder.embed(query_text)
    start = time.time()
    results = vector_index.search(query_vec, top_k=5)
    duration = time.time() - start
    assert duration < 2.0
    assert len(results) >= 1

def test_cross_component_access(example_docs, embedding_dim):
    extractor = TextExtractor()
    embedder = TextEmbedder()
    similarity_calculator = ContentSimilarityCalculator()
    vector_index = VectorIndexManager(embedding_dim)

    embeddings_dict = {}
    for i, (fname, fpath) in enumerate(example_docs):
        text = extractor.extract_text(fpath)
        emb = embedder.embed(text)
        vid = make_id(fname, i)
        embeddings_dict[vid] = emb
        
    vector_index.build_index(embeddings_dict)
    query = "Explain the concept of lift in aerospace."
    query_emb = embedder.embed(query)
    results = vector_index.search(query_emb, top_k=3)
    
    for res in results:
        # result is (id, score, meta)
        if isinstance(res, (tuple, list)) and len(res) >= 1:
            res_id = res[0]
            result_vec = embeddings_dict.get(res_id)
            if result_vec is not None:
                sim = similarity_calculator.similarity_score(query_emb, result_vec, metric="cosine")
                assert 0.0 <= sim <= 1.0
