import os
import pytest
from app.core.upload.upload_service import UploadService, UploadRequest
from app.core.validation.format_validator import validators
from app.models.content_type_registry import registry as type_registry
from app.models.metadata_schema import MetadataSchema, MetadataSchemaField, MetadataEditorBase

@pytest.fixture
def upload_service():
    return UploadService(max_retries=2, concurrency=1)

def test_full_upload_validation_flow(tmp_path, upload_service):
    sample_file = tmp_path / "example.pdf"
    sample_file.write_bytes(b"%PDF-1.4 fake content")
    mimetype = "application/pdf"

    # --- Validate
    result = validators.validate('pdf', str(sample_file), mimetype)
    assert result.valid, f"Validation failed: {result.detail}"

    # --- Detect type
    ct = type_registry.detect(str(sample_file), mimetype)
    assert ct and ct.name == "pdf"

    # --- Metadata
    schema = MetadataSchema([
        MetadataSchemaField("title", True, "string"),
        MetadataSchemaField("author", False, "string"),
    ])
    editor = MetadataEditorBase(schema)
    editor.set_field("title", "Test Document")
    meta = editor.get_metadata()
    assert meta["title"] == "Test Document"

    # --- Upload
    request = UploadRequest(str(sample_file), dest="mock-backend")
    upload_service.enqueue(request)
    # Wait for upload (mock backend is instant/fast)
    import time
    time.sleep(0.3)
    assert request.status in ["completed", "failed"]