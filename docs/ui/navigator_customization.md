# Course Material Navigator - Customization & Extension Guide

**File location:** `/docs/ui/navigator_customization.md`

## Overview

The Course Material Navigator is a hierarchical navigation system that organizes and presents course materials in the student dashboard.

---

## Customization Options

- **Navigation Structure:**  
  Define custom folder/content hierarchies by subclassing the core navigator or adjusting provided configuration/registry mechanisms.

- **Content Type Filtering:**  
  Register additional content types for filtering by extending the filter registry in `/app/ui/student/widgets/course_navigator.py`.

- **Breadcrumb and History:**  
  Override or enhance the breadcrumb/historical navigation by customizing state handlers.

- **Favorites & Recently Accessed:**  
  Integrate new backends (database/local/cloud) for favorites/history persistence by implementing compatible adapters.

---

## Key Extension Points

1. **Adding New Content Types**  
   Extend the allowed content types via configuration or by subclassing the navigator and registering additional types.

2. **Custom Filtering Logic**  
   Add advanced filters based on tags, user progress, or metadata.

3. **Integration with Other UI Components**  
   Expose navigator state to other widgets (e.g., for note-linking or content highlighting) via shared application context/events.

---

## Example: Registering a New Content Type

```python
# In your app/ui/student/widgets/course_navigator.py or similar module:
CourseNavigator.register_content_type('interactive_lab', InteractiveLabViewer)
```

---

## Best Practices

- Use the navigator’s event hooks to track user navigation and drive analytics.
- Document custom content schemas for clarity.
- Ensure that UI state is synced if integrating with real-time collaboration or cloud-backed navigation.

---

## More

For further details, review the implementation in `/app/ui/student/widgets/course_navigator.py` and related tests in `/tests/ui/`.