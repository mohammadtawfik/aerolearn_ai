"""
Format Validation Framework for AeroLearn AI

- Pluggable architecture (built-in & plugin validators)
- Example: PDF, image, video, text
- Supports aerospace/CAD extensions
"""

from typing import Any

class ValidationResult:
    def __init__(self, valid: bool, detail: str = '', code: str = ''):
        self.valid = valid
        self.detail = detail
        self.code = code

class BaseValidator:
    def validate(self, filepath: str, mimetype: str) -> ValidationResult:
        raise NotImplementedError("Validator must implement validate()")

class PDFValidator(BaseValidator):
    def validate(self, filepath: str, mimetype: str) -> ValidationResult:
        # Only accept PDFs with readable content (stub: checks extension/mimetype)
        if mimetype != "application/pdf":
            return ValidationResult(False, "Not a PDF", "invalid-mimetype")
        if not filepath.lower().endswith('.pdf'):
            return ValidationResult(False, "File extension mismatch", "invalid-extension")
        # TODO: Add real PDF parsing/content check
        return ValidationResult(True)

class ImageValidator(BaseValidator):
    def validate(self, filepath: str, mimetype: str) -> ValidationResult:
        if not mimetype.startswith("image/"):
            return ValidationResult(False, "Not an image", "invalid-mimetype")
        # TODO: Actual image content test (PIL etc)
        return ValidationResult(True)

class VideoValidator(BaseValidator):
    def validate(self, filepath: str, mimetype: str) -> ValidationResult:
        if not mimetype.startswith("video/"):
            return ValidationResult(False, "Not a video", "invalid-mimetype")
        # TODO: Extension/content sniff
        return ValidationResult(True)

class TextValidator(BaseValidator):
    def validate(self, filepath: str, mimetype: str) -> ValidationResult:
        if not (mimetype == "text/plain" or filepath.endswith('.txt')):
            return ValidationResult(False, "Not plain text", "invalid-mimetype")
        return ValidationResult(True)

class ValidatorRegistry:
    def __init__(self):
        self.validators = {}

    def register(self, name: str, validator: BaseValidator):
        self.validators[name] = validator

    def validate(self, name: str, filepath: str, mimetype: str) -> ValidationResult:
        if name in self.validators:
            return self.validators[name].validate(filepath, mimetype)
        return ValidationResult(False, "No validator found", "no-validator")

# EXAMPLE USAGE
validators = ValidatorRegistry()
validators.register('pdf', PDFValidator())
validators.register('image', ImageValidator())
validators.register('video', VideoValidator())
validators.register('text', TextValidator())