"""
Main application window for AeroLearn AI.

Implements:
- Central widget layout with view-switching (navigation)
- Role-based navigation (hooked)
- Status bar showing integration health
- Window state persistence/restoration
- Theme and style management

Requires PyQt6 (or compatible PySide6).
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QStatusBar, QLabel, QToolBar, QApplication
)
from PyQt6.QtGui import QAction  # QAction is in QtGui in PyQt6, not QtWidgets
from PyQt6.QtCore import Qt, QSettings, QSize
from app.ui.common.navigation import NavigationManager

class MainWindow(QMainWindow):
    def __init__(self, config, auth_service, parent=None):
        super().__init__(parent)

        self.config = config
        self.auth_service = auth_service
        self._settings = QSettings("AeroLearnAI", "MainWindow")
        self.theme = self.load_theme_from_settings()

        self.setWindowTitle("AeroLearn AI")
        self.setMinimumSize(QSize(900, 600))
        self.restore_window_state()

        # Central widget/layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        # Navigation and main stacked view
        self.navigation = NavigationManager(self, self.auth_service)
        main_layout.addWidget(self.navigation.sidebar_widget)  # sidebar nav
        self.stacked_views = QStackedWidget()
        main_layout.addWidget(self.stacked_views)
        self.navigation.set_stacked_widget(self.stacked_views)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.health_label = QLabel("Integration Health: Unknown")
        self.status.addPermanentWidget(self.health_label)

        # Toolbar for theme switching
        toolbar = QToolBar("Toolbar")
        theme_action = QAction("Toggle Theme", self)
        theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(theme_action)
        self.addToolBar(toolbar)

        # For demonstration, add example views
        self.add_example_views()

        # Connect auth signals for role-based navigation updates
        if hasattr(self.auth_service, "authentication_changed"):
            self.auth_service.authentication_changed.connect(self.update_role_navigation)
        self.update_role_navigation()

        # Status bar updates via health monitoring (stub)
        self.update_integration_health("OK")

    def add_example_views(self):
        # In real use, import and add real UI screens
        user_view = QLabel("User Dashboard View")
        professor_view = QLabel("Professor Dashboard View")
        admin_view = QLabel("Admin Dashboard View")
        self.stacked_views.addWidget(user_view)          # index 0
        self.stacked_views.addWidget(professor_view)     # index 1
        self.stacked_views.addWidget(admin_view)         # index 2
        self.navigation.register_view("student", 0)
        self.navigation.register_view("professor", 1)
        self.navigation.register_view("admin", 2)

    def update_role_navigation(self):
        # Switch view/controls based on user role
        role = getattr(self.auth_service, "get_current_role", lambda: "student")()
        self.navigation.switch_to_role(role)
        self.status.showMessage(f"Navigation updated for role: {role}")

    def update_integration_health(self, health_status: str):
        # In production, fetch from monitoring API/module
        self.health_label.setText(f"Integration Health: {health_status}")

    def closeEvent(self, event):
        # Save settings/state
        self.save_window_state()
        super().closeEvent(event)

    def save_window_state(self):
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.setValue("windowState", self.saveState())
        self._settings.setValue("theme", self.theme)

    def restore_window_state(self):
        geom = self._settings.value("geometry")
        if geom:
            self.restoreGeometry(geom)
        winstate = self._settings.value("windowState")
        if winstate:
            self.restoreState(winstate)

    def load_theme_from_settings(self):
        return self._settings.value("theme", "light")

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme(self.theme)
        self.status.showMessage(f"Theme set to: {self.theme}", 2000)

    def apply_theme(self, theme):
        if theme == "dark":
            self.setStyleSheet("""QMainWindow { background: #23242b; color: #eee; }
                                  QLabel { color: #eee; }
                                  QStatusBar { background: #222; color: #eee; }""")
        else:
            self.setStyleSheet("")
