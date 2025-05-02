"""
File location: /app/ui/student/widgets/note_reference_linker.py

Purpose:
    Allows students to link notes with specific course content (lessons, modules, highlights, or even precise locations in documents/videos),
    supporting cross-referencing and deep linking in the AeroLearn AI note-taking workflow.

Context:
    Core for Task 3.2.4: Student Note-Taking System — content reference linking.

Integration:
    Can be used alongside the rich text editor, viewers, and persistent storage systems.

Author:
    AeroLearn AI Development
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QInputDialog, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

class NoteReferenceLinker(QWidget):
    # Signal emitted when a reference is created/selected: {type, ref_id, label}
    reference_linked = pyqtSignal(dict)

    def __init__(self, content_context, parent=None):
        """
        :param content_context: dict with available context for linking
            Example:
             {
                 'course': 'Intro to Aero',
                 'module': {'id': 'mod01', 'title': 'Aerodynamics Basics'},
                 'lesson': {'id': 'lsn05', 'title': 'Bernoulli’s Principle'},
                 'highlighted_text': 'Example: Pressure drop in venturi tube',
                 # Optionally: 'video_time': 420.5, etc.
             }
        """
        super().__init__(parent)
        self.content_context = content_context
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Link this note to:")
        self.layout.addWidget(self.label)

        # Possible reference types, dynamically available
        self.combo = QComboBox()
        self.references = self._prepare_reference_options(content_context)
        self.combo.addItems([ref['label'] for ref in self.references])
        self.layout.addWidget(self.combo)

        self.link_button = QPushButton("Create Link")
        self.link_button.clicked.connect(self.link_selected)
        self.layout.addWidget(self.link_button)

    def _prepare_reference_options(self, ctx):
        refs = []
        if 'lesson' in ctx:
            refs.append({
                'type': 'lesson',
                'ref_id': ctx['lesson']['id'],
                'label': f"Lesson: {ctx['lesson']['title']}"
            })
        if 'module' in ctx:
            refs.append({
                'type': 'module',
                'ref_id': ctx['module']['id'],
                'label': f"Module: {ctx['module']['title']}"
            })
        if 'highlighted_text' in ctx:
            refs.append({
                'type': 'highlight',
                'ref_id': None,
                'label': f"Highlight: \"{ctx['highlighted_text'][:30]}{'...' if len(ctx['highlighted_text'])>30 else ''}\""
            })
        if 'video_time' in ctx:
            refs.append({
                'type': 'video_time',
                'ref_id': ctx['video_time'],
                'label': f"Video @ {ctx['video_time']}s"
            })
        if 'course' in ctx:
            refs.append({
                'type': 'course',
                'ref_id': ctx['course'],
                'label': f"Course: {ctx['course']}"
            })
        return refs

    def link_selected(self):
        idx = self.combo.currentIndex()
        if idx < 0 or idx >= len(self.references):
            QMessageBox.warning(self, "No Selection", "Please select a reference to link.")
            return
        ref = self.references[idx]
        self.reference_linked.emit(ref)
        QMessageBox.information(self, "Reference Linked", f"Linked to: {ref['label']}")