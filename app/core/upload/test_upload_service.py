import os
import tempfile
import pytest
from PyQt6.QtCore import QCoreApplication
from app.core.upload.upload_service import UploadService

@pytest.fixture(scope="module")
def qapp():
    app = QCoreApplication([])
    yield app

@pytest.fixture
def dummy_file():
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    tmpfile.write(b"A" * 5 * 1024 * 1024)  # 5MB file
    tmpfile.close()
    yield tmpfile.name
    os.unlink(tmpfile.name)

def test_successful_upload(qapp, dummy_file):
    service = UploadService(chunk_size=1024*1024, max_retries=1)
    results = {'progress': [], 'completed': False}

    def on_progress(fid, percent):
        results['progress'].append(percent)
    def on_complete(fid, success):
        results['completed'] = success

    service.uploadProgress.connect(on_progress)
    service.uploadCompleted.connect(on_complete)
    service.upload_files([{'filepath': dummy_file, 'mimetype': 'application/pdf'}])

    # Wait for upload finish
    import time
    timeout = time.time() + 5
    while not results['completed'] and time.time() < timeout:
        qapp.processEvents()
        time.sleep(0.1)

    assert results['progress'][-1] == 100
    assert results['completed'] is True

def test_upload_retries_on_error(qapp, dummy_file, monkeypatch):
    service = UploadService(chunk_size=1024*1024, max_retries=2, retry_delay=0.1)
    attempted = []

    # Patch _upload_file to fail once, then succeed
    def flaky_upload(file):
        if not attempted:
            attempted.append(True)
            raise IOError("Mock upload fail")
        else:
            return UploadService._upload_file(service, file)

    monkeypatch.setattr(service, "_upload_file", flaky_upload)
    completed = {'val': False}

    def on_complete(fid, success):
        completed['val'] = success

    service.uploadCompleted.connect(on_complete)
    service.upload_files([{'filepath': dummy_file, 'mimetype': 'application/pdf'}])

    import time
    timeout = time.time() + 5
    while not completed['val'] and time.time() < timeout:
        qapp.processEvents()
        time.sleep(0.05)

    assert completed['val'] is True
    assert len(attempted) == 1

def test_upload_failed_emits_error(qapp, dummy_file, monkeypatch):
    service = UploadService(chunk_size=1024*1024, max_retries=1, retry_delay=0.05)
    monkeypatch.setattr(service, "_upload_file", lambda file: (_ for _ in ()).throw(IOError("Always fails")))
    failed = []

    def on_fail(fid, err):
        failed.append((fid, err))

    service.uploadFailed.connect(on_fail)
    service.upload_files([{'filepath': dummy_file, 'mimetype': 'application/pdf'}])

    import time
    timeout = time.time() + 3
    while not failed and time.time() < timeout:
        qapp.processEvents()
        time.sleep(0.05)

    assert len(failed) == 1
    assert "Always fails" in failed[0][1]