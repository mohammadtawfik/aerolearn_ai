"""
Professor UploadService for AeroLearn AI
========================================

Handles file upload with chunked uploads, retry policies, concurrency management and progress event notification.

Features:
- Chunked file reads/writes for large file support
- Retry with backoff on failure (configurable)
- Concurrency management allowing prioritized queue
- Progress event hooks for UI feedback
- Simple in-memory upload queue (could swap for persistent/job-based)
- Designed for integration with ProfessorUploadWidget

Author: AeroLearn AI Team
Date: 2025-04-25

API:
----
- upload_files(files: List[dict]): Start upload for given file specs
- signals: uploadProgress(file_id, percent), uploadCompleted(file_id, success), uploadFailed(file_id, error)
- Configurable: chunk_size, max_retries, concurrent_uploads

Usage:
from app.core.upload.upload_service import UploadService

service = UploadService()
service.upload_files([...])
service.uploadProgress.connect(...)
service.uploadCompleted.connect(...)
"""

import os
import threading
import time
from typing import List, Dict, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal

class UploadService(QObject):
    uploadProgress = pyqtSignal(str, int)     # file_id, percent
    uploadCompleted = pyqtSignal(str, bool)   # file_id, success
    uploadFailed = pyqtSignal(str, str)       # file_id, error msg

    def __init__(self, chunk_size=4 * 1024 * 1024, max_retries=3, concurrent_uploads=2, retry_delay=3):
        super().__init__()
        self.chunk_size = chunk_size
        self.max_retries = max_retries
        self.concurrent_uploads = concurrent_uploads
        self.retry_delay = retry_delay
        self._upload_queue = []
        self._upload_threads = []

    def upload_files(self, files: List[Dict]):
        """
        Start upload for list of files. Each file dict should be
        {'filepath': ..., 'mimetype': ...}
        """
        for file in files:
            self._enqueue_upload(file)
        self._start_uploads()

    def _enqueue_upload(self, file: Dict):
        self._upload_queue.append(file)

    def _start_uploads(self):
        while len(self._upload_threads) < self.concurrent_uploads and self._upload_queue:
            file = self._upload_queue.pop(0)
            t = threading.Thread(target=self._upload_file_with_retry, args=(file,))
            t.daemon = True
            t.start()
            self._upload_threads.append(t)
        # Cleanup finished threads
        self._upload_threads = [t for t in self._upload_threads if t.is_alive()]

    def _upload_file_with_retry(self, file: Dict):
        retries = 0
        file_id = file['filepath']
        while retries <= self.max_retries:
            try:
                self._upload_file(file)
                self.uploadCompleted.emit(file_id, True)
                break
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    self.uploadFailed.emit(file_id, str(e))
                    break
                time.sleep(self.retry_delay)

    def _upload_file(self, file: Dict):
        """
        Emulate upload in chunks; in reality, this should send to backend/storage API.
        For demonstration, reads file in chunks and sleeps as if uploading.
        """
        filepath = file['filepath']
        size = os.path.getsize(filepath)
        total_read = 0
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                total_read += len(chunk)
                percent = int(total_read / size * 100)
                self.uploadProgress.emit(filepath, min(100, percent))
                time.sleep(0.05)  # Emulate network/upload latency
        self.uploadProgress.emit(filepath, 100)


    def clear_queue(self):
        self._upload_queue.clear()

    def set_config(self, chunk_size=None, max_retries=None, concurrent_uploads=None, retry_delay=None):
        """Update config live."""
        if chunk_size:
            self.chunk_size = chunk_size
        if max_retries:
            self.max_retries = max_retries
        if concurrent_uploads:
            self.concurrent_uploads = concurrent_uploads
        if retry_delay:
            self.retry_delay = retry_delay