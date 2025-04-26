"""
Navigation management for AeroLearn AI main window.

Handles:
- Sidebar navigation UI
- View registration and switching
- Role-based navigation

Requires PyQt6 (or compatible PySide6).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt

class NavigationManager:
    def __init__(self, parent, auth_service):
        self.parent = parent
        self.auth_service = auth_service
        self.sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.list_widget = QListWidget()
        sidebar_layout.addWidget(self.list_widget)
        self.role_view_map = {}
        self.stacked_widget = None

        self.list_widget.currentRowChanged.connect(self.on_navigate)

    def set_stacked_widget(self, stacked_widget):
        self.stacked_widget = stacked_widget

    def register_view(self, role: str, view_index: int):
        self.role_view_map[role] = view_index

    def switch_to_role(self, role: str):
        """Change sidebar and stacked view to current role."""
        self.list_widget.clear()
        role = role or "student"
        for r, idx in self.role_view_map.items():
            # Only list roles equal/higher than current
            if r == role:
                item = QListWidgetItem(r.capitalize() + " View")
                self.list_widget.addItem(item)
                self.list_widget.setCurrentRow(0)
                if self.stacked_widget:
                    self.stacked_widget.setCurrentIndex(idx)

    def on_navigate(self, row):
        # Called when sidebar selection changes -- can expand as needed
        if row < 0 or not self.stacked_widget:
            return
        self.stacked_widget.setCurrentIndex(row)