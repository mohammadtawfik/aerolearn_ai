# /app/ui/common/tag_autocomplete.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QListWidgetItem, QCompleter
from PyQt6.QtCore import Qt, QStringListModel

class TagAutocomplete(QWidget):
    """
    UI for assigning tags with autocomplete and free entry.
    """
    def __init__(self, all_tags=None, selected_tags=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Assign Tags")
        self.layout = QVBoxLayout(self)
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Enter or select tags...")
        self.completer = QCompleter()
        self._update_completer(all_tags or [])
        self.tag_input.setCompleter(self.completer)
        self.layout.addWidget(QLabel("Tags:"))
        self.layout.addWidget(self.tag_input)
        self.selected_list = QListWidget()
        self.layout.addWidget(self.selected_list)
        self.add_button = QPushButton("Add Tag")
        self.layout.addWidget(self.add_button)
        self.tags = set(selected_tags or [])
        self.all_tags = set(all_tags or [])
        self._refresh_list()
        self.add_button.clicked.connect(self._add_tag)

    def _update_completer(self, tag_list):
        self.completer.setModel(QStringListModel(list(tag_list)))

    def _refresh_list(self):
        self.selected_list.clear()
        for tag in sorted(self.tags):
            item = QListWidgetItem(tag)
            self.selected_list.addItem(item)

    def _add_tag(self):
        tag = self.tag_input.text().strip()
        if tag:
            self.tags.add(tag)
            self._refresh_list()
            self.tag_input.clear()

    def get_selected_tags(self):
        return list(self.tags)
