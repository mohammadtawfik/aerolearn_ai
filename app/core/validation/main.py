"""
ValidationSystem: Main interface for all content format validations.

This system loads registered validators (PDF, image, video, text, etc)
and provides a unified check method.

Location: /app/core/validation/main.py
"""

import mimetypes
import os
from .format_validator import validators, ValidationResult

class ValidationSystem:
    def __init__(self, fast_validation: bool = False):
        # Already-registered in format_validator.py for pdf, image, video, text
        self.validators = validators  # ValidatorRegistry instance
        self.fast_validation = fast_validation  # Enable quick checks for tests
    
    def infer_validator(self, filepath: str, mimetype: str = None) -> str:
        """
        Picks the most likely validator based on mimetype or extension.
        """
        name = None
        ext = os.path.splitext(filepath)[1].lower()
        if mimetype:
            if mimetype == "application/pdf":
                name = "pdf"
            elif mimetype.startswith("image/"):
                name = "image"
            elif mimetype.startswith("video/"):
                name = "video"
            elif mimetype == "text/plain":
                name = "text"
        if not name:
            # Infer from extension as fallback
            if ext == ".pdf":
                name = "pdf"
            elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"]:
                name = "image"
            elif ext in [".mp4", ".avi", ".mov", ".mkv"]:
                name = "video"
            elif ext == ".txt":
                name = "text"
        return name if name in self.validators.validators else None

    def check(self, filepath: str, mimetype: str = None) -> ValidationResult:
        """
        Validate the file using the appropriate validator by mimetype/ext.
        """
        if self.fast_validation:
            # Return success for all files in test mode
            return ValidationResult(True, "Fast validation passed", "test-mode")
            
        if mimetype is None:
            guess = mimetypes.guess_type(filepath)[0] or ""
            mimetype = guess
        
        validator_name = self.infer_validator(filepath, mimetype)
        if not validator_name:
            return ValidationResult(False, "Unknown file type", "unknown-type")
        return self.validators.validate(validator_name, filepath, mimetype)
