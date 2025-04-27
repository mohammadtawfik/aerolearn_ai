import pytest
import sys
from PyQt6.QtWidgets import QApplication, QWidget
from app.ui.professor.upload_widget import ProfessorUploadWidget

# Guarantee a single QApplication instance for PyQt6 widgets, needed for pytest-qt's qtbot.
@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

@pytest.fixture
def widget(qapp, qtbot):
    test_widget = ProfessorUploadWidget()
    qtbot.addWidget(test_widget)
    # --- Diagnostic prints for debugging PyQt6 class ancestry ---
    print("ProfessorUploadWidget class:", type(test_widget))
    print("ProfessorUploadWidget base classes:", ProfessorUploadWidget.__bases__)
    print("ProfessorUploadWidget QWidget ancestry:", isinstance(test_widget, QWidget))
    print("ProfessorUploadWidget QWidget module:", QWidget.__module__)
    print("ProfessorUploadWidget type module:", type(test_widget).__module__)
    print("QWidget id:", id(QWidget))
    print("test_widget QWidget id:", id(type(test_widget).__bases__[0]))
    return test_widget

def test_add_files_and_selection(widget):
    files = [
        {'filepath': '/tmp/test1.pdf', 'mimetype': 'application/pdf'},
        {'filepath': '/tmp/test2.jpg', 'mimetype': 'image/jpeg'}
    ]
    widget.add_files(files)
    # After adding, files should be tracked in current_uploads by path
    assert '/tmp/test1.pdf' in widget.current_uploads
    assert '/tmp/test2.jpg' in widget.current_uploads

def test_mimetype_detection(widget):
    file_pdf = "/tmp/file.pdf"
    file_img = "/tmp/file.jpg"
    file_vid = "/tmp/file.mp4"
    assert widget.detect_mimetype(file_pdf) == "application/pdf"
    assert widget.detect_mimetype(file_img) == "image/jpeg"
    assert widget.detect_mimetype(file_vid) == "video/mp4"

def test_progress_bar_updates(widget, qtbot):
    files = [{'filepath': '/tmp/mockfile.pdf', 'mimetype': 'application/pdf'}]
    widget.add_files(files)
    widget.set_progress('/tmp/mockfile.pdf', 57)
    # Check via current_uploads mapping
    pb = widget.current_uploads['/tmp/mockfile.pdf']
    assert pb.value() == 57

def test_completed_and_failed_labels(widget, qtbot):
    files = [
        {'filepath': '/tmp/mockdone.pdf', 'mimetype': 'application/pdf'},
        {'filepath': '/tmp/mockfail.pdf', 'mimetype': 'application/pdf'}
    ]
    widget.add_files(files)
    widget.mark_completed('/tmp/mockdone.pdf', True)
    # Completed bar should be at 100
    assert widget.current_uploads['/tmp/mockdone.pdf'].value() == 100
    widget.mark_completed('/tmp/mockfail.pdf', False)
    # Failed bar should be at 0 (failure indicator)
    assert widget.current_uploads['/tmp/mockfail.pdf'].value() == 0
