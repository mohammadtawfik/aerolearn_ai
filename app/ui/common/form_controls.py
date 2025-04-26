"""
AeroLearn AI — Standardized UI Form Controls module

This module provides reusable, themed UI form controls for the desktop UI. 
Designed to be used with a UI toolkit such as PyQt5/PySide2 (Qt), though logic is separated
for backend/UI framework independence and testability.

Includes:
- TextInputControl (single-line)
- PasswordInputControl
- MultiLineTextControl
- DropdownControl
- CheckboxControl

Implements:
- Input validation
- Error/validation message display
- Event emission (value changed, validation status)
- Theme/style compatibility
- Basic accessibility support

Integration: Hooks into EventBus system for notification and validation events.

"""

from typing import Any, Callable, List, Optional, Dict, Union

try:
    from PyQt5.QtWidgets import (QWidget, QLineEdit, QVBoxLayout, QLabel, QCheckBox, QComboBox, QTextEdit)
    from PyQt5.QtCore import pyqtSignal, Qt
except ImportError:
    # For non-UI headless or testing environments
    QWidget, QLineEdit, QVBoxLayout, QLabel, QCheckBox, QComboBox, QTextEdit, pyqtSignal, Qt = (object,) * 8

# EventBus integration placeholder
try:
    from integrations.events.event_bus import EventBus
except ImportError:
    EventBus = None

class BaseFormControl(QWidget):
    """Abstract base for AeroLearn form controls."""
    value_changed = pyqtSignal(object)
    validation_failed = pyqtSignal(str)
    validation_passed = pyqtSignal()

    def __init__(self, label: Optional[str] = None, required: bool = False, validator: Optional[Callable] = None):
        super().__init__()
        self.label = label
        self.required = required
        self.validator = validator
        self._setup_ui()
        self._connect_events()

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        if self.label:
            self.label_widget = QLabel(self.label)
            self.layout.addWidget(self.label_widget)
        self.setLayout(self.layout)

    def _connect_events(self):
        pass # To be implemented in subclasses

    def get_value(self):
        raise NotImplementedError

    def set_value(self, value):
        raise NotImplementedError

    def validate(self):
        val = self.get_value()
        if self.required and (val is None or val == ''):
            self.validation_failed.emit("This field is required.")
            return False
        if self.validator:
            try:
                if not self.validator(val):
                    self.validation_failed.emit(f"Validation failed for value: {val}")
                    return False
            except Exception as e:
                self.validation_failed.emit(str(e))
                return False
        self.validation_passed.emit()
        return True

class TextInputControl(BaseFormControl):
    def _setup_ui(self):
        super()._setup_ui()
        self.input = QLineEdit()
        self.layout.addWidget(self.input)

    def _connect_events(self):
        self.input.textChanged.connect(lambda val: self.value_changed.emit(val))
        self.input.editingFinished.connect(self.validate)

    def get_value(self):
        return self.input.text()

    def set_value(self, value):
        self.input.setText(str(value) if value is not None else "")

class PasswordInputControl(TextInputControl):
    def _setup_ui(self):
        super()._setup_ui()
        self.input.setEchoMode(QLineEdit.Password)

class MultiLineTextControl(BaseFormControl):
    def _setup_ui(self):
        super()._setup_ui()
        self.input = QTextEdit()
        self.layout.addWidget(self.input)

    def _connect_events(self):
        self.input.textChanged.connect(lambda: self.value_changed.emit(self.get_value()))
        self.input.focusOutEvent = lambda e: (self.validate(), QTextEdit.focusOutEvent(self.input, e))

    def get_value(self):
        return self.input.toPlainText()

    def set_value(self, value):
        self.input.setPlainText(str(value) if value is not None else "")

class DropdownControl(BaseFormControl):
    def __init__(self, label: Optional[str]=None, options: Optional[List[str]]=None, required: bool=False, validator=None):
        self.options = options or []
        super().__init__(label, required, validator)

    def _setup_ui(self):
        super()._setup_ui()
        self.input = QComboBox()
        self.input.addItems(self.options)
        self.layout.addWidget(self.input)

    def _connect_events(self):
        self.input.currentTextChanged.connect(lambda val: self.value_changed.emit(val))
        self.input.activated.connect(lambda idx: self.validate())

    def get_value(self):
        return self.input.currentText()

    def set_value(self, value):
        idx = self.input.findText(value)
        if idx >= 0:
            self.input.setCurrentIndex(idx)

class CheckboxControl(BaseFormControl):
    def _setup_ui(self):
        super()._setup_ui()
        self.input = QCheckBox()
        self.layout.addWidget(self.input)

    def _connect_events(self):
        self.input.stateChanged.connect(lambda val: self.value_changed.emit(bool(val)))
        self.input.clicked.connect(lambda: self.validate())

    def get_value(self):
        return self.input.isChecked()

    def set_value(self, value):
        self.input.setChecked(bool(value))

# Example minimal form usage - for testability
def create_test_form():
    import sys
    from PyQt5.QtWidgets import QApplication, QFormLayout, QPushButton, QDialog

    app = QApplication(sys.argv)
    dialog = QDialog()
    form = QFormLayout()
    name = TextInputControl("Name", required=True)
    password = PasswordInputControl("Password", required=True)
    bio = MultiLineTextControl("Bio")
    subscribe = CheckboxControl("Subscribe", required=False)
    role = DropdownControl("Role", options=["Student", "Professor", "Admin"], required=True)

    controls = [name, password, bio, subscribe, role]
    for ctrl in controls:
        form.addRow(ctrl.label, ctrl)

    dialog.setLayout(form)
    dialog.exec_()

if __name__ == '__main__':
    # For direct test run
    create_test_form()