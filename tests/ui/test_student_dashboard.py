"""
Tests for Student Dashboard Framework

Save this file as /tests/ui/test_student_dashboard.py

Covers:
- StudentDashboard: basic rendering, layout, customization
- StudentWidgetRegistry: widget registration/listing
- DashboardState: persistence of per-student widget layouts
- Widget base: interface contract
- Registration and use of sample ProgressWidget

Uses pytest style, consistent with other UI component tests.
"""

import pytest

from app.ui.student.dashboard import StudentDashboard
from app.ui.student.widget_registry import StudentWidgetRegistry
from app.ui.student.widget_base import StudentDashboardWidget
from app.ui.student.dashboard_state import DashboardState
from app.ui.student.register_widgets import register_student_widgets
from app.ui.student.widgets.progress import ProgressWidget

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