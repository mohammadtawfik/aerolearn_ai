# Content Extraction Guide — AeroLearn AI

_Last updated: 2024-06-13 (Completed Task 12.2, all tests passing)_

## Overview

AeroLearn AI provides robust extraction of instructional content from PDFs, Word documents, PowerPoint slides, and multimedia files. Features include text & table extraction, metadata harvesting, and content preprocessing for downstream AI/classification tasks.

---

## Extraction Features & Capabilities

### 1. Text Extraction

| Format | Status | Details                      | Notes                     |
|--------|--------|-----------------------------|---------------------------|
| PDF    | ✔      | Direct & OCR fallback        | Via pdfplumber, pytesseract|
| DOCX   | ✔      | All paragraph text           | python-docx               |
| PPTX   | ✔      | Slide text/shape extraction  | python-pptx               |

If the format is unsupported, the extractor will raise a clear error.

### 2. Structured Data Extraction

| Format | Status | Details                       | Notes          |
|--------|--------|------------------------------|----------------|
| PDF    | ✔      | All tables (pdfplumber)      | Accurate on tagged/celled tables|
| DOCX   | ✔      | All tables (python-docx)     | Preserves row/column order|
| PPTX   | ✔      | Table shapes (python-pptx)   | Structure only |

Diagram extraction is placeholder/stub (future ML/vision).

### 3. Multimedia Metadata Extraction

| Type   | Status | Details                             | Notes                                 |
|--------|--------|-------------------------------------|---------------------------------------|
| Image  | ✔      | PNG/JPG/BMP, format, mode, size     | PIL (Pillow) based; EXIF supported    |
| Audio  | ✖      | (Stub/not implemented)              | Mutagen or similar required           |
| Video  | ✖      | (Stub/not implemented)              | MoviePy/OpenCV required               |

### 4. Preprocessing

All extracted content is cleaned and normalized:
- Lowercased (configurable)
- Punctuation removed (configurable)
- Whitespace normalization
- Batch functions for scaling

---

## Usage Examples

### Basic Extraction

```python
from app.core.extraction import TextExtractor, StructuredDataExtractor, MultimediaMetadataExtractor

# Extract text from various document formats
text_extractor = TextExtractor()
pdf_text = text_extractor.extract_text("lecture_notes.pdf")
docx_text = text_extractor.extract_text("syllabus.docx")
pptx_text = text_extractor.extract_text("presentation.pptx")

# Extract tables from documents
data_extractor = StructuredDataExtractor()
pdf_tables = data_extractor.extract_tables("data_report.pdf")
docx_tables = data_extractor.extract_tables("grades.docx")

# Extract image metadata
meta_extractor = MultimediaMetadataExtractor()
image_meta = meta_extractor.extract_image_metadata("diagram.png")
```

### Advanced Preprocessing

```python
from app.core.ai.preprocessing import ContentPreprocessor

# Initialize preprocessor with custom settings
preprocessor = ContentPreprocessor(
    lowercase=True,
    remove_punctuation=True,
    normalize_whitespace=True
)

# Clean individual text
cleaned_text = preprocessor.clean_text(pdf_text)

# Process multiple documents in batch
document_texts = [pdf_text, docx_text, pptx_text]
cleaned_texts = preprocessor.preprocess_batch(document_texts)

# Extract key terms (if implemented)
key_terms = preprocessor.extract_key_terms(cleaned_text)
```

---

## API Summary

**TextExtractor** — `/app/core/extraction/text_extractor.py`
- `extract_text(filepath: str) -> str`
- `extract_text_from_pdf(filepath: str) -> str`
- `extract_text_from_docx(filepath: str) -> str`
- `extract_text_from_pptx(filepath: str) -> str`

**StructuredDataExtractor** — `/app/core/extraction/structured_data_extractor.py`
- `extract_tables(filepath: str) -> List[List[Any]]`
- `extract_diagrams(filepath: str) -> List[Any]` (stub)

**MultimediaMetadataExtractor** — `/app/core/extraction/multimedia_metadata_extractor.py`
- `extract_image_metadata(filepath: str) -> dict`
- `extract_audio_metadata(filepath: str) -> dict` (not implemented)
- `extract_video_metadata(filepath: str) -> dict` (not implemented)

**ContentPreprocessor** — `/app/core/ai/preprocessing.py`
- `clean_text(text: str, lowercase=True, remove_punctuation=True, normalize_whitespace=True) -> str`
- `preprocess_batch(texts: List[str], **kwargs) -> List[str]`
- `extract_key_terms(text: str, max_terms=10) -> List[str]`

---

## Limitations & Extending

### Current Limitations

- **PDF Extraction**: OCR depends on tesseract quality and configuration; complex layouts may not extract perfectly
- **Table Extraction**: Works best with standard tables; complex merged cells or graphical tables may have issues
- **PPTX**: Limited extraction of complex SmartArt or custom graphics
- **Images**: Only metadata extraction, no content analysis of images
- **Audio/Video**: Metadata extraction not yet implemented

### Extending the System

To add support for new formats:

1. Extend the appropriate extractor class
2. Implement format detection logic
3. Add format-specific extraction method
4. Update unit tests

Example for adding new format support:

```python
# In text_extractor.py
def extract_text_from_epub(self, filepath: str) -> str:
    """Extract text from EPUB e-books"""
    # Implementation using ebooklib or similar
    pass
```

---

## Testing

Unit tests for all extractor classes are in:
- `/tests/core/extraction/test_text_extractor.py`
- `/tests/core/extraction/test_structured_data_extractor.py`
- `/tests/core/extraction/test_multimedia_metadata_extractor.py`
- `/tests/core/ai/test_preprocessing.py`

Run them using:
```bash
pytest tests/core/extraction/
```

---

## Troubleshooting

Common issues and solutions:

1. **OCR not working**: Ensure Tesseract is installed and in PATH
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   # macOS
   brew install tesseract
   ```

2. **Slow PDF processing**: For large documents, consider using batch processing or pagination:
   ```python
   # Process large PDF in chunks
   for page_num in range(1, pdf_doc.page_count, 10):
       chunk = text_extractor.extract_text(pdf_path, pages=range(page_num, page_num+10))
       # Process chunk
   ```

3. **Memory issues**: For very large files, stream processing is recommended:
   ```python
   with open('output.txt', 'w') as out_file:
       for text_chunk in text_extractor.stream_extract(large_file_path):
           out_file.write(text_chunk)
   ```

---

## Changelog

- `2024-06-13`: **Task 12.2 COMPLETE** — Initial stable content extraction pipeline established; all checklist points and tests passing.
