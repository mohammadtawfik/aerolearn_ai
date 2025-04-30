import pytest
from app.core.extraction.multimedia_metadata_extractor import MultimediaMetadataExtractor, MultimediaMetadataExtractionError

def test_image_metadata_importerror(monkeypatch):
    # Simulate ImportError
    monkeypatch.setattr("app.core.extraction.multimedia_metadata_extractor.Image", None)
    extractor = MultimediaMetadataExtractor()
    with pytest.raises(ImportError):
        extractor.extract_image_metadata("image.png")

def test_audio_metadata_not_implemented():
    extractor = MultimediaMetadataExtractor()
    with pytest.raises(NotImplementedError):
        extractor.extract_audio_metadata("audio.mp3")

def test_video_metadata_not_implemented():
    extractor = MultimediaMetadataExtractor()
    with pytest.raises(NotImplementedError):
        extractor.extract_video_metadata("video.mp4")