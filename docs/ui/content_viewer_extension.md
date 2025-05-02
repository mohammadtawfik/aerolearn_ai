# Multi-Format Content Viewer – Extension Points & Integration

**File location:** `/docs/ui/content_viewer_extension.md`

## Overview

The Multi-Format Content Viewer supports rich rendering of PDFs, text, HTML, video, code snippets (with syntax highlighting), and images (with annotation).  
It is integrated within the student dashboard via pluggable widget architecture.

---

## Extension Points

- **Adding a New File/Content Type:**  
  Implement a new QWidget-based viewer (e.g. `Custom3DViewer`) and register it in the content viewer registry.

- **Format Detection:**  
  Override or extend the format detection logic in `/app/ui/student/widgets/`.

- **Annotation/Interaction API:**  
  Provide custom annotation tools by composing with or subclassing the base image/code/doc viewers.

---

## Integration Guide

1. **Implementing a Custom Viewer:**
    ```python
    from PyQt6.QtWidgets import QWidget
    class MySpecialViewer(QWidget):
        # Implement viewer logic
        pass
    ```

2. **Registering the Viewer:**
    Add to the registry (usually in `register_widgets.py` or similar initializer):

    ```python
    content_viewer_registry.register('special', MySpecialViewer)
    ```

3. **Testing:**
    Extend `/tests/ui/test_multi_format_content_viewer.py` with tests for the new viewer.

---

## Customizing User Experience

- Expose user preferences to select default viewers or opt-in to experimental features.
- Use event bus hooks for analytics or cross-widget communication.

---

## Related Files

- `/app/ui/student/widgets/document_viewer.py`
- `/app/ui/student/widgets/video_player.py`
- `/app/ui/student/widgets/code_snippet_viewer.py`
- `/app/ui/student/widgets/image_viewer.py`

See `/tests/ui/test_multi_format_content_viewer.py` for reference test scaffolding.