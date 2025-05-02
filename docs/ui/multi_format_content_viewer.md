# Multi-Format Content Viewer (Student UI)

*File Location: `/docs/ui/student/multi_format_content_viewer.md`*

This guide documents the features, integration methods, and extension points for the student multi-format content viewers introduced in Task 3.2.2.

---

## Supported Viewers

- **DocumentViewerWidget** – Supports PDF, text, and HTML
- **VideoPlayerWidget** – Handles video playback and future learning features
- **CodeSnippetViewerWidget** – Syntax-highlighted code display (Python; extendable)
- **ImageViewerWidget** – Image viewing, with future annotation features

---

## Integration

All viewers are registered in `/app/ui/student/widget_registry.py` and can be dynamically loaded by the student dashboard and UI composition tools.

**Example Integration:**
```python
from app.ui.student.widgets.document_viewer import DocumentViewerWidget

viewer = DocumentViewerWidget()
viewer.load_content("path/to/content.pdf")
```

---

## Extending Viewers

- **Add New Viewer**
  1. Create a widget in `/app/ui/student/widgets/new_viewer_name.py`
  2. Register in `/app/ui/student/widget_registry.py`
  3. Add tests under `/tests/ui/`
  4. Update this documentation

- **DocumentViewerWidget**: Add more document type handlers in `load_content`.
- **CodeSnippetViewerWidget**: Extend lexer selection or use a different syntax highlighter for other languages.

---

## Testing

Automated tests live in `/tests/ui/test_multi_format_content_viewer.py`.

---

## Maintenance

- Keep all 3rd party dependencies up to date (PyQt6, QScintilla, etc.)
- Extend viewers’ capabilities by subclassing. Use PyQt signals/slots for integration.