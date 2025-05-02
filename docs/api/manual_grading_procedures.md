# Manual Grading Procedures – AeroLearn AI

## Overview

This guide outlines the procedures for rubric-based and batch/manual grading as required for essay and complex open-ended questions.

## Workflow

1. **Assignment Viewer**
    - Professors or staff retrieve grading assignments from the `ManualGradingService`.
    - Viewer lists all sessions and questions requiring manual/rubric grading.

2. **Rubric Grading Tools**
    - Grader reviews student response and applies rubric criteria.
    - Each rubric criterion maps to a point score.

3. **Feedback Annotations**
    - Grader can annotate response with feedback, strengths, weaknesses, or notes.

4. **Batch Grading Workflow**
    - Multiple submissions may be selected and graded in a batch, reducing repetitive work.
    - Rubrics applied per-response; notes and scores stored per-student.

5. **Grading Finalization**
    - On grade completion, scores and feedback are made available to students.
    - Manual grades are integrated into the user's progress and feedback history.

6. **Audit & Analytics**
    - All manual grades and feedback are auditable.
    - Analytics available for grading turnaround and fairness tracking.

## Core APIs

- `ManualGradingService` (`app.core.assessment.manual_grading`)
- `Rubric` and assignment models (`app.models.assessment`)