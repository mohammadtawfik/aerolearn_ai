# Intervention Suggestion System API

**Location:** `/docs/api/interventions_api.md`

## Overview

This API supports programmatic suggestion and creation of learning interventions for at-risk students.

## Key Functions

- `early_warning_indicator(student)`
    - Returns: `bool`
    - Detects simple early warning criteria.

- `recommend_resources(student, weakness_areas)`
    - Returns: `List[str]`
    - Suggests content/resource IDs tailored to identified weaknesses.

- `suggest_learning_path(student, objectives)`
    - Returns: `List[str]`
    - Sequenced pathway of lesson IDs for the objectives.

- `notify_professor_at_risk_students(professor, students_at_risk)`
    - Notifies professor by mutating/providing data.

- `create_intervention(student_id, pattern)`
    - Returns dict: `{ "student_id": ..., "type": ..., "intervention": ... }`
    - Encapsulates pattern for unified downstream handling.

## Implementation Locations

All APIs implemented in:  
- `app/core/monitoring/interventions.py`

## Usage Flow

1. Call `run_pattern_detection`/aggregate.
2. On risk detection, use `create_intervention` and notify as needed.

## Extension

- Override or extend `create_intervention` for richer types, routing.
- Integrate with system/event bus for production notification flows.

## Testing

- Core integration tests:  
  `/tests/integration/test_learning_analytics_integration.py`