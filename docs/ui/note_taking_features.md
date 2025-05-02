# Student Note-Taking System – User & Dev Guide

**File location:** `/docs/ui/note_taking_features.md`

## Overview

The Student Note-Taking System lets users create, organize, and retrieve notes directly from the dashboard, integrated with course content.

---

## Features

- **Rich Text Editor:**  
  Text formatting (bold, italic, lists), embedding media, and direct in-dashboard note creation (see `RichTextNoteEditor`).

- **Content Reference Linking:**  
  Link notes to specific course/module/lesson content via reference widgets and UI hooks.

- **Tagging & Organization:**  
  Add user-defined tags, organize notes in folders, search/filter by tag/content.

- **Note Search:**  
  Indexed note search for keywords, tags, or references.

- **Cloud Sync:**  
  Optional: Synchronize notes between devices via the system’s local cache or integrated cloud API.

---

## Integration

- Each note widget instance is tied to content context or user profile in the dashboard.
- Reference linking components listen for selection/events from the active viewer or navigator widget.

---

## Extension Points

- **Custom Storage:**  
  Plug in a different backend (SQLite, cloud service) by implementing the note service interface.

- **UI Integration:**  
  Integrate with other student widgets by subscribing/publishing to the dashboard event bus.

---

## Usage Example

```python
# Embed a RichTextNoteEditor in a dashboard layout:
note_widget = RichTextNoteEditor(initial_note="Welcome!", parent=self)
dashboard.add_widget("richtext_note_editor", note_widget)
```

---

## Testing & Sync

- Test persistence and sync by extending `/tests/ui/test_student_dashboard.py` and (optionally) integration tests in `/tests/integration/`.

---

## References

- `/app/ui/student/widgets/richtext_note_editor.py`
- `/app/ui/student/widgets/note_reference_linker.py`
- `/app/ui/student/widgets/note_organizer.py`
- `/app/ui/student/widgets/note_search.py`