# PyQt6/pytest-qt Environment Configuration & Troubleshooting Guide

This guide outlines the **robust configuration and troubleshooting steps** for running PyQt6 and pytest-qt together. Use this if you experience errors like:

```
ImportError: DLL load failed while importing QtCore: The specified module could not be found.
```

## 1. Set `qt_api=pyqt6` in `pytest.ini`

In your project's `pytest.ini`, add:

```ini
[pytest]
qt_api = pyqt6
```
This **instructs pytest-qt to use PyQt6** explicitly, eliminating backend guessing or mixing with PySide or older PyQt5.

## 2. Remove redundant `os.environ["QT_API"] = "pyqt6"` lines

This includes:
- At the top of `tests/conftest.py`
- At the top of any test module; e.g., `tests/ui/test_professor_upload_widget.py`

**Only the `pytest.ini` setting is required.**  
Too many locations, or conflicting settings, may interfere with pytest's plugin auto-configuration.

## 3. Ensure ONLY PyQt6 is installed in your venv

Run:

```sh
pip uninstall PyQt5 PySide2 PySide6
pip install --upgrade pip
pip install --upgrade pytest pytest-qt PyQt6
```
Do **not** install both PyQt5 and PyQt6 or any PySide module.  
A clean venv is recommended if you continue to observe issues.

## 4. DLL Issues and PATH Conflicts

On Windows, sometimes orphan DLLs or PATH inconsistencies (anaconda, old Qt installs, etc) can also cause this error.  
Ensure your `PATH` has **no Qt-related folders**, other than those from your PyQt6 wheel.  
A reboot may clear locked DLLs after uninstalling or upgrading Qt related packages.

## 5. Confirm it works

```sh
pytest
```
Or via IDE, rerun your tests.


---
## Example Minimal `pytest.ini`

```ini
[pytest]
minversion = 7.0
addopts = -ra -q
testpaths = 
    tests
python_files = test_*.py
python_classes = Test* test*
python_functions = test_*
pythonpath = .
asyncio_default_fixture_loop_scope = function
qt_api = pyqt6
```

---

## 6. Reference

- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/en/latest/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [PyPI - pytest-qt](https://pypi.org/project/pytest-qt/)

---

## 7. Why This Fixes the Error

- **qt_api = pyqt6** (pytest.ini): forces pytest-qt to use your installed PyQt6.
- Removing `os.environ["QT_API"] = "pyqt6"`: avoids "double loading" and disables confusing order issues.
- Installing only PyQt6: prevents dll conflicts.
- Clean venv: avoids legacy DLLs from previous Qt bindings.

---

**If you still encounter problems after following all above, create a new venv, install only PyQt6 and pytest-qt, and test there to eliminate any lingering system conflicts.**