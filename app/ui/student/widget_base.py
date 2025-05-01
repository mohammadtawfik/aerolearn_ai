"""
Widget base class for all student dashboard widgets.
Save at: /app/ui/student/widget_base.py

Defines standard API for rendering, configuration and settings.
"""

class StudentDashboardWidget:
    # Each widget implements this minimal interface
    def __init__(self, student_id: str, config=None):
        self.student_id = student_id
        self.config = config or {}

    def render(self) -> str:
        """
        Render the widget as a string (HTML or other template).
        """
        raise NotImplementedError("Each widget must implement render()")

    def get_config_schema(self) -> dict:
        """
        Returns JSON-schema-like dict for widget customization (stub).
        """
        return {}