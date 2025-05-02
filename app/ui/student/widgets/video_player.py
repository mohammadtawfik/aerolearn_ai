"""
File Location: /app/ui/student/widgets/video_player.py
Purpose: VideoPlayerWidget for rendering video content within the student UI with learning-centric controls.
Reason: Required for Task 3.2.2 as part of the Multi-Format Content Viewer set.
Add student_id param to support integration context.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QFileDialog
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt, QUrl

class VideoPlayerWidget(QWidget):
    """
    Video Player Widget for student content consumption.
    Core features: Play, Pause, Seek. Extensible for learning features (speed, bookmarks).
    """

    def __init__(self, student_id=None, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.layout = QVBoxLayout(self)

        self.video_widget = QVideoWidget(self)
        self.layout.addWidget(self.video_widget)

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        # Controls
        self.play_button = QPushButton("Play", self)
        self.pause_button = QPushButton("Pause", self)
        self.position_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.position_slider.setRange(0, 0)
        self.status_label = QLabel("", self)

        self.layout.addWidget(self.play_button)
        self.layout.addWidget(self.pause_button)
        self.layout.addWidget(self.position_slider)
        self.layout.addWidget(self.status_label)

        self.play_button.clicked.connect(self.player.play)
        self.pause_button.clicked.connect(self.player.pause)
        self.player.positionChanged.connect(self.position_slider.setValue)
        self.player.durationChanged.connect(self.position_slider.setMaximum)
        self.position_slider.sliderMoved.connect(self.player.setPosition)
        self.player.mediaStatusChanged.connect(self._on_media_status)

    def load_content(self, file_path: str):
        url = QUrl.fromLocalFile(file_path)
        self.player.setSource(url)
        self.status_label.setText(f"Loaded: {file_path}")

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.status_label.setText("Playback finished.")

    # Room for later: playback speed, bookmark features, learning analytics, etc.
