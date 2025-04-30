import pytest
from app.core.extraction.structured_data_extractor import StructuredDataExtractor, StructuredDataExtractionError

def test_extract_tables_unsupported():
    extractor = StructuredDataExtractor()
    with pytest.raises(StructuredDataExtractionError):
        extractor.extract_tables("file.unknown")

def test_extract_diagrams_placeholder():
    extractor = StructuredDataExtractor()
    diagrams = extractor.extract_diagrams("file.pdf")
    assert diagrams == []