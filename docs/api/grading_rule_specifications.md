# Grading Rule Specifications – AeroLearn AI

## Supported Question Types

- **Multiple Choice (MCQ)**
- **Text/NLP Response**
- **Code Submission**
- **Essay (manual/rubric)**

## Rules

### Multiple Choice (MCQ)

- Full credit (1.0): selected option matches the correct answer
- No credit (0.0): any other selection

### Text/NLP Response

- Full credit (1.0): response exactly matches expected answer (ignoring case/punctuation)
- Keyword-based:
    - All expected keywords present: full credit (1.0)
    - Some keywords matched: 0.5 + (0.5 × matched/total)
    - No keywords, non-empty answer: 0.5
    - Blank: 0.0

### Code Submission

- Full credit (1.0): code exactly matches expected solution (prototype evaluation only)
- No credit (0.0): any discrepancy (pending future sandbox/runner integration)

### Partial Credit & Rubrics

- If a rubric is attached, score is the sum of achieved criteria divided by sum of all possible criteria.
- Used for essay/manual questions.

## Partial Credit Example

If a question expects keywords ["force", "mass", "acceleration"]:
- A response matching "force" and "acceleration" but missing "mass" earns:  
  0.5 + (0.5 × 2/3) ≈ 0.83

## References

- Source: `/app/core/assessment/grading.py`
- Manual grading: See `/docs/api/manual_grading_procedures.md`