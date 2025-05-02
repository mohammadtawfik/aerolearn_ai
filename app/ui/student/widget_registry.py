"""
Student Widget Registry for Dashboard
Save at: /app/ui/student/widget_registry.py

Handles registration of widgets so that dashboard containers are composable and extensible.
"""

from typing import Dict, Type
from .widgets.course_navigator import CourseMaterialNavigator
from .widgets.document_viewer import DocumentViewerWidget
from .widgets.video_player import VideoPlayerWidget
from .widgets.code_snippet_viewer import CodeSnippetViewerWidget
from .widgets.image_viewer import ImageViewerWidget

# Imports for new interactive content and note-taking widgets
from .widgets.interactive_quiz import InteractiveQuizWidget
from .widgets.content_highlighter import ContentHighlighterWidget
from .widgets.interactive_diagram import InteractiveDiagramWidget
from .widgets.flashcard_widget import FlashcardWidget
from .widgets.richtext_note_editor import RichTextNoteEditor
from .widgets.note_reference_linker import NoteReferenceLinker
from .widgets.note_organizer import NoteOrganizerWidget
from .widgets.note_search import NoteSearchWidget

class StudentWidgetRegistry:
    def __init__(self):
        self._widgets: Dict[str, Type] = {}

    def register(self, widget_id: str, widget_cls: type):
        """
        Registers a widget class with the specified ID.
        """
        self._widgets[widget_id] = widget_cls

    def get_widget(self, widget_id: str):
        """
        Retrieve a widget class by its ID, or None if not registered.
        """
        return self._widgets.get(widget_id)

    def list_widgets(self):
        return list(self._widgets.keys())


# Create a default registry instance with standard widgets
student_widget_registry = StudentWidgetRegistry()
student_widget_registry.register("course_material_navigator", CourseMaterialNavigator)
student_widget_registry.register("document_viewer", DocumentViewerWidget)
student_widget_registry.register("video_player", VideoPlayerWidget)
student_widget_registry.register("code_snippet_viewer", CodeSnippetViewerWidget)
student_widget_registry.register("image_viewer", ImageViewerWidget)

# Register newly added interactive widgets
student_widget_registry.register("interactive_quiz", InteractiveQuizWidget)
student_widget_registry.register("content_highlighter", ContentHighlighterWidget)
student_widget_registry.register("interactive_diagram", InteractiveDiagramWidget)
student_widget_registry.register("flashcard_widget", FlashcardWidget)

# Register note-taking widgets
student_widget_registry.register("richtext_note_editor", RichTextNoteEditor)
student_widget_registry.register("note_reference_linker", NoteReferenceLinker)
student_widget_registry.register("note_organizer", NoteOrganizerWidget)
student_widget_registry.register("note_search", NoteSearchWidget)
