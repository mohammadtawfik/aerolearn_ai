"""
File location: /app/ui/student/widgets/note_search.py

Purpose:
    Enables students to search and filter their notes by title, tag, or note content.
    Supports signal-based integration with note organizer and editor widgets.

Context:
    Satisfies Task 3.2.4: Student Note-Taking System (note search and filtering).

Integration:
    Meant to be invoked from the student dashboard, note organizer, or as a standalone search feature.

Author:
    AeroLearn AI Development
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import pyqtSignal

class NoteSearchWidget(QWidget):
    note_found = pyqtSignal(dict)  # Emits the matched note
    search_completed = pyqtSignal(list)  # Emits all filtered note dicts

    def __init__(self, notes_data, parent=None):
        """
        :param notes_data: list of dicts [{'id', 'title', 'tags', 'content_html'}]
        """
        super().__init__(parent)
        self.notes_data = notes_data or []
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search notes by title, tag, or content...")
        self.layout.addWidget(self.search_bar)

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        self.layout.addWidget(self.search_btn)

        self.result_list = QListWidget()
        self.result_list.itemClicked.connect(self.select_result)
        self.layout.addWidget(self.result_list)

        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

    def perform_search(self):
        query = self.search_bar.text().strip().lower()
        if not query:
            self.status_label.setText("Enter a search term.")
            return
        filtered = []
        for note in self.notes_data:
            if (query in note['title'].lower()) or \
               (any(query in tag.lower() for tag in note.get('tags', []))) or \
               (query in note.get('content_html', '').lower()):
                filtered.append(note)
        self.result_list.clear()
        for note in filtered:
            tags = ", ".join(note.get('tags', []))
            item = QListWidgetItem(f"{note['title']} [{tags}]")
            item.setData(1, note['id'])
            self.result_list.addItem(item)
        self.status_label.setText(f"{len(filtered)} notes found.")
        self.search_completed.emit(filtered)

    def select_result(self, item):
        note_id = item.data(1)
        note = next((n for n in self.notes_data if n['id'] == note_id), None)
        if note:
            self.note_found.emit(note)
            self.status_label.setText(f"Selected: {note['title']}")