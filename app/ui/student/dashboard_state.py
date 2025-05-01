"""
DashboardState for layout and widget tracking per student.
Save at: /app/ui/student/dashboard_state.py

Stub persistence with in-memory dict; extendible for DB/Redis.
"""

from typing import Dict

class DashboardState:
    def __init__(self):
        # map from student_id to list of widget_ids (dashboard layout)
        self._layout: Dict[str, list] = {}

    def get_layout(self, student_id: str) -> list:
        # Default layout if none saved
        return self._layout.get(student_id, ["progress", "enrollments", "notifications"])

    def set_layout(self, student_id: str, layout: list):
        self._layout[student_id] = layout