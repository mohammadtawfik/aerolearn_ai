from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import pyqtSignal
from app.core.upload.batch_controller import BatchUploadController

class BatchUploadUI(QWidget):
    batch_progress_updated = pyqtSignal(int)
    batch_status_changed = pyqtSignal(str)
    
    def __init__(self, controller: BatchUploadController):
        super().__init__()
        self.controller = controller
        self.layout = QVBoxLayout()
        
        # Progress display
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Batch Status: Idle")
        
        # Layout setup
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)
        
        # Connect signals
        self.controller.add_listener(self)
        
    def on_batch_event(self, event):
        if event.event_type == "batch_progress":
            self.progress_bar.setValue(event.payload["progress"])
            self.status_label.setText(f"Progress: {event.payload['progress']}%")
        elif event.event_type == "batch_completed":
            self.status_label.setText("Batch Completed Successfully")
        elif event.event_type == "batch_failed":
            self.status_label.setText(f"Batch Failed: {event.payload['reason']}")