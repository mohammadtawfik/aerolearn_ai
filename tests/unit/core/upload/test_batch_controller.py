import pytest
from unittest.mock import MagicMock, patch, mock_open
from app.core.upload.batch_controller import BatchUploadController, BatchUploadListener, BatchEvent, BatchStatus
import threading
import time

class DummyListener(BatchUploadListener):
    def __init__(self):
        self.events = []
    def on_batch_event(self, event):
        self.events.append((event.event_type, event.payload))

@pytest.fixture
def fake_files():
    # A dict mapping file names to fake file sizes (in bytes)
    return {
        "test1.pdf": 1024,
        "test2.mp4": 2048,
        "ok1.pdf": 512,
        "bad1.sim": 128,
        "a.pdf": 512,
        "b.img": 1024,
    }

@pytest.fixture
def file_patches(fake_files):
    # Patch os.path.getsize and open for all tests
    size_side_effect = lambda filename: fake_files[filename] if filename in fake_files else 100
    mopen = mock_open(read_data=b"x" * 512)
    with patch("os.path.getsize", side_effect=size_side_effect):
        with patch("builtins.open", mopen):
            yield

@pytest.fixture
def dummy_upload_service():
    class DummyRequest:
        # Simulates a request object used by upload_service
        def __init__(self, fp):
            self.id = fp
            self.filepath = fp
            self.progress = 0
            self.status = BatchStatus.PENDING
            
    class DummyUploadService:
        def __init__(self):
            self.paused = False
            self.cancelled = False
            self.resume_event = threading.Event()
            self.requests = {}
            
        def upload_iter(self, filename):
            req = DummyRequest(filename)
            self.requests[filename] = req
            
            # Simulate slow, interruptible upload
            req.status = BatchStatus.IN_PROGRESS
            for progress in [0, 25, 50, 75, 100]:
                if self.cancelled:
                    req.status = BatchStatus.CANCELED
                    yield progress
                    return
                    
                while self.paused:
                    req.status = BatchStatus.PAUSED
                    self.resume_event.wait(0.05)
                    
                req.progress = progress
                req.status = BatchStatus.IN_PROGRESS
                yield progress
                time.sleep(0.03)
                
            req.status = BatchStatus.COMPLETED
            
    return DummyUploadService()

@pytest.fixture
def dummy_validation_framework():
    class DummyV:
        def __init__(self):
            self.last_report = None
        def validate_batch(self, files):
            self.last_report = {"success": all("bad" not in f for f in files), "errors": [f for f in files if "bad" in f]}
            return self.last_report
    return DummyV()

def test_batch_add_and_progress(file_patches, dummy_upload_service, dummy_validation_framework):
    c = BatchUploadController(dummy_upload_service, dummy_validation_framework)
    c.add_files(["test1.pdf", "test2.mp4"])
    l = DummyListener()
    c.add_listener(l)
    c.upload_batch()
    time.sleep(0.25)  # wait for upload to finish
    progress = c.get_total_progress()
    assert progress == 100
    assert c.status == BatchStatus.COMPLETED
    events = [ev[0] for ev in l.events]
    assert "validation" in events
    assert "batch_completed" in events

def test_batch_validation_fail(file_patches, dummy_upload_service, dummy_validation_framework):
    c = BatchUploadController(dummy_upload_service, dummy_validation_framework)
    c.add_files(["ok1.pdf", "bad1.sim"])
    l = DummyListener()
    c.add_listener(l)
    c.upload_batch()
    time.sleep(0.2)
    assert c.status == BatchStatus.VALIDATION_FAILED
    assert dummy_validation_framework.last_report["success"] is False

def test_pause_resume_cancel(file_patches, dummy_upload_service, dummy_validation_framework):
    c = BatchUploadController(dummy_upload_service, dummy_validation_framework)
    c.add_files(["a.pdf","b.img"])
    l = DummyListener()
    c.add_listener(l)
    t = threading.Thread(target=c.upload_batch)
    t.start()
    time.sleep(0.05)  # Let upload thread make some progress
    
    c.pause()
    time.sleep(0.05)  # Allow status to propagate
    assert c.status == BatchStatus.PAUSED
    
    c.resume()
    time.sleep(0.05)  # Allow time for resumes
    assert c.status == BatchStatus.IN_PROGRESS
    
    c.cancel()
    time.sleep(0.05)  # Allow cancel time to propagate
    assert c.status == BatchStatus.CANCELED
    t.join()

def test_file_not_found(file_patches, dummy_upload_service, dummy_validation_framework):
    c = BatchUploadController(dummy_upload_service, dummy_validation_framework)
    c.add_files(["nonexistent.pdf"])
    l = DummyListener()
    c.add_listener(l)
    
    # Even with patched file operations, the controller should handle missing files gracefully
    c.upload_batch()
    time.sleep(0.1)
    
    # Check that appropriate events were fired
    error_events = [ev for ev in l.events if ev[0] == "error"]
    assert len(error_events) > 0

def test_mixed_file_validation(file_patches, dummy_upload_service, dummy_validation_framework):
    """Test validation with mixed valid and invalid files."""
    c = BatchUploadController(dummy_upload_service, dummy_validation_framework)
    c.add_files(["ok1.pdf", "bad1.sim", "test1.pdf"])
    l = DummyListener()
    c.add_listener(l)
    
    # Validate without uploading
    result = c.validate_batch()
    assert result["success"] is False
    assert len([f for f in result["errors"] if "bad" in f]) == 1
    
    # Check that validation events were fired
    validation_events = [ev for ev in l.events if ev[0] == "validation"]
    assert len(validation_events) > 0

def test_batch_with_named_id(file_patches, dummy_upload_service, dummy_validation_framework):
    """Test creating a batch with a specific ID and destination."""
    c = BatchUploadController(dummy_upload_service, dummy_validation_framework)
    batch_id = "test_batch_001"
    destination = "/uploads/special"
    
    c.start_batch(batch_id, ["test1.pdf", "test2.mp4"], destination)
    assert c.batch_id == batch_id
    assert c.destination == destination
    assert len(c.files) == 2
    
    l = DummyListener()
    c.add_listener(l)
    c.upload_batch()
    time.sleep(0.25)
    
    assert c.status == BatchStatus.COMPLETED
    assert c.get_total_progress() == 100

def test_detailed_progress_reporting(file_patches, dummy_upload_service, dummy_validation_framework):
    """Test that detailed progress information is available per file."""
    c = BatchUploadController(dummy_upload_service, dummy_validation_framework)
    c.add_files(["test1.pdf", "test2.mp4"])
    
    # Start upload in a thread
    t = threading.Thread(target=c.upload_batch)
    t.start()
    time.sleep(0.1)  # Let upload make some progress
    
    # Get detailed progress
    details = c.get_progress_details()
    assert isinstance(details, dict)
    assert len(details) == 2
    
    # Each file should have progress information
    for filename in ["test1.pdf", "test2.mp4"]:
        assert filename in details
        assert "progress" in details[filename]
        assert "status" in details[filename]
    
    c.cancel()
    t.join()

def test_validation_events(file_patches, dummy_upload_service, dummy_validation_framework):
    """Test that validation events are properly fired."""
    c = BatchUploadController(dummy_upload_service, dummy_validation_framework)
    c.add_files(["ok1.pdf", "bad1.sim"])
    
    l = DummyListener()
    c.add_listener(l)
    
    # Trigger validation
    c.validate_batch()
    
    # Check for validation events
    validation_events = [ev for ev in l.events if ev[0] == "validation"]
    assert len(validation_events) > 0
    
    # The payload should contain validation results
    assert "success" in validation_events[0][1]
    assert validation_events[0][1]["success"] is False
