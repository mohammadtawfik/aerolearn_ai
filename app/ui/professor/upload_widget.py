"""
Professor Material Upload Widget for AeroLearn AI
=================================================

PyQt6 widget for file uploads with drag-and-drop, multi-selection dialog,
file type detection, MIME validation, and event notification.

Features:
- Drag-and-drop upload zone with visual feedback
- File dialog selection with multi-file and MIME filtering
- Progress visualization per file
- MIME type validation and pluggable acceptance logic
- Upload event system (signals) for cross-component integration
- Extensible for backend upload integration

Author: AeroLearn AI Team
Date: 2025-04-25

Usage:
------
from app.ui.professor.upload_widget import ProfessorUploadWidget
# Add as a widget in your view/layout

API:
----
- fileUploadRequested(list[dict]): Emitted after validation with list of files
- fileUploadProgress(str, int): Emitted to update progress (file_id, percent)
- fileUploadCompleted(str, bool): Emitted on upload completion (file_id, success)
See method and signal docstrings for more.

"""

import os
from typing import List, Callable, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QProgressBar, QListWidget, QListWidgetItem, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

def default_mime_validator(filepath: str, mimetype: str) -> bool:
    # Accept common educational formats by default
    accepted_types = [
        "application/pdf", "image/jpeg", "image/png", "video/mp4",
        "text/plain", "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/zip"
    ]
    return mimetype in accepted_types

class ProfessorUploadWidget(QWidget):
    fileUploadRequested = pyqtSignal(list)  # [{'filepath': ..., 'mimetype': ...}, ...]
    fileUploadProgress = pyqtSignal(str, int)  # file_id, percent
    fileUploadCompleted = pyqtSignal(str, bool)  # file_id, success/fail

    def __init__(self, mime_validator: Optional[Callable[[str, str], bool]] = None, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.mime_validator = mime_validator or default_mime_validator

        self.setMinimumSize(350, 240)
        self.layout = QVBoxLayout(self)
        self.info_label = QLabel("Drag & drop files here or select from your computer.\nSupported: PDF, images, video, docs")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.info_label)

        self.select_btn = QPushButton("Select Files")
        self.select_btn.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(self.select_btn)

        self.progress_list = QListWidget()
        self.progress_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.layout.addWidget(self.progress_list)

        # Track uploads to associate progress/per file
        self.current_uploads = {}

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("border: 2px dashed #4593fc; background: #eef6ff;")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        files = []
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            mimetype = self.detect_mimetype(filepath)
            if self.mime_validator(filepath, mimetype):
                files.append({'filepath': filepath, 'mimetype': mimetype})
            else:
                QMessageBox.warning(self, "Upload Error",
                    f"Unsupported file type: {os.path.basename(filepath)} ({mimetype})")
        if files:
            self.add_files(files)

    def open_file_dialog(self):
        filter_str = "All Supported Files (*.pdf *.jpg *.jpeg *.png *.mp4 *.txt *.ppt *.pptx *.zip);;All Files (*)"
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Upload", "", filter_str)
        valid_files = []
        for filepath in files:
            mimetype = self.detect_mimetype(filepath)
            if self.mime_validator(filepath, mimetype):
                valid_files.append({'filepath': filepath, 'mimetype': mimetype})
            else:
                QMessageBox.warning(self, "Selection Error",
                    f"Unsupported file type: {os.path.basename(filepath)} ({mimetype})")
        if valid_files:
            self.add_files(valid_files)

    def add_files(self, file_list: List[dict]):
        """Add files to list and emit upload requested event."""
        for file in file_list:
            fname = os.path.basename(file['filepath'])
            mimetype = file['mimetype']
            file_id = file['filepath']  # Use full path as unique key (could hash for privacy)
            item = QListWidgetItem(f"{fname} ({mimetype})")
            progress_bar = QProgressBar()
            progress_bar.setValue(0)
            self.current_uploads[file_id] = progress_bar
            self.progress_list.addItem(item)
            self.progress_list.setItemWidget(item, progress_bar)
        # Notify listeners for upload
        self.fileUploadRequested.emit(file_list)

    def set_progress(self, file_id: str, percent: int):
        """Update progress bar for ongoing upload."""
        bar = self.current_uploads.get(file_id)
        if bar:
            bar.setValue(percent)
        self.fileUploadProgress.emit(file_id, percent)

    def mark_completed(self, file_id: str, success: bool):
        bar = self.current_uploads.get(file_id)
        if bar:
            bar.setValue(100 if success else 0)
        self.fileUploadCompleted.emit(file_id, success)
        # Optionally: update appearance/disable/etc

    @staticmethod
    def detect_mimetype(filepath: str) -> str:
        # Light-weight detection using extension (for demonstration); real impl should use python-magic or similar
        ext = os.path.splitext(filepath)[1].lower()
        if ext in [".pdf"]:
            return "application/pdf"
        elif ext in [".jpg", ".jpeg"]:
            return "image/jpeg"
        elif ext in [".png"]:
            return "image/png"
        elif ext in [".mp4"]:
            return "video/mp4"
        elif ext in [".txt"]:
            return "text/plain"
        elif ext in [".ppt"]:
            return "application/vnd.ms-powerpoint"
        elif ext in [".pptx"]:
            return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif ext in [".zip"]:
            return "application/zip"
        else:
            return "application/octet-stream"

    def clear(self):
        """Clear the upload list and reset state."""
        self.progress_list.clear()
        self.current_uploads.clear()