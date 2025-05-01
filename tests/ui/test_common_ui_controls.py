# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---
import os
import sys

def _add_project_root_to_syspath():
    here = os.path.abspath(os.path.dirname(__file__))
    root = here
    while root and not (os.path.isdir(os.path.join(root, "app")) and os.path.isdir(os.path.join(root, "tests"))):
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    if root not in sys.path:
        sys.path.insert(0, root)
_add_project_root_to_syspath()
# --- END PATCH ---

"""
Test Suite for AeroLearn Common UI Controls (Task 4.3, PyQt6 version)

Covers:
- Form controls: validation, value change, error display
- Content browser: item listing, search, selection, drag event
- Content preview: file/type-based preview, error, notification
- Notification signal aggregation
- Simulated drag-and-drop (programmatic, for basic verification)
- Hooks for manual interaction

Requirements: PyQt6, minimal test assets (text/image files for preview step)

To run:
$ python tests/ui/test_common_ui_controls.py

Note: Because most UI verification requires human observation (and/or QtTest for full automation), this provides BOTH interactive UI and signal logging for confirmation.

"""

import sys
import os

try:
    from PyQt6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
    )
    from PyQt6.QtCore import Qt
except ImportError:
    print(
        "ERROR: PyQt6 is not installed in the current environment. "
        "Install it with `pip install PyQt6 PyQt6-Charts` and re-run the test."
    )
    sys.exit(1)

# Import widgets
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app/ui/common")))

from form_controls import TextInputControl, PasswordInputControl, MultiLineTextControl, DropdownControl, CheckboxControl
from content_browser import ContentBrowser
from content_preview import ContentPreview

# --- Notification mock

class NotificationManager(QWidget):
    """Simple notification logger for UI tests."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AeroLearn Notification Center")
        self.layout = QVBoxLayout()
        self.log = QLabel("No notifications.")
        self.layout.addWidget(self.log)
        self.setLayout(self.layout)
        self.history = []

    def notify(self, msg):
        self.history.append(msg)
        self.log.setText("\n".join(self.history[-5:]))

# --- Main Window for Multi-Component Demo

class TestMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AeroLearn - Common UI Controls Test")
        self.layout = QHBoxLayout()
        # Left: Form controls
        self.form_col = QVBoxLayout()
        self.form_col.addWidget(QLabel("<b>Form Controls</b>"))
        self.name_input = TextInputControl("Name", required=True)
        self.password_input = PasswordInputControl("Password (min 4)", required=True, validator=lambda v: len(str(v)) >= 4)
        self.about_input = MultiLineTextControl("About You")
        self.role_dropdown = DropdownControl("Role", options=["Student", "Professor", "Admin"], required=True)
        self.subscribe_chk = CheckboxControl("Subscribe to Notifications")
        for ctrl in [self.name_input, self.password_input, self.about_input, self.role_dropdown, self.subscribe_chk]:
            self.form_col.addWidget(ctrl)

        self.submit_btn = QPushButton("Submit Form")
        self.form_col.addWidget(self.submit_btn)
        self.submit_btn.clicked.connect(self.submit_form)

        # Center: Content Browser
        self.content_col = QVBoxLayout()
        self.content_col.addWidget(QLabel("<b>Content Browser</b>"))
        self.browser = ContentBrowser(content_items=[
            {'id': 't1', 'label': 'Course Syllabus', 'type': 'Document', 'body': 'Read carefully!'},
            {'id': 't2', 'label': 'Lecture 1 Slides', 'type': 'PDF', 'path': 'sample.pdf'},
            {'id': 't3', 'label': 'Rocket Image', 'type': 'Image', 'path': 'sample.png'},
            {'id': 't4', 'label': 'Aerodynamics Video', 'type': 'Video', 'path': 'sample.mp4'},
            {'id': 't5', 'label': 'Welcome Notes', 'type': 'Text', 'body': 'Hello AeroLearn!'},
        ])
        self.content_col.addWidget(self.browser)

        # Right: Content Preview + Notifications
        self.right_col = QVBoxLayout()
        self.right_col.addWidget(QLabel("<b>Content Preview</b>"))
        self.preview = ContentPreview()
        self.right_col.addWidget(self.preview)
        self.notif_center = NotificationManager()
        self.right_col.addWidget(QLabel("<b>Notifications</b>"))
        self.right_col.addWidget(self.notif_center)

        # Event wiring (signal to notification)
        self.preview.notification.connect(self.notif_center.notify)
        self.preview.error_occurred.connect(lambda msg: self.notif_center.notify("ERROR: " + msg))
        self.browser.content_selected.connect(self.preview.preview_content)
        self.browser.content_dragged.connect(lambda c: self.notif_center.notify(f"Drag started: {c.get('label')}"))

        self.layout.addLayout(self.form_col)
        self.layout.addLayout(self.content_col)
        self.layout.addLayout(self.right_col)
        self.setLayout(self.layout)
        self.resize(1200, 600)

    def submit_form(self):
        valid = True
        form_vals = {}
        for ctrl in [self.name_input, self.password_input, self.role_dropdown]:
            if not ctrl.validate():
                valid = False
        # Collect if valid
        form_vals['name'] = self.name_input.get_value()
        form_vals['password'] = self.password_input.get_value()
        form_vals['role'] = self.role_dropdown.get_value()
        if valid:
            self.notif_center.notify("Form submitted: " + str(form_vals))
        else:
            self.notif_center.notify("Form validation failed.")

def main():
    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    sys.exit(app.exec())

def test_pyqt6_installed():
    """Minimal test to show that the UI test suite is present and PyQt6 is importable."""
    try:
        from PyQt6.QtWidgets import QApplication
        assert True
    except ImportError:
        assert False, "PyQt6 not installed"

if __name__ == "__main__":
    # For manual testing with UI interaction:
    # Run "python tests/ui/test_common_ui_controls.py" for the full UI/manual check
    main()
