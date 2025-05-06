"""
File: /tests/ui/test_ui_env_preflight.py

Purpose:
- Enforce all README and troubleshooting doc requirements from code, for the UI venv/dev/test environment.
- Catch the most common bootstrap and runtime errors *before* they hit main.py or CI.

References:
- /README.md (PyQt6 policy)
- /docs/development/pytest-qt-pyqt6-fix.md
"""

import os
import sys
import subprocess
import pytest

def test_venv_is_active():
    """Fail if not running in a virtual environment."""
    assert (
        sys.prefix != sys.base_prefix or hasattr(sys, "real_prefix")
    ), (
        "You must use a Python virtual environment for UI work. See /README.md and /docs/development/pytest-qt-pyqt6-fix.md"
    )

def test_no_pyqt5_or_pyside():
    """Fail if PyQt5 or PySide2/PySide6 are installed (per docs)."""
    forbidden = []
    try:
        import PyQt5  # noqa
        forbidden.append("PyQt5")
    except ImportError:
        pass
    try:
        import PySide2  # noqa
        forbidden.append("PySide2")
    except ImportError:
        pass
    try:
        import PySide6  # noqa
        forbidden.append("PySide6")
    except ImportError:
        pass
    assert not forbidden, (
        f"Forbidden packages found: {forbidden}. Remove them from this venv. Only PyQt6 is allowed. See /README.md"
    )

def test_pyqt6_importable():
    """Fail if PyQt6 is not installed or importable."""
    try:
        import PyQt6.QtWidgets
    except ImportError as e:
        pytest.fail(
            "PyQt6 is not installed or importable. See /README.md and /docs/development/pytest-qt-pyqt6-fix.md"
        )

def test_env_var_is_present():
    """Fail if the UI env variable is not set."""
    assert os.environ.get("AEROLEARN_UI_VENV") == "1", (
        "Set the environment variable AEROLEARN_UI_VENV=1 in your UI venv. "
        "See /README.md"
    )

def test_can_create_qt_app():
    """Try to launch a minimal QApplication to ensure DLLs are correct."""
    from PyQt6.QtWidgets import QApplication
    import sys

    # QApplication must be created only once per process and in the main thread.
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    assert app is not None, (
        "Could not create QApplication. This usually means Qt DLLs are still broken. "
        "See /docs/development/pytest-qt-pyqt6-fix.md"
    )