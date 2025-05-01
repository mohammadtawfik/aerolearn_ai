# Student Dashboard Widget API

**Save this file to `/docs/api/student_dashboard_widgets.md`**

## Overview

This document describes the interface and registration API for widgets used in the Student Dashboard.

## Widget Requirements

- Inherit from `StudentDashboardWidget`
- Implement `render(self)` to return HTML string (or framework-specific view)
- May define `get_config_schema(self)` for customization

## Registration

To make a widget available:
```python
from app.ui.student.widget_registry import StudentWidgetRegistry
from my_widget import MyWidget

registry = StudentWidgetRegistry()
registry.register("my_widget_id", MyWidget)
```

## Example

```python
class MyWidget(StudentDashboardWidget):
    def render(self):
        return "<div>My custom info</div>"
```

## Dashboard Usage

The dashboard will fetch and render each widget in the current student’s layout, as registered.

---

You may extend this API for more dynamic configuration and integration as needed.