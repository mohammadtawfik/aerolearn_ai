# Course Material Navigator – Developer Guide

**Location:** `/app/ui/student/widgets/course_navigator.py`  
**Documentation:** `/docs/development/student_course_navigator.md`

## Overview

The `CourseMaterialNavigator` widget provides a hierarchical, filterable, and searchable navigation interface for course content in the AeroLearn AI student UI. It enables integration of navigation with dynamic content types, breadcrumbs, favorites, and tracking of recently accessed items.

## Customization & Extension

### 1. Initialization and Data
- Instantiate with a list of `Course` objects (see `/app/models/course.py`).
- Courses should contain `modules`, which contain `lessons`, compatible with the widget's navigation tree.

### 2. Adding New Content Types
- Update the `_content_type_filter` combo box to include additional content types (e.g., "Podcast", "Simulation").
- Ensure your `Lesson` or content objects have a `type` attribute for filtering.

### 3. UI Integration
- Register in `widget_registry.py` under `"course_material_navigator"`.
- Use in the student dashboard via:

  ```python
  from app.ui.student.widgets.course_navigator import CourseMaterialNavigator
  nav = CourseMaterialNavigator(courses)
  ```

### 4. Favorites & Recents
- Use `set_favorites()` / `get_favorites()` and `set_recent()` / `get_recent()` to integrate with user profile persistence.

### 5. Extending Filters
- Use `apply_custom_filter(function)` for complex or permission-based filtering.

### 6. Signals
- Listen to `materialSelected` to update the main view.

## Testing

Basic tests included in `/tests/unit/ui/test_component_architecture.py`. Extend these with model-backed content as you expand integration.

---

For full integration, see docstrings in the code and dashboard example usage.