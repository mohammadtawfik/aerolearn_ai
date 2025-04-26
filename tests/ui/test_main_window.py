"""
Test cases for MainWindow and Navigation system.

Uses pytest-qt or manual app launch for functional/smoke tests.
"""
import sys
import pytest

from PyQt6.QtWidgets import QApplication
from app.ui.common.main_window import MainWindow

class DummyAuthService:
    def __init__(self, initial_role="student"):
        self.role = initial_role
    def get_current_role(self):
        return self.role

@pytest.fixture(scope="session")
def qt_app():
    """Provide QApplication only once per pytest session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_window_initialization(qt_app):
    win = MainWindow(config={}, auth_service=DummyAuthService())
    win.show()
    assert win.windowTitle() == "AeroLearn AI"
    assert win.minimumWidth() == 900
    assert win.theme in ("light", "dark")
    win.close()

def test_navigation_role_switch(qt_app):
    service = DummyAuthService()
    win = MainWindow(config={}, auth_service=service)
    win.show()
    # Should default to student
    assert win.stacked_views.currentIndex() == 0
    service.role = "admin"
    win.update_role_navigation()
    assert win.stacked_views.currentIndex() == 2
    win.close()

def test_status_bar_health(qt_app):
    win = MainWindow(config={}, auth_service=DummyAuthService())
    win.update_integration_health("DOWN")
    assert "DOWN" in win.health_label.text()
    win.close()

def test_theme_toggle(qt_app):
    win = MainWindow(config={}, auth_service=DummyAuthService())
    old_theme = win.theme
    win.toggle_theme()
    assert win.theme != old_theme
    win.close()

def test_window_state_persistence(qt_app):
    win = MainWindow(config={}, auth_service=DummyAuthService())
    win.show()
    geom1 = win.saveGeometry()
    win.save_window_state()
    win.close()
    # Simulate new window using saved state
    win2 = MainWindow(config={}, auth_service=DummyAuthService())
    win2.restore_window_state()
    assert isinstance(win2.theme, str)
    win2.close()