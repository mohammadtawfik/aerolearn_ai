"""
Content Type Registry

- Provides taxonomy and categorization for content
- Pluggable for future AI/content analysis
- Used in validation, display, extraction
"""

class ContentType:
    def __init__(self, name, extensions, mimetypes, category):
        self.name = name
        self.extensions = extensions
        self.mimetypes = mimetypes
        self.category = category

class ContentTypeRegistry:
    def __init__(self):
        self.types = []

    def register(self, ct: ContentType):
        self.types.append(ct)

    def detect(self, filename: str, mimetype: str):
        fname = filename.lower()
        for ct in self.types:
            if any(fname.endswith(ext) for ext in ct.extensions) or mimetype in ct.mimetypes:
                return ct
        return None

# Example setup
registry = ContentTypeRegistry()
registry.register(ContentType('pdf', ['.pdf'], ['application/pdf'], 'document'))
registry.register(ContentType('image', ['.jpg', '.jpeg', '.png'], ['image/jpeg', 'image/png'], 'media'))
registry.register(ContentType('video', ['.mp4'], ['video/mp4'], 'media'))
registry.register(ContentType('text', ['.txt'], ['text/plain'], 'document'))