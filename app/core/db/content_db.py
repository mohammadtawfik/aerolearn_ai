"""
ContentDB stub for integration testing.

Provides minimal is_uploaded logic for test_professor_upload_workflow.

Location: /app/core/db/content_db.py
"""

class ContentDB:
    def __init__(self):
        # In actual implementation, connect to DB or manage storage
        self.uploaded_files = set()  # Changed from _uploaded_files to match test assertions

    def mark_uploaded(self, filepath: str):
        self.uploaded_files.add(str(filepath))

    def is_uploaded(self, filepath: str) -> bool:
        return str(filepath) in self.uploaded_files
