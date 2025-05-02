"""
Student Dashboard: Main entrypoint for the student dashboard UI.

This file should be saved as /app/ui/student/dashboard.py based on current project structure.

This version integrates all interactive content and note-taking widgets.

The dashboard provides:
- Responsive grid layout for widgets
- State management and persistence
- Widget registration/integration
- Customization hooks (stubbed)
- Course material navigation
- Multi-format and interactive content viewers
- Note-taking and organization tools
"""

import os
from PyQt6.QtWidgets import QLabel
from .widget_registry import StudentWidgetRegistry, student_widget_registry
from .dashboard_state import DashboardState
from .widgets.course_navigator import CourseMaterialNavigator
from .widgets.document_viewer import DocumentViewerWidget
from .widgets.video_player import VideoPlayerWidget
from .widgets.code_snippet_viewer import CodeSnippetViewerWidget
from .widgets.image_viewer import ImageViewerWidget

# Import interactive content widgets
from .widgets.interactive_quiz import InteractiveQuizWidget
from .widgets.content_highlighter import ContentHighlighterWidget
from .widgets.interactive_diagram import InteractiveDiagramWidget
from .widgets.flashcard_widget import FlashcardWidget

# Import note-taking widgets
from .widgets.richtext_note_editor import RichTextNoteEditor
from .widgets.note_reference_linker import NoteReferenceLinker
from .widgets.note_organizer import NoteOrganizerWidget
from .widgets.note_search import NoteSearchWidget

class StudentDashboard:
    def __init__(self, registry=None, state_manager=None):
        self.registry = registry or student_widget_registry
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
        # Define all available widgets
        widget_ids = [
            "course_material_navigator",
            "document_viewer",
            "video_player",
            "code_snippet_viewer",
            "image_viewer",
            # Interactive widgets
            "interactive_quiz",
            "content_highlighter",
            "interactive_diagram",
            "flashcard_widget",
            # Note-taking widgets
            "richtext_note_editor",
            "note_reference_linker",
            "note_organizer",
            "note_search",
        ]

        # Get layout from state or use default widget list
        grid = self.state.get_layout(student_id) or widget_ids
        
        # Create two-column dashboard layout
        content = "<div class='student-dashboard-container'>"
        
        # Left column: Course navigator + note organization widgets
        left_col_widgets = ["course_material_navigator", "note_organizer", "note_search"]
        left_col_html = ""
        for widget_id in left_col_widgets:
            widget_cls = self.registry.get_widget(widget_id)
            if widget_cls is not None:
                try:
                    # Try to instantiate with student_id if possible
                    try:
                        widget_instance = widget_cls(student_id=student_id)
                    except TypeError:
                        widget_instance = widget_cls()
                        
                    if hasattr(widget_instance, "render"):
                        left_col_html += widget_instance.render()
                    else:
                        left_col_html += f"<div class='dashboard-widget-qt'>[{widget_id} widget loaded]</div>"
                except Exception as ex:
                    left_col_html += f"<div class='widget-error'>Widget error ({widget_id}): {str(ex)}</div>"
            else:
                left_col_html += f"<div class='widget-error'>Missing widget: {widget_id}</div>"
        
        content += f"<div class='course-navigator-column'>{left_col_html}</div>"
        
        # Right column: Content viewers, interactive widgets, and note editor
        right_col_widgets = [wid for wid in grid if wid not in left_col_widgets]
        right_col_html = "<div class='student-dashboard-grid'>"
        
        for widget_id in right_col_widgets:
            widget_cls = self.registry.get_widget(widget_id)
            if widget_cls is not None:
                try:
                    # Try to instantiate with student_id if possible
                    try:
                        widget_instance = widget_cls(student_id=student_id)
                    except TypeError:
                        widget_instance = widget_cls()
                        
                    if hasattr(widget_instance, "render"):
                        right_col_html += f"<div class='dashboard-widget'>{widget_instance.render()}</div>"
                    else:
                        right_col_html += f"<div class='dashboard-widget-qt'>[{widget_id} widget loaded]</div>"
                except Exception as ex:
                    right_col_html += f"<div class='widget-error'>Widget error ({widget_id}): {str(ex)}</div>"
            else:
                right_col_html += f"<div class='widget-error'>Missing widget: {widget_id}</div>"
        
        right_col_html += "</div>"
        
        # Content viewer area
        content_viewer = self.render_content_viewer()
        right_col_html += f"<div class='content-viewer-area'>{content_viewer}</div>"
        
        content += f"<div class='student-dashboard-right-column'>{right_col_html}</div>"
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
