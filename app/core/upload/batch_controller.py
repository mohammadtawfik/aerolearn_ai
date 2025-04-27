"""
BatchUploadController: Coordinate and track multiple simultaneous uploads.

- Aggregates progress
- Controls pause/resume/cancel for all or any
- Reports status per file & batch
"""

from typing import List, Dict, Callable, Optional, Any
from enum import Enum
from .upload_service import UploadRequest, UploadService


class BatchStatus(Enum):
    """Status of a batch upload operation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class BatchUploadController:
    def __init__(self, upload_service: UploadService):
        self.upload_service = upload_service
        self.active_batches: Dict[str, Dict[str, Any]] = {}

    def start_batch(self, batch_id: str, files: List[str], dest: str, callbacks: Optional[dict] = None):
        """
        Start a new batch upload operation
        
        Args:
            batch_id: Unique identifier for this batch
            files: List of file paths to upload
            dest: Destination path/URL
            callbacks: Optional callbacks for batch events
        """
        if batch_id in self.active_batches:
            raise ValueError(f"Batch ID {batch_id} already exists")
            
        requests = []
        for fp in files:
            # Create individual file callbacks that also trigger batch-level events
            file_callbacks = self._create_file_callbacks(batch_id, fp, callbacks)
            req = UploadRequest(fp, dest, file_callbacks)
            self.upload_service.enqueue(req)
            requests.append(req)
            
        self.active_batches[batch_id] = {
            "requests": requests,
            "status": BatchStatus.IN_PROGRESS,
            "callbacks": callbacks,
            "total_files": len(files),
            "completed_files": 0,
            "failed_files": 0
        }
        
        # Trigger batch started callback if provided
        if callbacks and "on_batch_start" in callbacks:
            callbacks["on_batch_start"](batch_id, len(files))

    def _create_file_callbacks(self, batch_id: str, file_path: str, batch_callbacks: Optional[dict]) -> dict:
        """Create file-specific callbacks that also update batch status"""
        file_callbacks = {}
        
        def on_progress(progress: int):
            # Update batch progress when individual file progress changes
            if batch_callbacks and "on_batch_progress" in batch_callbacks:
                batch_callbacks["on_batch_progress"](batch_id, self.aggregated_progress(batch_id))
                
        def on_complete():
            batch = self.active_batches[batch_id]
            batch["completed_files"] += 1
            
            # Check if batch is complete
            if batch["completed_files"] + batch["failed_files"] == batch["total_files"]:
                if batch["failed_files"] == 0:
                    batch["status"] = BatchStatus.COMPLETED
                    if batch_callbacks and "on_batch_complete" in batch_callbacks:
                        batch_callbacks["on_batch_complete"](batch_id)
                else:
                    batch["status"] = BatchStatus.FAILED
                    if batch_callbacks and "on_batch_error" in batch_callbacks:
                        batch_callbacks["on_batch_error"](batch_id, f"{batch['failed_files']} files failed")
        
        def on_error(error: str):
            batch = self.active_batches[batch_id]
            batch["failed_files"] += 1
            
            if batch_callbacks and "on_file_error" in batch_callbacks:
                batch_callbacks["on_file_error"](batch_id, file_path, error)
        
        file_callbacks["on_progress"] = on_progress
        file_callbacks["on_complete"] = on_complete
        file_callbacks["on_error"] = on_error
        
        return file_callbacks

    def pause_batch(self, batch_id: str):
        """Pause all uploads in a batch"""
        if batch_id not in self.active_batches:
            raise ValueError(f"Batch ID {batch_id} not found")
            
        batch = self.active_batches[batch_id]
        if batch["status"] != BatchStatus.IN_PROGRESS:
            return
            
        batch["status"] = BatchStatus.PAUSED
        
        # Pause all requests in the batch
        for req in batch["requests"]:
            self.upload_service.pause(req)
            
        # Trigger callback if provided
        if batch["callbacks"] and "on_batch_pause" in batch["callbacks"]:
            batch["callbacks"]["on_batch_pause"](batch_id)

    def resume_batch(self, batch_id: str):
        """Resume all uploads in a paused batch"""
        if batch_id not in self.active_batches:
            raise ValueError(f"Batch ID {batch_id} not found")
            
        batch = self.active_batches[batch_id]
        if batch["status"] != BatchStatus.PAUSED:
            return
            
        batch["status"] = BatchStatus.IN_PROGRESS
        
        # Resume all requests in the batch
        for req in batch["requests"]:
            self.upload_service.resume(req)
            
        # Trigger callback if provided
        if batch["callbacks"] and "on_batch_resume" in batch["callbacks"]:
            batch["callbacks"]["on_batch_resume"](batch_id)

    def cancel_batch(self, batch_id: str):
        """Cancel all uploads in a batch"""
        if batch_id not in self.active_batches:
            raise ValueError(f"Batch ID {batch_id} not found")
            
        batch = self.active_batches[batch_id]
        batch["status"] = BatchStatus.CANCELED
        
        # Cancel all requests in the batch
        for req in batch["requests"]:
            self.upload_service.cancel(req)
            
        # Trigger callback if provided
        if batch["callbacks"] and "on_batch_cancel" in batch["callbacks"]:
            batch["callbacks"]["on_batch_cancel"](batch_id)

    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get detailed status information about a batch"""
        if batch_id not in self.active_batches:
            raise ValueError(f"Batch ID {batch_id} not found")
            
        batch = self.active_batches[batch_id]
        
        # Collect individual file statuses
        file_statuses = []
        for req in batch["requests"]:
            file_statuses.append({
                "file": req.file_path,
                "progress": req.progress,
                "status": req.status if hasattr(req, "status") else "unknown"
            })
            
        return {
            "id": batch_id,
            "status": batch["status"].value,
            "progress": self.aggregated_progress(batch_id),
            "total_files": batch["total_files"],
            "completed_files": batch["completed_files"],
            "failed_files": batch["failed_files"],
            "files": file_statuses
        }

    def aggregated_progress(self, batch_id: str) -> int:
        """Calculate the overall progress percentage of a batch"""
        if batch_id not in self.active_batches:
            raise ValueError(f"Batch ID {batch_id} not found")
            
        batch = self.active_batches[batch_id]
        requests = batch["requests"]
        
        if not requests:
            return 0
            
        total = sum(r.progress for r in requests)
        return int(total / len(requests))
