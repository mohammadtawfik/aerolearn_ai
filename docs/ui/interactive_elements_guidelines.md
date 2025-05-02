# Interactive Content Elements – Guidelines

**File location:** `/docs/ui/interactive_elements_guidelines.md`

## Overview

This document describes best practices and required steps for creating, extending, and integrating interactive content widgets in the student dashboard.

These include:  
- Interactive Quiz Element  
- Content Highlighting & Annotation  
- Interactive Diagrams  
- Flashcard Component  

---

## Widget Creation

- **Subclass the StudentDashboardWidget base:**  
    All interactive widgets should inherit from `StudentDashboardWidget` for consistency.

- **Stateful Data:**  
    Use internal state objects and connect signals for interaction-driven updates.

- **Signals & Events:**  
    Emit signals for interaction events (e.g., `quiz_completed`, `annotation_made`) to support cross-component UX and analytics.

---

## Data Persistence & Retrieval

- **Persistence Strategies:**  
    Use provided state managers, or implement your own data bridge to save interaction results (e.g., quiz answers, highlights) via local storage or cloud sync.

- **Widget Identifiers:**  
    Provide unique widget IDs for clean integration with the dashboard’s layout and registry.

---

## Integration Steps

1. **Register the Widget:**
    ```python
    student_widget_registry.register('my_interactive', MyInteractiveWidget)
    ```

2. **Connect Events:**
    Optionally subscribe to other widgets’/dashboard events for richer, contextual interaction.

3. **Test Data Flow:**
    Add/extend tests in `/tests/ui/test_student_dashboard.py` to simulate interactions and check for correct data persistence.

---

## Example – Quiz Widget

- Stores question/answer progress in dashboard state.
- Emits `quiz_completed(score: int)` signal.
- Supports session-resume (loads prior answers).

---

## Best Practices

- Store each interaction's payload in a recoverable format (JSON, dict).
- Keep UI and persistence logic separated when possible.
- Document the intent and integration points of each custom interactive element.

---

## See Also

- `/app/ui/student/widgets/interactive_quiz.py`
- `/app/ui/student/widgets/content_highlighter.py`
- `/app/ui/student/widgets/interactive_diagram.py`
- `/app/ui/student/widgets/flashcard_widget.py`
- `/tests/ui/test_student_dashboard.py`