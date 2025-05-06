"""
Test File: /tests/ui/test_pyqt6_import_policy.py

Purpose:
- Enforce documentation policy that PyQt6/UI dependencies must never be globally required,
  and importing UI entry points in the wrong environment should fail gracefully.
- Ensures devs/testers are aware of required venv isolation for PyQt6.

See:
- /docs/development/pytest-qt-pyqt6-fix.md
- /docs/architecture/architecture_overview.md (layered separation)
- /code_summary.md (project structure)
"""

import os
import pytest

def test_pyqt6_import_env_policy(monkeypatch):
    """
    This test simulates the presence/absence of PyQt6 and enforces the rule:
    - PyQt6 should only be installed or imported in UI-dev/test venvs.
    - Importing main.py with PyQt6 imports in the main venv should error (expected).

    Passes if:
    - In a non-UI venv, import errors occur as expected.
    - In a UI/test venv, import succeeds.
    """
    is_ui_venv = os.environ.get("AEROLEARN_UI_VENV", "0") == "1"
    try:
        import PyQt6.QtWidgets
        imported = True
    except ImportError:
        imported = False

    if is_ui_venv:
        assert imported, (
            "UI venv (AEROLEARN_UI_VENV=1) should have PyQt6 installed and importable. "
            "See /docs/development/pytest-qt-pyqt6-fix.md."
        )
    else:
        assert not imported, (
            "Non-UI venv should NOT have PyQt6 installed/importable. "
            "If this fails, your venv is contaminated or policy not followed. "
            "See /docs/development/pytest-qt-pyqt6-fix.md."
        )