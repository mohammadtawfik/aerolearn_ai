"""
File Location: /app/ui/student/widgets/document_viewer.py
Purpose: DocumentViewerWidget for rendering PDF, text, and HTML course content.
Reason: Support optional student_id for context; fits project convention for student content widgets.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtCore import QFileInfo
import os

class DocumentViewerWidget(QWidget):
    """
    Multi-format Document Viewer Widget for student content interaction.
    Supports: PDF, Text, HTML

    Usage:
        widget = DocumentViewerWidget(student_id='abc123')
        widget.load_content(filepath)
    """

    def __init__(self, student_id=None, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.layout = QVBoxLayout(self)
        self.browser = QTextBrowser(self)
        self.pdf_view = QPdfView(self)

        self.layout.addWidget(self.browser)
        self.layout.addWidget(self.pdf_view)

        self.browser.hide()
        self.pdf_view.hide()

    def load_content(self, file_path: str):
        """
        Load and render a document based on its file extension.
        Supported: .pdf, .txt, .html, .htm
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            self._show_pdf(file_path)
        elif ext in ('.txt', '.html', '.htm', '.md'):
            self._show_text_or_html(file_path, ext)
        else:
            self._show_unsupported(file_path)

    def _show_pdf(self, file_path):
        from PyQt6.QtPdf import QPdfDocument
        pdf_doc = QPdfDocument(self)
        pdf_doc.load(file_path)
        self.pdf_view.setDocument(pdf_doc)
        self.pdf_view.show()
        self.browser.hide()

    def _show_text_or_html(self, file_path, ext):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        if ext == '.txt' or ext == '.md':
            self.browser.setPlainText(text)
        else:
            self.browser.setHtml(text)
        self.browser.show()
        self.pdf_view.hide()

    def _show_unsupported(self, file_path):
        self.browser.setPlainText(f"Unsupported file type: {QFileInfo(file_path).suffix()}")
        self.browser.show()
        self.pdf_view.hide()
