"""
File location: /app/ui/student/widgets/richtext_note_editor.py

Purpose:
    Provides a rich text note editor for the AeroLearn AI student interface,
    supporting text formatting (bold, italic, underline, lists), content embedding, and basic organization,
    as the first step of Task 3.2.4: Student Note-Taking System.

Integration:
    To be embedded within student dashboard/content views.
    Will later be linked to note persistence and content reference features.

Author:
    AeroLearn AI Development
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QToolBar, QFileDialog, QMessageBox, QInputDialog
)
from PyQt6.QtGui import QIcon, QTextCursor, QTextCharFormat, QTextListFormat, QFont, QAction
from PyQt6.QtCore import pyqtSignal

class RichTextNoteEditor(QWidget):
    note_saved = pyqtSignal(str)  # Emitted when note is saved (plain+rich version could be added)
    note_edited = pyqtSignal(str)
    
    def __init__(self, initial_note="", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.toolbar = QToolBar("Formatting")
        self.layout.addWidget(self.toolbar)

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(initial_note)
        self.layout.addWidget(self.text_edit)
        
        # Formatting actions
        bold_action = QAction(QIcon(), "Bold", self)
        bold_action.setShortcut("Ctrl+B")
        bold_action.triggered.connect(self.make_bold)
        self.toolbar.addAction(bold_action)

        italic_action = QAction(QIcon(), "Italic", self)
        italic_action.setShortcut("Ctrl+I")
        italic_action.triggered.connect(self.make_italic)
        self.toolbar.addAction(italic_action)

        underline_action = QAction(QIcon(), "Underline", self)
        underline_action.setShortcut("Ctrl+U")
        underline_action.triggered.connect(self.make_underline)
        self.toolbar.addAction(underline_action)

        self.toolbar.addSeparator()

        bullet_action = QAction("• List", self)
        bullet_action.triggered.connect(self.make_bullet_list)
        self.toolbar.addAction(bullet_action)

        number_action = QAction("1. List", self)
        number_action.triggered.connect(self.make_number_list)
        self.toolbar.addAction(number_action)

        self.toolbar.addSeparator()

        save_action = QAction(QIcon(), "Save note", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_note)
        self.toolbar.addAction(save_action)

        # Signals for note tracking
        self.text_edit.textChanged.connect(self.on_text_changed)

    def on_text_changed(self):
        self.note_edited.emit(self.text_edit.toHtml())

    def make_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold)
        self.merge_format_on_word_or_selection(fmt)

    def make_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(True)
        self.merge_format_on_word_or_selection(fmt)

    def make_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(True)
        self.merge_format_on_word_or_selection(fmt)

    def make_bullet_list(self):
        cursor = self.text_edit.textCursor()
        cursor.insertList(QTextListFormat.Style.ListDisc)

    def make_number_list(self):
        cursor = self.text_edit.textCursor()
        cursor.insertList(QTextListFormat.Style.ListDecimal)

    def merge_format_on_word_or_selection(self, format):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.text_edit.mergeCurrentCharFormat(format)

    def save_note(self):
        text = self.text_edit.toHtml()
        # Optionally, open dialog for save location or name
        name, ok = QInputDialog.getText(self, "Save Note", "Enter note name:")
        if ok and name.strip():
            # Here, real persistence logic would save 'text' under 'name'
            self.note_saved.emit(text)
            QMessageBox.information(self, "Note Saved", f"Note '{name}' saved (simulated).")
        else:
            QMessageBox.warning(self, "Note Not Saved", "Please provide a note name to save.")
