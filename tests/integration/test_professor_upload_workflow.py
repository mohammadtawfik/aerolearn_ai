"""
Integration Test: Professor Upload Workflow

This test covers:
- UI upload → backend service → validation → event/callback → metadata
- Batch upload and progress
- Metadata assignment and consistency

Location: /tests/integration/test_professor_upload_workflow.py
"""
import pytest
import time
from PyQt6.QtWidgets import QApplication
from app.ui.professor.upload_widget import ProfessorUploadWidget
from app.core.upload.upload_service import UploadService
from app.core.validation.main import ValidationSystem
from app.core.db.content_db import ContentDB
from integrations.events.event_bus import EventBus
from app.models.metadata_manager import MetadataManager
from concurrent.futures import ThreadPoolExecutor

def publish(self, event_or_type, payload=None):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(self._publish_internal, event_or_type, payload)
        try:
            future.result(timeout=2)  # 2-second timeout
        except TimeoutError:
            logger.warning("Event processing timed out")


@pytest.fixture
def qapp():
    """Ensure a QApplication exists."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_full_upload_workflow(qapp, tmp_path):
    # Arrange: Create mock files
    pdf_file = tmp_path / "lecture_notes.pdf"
    img_file = tmp_path / "aircraft_diagram.png"
    with pdf_file.open("wb") as f: f.write(b"%PDF-1.4 example test")
    with img_file.open("wb") as f: f.write(b"\x89PNG\r\n test image")

    # Mock subsystem setup with test-optimized services
    validator = ValidationSystem(fast_validation=True)  # Use faster validation
    upload_service = UploadService(test_mode=True)  # Use test mode for faster tests
    event_bus = EventBus.get()  # Use singleton instance instead of constructor
    meta_manager = MetadataManager(use_memory_store=True)  # Use in-memory storage
    content_db = ContentDB(test_mode=True)  # Use test mode for database
    
    # Ensure widget is aware of all services for full integration
    widget = ProfessorUploadWidget(
        metadata_manager=meta_manager,
        content_db=content_db,
        event_bus=event_bus,
        upload_service=upload_service  # Pass dummy service explicitly
    )
    
    # Register mock event listeners
    complete = []
    def on_completed(event_type, payload):
        if event_type == "upload.completed":
            complete.append((payload["status"], payload["files"]))
    event_bus.subscribe(on_completed)

    # Act: Simulate drag-and-drop upload of both files through UI
    widget.simulate_drag_and_drop([str(pdf_file), str(img_file)])

    # (System is event-driven: wait for completion/status)
    widget.wait_for_uploads(timeout=2.0)  # Use shorter timeout for tests

    # Add event waiting helper
    def wait_for_event():
        start = time.time()
        while time.time() - start < 5:  # 5 second timeout
            # Process both Qt and Python events
            QApplication.processEvents()
            qapp.processEvents()
            
            if len(complete) > 0:
                return True
            time.sleep(0.1)
        return False
    
    # Wait for events to complete
    assert wait_for_event(), "No upload.completed events received within timeout"

    # Assert: UploadManager accepted the files and ValidationSystem ran
    for uploaded_file in [pdf_file, img_file]:
        val_result = validator.check(str(uploaded_file))
        assert val_result.success, f"Validation failed for {uploaded_file}: {val_result.errors}"
        meta = meta_manager.get_metadata(str(uploaded_file))
        # The metadata manager returns {"data": md_dict, "content_type": ...}
        assert meta is not None and meta["data"]["filename"] == uploaded_file.name

    # Batch summary
    status, files = complete[0]
    assert status == "success"
    assert set([f['filename'] for f in files]) == {pdf_file.name, img_file.name}

    # Metadata and DB update
    for uploaded_file in [pdf_file, img_file]:
        assert content_db.is_uploaded(str(uploaded_file))
        assert meta_manager.get_metadata(str(uploaded_file)) is not None

    # UI feedback
    assert widget.last_status_message == "Upload completed successfully"


def stop(self):
    """Force immediate shutdown with thread cleanup"""
    self.running = False
    with self.lock:
        # Cancel all active uploads
        for upload in self.active_uploads.values():
            upload.cancel_event.set()
        self.active_uploads.clear()

    # Clear queue and terminate workers
    while not self.upload_queue.empty():
        try: self.upload_queue.get_nowait()
        except queue.Empty: break

    for t in self.threads:
        if t.is_alive():
            t.join(timeout=0.5)# In test_professor_upload_workflow.py
def test_full_upload_workflow(qapp, tmp_path):
    # Configure test-optimized services
    upload_service = UploadService(
        test_mode=True,
        max_retries=0,  # Disable retries
        concurrency=1,  # Single worker
        chunk_size=512  # Small chunks for fast completion
    )

    # Bypass normal validation
    validator = ValidationSystem(fast_validation=True)

    # Direct service injection
    widget = ProfessorUploadWidget()
    widget.upload_service = upload_service
    widget.metadata_manager = MetadataManager()# In event_bus.py

