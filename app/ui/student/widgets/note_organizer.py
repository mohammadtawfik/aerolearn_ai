"""
File location: /app/ui/student/widgets/note_organizer.py

Purpose:
    Provides a UI for organizing student notes—listing all notes, tagging them, renaming, deleting, and basic note categorization.

Context:
    Fulfills Task 3.2.4 (Student Note-Taking System): note organization and tagging.

Integration:
    Callable from the dashboard/note editor or embedded as needed.
    Expects notes_data as [{'id', 'title', 'tags', 'content_html'}].

Author:
    AeroLearn AI Development
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel,
    QInputDialog, QMessageBox, QListWidgetItem, QLineEdit
)
from PyQt6.QtCore import pyqtSignal

class NoteOrganizerWidget(QWidget):
    note_selected = pyqtSignal(dict)
    note_deleted = pyqtSignal(str)
    note_renamed = pyqtSignal(str, str)
    note_tagged = pyqtSignal(str, list)

    def __init__(self, notes_data, parent=None):
        """
        :param notes_data: list of dicts [{'id', 'title', 'tags', 'content_html'}]
        """
        super().__init__(parent)
        self.notes_data = notes_data or []
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.select_note)
        self.layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self.rename_note)
        btn_layout.addWidget(self.rename_btn)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_note)
        btn_layout.addWidget(self.delete_btn)
        self.tag_btn = QPushButton("Tag")
        self.tag_btn.clicked.connect(self.tag_note)
        btn_layout.addWidget(self.tag_btn)
        self.layout.addLayout(btn_layout)

        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        self.refresh_notes()

    def refresh_notes(self):
        self.list_widget.clear()
        for note in self.notes_data:
            tags = ", ".join(note.get('tags', []))
            item = QListWidgetItem(f"{note['title']} [{tags}]")
            item.setData(1, note['id'])
            self.list_widget.addItem(item)

    def find_note_by_id(self, note_id):
        return next((n for n in self.notes_data if n['id'] == note_id), None)

    def select_note(self, item):
        note_id = item.data(1)
        note = self.find_note_by_id(note_id)
        if note:
            self.note_selected.emit(note)
            self.status_label.setText(f"Selected: {note['title']}")

    def delete_note(self):
        item = self.list_widget.currentItem()
        if not item:
            self.status_label.setText("No note selected.")
            return
        note_id = item.data(1)
        note = self.find_note_by_id(note_id)
        if not note:
            return
        res = QMessageBox.question(self, "Delete Note", f"Delete '{note['title']}'?")
        if res == QMessageBox.StandardButton.Yes:
            self.notes_data = [n for n in self.notes_data if n['id'] != note_id]
            self.refresh_notes()
            self.note_deleted.emit(note_id)
            self.status_label.setText(f"Deleted note '{note['title']}'.")

    def rename_note(self):
        item = self.list_widget.currentItem()
        if not item:
            self.status_label.setText("No note selected.")
            return
        note_id = item.data(1)
        note = self.find_note_by_id(note_id)
        if not note:
            return
        new_title, ok = QInputDialog.getText(self, "Rename Note", "New title:", QLineEdit.EchoMode.Normal, note['title'])
        if ok and new_title.strip():
            note['title'] = new_title.strip()
            self.refresh_notes()
            self.note_renamed.emit(note_id, new_title)
            self.status_label.setText(f"Renamed note to '{new_title}'.")

    def tag_note(self):
        item = self.list_widget.currentItem()
        if not item:
            self.status_label.setText("No note selected.")
            return
        note_id = item.data(1)
        note = self.find_note_by_id(note_id)
        if not note:
            return
        current_tags = ", ".join(note.get('tags', []))
        tags, ok = QInputDialog.getText(self, "Tag Note", "Enter tags (comma-separated):", QLineEdit.EchoMode.Normal, current_tags)
        if ok:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            note['tags'] = tag_list
            self.refresh_notes()
            self.note_tagged.emit(note_id, tag_list)
            self.status_label.setText(f"Updated tags for note '{note['title']}'.")