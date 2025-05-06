import sys
import pytest

try:
    from PyQt6.QtWidgets import QApplication
except ImportError as e:
    raise ImportError(
        "PyQt6 is required for all UI testing. "
        "Do not install PyQt5 or PySide. See /docs/development/pytest-qt-pyqt6-fix.md for venv setup."
    ) from e

@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Session-wide QApplication fixture for PyQt6 widget testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
