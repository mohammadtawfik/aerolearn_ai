import pytest
from app.models.content_type_registry import ContentTypeRegistry, content_type_registry, register_plugin

def test_pdf_detection_by_extension():
    r = content_type_registry
    assert r.detect("lecture1.pdf", "application/pdf") == "pdf"
    assert r.detect("lecture1.PDF", "application/pdf") == "pdf"
    assert r.detect("lecture1.pdf", "foo/type") == "pdf"
    assert r.get_category("pdf") == "Document/PDF"
    assert r.extract_metadata("pdf", "lecture1.pdf") == {"page_count": 10}

def test_pdf_detection_by_mimetype():
    r = content_type_registry
    assert r.detect("randomfile", "application/pdf") == "pdf"

def test_slide_deck_detection():
    r = content_type_registry
    assert r.detect("lesson.ppt", "application/vnd.ms-powerpoint") == "slide_deck"
    assert r.detect("slides.pptx", "application/any") == "slide_deck"
    assert r.detect("slides.any", "application/vnd.openxmlformats-officedocument.presentationml.presentation") == "slide_deck"

def test_image_detection():
    r = content_type_registry
    assert r.detect("pic.jpg", "image/jpeg") == "image"
    assert r.detect("photo.png", "foo/bar") == "image"
    assert r.detect("photo.JPG", None) == "image"
    assert r.detect("picture.png", None) == "image"

def test_video_detection():
    r = content_type_registry
    assert r.detect("movie.mp4", "video/mp4") == "video"
    assert r.detect("clip.avi", "video/avi") == "video"

def test_cad_detection():
    r = content_type_registry
    assert r.detect("wing.step", None) == "cad"

def test_simulation_detection():
    r = content_type_registry
    assert r.detect("scenario.sim", None) == "sim"

def test_unknown_detection():
    r = content_type_registry
    assert r.detect("notype.unknown", None) is None

def test_ai_detector_fallback():
    # Test with context containing AI result
    context = {"ai_result": "ai_detected_type"}
    r = content_type_registry
    assert r.detect("mystery.file", "application/octet-stream", context) == "ai_detected_type"
    
    # Test with function-based AI detector
    ai_mock = lambda f: "pdf" if f.endswith(".strange") else None
    assert r.detect("strangetype.strange", None, ai_detector=ai_mock) == "pdf"

def test_metadata_extraction():
    r = content_type_registry
    meta = r.extract_metadata("pdf", "lecture1.pdf")
    assert "page_count" in meta
    
    # Test metadata extraction for other types
    assert isinstance(r.extract_metadata("image", "photo.jpg"), dict)
    assert isinstance(r.extract_metadata("video", "movie.mp4"), dict)

def test_supported_types_and_taxonomy():
    r = content_type_registry
    types = r.supported_types()
    taxonomy = r.get_taxonomy()
    
    # All registered types should have a category
    for name in types:
        assert name in taxonomy
        assert taxonomy[name]

def test_plugin_registration_and_detection():
    # Dynamically register a new type plugin
    class CustomPlugin:
        @staticmethod
        def custom_detector(path, mimetype, context):
            if path and path.lower().endswith('.custom'):
                return "custom_type"
            return None
            
        @staticmethod
        def register_with_registry(registry):
            registry.register(
                name="custom_type",
                category="Custom/Type",
                mimetypes=["application/custom"],
                extensions=[".custom"],
                detector=CustomPlugin.custom_detector,
                description="Custom File Type"
            )
    
    register_plugin(CustomPlugin)
    r = content_type_registry
    assert r.detect("file.custom", "application/custom") == "custom_type"
    assert r.get_category("custom_type") == "Custom/Type"

def test_error_handling():
    r = content_type_registry
    # Test with None inputs
    assert r.detect(None, None) is None
    
    # Test with invalid type for metadata extraction
    with pytest.raises(ValueError):
        r.extract_metadata("nonexistent_type", "file.xyz")
    
    # Test with invalid category lookup
    with pytest.raises(KeyError):
        r.get_category("nonexistent_type")
