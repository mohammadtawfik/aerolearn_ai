import pytest
from PyQt6.QtWidgets import QApplication
from app.ui.student.widgets.course_navigator import CourseMaterialNavigator

class DummyLesson:
    def __init__(self, title, type="Video"):
        self.title = title
        self.type = type

class DummyModule:
    def __init__(self, title, lessons=None):
        self.title = title
        self.lessons = lessons or []

class DummyCourse:
    def __init__(self, title, modules=None):
        self.title = title
        self.modules = modules or []

@pytest.fixture(scope="module")
def app():
    # PyQt needs to run within a QApplication context even for tests
    return QApplication([])

def test_navigator_shows_courses_and_lessons(app):
    course = DummyCourse("Physics 101", [
        DummyModule("Kinematics", [
            DummyLesson("Intro to Motion"),
            DummyLesson("Velocity Lab"),
        ])
    ])
    nav = CourseMaterialNavigator([course])
    assert nav._tree.topLevelItemCount() == 1
    assert nav._tree.topLevelItem(0).text(0) == "Physics 101"

def test_navigator_search_filters_lessons(app):
    course = DummyCourse("Math", [
        DummyModule("Algebra", [DummyLesson("Quadratic Equations"), DummyLesson("Linear Equations", type="Document")])
    ])
    nav = CourseMaterialNavigator([course])
    nav._search_bar.setText("quad")
    assert nav._tree.topLevelItemCount() == 1
    algebra_module = nav._tree.topLevelItem(0).child(0)
    assert algebra_module.child(0).text(0) == "Quadratic Equations"
    assert algebra_module.childCount() == 1

def test_navigator_favorites_and_recent(app):
    lesson = DummyLesson("Newton's Laws")
    course = DummyCourse("Physics", [DummyModule("Dynamics", [lesson])])
    nav = CourseMaterialNavigator([course])
    nav._add_to_favorites(lesson)
    nav._add_to_recent(lesson)
    assert nav._favorites[0] == lesson
    assert nav._recent[0] == lesson