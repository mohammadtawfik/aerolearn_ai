import pytest
from PyQt6.QtWidgets import QApplication
import sys

# Assume all UI imports are direct and correct (as from course_structure_editor)
from app.ui.common.course_structure_editor import CourseStructureEditor

@pytest.fixture(scope='module')
def qapp():
    """Global QApplication fixture"""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

def mock_course_data():
    return {
        "modules": [
            {
                "title": "Module A",
                "order": 1,
                "lessons": [
                    {"title": "Lesson A1", "order": 1},
                    {"title": "Lesson A2", "order": 2}
                ]
            },
            {
                "title": "Module B",
                "order": 2,
                "lessons": []
            }
        ]
    }

def test_load_and_reorder(qapp):
    widget = CourseStructureEditor()
    data = mock_course_data()
    widget.load_course_structure(data)
    assert widget.tree.topLevelItemCount() == 2
    assert widget.tree.topLevelItem(0).text(0) == "Module A"
    # Simulate reorder in code
    widget.tree.insertTopLevelItem(0, widget.tree.takeTopLevelItem(1))
    widget.recalculate_orders()
    # Validate order is correct in tree
    assert widget.tree.topLevelItem(0).text(0) == "Module B"
    assert widget.tree.topLevelItem(0).text(2) == "1"
    assert widget.tree.topLevelItem(1).text(2) == "2"

def test_save_structure(qapp):
    widget = CourseStructureEditor()
    data = mock_course_data()
    widget.load_course_structure(data)
    widget.recalculate_orders()
    # Simulate save, ensure output shape
    # Here, you could simulate/patch actual database saves
    widget.save_structure()  # Should show QMessageBox if running in real Qt

def test_prerequisite_dialog(qapp):
    widget = CourseStructureEditor()
    data = mock_course_data()
    widget.load_course_structure(data)
    widget.show_prerequisites_dialog()  # Activate dialog for coverage
