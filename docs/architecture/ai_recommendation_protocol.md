# AI Recommendation Protocol  
**(Student Learning Path Recommendations)**

## Purpose

This protocol specifies the interfaces, required field names, expected method signatures, return types, and test/validation requirements for implementing Student Learning Path Recommendation functionality in AeroLearn AI.

---

## 1. API Scope

This protocol governs all code for:
- Personalized learning path generation
- Prerequisite/path sequencing
- Adaptive difficulty progression
- Personalized pace recommendations
- Cross-course content recommendations
- Curriculum-wide optimization suggestions

---

## 2. Core Concepts & Entities

- **LearningPathRecommendationEngine**: Main protocol-compliant service/class implementing learning path generation.
- **LearningPathRecommendation**: Result object or dict representing a recommended path.
- **LearningPathStep**: Each atomic step in the path—lesson, module, quiz, etc.
- **StudentProfile**: Lightweight protocol for student features leveraged (profile, completion, performance).
- **RecommendationContext**: Input struct/dict; must include at least user_id and/or StudentProfile, as well as available content IDs.

---

## 3. Method Signatures (Canonical)

The following method is protocol-mandated:

```python
def generate_learning_path(
    student: StudentProfile | dict,
    candidate_content: list,
    *,
    max_length: int = 10,
    adaptivity: bool = True
) -> LearningPathRecommendation:
    """
    Generates an ordered recommendation of content (lessons/modules/quizzes) as a personalized path for the given student.
    Args:
        student: StudentProfile or dict with schema defined below.
        candidate_content: List of content item descriptors (IDs, metadata, type, prerequisites, difficulty).
        max_length: Optional cap on length of the recommended path.
        adaptivity: If True, path should adapt for difficulty/pacing.
    Returns:
        LearningPathRecommendation: Dict with explicit fields below.
    """
```

### Input Entities

- **StudentProfile (dict required fields):**
    - `id` _(str)_: Unique user ID.
    - `level` _(str/int)_: User level/classification.
    - `completed_content` _(list[str])_: Content previously completed.
    - `performance` _(dict, optional)_: Mapping content ID -> metrics.
    - (Add extensible fields as needed for future personalization.)

- **Candidate Content (list[dict]):**
    - Each has:
      - `id` _(str)_: Unique content ID.
      - `type` _(str)_: Lesson, Module, Quiz, etc.
      - `prerequisites` _(list[str])_: IDs of prerequisite content.
      - `difficulty` _(str/int)_: For sequencing/adaptive decisions.
      - `metadata` _(dict, optional)_

### Output Entity

- **LearningPathRecommendation (dict):**
    - `student_id` _(str)_
    - `generated_at` _(RFC3339/timestamp as str)_
    - `steps` _(list[LearningPathStep])_

- **LearningPathStep (dict):**
    - `order` _(int)_: 1-based sequence position.
    - `content_id` _(str)_
    - `content_type` _(str)_
    - `justification` _(str)_: Brief rationale for this step's selection (prerequisite, pacing, review, etc.)
    - `difficulty` _(str/int)_
    - `prerequisites_satisfied` _(bool)_

---

## 4. Test/Validation Contract

Tests MUST:
- Exercise:
    - Path output for a variety of student profiles and candidate pools.
    - Sequencing requirements (no step with unsatisfied prerequisites).
    - Adaptive progression: verify changes when `adaptivity` is toggled.
    - Limit cases (path shorter than, equal to, or exceeding `max_length`).
    - Justification strings and prerequisites tracking are present and accurate.
- Validate all required fields are present in outputs (including step metadata and parent recommendation meta).
- Run as modular/unit tests at `/tests/unit/core/ai/test_learning_path.py`.

---

## 5. Privacy/Security

- All recommendation responses must only return documented fields.
- Do not leak internal model weights, debug info, or training/private annotations.

---

## 6. Documentation and Extensibility

- This protocol must be kept in sync with `/docs/development/day25_plan.md` and `/code_summary.md` as implementation surfaces arise.
- Extensions for explanation, alternative paths, or advanced personalization must be proposed via a protocol doc update.

---

## 7. Examples

### Minimal Input

```python
student = {
  "id": "stu-123",
  "level": "intro",
  "completed_content": ["mod1", "less1"],
}
candidate_content = [
  {"id": "less2", "type": "Lesson", "prerequisites": ["less1"], "difficulty": "easy"},
  {"id": "quiz1", "type": "Quiz", "prerequisites": ["less2"], "difficulty": "medium"}
]
```

### Expected Output (abbreviated)
```python
{
  "student_id": "stu-123",
  "generated_at": "2024-06-12T12:00:00Z",
  "steps": [
    {
      "order": 1,
      "content_id": "less2",
      "content_type": "Lesson",
      "justification": "Next lesson after completed: less1.",
      "difficulty": "easy",
      "prerequisites_satisfied": True
    },
    {
      "order": 2,
      "content_id": "quiz1",
      "content_type": "Quiz",
      "justification": "Review quiz after lesson: less2.",
      "difficulty": "medium",
      "prerequisites_satisfied": True
    }
  ]
}
```

---

## 8. Implementation Surface (Initial)

- Protocol-compliant engine should be implemented at `/app/core/ai/learning_path.py`.
- All TDD/unit tests reside at `/tests/unit/core/ai/test_learning_path.py`.
- Protocol updates must be cited in all code commits and cross-linked in `/code_summary.md` and `/docs/architecture/architecture_overview.md`.

---

## 9. Cross-Course Recommendation Engine Protocol

### Class: `CrossCourseRecommendationEngine`

#### API:
- `aggregate_cross_course_data(student_id: str, course_ids: list) -> Dict`
    *Aggregates relevant progress, content, and assessment data for a student across courses. Returns protocol fields keyed for recommendation engine.*
- `generate_cross_course_recommendations(student_id: str, course_ids: list, max_items: int = 10) -> List[Dict]`
    *Returns a unified, protocol-compliant list of recommended content/resources spanning the specified courses. Each result contains field-matched references, sources, and justifications.*
- `cross_reference_related_content(content_id: str, scope: list = None) -> List[Dict]`
    *Finds and outputs related content (by concept/skill/metadata) across courses, within the provided scope or globally.*
- `suggest_curriculum_optimizations(curriculum_id: str) -> Dict`
    *Analyzes all courses/content within a curriculum and outputs protocol-compliant optimization suggestions (sequence, redundancy, prerequisite gaps, etc.).*
- `clear()`: Clear engine cache/state.

#### Data Contracts

- **CrossCourseRecommendation:**
    - `student_id`: str
    - `recommended_items`: List[Dict]
        - Each item:
            - `content_id`: str
            - `course_id`: str
            - `title`: str
            - `justification`: str
            - `source`: str  # e.g., 'course', 'external', etc.
            - `score`: float (0..1)
            - `timestamp`: int (UTC)

- **CrossReferenceResult:**
    - `content_id`: str
    - `related_content`: List[Dict]
        - Each:
            - `content_id`: str
            - `course_id`: str
            - `similarity_score`: float (0..1)
            - `link_reason`: str

- **CurriculumOptimizationSuggestion:**
    - `curriculum_id`: str
    - `issues_found`: int
    - `optimizations`: List[Dict]  # e.g., {'type', 'description'}
    - `timestamp`: int (UTC)

#### Test-Driven Requirements (TDD)
- Modular/unit test: `/tests/unit/core/ai/test_crosscourse_reco.py`
- Integration test: `/tests/integration/ai/test_crosscourse_reco.py`
- End-to-end: Ensure unified engine, aggregation, and optimization APIs satisfy all required fields, with test scenarios for each.
- No code merged until API/fields/tests/doc are in sync.

#### Example Usage

```python
# Example usage of cross-course recommendation
engine = CrossCourseRecommendationEngine()

# Get recommendations across multiple courses
recommendations = engine.generate_cross_course_recommendations(
    student_id="stu-456",
    course_ids=["course-101", "course-202", "course-303"],
    max_items=5
)

# Example output
# {
#   "student_id": "stu-456",
#   "recommended_items": [
#     {
#       "content_id": "less-789",
#       "course_id": "course-202",
#       "title": "Advanced Data Structures",
#       "justification": "Builds on recently completed algorithms content",
#       "source": "course",
#       "score": 0.92,
#       "timestamp": 1656789012
#     },
#     ...
#   ]
# }

# Find related content across curriculum
related = engine.cross_reference_related_content(
    content_id="mod-555",
    scope=["course-101", "course-303"]
)

# Suggest curriculum optimizations
optimizations = engine.suggest_curriculum_optimizations(
    curriculum_id="curr-999"
)
```

---

## Status Update (Day 25 – Task 4.4.3)

- All API surfaces, required fields, and workflow logic for personalized material selection have been implemented and documented as per protocol (see `/app/core/ai/material_selection.py`).
- Modular/unit test suite (`/tests/unit/core/ai/test_material_selection.py`) covers all documented protocol scenarios and passes.
- No undocumented, extra, or missing fields remain for this workflow; protocol and implementation are synchronized.

## Status Update (Day 30 – Task 5.2.1)

- Cross-Course Recommendation Engine protocol has been defined with all required API surfaces, data contracts, and test requirements.
- Implementation pending at `/app/core/ai/cross_course_reco.py`.
- Test scaffolding created at `/tests/unit/core/ai/test_crosscourse_reco.py` and `/tests/integration/ai/test_crosscourse_reco.py`.

## Status Update (Day 35 – Task 5.3.2)

- All fields, APIs, and data models for cross-course recommendation/aggregation are now fully implemented.
- Implementation complete at `/app/core/ai/cross_course_reco.py` with all protocol-compliant interfaces.
- TDD and integration tests passing at `/tests/unit/core/ai/test_crosscourse_reco.py` and `/tests/integration/ai/test_crosscourse_reco.py`.
- All documentation and implementation are synchronized and in full protocol compliance.
- Cross-course recommendation engine successfully handles multi-course content aggregation, related content discovery, and curriculum optimization suggestions.
