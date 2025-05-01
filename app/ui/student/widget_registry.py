"""
Student Widget Registry for Dashboard
Save at: /app/ui/student/widget_registry.py

Handles registration of widgets so that dashboard containers are composable and extensible.
"""

from typing import Dict, Type

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