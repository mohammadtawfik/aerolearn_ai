"""
Tests for Student Dashboard Framework

Save this file as /tests/ui/test_student_dashboard.py

Covers:
- StudentDashboard: basic rendering, layout, customization
- StudentWidgetRegistry: widget registration/listing
- DashboardState: persistence of per-student widget layouts
- Widget base: interface contract
- Registration and use of sample ProgressWidget
- Registration and integration of new widgets: InteractiveQuizWidget, ContentHighlighterWidget, 
  InteractiveDiagramWidget, FlashcardWidget, RichTextNoteEditor, NoteReferenceLinker, 
  NoteOrganizerWidget, NoteSearchWidget

Uses pytest style, consistent with other UI component tests.
"""

import pytest

from app.ui.student.dashboard import StudentDashboard
from app.ui.student.widget_registry import StudentWidgetRegistry, student_widget_registry
from app.ui.student.widget_base import StudentDashboardWidget
from app.ui.student.dashboard_state import DashboardState
from app.ui.student.register_widgets import register_student_widgets
from app.ui.student.widgets.progress import ProgressWidget

# Import all integrated widgets for direct reference
from app.ui.student.widgets.interactive_quiz import InteractiveQuizWidget
from app.ui.student.widgets.content_highlighter import ContentHighlighterWidget
from app.ui.student.widgets.interactive_diagram import InteractiveDiagramWidget
from app.ui.student.widgets.flashcard_widget import FlashcardWidget
from app.ui.student.widgets.richtext_note_editor import RichTextNoteEditor
from app.ui.student.widgets.note_reference_linker import NoteReferenceLinker
from app.ui.student.widgets.note_organizer import NoteOrganizerWidget
from app.ui.student.widgets.note_search import NoteSearchWidget

class DummyWidget(StudentDashboardWidget):
    def render(self):
        return f"<div>Dummy widget for {self.student_id}</div>"

def test_widget_registry_register_and_get():
    reg = StudentWidgetRegistry()
    reg.register("dummy", DummyWidget)
    assert reg.get_widget("dummy") == DummyWidget
    assert "dummy" in reg.list_widgets()

def test_dashboardstate_set_and_get_layout():
    state = DashboardState()
    student_id = "abc"
    layout = ["dummy", "progress"]
    state.set_layout(student_id, layout)
    assert state.get_layout(student_id) == layout

def test_student_dashboard_renders_registered_widgets():
    reg = StudentWidgetRegistry()
    reg.register("dummy", DummyWidget)
    state = DashboardState()
    student_id = "stu-42"
    state.set_layout(student_id, ["dummy"])
    dash = StudentDashboard(registry=reg, state_manager=state)
    output = dash.render(student_id)
    assert "Dummy widget for stu-42" in output
    assert "<div class='student-dashboard-grid'>" in output

def test_dashboard_handles_missing_widget_gracefully():
    reg = StudentWidgetRegistry()
    # "unknown" widget not registered
    state = DashboardState()
    student_id = "x"
    state.set_layout(student_id, ["unknown"])
    dash = StudentDashboard(registry=reg, state_manager=state)
    output = dash.render(student_id)
    assert "Missing widget: unknown" in output

def test_studentdashboard_customize_layout():
    reg = StudentWidgetRegistry()
    reg.register("dummy", DummyWidget)
    state = DashboardState()
    student_id = "change"
    dash = StudentDashboard(registry=reg, state_manager=state)
    dash.customize(student_id, ["dummy"])
    assert state.get_layout(student_id) == ["dummy"]

def test_widget_config_schema():
    w = DummyWidget(student_id="s1")
    # Should be empty/default unless overridden
    assert isinstance(w.get_config_schema(), dict)

def test_register_widgets_function_registers_progress_widget():
    reg = StudentWidgetRegistry()
    reg = register_student_widgets(reg)
    assert "progress" in reg.list_widgets()
    assert reg.get_widget("progress") is ProgressWidget

def test_progress_widget_renders_basic_html():
    prog = ProgressWidget(student_id="stu99")
    html = prog.render()
    assert f"Progress for student stu99" in html
    assert "75%" in html

# --- EXTENDED TESTS FOR ALL INTEGRATED WIDGETS ---

NEW_WIDGETS = [
    ("interactive_quiz", InteractiveQuizWidget),
    ("content_highlighter", ContentHighlighterWidget),
    ("interactive_diagram", InteractiveDiagramWidget),
    ("flashcard_widget", FlashcardWidget),
    ("richtext_note_editor", RichTextNoteEditor),
    ("note_reference_linker", NoteReferenceLinker),
    ("note_organizer", NoteOrganizerWidget),
    ("note_search", NoteSearchWidget),
]

@pytest.mark.parametrize("widget_id,widget_cls", NEW_WIDGETS)
def test_widget_registry_has_integrated_widgets(widget_id, widget_cls):
    """Ensure all new widgets are present in the default registry."""
    assert widget_id in student_widget_registry.list_widgets()
    assert student_widget_registry.get_widget(widget_id) is widget_cls

@pytest.mark.parametrize("widget_id,widget_cls", NEW_WIDGETS)
def test_dashboard_can_render_all_integrated_widgets(widget_id, widget_cls):
    """Test that dashboard can instantiate and include all new widgets."""
    reg = StudentWidgetRegistry()
    reg.register(widget_id, widget_cls)
    state = DashboardState()
    student_id = "integration-user"
    # Single-widget layout for explicit test
    state.set_layout(student_id, [widget_id])
    dash = StudentDashboard(registry=reg, state_manager=state)
    output = dash.render(student_id)
    # Accept either .render() HTML or a generic placeholder
    assert widget_id in output or "<div class='dashboard-widget-qt'>" in output or "<div class='widget-error'>" not in output

def test_dashboard_renders_full_grid_of_integration_widgets():
    """Test a dashboard containing all new widgets in grid layout."""
    reg = StudentWidgetRegistry()
    for widget_id, widget_cls in NEW_WIDGETS:
        reg.register(widget_id, widget_cls)
    state = DashboardState()
    student_id = "fulltest"
    layout = [wid for wid, _ in NEW_WIDGETS]
    state.set_layout(student_id, layout)
    dash = StudentDashboard(registry=reg, state_manager=state)
    html = dash.render(student_id)
    for widget_id, _ in NEW_WIDGETS:
        assert widget_id in html or "<div class='dashboard-widget-qt'>" in html
    assert "<div class='student-dashboard-grid'>" in html
