"""
Registers built-in student dashboard widgets.
Save as /app/ui/student/register_widgets.py
"""

from .widget_registry import StudentWidgetRegistry
from .widgets.progress import ProgressWidget

def register_student_widgets(registry=None):
    registry = registry or StudentWidgetRegistry()
    registry.register("progress", ProgressWidget)
    # TODO: register more widgets (enrollments, notifications, etc.)
    return registry