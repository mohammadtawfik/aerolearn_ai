"""
Sample progress widget for dashboard.
Save as /app/ui/student/widgets/progress.py

Shows standard widget pattern for extension.
"""

from app.ui.student.widget_base import StudentDashboardWidget

class ProgressWidget(StudentDashboardWidget):
    def render(self):
        # In reality, would fetch progress data for self.student_id
        return f"<div class='progress-widget'>Progress for student {self.student_id}: 75%</div>"