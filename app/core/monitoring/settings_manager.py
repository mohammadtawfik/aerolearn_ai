"""
System Settings Manager for AeroLearn AI
Save at: /app/core/monitoring/settings_manager.py

Provides:
- Definition of global system settings (as schema)
- Validated set/get/update methods
- Persistence (JSON or YAML)
- Change notification (callback/event hooks)
- Default settings with override support
"""

import os
import json
from typing import Any, Dict, Callable, Optional

SETTINGS_SCHEMA = {
    "max_upload_size_mb": {"type": int, "min": 10, "max": 512, "default": 50},
    "enable_alerts": {"type": bool, "default": True},
    "alert_email": {"type": str, "default": ""},
    "dependency_visual_theme": {"type": str, "default": "light"},
    "maintenance_mode": {"type": bool, "default": False},
    # Add more settings and their schema here
}

SETTINGS_FILE = os.path.join(
    os.path.dirname(__file__), "system_settings.json"
)

class SettingValidationError(Exception):
    pass

class SystemSettingsManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._settings: Dict[str, Any] = {}
        self._callbacks = []
        self._load()

    def _validate(self, key: str, value: Any):
        if key not in SETTINGS_SCHEMA:
            raise SettingValidationError(f"Unknown setting: {key}")
        schema = SETTINGS_SCHEMA[key]
        if not isinstance(value, schema["type"]):
            raise SettingValidationError(
                f"Setting '{key}' must be of type {schema['type'].__name__}"
            )
        if "min" in schema and value < schema["min"]:
            raise SettingValidationError(
                f"Setting '{key}' below minimum ({schema['min']})"
            )
        if "max" in schema and value > schema["max"]:
            raise SettingValidationError(
                f"Setting '{key}' above maximum ({schema['max']})"
            )

    def _load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    raw_settings = json.load(f)
                for key, val in raw_settings.items():
                    self._validate(key, val)
                    self._settings[key] = val
            except Exception:
                self._settings = {}
        # Fill in defaults for anything missing
        for key, schema in SETTINGS_SCHEMA.items():
            if key not in self._settings:
                self._settings[key] = schema["default"]

    def save(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self._settings, f, indent=2)

    def get(self, key: str) -> Any:
        if key not in self._settings:
            raise KeyError(f"Unknown setting: {key}")
        return self._settings[key]

    def set(self, key: str, value: Any):
        self._validate(key, value)
        old_value = self._settings.get(key)
        self._settings[key] = value
        self.save()
        self._notify_callbacks(key, old_value, value)

    def all(self) -> Dict[str, Any]:
        return dict(self._settings)

    def register_callback(self, callback: Callable[[str, Any, Any], None]):
        self._callbacks.append(callback)

    def _notify_callbacks(self, key, old_value, new_value):
        for cb in self._callbacks:
            try:
                cb(key, old_value, new_value)
            except Exception as e:
                # Log or handle callback error
                pass

# Singleton accessor for convenience
system_settings = SystemSettingsManager()