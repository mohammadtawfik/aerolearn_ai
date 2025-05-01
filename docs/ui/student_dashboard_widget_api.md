# Student Dashboard Widget API Documentation

**Location:** `/docs/ui/student_dashboard_widget_api.md`  
**(Place in /docs/ui/ to match doc structure for UI widget APIs.)**

## Overview

The Student Dashboard Widget offers real-time, personalized insights and actions for students. It integrates academic progress, content recommendations, deadlines, and notifications into a single, extensible UI component for the AeroLearn AI platform.

---

## Widget Structure

- **Component:** `StudentDashboardWidget`
- **Location in code:** `app/ui/student/dashboard_widget.py` *(suggested; confirm with implementation)*
- **API Type:** UI Integration & Data Service

---

## Available Props / Inputs

| Prop            | Type              | Required | Description                                              |
|:---------------:|:-----------------:|:--------:|:---------------------------------------------------------|
| `user_id`       | `str`             | Yes      | ID of the currently logged-in student                    |
| `courses`       | `List[Course]`    | Yes      | Active courses with summary info                         |
| `show_metrics`  | `bool`            | No       | Toggle progress metrics panel                            |
| `widgets`       | `List[Widget]`    | No       | Custom dashboard widget extensions                       |
| `theme`         | `str|ThemeObj`    | No       | Theme customization                                      |
| `onAction`      | `Callable`        | No       | Handler for widget-specific student actions              |

---

## Data Model & API

### Dashboard Data Contract

**The widget expects a data payload structured as:**

```json
{
  "user": {
    "id": "...",
    "name": "...",
    "avatar_url": "...",
    "notifications": [/* ... */]
  },
  "courses": [
    {
      "id": "...",
      "title": "...",
      "progress": 0.75,
      "next_deadline": "2024-06-01"
    },
    ...
  ],
  "recommendations": [
    {
      "content_id": "...",
      "type": "quiz|lesson|resource",
      "title": "...",
      "action_url": "..."
    }
  ],
  "metrics": {
    "overall_progress": 0.63,
    "badges": [ "consistent-learner", ... ]
  }
}
```

*Refer to `/app/models/user.py`, `/app/models/course.py`, `/app/models/content.py` for full model details.*

---

## Events & Callbacks

| Event       | Params                           | Description                                    |
|:-----------:|:--------------------------------:|:-----------------------------------------------|
| `onNavigateCourse` | `course_id`                  | Triggered when a user navigates to a course    |
| `onViewContent`    | `content_id`, `type`         | When a user opens any recommended content      |
| `onAcknowledgeNotification` | `notification_id`   | User acknowledges system notification          |
| `onAction`         | *(custom payload)*           | General action routing (see prop)              |

---

## API Endpoints Used

- `/api/student/summary/{user_id}` – Summary of student progress/courses/metrics
- `/api/content/recommendations/{user_id}` – Per-user recommendations
- `/api/notifications/{user_id}` – Notification feed

Returns must conform to the widget data contract (see above).

---

## Extensibility

- **Slots for custom widgets:** Accept `widgets` prop (see above) for injection of institution-specific dashboard cards.
- **Custom themes:** Accepts `theme` prop for CSS-based or JSON-driven theming.
- **Callback wiring:** All primary events/clicks are exposed via callbacks for parent page integration.

---

## Usage Example

```python
from app.ui.student.dashboard_widget import StudentDashboardWidget

dashboard = StudentDashboardWidget(
    user_id=current_user.id,
    courses=my_courses,
    show_metrics=True,
    widgets=[CustomGPAWidget()],
    theme="dark",
    onAction=handle_dashboard_action
)
```

---

## Security & Privacy

- Student dashboard widgets must enforce that the `user_id` matches the authenticated session.
- Notifications and recommendations must be filtered per user role/permission as per `/app/core/auth/authorization.py`.

---

## Related Docs

- [Student Dashboard Widget User Guide](/docs/ui/student_dashboard_widget_user.md)
- [Student Dashboard Widget Examples](/docs/ui/student_dashboard_widget_examples.md) *(create if not present)*
- [Course API](/docs/api/course_management_api.md)
- [User API](/docs/api/user_management_api.md)

---

## Version History

| Version | Date       | Author        | Changelog               |
|---------|------------|---------------|-------------------------|
| 1.0     | 2024-06-06 | System Update | Initial documentation   |

---

**Save this file at: `/docs/ui/student_dashboard_widget_api.md` as per project structure conventions.**