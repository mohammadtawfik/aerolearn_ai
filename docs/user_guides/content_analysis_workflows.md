# Content Analysis Integration Testing & Workflows

This document provides a comprehensive guide to the content analysis capabilities of AeroLearn AI, focusing on the integration testing approach, results, and metrics for the content analysis pipeline.

## 1. Overview

Integration tests and selftests verify the end-to-end content analysis pipeline:
- Content extraction (from real documents)
- Embedding/vector representation generation
- Content similarity measurement
- Vector index/database querying
- Cross-component integration

## 2. Integration Testing Scope

Integration testing for the content analysis system ensures that all pipeline components work together as expected. The following key aspects are covered:

- **Similarity detection across content types** (TXT, DOCX, PDF, etc.)
- **Extraction pipeline verification with complex/real-world documents**
- **Vector search relevance and performance validation**
- **Cross-component access to similarity data**

## 3. Test Locations

- **Integration tests:**  
  `/tests/integration/test_content_analysis_integration.py`  
- **Selftest script:**  
  `/scripts/content_analysis_selftest.py`  
- **Demo fixtures:**  
  `/tests/fixtures/sample_content/` (must provide representative test files)

## 4. Running the Integration Tests

### With pytest
```shell
pytest tests/integration/test_content_analysis_integration.py
```

### With the Self-Test Script
```shell
python scripts/content_analysis_selftest.py
```

## 5. Key Tests & What Is Tested

- **Content Extraction Pipeline**  
  Verifies text extraction from all supported file formats (PDF, DOCX, images with OCR), using real on-disk files.
- **Embedding and Vector Index**  
  Ensures texts are embedded to the correct vector size and indexed, and that similarity search returns sensible results.
- **Similarity Across Content Types**  
  Checks that the similarity engine gives high scores to related documents and low scores to unrelated ones, across formats.
- **Vector Search Performance**  
  Measures the speed of vector searching to ensure it meets performance constraints (e.g., sub-2s for small collections).
- **Cross-Component Access**  
  Simulates realistic user queries and ensures the vector index, similarity calculation, and extraction all interoperate.

## 6. Example Test Outputs & Observations

- Extraction succeeds on TXT, DOCX, and PDF inputs (if libraries installed). Skips unsupported formats gracefully.
- Embedded vectors are always of the correct dimensionality; mismatches are detected immediately and fail fast.
- Similarity scores between related texts typically exceed 0.7 (cosine); scores for unrelated items remain below 0.5.
- Vector search retrieves relevant matches within 2 seconds for test-scale data (dozens to hundreds of vectors).
- Results are consistently repeatable using the default pipeline and embedder.

## 7. Metrics and Results Summary

| Test                        | Status    | Notes                                                                 |
|-----------------------------|-----------|-----------------------------------------------------------------------|
| Extraction Pipeline         | PASS      | Tested with TXT/DOCX/PDF; real-world data supported                   |
| Embedding & Indexing        | PASS      | Embeddings correctly sized & indexed; search returns relevant results |
| Similarity Calculation      | PASS      | Scores in expected range; threshold behavior consistent               |
| Vector Search Performance   | PASS      | All searches sub-2s for test scale                                    |
| Cross-Component Integration | PASS      | Components interact correctly; no data format errors                  |

## 8. How to Analyze Results

- Integration tests will **fail** if extraction or content similarity logic is broken
- Self-test script will **print out** similarity scores and retrieval results; scores close to 1 indicate high similarity
- Vector DB search results with the correct label/metadata prove end-to-end workflow
- **Integration test metrics** are recorded in the test output (see pytest logs for per-case timings)

## 9. Troubleshooting

- **Embedding dimension mismatch:** Ensure all uses of the embedder extract the embedding dimension dynamically at runtime, as in tests.
- **File extraction failures:** Confirm required libraries are installed for DOCX/PDF, or skip gracefully.
- **Slow vector search:** For large-scale ops, consider optimized vector DBs beyond the in-memory default.

## 10. Extending and Debugging

To add scenarios:
- Place more test files in `/tests/fixtures/sample_content/`
- Add new functions in `test_content_analysis_integration.py` to cover additional content types or edge cases

## 11. References

- Implementation: `/app/core/extraction/`, `/app/core/ai/embedding.py`, `/app/core/ai/content_similarity.py`, `/app/core/vector_db/`
- Tests: `/tests/integration/test_content_analysis_integration.py`
- Architecture/API Docs: `/docs/architecture/vector_db.md`, `/docs/api/vector_db_api.md`

---

_Last updated: 2024-06-14_
