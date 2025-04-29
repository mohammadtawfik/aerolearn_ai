# /app/ui/common/category_multiselect.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton
from PyQt6.QtCore import Qt

class CategoryMultiSelect(QWidget):
    """
    UI control for multi-selecting categories to assign to Course, Module, or Lesson.
    """
    def __init__(self, categories=None, selected_ids=None, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setWindowTitle("Select Categories")
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.layout.addWidget(QLabel("Select one or more categories:"))
        self.layout.addWidget(self.list_widget)
        self.confirm_button = QPushButton("Confirm Selection")
        self.layout.addWidget(self.confirm_button)
        self.categories = categories or []
        self.selected_ids = set(selected_ids or [])
        self.confirm_button.clicked.connect(self._emit_selection)
        self._populate_list()

    def _populate_list(self):
        self.list_widget.clear()
        for cat in self.categories:
            item = QListWidgetItem(cat.get("name", "Unnamed Category"))
            item.setData(Qt.ItemDataRole.UserRole, cat.get("id"))
            if cat.get("id") in self.selected_ids:
                item.setSelected(True)
            self.list_widget.addItem(item)

    def get_selected_category_ids(self):
        return [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.list_widget.selectedItems()
        ]

    def _emit_selection(self):
        # Placeholder: integrate with event bus or direct callback
        selected_ids = self.get_selected_category_ids()
        print("Selected category ids:", selected_ids)
        # In final implementation, emit signal or call callback.
