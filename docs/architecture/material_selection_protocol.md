# Material Selection Protocol  
**(Personalized Content Matching for Learners)**

## Purpose

Specifies the interfaces, method signatures, canonical input/output fields, contract requirements, and TDD/test surface for all personalized material selection features in AeroLearn AI.

---

## 1. API Scope

This protocol governs:
- Automated or semi-automated selection of educational materials personalized by student profile, learning style, and engagement history.
- Material-content style matching, content filtering, and adaptive presentation integration.
- Support for future collaboration between user-facing material selection and backend analytics/monitoring.

---

## 2. Core Entities & Structures

- **MaterialSelectionEngine**: Protocol-compliant class/module/function responsible for recommending a filtered/personalized subset and ordering of supplied content for a student.
- **MaterialSelectionResult**: Result object/dict summarizing output.
- **MaterialSelectionStep**: Each recommended item and rationale.
- **StudentProfile**: Same baseline definition as other protocols: id, level, completed_content, learning_style, performance (see below).
- **MaterialSelectionContext**: Optional extra controls on filtering, priorities, tracking, or integration points.

---

## 3. Main Method: Canonical Signature

```python
def select_personalized_materials(
    student: dict,
    candidate_content: list,
    *,
    context: dict = None,
    max_items: int = 10
) -> dict:
    """
    Select and sequence the most appropriate subset of candidate materials for a student, based on protocol-defined learning style and history.
    Args:
        student: Required. StudentProfile or dict (fields below).
        candidate_content: List of content descriptors (dicts with fields below).
        context: Optional. Dict for additional priorities, exclusions, analytics integration.
        max_items: Optional. Cap on number of recommended materials.
    Returns:
        MaterialSelectionResult (fields below).
    """
```

### Input: StudentProfile (dict) [required fields]

- `id` (str)
- `level` (str/int)
- `completed_content` (list[str])
- `performance` (dict, optional): content_id -> metric(s)
- `learning_style` (str, optional): e.g. "visual", "auditory", "kinesthetic", "reading/writing", etc.
- (extensible as future personalization fields added)

### Input: candidate_content (list[dict])

Each item:
  - `id` (str): Content ID
  - `type` (str): "Lesson", "Video", "Reading", "Quiz", etc.
  - `tags` (list[str], optional): Content characteristics (e.g., "visual", "applied", "quiz", "theoretical")
  - `difficulty` (str/int): Protocolized value for adaptation
  - `format` (str, optional): e.g. "video", "reading", "interactive", "demo", etc.
  - `metadata` (dict, optional)

### Input: context (dict, optional)

May include:
- `required_style` (str): e.g., only match materials with this style/format.
- `exclude_ids` (list[str]): Explicitly filter out specified content items.
- `prioritize_tags` (list[str]): List of tags to boost in ranking.
- `presentation_mode` (str): e.g., "adaptive", "standard", etc.

---

## 4. Output: MaterialSelectionResult (dict)

- `student_id` (str): Echo input.
- `selected_materials` (list[MaterialSelectionStep]): Ordered material subset with justifications.
- `generated_at` (str): RFC3339 timestamp.
- `selection_context` (dict): Echo relevant effective fields/filters/tags used.

### Each MaterialSelectionStep (dict):

- `order` (int): 1-based sequence.
- `content_id` (str)
- `content_type` (str)
- `format` (str, optional)
- `reason` (str): Rationale for inclusion and relative ranking (matches learning style, completion gap, performance, etc.)
- `score` (float, optional): Relative or absolute score if ranking logic is applied.

---

## 5. Test/Validation Contract

- Tests must reside in `/tests/unit/core/ai/test_material_selection.py`.
- TDD must exercise:
    - Selection changes for different learning styles / context toggles.
    - Exclusion of completed/excluded content.
    - Tag, style, and format preference enforcement.
    - Length cap enforcement (`max_items`).
    - Field contract and required output fields.
    - Rationale/reason field meaningful for every selected material.
    - Timestamp must be RFC3339.

---

## 6. Privacy/Security

- Recommendations must not leak internal model weights, debug traces, or user private data.
- Output only documented fields, with all filtering and rationale explainable at the API surface.

---

## 7. Documentation, Audit, & Extensibility

- All protocol/candidate/test surfaces must be cross-referenced in `/code_summary.md` and `/docs/architecture/architecture_overview.md`.
- Extensions (new style types, relevance explainability, batch analytics, etc.) require doc update & TDD/test addition.

---

## 8. Example

### Input

```python
student = {
    "id": "stu-456",
    "level": "advanced",
    "completed_content": ["mod2", "read1"],
    "learning_style": "visual"
}
candidate_content = [
    {"id": "vid1", "type": "Lesson", "format": "video", "tags": ["visual"], "difficulty": "medium"},
    {"id": "read1", "type": "Reading", "format": "reading", "tags": ["reading"], "difficulty": "easy"},
    {"id": "quiz2", "type": "Quiz", "tags": ["applied"], "difficulty": "hard"},
]
context = {"required_style": "visual"}
```

### Output

```python
{
    "student_id": "stu-456",
    "selected_materials": [
        {
            "order": 1,
            "content_id": "vid1",
            "content_type": "Lesson",
            "format": "video",
            "reason": "Matches preferred learning style 'visual' and is not completed.",
            "score": 0.95
        }
    ],
    "generated_at": "2024-06-13T11:00:00Z",
    "selection_context": {
        "required_style": "visual"
    }
}
```

---

## 9. Implementation Surface

- Implementation/class/module lives at `/app/core/ai/material_selection.py`.
- Tests reside at `/tests/unit/core/ai/test_material_selection.py`.
- Protocol/test/impl cross-referenced in `/code_summary.md` and `/docs/architecture/architecture_overview.md`.