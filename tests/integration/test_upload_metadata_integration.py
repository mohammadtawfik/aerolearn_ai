import pytest
from app.core.upload.batch_controller import BatchUploadController, BatchUploadListener, BatchEvent
from app.models.content_type_registry import ContentTypeRegistry
from app.models.metadata_manager import MetadataManager
from app.ui.professor.batch_upload_ui import BatchUploadUI

class DummyUploadRequest:
    def __init__(self, filepath, dest, callbacks, metadata=None):
        self.file_path = filepath
        self.progress = 100
        self.status = "completed"
        self.size = 123
        self.dest = dest
        self.callbacks = callbacks
        self.metadata = metadata or {}

class DummyUpload:
    def __init__(self):
        self.requests = []
        
    def upload_iter(self, fname):
        for p in [0, 100]:
            yield p
            
    def enqueue(self, req):
        # Store request for later inspection
        self.requests.append(req)
        
        # Simulate immediate progress
        if hasattr(req, "callbacks") and "on_progress" in req.callbacks:
            req.callbacks["on_progress"](100)
        if hasattr(req, "callbacks") and "on_complete" in req.callbacks:
            req.callbacks["on_complete"]()
            
    def pause(self, req): pass
    def resume(self, req): pass
    def cancel(self, req): pass

class DummyValidationFramework:
    def __init__(self):
        self.last_report = {}
        
    def validate_batch(self, batch_name, files=None):
        """Match the actual framework interface with batch_name as first parameter"""
        if files is None:
            files = []
        invalid_files = [f for f in files if not self.validate_file(f)]
        valid = not bool(invalid_files)
        self.last_report = {
            "success": valid,
            "invalid_files": invalid_files,
        }
        return valid, self.last_report
        
    def validate_file(self, filepath):
        # Simulate validation based on file extension
        valid_extensions = ('.pdf', '.png', '.jpg', '.mp4', '.txt')
        return any(filepath.endswith(ext) for ext in valid_extensions) and not filepath.endswith('.fail')
        
    def validate(self, filepath, mimetype=None):
        """Match the actual framework interface with mimetype parameter"""
        return self.validate_file(filepath)

@pytest.fixture(autouse=True)
def patch_upload_request(monkeypatch):
    # Patch UploadRequest in both places used by BatchUploadController
    import app.core.upload.upload_service as upload_service_mod
    import app.core.upload.batch_controller as batch_controller_mod
    monkeypatch.setattr(upload_service_mod, "UploadRequest", DummyUploadRequest)
    monkeypatch.setattr(batch_controller_mod, "UploadRequest", DummyUploadRequest)
    yield
    monkeypatch.undo()

def test_batch_upload_metadata_consistency():
    upload = DummyUpload()
    val = DummyValidationFramework()
    batch = BatchUploadController(upload, val)
    files = ["lecture.pdf", "diagram.png", "simulation.fail"]
    batch.add_files(files)
    batch.batch_name = "test_batch"
    received = []
    class Listener(BatchUploadListener):
        def on_batch_event(self, event, data):
            received.append((event, data))
    batch.add_listener(Listener())
    batch.upload_batch()
    import time; time.sleep(0.2)
    event_types = [e[0].event_type for e in received]
    assert "batch_started" in event_types
    assert "validation_failed" in event_types or "validation_passed" in event_types
    assert batch.status.name.upper() in ["FAILED", "COMPLETED"]
    assert ContentTypeRegistry.detect_type("lecture.pdf") == "pdf"
    assert ContentTypeRegistry.detect_type("diagram.png") == "image"
    mm = MetadataManager()
    mm.set_metadata("lecture.pdf","pdf",{"title":"x"})
    mm.set_metadata("diagram.png","image",{"title":"y"})
    assert mm.get_metadata("lecture.pdf")["data"]["title"] == "x"
    assert mm.get_metadata("diagram.png")["data"]["title"] == "y"
    
    # Test validation interface directly
    valid, report = batch.validate_batch("test_batch")
    assert isinstance(valid, bool)
    assert "invalid_files" in report

def test_batch_metadata_inheritance():
    """Test that batch metadata is properly inherited by all files in the batch"""
    upload = DummyUpload()
    val = DummyValidationFramework()
    batch = BatchUploadController(upload, val)
    
    # Create batch with metadata
    metadata = {"course": "Aero101", "instructor": "Dr. Smith"}
    files = ["lecture1.pdf", "demo.mp4"]
    
    # Start batch with metadata
    batch.start_batch("lectures", files, "/courses", callbacks={}, metadata=metadata)
    
    # Verify metadata is passed to upload requests
    for req in upload.requests:
        assert req.metadata == metadata, "Metadata not inherited correctly"
    
    # Verify metadata inheritance in metadata manager
    metadata_manager = MetadataManager()
    for file in files:
        file_metadata = metadata_manager.get_metadata(file)
        assert file_metadata["data"]["course"] == "Aero101"
        assert file_metadata["data"]["instructor"] == "Dr. Smith"
        assert file_metadata["metadata_source"] == "batch_inherited"

def test_ui_batch_progress():
    """Test UI integration with batch upload progress tracking"""
    upload = DummyUpload()
    val = DummyValidationFramework()
    controller = BatchUploadController(upload, val)
    
    # Test UI integration
    ui = BatchUploadUI(controller)
    progress_data = []
    ui.batch_progress.connect(lambda data: progress_data.append(data))
    
    ui.start_batch_upload(["file1.pdf", "file2.mp4"], "/uploads")
    
    # Verify progress data was captured
    assert len(progress_data) > 0
    assert "total_files" in progress_data[0]
    assert progress_data[0]["total_files"] == 2
    
def test_end_to_end_workflow():
    """Test complete end-to-end workflow from batch creation to completion"""
    upload = DummyUpload()
    val = DummyValidationFramework()
    controller = BatchUploadController(upload, val)
    ui = BatchUploadUI(controller)
    
    # Track events
    events = []
    controller.add_listener(BatchUploadListener())
    controller.listeners[0].on_batch_event = lambda event, data: events.append((event.event_type, data))
    
    # Setup batch with metadata
    files = ["lecture1.pdf", "exercise.pdf", "video.mp4"]
    metadata = {"course": "Physics101", "semester": "Fall 2023"}
    
    # Start batch upload through UI
    ui.start_batch_upload(files, "/courses/physics", callbacks={}, metadata=metadata)
    import time; time.sleep(0.2)
    
    # Verify workflow completed successfully
    event_types = [e[0] for e in events]
    assert "batch_started" in event_types
    assert "batch_completed" in event_types
    
    # Verify metadata was applied
    metadata_manager = MetadataManager()
    for file in files:
        file_metadata = metadata_manager.get_metadata(file)
        assert file_metadata["data"]["course"] == "Physics101"
        assert file_metadata["data"]["semester"] == "Fall 2023"
