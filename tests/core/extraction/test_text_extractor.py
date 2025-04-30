import pytest
from app.core.extraction.text_extractor import TextExtractor, TextExtractionError

def test_extract_text_unsupported():
    extractor = TextExtractor()
    with pytest.raises(TextExtractionError):
        extractor.extract_text("file.unsupported")

# For demonstration: future tests would use sample PDF/DOCX/PPTX files with known outputs.
# def test_extract_text_pdf(sample_pdf_file):
#     extractor = TextExtractor()
#     text = extractor.extract_text(sample_pdf_file)
#     assert "Known text" in text