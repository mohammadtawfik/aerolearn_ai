# Content Optimization Protocol  
**(Content Improvement Suggestions & Analytics)**

## Purpose

Defines the canonical API, method surface, required arguments/returns, field contract, and TDD validation requirements for all content optimization suggestion features in AeroLearn AI.

---

## 1. API Scope

Covers:
- Suggestion of improvements for educational content (text, problem sets, quizzes, lectures, etc.)
- Application of enhancement templates (clarity, engagement, accessibility, depth, etc.)
- Tracking and previewing before/after changes
- Analytics of optimization frequency, acceptance, and efficacy

---

## 2. Core Entities & Structures

- **ContentOptimizationEngine**: Main protocol-surfaced component (class/module/function) producing optimization suggestions and analytics.
- **ContentOptimizationSuggestion**: The result object/dict for a single suggestion.
- **ContentImprovementWorkflow**: A batch of suggestions or an orchestrated surface for suggestion previews and acceptance tracking.
- **OptimizationContext**: Input struct/dict; contains content item data, metadata, user/editor ID, improvement goals, and constraints.

---

## 3. Main Method: Canonical Signature

```python
def suggest_content_optimizations(
    content_item: dict,
    *,
    templates: list = None,
    context: dict = None
) -> dict:
    """
    Generate protocol-compliant optimization suggestions for the provided content.
    Args:
        content_item: Required. Dict with keys below ("id", "type", "body", "metadata").
        templates: Optional. List of template/tag names to focus suggestions (e.g. ["clarity", "engagement", "accessibility"]).
        context: Optional. Dict describing editor/user, workflow state, or constraints.
    Returns:
        ContentOptimizationSuggestion: Dict, see below.
    """
```

### Input (`content_item`) Required Fields

- `id` (str): Unique ID of the content to optimize
- `type` (str): Content type, e.g. "Lesson", "Quiz", "Text", etc.
- `body` (str): Main content text/HTML/markdown
- `metadata` (dict, optional): Per-content metadata, tags, language, difficulty, etc.

### Input (`templates`) (Optional)

- List of named improvements to be prioritized (defaults: all supported if None)
  - Supported template names: "clarity", "engagement", "accessibility", "depth", "brevity", "accuracy", "readability", "diversity", "formatting", "examples", "multimedia".

### Input (`context`) (Optional)

- `editor_id` (str): Optional, for auditing.
- `goals` (list[str]): List of desired improvement goals as requested by user/editor.
- `constraints` (dict): Constraints to avoid (e.g. language level, length cap).
- Other extensible fields as workflow evolves.

### Output (`ContentOptimizationSuggestion`)

- `content_id` (str): Must match `content_item["id"]`
- `suggestions` (list of SuggestionStep):
    - Each SuggestionStep is a dict:
        - `template` (str): Name of template/rule applied.
        - `before` (str): Excerpt/section before suggestion.
        - `after` (str): New proposed/optimized excerpt/section.
        - `explanation` (str): Why change is suggested (brief, human-readable).
        - `score_delta` (float, optional): Projected improvement (e.g. readability score, engagement estimate).
- `overall_analysis` (dict):
    - `original_score` (float, optional): Baseline analytic score (if applicable e.g., readability, Flesch–Kincaid, etc.)
    - `expected_score` (float, optional): Post-optimization analytic value
    - `tags` (list[str]): Keywords summarizing major focus areas
    - `preview_html` (str, optional): HTML preview (diff or improved full text)
- `generated_at` (str): RFC3339 timestamp.

---

## 4. Test/Validation Contract

- Tests are placed in `/tests/unit/core/ai/test_content_optimization.py`.
- Test input scenarios must cover:
    - Content with multiple eligible templates and goals.
    - Preview consistency (output must include "before", "after", and "explanation" for each suggestion).
    - No changes suggested if content is already optimal for requested templates (valid "no-op" case).
    - Fields/types are present and correct, even for empty output (no missing required keys).
    - Output/batch structure consistent for single and multiple suggestions.
    - Timestamps format is RFC3339 (as for other protocol outputs).
    - Score deltas/analytic projections only present if calculated.

---

## 5. Privacy/Security

- No suggestion should leak internal metrics, debug info, or unrequested user data.
- All fields returned must be protocol-documented.  
- No unintended exposure of full historical editorial suggestions (unless specifically enabled by workflow).

---

## 6. Documentation & Extensibility

- Any field, template, or analytic extension must update this protocol doc and cite in commits and summary docs.
- Cross-link with architecture overview and code_summary after every major implementation.
- Advanced preview integrations (e.g. multimedia diff, code block formatting) require protocol proposal/extension.

---

## 7. Example

### Input

```python
content_item = {
    "id": "less3",
    "type": "Lesson",
    "body": "The cat sat.",
    "metadata": {"difficulty": "easy"}
}
templates = ["clarity", "engagement"]
context = {"editor_id": "prof001", "goals": ["clarify", "make interactive"]}
```

### Output Example

```python
{
    "content_id": "less3",
    "suggestions": [
        {
            "template": "clarity",
            "before": "The cat sat.",
            "after": "The cat sat peacefully by the window.",
            "explanation": "Added detail to clarify setting."
        },
        {
            "template": "engagement",
            "before": "The cat sat peacefully by the window.",
            "after": "Can you picture the cat sitting peacefully by the window?",
            "explanation": "Engages the learner with a question."
        }
    ],
    "overall_analysis": {
        "original_score": 60.0,
        "expected_score": 80.0,
        "tags": ["clarity", "engagement"],
        "preview_html": "<span class='highlight'>The cat sat peacefully by the window.</span> Can you picture the cat sitting peacefully by the window?"
    },
    "generated_at": "2024-06-13T10:00:00Z"
}
```

---

## 8. Implementation Surface

- Implementation/class lives at `/app/core/ai/content_optimization.py`.
- Tests reside at `/tests/unit/core/ai/test_content_optimization.py`.
- Protocol updates and rationale must be cited in `/code_summary.md` and `/docs/architecture/architecture_overview.md`.