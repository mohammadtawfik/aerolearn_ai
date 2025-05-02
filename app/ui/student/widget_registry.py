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
