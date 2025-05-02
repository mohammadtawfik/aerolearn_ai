import sys
import pytest

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    from PyQt5.QtWidgets import QApplication

@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Session-wide QApplication fixture for PyQt widget testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app