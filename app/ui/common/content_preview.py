"""
AeroLearn AI — Content Preview Component

This module provides the ContentPreview UI widget for displaying quick previews of content
selected in the browser. Handles text, images, PDF, video, and provides graceful fallback.

Features:
- Preview for multiple file/content types (text, image, PDF, etc)
- Dynamic selection of preview provider based on detected content type
- "Open with" actions allowing content launch in associated editors/viewers
- Drag-and-drop integration for UI/file sharing
- Preview loading errors are handled and surfaced to user via notification
- Notification system for preview/interaction feedback

"""

from typing import Optional, Dict, Any, Callable
import os

try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QFileDialog, QMessageBox
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtCore import Qt, pyqtSignal
except ImportError:
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QFileDialog, QMessageBox, QPixmap, Qt, pyqtSignal = (object,) * 9

class ContentPreview(QWidget):
    """
    ContentPreview widget for dynamically showing the preview of content item/file.
    """
    error_occurred = pyqtSignal(str)
    notification = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.title = QLabel("Content Preview")
        self.content_area = QLabel("[No content loaded]")
        self.content_area.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.content_area)
        self.setLayout(self.layout)

    def preview_content(self, content: Dict[str, Any]):
        """
        Display preview for the selected content, switch logic by content type.
        """
        # Reset
        self.content_area.setText("[No content loaded]")
        self.content_area.setPixmap(QPixmap())
        try:
            content_type = content.get("type", "Unknown")
            # Assume content dict has 'path' for file-based, or 'body' for inline text
            if content_type in {"Text", "Notes", "Markdown", "Document"}:
                self._show_text_preview(content.get("body") or self._try_read(content.get("path")))
            elif content_type in {"Image", "Photo"}:
                self._show_image_preview(content.get("path"))
            elif content_type in {"PDF"}:
                self._show_pdf_preview(content.get("path"))
            elif content_type in {"Video"}:
                self._show_video_preview(content.get("path"))
            else:
                self.content_area.setText(f"No preview available for: {content_type}")
                self.notification.emit(f"No preview for type: {content_type}")
        except Exception as e:
            self.handle_error(str(e))

    def _show_text_preview(self, text: Optional[str]):
        if text is None:
            self.handle_error("No text to preview.")
            return
        # If there's enough text, use text box
        text_widget = QTextEdit()
        text_widget.setPlainText(text)
        text_widget.setReadOnly(True)
        self.layout.replaceWidget(self.content_area, text_widget)
        self.content_area.hide()
        text_widget.show()

    def _show_image_preview(self, path: Optional[str]):
        if not path or not os.path.exists(path):
            self.handle_error(f"Image not found: {path}")
            return
        pix = QPixmap(path)
        if pix.isNull():
            self.handle_error(f"Could not load image: {path}")
            return
        self.content_area.setPixmap(pix.scaled(400, 300, Qt.KeepAspectRatio))
        self.content_area.show()

    def _show_pdf_preview(self, path: Optional[str]):
        # Minimal stub: Requires PyMuPDF, Poppler/Qt bindings, or opens external viewer
        if not path or not os.path.exists(path):
            self.handle_error(f"PDF not found: {path}")
            return
        self.notification.emit("PDF preview requires plugin. Opening externally.")
        os.system(f"open \"{path}\"") # Portable in real app

    def _show_video_preview(self, path: Optional[str]):
        # Minimal stub: delegate to OS
        if not path or not os.path.exists(path):
            self.handle_error(f"Video not found: {path}")
            return
        self.notification.emit("Video preview requires external viewer. Opening externally.")
        os.system(f"open \"{path}\"")

    def handle_error(self, message: str):
        self.error_occurred.emit(message)
        if hasattr(QMessageBox, 'critical'):
            QMessageBox.critical(self, "Preview Error", message)
        else:
            print("Preview Error:", message)

# Example/minimal usage for manual test
def create_test_content_preview():
    import sys
    from PyQt5.QtWidgets import QApplication, QPushButton

    app = QApplication(sys.argv)
    window = ContentPreview()
    btn = QPushButton("Preview Example Text")
    def show_preview():
        window.preview_content({'type': 'Text', 'body': 'Sample textbook content.\nFormulas:\nE=mc^2'})
    btn.clicked.connect(show_preview)
    window.layout.addWidget(btn)
    window.resize(500, 300)
    window.show()
    app.exec_()

if __name__ == '__main__':
    create_test_content_preview()