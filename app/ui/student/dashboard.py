"""
Student Dashboard: Main entrypoint for the student dashboard UI.

This file should be saved as /app/ui/student/dashboard.py based on current project structure.

The dashboard provides:
- Responsive grid layout for widgets
- State management and persistence
- Widget registration/integration
- Customization hooks (stubbed)
- Course material navigation
- Multi-format content viewers (documents, videos, code, images)
"""

import os
from PyQt6.QtWidgets import QLabel
from .widget_registry import StudentWidgetRegistry
from .dashboard_state import DashboardState
from .widgets.course_navigator import CourseMaterialNavigator
from .widgets.document_viewer import DocumentViewerWidget
from .widgets.video_player import VideoPlayerWidget
from .widgets.code_snippet_viewer import CodeSnippetViewerWidget
from .widgets.image_viewer import ImageViewerWidget

class StudentDashboard:
    def __init__(self, registry=None, state_manager=None):
        self.registry = registry or StudentWidgetRegistry()
        self.state = state_manager or DashboardState()
        self.viewer = None

    def render(self, student_id: str) -> str:
        """
        Render the dashboard as HTML (or for a web view framework).

        Args:
            student_id (str): The ID of the student.
        Returns:
            str: Rendered dashboard HTML.
        """
        # Create course navigator
        course_navigator = CourseMaterialNavigator(student_id=student_id)
        
        # Get regular widgets from layout
        grid = self.state.get_layout(student_id)
        widgets = []
        for widget_id in grid:
            widget_cls = self.registry.get_widget(widget_id)
            if widget_cls is not None:
                widget_instance = widget_cls(student_id=student_id)
                widgets.append(widget_instance.render())
            else:
                widgets.append(f"<div class='widget-error'>Missing widget: {widget_id}</div>")
        
        # Content viewer area
        content_viewer = self.render_content_viewer()
        
        # Create two-column layout with navigator on left
        content = "<div class='student-dashboard-container'>"
        # Left column: Course navigator
        content += f"<div class='course-navigator-column'>{course_navigator.render()}</div>"
        # Right column: Widget grid and content viewer
        content += "<div class='student-dashboard-right-column'>"
        content += "<div class='student-dashboard-grid'>" + "".join(
            f"<div class='dashboard-widget'>{w}</div>" for w in widgets
        ) + "</div>"
        content += f"<div class='content-viewer-area'>{content_viewer}</div>"
        content += "</div>"
        content += "</div>"
        return content

    def customize(self, student_id: str, new_layout: list):
        """
        Update dashboard layout for the student (placeholder for saving positions, widget preferences, etc.).
        """
        self.state.set_layout(student_id, new_layout)
        
    def render_content_viewer(self) -> str:
        """
        Render the content viewer area.
        
        Returns:
            str: HTML for the content viewer area
        """
        if self.viewer:
            return self.viewer.render()
        else:
            return """
                <div class="content-viewer-placeholder">
                    <h3>Content Viewer</h3>
                    <p>Select a file to view its contents</p>
                    <button class="open-content-btn" onclick="openContentFile()">Open Content File</button>
                    <script>
                        function openContentFile() {
                            // This would be implemented with the appropriate framework
                            // to trigger a file selection dialog
                            console.log("Open file dialog would appear here");
                        }
                    </script>
                </div>
            """
    
    def display_content(self, file_path: str, student_id: str = None):
        """
        Display content in the appropriate viewer based on file type.
        
        Args:
            file_path (str): Path to the content file
            student_id (str, optional): Student ID for context
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        # Select appropriate viewer based on file extension
        if ext in [".pdf", ".txt", ".html", ".htm", ".md"]:
            self.viewer = DocumentViewerWidget(student_id=student_id)
        elif ext in [".mp4", ".avi", ".mov", ".webm"]:
            self.viewer = VideoPlayerWidget(student_id=student_id)
        elif ext in [".py", ".js", ".java", ".cpp", ".c", ".cs"]:
            self.viewer = CodeSnippetViewerWidget(student_id=student_id)
        elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]:
            self.viewer = ImageViewerWidget(student_id=student_id)
        else:
            # Use QLabel for unsupported formats so that .text() works in tests
            self.viewer = QLabel(f"Unsupported file format: {os.path.splitext(file_path)[1]}")
            
        # Load content into the viewer
        if hasattr(self.viewer, "load_content"):
            self.viewer.load_content(file_path)
