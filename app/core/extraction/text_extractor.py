import os
from typing import Union, List, Dict, Any

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
try:
    import pytesseract
except ImportError:
    pytesseract = None
try:
    from PIL import Image
except ImportError:
    Image = None
try:
    import docx
except ImportError:
    docx = None
try:
    import pptx
except ImportError:
    pptx = None

class TextExtractionError(Exception):
    pass

class TextExtractor:
    """
    Extracts raw text from various document formats including PDF, DOCX, and PPTX.
    Falls back to OCR with tesseract or PIL if necessary.
    """
    def extract_text(self, filepath: str) -> str:
        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.pdf':
            return self._extract_text_from_pdf(filepath)
        elif ext == '.docx':
            return self._extract_text_from_docx(filepath)
        elif ext == '.pptx':
            return self._extract_text_from_pptx(filepath)
        else:
            raise TextExtractionError(f"Unsupported file type: {ext}")

    def _extract_text_from_pdf(self, filepath: str) -> str:
        if not pdfplumber:
            raise ImportError("pdfplumber is required for PDF text extraction.")
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                # If no text, try OCR
                if not text.strip() and pytesseract and Image:
                    im = page.to_image(resolution=300).original
                    text += pytesseract.image_to_string(im)
        return text

    def _extract_text_from_docx(self, filepath: str) -> str:
        if not docx:
            raise ImportError("python-docx is required for DOCX text extraction.")
        doc = docx.Document(filepath)
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

    def _extract_text_from_pptx(self, filepath: str) -> str:
        if not pptx:
            raise ImportError("python-pptx is required for PPTX text extraction.")
        prs = pptx.Presentation(filepath)
        text_runs = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text_runs.append(shape.text)
        return "\n".join(text_runs)