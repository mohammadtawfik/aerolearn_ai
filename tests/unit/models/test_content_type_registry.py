import pytest
from app.models.content_type_registry import ContentTypeRegistry

def test_pdf_detection():
    assert ContentTypeRegistry.detect_type("report.pdf") == "pdf"

def test_image_detection():
    assert ContentTypeRegistry.detect_type("photo.JPG") == "image"
    assert ContentTypeRegistry.detect_type("picture.png") == "image"

def test_video_detection():
    assert ContentTypeRegistry.detect_type("movie.mp4") == "video"

def test_cad_detection():
    assert ContentTypeRegistry.detect_type("wing.step") == "cad"

def test_simulation_detection():
    assert ContentTypeRegistry.detect_type("scenario.sim") == "sim"

def test_fallback_ai_detector():
    ai_mock = lambda f: "pdf" if f.endswith(".strange") else None
    assert ContentTypeRegistry.detect_type("strangetype.strange", ai_detector=ai_mock) == "pdf"