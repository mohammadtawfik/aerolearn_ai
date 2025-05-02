"""
File Location: /app/ui/student/widgets/code_snippet_viewer.py
Purpose: CodeSnippetViewerWidget for displaying code files with syntax highlighting.
Reason: Required for Task 3.2.2. Follows project UI widget conventions.
Notes: Uses QScintilla if available, else basic display.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import QFileInfo

try:
    from PyQt6.Qsci import QsciScintilla, QsciLexerPython
    QSCI_AVAILABLE = True
except ImportError:
    QSCI_AVAILABLE = False

class CodeSnippetViewerWidget(QWidget):
    """
    Displays code with syntax highlighting.
    Supports: Python; extendable for other syntaxes.
    """
    def __init__(self, student_id=None, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.layout = QVBoxLayout(self)

        if QSCI_AVAILABLE:
            self.editor = QsciScintilla(self)
            self.editor.setFont(QFont("Consolas", 12))
            lexer = QsciLexerPython()
            self.editor.setLexer(lexer)
            self.layout.addWidget(self.editor)
        else:
            from PyQt6.QtWidgets import QTextEdit
            self.editor = QTextEdit(self)
            self.editor.setFont(QFont("Consolas", 12))
            self.layout.addWidget(self.editor)

    def load_content(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        if QSCI_AVAILABLE:
            self.editor.setText(code)
        else:
            self.editor.setPlainText(code)
