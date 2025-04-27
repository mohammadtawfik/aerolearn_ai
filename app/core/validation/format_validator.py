"""
Format Validation Framework for AeroLearn AI

- Pluggable architecture (built-in & plugin validators)
- Example: PDF, image, video, text
- Supports aerospace/CAD extensions
"""

from typing import Any, Dict, Type

class ValidationResult:
    def __init__(self, valid: bool, detail: str = '', code: str = ''):
        self.valid = valid
        self.detail = detail
        self.code = code
        
    @property
    def success(self):
        """Alias for compatibility: .success == .valid"""
        return self.valid

    @property
    def errors(self):
        """Alias for compatibility: .errors == .detail (usually string/list)"""
        return self.detail

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

# Type alias for validator registry
ValidatorRegistry = Dict[str, BaseValidator]

class ValidationFramework:
    def __init__(self):
        self.validators: ValidatorRegistry = {}
        self._plugins: list[BaseValidator] = []

    def register(self, name: str, validator: BaseValidator):
        self.validators[name] = validator
        
    def register_plugin(self, plugin: BaseValidator):
        self._plugins.append(plugin)

    def validate(self, name: str, filepath: str, mimetype: str) -> ValidationResult:
        if name in self.validators:
            return self.validators[name].validate(filepath, mimetype)
        return ValidationResult(False, "No validator found", "no-validator")

# Create and configure instance
validation_framework = ValidationFramework()
validation_framework.register('pdf', PDFValidator())
validation_framework.register('image', ImageValidator())
validation_framework.register('video', VideoValidator())
validation_framework.register('text', TextValidator())

# Export both class and instance
__all__ = ['ValidationFramework', 'validation_framework', 'ValidatorRegistry']
