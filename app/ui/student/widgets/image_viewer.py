"""
File Location: /app/ui/student/widgets/image_viewer.py
Purpose: ImageViewerWidget for displaying images and providing annotation tools.
Reason: Required for Task 3.2.2, per viewer widget convention.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt

class ImageViewerWidget(QWidget):
    """
    Image Viewer with annotation features (stub version).
    For: student content interaction.
    """

    def __init__(self, student_id=None, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.image_label)

        # Annotation stub (expand later)
        self.annotate_button = QPushButton("Annotate (Coming Soon)", self)
        self.annotate_button.setEnabled(False)
        self.layout.addWidget(self.annotate_button)

    def load_content(self, file_path: str):
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.image_label.setText("Failed to load image.")
        else:
            self.image_label.setPixmap(pixmap.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio))
