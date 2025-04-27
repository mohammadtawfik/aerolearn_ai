# Batch Upload System API Documentation

## Event Types
- `batch_started`: Batch initialization
- `file_upload_progress`: Individual file progress
- `batch_paused`/`batch_resumed`/`batch_canceled`
- `validation_started`/`validation_completed`/`validation_failed`
- `batch_summary`: Final status report

## Core Methods
```python
class BatchUploadController:
    def start_batch(batch_id: str, files: List[str], dest: str) 
    def validate_batch(batch_id: str) -> Tuple[bool, dict]
    def get_validation_report(batch_id: str) -> dict
    def pause_batch(batch_id: str)
    def resume_batch(batch_id: str)
    def cancel_batch(batch_id: str)
    def get_batch_status(batch_id: str) -> dict
```

## Usage Example
```python
controller = BatchUploadController(upload_service, validator)
controller.start_batch("lectures", files, "/course-materials")

# Register event listener
class MyListener(BatchUploadListener):
    def on_batch_event(self, event):
        if event.event_type == "batch_validated":
            handle_validation(event.payload)
            
controller.add_listener(MyListener())
```

## Validation Report Structure
```json
{
  "valid": false,
  "summary": "2 of 5 files invalid",
  "invalid_files": [
    {
      "file": "presentation.ppt",
      "errors": ["Unsupported file format"],
      "suggested_format": "pptx"
    }
  ]
}
```