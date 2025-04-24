"""
Main entry point for the AeroLearn AI application.
"""

import sys
from PyQt6.QtWidgets import QApplication

from app.ui.common.main_window import MainWindow
from app.core.auth.authentication import AuthenticationService
from app.utils.config_loader import load_config


def main():
 """Initialize and run the AeroLearn AI application."""
 # Load configuration
 config = load_config()
 
 # Initialize the application
 app = QApplication(sys.argv)
 app.setApplicationName("AeroLearn AI")
 app.setApplicationVersion("0.1.0")
 
 # Initialize services
 auth_service = AuthenticationService()
 
 # Create and show the main window
 window = MainWindow(config, auth_service)
 window.show()
 
 # Start the application event loop
 sys.exit(app.exec())


if __name__ == "__main__":
 main()
