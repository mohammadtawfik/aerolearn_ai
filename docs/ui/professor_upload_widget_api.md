# ProfessorUploadWidget API Documentation

## Overview

The `ProfessorUploadWidget` provides a PyQt6-based drag-and-drop interface for professors to upload multiple files, with integrated progress visualization, event hooks, and MIME/type detection.

## Signals

- **uploadStarted** (`list[dict]`):  
  Emitted when upload is initiated. Each dict contains:
  - `file_id`: unique identifier for the file
  - `filepath`: path to selected file
  - `mimetype`: detected MIME type
  - `size`: file size in bytes

- **uploadProgress** (`file_id: str, percent: int`):  
  Emitted during upload to update UI progress for file.

- **uploadCompleted** (`file_id: str, success: bool`):  
  Emitted when upload is complete (success or failure).

- **uploadFailed** (`file_id: str, error: str`):  
  Emitted when upload fails with error details.

## Core Methods

- **add_files(file_paths: List[str])**  
  Add selected/dropped files to upload list.

- **detect_mimetype(filepath: str) -> str**  
  Returns inferred MIME type string for a file.

- **start_upload()**  
  Triggers upload via underlying UploadService.

- **on_upload_progress(file_id: str, percent: int)**  
  Updates file progress bar.

- **on_upload_completed(file_id: str, success: bool)**  
  Handles file upload completion.

- **on_upload_failed(file_id: str, error: str)**  
  Handles file upload failure.

- **clear()**  
  Clear upload list and reset for new uploads.

## Configuration

- **mime_validator**: Pass custom callable to check file type acceptance.
- **allowed_extensions**: List of allowed file extensions (default: all).
- **max_file_size**: Maximum allowed file size in bytes (default: no limit).

## Integration Examples

### Basic Usage

```python
from app.ui.professor.upload_widget import ProfessorUploadWidget

widget = ProfessorUploadWidget()
widget.uploadStarted.connect(handle_upload_start)
widget.uploadCompleted.connect(handle_upload_complete)
widget.uploadFailed.connect(handle_upload_failure)
layout.addWidget(widget)
```

### With Upload Service

```python
from app.ui.professor.upload_widget import ProfessorUploadWidget
from app.core.upload.upload_service import UploadService

# Create and configure components
upload_widget = ProfessorUploadWidget()
upload_service = UploadService()

# Connect widget to service (signal/slot)
upload_widget.uploadStarted.connect(upload_service.upload_files)
upload_service.progress.connect(upload_widget.on_upload_progress)
upload_service.completed.connect(upload_widget.on_upload_completed)
upload_service.failed.connect(upload_widget.on_upload_failed)

# Add widget to main window/layout
main_layout.addWidget(upload_widget)
```

## Extension Points

- Subclass to add custom validation hooks, additional UI, or events
- Override `detect_mimetype` to implement custom MIME detection
- Customize file dialog filter by modifying the filter string in `open_file_dialog`

## Notes

- Files are _not uploaded_ until you connect `uploadStarted` to an upload handler (service/controller)
- Widget is designed for professor UI but can be extended for students/admin as needed
- Easily testable: UI state and event signals, non-UI business logic unit testable
