"""
File Location: /tests/ui/test_student_dashboard_content_viewer.py
Purpose: Integration tests for StudentDashboard's handling of multi-format content viewing.
"""

import pytest

from PyQt6.QtWidgets import QApplication
from app.ui.student.dashboard import StudentDashboard

@pytest.fixture(scope="module")
def qt_app():
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    yield app

def test_dashboard_text_viewer(qt_app, tmp_path):
    dash = StudentDashboard()
    path = tmp_path / "test.txt"
    path.write_text("hello docs")
    dash.display_content(str(path))
    assert dash.viewer is not None
    assert hasattr(dash.viewer, "load_content")

def test_dashboard_html_viewer(qt_app, tmp_path):
    dash = StudentDashboard()
    path = tmp_path / "test.html"
    path.write_text("<h1>Hello</h1>")
    dash.display_content(str(path))
    assert type(dash.viewer).__name__ == "DocumentViewerWidget"

def test_dashboard_code_viewer(qt_app, tmp_path):
    dash = StudentDashboard()
    path = tmp_path / "code.py"
    path.write_text("print('test')")
    dash.display_content(str(path))
    assert type(dash.viewer).__name__ == "CodeSnippetViewerWidget"

def test_dashboard_image_viewer(qt_app, tmp_path):
    dash = StudentDashboard()
    path = tmp_path / "img.png"
    # Simulate image load: no error if file missing (since image logic handles failure gracefully)
    dash.display_content(str(path))
    assert hasattr(dash.viewer, "load_content") or "Image" in type(dash.viewer).__name__

def test_dashboard_unsupported_extension(qt_app, tmp_path):
    dash = StudentDashboard()
    path = tmp_path / "unknown.xyz"
    path.write_text("???")
    dash.display_content(str(path))
    assert "Unsupported" in dash.viewer.text()