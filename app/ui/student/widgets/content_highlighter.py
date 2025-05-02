"""
File location: /app/ui/student/widgets/content_highlighter.py

Purpose:
    Provides an interactive widget for students to highlight and annotate content (text) in the AeroLearn AI platform.

Context:
    Fulfills Interactive Content Elements, as per Task 3.2.3 (second subtask) in /docs/development/day16_plan.md.

To be used:
    Embedded in content viewer UI; communicates with persistence backend for storing highlights/annotations.

Author:
    AeroLearn AI Development
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTextEdit, QInputDialog, QColorDialog
)
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import pyqtSignal

class ContentHighlighterWidget(QWidget):
    highlight_added = pyqtSignal(dict)
    annotation_added = pyqtSignal(dict)

    def __init__(self, initial_text="", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(initial_text)
        self.text_edit.setReadOnly(False)
        self.layout.addWidget(self.text_edit)

        self.highlight_button = QPushButton("Highlight Selection")
        self.highlight_button.clicked.connect(self.highlight_selection)
        self.layout.addWidget(self.highlight_button)

        self.annotate_button = QPushButton("Add Annotation to Selection")
        self.annotate_button.clicked.connect(self.annotate_selection)
        self.layout.addWidget(self.annotate_button)

    def highlight_selection(self):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            return

        color = QColorDialog.getColor(QColor("#FFFF00"), self, "Select highlight color")
        if not color.isValid():
            return

        fmt = QTextCharFormat()
        fmt.setBackground(color)
        cursor.mergeCharFormat(fmt)

        highlight_info = {
            'start': cursor.selectionStart(),
            'end': cursor.selectionEnd(),
            'color': color.name(),
            'text': cursor.selectedText()
        }
        self.highlight_added.emit(highlight_info)

    def annotate_selection(self):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            return

        annotation, ok = QInputDialog.getText(self, "Add Annotation", "Enter your annotation:")
        if not ok or not annotation.strip():
            return

        # Optionally store annotation meta info in charFormat (not visible to user, but demo for extensibility)
        fmt = QTextCharFormat()
        fmt.setToolTip(annotation)
        fmt.setBackground(QColor("#B2EBF2"))  # Cyan tint to indicate annotation
        cursor.mergeCharFormat(fmt)

        annotation_info = {
            'start': cursor.selectionStart(),
            'end': cursor.selectionEnd(),
            'annotation': annotation,
            'text': cursor.selectedText()
        }
        self.annotation_added.emit(annotation_info)