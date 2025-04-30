# Content Similarity Module API

**Location:** `docs/api/content_similarity_api.md`

---

## Purpose

This API documentation describes the interfaces and callable functions for the AeroLearn AI content similarity foundation.

## Modules

### /app/core/ai/embedding.py

#### Classes

- `BaseEmbedder`
  - Abstract class for embedders.  
  - `embed(content)`: Abstract method.

- `TextEmbedder(BaseEmbedder)`
  - `embed(text: str) -> np.ndarray`: Embeds plain text into a vector.

- `DocumentEmbedder(BaseEmbedder)`
  - `embed(document_text: str) -> np.ndarray`: Embeds text extracted from a document.

- `MultimediaEmbedder(BaseEmbedder)`
  - `embed(metadata: dict) -> np.ndarray`: Embeds multimedia content based on metadata.

---

### /app/core/ai/content_similarity.py

#### Classes

- `SimilarityCalculator`
  - `cosine_similarity(vec1, vec2) -> float`
  - `jaccard_similarity(vec1, vec2) -> float`

#### Functions

- `calculate_similarity(content_a, content_b, content_type, metric, threshold)`
  - Embeds inputs and calculates similarity score.  
  - Returns `(score: float, match: bool)`.

- `cross_content_similarity(content_list_a, content_list_b, content_type, metric, threshold)`
  - Computes pairwise similarity for two lists.
  - Returns matrix of dicts: `{score, match}` per pair.

- `get_content_recommendations(target_content, candidate_contents, content_type, metric, top_k, threshold)`
  - Returns top-K similar items from candidates, with scores.

---

## Configuration

- Similarity threshold can be set per call or configured system-wide.
- Metrics: `"cosine"` (recommended) or `"jaccard"` (basic).

## Example Usage

```python
from app.core.ai.content_similarity import calculate_similarity, get_content_recommendations

text1 = "Principles of flight"
text2 = "Factors affecting aircraft lift"

score, is_match = calculate_similarity(text1, text2, content_type="text", metric="cosine", threshold=0.75)

recs = get_content_recommendations(
   target_content="Python basics",
   candidate_contents=["Intro to Python", "Advanced C++", "Python data structures"],
   content_type="text",
   metric="cosine",
   top_k=2,
   threshold=0.7
)
```

## Output Types and Guarantees

- All `'match'` fields in function outputs are guaranteed to be pure Python `bool` (never numpy types).
- Type-safe for use with strict Python checks and client code.

## Extending

- Implement new Embedders by subclassing `BaseEmbedder`.
- Add new metrics to `SimilarityCalculator`.

## Test Status

- All module and component tests have been run and **passed** as of 2024-06-13.

---

_For detailed design and revision history, refer to `/docs/architecture/content_similarity.md`._
