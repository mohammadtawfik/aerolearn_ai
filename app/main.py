"""
Main entry point for the AeroLearn AI application.

Location: /app/main.py
- Hardened for production demo: adds robust error handling, startup info, and user-friendly feedback
- Handles configuration errors gracefully with fallbacks and clear user messaging
- Provides detailed console output for troubleshooting during demos
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox

from app.ui.common.main_window import MainWindow
from app.core.auth.authentication import AuthenticationService
from app.utils.config_loader import load_config


def show_critical_error(title, message):
    """Show a modal error dialog (PyQt-safe). Useful for demo mode."""
    app = QApplication.instance() or QApplication(sys.argv)
    QMessageBox.critical(None, title, message)
    # If in demo, exit after showing error
    sys.exit(1)


def main():
    """Initialize and run the AeroLearn AI application, with demo-friendly error handling and output."""
    try:
        # -------- CONFIG LOAD --------
        try:
            config = load_config()
            print(f"[INFO] Loaded config: {config}")
        except FileNotFoundError as e:
            msg = (f"[ERROR] {str(e)}\n"
                   "The application will use built-in defaults, but some features might be unavailable."
                   "\nTo resolve: Place a valid 'config.json' or 'config.py' in the project root.")
            print(msg)
            config = {}  # Use empty config for demo; app should guard against missing keys.
        except ValueError as e:
            show_critical_error("Config Error", f"Could not parse config: {e}")
            return

        # -------- INIT QT APP --------
        app = QApplication(sys.argv)
        app.setApplicationName("AeroLearn AI")
        app.setApplicationVersion("0.1.0")

        # -------- INIT SERVICES --------
        auth_service = AuthenticationService()
        print("[INFO] AuthenticationService initialized with default test users.")

        # -------- INIT MAIN WINDOW --------
        try:
            window = MainWindow(config, auth_service)
        except Exception as e:
            show_critical_error(
                "UI Initialization Failed",
                f"The main window could not be started:\n\n{e}"
            )
            return
        window.show()

        # -------- USER-FRIENDLY STARTUP INFO --------
        print("[INFO] Main window launched successfully - AeroLearn AI is running.")
        print("         Available roles for login in demo: admin / student")

        # -------- RUN QT EVENT LOOP --------
        sys.exit(app.exec())
    except Exception as exc:
        # Catch-all: Robust for live demo!
        print(f"[FATAL ERROR] Unexpected error: {exc}")
        try:
            show_critical_error("Application Error", f"Fatal error: {exc}")
        except Exception:
            pass  # If even QMessageBox fails


if __name__ == "__main__":
    main()

# ---------------------
# PLACEMENT NOTE:
# This is '/app/main.py' and must remain at this top-level app location
# as the primary entry point for the application.
# ---------------------
