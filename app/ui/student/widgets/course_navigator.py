"""
Course Material Navigator Widget for Student UI

Location: /app/ui/student/widgets/course_navigator.py
-------------------------------------------------------------------------------
Implements:
    - Hierarchical navigation structure (Course > Module > Lesson > Content)
    - Content type filtering (by video, document, quiz, etc.)
    - Search within course materials
    - Breadcrumb navigation and navigation history
    - Favorites and recently accessed tracking
    - Dynamic integration with different content types
    - Customization extension points
-------------------------------------------------------------------------------
Fix:
    - Filtering/search now builds filtered tree for display, never modifying the originals
      (avoids empty tree during/after search and failures in testing).
-------------------------------------------------------------------------------

Integrate this widget into the student dashboard or main content view for content exploration.

Dependencies:
    - Expects Course, Module, Lesson data structures (from app/models)
    - Optionally interacts with user profile or preferences for favorites/recent
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLineEdit, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

# Placeholder imports (customize as required)
# from app.models.course import Course, Module, Lesson
# from app.models.content import Content

class CourseMaterialNavigator(QWidget):
    # Signals for navigation and selection
    materialSelected = pyqtSignal(object)  # e.g., lesson/content selected

    def __init__(self, courses, parent=None):
        """
        courses: list of Course objects (loaded from models)
        """
        super().__init__(parent)
        self.courses = courses  # Full course tree - do NOT mutate during filtering!
        self._search_query = ""
        self._filter_type = "All"

        # UI Components
        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText("Search course materials...")
        self._content_type_filter = QComboBox()
        self._content_type_filter.addItems([
            "All", "Video", "Document", "Quiz", "Code", "Image"
        ])
        self._breadcrumb_bar = QLabel("Home")
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Course Materials"])
        self._favorites_list = QListWidget()
        self._recent_list = QListWidget()

        # Layouts
        self._layout = QVBoxLayout()
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Type:"))
        filter_row.addWidget(self._content_type_filter)
        filter_row.addWidget(self._search_bar)

        nav_row = QHBoxLayout()
        nav_row.addWidget(QLabel("Breadcrumb:"))
        nav_row.addWidget(self._breadcrumb_bar)

        lists_row = QHBoxLayout()
        lists_row.addWidget(QLabel("Favorites:"))
        lists_row.addWidget(self._favorites_list)
        lists_row.addWidget(QLabel("Recently Accessed:"))
        lists_row.addWidget(self._recent_list)

        self._layout.addLayout(filter_row)
        self._layout.addLayout(nav_row)
        self._layout.addWidget(self._tree, 1)
        self._layout.addLayout(lists_row)
        self.setLayout(self._layout)

        # Internal state
        self._breadcrumb = []
        self._favorites = []
        self._recent = []

        # Connections
        self._search_bar.textChanged.connect(self._on_search)
        self._content_type_filter.currentIndexChanged.connect(self._on_filter)
        self._tree.itemClicked.connect(self._on_tree_item_clicked)
        self._favorites_list.itemClicked.connect(self._on_favorite_clicked)
        self._recent_list.itemClicked.connect(self._on_recent_clicked)

        # Populate UI
        self._refresh_tree()

    # --- Navigation Tree Logic ---
    def _refresh_tree(self):
        self._tree.clear()
        # Filter courses for display (do not mutate originals!)
        for course in self._filtered_courses():
            course_item = QTreeWidgetItem([course.title])
            course_item.setData(0, Qt.ItemDataRole.UserRole, course)
            for module in self._filtered_modules(course):
                module_item = QTreeWidgetItem([module.title])
                module_item.setData(0, Qt.ItemDataRole.UserRole, module)
                for lesson in self._filtered_lessons(module):
                    lesson_item = QTreeWidgetItem([lesson.title])
                    lesson_item.setData(0, Qt.ItemDataRole.UserRole, lesson)
                    module_item.addChild(lesson_item)
                if module_item.childCount() > 0:
                    course_item.addChild(module_item)
            if course_item.childCount() > 0:
                self._tree.addTopLevelItem(course_item)
        self._tree.expandAll()

    def _filtered_courses(self):
        # Returns all courses that match filter or have children after filtering
        return [
            c for c in self.courses
            if self._query_match(c.title) or any(self._filtered_modules(c))
        ]

    def _filtered_modules(self, course):
        # Returns modules of a course passing filter/query, with children
        modules = getattr(course, "modules", [])
        return [
            m for m in modules
            if self._query_match(m.title) or any(self._filtered_lessons(m))
        ]

    def _filtered_lessons(self, module):
        # Returns lessons matching search/filter
        lessons = getattr(module, "lessons", [])
        result = []
        for l in lessons:
            if self._filter_lessons(l):
                result.append(l)
        return result

    def _filter_lessons(self, lesson):
        type_match = (self._filter_type == "All" or getattr(lesson, "type", "Any") == self._filter_type)
        query_match = self._query_match(lesson.title)
        return type_match and query_match

    def _query_match(self, text):
        # Returns True if search query is in text (case-insensitive), otherwise True if query is empty
        if not self._search_query:
            return True
        return self._search_query in text.lower()

    # --- Search and Filtering Logic ---
    def _on_search(self, query):
        self._search_query = query.lower()
        self._refresh_tree()

    def _on_filter(self, idx):
        self._filter_type = self._content_type_filter.currentText()
        self._refresh_tree()

    # --- Breadcrumb Navigation & History ---
    def _update_breadcrumb(self, item):
        labels = []
        obj = item.data(0, Qt.ItemDataRole.UserRole)
        while item:
            labels.append(item.text(0))
            item = item.parent()
        self._breadcrumb = list(reversed(labels))
        self._breadcrumb_bar.setText(" > ".join(self._breadcrumb))

    def _on_tree_item_clicked(self, item, col):
        obj = item.data(0, Qt.ItemDataRole.UserRole)
        self._update_breadcrumb(item)
        self._add_to_recent(obj)
        self.materialSelected.emit(obj)

    # --- Favorites and Recently Accessed ---
    def _add_to_favorites(self, obj):
        if obj not in self._favorites:
            self._favorites.append(obj)
            self._favorites_list.addItem(QListWidgetItem(obj.title))

    def _add_to_recent(self, obj):
        if obj not in self._recent:
            self._recent.insert(0, obj)
            self._recent_list.insertItem(0, QListWidgetItem(obj.title))
            # Limit recent list
            if self._recent_list.count() > 10:
                self._recent.pop()
                self._recent_list.takeItem(10)

    def _on_favorite_clicked(self, item):
        idx = self._favorites_list.row(item)
        obj = self._favorites[idx]
        self.materialSelected.emit(obj)

    def _on_recent_clicked(self, item):
        idx = self._recent_list.row(item)
        obj = self._recent[idx]
        self.materialSelected.emit(obj)

    # --- Extension Point for Customization/Integration ---
    def add_course(self, course):
        """Dynamically add a course and refresh the tree."""
        self.courses.append(course)
        self.filtered_courses = self.courses
        self._refresh_tree()

    def apply_custom_filter(self, filter_func):
        """Inject custom filter logic."""
        # This extension point would need to be integrated with the non-destructive filtering
        # For now, just refresh the tree
        self._refresh_tree()

    # --- Saving/Restoring State (for persistence/integration) ---
    def get_favorites(self):
        return self._favorites

    def get_recent(self):
        return self._recent

    def set_favorites(self, favorites):
        self._favorites = favorites
        self._favorites_list.clear()
        for obj in favorites:
            self._favorites_list.addItem(QListWidgetItem(obj.title))

    def set_recent(self, recent):
        self._recent = recent
        self._recent_list.clear()
        for obj in recent:
            self._recent_list.addItem(QListWidgetItem(obj.title))

# Example of usage would be in /app/ui/student/dashboard.py or main content pane.
# To persist favorites/recent list, integrate with user profile storage.

"""
DOCUMENTATION:

CourseMaterialNavigator
-----------------------
A PyQt6 widget for hierarchical exploration of course materials. Supports customization for different content types and is extensible for new navigation paradigms.

Extension Points:
  - add_course(): dynamically augment the tree
  - apply_custom_filter(): add new filtering logic
  - set_favorites()/get_favorites(), set_recent()/get_recent(): for persistent user experience

Widget Location:
    /app/ui/student/widgets/course_navigator.py

Integrate with dashboard or register in widget_registry as appropriate.
"""
