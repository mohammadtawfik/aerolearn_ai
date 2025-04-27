"""
UploadService: Handles efficient, robust file uploads for AeroLearn AI.
Features:
- Chunked upload for large files
- Retry mechanism with configurable policies
- Concurrent upload management (queue, pausing)
- Progress tracking & status reporting
- Pluggable backend destination (cloud/local for now)
- Backoff strategy for retries
- Upload cancellation support

NOTE: This is a scaffold/partial for integration; extend as needed.

Author: AeroLearn AI Team
"""

import os
import time
import uuid
import logging
from typing import Callable, Optional, Any, List, Dict
from threading import Lock, Thread, Event
import queue

class UploadStatus:
    QUEUED = 'queued'
    UPLOADING = 'uploading'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class UploadRequest:
    def __init__(self, filepath: str, dest: str, callbacks: Optional[dict]=None, 
                 metadata: Optional[dict]=None):
        self.id = str(uuid.uuid4())
        self.filepath = filepath
        self.dest = dest
        self.size = os.path.getsize(filepath)
        self.status = UploadStatus.QUEUED
        self.progress = 0
        self.attempts = 0
        self.callbacks = callbacks or {}
        self.metadata = metadata or {}
        self.cancel_event = Event()
        self.error = None
        self.last_error_time = 0

class BackoffStrategy:
    """Implements exponential backoff with jitter for retries"""
    
    def __init__(self, initial_delay: float = 1.0, max_delay: float = 60.0, 
                 factor: float = 2.0, jitter: float = 0.1):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.factor = factor
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter"""
        delay = min(self.initial_delay * (self.factor ** attempt), self.max_delay)
        # Add jitter to avoid thundering herd problem
        jitter_amount = delay * self.jitter
        return delay + (jitter_amount * (2 * (0.5 - random.random())))

class UploadService:
    CHUNK_SIZE = 2 * 1024 * 1024  # 2 MB default chunk size

    def __init__(self, max_retries: int = 3, concurrency: int = 2, 
                 chunk_size: int = None, backend=None):
        self.max_retries = max_retries
        self.concurrency = concurrency
        self.chunk_size = chunk_size or self.CHUNK_SIZE
        self.backend = backend  # Storage backend (could be S3, local, etc.)
        self.upload_queue = queue.Queue()
        self.active_uploads: Dict[str, UploadRequest] = {}
        self.lock = Lock()
        self.running = True
        self.backoff = BackoffStrategy()
        self.logger = logging.getLogger("UploadService")
        
        # Start worker threads
        self.threads = [
            Thread(target=self._worker, daemon=True, name=f"UploadWorker-{i}")
            for i in range(concurrency)
        ]
        for t in self.threads:
            t.start()

    def enqueue(self, upload: UploadRequest) -> str:
        """Add an upload to the queue and return its ID"""
        with self.lock:
            self.active_uploads[upload.id] = upload
        self.upload_queue.put(upload)
        return upload.id
        
    def get_upload_status(self, upload_id: str) -> Optional[UploadRequest]:
        """Get the current status of an upload by ID"""
        with self.lock:
            return self.active_uploads.get(upload_id)
            
    def cancel_upload(self, upload_id: str) -> bool:
        """Cancel an upload by ID"""
        with self.lock:
            if upload_id in self.active_uploads:
                upload = self.active_uploads[upload_id]
                upload.cancel_event.set()
                upload.status = UploadStatus.CANCELLED
                if 'cancelled' in upload.callbacks:
                    upload.callbacks['cancelled'](upload)
                return True
        return False

    def _worker(self):
        """Worker thread that processes uploads from the queue"""
        while self.running:
            try:
                upload: UploadRequest = self.upload_queue.get(timeout=1)
                self._process_upload(upload)
                self.upload_queue.task_done()
            except queue.Empty:
                continue
            except Exception as ex:
                self.logger.exception(f"Unexpected error in upload worker: {ex}")

    def _process_upload(self, upload: UploadRequest):
        """Process a single upload with retry logic"""
        upload.status = UploadStatus.UPLOADING
        
        # Notify started callback if available
        if 'started' in upload.callbacks:
            upload.callbacks['started'](upload)
            
        while upload.attempts < self.max_retries:
            if upload.cancel_event.is_set():
                self.logger.info(f"Upload {upload.id} was cancelled")
                return
                
            try:
                self._upload_file(upload)
                
                # If we get here, upload was successful
                upload.status = UploadStatus.COMPLETED
                if 'completed' in upload.callbacks:
                    upload.callbacks['completed'](upload)
                    
                # Remove from active uploads if completed
                with self.lock:
                    self.active_uploads.pop(upload.id, None)
                return
                
            except Exception as ex:
                upload.attempts += 1
                upload.error = str(ex)
                upload.last_error_time = time.time()
                
                self.logger.warning(f"Upload attempt {upload.attempts} failed for {upload.id}: {ex}")
                
                # Check if we've exhausted retries
                if upload.attempts >= self.max_retries:
                    upload.status = UploadStatus.FAILED
                    if 'failed' in upload.callbacks:
                        upload.callbacks['failed'](upload, ex)
                    
                    # Remove from active uploads if failed
                    with self.lock:
                        self.active_uploads.pop(upload.id, None)
                    return
                
                # Wait with backoff before retrying
                retry_delay = self.backoff.get_delay(upload.attempts)
                self.logger.info(f"Retrying upload {upload.id} in {retry_delay:.2f}s")
                
                # Wait but allow for cancellation during the wait
                if upload.cancel_event.wait(retry_delay):
                    upload.status = UploadStatus.CANCELLED
                    if 'cancelled' in upload.callbacks:
                        upload.callbacks['cancelled'](upload)
                    return

    def _upload_file(self, upload: UploadRequest):
        """Upload a file in chunks with progress tracking"""
        with open(upload.filepath, 'rb') as f:
            sent = 0
            total = upload.size
            chunk_num = 0
            
            # Calculate optimal chunk size based on file size
            chunk_size = self._calculate_optimal_chunk_size(total)
            
            while sent < total:
                if upload.cancel_event.is_set():
                    raise InterruptedError("Upload was cancelled")
                    
                # Read the next chunk
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                    
                # Upload the chunk (either to backend or mock implementation)
                self._upload_chunk(upload, chunk, chunk_num, sent)
                
                # Update progress
                sent += len(chunk)
                chunk_num += 1
                upload.progress = int(100 * sent / total)
                
                # Call progress callback if provided
                if 'progress' in upload.callbacks:
                    upload.callbacks['progress'](upload, upload.progress)

    def _upload_chunk(self, upload: UploadRequest, chunk: bytes, chunk_num: int, offset: int):
        """Upload a single chunk to the backend"""
        # If we have a backend, use it
        if self.backend:
            self.backend.upload_chunk(
                upload_id=upload.id,
                chunk_data=chunk,
                chunk_number=chunk_num,
                offset=offset,
                destination=upload.dest,
                metadata=upload.metadata
            )
        else:
            # Mock implementation - simulate network delay
            time.sleep(0.1)  # Simulate network latency
            # In a real implementation, this would send to S3, GCS, etc.
            self.logger.debug(f"Mock upload chunk {chunk_num} for {upload.id}, size={len(chunk)}")

    def _calculate_optimal_chunk_size(self, file_size: int) -> int:
        """Calculate optimal chunk size based on file size"""
        # For very small files, use smaller chunks
        if file_size < 1024 * 1024:  # < 1MB
            return min(file_size, 256 * 1024)  # 256KB or file size
        # For medium files
        elif file_size < 100 * 1024 * 1024:  # < 100MB
            return 1 * 1024 * 1024  # 1MB
        # For large files
        else:
            return self.chunk_size  # Use default (2MB)

    def pause_upload(self, upload_id: str) -> bool:
        """Pause an upload by ID"""
        with self.lock:
            if upload_id in self.active_uploads:
                upload = self.active_uploads[upload_id]
                if upload.status == UploadStatus.UPLOADING:
                    upload.status = UploadStatus.PAUSED
                    # In a real implementation, we'd need to handle this in the worker
                    if 'paused' in upload.callbacks:
                        upload.callbacks['paused'](upload)
                    return True
        return False

    def resume_upload(self, upload_id: str) -> bool:
        """Resume a paused upload"""
        with self.lock:
            if upload_id in self.active_uploads:
                upload = self.active_uploads[upload_id]
                if upload.status == UploadStatus.PAUSED:
                    upload.status = UploadStatus.QUEUED
                    self.upload_queue.put(upload)
                    return True
        return False

    def get_all_uploads(self) -> List[UploadRequest]:
        """Get a list of all active uploads"""
        with self.lock:
            return list(self.active_uploads.values())

    def stop(self):
        """Stop the upload service and its worker threads"""
        self.running = False
        for t in self.threads:
            t.join(timeout=2.0)
import random  # Add this at the top of the file with other imports
