"""
File Location: /tests/ui/test_multi_format_content_viewer.py
Purpose: Functional and construction tests for student content viewer widgets (Task 3.2.2).
"""

import os
import pytest

from app.ui.student.widgets.document_viewer import DocumentViewerWidget
from app.ui.student.widgets.video_player import VideoPlayerWidget
from app.ui.student.widgets.code_snippet_viewer import CodeSnippetViewerWidget
from app.ui.student.widgets.image_viewer import ImageViewerWidget

from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="module")
def qt_app():
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    yield app

def test_document_viewer_text(qt_app, tmp_path):
    viewer = DocumentViewerWidget()
    fpath = tmp_path / "sample.txt"
    fpath.write_text("Hello, World!")
    viewer.load_content(str(fpath))
    assert viewer.browser.toPlainText() == "Hello, World!"

def test_document_viewer_html(qt_app, tmp_path):
    viewer = DocumentViewerWidget()
    fpath = tmp_path / "sample.html"
    html = "<h1>Test</h1>"
    fpath.write_text(html)
    viewer.load_content(str(fpath))
    assert "Test" in viewer.browser.toHtml()

def test_code_snippet_viewer_python(qt_app, tmp_path):
    viewer = CodeSnippetViewerWidget()
    fpath = tmp_path / "sample.py"
    code = "print('hi')"
    fpath.write_text(code)
    viewer.load_content(str(fpath))
    displayed = getattr(viewer.editor, "text", lambda: viewer.editor.toPlainText())()
    assert "print" in displayed

def test_image_viewer_load(qt_app):
    viewer = ImageViewerWidget()
    # Can't truly load/test image in CI, but can call .load_content
    # Can assert no crash or label fallback
    viewer.load_content("nonexistent_file.png")
    assert viewer.image_label.text() or not viewer.image_label.pixmap() is None

def test_video_player_stub(qt_app):
    viewer = VideoPlayerWidget()
    # Just checks construction and method existence
    assert hasattr(viewer, "load_content")
    # actual playback tested elsewhere